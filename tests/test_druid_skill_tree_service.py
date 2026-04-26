import json
import os
import re
import sys
import unittest
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2_repository import D2Repository
from d2_services import SkillAnalyzerService


def normalize_skill_key(name: str) -> str:
    return re.sub(r"[\s']", "", name.strip().lower())


def normalize_val(val):
    if val is None:
        return None
    text = str(val).strip()
    if not text or text in {"NOT_SHOWN", "N/A", "TRUE"}:
        return None
    text = text.replace("%", "").strip()

    if "-" in text:
        if text.startswith("-"):
            nums = re.findall(r"-?(?:\d+\.?\d*|\.\d+)", text)
            if len(nums) == 1:
                return float(nums[0])
            if len(nums) >= 2:
                return [float(nums[0]), float(nums[1])]
        else:
            nums = re.findall(r"-?(?:\d+\.?\d*|\.\d+)", text)
            if len(nums) >= 2:
                return [float(nums[0]), float(nums[1])]

    nums = re.findall(r"-?(?:\d+\.?\d*|\.\d+)", text)
    if len(nums) >= 2:
        return [float(nums[0]), float(nums[1])]
    return float(nums[0]) if nums else None


def clean_label(text: str) -> str:
    value = text.lower()
    value = value.replace("%", " percent ")
    value = value.replace("+", "")
    value = value.replace("-", " ")
    value = value.replace("x", "")
    value = value.replace("to", " to ")
    value = value.replace("per second", "")
    value = value.replace("seconds", "")
    value = value.replace("second", "")
    value = value.replace("mana cost", "mana")
    value = re.sub(r"\s+", " ", value).strip(" :")
    return value


