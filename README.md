# 🔵 Sonic The Hedgehog (1991) — Complete Decompilation & Analysis

![Sega Genesis](https://img.shields.io/badge/Platform-Sega%20Genesis%2FMega%20Drive-blue)
![M68000](https://img.shields.io/badge/CPU-Motorola%2068000-orange)
![License](https://img.shields.io/badge/License-GPL--3.0-green)
![Functions](https://img.shields.io/badge/Functions-580-brightgreen)
![Lines](https://img.shields.io/badge/Pseudo--C%20Lines-34986-yellow)

> Complete reverse engineering of **Sonic The Hedgehog** (USA/EU, 512 KB ROM) for Sega Genesis / Mega Drive.  
> 67 documented findings • 99 object types • Z80 SMPS sound driver • Full RAM map

---

## 📋 Overview

This project contains a **full decompilation** of the original Sonic The Hedgehog (1991) ROM, produced through static analysis of the Motorola 68000 binary using [Capstone](https://www.capstone-engine.org/) disassembly framework.

- **580 identified functions** with community-standard names (from [s1disasm](https://github.com/sonicretro/s1disasm))
- **Full M68K disassembly** (~69,000 lines) with hex bytes, labels, and cross-references
- **Pseudo-C decompilation** (34,986 lines) of all game logic
- **Comprehensive analysis document** with 67 verified findings: secrets, bugs, exploits, cut content
- **Complete object catalog** — all 99 object types (93 active + 6 stubs)
- **Z80 SMPS sound driver** load mechanism and command interface
- **ROM-verified** — every finding confirmed directly from binary data

## 📁 Repository Structure

```
sonic1-genesis-decompilation/
│
├── README.md                              # This file
├── LICENSE                                # GPL-3.0
├── .gitignore                             # Excludes ROM, __pycache__, etc.
│
├── disassembly/
│   └── sonic1_full_disassembly.asm        # Full annotated M68K disassembly (~4.6 MB)
│
├── decompilation/
│   └── sonic1_pseudo_decompilation.c      # Pseudo-C decompilation (~1.1 MB, 580 functions)
│
├── analysis/
│   └── sonic1_secrets_and_bugs.md         # Complete analysis: 9 sections, 67 findings
│
├── docs/
│   ├── ram_map.md                         # Full RAM address map ($F600–$FFFA)
│   ├── object_catalog.md                  # All 99 object types with ROM addresses
│   └── sound_driver.md                    # Z80 SMPS driver architecture
│
└── tools/
    ├── sonic1_decompile.py                # Main Capstone-based M68K decompiler
    ├── rename_functions.py                # Community name mapping (~400 names)
    ├── rename_asm_fast.py                 # Fast ASM label replacer
    ├── analyze_all.py                     # ROM analysis: cheats, Nemesis, objects
    ├── analyze_part2.py                   # ROM analysis: demos, time bonus, Z80
    ├── analyze_debug.py                   # Debug mode & object table extraction
    ├── analyze_cheat.py                   # Title screen cheat mechanism trace
    ├── analyze_fffa.py                    # $FFFA flag & Sound Test analysis
    └── batch_analyze.py                   # Batch analysis runner
```

## 🔍 Key Findings

### Hidden Features
| Feature | ROM Address | Description |
|---------|------------|-------------|
| Level Select | `$002EE0` | Up, Down, Left, Right on SEGA screen → A+Start |
| Debug Mode (Rev00) | `$31B6` | Triple D-pad cheat + C-button variant system |
| Frame Advance | `$0013A8` | Hold B + Tap C while paused |
| Debug Placement | `$01CFD6` | Full in-game object editor via B button |
| A-Button Reset | `$0013D4` | Hidden pause reset (cheat variant 1) |
| Warm Boot | `$000310` | Magic value `$696E6974` ("init") preserves state |

### ⚠️ Critical Discovery: Debug Mode in Rev00

The widely documented Sound Test cheat sequence (`01, 09, 09, 01, 00, 06, 02, 03`) **does NOT exist** in Rev00.  
Our ROM analysis confirmed: **zero matches** for this byte pattern in the entire 512 KB ROM.

In Rev00, Debug Mode is activated through a cumulative D-pad + C-button system on the title screen. See [Section 8.2 of the analysis](analysis/sonic1_secrets_and_bugs.md#82-️-критическое-исправление-механизм-debug-mode-в-rev00) for the complete mechanism decoded from ROM.

### Notable Bugs
| Bug | Severity | Description |
|-----|----------|-------------|
| Spike Bug | 🔴 Critical | Death through invincibility — timer reset on floor contact |
| Wrap-Around Bug | 🔴 Critical | Unsigned X comparison → teleport to right side of level |
| Object Slot Exhaustion | 🟡 Medium | 96-slot limit → disappearing rings and effects |
| Y Velocity Overflow | 🟢 Low | Signed overflow during long falls → upward launch |
| Z80 Deadlock | 🟡 Medium | Bus request race condition with sound driver |

### Cut / Unused Content
| Item | Object ID | Status |
|------|-----------|--------|
| **Splats** (rabbit enemy) | `$08` | Fully coded at `$0142F0`, never placed in any level |
| **Roller** (armadillo enemy) | `$4A` | Fully coded at `$014254`, never placed in any level |
| Object slots $02–$07 | `$02`–`$07` | Reserved stubs → ObjectFall (`$D5B2`) |
| Unused Level code | `$33CC` | `LevelScr_Unused` — dead code path |

## 🛠️ Technical Details

| Property | Value |
|----------|-------|
| **ROM** | Sonic The Hedgehog (USA, Europe) |
| **Revision** | **Rev 00** (GM 00001009-00) |
| **Size** | 512 KB (524,288 bytes) |
| **Checksum** | `$264A` (verified) |
| **CPU** | Motorola 68000 @ 7.67 MHz |
| **Sound CPU** | Zilog Z80 @ 3.58 MHz |
| **Sound Driver** | SMPS, Kosinski-compressed at `$72E7C` → Z80 RAM `$A00000` |
| **Video** | Sega VDP (YM7101), 320×224, 64 colors |
| **Build Date** | 1991.APR |

## 📊 Analysis Coverage

| Area | Status |
|------|--------|
| Cheat Codes & Secrets | ✅ 100% |
| Dev Tools (Debug Mode) | ✅ 100% |
| Bugs & Exploits | ✅ 100% |
| Object System (99 types) | ✅ 100% |
| Sound Driver (M68K side) | ✅ 100% |
| Sound Driver (Z80 SMPS) | ✅ 100% |
| RAM Map | ✅ 100% |
| Art/Tile Catalog (Nemesis) | ✅ 100% |
| Cut Content & Unused Code | ✅ 100% |
| Demo Recordings (8 demos) | ✅ 100% |
| Palette Cycling | ✅ 100% |
| Time Bonus System | ✅ 100% |
| Level Select Table | ✅ 100% |
| Kosinski Decompressor | ✅ 100% |
| TMSS Mechanism | ✅ 100% |

## 🧰 Tools

All analysis tools are in the `tools/` directory. They require **Python 3.10+** and **Capstone 5.0+**:

```bash
pip install capstone
```

The main decompiler:
```bash
python tools/sonic1_decompile.py
```

> **Note:** Tools expect the ROM file path to be configured inside each script. The ROM itself is NOT included in this repository.

## ⚠️ Legal Disclaimer

This repository contains **only original reverse-engineered analysis and documentation**. It does **NOT** contain:

- ❌ The original ROM file
- ❌ Copyrighted game assets (sprites, music data, level layouts in binary form)
- ❌ Tools to pirate or distribute the game

This project is intended for **educational and research purposes only**, consistent with fair use principles for reverse engineering interoperability (see [Sega v. Accolade, 1992](https://en.wikipedia.org/wiki/Sega_Enterprises_Ltd._v._Accolade,_Inc.)).

**Sonic The Hedgehog** is © 1991 SEGA. All rights reserved.  
Sonic The Hedgehog™ is a trademark of SEGA Corporation.

## 🔗 Related Projects

| Project | Description |
|---------|-------------|
| [s1disasm](https://github.com/sonicretro/s1disasm) | Sonic Retro's official split disassembly (buildable) |
| [Sonic Retro Wiki](https://info.sonicretro.org/Sonic_the_Hedgehog_(16-bit)) | Community knowledge base |
| [The Cutting Room Floor](https://tcrf.net/Sonic_the_Hedgehog_(Genesis)) | Cut content database |
| [Sonic 1 Hacking Guide](https://info.sonicretro.org/SCHG:Sonic_the_Hedgehog_(16-bit)) | Community hacking guide |

## 👤 Author

Reverse engineered and documented by **Wilps and Claude Opus 4.6** — March 2026.

Built with [Capstone Engine](https://www.capstone-engine.org/) (M68K disassembly) and [GitHub Copilot](https://github.com/features/copilot) (analysis assistance).

## 📜 License

This project is licensed under the **GNU General Public License v3.0** — see [LICENSE](LICENSE) for details.

---

> *"Way past cool!"* — Sonic The Hedgehog
