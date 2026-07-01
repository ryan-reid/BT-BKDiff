import os
import sys
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.services import ItemAnalyzerService


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


if __name__ == "__main__":
    unittest.main()
