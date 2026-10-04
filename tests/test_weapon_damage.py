import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d2lib.services.items import BaseItemAnalyzerService
from d2lib.wiki.comparison import base_item_comparison_context


class EmptyRepo:
    def get_excel_table(self, name):
        return []

    def get_string(self, key):
        return key


class TestWeaponDamage(unittest.TestCase):
    def analyze(self, **values):
        row = dict(code='test', name='Test weapon', type='weap', mindam='', maxdam='',
                   minmisdam='', maxmisdam='', **{'2handmindam': '', '2handmaxdam': ''})
        row.update(values)
        return BaseItemAnalyzerService(EmptyRepo(), None)._analyze_item(row, 'Normal')

    def damage_rows(self, item, old=None):
        return {r['label']: r for r in base_item_comparison_context(item, old)['stat_rows'] if r['label'].endswith('Damage')}

    def test_one_hand_only(self):
        item = self.analyze(mindam='3', maxdam='11')
        rows = self.damage_rows(item)
        self.assertEqual(['One-Hand Damage'], list(rows))
        self.assertEqual('3-11', rows['One-Hand Damage']['new'])
        self.assertIsNone(item['throw_damage_min'])

    def test_two_hand_only_ignores_unused_one_hand_values(self):
        item = self.analyze(mindam='1', maxdam='2', **{'2handed': '1', '2handmindam': '125', '2handmaxdam': '149'})
        rows = self.damage_rows(item)
        self.assertEqual(['Two-Hand Damage'], list(rows))
        self.assertEqual('125-149', rows['Two-Hand Damage']['new'])

    def test_flexible_weapon_preserves_both_ranges(self):
        item = self.analyze(mindam='38', maxdam='98', **{'2handed': '1', '1or2handed': '1', '2handmindam': '87', '2handmaxdam': '173'})
        rows = self.damage_rows(item)
        self.assertEqual('38-98', rows['One-Hand Damage']['new'])
        self.assertEqual('87-173', rows['Two-Hand Damage']['new'])

    def test_throwing_preserves_melee_and_throw_ranges(self):
        item = self.analyze(mindam='6', maxdam='11', minmisdam='12', maxmisdam='18')
        rows = self.damage_rows(item)
        self.assertEqual(['One-Hand Damage', 'Throwing Damage'], list(rows))
        self.assertEqual('6-11', rows['One-Hand Damage']['new'])
        self.assertEqual('12-18', rows['Throwing Damage']['new'])

    def test_throw_only_does_not_become_melee(self):
        item = self.analyze(minmisdam='12', maxmisdam='18')
        self.assertEqual(['Throwing Damage'], list(self.damage_rows(item)))
        self.assertIsNone(item['damage_min'])

    def test_damage_modes_compare_independently(self):
        old = self.analyze(mindam='6', maxdam='11', minmisdam='12', maxmisdam='18')
        new = self.analyze(mindam='6', maxdam='11', minmisdam='14', maxmisdam='20')
        rows = self.damage_rows(new, old)
        self.assertEqual('same', rows['One-Hand Damage']['status'])
        self.assertEqual('changed', rows['Throwing Damage']['status'])
        rows = self.damage_rows(self.analyze(mindam='6', maxdam='11'), old)
        self.assertEqual('removed', rows['Throwing Damage']['status'])

    def test_blank_and_zero_ranges_do_not_display(self):
        self.assertEqual({}, self.damage_rows(self.analyze()))
        self.assertEqual({}, self.damage_rows(self.analyze(mindam='0', maxdam='0')))
