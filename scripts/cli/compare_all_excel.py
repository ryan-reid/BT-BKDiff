import os
import argparse
from d2lib.repository import D2Repository
from d2lib.services import ExcelComparisonService
from d2lib.exporters import HtmlReportExporter, JsonExporter


def remove_stale_markdown_reports(report_dir: str) -> None:
    if not os.path.isdir(report_dir):
        return
    for root, _, files in os.walk(report_dir):
        for filename in files:
            if filename.lower().endswith(".md"):
                os.remove(os.path.join(root, filename))

def get_key_column(filename: str) -> str:
    mapping = {
        'armor.txt': 'name', 'automagic.txt': 'Name', 'charstats.txt': 'class', 'cubemain.txt': 'description',
        'difficultylevels.txt': 'Name', 'experience.txt': 'Level', 'gamble.txt': 'name', 'gems.txt': 'name',
        'itemstatcost.txt': 'Stat', 'itemtypes.txt': 'ItemType', 'levels.txt': 'Name', 'missiles.txt': 'Missile',
        'monstats.txt': 'Id', 'properties.txt': 'code', 'skills.txt': 'skill', 'uniqueitems.txt': 'index'
    }
    return mapping.get(filename, 'code')

def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two Diablo II Excel directories and export JSON and HTML diffs.")
    parser.add_argument("--new-dir", default="../mods/BKDiablo/bkdiablo.mpq/data/global/excel", help="Path to the new/target Excel directory")
    parser.add_argument("--old-dir", default="../mods/BTDiablo/btdiablo.mpq/data/global/excel", help="Path to the old/base Excel directory")
    parser.add_argument("--out", default="../output/excel_diff_report", help="Output directory for generated diff reports")
    args = parser.parse_args()

    bk_dir = args.new_dir
    bt_dir = args.old_dir
    report_dir = args.out
    remove_stale_markdown_reports(report_dir)
    
    repo = D2Repository(".")
    html_exporter = HtmlReportExporter()
    json_exporter = JsonExporter()
    summary_rows = []
    
    files_bk = {f for f in os.listdir(bk_dir) if f.endswith('.txt')}
    files_bt = {f for f in os.listdir(bt_dir) if f.endswith('.txt')}
    common_files = sorted(files_bk & files_bt)
    
    for filename in common_files:
        print(f"Comparing {filename}...")
        table_bk = repo.load_tsv(os.path.join(bk_dir, filename))
        table_bt = repo.load_tsv(os.path.join(bt_dir, filename))
        
        diff = ExcelComparisonService.compare_tables(table_bk, table_bt, get_key_column(filename), filename)
        report_stem = filename[:-4]
        report_name = f"{report_stem}.html"
        json_exporter.export(
            {
                "schema": "bt-bkdiff.excel-diff.v1",
                "diff": diff,
            },
            os.path.join(report_dir, f"{report_stem}.json"),
        )
        html_exporter.export_excel_diff(diff, os.path.join(report_dir, report_name))
        summary_rows.append({
            "filename": filename,
            "report_name": report_name,
            "added_cols": len(diff["added_cols"]),
            "removed_cols": len(diff["removed_cols"]),
            "added_rows": len(diff["added_rows"]),
            "removed_rows": len(diff["removed_rows"]),
            "modified_rows": len(diff["modified_rows"]),
        })

    os.makedirs(report_dir, exist_ok=True)
    json_exporter.export(
        {
            "schema": "bt-bkdiff.excel-diff-summary.v1",
            "files": summary_rows,
        },
        os.path.join(report_dir, "summary.json"),
    )
    html_exporter.export_excel_summary(summary_rows, os.path.join(report_dir, "index.html"))

    print(f"Reports generated in {report_dir}")

if __name__ == "__main__":
    main()
