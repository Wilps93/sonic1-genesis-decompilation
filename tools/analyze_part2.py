#!/usr/bin/env python3
"""Part 2 analysis: object table, Z80 driver, debug mode sequence, demo data."""

import struct
rom = open(r'C:\Users\Dokuchaev_ts\Downloads\Sonic The Hedgehog (USA, Europe)\Sonic The Hedgehog (USA, Europe).gen', 'rb').read()

def rw(a): return struct.unpack('>H', rom[a:a+2])[0]
def rl(a): return struct.unpack('>I', rom[a:a+4])[0]

# ============================================================
# 1. OBJECT HANDLER TABLE
# ============================================================
print("=" * 70)
print("OBJECT HANDLER TABLE")
print("=" * 70)
base = 0xD37E
# The table is indexed: id * 4, each entry is a longword pointer
# But wait -- ExecuteObjects at $D338 uses: movea.l $D37E(pc, d0.w), a1
# However, the actual table may not be at $D37E in ROM because
# this is running from ROM, not RAM. Let's verify.
# At $D350: movea.l $d37e(pc, d0.w), a1
# PC = $D350 + 2 = $D352, offset to table = $D37E - $D352 = $2C
# So the actual opcode at $D350 should reference offset $2C
# Let's check: instruction at $D350 is: 22 7B 00 2C = movea.l (pc, d0.w, $2C), a1
# Table is at $D350 + 2 + $2C = $D37E. OK confirmed.

for obj_id in range(0x80):
    offset = base + obj_id * 4
    if offset + 4 > len(rom):
        break
    ptr = rl(offset)
    if ptr == 0 or ptr > 0x80000:
        print(f"  LAST VALID: Obj ${obj_id-1:02X}")
        break
    # Check stub
    if ptr < len(rom) - 2:
        w = rw(ptr)
        status = "STUB" if w == 0x4E75 else "ACTIVE"
    else:
        status = "OOB"
    print(f"  Obj ${obj_id:02X} -> ${ptr:06X} [{status}]")

# ============================================================
# 2. Z80 SOUND DRIVER
# ============================================================
print("\n" + "=" * 70)
print("Z80 SOUND DRIVER")
print("=" * 70)

# The Z80 driver in Sonic 1 is loaded by the SoundDriverLoad routine
# In the US/EU ROM, this function is at around $135C
# Let's find the Z80 driver data location

# The load function copies data to Z80 RAM ($A00000-$A01FFF)
# Let's find the code that does the copy
# Pattern: move.b (a0)+, $A00000(a1) or similar
# Or: write to $A00000.l

# Let's look at the function at $135C more carefully
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
md = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
md.detail = False

print("\n--- Code at $1352 (SoundDriverLoad area) ---")
for insn in md.disasm(rom[0x1352:0x13A0], 0x1352):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# Now look at what's referenced - the copy loop
print("\n--- Copy loop area ---")
for insn in md.disasm(rom[0x1352:0x13FF], 0x1352):
    s = f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}"
    if 'a0' in insn.op_str or 'a11' in insn.op_str or 'dbra' in insn.mnemonic:
        print(s)

# The Z80 driver data - search for DI (F3) at potential Z80 code locations
# Z80 code in Sonic 1 is typically around $E72-$F80
print("\n--- Searching for Z80 code data ---")
# Standard SMPS Z80 driver starts with:
# F3       DI
# ED 56    IM 1
# or F3 31 xx xx (DI; LD SP, xxxx)
for addr in range(0xE00, 0x1400):
    if rom[addr] == 0xF3:
        b1 = rom[addr+1]
        b2 = rom[addr+2] if addr+2 < len(rom) else 0
        if b1 == 0xED and b2 == 0x56:  # DI; IM 1
            print(f"  Z80 signature DI+IM1 at ROM ${addr:06X}")
            # Check if this matches typical SMPS driver
            print(f"  Context: {' '.join(f'{rom[addr+i]:02X}' for i in range(32))}")
        elif b1 == 0x31:  # DI; LD SP,nn
            nn = rom[addr+2] | (rom[addr+3] << 8)
            print(f"  Z80 signature DI+LD SP,${nn:04X} at ROM ${addr:06X}")
            print(f"  Context: {' '.join(f'{rom[addr+i]:02X}' for i in range(32))}")

# Try broader search
for addr in range(0x0000, 0x2000):
    if rom[addr] == 0xF3 and addr+3 < len(rom):
        if rom[addr+1] == 0xED and rom[addr+2] == 0x56:
            print(f"  Z80 DI+IM1 at ${addr:06X}")
        if rom[addr+1] == 0x31:
            nn = rom[addr+2] | (rom[addr+3] << 8)
            if 0x1F00 <= nn <= 0x2000:
                print(f"  Z80 DI+LD SP,${nn:04X} at ${addr:06X} (plausible stack)")

# Actually, in Sonic 1 the Z80 code is loaded differently
# The SMPS driver data is at an address referenced by lea in the load routine
# Let's search for all lea instructions that point to $xxxx where the data contains Z80 opcodes
# The init code for Z80 is short - it's mainly the DAC driver
# Main SMPS Z80 code is typically after $60000 in the ROM for music data

print("\n--- Searching for SMPS music data pointers ---")
# Sound driver command area in the M68K side
# PlaySound at $139C typically writes to $F621 / $F622
for insn in md.disasm(rom[0x139C:0x13D0], 0x139C):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# ============================================================
# 3. DEBUG MODE SEQUENCE
# ============================================================
print("\n" + "=" * 70)
print("DEBUG MODE ACTIVATION CODE")
print("=" * 70)

