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
        # Supplemental files should be placed in data/retail/ within the repo
        self.supplemental_path: str = os.path.join(os.path.dirname(__file__), "..", "data", "retail")
        self.strings: Dict[str, str] = {}
        self.excel_cache: Dict[str, List[Dict[str, str]]] = {}
        self._load_strings()

    def _load_strings(self) -> None:
        """Loads string JSON files with strict file-level precedence."""
        # 1. Map all available string files in the mod path
        mod_string_dir = os.path.join(self.mpq_path, "data", "local", "lng", "strings")
        mod_files = {}
        if os.path.exists(mod_string_dir):
            mod_files = {f: os.path.join(mod_string_dir, f) for f in os.listdir(mod_string_dir) if f.endswith(".json")}

        # 2. Map supplemental files from local data/retail that don't exist in the mod
        supp_files = {}
        supp_string_dir = os.path.join(self.supplemental_path, "local", "lng", "strings")
        if os.path.exists(supp_string_dir):
            supp_files = {f: os.path.join(supp_string_dir, f) for f in os.listdir(supp_string_dir) 
                            if f.endswith(".json") and f not in mod_files}

        # 3. Load all files. Files present in the mod are used exclusively for their filename.
        # Supplemental files are only used if the filename is missing from the mod.
        all_files = {**supp_files, **mod_files}
        
        for filename, filepath in all_files.items():
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    clean_content = strip_json_comments(content)
                    data = json.loads(clean_content)
                    for entry in data:
                        if "Key" in entry and "enUS" in entry:
                            if entry["Key"] not in self.strings:
                                self.strings[entry["Key"]] = entry["enUS"]
            except Exception as e:
                print(f"Error loading strings from {filename}: {e}", file=sys.stderr)

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
        """Retrieves data from a D2 Excel table with strict file-level precedence."""
        if table_name in self.excel_cache:
            return self.excel_cache[table_name]
        
        # 1. Try Mod Path
        filepath = os.path.join(self.mpq_path, "data", "global", "excel", f"{table_name}.txt")
        data = []
        if os.path.exists(filepath):
            data = self.load_tsv(filepath)
        
        # 2. Try Supplemental Fallback ONLY if file is missing from mod
        if not data:
            supp_file = os.path.join(self.supplemental_path, "global", "excel", f"{table_name}.txt")
            if os.path.exists(supp_file):
                data = self.load_tsv(supp_file)
        
        self.excel_cache[table_name] = data
        return data

    def get_string(self, key: str) -> str:
        """Resolves a D2 string key to its localized value and strips color codes."""
        if not key: return ""
        raw = self.strings.get(key, key)
        # Strip D2 color codes like ÿc0, ÿc;, etc.
        return re.sub(r'ÿc[0-9:;<=>?@A-Z]', '', raw)
