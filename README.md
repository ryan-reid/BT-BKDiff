# BT-BKDiff: Diablo 2 Excel & Item Comparison Tool

This project provides a suite of Python scripts designed to compare Diablo 2 (D2R mod) data between two different mod versions. It handles both raw Excel (`.txt`) file differences and high-level Item Database comparisons.

In this setup:
- **BKDiablo (`bkdiablo.mpq`)** is treated as the **New/Target** version.
- **BTDiablo (`btdiablo.mpq`)** is treated as the **Old/Base** version.

---

## 1. Item Database Comparison (The "High-Level" View)

This tool exports items (Uniques, Sets, Runewords) into human-readable Markdown and then compares them surgically.

### Scripts:
*   **`d2_item_analyzer.py`**: Extracts item data from MPQ directories and saves them as `.md` files.
    *   **Usage**: 
        ```bash
        python d2_item_analyzer.py --mpq bkdiablo.mpq --type export --out item_db
        python d2_item_analyzer.py --mpq btdiablo.mpq --type export --out item_db_bt
        ```
    *   **Advanced**: Uses `propertygroups.txt` to resolve complex "composite" properties and random affix groups into human-readable text.
*   **`compare_item_db.py`**: Compares the two exported databases and generates a multi-page report.
    *   **Usage**: `python compare_item_db.py`
    *   **Output**: Files are saved in `item_diff_report/`:
        *   `SUMMARY.md`: High-level counts and links.
        *   `ADDED.md`: Full breakdown of new items.
        *   `MODIFIED.md`: Surgical side-by-side diffs of changed items.
        *   `REMOVED.md`: List of deleted items.

---

## 2. Excel TSV Comparison (The "Raw Data" View)

Generates detailed technical reports highlighting additions, removals, and modifications in columns and rows of the game's `.txt` files.

### Scripts:
*   **`compare_all_excel.py`**: The primary orchestration script for raw data.
    *   **Usage**: `python compare_all_excel.py`
    *   **Output**: Detailed `.md` reports for every changed file in `excel_diff_report/SUMMARY.md`.
*   **`compare_excel.py`**: Standalone utility used to compare any two specific TSV files.
*   **`analyze_headers.py`**: Inspects headers and first rows to help identify "key columns" for matching.

---

## Technical Features

*   **Surgical Highlighting**: Mod-level changes are highlighted token-by-token (e.g., if a range `10-20` changes to `10-30`, only the `30` is highlighted).
*   **Smart Normalization**:
    *   Ignores immaterial differences like Diablo II color codes (`ÿc1`), bullets (`•`), and formatting.
    *   Treats equivalent phrasing (e.g., "Physical Damage Received Reduced by" vs "Damage Reduced by") as identical.
    *   Distinguishes between flat reduction and percentile reduction by preserving the `%` sign in keys.
*   **Property Group Resolution**: Unpacks custom mod properties (like `Incendiary-Affix1`) using the `propertygroups.txt` definition file.

## Requirements

- Python 3.x
- No external libraries required (uses standard `csv`, `json`, `difflib`, and `os` modules).
