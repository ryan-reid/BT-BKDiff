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

    def test_runeword_and_set_names_resolve_from_strings_with_stable_ids(self):
        repo = FakeRepo()
        repo.tables["armor"] = [{"code": "uap", "name": "Light Plate", "namestr": "uap", "type": "tors"}]
        repo.tables["itemtypes"].append({"Code": "tors", "ItemType": "Armor"})
        repo.tables["sets"] = [
            {"index": "McAuley's Folly", "name": "McAuley's Folly", "version": "0"},
            {"index": "Fallback Set", "name": "Fallback Set", "version": "100"},
        ]
        repo.strings.update({
            "runeword64": "Judgement",
            "runeword171": "Hysteria",
            "runeword172": "Mania",
            "runeword56": "Revenge",
            "runeword185": "Revenge",
            "mcauley's folly": "Sander's Folly",
            "mcauley's boots": "Sander's Riprap",
            "uap": "Light Plate",
            "armor": "Armor",
        })

        analyzer = ItemAnalyzerService(repo, FakeResolver())

        hysteria = analyzer.analyze_runeword({"Name": "Runeword171", "*Rune Name": "Hustle (armor)", "Rune1": "r03", "itype1": "helm"})
        mania = analyzer.analyze_runeword({"Name": "Runeword172", "*Rune Name": "Hustle (weapon)", "Rune1": "r03", "itype1": "mele"})
        judgement = analyzer.analyze_runeword({"Name": "Runeword64", "*Rune Name": "Judgment", "Rune1": "r03", "itype1": "mele"})
        missing_str = analyzer.analyze_runeword({"Name": "Runeword999", "*Rune Name": "Future Word", "Rune1": "r03", "itype1": "mele"})
        no_comment = analyzer.analyze_runeword({"Name": "Runeword998", "Rune1": "r03", "itype1": "mele"})
        dup_a = analyzer.analyze_runeword({"Name": "Runeword56", "*Rune Name": "Revenge", "Rune1": "r03"})
        dup_b = analyzer.analyze_runeword({"Name": "Runeword185", "*Rune Name": "Revenge", "Rune1": "r03", "itype1": "mele"})

        self.assertEqual(("Runeword171", "Hysteria"), (hysteria["id"], hysteria["name"]))
        self.assertEqual(("Runeword172", "Mania"), (mania["id"], mania["name"]))
        self.assertEqual(("Runeword64", "Judgement"), (judgement["id"], judgement["name"]))
        self.assertEqual(("Runeword999", "Future Word"), (missing_str["id"], missing_str["name"]))
        self.assertEqual(("Runeword998", "Runeword998"), (no_comment["id"], no_comment["name"]))
        self.assertNotEqual(dup_a["id"], dup_b["id"])
        self.assertEqual(("Revenge", "Revenge"), (dup_a["name"], dup_b["name"]))

        ko_repo = FakeRepo()
        ko_repo.strings["runeword171"] = "광기"
        ko_hysteria = ItemAnalyzerService(ko_repo, FakeResolver()).analyze_runeword(
            {"Name": "Runeword171", "*Rune Name": "Hustle (armor)", "Rune1": "r03"}
        )
        self.assertEqual(("Runeword171", "광기"), (ko_hysteria["id"], ko_hysteria["name"]))

        set_item = analyzer.analyze_set_item({"index": "McAuley's Boots", "set": "McAuley's Folly", "item": "uap", "lvl req": "20"})
        fallback_set_item = analyzer.analyze_set_item({"index": "Missing Item", "set": "Fallback Set", "item": "uap", "lvl req": "10"})
        self.assertEqual("Sander's Folly", set_item["set_name"])
        self.assertEqual("Sander's Riprap", set_item["display_name"])
        self.assertEqual("Fallback Set", fallback_set_item["set_name"])


