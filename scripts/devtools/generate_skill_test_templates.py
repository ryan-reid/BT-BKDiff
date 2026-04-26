import json
import os
import re
import sys
from collections import OrderedDict
from typing import Dict, List, Tuple


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, SCRIPTS_ROOT)

from d2_repository import D2Repository
from d2_services import SkillAnalyzerService


DEFAULT_SCENARIOS: List[Tuple[int, int]] = [(1, 1), (20, 20), (30, 20)]
CLASS_OUTPUTS = {
    "dru": "druid_test_cases.template.json",
    "war": "warlock_test_cases.template.json",
}
CLASS_GROUPS = {
    "dru": OrderedDict(
        [
            ("Summoning", [
                "Raven",
                "Poison Creeper",
                "Oak Sage",
                "Summon Spirit Wolf",
                "Carrion Vine",
                "Heart of Wolverine",
                "Summon Dire Wolf",
                "Solar Creeper",
                "Spirit of Barbs",
                "Summon Grizzly",
            ]),
            ("Shape Shifting", [
                "Werewolf",
                "Lycanthropy",
                "Werebear",
                "Feral Rage",
                "Maul",
                "Rabies",
                "Fire Claws",
                "Hunger",
                "Shock Wave",
                "Fury",
            ]),
            ("Elemental", [
                "Firestorm",
                "Molten Boulder",
                "Arctic Blast",
                "Fissure",
                "Cyclone Armor",
                "Twister",
                "Volcano",
                "Tornado",
                "Armageddon",
                "Hurricane",
            ]),
        ]
    ),
    "war": OrderedDict(
        [
            ("Demonic Summoning", [
                "Summon Goatman",
                "Demonic Mastery",
                "Death Mark",
                "Summon Tainted",
                "Summon Defiler",
                "Blood Oath",
                "Engorge",
                "Blood Boil",
                "Consume",
                "Bind Demon",
            ]),
            ("Hexcraft & Blades", [
                "Levitation Mastery",
                "Eldritch Blast",
                "Hex: Bane",
                "Hex: Siphon",
                "Psychic Ward",
                "Echoing Strike",
                "Hex: Purge",
                "Blade Warp",
                "Cleave",
                "Mirrored Blades",
            ]),
            ("Sigils & Cataclysm", [
                "Sigil: Lethargy",
                "Ring of Fire",
                "Miasma Bolt",
                "Sigil: Rancor",
                "Enhanced Entropy",
                "Flame Wave",
                "Miasma Chain",
                "Sigil: Death",
                "Apocalypse",
                "Abyss",
            ]),
        ]
    ),
}


def collect_effect_labels(service: SkillAnalyzerService, skill_key: str, scenarios: List[Tuple[int, int]]) -> List[str]:
    labels: "OrderedDict[str, None]" = OrderedDict()
    for lvl, blvl in scenarios:
        for effect in service.get_skill_display_effects(skill_key, lvl, blvl, {}):
            label = effect.get("label", "").strip()
            value = str(effect.get("value", "")).strip()
            normalized_label = re.sub(r"\s+", " ", label.lower()).strip()
            if (
                label
                and re.search(r"\d", value)
                and "receives bonuses" not in normalized_label
                and "per level" not in normalized_label
            ):
                labels.setdefault(label, None)
    return list(labels.keys())


def build_template(service: SkillAnalyzerService, class_abbr: str, scenarios: List[Tuple[int, int]]) -> Dict:
    tree = service.generate_skill_tree(class_abbr)
    skill_templates = OrderedDict()

    for skill in tree["skills"]:
        skill_key = skill.get("raw_row", {}).get("skill", skill["name"])
        skill_name = skill["name"]
        effect_labels = collect_effect_labels(service, skill_key, scenarios)
        skill_templates[skill_name] = {
            "synergies": OrderedDict((syn["name"], None) for syn in skill.get("synergies", [])),
            "scenarios": [
                {
                    "lvl": lvl,
                    "blvl": blvl,
                    "ui": OrderedDict((label, "") for label in effect_labels),
                }
                for lvl, blvl in scenarios
            ],
        }

    grouped_skills: "OrderedDict[str, OrderedDict]" = OrderedDict()
    for group_name, skill_names in CLASS_GROUPS[class_abbr].items():
        grouped_skills[group_name] = OrderedDict(
            (skill_name, skill_templates[skill_name])
            for skill_name in skill_names
            if skill_name in skill_templates
        )

    return {
        "class": tree["class_name"].lower(),
        "equipment_bonus": None,
        "groups": grouped_skills,
    }


def main() -> None:
    repo_root = os.path.dirname(SCRIPTS_ROOT)
    repo = D2Repository(os.path.join(repo_root, "mods", "BKDiablo", "bkdiablo.mpq"))
    service = SkillAnalyzerService(repo)
    tests_dir = os.path.join(repo_root, "tests")

    for class_abbr, filename in CLASS_OUTPUTS.items():
        payload = build_template(service, class_abbr, DEFAULT_SCENARIOS)
        output_path = os.path.join(tests_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
