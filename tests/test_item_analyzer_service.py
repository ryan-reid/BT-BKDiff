import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.services import BaseItemAnalyzerService, ItemAnalyzerService, SkillAnalyzerService


class FakeRepo:
    def __init__(self):
        self.tables = {
            "armor": [],
            "weapons": [],
            "misc": [],
            "itemtypes": [
                {"Code": "mele", "ItemType": "Melee Weapon", "RunewordCategory1": "r_mel"},
                {"Code": "helm", "ItemType": "Merc Equip", "RunewordCategory1": "r_hel"},
            ],
            "sets": [],
            "gems": [
                {
                    "code": "r30",
                    "weaponMod1Code": "crush",
                    "weaponMod1Param": "",
                    "weaponMod1Min": "20",
                    "weaponMod1Max": "20",
                    "weaponMod2Code": "addxp",
                    "weaponMod2Param": "",
                    "weaponMod2Min": "2",
                    "weaponMod2Max": "2",
                },
                {
                    "code": "r03",
                    "weaponMod1Code": "mana-kill",
                    "weaponMod1Param": "",
                    "weaponMod1Min": "2",
                    "weaponMod1Max": "2",
                },
            ],
        }
        self.strings = {
            "r30": "•••Ber Rune (30)•••",
            "r30l": "Ber",
            "r03": "Tir Rune (3)",
            "r03l": "Tir",
            "melee weapon": "Melee Weapon",
            "merc equip": "Merc Equip",
        }

    def get_excel_table(self, table_name):
        return self.tables.get(table_name, [])

    def get_string(self, key):
        return self.strings.get(str(key).lower(), key)


class FakeResolver:
    def resolve_property(self, code, param, min_val, max_val):
        return {
            "code": code,
            "param": param,
            "min_val": min_val,
            "max_val": max_val,
            "resolved_text": {
                "crush": "20% Chance of Crushing Blow",
                "addxp": "+2% to Experience Gained",
                "mana-kill": "+2 to Mana after each Kill",
            }.get(code, ""),
        }


class TestItemAnalyzerService(unittest.TestCase):
    def test_runewords_use_clean_short_rune_names(self):
        analyzer = ItemAnalyzerService(FakeRepo(), FakeResolver())
        runeword = analyzer.analyze_runeword(
            {
                "*Rune Name": "Practice",
                "Rune1": "r30",
                "Rune2": "r03",
                "itype1": "mele",
            }
        )

        self.assertEqual(["Ber", "Tir"], runeword["runes"])
        self.assertEqual(
            [
                {
                    "rune": "Ber",
                    "properties": [
                        {
                            "code": "crush",
                            "param": "",
                            "min_val": "20",
                            "max_val": "20",
                            "resolved_text": "20% Chance of Crushing Blow",
                        },
                        {
                            "code": "addxp",
                            "param": "",
                            "min_val": "2",
                            "max_val": "2",
                            "resolved_text": "+2% to Experience Gained",
                        },
                    ],
                },
                {
                    "rune": "Tir",
                    "properties": [
                        {
                            "code": "mana-kill",
                            "param": "",
                            "min_val": "2",
                            "max_val": "2",
                            "resolved_text": "+2 to Mana after each Kill",
                        }
                    ],
                },
            ],
            runeword["rune_properties"],
        )

    def test_runeword_base_items_normalize_merc_equip_to_helm(self):
        analyzer = ItemAnalyzerService(FakeRepo(), FakeResolver())
        runeword = analyzer.analyze_runeword(
            {
                "*Rune Name": "Practice",
                "Rune1": "r30",
                "itype1": "helm",
            }
        )

        self.assertEqual(["Helm"], runeword["base_items"])
        self.assertNotIn("Merc Equip", runeword["base_items"])

    def test_base_item_and_skill_services_derive_localized_classes_from_charstats(self):
        repo = FakeRepo()
        repo.tables.update({
            "charstats": [
                {"class": "Sorceress"},
                {"class": "Expansion"},
                {"class": "Cleric"},
            ],
            "itemtypes": [
                {"Code": "cace", "ItemType": "Mace", "Class": "cle", "StaffMods": "cle"},
                {"Code": "orb", "ItemType": "Orb", "Class": "sor", "StaffMods": "sor"},
                {"Code": "unk", "ItemType": "Relic", "Class": "xyz", "StaffMods": "xyz"},
            ],
            "weapons": [
                {"name": "Cleric Mace", "namestr": "Cleric Mace", "code": "c1", "type": "cace", "normcode": "c1", "ubercode": "c1", "ultracode": "c1", "mindam": "2", "maxdam": "5", "gemsockets": "2"},
                {"name": "Sorceress Orb", "namestr": "Sorceress Orb", "code": "o1", "type": "orb", "normcode": "o1", "ubercode": "o1", "ultracode": "o1", "mindam": "1", "maxdam": "3", "gemsockets": "1"},
                {"name": "Mystery Relic", "namestr": "Mystery Relic", "code": "u1", "type": "unk", "normcode": "u1", "ubercode": "u1", "ultracode": "u1", "mindam": "1", "maxdam": "2", "gemsockets": "1"},
            ],
            "skills": [
                {"skill": "Smite Evil", "charclass": "cle", "skilldesc": "smite"},
                {"skill": "Fireball", "charclass": "sor", "skilldesc": "fball"},
            ],
            "skilldesc": [
                {"skilldesc": "smite", "str name": "Smite Evil"},
                {"skilldesc": "fball", "str name": "Fireball"},
            ],
        })
        repo.strings.update({
            "sorceress": "원소술사",
            "cleric": "Kleriker",
        })

        families = {family["name"]: family["members"][0] for family in BaseItemAnalyzerService(repo, FakeResolver()).analyze_base_items()}
        self.assertEqual("Kleriker", families["Cleric Mace"]["class_restriction"])
        self.assertEqual("Kleriker", families["Cleric Mace"]["staffmod_class"])
        self.assertEqual("원소술사", families["Sorceress Orb"]["class_restriction"])
        self.assertEqual("xyz", families["Mystery Relic"]["class_restriction"])

        skill_service = SkillAnalyzerService(repo)
        self.assertEqual("Kleriker", skill_service.generate_skill_tree("cle")["class_name"])
        self.assertEqual("원소술사", skill_service.generate_skill_tree("sor")["class_name"])
        self.assertEqual("XYZ", skill_service.generate_skill_tree("xyz")["class_name"])
        self.assertNotIn("exp", skill_service.class_map)


if __name__ == "__main__":
    unittest.main()
