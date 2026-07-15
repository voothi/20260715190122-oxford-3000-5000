#!/usr/bin/env python3
"""
ZID: 20260715190326
Description: Processes raw copy-paste TSV lists in isolation. It removes parts of speech,
             CEFR levels, and copy-paste artifacts to output only the word names themselves,
             one word per line.
"""

import sys
import os
import re

# POS patterns, including standard, exclamations, and articles
pos_pattern = re.compile(r'\b(modal v\.|modal|n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|adj\./adv\.|exclam\.|indefinite article|definite article)')

def clean_word_designations(w):
    w = w.strip()
    while True:
        prev = w
        # Remove trailing levels
        w = re.sub(r'\s+[A-Z][12]\b\s*,?$', '', w, flags=re.IGNORECASE)
        # Remove trailing POS tags
        w = re.sub(r'\s+(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|number|det\.|exclam\.|n|v|adj|adv|prep|pron|conj|det)\b\s*,?$', '', w, flags=re.IGNORECASE)
        # Remove trailing commas, dots, and spaces
        w = re.sub(r'[,.\s]+$', '', w)
        if w == prev:
            break
    w = w.replace("\xa0", " ") # Convert non-breaking spaces
    return w

def parse_line_to_word(line):
    line = line.strip()
    if not line:
        return None
    
    # Check if the line consists only of POS and level designations (no word)
    pos_starts = ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.', 'pron.', 'det.', 'exclam.']
    for ps in pos_starts:
        if line.startswith(ps):
            return None
            
    # Handle the 'number' word case specially
    if line.startswith("number ") or line == "number":
        return "number"
        
    match = pos_pattern.search(line)
    if not match:
        return clean_word_designations(line)
    
    start_pos_idx = match.start()
    word = line[:start_pos_idx].strip()
    word = clean_word_designations(word)
    if not word:
        return None
    return word

def process_file(path):
    if not os.path.exists(path):
        print(f"Error: File {path} does not exist!")
        return
        
    cleaned_words = []
    with open(path, "r", encoding="utf-8") as f:
        for lno, line in enumerate(f, 1):
            w = parse_line_to_word(line)
            if w:
                cleaned_words.append(w)
            else:
                print(f"Skipped L{lno}: {repr(line.strip())}")

    # Write cleaned words back (overwrite)
    with open(path, "w", encoding="utf-8") as f:
        for w in cleaned_words:
            f.write(f"{w}\n")

    print(f"Successfully processed. Wrote {len(cleaned_words)} cleaned words back to {path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        # Default target path
        target_path = r"C:\Users\voothi\Desktop\20260715160822-oxford-3000-copy-paste-wo.en.tsv"
    
    print(f"Processing target path: {target_path}")
    process_file(target_path)
