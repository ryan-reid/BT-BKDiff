import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d2lib.services.item_types import ItemTypeTaxonomy
from d2lib.wiki.generator import WikiContentBuilder
from urllib.parse import parse_qs, urlparse


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

    def test_base_link_preserves_multiple_types_and_exclusions(self):
        url = WikiContentBuilder._runeword_base_filter_url({'raw_row': {'itype1': 'mace', 'itype2': 'swor', 'etype1': 'hamm'}, 'base_items': ['Mace', 'Sword']}, 3)
        params = parse_qs(urlparse(url).query)
        self.assertEqual(['mace|swor'], params['types'])
        self.assertEqual(['hamm'], params['exclude'])
        self.assertEqual(['3'], params['minSockets'])
