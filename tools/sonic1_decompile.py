"""
Sonic The Hedgehog (Sega Genesis) - Full ROM Disassembler / Pseudo-Decompiler
Uses Capstone for M68K disassembly with recursive descent analysis.
Produces annotated assembly + pseudo-C for each function.
"""

import struct
import sys
import os
from collections import defaultdict, OrderedDict
from capstone import *
from capstone.m68k import *

ROM_PATH = r"C:\Users\Dokuchaev_ts\Downloads\Sonic The Hedgehog (USA, Europe)\Sonic The Hedgehog (USA, Europe).gen"
OUTPUT_DIR = r"c:\Users\Dokuchaev_ts\1"

# ============================================================
# Sega Genesis constants
# ============================================================
VDP_CONTROL    = 0xC00004
VDP_DATA       = 0xC00000
Z80_BUS_REQ    = 0xA11100
Z80_RESET      = 0xA11200
IO_CTRL_1      = 0xA10009
IO_CTRL_2      = 0xA1000B
IO_CTRL_EXT    = 0xA1000D
IO_DATA_1      = 0xA10003
IO_DATA_2      = 0xA10005
TMSS_REG       = 0xA14000
PSG_PORT       = 0xC00011
Z80_RAM_START  = 0xA00000
RAM_START      = 0xFF0000
RAM_END        = 0xFFFFFF

HW_REGISTERS = {
    0xA00000: "Z80_RAM",
    0xA10001: "IO_VERSION",
    0xA10003: "IO_DATA_1",
    0xA10005: "IO_DATA_2",
    0xA10007: "IO_DATA_EXT",
    0xA10009: "IO_CTRL_1",
    0xA1000B: "IO_CTRL_2",
    0xA1000D: "IO_CTRL_EXT",
    0xA11100: "Z80_BUS_REQ",
    0xA11200: "Z80_RESET",
    0xA14000: "TMSS_REG",
    0xC00000: "VDP_DATA",
    0xC00002: "VDP_DATA_MIRROR",
    0xC00004: "VDP_CTRL",
    0xC00006: "VDP_CTRL_MIRROR",
    0xC00008: "VDP_HVCOUNTER",
    0xC00011: "PSG_PORT",
}

VECTOR_NAMES = [
    "InitialSSP", "EntryPoint", "BusError", "AddressError",
    "IllegalInstruction", "ZeroDivide", "CHKException", "TRAPVException",
    "PrivilegeViolation", "Trace", "LineAEmulator", "LineFEmulator",
    "Reserved_0C", "Reserved_0D", "Reserved_0E", "UninitializedInt",
    "Reserved_10", "Reserved_11", "Reserved_12", "Reserved_13",
    "Reserved_14", "Reserved_15", "Reserved_16", "Reserved_17",
    "SpuriousInterrupt", "IRQ1_ExternalInt", "IRQ2_ExternalInt", "IRQ3_ExternalInt",
    "IRQ4_HBlank", "IRQ5_ExternalInt", "IRQ6_VBlank", "IRQ7_NMI",
]
for i in range(16):
    VECTOR_NAMES.append(f"TRAP_{i}")
for i in range(16):
    VECTOR_NAMES.append(f"Reserved_{0x30+i:02X}")


