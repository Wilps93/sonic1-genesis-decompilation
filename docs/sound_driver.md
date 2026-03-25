# Sonic 1 (Genesis/Mega Drive) — Sound Driver (SMPS)

> **ROM:** Sonic The Hedgehog (USA, Europe) Rev00 — GM 00001009-00  
> **Sound System:** SMPS (Sample Music Playback System) — Sega standard  
> **Driver Location:** ROM $72E7C (Kosinski-compressed) → Z80 RAM $A00000

---

## Architecture Overview

Unlike later Sega Genesis games where the Z80 runs the sound driver autonomously, Sonic 1's sound system is a **hybrid M68K/Z80** design:

| Component | Processor | Description |
|-----------|-----------|-------------|
| SMPS Driver | Z80 | Music/SFX playback, channel management |
| Sound Commands | M68K | Queue-based: M68K writes IDs, Z80 reads per frame |
| Bus Arbitration | M68K | M68K requests Z80 bus for communication |
| YM2612 (FM) | — | 6 FM synthesis channels |
| SN76489 (PSG) | — | 4 PSG channels (3 tone + 1 noise) via VDP |
| DAC | — | 1 PCM sample channel |

**Total channels:** 6 FM + 4 PSG + 1 DAC = **11 channels**

---

## Driver Loading

The SMPS driver is loaded during game initialization at `SoundDriverLoad` ($1352):

```m68k
; SoundDriverLoad ($1352)
$1354  move.w   #$100, $A11100.l    ; Request Z80 Bus
$135C  move.w   #$100, $A11200.l    ; Assert Z80 Reset
$1364  lea.l    $72E7C.l, a0        ; Source: ROM $72E7C (Kosinski compressed)
$136A  lea.l    $A00000.l, a1       ; Destination: Z80 RAM
$1370  bsr.w    $189C               ; KosDec — Kosinski decompression
$1374  move.w   #$0, $A11200.l      ; Release Z80 Reset (Z80 begins execution)
$138C  move.w   #$0, $A11100.l      ; Release Z80 Bus
```

### Z80 Initial Stub

A tiny Z80 bootstrap exists at ROM $02EA:

```z80
$02EA: F3        DI          ; Disable interrupts
$02EB: ED 56     IM 1        ; Set Interrupt Mode 1
```

After decompression, the full SMPS driver (~2.5 KB) runs from Z80 RAM address $0000.

---

## Sound Queues (M68K → Z80)

Communication between the M68K game code and Z80 sound driver uses three RAM queues. The M68K writes a sound ID; the Z80 reads and processes it on the next frame.

```m68k
; PlaySound_Special — Queue 1 ($1396)
$1396  move.b   d0, $F00A.w       ; Sound Queue 1

; PlaySound — Main Queue 2 ($139C)
$139C  move.b   d0, $F00B.w       ; Sound Queue 2

; PlaySound_2 — Queue 3 ($13A2)  
$13A2  move.b   d0, $F00C.w       ; Sound Queue 3
```

| RAM Address | Queue | Used By |
|-------------|-------|---------|
| `$F00A` | Queue 1 (Special) | Priority sounds, commands |
| `$F00B` | Queue 2 (Main) | Standard music & SFX |
| `$F00C` | Queue 3 | Additional SFX |

---

## Sound ID Ranges

| ID Range | Type | Description |
|----------|------|-------------|
| `$01–$7F` | — | Reserved / unused |
| `$80–$8F` | **Music** | Level themes, title, boss, etc. |
| `$90–$9F` | **Music** | Special Stage, invincibility, etc. |
| `$A0–$CF` | **SFX** | Sound effects (jump, ring, spring, etc.) |
| `$D0–$DF` | **SFX** | Additional sound effects |
| `$E0` | **Command** | Fade out |
| `$E1–$E4` | **Command** | Special music commands |
| `$E5+` | **Command** | Undocumented — reads beyond track table (potential OOB) |

### Sound Test

The Level Select Sound Test allows values `$00–$4F`:

