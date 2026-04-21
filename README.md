# BT-BKDiff: Diablo 2 Excel Comparison Tool

This project provides a suite of Python scripts designed to compare Diablo 2 (D2R mod) Excel (`.txt`) files between two different mod versions. It generates detailed Markdown reports highlighting additions, removals, and modifications in columns and rows.

In this specific setup:
- **BKDiablo (`bkdiablo.mpq`)** is treated as the **New/Target** version.
- **BTDiablo (`btdiablo.mpq`)** is treated as the **Old/Base** version.

## Project Structure

- `bkdiablo.mpq/`: Contains the target mod files (New).
- `btdiablo.mpq/`: Contains the base mod files (Old).
- `excel_diff_report/`: Directory where the generated Markdown reports are saved.
- `SUMMARY.md`: Found inside `excel_diff_report/`, this serves as the main index for all comparisons.

## Scripts

### 1. `compare_all_excel.py`
The primary orchestration script. It iterates through all common Excel files in both mod folders and generates a comprehensive report.
- **Usage**: `python compare_all_excel.py`
- **What it does**: 
    - Loads a predefined mapping of filenames to "key columns" (e.g., `code` for items, `skill` for skills) to ensures rows are matched correctly even if they move positions.
    - Generates a `.md` file for every Excel file that has changes.
    - Creates `SUMMARY.md` in the `excel_diff_report` folder.

### 2. `compare_excel.py`
A standalone utility used by `compare_all_excel.py`. It can be run individually to compare any two specific TSV files.
- **Usage**: `python compare_excel.py <bk_file> <bt_file> [key_col]`
- **Output**: Returns a JSON object to stdout containing the diff data.

### 3. `analyze_headers.py`
A simple utility to inspect the headers and the first row of all Excel files in a directory.
- **Usage**: `python analyze_headers.py`
- **Purpose**: Helps developers identify which column should be used as a "key column" for new files.

## How to Read the Reports

1. Open `excel_diff_report/SUMMARY.md` in a Markdown viewer (like VS Code or GitHub).
2. The summary table shows:
    - **Added/Rem Cols**: Changes to the structure of the Excel file.
    - **Added/Rem Rows**: New entries or deleted entries.
    - **Mod Rows**: Existing entries where values have changed.
3. Click the links in the **Link** column to view the granular details for a specific file.

### Detailed Report Format
Within a detailed report (e.g., `armor.md`):
- **Added Rows**: Lists keys that exist in the New version but not the Old.
- **Modified Rows**: Shows the specific column that changed, the old value, and the new value.
  - Example: `minac`: `10` (Old) &rarr; **`15` (New)**

## Requirements

- Python 3.x
- No external libraries required (uses standard `csv`, `json`, and `os` modules).
