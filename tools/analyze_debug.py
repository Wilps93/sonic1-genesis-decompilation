#!/usr/bin/env python3
"""Analyze debug mode activation, Z80 init, object table, and demo data"""
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
# 1. Debug mode activation - two locations
# ============================================================
print("=" * 60)
print("SECTION 1: DEBUG MODE ACTIVATION")
print("=" * 60)

# Location 1: $12C4C - This is inside the Sound Test cheat check
print("\n--- Around $012C4C (Debug mode set #1) ---")
disasm_range(0x12C00, 0x12C80, highlight=0x12C4C)

print("\n--- Around $01B9F2 (Debug mode set #2) ---")
disasm_range(0x1B9C0, 0x1BA50, highlight=0x1B9F2)

# Let's find the Sound Test cheat comparison data
# The known cheat for debug mode is checking a sequence at the sound test
# Look at what code leads to $12C4C
print("\n--- Wider context around $012C00 ---")
disasm_range(0x12B80, 0x12C80)

# ============================================================
# 2. Level select cheat - $3364 area (title screen)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: LEVEL SELECT CHEAT SEQUENCE")
print("=" * 60)

# Cheat sequence at $33A4 (decoded as Up,Down,Left,Right)
# Let's look at the cheat checking code
print("\n--- Cheat check code around $3364 ---")
disasm_range(0x3360, 0x33D0)

# Show raw bytes of cheat sequence
print(f"\nCheat sequence at $33A4: {' '.join(f'{rom[0x33A4+i]:02X}' for i in range(16))}")
print(f"Cheat sequence at $33AA: {' '.join(f'{rom[0x33AA+i]:02X}' for i in range(16))}")

# ============================================================
# 3. Z80 driver init code at $02EA
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Z80 DRIVER INIT STUB")
print("=" * 60)

# The Z80 init stub at $02EA in ROM - this is what gets loaded first
data = rom[0x2EA:0x320]
print(f"\nRaw bytes at $02EA: {' '.join(f'{b:02X}' for b in data)}")

# Simple Z80 disassembly
z80ops = {0xF3:'DI', 0xFB:'EI', 0x00:'NOP', 0x76:'HALT', 0xC9:'RET', 0xAF:'XOR A',
           0xC7:'RST $00', 0xCF:'RST $08', 0xD7:'RST $10', 0xDF:'RST $18',
           0xE7:'RST $20', 0xEF:'RST $28', 0xF7:'RST $30', 0xFF:'RST $38',
           0x77:'LD (HL),A', 0x23:'INC HL', 0x2B:'DEC HL', 0x0B:'DEC BC',
           0x03:'INC BC', 0x13:'INC DE', 0x1B:'DEC DE', 0x78:'LD A,B',
           0x79:'LD A,C', 0xB1:'OR C', 0xB0:'OR B', 0xA9:'XOR C', 0xA8:'XOR B',
           0x10:'DJNZ'}

