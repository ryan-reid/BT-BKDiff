from __future__ import annotations
from difflib import SequenceMatcher
from itertools import zip_longest
from typing import Any, Dict, List, Optional, Tuple

from d2lib.services.resolver import PropertyResolverService


def _affix_tier_match(old, new) -> int:
    if old["settings"] == new["settings"] and old["properties"] == new["properties"]:
        return 100

    before, after = old["identity"], new["identity"]
    old_types, new_types = set(before["itype"]), set(after["itype"])
    same_types = bool(old_types and old_types == new_types)
    type_overlap = bool(old_types & new_types)
    property_overlap = bool(set(before["properties"]) & set(after["properties"]))
    same = {field for field, value in before.items() if value and value == after[field]}
    if not (
        ("level" in same and (type_overlap or "group" in same))
        or (same_types and ("levelreq" in same or "group" in same or property_overlap))
        or ({"level", "version"} <= same and property_overlap)
    ):
        return 0

    return (
        10 * same_types + 7 * ("level" in same) + 5 * ("version" in same)
        + 4 * ("group" in same) + 3 * type_overlap + 3 * ("levelreq" in same)
        + 2 * property_overlap + len(same & {"class", "etype", "spawnable"})
    )


def affix_card_context(entry: Dict[str, Any]) -> Dict[str, Any]:
    def comparison_rows(old_roll, new_roll, field):
        old_values, new_values = old_roll.get(field, ()), new_roll.get(field, ())
        rows = []
        for _, old_start, old_end, new_start, new_end in SequenceMatcher(None, old_values, new_values).get_opcodes():
            for old, new in zip_longest(old_values[old_start:old_end], new_values[new_start:new_end], fillvalue=""):
                status = "same" if old == new else "changed" if old and new else "added" if new else "removed"
                rows.append({"old": old, "new": new, "status": status})
        return rows

    old = entry["old"]
    new = entry["new"]
    card = {
        "title": entry["label"],
        "summary": entry["status"],
        "status": entry["status"].lower(),
        "search_text": entry["search_text"],
        "card_quality": "magic",
    }
    if len(old) <= 1 and len(new) <= 1:
        old_roll = old[0] if old else {}
        new_roll = new[0] if new else {}
        card["stat_rows"] = comparison_rows(old_roll, new_roll, "settings")
        card["property_rows"] = comparison_rows(old_roll, new_roll, "properties")
        return card

    # Match exact copies first, then use the strongest shared tier metadata.
    # Source order only breaks ties between otherwise equivalent candidates.
    candidates = sorted(
        (-score, old_index, new_index)
        for old_index, old_roll in enumerate(old)
        for new_index, new_roll in enumerate(new)
        if (score := _affix_tier_match(old_roll, new_roll))
    )
    matches = {}
    used_old = set()
    for _, old_index, new_index in candidates:
        if old_index not in used_old and new_index not in matches:
            matches[new_index] = old[old_index]
            used_old.add(old_index)
    pairs = [(matches.get(index, {}), roll) for index, roll in enumerate(new)]
    pairs.extend((roll, {}) for index, roll in enumerate(old) if index not in used_old)

    card["comparison_sections"] = [
        {
            "title": f"Roll {index}",
            "stat_rows": comparison_rows(old_roll, new_roll, "settings"),
            "property_rows": comparison_rows(old_roll, new_roll, "properties"),
        }
        for index, (old_roll, new_roll) in enumerate(pairs, 1)
    ]
    return card


def item_diff_status(entry: Dict[str, Any], old_entry: Optional[Dict[str, Any]]) -> str:
    if old_entry is None:
        return "added"
    if entries_match(entry, old_entry):
        return "unchanged"
    return "modified"


def entries_match(entry: Dict[str, Any], old_entry: Dict[str, Any]) -> bool:
    keys = ["base_item", "item_type", "lvl_req"]
    if any(str(entry.get(key, "")) != str(old_entry.get(key, "")) for key in keys):
        return False
    return property_texts(entry) == property_texts(old_entry)


def property_texts(entry: Dict[str, Any]) -> List[str]:
    return [str(prop.get("resolved_text", "")) for prop in entry.get("properties", [])]


