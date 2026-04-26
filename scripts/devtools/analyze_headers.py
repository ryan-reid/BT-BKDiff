import sys
import os
from d2lib.repository import D2Repository

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python analyze_headers.py <file_or_dir>", file=sys.stderr)
        return

    repo = D2Repository(".")
    target: str = sys.argv[1]
    
    files = []
    if os.path.isdir(target):
        files = [os.path.join(target, f) for f in os.listdir(target) if f.endswith('.txt')]
    else:
        files = [target]
        
    for f_path in files:
        data = repo.load_tsv(f_path)
        if data:
            headers = list(data[0].keys())
            print(f"{os.path.basename(f_path)}: {', '.join(headers)}")

if __name__ == "__main__":
    main()
