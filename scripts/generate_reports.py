import subprocess
import os
import sys
import csv
from typing import List

# Ensure D2-Safe I/O
csv.field_size_limit(1000000)

def run_command(command: List[str], description: str) -> None:
    """Runs a shell command and logs output/errors."""
    print(f"--- {description} ---")
    print(f"Executing: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}:\n{e.stderr}", file=sys.stderr)

def main() -> None:
    # 1. Export BK Item Database (Markdown & JSON for comparison)
    run_command([
        sys.executable, "d2_item_analyzer.py", "--mpq", "../mods/BKDiablo/bkdiablo.mpq", "--type", "export", "--out", "../exports/item_db", "--format", "markdown"
    ], "Exporting BK Item Database (Markdown)")
    run_command([
        sys.executable, "d2_item_analyzer.py", "--mpq", "../mods/BKDiablo/bkdiablo.mpq", "--type", "export", "--out", "../exports/item_db", "--format", "json"
    ], "Exporting BK Item Database (JSON)")

    # 2. Export BT Item Database (Markdown & JSON for comparison)
    run_command([
        sys.executable, "d2_item_analyzer.py", "--mpq", "../mods/BTDiablo/btdiablo.mpq", "--type", "export", "--out", "../exports/item_db_bt", "--format", "markdown"
    ], "Exporting BT Item Database (Markdown)")
    run_command([
        sys.executable, "d2_item_analyzer.py", "--mpq", "../mods/BTDiablo/btdiablo.mpq", "--type", "export", "--out", "../exports/item_db_bt", "--format", "json"
    ], "Exporting BT Item Database (JSON)")

    # 3. Compare Item Databases
    run_command([
        sys.executable, "compare_item_db.py"
    ], "Generating Item Comparison Reports")

    # 4. Compare Excel Tables
    run_command([
        sys.executable, "compare_all_excel.py"
    ], "Generating Excel Comparison Reports")

    print("--- All Tasks Completed Successfully ---")

if __name__ == "__main__":
    main()
