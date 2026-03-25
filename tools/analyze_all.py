#!/usr/bin/env python3
"""
Complete Sonic 1 ROM analysis script.
Closes all remaining gaps: cheat codes, Z80 driver, tilesets, demo data, time bonuses, palette cycles, TMSS.
"""

import struct
import os

ROM_PATH = r'C:\Users\Dokuchaev_ts\Downloads\Sonic The Hedgehog (USA, Europe)\Sonic The Hedgehog (USA, Europe).gen'
rom = open(ROM_PATH, 'rb').read()

def read_word(addr):
    return struct.unpack('>H', rom[addr:addr+2])[0]

def read_long(addr):
    return struct.unpack('>I', rom[addr:addr+4])[0]

def read_sword(addr):
    return struct.unpack('>h', rom[addr:addr+2])[0]

# Button bit masks for $F605 (active-low inverted, so 1 = pressed)
BTN = {0: 'END', 1: 'Up', 2: 'Down', 4: 'Left', 8: 'Right',
       0x10: 'B', 0x20: 'C', 0x40: 'A', 0x80: 'Start'}

print("=" * 70)
print("SONIC 1 (US/EU) — COMPLETE ROM ANALYSIS")
print("=" * 70)

# =====================================================================
# 1. CHEAT CODE SEQUENCES
# =====================================================================
print("\n" + "=" * 70)
print("1. CHEAT CODE SEQUENCES (from ROM)")
print("=" * 70)

# Title screen code at $31C4-$31D4:
#   $31C4: lea $33A4(pc), a0    ; US/EU table
#   $31BC: lea $33AA(pc), a0    ; JP table (if $FFF8 flag set)
# The code at $31D0: reads $F605 (new presses), masks with $0F (D-pad only)
# Compares with byte at (a0) sequentially
# When sequence complete and byte = $00, cheat activated

print("\n--- US/EU Level Select Sequence (table at $33A4) ---")
addr = 0x33A4
seq = []
for i in range(20):
    b = rom[addr + i]
    seq.append(b)
    if b == 0:
        break
print(f"  Raw: {' '.join(f'{b:02X}' for b in seq)}")
print(f"  Buttons: {' -> '.join(BTN.get(b, f'?{b:02X}') for b in seq)}")

print("\n--- Japanese Level Select Sequence (table at $33AA) ---")
addr = 0x33AA
seq2 = []
for i in range(20):
    b = rom[addr + i]
    seq2.append(b)
    if b == 0:
        break
print(f"  Raw: {' '.join(f'{b:02X}' for b in seq2)}")
print(f"  Buttons: {' -> '.join(BTN.get(b, f'?{b:02X}') for b in seq2)}")

# Now look at what happens after sequence detected
# At $3222-$3238: check $F605 & $80 (Start button)
# At $3242: check $FFE0 (cheat flag)
# At $324A: check bit 6 of $F604 (A button held)
print("\n--- Activation after sequence ---")
print("  1. Sequence sets flag at $FFE0")
print("  2. On title screen: press Start (bit 7 of $F605)")
print("  3. If $FFE0 set AND A held (bit 6 of $F604):")
print("     -> Enter Level Select (branch to $3254)")
print("  4. If $FFE0 NOT set or A NOT held:")
print("     -> Normal game start (branch to $3342)")

# Debug mode sound test sequence
# The debug check is in the Level Select screen, checking $FE08
# Let's find the Sound Test comparison code
print("\n--- Debug Mode Activation ---")
# At $3350-$33A4 area, or in the Level Select handler
# In Sonic 1, the debug mode flag $FE08 is set by playing sounds in order:
# The check is typically: after entering Level Select, go to Sound Test
# and play: 01, 09, 09, 01, 00, 06, 02, 03
# This is stored as comparison data

# Search for the debug sequence in ROM
# Known sequence: 01 09 09 01 00 06 02 03
debug_seq = bytes([0x01, 0x09, 0x09, 0x01, 0x00, 0x06, 0x02, 0x03])
pos = rom.find(debug_seq)
if pos != -1:
    print(f"  Debug sequence found at ROM offset ${pos:06X}")
    print(f"  Sequence: 01, 09, 09, 01, 00, 06, 02, 03")
else:
    print("  Debug sequence bytes not found as contiguous block")
    # It may be checked byte-by-byte in code
    # Look at Level Select Sound Test handler area
    # The flag is at $FE08 — search for writes to it
    print("  Searching for $FE08 references...")
    fe08_bytes = b'\xFE\x08'
    found = []
    start = 0
    while True:
        p = rom.find(fe08_bytes, start)
        if p == -1 or p > 0x4000:
            break
        found.append(p)
        start = p + 1
    print(f"  $FE08 referenced at ROM offsets: {[f'${x:04X}' for x in found[:10]]}")

