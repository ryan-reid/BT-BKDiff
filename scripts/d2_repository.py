import csv
import os
import json
import sys
import re
from typing import List, Dict, Tuple, Optional, Any

# Increase CSV field size limit for large D2 fields
csv.field_size_limit(1000000)

def normalize_d2_value(val: Any) -> str:
    """Normalizes D2 data values for consistent comparison."""
    if val is None:
        return ""
    v = str(val).strip()
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    return v.strip()

def strip_json_comments(text: str) -> str:
    """Removes C-style block (/* */) and single-line (//) comments from JSON text."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'(?m)^\s*//.*$', '', text)
    return text

class D2Repository:
    def __init__(self, mpq_path: str):
        self.mpq_path: str = mpq_path
        self.strings: Dict[str, str] = {}
        self.excel_cache: Dict[str, List[Dict[str, str]]] = {}
        self._load_strings()

    def _load_strings(self) -> None:
        """Loads string JSON files from the MPQ data structure."""
        string_dir = os.path.join(self.mpq_path, "data", "local", "lng", "strings")
        if not os.path.exists(string_dir):
            return
        
        try:
            for filename in os.listdir(string_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(string_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8-sig') as f:
                            content = f.read()
                            clean_content = strip_json_comments(content)
                            data = json.loads(clean_content)
                            for entry in data:
                                if "Key" in entry and "enUS" in entry:
                                    self.strings[entry["Key"]] = entry["enUS"]
                    except Exception as e:
                        print(f"Error loading strings from {filename}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error accessing string directory {string_dir}: {e}", file=sys.stderr)

    def load_tsv(self, file_path: str) -> List[Dict[str, str]]:
        """Loads a D2 TSV file and returns data rows."""
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip('\n\r') for line in f if line.strip('\n\r')]
                if not lines:
                    return []
                
                if lines[0].startswith('\ufeff'):
                    lines[0] = lines[0][1:]
                    
                reader = csv.DictReader(lines, delimiter='\t', quoting=csv.QUOTE_NONE)
                data: List[Dict[str, str]] = []
                for row in reader:
                    clean_row = {
                        (str(k).strip() if k else str(k)): (str(v).strip() if v else "") 
                        for k, v in row.items()
                    }
                    data.append(clean_row)
                return data
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            return []

    def get_excel_table(self, table_name: str) -> List[Dict[str, str]]:
        """Retrieves and caches data from a D2 Excel table."""
        if table_name in self.excel_cache:
            return self.excel_cache[table_name]
        
        # Check standard path
        filepath = os.path.join(self.mpq_path, "data", "global", "excel", f"{table_name}.txt")
        data = self.load_tsv(filepath)
        
        self.excel_cache[table_name] = data
        return data

    def get_string(self, key: str) -> str:
        """Resolves a D2 string key to its localized value."""
        if not key: return ""
        return self.strings.get(key, key)
