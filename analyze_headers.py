import os

def analyze_headers(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.txt')] 
    for filename in sorted(files):
        path = os.path.join(directory, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            header = f.readline().strip().split('\t')
            first_row = f.readline().strip().split('\t')
            print(f"FILE: {filename}")
            print(f"  HEAD: {header[:5]} ...")
            if first_row:
                print(f"  DATA: {first_row[:5]} ...")
            print("-" * 20)

if __name__ == "__main__":
    analyze_headers("bkdiablo.mpq/data/global/excel")

