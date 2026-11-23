import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d2lib.services.item_types import ItemTypeTaxonomy


class Repo:
    def __init__(self):
        self.strings = {
            'maces': 'Maces',
            'throw': 'Throwing',
            'amazo': 'Amazon',
            'warlo': 'Warlock',
            'circl': 'Circlets',
            'armor': 'Armor',
        }

    def get_excel_table(self, table):
        if table != 'itemtypes':
            return []
        return [
            {'Code': 'weap', 'ItemType': 'Weapon', 'StorePage': 'weap'},
            {'Code': 'armo', 'ItemType': 'Armor', 'StorePage': 'armo'},
            {'Code': 'mele', 'Equiv1': 'weap'},
            {'Code': 'blun', 'Equiv1': 'mele'},
            {'Code': 'bow', 'Equiv1': 'weap'},
            {'Code': 'shld', 'Equiv1': 'armo'},
            {'Code': 'helm', 'Equiv1': 'armo'},
            {'Code': 'mace', 'Equiv1': 'blun', 'UICategory': 'maces'},
            {'Code': 'hamm', 'Equiv1': 'blun', 'UICategory': 'maces'},
            {'Code': 'club', 'Equiv1': 'blun', 'UICategory': 'maces'},
            {'Code': 'axe', 'Equiv1': 'mele', 'UICategory': 'axes'},
            {'Code': 'taxe', 'Equiv1': 'axe', 'UICategory': 'throw'},
            {'Code': 'abow', 'Equiv1': 'bow', 'UICategory': 'amazo', 'Class': 'ama'},
            {'Code': 'grim', 'Equiv1': 'shld', 'UICategory': 'warlo', 'Class': 'war'},
            {'Code': 'circ', 'Equiv1': 'helm', 'UICategory': 'circl'},
            {'Code': 'limited', 'Equiv1': 'mace', 'MaxSockets1': '1', 'MaxSockets2': '2', 'MaxSockets3': '2'},
            {'Code': 'cycle1', 'Equiv1': 'cycle2'},
            {'Code': 'cycle2', 'Equiv1': 'cycle1'},
        ]

    def get_string(self, key):
        return self.strings.get(str(key).lower(), key)


class TestItemTypes(unittest.TestCase):
    def setUp(self):
        self.types = ItemTypeTaxonomy(Repo())

    def test_loot_categories_do_not_determine_runeword_eligibility(self):
        runeword = {'itype1': 'mace', 'Rune1': 'r01', 'Rune2': 'r02', 'Rune3': 'r03'}
        for code in ('mace', 'club', 'hamm'):
            base = {'type': code, 'gemsockets': '4'}
            self.assertEqual('Maces', self.types.category(base))
            self.assertEqual(code == 'mace', self.types.accepts(runeword, base))
            self.assertTrue(self.types.accepts({'itype1': 'mele', 'Rune1': 'r01'}, base))

    def test_specific_loot_categories_take_precedence_over_parent_types(self):
        for code, expected in [('taxe', 'Throwing'), ('abow', 'Amazon'), ('grim', 'Warlock'), ('circ', 'Circlets')]:
            self.assertEqual(expected, self.types.category({'type': code}))
        self.assertEqual('Armor', self.types.group('Warlock'))

    def test_all_includes_exclusions_secondary_types_and_socket_caps(self):
        rule = {'itype1': 'axe', 'itype2': 'blun', 'etype1': 'hamm', 'Rune1': 'r01', 'Rune2': 'r02', 'Rune3': 'r03'}
        self.assertTrue(self.types.accepts(rule, {'type': 'mace', 'gemsockets': '4'}))
        self.assertFalse(self.types.accepts(rule, {'type': 'hamm', 'gemsockets': '6'}))
        self.assertFalse(self.types.accepts(rule, {'type': 'limited', 'gemsockets': '6'}))
        self.assertTrue(self.types.accepts(rule, {'type': 'unknown', 'type2': 'axe', 'gemsockets': '3'}))

    def test_chain_handles_cycles(self):
        self.assertEqual(['cycle1', 'cycle2'], self.types.chain('cycle1'))


