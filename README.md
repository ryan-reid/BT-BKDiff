# BT-BKDiff: Diablo 2 Excel & Item Comparison Tool

This project provides a suite of Python scripts designed to compare Diablo 2 (D2R mod) data between two different mod versions. It handles both raw Excel (`.txt`) file differences and high-level Item Database comparisons.

## Project Structure

```text
/
├── data/           # Configuration files (propertygroups.txt)
├── docs/           # Modding guides and references
├── exports/        # Parsed item database dumps (.md)
├── mods/           # Mod data (Submodules: BKDiablo, BTDiablo)
├── output/         # Generated comparison reports
├── scripts/        # Python analysis and comparison logic
└── README.md
```

---

## 1. Item Database Comparison (The "High-Level" View)

This tool exports items (Uniques, Sets, Runewords) into human-readable Markdown and then compares them surgically.

### Scripts:
*   **`scripts/d2_item_analyzer.py`**: Extracts item data from MPQ directories and saves them as `.md` files.
    *   **Usage**: 
        ```bash
        cd scripts
        python d2_item_analyzer.py --mpq ../mods/BKDiablo/bkdiablo.mpq --type export --out ../exports/item_db
        python d2_item_analyzer.py --mpq ../mods/BTDiablo/btdiablo.mpq --type export --out ../exports/item_db_bt
        ```
    *   **Advanced**: Uses `data/propertygroups.txt` to resolve complex "composite" properties and random affix groups into human-readable text.
*   **`scripts/compare_item_db.py`**: Compares the two exported databases and generates a multi-page report.
    *   **Usage**: `cd scripts; python compare_item_db.py`
    *   **Output**: Files are saved in `output/item_diff_report/`:
        *   `SUMMARY.md`: High-level counts and links.
        *   `ADDED.md`: Full breakdown of new items.
        *   `MODIFIED.md`: Surgical side-by-side diffs of changed items.
        *   `REMOVED.md`: List of deleted items.

---

## 2. Excel TSV Comparison (The "Raw Data" View)

Generates detailed technical reports highlighting additions, removals, and modifications in columns and rows of the game's `.txt` files.

### Scripts:
*   **`scripts/compare_all_excel.py`**: The primary orchestration script for raw data.
    *   **Usage**: `cd scripts; python compare_all_excel.py`
    *   **Output**: Detailed `.md` reports for every changed file in `output/excel_diff_report/SUMMARY.md`.
*   **`scripts/compare_excel.py`**: Standalone utility used to compare any two specific TSV files.
*   **`scripts/analyze_headers.py`**: Inspects headers and first rows to help identify "key columns" for matching.

---

## Technical Features

*   **Surgical Highlighting**: Mod-level changes are highlighted token-by-token (e.g., if a range `10-20` changes to `10-30`, only the `30` is highlighted).
*   **Smart Normalization**:
    *   Ignores immaterial differences like Diablo II color codes (`ÿc1`), bullets (`•`), and formatting.
    *   Treats equivalent phrasing (e.g., "Physical Damage Received Reduced by" vs "Damage Reduced by") as identical.
    *   Distinguishes between flat reduction and percentile reduction by preserving the `%` sign in keys.
*   **Property Group Resolution**: Unpacks custom mod properties (like `Incendiary-Affix1`) using the `data/propertygroups.txt` definition file.

## Requirements

- Python 3.x
- No external libraries required (uses standard `csv`, `json`, `difflib`, and `os` modules).
