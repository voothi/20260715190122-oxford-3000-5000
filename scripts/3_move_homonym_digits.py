#!/usr/bin/env python3
"""
ZID: 20260715190326
Description: Scans the target TSV files for words ending in homonym numbers (including
             digits before parenthetical descriptors) and moves them to a new, separate 'Value' column.
"""

import sys
import os
import re

def extract_annotation_and_sense(word):
    # First extract homonym digit
    match = re.match(r'^([^(]*?)(\d+)(\s*\(.*\))?$', word)
    if match:
        prefix = match.group(1)
        digit = match.group(2)
        suffix = match.group(3) or ""
        word_with_suffix = prefix.strip() + suffix
        sense = digit
    else:
        word_with_suffix = word.strip()
        sense = ""
        
    # Now extract parenthetical annotation
    match_ann = re.search(r'\s+(\(.*\))$', word_with_suffix)
    if match_ann:
        annotation = match_ann.group(1).strip()
        clean_word = word_with_suffix[:-len(match_ann.group(0))].strip()
    else:
        annotation = ""
        clean_word = word_with_suffix
        
    return clean_word, annotation, sense

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
    header_parts = [p.strip() for p in header.split("\t")]
    
    # We always write the target 5-column header
    new_header = "Word\tAnnotation\tSense\tPart of Speech\tLevel\n"
    new_lines = [new_header]
    updated_count = 0
    
    for lno, line in enumerate(lines[1:], 2):
        stripped = line.strip()
        if not stripped:
            new_lines.append("\n")
            continue
            
        parts = stripped.split("\t")
        word = parts[0]
        
        # Map columns dynamically based on the input header size
        if len(header_parts) == 5:
            # Word, Annotation, Sense, Part of Speech, Level
            ann = parts[1] if len(parts) > 1 else ""
            sense = parts[2] if len(parts) > 2 else ""
            pos = parts[3] if len(parts) > 3 else ""
            level = parts[4] if len(parts) > 4 else ""
        elif len(header_parts) == 4:
            # Word, Sense, Part of Speech, Level (old format)
            ann = ""
            sense = parts[1] if len(parts) > 1 else ""
            pos = parts[2] if len(parts) > 2 else ""
            level = parts[3] if len(parts) > 3 else ""
        else:
            # Word, Part of Speech, Level
            ann = ""
            sense = ""
            pos = parts[1] if len(parts) > 1 else ""
            level = parts[2] if len(parts) > 2 else ""
            
        # Parse the word column in case it still has annotation/sense in it
        w_clean, ann_ext, sense_ext = extract_annotation_and_sense(word)
        
        final_ann = ann_ext if ann_ext else ann
        final_sense = sense_ext if sense_ext else sense
        
        if final_sense != sense:
            updated_count += 1
            
        new_line = f"{w_clean}\t{final_ann}\t{final_sense}\t{pos}\t{level}\n"
        new_lines.append(new_line)
        
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        
    print(f"Successfully processed {path}.")
    print(f"  Total lines: {len(lines)}")
    print(f"  Moved/extracted digits for {updated_count} words.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        # Default target paths relative to the repository
        paths = [
            os.path.join(repo_root, "20260715165539-oxford-5000-expanded.en.tsv"),
            os.path.join(repo_root, "20260715160822-oxford-3000.en.tsv")
        ]
        
    for p in paths:
        print(f"Processing path: {p}")
        process_file(p)
        print()
