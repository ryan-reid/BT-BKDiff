import csv
import os
import json
import sys
import re
from typing import List, Dict, Tuple, Optional, Any
from typing import Protocol, runtime_checkable
from d2lib.utils import slugify, strip_d2_formatting

# Increase CSV field size limit for large D2 fields
csv.field_size_limit(1000000)

LOCALE_TO_BCP47: Dict[str, str] = {
    "enUS": "en",
    "deDE": "de",
    "esES": "es",
    "esMX": "es-MX",
    "frFR": "fr",
    "itIT": "it",
    "jaJP": "ja",
    "koKR": "ko",
    "plPL": "pl",
    "ptBR": "pt-BR",
    "ruRU": "ru",
    "zhCN": "zh-Hans",
    "zhTW": "zh-Hant",
}

_DIFFICULTY_STRING_KEYS: Dict[str, Tuple[str, str]] = {
    "1": ("strCreateGameNormalText", "Normal"),
    "normal": ("strCreateGameNormalText", "Normal"),
    "2": ("strCreateGameNightmareText", "Nightmare"),
    "nightmare": ("strCreateGameNightmareText", "Nightmare"),
    "3": ("strCreateGameHellText", "Hell"),
    "hell": ("strCreateGameHellText", "Hell"),
}

_ELEMENT_STRING_KEYS: Dict[str, Tuple[Tuple[str, ...], str]] = {
    "fire": (("strskltree25", "ecfra"), "Fire"),
    "cold": (("strskltree23", "strhirespecial6"), "Cold"),
    "ltng": (("strskltree24", "skillname49"), "Lightning"),
    "pois": (("strskltree17", "poison"), "Poison"),
    "mag": (("strbsmagic",), "Magic"),
    "burn": (("burn",), "Burn"),
    "stun": (("skillname139",), "Stun"),
    "phys": (("physical",), "Physical"),
}


def locale_to_html_lang(locale: str) -> str:
    """Converts a D2R locale code (e.g. koKR, deDE) into a BCP-47 HTML lang attribute."""
    clean = str(locale or "").strip()
    if clean in LOCALE_TO_BCP47:
        return LOCALE_TO_BCP47[clean]
    if len(clean) >= 2 and clean[:2].isalpha():
        return clean[:2].lower()
    return "en"