class TestTaxonomyAndMiscLocalization(unittest.TestCase):
    class _StubRepo:
        def __init__(self, tables, strings):
            self.tables = tables
            self.strings = {k.lower(): v for k, v in strings.items()}

        def get_excel_table(self, name):
            return list(self.tables.get(name, []))

        def get_string(self, key):
            return self.strings.get(str(key).lower(), str(key))

        def load_tsv(self, file_path):
            return []

    class _StubResolver:
        def resolve_properties(self, row, prefix="", count=0, **kwargs):
            return [f"{prefix}{row.get(f'{prefix}Code1', 'prop')}"] if row.get(f"{prefix}Code1") else []

        def resolve_property(self, code, param="", min_val="", max_val=""):
            return {"code": code, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": code}

    @staticmethod
    def _base_tables():
        return {
            "itemtypes": [
                {"ItemType": "Armor", "Code": "armo", "Equiv1": "", "Equiv2": "", "UICategory": "", "RunewordCategory1": ""},
                {"ItemType": "Weapon", "Code": "weap", "Equiv1": "", "Equiv2": "", "UICategory": "", "RunewordCategory1": ""},
                {"ItemType": "Mercenary", "Code": "merc", "Equiv1": "armo", "Equiv2": "", "UICategory": "", "RunewordCategory1": "r_hel"},
                {"ItemType": "Merc Equip", "Code": "helm", "Equiv1": "armo", "Equiv2": "merc", "UICategory": "helms", "RunewordCategory1": ""},
                {"ItemType": "Sword", "Code": "swor", "Equiv1": "weap", "Equiv2": "", "UICategory": "sword", "RunewordCategory1": "r_mel"},
                {"ItemType": "Rune", "Code": "rune", "Equiv1": "", "Equiv2": "", "UICategory": "", "RunewordCategory1": ""},
                {"ItemType": "Gem", "Code": "gem", "Equiv1": "", "Equiv2": "", "UICategory": "", "RunewordCategory1": ""},
                {"ItemType": "Potion", "Code": "poti", "Equiv1": "", "Equiv2": "", "UICategory": "potis", "RunewordCategory1": ""},
                {"ItemType": "Stamina Potion", "Code": "spot", "Equiv1": "poti", "Equiv2": "", "UICategory": "potis", "RunewordCategory1": ""},
                {"ItemType": "Healing Potion", "Code": "hpot", "Equiv1": "", "Equiv2": "", "UICategory": "potis", "RunewordCategory1": ""},
                {"ItemType": "Key", "Code": "key", "Equiv1": "", "Equiv2": "", "UICategory": "keysr", "RunewordCategory1": ""},
            ],
            "armor": [
                {"name": "Cap", "code": "cap", "normcode": "cap", "ubercode": "", "ultracode": "", "type": "helm", "minac": "3", "maxac": "5", "spawnable": "1"},
            ],
            "weapons": [
                {"name": "Short Sword", "code": "ssd", "normcode": "ssd", "ubercode": "", "ultracode": "", "type": "swor", "spawnable": "1"},
            ],
            "misc": [
                {"name": "El Rune", "code": "r01", "type": "rune", "spawnable": "1", "UICatOverride": ""},
                {"name": "Perfect Ruby", "code": "gpr", "type": "gem", "spawnable": "1", "UICatOverride": ""},
                {"name": "Terrorize Token", "code": "tok", "type": "ques", "spawnable": "1", "UICatOverride": "terrt"},
                {"name": "Token of Absolution", "code": "toa", "type": "ques", "spawnable": "1", "UICatOverride": "absol"},
                {"name": "Custom Idol", "code": "xid", "type": "ques", "spawnable": "1", "UICatOverride": "xcust"},
                {"name": "Greater Healing Potion", "code": "hp4", "type": "hpot", "spawnable": "1", "UICatOverride": "Null"},
                {"name": "Invisible Token", "code": "inv", "type": "key", "spawnable": "1", "UICatOverride": "dns"},
                {"name": "(B)Crafting Tablet", "code": "bct", "type": "spot", "quest": "", "useable": "0", "spawnable": "1", "UICatOverride": ""},
                {"name": "Stamina Potion", "code": "vps", "type": "spot", "quest": "", "useable": "1", "spawnable": "1", "UICatOverride": ""},
                {"name": "Pandemonium Key", "code": "pk1", "type": "spot", "quest": "", "useable": "0", "spawnable": "1", "UICatOverride": "uberm"},
            ],
            "gems": [
                {
                    "code": "r01",
                    "weaponMod1Code": "att",
                    "helmMod1Code": "light",
                    "shieldMod1Code": "res-pois",
                },
                {
                    "code": "gpr",
                    "weaponMod1Code": "fire-min",
                    "helmMod1Code": "hp",
                    "shieldMod1Code": "res-fire",
                },
            ],
            "uniqueitems": [
                {"index": "Biggin's Bonnet", "code": "cap", "lvl req": "3"},
            ],
            "runes": [
                {"Name": "Runeword99", "Rune1": "r01", "itype1": "helm", "T1Code1": "ac"},
            ],
            "setitems": [],
        }

    def test_multilocale_export_groups_runeword_bases_and_misc_categories(self):
        from d2lib.services.items import ItemAnalyzerService
        from d2lib.services.misc import MiscAnalyzerService
        from d2lib.wiki.comparison import gem_rune_comparison_context

        locales = {
            "enUS": {
                "Armor": "Armor",
                "Weapon": "Weapon",
                "helms": "Helms",
                "sword": "Swords",
                "r_hel": "Helmet",
                "r_mel": "Melee",
                "r01": "El Rune",
                "r01L": "El",
                "gpr": "Perfect Ruby",
                "potis": "Potions",
                "keysr": "Keys",
                "terrt": "Terrorize Tokens",
                "absol": "Essence / Token of Absolution",
                "uberm": "Uber Materials",
                "xcust": "Custom Misc",
                "StrGemX1": "Helms:",
                "StrGemX2": "Shields:",
                "StrGemX3": "Weapons:",
                "StrGemX4": "Armor:",
            },
            "deDE": {
                "Armor": "Rüstung",
                "Weapon": "Waffe",
                "helms": "Helme",
                "sword": "Schwerter",
                "r_hel": "Helm",
                "r_mel": "Nahkampf",
                "r01": "El-Rune",
                "r01L": "El",
                "gpr": "Perfekter Rubin",
                "potis": "Tränke",
                "keysr": "Schlüssel",
                "terrt": "Schreckenszeichen",
                "absol": "Essenz / Zeichen der Absolution",
                "uberm": "Über-Materialien",
                "xcust": "Benutzerdefiniert",
                "StrGemX1": "Helme:",
                "StrGemX2": "Schilde:",
                "StrGemX3": "Waffen:",
                "StrGemX4": "Rüstungen:",
            },
            "koKR": {
                "Armor": "방어구",
                "Weapon": "무기",
                "helms": "투구",
                "sword": "검",
                "r_hel": "투구",
                "r_mel": "근접",
                "r01": "엘 룬",
                "r01L": "엘",
                "gpr": "완벽한 루비",
                "potis": "물약",
                "keysr": "열쇠",
                "terrt": "공포의 마수 토큰",
                "absol": "정수 / 면죄의 징표",
                "uberm": "우버 재료",
                "xcust": "사용자 지정",
                "StrGemX1": "투구:",
                "StrGemX2": "방패:",
                "StrGemX3": "무기:",
                "StrGemX4": "갑옷:",
            },
        }
        tables = self._base_tables()

        for locale, strings in locales.items():
            with self.subTest(locale=locale):
                repo = self._StubRepo(tables, strings)
                resolver = self._StubResolver()
                analyzer = ItemAnalyzerService(repo, resolver)

                self.assertEqual(strings["r_hel"], analyzer.get_item_category("cap"))
                self.assertEqual(("Others", "helms", strings["helms"]), analyzer.get_unique_export_groups({"code": "cap"}))
                base_families = BaseItemAnalyzerService(repo, resolver).analyze_base_items()
                cap_family = next(f for f in base_families if f["members"][0]["code"] == "cap")
                self.assertEqual(strings["Armor"], cap_family["group"])
                self.assertEqual(strings["helms"], cap_family["members"][0]["loot_category"])
                rw_group = analyzer.get_runeword_export_group({"Name": "Runeword99", "itype1": "helm"})
                self.assertEqual(("helms", "helm", strings["r_hel"]), rw_group)
                rw_dto = analyzer.analyze_runeword({"Name": "Runeword99", "Rune1": "r01", "itype1": "helm", "T1Code1": "ac"})
                self.assertEqual([strings["r_hel"]], rw_dto["base_items"])

                misc_service = MiscAnalyzerService(repo, resolver)
                groups = misc_service.analyze_misc_items()
                by_key = {g["category_key"]: g for g in groups}
                self.assertIn("runes", by_key)
                self.assertIn("gems", by_key)
                self.assertEqual(strings["terrt"], by_key["terrt"]["category"])
                self.assertEqual(strings["absol"], by_key["absol"]["category"])
                self.assertEqual(strings["xcust"], by_key["xcust"]["category"])
                self.assertEqual("Crafting Materials", by_key["crafting"]["category"])
                self.assertIn("bct", [m["code"] for m in by_key["crafting"]["members"]])
                potis_codes = [m["code"] for m in by_key["potis"]["members"]]
                self.assertIn("hp4", potis_codes)
                self.assertIn("vps", potis_codes)
                self.assertNotIn("bct", potis_codes)
                self.assertEqual(strings["uberm"], by_key["uberm"]["category"])
                self.assertIn("pk1", [m["code"] for m in by_key["uberm"]["members"]])
                self.assertIn("inv", [m["code"] for m in by_key["keysr"]["members"]])

                rune_item = by_key["runes"]["members"][0]
                ctx = gem_rune_comparison_context(rune_item, None)
                expected_slots = [
                    strings["StrGemX3"].rstrip(":").strip(),
                    f"{strings['StrGemX4'].rstrip(':').strip()}/{strings['StrGemX1'].rstrip(':').strip()}",
                    strings["StrGemX2"].rstrip(":").strip(),
                ]
                self.assertEqual(expected_slots, [row["label"] for row in ctx["property_rows"]])

    def test_should_include_item_filters_blank_separator_rows_but_keeps_synthetic_test_rows(self):
        from d2lib.wiki.item_helpers import should_include_item

        self.assertFalse(
            should_include_item(
                {
                    "id": "Expansion",
                    "base_item": "Expansion",
                    "item_type": "Miscellaneous",
                    "properties": [],
                    "raw_row": {"index": "Expansion", "code": ""},
                },
                "unique",
            )
        )
        self.assertFalse(
            should_include_item(
                {
                    "id": "Expansion",
                    "base_item": "확장팩",
                    "item_type": "기타",
                    "properties": [],
                    "raw_row": {"index": "Expansion", "item": ""},
                },
                "set",
            )
        )
        self.assertTrue(
            should_include_item(
                {
                    "id": "Set Cap",
                    "base_item": "Cap",
                    "item_type": "Helm",
                    "properties": [],
                    "raw_row": {"set": "Practice Set"},
                },
                "set",
            )
        )


if __name__ == "__main__":
    unittest.main()
