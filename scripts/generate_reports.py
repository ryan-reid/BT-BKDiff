import subprocess
import os
import sys
import csv
from typing import List

# Ensure D2-Safe I/O
csv.field_size_limit(1000000)

def run_command(command: List[str], description: str) -> None:
    """Runs a shell command and logs output/errors to the console."""
    print(f"--- {description} ---")
    print(f"Executing: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}:", file=sys.stderr)
        if e.stdout:
            print(e.stdout, file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(1)

def main() -> None:
    # Base paths relative to the scripts directory
    bk_mpq: str = "../mods/BKDiablo/bkdiablo.mpq"
    bt_mpq: str = "../mods/BTDiablo/btdiablo.mpq"
    bk_export: str = "../exports/item_db"
    bt_export: str = "../exports/item_db_bt"

    # 1. Export BK Items
    run_command([
        sys.executable, "d2_item_analyzer.py",
        "--mpq", bk_mpq,
        "--type", "export",
        "--out", bk_export
    ], "Exporting BK Item Database")

    # 2. Export BT Items
    run_command([
        sys.executable, "d2_item_analyzer.py",
        "--mpq", bt_mpq,
        "--type", "export",
        "--out", bt_export
    ], "Exporting BT Item Database")

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
