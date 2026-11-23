from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Tuple

from d2lib.repository import resolve_localized_string
from d2lib.services.references import ReferenceAnalyzerService


AFFIX_FUNCTIONS_SLUG = "affixes-by-function"

_ELEMENTAL_MERGE_PAIRS: Tuple[Tuple[frozenset[str], str, str], ...] = (
    (frozenset({"firemindam", "firemaxdam"}), "strModFireDamage", "Fire Damage"),
    (frozenset({"lightmindam", "lightmaxdam"}), "strModLightningDamage", "Lightning Damage"),
    (frozenset({"coldmindam", "coldmaxdam"}), "strModColdDamage", "Cold Damage"),
    (frozenset({"magicmindam", "magicmaxdam"}), "strModMagicDamage", "Magic Damage"),
    (frozenset({"poisonmindam", "poisonmaxdam"}), "strskill8", "Poison Damage"),
    (frozenset({"mindamage", "maxdamage"}), "strModMinDamage", "Damage"),
)


def _prop_stats(prop: Dict[str, Any], resolver) -> frozenset[str]:
    stats = prop.get("stats") or ()
    if stats:
        return frozenset(str(st) for st in stats if st)
    code = str(prop.get("code", "")).lower()
    definition = resolver.properties.get(code, {})
    return frozenset({definition.get(f"stat{i}", "") for i in range(1, 8)} - {""}) or frozenset({code})


def _prop_label(prop: Dict[str, Any], resolver) -> str:
    label = str(prop.get("label") or "").strip()
    if label:
        return label
    text = str(prop.get("text") or "").strip()
    return resolver.label_from_template(text)


def _prop_sort_key(prop: Dict[str, Any], resolver) -> Tuple[str, Tuple[float, ...], str]:
    label = _prop_label(prop, resolver).casefold()
    numbers = tuple(float(v) for v in (prop.get("numeric_values") or ()))
    text = str(prop.get("text") or "").casefold()
    return label, numbers, text


def _function_title(sorted_details: Tuple[Dict[str, Any], ...], resolver) -> str:
    all_stats = frozenset(st for prop in sorted_details for st in _prop_stats(prop, resolver))
    suppress_stats: set[str] = set()
    if {"coldmindam", "coldmaxdam"} <= all_stats:
        suppress_stats.add("coldlength")
    if {"poisonmindam", "poisonmaxdam"} <= all_stats:
        suppress_stats.add("poisonlength")

    active_pairs = []
    for pair_stats, str_key, fallback_title in _ELEMENTAL_MERGE_PAIRS:
        if pair_stats <= all_stats:
            loc_tpl = resolve_localized_string(resolver.repo, str_key)
            merged_label = resolver.label_from_template(loc_tpl) if loc_tpl else fallback_title
            active_pairs.append((pair_stats, merged_label or fallback_title))

    labels: List[str] = []
    emitted_pairs: set[frozenset[str]] = set()
    for prop in sorted_details:
        p_stats = _prop_stats(prop, resolver)
        if suppress_stats and p_stats <= suppress_stats:
            continue
        matched_pair = next(((pair, mlabel) for pair, mlabel in active_pairs if p_stats & pair), None)
        if matched_pair is not None:
            pair, merged_label = matched_pair
            if pair not in emitted_pairs:
                emitted_pairs.add(pair)
                labels.append(merged_label)
            continue
        if prop.get("is_unknown"):
            labels.append(_prop_label(prop, resolver))
            continue
        label = _prop_label(prop, resolver)
        if label:
            labels.append(label)
    return " + ".join(dict.fromkeys(labels))


def _property_identity(tier, resolver) -> Tuple[Tuple[str, ...], Tuple[Tuple[str, str], ...]]:
    stats: set[str] = set()
    parameters: set[Tuple[str, str]] = set()
    codes = {
        str(prop.get("canonical_code") or str(prop["code"]).lower())
        for prop in tier.property_details
    }
    for prop in tier.property_details:
        code = str(prop.get("canonical_code") or str(prop["code"]).lower())
        if code == "pois-len" and "dmg-pois" in codes:
            continue
        if code == "cold-len" and ("dmg-cold" in codes or {"cold-min", "cold-max"} <= codes):
            continue
        stats.update(_prop_stats(prop, resolver))
        param_key = str(prop.get("parameter_key") or "").strip()
        if param_key:
            parameters.add((code, param_key))
    if {"coldmindam", "coldmaxdam"} <= stats:
        stats.discard("coldlength")
    if {"poisonmindam", "poisonmaxdam"} <= stats:
        stats.discard("poisonlength")
    return tuple(sorted(stats)), tuple(sorted(parameters))


def affix_function_groups(service: ReferenceAnalyzerService):
    groups = defaultdict(list)
    resolver = service.resolver
    for table, kind in (("magicprefix", "Prefix"), ("magicsuffix", "Suffix")):
        for name, tiers in service.affix_groups(table).values():
            for tier in tiers:
                if not tier.spawnable:
                    continue
                sorted_details = tuple(sorted(tier.property_details, key=lambda p: _prop_sort_key(p, resolver)))
                roll_ranges = tuple(prop["text"] for prop in sorted_details)
                roll_numbers = tuple(tuple(float(v) for v in (prop.get("numeric_values") or ())) for prop in sorted_details)
                title = _function_title(sorted_details, resolver)
                identity = _property_identity(tier, resolver)
                excludes_map = getattr(tier, "excludes", None) or {}
                excludes = f"Excludes · {', '.join(excludes_map.values())}" if excludes_map else ""
                groups[title, identity].append({
                    "level": tier.identity["level"],
                    "roll_ranges": roll_ranges,
                    "_roll_numbers": roll_numbers,
                    "kind": kind,
                    "name": name,
                    "item_types": tier.item_types,
                    "excludes": excludes,
                    "can_roll_on_rares": tier.can_roll_on_rares,
                })

    def sort_key(row):
        level = row["level"]
        return (
            row["_roll_numbers"],
            not level.isdecimal(),
            int(level) if level.isdecimal() else 0,
            row["name"].casefold(),
            row["kind"],
            tuple(row["item_types"]),
        )

    title_counts = Counter(title for title, _ in groups)
    contexts = {
        identity: " / ".join(dict.fromkeys(
            resolver.skill_tab_classes[param]
            for code, param in identity[1]
            if code == "skilltab" and param in resolver.skill_tab_classes
        ))
        for _, identity in groups
    }
    unqualified_counts = Counter(title for title, identity in groups if not contexts[identity])
    result = []
    for (title, identity), rows in groups.items():
        if title_counts[title] > 1:
            if contexts[identity]:
                title = f"{title} {contexts[identity]}"
            elif unqualified_counts[title] > 1:
                stats, parameters = identity
                detail = ", ".join([*stats, *(f"{code} {param}" for code, param in parameters)])
                title = f"{title} ({detail})"
        sorted_rows = [
            {k: v for k, v in row.items() if k != "_roll_numbers"}
            for row in sorted(rows, key=sort_key)
        ]
        result.append({"title": title, "rows": sorted_rows})
    return sorted(result, key=lambda group: group["title"].casefold())
