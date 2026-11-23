import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d2lib.services.item_types import ItemTypeTaxonomy


class Repo:
    def get_excel_table(self, table):
        if table != 'itemtypes':
            return []
        return [
            {'Code': 'weap', 'ItemType': 'Weapon'},
            {'Code': 'mele', 'Equiv1': 'weap'},
            {'Code': 'blun', 'Equiv1': 'mele'},
            {'Code': 'mace', 'Equiv1': 'blun', 'UICategory': 'maces'},
            {'Code': 'hamm', 'Equiv1': 'blun', 'UICategory': 'maces'},
            {'Code': 'club', 'Equiv1': 'blun', 'UICategory': 'maces'},
            {'Code': 'axe', 'Equiv1': 'mele', 'UICategory': 'axes'},
            {'Code': 'taxe', 'Equiv1': 'axe', 'UICategory': 'throw'},
            {'Code': 'abow', 'Equiv1': 'bow', 'UICategory': 'amazo'},
            {'Code': 'grim', 'Equiv1': 'shld', 'UICategory': 'warlo'},
            {'Code': 'circ', 'Equiv1': 'helm', 'UICategory': 'circl'},
            {'Code': 'limited', 'Equiv1': 'mace', 'MaxSockets1': '1', 'MaxSockets2': '2', 'MaxSockets3': '2'},
            {'Code': 'cycle1', 'Equiv1': 'cycle2'},
            {'Code': 'cycle2', 'Equiv1': 'cycle1'},
        ]

    def get_string(self, key):
        return key


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
            {"ItemType": "Armor", "Code": "armo", "Equiv1": "", "Equiv2": "", "UICategory": "", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Weapon", "Code": "weap", "Equiv1": "", "Equiv2": "", "UICategory": "", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Melee Weapon", "Code": "mele", "Equiv1": "weap", "Equiv2": "", "UICategory": "", "RunewordCategory1": "r_mel", "RunewordCategory2": ""},
            {"ItemType": "Missile Weapon", "Code": "miss", "Equiv1": "weap", "Equiv2": "", "UICategory": "", "RunewordCategory1": "r_mis", "RunewordCategory2": ""},
            {"ItemType": "Mercenary", "Code": "merc", "Equiv1": "armo", "Equiv2": "", "UICategory": "", "RunewordCategory1": "r_hel", "RunewordCategory2": ""},
            {"ItemType": "Merc Equip", "Code": "helm", "Equiv1": "armo", "Equiv2": "merc", "UICategory": "helms", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Body Armor", "Code": "tors", "Equiv1": "armo", "Equiv2": "", "UICategory": "armor", "RunewordCategory1": "r_arm", "RunewordCategory2": ""},
            {"ItemType": "Sword", "Code": "swor", "Equiv1": "weap", "Equiv2": "mele", "UICategory": "sword", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Bow", "Code": "bow", "Equiv1": "weap", "Equiv2": "miss", "UICategory": "bows", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Ring", "Code": "ring", "Equiv1": "", "Equiv2": "", "UICategory": "rings", "RunewordCategory1": "", "RunewordCategory2": ""},
            {"ItemType": "Relic", "Code": "xrel", "Equiv1": "armo", "Equiv2": "", "UICategory": "xrelic", "RunewordCategory1": "", "RunewordCategory2": ""},
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
                "sword": "Swords",
                "bows": "Bows",
                "rings": "Rings",
                "xrelic": "Relics",
                "r_hel": "Helmet",
                "r_arm": "Body Armor",
                "r_mel": "Melee",
                "r_mis": "Missile",
            },
            "deDE": {
                "armor": "Rüstung",
                "Weapon": "Waffe",
                "StrSklTabItem3": "Waffen",
                "StrGemX3": "Waffen:",
                "helms": "Helme",
                "sword": "Schwerter",
                "bows": "Bögen",
                "rings": "Ringe",
                "xrelic": "Relikte",
                "r_hel": "Helm",
                "r_arm": "Körperrüstung",
                "r_mel": "Nahkampf",
                "r_mis": "Fernkampf",
            },
            "koKR": {
                "armor": "방어구",
                "Weapon": "무기",
                "StrSklTabItem3": "무기",
                "StrGemX3": "무기:",
                "helms": "투구",
                "sword": "검",
                "bows": "활",
                "rings": "반지",
                "xrelic": "유물",
                "r_hel": "투구",
                "r_arm": "갑옷",
                "r_mel": "근접",
                "r_mis": "투사체",
            },
        }
        rows = self._fixture_rows()

        for locale, strings in locales.items():
            with self.subTest(locale=locale):
                taxonomy = ItemTypeTaxonomy(self._FakeRepo(rows, strings))
                weapons_group = strings["StrGemX3"].rstrip(":").strip()
                armor_group = strings["armor"]
                self.assertEqual(strings["r_hel"], taxonomy.label("helm"))
                self.assertNotEqual("Merc Equip", taxonomy.label("helm"))
                self.assertEqual(strings["helms"], taxonomy.category({"type": "helm"}))
                self.assertEqual(strings["xrelic"], taxonomy.category({"type": "xrel"}))
                self.assertEqual(armor_group, taxonomy.group({"type": "xrel"}))
                self.assertEqual(weapons_group, taxonomy.group({"type": "swor"}))

                all_groups = taxonomy.loot_groups(include_accessories=True)
                self.assertIn(strings["xrelic"], all_groups[armor_group])
                self.assertIn(strings["helms"], all_groups[armor_group])
                self.assertIn(strings["sword"], all_groups[weapons_group])

                base_only = taxonomy.loot_groups(include_accessories=False)
                for cats in base_only.values():
                    self.assertNotIn(strings["rings"], cats)
