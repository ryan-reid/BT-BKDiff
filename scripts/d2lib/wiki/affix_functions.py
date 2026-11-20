from collections import defaultdict
import re

from d2lib.services.references import ReferenceAnalyzerService
from d2lib.services.resolver import PropertyResolverService


AFFIX_FUNCTIONS_SLUG = "affixes-by-function"

FUNCTION_LABELS = {
    "att%": "Percent Attack Rating",
    "att-skill": "Chance to Cast on Attack",
    "charged": "Skill Charges",
    "dmg": "Flat Damage",
    "dmg-norm": "Added Physical Damage",
    "dmg-cold": "Cold Damage",
    "dmg-fire": "Fire Damage",
    "dmg-ltng": "Lightning Damage",
    "dmg-pois": "Poison Damage",
    "gethit-skill": "Chance to Cast When Struck",
    "hit-skill": "Chance to Cast on Striking",
    "kill-skill": "Chance to Cast on Kill",
    "oskill": "Non-Class Skills",
    "skilltab": "Skill Tab Bonuses",
    "res-fire": "Fire Resistance",
    "res-cold": "Cold Resistance",
    "res-ltng": "Lightning Resistance",
    "res-pois": "Poison Resistance",
    "mag%": "Magic Find",
    "pierce-cold": "Enemy Cold Resistance Reduction",
    "pierce-dmg": "Enemy Physical Resistance Reduction",
    "pierce-fire": "Enemy Fire Resistance Reduction",
    "pierce-ltng": "Enemy Lightning Resistance Reduction",
    "pierce-mag": "Enemy Magic Resistance Reduction",
    "pierce-pois": "Enemy Poison Resistance Reduction",
    "red-mag": "Magic Damage Reduction",
    "red-dmg": "Flat Physical Damage Reduction",
    "red-dmg%": "Percent Physical Damage Reduction",
    "rep-dur": "Durability Repair",
    "rep-quant": "Quantity Replenishment",
    "res-pois-len": "Poison Length Reduction",
    "sock": "Sockets",
    "thorns": "Damage Returned to Attacker",
}

ELEMENTAL_COMPONENTS = {
    "dmg-cold": {"cold-min", "cold-max", "cold-len"},
    "dmg-fire": {"fire-min", "fire-max"},
    "dmg-ltng": {"ltng-min", "ltng-max"},
}


def _function_label(code: str, resolver: PropertyResolverService) -> str:
    if code in FUNCTION_LABELS:
        return FUNCTION_LABELS[code]
    tooltip = resolver.properties.get(code, {}).get("*Tooltip", "")
    # Property tooltips use # for roll values and brackets for parameters.
    label = re.sub(r"[+\-]?#%?", "", tooltip)
    label = " ".join(label.split()).removeprefix("to ")
    return label[0].upper() + label[1:] if label and label != "0" else code


def _function_title(codes: list[str], resolver: PropertyResolverService) -> str:
    codes = {resolver.aliases.get(code.lower(), code.lower()) for code in codes}
    for damage, components in ELEMENTAL_COMPONENTS.items():
        damage_endpoints = components - {"cold-len"}
        if damage in codes or damage_endpoints <= codes:
            codes = (codes - components) | {damage}
    if "dmg-pois" in codes:
        codes.discard("pois-len")
    return " + ".join(sorted({_function_label(code, resolver) for code in codes}, key=str.casefold))


def affix_function_groups(service: ReferenceAnalyzerService):
    groups = defaultdict(list)
    for table, kind in (("magicprefix", "Prefix"), ("magicsuffix", "Suffix")):
        for name, tiers in service.affix_groups(table).values():
            for tier in tiers:
                if not tier.spawnable:
                    continue
                title = _function_title(tier.identity["properties"], service.resolver)
                excludes = next((setting for setting in tier.settings if setting.startswith("Excludes · ")), "")
                groups[title].append({
                    "level": tier.identity["level"],
                    "roll_ranges": tier.properties,
                    "kind": kind,
                    "name": name,
                    "item_types": tier.item_types,
                    "excludes": excludes,
                    "can_roll_on_rares": tier.can_roll_on_rares,
                })

    def sort_key(row):
        level = row["level"]
        return (not level.isdecimal(), int(level) if level.isdecimal() else 0,
                row["name"].casefold(), row["kind"], row["roll_ranges"], tuple(row["item_types"]))

    return [
        {"title": title, "rows": sorted(rows, key=sort_key)}
        for title, rows in sorted(groups.items(), key=lambda group: group[0].casefold())
    ]