# Check at the title screen - the cheat check with C button presses on SEGA screen
# At $31E4-$3210 area: counter for C button presses
print("\n--- SEGA Screen C-button Sequence ---")
# At $2EE8 area: SEGA screen transitions to title
# Actually the C-presses on SEGA screen is part of the older version
# In US/EU v1.0, the sequence is entered on the title screen directly
# Let's check the $FFE4/$FFE6 counters
print("  $FFE4 = cheat sequence position counter")
print("  $FFE6 = C-button press counter")
print("  Code at $3222-$3230: check $F605 & $20 (C button)")
print("  If pressed: increment $FFE6")
print("  $FFE6 >> 1, AND #3 determines sub-cheat variant")

# =====================================================================
# 2. Z80 SOUND DRIVER ANALYSIS
# =====================================================================
print("\n" + "=" * 70)
print("2. Z80 SOUND DRIVER ANALYSIS")
print("=" * 70)

# Z80 code in Sonic 1 is loaded by SoundDriverLoad at around $135C
# The Z80 program data is stored in the ROM 
# Let's find it by looking at the SoundDriverLoad function
# At $1352: the function that loads Z80 code

# The Z80 code starts being loaded at the address pointed to by the loader
# Typically in Sonic 1, the Z80 driver is at the end of the 68K code area
# Let's look at addresses referenced by SoundDriverLoad

# From our disassembly, SoundDriverLoad is at $11B8 area
# Let's check the loading loop
print("\n--- Z80 Driver Location ---")

# Search for Z80 bus request pattern: move.w #$100, $A11100
z80_bus = b'\x33\xFC\x01\x00\x00\xA1\x11\x00'
pos = rom.find(z80_bus)
if pos != -1:
    print(f"  Z80 bus request found at ${pos:06X}")

# In Sonic 1 us/eu, the Z80 driver data typically starts around $E72-$F80 area
# loaded to Z80 RAM $0000
# Let's find the load loop that copies ROM data to Z80 RAM ($A00000)
# Pattern: move.b (a0)+, $A00000 or similar
z80_ram_write = b'\x00\xA0\x00\x00'  # $A00000
positions = []
start = 0
while True:
    p = rom.find(z80_ram_write, start, 0x2000)
    if p == -1:
        break
    positions.append(p)
    start = p + 1
print(f"  $A00000 (Z80 RAM) references: {[f'${x:04X}' for x in positions[:8]]}")

# The actual Z80 driver in Sonic 1 is loaded from a table
# Let's look at SoundDriverLoad more carefully
# SoundDriverLoad at $11B8 (from our analysis)
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000

md = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
md.detail = False

print("\n--- SoundDriverLoad disassembly ---")
code = rom[0x11B8:0x1352]
for insn in md.disasm(code, 0x11B8):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")
    if insn.address > 0x1260:
        break

# Find where Z80 program data is stored
# Usually referenced as a lea instruction loading address of Z80 code block
# In Sonic 1, the Z80 driver is typically embedded starting around $E72
# Let's extract and analyze Z80 code
print("\n--- Z80 Driver Code Extraction ---")
# The Z80 program is copied to Z80 address space starting at $0000
# In Sonic 1 (US/EU), the Z80 code block is loaded from ROM
# Standard location: $E72 for the init code, with main driver following

# Let's try to find the Z80 code by looking for the standard Z80 opcodes
# Z80 programs typically start with DI (F3) or JP/JR instructions
# In Sonic 1, the driver starts with:
#   F3       DI
#   ED 56    IM 1
#   3E xx    LD A, xx

# Search around $E72-$1300
z80_start_pattern = bytes([0xF3, 0xED, 0x56])  # DI; IM 1
for search_start in range(0xE00, 0x1400):
    if rom[search_start:search_start+3] == z80_start_pattern:
        print(f"  Z80 code signature (DI; IM 1) found at ROM ${search_start:06X}")
        # Dump first 64 bytes of Z80 code
        z80_code_start = search_start
        print(f"  First 64 bytes of Z80 driver:")
        for i in range(0, 64, 16):
            hexstr = ' '.join(f'{rom[z80_code_start+i+j]:02X}' for j in range(16))
            print(f"    ${z80_code_start+i:06X}: {hexstr}")
        break