```c
// LevelSelect Sound Test
d0 = $FF84.w;           // Sound test value: 0–$4F
d0 += #$80;             // Translate to PlaySound ID: $80–$CF
```

**Note:** The `PlaySound` and `PlaySound_Special` routines do NOT validate the sound ID. IDs beyond `$CF` are interpreted as **commands** by `SndDrv_CmdHandler`, not as music tracks.

---

## Channel Architecture

The sound driver processes channels sequentially each frame:

```m68k
; SoundDriver_Main — channel update loop
$71BD8  moveq   #$5, d7           ; 6 FM channels (0–5)
$71BDA  adda.w  #$30, a5          ; Each channel = $30 (48) bytes
$71BE2  jsr     SndDrv_UpdateFM   ; Update FM channels

$71BEA  moveq   #$2, d7           ; 3 PSG channels (0–2)
$71BEC  adda.w  #$30, a5
$71BF4  jsr     SndDrv_UpdatePSG  ; Update PSG channels
```

Each channel occupies **$30 (48) bytes** in the driver's RAM workspace at `$FFF000+`.

---

## Bus Arbitration

The M68K must claim the Z80 bus before accessing Z80 RAM:

```m68k
; SoundDriver_Main ($71B4C)
$71B4C  move.w  #$100, $A11100.l  ; Request Z80 bus
$71B5A  btst.b  #7, $A01FFD.l     ; Z80 ready?
$71B6C  beq.b   loc_71B82         ; Yes → proceed
$71B80  bra.b   SoundDriver_Main  ; No → retry (infinite loop!)
```

### Known Bug: Z80 Deadlock

If the Z80 hangs (hardware fault, bus conflict), the bus request loop at `$71B4C` has **no timeout**. The M68K will spin forever, completely freezing the game. This affects all revisions of Sonic 1.

---

## Hardware Registers

### YM2612 (FM Synthesizer)

| M68K Address | Description |
|-------------|-------------|
| `$A04000` | YM2612 Address Port (Part I) |
| `$A04001` | YM2612 Data Port (Part I) |
| `$A04002` | YM2612 Address Port (Part II) |
| `$A04003` | YM2612 Data Port (Part II) |

### SN76489 (PSG)

| Access | Description |
|--------|-------------|
| VDP Port `$C00011` | PSG write (directly through VDP) |

### Z80 Control

| M68K Address | Description |
|-------------|-------------|
| `$A11100` | Z80 Bus Request (write $100 = request, $000 = release) |
| `$A11200` | Z80 Reset (write $100 = assert, $000 = release) |
| `$A00000–$A01FFF` | Z80 RAM (8 KB, accessible when bus granted) |

---

## Music Track List

Based on Sound Test IDs ($80+):

| ID | Track |
|----|-------|
| `$81` | Green Hill Zone |
| `$82` | Labyrinth Zone |
| `$83` | Marble Zone |
| `$84` | Star Light Zone |
| `$85` | Spring Yard Zone |
| `$86` | Scrap Brain Zone |
| `$87` | Invincibility |
| `$88` | Extra Life |
| `$89` | Special Stage |
| `$8A` | Title Screen |
| `$8B` | Ending |
| `$8C` | Boss |
| `$8D` | Final Zone |
| `$8E` | Act Clear |
| `$8F` | Game Over |
| `$90` | Continue |
| `$91` | Credits |
| `$92` | Drowning |
| `$93` | Chaos Emerald |

---

## Kosinski Compression

The SMPS driver data at ROM `$72E7C` uses Kosinski compression (a Sega-proprietary LZ77 variant):

- **Compressed size:** Variable (stored in ROM)
- **Decompressed size:** ~2.5 KB
- **Decompressor:** `KosDec` at ROM $189C
- **Destination:** Z80 RAM $A00000 (= Z80 address $0000)

The decompression runs on the M68K while the Z80 is held in reset. After decompression completes, the Z80 is released and begins executing the driver code from address $0000.

---

*Generated from ROM analysis of Sonic The Hedgehog (USA, Europe) Rev00.*
