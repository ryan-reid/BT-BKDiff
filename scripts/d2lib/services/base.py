from __future__ import annotations
import re
from typing import List, Dict, Optional, Any
from d2lib.repository import normalize_d2_value
from d2lib.models import ExcelDiffDTO

def _row_changed(row: Dict[str, str], old_row: Optional[Dict[str, str]]) -> bool:
    if not old_row:
        return True
    for key in set(row.keys()) | set(old_row.keys()):
        if normalize_d2_value(row.get(key, "")) != normalize_d2_value(old_row.get(key, "")):
            return True
    return False

def _status_for_row(key: str, row: Dict[str, str], old_rows: Dict[str, Dict[str, str]]) -> str:
    old_row = old_rows.get(key)
    if not old_row:
        return "added"
    return "modified" if _row_changed(row, old_row) else "unchanged"

def _summarize_excel_diff(diff: ExcelDiffDTO, limit: int = 24) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for key in diff.get("added_rows", [])[:limit]:
        rows.append({"name": key, "status": "added", "fields": [], "field_count": 0})
    for key in diff.get("removed_rows", [])[:limit]:
        rows.append({"name": key, "status": "removed", "fields": [], "field_count": 0})
    remaining = max(0, limit - len(rows))
    for key, changes in list(diff.get("modified_rows", {}).items())[:remaining]:
        fields = sorted(changes.keys())
        rows.append({"name": key, "status": "modified", "fields": fields[:8], "field_count": len(fields)})
    return rows

def _slugify(value: str) -> str:
    text = value.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-") or "untitled"
