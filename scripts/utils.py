import csv
import os
import json
from typing import List, Dict, Tuple, Optional

# Increase CSV field size limit for large D2 fields
csv.field_size_limit(1000000)

def load_tsv(file_path: str) -> Tuple[List[str], List[Dict]]:
    """Loads a D2 TSV file and returns headers and data rows."""
    if not os.path.exists(file_path):
        return [], []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip('\n\r') for line in f if line.strip('\n\r')]
            if not lines:
                return [], []
            
            # Handle BOM if present
            if lines[0].startswith('\ufeff'):
                lines[0] = lines[0][1:]
                
            reader = csv.DictReader(lines, delimiter='\t', quoting=csv.QUOTE_NONE)
            headers = [h.strip() for h in reader.fieldnames] if reader.fieldnames else []
            data = []
            for row in reader:
                # Clean keys and values
                clean_row = {
                    (k.strip() if k else k): (v.strip() if v else v) 
                    for k, v in row.items()
                }
                data.append(clean_row)
            return headers, data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return [], []

def normalize_d2_value(val: str) -> str:
    """Normalizes D2 data values for consistent comparison."""
    if val is None:
        return ""
    v = str(val).strip()
    # Remove surrounding quotes often found in D2 strings
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    return v.strip()

def get_mod_path(base_dir: str, mod_name: str) -> str:
    """Helper to construct standard mod data paths."""
    return os.path.join(base_dir, "mods", mod_name, f"{mod_name.lower()}.mpq")

def ensure_dir(path: str):
    """Ensures a directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)
