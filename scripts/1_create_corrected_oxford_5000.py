#!/usr/bin/env python3
"""
ZID: 20260715190326
Description: Merges the incomplete oxford-5000-expanded list (File 1) with the raw copy-paste 
             expanded list (File 2) to resolve missing A-words (abolish to anticipate, assemble to asset, etc.).
             It normalizes homonym notations, resolves level and POS formatting errors, and outputs
             a clean, alphabetically sorted TSV file.
"""

import os
import re

def clean_word_designations(w):
    # Strip any trailing level or POS designations that weren't caught by the parser
    w = w.strip()
    while True:
        prev = w
        w = re.sub(r'\s+[A-Z][12]\b\s*,?$', '', w, flags=re.IGNORECASE)
        w = re.sub(r'\s+(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|n|v|adj|adv|prep|pron|conj|det)\b\s*,?$', '', w, flags=re.IGNORECASE)
        w = re.sub(r'[,.\s]+$', '', w)
        if w == prev:
            break
    return w

def parse_f1(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for lno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            word = parts[0]
            pos = parts[1]
            level = parts[2] if len(parts) > 2 else ""
            records.append((word, pos, level, lno))
    return records

def parse_f2_line(line, pos_pattern):
    line = line.strip()
    if not line:
        return None
    
    match = pos_pattern.search(line)
    if not match:
        word = clean_word_designations(line)
        return {"word": word, "pos": "", "level": ""}
    
    start_pos_idx = match.start()
    word = line[:start_pos_idx].strip()
    word = clean_word_designations(word)
    if not word:
        return None
        
    pos_level_part = line[start_pos_idx:].strip()
    subparts = re.split(r',\s*(?=(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|adj\./adv\.))', pos_level_part)
    
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
    
    combined_pos = ", ".join(p for p, l in parsed_subparts if p)
    combined_lvl = ", ".join(l for p, l in parsed_subparts if l)
    
    combined_pos = re.sub(r'\s+', ' ', combined_pos)
    combined_pos = re.sub(r',\s*$', '', combined_pos)
    combined_pos = re.sub(r'^,\s*', '', combined_pos)
    
    return {
        "word": word,
        "pos": combined_pos,
        "level": combined_lvl
    }

def load_f2(path):
    pos_pattern = re.compile(r'\b(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|adj\./adv\.)')
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for lno, line in enumerate(f, 1):
            parsed = parse_f2_line(line, pos_pattern)
            if parsed:
                records.append((parsed["word"], parsed["pos"], parsed["level"], lno))
    return records

def clean_key(w):
    w = w.lower().strip()
    w = w.replace("²", "").replace("'", "").replace("’", "")
    w = re.sub(r'\d+$', '', w)
    w = w.replace("-", "")
    return w

def normalize_f2_name(w):
    if w == "bass1": return "bass"
    if w == "bow1": return "bow'"
    if w == "content2": return "content²"
    if w == "minute2": return "minute²"
    if w == "recount1": return "recount'"
    if w == "well-being": return "wellbeing"
    return w

def main():
    path1 = r"C:\Users\voothi\Desktop\20260715165539-oxford-5000-expanded.en.tsv"
    path2 = r"C:\Users\voothi\Desktop\20260715165539-oxford-5000-expanded-copy-paste.en.tsv"
    output_path = r"C:\Users\voothi\Desktop\20260715165539-oxford-5000-expanded-corrected.en.tsv"

    print("Loading File 1...")
    f1_records = parse_f1(path1)
    print("Loading File 2...")
    f2_records = load_f2(path2)

    db = {}
    # Seed with File 1 records
    for w, p, l, lno in f1_records:
        k = clean_key(w)
        db[k] = {
            "word": w,
            "pos": p,
            "level": l
        }

    # Merge with File 2 records
    new_words_count = 0
    for w, p, l, lno in f2_records:
        w_norm = normalize_f2_name(w)
        k = clean_key(w_norm)
        if k in db:
            # Resolve missing level in File 1 (e.g. citizenship level empty, but C1 in File 2)
            if db[k]["level"] == "" and l != "":
                db[k]["level"] = l
        else:
            db[k] = {
                "word": w_norm,
                "pos": p,
                "level": l
            }
            new_words_count += 1

    print(f"Added {new_words_count} missing words from File 2.")

    # Sort alphabetically
    def sort_key(item):
        w = item[1]["word"]
        w_clean = w.lower().replace("²", "").replace("'", "").replace("’", "").strip()
        w_clean = re.sub(r'\d+$', '', w_clean)
        return w_clean

    sorted_items = sorted(db.items(), key=sort_key)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        for k, info in sorted_items:
            f.write(f"{info['word']}\t{info['pos']}\t{info['level']}\n")

    print(f"Successfully wrote {len(sorted_items)} sorted records to {output_path}")

if __name__ == "__main__":
    main()
