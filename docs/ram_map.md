# Sonic 1 (Genesis/Mega Drive) — RAM Map

> **ROM:** Sonic The Hedgehog (USA, Europe) Rev00 — GM 00001009-00  
> **Platform:** Sega Genesis / Mega Drive — Motorola 68000 @ 7.67 MHz  
> **RAM:** 64 KB ($FF0000–$FFFFFF, mirrored at $0000–$FFFF with short addressing)

---

## System Registers

| Address | Size | Description |
|---------|------|-------------|
| `$F600` | Word | **Game Mode** ($00=SEGA logo, $04=Title Screen, $08=Level Play, $0C=Special Stage Exit, $10=Special Stage, $14=Continue, $18=Ending, $1C=Credits) |
| `$F601` | Byte | Sound queue 1 (PlaySound_Special) |
| `$F602` | Word | Processed joypad state (overwritable!) |
| `$F604` | Word | Held joypad buttons |
| `$F605` | Byte | Newly pressed buttons (one-shot) |
| `$F609` | Byte | Sound queue 2 (PlaySound — main) |
| `$F60A` | Byte | Sound queue 3 (PlaySound_2) |
| `$F614` | Word | General countdown timer |
| `$F62A` | Word | VBlank routine ID |
| `$F632` | Word | Palette cycling offset |
| `$F646` | Word | Water surface Y position |

---

## Camera

| Address | Size | Description |
|---------|------|-------------|
| `$F700` | Word | Camera X position |
| `$F704` | Word | Camera Y position |
| `$F726` | Word | Saved Camera Y |
| `$F728` | Word | Camera left boundary |
| `$F72A` | Word | Camera right boundary |
| `$F72C` | Word | Saved Camera X |

---

## Physics

| Address | Size | Description |
|---------|------|-------------|
| `$F760` | Word | Max horizontal speed |
| `$F762` | Word | Acceleration |
| `$F764` | Word | Deceleration |
| `$F782` | Word | Rotation counter (Special Stage) |
| `$F7CC` | Word | Control Lock (1 = input disabled) |

---

## Demo Playback

| Address | Size | Description |
|---------|------|-------------|
| `$F790` | Word | Demo data read offset |
| `$F792` | Word | Demo frame countdown |

---

## Sound Driver (M68K-side)

| Address | Size | Description |
|---------|------|-------------|
| `$F00A` | Byte | Sound queue 1 — M68K writes, Z80 reads each frame |
| `$F00B` | Byte | Sound queue 2 (main) |
| `$F00C` | Byte | Sound queue 3 |

---

## Debug Mode

| Address | Size | Description |
|---------|------|-------------|
| `$FE08` | Word | **Debug Mode active flag** — checked in 22 places across ROM |
| `$FE06` | Word | Debug: selected object index |
| `$FE0A` | Word | Debug: acceleration timer |
| `$FE0B` | Word | Debug: current movement speed |

---

## Game State

| Address | Size | Description |
|---------|------|-------------|
| `$FE10` | Word | Current Zone ID (high byte = zone, low byte = act) |
| `$FE11` | Byte | Act number (0–3) |
| `$FE12` | Word | Lives count |
| `$FE1A` | Word | Continue available flag |
| `$FE1E` | Word | Timer update flag |
| `$FE20` | Word | Ring count |
| `$FE22` | Long | Internal time (minutes : seconds : frames) |
| `$FE26` | Long | Score |
| `$FE2D` | Word | Shield flag |
| `$FE30` | Word | Water level |
| `$FE57` | Word | Chaos Emerald count (0–6) |
| `$FE58+` | Array | Collected Emerald IDs |
| `$FFC0` | Long | Score threshold for extra life |
| `$FFF0` | Word | Play/Demo status ($8001 = demo mode) |
| `$FFF4` | Word | Continue counter (max 9) |
| `$FFFC` | Long | Warm boot marker ("init" = $696E6974) |

---

## Level Select

| Address | Size | Description |
|---------|------|-------------|
| `$FF80` | Word | Level Select: key repeat timer |
| `$FF82` | Word | Level Select: cursor position (0–20) |
| `$FF84` | Word | Sound Test: value (0–$4F) |

---

## Cheat System

| Address | Size | Description |
|---------|------|-------------|
| `$FFE0` | Byte | Cheat variant 0 (0–1 C presses) → **Level Select enabled** |
| `$FFE1` | Byte | Cheat variant 1 (2–3 C presses) → **A-button reset on pause** |
| `$FFE2` | Byte | Cheat variant 2 (4–5 C presses) → **Debug Mode available** |
| `$FFE3` | Byte | Cheat variant 3 (6–7 C presses) → unused |
| `$FFE4` | Word | Cheat sequence input position (0–8) |
| `$FFE6` | Word | C-button press counter (cumulative, NOT reset between inputs) |
| `$FFFA` | Word | Debug available flag (set by Level Select when $FFE2=1 and A held) |

---

## Sonic Object ($D000)

Dynamic object data — Sonic is always Object Slot 0 at RAM $D000:

| Offset | Size | Description |
|--------|------|-------------|
| `$00` | Byte | Object ID |
| `$01` | Byte | Render flags (bit 0=visible, bit 6=underwater, bit 7=facing left) |
| `$04` | Long | Mapping data pointer |
| `$08` | Long | X position (16.16 fixed point) |
| `$0C` | Long | Y position (16.16 fixed point) |
| `$10` | Word | X velocity |
| `$12` | Word | Y velocity |
| `$14` | Word | Ground velocity |
| `$1A` | Word | Sprite priority |
| `$1C` | Byte | Animation ID (0=walk, 2=rolling, ...) |
| `$22` | Byte | Status bits (bit 1=in air, bit 2=rolling, bit 6=underwater) |
| `$24` | Byte | Routine counter (0=init, 2=normal, 4=hurt, 6=dead, 8=restart) |
| `$28` | Byte | Subtype |
| `$30` | Word | Invincibility / flash timer |

---

## Object Slots Layout

| RAM Range | Slot | Description |
|-----------|------|-------------|
| `$D000–$D03F` | 0 | **Sonic** (always) |
| `$D040–$D07F` | 1 | Reserved |
| `$D080–$DFFF` | 2–31 | Dynamic objects (enemies, items, platforms) |
| Each slot = 64 ($40) bytes

---

## Stack

| Address | Description |
|---------|-------------|
| `$FFFE00` | Initial Stack Pointer (SSP) — grows downward |
| `$FF0000–$FFFE00` | Available RAM for game variables and object slots |

---

## Hardware I/O (Memory-Mapped)

| Address | Description |
|---------|-------------|
| `$A11100` | Z80 Bus Request |
| `$A11200` | Z80 Reset |
| `$A00000+` | Z80 RAM (8 KB) |
| `$C00000` | VDP Data Port |
| `$C00004` | VDP Control Port |
| `$A10003` | Controller Port 1 Data |
| `$A10009` | Controller Port 1 Control |

---

*Generated from ROM analysis of Sonic The Hedgehog (USA, Europe) Rev00.*