@runtime_checkable
class D2RepositoryProtocol(Protocol):
    """Structural interface for D2 data access.

    Services and builders should type-hint against this Protocol rather than
    the concrete D2Repository class, keeping them decoupled from file I/O
    details and making unit-testing with lightweight fakes straightforward.
    """
    def get_excel_table(self, table_name: str) -> List[Dict[str, str]]: ...
    def get_string(self, key: str) -> str: ...
    def load_tsv(self, file_path: str) -> List[Dict[str, str]]: ...

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
    def __init__(self, mpq_path: str, locale: str = "enUS"):
        self.mpq_path: str = os.path.abspath(mpq_path)
        self.locale: str = str(locale or "enUS").strip() or "enUS"
        self.repo_root: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        # Supplemental files should be placed in data/retail/ within the repo
        self.supplemental_path: str = os.path.join(self.repo_root, "data", "retail")
        self.strings: Dict[str, str] = {}
        self.canonical_strings: Dict[str, str] = {}
        self.excel_cache: Dict[str, List[Dict[str, str]]] = {}
        self.excel_sources: Dict[str, str] = {}
        self._load_strings()

    def _candidate_string_dirs(self) -> List[str]:
        return [
            os.path.join(self.mpq_path, "data", "local", "lng", "strings"),
            os.path.join(self.mpq_path, "local", "lng", "strings"),
            os.path.join(self.mpq_path, "strings"),
        ]

    def _candidate_excel_paths(self, table_name: str) -> List[str]:
        filename = f"{table_name}.txt"
        return [
            os.path.join(self.mpq_path, "data", "global", "excel", filename),
            os.path.join(self.mpq_path, "global", "excel", filename),
            os.path.join(self.mpq_path, "excel", filename),
        ]

    def _load_strings(self) -> None:
        """Loads string JSON files with strict precedence (Mod > Retail) and per-key enUS fallback."""
        if not hasattr(self, "canonical_strings"):
            self.canonical_strings = {}
        ordered_dirs = []

        # 1. Highest Priority: Mod strings (from MPQ path)
        for mod_string_dir in self._candidate_string_dirs():
            if os.path.exists(mod_string_dir):
                ordered_dirs.append(mod_string_dir)

        # 2. Supplemental Fallback: Retail strings
        retail_string_dirs = [
            os.path.join(self.supplemental_path, "local", "lng", "strings"),
            os.path.join(self.supplemental_path, "strings"),
        ]
        for retail_string_dir in retail_string_dirs:
            if os.path.exists(retail_string_dir):
                ordered_dirs.append(retail_string_dir)

        for string_dir in ordered_dirs:
            for filename in sorted(os.listdir(string_dir)):
                if not filename.endswith(".json"):
                    continue
                # Exclude localization overlays (e.g. chinese-overlay.json censorship overrides)
                if "overlay" in filename.lower():
                    continue
                filepath = os.path.join(string_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                        clean_content = strip_json_comments(content)
                        data = json.loads(clean_content)
                        for entry in data:
                            if not isinstance(entry, dict) or "Key" not in entry:
                                continue
                            key_lower = str(entry["Key"]).lower()
                            locale_val = entry.get(self.locale)
                            en_val = entry.get("enUS")
                            if key_lower not in self.canonical_strings and isinstance(en_val, str) and en_val.strip():
                                self.canonical_strings[key_lower] = en_val
                            if key_lower in self.strings:
                                continue
                            if isinstance(locale_val, str) and locale_val.strip():
                                self.strings[key_lower] = locale_val
                            elif isinstance(en_val, str):
                                self.strings[key_lower] = en_val
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
        
        data = []
        source_path = ""
        for filepath in self._candidate_excel_paths(table_name):
            if not os.path.exists(filepath):
                continue
            data = self.load_tsv(filepath)
            if data:
                source_path = filepath
                break
        
        # 2. Try Supplemental Fallback ONLY if file is missing from mod
        if not data:
            supp_file = os.path.join(self.supplemental_path, "global", "excel", f"{table_name}.txt")
            if os.path.exists(supp_file):
                data = self.load_tsv(supp_file)
                if data:
                    source_path = supp_file
        
        self.excel_cache[table_name] = data
        self.excel_sources[table_name] = source_path
        return data

    def get_string(self, key: str) -> str:
        """Resolves a D2 string key to its localized value and strips formatting codes."""
        if not key:
            return ""
        raw = self.strings.get(key.lower(), key)
        return strip_d2_formatting(raw)

    def get_canonical_string(self, key: str) -> str:
        """Resolves a D2 string key to its canonical enUS text with formatting stripped."""
        if not key:
            return ""
        raw = getattr(self, "canonical_strings", {}).get(key.lower(), "")
        return strip_d2_formatting(raw) if raw else ""


def resolve_localized_string(repo: D2RepositoryProtocol, key: str) -> str:
    """Resolves a string key only when a non-empty localization entry exists."""
    clean_key = str(key or "").strip()
    if not clean_key:
        return ""
    localized = str(repo.get_string(clean_key) or "").strip()
    if not localized:
        return ""
    strings_map = getattr(repo, "strings", None)
    if isinstance(strings_map, dict):
        if clean_key.lower() in strings_map or clean_key in strings_map:
            return localized
        if localized.casefold() != clean_key.casefold():
            return localized
        return ""
    return localized if localized.casefold() != clean_key.casefold() else ""


def resolve_difficulty_name(repo: D2RepositoryProtocol, difficulty: Any) -> str:
    """Resolves a numeric or canonical D2 difficulty key using strCreateGame*Text localization."""
    raw = str(difficulty or "").strip()
    if not raw:
        return ""
    entry = _DIFFICULTY_STRING_KEYS.get(raw.casefold())
    if entry is None:
        return resolve_localized_string(repo, raw) or raw
    string_key, fallback = entry
    return resolve_localized_string(repo, string_key) or fallback


def resolve_canonical_string(repo: D2RepositoryProtocol, key: str) -> str:
    """Resolves a string key to canonical enUS text when available, else falls back to localized text."""
    clean_key = str(key or "").strip()
    if not clean_key:
        return ""
    if hasattr(repo, "get_canonical_string"):
        canonical = str(repo.get_canonical_string(clean_key) or "").strip()
        if canonical:
            return canonical
    return resolve_localized_string(repo, clean_key)


def resolve_element_name(repo: Optional[D2RepositoryProtocol], etype: Any) -> str:
    """Resolves a canonical D2 EType code (e.g. 'fire', 'pois') to a localized element name."""
    raw = str(etype or "").strip()
    if not raw:
        return ""
    entry = _ELEMENT_STRING_KEYS.get(raw.casefold())
    if entry is None:
        return (resolve_localized_string(repo, raw) if repo is not None else "") or raw
    string_keys, fallback = entry
    if repo is not None:
        for string_key in string_keys:
            localized = resolve_localized_string(repo, string_key)
            if localized:
                return localized
    return fallback


def get_charstats_class_rows(repo: D2RepositoryProtocol) -> List[Dict[str, str]]:
    """Returns non-separator class rows from charstats.txt in table order."""
    return [
        row for row in repo.get_excel_table("charstats")
        if str(row.get("class", "")).strip()
        and str(row.get("class", "")).strip().casefold() != "expansion"
    ]


def get_class_name_maps(repo: D2RepositoryProtocol) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Maps canonical class indices and 3-letter codes from charstats.txt to localized names."""
    by_index: Dict[str, str] = {}
    by_abbr: Dict[str, str] = {}
    for index, row in enumerate(get_charstats_class_rows(repo)):
        raw_class = str(row.get("class", "")).strip()
        localized = str(repo.get_string(raw_class) or "").strip() or raw_class
        by_index[str(index)] = localized
        by_abbr[raw_class[:3].casefold()] = localized
    return by_index, by_abbr


def get_class_slug_map(repo: D2RepositoryProtocol) -> Dict[str, str]:
    """Maps 3-letter class codes from charstats.txt to locale-stable URL slugs."""
    return {
        str(row.get("class", "")).strip()[:3].casefold(): slugify(str(row.get("class", "")).strip())
        for row in get_charstats_class_rows(repo)
    }
