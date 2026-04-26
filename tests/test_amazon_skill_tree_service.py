import json
import os
import re
import sys
import unittest
from typing import Dict, List, Optional


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2_repository import D2Repository
from d2lib.repository import strip_json_comments
from d2_services import SkillAnalyzerService


def normalize_skill_key(name: str) -> str:
    return re.sub(r"[\s']", "", name.strip().lower())


def normalize_val(val):
    if val is None:
        return None
    text = str(val).strip()
    if not text or text == "NOT_SHOWN":
        return None
    text = text.replace("%", "").strip()

    if "-" in text:
        if text.startswith("-"):
            nums = re.findall(r"-?\d+\.?\d*", text)
            if len(nums) == 1:
                return float(nums[0])
            if len(nums) >= 2:
                return [float(nums[0]), float(nums[1])]
        else:
            nums = re.findall(r"-?\d+\.?\d*", text)
            if len(nums) >= 2:
                return [float(nums[0]), float(nums[1])]

    nums = re.findall(r"-?\d+\.?\d*", text)
    if len(nums) >= 2:
        return [float(nums[0]), float(nums[1])]
    return float(nums[0]) if nums else None


def clean_label(text: str) -> str:
    value = text.lower()
    value = value.replace("%", "")
    value = value.replace("+", "")
    value = value.replace("-", " ")
    value = value.replace("x", "")
    value = value.replace("to", " to ")
    value = value.replace("per second", "")
    value = value.replace("seconds", "")
    value = value.replace("second", "")
    value = value.replace("freezes for", "freeze duration")
    value = value.replace("freezing arrows", "freezing arrows")
    value = value.replace("releases bolts", "bolts")
    value = value.replace("attacks up to targets", "attacks up to targets")
    value = value.replace("mana cost", "mana")
    value = value.replace("fire explosion damage", "explosion damage")
    value = value.replace("average fire damage", "fire damage")
    value = value.replace("converts physical damage to magic damage", "converts physical damage to magic damage")
    value = value.replace("converts physical damage to elemental damage", "converts physical damage to elemental damage")
    value = value.replace("chance", "chance")
    value = re.sub(r"\s+", " ", value).strip(" :")
    return value


class TestAmazonSkillTreeService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.repo = FrozenSnapshotRepository(os.path.join(root, "tests", "fixtures", "amazon_skill_snapshot", "mod"))
        cls.service = SkillAnalyzerService(cls.repo)
        with open(os.path.join(root, "tests", "amazon_test_cases.json"), "r", encoding="utf-8") as f:
            cls.expectations = json.load(f)

    def render_skill_effects(self, skill_name: str, lvl: int, blvl: int, synergies: Dict[str, int]) -> List[Dict[str, str]]:
        scenario_levels = {normalize_skill_key(skill_name): blvl}
        scenario_levels.update({normalize_skill_key(name): int(level) for name, level in synergies.items()})
        return self.service.get_skill_display_effects(skill_name, lvl, blvl, scenario_levels)

    def match_effect_value(self, effects: List[Dict[str, str]], expected_key: str) -> Optional[str]:
        expected_clean = clean_label(expected_key)
        best_match = None
        best_score = -1

        for effect in effects:
            label_clean = clean_label(effect["label"])
            score = -1
            if label_clean == expected_clean:
                score = 100
            elif expected_clean in label_clean or label_clean in expected_clean:
                score = min(len(expected_clean), len(label_clean))

            if score > best_score:
                best_score = score
                best_match = effect["value"]

        return best_match if best_score >= 0 else None

    def test_amazon_skill_expectations(self):
        for group_name, skills in self.expectations["groups"].items():
            for skill_name, skill_data in skills.items():
                for scenario in skill_data["scenarios"]:
                    lvl = scenario["lvl"]
                    blvl = scenario["blvl"]
                    effects = self.render_skill_effects(skill_name, lvl, blvl, skill_data.get("synergies", {}))

                    with self.subTest(group=group_name, skill=skill_name, lvl=lvl, blvl=blvl):
                        for ui_key, expected_raw in scenario["ui"].items():
                            if expected_raw in ["", "NOT_SHOWN"]:
                                continue

                            actual_raw = self.match_effect_value(effects, ui_key)
                            self.assertIsNotNone(actual_raw, f"Could not match UI field '{ui_key}' for {skill_name}. Effects: {effects}")

                            expected = normalize_val(expected_raw)
                            actual = normalize_val(actual_raw)
                            self.assertIsNotNone(actual, f"No numeric value found for '{ui_key}' in {skill_name}: {actual_raw}")

                            if isinstance(expected, list) and isinstance(actual, list):
                                delta = 5.0 if max(expected) > 1000 else 1.1
                                self.assertAlmostEqual(expected[0], actual[0], delta=delta, msg=f"{skill_name} L{lvl}/{blvl} {ui_key} min mismatch: expected {expected_raw}, actual {actual_raw}")
                                self.assertAlmostEqual(expected[1], actual[1], delta=delta, msg=f"{skill_name} L{lvl}/{blvl} {ui_key} max mismatch: expected {expected_raw}, actual {actual_raw}")
                            elif not isinstance(expected, list) and not isinstance(actual, list):
                                delta = 5.0 if expected > 1000 else 1.1
                                self.assertAlmostEqual(expected, actual, delta=delta, msg=f"{skill_name} L{lvl}/{blvl} {ui_key} mismatch: expected {expected_raw}, actual {actual_raw}")
                            else:
                                self.fail(f"Mismatched value shape for {skill_name} {ui_key}: expected {expected_raw}, actual {actual_raw}")


class FrozenSnapshotRepository(D2Repository):
    def __init__(self, snapshot_mod_path: str):
        self.mpq_path = snapshot_mod_path
        self.supplemental_path = snapshot_mod_path
        self.strings: Dict[str, str] = {}
        self.excel_cache: Dict[str, List[Dict[str, str]]] = {}
        self._load_strings()

    def _load_strings(self) -> None:
        string_dir = os.path.join(self.mpq_path, "data", "local", "lng", "strings")
        if not os.path.exists(string_dir):
            return

        for filename in os.listdir(string_dir):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(string_dir, filename)
            with open(filepath, "r", encoding="utf-8-sig") as f:
                data = json.loads(strip_json_comments(f.read()))
            for entry in data:
                key = entry.get("Key", "").lower()
                value = entry.get("enUS", "")
                if key:
                    self.strings[key] = value

    def get_excel_table(self, table_name: str) -> List[Dict[str, str]]:
        if table_name in self.excel_cache:
            return self.excel_cache[table_name]

        filepath = os.path.join(self.mpq_path, "data", "global", "excel", f"{table_name}.txt")
        data = self.load_tsv(filepath)
        self.excel_cache[table_name] = data
        return data


if __name__ == "__main__":
    unittest.main()