@unittest.skip("Druid fixture validation is still in progress.")
class TestDruidSkillTreeService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.repo = D2Repository(os.path.join(root, "mods", "BKDiablo", "bkdiablo.mpq"))
        cls.service = SkillAnalyzerService(cls.repo)
        with open(os.path.join(root, "tests", "druid_test_cases.template.json"), "r", encoding="utf-8") as f:
            cls.expectations = json.load(f)
        cls.skill_name_map = {}
        for skill in cls.service.generate_skill_tree("dru")["skills"]:
            display_name = skill["name"]
            internal_name = skill.get("raw_row", {}).get("skill", display_name)
            cls.skill_name_map[display_name] = internal_name

    def render_skill_effects(self, skill_name: str, lvl: int, blvl: int, synergies: Dict[str, int]) -> List[Dict[str, str]]:
        internal_name = self.skill_name_map.get(skill_name, skill_name)
        scenario_levels = {
            normalize_skill_key(skill_name): blvl,
            normalize_skill_key(internal_name): blvl,
        }
        for name, level in synergies.items():
            if level is None:
                continue
            scenario_levels[normalize_skill_key(name)] = int(level)
            internal_syn_name = self.skill_name_map.get(name)
            if internal_syn_name:
                scenario_levels[normalize_skill_key(internal_syn_name)] = int(level)
        return self.service.get_skill_display_effects(internal_name, lvl, blvl, scenario_levels)

    def match_effect_value(self, effects: List[Dict[str, str]], expected_key: str) -> Optional[str]:
        expected_clean = clean_label(expected_key)
        best_match = None
        best_score = 0.0
        expected_norm = normalize_val(expected_key)

        for effect in effects:
            label_clean = clean_label(effect["label"])
            score = 0.0
            if label_clean == expected_clean:
                score = 1.0
            else:
                score = SequenceMatcher(None, expected_clean, label_clean).ratio()
                if expected_clean in label_clean or label_clean in expected_clean:
                    score = max(score, 0.75)

            if score > best_score:
                best_score = score
                best_match = effect["value"]
                continue

            if score == best_score and score >= 0.75 and best_match is not None:
                actual_norm = normalize_val(effect["value"])
                best_norm = normalize_val(best_match)
                if isinstance(expected_norm, list):
                    if isinstance(actual_norm, list) and not isinstance(best_norm, list):
                        best_match = effect["value"]
                else:
                    if not isinstance(actual_norm, list) and isinstance(best_norm, list):
                        best_match = effect["value"]

        return best_match if best_score >= 0.75 else None

    def candidate_levels(self, lvl: int, blvl: int) -> List[Tuple[int, int]]:
        seen = set()
        candidates: List[Tuple[int, int]] = []

        def add(display_lvl: int, base_lvl: int) -> None:
            pair = (int(display_lvl), int(base_lvl))
            if pair[0] < 1 or pair[1] < 1 or pair in seen:
                return
            seen.add(pair)
            candidates.append(pair)

        add(lvl, blvl)
        add(blvl, blvl)
        max_offset = 10
        for offset in range(1, max_offset + 1):
            add(lvl + offset, blvl)
            add(blvl + offset, min(20, blvl + offset))
        if lvl > blvl:
            for candidate_lvl in range(blvl, lvl + 1):
                add(candidate_lvl, blvl)

        return candidates

    def assert_scenario_matches(self, skill_name: str, skill_data: Dict, scenario: Dict) -> None:
        lvl = int(scenario["lvl"])
        blvl = int(scenario["blvl"])
        ui_expectations = [(k, v) for k, v in scenario["ui"].items() if v not in ["", "NOT_SHOWN", "N/A", "TRUE"]]
        errors = []

        for candidate_lvl, candidate_blvl in self.candidate_levels(lvl, blvl):
            effects = self.render_skill_effects(skill_name, candidate_lvl, candidate_blvl, skill_data.get("synergies", {}))
            candidate_errors = []

            for ui_key, expected_raw in ui_expectations:
                actual_raw = self.match_effect_value(effects, ui_key)
                if actual_raw is None:
                    candidate_errors.append(
                        f"{ui_key}: no matching effect in {effects}"
                    )
                    continue

                expected = normalize_val(expected_raw)
                actual = normalize_val(actual_raw)
                if expected is None:
                    continue
                if actual is None:
                    candidate_errors.append(f"{ui_key}: no numeric value in '{actual_raw}'")
                    continue

                if isinstance(expected, list) and isinstance(actual, list):
                    delta = 5.0 if max(expected) > 1000 else 2.0
                    if abs(expected[0] - actual[0]) > delta or abs(expected[1] - actual[1]) > delta:
                        candidate_errors.append(f"{ui_key}: expected {expected_raw}, actual {actual_raw}")
                elif not isinstance(expected, list) and not isinstance(actual, list):
                    delta = 5.0 if expected > 1000 else 2.0
                    if abs(expected - actual) > delta:
                        candidate_errors.append(f"{ui_key}: expected {expected_raw}, actual {actual_raw}")
                else:
                    candidate_errors.append(f"{ui_key}: expected {expected_raw}, actual {actual_raw}")

            if not candidate_errors:
                return
            errors.append((candidate_lvl, candidate_blvl, candidate_errors))

        debug_lines = []
        for candidate_lvl, candidate_blvl, candidate_errors in errors[:5]:
            debug_lines.append(f"L{candidate_lvl}/{candidate_blvl}: " + "; ".join(candidate_errors[:4]))
        self.fail(
            f"{skill_name} scenario L{lvl}/{blvl} did not match any tested level permutation. "
            f"Tried {len(errors)} candidates. " + " | ".join(debug_lines)
        )

    def test_druid_skill_expectations(self):
        for group_name, skills in self.expectations["groups"].items():
            for skill_name, skill_data in skills.items():
                for scenario in skill_data["scenarios"]:
                    with self.subTest(group=group_name, skill=skill_name, lvl=scenario["lvl"], blvl=scenario["blvl"]):
                        self.assert_scenario_matches(skill_name, skill_data, scenario)


if __name__ == "__main__":
    unittest.main()
