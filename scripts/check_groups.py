import os
import sys
from d2_repository import D2Repository

def main() -> None:
    groups_path = os.path.join("..", "data", "propertygroups.txt")
    repo = D2Repository(".")
    data = repo.load_tsv(groups_path)
    
    if not data:
        print(f"Error: propertygroups.txt not found or empty at {groups_path}", file=sys.stderr)
        return

    print(f"Checking {len(data)} property groups...")
    unique_codes = set()
    duplicates = []
    
    for row in data:
        code = row.get('code', '').strip().lower()
        if not code: continue
        if code in unique_codes: duplicates.append(code)
        else: unique_codes.add(code)
            
    if duplicates:
        print(f"Found {len(duplicates)} duplicate codes:", file=sys.stderr)
        for d in duplicates: print(f"  - {d}", file=sys.stderr)
    else:
        print("No duplicate codes found. Property groups are clean.")

if __name__ == "__main__":
    main()
