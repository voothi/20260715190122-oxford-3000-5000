# Oxford 3000/5000 Wordlist Curation & Caching Pipeline

[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](https://github.com/voothi/20260715190122-oxford-3000-5000)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A specialized data curation project designed to produce highly accurate, clean, and verified TSV lists for the Oxford 3000 and Oxford 5000 vocabulary databases. This repository packages the sanitized datasets along with a suite of Python scripts and unit tests to manage and verify the data pipeline.

The official lists are based on the [Oxford Learner's Dictionaries Wordlists](https://www.oxfordlearnersdictionaries.com/wordlists/).

## Table of Contents
- [Project Goal](#project-goal)
- [AI Workflow & History](#ai-workflow--history)
- [Project Structure](#project-structure)
- [Data Modeling & Format Patterns](#data-modeling--format-patterns)
  - [1. Single CEFR Level Pattern](#1-single-cefr-level-pattern)
  - [2. Multiple CEFR Levels Pattern](#2-multiple-cefr-levels-pattern)
- [Pipelines & Scripts Details](#pipelines--scripts-details)
- [Test Fixtures & Archives](#test-fixtures--archives)
- [Usage](#usage)
  - [Running the Unit Tests](#running-the-unit-tests)
  - [Running POS/Level Verification](#running-poslevel-verification)
- [License](#license)

---

## Project Goal
The primary objective of this project is to compile, sanitize, and verify the Oxford 3000 and Oxford 5000 wordlists to a high standard of accuracy. This includes normalizing part-of-speech tags, separating homonym sense indexes (like `can1` $\rightarrow$ Word: `can`, Value: `1`), and structuring CEFR levels (A1–C1) into separate columns. The processing scripts and verification tests are packaged with the data to support future adjustments and reproducibility.

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## AI Workflow & History
These datasets were curated and verified in partnership with **Gemini Chat in Pro (Extended) mode (Gemini 3.1 Pro)**. The process evolved through the following stages:

1.  **Initial OCR Attempt:** The source PDFs were initially uploaded directly to Gemini for OCR extraction and TSV formatting.
2.  **Optimized Copy-Paste Pipeline:** To improve accuracy and resolve parsing gaps, the text was copied directly from the PDF files into intermediate flat text files, sorted, and submitted for structured comparisons.
3.  **Algorithmic Corrections:** A suite of local Python scripts was developed to merge the files, strip formatting noise, isolate homonym digits, and format the output according to strict level formatting patterns.

### Prompt Logs
Below are the exact historical prompts used during the curation process:

```text
20260715160519 Recognize this in a TSV file. The words should be purely in a separate column. The level is also in a separate place. Part of speech separately. What else is there. Compare the number of results and their order with what
```
```text
20260715162052 Continue and finish this list to the end
```
```text
20260715165712 Check these files to see if all the words are there, count the words.
```
```text
20260715171247 Compare 2 files. A file created by AI and a file that I manually copied from the PDF. Output the final list by correcting the AI file.
```

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

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
├── .gitattributes                          # Git attributes configuration
├── .gitignore                              # Git ignore configuration
├── 20260715160822-oxford-3000.en.pdf       # Oxford 3000 source PDF
├── 20260715160822-oxford-3000.en.tsv       # Oxford 3000 clean target TSV
├── 20260715165539-oxford-5000.en.pdf       # Oxford 5000 source PDF
├── 20260715165539-oxford-5000-expanded.en.tsv # Oxford 5000 clean target TSV
├── LICENSE                                # MIT license
└── README.md                              # Project documentation
```

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## Data Modeling & Format Patterns

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

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## Pipelines & Scripts Details

1.  **`1_create_corrected_oxford_5000.py`:**
    *   *Input:* `20260715165539-oxford-5000-expanded.en.tsv` and raw `20260715165539-oxford-5000-expanded-copy-paste.en.tsv`.
    *   *Operation:* Automatically identifies missing alphabetical word groups in File 1 (e.g., A-words), cleans up trailing tags, merges them, and generates a fully reconstructed, sorted target file.
2.  **`2_clean_copy_paste_words.py`:**
    *   *Operation:* Isolates raw copy-pasted lines and strips all parts of speech tags, CEFR tags, and double spaces, outputting a clean, flat list of word names (one per line) for dictionary import validation.
3.  **`3_move_homonym_digits.py`:**
    *   *Operation:* Scans the Word column for trailing homonym index digits (including digits directly preceding parenthetical descriptions, e.g., `close1` or `last1 (final)`) and extracts them into a new, separate `Value` column to isolate the clean dictionary headword.
4.  **`4_apply_pos_level_pattern.py`:**
    *   *Operation:* Reads raw copy-pasted files and processes POS and Level formatting logic recursively to align target files with the single-level and multi-level patterns.
5.  **`5_verify_pos_level.py`:**
    *   *Operation:* Aligns the target TSV and raw copy-pasted inputs on clean keys, performing an automated comparison check across the Part of Speech and Level columns to catch formatting discrepancies and missing definitions.

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## Test Fixtures & Archives
The files inside `tests/fixtures/` serve as:
1.  **Archival Snapshots:** They record the exact intermediate outputs (like words-only outputs `-wo.en.tsv` and corrected drafts `-corrected.tsv`) of the processing stages.
2.  **Test Fixtures:** They are used as static inputs and expected baseline comparisons for integration validation.

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## Usage

### Running the Unit Tests
Execute the unit test suite from the terminal to verify the parsing functions, word cleaning logic, homonym separation, and pattern formatting:
```powershell
python U:\voothi\20260715190122-oxford-3000-5000\tests\test_scripts.py
```

### Running POS/Level Verification
To run the alignment validator between the target TSV and raw copy-paste TSV:
```powershell
python U:\voothi\20260715190122-oxford-3000-5000\scripts\5_verify_pos_level.py
```

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## License
MIT License. See `LICENSE` for details.

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)