# Try to find Z80 code size by looking for SoundDriverLoad's copy loop counter
print("\n--- Z80 Driver Size ---")
# Look for a dbra loop that copies Z80 data
# Typically: move.b (a0)+, (a1) ... dbra d0, loop
# The counter value tells us the size
# In the SoundDriverLoad, find the counter setup
for insn in md.disasm(rom[0x11B8:0x1352], 0x11B8):
    if 'moveq' in insn.mnemonic or ('move' in insn.mnemonic and '#' in insn.op_str):
        if insn.address < 0x1250:
            line = f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}"
            if any(x in insn.op_str for x in ['d1', 'd2', 'd3', 'd7']):
                print(line)

# Disassemble the Z80 driver using a simple Z80 disassembler
print("\n--- Z80 Driver Disassembly (first instructions) ---")
try:
    z80_md = Cs(3, 0)  # CS_ARCH_SYSZ? Let's try...
    print("  (Capstone Z80 mode not available, using manual decode)")
except:
    print("  (Using manual Z80 decode)")

# Manual Z80 decode for key instructions
z80_opcodes = {
    0x00: "NOP", 0x76: "HALT", 0xF3: "DI", 0xFB: "EI",
    0xC3: "JP nn", 0xCD: "CALL nn", 0xC9: "RET",
    0x3E: "LD A,n", 0x06: "LD B,n", 0x0E: "LD C,n",
    0x16: "LD D,n", 0x1E: "LD E,n", 0x26: "LD H,n", 0x2E: "LD L,n",
    0x21: "LD HL,nn", 0x31: "LD SP,nn", 0x11: "LD DE,nn", 0x01: "LD BC,nn",
    0xD3: "OUT (n),A", 0xDB: "IN A,(n)",
    0x32: "LD (nn),A", 0x3A: "LD A,(nn)",
    0x77: "LD (HL),A", 0x7E: "LD A,(HL)",
    0xAF: "XOR A", 0xB7: "OR A", 0xFE: "CP n",
    0x18: "JR n", 0x20: "JR NZ,n", 0x28: "JR Z,n",
    0xC2: "JP NZ,nn", 0xCA: "JP Z,nn",
}

if 'z80_code_start' in dir():
    addr = z80_code_start
    z80_data = rom[addr:addr+256]
    pos = 0
    lines_printed = 0
    while pos < len(z80_data) and lines_printed < 40:
        b = z80_data[pos]
        z80_addr = pos  # Z80 address (starts at 0)
        
        if b == 0xED and pos+1 < len(z80_data):
            b2 = z80_data[pos+1]
            ed_ops = {0x56: "IM 1", 0x46: "IM 0", 0x5E: "IM 2", 
                      0x47: "LD I,A", 0x57: "LD A,I", 0x4F: "LD R,A",
                      0xB0: "LDIR", 0xB8: "LDDR"}
            op = ed_ops.get(b2, f"ED {b2:02X}")
            print(f"  Z80 ${z80_addr:04X}: ED {b2:02X}      {op}")
            pos += 2
        elif b in [0xC3, 0xCD, 0xC2, 0xCA, 0x21, 0x31, 0x11, 0x01, 0x32, 0x3A]:
            if pos+2 < len(z80_data):
                lo = z80_data[pos+1]
                hi = z80_data[pos+2]
                nn = (hi << 8) | lo
                op = z80_opcodes.get(b, f"??? {b:02X}")
                print(f"  Z80 ${z80_addr:04X}: {b:02X} {lo:02X} {hi:02X}  {op.replace('nn', f'${nn:04X}')}")
                pos += 3
            else:
                break
        elif b in [0x3E, 0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0xD3, 0xDB, 0xFE]:
            if pos+1 < len(z80_data):
                n = z80_data[pos+1]
                op = z80_opcodes.get(b, f"??? {b:02X}")
                print(f"  Z80 ${z80_addr:04X}: {b:02X} {n:02X}     {op.replace('n', f'${n:02X}')}")
                pos += 2
            else:
                break
        elif b in [0x18, 0x20, 0x28]:
            if pos+1 < len(z80_data):
                n = z80_data[pos+1]
                rel = n if n < 128 else n - 256
                target = pos + 2 + rel
                op = z80_opcodes.get(b, f"??? {b:02X}")
                print(f"  Z80 ${z80_addr:04X}: {b:02X} {n:02X}     {op.replace('n', f'${target:04X}')}")
                pos += 2
            else:
                break
        else:
            op = z80_opcodes.get(b, f"DB ${b:02X}")
            print(f"  Z80 ${z80_addr:04X}: {b:02X}        {op}")
            pos += 1
        lines_printed += 1

