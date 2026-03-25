#!/usr/bin/env python3
"""
Sonic 1 Decompilation - Function Renamer
Applies community-standard names to all auto-generated function/label names.
Based on the Sonic Retro / sonicresearch.org disassembly project.
"""

import re
import os

# =============================================================================
# COMPREHENSIVE NAME MAPPING: auto-name -> community name
# =============================================================================

RENAME_MAP = {
    # ===== ENTRY POINT & INIT (0x000-0x5FF) =====
    "Reserved_3F":           "GameInit",
    "EntryPoint":            "EntryPoint",  # keep as-is
    "sub_0003BA":            "CheckSumOk",
    "BusError":              "BusError",
    "AddressError":          "AddressError",
    "IllegalInstruction":    "IllegalInstruction",
    "ZeroDivide":            "ZeroDivide",
    "CHKException":          "CHKException",
    "TRAPVException":        "TRAPVException",
    "PrivilegeViolation":    "PrivilegeViolation",
    "Trace":                 "Trace",
    "LineAEmulator":         "LineAEmulator",
    "LineFEmulator":         "LineFEmulator",
    "SpuriousInterrupt":     "SpuriousInterrupt",
    "loc_000488":            "ShowErrorScreen",
    "sub_0004D2":            "ErrorText_Data",
    "loc_0005BA":            "ShowHex_Long",
    "loc_0005E0":            "Error_WaitForC",
    "sub_0005F0":            "GameModeArray",

    # ===== VBLANK / HBLANK (0xB10-0x11E6) =====
    "IRQ6_VBlank":           "VBlank_Handler",
    "loc_000D84":            "VInt_Level",
    "sub_00106E":            "VInt_UpdateDisplay",
    "IRQ4_HBlank":           "HBlank_Handler",
    "loc_0011B6":            "JoypadInit",
    "loc_0011E6":            "ReadJoypads",

    # ===== VDP / DMA / CLEAR (0x1222-0x1352) =====
    "loc_001222":            "VDPSetupGame",
    "loc_0012C4":            "ClearScreen",
    "loc_001352":            "SoundDriverLoad",

    # ===== SOUND (0x1396-0x13A8) =====
    "sub_001396":            "PlaySound",
    "loc_00139C":            "PlaySound_Special",
    "sub_0013A8":            "PauseGame",

    # ===== PLANE MAP / NEMESIS DEC (0x1420-0x15EC) =====
    "loc_001420":            "PlaneMapToVRAM",
    "loc_001440":            "NemDec",
    "loc_0014CC":            "NemDec_WritePixel",
    "loc_00152E":            "NemDec_BuildCodeTable",
    "sub_001580":            "LoadPLC",
    "sub_0015B2":            "LoadPLC_ClearFirst",
    "loc_0015DE":            "ClearPLC",
    "loc_0015EC":            "RunPLC_Start",

    # ===== PLC / NEMESIS / ENIGMA / KOSINSKI (0x1642-0x18FF) =====
    "sub_001642":            "RunPLC",
    "loc_00165E":            "RunPLC_VInt",
    "sub_0016EC":            "ProcessPLCQueue",
    "loc_00171E":            "NemDec_Full",
    "sub_0017DC":            "EniDec_ProcessTile",
    "loc_00188C":            "NemDec_FetchBits",
    "loc_00189C":            "KosDec",

    # ===== GAME MODE / PALETTE (0x193C-0x214C) =====
    "sub_00193C":            "GameModeSwitch",
    "sub_00195C":            "PalCycle_Underwater",
    "sub_001DAC":            "PaletteFadeIn",
    "sub_001DB2":            "PaletteFadeIn_Step",
    "loc_001E52":            "PaletteFadeOut",
    "loc_001E72":            "PaletteFadeOut_Step",
    "sub_001ED0":            "PaletteWhiteIn",
    "sub_001F7C":            "PaletteWhiteOut",
    "loc_001F9C":            "PaletteWhiteOut_Step",
    "loc_00200A":            "WaterPalette_Update",
    "sub_0020FC":            "PalLoad_ForFade",
    "loc_002118":            "PalLoad_Now",
    "sub_002130":            "PalLoad_Water",
    "sub_00214C":            "PalLoad_Underwater",

    # ===== UTILITY (0x29A8-0x2CA8) =====
    "loc_0029A8":            "WaitForVBlank",
    "sub_0029B4":            "RandomNumber",
    "sub_0029DA":            "CalcSine",
    "sub_002CA8":            "CalcAngle",

    # ===== LEVEL SELECT / TITLE (0x3460-0x489C) =====
    "sub_003460":            "LevelSelect",
    "loc_0034E6":            "LevelSelect_DrawMenu",
    "loc_003572":            "LevelSelect_DrawHexDigit",
    "loc_003586":            "LevelSelect_DrawRow",
    "sub_003BD0":            "Camera_SetLimits",
    "loc_003C32":            "MoveWater_SetSpeed",
    "loc_003E32":            "CheckWaterEntry",
    "loc_003F34":            "Sonic_WaterSlide",
    "sub_003FD0":            "DemoPlayback",
    "sub_0040F0":            "Demo_SetDataPtr",
    "sub_004118":            "InitOscillations",
    "sub_00416E":            "UpdateOscillations",
    "sub_004206":            "AnimateTiles",
    "sub_004274":            "BossLockCamera",
    "sub_00489C":            "TitleScreen_LoadTiles",
    "sub_004962":            "AnimateLevelGfx",

    # ===== SCROLLING / CAMERA (0x4BE4-0x6CA6) =====
    "sub_004BE4":            "HScrollDeform",
    "sub_005370":            "GotThroughAct",
    "sub_005898":            "Continue_SetupLevel",
    "sub_005EBE":            "LevelSizeLoad",
    "loc_0061EC":            "LevelSizeLoad_SetBGScroll",
    "sub_006286":            "Camera_Update",
    "sub_0064A8":            "Scroll_GHZ_BG",
    "loc_00657E":            "MoveScreenHoriz",
    "loc_006616":            "MoveScreenVert",
    "sub_006768":            "BGScroll_Update",
    "sub_0067D2":            "ScrollBlock1",
    "sub_006814":            "ScrollBlock2",
    "sub_006844":            "ScrollBlock3",
    "sub_006886":            "DrawLevelBG",
    "loc_0068B2":            "DrawTilesWhenMoving",
    "loc_006954":            "DrawBGScrollBlock1",
    "loc_0069F4":            "DrawBGScrollBlock2",
    "loc_006AD8":            "DrawBlockCol",
    "loc_006ADA":            "DrawTiles",
    "loc_006B04":            "DrawBlocks_LR",
    "loc_006B06":            "DrawBlocks_LR_Partial",
    "loc_006B32":            "DrawBlock",
    "loc_006BD6":            "GetLevelBlock",
    "loc_006C20":            "CalcVRAMAddr",
    "sub_006C3C":            "CalcVRAMAddrByScroll",
    "sub_006C58":            "DrawEntireScreen",
    "loc_006C7E":            "DrawFullScreen",
    "sub_006CA6":            "LevelDataLoad",
    "loc_006D12":            "LevelScr_LoadScrollData",
    "loc_006D32":            "LevelScr_LoadScrollBlockRow",
    "sub_006D3D":            "LevelScr_Unused",
    "loc_006D6C":            "LevelSizeLoad_DynResize",

    # ===== DYNAMIC LEVEL EVENTS (0x7180-0x7328) =====
    "sub_007180":            "Dyn_GHZ_Act3",
    "sub_0071A4":            "Dyn_Marble",
    "sub_0071D0":            "Dyn_MZ_Act1_LavaRise",
    "sub_007202":            "Dyn_CopyScrollPos",
    "sub_00720A":            "Dyn_SYZ",
    "sub_007244":            "Dyn_LZ_Sub",
    "sub_00727C":            "Dyn_LZ_Act1_Boss",
    "sub_00729A":            "Dyn_LZ_Act2",
    "sub_0072CA":            "Dyn_SBZ_Sub",
    "sub_007324":            "Dyn_SBZ_CopyScrollPos",

    # ===== TITLE CARD (0x7328-0x7934) =====
    "sub_007328":            "Obj_TitleCard",
    "sub_0076CC":            "Map_TitleCard_Data",
    "sub_0078FC":            "TitleCard_DeleteChildren",
    "sub_007928":            "DeleteObject_Wrapper",
    "sub_00792E":            "DisplaySprite_Wrapper",
    "sub_007934":            "TitleCard_VRAMData",

    # ===== PLATFORM / SOLID OBJECT ENGINE (0x744C-0x7F76) =====
    "sub_00744C":            "PlatformObject",
    "sub_0074AE":            "MountPlatform",
    "sub_007520":            "SlopedPlatform",
    "sub_00755C":            "FlatPlatform",
    "sub_0075C0":            "ExitPlatform",
    "sub_0075F4":            "AlignPlayerOnPlatformY",
    "sub_007620":            "SwingingPlatform_Segments",
    "sub_007B22":            "SolidObject_CrushDown",
    "sub_007B2E":            "Platform_SetSonicOnTop",
    "sub_007B64":            "RotatePlatformAroundCenter",
    "sub_007B7A":            "OscillatingPlatform",
    "loc_007BBA":            "OrbitChildObjects",
    "sub_007BFE":            "DeleteChildrenIfOffscreen",
    "sub_007C3E":            "DeleteSelf_Wrapper",
    "sub_007C44":            "DisplaySprite_Wrapper2",
    "sub_007D88":            "AnimateByOscillation",
    "sub_007DA8":            "DeleteWithChildrenIfOffscreen",
    "sub_007DF0":            "AnimateAndDisplay",
    "sub_007F2C":            "OscillateObjectY",
    "sub_007F46":            "Obj_SubtypeDispatch",
    "sub_007F76":            "MoveObjectOscillateX",
    "sub_0080D8":            "DeleteIfOffscreen_BaseX",

    # ===== BRIDGE (0x829C-0x8570) =====
    "sub_00829C":            "Obj_Bridge",
    "sub_00830A":            "Obj_Bridge_MoveAndDisplay",
    "sub_008320":            "Obj_Bridge_Main",
    "sub_0083D8":            "Obj_Bridge_Solid",
    "sub_00843C":            "Obj_Bridge_MoveAndDelete",
    "sub_008452":            "BreakObjectIntoPieces",
    "loc_00852A":            "Obj_Bridge_HeightCheck",
    "sub_008570":            "Bridge_HeightData",

    # ===== OBJECTS (0x88DA-0x9688) =====
    "sub_0088DA":            "DeleteSelf",
    "sub_0088E0":            "CheckPlayerOnTop",
    "sub_00891C":            "Obj_Crabmeat",
    "sub_008A62":            "SolidObject_FullCollision",
    "loc_008ADA":            "Enemy_CheckCollision",
    "sub_008B4C":            "Obj_Crabmeat_Init",
    "sub_008BAE":            "Obj_Crabmeat_FireProjectile",
    "sub_0093C4":            "FallingBlock_FindFloor",
    "sub_0093EC":            "FacePlayer",
    "sub_009404":            "CalcHorizDistToPlayer",

    # ===== SONIC HELPERS / OBJECTS (0x9688-0xAE22) =====
    "sub_009688":            "CalcSlopeIndex",
    "sub_009C76":            "CollectRing",
    "sub_00A48E":            "Touch_ChkHurt",
    "sub_00A718":            "AnimateSprite",
    "sub_00AE22":            "ObjFacePlayer",

    # ===== OBJECT ROUTINES / DISPATCHERS (0xAF9E-0xBAC6) =====
    "sub_00AF9E":            "Obj_RoutineDispatch_3bit_A",
    "sub_00B09C":            "AddToTouchResponse",
    "sub_00B4DE":            "Obj_RoutineDispatch_3bit_B",
    "sub_00B834":            "Obj_RoutineDispatch_4bit",
    "sub_00BAC6":            "Obj_RoutineDispatch_Full",
    "sub_00BE22":            "CheckCollision_Monitor",

    # ===== LARGE OBJECTS (0xC186-0xD338) =====
    "sub_00C186":            "Obj_PushBlock",
    "sub_00CF46":            "Obj_RoutineDispatch_C",
    "sub_00CF86":            "PulsateObject",
    "sub_00D1EE":            "SmashObject",

    # ===== CORE ENGINE (0xD338-0xDAA2) =====
    "sub_00D338":            "ExecuteObjects",
    "sub_00D5B2":            "ObjectFall",
    "loc_00D5DE":            "SpeedToPos",
    "loc_00D604":            "DisplaySprite",
    "loc_00D622":            "DisplaySprite_a1",
    "loc_00D640":            "DeleteObject",
    "sub_00D642":            "DeleteObject_a1",
    "sub_00D65E":            "BuildSprites",
    "loc_00D750":            "BuildSprites_Flipped",
    "loc_00D762":            "BuildSprites_Normal",
    "sub_00D87E":            "ChkObjOnScreen",
    "sub_00D8A6":            "ChkObjOnScreen_Wide",
    "sub_00D8DA":            "ScrollManager",
    "sub_00DA3C":            "SingleObjLoad_Layout",
    "loc_00DA8C":            "FindFreeObj",
    "sub_00DAA2":            "FindNextFreeObj",

    # ===== BOSS / SPECIAL (0xE152-0xEF10) =====
    "sub_00E152":            "Boss_CheckActivate",
    "sub_00EC8A":            "GotThroughAct_ScoreTally",
    "sub_00EEBA":            "SpawnAnimal",

    # ===== OBJECT CODE (0xF70C-0xFA1C) =====
    "sub_00F70C":            "Obj_FallWithParticles",
    "sub_00F770":            "Obj_AnimateDisplay",
    "sub_00F808":            "ObjCheckWallDist",
    "sub_00F83A":            "Obj_Index",
    "sub_00F8A0":            "Obj_ActRoutine",
    "sub_00F8E4":            "Obj_SlideOnFloor",
    "sub_00F91C":            "AnimData_Embedded",
    "sub_00F9D6":            "SolidObject",
    "sub_00FA1C":            "SolidObject_Always",
    "sub_00FA62":            "SolidObject_Full",
    "loc_00FAC8":            "SolidObject_NoMap",

    # ===== MONITOR / PATH SWAPPER (0xFC92-0xFFEE) =====
    "sub_00FC92":            "Obj_Monitor",
    "sub_00FCFE":            "Obj_Monitor_BreakOpen",
    "sub_00FEE6":            "Obj_PathSwapper",
    "sub_00FF12":            "Obj_PathSwapper_SetXPos",
    "sub_00FF32":            "Platform_CheckPlayerStanding",
    "sub_00FF40":            "Platform_AnimateWithFloor",
    "sub_00FF60":            "Platform_AnimateAndAdvance",
    "sub_00FF80":            "Platform_FallWithGravity",
    "sub_00FFA2":            "Platform_DeleteIfOffscreen",
    "sub_00FFCE":            "Platform_UpdateYFromBoundary",
    "sub_00FFEE":            "Platform_OscillatePosition",

    # ===== SWING / BRIDGE HIGH (0x1014A-0x10700) =====
    "sub_01014A":            "Obj15_Sub_GHZSwing",
    "sub_01018C":            "Obj15_Landed",
    "sub_0101C8":            "Obj15_Sub3",
    "sub_0101F6":            "Obj15_CalcDist",
    "sub_010218":            "Obj15_Delete",
    "sub_01022A":            "Obj15_Data",
    "sub_0103F4":            "Bridge_GetXPos",
    "sub_010422":            "Bridge_GetYPos",
    "sub_010450":            "Obj11_Bridge_Main",
    "sub_01057A":            "Obj11_Depress",
    "sub_010700":            "Map_Bridge_Data",

    # ===== ORBITING / OSCILLATING PLATFORMS (0x108BE-0x10E82) =====
    "sub_0108BE":            "Obj0B_OrbitChildren",
    "sub_010910":            "ChkObjOnScreen_Delete",
    "sub_010952":            "DisplaySprite_Wrapper3",
    "sub_010A22":            "OscillateX_Offset",
    "sub_010A44":            "OscillateY_Offset",
    "sub_010A68":            "Orbit_SingleChild",
    "sub_010AA0":            "Orbit_Data",
    "sub_010B4E":            "Obj18_Platform_Main",
    "sub_010BD6":            "Obj18_TypeIndex",
    "sub_010C00":            "Obj18_Type0_Wait",
    "sub_010C0E":            "Obj18_Type1_Step",
    "sub_010C22":            "Obj18_Type2_Step",
    "sub_010C34":            "Obj18_Type3_Step",
    "sub_010C56":            "Obj18_Type4_Step",
    "sub_010C78":            "Obj18_Type5_Step",
    "sub_010CB2":            "Obj18_TimerLogic",
    "sub_010CFC":            "Obj18_SlideTimer",

    # ===== SBZ PLATFORM / ZONE OBJECTS (0x10D48-0x10FCC) =====
    "sub_010D48":            "Obj1A_SBZPlatform_Main",
    "sub_010DEC":            "Obj1A_TypeIndex",
    "sub_010E42":            "Obj1A_RotatePos",
    "sub_010E82":            "Obj1F_ZoneObj_Main",
    "sub_010FC0":            "Obj_SmallHelper",
    "sub_010FCC":            "Obj_FlashTimer",

    # ===== TITLE/HUD ELEMENTS (0x11010-0x114B0) =====
    "sub_011010":            "Obj_PalCycleStep",
    "sub_01103A":            "NullSub",
    "sub_01103C":            "Obj_TitleElement_Init",
    "sub_0114B0":            "DeleteObject_Wrapper3",

    # ===== SOLID BLOCKS / DOORS (0x11718-0x11DBE) =====
    "sub_011718":            "Obj36_SolidBlock_Main",
    "sub_01174A":            "Obj36_Init",
    "loc_011766":            "Obj36_Sub",
    "sub_011792":            "Obj3B_SBZDoor_Main",
    "sub_011A3C":            "Obj26_AnimObj_Main",
    "sub_011A98":            "Obj26_Countdown",
    "sub_011ABE":            "Obj26_Sub",
    "sub_011AD2":            "Obj26_Move",
    "sub_011B60":            "Obj_BreakApart",
    "sub_011DBE":            "Obj_ProximityTrigger",

    # ===== SONIC CHARACTER CODE (0x120C0-0x13916) =====
    "sub_0120C0":            "Sonic_InvincTimer",
    "sub_0120E6":            "Obj_FallWithFloor",
    "sub_012108":            "Obj_MoveWithWall",
    "sub_012128":            "Obj_MoveHelper",
    "sub_01213A":            "Obj_FloorCheck",
    "sub_012180":            "Obj_BobPlatformY",
    "sub_012284":            "Obj25_Ring_Main",
    "sub_0123F6":            "Obj25_Ring_Collect",
    "sub_012502":            "Obj25_Ring_Attract",
    "loc_012570":            "Obj25_FindTarget",
    "sub_01294C":            "Obj_CheckSonicRange",
    "sub_01295E":            "Touch_ChkSonicProx",
    "sub_012C58":            "Sonic_Main",
    "sub_012D5E":            "Sonic_RecordPos",
    "sub_012D78":            "Sonic_Water",
    "sub_012E3C":            "Sonic_Water_Sub",
    "sub_012E66":            "Sonic_ModeSecondary",
    "sub_012E86":            "Sonic_ModeNormal",
    "sub_012EB0":            "Sonic_Move",
    "loc_01307E":            "Sonic_MoveLeft",
    "loc_0130EA":            "Sonic_MoveRight",
    "sub_013150":            "Sonic_Roll",
    "loc_013202":            "Sonic_Roll_Sub",
    "loc_013226":            "Sonic_Roll_Sub2",
    "sub_013248":            "Sonic_Jump",
    "sub_0132D4":            "Sonic_JumpHeight",
    "sub_013304":            "Sonic_SlopeResist",
    "sub_013384":            "Sonic_SlopeRepel",
    "loc_0133AC":            "Sonic_ResetOnFloor",
    "sub_0133EA":            "Sonic_CheckFloor",
    "sub_013498":            "Sonic_LevelBound",
    "sub_0134D4":            "Sonic_RollSpeed",
    "sub_01350A":            "Sonic_RollLeft",
    "sub_013546":            "Sonic_RollRight",
    "sub_013588":            "Sonic_ChkRollStop",
    "sub_0135A4":            "Sonic_DoLevelBound",
    "loc_0137A0":            "Sonic_HurtRecoil",
    "sub_0137F2":            "Sonic_Display_Hurt",
    "sub_013826":            "Sonic_Dead",
    "sub_013862":            "Sonic_DeathDisplay",
    "sub_01387E":            "Sonic_Restart",
    "sub_013902":            "Sonic_GameOver",
    "sub_013916":            "Sonic_ChkLayerSwitch",

    # ===== SONIC ANIMATION / DYNPLC (0x139C4-0x13C98) =====
    "sub_0139C4":            "Sonic_Animate",
    "loc_013A0C":            "Sonic_Animate_Step",
    "sub_013C3E":            "LoadSonicDynPLC",
    "sub_013C98":            "Obj0A_EndSign_Main",

    # ===== SONIC COLLISION HELPERS (0x13E1C-0x142F0) =====
    "sub_013E1C":            "Sonic_CollisionData",
    "sub_013F86":            "Sonic_WallCollide",
    "loc_01408E":            "Sonic_HitCeiling",
    "sub_0140B8":            "Sonic_FloorDist_Short",
    "sub_014198":            "Obj_Empty",
    "sub_0141A4":            "Sonic_SetStandAni",
    "sub_014270":            "Sonic_WalkingAni",
    "sub_0142F0":            "Sonic_PushAni",

    # ===== FLOOR / WALL / CEILING SENSORS (0x145EE-0x1509A) =====
    "sub_0145EE":            "Sonic_AnglePos",
    "sub_0146E8":            "FindFloor_Alt",
    "sub_01470C":            "FindCeiling_Angle",
    "sub_014728":            "Noop_Return",
    "sub_01472A":            "Obj_UnmoveXY",
    "loc_014750":            "AngleSelect",
    "loc_01495C":            "FindBlock",
    "loc_0149CE":            "FindFloor",
    "loc_014A74":            "FindFloor2",
    "loc_014B0C":            "FindCeiling",
    "loc_014BB4":            "FindCeiling2",
    "sub_014C4C":            "FindWall_Stub",
    "sub_014C4E":            "FindWall_Right",
    "loc_014CDE":            "FindWall",
    "loc_014D48":            "FindWall_Block",
    "loc_014D70":            "FindWall_Block2",
    "sub_014DE8":            "ObjFloorDist2",
    "sub_014E18":            "ObjFloorDist",
    "sub_014E1C":            "ObjFloorDist_Entry2",
    "loc_014EB4":            "FindFloor_FromBelow",
    "loc_014EDA":            "FindFloor_Alt2",
    "loc_014F08":            "FindFloor_Alt3",
    "sub_014F9E":            "ObjWallDist",
    "loc_015042":            "ObjWallDist_Sub",
    "loc_01506C":            "ObjCeilingDist",
    "sub_01509A":            "CollisionEngine_Stub",

    # ===== PLATFORMS / ROTATING OBJECTS (0x15200-0x15F0E) =====
    "sub_015200":            "Obj_Platform_Solid",
    "sub_015248":            "Obj_Platform_Move",
    "sub_015272":            "Obj_Platform_Stub",
    "sub_015570":            "Obj_RotatingLog",
    "sub_015624":            "Obj_OrbitCalc",
    "sub_01565E":            "ChkObjOnScreen_Alt",
    "sub_0156EA":            "DeleteObject_Wrapper4",
    "sub_015730":            "Obj_JumpTable",
    "sub_015A14":            "Obj_ZoneObj_A",
    "sub_015A62":            "Obj_ZoneObj_B",
    "sub_015AB2":            "Obj_ZoneObj_C",
    "sub_015B26":            "Obj_ZoneObj_D",
    "sub_015D96":            "Obj_ZoneObj_E",
    "sub_015EAC":            "Obj_ZoneObj_F",
    "sub_015F0E":            "Obj_ZoneObj_G",

    # ===== PATH PLATFORMS / MONITORS (0x16300-0x1720C) =====
    "sub_016300":            "Obj_PathPlatform",
    "sub_016424":            "Obj_PathPlatform_Step",
    "sub_0165DE":            "Obj_PathPlatform_Sub",
    "sub_016608":            "Obj_PathPlatform_Stub1",
    "sub_016694":            "Obj_PathPlatform_Stub2",
    "sub_0166B0":            "Obj_PathObj",
    "sub_01675E":            "Obj_PathObj_Sub",
    "sub_016798":            "Obj_PathObj_Move",
    "sub_01681C":            "Obj_PathObj_Ani",
    "sub_0168AC":            "Obj_PathObj_Data",
    "sub_016952":            "Obj_LandingBlock",
    "sub_016EAE":            "Obj26_Monitor_Main",
    "sub_016F92":            "Obj26_Monitor_Sub",
    "sub_016F94":            "Obj26_Monitor_Fall",
    "sub_016FD2":            "Obj26_Monitor_Icon",
    "sub_01704C":            "Obj26_Monitor_Done",
    "sub_01720C":            "DeleteObject_Wrapper5",

    # ===== BOSSES (0x1784C-0x1984C) =====
    "sub_01784C":            "Boss_AddScore",
    "sub_017860":            "Boss_MakeExplosion",
    "sub_0178A4":            "Boss_MoveObject",
    "sub_0178CA":            "Obj3D_GHZBoss_Main",
    "sub_0179AC":            "Obj3D_GHZBoss_Move",
    "sub_017BB2":            "Obj3D_GHZBoss_Swing",
    "sub_017C2A":            "Obj3D_GHZBoss_Hit",
    "sub_017C68":            "Obj3D_GHZBoss_Flee",
    "sub_017E7C":            "Obj3D_GHZBoss_Chain",
    "sub_017F8E":            "Obj3D_GHZBoss_Explode",
    "sub_017FA0":            "Obj3D_GHZBoss_Defeat",
    "sub_01826C":            "Obj47_MZBoss_Setup",
    "sub_018392":            "Obj47_MZBoss_Score",
    "sub_0183AA":            "Obj47_MZBoss_AI",
    "sub_01849E":            "Obj47_MZBoss_Fire",
    "sub_0184F6":            "Obj47_MZBoss_Explode",
    "sub_01852C":            "Obj47_MZBoss_Defeat",
    "sub_018744":            "Obj48_SYZBoss_Init",
    "sub_018782":            "Obj48_SYZBoss_Child",
    "sub_0187D0":            "Obj48_SYZBoss_Floor",
    "sub_0187F0":            "Boss_FloorChk",
    "sub_018832":            "Boss_FloorChk2",
    "sub_018900":            "Obj4A_SYZBoss_Setup",
    "sub_018A46":            "Obj4A_SYZBoss_Score",
    "sub_018A5E":            "Obj4A_SYZBoss_Orbit",
    "sub_018DC6":            "Obj4B_LZBoss_Main",
    "sub_01903C":            "Boss_SpawnDebris",
    "sub_0190DE":            "Boss_Data",
    "sub_019136":            "Obj4C_SLZBoss_Setup",
    "sub_019258":            "Obj4C_SLZBoss_Score",
    "sub_019270":            "Obj4C_SLZBoss_AI",
    "sub_01944A":            "Obj4C_FindSeesaw",
    "sub_019474":            "Obj4C_SLZBoss_Attack",
    "sub_019556":            "Obj4D_SBZBoss_Stub",
    "sub_01955A":            "Obj4D_SBZBoss_Init",
    "sub_01957E":            "Obj4D_SBZBoss_Sub",
    "sub_01958A":            "Obj4D_SBZBoss_Main",
    "sub_019704":            "Obj4D_SBZBoss_Move",
    "sub_01977A":            "Obj4D_SBZBoss_Attack",
    "sub_01984C":            "Obj4D_SBZBoss_Defeat",

    # ===== TITLE CARDS / GAME OVER / SIGNPOST (0x19BFC-0x1A676) =====
    "sub_019BFC":            "Obj34_TitleCard_GO",
    "sub_019C94":            "Obj34_TitleCard_Setup",
    "sub_019DCE":            "Obj39_GameOver_Setup",
    "sub_019EA8":            "Obj39_GameOver_Main",
    "sub_019FD6":            "Obj_DrownTimer",
    "sub_01A15C":            "Obj3E_Signpost_Main",
    "sub_01A192":            "Obj3E_Signpost_Spin",
    "sub_01A28C":            "Obj_FollowParent",
    "sub_01A304":            "Obj_FollowParent2",
    "sub_01A338":            "Obj34_TitleCard_Text",
    "sub_01A472":            "Obj_EndSeq",
    "sub_01A5D4":            "Obj_EndSeq_Sub",
    "sub_01A604":            "Obj_EndSeq_Explode",
    "sub_01A676":            "Obj_EndSeq_Data",

    # ===== EFFECTS / RING SCATTER (0x1A89A-0x1AD6C) =====
    "sub_01A89A":            "Obj_Sparkle",
    "sub_01A990":            "Obj_SmallEffect1",
    "sub_01A9C0":            "Obj_SmallEffect2",
    "sub_01AA1E":            "Obj_SmallEffect3",
    "sub_01ABC2":            "Obj_Static1",
    "sub_01ABFE":            "Obj_Static2",
    "sub_01AC62":            "Obj_RingScatter_Move",
    "sub_01ACFA":            "Obj37_RingScatter",
    "sub_01AD4A":            "Obj_ChkRingsGone",
    "sub_01AD6C":            "Obj_RingScatter_Data",

    # ===== TOUCH RESPONSE / RING LOSS (0x1ADE4-0x1B098) =====
    "sub_01ADE4":            "TouchResponse",
    "sub_01AE2E":            "TouchResponse_Data",
    "sub_01AFF4":            "Sonic_LoseRings",
    "loc_01B098":            "Sonic_LoseRings_Sub",

    # ===== SPECIAL STAGE (0x1B14E-0x1BE8E) =====
    "sub_01B14E":            "SS_LayoutRender",
    "loc_01B290":            "SS_LayoutRender_Sub",
    "sub_01B43A":            "SS_Collision",
    "sub_01B4BA":            "SS_ChkBlock",
    "loc_01B4D0":            "SS_CalcOffset",
    "sub_01B4F0":            "SS_Helper1",
    "sub_01B532":            "SS_Helper2",
    "sub_01B568":            "SS_Helper3",
    "sub_01B598":            "SS_Helper4",
    "sub_01B5CA":            "SS_Helper5",
    "sub_01B5CE":            "SS_Helper6",
    "sub_01B60E":            "SS_Helper7",
    "sub_01B67C":            "SS_CollectItem",
    "sub_01B738":            "SS_VDPPattern_Data",
    "sub_01BA60":            "SS_SonicMove",
    "loc_01BAF8":            "SS_MoveLeft",
    "loc_01BB28":            "SS_MoveRight",
    "sub_01BB56":            "SS_Friction",
    "sub_01BB9A":            "SS_Stub",
    "sub_01BB9C":            "SS_AngleCheck",
    "sub_01BBB6":            "SS_BounceBack",
    "sub_01BBE0":            "SS_SonicAnimate",
    "sub_01BC56":            "SS_ObjectHandler",
    "loc_01BCE8":            "SS_ObjectHandler_Sub",
    "sub_01BD52":            "SS_Results",
    "sub_01BE8E":            "SS_Background",

    # ===== HUD / PLC / TILES / DEBUG (0x1C022-0x1D152) =====
    "sub_01C022":            "Noop_1C022",
    "sub_01C024":            "PLC_Process",
    "sub_01C10E":            "AnimateTiles_GHZ",
    "sub_01C1EC":            "AnimateTiles_MZ_SYZ",
    "sub_01C2A2":            "AnimateTiles_SBZ",
    "sub_01C3B6":            "Noop_1C3B6",
    "loc_01C3B8":            "VDP_WriteRow",
    "sub_01C3CE":            "VDP_Data_Fragment",
    "sub_01C3FA":            "BuildSprites_Type1",
    "sub_01C410":            "BuildSprites_Type2",
    "sub_01C41E":            "BuildSprites_Type3",
    "sub_01C434":            "BuildSprites_Type4",
    "sub_01C442":            "BuildSprites_Type5",
    "sub_01C458":            "BuildSprites_Type6",
    "sub_01C466":            "BuildSprites_Type7",
    "sub_01C47C":            "BuildSprites_Type8",
    "sub_01C48A":            "BuildSprites_Type9",
    "sub_01C4A0":            "BuildSprites_TypeA",
    "sub_01C4AE":            "BuildSprites_TypeB",
    "sub_01C4C4":            "BuildSprites_TypeC",
    "sub_01C4D2":            "BuildSprites_TypeD",
    "sub_01C4E8":            "BuildSprites_TypeE",
    "sub_01C4FA":            "BuildSprites_TypeF",
    "loc_01C510":            "PLC_LoadToVRAM",
    "loc_01C68C":            "AddPoints",
    "sub_01C6B8":            "HUD_DrawAll",
    "loc_01C80E":            "HUD_DrawScore",
    "sub_01C822":            "HUD_DrawTimer",
    "loc_01C87A":            "HUD_DrawRings",
    "loc_01C8D0":            "HUD_TimeUpdate",
    "loc_01C8DA":            "HUD_NumConvert",
    "sub_01C938":            "HUD_DrawLives",
    "sub_01C990":            "HUD_DrawDigit",
    "loc_01C9A8":            "HUD_Sub1",
    "loc_01C9B2":            "HUD_Sub2",
    "loc_01CA0C":            "HUD_Sub3",
    "loc_01CA6E":            "HUD_Sub4",
    "sub_01CFD6":            "DebugMode",
    "loc_01D152":            "DebugMode_Sub",

    # ===== COMPRESSED ART DATA (0x31A60+) =====
    "sub_031A60":            "ArtNem_GHZTiles",
    "sub_034A80":            "ArtNem_MZTiles",
    "sub_037D36":            "ArtNem_SYZTiles",
    "sub_037D9C":            "ArtNem_LZTiles",
    "sub_03BC98":            "ArtNem_SLZTiles",
    "sub_03C7C2":            "ArtNem_SBZTiles",
    "sub_041AEB":            "ArtNem_Sprites1",
    "sub_042729":            "ArtNem_Sprites2",
    "sub_0474B7":            "ArtNem_Sprites3",
    "sub_048523":            "ArtNem_Sprites4",
    "sub_04D6F5":            "ArtNem_Sprites5",
    "sub_04ED67":            "ArtNem_Sprites6",
    "sub_04F953":            "ArtNem_Sprites7",
    "sub_0516BD":            "ArtNem_Sprites8",
    "sub_0534CD":            "ArtNem_Sprites9",
    "sub_053527":            "ArtNem_Sprites10",
    "sub_05365D":            "ArtNem_SonicArt",
    "sub_053ECD":            "ArtNem_HUDArt",
    "sub_0596F6":            "ArtNem_LevelLayout1",
    "sub_059F47":            "ArtNem_LevelLayout2",
    "sub_05AEE5":            "ArtNem_Objects1",
    "sub_05CDB7":            "ArtNem_Objects2",
    "sub_05E279":            "ArtNem_Objects3",
    "sub_06270F":            "ArtNem_EndingArt",

    # ===== SOUND DRIVER (0x71B4C-0x72CB4) =====
    "sub_071B4C":            "SoundDriver_Main",
    "sub_071C4E":            "SndDrv_UpdateDAC",
    "sub_071CCA":            "SndDrv_UpdateFM",
    "sub_071CEC":            "FM_GetNote",
    "sub_071D22":            "FM_RestNote",
    "sub_071D40":            "FM_SetDuration",
    "loc_071D60":            "FM_FinishUpdate",
    "sub_071D9E":            "FM_NoteOffTimer",
    "sub_071DC6":            "FM_DoModulation",
    "sub_071E18":            "FM_SetFrequency",
    "sub_071F02":            "SndDrv_UpdateSFX",
    "sub_071F4C":            "SndDrv_UpdateSpecial",
    "sub_0723E0":            "SndDrv_StopAll",
    "sub_07247C":            "SndDrv_StopDAC_PSG",
    "sub_072504":            "SndDrv_TempoUpdate",
    "sub_07256A":            "SndDrv_TempoHelper",
    "sub_0725CA":            "SndDrv_FadeControl",
    "sub_07260C":            "FM_FadeTick",
    "sub_07267C":            "SndDrv_PlayMusic",
    "sub_0726FE":            "FM_NoteOff",
    "sub_07270A":            "PSG_NoteOff",
    "sub_072722":            "FM_SetVolume",
    "loc_07272E":            "FM_WriteReg_Part1",
    "loc_072764":            "FM_WriteReg_Part2",
    "sub_072850":            "SndDrv_UpdatePSG",
    "sub_072878":            "PSG_GetNote",
    "sub_0728AC":            "PSG_DoEnvelope",
    "sub_0728DC":            "PSG_EnvAttack",
    "sub_0728E2":            "PSG_EnvDecay",
    "sub_072926":            "PSG_SetFrequency",
    "loc_07296A":            "PSG_SetNoise",
    "loc_0729A0":            "PSG_Silence",
    "sub_0729A6":            "PSG_Helper",
    "loc_0729B6":            "SndDrv_CmdHandler",
    "sub_072A5A":            "SndDrv_CoordFlag",
    "sub_072C4E":            "FM_SetInstrument",
    "sub_072CB4":            "FM_CalcTotalLevel",

    # ===== END OF ROM =====
    "sub_07F27D":            "ROM_EndData",

    # ===== EXTRA WRAPPERS (from sub_0076CC range) =====
    "sub_0076CC":            "Map_TitleCard_Data",
}


