#!/usr/bin/env python3
"""
ZID: 20260717104308
Description: Sorts the Oxford 3000 and 5000 TSV files by word frequency using the
             lemma frequency index in kardenwort core.
"""

import os
import sys
import csv
import configparser

def load_lemma_frequency_index(file_path):
    lemma_index = {}
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile)
            for line_number, row in enumerate(csv_reader):
                if row and row[0] not in lemma_index:
                    lemma_index[row[0]] = line_number
    except FileNotFoundError:
        print(f"File not found: {file_path}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return {}
    return lemma_index

def get_word_frequency_key(word, lemma_index):
    # 1. Exact lookup
    if word in lemma_index:
        return (False, lemma_index[word], word.lower())
    
    # 2. Lowercase lookup
    word_lower = word.lower()
    if word_lower in lemma_index:
        return (False, lemma_index[word_lower], word_lower)
        
    # 3. Handle slash or comma separated words
    parts = []
    if ',' in word:
        parts = [p.strip() for p in word.split(',') if p.strip()]
    elif '/' in word:
        parts = [p.strip() for p in word.split('/') if p.strip()]
        
    if parts:
        found_indices = []
        for p in parts:
            p_lower = p.lower()
            if p in lemma_index:
                found_indices.append(lemma_index[p])
            elif p_lower in lemma_index:
                found_indices.append(lemma_index[p_lower])
        if found_indices:
            return (False, min(found_indices), word_lower)
            
    # 4. Fallback if not found
    return (True, 0, word_lower)

def sort_tsv_by_frequency(tsv_path, lemma_index):
    if not os.path.exists(tsv_path):
        print(f"TSV file not found: {tsv_path}", file=sys.stderr)
        return False
        
    print(f"Sorting {tsv_path} by frequency...")
    
    # Read headers and rows
    header = None
    rows = []
    with open(tsv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for row in reader:
            if row:
                rows.append(row)
                
    if not header or not rows:
        print(f"Empty file or no data in {tsv_path}", file=sys.stderr)
        return False
        
    # Sort rows stably
    # row[0] is the 'Word' column
    rows.sort(key=lambda r: get_word_frequency_key(r[0], lemma_index))
    
    # Write back
    with open(tsv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(header)
        writer.writerows(rows)
        
    print(f"Successfully sorted and saved {tsv_path}")
    return True

def main():
    # Resolve config.ini path
    possible_config_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "20241223170748-kardenwort", "config.ini")),
        r"U:\voothi\20241223170748-kardenwort\config.ini"
    ]
    
    config_path = None
    for p in possible_config_paths:
        if os.path.exists(p):
            config_path = p
            break
            
    if not config_path:
        print("Error: Could not locate kardenwort config.ini", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loaded config from {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    
    # Resolve frequency lemma index file path
    workspace_path = os.path.dirname(config_path)
    data_dir = config.get("project_structure", "data_dir", fallback="data")
    data_path = os.path.join(workspace_path, data_dir)
    
    try:
        lemma_file = config.get("language_resources", "lemma_file_en")
    except Exception as e:
        print(f"Error: Missing lemma_file_en in config: {e}", file=sys.stderr)
        sys.exit(1)
        
    lemma_index_path = os.path.join(data_path, lemma_file)
    print(f"Loading lemma frequency index from {lemma_index_path}...")
    lemma_index = load_lemma_frequency_index(lemma_index_path)
    if not lemma_index:
        print("Error: Failed to load lemma frequency index", file=sys.stderr)
        sys.exit(1)
        
    # Resolve paths to the target TSV files
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    tsv_files = [
        os.path.join(project_root, "20260715160822-oxford-3000-by-frequency.en.tsv"),
        os.path.join(project_root, "20260715165539-oxford-5000-expanded-by-frequency.en.tsv")
    ]
    
    success = True
    for tsv in tsv_files:
        if not sort_tsv_by_frequency(tsv, lemma_index):
            success = False
            
    if not success:
        sys.exit(1)
        
if __name__ == "__main__":
    main()