# Refs to $FE08 found at $304E, $39FE, $3B04, $3E34
# $304E is in title screen - writes to $FE08
# $39FE is likely in Level Select screen
# Let's check what sets $FE08

print("\n--- Code around $304E (title screen, writes $FE08) ---")
for insn in md.disasm(rom[0x3044:0x3060], 0x3044):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

print("\n--- Code around $39FE (Level Select, checks $FE08) ---")
for insn in md.disasm(rom[0x39E0:0x3A20], 0x39E0):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# Find where $FE08 is SET (not just read)
# Pattern: move.b #xx, $FE08.w or move.w #xx, $FE08.w
print("\n--- All $FE08 writes ---")
fe08 = b'\xFE\x08'
for i in range(0, min(len(rom), 0x50000)):
    if rom[i:i+2] == fe08:
        # Check if this is a destination (move.x something, $FE08)
        # Opcode before: 11FC = move.b #imm, abs.w
        #                31FC = move.w #imm, abs.w
        #                4278 = clr.w abs.w
        #                4238 = clr.b abs.w
        if i >= 4:
            prev2 = rw(i-2)
            prev4 = rw(i-4)
            if prev2 in [0x4278, 0x4238]:  # clr
                print(f"  ${i-2:06X}: clr $FE08")
            elif prev4 in [0x11FC, 0x31FC]:  # move.x #imm, abs.w
                imm = rw(i-2)
                print(f"  ${i-4:06X}: move #${imm:04X}, $FE08")
            elif prev2 == 0x11C0 or prev2 == 0x31C0:  # move.x d0, abs.w
                print(f"  ${i-2:06X}: move.x d0, $FE08")

# The debug mode in Sonic 1 works via Sound Test:
# Player plays sounds in sequence and a counter tracks progress
# When all 8 sounds match, $FE08 is set
# The checking code is in the Level Select handler

print("\n--- Level Select Sound Test check code ---")
# Level Select is game mode $04 after level select activation
# Let's find sound test comparison
# At around $39E0-$3A40
for insn in md.disasm(rom[0x39C0:0x3A60], 0x39C0):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# ============================================================
# 4. DEMO PLAYBACK FORMAT
# ============================================================
print("\n" + "=" * 70)
print("DEMO DATA DETAILS")
print("=" * 70)

# Demo data source address from title screen: $3F09A (Kosinski compressed)
# The demo table with level IDs
# From previous output, level table at $337A:
# $337A: $0000 (GHZ1), $0001 (GHZ2), $0002 (GHZ3), ...
# But the demo pointer table that maps demo index -> input data
# is typically at the beginning of title screen code

# In Sonic 1, demo playback uses:
# - $F790 = pointer to current demo input data
# - $F792 = remaining duration for current input
# Format: byte joypad_state, byte duration
# $FF = end of demo

# Let's find the demo data pointer table
# It's usually referenced when setting up demo playback
# At $3070-$309E area of title screen code

print("Demo data is Kosinski-compressed at $3F09A")  
print("Decompressed to $FF0000 and $B000")
print()

# Check how big the Kosinski block is
# Kosinski format: descriptor bytes followed by data
# Let's just estimate size by finding the next recognizable data after $3F09A
kos_start = 0x3F09A
# Look for end pattern or next data block
for i in range(kos_start, min(kos_start + 0x2000, len(rom))):
    # Kosinski blocks end when decompression yields enough data
    pass

# Alternative: count bytes from $3F09A to next aligned block
# In Sonic 1, art data typically starts at known addresses
# The next block after $3F09A might be at $3F600 or similar
print(f"Kosinski data starts at ${kos_start:06X}")
print(f"ROM size: ${len(rom):06X}")
print(f"Data context: {' '.join(f'{rom[kos_start+i]:02X}' for i in range(64))}")

# ============================================================
# 5. EXTENDED TIME BONUS TABLE
# ============================================================
print("\n" + "=" * 70)
print("COMPLETE TIME BONUS TABLE at $ECF0")
print("=" * 70)

# Table at $ECF0: word values, bonus amounts (x10 for display)
# Need to also find the time threshold table
# In s1disasm, the bonus table is indexed by time brackets

# Let's read more context around $ECF0
addr = 0xECF0
print("Bonus values (read 20 words):")
for i in range(20):
    val = rw(addr + i*2)
    print(f"  ${addr+i*2:06X}: {val:5d} (= {val*10:6d} points)")

# Find the comparison code that indexes this table
print("\nCode that references this area:")
for insn in md.disasm(rom[0xECC0:0xED20], 0xECC0):
    print(f"  {insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# ============================================================
# 6. FULL LEVEL ID TABLE
# ============================================================
print("\n" + "=" * 70)
print("LEVEL SELECT ORDER TABLE at $337A")
print("=" * 70)

zones = {0:"GHZ", 1:"LZ", 2:"MZ", 3:"SLZ", 4:"SYZ", 5:"SBZ", 6:"FZ"}
addr = 0x337A
for i in range(20):
    val = rw(addr + i*2)
    zone = (val >> 8) & 0xFF
    act = val & 0xFF
    zname = zones.get(zone, f"Zone{zone}")
    print(f"  #{i:2d}: ${val:04X} = {zname} Act {act+1}")
    if zone == 5 and act == 2:
        break
