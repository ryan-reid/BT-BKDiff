from __future__ import annotations
from typing import Any, Dict, List

from d2lib.utils import slugify, item_category_to_group


def item_filter_type(entry: Dict[str, Any], family: str) -> str:
    if family == "runeword":
        base_items = entry.get("base_items", [])
        return str(base_items[0]) if base_items else "Runeword"
    return str(entry.get("item_type", "")).strip() or "Item"


def item_filter_group(entry: Dict[str, Any], family: str) -> str:
    return item_category_to_group(item_filter_type(entry, family))


def should_include_item(entry: Dict[str, Any], family: str) -> bool:
    properties = entry.get("properties", [])
    if family == "runeword":
        base_items = [str(b).strip() for b in entry.get("base_items", []) if str(b).strip()]
        runes = [str(r).strip() for r in entry.get("runes", []) if str(r).strip()]
        if not properties and not runes:
            if not base_items or all(b.lower() == "expansion" for b in base_items):
                return False
        return True
    title = str(entry.get("display_name") or entry.get("id") or entry.get("name") or "").strip()
    base_item = str(entry.get("base_item", "")).strip()
    item_type = str(entry.get("item_type", "")).strip()
    if not properties:
        if title.lower() == "blank charm":
            return False
        if base_item.lower() == "expansion" and item_type.lower() == "expansion":
            return False
    return True


def item_sort_key(entry: Dict[str, Any]) -> str:
    return (entry.get("display_name") or entry.get("name") or entry.get("id") or "").lower()


def item_identity(entry: Dict[str, Any], family: str) -> str:
    item_id = entry.get("id")
    if item_id:
        return f"{family}|{slugify(str(item_id))}"
    title = entry.get("display_name") or entry.get("name") or ""
    base_item = entry.get("base_item") or ""
    item_type = entry.get("item_type") or ""
    lvl_req = entry.get("lvl_req") or ""
    return f"{family}|{slugify(str(title))}|{slugify(str(base_item))}|{slugify(str(item_type))}|{slugify(str(lvl_req))}"


def item_title(entry: Dict[str, Any], family: str) -> str:
    if family == "runeword":
        return entry.get("name", "Unknown Runeword")
    return entry.get("display_name") or entry.get("id") or entry.get("name") or "Unknown Item"


def item_summary(entry: Dict[str, Any], family: str) -> str:
    if family == "runeword":
        base_items = ", ".join(entry.get("base_items", [])) or "Unknown base"
        runes = " + ".join(entry.get("runes", [])) or "unknown runes"
        socket_count = len(entry.get("runes", []))
        socket_text = f"{socket_count}-socket " if socket_count else ""
        return f"{runes} in {socket_text}{base_items}."
    item_type_val = entry.get("item_type", "Item")
    base_item = entry.get("base_item", "Unknown base")
    lvl_req = entry.get("lvl_req", "0")
    return f"{item_type_val} based on {base_item}. Level requirement {lvl_req}."


def item_search_text(entry: Dict[str, Any], family: str) -> str:
    if family == "runeword":
        runes = " ".join(entry.get("runes", []))
        bases = " ".join(entry.get("base_items", []))
        props = " ".join(prop.get("resolved_text", "") for prop in entry.get("properties", []))
        return f"{entry.get('name', '')} {runes} {bases} {props}"
    props = " ".join(prop.get("resolved_text", "") for prop in entry.get("properties", []))
    drop_info = entry.get("drop_info") or {}
    return (
        f"{entry.get('display_name', '')} "
        f"{entry.get('base_item', '')} "
        f"{entry.get('item_type', '')} "
        f"{entry.get('raw_row', {}).get('set', '')} "
        f"{drop_info.get('drop_level', '')} {drop_info.get('label', '')} "
        f"{props}"
    )


def item_slug(entry: Dict[str, Any], family: str, title: str, used_paths: Dict[str, int]) -> str:
    base_slug = slugify(title)
    if family == "runeword":
        disambiguator = entry.get("base_items", [""])[0]
    else:
        disambiguator = entry.get("base_item") or entry.get("id") or ""

    candidate = base_slug
    if candidate in used_paths:
        dis_slug = slugify(disambiguator)
        if dis_slug:
            candidate = f"{base_slug}-{dis_slug}"
    root = candidate
    suffix = 2
    while candidate in used_paths:
        candidate = f"{root}-{suffix}"
        suffix += 1
    used_paths[candidate] = 1
    return candidate


def set_item_anchor(entry: Dict[str, Any]) -> str:
    set_name = str(entry.get("raw_row", {}).get("set") or "set").strip()
    item_name = str(entry.get("display_name") or entry.get("id") or entry.get("name") or "item").strip()
    return f"{slugify(set_name)}-{slugify(item_name)}"