# =====================================================================
# 3. NEMESIS TILESET CATALOG
# =====================================================================
print("\n" + "=" * 70)
print("3. NEMESIS-COMPRESSED ART CATALOG")
print("=" * 70)

# In Sonic 1, NemDec is called with a0 = pointer to compressed data
# Let's find all references to NemDec/NemDec_Full to catalog all tilesets
# NemDec at $1440, NemDec_Full (with output addr) references

# Pattern: lea $XXXXXX, a0 followed by bsr NemDec
# The lea.l pattern is: 41 F9 XX XX XX XX
# Followed by bsr.w NemDec ($1440 or nearby)

nemesis_refs = []
for i in range(0, min(len(rom)-10, 0x50000)):
    # lea.l $XXXXXX, a0 = 41 F9 XX XX XX XX
    if rom[i] == 0x41 and rom[i+1] == 0xF9:
        art_addr = read_long(i+2)
        # Check if next instruction is bsr to NemDec area ($1440-$1460)
        next_insn = i + 6
        if rom[next_insn] == 0x61 and rom[next_insn+1] == 0x00:  # bsr.w
            disp = read_sword(next_insn+2)
            target = next_insn + 2 + disp
            if 0x1430 <= target <= 0x1470:
                nemesis_refs.append((i, art_addr, 'NemDec'))
        # Also check for NemDec_Full calls
        if next_insn + 4 < len(rom):
            if rom[next_insn] == 0x61 and rom[next_insn+1] == 0x00:
                disp = read_sword(next_insn+2)
                target = next_insn + 2 + disp
                if 0x1700 <= target <= 0x1730:
                    nemesis_refs.append((i, art_addr, 'NemDec_Full'))

print(f"\nFound {len(nemesis_refs)} Nemesis art references:")
# Remove duplicates by art_addr
seen = set()
unique_arts = []
for code_addr, art_addr, func in nemesis_refs:
    if art_addr not in seen and 0 < art_addr < len(rom):
        seen.add(art_addr)
        unique_arts.append((code_addr, art_addr, func))

# For each art block, read Nemesis header to get tile count
print(f"Unique art blocks: {len(unique_arts)}")
print(f"\n{'Art Addr':>10} | {'Code Ref':>10} | {'Type':>12} | {'Header Word':>12} | {'Tiles':>6}")
print("-" * 65)
for code_addr, art_addr, func in sorted(unique_arts, key=lambda x: x[1]):
    if art_addr < len(rom) - 2:
        header = read_word(art_addr)
        # Nemesis header: bit 15 = XOR mode, bits 14-0 = number of tiles
        xor_mode = (header >> 15) & 1
        num_tiles = header & 0x7FFF
        mode = "XOR" if xor_mode else "Normal"
        print(f"  ${art_addr:06X}  |  ${code_addr:06X}  | {func:>12} | ${header:04X} ({mode:>6}) | {num_tiles:>5}")

# =====================================================================
# 4. CHECK FOR SPLATS AND GOGGLES ART
# =====================================================================
print("\n" + "=" * 70)
print("4. UNUSED OBJECT ART CHECK (Splats, Goggles)")
print("=" * 70)

# Object $08 (Splats) handler at $0142F0
# Object $09 (Goggles) handler at $01B984
# Let's check if these are real code or stubs

print("\n--- Object $08 handler at $0142F0 ---")
code08 = rom[0x142F0:0x14310]
for insn in md.disasm(code08, 0x142F0):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")
    if insn.mnemonic == 'rts':
        break

print("\n--- Object $09 handler at $01B984 ---")
code09 = rom[0x1B984:0x1B9A0]
for insn in md.disasm(code09, 0x1B984):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")
    if insn.mnemonic == 'rts':
        break

# =====================================================================
# 5. DEMO PLAYBACK DATA
# =====================================================================
print("\n" + "=" * 70)
print("5. DEMO PLAYBACK DATA")
print("=" * 70)

# Demo data pointers are typically stored in a table
# Title screen loads demo data based on demo counter
# Search for the demo pointer table
# In Sonic 1, demos are indexed by a counter at $F602 or similar
# Demo data format: pairs of bytes (joypad_state, duration)

# The demo data is loaded at $308A: lea $3F09A, a0 then KosDec
# So demo data might be Kosinski-compressed at $3F09A
print("\n--- Demo data source ---")
print(f"  Demo data loaded from $3F09A (Kosinski compressed)")
print(f"  Decompressed to $FF0000")

