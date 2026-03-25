# Sonic 1 (Genesis/Mega Drive) — Object Catalog

> **ROM:** Sonic The Hedgehog (USA, Europe) Rev00 — GM 00001009-00  
> **Object Handler Table:** ROM $D37E — 99 longword entries (Obj $01–$63)  
> **Dispatch code:** $D348 — reads Object ID byte from slot, multiplies ×4, jumps via table

---

## Object Dispatch Mechanism

```m68k
$D348  move.b   (a0), d0          ; Object ID from SST byte +0
$D34A  beq.b    $D358             ; ID = 0 → empty slot, skip
$D34C  add.w    d0, d0            ; ID × 2
$D34E  add.w    d0, d0            ; ID × 4 (longword index)
$D350  movea.l  $D37E(pc, d0.w), a1  ; Load handler address
$D354  jsr      (a1)              ; Call handler
```

---

## Summary

| Category | Count |
|----------|-------|
| Total table entries | 99 |
| **Active objects** | **93** |
| Stub slots (→ ObjectFall) | 6 |
| Unused enemies (cut content) | 2 (Splats, Roller) |
| Boss objects | 7 |
| Title screen objects | 4 |
| Player object | 1 (Sonic) |

---

## Full Object Table

### Player & Core

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$01` | `$012BD8` | **Sonic** | Main player object; routine dispatch via $24(a0) |
| `$09` | `$01B984` | **Debug Mode Object** | Placement mode controller |

### Stub Slots

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$02` | `$00D5B2` | *(stub)* | → ObjectFall (gravity + delete) |
| `$03` | `$00D5B2` | *(stub)* | → ObjectFall |
| `$04` | `$00D5B2` | *(stub)* | → ObjectFall |
| `$05` | `$00D5B2` | *(stub)* | → ObjectFall |
| `$06` | `$00D5B2` | *(stub)* | → ObjectFall |
| `$07` | `$00D5B2` | *(stub)* | → ObjectFall |

### Title Screen

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$0D` | `$00EB28` | TitleSonic | Animated Sonic on title |
| `$0E` | `$00A61C` | TitleTMText | "TM" trademark text |
| `$0F` | `$00A69C` | **TitlePressStart** | Blinking "PRESS START BUTTON" sprite |
| `$10` | `$01C022` | TitleBackground | Background elements |

### Water & Breathing (LZ)

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$0A` | `$013C98` | DrownCountdown | 5-4-3-2-1-0 countdown |
| `$0B` | `$011206` | BreathBubbles | Air bubble spawner |
| `$0C` | `$011346` | SmallBubbles | Decorative small bubbles |
| `$1B` | `$0110C6` | WaterSurface | Surface ripple effect |
| `$2C` | `$00ABDA` | WaterSound | Splash sound trigger |

### Platforms & Terrain

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$11` | `$007328` | Bridge | Multi-segment collapsing bridge (GHZ, SLZ) |
| `$15` | `$007952` | SwingingPlatform | Hanging platform on chain |
| `$16` | `$011F04` | Helipad | SLZ helicopter pad |
| `$17` | `$007CA2` | GHZ Platform | Green Hill stationary platform |
| `$18` | `$007E32` | GHZ EdgeWall | Wall at platform edge |
| `$19` | `$0081A8` | SBZ Moving Platforms | Scrap Brain moving platforms |
| `$1A` | `$008210` | SBZ Collapse Ledge | Breakaway ledge |
| `$1C` | `$0087CA` | Labyrinth Block | Pushable block (LZ) |
| `$1E` | `$008B4C` | ConveyorBelt | Conveyor belt surface |
| `$35` | `$00B1DC` | LZ Block | Labyrinth generic block |
| `$36` | `$00CE28` | CorkFloor | Cork floor (LZ) — Sonic breaks through |
| `$37` | `$009CB6` | MZ/SLZ Platform | Marble/Star Light platform |
| `$3C` | `$00D11C` | MZ Crumbling Platform | Marble Zone crumble-on-touch |
| `$41` | `$00DABE` | GHZ Block Complex | GHZ complex terrain block |

### Hazards

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$12` | `$00E90C` | SpinningLight | Marble Zone rotating fireball |
| `$13` | `$00E296` | LavafallMakers | Lava stream spawner (MZ) |
| `$14` | `$00E304` | Lavafall | Individual lava stream |
| `$1D` | `$00885E` | Labyrinth Gargoyle Head | Fireball-shooting gargoyle (LZ) |
| `$1F` | `$0094F0` | SYZ Spikeball | Swinging spikeball |
| `$27` | `$008D62` | GHZ Spikes | Static spike hazard |
| `$28` | `$008F22` | GHZ Retract Spikes | Retractable spikes |
| `$3F` | `$008DF6` | Spikes (universal) | General spike object |
| `$49` | `$00D0BE` | SBZ Flame Shooter | Fire jet hazard (SBZ) |
| `$53` | `$008320` | SBZ Swinging Ball | Wrecking ball on chain |