class SonicROMAnalyzer:
    def __init__(self, rom_path):
        with open(rom_path, 'rb') as f:
            self.rom = f.read()
        self.rom_size = len(self.rom)
        
        # Capstone disassembler for M68000 (big-endian)
        self.md = Cs(CS_ARCH_M68K, CS_MODE_M68K_000)
        self.md.detail = True
        self.md.skipdata = True
        
        # Analysis state
        self.functions = OrderedDict()      # addr -> FunctionInfo
        self.labels = {}                    # addr -> name
        self.xrefs_to = defaultdict(set)    # addr -> set of source addrs
        self.xrefs_from = defaultdict(set)  # addr -> set of target addrs
        self.data_refs = defaultdict(set)   # addr -> set of source addrs
        self.analyzed_addrs = set()         # addresses we've disassembled
        self.code_addrs = set()             # addresses that are code
        self.func_queue = []                # queue of addresses to analyze as functions
        self.comments = {}                  # addr -> comment
        
        # Parse ROM header
        self.parse_header()
    
    def read_long(self, addr):
        """Read a 32-bit big-endian value from ROM."""
        if addr + 4 <= self.rom_size:
            return struct.unpack('>I', self.rom[addr:addr+4])[0]
        return 0
    
    def read_word(self, addr):
        """Read a 16-bit big-endian value from ROM."""
        if addr + 2 <= self.rom_size:
            return struct.unpack('>H', self.rom[addr:addr+2])[0]
        return 0
    
    def read_byte(self, addr):
        if addr < self.rom_size:
            return self.rom[addr]
        return 0
    
    def parse_header(self):
        """Parse the Sega Genesis ROM header."""
        self.initial_ssp = self.read_long(0)
        self.entry_point = self.read_long(4)
        
        # Parse vector table
        self.vectors = {}
        for i in range(64):
            addr = i * 4
            target = self.read_long(addr)
            self.vectors[i] = target
            if i < len(VECTOR_NAMES):
                self.labels[addr] = f"Vec_{VECTOR_NAMES[i]}"
        
        # Parse ROM header at 0x100
        self.console_name = self.rom[0x100:0x110].decode('ascii', errors='replace').strip()
        self.copyright = self.rom[0x110:0x120].decode('ascii', errors='replace').strip()
        self.domestic_name = self.rom[0x120:0x150].decode('ascii', errors='replace').strip()
        self.overseas_name = self.rom[0x150:0x180].decode('ascii', errors='replace').strip()
        self.serial_number = self.rom[0x180:0x18E].decode('ascii', errors='replace').strip()
        self.rom_start = self.read_long(0x1A0)
        self.rom_end = self.read_long(0x1A4)
        self.ram_start_addr = self.read_long(0x1A8)
        self.ram_end_addr = self.read_long(0x1AC)
        
        print(f"Console: {self.console_name}")
        print(f"Game: {self.overseas_name}")
        print(f"Entry: 0x{self.entry_point:X}")
        print(f"SSP: 0x{self.initial_ssp:X}")
        print(f"ROM: 0x{self.rom_start:X}-0x{self.rom_end:X}")
    
    def get_label(self, addr):
        """Get or generate a label for an address."""
        if addr in self.labels:
            return self.labels[addr]
        if addr in self.functions:
            return self.functions[addr].name
        return None
    
    def add_label(self, addr, name=None):
        """Add a label for an address."""
        if addr not in self.labels:
            if name:
                self.labels[addr] = name
            elif addr in self.functions:
                self.labels[addr] = self.functions[addr].name
            else:
                self.labels[addr] = f"loc_{addr:06X}"
    
    def hw_reg_name(self, addr):
        """Get hardware register name if applicable."""
        if addr in HW_REGISTERS:
            return HW_REGISTERS[addr]
        if 0xA00000 <= addr <= 0xA0FFFF:
            return f"Z80_RAM+0x{addr-0xA00000:X}"
        if 0xFF0000 <= addr <= 0xFFFFFF:
            return f"RAM_{addr:06X}"
        return None
    
    def is_rom_addr(self, addr):
        return 0 <= addr < self.rom_size
    
    def disassemble_at(self, addr, max_bytes=None):
        """Disassemble instructions starting at addr."""
        if not self.is_rom_addr(addr):
            return []
        end = min(self.rom_size, addr + (max_bytes or 0x10000))
        code = self.rom[addr:end]
        return list(self.md.disasm(code, addr))
    
    def analyze_function(self, start_addr, name=None):
        """Recursively analyze a function using recursive descent."""
        if start_addr in self.functions:
            return
        if not self.is_rom_addr(start_addr):
            return
        if start_addr < 0x200:  # Skip vector table area
            return
            
        func = FunctionInfo(start_addr, name or f"sub_{start_addr:06X}")
        self.functions[start_addr] = func
        self.labels[start_addr] = func.name
        
        # BFS through the function
        queue = [start_addr]
        visited = set()
        
        while queue:
            addr = queue.pop(0)
            if addr in visited:
                continue
            if not self.is_rom_addr(addr):
                continue
            # Don't analyze into the vector table
            if addr < 0x200 and start_addr >= 0x200:
                continue
            # Don't analyze into a different existing function
            if addr != start_addr and addr in self.functions:
                continue
            visited.add(addr)
            
            instructions = self.disassemble_at(addr)
            if not instructions:
                continue
                
            for insn in instructions:
                ea = insn.address
                if ea in visited and ea != addr:
                    break
                visited.add(ea)
                self.code_addrs.add(ea)
                self.analyzed_addrs.add(ea)
                
                func.instructions[ea] = insn
                func.end_addr = max(func.end_addr, ea + insn.size)
                
                # Skip data pseudo-instructions
                if insn.id == 0:
                    break
                
                # Analyze the instruction
                mnemonic = insn.mnemonic.lower()
                
                # Check for branch/jump targets
                is_branch = False
                is_call = False
                is_unconditional = False
                is_return = False
                target = None
                
                if mnemonic in ('rts', 'rte', 'rtr'):
                    is_return = True
                elif mnemonic == 'jmp':
                    is_branch = True
                    is_unconditional = True
                    target = self._get_branch_target(insn)
                elif mnemonic == 'bra' or mnemonic == 'bra.w' or mnemonic == 'bra.s':
                    is_branch = True
                    is_unconditional = True
                    target = self._get_branch_target(insn)
                elif mnemonic.startswith('b') and mnemonic not in ('btst', 'bset', 'bclr', 'bchg', 'bfchg', 'bfclr', 'bfexts', 'bfextu', 'bfffo', 'bfins', 'bfset', 'bftst'):
                    is_branch = True
                    target = self._get_branch_target(insn)
                elif mnemonic in ('dbra', 'dbeq', 'dbne', 'dbgt', 'dbge', 'dblt', 'dble', 'dbhi', 'dbls', 'dbcc', 'dbcs', 'dbmi', 'dbpl', 'dbvc', 'dbvs', 'dbf', 'dbt'):
                    is_branch = True
                    target = self._get_branch_target(insn)
                elif mnemonic == 'jsr' or mnemonic == 'bsr' or mnemonic == 'bsr.w' or mnemonic == 'bsr.s':
                    is_call = True
                    target = self._get_branch_target(insn)
                
                if target is not None and self.is_rom_addr(target):
                    self.xrefs_from[ea].add(target)
                    self.xrefs_to[target].add(ea)
                    
                    if is_call:
                        # Queue as new function
                        if target not in self.functions:
                            self.func_queue.append(target)
                    elif is_branch:
                        # Same function branch - but don't jump into another function
                        if target not in self.functions and target >= 0x200:
                            self.add_label(target)
                            queue.append(target)
                        elif target in self.functions and target != start_addr:
                            # This is a tail call, treat it as such
                            pass
                
                # Check for data references (absolute addresses)
                self._check_data_refs(insn)
                
                if is_return:
                    break
                if is_unconditional and not is_call:
                    break
                if is_call:
                    # Continue after call
                    pass
        
        # Sort instructions
        func.instructions = OrderedDict(sorted(func.instructions.items()))
    
    def _parse_target_from_opstr(self, insn):
        """Parse branch target from op_str when operands aren't available."""
        op_str = insn.op_str.strip()
        # Remove size suffixes like .l, .w
        clean = op_str.split('(')[0].strip()  # Remove (pc,...) parts
        for suffix in ('.l', '.w', '.b', '.s'):
            clean = clean.replace(suffix, '')
        clean = clean.strip()
        
        if clean.startswith('$'):
            try:
                return int(clean[1:], 16)
            except ValueError:
                pass
        elif clean.startswith('0x'):
            try:
                return int(clean, 16)
            except ValueError:
                pass
        elif clean.startswith('#$'):
            try:
                return int(clean[2:], 16)
            except ValueError:
                pass
        elif clean.startswith('#0x'):
            try:
                return int(clean[1:], 16)
            except ValueError:
                pass
        return None

    def _get_branch_target(self, insn):
        """Extract branch/call target address from instruction."""
        if insn.id == 0:
            return None
        try:
            operands = insn.operands
        except Exception:
            return self._parse_target_from_opstr(insn)
        
        # Check ALL operands for BR_DISP (dbra has it as 2nd operand)
        for op in operands:
            if op.type == M68K_OP_BR_DISP:
                return op.br_disp.disp + insn.address + 2  # PC-relative
        
        # For JSR/JMP with absolute addressing: MEM with base=0, index=0
        if len(operands) > 0:
            op = operands[0]
            if op.type == M68K_OP_MEM:
                # If base and index are both 0, it's absolute - parse from op_str
                if op.mem.base_reg == 0 and op.mem.index_reg == 0:
                    return self._parse_target_from_opstr(insn)
                # PC-relative with disp only (no index)
                if op.mem.base_reg == 25 and op.mem.index_reg == 0:  # base=PC
                    return op.mem.disp + insn.address + 2
                # If has index register, can't resolve statically
                return None
            elif op.type == M68K_OP_IMM:
                return op.imm
        
        # Fallback: try parsing from op_str
        return self._parse_target_from_opstr(insn)
    
    def _check_data_refs(self, insn):
        """Check instruction for data references to known addresses."""
        if insn.id == 0:  # SKIPDATA pseudo-instruction
            return
        try:
            ops = insn.operands
        except Exception:
            return
        for op in ops:
            addr = None
            if op.type == M68K_OP_IMM:
                val = op.imm
                if 0xA00000 <= val <= 0xFFFFFF or (0 < val < self.rom_size and val > 0x200):
                    addr = val
            elif op.type == M68K_OP_MEM:
                if hasattr(op.mem, 'disp') and op.mem.disp:
                    val = op.mem.disp & 0xFFFFFFFF
                    if val in HW_REGISTERS or 0xFF0000 <= val <= 0xFFFFFF:
                        addr = val
            if addr is not None:
                self.data_refs[addr].add(insn.address)
    
    def analyze_all(self):
        """Perform full analysis of the ROM."""
        print("\n=== Starting Analysis ===")
        
        # Phase 1: Start from vector table entries
        print("Phase 1: Analyzing vector table entries...")
        for i in range(1, 64):  # Skip SSP at vector 0
            target = self.vectors.get(i, 0)
            if 0x200 <= target < self.rom_size:
                name = VECTOR_NAMES[i] if i < len(VECTOR_NAMES) else f"Vec{i}"
                self.func_queue.append(target)
                self.labels[target] = name
        
        # Special names
        self.labels[self.entry_point] = "EntryPoint"
        
        # Phase 1.5: Full ROM scan for all BSR/JSR targets
        print("Phase 1.5: Scanning entire ROM for call targets...")
        full_scan_targets = set()
        for insn in self.md.disasm(self.rom[0x200:], 0x200):
            if insn.id == 0:
                continue
            mn = insn.mnemonic.lower()
            if mn in ('jsr', 'bsr', 'bsr.w', 'bsr.s'):
                target = self._get_branch_target(insn)
                if target and 0x200 <= target < self.rom_size:
                    full_scan_targets.add(target)
        print(f"  Found {len(full_scan_targets)} unique call targets")
        for t in sorted(full_scan_targets):
            if t not in self.func_queue:
                self.func_queue.append(t)
        
        # Phase 2: Process function queue  
        print("Phase 2: Recursive function analysis...")
        iteration = 0
        while self.func_queue:
            addr = self.func_queue.pop(0)
            if addr in self.functions:
                continue
            name = self.labels.get(addr, None)
            self.analyze_function(addr, name)
            iteration += 1
            if iteration % 100 == 0:
                print(f"  Analyzed {iteration} functions, {len(self.func_queue)} remaining...")
        
        print(f"  Total functions after recursive descent: {len(self.functions)}")
        
        # Phase 3: Linear sweep for missed functions
        print("Phase 3: Linear sweep for missed code...")
        missed = 0
        addr = 0x200
        while addr < self.rom_size - 2:
            if addr not in self.code_addrs:
                # Check if this looks like valid code
                word = self.read_word(addr)
                if self._looks_like_code_start(addr, word):
                    self.analyze_function(addr)
                    # Process any new functions discovered
                    while self.func_queue:
                        faddr = self.func_queue.pop(0)
                        if faddr not in self.functions:
                            self.analyze_function(faddr)
                    missed += 1
                    if addr in self.functions:
                        addr = self.functions[addr].end_addr
                        continue
            addr += 2  # M68K is word-aligned
        
        print(f"  Found {missed} additional functions via linear sweep")
        print(f"  Total functions: {len(self.functions)}")
        
        # Sort functions by address
        self.functions = OrderedDict(sorted(self.functions.items()))
    
    def _looks_like_code_start(self, addr, word):
        """Heuristic: does this look like a function start?"""
        # Common M68K function prologues
        # LINK A6, #xx  -> 0x4E56
        if word == 0x4E56:
            return True
        # MOVEM.L regs, -(SP) -> 0x48E7
        if word == 0x48E7:
            return True
        # LEA (xx,PC), Ax -> 0x41FA, 0x43FA, 0x45FA, 0x47FA, 0x49FA, 0x4BFA, 0x4DFA, 0x4FFA
        if (word & 0xF1FF) == 0x41FA:
            return True
        # MOVEM.L regs, -(A7) -> 0x48E7
        if word == 0x48E7:
            return True
        # MOVEQ #xx, D0 -> 0x70xx (common start)
        if (word & 0xFF00) == 0x7000 and addr in self.xrefs_to:
            return True
        # If this address is referenced by other code as a call target
        if addr in self.xrefs_to:
            return True
        # Check if previous word was RTS (0x4E75) or RTE (0x4E73) - new function after return
        if addr >= 2:
            prev_word = self.read_word(addr - 2)
            if prev_word in (0x4E75, 0x4E73):  # RTS, RTE
                # Verify this word is a valid M68K instruction
                test_insns = self.disassemble_at(addr, 4)
                if test_insns and test_insns[0].id != 0 and test_insns[0].address == addr:
                    return True
        return False
    
    def format_operand_annotated(self, insn, op_str):
        """Add annotations to operands (register names, hw addresses)."""
        # Look for hex values that might be HW registers or RAM addresses
        annotations = []
        for addr, name in HW_REGISTERS.items():
            hex_str = f"${addr:x}"
            hex_str2 = f"0x{addr:x}"
            if hex_str in op_str.lower() or hex_str2 in op_str.lower():
                annotations.append(name)
        return annotations
    
    def generate_pseudocode(self, func):
        """Generate pseudo-C code for a function."""
        lines = []
        lines.append(f"// Function: {func.name}")
        lines.append(f"// Address: 0x{func.start_addr:06X} - 0x{func.end_addr:06X}")
        lines.append(f"// Size: {func.end_addr - func.start_addr} bytes")
        
        # Count calls and branches
        calls = []
        for ea, insn in func.instructions.items():
            mn = insn.mnemonic.lower()
            if mn in ('jsr', 'bsr', 'bsr.w', 'bsr.s'):
                target = self._get_branch_target(insn)
                if target:
                    tname = self.labels.get(target, f"sub_{target:06X}")
                    calls.append(tname)
        
        if calls:
            lines.append(f"// Calls: {', '.join(set(calls))}")
        
        # Callers
        callers = []
        for src_addr in self.xrefs_to.get(func.start_addr, set()):
            for faddr, f in self.functions.items():
                if src_addr in f.instructions:
                    callers.append(f.name)
                    break
        if callers:
            lines.append(f"// Called by: {', '.join(set(callers))}")
        
        lines.append(f"void {func.name}(void) {{")
        
        indent = "    "
        prev_was_branch = False
        
        for ea, insn in func.instructions.items():
            mn = insn.mnemonic.lower()
            ops = insn.op_str
            
            # Add label if referenced
            label = self.get_label(ea)
            if label and ea != func.start_addr:
                lines.append(f"  {label}:")
            
            # Generate pseudo-C based on instruction type
            comment = ""
            pseudo = ""
            
            # Annotations for HW registers
            annotations = self.format_operand_annotated(insn, ops)
            if annotations:
                comment = f" // {', '.join(annotations)}"
            
            # Convert to pseudo-C
            if mn == 'rts':
                pseudo = f"{indent}return;"
            elif mn == 'rte':
                pseudo = f"{indent}return; // from exception"
            elif mn in ('nop',):
                pseudo = f"{indent}// nop"
            elif mn in ('jsr', 'bsr', 'bsr.w', 'bsr.s'):
                target = self._get_branch_target(insn)
                if target:
                    tname = self.labels.get(target, f"sub_{target:06X}")
                    pseudo = f"{indent}{tname}();"
                else:
                    pseudo = f"{indent}call({ops});"
            elif mn in ('bra', 'bra.w', 'bra.s', 'jmp'):
                target = self._get_branch_target(insn)
                if target:
                    tname = self.labels.get(target, f"loc_{target:06X}")
                    # Check if it's a tail call to another function
                    if target in self.functions and target != func.start_addr:
                        pseudo = f"{indent}return {tname}(); // tail call"
                    else:
                        pseudo = f"{indent}goto {tname};"
                else:
                    pseudo = f"{indent}goto {ops}; // indirect jump"
            elif mn.startswith('beq'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (Z == 1) goto {tname};"
            elif mn.startswith('bne'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (Z == 0) goto {tname};"
            elif mn.startswith('bcc') or mn.startswith('bhs'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (C == 0) goto {tname}; // unsigned >="
            elif mn.startswith('bcs') or mn.startswith('blo'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (C == 1) goto {tname}; // unsigned <"
            elif mn.startswith('bgt'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (signed >) goto {tname};"
            elif mn.startswith('bge'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (signed >=) goto {tname};"
            elif mn.startswith('blt'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (signed <) goto {tname};"
            elif mn.startswith('ble'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (signed <=) goto {tname};"
            elif mn.startswith('bmi'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (N == 1) goto {tname}; // minus"
            elif mn.startswith('bpl'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (N == 0) goto {tname}; // plus"
            elif mn.startswith('bhi'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (unsigned >) goto {tname};"
            elif mn.startswith('bls'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (unsigned <=) goto {tname};"
            elif mn.startswith('bvs'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (V == 1) goto {tname};"
            elif mn.startswith('bvc'):
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                pseudo = f"{indent}if (V == 0) goto {tname};"
            elif mn.startswith('db'):  # DBcc loops
                target = self._get_branch_target(insn)
                tname = self.labels.get(target, f"loc_{target:06X}") if target else ops
                cond = mn[2:] if len(mn) > 2 else "ra"
                pseudo = f"{indent}if (!{cond} && --{ops.split(',')[0].strip()} != -1) goto {tname}; // loop"
            elif mn.startswith('move') or mn == 'movea':
                pseudo = f"{indent}// {mn} {ops}{comment}"
                # Try to make it more readable
                parts = ops.split(',')
                if len(parts) == 2:
                    src = parts[0].strip()
                    dst = parts[1].strip()
                    pseudo = f"{indent}{dst} = {src};{comment}"
            elif mn in ('add', 'addi', 'addq', 'adda', 'add.w', 'add.l', 'add.b', 
                         'addi.w', 'addi.l', 'addi.b', 'addq.w', 'addq.l', 'addq.b',
                         'adda.w', 'adda.l'):
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} += {parts[0].strip()};{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('sub', 'subi', 'subq', 'suba', 'sub.w', 'sub.l', 'sub.b',
                         'subi.w', 'subi.l', 'subi.b', 'subq.w', 'subq.l', 'subq.b',
                         'suba.w', 'suba.l'):
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} -= {parts[0].strip()};{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('and', 'andi', 'and.w', 'and.l', 'and.b', 'andi.w', 'andi.l', 'andi.b'):
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} &= {parts[0].strip()};{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('or', 'ori', 'or.w', 'or.l', 'or.b', 'ori.w', 'ori.l', 'ori.b'):
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} |= {parts[0].strip()};{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('eor', 'eori', 'eor.w', 'eor.l', 'eor.b', 'eori.w', 'eori.l', 'eori.b'):
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} ^= {parts[0].strip()};{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('cmp', 'cmpi', 'cmpa', 'cmp.w', 'cmp.l', 'cmp.b', 
                         'cmpi.w', 'cmpi.l', 'cmpi.b', 'cmpa.w', 'cmpa.l'):
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}compare({parts[1].strip()}, {parts[0].strip()});{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('tst', 'tst.w', 'tst.l', 'tst.b'):
                pseudo = f"{indent}test({ops});{comment}"
            elif mn in ('clr', 'clr.w', 'clr.l', 'clr.b'):
                pseudo = f"{indent}{ops} = 0;{comment}"
            elif mn in ('neg', 'neg.w', 'neg.l', 'neg.b'):
                pseudo = f"{indent}{ops} = -{ops};{comment}"
            elif mn in ('not', 'not.w', 'not.l', 'not.b'):
                pseudo = f"{indent}{ops} = ~{ops};{comment}"
            elif mn in ('ext', 'ext.w', 'ext.l'):
                pseudo = f"{indent}{ops} = sign_extend({ops});{comment}"
            elif mn in ('swap',):
                pseudo = f"{indent}{ops} = swap_words({ops});{comment}"
            elif mn in ('lsl', 'lsr', 'asl', 'asr', 'rol', 'ror',
                         'lsl.w', 'lsl.l', 'lsl.b', 'lsr.w', 'lsr.l', 'lsr.b',
                         'asl.w', 'asl.l', 'asl.b', 'asr.w', 'asr.l', 'asr.b',
                         'rol.w', 'rol.l', 'rol.b', 'ror.w', 'ror.l', 'ror.b'):
                parts = ops.split(',')
                if len(parts) == 2:
                    op = '<<' if 'l' in mn[:3] else '>>'
                    if 'ro' in mn[:3]:
                        pseudo = f"{indent}{parts[1].strip()} = rotate_{mn[:3]}({parts[1].strip()}, {parts[0].strip()});{comment}"
                    else:
                        pseudo = f"{indent}{parts[1].strip()} {op}= {parts[0].strip()};{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('btst', 'bset', 'bclr', 'bchg',
                         'btst.b', 'btst.l', 'bset.b', 'bset.l', 'bclr.b', 'bclr.l', 'bchg.b', 'bchg.l'):
                parts = ops.split(',')
                base = mn.split('.')[0]
                if len(parts) == 2:
                    if base == 'btst':
                        pseudo = f"{indent}test_bit({parts[1].strip()}, {parts[0].strip()});{comment}"
                    elif base == 'bset':
                        pseudo = f"{indent}set_bit({parts[1].strip()}, {parts[0].strip()});{comment}"
                    elif base == 'bclr':
                        pseudo = f"{indent}clear_bit({parts[1].strip()}, {parts[0].strip()});{comment}"
                    elif base == 'bchg':
                        pseudo = f"{indent}toggle_bit({parts[1].strip()}, {parts[0].strip()});{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('lea', 'lea.l'):
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} = &{parts[0].strip()};{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('pea', 'pea.l'):
                pseudo = f"{indent}push(&{ops});{comment}"
            elif mn == 'link':
                parts = ops.split(',')
                if len(parts) == 2:
                    pseudo = f"{indent}// frame setup: {parts[0].strip()}, size={parts[1].strip()}"
                else:
                    pseudo = f"{indent}// link {ops}"
            elif mn == 'unlk':
                pseudo = f"{indent}// frame teardown: {ops}"
            elif mn.startswith('movem'):
                pseudo = f"{indent}// save/restore regs: {ops}{comment}"
            elif mn in ('mulu', 'mulu.w', 'muls', 'muls.w'):
                parts = ops.split(',')
                sign = 'signed' if 'muls' in mn else 'unsigned'
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} *= {parts[0].strip()}; // {sign}{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn in ('divu', 'divu.w', 'divs', 'divs.w'):
                parts = ops.split(',')
                sign = 'signed' if 'divs' in mn else 'unsigned'
                if len(parts) == 2:
                    pseudo = f"{indent}{parts[1].strip()} /= {parts[0].strip()}; // {sign}, remainder in upper word{comment}"
                else:
                    pseudo = f"{indent}// {mn} {ops}{comment}"
            elif mn == 'trap':
                pseudo = f"{indent}trap({ops});{comment}"
            elif mn in ('stop',):
                pseudo = f"{indent}stop({ops}); // halt CPU{comment}"
            elif mn == 'illegal':
                pseudo = f"{indent}__illegal(); // trigger exception{comment}"
            elif mn in ('ori.b', 'ori.w', 'ori.l') and 'sr' in ops.lower():
                pseudo = f"{indent}SR |= {ops.split(',')[0].strip()};{comment}"
            elif mn in ('andi.b', 'andi.w', 'andi.l') and 'sr' in ops.lower():
                pseudo = f"{indent}SR &= {ops.split(',')[0].strip()};{comment}"
            elif mn in ('move.w', 'move.l') and 'sr' in ops.lower():
                pseudo = f"{indent}// {mn} {ops} (status register){comment}"
            else:
                pseudo = f"{indent}asm(\"{mn} {ops}\");{comment}"
            
            lines.append(f"/* {ea:06X} */  {pseudo}")
        
        lines.append("}")
        return '\n'.join(lines)
    
    def export_full_disassembly(self, filepath):
        """Export full annotated disassembly."""
        print(f"\nExporting disassembly to: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("; =============================================================\n")
            f.write(f"; {self.overseas_name}\n")
            f.write(f"; Console: {self.console_name}\n")
            f.write(f"; Copyright: {self.copyright}\n")
            f.write(f"; Serial: {self.serial_number}\n")
            f.write("; Processor: Motorola 68000\n")
            f.write(f"; ROM Size: 0x{self.rom_size:X} ({self.rom_size // 1024} KB)\n")
            f.write(f"; Entry Point: 0x{self.entry_point:06X}\n")
            f.write(f"; Initial SSP: 0x{self.initial_ssp:08X}\n")
            f.write(f"; Total Functions: {len(self.functions)}\n")
            f.write("; =============================================================\n\n")
            
            # Vector table
            f.write("; ==================== VECTOR TABLE ====================\n")
            for i in range(64):
                target = self.vectors.get(i, 0)
                name = VECTOR_NAMES[i] if i < len(VECTOR_NAMES) else f"Vector_{i}"
                tname = self.labels.get(target, f"0x{target:06X}")
                f.write(f";  {i*4:03X}: {name:30s} -> {tname} (0x{target:06X})\n")
            f.write("\n")
            
            # ROM Header
            f.write("; ==================== ROM HEADER ====================\n")
            f.write(f"; 0x100: Console:  {self.console_name}\n")
            f.write(f"; 0x110: Copyright: {self.copyright}\n")
            f.write(f"; 0x120: Domestic:  {self.domestic_name}\n")
            f.write(f"; 0x150: Overseas:  {self.overseas_name}\n")
            f.write(f"; 0x180: Serial:    {self.serial_number}\n")
            f.write(f"; 0x1A0: ROM Start: 0x{self.rom_start:08X}\n")
            f.write(f"; 0x1A4: ROM End:   0x{self.rom_end:08X}\n")
            f.write(f"; 0x1A8: RAM Start: 0x{self.ram_start_addr:08X}\n")
            f.write(f"; 0x1AC: RAM End:   0x{self.ram_end_addr:08X}\n")
            f.write("\n\n")
            
            # Function cross-reference table
            f.write("; ==================== FUNCTION TABLE ====================\n")
            for addr, func in self.functions.items():
                size = func.end_addr - func.start_addr
                ncalls = sum(1 for ea, insn in func.instructions.items() 
                           if insn.mnemonic.lower() in ('jsr', 'bsr', 'bsr.w', 'bsr.s'))
                f.write(f";  0x{addr:06X}: {func.name:40s} (size: 0x{size:X}, instructions: {len(func.instructions)}, calls: {ncalls})\n")
            f.write(f"; Total: {len(self.functions)} functions\n\n\n")
            
            # Full disassembly by function
            f.write("; ==================== CODE ====================\n\n")
            
            # Track what ROM ranges are covered by functions
            covered = set()
            
            for addr, func in self.functions.items():
                f.write(f"; {'='*60}\n")
                f.write(f"; FUNCTION: {func.name}\n")
                f.write(f"; Address:  0x{func.start_addr:06X} - 0x{func.end_addr:06X}\n")
                f.write(f"; Size:     {func.end_addr - func.start_addr} bytes\n")
                
                # Show callers
                callers = set()
                for src in self.xrefs_to.get(func.start_addr, set()):
                    for fa, ff in self.functions.items():
                        if src in ff.instructions:
                            callers.add(ff.name)
                            break
                if callers:
                    f.write(f"; Called by: {', '.join(sorted(callers))}\n")
                
                f.write(f"; {'='*60}\n")
                f.write(f"{func.name}:\n")
                
                for ea, insn in func.instructions.items():
                    covered.add(ea)
                    
                    # Label
                    label = self.get_label(ea)
                    if label and ea != func.start_addr:
                        f.write(f"\n{label}:\n")
                    
                    # Hex bytes
                    raw_bytes = ' '.join(f'{b:02X}' for b in self.rom[ea:ea+insn.size])
                    
                    # Annotation
                    ann = ""
                    annotations = self.format_operand_annotated(insn, insn.op_str)
                    if annotations:
                        ann = f"  ; {', '.join(annotations)}"
                    
                    # Check if branch target has a name
                    mn = insn.mnemonic.lower()
                    op_display = insn.op_str
                    if mn in ('jsr', 'bsr', 'bsr.w', 'bsr.s', 'jmp', 'bra', 'bra.w', 'bra.s') or \
                       (mn.startswith('b') and mn not in ('btst', 'bset', 'bclr', 'bchg')):
                        target = self._get_branch_target(insn)
                        if target and target in self.labels:
                            op_display = self.labels[target]
                    
                    f.write(f"  {ea:06X}  {raw_bytes:24s}  {insn.mnemonic:10s} {op_display}{ann}\n")
                
                f.write("\n\n")
            
            # Data sections (uncovered areas)
            f.write("; ==================== DATA ====================\n\n")
            
            in_data = False
            data_start = 0
            addr = 0x200  # Skip vector table
            while addr < self.rom_size:
                if addr not in covered:
                    if not in_data:
                        data_start = addr
                        in_data = True
                        # Check if this is a known data reference
                        dname = self.labels.get(addr, None)
                        if dname:
                            f.write(f"\n{dname}:\n")
                        elif addr in self.data_refs:
                            f.write(f"\ndat_{addr:06X}: ; referenced from: {', '.join(f'0x{x:06X}' for x in sorted(self.data_refs[addr])[:5])}\n")
                    
                    # Write data bytes (16 per line)
                    if addr % 16 == 0 or not in_data:
                        line_end = min(addr + 16, self.rom_size)
                        # Find next code addr
                        line_end = min(line_end, addr + 16)
                        for check in range(addr + 1, line_end):
                            if check in covered:
                                line_end = check
                                break
                        
                        raw = self.rom[addr:line_end]
                        hex_str = ' '.join(f'{b:02X}' for b in raw)
                        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw)
                        f.write(f"  {addr:06X}  {hex_str:48s}  ; {ascii_str}\n")
                        addr = line_end
                        continue
                else:
                    in_data = False
                addr += 1
            
            f.write("\n; === END OF DISASSEMBLY ===\n")
        
        print(f"Disassembly written: {os.path.getsize(filepath)} bytes")
    
    def export_pseudocode(self, filepath):
        """Export pseudo-C decompilation for all functions."""
        print(f"\nExporting pseudo-C to: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("/*\n")
            f.write(f" * {self.overseas_name}\n")
            f.write(f" * Pseudo-C Decompilation\n")
            f.write(f" * Processor: Motorola 68000 (Sega Genesis)\n")
            f.write(f" * Total Functions: {len(self.functions)}\n")
            f.write(f" *\n")
            f.write(f" * NOTE: This is automated pseudo-decompilation from M68K assembly.\n")
            f.write(f" * Register names (d0-d7, a0-a7) are used as variable names.\n")
            f.write(f" * Memory accesses use M68K addressing mode notation.\n")
            f.write(f" */\n\n")
            
            f.write("#include <stdint.h>\n\n")
            
            # Hardware register definitions
            f.write("// === Hardware Registers ===\n")
            for addr, name in sorted(HW_REGISTERS.items()):
                f.write(f"#define {name:20s} (*(volatile uint16_t*)0x{addr:06X})\n")
            f.write("\n")
            
            # Forward declarations
            f.write("// === Forward Declarations ===\n")
            for addr, func in self.functions.items():
                f.write(f"void {func.name}(void); // 0x{addr:06X}\n")
            f.write("\n\n")
            
            # Function bodies
            for addr, func in self.functions.items():
                f.write(f"\n{'/'*60}\n")
                pseudo = self.generate_pseudocode(func)
                f.write(pseudo)
                f.write("\n\n")
            
            f.write("// === END OF DECOMPILATION ===\n")
        
        print(f"Pseudo-C written: {os.path.getsize(filepath)} bytes")


class FunctionInfo:
    def __init__(self, start_addr, name):
        self.start_addr = start_addr
        self.end_addr = start_addr
        self.name = name
        self.instructions = OrderedDict()


def main():
    print("=" * 60)
    print("Sonic The Hedgehog - Full ROM Decompiler")
    print("=" * 60)
    
    analyzer = SonicROMAnalyzer(ROM_PATH)
    analyzer.analyze_all()
    
    # Export
    asm_path = os.path.join(OUTPUT_DIR, "sonic1_full_disassembly.asm")
    c_path = os.path.join(OUTPUT_DIR, "sonic1_pseudo_decompilation.c")
    
    analyzer.export_full_disassembly(asm_path)
    analyzer.export_pseudocode(c_path)
    
    print("\n" + "=" * 60)
    print("DONE!")
    print(f"  Disassembly: {asm_path}")
    print(f"  Pseudo-C:    {c_path}")
    print(f"  Functions:   {len(analyzer.functions)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