# Let's check the demo index table
# At $30A2-$30B6 area, the camera/scroll setup
# Demo index is typically at a fixed address
# Let's look for demo-related data tables

# Search for GHZ Act 1 level ID ($0000) near demo setup
# The demo counter increments and wraps at 4
# Demo 0 = GHZ1, Demo 1 = MZ1, Demo 2 = SYZ1, Demo 3 = SS1

# Find demo pointer table by looking at title screen code
# At $3082: lea $3F09A, a0 ... bsr KosDec
# The decompressed data at FF0000 contains the actual input recordings
# Let's look at the Kosinski header at $3F09A
kosinski_addr = 0x3F09A
print(f"\n--- Kosinski data at ${kosinski_addr:06X} ---")
print(f"  First 32 bytes: {' '.join(f'{rom[kosinski_addr+i]:02X}' for i in range(32))}")

# Check demo selection table
# Demo level IDs: search for the demo level table
# Typically stored near the title screen code
# At around $3340-$3380
print("\n--- Demo Level Table ---")
for addr in range(0x3340, 0x33A0, 2):
    val = read_word(addr)
    if val < 0x0700:  # valid level ID range
        print(f"  ${addr:06X}: Level ID ${val:04X} = Zone {val >> 8}, Act {val & 0xFF}")

# =====================================================================
# 6. TIME BONUS TABLE
# =====================================================================
print("\n" + "=" * 70)
print("6. TIME BONUS TABLE (Score Tally)")
print("=" * 70)

# Score tally is in GotThroughAct or similar function
# The time bonus table maps time ranges to bonus values
# Search for known bonus values: 50000 = $C350, 10000 = $2710
bonus_50000 = struct.pack('>H', 0xC350)  # or as BCD
# In Sonic 1, scores are often stored in BCD
# 50000 in BCD = $50000 (but stored differently)
# Actually in Sonic 1, the time bonus table uses word values
# Let's search for the pattern: descending bonus values

# Known table from s1disasm:
# TimeBonuses:
#   dc.w 5000, 5000 ; 0:00-0:29
#   dc.w 1000, 1000 ; etc
# Wait - scores are in units of 10 (since score ends in 0)
# So 50000 = stored as 5000 (x10), 10000 = 1000 (x10)

# Search for 5000 ($1388) followed by descending values
target_5000 = struct.pack('>H', 5000)
pos = 0
while True:
    p = rom.find(target_5000, pos, 0x20000)
    if p == -1:
        break
    # Check if following words are descending (1000, 500, 400, etc)
    w1 = read_word(p)
    w2 = read_word(p+2)
    w3 = read_word(p+4)
    if w1 == 5000 and w2 >= 100 and w3 >= 50:
        print(f"  Potential time bonus table at ${p:06X}:")
        for i in range(12):
            val = read_word(p + i*2)
            print(f"    ${p+i*2:06X}: {val:5d} (x10 = {val*10:6d} points)")
        break
    pos = p + 1

# Alternative: search for BCD values
# In Sonic 1 scoring, the actual scores might be BCD
# Let's try 50000 as BCD: 0x0005, 0x0000 (split across bytes)
# Or the table might use small multipliers
# Let's search around GotThroughAct function area
# GotThroughAct is likely around $3E48 based on common s1 layout
print("\n--- Searching in GotThroughAct area ---")
# Search for the classic Sonic 1 time bonus table pattern
# From s1disasm: the table is pairs (time_threshold, bonus)
# Format: word time_in_seconds_BCD, word bonus_x10
for search_addr in range(0x3400, 0x4000, 2):
    # Look for a sequence that starts with small numbers (time) and big numbers (bonus)
    vals = [read_word(search_addr + i*2) for i in range(8)]
    # Check if this looks like: 29 (time), 5000 (bonus), 44, 1000, 59, 500...
    if vals[0] < 100 and vals[1] > 400 and vals[2] < 200 and vals[3] > 100:
        if vals[1] > vals[3]:  # descending bonuses
            print(f"  Potential table at ${search_addr:06X}: {vals}")

# =====================================================================
# 7. PALETTE CYCLE TABLES
# =====================================================================
print("\n" + "=" * 70)
print("7. PALETTE CYCLE TABLES (per zone)")
print("=" * 70)

# AnimateLevelGfx at $4962 handles palette cycling
# PalCycle tables are zone-specific, accessed via level ID
# The main palette cycle handler is at around $195C (PalCycle_Underwater)
# and the GHZ waterfall cycle, etc.