### Items & Collectibles

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$22` | `$0097DE` | **Monitor** | Item box (ring, shoes, shield, invincibility, 1-up) |
| `$26` | `$00A118` | **Spring** | Red (strong) and yellow (weak) springs |
| `$29` | `$009412` | **Ring** | Standard collectible ring |
| `$2A` | `$008934` | Lost Rings | Scattered rings when hit |
| `$30` | `$00B39E` | **Lamppost** | Checkpoint (starpost) |
| `$32` | `$00BD2E` | 1-Up Monitor Icon | Floating 1-Up after breaking monitor |

### Enemies — Active

| Obj ID | ROM Address | Name | Zone | Notes |
|--------|-------------|------|------|-------|
| `$42` | `$00DD68` | **Chopper (Masher)** | GHZ | Jumping fish enemy |
| `$43` | `$00DFFA` | **Crabmeat** | GHZ, SYZ | Sideways-walking crab, shoots projectiles |
| `$44` | `$00E1D4` | **Buzz Bomber** | GHZ, MZ | Flying wasp, shoots downward |
| `$4C` | `$00ED84` | **Caterkiller** | MZ, SBZ | Segmented caterpillar, invincible body |
| `$4D` | `$00EE70` | **Motobug** | GHZ | Ground motorcycle bug |
| `$4E` | `$00F05E` | **Ball Hog** | SBZ | Throws bouncing bombs |
| `$4F` | `$00F806` | Crabmeat Projectile | — | Crabmeat's energy ball |
| `$50` | `$00F83A` | **Orbinaut** | LZ, SBZ | Floating enemy with spiked orbs |
| `$51` | `$00FC92` | **Jaws** | LZ | Underwater fish enemy |
| `$52` | `$00FDF8` | **Burrobot** | LZ | Drilling mole enemy |
| `$54` | `$00F1B8` | **Basaran** | SBZ | Bat enemy, drops from ceiling |
| `$55` | `$0100A8` | **Bomb** | SBZ | Bomb enemy (explodes on contact) |
| `$56` | `$010286` | Burrobot (SBZ variant) | SBZ | Different behavior variant |

### Enemies — Cut Content (Unused)

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$08` | `$0142F0` | **Splats** | Fully functional grasshopper enemy. Complete code with state dispatch (`moveq + move.b + jmp`). NOT placed in any level layout but works perfectly via Debug Mode. |
| `$4A` | `$014254` | **Roller** | Fully functional armadillo/hedgehog enemy. Rolls into ball, has player detection and attack AI. NOT placed in any level but fully operational. |

### Bosses

| Obj ID | ROM Address | Name | Zone |
|--------|-------------|------|------|
| `$3D` | `$017700` | **GHZ Boss** (EggMobile) | Green Hill Zone Act 3 |
| `$3E` | `$01AB22` | **MZ Boss** | Marble Zone Act 3 |
| `$48` | `$017AE4` | **LZ Boss** | Labyrinth Zone Act 3 |
| `$57` | `$010782` | **SYZ Boss** | Spring Yard Zone Act 3 |
| `$58` | `$010976` | **LZ Boss (alt)** | Alternate LZ boss handler |
| `$59` | `$010AD2` | **SLZ Boss** | Star Light Zone Act 3 |
| `$5A` | `$010D5A` | **SBZ Boss** | Scrap Brain Zone Act 3 |
| `$5B` | `$010E90` | **FZ Eggman** | Final Zone — final boss |
| `$5C` | `$011044` | FZ Plasma Ball | Final Zone boss projectile |

### Effects & UI

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$20` | `$008C1C` | SYZ Bumper Block | Bumper in Spring Yard |
| `$21` | `$01C548` | End Signpost | Spinning signpost at act end |
| `$23` | `$009932` | Explosion | Enemy destruction effect |
| `$24` | `$008CF2` | Animal | Released from destroyed enemy |
| `$25` | `$009B26` | Points (popup) | Score popup (100, 200, etc.) |
| `$2B` | `$00AB20` | End Bonus Points | Act clear bonus display |
| `$2D` | `$00ACA4` | SpindashDust | Dust/skid effect |
| `$2E` | `$00A302` | Shield | Blue shield orbit |
| `$2F` | `$00AEB8` | Game Over / Time Over | Text display object |
| `$33` | `$00BED2` | Invincibility Stars | Sparkle effect around Sonic |
| `$34` | `$00C306` | GHZ Waterfall | Waterfall visual effect |
| `$38` | `$014158` | SwirlBug | Caterkiller spinning segment |
| `$3B` | `$00D050` | Boss Explosion | Boss death explosion |
| `$40` | `$00F61A` | **HUD** | Heads-Up Display (score, time, rings, lives) |

### Special Stage

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$31` | `$00B67C` | Signpost Special Stage | Entry signpost |
| `$45` | `$00B99A` | Ring Special Stage | Ring in rotating maze |
| `$46` | `$00E7D0` | SS Bumper | Special Stage bumper |
| `$47` | `$00E9D0` | SS Goal Signpost | Goal in Special Stage |

### SBZ Specific

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$39` | `$00C4B8` | SBZ Door | Automatic/triggered door |
| `$3A` | `$00C572` | SBZ Defense Grid | Electrical hazard grid |
| `$4B` | `$009E06` | SLZ Cannon | Cannon launcher |
| `$5F` | `$0119F6` | SBZ Conveyor Object | Conveyor belt object |

### Ending & Credits

| Obj ID | ROM Address | Name | Notes |
|--------|-------------|------|-------|
| `$5D` | `$0114FC` | Credits Text | Text renderer for credits |
| `$5E` | `$01163C` | Credits Object | Credits scene handler |
| `$60` | `$011CCE` | Ending Scene Object | Ending cutscene controller |
| `$61` | `$011FD4` | Continue Text | "CONTINUE" text display |
| `$62` | `$0121E8` | Continue Sonic | Sonic sprite on continue screen |
| `$63` | `$01233C` | *(last entry)* | Last object in table |

---

*99 entries total. 93 active handlers + 6 stub slots ($02–$07 → ObjectFall at $D5B2).*  
*Generated from ROM analysis of Sonic The Hedgehog (USA, Europe) Rev00.*
