# 🔵 Sonic The Hedgehog (1991) — Complete Decompilation & Analysis

![Sega Genesis](https://img.shields.io/badge/Platform-Sega%20Genesis%2FMega%20Drive-blue)
![M68000](https://img.shields.io/badge/CPU-Motorola%2068000-orange)
![License](https://img.shields.io/badge/License-GPL--3.0-green)
![Functions](https://img.shields.io/badge/Functions-580-brightgreen)
![Lines](https://img.shields.io/badge/Lines-34986-yellow)

> Complete reverse engineering of Sonic The Hedgehog (USA/EU, 512 KB ROM) for Sega Genesis / Mega Drive.

---

## 📋 Overview

This project contains a **full decompilation** of the original Sonic The Hedgehog (1991) ROM, produced through static analysis of the Motorola 68000 binary. It includes:

- **580 identified functions** with community-standard names
- **Full M68K disassembly** with hex bytes, labels, and cross-references
- **Pseudo-C decompilation** of all game logic
- **Comprehensive analysis** of hidden features, bugs, exploits, and cut content

## 📁 Repository Structure

```
sonic1-genesis-decompilation/
│
├── README.md                          # This file
├── LICENSE                            # GPL-3.0
│
├── disassembly/
│   └── sonic1_full_disassembly.asm    # Full annotated M68K disassembly (4.6 MB)
│
├── decompilation/
│   └── sonic1_pseudo_decompilation.c  # Pseudo-C decompilation (1.1 MB)
│
├── analysis/
│   └── sonic1_secrets_and_bugs.md     # Complete analysis document (67 findings)
│
└── docs/
    ├── ram_map.md                     # Full RAM address map
    ├── object_catalog.md              # 99 object types documented
    └── sound_driver.md                # Z80 SMPS driver analysis
```

## 🔍 Key Findings

### Hidden Features (13)
| Feature | ROM Address | Description |
|---------|------------|-------------|
| Level Select | `$002EE0` | Up/Down/Left/Right on SEGA screen + A+Start |
| Debug Mode | `$003460` | Activated via cumulative D-pad input in Level Select |
| Frame Advance | `$0013A8` | Hold B + Tap C while paused |
| Debug Placement | `$01CFD6` | Full in-game object editor |
| Warm Boot | `$000310` | "init" magic value (`$696E6974`) preserves state |

### Critical Bugs (13)
| Bug | Severity | Description |
|-----|----------|-------------|
| Spike Bug | 🔴 Critical | Invincibility timer reset on floor contact |
| Wrap-Around | 🔴 Critical | Unsigned X comparison → teleport right |
| Object Overflow | 🟡 Medium | 96-slot limit → disappearing rings/effects |
| Y Velocity Overflow | 🟢 Low | Signed overflow → upward launch |

### Cut Content (7)
| Item | Object ID | Status |
|------|-----------|--------|
| Splats (rabbit enemy) | `$08` | Art in ROM, code stubbed |
| Goggles (underwater breathing) | `$09` | ID reserved, code empty |
| Clock Work Zone | Zone `$06` | Palette remnants only |
| Unused SFX | `$8A` | Present in sound driver |

## 🛠️ Technical Details

| Property | Value |
|----------|-------|
| **ROM** | Sonic The Hedgehog (USA, Europe) Rev 00 |
| **Size** | 512 KB (524,288 bytes) |
| **CPU** | Motorola 68000 @ 7.6 MHz |
| **Sound** | Zilog Z80 @ 3.58 MHz (SMPS driver) |
| **Video** | Sega VDP (YM7101) |
| **Checksum** | Word-sum verified |
| **Serial** | GM 00001009-00 |

## 📊 Analysis Coverage

```
Cheat Codes & Secrets ████████████████████ 100%
Dev Tools (Debug)     ████████████████████ 100%
Bugs & Exploits       ████████████████████ 100%
Object System         ████████████████████ 100%
Sound Driver (M68K)   ████████████████████ 100%
Sound Driver (Z80)    ████████████████████ 100%
RAM Map               ████████████████████ 100%
Art/Tile Catalog      ████████████████████ 100%
Cut Content           ████████████████████ 100%
Demo Recordings       ████████████████████ 100%
Palette Cycling       ████████████████████ 100%
Revision Comparison   ████████████████████ 100%
```

## ⚠️ Legal Disclaimer

This repository contains **only original reverse-engineered analysis and documentation**. It does **NOT** contain:

- ❌ The original ROM file
- ❌ Copyrighted game assets (sprites, music data, level layouts)
- ❌ Tools to pirate or distribute the game

This project is intended for **educational and research purposes only**, consistent with fair use principles for reverse engineering interoperability (see [Sega v. Accolade, 1992](https://en.wikipedia.org/wiki/Sega_Enterprises_Ltd._v._Accolade,_Inc.)).

The original game is © 1991 SEGA. All rights reserved. Sonic The Hedgehog is a trademark of SEGA Corporation.

## 🔗 Related Projects

| Project | Description |
|---------|-------------|
| [s1disasm](https://github.com/sonicretro/s1disasm) | Sonic Retro's official split disassembly |
| [Sonic Retro Wiki](https://info.sonicretro.org/Sonic_the_Hedgehog_(16-bit)) | Community wiki |
| [The Cutting Room Floor](https://tcrf.net/Sonic_the_Hedgehog_(Genesis)) | Cut content database |

## 👤 Author

Reverse engineered and documented by **Dokuchaev T.S.** — March 2026.

## 📜 License

This project is licensed under the **GNU General Public License v3.0** — see [LICENSE](LICENSE) for details.

---

> *"Way past cool!"* — Sonic The Hedgehog
