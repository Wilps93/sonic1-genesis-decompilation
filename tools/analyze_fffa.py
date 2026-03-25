#!/usr/bin/env python3
"""Trace FFFA flag writes and Sound Test cheat mechanism"""
import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000

ROM_PATH = r'C:\Users\Dokuchaev_ts\Downloads\Sonic The Hedgehog (USA, Europe)\Sonic The Hedgehog (USA, Europe).gen'
rom = open(ROM_PATH, 'rb').read()
md = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
md.detail = False

def disasm_range(start, end, highlight=None):
    for insn in md.disasm(rom[start:end], start):
        marker = ' <<<' if highlight and insn.address == highlight else ''
        print(f'  ${insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}{marker}')

# ============================================================
# 1. Find ALL references to $FFFA
# ============================================================
print("=" * 60)
print("SECTION 1: ALL REFERENCES TO $FFFA")
print("=" * 60)

# Search for $FFFA in instruction operands
# In M68K encoding, $FFFA.w can appear as 0xFFFA in the instruction stream
# But also need absolute short addressing format
# tst.w $FFFA.w = 4A79 0000 FFFA (absolute long) or 4A78 FFFA (absolute short)

# Search for FFFA pattern
hits = []
for i in range(0, len(rom) - 2, 2):
    w = struct.unpack('>H', rom[i:i+2])[0]
    if w == 0xFFFA:
        # Check if previous instruction references this as address
        hits.append(i)

# Filter to meaningful hits - disassemble around each
print(f"\nFound {len(hits)} occurrences of $FFFA bytes")
print("\nDisassembling context for each valid reference:")
seen_addrs = set()
for hit in hits:
    # Disassemble from a bit before to find the instruction using FFFA
    start = max(0, hit - 8)
    start = start & ~1  # align to word
    found = False
    for insn in md.disasm(rom[start:hit+8], start):
        if 'fffa' in insn.op_str.lower() and insn.address not in seen_addrs:
            seen_addrs.add(insn.address)
            found = True
            # Determine operation type
            op_type = "READ" if insn.mnemonic.startswith('tst') or insn.mnemonic.startswith('cmp') or insn.mnemonic.startswith('btst') else "WRITE" if insn.mnemonic.startswith('move') or insn.mnemonic.startswith('clr') or insn.mnemonic.startswith('set') or insn.mnemonic.startswith('bset') or insn.mnemonic.startswith('bclr') else "OTHER"
            print(f"\n  [{op_type}] ${insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")
            # Show context
            ctx_start = max(0, insn.address - 16) & ~1
            ctx_end = min(len(rom), insn.address + 24)
            print("  Context:")
            for ci in md.disasm(rom[ctx_start:ctx_end], ctx_start):
                m = " <<<" if ci.address == insn.address else ""
                print(f"    ${ci.address:06X}  {ci.mnemonic:10s} {ci.op_str}{m}")

# ============================================================
# 2. Level Select Sound Test screen code
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: LEVEL SELECT / SOUND TEST CODE")
print("=" * 60)

# The level select is Game Mode $0C (value 12)
# Title screen is mode $00 or similar
# Look for the Level Select code - it's around $3990
print("\n--- Level Select code (around $3990) ---")
disasm_range(0x3990, 0x3AF0)

# The cheat check probably happens at the title screen
# Title screen = Game Mode $00
# Look at the title screen code more carefully
print("\n--- Title screen cheat check area ---")
# The cheat check is known to be around $3250-$3360
disasm_range(0x3240, 0x33E0)

# ============================================================
# 3. Sound Test cheat: checking $FFE0 / $FFE4 
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: CHEAT VARIABLES FFE0/FFE4/FFE6")
print("=" * 60)

