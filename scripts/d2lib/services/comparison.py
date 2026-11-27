from __future__ import annotations
import re
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import normalize_d2_value
from d2lib.models import ExcelDiffDTO, ItemDiffDTO

from d2lib.utils import normalize_d2_text

class ItemComparisonService:
    def __init__(self):
        pass

    def normalize_text(self, s: str) -> str:
        return normalize_d2_text(s)

    def align_properties(self, old_props: List[str], new_props: List[str]) -> List[Tuple[str, str]]:
        def get_stat_key(s):
            s = self.normalize_text(s)
            return re.sub(r'[+-]?\d+(?:-\d+)?', '', s).strip().lower()

        aligned = []
        old_used, new_used = set(), set()
        for i, op in enumerate(old_props):
            onorm = self.normalize_text(op)
            for j, np in enumerate(new_props):
                if j in new_used: continue
                if onorm == self.normalize_text(np):
                    aligned.append((op, np))
                    old_used.add(i); new_used.add(j); break
        for i, op in enumerate(old_props):
            if i in old_used: continue
            okey = get_stat_key(op)
            for j, np in enumerate(new_props):
                if j in new_used: continue
                if okey == get_stat_key(np) and okey != "":
                    aligned.append((op, np))
                    old_used.add(i); new_used.add(j); break
        for i, op in enumerate(old_props):
            if i not in old_used: aligned.append((op, "(removed)"))
        for j, np in enumerate(new_props):
            if j not in new_used: aligned.append(("", np))
        return aligned

    @staticmethod
    def _property_signature(prop: Dict[str, Any]) -> Tuple[Any, ...]:
        code = str(prop.get("canonical_code") or prop.get("code") or "").strip().lower()
        param_raw = prop.get("parameter_key")
        if param_raw in (None, ""):
            param_raw = prop.get("param", "")
        param = str(param_raw).strip().lower()
        min_v = str(prop.get("min_val", "")).strip()
        max_v = str(prop.get("max_val", "")).strip()
        return (code, param, min_v, max_v)

    @staticmethod
    def _raw_sequence(raw_row: Dict[str, Any], prefix: str, count: int) -> Tuple[bool, List[str]]:
        has_cols = any(f"{prefix}{i}" in raw_row for i in range(1, count + 1))
        values = [
            str(raw_row.get(f"{prefix}{i}", "")).strip().lower()
            for i in range(1, count + 1)
            if str(raw_row.get(f"{prefix}{i}", "")).strip() not in ("", "xxx")
        ]
        return has_cols, values

    def compare_item_lists(self, bk_items: Dict[str, Any], bt_items: Dict[str, Any]) -> ItemDiffDTO:
        added_ids = [k for k in bk_items if k not in bt_items]
        removed_ids = [k for k in bt_items if k not in bk_items]
        modified = {}
        common = [k for k in bk_items if k in bt_items]
        for k in common:
            bk, bt = bk_items[k], bt_items[k]

            bk_base = bk.get('base_item') or ', '.join(bk.get('base_items', []))
            bt_base = bt.get('base_item') or ', '.join(bt.get('base_items', []))
            bk_lvl = bk.get('lvl_req', '0')
            bt_lvl = bt.get('lvl_req', '0')

            raw_bk = bk.get('raw_row') or {}
            raw_bt = bt.get('raw_row') or {}
            bk_code = str(raw_bk.get('code') or raw_bk.get('item') or '').strip().lower()
            bt_code = str(raw_bt.get('code') or raw_bt.get('item') or '').strip().lower()
            if bk_code and bt_code:
                base_diff = bk_code != bt_code
            else:
                bk_has_it, bk_it = self._raw_sequence(raw_bk, 'itype', 6)
                bt_has_it, bt_it = self._raw_sequence(raw_bt, 'itype', 6)
                bk_has_rn, bk_rn = self._raw_sequence(raw_bk, 'Rune', 6)
                bt_has_rn, bt_rn = self._raw_sequence(raw_bt, 'Rune', 6)
                if (bk_has_it and bt_has_it) or (bk_has_rn and bt_has_rn):
                    base_diff = (bk_it != bt_it if (bk_has_it and bt_has_it) else False) or (
                        bk_rn != bt_rn if (bk_has_rn and bt_has_rn) else False
                    )
                else:
                    base_diff = self.normalize_text(bk_base) != self.normalize_text(bt_base)

            header_diff = base_diff or (self.normalize_text(bk_lvl) != self.normalize_text(bt_lvl))

            bk_props = bk.get('properties', [])
            bt_props = bt.get('properties', [])
            all_structured = all(
                any(field in p for field in ('min_val', 'max_val', 'numeric_values', 'parameter_key'))
                for p in (*bk_props, *bt_props)
            )
            if all_structured and (bk_props or bt_props):
                bk_norm = sorted([self._property_signature(p) for p in bk_props])
                bt_norm = sorted([self._property_signature(p) for p in bt_props])
            else:
                bk_norm = sorted([self.normalize_text(p['resolved_text']) for p in bk_props])
                bt_norm = sorted([self.normalize_text(p['resolved_text']) for p in bt_props])

            if header_diff or bk_norm != bt_norm:
                modified[k] = {
                    'name': bk.get('display_name') or bk.get('name'),
                    'bk_base': bk_base, 'bt_base': bt_base,
                    'bk_lvl': bk_lvl, 'bt_lvl': bt_lvl,
                    'bk_props': [p['resolved_text'] for p in bk['properties']],
                    'bt_props': [p['resolved_text'] for p in bt['properties']],
                    'item_type': bk.get('item_type', 'Other'),
                    'raw_row': bk.get('raw_row', {})
                }
        return {
            'added': {k: bk_items[k] for k in added_ids},
            'removed': {k: bt_items[k] for k in removed_ids},
            'modified': modified
        }

class ExcelComparisonService:
    @staticmethod
    def compare_tables(table_bk: List[Dict[str, str]], table_bt: List[Dict[str, str]], key_col: str, filename: str) -> ExcelDiffDTO:
        map_new = {str(row[key_col]).strip().lower(): row for row in table_bk if row.get(key_col)}
        map_old = {str(row[key_col]).strip().lower(): row for row in table_bt if row.get(key_col)}
        h_new = list(table_bk[0].keys()) if table_bk else []; h_old = list(table_bt[0].keys()) if table_bt else []
        common_cols = [c for c in h_new if c in h_old]
        all_keys = sorted(set(map_new.keys()) | set(map_old.keys()))
        diff = {
            "filename": filename, "key_used": key_col, "added_cols": [c for c in h_new if c not in h_old],
            "removed_cols": [c for c in h_old if c not in h_new], "added_rows": [], "removed_rows": [], "modified_rows": {}
        }
        for key in all_keys:
            if key not in map_old: diff["added_rows"].append(key)
            elif key not in map_new: diff["removed_rows"].append(key)
            else:
                row_diff = {}
                for col in common_cols:
                    if normalize_d2_value(map_new[key][col]) != normalize_d2_value(map_old[key][col]):
                        row_diff[col] = {"bk_new": map_new[key][col], "bt_old": map_old[key][col]}
                if row_diff: diff["modified_rows"][key] = row_diff
        return diff
