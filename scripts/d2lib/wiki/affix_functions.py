from collections import Counter, defaultdict
import re

from d2lib.services.references import ReferenceAnalyzerService


AFFIX_FUNCTIONS_SLUG = "affixes-by-function"
NUMBER_PATTERN = re.compile(r"(?<![\w.])[+-]?\d+(?:\.\d+)?")
ROLL_PATTERN = re.compile(NUMBER_PATTERN.pattern + r"(?:-[+-]?\d+(?:\.\d+)?)?")


def _property_label(text: str, protected_names=()) -> str:
    # Keep the game's wording while removing the rolled values.
    if text.startswith("Unknown property: "):
        return re.sub(r"\s+\([^()]*\)$", "", text)
    replacements = {}
    for index, name in enumerate(protected_names):
        marker = f"__parameter{'x' * (index + 1)}__"
        if name in text:
            text = text.replace(name, marker)
            replacements[marker] = name
    text = re.sub(r"^\([^)]* per clvl\)\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(:\s*)[0-9.\-]+ seconds? \([0-9.\-]+ frames\)", "", text, flags=re.IGNORECASE)
    label = re.sub(r"\bOver [0-9.\-]+ Seconds\b", "", text, flags=re.IGNORECASE)
    label = ROLL_PATTERN.sub("", label)
    label = re.sub(r"\(\s*\)", "", label)
    label = label.replace("(/ Charges)", "(Charges)")
    label = " ".join(label.split()).strip(" +-:").lstrip("% ")
    label = re.sub(r"^(?:to|Adds)\s+", "", label, flags=re.IGNORECASE)
    for marker, name in replacements.items():
        label = label.replace(marker, name)
    return label[0].upper() + label[1:] if label else ""


def _function_title(properties: tuple[str, ...], protected_names=()) -> str:
    labels = dict.fromkeys(_property_label(part, protected_names) for text in properties for part in text.split(" · "))
    # Combine minimum/maximum elemental damage only when both components exist.
    for label in list(labels):
        if label.startswith("Minimum ") and label.endswith(" Damage") and "Maximum " + label[8:] in labels:
            labels = dict.fromkeys(
                part[8:] if part in (label, "Maximum " + label[8:]) else part
                for part in labels
            )
    for label in list(labels):
        if label.endswith(" Duration") and label.removesuffix(" Duration") + " Damage" in labels:
            del labels[label]
    return " + ".join(label for label in labels if label)


def _property_sort_key(text: str):
    effect = " ".join(re.findall(r"[^\W\d_]+", text.casefold()))
    effect = re.sub(r"^(?:to|adds)\s+", "", effect)
    values = tuple(float(value) for value in NUMBER_PATTERN.findall(text))
    return effect, values, text.casefold()


def _property_identity(tier, resolver):
    stats = set()
    parameters = set()
    codes = {resolver.aliases.get(prop["code"].lower(), prop["code"].lower()) for prop in tier.property_details}
    for prop in tier.property_details:
        code = resolver.aliases.get(prop["code"].lower(), prop["code"].lower())
        if code == "pois-len" and "dmg-pois" in codes:
            continue
        if code == "cold-len" and ("dmg-cold" in codes or {"cold-min", "cold-max"} <= codes):
            continue
        definition = resolver.properties.get(code, {})
        property_stats = {definition.get(f"stat{i}", "") for i in range(1, 8)} - {""}
        stats.update(property_stats or {code})
        tooltip = definition.get("*Tooltip", "")
        if "[" in tooltip or "%s" in tooltip:
            parameters.add((code, prop["param"]))
    if {"coldmindam", "coldmaxdam"} <= stats:
        stats.discard("coldlength")
    if {"poisonmindam", "poisonmaxdam"} <= stats:
        stats.discard("poisonlength")
    return tuple(sorted(stats)), tuple(sorted(parameters))


def affix_function_groups(service: ReferenceAnalyzerService):
    groups = defaultdict(list)
    for table, kind in (("magicprefix", "Prefix"), ("magicsuffix", "Suffix")):
        for name, tiers in service.affix_groups(table).values():
            for tier in tiers:
                if not tier.spawnable:
                    continue
                roll_ranges = tuple(sorted(tier.properties, key=_property_sort_key))
                protected_names = []
                for prop in tier.property_details:
                    definition = service.resolver.properties.get(prop["code"].lower(), {})
                    tooltip = definition.get("*Tooltip", "")
                    if prop["param"] and ("[Skill]" in tooltip or "%s" in tooltip):
                        protected_names.append(service.resolver.resolve_skill_name(prop["param"]))
                    if prop["code"].lower() == "skilltab":
                        protected_names.append(f"Tab {prop['param']}")
                title = _function_title(roll_ranges, protected_names)
                identity = _property_identity(tier, service.resolver)
                excludes = next((setting for setting in tier.settings if setting.startswith("Excludes · ")), "")
                groups[title, identity].append({
                    "level": tier.identity["level"],
                    "roll_ranges": roll_ranges,
                    "kind": kind,
                    "name": name,
                    "item_types": tier.item_types,
                    "excludes": excludes,
                    "can_roll_on_rares": tier.can_roll_on_rares,
                })

    def sort_key(row):
        level = row["level"]
        return (tuple(_property_sort_key(prop)[1] for prop in row["roll_ranges"]),
                not level.isdecimal(), int(level) if level.isdecimal() else 0,
                row["name"].casefold(), row["kind"], tuple(row["item_types"]))

    title_counts = Counter(title for title, _ in groups)
    contexts = {
        identity: " / ".join(dict.fromkeys(
            service.resolver.skill_tab_classes[param]
            for code, param in identity[1]
            if code == "skilltab" and param in service.resolver.skill_tab_classes
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
        result.append({"title": title, "rows": sorted(rows, key=sort_key)})
    return sorted(result, key=lambda group: group["title"].casefold())
