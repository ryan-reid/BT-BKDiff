import subprocess
import os
import sys

def run_command(command, description):
    print(f"--- {description} ---")
    print(f"Executing: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}:")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

def main():
    # Base paths relative to the scripts directory
    bk_mpq = "../mods/BKDiablo/bkdiablo.mpq"
    bt_mpq = "../mods/BTDiablo/btdiablo.mpq"
    bk_export = "../exports/item_db"
    bt_export = "../exports/item_db_bt"
    report_out = "../output/item_diff_report"

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
