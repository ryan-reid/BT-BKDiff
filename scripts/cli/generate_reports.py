import subprocess
import os
import sys
import csv
from typing import List

# Ensure D2-Safe I/O
csv.field_size_limit(1000000)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)

def run_command(command: List[str], description: str) -> bool:
    """Runs a shell command and logs output/errors."""
    print(f"--- {description} ---")
    print(f"Executing: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=SCRIPTS_ROOT)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}:\n{e.stderr}", file=sys.stderr)
        return False

def main() -> None:
    failures = []

    # 1. Export BK Item Database (Markdown & JSON for comparison)
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "d2_item_analyzer.py"), "--mpq", "../mods/BKDiablo/bkdiablo.mpq", "--type", "export", "--out", "../exports/item_db", "--format", "markdown"
    ], "Exporting BK Item Database (Markdown)"):
        failures.append("Exporting BK Item Database (Markdown)")
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "d2_item_analyzer.py"), "--mpq", "../mods/BKDiablo/bkdiablo.mpq", "--type", "export", "--out", "../exports/item_db", "--format", "json"
    ], "Exporting BK Item Database (JSON)"):
        failures.append("Exporting BK Item Database (JSON)")

    # 2. Export BT Item Database (Markdown & JSON for comparison)
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "d2_item_analyzer.py"), "--mpq", "../mods/BTDiablo/btdiablo.mpq", "--type", "export", "--out", "../exports/item_db_bt", "--format", "markdown"
    ], "Exporting BT Item Database (Markdown)"):
        failures.append("Exporting BT Item Database (Markdown)")
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "d2_item_analyzer.py"), "--mpq", "../mods/BTDiablo/btdiablo.mpq", "--type", "export", "--out", "../exports/item_db_bt", "--format", "json"
    ], "Exporting BT Item Database (JSON)"):
        failures.append("Exporting BT Item Database (JSON)")

    # 3. Export Retail Item Database (Markdown & JSON for comparison)
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "d2_item_analyzer.py"), "--mpq", "../data/retail", "--type", "export", "--out", "../exports/item_db_retail", "--format", "markdown"
    ], "Exporting Retail Item Database (Markdown)"):
        failures.append("Exporting Retail Item Database (Markdown)")
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "d2_item_analyzer.py"), "--mpq", "../data/retail", "--type", "export", "--out", "../exports/item_db_retail", "--format", "json"
    ], "Exporting Retail Item Database (JSON)"):
        failures.append("Exporting Retail Item Database (JSON)")

    # 4. Compare BK vs BT Item Databases
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "compare_item_db.py"),
        "--new-db", "../exports/item_db",
        "--old-db", "../exports/item_db_bt",
        "--out", "../output/item_diff_report_bt_bk",
        "--old-label", "BT Diablo",
        "--new-label", "BK Diablo"
    ], "Generating BK vs BT Item Comparison Reports"):
        failures.append("Generating BK vs BT Item Comparison Reports")

    # 5. Compare BK vs Retail Item Databases
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "compare_item_db.py"),
        "--new-db", "../exports/item_db",
        "--old-db", "../exports/item_db_retail",
        "--out", "../output/item_diff_report_retail_bk",
        "--old-label", "Retail",
        "--new-label", "BK Diablo"
    ], "Generating BK vs Retail Item Comparison Reports"):
        failures.append("Generating BK vs Retail Item Comparison Reports")

    # 6. Compare BK vs BT Excel Tables
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "compare_all_excel.py"),
        "--new-dir", "../mods/BKDiablo/bkdiablo.mpq/data/global/excel",
        "--old-dir", "../mods/BTDiablo/btdiablo.mpq/data/global/excel",
        "--out", "../output/excel_diff_report_bt_bk"
    ], "Generating BK vs BT Excel Comparison Reports"):
        failures.append("Generating BK vs BT Excel Comparison Reports")

    # 7. Compare BK vs Retail Excel Tables
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "compare_all_excel.py"),
        "--new-dir", "../mods/BKDiablo/bkdiablo.mpq/data/global/excel",
        "--old-dir", "../data/retail/excel",
        "--out", "../output/excel_diff_report_retail_bk"
    ], "Generating BK vs Retail Excel Comparison Reports"):
        failures.append("Generating BK vs Retail Excel Comparison Reports")

    # 8. Generate BK class skill trees
    if not run_command([
        sys.executable, os.path.join(SCRIPTS_ROOT, "extract_class_skills.py"),
        "--mpq", "../mods/BKDiablo/bkdiablo.mpq",
        "--out", "../output/skill_trees"
    ], "Generating BK Class Skill Trees"):
        failures.append("Generating BK Class Skill Trees")

    if failures:
        print("--- Some Tasks Failed ---", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        sys.exit(1)

    print("--- All Tasks Completed Successfully ---")

if __name__ == "__main__":
    main()
