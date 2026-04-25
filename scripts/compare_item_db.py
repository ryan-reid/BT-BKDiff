import os
import sys
import json
import glob
from typing import Dict, List, Any
from d2_repository import D2Repository
from d2_services import ItemComparisonService
from d2_exporters import MarkdownExporter

def load_json_db(db_dir: str) -> Dict[str, Any]:
    items = {}
    pattern = os.path.join(db_dir, "**", "*.json")
    for filepath in glob.glob(pattern, recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        items[item['id']] = item
                elif isinstance(data, dict):
                    # Should be a dict of categories or items
                    for k, v in data.items():
                        if isinstance(v, list):
                            for item in v: items[item['id']] = item
                        else:
                            items[v['id']] = v
        except Exception as e:
            print(f"Error loading {filepath}: {e}", file=sys.stderr)
    return items

def main() -> None:
    bk_json_dir = "../exports/item_db"
    bt_json_dir = "../exports/item_db_bt"
    out_dir = "../output/item_diff_report"

    # We need to run with --format json to have these files
    print("Loading Item Databases...")
    bk_items = load_json_db(bk_json_dir)
    bt_items = load_json_db(bt_json_dir)

    if not bk_items or not bt_items:
        print("Error: Item databases missing or empty. Ensure d2_item_analyzer was run with --format json.", file=sys.stderr)
        return

    print(f"Comparing {len(bk_items)} BK items against {len(bt_items)} BT items...")
    service = ItemComparisonService()
    diff = service.compare_item_lists(bk_items, bt_items)
    
    exporter = MarkdownExporter()
    exporter.export_item_diff(diff, out_dir)
    
    print(f"Reports generated in {out_dir}")

if __name__ == "__main__":
    main()
