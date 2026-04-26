import os
import sys
import json
import glob
from typing import Dict, List, Any
from d2_repository import D2Repository
from d2_services import ItemComparisonService
from d2_exporters import MarkdownExporter

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
    bk_json_dir = "../exports/item_db"
    bt_json_dir = "../exports/item_db_bt"
    out_dir = "../output/item_diff_report"

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
    exporter.export_item_diff(combined_diff, out_dir)
    
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
