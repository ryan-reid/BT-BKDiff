import json
import os
import re
import sys
import unittest
from typing import Dict, List, Optional


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.repository import D2Repository
from d2lib.repository import strip_json_comments
from d2lib.services import SkillAnalyzerService


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

    def _clone_snapshot_tables(self):
        return {
            table: [dict(row) for row in self.repo.get_excel_table(table)]
            for table in ("skills", "skilldesc", "missiles", "monstats", "monlvl", "charstats")
        }

    def test_immolation_arrow_uses_skills_txt_calc_columns_dynamically(self):
        tables = self._clone_snapshot_tables()
        imm = next(r for r in tables["skills"] if r.get("skill") == "Immolation Arrow")
        imm["Param8"] = "10"
        repo = _MutableSnapshotRepo(tables, self.repo.strings)
        svc = SkillAnalyzerService(repo)

        synergies = {normalize_skill_key("Fire Arrow"): 20, normalize_skill_key("Exploding Arrow"): 20, "immolationarrow": 20}
        effects = svc.get_skill_display_effects("Immolation Arrow", 24, 20, synergies)
        by_label_raw = {e["label"]: e["value"] for e in effects}
        # Base explosion at lvl 24 (Param8=5 was 390-396 at 3x mult -> 130-132 base -> 5x mult with Param8=10 = 650-660)
        self.assertEqual("650.00-660.00", by_label_raw["Fire Explosion Damage"])
        # Burn dps scaled dynamically via mael formula using (20+20)*10=400% -> 5x vs baseline 3x
        base_dps = [float(x) for x in self.match_effect_value(
            self.render_skill_effects("Immolation Arrow", 24, 20, {"Fire Arrow": 20, "Exploding Arrow": 20}),
            "Fire Damage per Second",
        ).replace(" dmg/s", "").split("-")]
        scaled_dps = [float(x) for x in by_label_raw["Average Fire Damage"].replace(" dmg/s", "").split("-")]
        self.assertAlmostEqual(base_dps[0] * (5.0 / 3.0), scaled_dps[0], delta=1.5)
        self.assertAlmostEqual(base_dps[1] * (5.0 / 3.0), scaled_dps[1], delta=1.5)

        # Remove Exploding Arrow from EDmgSymPerCalc and confirm mael drops from 5x to 3x
        imm["EDmgSymPerCalc"] = "skill('Fire Arrow'.blvl) * par8"
        svc2 = SkillAnalyzerService(_MutableSnapshotRepo(tables, self.repo.strings))
        eff2 = svc2.get_skill_display_effects("Immolation Arrow", 24, 20, synergies)
        by_label2_raw = {e["label"]: e["value"] for e in eff2}
        self.assertEqual("390.00-396.00", by_label2_raw["Fire Explosion Damage"])
        scaled_dps2 = [float(x) for x in by_label2_raw["Average Fire Damage"].replace(" dmg/s", "").split("-")]
        self.assertAlmostEqual(base_dps[0], scaled_dps2[0], delta=1.5)

    def test_descline_13_summon_life_reads_from_monstats_and_skills(self):
        tables = self._clone_snapshot_tables()
        valk_mon = next(r for r in tables["monstats"] if r.get("Id", "").lower() == "valkyrie")
        valk_mon["minHP"] = "500"
        valk_mon["maxHP"] = "700"  # average 600
        svc = SkillAnalyzerService(_MutableSnapshotRepo(tables, self.repo.strings))

        for decoy_lvl, expected_hp in ((0, 600.0), (10, 1800.0), (20, 3000.0)):
            eff = svc.get_skill_display_effects("Valkyrie", 1, 1, {"valkyrie": 1, "decoy": decoy_lvl})
            life = next(normalize_val(e["value"]) for e in eff if e["label"] == "Life")
            self.assertAlmostEqual(expected_hp, life, delta=0.5, msg=f"decoy_lvl={decoy_lvl}")

    def test_multi_locale_parity_and_skill_tree_synergies(self):
        tables = self._clone_snapshot_tables()
        # Add charstats & a synergy row with a missing string key to guard against NameError
        tables["charstats"] = [{"class": "Amazon"}]
        de_strings = {
            "amazon": "Amazone",
            "strskill3": "Manakosten: %d",
            "strskill5": "Feuerschaden: %d-%d",
            "strskill6": "Kälteschaden: %d-%d",
            "strskill8": "Giftschaden: %d-%d",
            "strskill13": "Dauer der Kälte: %d Sek.",
            "strskill18": "Radius: %d Meter",
            "strskill20": "Dauer: %d Sek.",
            "strskill21": "Verteidigung: %+d%%",
            "strskill22": "Angriffswert: %+d%%",
            "strskill42": "Leben: %d",
            "strskill63": "über %d Sek.",
            "strskill82": "Dauer des Feuers: %d Sek.",
            "strskill83": "Feuerexplosionsschaden: %d-%d",
            "strskilldamagepercent": "Schaden: %+d%%",
            "strskillfiredamageaveragepersecond": "Durchschnittlicher Feuerschaden: %d-%d pro Sekunde",
            "strskillcoldlengthsingular": "Dauer der Kälte: %d Sekunde",
            "strskillpoisonlengthsingular": "über %d Sekunde",
            "strskillfiredurationsingular": "Dauer des Feuers: %d Sekunde",
            "strskilldurationsingular": "Dauer: %d Sekunde",
            "strskillradiussingular": "Radius: %d Meter",
            "strskillcastingdelaysingular": "Einsatzverzögerung: %d Sek.",
            "strskillenemydefenseflatbonus": "Gegnerische Verteidigung: %+d",
            "convphy2magalt": "Wandelt %d%% physischen Schaden in Elementarschaden um",
            "firedplev": "%s: %+d%% Feuerschaden pro Level",
            "afdimm": "%s: %+d%% Durchschnittlicher Feuerschaden pro Sekunde pro Level",
            "poisdplev": "%s: %+d%% Giftschaden pro Level",
            "hpplev": "%s: %+d%% Leben pro Level",
            "attrateplev": "%s: %+d%% Angriffswert pro Level",
            "colddplev": "%s: %+d%% Kälteschaden pro Level",
            "frezlenplev": "%s: %+d%% Einfrierdauer pro Level",
            "skillname7": "Feuerpfeil",
            "skillname16": "Explodierender Pfeil",
            "skillname23": "Durchschlagen",
            "skillname27": "Feuerbrandpfeil",
            "skillname28": "Lockvogel",
            "skillname32": "Walküre",
            "strskltree17": "Gift",
            "strskltree23": "Kälte",
            "strskltree25": "Feuer",
        }
        ko_strings = {
            "amazon": "아마존",
            "strskill3": "마나 소모: %d",
            "strskill5": "화염 피해: %d-%d",
            "strskill6": "냉기 피해: %d-%d",
            "strskill8": "독 피해: %d-%d",
            "strskill13": "냉기 지속시간: %d초",
            "strskill18": "반경: %d미터",
            "strskill20": "지속시간: %d초",
            "strskill21": "방어력: %+d%%",
            "strskill22": "명중률: %+d%%",
            "strskill42": "생명력: %d",
            "strskill63": "%d초에 걸쳐",
            "strskill82": "화염 지속시간: %d초",
            "strskill83": "화염 폭발 피해: %d-%d",
            "strskilldamagepercent": "공격력: %+d%%",
            "strskillfiredamageaveragepersecond": "평균 화염 피해: 초당 %d-%d",
            "strskillcoldlengthsingular": "냉기 지속시간: %d초",
            "strskillpoisonlengthsingular": "%d초에 걸쳐",
            "strskillfiredurationsingular": "화염 지속시간: %d초",
            "strskilldurationsingular": "지속시간: %d초",
            "strskillradiussingular": "반경: %d미터",
            "strskillcastingdelaysingular": "시전 지연 시간: %d초",
            "strskillenemydefenseflatbonus": "적 방어력: %+d",
            "convphy2magalt": "물리 피해의 %d%%를 원소 피해로 전환",
            "firedplev": "%s: 레벨당 화염 피해 %+d%%",
            "afdimm": "%s: 레벨당 초당 평균 화염 피해 %+d%%",
            "poisdplev": "%s: 레벨당 독 피해 %+d%%",
            "hpplev": "%s: 레벨당 생명력 %+d%%",
            "attrateplev": "%s: 레벨당 명중률 %+d%%",
            "colddplev": "%s: 레벨당 냉기 피해 %+d%%",
            "frezlenplev": "%s: 레벨당 빙결 시간 %+d%%",
            "skillname7": "화염 화살",
            "skillname16": "폭발 화살",
            "skillname23": "간파",
            "skillname27": "제물 화살",
            "skillname28": "미끼",
            "skillname32": "발키리",
            "strskltree17": "독",
            "strskltree23": "냉기",
            "strskltree25": "화염",
        }

        def unit_of(val_str: str) -> str:
            for suffix in (" dmg/s", "%", "s", "y"):
                if val_str.endswith(suffix):
                    return suffix
            return ""

        en_svc = self.service
        de_svc = SkillAnalyzerService(_MutableSnapshotRepo(tables, de_strings, self.repo.strings, locale="deDE"))
        ko_svc = SkillAnalyzerService(_MutableSnapshotRepo(tables, ko_strings, self.repo.strings, locale="koKR"))

        test_cases = [
            ("Immolation Arrow", 24, 20, {"firearrow": 20, "explodingarrow": 20}),
            ("Cold Arrow", 20, 20, {"icearrow": 20, "freezingarrow": 20}),
            ("Poison Javelin", 20, 20, {"plaguejavelin": 20}),
            ("Inner Sight", 20, 20, {}),
            ("Valkyrie", 20, 20, {"decoy": 20, "penetrate": 5}),
        ]
        for sname, lvl, blvl, syn in test_cases:
            en_eff = en_svc.get_skill_display_effects(sname, lvl, blvl, syn)
            de_eff = de_svc.get_skill_display_effects(sname, lvl, blvl, syn)
            ko_eff = ko_svc.get_skill_display_effects(sname, lvl, blvl, syn)
            self.assertEqual(
                [(normalize_val(e["value"]), unit_of(e["value"])) for e in en_eff],
                [(normalize_val(e["value"]), unit_of(e["value"])) for e in de_eff],
                f"deDE value/unit mismatch for {sname}",
            )
            self.assertEqual(
                [(normalize_val(e["value"]), unit_of(e["value"])) for e in en_eff],
                [(normalize_val(e["value"]), unit_of(e["value"])) for e in ko_eff],
                f"koKR value/unit mismatch for {sname}",
            )

        de_tree = de_svc.generate_skill_tree("ama")
        ko_tree = ko_svc.generate_skill_tree("ama")
        self.assertEqual("Amazone", de_tree["class_name"])
        self.assertEqual("아마존", ko_tree["class_name"])

        de_by_id = {sk["id"]: sk for sk in de_tree["skills"]}
        ko_by_id = {sk["id"]: sk for sk in ko_tree["skills"]}
        self.assertEqual("immolation-arrow", de_by_id["Immolation Arrow"]["slug"])
        self.assertEqual("immolation-arrow", ko_by_id["Immolation Arrow"]["slug"])
        self.assertEqual("Feuerbrandpfeil", de_by_id["Immolation Arrow"]["name"])
        self.assertEqual("제물 화살", ko_by_id["Immolation Arrow"]["name"])
        self.assertTrue(
            any("Feuerschaden pro Level" in s["effect"] and "per Level" not in s["effect"]
                for s in de_by_id["Immolation Arrow"]["synergies"])
        )
        self.assertTrue(
            any("레벨당 화염 피해" in s["effect"] and "per Level" not in s["effect"]
                for s in ko_by_id["Immolation Arrow"]["synergies"])
        )

        # Ensure missing synergy string key does not raise NameError
        tables_missing = self._clone_snapshot_tables()
        sd_row = next(r for r in tables_missing["skilldesc"] if r.get("skilldesc") == "fire arrow")
        sd_row["dsc3textb2"] = "missing_synergy_skill_key"
        missing_tree = SkillAnalyzerService(_MutableSnapshotRepo(tables_missing, de_strings, locale="deDE")).generate_skill_tree("ama")
        self.assertIn("Fire Arrow", {s["id"] for s in missing_tree["skills"]})


class _MutableSnapshotRepo:
    def __init__(self, tables, strings, canonical_strings=None, locale="enUS"):
        self.tables = tables
        self.strings = {k.lower(): v for k, v in strings.items()}
        self.canonical_strings = {k.lower(): v for k, v in (canonical_strings or {}).items()}
        self.locale = locale

    def get_excel_table(self, table_name: str):
        return self.tables.get(table_name, [])

    def get_string(self, key: str) -> str:
        return self.strings.get(key.lower(), key) if key else ""

    def get_canonical_string(self, key: str) -> str:
        return self.canonical_strings.get(key.lower(), "") if key else ""

    def load_tsv(self, file_path: str):
        return []


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