def property_occurrence_map(entry: Dict[str, Any]) -> Dict[Tuple[str, str, int], str]:
    occurrences: Dict[Tuple[str, str], int] = {}
    values: Dict[Tuple[str, str, int], str] = {}

    for prop in entry.get("properties", []):
        code = str(prop.get("code", "")).strip() or "unknown"
        param = str(prop.get("param", "")).strip()
        base_key = (code, param)
        occurrences[base_key] = occurrences.get(base_key, 0) + 1
        values[(code, param, occurrences[base_key])] = str(prop.get("resolved_text", "")).strip()

    for partial in entry.get("partial_set_properties", []) or []:
        count = partial.get("count", 0)
        for prop in partial.get("properties", []):
            code = str(prop.get("code", "")).strip() or "unknown"
            param = str(prop.get("param", "")).strip()
            code_key = f"partial-{count}-{code}"
            base_key = (code_key, param)
            occurrences[base_key] = occurrences.get(base_key, 0) + 1
            resolved = str(prop.get("resolved_text", "")).strip()
            values[(code_key, param, occurrences[base_key])] = f"{resolved} (With {count} Items)"

    return values


def rune_property_occurrence_map(entry: Dict[str, Any]) -> Dict[Tuple[str, str, int], str]:
    occurrences: Dict[Tuple[str, str], int] = {}
    values: Dict[Tuple[str, str, int], str] = {}
    for rune_entry in entry.get("rune_properties", []):
        for prop in rune_entry.get("properties", []):
            code = str(prop.get("code", "")).strip() or "unknown"
            param = str(prop.get("param", "")).strip()
            text = str(prop.get("resolved_text", "")).strip()
            if not text:
                continue
            base_key = (code, param)
            occurrences[base_key] = occurrences.get(base_key, 0) + 1
            values[(code, param, occurrences[base_key])] = text
    return values


def comparison_property_label(
    old_value: str, new_value: str, code: str, occurrence: int
) -> str:
    # Resolved text already contains the stat name (e.g. '+10 to Strength'),
    # so a separate label would be redundant.
    return ""


def comparison_stat_rows(
    entry: Dict[str, Any],
    family: str,
    old_entry: Optional[Dict[str, Any]],
) -> List[Tuple[str, str, str]]:
    def get_val(item: Optional[Dict[str, Any]], key: str, subkey: Optional[str] = None) -> str:
        if not item:
            return ""
        if subkey:
            return str(item.get("raw_row", {}).get(subkey, ""))
        return str(item.get(key, ""))

    if family == "runeword":
        return [
            ("Runes", " + ".join(old_entry.get("runes", [])) if old_entry else "", " + ".join(entry.get("runes", []))),
            ("Base Items", ", ".join(old_entry.get("base_items", [])) if old_entry else "", ", ".join(entry.get("base_items", []))),
            ("Required Level", get_val(old_entry, "required_level"), get_val(entry, "required_level")),
        ]

    fields: List[Tuple[str, str, str]] = [
        ("Base Item", get_val(old_entry, "base_item"), get_val(entry, "base_item")),
        ("Item Type", get_val(old_entry, "item_type"), get_val(entry, "item_type")),
        ("Level Requirement", get_val(old_entry, "lvl_req"), get_val(entry, "lvl_req")),
    ]
    if family == "set":
        fields.append(("Set", get_val(old_entry, "raw_row", "set"), get_val(entry, "raw_row", "set")))
    return fields


def runeword_compare_rows(
    entry: Dict[str, Any],
    old_entry: Optional[Dict[str, Any]],
) -> List[Dict[str, str]]:
    old_props = property_occurrence_map(old_entry or {})
    new_props = property_occurrence_map(entry)
    keys = list(new_props.keys()) + [k for k in old_props if k not in new_props]

    def _status(old_v: str, new_v: str) -> str:
        if old_v and new_v:
            return "changed" if old_v != new_v else "same"
        return "added" if new_v else "removed" if old_v else "same"

    rows: List[Dict[str, str]] = [
        {"old": old_props.get(k, ""), "new": new_props.get(k, ""), "status": _status(old_props.get(k, ""), new_props.get(k, ""))}
        for k in keys
    ]

    old_rune = rune_property_occurrence_map(old_entry or {})
    new_rune = rune_property_occurrence_map(entry)
    if old_rune or new_rune:
        rows.append({"old": "", "new": "", "status": "separator"})
        rune_keys = list(new_rune.keys()) + [k for k in old_rune if k not in new_rune]
        rows.extend(
            {"old": old_rune.get(k, ""), "new": new_rune.get(k, ""), "status": _status(old_rune.get(k, ""), new_rune.get(k, ""))}
            for k in rune_keys
        )
    return rows


