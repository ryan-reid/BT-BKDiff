import os
import sys
import csv
from typing import List, Optional

# Ensure D2-Safe I/O
csv.field_size_limit(1000000)

# Add scripts directory to path for relative imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPTS_ROOT not in sys.path:
    sys.path.append(SCRIPTS_ROOT)

from d2lib.repository import D2Repository
from cli import (
    d2_item_analyzer,
    compare_item_db,
    compare_all_excel,
    compare_override_files,
    extract_class_skills,
    generate_wiki
)

class Orchestrator:
    def __init__(self):
        self.repo_cache = {}

    def get_repo(self, path: str) -> D2Repository:
        norm_path = os.path.normpath(os.path.abspath(path))
        if norm_path not in self.repo_cache:
            print(f"--- Loading Repository: {path} ---")
            self.repo_cache[norm_path] = D2Repository(path)
        return self.repo_cache[norm_path]

    def run_task(self, description: str, func, *args, **kwargs) -> bool:
        print(f"--- {description} ---")
        try:
            func(*args, **kwargs)
            return True
        except Exception as e:
            print(f"Error during {description}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False

def main() -> None:
    failures = []
    orch = Orchestrator()

    # Paths relative to SCRIPTS_ROOT
    bk_mpq = os.path.join(SCRIPTS_ROOT, "../mods/BKDiablo/bkdiablo.mpq")
    bt_mpq = os.path.join(SCRIPTS_ROOT, "../mods/BTDiablo/btdiablo.mpq")
    retail_data = os.path.join(SCRIPTS_ROOT, "../data/retail")
    
    bk_out = os.path.join(SCRIPTS_ROOT, "../exports/item_db")
    bt_out = os.path.join(SCRIPTS_ROOT, "../exports/item_db_bt")
    retail_out = os.path.join(SCRIPTS_ROOT, "../exports/item_db_retail")
    
    item_diff_bt_bk = os.path.join(SCRIPTS_ROOT, "../output/item_diff_report_bt_bk")
    item_diff_retail_bk = os.path.join(SCRIPTS_ROOT, "../output/item_diff_report_retail_bk")
    
    excel_diff_bt_bk = os.path.join(SCRIPTS_ROOT, "../output/excel_diff_report_bt_bk")
    excel_diff_retail_bk = os.path.join(SCRIPTS_ROOT, "../output/excel_diff_report_retail_bk")
    
    file_diff_retail_bk = os.path.join(SCRIPTS_ROOT, "../output/file_diff_report_retail_bk")
    skill_trees_out = os.path.join(SCRIPTS_ROOT, "../output/skill_trees")
    wiki_out = os.path.join(SCRIPTS_ROOT, "../output/wiki")

    # Shared Repos
    repo_bk = orch.get_repo(bk_mpq)
    repo_bt = orch.get_repo(bt_mpq)
    repo_retail = orch.get_repo(retail_data)

    # Pre-load property groups
    prop_groups_path = os.path.join(SCRIPTS_ROOT, "../data/propertygroups.txt")
    prop_groups = repo_bk.load_tsv(prop_groups_path)

    # 1. Export BK Item Database
    if not orch.run_task("Exporting BK Item Database (Markdown)", d2_item_analyzer.run, bk_mpq, bk_out, "markdown", repo=repo_bk, property_groups=prop_groups):
        failures.append("Exporting BK Item Database (Markdown)")
    if not orch.run_task("Exporting BK Item Database (JSON)", d2_item_analyzer.run, bk_mpq, bk_out, "json", repo=repo_bk, property_groups=prop_groups):
        failures.append("Exporting BK Item Database (JSON)")

    # 2. Export BT Item Database
    if not orch.run_task("Exporting BT Item Database (Markdown)", d2_item_analyzer.run, bt_mpq, bt_out, "markdown", repo=repo_bt, property_groups=prop_groups):
        failures.append("Exporting BT Item Database (Markdown)")
    if not orch.run_task("Exporting BT Item Database (JSON)", d2_item_analyzer.run, bt_mpq, bt_out, "json", repo=repo_bt, property_groups=prop_groups):
        failures.append("Exporting BT Item Database (JSON)")

    # 3. Export Retail Item Database
    if not orch.run_task("Exporting Retail Item Database (Markdown)", d2_item_analyzer.run, retail_data, retail_out, "markdown", repo=repo_retail, property_groups=prop_groups):
        failures.append("Exporting Retail Item Database (Markdown)")
    if not orch.run_task("Exporting Retail Item Database (JSON)", d2_item_analyzer.run, retail_data, retail_out, "json", repo=repo_retail, property_groups=prop_groups):
        failures.append("Exporting Retail Item Database (JSON)")

    # 4. Compare BK vs BT Item Databases
    if not orch.run_task("Generating BK vs BT Item Comparison Reports", compare_item_db.run, bk_out, bt_out, item_diff_bt_bk):
        failures.append("Generating BK vs BT Item Comparison Reports")

    # 5. Compare BK vs Retail Item Databases
    if not orch.run_task("Generating BK vs Retail Item Comparison Reports", compare_item_db.run, bk_out, retail_out, item_diff_retail_bk):
        failures.append("Generating BK vs Retail Item Comparison Reports")

    # 6. Compare BK vs BT Excel Tables
    bk_excel = os.path.join(bk_mpq, "data/global/excel")
    bt_excel = os.path.join(bt_mpq, "data/global/excel")
    if not orch.run_task("Generating BK vs BT Excel Comparison Reports", compare_all_excel.run, bk_excel, bt_excel, excel_diff_bt_bk):
        failures.append("Generating BK vs BT Excel Comparison Reports")

    # 7. Compare BK vs Retail Excel Tables
    rt_excel = os.path.join(retail_data, "global/excel")
    if not orch.run_task("Generating BK vs Retail Excel Comparison Reports", compare_all_excel.run, bk_excel, rt_excel, excel_diff_retail_bk):
        failures.append("Generating BK vs Retail Excel Comparison Reports")

    # 8. Compare BK override text/JSON files against retail files
    if not orch.run_task("Generating BK vs Retail Override File Comparison Report", compare_override_files.run, bk_mpq, retail_data, file_diff_retail_bk):
        failures.append("Generating BK vs Retail Override File Comparison Report")

    # 9. Generate BK class skill trees
    if not orch.run_task("Generating BK Class Skill Trees", extract_class_skills.run, bk_mpq, skill_trees_out, repo=repo_bk):
        failures.append("Generating BK Class Skill Trees")

    # 10. Generate the static wiki site
    if not orch.run_task("Generating Wiki Pages", generate_wiki.run, bk_out, skill_trees_out, wiki_out, old_item_db_dir=retail_out, game_data_dir=bk_mpq, retail_data_dir=retail_data, old_label="Retail", new_label="BKDiablo"):
        failures.append("Generating Wiki Pages")

    if failures:
        print("--- Some Tasks Failed ---", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        sys.exit(1)

    print("--- All Tasks Completed Successfully ---")

if __name__ == "__main__":
    main()