def rename_file(filepath):
    """Apply all renames to a single file."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    original_size = len(content)
    total_replacements = 0
    
    # Sort by length descending to avoid partial matches
    # e.g. "sub_01014A" should be replaced before "sub_01"
    sorted_names = sorted(RENAME_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    
    for old_name, new_name in sorted_names:
        if old_name == new_name:
            continue  # skip identity mappings
        
        # Use word boundary matching to avoid partial replacements
        pattern = r'\b' + re.escape(old_name) + r'\b'
        new_content = re.sub(pattern, new_name, content)
        
        if new_content != content:
            count = len(re.findall(pattern, content))
            total_replacements += count
            print(f"  {old_name:40s} -> {new_name:40s} ({count} occurrences)")
            content = new_content
    
    # Write result
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Total replacements: {total_replacements}")
    print(f"  File size: {original_size} -> {len(content)} bytes")
    return total_replacements


def main():
    base_dir = r"c:\Users\Dokuchaev_ts\1"
    
    c_file = os.path.join(base_dir, "sonic1_pseudo_decompilation.c")
    asm_file = os.path.join(base_dir, "sonic1_full_disassembly.asm")
    
    total = 0
    
    if os.path.exists(c_file):
        total += rename_file(c_file)
    else:
        print(f"WARNING: {c_file} not found!")
    
    if os.path.exists(asm_file):
        total += rename_file(asm_file)
    else:
        print(f"WARNING: {asm_file} not found!")
    
    print(f"\n=== DONE: {total} total replacements across all files ===")
    print(f"Mapping contains {len(RENAME_MAP)} entries")
    print(f"Non-identity mappings: {sum(1 for k,v in RENAME_MAP.items() if k != v)}")


if __name__ == "__main__":
    main()