class TestItemTypeTaxonomyLocalization(unittest.TestCase):
    class _FakeRepo:
        def __init__(self, itemtypes, strings):
            self.tables = {"itemtypes": itemtypes}
            self.strings = {k.lower(): v for k, v in strings.items()}

        def get_excel_table(self, name):
            return list(self.tables.get(name, []))

        def get_string(self, key):
            return self.strings.get(str(key).lower(), str(key))

        def load_tsv(self, file_path):
            return []

    @staticmethod
    def _fixture_rows():
        return [
            {"ItemType": "Armor", "Code": "armo", "Equiv1": "", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "armo", "UICategory": "", "RunewordCategory1": "r_arm", "RunewordCategory2": ""},
            {"ItemType": "Weapon", "Code": "weap", "Equiv1": "", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "weap", "UICategory": "", "RunewordCategory1": "r_mis", "RunewordCategory2": "r_mel"},
            {"ItemType": "Misc", "Code": "misc", "Equiv1": "", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "misc", "UICategory": "", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Melee Weapon", "Code": "mele", "Equiv1": "weap", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "weap", "UICategory": "", "RunewordCategory1": "r_mel", "RunewordCategory2": ""},
            {"ItemType": "Missile Weapon", "Code": "miss", "Equiv1": "weap", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "weap", "UICategory": "", "RunewordCategory1": "r_mis", "RunewordCategory2": ""},
            {"ItemType": "Mercenary", "Code": "merc", "Equiv1": "armo", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "armo", "UICategory": "helms", "RunewordCategory1": "r_hel", "RunewordCategory2": ""},
            {"ItemType": "Merc Equip", "Code": "helm", "Equiv1": "armo", "Equiv2": "merc", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "armo", "UICategory": "helms", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Body Armor", "Code": "tors", "Equiv1": "armo", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "armo", "UICategory": "armor", "RunewordCategory1": "r_arm", "RunewordCategory2": ""},
            {"ItemType": "Belt", "Code": "belt", "Equiv1": "armo", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "armo", "UICategory": "belts", "RunewordCategory1": "r_blt", "RunewordCategory2": ""},
            {"ItemType": "Sword", "Code": "swor", "Equiv1": "weap", "Equiv2": "mele", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "weap", "UICategory": "sword", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Bow", "Code": "bow", "Equiv1": "weap", "Equiv2": "miss", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "weap", "UICategory": "bows", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Amazon Bow", "Code": "abow", "Equiv1": "bow", "Equiv2": "", "Class": "ama", "Magic": "", "Rare": "", "Normal": "", "StorePage": "weap", "UICategory": "amazo", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Potion", "Code": "poti", "Equiv1": "misc", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "1", "StorePage": "misc", "UICategory": "potis", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Ring", "Code": "ring", "Equiv1": "misc", "Equiv2": "", "Class": "", "Magic": "1", "Rare": "1", "Normal": "", "StorePage": "misc", "UICategory": "rings", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Talisman", "Code": "xtal", "Equiv1": "misc", "Equiv2": "", "Class": "", "Magic": "1", "Rare": "", "Normal": "", "StorePage": "misc", "UICategory": "xtali", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Relic", "Code": "xrel", "Equiv1": "armo", "Equiv2": "", "Class": "", "Magic": "", "Rare": "", "Normal": "", "StorePage": "armo", "UICategory": "xrelic", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Monk Tome", "Code": "xtom", "Equiv1": "armo", "Equiv2": "", "Class": "mnk", "Magic": "", "Rare": "", "Normal": "", "StorePage": "armo", "UICategory": "xmonk", "RunewordCategory1": "", "RunewordCategory2": ""},
        ]

    def test_multilocale_categories_groups_labels_and_dynamic_loot_groups(self):
        from d2lib.services.item_types import ItemTypeTaxonomy

        locales = {
            "enUS": {
                "armor": "Armor",
                "Weapon": "Weapon",
                "StrSklTabItem3": "Weapons",
                "StrGemX3": "Weapons:",
                "helms": "Helms",
                "belts": "Belts",
                "sword": "Swords",
                "bows": "Bows",
                "amazo": "Amazon",
                "potis": "Potions",
                "rings": "Rings",
                "xtali": "Talismans",
                "xrelic": "Relics",
                "xmonk": "Monk",
                "r_hel": "Helmet",
                "r_arm": "Body Armor",
                "r_mel": "Melee",
                "r_mis": "Missile",
                "r_blt": "Waist",
            },
            "deDE": {
                "armor": "Rüstung",
                "Weapon": "Waffe",
                "StrSklTabItem3": "Waffen",
                "StrGemX3": "Waffen:",
                "helms": "Helme",
                "belts": "Gürtel",
                "sword": "Schwerter",
                "bows": "Bögen",
                "amazo": "Amazone",
                "potis": "Tränke",
                "rings": "Ringe",
                "xtali": "Talismane",
                "xrelic": "Relikte",
                "xmonk": "Mönch",
                "r_hel": "Helm",
                "r_arm": "Körperrüstung",
                "r_mel": "Nahkampf",
                "r_mis": "Fernkampf",
                "r_blt": "Gurt",
            },
            "koKR": {
                "armor": "방어구",
                "Weapon": "무기",
                "StrSklTabItem3": "무기",
                "StrGemX3": "무기:",
                "helms": "투구",
                "belts": "허리띠",
                "sword": "검",
                "bows": "활",
                "amazo": "아마존",
                "potis": "물약",
                "rings": "반지",
                "xtali": "부적",
                "xrelic": "유물",
                "xmonk": "수도사",
                "r_hel": "투구",
                "r_arm": "갑옷",
                "r_mel": "근접",
                "r_mis": "투사체",
                "r_blt": "허리띠",
            },
        }
        rows = self._fixture_rows()

        for locale, strings in locales.items():
            with self.subTest(locale=locale):
                taxonomy = ItemTypeTaxonomy(self._FakeRepo(rows, strings))
                weapons_group = strings["StrGemX3"].rstrip(":").strip()
                armor_group = strings["armor"]
                accessories_group = "Accessories"
                self.assertEqual(strings["r_hel"], taxonomy.label("helm"))
                self.assertNotEqual("Merc Equip", taxonomy.label("helm"))
                self.assertEqual(strings["helms"], taxonomy.category({"type": "helm"}))
                self.assertEqual(strings["xrelic"], taxonomy.category({"type": "xrel"}))
                self.assertEqual(armor_group, taxonomy.group({"type": "xrel"}))
                self.assertEqual(weapons_group, taxonomy.group({"type": "swor"}))
                self.assertEqual(accessories_group, taxonomy.group({"type": "xtal"}))
                self.assertEqual("r_blt", taxonomy.runeword_export_bucket("belt"))
                self.assertEqual("r_hel", taxonomy.runeword_export_bucket("helm"))
                self.assertEqual("weapons", taxonomy.runeword_export_bucket("weap"))

                all_groups = taxonomy.loot_groups(include_accessories=True)
                self.assertIn(strings["xrelic"], all_groups[armor_group])
                self.assertIn(strings["helms"], all_groups[armor_group])
                self.assertIn(strings["xmonk"], all_groups[armor_group])
                # Non-class armor categories precede class categories in each group.
                self.assertLess(
                    all_groups[armor_group].index(strings["xrelic"]),
                    all_groups[armor_group].index(strings["xmonk"]),
                )
                self.assertIn(strings["sword"], all_groups[weapons_group])
                self.assertLess(
                    all_groups[weapons_group].index(strings["sword"]),
                    all_groups[weapons_group].index(strings["amazo"]),
                )
                self.assertEqual(sorted([strings["rings"], strings["xtali"]], key=str.casefold), all_groups[accessories_group])
                for cats in all_groups.values():
                    self.assertNotIn(strings["potis"], cats)

                base_only = taxonomy.loot_groups(include_accessories=False)
                for cats in base_only.values():
                    self.assertNotIn(strings["rings"], cats)
