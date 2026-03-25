#!/usr/bin/env python3
"""Fast renaming for the large .asm file using str.replace instead of regex."""

import os
import sys

# Import the mapping from the main script
sys.path.insert(0, r"c:\Users\Dokuchaev_ts\1")
from rename_functions import RENAME_MAP

def rename_asm_fast(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    original_size = len(content)
    total = 0
    
    # Sort by length descending to avoid partial matches
    sorted_names = sorted(
        [(k, v) for k, v in RENAME_MAP.items() if k != v],
        key=lambda x: len(x[0]), reverse=True
    )
    
    for old_name, new_name in sorted_names:
        if old_name not in content:
            continue
        count = content.count(old_name)
        content = content.replace(old_name, new_name)
        total += count
        print(f"  {old_name:40s} -> {new_name:40s} ({count})")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Total: {total} replacements")
    print(f"  Size: {original_size} -> {len(content)}")
    return total

if __name__ == "__main__":
    asm_file = r"c:\Users\Dokuchaev_ts\1\sonic1_full_disassembly.asm"
    if os.path.exists(asm_file):
        rename_asm_fast(asm_file)
    else:
        print(f"File not found: {asm_file}")
