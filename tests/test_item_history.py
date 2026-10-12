import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d2lib.wiki.history import HistoryCollector, Snapshot, differences, parse_table
from d2lib.wiki.renderers import WikiRenderer


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.game = self.root / 'game'
        self.excel = self.game / 'data/global/excel'
        self.excel.mkdir(parents=True)
        self.cache = Path(self.temp.name) / 'cache'
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'History test')
        self.git('config', 'user.email', 'history@example.test')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.hooksPath', str(Path(self.temp.name) / 'no-hooks'))
        self.tables = {
            'weapons': [{'code': 'mac', 'name': 'Mace', 'type': 'mace', 'mindam': '2', 'maxdam': '6', 'gemsockets': '3'}],
            'armor': [], 'misc': [{'code': 'r01', 'type': 'rune', 'levelreq': '10'}],
            'itemtypes': [{'Code': 'mace', 'Equiv1': 'weap'}, {'Code': 'weap'}, {'Code': 'rune'}],
            'uniqueitems': [{'index': 'Unique', 'code': 'mac', 'spawnable': '1', 'prop1': 'dmg', 'min1': '10', 'max1': '20'}],
            'setitems': [{'index': 'Piece', 'item': 'mac', 'set': 'Set'}],
            'sets': [{'name': 'Set', 'PCode2a': 'dmg', 'PMin2a': '4'}],
            'runes': [{'Name': 'Runeword1', '*Rune Name': 'Word', 'itype1': 'mace', 'Rune1': 'r01', 'complete': '1'}],
            'gems': [{'code': 'r01', 'weaponMod1Code': 'dmg', 'weaponMod1Min': '1'}],
            'properties': [{'code': 'dmg', 'stat1': 'damage', 'func1': '1'}],
            'itemstatcost': [{'Stat': 'damage', 'Save Bits': '8'}],
            'automagic': [], 'qualityitems': [], 'skills': [],
        }
        self.commit('Initial data')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.PIPE).decode().strip()

    def commit(self, message):
        for table, rows in self.tables.items():
            fields = sorted({k for r in rows for k in r}) or ['name', 'empty']
            with (self.excel / f'{table}.txt').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fields, delimiter='\t', quoting=csv.QUOTE_NONE)
                writer.writeheader()
                writer.writerows(rows)
        self.git('add', '.')
        self.git('commit', '-qm', message, '--allow-empty')
        return self.git('rev-parse', 'HEAD')

    def collect(self, config=None, cache=None):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            return HistoryCollector(self.game, cache or self.cache, config).collect()

    def test_first_added_removed_reappeared_and_activation(self):
        self.tables['uniqueitems'].append({'index': 'New', 'code': 'mac', 'spawnable': '0'})
        added = self.commit('New entry')
        self.tables['uniqueitems'][1]['spawnable'] = '1'
        self.commit('Enable')
        row = self.tables['uniqueitems'].pop()
        self.commit('Remove')
        self.tables['uniqueitems'].append(row)
        self.commit('Return')
        result = self.collect()
        self.assertEqual('complete', result['coverage'])
        self.assertEqual('first_recorded', result['items']['unique:Unique']['first']['kind'])
        record = result['items']['unique:New']
        self.assertEqual(added, record['first']['commit'])
        self.assertEqual(['added', 'activation_changed', 'removed', 'reappeared'], [e['kind'] for e in record['events']])

    def test_shared_dependencies_and_independent_damage_modes(self):
        self.tables['weapons'][0].update(mindam='5', minmisdam='8', maxmisdam='12', **{'2handmindam': '20', '2handmaxdam': '30'})
        damage_commit = self.commit('Base damage')
        self.tables['sets'][0]['PMin2a'] = '9'
        set_commit = self.commit('Set bonus')
        self.tables['gems'][0]['weaponMod1Min'] = '3'
        rune_commit = self.commit('Rune effect')
        self.tables['properties'][0]['func1'] = '2'
        prop_commit = self.commit('Shared property')
        result = self.collect()['items']
        unique_events = result['unique:Unique']['events']
        fields = {c['field'] for e in unique_events if e['commit'] == damage_commit for c in e['changes']}
        self.assertTrue({'mindam', 'minmisdam', '2handmindam'}.issubset(fields))
        self.assertIn(set_commit, [e['commit'] for e in result['set:Piece']['events']])
        self.assertNotIn(set_commit, [e['commit'] for e in unique_events])
        self.assertIn(rune_commit, [e['commit'] for e in result['runeword:Runeword1']['events']])
        # Property/stat definitions are shared table content, not item data: a
        # properties.txt edit no longer surfaces as an item change.
        self.assertNotIn(prop_commit, [e['commit'] for e in unique_events])
        self.assertEqual(damage_commit, result['unique:Unique']['last_change']['commit'])

    def test_cosmetic_reordering_whitespace_and_unrelated_changes_ignored(self):
        self.tables['weapons'][0].update(name='Different name', invfile='different-icon')
        self.tables['uniqueitems'][0]['*comment'] = 'Comment only'
        self.tables['uniqueitems'][0]['min1'] = ' 10 '
        self.tables['properties'].append({'code': 'unrelated', 'stat1': 'unused'})
        self.tables['itemtypes'].reverse()
        self.commit('Cosmetics')
        record = self.collect()['items']['unique:Unique']
        self.assertEqual(1, len(record['events']))
        self.assertIsNone(record['last_change'])

    def test_alias_continuity_and_duplicate_gap(self):
        self.tables['uniqueitems'][0]['index'] = 'Renamed'
        self.commit('Rename')
        config = {'aliases': {'unique:Unique': 'unique:Renamed'}, 'releases': []}
        result = self.collect(config)
        self.assertEqual(1, len(result['items']['unique:Renamed']['events']))
        self.tables['uniqueitems'].append(dict(self.tables['uniqueitems'][0]))
        self.commit('Duplicate')
        result = self.collect(config)
        self.assertEqual('incomplete', result['items']['unique:Renamed']['coverage'])
        self.assertTrue(any('Duplicate identity' in g['reason'] for g in result['gaps']))

    def test_automagic_superior_and_eligibility_dependencies(self):
        self.tables['weapons'][0]['auto prefix'] = '7'
        self.tables['automagic'] = [{'Name': 'Auto', 'group': '7', 'itype1': 'mace', 'mod1code': 'dmg', 'mod1min': '2'}]
        self.tables['qualityitems'] = [{'name': 'Superior', 'weapon': '1', 'mod1code': 'dmg', 'mod1min': '3'}]
        self.commit('Initial shared bonuses')
        self.tables['automagic'][0]['mod1min'] = '4'
        auto = self.commit('Automagic')
        self.tables['qualityitems'][0]['mod1min'] = '5'
        quality = self.commit('Superior')
        self.tables['weapons'][0]['gemsockets'] = '0'
        eligibility = self.commit('Socket capacity')
        result = self.collect()['items']
        events = result['unique:Unique']['events']
        # Auto-prefix automagic applies to magic/rare drops of a base, not to a
        # unique/set built on it, so it no longer surfaces as a unique-item change.
        self.assertNotIn(auto, [e['commit'] for e in events])
        self.assertIn(auto, [e['commit'] for e in result['base:mac']['events']])
        self.assertNotIn(quality, [e['commit'] for e in events])
        self.assertIn(quality, [e['commit'] for e in result['base:mac']['events']])
        word = result['runeword:Runeword1']['last_change']
        self.assertEqual(eligibility, word['commit'])
        self.assertIn('Eligible bases', word['causes'])

    def test_unrelated_rune_socket_effects_do_not_touch_weapon_word(self):
        self.tables['gems'][0]['shieldMod1Code'] = 'dmg'
        self.tables['gems'][0]['shieldMod1Min'] = '99'
        self.commit('Shield-only rune change')
        self.assertEqual(1, len(self.collect()['items']['runeword:Runeword1']['events']))

    def test_skill_behavior_is_not_item_history_but_grants_and_availability_are(self):
        self.tables['properties'].append({'code': 'oskill'})
        self.tables['uniqueitems'][0].update(prop2='oskill', par2='Test Skill', min2='1', max2='1')
        self.tables['skills'] = [{'skill': 'Test Skill', 'Id': '1', 'Param1': '10'}]
        self.commit('Grant skill')
        self.tables['skills'][0]['Param1'] = '99'
        behavior = self.commit('Skill behavior only')
        self.tables['skills'] = []
        missing = self.commit('No skill behavior data')
        self.tables['uniqueitems'][0]['max2'] = '2'
        grant = self.commit('Grant more skill levels')
        self.tables['uniqueitems'][0]['rarity'] = '99'
        availability = self.commit('Drop weighting')
        record = self.collect()['items']['unique:Unique']
        commits = [event['commit'] for event in record['events']]
        self.assertNotIn(behavior, commits)
        self.assertNotIn(missing, commits)
        self.assertIn(grant, commits)
        self.assertEqual('complete', record['coverage'])
        self.assertEqual(availability, record['last_change']['commit'])
        self.assertEqual('activation_changed', record['last_change']['kind'])

    def test_missing_dependency_and_table_boundary(self):
        del self.tables['runes']
        (self.excel / 'runes.txt').unlink()
        self.commit('Missing table')
        self.tables['runes'] = [{'Name': 'NewWord', 'itype1': 'mace'}]
        self.commit('Table restored')
        self.tables['uniqueitems'][0]['code'] = 'missing'
        self.commit('Unresolvable base')
        result = self.collect()
        self.assertEqual('recorded_after_gap', result['items']['runeword:NewWord']['first']['kind'])
        self.assertEqual('incomplete', result['items']['unique:Unique']['coverage'])

    def test_late_table_initial_contents_are_first_recorded(self):
        # Introduce an armor table for the first time, not merely an empty existing one.
        self.git('checkout', '--orphan', 'late')
        self.git('rm', '-rf', '.')
        (self.root / 'README').write_text('Repository predates game data')
        self.git('add', '.')
        self.git('commit', '-qm', 'Before tables')
        self.excel.mkdir(parents=True, exist_ok=True)
        self.commit('Initial table import')
        result = self.collect()
        self.assertEqual('first_recorded', result['items']['base:mac']['first']['kind'])

    def test_presence_date_does_not_wait_for_shared_dependencies(self):
        self.tables['uniqueitems'].append({'index': 'Incomplete', 'code': 'not-yet-present'})
        added = self.commit('Item row exists')
        self.tables['weapons'].append({'code': 'not-yet-present', 'type': 'mace'})
        self.commit('Dependency arrives')
        record = self.collect()['items']['unique:Incomplete']
        self.assertEqual(added, record['first']['commit'])
        self.assertEqual('added', record['first']['kind'])
        self.assertEqual('incomplete', record['coverage'])

    def test_missing_table_at_tip_marks_existing_history_incomplete(self):
        del self.tables['runes']
        (self.excel / 'runes.txt').unlink()
        self.commit('Missing at tip')
        record = self.collect()['items']['runeword:Runeword1']
        self.assertEqual('incomplete', record['coverage'])
        self.assertIn('ends with', record['gaps'][-1]['reason'])

    def test_cache_release_and_divergent_history(self):
        first = self.git('rev-parse', 'HEAD')
        self.tables['weapons'][0]['mindam'] = '7'
        second = self.commit('Change')
        config = {'aliases': {}, 'releases': [{'label': 'Verified v1', 'first': first, 'last': second}]}
        cold = self.collect(config)
        self.assertEqual(cold, self.collect(config))
        self.assertEqual('Verified v1', cold['items']['base:mac']['last_change']['release'])
        self.git('checkout', '-qb', 'divergent', first)
        self.tables['weapons'][0]['mindam'] = '9'
        different = self.commit('Different branch')
        result = self.collect()
        self.assertEqual(different, result['source_revision'])
        self.assertNotIn(second, [e['commit'] for e in result['items']['base:mac']['events']])

    def test_first_parent_merge_uses_merge_commit(self):
        self.git('checkout', '-qb', 'feature')
        self.tables['weapons'][0]['mindam'] = '9'
        feature = self.commit('Feature change')
        self.git('checkout', 'main')
        self.git('merge', '--no-ff', 'feature', '-m', 'Merge feature')
        result = self.collect()['items']['base:mac']
        self.assertEqual(self.git('rev-parse', 'HEAD'), result['last_change']['commit'])
        self.assertNotIn(feature, [e['commit'] for e in result['events']])

    def test_shallow_and_dirty_are_unavailable(self):
        clone = Path(self.temp.name) / 'clone'
        subprocess.check_output(['git', 'clone', '--depth=1', self.root.as_uri(), str(clone)], stderr=subprocess.PIPE)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            result = HistoryCollector(clone / 'game', self.cache).collect()
        self.assertEqual('unavailable', result['coverage'])
        (self.excel / 'weapons.txt').write_text('local edit')
        self.assertEqual('unavailable', self.collect()['coverage'])

    def test_html_is_escaped_and_works_without_scripts(self):
        record = self.collect()['items']['unique:Unique']
        record['events'][0]['release'] = '<script>bad()</script>'
        html = WikiRenderer().environment.get_template('history.html').module.item_history(record)
        self.assertIn('<details>', html)
        self.assertIn('Last changed:', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)
        self.assertIn('https://github.com/BaronBeefStick/BKDiablo-Ascenstion/commit/', html)


if __name__ == '__main__':
    unittest.main()