# These are the cheat status variables
for var_name, var_addr in [("FFE0", 0xFFE0), ("FFE4", 0xFFE4), ("FFE6", 0xFFE6)]:
    print(f"\n--- References to ${var_name} ---")
    hits = []
    for i in range(0, len(rom) - 2, 2):
        w = struct.unpack('>H', rom[i:i+2])[0]
        if w == var_addr:
            hits.append(i)
    
    seen = set()
    for hit in hits:
        start = max(0, hit - 8) & ~1
        for insn in md.disasm(rom[start:hit+8], start):
            if f'{var_addr:04x}' in insn.op_str.lower() and insn.address not in seen:
                seen.add(insn.address)
                op_type = "WRITE" if any(insn.mnemonic.startswith(x) for x in ['move', 'clr', 'set', 'bset', 'bclr', 'add', 'sub', 'or', 'and', 'eor']) else "READ"
                print(f"  [{op_type}] ${insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# ============================================================ 
# 4. Demo data format
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: DEMO DATA FORMAT")
print("=" * 60)

# Demo pointer table - these point to decompressed data locations
# But wait - these point to ROM addresses, not RAM
# $42AC, $432C, $445C, $44DC - these are in ROM
# So demo data might NOT be Kosinski compressed after all
# Let's look at the actual demo data

print("\nDemo 0 (GHZ) data at $42AC (first 64 bytes):")
data = rom[0x42AC:0x42AC+64]
print(f"  {' '.join(f'{b:02X}' for b in data[:32])}")
print(f"  {' '.join(f'{b:02X}' for b in data[32:64])}")

# Demo data format: pairs of (duration, joypad_input)
# Each byte pair: first byte = joypad state, second byte = duration in frames
print("\nDecoding demo 0 as (joypad_state, duration) pairs:")
pos = 0
total_frames = 0
while pos < 128 and 0x42AC + pos < len(rom):
    jp = rom[0x42AC + pos]
    dur = rom[0x42AC + pos + 1]
    if jp == 0xFF:
        print(f"  END marker at offset {pos}")
        break
    
    # Decode joypad bits
    buttons = []
    if jp & 0x01: buttons.append("Up")
    if jp & 0x02: buttons.append("Down")
    if jp & 0x04: buttons.append("Left")
    if jp & 0x08: buttons.append("Right")
    if jp & 0x10: buttons.append("B")
    if jp & 0x20: buttons.append("C")
    if jp & 0x40: buttons.append("A")
    if jp & 0x80: buttons.append("Start")
    btn_str = "+".join(buttons) if buttons else "None"
    
    print(f"  [{pos:3d}] Joypad=${jp:02X} ({btn_str:20s}) for {dur} frames ({dur/60:.1f}s)")
    total_frames += dur
    pos += 2

print(f"\n  Total: {total_frames} frames ({total_frames/60:.1f}s)")

# Demo 1
print("\nDemo 1 (MZ) data at $432C (first 32 bytes):")
data = rom[0x432C:0x432C+32]
print(f"  {' '.join(f'{b:02X}' for b in data)}")

# ============================================================
# 5. Check what $FFFA actually is - it may be "level select enabled" flag
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: EXAMINING ROM HEADER AND REVISION")
print("=" * 60)

# ROM header
print(f"\nROM name: {rom[0x120:0x150].decode('ascii', errors='replace').strip()}")
print(f"ROM domestic: {rom[0x150:0x180].decode('ascii', errors='replace').strip()}")
print(f"ROM version: {rom[0x180:0x190].decode('ascii', errors='replace').strip()}")
print(f"Build date: {rom[0x118:0x120].decode('ascii', errors='replace').strip()}")
print(f"Serial: {rom[0x180:0x18E].decode('ascii', errors='replace').strip()}")

# Check if this is Rev00 or Rev01
# The version byte is typically at offset $18C or in the serial
serial = rom[0x183:0x18F].decode('ascii', errors='replace').strip()
print(f"\nSerial/version string: {serial}")
print(f"Byte at $18C (revision): ${rom[0x18C]:02X}")
print(f"Byte at $18D: ${rom[0x18D]:02X}")

# Checksum
checksum_stored = struct.unpack('>H', rom[0x18E:0x190])[0]
print(f"\nStored checksum: ${checksum_stored:04X}")

# Calculate checksum
calc_sum = 0
for i in range(0x200, len(rom), 2):
    calc_sum = (calc_sum + struct.unpack('>H', rom[i:i+2])[0]) & 0xFFFF
print(f"Calculated checksum: ${calc_sum:04X}")
print(f"Checksums match: {checksum_stored == calc_sum}")

# ============================================================
# 6. The actual cheat entry mechanism at title screen
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: TITLE SCREEN CHEAT ENTRY (detailed)")
print("=" * 60)

# The title screen code handles joypad input and checks against cheat sequence
# Let's look more carefully at the title screen routines
# GM_Title is typically around $2F18 or so
# Sub-routines that handle Start button and cheat input

print("\n--- Title screen main loop area (around $2F18-$3080) ---")
disasm_range(0x2F18, 0x3100)
