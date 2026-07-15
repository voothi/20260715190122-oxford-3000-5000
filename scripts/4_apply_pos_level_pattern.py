#!/usr/bin/env python3
"""
ZID: 20260715190326
Description: Updates the target TSV file's 'Part of Speech' and 'Level' columns based on the 
             copy-paste file, applying the multi-level pattern.
             - If multiple levels exist in the copy-paste string, the exact POS/level string is kept
               in 'Part of Speech' and combined in 'Level' (e.g. n. A2, v. B1 -> Level: A2, B1).
             - If a single level exists, POS is kept clean, and Level holds the single level value.
"""

import sys
import os
import re

pos_pattern = re.compile(r'\b(modal v\.|modal|n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|adj\./adv\.|exclam\.|indefinite article|definite article)')

def clean_word_designations(w):
    w = w.strip()
    while True:
        prev = w
        w = re.sub(r'\s+[A-Z][12]\b\s*,?$', '', w, flags=re.IGNORECASE)
        w = re.sub(r'\s+(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|exclam\.|n|v|adj|adv|prep|pron|conj|det)\b\s*,?$', '', w, flags=re.IGNORECASE)
        w = re.sub(r'[,.\s]+$', '', w)
        if w == prev:
            break
    w = w.replace("\xa0", " ")
    return w

def get_parsed_pos_level_from_cp(line):
    line = line.strip()
    if not line:
        return "", ""
        
    if line.startswith("number ") or line == "number":
        pos_level_part = line[6:].strip()
    else:
        match = pos_pattern.search(line)
        if not match:
            return "", ""
        start_pos_idx = match.start()
        pos_level_part = line[start_pos_idx:].strip()
    
    subparts = re.split(r',\s*(?=(?:modal v\.|modal|n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|adj\./adv\.|exclam\.|indefinite article|definite article))', pos_level_part)
    
    parsed_subparts = []
    for sub in subparts:
        sub = sub.strip()
        match_lvl = re.search(r'([AB-Y][12](?:,\s*[AB-Y][12])?)$', sub)
        level = ""
        pos = sub
        if match_lvl:
            level = match_lvl.group(1)
            pos = sub[:-len(level)].strip()
        pos = re.sub(r',\s*$', '', pos).strip()
        parsed_subparts.append((pos, level))
    
    # Check unique levels
    levels_found = [l for p, l in parsed_subparts if l]
    unique_levels = []
    for l in levels_found:
        sub_lvls = [sl.strip() for sl in l.split(",") if sl.strip()]
        for sl in sub_lvls:
            if sl not in unique_levels:
                unique_levels.append(sl)
                
    if len(unique_levels) > 1:
        # Multiple levels pattern: POS contains the exact raw string, Level has the levels list
        pos_col = re.sub(r'\s+', ' ', pos_level_part)
        pos_col = re.sub(r',\s*$', '', pos_col).strip()
        lvl_col = ", ".join(unique_levels)
    else:
        # Single level pattern: POS has POS only, Level has Level
        pos_col = ", ".join(p for p, l in parsed_subparts if p)
        pos_col = re.sub(r'\s+', ' ', pos_col)
        pos_col = re.sub(r',\s*$', '', pos_col)
        pos_col = re.sub(r'^,\s*', '', pos_col)
        lvl_col = unique_levels[0] if unique_levels else ""
        
    return pos_col, lvl_col

def extract_homonym_digit(w):
    match = re.match(r'^([^(]*?)(\d+)(\s*\(.*\))?$', w)
    if match:
        prefix = match.group(1)
        digit = match.group(2)
        suffix = match.group(3) or ""
        new_word = prefix.strip() + suffix
        return new_word, digit
    else:
        return w, ""

def main():
    path_cp = r"C:\Users\voothi\Desktop\20260715160822-oxford-3000-copy-paste.en.tsv"
    path_target = r"U:\voothi\20241223170748-kardenwort\data\en\20260715160822-oxford-3000.en.tsv"

    print(f"Reading copy-paste file: {path_cp}")
    output_lines = []
    processed_count = 0
    
    with open(path_cp, "r", encoding="utf-8") as f:
        for lno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            pos_starts = ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.', 'pron.', 'det.', 'exclam.']
            if any(line.startswith(ps) for ps in pos_starts):
                continue
                
            if line.startswith("number ") or line == "number":
                word = "number"
            else:
                match = pos_pattern.search(line)
                if not match:
                    word = clean_word_designations(line)
                else:
                    word = clean_word_designations(line[:match.start()])
            
            if not word:
                continue
                
            w_norm, val = extract_homonym_digit(word)
            pos_col, lvl_col = get_parsed_pos_level_from_cp(line)
            
            output_lines.append((w_norm, val, pos_col, lvl_col))
            processed_count += 1

    # Load and preserve header of target file
    with open(path_target, "r", encoding="utf-8") as f:
        lines = f.readlines()
    header = lines[0]
    
    # Reconstruct target file lines in the order they appear in copy-paste
    new_lines = [header]
    for w, val, pos, lvl in output_lines:
        new_lines.append(f"{w}\t{val}\t{pos}\t{lvl}\n")
        
    with open(path_target, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Successfully processed {processed_count} words and wrote to {path_target}")

if __name__ == "__main__":
    main()
