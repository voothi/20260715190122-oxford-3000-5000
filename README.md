# Oxford 3000/5000 Wordlist Processing Pipeline

[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](https://github.com/voothi/20260715190122-oxford-3000-5000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A specialized Python utility suite to clean, merge, format, and verify the Oxford 3000 and 5000 wordlists. This repository manages the data pipeline that extracts clean dictionary entries from raw copy-pasted text, organizes CEFR levels, separates homonym sense indexes, and aligns target TSV files with parsed copy-paste sources.

## Table of Contents
- [Description](#description)
- [Project Structure](#project-structure)
- [Data Modeling and Format Patterns](#data-modeling-and-format-patterns)
  - [1. Single CEFR Level Pattern](#1-single-cefr-level-pattern)
  - [2. Multiple CEFR Levels Pattern](#2-multiple-cefr-levels-pattern)
- [Pipelines and Scripts](#pipelines-and-scripts)
- [Test Fixtures and Archives](#test-fixtures-and-archives)
- [Usage](#usage)
  - [Running the Unit Tests](#running-the-unit-tests)
  - [Verifying POS/Level Alignments](#verifying-poslevel-alignments)
- [License](#license)

---

## Description
This repository contains the source data files and processing pipeline for compiling the Oxford 3000 and Oxford 5000 wordlists. During PDF extraction, various formatting inconsistencies (e.g., trailing parts of speech, CEFR levels mixed into strings, merged homonym digits) were normalized. 

The pipeline ensures:
1.  **Word-Only Cleaning:** Extracts clean words in isolation, removing formatting noise.
2.  **Homonym Separation:** Scans word names and pulls index digits (like `can1` $\rightarrow$ Word: `can`, Sense: `1`) into a separate `Value`/`Sense` column.
3.  **POS/Level Alignment:** Standardizes part-of-speech lists and CEFR levels (A1–C1) into structured TSV columns according to strict formatting rules.

---

## Project Structure
```text
U:\voothi\20260715190122-oxford-3000-5000\
├── scripts/                               # Core pipeline scripts
│   ├── 1_create_corrected_oxford_5000.py  # Merges and resolves missing A-words
│   ├── 2_clean_copy_paste_words.py        # Cleans raw copy-paste to word-only lists
│   ├── 3_move_homonym_digits.py           # Moves homonym digits to a Value column
│   ├── 4_apply_pos_level_pattern.py       # Rebuilds target TSVs under multi-level pattern
│   └── 5_verify_pos_level.py              # Validates column alignment with copy-paste
├── tests/                                 # Unit testing suite
│   ├── test_scripts.py                    # Standard unittest test suite
│   └── fixtures/                          # Archival data and test fixtures
│       ├── 20260715160822-oxford-3000-copy-paste.en.tsv
│       ├── 20260715160822-oxford-3000-copy-paste-wo.en.tsv
│       ├── 20260715160822-oxford-3000-corrected.tsv
│       ├── 20260715165539-oxford-5000-expanded-copy-paste.en.tsv
│       ├── 20260715165539-oxford-5000-expanded-copy-paste-wo.en.tsv
│       └── 20260715165539-oxford-5000-expanded-corrected.en.tsv
├── 20260715160822-oxford-3000.en.pdf       # Oxford 3000 source PDF
├── 20260715160822-oxford-3000.en.tsv       # Oxford 3000 clean target TSV
├── 20260715165539-oxford-5000.en.pdf       # Oxford 5000 source PDF
├── 20260715165539-oxford-5000-expanded.en.tsv # Oxford 5000 clean target TSV
├── LICENSE                                # MIT license
└── README.md                              # Project documentation
```

---

## Data Modeling and Format Patterns

The pipeline maps raw parts of speech and level notations from copy-pasted PDF texts into the target TSV using two distinct patterns:

### 1. Single CEFR Level Pattern
If a word possesses only one level across all its parts of speech (or multiple parts of speech sharing a single level tag at the end, e.g., `bet v., n. B2` or `about prep., adv. A1`):
*   **Part of Speech Column:** Contains only the POS tags, separated by a comma (e.g., `v., n.` or `prep., adv.`).
*   **Level Column:** Contains the single CEFR level (e.g., `B2` or `A1`).

### 2. Multiple CEFR Levels Pattern
If a word has multiple parts of speech, each associated with distinct CEFR levels (e.g., `benefit n. A2, v. B1` or `best adj. A1, adv., n. A2`):
*   **Part of Speech Column:** Retains the exact copy-paste string, keeping the CEFR levels inline within the POS column (e.g., `n. A2, v. B1` or `adj. A1, adv., n. A2`).
*   **Level Column:** Combines all unique levels found in the entry into a comma-separated list (e.g., `A2, B1` or `A1, A2`).

> [!NOTE]
> This dual approach preserves the precise mapping of which level belongs to which part of speech for complex entries while maintaining clean, separate columns for simple ones.

---

## Pipelines and Scripts
*   **`1_create_corrected_oxford_5000.py`:** Restores missing word groups in the Oxford 5000 expanded list by scanning and merging missing data from the copy-paste file.
*   **`2_clean_copy_paste_words.py`:** Isolates raw copy-pasted text to strip POS tags, CEFR tags, and double spaces, outputting a flat list of words.
*   **`3_move_homonym_digits.py`:** Searches the Word column for homonym digits (e.g., `close1` and `close2`) and moves them to a separate `Value` column (leaving `close` in the Word column).
*   **`4_apply_pos_level_pattern.py`:** Standardizes the target files to align with the single-level and multi-level data format patterns.
*   **`5_verify_pos_level.py`:** Runs a comparison check between the target TSV and the copy-paste file to ensure the Part of Speech and Level columns are in sync.

---

## Test Fixtures and Archives
The files inside `tests/fixtures/` serve as:
1.  **Archival Snapshots:** They record the exact intermediate outputs (like words-only outputs `-wo.en.tsv` and corrected drafts `-corrected.tsv`) of the processing stages.
2.  **Test Fixtures:** They are used as static inputs and expected baseline comparisons for integration validation.

---

## Usage

### Running the Unit Tests
Execute the unit test suite from the terminal to verify the parsing functions, word cleaning logic, homonym separation, and pattern formatting:
```powershell
python U:\voothi\20260715190122-oxford-3000-5000\tests\test_scripts.py
```

### Verifying POS/Level Alignments
To run the alignment validator between the target TSV and raw copy-paste TSV:
```powershell
python U:\voothi\20260715190122-oxford-3000-5000\scripts\5_verify_pos_level.py
```

---

## License
MIT License. See `LICENSE` for details.
