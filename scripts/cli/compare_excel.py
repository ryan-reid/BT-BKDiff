import sys
import os
import json
from d2lib.repository import D2Repository
from d2lib.services import ExcelComparisonService

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python compare_excel.py <bk_file> <bt_file> [key_col]", file=sys.stderr)
        return
        
    file_bk_path, file_bt_path = sys.argv[1], sys.argv[2]
    key_col = sys.argv[3] if len(sys.argv) > 3 else 'code'
    
    # We use a dummy repo path just for the loader
    repo = D2Repository(".")
    table_bk = repo.load_tsv(file_bk_path)
    table_bt = repo.load_tsv(file_bt_path)
    
    if not table_bk or not table_bt:
        print("Error: Could not load tables.", file=sys.stderr)
        return
        
    diff = ExcelComparisonService.compare_tables(table_bk, table_bt, key_col, os.path.basename(file_bk_path))
    print(json.dumps(diff, indent=2))

if __name__ == "__main__":
    main()
