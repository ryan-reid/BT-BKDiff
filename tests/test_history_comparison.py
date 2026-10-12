import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d2lib.wiki.history_comparison import HistoricalRepository, analyze_revision, with_shared_set_bonuses, availability_rows, comparison_has_changes
from d2lib.wiki.comparison import base_item_comparison_context
from d2lib.wiki.renderers import WikiRenderer


class HistoryComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tables = {
            'weapons': [{'code': 'ax', 'name': 'Axe', 'type': 'axe', 'mindam': '2', 'maxdam': '8',
                         '2handmindam': '4', '2handmaxdam': '12', 'minmisdam': '3', 'maxmisdam': '9'}],
            'itemtypes': [{'Code': 'axe', 'Equiv1': 'weap'}, {'Code': 'weap'}],
            'qualityitems': [],
        }

    def analyze(self, tables=None, identity='base:ax', canonical=lambda value: value):
        return analyze_revision(tables or self.tables, {}, identity, canonical)

    def test_revisions_compare_independent_damage_to_fixed_baseline(self):
        first = self.analyze()['entry']
        modified = copy.deepcopy(self.tables)
        modified['weapons'][0].update(mindam='5', **{'2handmindam': '7', 'minmisdam': '6'})
        second = self.analyze(modified)['entry']
        comparison = base_item_comparison_context(second, first)
        rows = {row['label']: row for row in comparison['stat_rows']}
        for label, before, after in [('One-Hand Damage', '2-8', '5-8'), ('Two-Hand Damage', '4-12', '7-12'), ('Throwing Damage', '3-9', '6-9')]:
            self.assertEqual(before, rows[label]['old'])
            self.assertEqual(after, rows[label]['new'])
        self.assertEqual('2', self.tables['weapons'][0]['mindam'])

    def test_missing_dependencies_never_use_current_data(self):
        del self.tables['itemtypes']
        result = self.analyze()
        # Missing dependency tables no longer fail the whole revision; the entry
        # is reconstructed leniently from the historical tables only (no current
        # data fallback), with the raw type code preserved.
        self.assertEqual('available', result['status'])
        self.assertIn('entry', result)
        self.assertEqual('axe', result['entry']['type'])
        repo = HistoricalRepository({}, {})
        self.assertEqual([], repo.get_excel_table('weapons'))

    def test_alias_absence_and_duplicate_identity(self):
        self.assertEqual('available', self.analyze(identity='base:renamed', canonical=lambda _: 'base:renamed')['status'])
        self.assertEqual('absent', self.analyze(identity='base:missing')['status'])
        self.tables['weapons'].append(dict(self.tables['weapons'][0]))
        self.assertEqual('unavailable', self.analyze()['status'])

    def test_revision_markup_escapes_values(self):
        comparison = {'stat_rows': [{'label': 'Name', 'old': '<script>bad</script>', 'new': 'safe', 'status': 'changed'}], 'property_rows': []}
        html = WikiRenderer().render('history_revision.html', comparison=comparison, is_first=False, prev_date='2026-01-01', this_date='2026-02-02')
        self.assertNotIn('<script>', html)
        self.assertIn('Previous Revision · 2026-01-01', html)
        self.assertIn('BK At · 2026-02-02', html)

    def test_shared_set_bonuses_preserve_slots_and_input(self):
        class Resolver:
            def resolve_property(self, code, param, minimum, maximum):
                return {'code': code, 'param': param, 'resolved_text': f'{minimum}-{maximum} {code}'}
        entry = {'raw_row': {'set': 'Arctic'}, 'properties': []}
        sets = {'Arctic': {'PCode2a': 'dmg', 'PMin2a': '4', 'PMax2a': '8', 'FCode1': 'str', 'FMin1': '10'}}
        resolved = with_shared_set_bonuses(entry, sets, Resolver())
        self.assertEqual([], entry['properties'])
        self.assertEqual('shared-PCode2a', resolved['properties'][0]['code'])
        self.assertIn('Shared set bonus (2 pieces): 4-8 dmg', resolved['properties'][0]['resolved_text'])
        self.assertIn('full set', resolved['properties'][1]['resolved_text'])

    def test_unique_includes_historical_base_stats(self):
        self.tables['uniqueitems'] = [{'index': 'Unique', 'code': 'ax'}]
        entry = self.analyze(identity='unique:Unique')['entry']
        self.assertEqual(2, entry['history_base']['damage_min'])
        self.tables['weapons'][0].update(reqstr='95', gemsockets='4')
        entry = self.analyze(identity='unique:Unique')['entry']
        self.assertEqual(95, entry['history_base']['str_req'])
        self.assertEqual(4, entry['history_base']['sockets'])

    def test_availability_distinguishes_false_missing_and_absent(self):
        rows = {row['label']: row for row in availability_rows({'enabled': '0', 'rarity': '99'}, {'enabled': '1'})}
        self.assertEqual('No', rows['Enabled']['new'])
        self.assertEqual('Yes', rows['Enabled']['old'])
        self.assertEqual('Not specified', rows['Drop selection weight']['old'])
        self.assertEqual('99', rows['Drop selection weight']['new'])
        rows = availability_rows({}, {'spawnable': '1'}, current_present=False)
        self.assertEqual('Not present', rows[0]['new'])
        self.assertEqual('—', rows[1]['new'])

    def test_comparison_has_changes(self):
        self.assertFalse(comparison_has_changes({'stat_rows': [{'status': 'same'}], 'property_rows': [{'status': 'same'}]}))
        self.assertTrue(comparison_has_changes({'stat_rows': [{'status': 'same'}], 'property_rows': [{'status': 'changed'}]}))
        self.assertTrue(comparison_has_changes({'stat_rows': [{'status': 'added'}], 'property_rows': []}))
        self.assertFalse(comparison_has_changes({'stat_rows': [], 'property_rows': [{'status': 'separator'}]}))
        self.assertTrue(comparison_has_changes({}, availability=[{'status': 'changed'}]))
        self.assertFalse(comparison_has_changes({}, availability=[{'status': 'same'}]))


if __name__ == '__main__':
    unittest.main()