print("\nZ80 disassembly of init stub:")
pos = 0
while pos < len(data) and pos < 40:
    b = data[pos]
    addr = 0x2EA + pos
    if b == 0xED and pos+1 < len(data):
        b2 = data[pos+1]
        ed = {0x56:'IM 1', 0x46:'IM 0', 0x5E:'IM 2', 0x47:'LD I,A', 0x57:'LD A,I',
              0xB0:'LDIR', 0xB8:'LDDR'}
        print(f'  ${addr:04X}: ED {b2:02X}        {ed.get(b2, f"ED {b2:02X}")}')
        pos += 2
    elif b in [0xC3, 0x21, 0x31, 0x11, 0x01, 0x32, 0x3A, 0xCD, 0x22, 0x2A]:
        if pos+2 < len(data):
            nn = data[pos+1] | (data[pos+2] << 8)
            ops3 = {0xC3:'JP', 0x21:'LD HL,', 0x31:'LD SP,', 0x11:'LD DE,', 
                    0x01:'LD BC,', 0x32:'LD (nn),A', 0x3A:'LD A,(nn)', 0xCD:'CALL',
                    0x22:'LD (nn),HL', 0x2A:'LD HL,(nn)'}
            print(f'  ${addr:04X}: {b:02X} {data[pos+1]:02X} {data[pos+2]:02X}    {ops3[b]} ${nn:04X}')
            pos += 3
        else: break
    elif b == 0x10 and pos+1 < len(data):
        n = data[pos+1]
        rel = n if n < 128 else n - 256
        target = addr + 2 + rel
        print(f'  ${addr:04X}: {b:02X} {n:02X}       DJNZ ${target:04X}')
        pos += 2
    elif b in [0x3E, 0x06, 0x0E, 0x16, 0x1E, 0x26, 0x2E, 0xD3, 0xDB, 0xFE, 0xC6, 0xE6, 0xF6]:
        if pos+1 < len(data):
            n = data[pos+1]
            ops2 = {0x3E:'LD A,', 0x06:'LD B,', 0x0E:'LD C,', 0x16:'LD D,',
                    0x1E:'LD E,', 0x26:'LD H,', 0x2E:'LD L,', 0xD3:'OUT (n),A',
                    0xDB:'IN A,(n)', 0xFE:'CP', 0xC6:'ADD A,', 0xE6:'AND', 0xF6:'OR'}
            print(f'  ${addr:04X}: {b:02X} {n:02X}       {ops2[b]} ${n:02X}')
            pos += 2
        else: break
    elif b in [0x18, 0x20, 0x28, 0x30, 0x38]:
        if pos+1 < len(data):
            n = data[pos+1]
            rel = n if n < 128 else n - 256
            target = addr + 2 + rel
            jr = {0x18:'JR', 0x20:'JR NZ,', 0x28:'JR Z,', 0x30:'JR NC,', 0x38:'JR C,'}
            print(f'  ${addr:04X}: {b:02X} {n:02X}       {jr[b]} ${target:04X}')
            pos += 2
        else: break
    else:
        print(f'  ${addr:04X}: {b:02X}          {z80ops.get(b, f"DB ${b:02X}")}')
        pos += 1

# ============================================================
# 4. Object handler table - fixed
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: OBJECT HANDLER TABLE (from $D37E)")
print("=" * 60)

# The table at $D37E contains WORD offsets that get added to a base, or it's a jump table
# Let's look at how the object handler dispatches
# First, let's see the code that uses this table
print("\n--- Object handler dispatch code around $D340 ---")
disasm_range(0xD340, 0xD3A0)

# Now read the table as words (not longs)
print("\nObject handler table (reading as longword pointers):")
base = 0xD37E
# Actually, let's look at the pattern. If entries are longwords:
for i in range(100):
    offset = base + i * 4
    if offset + 4 > len(rom):
        break
    val = struct.unpack('>I', rom[offset:offset+4])[0]
    if val == 0 and i > 5:  # End marker
        print(f"  Obj ${i:02X}: $000000 (END)")
        break
    # Check if it looks like a valid ROM pointer
    if val < 0x100000:
        print(f"  Obj ${i:02X}: ${val:06X}")
    else:
        # Try as word entries instead
        pass

# Let's also try reading as word entries
print("\nTrying as word-sized entries from $D37E:")
for i in range(50):
    offset = base + i * 2
    val = struct.unpack('>H', rom[offset:offset+2])[0]
    print(f"  Entry {i:2d}: ${val:04X}")
    if val == 0 and i > 5:
        break

# ============================================================
# 5. Sound Test cheat in Level Select
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: SOUND TEST DEBUG CHEAT")
print("=" * 60)

# The debug mode cheat in Level Select is entered by playing sounds
# in a specific order in the Sound Test: 01, 09, 09, 01, 00, 06, 02, 03
# Let's find where this sequence is stored

# Search for the byte pattern 01 09 09 01 00 06 02 03
patterns = [
    bytes([0x01, 0x09, 0x09, 0x01, 0x00, 0x06, 0x02, 0x03]),
    bytes([0x00, 0x01, 0x00, 0x09, 0x00, 0x09, 0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x00, 0x02, 0x00, 0x03]),
]

