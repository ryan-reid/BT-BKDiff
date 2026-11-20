from collections import defaultdict
import re

from d2lib.services.references import ReferenceAnalyzerService


AFFIX_FUNCTIONS_SLUG = "affixes-by-function"

def _property_label(text: str) -> str:
    # Keep the game's wording while removing the rolled values.
    text = re.sub(r"^\([^)]* per clvl\)\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(:\s*)[0-9.\-]+ seconds? \([0-9.\-]+ frames\)", "", text, flags=re.IGNORECASE)
    label = re.sub(r"\bOver [0-9.\-]+ Seconds\b", "", text, flags=re.IGNORECASE)
    label = re.sub(r"[+\-]?\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?", "", label)
    label = re.sub(r"\(\s*\)", "", label)
    label = label.replace("(/ Charges)", "(Charges)")
    label = " ".join(label.split()).strip(" +-:").lstrip("% ")
    label = re.sub(r"^(?:to|Adds)\s+", "", label, flags=re.IGNORECASE)
    label = re.sub(r"\b(?:Minimum|Maximum) (?=\w+ Damage)", "", label)
    return label[0].upper() + label[1:] if label else ""


def _function_title(properties: tuple[str, ...]) -> str:
    labels = dict.fromkeys(_property_label(text) for text in properties)
    for label in list(labels):
        if label.endswith(" Duration") and label.removesuffix(" Duration") + " Damage" in labels:
            del labels[label]
    return " + ".join(label for label in labels if label)


def _property_sort_key(text: str):
    effect = " ".join(re.findall(r"[^\W\d_]+", text.casefold()))
    values = tuple(float(value) for value in re.findall(r"\d+(?:\.\d+)?", text))
    return effect, values, text.casefold()


def affix_function_groups(service: ReferenceAnalyzerService):
    groups = defaultdict(list)
    for table, kind in (("magicprefix", "Prefix"), ("magicsuffix", "Suffix")):
        for name, tiers in service.affix_groups(table).values():
            for tier in tiers:
                if not tier.spawnable:
                    continue
                roll_ranges = tuple(sorted(tier.properties, key=_property_sort_key))
                title = _function_title(roll_ranges)
                excludes = next((setting for setting in tier.settings if setting.startswith("Excludes · ")), "")
                groups[title].append({
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

    return [
        {"title": title, "rows": sorted(rows, key=sort_key)}
        for title, rows in sorted(groups.items(), key=lambda group: group[0].casefold())
    ]