# In Sonic 1, palette cycling is done by PalCycle_<Zone> functions
# Let's find all PalCycle functions by searching for the pattern
# that writes to palette RAM ($FB00 area)

print("\n--- PalCycle function addresses ---")
# Known palette cycle addresses from s1disasm:
palcycle_addrs = {
    0x195C: "PalCycle_Underwater (LZ)",
    0x1992: "PalCycle_GHZ",  # might be slightly different
}

# Let's search for palette writes pattern: move.w Xx, $FBxx
# Pattern: 31 FC XX XX FB XX (move.w #imm, $FBxx.w)
# Or: 33 C0 00 00 FB XX (move.w d0, $00FBxx.l)
print("  Searching for palette RAM ($FB00-$FB7F) write patterns...")
fb_writes = set()
for i in range(0x1900, 0x2000):
    if rom[i:i+2] == b'\xFB\x00' or rom[i:i+2] == b'\xFB\x20' or rom[i:i+2] == b'\xFB\x40':
        fb_writes.add(i)

for addr in sorted(fb_writes)[:10]:
    context = rom[max(0,addr-6):addr+8]
    print(f"  ${addr:06X}: ...{context.hex()}...")

# Actually, let's just disassemble the AnimateLevelGfx area more carefully
# and the PalCycle handlers
print("\n--- PalCycle_GHZ/MZ/SYZ/SLZ/SBZ ---")
# These are indexed by zone in a jump table
# In Sonic 1, the palette cycle for each zone is handled by 
# different code paths within AnimateLevelGfx ($4962)
# The function reads the current zone and routes to the right handler

# Let's look at $1992 onwards for the other palette cycle functions
pal_code = rom[0x1992:0x1A80]
print("  Palette cycle code at $1992:")
for insn in md.disasm(pal_code, 0x1992):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")
    if insn.address > 0x1A40:
        break

# =====================================================================
# 8. TMSS VERIFICATION
# =====================================================================
print("\n" + "=" * 70)
print("8. TMSS (Trademark Security System)")
print("=" * 70)

# TMSS write at start of ROM init
# Search for $A14000 reference
tmss_pattern = b'\x00\xA1\x40\x00'
pos = rom.find(tmss_pattern)
if pos:
    print(f"  TMSS register ($A14000) referenced at ROM ${pos-2:06X}")
    # Show the instruction
    context = rom[pos-6:pos+8]
    for insn in md.disasm(context, pos-6):
        print(f"    {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# SEGA string check
sega_pattern = b'\x53\x45\x47\x41'  # "SEGA"
pos = 0
sega_refs = []
while True:
    p = rom.find(sega_pattern, pos, 0x400)
    if p == -1:
        break
    sega_refs.append(p)
    pos = p + 1
print(f"\n  'SEGA' ($53454741) found at offsets: {[f'${x:04X}' for x in sega_refs]}")

# Check VDP model detection (for TMSS requirement)
# Model 1 vs Model 2 detection via $A10001
print("\n  TMSS write mechanism:")
print("    1. Read $A10001 to detect console version")
print("    2. If version >= Model 2: write 'SEGA' to $A14000")
print("    3. Without this, VDP remains locked on Model 2+ hardware")

# =====================================================================
# 9. OBJECT MAPPING TABLE - ALL ENTRIES
# =====================================================================
print("\n" + "=" * 70)
print("9. COMPLETE OBJECT HANDLER TABLE ($D37E)")
print("=" * 70)

table_base = 0xD37E
# In Sonic 1, there are about $88 objects (max ID in jump table)
print(f"{'ObjID':>6} | {'Handler':>10} | {'Status'}")
print("-" * 40)
for obj_id in range(0x80):
    offset = table_base + obj_id * 4
    if offset + 4 > len(rom):
        break
    ptr = read_long(offset)
    if ptr > 0x80000 or ptr == 0:
        break
    
    # Check if handler is just RTS ($4E75)
    if ptr < len(rom) - 2:
        first_word = read_word(ptr)
        if first_word == 0x4E75:
            status = "STUB (rts)"
        elif first_word == 0x6000 or first_word == 0x4EF9:
            # bra or jmp - redirect
            status = "redirect"
        else:
            status = "active"
    else:
        status = "OUT_OF_RANGE"
    
    print(f"  ${obj_id:02X}   |  ${ptr:06X}  | {status}")

print("\n\nAnalysis complete!")
