#!/usr/bin/env python3
"""Analyze title screen cheat check and Sound Test in Level Select"""
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
# 1. Title screen cheat check continuation
# ============================================================
print("=" * 60)
print("SECTION 1: TITLE SCREEN CHEAT CHECK ($3100-$3260)")
print("=" * 60)

disasm_range(0x3100, 0x3270)

# ============================================================
# 2. Level Select Sound Test - the user interface
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: LEVEL SELECT SOUND TEST UI ($3950-$39A0)")
print("=" * 60)

# The Level Select already sets $FFFA=1 at $3990
# Let's see what happens when you're IN Level Select - the sound test
# The Level Select mode handler is further along
disasm_range(0x3950, 0x3990)

# And the Level Select main loop
print("\n--- Level Select main loop (after init, around $3AEC-$3C00) ---")
disasm_range(0x3AEC, 0x3C00)

# ============================================================
# 3. Check if there's a Sound Test cheat that sets additional flags
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: SOUND TEST CHEAT CHECK IN LEVEL SELECT")
print("=" * 60)

# In Sonic 1 Rev01+ the Sound Test cheat checks played sounds
# In Rev00, let's see if there's anything similar
# Look for cmpi.b with values like #$01, #$09 etc near Level Select code
disasm_range(0x3C00, 0x3E00)

# ============================================================
# 4. Object catalog - verify all 99 objects status
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: OBJECT STATUS CHECK (stub vs active)")
print("=" * 60)

# Read the object table we extracted
obj_table_base = 0xD382  # Obj $01 starts here (skip Obj $00's slot which is -$16 before table)
# Actually from analysis: Obj $00 doesn't exist, table at $D37E is indexed by ID*4
# So Obj $01 = $D37E + 4 = $D382

# Let's check which objects are stubs (point to $D5B2)
stub_addr = 0x00D5B2
print(f"\nStub address (ObjectFall/DeleteObject): ${stub_addr:06X}")
print("\n--- Stub check ---")
disasm_range(0xD5B2, 0xD5D0)  # What's at the stub address?

# Build the object table
obj_names = {
    0x01: "Sonic", 0x02: "Unused02", 0x03: "Unused03", 0x04: "Unused04",
    0x05: "Unused05", 0x06: "Unused06", 0x07: "Unused07",
    0x08: "Splats", 0x09: "ObjDebugMode/Goggles", 0x0A: "DrownCountdown",
    0x0B: "BreathBubbles", 0x0C: "SmallBubbles", 0x0D: "TitleSonic",
    0x0E: "TitleTMText", 0x0F: "TitlePressStart", 0x10: "TitleBG",
    0x11: "Bridge", 0x12: "SpinningLight", 0x13: "LavafallMakers",
    0x14: "Lavafall", 0x15: "SwingingPlatform", 0x16: "Helipad",
    0x17: "GHZPlatform", 0x18: "GHZEdgeWall", 0x19: "SBZPlatformsMoving",
    0x1A: "SBZCollapseLedge", 0x1B: "WaterSurface", 0x1C: "LabyrinthBlock",
    0x1D: "LabyrinthGargoyleHead", 0x1E: "ConveyorBelt",
    0x1F: "SYZSpikeball", 0x20: "SYZBumperBlock", 0x21: "EndSignpost",
    0x22: "Monitor", 0x23: "Explosion", 0x24: "Animal",
    0x25: "Points", 0x26: "RedSpring", 0x27: "GHZSpikes",
    0x28: "GHZRetractSpikes", 0x29: "Ring", 0x2A: "LostRings",
    0x2B: "EndBonusPoints", 0x2C: "WaterSound", 0x2D: "SpindashDust",
    0x2E: "Shield", 0x2F: "GameOver", 0x30: "Lamppost",
    0x31: "Signpost_SS", 0x32: "1Up", 0x33: "Invincibility",
    0x34: "GHZWaterfall", 0x35: "LZBlock", 0x36: "CorkFloor",
    0x37: "MZPlatform", 0x38: "SwirlBug", 0x39: "SBZDoor",
    0x3A: "SBZDefenseGrid", 0x3B: "BossExplosion", 0x3C: "MZCrumblingPlatform",
    0x3D: "GHZBoss", 0x3E: "SLZBoss", 0x3F: "Spikes",
    0x40: "HUD", 0x41: "GHZBlockComplex", 0x42: "GHZMasherEnemy",
    0x43: "GHZCrabmeat", 0x44: "GHZBuzzbomber", 0x45: "Ring_SS",
    0x46: "SSBumper", 0x47: "SSGoalSignpost", 0x48: "MZBoss",
    0x49: "SBZFlameShooter", 0x4A: "Roller", 0x4B: "SLZCannon",
    0x4C: "SYZCaterkiller", 0x4D: "Motobug", 0x4E: "BallHog",
    0x4F: "CrabmeatBomb", 0x50: "Orbinaut", 0x51: "LZTriton",
    0x52: "LZBatbot", 0x53: "SBZBall", 0x54: "SBZBasaran",
    0x55: "SBZJaws", 0x56: "SBZBurrobot", 0x57: "LZBoss",
    0x58: "SYZBoss", 0x59: "SLZBoss2", 0x5A: "SBZBoss",
    0x5B: "FZEggman", 0x5C: "FZPlasma", 0x5D: "CreditsText",
    0x5E: "CreditsObj", 0x5F: "ScrapBrainConveyorObj", 0x60: "EndingObj",
    0x61: "ContinueText", 0x62: "ContinueSonic", 0x63: "EndOfList"
}

