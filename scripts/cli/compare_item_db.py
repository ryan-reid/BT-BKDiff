import os
import sys
import json
import glob
import argparse
from typing import Dict, List, Any
from d2lib.repository import D2Repository
from d2lib.services import ItemComparisonService
from d2lib.exporters import MarkdownExporter

def load_json_db(db_dir: str) -> Dict[str, Dict[str, Any]]:
    # type -> id -> item
    types = {'uniques': {}, 'sets': {}, 'runewords': {}}
    for t in types:
        pattern = os.path.join(db_dir, t, "**", "*.json")
        for filepath in glob.glob(pattern, recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            item_id = item.get('id') or item.get('name')
                            types[t][item_id] = item
                    elif isinstance(data, dict):
                        # Some files might be dict of items directly
                        for k, v in data.items():
                            if isinstance(v, list):
                                for item in v:
                                    item_id = item.get('id') or item.get('name')
                                    types[t][item_id] = item
                            else:
                                item_id = v.get('id') or v.get('name')
                                types[t][item_id] = v
            except Exception as e:
                print(f"Error loading {filepath}: {e}", file=sys.stderr)
    return types

def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two exported item databases and generate markdown reports.")
    parser.add_argument("--new-db", default="../exports/item_db", help="Path to the new/target exported JSON item database")
    parser.add_argument("--old-db", default="../exports/item_db_bt", help="Path to the old/base exported JSON item database")
    parser.add_argument("--out", default="../output/item_diff_report", help="Output directory for generated markdown diffs")
    parser.add_argument("--new-label", default="BK Diablo", help="Display label for the new/target database in markdown reports")
    parser.add_argument("--old-label", default="BT Diablo", help="Display label for the old/base database in markdown reports")
    args = parser.parse_args()

    bk_json_dir = args.new_db
    bt_json_dir = args.old_db
    out_dir = args.out

    print("Loading Item Databases...")
    bk_db = load_json_db(bk_json_dir)
    bt_db = load_json_db(bt_json_dir)

    service = ItemComparisonService()
    
    # We'll aggregate into a single ItemDiffDTO but keep track of counts for the summary
    combined_added = {}
    combined_removed = {}
    combined_modified = {}
    
    type_counts = {}

    for t in ['uniques', 'sets', 'runewords']:
        diff = service.compare_item_lists(bk_db[t], bt_db[t])
        combined_added.update(diff['added'])
        combined_removed.update(diff['removed'])
        combined_modified.update(diff['modified'])
        type_counts[t] = {
            'added': len(diff['added']),
            'removed': len(diff['removed']),
            'modified': len(diff['modified'])
        }

    combined_diff = {
        'added': combined_added,
        'removed': combined_removed,
        'modified': combined_modified
    }
    
    exporter = MarkdownExporter()
    exporter.export_item_diff(combined_diff, out_dir, old_label=args.old_label, new_label=args.new_label)
    
    # Inject breakdown into SUMMARY.md
    summary_path = os.path.join(out_dir, "SUMMARY.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Item Database Comparison Summary\n\n")
        f.write("| Category | [Added](ADDED.md) | [Removed](REMOVED.md) | [Modified](MODIFIED.md) |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for t in ['uniques', 'sets', 'runewords']:
            c = type_counts[t]
            f.write(f"| {t.capitalize()} | {c['added']} | {c['removed']} | {c['modified']} |\n")
        f.write(f"| **Total** | **{len(combined_added)}** | **{len(combined_removed)}** | **{len(combined_modified)}** |\n\n")
        f.write("Click the links in the header to see detailed breakdowns.\n")
    
    print(f"Reports generated in {out_dir}")

if __name__ == "__main__":
    main()
