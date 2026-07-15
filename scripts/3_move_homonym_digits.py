#!/usr/bin/env python3
"""
ZID: 20260715190326
Description: Scans the target TSV files for words ending in homonym numbers (including
             digits before parenthetical descriptors) and moves them to a new, separate 'Value' column.
"""

import sys
import os
import re

def extract_digit(word):
    # Matches a digit either at the end of a word or before a parenthetical suffix
    match = re.match(r'^([^(]*?)(\d+)(\s*\(.*\))?$', word)
    if match:
        prefix = match.group(1)
        digit = match.group(2)
        suffix = match.group(3) or ""
        new_word = prefix.strip() + suffix
        return new_word, digit
    else:
        return word, ""

def process_file(path):
    if not os.path.exists(path):
        print(f"Error: File {path} does not exist!")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    if not lines:
        print(f"Error: File {path} is empty!")
        return
        
    header = lines[0].strip()
    header_parts = header.split("\t")
    
    # Add Value column to header if not already present
    if "Value" not in header_parts:
        new_header = f"{header}\tValue\n"
    else:
        new_header = f"{header}\n"
        
    new_lines = [new_header]
    updated_count = 0
    
    for lno, line in enumerate(lines[1:], 2):
        stripped = line.strip()
        if not stripped:
            new_lines.append("\n")
            continue
            
        parts = stripped.split("\t")
        word = parts[0]
        # Preserve existing columns
        pos = parts[1] if len(parts) > 1 else ""
        level = parts[2] if len(parts) > 2 else ""
        
        # In case the file already has Sense/Value columns, preserve them
        rest = "\t".join(parts[3:]) if len(parts) > 3 else ""
        
        new_word, val = extract_digit(word)
        if val:
            updated_count += 1
            
        if rest:
            # If there's already extra columns, append Value at the end
            new_line = f"{new_word}\t{pos}\t{level}\t{rest}\t{val}\n"
        else:
            new_line = f"{new_word}\t{pos}\t{level}\t{val}\n"
            
        new_lines.append(new_line)
        
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    print(f"Successfully processed {path}.")
    print(f"  Total lines: {len(lines)}")
    print(f"  Moved digits for {updated_count} words.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        paths = [
            r"U:\voothi\20241223170748-kardenwort\data\en\20260715165539-oxford-5000-expanded.en.tsv",
            r"U:\voothi\20241223170748-kardenwort\data\en\20260715160822-oxford-3000.en.tsv"
        ]
        
    for p in paths:
        print(f"Processing path: {p}")
        process_file(p)
        print()