print("\n--- Full Object Catalog ---")
for obj_id in range(1, 100):
    offset = 0xD37E + obj_id * 4
    if offset + 4 > len(rom):
        break
    addr = struct.unpack('>I', rom[offset:offset+4])[0]
    if addr >= 0x100000:
        break
    
    name = obj_names.get(obj_id, f"Unknown{obj_id:02X}")
    is_stub = (addr == stub_addr)
    status = "STUB (=> DeleteObject)" if is_stub else "ACTIVE"
    
    # For active objects, check first few instructions
    if not is_stub and addr < len(rom) - 8:
        first_bytes = rom[addr:addr+8]
        hex_first = ' '.join(f'{b:02X}' for b in first_bytes)
    else:
        hex_first = ""
    
    print(f"  Obj ${obj_id:02X} ({name:30s}): ${addr:06X} [{status}]  {hex_first}")

# ============================================================
# 5. Verify: does Rev00 have Sound Test debug cheat?
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: REV00 DEBUG MODE MECHANISM")
print("=" * 60)

print("""
ANALYSIS SUMMARY:
- ROM: Sonic The Hedgehog (USA, Europe) Rev00 (GM 00001009-00)
- Level Select cheat at title screen: Up, Down, Left, Right + A ($33A4)
- When Level Select is entered, $FFFA is set to 1 at $3990
- During gameplay, if $FFFA != 0 AND C button is pressed:
  -> $FE08 (debug mode) is set to 1
  -> This happens at $012C4C (Sonic object) and $01B9F2 (secondary check)
- The Sound Test cheat (01,09,09,01,00,06,02,03) does NOT exist in Rev00
- In Rev00, debug mode is activated by:
  1. Enter Level Select (Up+Down+Left+Right+A at title)
  2. Hold C when starting a level (C button = btst #4 of $F605)
- The 01,09,09,01,00,06,02,03 cheat was added in Rev01
""")

# ============================================================
# 6. Z80 driver full analysis
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Z80 SOUND DRIVER ANALYSIS")
print("=" * 60)

# The Z80 driver is Kosinski-compressed at $72E7C
# It's loaded by SoundDriverLoad at $1352
# Let's look at the load routine
print("\n--- SoundDriverLoad at $1352 ---")
disasm_range(0x1352, 0x1400)

# Z80 bus control ports
print("\n--- Z80 init sequence at $15DE ---")
disasm_range(0x15DE, 0x1650)

# The driver after decompression lives at $A00000 in Z80 address space
# Let's try to find the Kosinski decompressor and manually decompress
# Actually, let's just analyze what we can see about the Z80 driver
# The SMPS (Sample Music Playback System) driver

# Let's find the sound driver addresses/pointers
# Music pointer table, SFX pointer table
print("\n--- After SoundDriverLoad, check $138C for PlaySound ---")
disasm_range(0x138C, 0x13A8)

print("\n--- PlaySound/PlayMusic at $139C ---")
disasm_range(0x139C, 0x13DC)

# Sound command mechanism: M68K writes to Z80 RAM via $A00000 bus
# Let's check the sound command send routine
print("\n--- Sound command routine ---")
disasm_range(0x13A8, 0x1440)

# ============================================================
# 7. Palette cycle data per zone
# ============================================================
print("\n" + "=" * 60)
print("SECTION 7: PALETTE CYCLE DATA")
print("=" * 60)

# GHZ waterfall: code at $1992, data at $FB56/$FAD6
print("\n--- PalCycle code at $1992 ---")
disasm_range(0x1992, 0x1A60)

# Read palette data 
print(f"\nPalette data at $FB56: {' '.join(f'{rom[0x1992+i]:02X}' for i in range(16))}")

# ============================================================
# 8. Complete level layout pointer table
# ============================================================
print("\n" + "=" * 60) 
print("SECTION 8: LEVEL LAYOUT POINTERS")
print("=" * 60)

# Level data pointers are typically stored in tables
# The main level data table includes:
# - Layout pointer
# - Object layout pointer
# - Ring layout pointer
# - Art/palette pointers

# Let's find the main level header table
# It's usually around $42AC or accessed from the level init code
# Search for where $FE10 (level ID) is used to index into tables
print("\n--- Code that loads level data (around $4000) ---")
disasm_range(0x4000, 0x40C0)

print("\n--- Level art/palette pointer tables ---")
# There's usually a table of longword pointers
for tbl_name, tbl_addr in [("Level layout ptrs", 0x42AC), ("Normal demo ptrs", 0x4080), ("Special demo ptrs", 0x40A0)]:
    print(f"\n{tbl_name} at ${tbl_addr:06X}:")
    for i in range(8):
        val = struct.unpack('>I', rom[tbl_addr + i*4:tbl_addr + (i+1)*4])[0]
        print(f"  [{i}] ${val:06X}")
