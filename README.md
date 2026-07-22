# The Oxford 3000/5000 Wordlist Curation & Caching Pipeline

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
The primary objective of this project is to compile, sanitize, and verify the Oxford 3000 and Oxford 5000 vocabulary lists to a high standard of accuracy. This includes normalizing part-of-speech tags, extracting parenthetical annotations (like `bank (money)` $\rightarrow$ Word: `bank`, Annotation: `(money)`), separating homonym sense indexes (like `can1` $\rightarrow$ Word: `can`, Sense: `1`), and structuring CEFR levels (A1–C1) into separate columns. The processing scripts and verification tests are packaged with the data to support future adjustments and reproducibility.

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## AI Workflow & History
These datasets were curated and verified in partnership with **Gemini Chat in Pro (Extended) mode (Gemini 3.1 Pro)**. The process evolved through the following stages:

1.  **Initial OCR Attempt:** The source PDFs were initially uploaded directly to Gemini for OCR extraction and TSV formatting.
2.  **Optimized Copy-Paste Pipeline:** To improve accuracy and resolve parsing gaps, the text was copied directly from the PDF files into intermediate flat text files, sorted, and submitted for structured comparisons.
3.  **Algorithmic Corrections:** A suite of local Python scripts was developed to merge the files, strip formatting noise, isolate parenthetical annotations and homonym digits, and format the output according to strict level formatting patterns.

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
├── scripts/
├── tests/
├── .gitattributes
├── .gitignore
├── 20260715160822-oxford-3000-freq-ru.en.html            # Oxford 3000 Frequency-ordered HTML (with Russian)
├── 20260715160822-oxford-3000-freq-ru.en.pdf             # Oxford 3000 Frequency-ordered PDF (with Russian)
├── 20260715160822-oxford-3000-freq-ru.en.tsv             # Oxford 3000 Frequency-ordered TSV (with Russian)
├── 20260715160822-oxford-3000-freq.en.html               # Oxford 3000 Frequency-ordered HTML
├── 20260715160822-oxford-3000-freq.en.pdf                # Oxford 3000 Frequency-ordered PDF
├── 20260715160822-oxford-3000-freq.en.tsv                # Oxford 3000 Frequency-ordered TSV
├── 20260715160822-oxford-3000.en.html                    # Oxford 3000 Alphabetical HTML
├── 20260715160822-oxford-3000.en.pdf                     # Oxford 3000 Alphabetical PDF
├── 20260715160822-oxford-3000.en.tsv                     # Oxford 3000 Alphabetical TSV
├── 20260715165539-oxford-5000-expanded-freq-ru.en.html   # Oxford 5000 Frequency-ordered HTML (with Russian)
├── 20260715165539-oxford-5000-expanded-freq-ru.en.pdf    # Oxford 5000 Frequency-ordered PDF (with Russian)
├── 20260715165539-oxford-5000-expanded-freq-ru.en.tsv    # Oxford 5000 Frequency-ordered TSV (with Russian)
├── 20260715165539-oxford-5000-expanded-freq.en.html      # Oxford 5000 Frequency-ordered HTML
├── 20260715165539-oxford-5000-expanded-freq.en.pdf       # Oxford 5000 Frequency-ordered PDF
├── 20260715165539-oxford-5000-expanded-freq.en.tsv       # Oxford 5000 Frequency-ordered TSV
├── 20260715165539-oxford-5000-expanded.en.html           # Oxford 5000 Alphabetical HTML
├── 20260715165539-oxford-5000-expanded.en.pdf            # Oxford 5000 Alphabetical PDF
├── 20260715165539-oxford-5000-expanded.en.tsv            # Oxford 5000 Alphabetical TSV
├── LICENSE
└── README.md
```

[Return to Top](#oxford-30005000-wordlist-curation--caching-pipeline)

## Data Modeling & Format Patterns

The pipeline maps raw parts of speech and level notations from copy-pasted PDF texts into a 5-column target TSV with the following headers:
- `Word`: The clean lowercase dictionary headword (excluding homonym numbers and parenthetical details).
- `Annotation`: Parenthetical descriptors denoting semantic category or contextual qualifiers (e.g., `(money)`, `(river)`, `(taking time)`).
- `Sense`: The homonym sense index number (e.g., `1`, `2`) if multiple records exist for the same headword.
- `Part of Speech`: The word's grammatical POS tags.
- `Level`: The word's CEFR levels.

The parser handles POS and level mappings using two patterns:

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
    *   *Operation:* Automatically identifies missing alphabetical word groups in File 1 (e.g., A-words), cleans up trailing tags, parses annotations and homonym sense indices using `extract_annotation_and_sense`, merges them using a composite key `(clean_key(word), annotation, sense)`, and generates a fully reconstructed, sorted target file.
2.  **`2_clean_copy_paste_words.py`:**
    *   *Operation:* Isolates raw copy-pasted lines and strips all parts of speech tags, CEFR tags, and double spaces, outputting a clean, flat list of word names (one per line) for dictionary import validation.
3.  **`3_move_homonym_digits.py`:**
    *   *Operation:* Scans the Word column for trailing homonym index digits and parenthetical qualifiers, extracting them into separate `Sense` and `Annotation` columns respectively to isolate the clean dictionary headword. Dynamically supports 3, 4, or 5 column inputs based on headers.
4.  **`4_apply_pos_level_pattern.py`:**
    *   *Operation:* Reads raw copy-pasted files, separates parenthetical annotations, and processes POS and Level formatting logic recursively to align target files with the single-level and multi-level patterns under the 5-column structure.
5.  **`5_verify_pos_level.py`:**
    *   *Operation:* Aligns the target TSV and raw copy-pasted inputs on composite keys `(clean_key(word + annotation), sense)`, performing an automated comparison check across the Part of Speech and Level columns to catch formatting discrepancies and missing definitions.

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

## Generating PDF from TSV

You can provide the AI with the TSV file and use the following prompt to trigger the exact same PDF generation process:

> **Prompt:** "Please read the attached TSV file containing the dictionary list. Using your Python execution environment, generate an HTML file and convert it to a 3-column A4 PDF using `pandas` and `weasyprint`. Format the 'Word' (or 'Annotation') in bold black, the 'Part of Speech' and 'Level' in grey italics, and append the 'Russian' translation from the last column in blue. Include page numbers and copyright text at the bottom. Do not let individual entries break across pages or columns."

There is also a Python script `scripts/tsv_to_pdf.py` available if you want to run this locally in your own environment.
