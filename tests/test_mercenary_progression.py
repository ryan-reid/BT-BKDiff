import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d2lib.wiki.generator import WikiContentBuilder


class TestMercenaryProgression(unittest.TestCase):
    def test_growth_units_and_rounding(self):
        source = {'Level': '67', 'HP': '900', 'HP/Lvl': '30',
                  'Defense': '744', 'Def/Lvl': '23', 'Dmg-Min': '30', 'Dmg/Lvl': '6',
                  'ResistFire': '100', 'ResistFire/Lvl': '5',
                  'Skill1': 'Fire Arrow', 'Level1': '22', 'LvlPerLvl1': '10',
                  'Chance1': '25', 'ChancePerLvl1': '2'}
        result = WikiContentBuilder._mercenary_stats_at_level(source, 80)
        for field, expected in {'HP': '1290', 'Defense': '1043', 'Dmg-Min': '39',
                                'ResistFire': '116', 'Level1': '26', 'Chance1': '31'}.items():
            self.assertEqual(result[field], expected)
        self.assertEqual(source['HP'], '900')
        self.assertEqual(WikiContentBuilder._mercenary_stats_at_level({}, 80), {})

    def test_classic_rows_do_not_leak_into_expansion(self):
        builder = WikiContentBuilder('', '', '')
        rows = [{'Hireling': 'Rogue Scout', '*SubType': 'Fire - Normal', 'Level': '25',
                 'Version': '0', 'HP': '221'},
                {'Hireling': 'Rogue Scout', '*SubType': 'Fire - Normal', 'Level': '67',
                 'Version': '100', 'HP': '900'}]
        builder._repo = Mock(mpq_path='mod')
        builder._retail_repo = Mock(mpq_path='retail')
        builder._repo.load_tsv.return_value = rows
        builder._retail_repo.load_tsv.return_value = rows
        data = builder._load_mercenary_data()
        self.assertEqual(len(data['rows']), 1)
        self.assertEqual(data['rows'][0]['level'], '67')

    def test_growth_only_changes_are_counted(self):
        builder = WikiContentBuilder('', '', '')
        base = {'Hireling': 'Rogue Scout', '*SubType': 'Fire - Normal', 'Level': '67',
                'Version': '100', 'HP': '900', 'HP/Lvl': '30'}
        builder._repo = Mock(mpq_path='mod')
        builder._retail_repo = Mock(mpq_path='retail')
        builder._repo.load_tsv.return_value = [dict(base, **{'HP/Lvl': '40'})]
        builder._retail_repo.load_tsv.return_value = [base]
        data = builder._load_mercenary_data()
        self.assertEqual(data['rows'][0]['status'], 'changed')
        self.assertEqual(data['rows'][0]['changed_fields'], ['HP/Lvl'])
