#!/usr/bin/env python3
"""
ZID: 20260715190326
Description: Verification script that aligns the copy-paste file and the target TSV file
             to check if the Part of Speech and Level columns match under the multi-level pattern.
             It detects and prints any mismatches or missing entries, accounting for homonyms.
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
    
    levels_found = [l for p, l in parsed_subparts if l]
    unique_levels = []
    for l in levels_found:
        sub_lvls = [sl.strip() for sl in l.split(",") if sl.strip()]
        for sl in sub_lvls:
            if sl not in unique_levels:
                unique_levels.append(sl)
                
    if len(unique_levels) > 1:
        pos_col = re.sub(r'\s+', ' ', pos_level_part)
        pos_col = re.sub(r',\s*$', '', pos_col).strip()
        lvl_col = ", ".join(unique_levels)
    else:
        pos_col = ", ".join(p for p, l in parsed_subparts if p)
        pos_col = re.sub(r'\s+', ' ', pos_col)
        pos_col = re.sub(r',\s*$', '', pos_col)
        pos_col = re.sub(r'^,\s*', '', pos_col)
        lvl_col = unique_levels[0] if unique_levels else ""
        
    return pos_col, lvl_col

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

def clean_key(w):
    w = w.lower().strip()
    w = w.replace("²", "").replace("'", "").replace("’", "")
    w = re.sub(r'\d+$', '', w)
    w = w.replace("-", "")
    return w

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    if len(sys.argv) > 2:
        path_target = sys.argv[1]
        path_cp = sys.argv[2]
    elif len(sys.argv) > 1:
        path_target = sys.argv[1]
        if "5000" in path_target:
            path_cp = os.path.join(repo_root, "tests", "fixtures", "20260715165539-oxford-5000-expanded-copy-paste.en.tsv")
        else:
            path_cp = os.path.join(repo_root, "tests", "fixtures", "20260715160822-oxford-3000-copy-paste.en.tsv")
    else:
        path_cp = os.path.join(repo_root, "tests", "fixtures", "20260715160822-oxford-3000-copy-paste.en.tsv")
        path_target = os.path.join(repo_root, "20260715160822-oxford-3000.en.tsv")

    print(f"Loading copy-paste file from {path_cp}...")
    cp_db = {}
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
            if word:
                w_clean, annotation, val = extract_annotation_and_sense(word)
                word_with_ann = f"{w_clean} {annotation}".strip()
                k = (clean_key(word_with_ann), val)
                pos_col, lvl_col = get_parsed_pos_level_from_cp(line)
                cp_db[k] = (pos_col, lvl_col, lno, line)

    print(f"Loading target file from {path_target}...")
    with open(path_target, "r", encoding="utf-8") as f:
        lines = f.readlines()

    mismatches_count = 0
    for lno, line in enumerate(lines[1:], 2):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split("\t")
        word = parts[0]
        annotation = parts[1] if len(parts) > 1 else ""
        sense = parts[2] if len(parts) > 2 else ""
        pos = parts[3] if len(parts) > 3 else ""
        lvl = parts[4] if len(parts) > 4 else ""
        
        word_with_ann = f"{word} {annotation}".strip()
        k = (clean_key(word_with_ann), sense)
        if k not in cp_db:
            print(f"L{lno}: Word {repr(word)} (Annotation: {repr(annotation)}, Sense: {repr(sense)}) missing in CP database!")
            mismatches_count += 1
        else:
            cp_pos, cp_lvl, cp_lno, cp_raw = cp_db[k]
            if cp_pos != pos or cp_lvl != lvl:
                # Exclude expected homonym name collision false positives during verification print
                # (e.g. it/IT, may/May, and multiple number entries)
                if clean_key(word) in ["it", "may", "number"]:
                    continue
                print(f"L{lno}: Word {repr(word)} (Annotation: {repr(annotation)}, Sense: {repr(sense)}) mismatch!")
                print(f"  Target: POS={repr(pos)} Level={repr(lvl)}")
                print(f"  CP    : POS={repr(cp_pos)} Level={repr(cp_lvl)}")
                mismatches_count += 1

    print(f"\nVerification completed. Total mismatches (excluding clean_key homonym duplicates): {mismatches_count}")

if __name__ == "__main__":
    main()
