import csv
import sys
import os
import json

# Increase CSV field size limit for large D2 fields
csv.field_size_limit(1000000)

def load_tsv(file_path):
    if not os.path.exists(file_path):
        return [], []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.strip('\n\r') for line in f if line.strip('\n\r')]
        if not lines:
            return [], []
        
        reader = csv.DictReader(lines, delimiter='\t', quoting=csv.QUOTE_NONE)
        headers = reader.fieldnames
        data = list(reader)
        return headers, data

def compare_files(file_bk, file_bt, key_col='code'):
    # file_bk = New Version
    # file_bt = Old Version
    h_new, d_new = load_tsv(file_bk)
    h_old, d_old = load_tsv(file_bt)

    if not h_new or not h_old:
        return {"error": "Could not read one or both files"}

    # Fallback for key column logic
    if key_col not in h_new or key_col not in h_old:
        # Priority list for fallback keys
        priority_keys = ['Code', 'code', 'Id', 'id', 'skillid', 'stat']
        # Also look for anything starting with *
        star_keys = [c for c in h_new if c.startswith('*') and c in h_old]
        
        found_key = False
        for pk in priority_keys:
            if pk in h_new and pk in h_old:
                key_col = pk
                found_key = True
                break
        
        if not found_key and star_keys:
            key_col = star_keys[0]
            found_key = True
        
        if not found_key:
            if 'name' in h_new and 'name' in h_old:
                key_col = 'name'
            elif h_new and h_old:
                key_col = h_new[0]

    map_new = {str(row[key_col]).strip().lower(): row for row in d_new if row.get(key_col)}
    map_old = {str(row[key_col]).strip().lower(): row for row in d_old if row.get(key_col)}

    common_cols = [c for c in h_new if c in h_old]
    all_keys = sorted(set(map_new.keys()) | set(map_old.keys()))

    report = {
        "filename": os.path.basename(file_bk),
        "key_used": key_col,
        "columns": {
            "added_in_bk": [c for c in h_new if c not in h_old],
            "removed_in_bk": [c for c in h_old if c not in h_new]
        },
        "rows": {
            "bk_new_count": len(d_new),
            "bt_old_count": len(d_old),
            "added_in_bk": [],
            "removed_in_bk": [],
            "modified": {}
        }
    }

    for key in all_keys:
        if key not in map_old:
            report["rows"]["added_in_bk"].append(key)
        elif key not in map_new:
            report["rows"]["removed_in_bk"].append(key)
        else:
            diffs = {}
            for col in common_cols:
                v_new = map_new[key].get(col, '')
                v_old = map_old[key].get(col, '')
                if v_new != v_old:
                    diffs[col] = {"bk_new": v_new, "bt_old": v_old}
            if diffs:
                report["rows"]["modified"][key] = diffs

    return report

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_excel.py <bk_file> <bt_file> [key_col]")
    else:
        file_bk = sys.argv[1]
        file_bt = sys.argv[2]
        key = sys.argv[3] if len(sys.argv) > 3 else 'code'
        report = compare_files(file_bk, file_bt, key)
        print(json.dumps(report, indent=2))
