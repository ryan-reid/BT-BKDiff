from __future__ import annotations
from difflib import SequenceMatcher
from itertools import zip_longest
from typing import Any, Dict, List, Optional, Tuple

from d2lib.services.resolver import PropertyResolverService


def skill_card_context(skill: Dict[str, Any]) -> Dict[str, Any]:
    tooltip = skill["tooltip"]
    base_rows = [tooltip] if tooltip["old"] or tooltip["new"] else []
    base_rows.extend(skill["facts"])

    return {
        "title": skill["name"],
        "anchor": skill["slug"],
        "summary": skill["display_status"].title(),
        "status": skill["display_status"],
        "search_text": skill["search_text"],
        "card_quality": "magic",
        "comparison_sections": [
            {"title": title, "stat_rows": [
                dict(row, status="same" if row["status"] == "unchanged" else row["status"])
                for row in rows
            ]}
            for title, rows in (
                ("Base skill information", base_rows),
                ("Formulas", skill["formula_rows"]),
                ("Synergies", skill["synergy_rows"]),
            )
            if rows
        ],
    }


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


def affix_card_contexts(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    def comparison_rows(old_roll, new_roll, field):
        old_values, new_values = old_roll.get(field, ()), new_roll.get(field, ())
        if field == "settings":
            def visible_settings(roll):
                entries = roll.get("setting_entries")
                if entries:
                    return [text for key, text in entries if key not in {"group", "version"}]
                return [
                    setting for setting in roll.get("settings", ())
                    if not setting.startswith(("Group ", "Version "))
                ]

            old_values, new_values = visible_settings(old_roll), visible_settings(new_roll)
        rows = []
        for _, old_start, old_end, new_start, new_end in SequenceMatcher(None, old_values, new_values).get_opcodes():
            for old, new in zip_longest(old_values[old_start:old_end], new_values[new_start:new_end], fillvalue=""):
                status = "same" if old == new else "changed" if old and new else "added" if new else "removed"
                rows.append({"old": old, "new": new, "status": status})
        return rows

    def item_type_codes(rolls):
        return "|".join(sorted({code for roll in rolls for code in roll.get("item_types", {})}))

    cards = []
    for old_roll, new_roll in _affix_roll_pairs(entry["old"], entry["new"]):
        status = (
            "Added" if not old_roll else "Removed" if not new_roll
            else "Unchanged" if _affix_tier_match(old_roll, new_roll) == 100 else "Changed"
        )
        rolls = (old_roll, new_roll)
        cards.append({
            "title": entry["label"],
            "summary": status,
            "status": status.lower(),
            "search_text": " ".join([
                entry["label"], status,
                *(value for roll in rolls for field in ("settings", "properties") for value in roll.get(field, ())),
            ]),
            "card_quality": "magic",
            "item_type": item_type_codes(rolls),
            "affix_spawnable": new_roll.get("spawnable", False),
            "rare_item_types": item_type_codes([new_roll]) if new_roll.get("can_roll_on_rares") else None,
            "stat_rows": comparison_rows(old_roll, new_roll, "settings"),
            "property_rows": comparison_rows(old_roll, new_roll, "properties"),
        })
    return cards


def _affix_roll_pairs(old, new):
    if len(old) <= 1 and len(new) <= 1:
        return [(old[0] if old else {}, new[0] if new else {})]

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

    return pairs


def item_diff_status(entry: Dict[str, Any], old_entry: Optional[Dict[str, Any]]) -> str:
    if old_entry is None:
        return "added"
    if entries_match(entry, old_entry):
        return "unchanged"
    return "modified"


def _has_structured_prop(prop: Dict[str, Any]) -> bool:
    return any(key in prop for key in ("min_val", "max_val", "numeric_values", "parameter_key"))


def _property_signature(prop: Dict[str, Any]) -> Tuple[Any, ...]:
    code = str(prop.get("canonical_code") or prop.get("code") or "").strip().lower()
    if _has_structured_prop(prop):
        param_raw = prop.get("parameter_key")
        if param_raw in (None, ""):
            param_raw = prop.get("param", "")
        param = str(param_raw).strip().lower()
        min_v = str(prop.get("min_val", "")).strip()
        max_v = str(prop.get("max_val", "")).strip()
        return ("struct", code, param, min_v, max_v)
    param = str(prop.get("param", "")).strip().lower()
    return ("text", code, param, str(prop.get("resolved_text", "")).strip())


def _raw_sequence(raw_row: Dict[str, Any], prefix: str, count: int) -> Tuple[bool, List[str]]:
    has_cols = any(f"{prefix}{i}" in raw_row for i in range(1, count + 1))
    values = [
        str(raw_row.get(f"{prefix}{i}", "")).strip().lower()
        for i in range(1, count + 1)
        if str(raw_row.get(f"{prefix}{i}", "")).strip() not in ("", "xxx")
    ]
    return has_cols, values


def _is_runeword_entry(entry: Dict[str, Any]) -> bool:
    raw = entry.get("raw_row") or {}
    return (
        "runes" in entry
        or "base_items" in entry
        or "Rune1" in raw
        or "itype1" in raw
    )


def _entry_property_signatures(
    entry: Dict[str, Any],
) -> Tuple[Tuple[Tuple[Any, ...], ...], Tuple[Tuple[int, Tuple[Tuple[Any, ...], ...]], ...]]:
    main = tuple(_property_signature(prop) for prop in entry.get("properties", []))
    partial = tuple(
        (
            int(group.get("count", 0) or 0),
            tuple(_property_signature(prop) for prop in group.get("properties", [])),
        )
        for group in (entry.get("partial_set_properties") or [])
    )
    return main, partial


def entries_match(entry: Dict[str, Any], old_entry: Dict[str, Any]) -> bool:
    raw_new = entry.get("raw_row") or {}
    raw_old = old_entry.get("raw_row") or {}
    if _is_runeword_entry(entry) or _is_runeword_entry(old_entry):
        new_has_runes, new_runes = _raw_sequence(raw_new, "Rune", 6)
        old_has_runes, old_runes = _raw_sequence(raw_old, "Rune", 6)
        if new_has_runes and old_has_runes:
            if new_runes != old_runes:
                return False
        elif entry.get("runes", []) != old_entry.get("runes", []):
            return False

        new_has_types, new_types = _raw_sequence(raw_new, "itype", 6)
        old_has_types, old_types = _raw_sequence(raw_old, "itype", 6)
        if new_has_types and old_has_types:
            if new_types != old_types:
                return False
        elif entry.get("base_items", []) != old_entry.get("base_items", []):
            return False

        new_lvl = str(entry.get("required_level") if "required_level" in entry else entry.get("lvl_req", "")).strip()
        old_lvl = str(old_entry.get("required_level") if "required_level" in old_entry else old_entry.get("lvl_req", "")).strip()
        if new_lvl != old_lvl:
            return False
    else:
        new_code = str(raw_new.get("code") or raw_new.get("item") or "").strip().lower()
        old_code = str(raw_old.get("code") or raw_old.get("item") or "").strip().lower()
        if new_code and old_code:
            if new_code != old_code:
                return False
            new_lvl = str(raw_new.get("lvl req") if "lvl req" in raw_new else entry.get("lvl_req", "")).strip()
            old_lvl = str(raw_old.get("lvl req") if "lvl req" in raw_old else old_entry.get("lvl_req", "")).strip()
            if new_lvl != old_lvl:
                return False
            new_set = str(raw_new.get("set", "")).strip().lower()
            old_set = str(raw_old.get("set", "")).strip().lower()
            if (new_set or old_set) and new_set != old_set:
                return False
        else:
            keys = ["base_item", "item_type", "lvl_req"]
            if any(str(entry.get(key, "")) != str(old_entry.get(key, "")) for key in keys):
                return False

    return _entry_property_signatures(entry) == _entry_property_signatures(old_entry)


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


def _property_signature_occurrence_map(entry: Dict[str, Any]) -> Dict[Tuple[str, str, int], Tuple[Tuple[Any, ...], Tuple[Any, ...]]]:
    occurrences: Dict[Tuple[str, str], int] = {}
    signatures: Dict[Tuple[str, str, int], Tuple[Tuple[Any, ...], Tuple[Any, ...]]] = {}

    for prop in entry.get("properties", []):
        code = str(prop.get("code", "")).strip() or "unknown"
        param = str(prop.get("param", "")).strip()
        base_key = (code, param)
        occurrences[base_key] = occurrences.get(base_key, 0) + 1
        signatures[(code, param, occurrences[base_key])] = (("main",), _property_signature(prop))

    for partial in entry.get("partial_set_properties", []) or []:
        count = partial.get("count", 0)
        for prop in partial.get("properties", []):
            code = str(prop.get("code", "")).strip() or "unknown"
            param = str(prop.get("param", "")).strip()
            code_key = f"partial-{count}-{code}"
            base_key = (code_key, param)
            occurrences[base_key] = occurrences.get(base_key, 0) + 1
            signatures[(code_key, param, occurrences[base_key])] = (("partial", int(count or 0)), _property_signature(prop))

    return signatures


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


def comparison_stat_row_entries(
    entry: Dict[str, Any],
    family: str,
    old_entry: Optional[Dict[str, Any]],
) -> List[Dict[str, str]]:
    def get_val(item: Optional[Dict[str, Any]], key: str, subkey: Optional[str] = None) -> str:
        if not item:
            return ""
        if subkey:
            return str(item.get("raw_row", {}).get(subkey, ""))
        return str(item.get(key, ""))

    def row_entry(key: str, label: str, old_val: str, new_val: str, canonical_same: Optional[bool] = None) -> Dict[str, str]:
        if new_val and not old_val:
            status = "added"
        elif old_val and not new_val:
            status = "changed"
        elif canonical_same is not None:
            status = "same" if canonical_same else "changed"
        else:
            status = "same" if old_val == new_val else "changed"
        return {"key": key, "label": label, "old": old_val, "new": new_val, "status": status}

    raw_new = entry.get("raw_row") or {}
    raw_old = (old_entry or {}).get("raw_row") or {}

    if family == "runeword":
        new_has_runes, new_runes = _raw_sequence(raw_new, "Rune", 6)
        old_has_runes, old_runes = _raw_sequence(raw_old, "Rune", 6)
        runes_same = (new_runes == old_runes) if (old_entry and new_has_runes and old_has_runes) else None

        new_has_types, new_types = _raw_sequence(raw_new, "itype", 6)
        old_has_types, old_types = _raw_sequence(raw_old, "itype", 6)
        types_same = (new_types == old_types) if (old_entry and new_has_types and old_has_types) else None

        return [
            row_entry(
                "runes",
                "Runes",
                " + ".join(old_entry.get("runes", [])) if old_entry else "",
                " + ".join(entry.get("runes", [])),
                canonical_same=runes_same,
            ),
            row_entry(
                "base_items",
                "Base Items",
                ", ".join(old_entry.get("base_items", [])) if old_entry else "",
                ", ".join(entry.get("base_items", [])),
                canonical_same=types_same,
            ),
            row_entry(
                "required_level",
                "Required Level",
                get_val(old_entry, "required_level"),
                get_val(entry, "required_level"),
            ),
        ]

    code_col = "code" if family == "unique" else "item"
    new_code = str(raw_new.get(code_col, "") or raw_new.get("code", "") or raw_new.get("item", "")).strip().lower()
    old_code = str(raw_old.get(code_col, "") or raw_old.get("code", "") or raw_old.get("item", "")).strip().lower()
    base_same = (new_code == old_code) if (old_entry and new_code and old_code) else None

    old_base_text = get_val(old_entry, "base_item")
    new_base_text = get_val(entry, "base_item")
    old_type_text = get_val(old_entry, "item_type")
    new_type_text = get_val(entry, "item_type")
    type_same = True if base_same is True else (old_type_text == new_type_text if old_entry else None)

    fields: List[Dict[str, str]] = [
        row_entry("base_item", "Base Item", old_base_text, new_base_text, canonical_same=base_same),
        row_entry("item_type", "Item Type", old_type_text, new_type_text, canonical_same=type_same),
        row_entry("level_req", "Level Requirement", get_val(old_entry, "lvl_req"), get_val(entry, "lvl_req")),
    ]
    if family == "set":
        old_set = get_val(old_entry, "set_name") or get_val(old_entry, "raw_row", "set")
        new_set = get_val(entry, "set_name") or get_val(entry, "raw_row", "set")
        new_set_id = str(raw_new.get("set", "")).strip().lower()
        old_set_id = str(raw_old.get("set", "")).strip().lower()
        set_same = (new_set_id == old_set_id) if (old_entry and new_set_id and old_set_id) else None
        fields.append(row_entry("set", "Set", old_set, new_set, canonical_same=set_same))
    return fields


def comparison_stat_rows(
    entry: Dict[str, Any],
    family: str,
    old_entry: Optional[Dict[str, Any]],
) -> List[Tuple[str, str, str]]:
    return [
        (row["label"], row["old"], row["new"])
        for row in comparison_stat_row_entries(entry, family, old_entry)
    ]


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
    stat_rows = comparison_stat_row_entries(entry, family, old_entry)

    property_rows = []
    old_props = property_occurrence_map(old_entry or {})
    new_props = property_occurrence_map(entry)
    old_sigs = _property_signature_occurrence_map(old_entry or {})
    new_sigs = _property_signature_occurrence_map(entry)
    all_keys = list(new_props.keys()) + [k for k in old_props if k not in new_props]
    for key in all_keys:
        old_val = old_props.get(key, "")
        new_val = new_props.get(key, "")
        if old_val and new_val:
            old_sig = old_sigs.get(key)
            new_sig = new_sigs.get(key)
            if old_sig is not None and new_sig is not None and old_sig[1][0] == "struct" and new_sig[1][0] == "struct":
                status = "changed" if old_sig != new_sig else "same"
            else:
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

    def add_stat(stat_key: str, label: str, old_v: str, new_v: str) -> None:
        if not old_v and not new_v:
            return
        status = "same" if old_v == new_v else "added" if not old_v else "removed" if not new_v else "changed"
        stat_rows.append({"key": stat_key, "label": label, "old": old_v, "new": new_v, "status": status})

    add_stat("defense", "Def", range_text(old_item, "defense_min", "defense_max"), range_text(item, "defense_min", "defense_max"))
    has_damage = False
    for stat_key, label, min_key, max_key in [
        ("one_hand_damage", "One-Hand Damage", "damage_min", "damage_max"),
        ("two_hand_damage", "Two-Hand Damage", "two_hand_damage_min", "two_hand_damage_max"),
        ("throw_damage", "Throwing Damage", "throw_damage_min", "throw_damage_max"),
    ]:
        old_damage = range_text(old_item, min_key, max_key)
        new_damage = range_text(item, min_key, max_key)
        if min_key == "damage_min":
            if old_item and old_item.get("two_handed_only"):
                old_damage = ""
            if item.get("two_handed_only"):
                new_damage = ""
        add_stat(stat_key, label, old_damage, new_damage)
        has_damage = has_damage or bool(old_damage or new_damage)

    for stat_key, label, key in [
        ("level", "Base Lvl", "level"),
        ("level_req", "Req Lvl", "level_req"),
        ("str_req", "Str", "str_req"),
        ("dex_req", "Dex", "dex_req"),
        ("max_sockets", "Max Sockets", "sockets"),
    ]:
        add_stat(stat_key, label, str(old_item.get(key, "")) if old_item else "", str(item.get(key, "")))

    old_block = int(old_item.get("block", 0)) if old_item else 0
    new_block = int(item.get("block", 0))
    if old_block or new_block:
        add_stat("block", "Block", str(old_block) if old_item else "", str(new_block))

    if has_damage and item.get("defense_min") is None:
        old_speed = str(old_item.get("speed", "")) if old_item else ""
        add_stat("speed", "WSM", old_speed, str(item.get("speed", "")))

    property_rows: List[Dict[str, Any]] = []

    def add_prop_group(prop_key: str, label: str, old_list: List[str], new_list: List[str]) -> None:
        for i in range(max(len(old_list), len(new_list))):
            o = old_list[i] if i < len(old_list) else ""
            n = new_list[i] if i < len(new_list) else ""
            status = "same" if o == n else "added" if n and not o else "removed" if o and not n else "changed"
            property_rows.append({"key": prop_key, "label": label if i == 0 else "", "old": o, "new": n, "status": status})

    add_prop_group("inherent", "Inherent", old_item.get("inherent_stats", []) if old_item else [], item.get("inherent_stats", []))
    add_prop_group("auto_prefix", "Auto Prefix", old_item.get("auto_prefix_summary", []) if old_item else [], item.get("auto_prefix_summary", []))
    add_prop_group("superior_bonuses", "Superior Bonuses", old_item.get("quality_bonus_summary", []) if old_item else [], item.get("quality_bonus_summary", []))

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
        stat_rows.append({"key": key, "label": label, "old": old_val, "new": new_val, "status": status})

    has_canonical_slots = "socket_effects_by_slot" in item or (old_item is not None and "socket_effects_by_slot" in old_item)
    socket_rows = []
    if has_canonical_slots:
        old_slots = (old_item or {}).get("socket_effects_by_slot", {})
        new_slots = item.get("socket_effects_by_slot", {})
        slot_labels = item.get("socket_slot_labels") or (old_item or {}).get("socket_slot_labels") or {}
        default_labels = {"weapon": "Weapons", "helm": "Armor/Helms", "shield": "Shields"}
        for slot_key in ("weapon", "helm", "shield"):
            old_eff = "; ".join(old_slots.get(slot_key, []))
            new_eff = "; ".join(new_slots.get(slot_key, []))
            status = "added" if new_eff and not old_eff else "same" if old_eff == new_eff else "changed"
            socket_rows.append({
                "key": slot_key,
                "label": slot_labels.get(slot_key, default_labels[slot_key]),
                "old": old_eff,
                "new": new_eff,
                "status": status,
            })
    else:
        old_effects = old_item.get("socket_effects", {}) if old_item else {}
        new_effects = item.get("socket_effects", {})
        for slot_key, slot in [("weapon", "Weapon"), ("helm", "Armor/Helm"), ("shield", "Shield")]:
            old_eff = "; ".join(old_effects.get(slot, []))
            new_eff = "; ".join(new_effects.get(slot, []))
            status = "added" if new_eff and not old_eff else "same" if old_eff == new_eff else "changed"
            socket_rows.append({"key": slot_key, "label": slot, "old": old_eff, "new": new_eff, "status": status})

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