print("\nSearching for Sound Test debug cheat sequence...")
for pidx, pat in enumerate(patterns):
    hex_pat = ' '.join(f'{b:02X}' for b in pat)
    print(f"\n  Pattern {pidx}: {hex_pat}")
    pos = 0
    while True:
        pos = rom.find(pat, pos)
        if pos == -1:
            break
        print(f"    Found at ${pos:06X}")
        # Show context
        ctx = rom[max(0,pos-8):pos+len(pat)+8]
        print(f"    Context: {' '.join(f'{b:02X}' for b in ctx)}")
        pos += 1

# Also search for the word-sized version used in cmpi.w comparisons
# The values 1,9,9,1,0,6,2,3 as words
print("\nSearching for word-sized sequence (00 01 00 09 00 09...)...")
word_pat = bytes([0x00, 0x01, 0x00, 0x09, 0x00, 0x09, 0x00, 0x01])
pos = 0
while True:
    pos = rom.find(word_pat, pos)
    if pos == -1:
        break
    print(f"  Found at ${pos:06X}")
    ctx = rom[pos:pos+24]
    print(f"  Full: {' '.join(f'{b:02X}' for b in ctx)}")
    pos += 1

# The cheat might be implemented as a series of cmpi.w #$xx, d0 instructions
# Search the code near $12C4C for cmp instructions
print("\n--- Full code analysis around debug mode activation ---")
print("--- Searching back from $012C4C for comparison chain ---")
disasm_range(0x12B00, 0x12C80)

# ============================================================
# 6. Demo data
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: DEMO PLAYBACK DATA")
print("=" * 60)

# Demo pointer table at $4080
print("\nDemo pointer table at $4080 (normal):")
for i in range(8):
    ptr = struct.unpack('>I', rom[0x4080 + i*4 : 0x4084 + i*4])[0]
    print(f"  Demo {i}: ${ptr:06X}")

print("\nDemo pointer table at $40A0 (special stage):")
for i in range(4):
    ptr = struct.unpack('>I', rom[0x40A0 + i*4 : 0x40A4 + i*4])[0]
    print(f"  Special Demo {i}: ${ptr:06X}")

# Demo data at $3F09A is Kosinski compressed
# Let's look at the raw Kosinski header
print(f"\nKosinski data header at $3F09A: {' '.join(f'{rom[0x3F09A+i]:02X}' for i in range(32))}")

# Demo timer
print(f"\nDemo timer value at $F614 loaded with: search for 0708 (1800 frames = 30 sec)")
# Search for move.w #$708 in code
for i in range(0, len(rom)-4, 2):
    if rom[i:i+4] == bytes([0x33, 0xFC, 0x07, 0x08]):  # move.w #$0708
        # Check if next bytes reference $F614
        ctx = rom[i:i+10]
        print(f"  move.w #$0708 at ${i:06X}: {' '.join(f'{b:02X}' for b in ctx)}")

# ============================================================
# 7. Unused objects/content scan
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: UNUSED / STUB OBJECTS SCAN")
print("=" * 60)

# Known unused objects from community: Splats ($08), Roller ($09 or different)
# Let's check a few more object slots
# Object handler uses the table at $D37E
# But first let's properly read it by looking at the dispatch code

# The ObjectLoad routine typically does:
#   move.b 0(a0),d0   ; get object ID
#   lsl.w #2,d0        ; multiply by 4 (longword table)
#   lea Obj_Index,a1   ; table address
#   movea.l (a1,d0.w),a1  ; get handler address
#   jmp (a1)           ; jump to it

# Let's check what Obj_Index points to
# Looking at the dispatch code at $D340+
print("\nSearching for object dispatch pattern (lea + movea.l + jmp)...")
for insn in md.disasm(rom[0xD340:0xD3E0], 0xD340):
    print(f"  ${insn.address:06X}  {insn.mnemonic:10s} {insn.op_str}")

# ============================================================
# 8. Kosinski decompressor analysis
# ============================================================
print("\n" + "=" * 60)
print("SECTION 8: KOSINSKI DECOMPRESSOR")
print("=" * 60)

# KosDec routine
# Search for the well-known Sonic 1 KosDec
# It usually starts around $1448 or similar
print("\n--- KosDec routine ---")
disasm_range(0x1448, 0x14E0)