def comparison_summary_context(comparison: Dict[str, Any]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {"added": [], "removed": [], "changed": []}
    for row in comparison.get("rows", []):
        label = str(row.get("label", ""))
        old_value = str(row.get("old", ""))
        new_value = str(row.get("new", ""))
        status = row.get("status", "")
        if status == "added" and new_value:
            summary["added"].append({"label": label, "value": new_value})
        elif status == "removed" and old_value:
            summary["removed"].append({"label": label, "value": old_value})
        elif status == "changed":
            summary["changed"].append({"label": label, "old": old_value, "new": new_value})
    summary["has_changes"] = any(summary[key] for key in ("added", "removed", "changed"))
    return summary


def item_comparison_context(
    entry: Dict[str, Any],
    family: str,
    old_entry: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    stat_rows = []
    for label, old_value, new_value in comparison_stat_rows(entry, family, old_entry):
        status = "added" if new_value and not old_value else "same" if old_value == new_value else "changed"
        stat_rows.append({"label": label, "old": old_value, "new": new_value, "status": status})

    property_rows = []
    old_props = property_occurrence_map(old_entry or {})
    new_props = property_occurrence_map(entry)
    all_keys = list(new_props.keys()) + [k for k in old_props if k not in new_props]
    for key in all_keys:
        old_val = old_props.get(key, "")
        new_val = new_props.get(key, "")
        if old_val and new_val:
            status = "changed" if old_val != new_val else "same"
        elif new_val:
            status = "added"
        elif old_val:
            status = "removed"
        else:
            status = "same"
        property_rows.append({
            "label": comparison_property_label(old_val, new_val, key[0], key[2]),
            "old": old_val,
            "new": new_val,
            "status": status,
        })

    has_changes = any(r["status"] != "same" for r in stat_rows + property_rows)
    return {
        "state": "added" if not old_entry else "modified" if has_changes else "unchanged",
        "stat_rows": stat_rows,
        "property_rows": property_rows,
        "rows": [r for r in stat_rows + property_rows if r["status"] != "same"],
    }


def base_item_comparison_context(
    item: Dict[str, Any],
    old_item: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    stat_rows: List[Dict[str, Any]] = []

    def range_text(row: Optional[Dict[str, Any]], min_key: str, max_key: str) -> str:
        if not row:
            return ""
        min_v = row.get(min_key)
        max_v = row.get(max_key)
        if min_v is None or max_v is None or (int(min_v) == 0 and int(max_v) == 0):
            return ""
        return f"{min_v}-{max_v}"

    def add_stat(label: str, old_v: str, new_v: str) -> None:
        if not old_v and not new_v:
            return
        status = "same" if old_v == new_v else "added" if not old_v else "removed" if not new_v else "changed"
        stat_rows.append({"label": label, "old": old_v, "new": new_v, "status": status})

    add_stat("Def", range_text(old_item, "defense_min", "defense_max"), range_text(item, "defense_min", "defense_max"))
    has_damage = False
    for label, min_key, max_key in [
        ("One-Hand Damage", "damage_min", "damage_max"),
        ("Two-Hand Damage", "two_hand_damage_min", "two_hand_damage_max"),
        ("Throwing Damage", "throw_damage_min", "throw_damage_max"),
    ]:
        old_damage = range_text(old_item, min_key, max_key)
        new_damage = range_text(item, min_key, max_key)
        if min_key == "damage_min":
            if old_item and old_item.get("two_handed_only"):
                old_damage = ""
            if item.get("two_handed_only"):
                new_damage = ""
        add_stat(label, old_damage, new_damage)
        has_damage = has_damage or bool(old_damage or new_damage)

    for label, key in [("Base Lvl", "level"), ("Req Lvl", "level_req"), ("Str", "str_req"), ("Dex", "dex_req"), ("Max Sockets", "sockets")]:
        add_stat(label, str(old_item.get(key, "")) if old_item else "", str(item.get(key, "")))

    old_block = int(old_item.get("block", 0)) if old_item else 0
    new_block = int(item.get("block", 0))
    if old_block or new_block:
        add_stat("Block", str(old_block) if old_item else "", str(new_block))

    if has_damage:
        old_speed = f"{old_item.get('speed', '')} ({old_item.get('speed_label', '')})" if old_item else ""
        add_stat("WSM", old_speed, f"{item.get('speed', '')} ({item.get('speed_label', '')})")

    property_rows: List[Dict[str, Any]] = []

    def add_prop_group(label: str, old_list: List[str], new_list: List[str]) -> None:
        for i in range(max(len(old_list), len(new_list))):
            o = old_list[i] if i < len(old_list) else ""
            n = new_list[i] if i < len(new_list) else ""
            status = "same" if o == n else "added" if n and not o else "removed" if o and not n else "changed"
            property_rows.append({"label": label if i == 0 else "", "old": o, "new": n, "status": status})

    add_prop_group("Inherent", old_item.get("inherent_stats", []) if old_item else [], item.get("inherent_stats", []))
    add_prop_group("Auto Prefix", old_item.get("auto_prefix_summary", []) if old_item else [], item.get("auto_prefix_summary", []))
    add_prop_group("Superior Bonuses", old_item.get("quality_bonus_summary", []) if old_item else [], item.get("quality_bonus_summary", []))

    has_changes = any(r["status"] != "same" for r in stat_rows + property_rows)
    return {
        "state": "added" if not old_item else "modified" if has_changes else "unchanged",
        "stat_rows": stat_rows,
        "property_rows": property_rows,
    }


def gem_rune_comparison_context(
    item: Dict[str, Any],
    old_item: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    stat_rows = []
    for label, key in [("Level", "level"), ("Level Requirement", "level_req"), ("Cost", "cost")]:
        old_val = str(old_item.get(key, "")) if old_item else ""
        new_val = str(item.get(key, ""))
        status = "added" if new_val and not old_val else "same" if old_val == new_val else "changed"
        stat_rows.append({"label": label, "old": old_val, "new": new_val, "status": status})

    old_effects = old_item.get("socket_effects", {}) if old_item else {}
    new_effects = item.get("socket_effects", {})
    socket_rows = []
    for slot in ["Weapon", "Armor/Helm", "Shield"]:
        old_eff = "; ".join(old_effects.get(slot, []))
        new_eff = "; ".join(new_effects.get(slot, []))
        status = "added" if new_eff and not old_eff else "same" if old_eff == new_eff else "changed"
        socket_rows.append({"label": slot, "old": old_eff, "new": new_eff, "status": status})

    has_changes = any(r["status"] != "same" for r in stat_rows + socket_rows)
    return {
        "state": "added" if not old_item else "modified" if has_changes else "unchanged",
        "stat_rows": stat_rows,
        "property_rows": socket_rows,
    }


def set_bonus_comparison(
    set_name: str,
    bk_row: Dict[str, str],
    rt_row: Dict[str, str],
    resolver_bk: PropertyResolverService,
    resolver_rt: PropertyResolverService,
) -> List[Dict[str, Any]]:
    bonus_rows: List[Dict[str, Any]] = []

    def _resolve(resolver: PropertyResolverService, row: Dict[str, str], code_k: str, param_k: str, min_k: str, max_k: str) -> str:
        code = row.get(code_k, "").strip()
        if not code:
            return ""
        return resolver.resolve_property(code, row.get(param_k, ""), row.get(min_k, ""), row.get(max_k, ""))["resolved_text"]

    def _status(o: str, n: str) -> str:
        return "same" if o == n else "added" if n and not o else "removed" if o and not n else "changed"

    def _append(label: str, o_val: str, n_val: str, is_sep: bool) -> None:
        if o_val or n_val:
            bonus_rows.append({"label": label, "old": o_val, "new": n_val, "status": _status(o_val, n_val), "is_separator": is_sep})

    for count in range(2, 6):
        for suffix in ["a", "b"]:
            o = _resolve(resolver_rt, rt_row, f"PCode{count}{suffix}", f"PParam{count}{suffix}", f"PMin{count}{suffix}", f"PMax{count}{suffix}")
            n = _resolve(resolver_bk, bk_row, f"PCode{count}{suffix}", f"PParam{count}{suffix}", f"PMin{count}{suffix}", f"PMax{count}{suffix}")
            _append(f"{count} Pieces" if suffix == "a" else "", o, n, suffix == "a")

    for i in range(1, 9):
        o = _resolve(resolver_rt, rt_row, f"FCode{i}", f"FParam{i}", f"FMin{i}", f"FMax{i}")
        n = _resolve(resolver_bk, bk_row, f"FCode{i}", f"FParam{i}", f"FMin{i}", f"FMax{i}")
        _append("Full Set" if i == 1 else "", o, n, i == 1)

    return bonus_rows
