import os
import sys
import argparse
from d2lib.repository import D2Repository
from d2lib.services import ExcelComparisonService
from d2lib.exporters import MarkdownExporter

def get_key_column(filename: str) -> str:
    mapping = {
        'armor.txt': 'name',
        'automagic.txt': 'Name',
        'charstats.txt': 'class',
        'cubemain.txt': 'description',
        'difficultylevels.txt': 'Name',
        'experience.txt': 'Level',
        'gamble.txt': 'name',
        'gems.txt': 'name',
        'hireling.txt': 'Hireling',
        'inventory.txt': 'class',
        'itemstatcost.txt': 'Stat',
        'itemtypes.txt': 'ItemType',
        'levels.txt': 'Name',
        'lvlmaze.txt': 'Name',
        'lvlprest.txt': 'Name',
        'lvlwarp.txt': 'Name',
        'magicprefix.txt': 'Name',
        'magicsuffix.txt': 'Name',
        'missiles.txt': 'Missile',
        'monai.txt': 'AI',
        'monlvl.txt': 'Level',
        'monprop.txt': 'Id',
        'monstats.txt': 'Id',
        'monstats2.txt': 'Id',
        'monumod.txt': 'uniquemod',
        'npc.txt': 'npc',
        'overlay.txt': 'overlay',
        'properties.txt': 'code',
        'runes.txt': 'Name',
        'setitems.txt': 'index',
        'sets.txt': 'index',
        'shrines.txt': 'Name',
        'skilldesc.txt': 'skilldesc',
        'skills.txt': 'skill',
        'states.txt': 'state',
        'superuniques.txt': 'Superunique',
        'treasureclassex.txt': 'Treasure Class',
        'uniqueitems.txt': 'index',
        'uniqueprefix.txt': 'Name',
    }
    return mapping.get(filename, 'code')

def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two Diablo II Excel directories and export markdown diffs.")
    parser.add_argument("--new-dir", default="../mods/BKDiablo/bkdiablo.mpq/data/global/excel", help="Path to the new/target Excel directory")
    parser.add_argument("--old-dir", default="../mods/BTDiablo/btdiablo.mpq/data/global/excel", help="Path to the old/base Excel directory")
    parser.add_argument("--out", default="../output/excel_diff_report", help="Output directory for generated markdown diffs")
    args = parser.parse_args()

    bk_dir = args.new_dir
    bt_dir = args.old_dir
    report_dir = args.out
    
    repo = D2Repository(".")
    exporter = MarkdownExporter()
    summary_rows = []
    
    files_bk = {f for f in os.listdir(bk_dir) if f.endswith('.txt')}
    files_bt = {f for f in os.listdir(bt_dir) if f.endswith('.txt')}
    common_files = sorted(files_bk & files_bt)
    
    for filename in common_files:
        print(f"Comparing {filename}...")
        table_bk = repo.load_tsv(os.path.join(bk_dir, filename))
        table_bt = repo.load_tsv(os.path.join(bt_dir, filename))
        
        diff = ExcelComparisonService.compare_tables(table_bk, table_bt, get_key_column(filename), filename)
        report_name = filename.replace('.txt', '.md')
        exporter.export_excel_diff(diff, os.path.join(report_dir, report_name))
        summary_rows.append({
            "filename": filename,
            "report_name": report_name,
            "added_cols": len(diff["added_cols"]),
            "removed_cols": len(diff["removed_cols"]),
            "added_rows": len(diff["added_rows"]),
            "removed_rows": len(diff["removed_rows"]),
            "modified_rows": len(diff["modified_rows"]),
        })

    summary_lines = ["# Excel Diff Summary\n"]
    summary_lines.append("| File | Added Cols | Removed Cols | Added Rows | Removed Rows | Modified Rows |")
    summary_lines.append("| :--- | ---: | ---: | ---: | ---: | ---: |")
    for row in summary_rows:
        summary_lines.append(
            f"| [{row['filename']}]({row['report_name']}) | {row['added_cols']} | {row['removed_cols']} | {row['added_rows']} | {row['removed_rows']} | {row['modified_rows']} |"
        )

    total_added_cols = sum(row["added_cols"] for row in summary_rows)
    total_removed_cols = sum(row["removed_cols"] for row in summary_rows)
    total_added_rows = sum(row["added_rows"] for row in summary_rows)
    total_removed_rows = sum(row["removed_rows"] for row in summary_rows)
    total_modified_rows = sum(row["modified_rows"] for row in summary_rows)
    summary_lines.append(
        f"| **Total** | **{total_added_cols}** | **{total_removed_cols}** | **{total_added_rows}** | **{total_removed_rows}** | **{total_modified_rows}** |"
    )

    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines).strip() + "\n")

    print(f"Reports generated in {report_dir}")

if __name__ == "__main__":
    main()
