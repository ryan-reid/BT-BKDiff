"""Deterministic BK item history from data blobs, never historical Python code.

No D2Repository fallback is used here: every dependency belongs to the snapshot.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import warnings
from pathlib import Path

VERSION = 10
UPSTREAM = 'https://github.com/BaronBeefStick/BKDiablo-Ascenstion'
PRIMARY = {'uniqueitems': ('unique', 'index'), 'setitems': ('set', 'index'),
           'runes': ('runeword', 'Name'), 'weapons': ('base', 'code'),
           'armor': ('base', 'code'), 'misc': ('base', 'code')}
KEYS = dict((table, key) for table, (_, key) in PRIMARY.items())
KEYS.update(itemtypes='Code', properties='code', itemstatcost='Stat', sets='name',
            gems='code', skills='skill')
TABLES = tuple(KEYS) + ('automagic', 'qualityitems')
ACTIVATION = {'disabled', 'enabled', 'spawnable', 'complete', 'rarity', 'firstLadderSeason',
              'lastLadderSeason', 'disallowCraftingInLadder', 'disallowCraftingInNonLadder'}
# Fields excluded from the item fingerprint: non-gameplay metadata plus values the
# comparison UI does not surface (show-level toggle, gamble cost, armor WSM, etc.).
COSMETIC = {'name', 'namestr', 'ItemType', 'index', 'Name', 'skill', 'code', 'Code', 'Stat',
            'version', 'compactsave', 'StorePage', 'UICategory', 'Transform', 'InvTrans',
            'invtransform', 'transform', 'SkipName', 'Nameable', 'spelldesc', 'spelldescstr',
            'spelldescstr2', 'spelldesccalc', 'skilldesc', 'uiRangeType',
            'ShowLevel', 'gamble cost', 'speed', 'hasinv', 'lvl', 'type2',
            'minstack', 'spawnstack'}
COSMETIC_PREFIX = ('*', 'inv', 'flp', 'chr', 'alternate', 'dropsfx', 'usesound', 'dropsound',
                   'desc', 'dgrp', 'ddam', 'dpos', 'dneg')
BASE_FIELDS = set(('type level levelreq reqstr reqdex mindam maxdam 2handmindam '
    '2handmaxdam minmisdam maxmisdam 2handed 1or2handed minac maxac block gemsockets '
    'durability nodurability magic lvl').split()) | {'magic lvl'}
TYPE_FIELDS = {'Equiv1', 'Equiv2', 'Class', 'StaffMods', 'MaxSockets1', 'MaxSockets2',
               'MaxSockets3', 'MaxSocketsLevelThreshold1', 'MaxSocketsLevelThreshold2',
               'MaxSocketsLevelThresholdOne', 'MaxSocketsLevelThresholdTwo',
               'RunewordCategory1', 'RunewordCategory2'}
QUALITY = {'weap': 'weapon', 'armo': 'armor', 'shld': 'shield', 'shie': 'shield',
           'ashd': 'shield', 'scep': 'scepter', 'wand': 'wand', 'staf': 'staff',
           'bow': 'bow', 'xbow': 'bow', 'boot': 'boots', 'glov': 'gloves', 'belt': 'belt'}
# `gemapplytype` is a numeric enum on base items selecting which gem-mod group applies.
GEM_APPLY_TYPE = {'0': 'weapon', '1': 'armor', '2': 'shield'}
# Skill-granting property codes whose `par` column holds a skill reference (id or
# name). Normalized to the stable numeric id so "431" and "Magic Conviction" compare
# equal without touching the skill's own behavior (which belongs to skills.txt history).
SKILL_PROPERTY_CODES = frozenset({'aura', 'oskill', 'skill', 'att-skill', 'hit-skill',
                                  'gethit-skill', 'kill-skill', 'death-skill', 'level-skill',
                                  'levelup-skill'})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def clean(row, fields=None):
    """Source values, excluding non-gameplay metadata and empty-column churn."""
    return {key: value for key, value in sorted(row.items()) if value and
            (key in fields if fields is not None else
             key not in COSMETIC and not key.lower().startswith(COSMETIC_PREFIX))}


def _has_damage(row):
    """True when a base item carries non-zero damage, i.e. the comparison UI treats it
    as a weapon and surfaces its WSM (`speed`)."""
    for key in ('mindam', 'maxdam', '2handmindam', '2handmaxdam', 'minmisdam', 'maxmisdam'):
        value = str(row.get(key, '')).strip()
        if value and value != '0':
            return True
    return False


def parse_table(data):
    text = data.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text), delimiter='\t', quoting=csv.QUOTE_NONE)
    if not reader.fieldnames or len(reader.fieldnames) < 2:
        raise ValueError('Unsupported table header')
    rows = []
    for row in reader:
        overflow = row.pop(None, [])
        if any(cell.strip() for cell in overflow):
            raise ValueError('Row has more nonempty cells than its header')
        rows.append({key.strip(): (value or '').strip() for key, value in row.items()})
    return rows


class Snapshot:
    """Current semantic analyzer over one complete, isolated data snapshot."""
    def __init__(self, tables, skill_id_by_name=None):
        self.tables = tables
        self.indexes = {}
        self.ambiguous = set()
        self.type_cache = {}
        for table, key in KEYS.items():
            if table not in tables:
                continue
            if tables[table] and key not in tables[table][0]:
                raise ValueError(f'Unsupported identity column: {table}/{key}')
            index = {}
            for row in tables[table]:
                identity = row.get(key, '')
                if not identity or identity.lower() in ('expansion', 'null'):
                    continue
                if identity in index:
                    self.ambiguous.add((table, identity))
                index[identity] = row
            self.indexes[table] = index
        if skill_id_by_name is None:
            skill_id_by_name = {}
            for name, row in self.indexes.get('skills', {}).items():
                s_id = row.get('*Id') or row.get('Id') or row.get('*ID') or row.get('ID')
                if s_id:
                    skill_id_by_name[name.strip().lower()] = str(s_id).strip()
        self.skill_id_by_name = skill_id_by_name

    def require(self, table, key):
        if table in ('properties', 'itemstatcost', 'skills') and table in self.indexes:
            key = next((candidate for candidate in self.indexes[table] if candidate.casefold() == key.casefold()), key)
        if (table, key) in self.ambiguous:
            raise ValueError(f'Duplicate identity: {table}/{key}')
        if table not in self.indexes or key not in self.indexes[table]:
            raise ValueError(f'Missing dependency: {table}/{key}')
        return self.indexes[table][key]

    def types(self, *codes):
        if codes in self.type_cache:
            return self.type_cache[codes]
        found = {}
        def visit(code):
            if not code or code in found:
                return
            row = self.require('itemtypes', code)
            found[code] = clean(row, TYPE_FIELDS)
            visit(row.get('Equiv1'))
            visit(row.get('Equiv2'))
        for code in codes:
            visit(code)
        self.type_cache[codes] = found
        return found

    def properties(self, row, result):
        # Property and stat definitions are shared table content, not item data: a
        # change to a property formula belongs to properties.txt history, not to every
        # item that references it. Only validate that referenced property/stat rows
        # exist so a missing dependency still records a coverage gap.
        for key, code in row.items():
            if not re.fullmatch(r'(?:prop\d+|aprop\d+[ab]|[PF]Code\d+[ab]?|T1Code\d+|mod\d+code|(?:weapon|helm|shield)Mod\d+Code)', key):
                continue
            if not code or code in ('xxx', '0'):
                continue
            code = code.lower()
            prop = self.require('properties', code)
            for stat_key, stat in prop.items():
                if re.fullmatch(r'stat\d+', stat_key) and stat:
                    self.require('itemstatcost', stat)
            # The item's skill reference, level and trigger chance live in its own
            # record. Changes inside the skill belong to skill history, not items.

    def base(self, row, result, prefix='Base stats', superior=True):
        fields = BASE_FIELDS | ({'auto prefix'} if superior else set())
        if _has_damage(row):
            fields = fields | {'speed'}
        result[f'{prefix}/{row["code"]}'] = clean(row, fields)
        types = self.types(row.get('type'), row.get('type2'))
        # Auto-prefix automagic and superior bonuses belong to the base item's own
        # history only. A unique/set item does not inherit them, so the dependency
        # path (superior=False) skips them rather than attributing a shared base-item
        # edit to every unique/set built on that base.
        if superior:
            group = row.get('auto prefix', '')
            if group and group != '0':
                if 'automagic' not in self.tables:
                    raise ValueError('Missing dependency: automagic')
                for auto in self.tables['automagic']:
                    included = {v for k, v in auto.items() if k.startswith('itype') and v}
                    excluded = {v for k, v in auto.items() if k.startswith('etype') and v}
                    if auto.get('group') == group and (not included or included.intersection(types)) and not excluded.intersection(types):
                        value = clean(auto)
                        result.setdefault('Automagic', []).append(value)
                        self.properties(auto, result)
            columns = {QUALITY[c] for c in types if c in QUALITY}
            if columns:
                if 'qualityitems' not in self.tables:
                    raise ValueError('Missing dependency: qualityitems')
                for quality in self.tables['qualityitems']:
                    if any(quality.get(c) == '1' for c in columns):
                        result.setdefault('Superior bonuses', []).append(clean(quality))
                        self.properties(quality, result)

    def _canonical_skill(self, reference):
        ref = str(reference).strip()
        if not ref or ref == '0':
            return ref
        if ref.isdigit():
            return ref
        return self.skill_id_by_name.get(ref.lower(), ref.lower())

    def _normalize_item(self, row):
        normalized = dict(row)
        for i in range(1, 13):
            prop = str(normalized.get(f'prop{i}', '')).strip().lower()
            par_key = f'par{i}'
            if prop in SKILL_PROPERTY_CODES and par_key in normalized:
                normalized[par_key] = self._canonical_skill(normalized[par_key])
        return normalized

    def state(self, table, row):
        self.require(table, row[KEYS[table]])
        item = clean(self._normalize_item(row))
        if 'gemapplytype' in item:
            item['gemapplytype'] = GEM_APPLY_TYPE.get(item['gemapplytype'], item['gemapplytype'])
        result = {'Item': item}
        if table in ('weapons', 'armor', 'misc'):
            self.base(row, result)
        else:
            self.properties(row, result)
            if table in ('uniqueitems', 'setitems'):
                code = row.get('code' if table == 'uniqueitems' else 'item', '')
                base = next((self.indexes.get(t, {}).get(code) for t in ('weapons', 'armor', 'misc') if code in self.indexes.get(t, {})), None)
                if base is None:
                    raise ValueError(f'Missing base: {code}')
                self.base(base, result, superior=False)
            if table == 'setitems' and row.get('set'):
                shared = self.require('sets', row['set'])
                result['Shared set bonus'] = clean(shared)
                self.properties(shared, result)
            if table == 'runes':
                included = {v for k, v in row.items() if re.fullmatch('itype[0-9]+', k) and v and v != 'xxx'}
                excluded = {v for k, v in row.items() if re.fullmatch('etype[0-9]+', k) and v and v != 'xxx'}
                self.types(*sorted(included | excluded))  # validate referenced types exist
                socket_count = sum(bool(row.get(f'Rune{i}', '') not in ('', 'xxx')) for i in range(1, 7))
                socket_groups = set()
                eligible = []
                for base_table in ('weapons', 'armor'):
                    if base_table not in self.indexes:
                        raise ValueError(f'Missing dependency: {base_table}')
                    for base_code, base in self.indexes[base_table].items():
                        chain = self.types(base.get('type'), base.get('type2'))
                        caps = [int(self.types(base.get('type')).get(base.get('type'), {}).get(f'MaxSockets{i}', '0') or 0) for i in range(1, 4)]
                        capacity = int(base.get('gemsockets', '0') or 0)
                        if max(caps):
                            capacity = min(capacity, max(caps))
                        if included.intersection(chain) and not excluded.intersection(chain) and capacity >= socket_count:
                            eligible.append(base_code)
                            socket_groups.add('weapon' if 'weap' in chain else 'shield' if 'shld' in chain else 'helm')
                result['Eligible bases'] = sorted(eligible)
                for key, code in row.items():
                    if re.fullmatch('Rune[1-6]', key) and code and code != 'xxx':
                        rune = {k: v for k, v in self.require('gems', code).items() if any(k.startswith(group + 'Mod') for group in socket_groups)}
                        result[f'Rune effects/{code}'] = clean(rune)
                        result[f'Rune requirements/{code}'] = clean(self.require('misc', code), {'levelreq'})
                        self.properties(rune, result)
        # Stable order, including identical rows and changes to row ordering.
        for key, value in result.items():
            if isinstance(value, list):
                result[key] = sorted(value, key=lambda v: json.dumps(v, sort_keys=True))
        return result


def differences(before, after):
    changes = []
    for source in sorted(before.keys() | after.keys()):
        old, new = before.get(source), after.get(source)
        if isinstance(old, dict) and isinstance(new, dict):
            for field in sorted(old.keys() | new.keys()):
                if old.get(field) != new.get(field):
                    changes.append({'source': source, 'field': field, 'before': old.get(field), 'after': new.get(field)})
        elif old != new:
            changes.append({'source': source, 'field': '', 'before': old, 'after': new})
    return changes


class HistoryCollector:
    def __init__(self, game_dir, cache_dir, config=None):
        self.game_dir = Path(game_dir).resolve()
        self.cache_dir = Path(cache_dir)
        self.config = config or {'aliases': {}, 'releases': []}

    def git(self, *args, binary=False):
        output = subprocess.check_output(['git', '-C', str(getattr(self, 'git_root', self.game_dir)), *args], stderr=subprocess.PIPE)
        return output if binary else output.decode('utf-8').strip()

    def canonical(self, identity):
        seen = set()
        while identity in self.config.get('aliases', {}):
            if identity in seen:
                raise ValueError('History identity alias cycle')
            seen.add(identity)
            identity = self.config['aliases'][identity]
        return identity

    def cached(self, name, build):
        path = self.cache_dir / name
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            result = build()
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(result, ensure_ascii=True, sort_keys=True), encoding='utf-8')
            temporary.replace(path)
            return result

    def _skill_id_by_name(self, revision):
        """Build a stable skill-name -> id map from the tip snapshot so skill
        references (id vs name) canonicalize consistently across all history."""
        mapping = {}
        try:
            for line in self.git('ls-tree', '-r', revision, '--', self.excel_path).splitlines():
                path = line.split('\t', 1)[1]
                if Path(path).stem != 'skills':
                    continue
                blob = line.split()[2]
                rows = self.cached(f'table-{VERSION}-{blob}.json',
                                   lambda b=blob: parse_table(self.git('cat-file', 'blob', b, binary=True)))
                for row in rows:
                    name = str(row.get('skill', '')).strip().lower()
                    s_id = row.get('*Id') or row.get('Id') or row.get('*ID') or row.get('ID')
                    if name and s_id:
                        mapping[name] = str(s_id).strip()
                break
        except (ValueError, subprocess.CalledProcessError):
            pass
        return mapping

    def collect(self):
        revision = None
        try:
            root = Path(self.git('rev-parse', '--show-toplevel')).resolve()
            # Avoid treating a plain data directory in the parent wiki repository as BK history.
            if root == Path(__file__).resolve().parents[3]:
                raise ValueError('Game data is not a separate Git repository')
            self.git_root = root
            revision = self.git('rev-parse', 'HEAD')
            if self.git('rev-parse', '--is-shallow-repository') == 'true':
                raise ValueError('BK history is shallow; fetch complete history')
            prefix = self.game_dir.relative_to(root).as_posix()
            if prefix == '.':
                prefix = ''
            self.excel_path = '/'.join(p for p in (prefix, 'data/global/excel') if p)
            if self.git('status', '--porcelain', '--untracked-files=all', '--', self.excel_path):
                raise ValueError('BK data has local edits; commit history cannot describe those edits')
            analyzer = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            for alias in self.config.get('aliases', {}):
                target = self.canonical(alias)
                if alias.split(':', 1)[0] != target.split(':', 1)[0]:
                    raise ValueError('Aliases must stay within the same item family')
            key = digest([VERSION, analyzer, revision, self.excel_path, self.config])
            result = self.cached(f'history-{key}.json', lambda: self.scan(revision))
        except (OSError, ValueError, subprocess.CalledProcessError, UnicodeError) as exc:
            result = {'schema_version': VERSION, 'source_revision': revision, 'coverage': 'unavailable',
                      'gaps': [{'reason': str(exc)}], 'items': {}}
        if result['coverage'] != 'complete':
            warnings.warn(f'BK item history {result["coverage"]}: {len(result["gaps"])} coverage gaps', stacklevel=2)
        return result

    def scan(self, revision):
        commits = [line.split('\t', 1) for line in self.git('log', '--first-parent', '--reverse', '--format=%H%x09%cI', revision).splitlines()]
        commit_ids = [sha for sha, _ in commits]
        releases = {}
        for release in self.config.get('releases', []):
            mapped = release.get('commits', [])
            if 'first' in release or 'last' in release:
                start, end = commit_ids.index(release['first']), commit_ids.index(release['last'])
                if start > end:
                    raise ValueError('Release range is reversed')
                mapped = mapped + commit_ids[start:end + 1]
            for sha in mapped:
                if sha not in commit_ids or sha in releases:
                    raise ValueError('Release mapping is unknown or overlapping')
                releases[sha] = release['label']
        histories, previous, seen_tables, gaps = {}, {}, set(), []
        interrupted = set()
        global_skill_id_by_name = self._skill_id_by_name(revision)
        for sha, timestamp in commits:
            event_base = {'commit': sha, 'short_commit': sha[:7], 'timestamp': timestamp,
                          'date': timestamp[:10], 'url': f'{UPSTREAM}/commit/{sha}',
                          'release': releases.get(sha)}
            tables = {}
            try:
                entries = self.git('ls-tree', '-r', sha, '--', self.excel_path).splitlines()
                blobs = {Path(line.split('\t', 1)[1]).stem: line.split()[2]
                         for line in entries if Path(line.split('\t', 1)[1]).stem in TABLES}
                for table, blob in blobs.items():
                    tables[table] = self.cached(f'table-{VERSION}-{blob}.json', lambda b=blob: parse_table(self.git('cat-file', 'blob', b, binary=True)))
                snapshot = Snapshot(tables, global_skill_id_by_name)
            except (ValueError, UnicodeError) as exc:
                gaps.append(dict(event_base, reason=str(exc)))
                interrupted.update(PRIMARY)
                continue
            for table, (family, _) in PRIMARY.items():
                if table not in snapshot.indexes:
                    if table in seen_tables:
                        gaps.append(dict(event_base, reason=f'Missing table: {table}'))
                        interrupted.add(table)
                    continue
                first_table = table not in seen_tables
                seen_tables.add(table)
                current = {}
                for raw_key, row in snapshot.indexes[table].items():
                    identity = self.canonical(f'{family}:{raw_key}')
                    if identity in current:
                        raise ValueError(f'Alias collision: {identity}')
                    current[identity] = row
                old = previous.get(table, {})
                next_states = {}
                for identity in sorted(old.keys() | current.keys()):
                    record = histories.setdefault(identity, {'id': identity, 'coverage': 'complete', 'first': None,
                                                            'last_change': None, 'events': [], 'gaps': []})
                    if table in interrupted:
                        record['coverage'] = 'incomplete'
                        record['gaps'].append(dict(event_base, reason='A preceding snapshot or source table could not be read'))
                    # Presence is evidence even if a shared gameplay dependency is missing.
                    # A duplicate primary identity, however, cannot identify an individual item.
                    first_seen_now = False
                    if record['first'] is None and identity in current and (table, current[identity][KEYS[table]]) not in snapshot.ambiguous:
                        kind = 'first_recorded' if first_table else 'recorded_after_gap' if table in interrupted or identity in old else 'added'
                        event = dict(event_base, kind=kind, changes=[], causes=[])
                        record['first'] = event
                        record['events'].append(event)
                        first_seen_now = True
                    try:
                        state = snapshot.state(table, current[identity]) if identity in current else None
                    except ValueError as exc:
                        gap = dict(event_base, reason=str(exc), item_id=identity)
                        gaps.append(gap)
                        record['coverage'] = 'incomplete'
                        if not record['gaps'] or record['gaps'][-1]['reason'] != gap['reason']:
                            record['gaps'].append(gap)
                        next_states[identity] = {'state': None, 'gap': True}
                        continue
                    before = old.get(identity)
                    interrupted_item = table in interrupted or (before and before.get('gap'))
                    events = []
                    if first_seen_now:
                        pass
                    elif interrupted_item:
                        if state is not None:
                            events.append(('recorded_after_gap', []))
                    elif state is None and before and before['state'] is not None:
                        events.append(('removed', []))
                    elif state is not None and (before is None or before['state'] is None):
                        kind = 'first_recorded' if first_table else 'reappeared' if record['first'] else 'added'
                        events.append((kind, []))
                    elif state is not None:
                        changes = differences(before['state'], state)
                        activation = [c for c in changes if c['source'] == 'Item' and c['field'] in ACTIVATION]
                        gameplay = [c for c in changes if c not in activation]
                        if activation:
                            events.append(('activation_changed', activation))
                        if gameplay:
                            events.append(('changed', gameplay))
                    for kind, changes in events:
                        causes = sorted({c['source'].split('/')[0] for c in changes})
                        event = dict(event_base, kind=kind, changes=changes, causes=causes)
                        record['events'].append(event)
                        if record['first'] is None and state is not None:
                            record['first'] = event
                        if kind in ('changed', 'activation_changed', 'removed', 'reappeared'):
                            record['last_change'] = event
                    record['present'] = state is not None
                    next_states[identity] = {'state': state, 'gap': False}
                previous[table] = next_states
                interrupted.discard(table)
        if not histories:
            raise ValueError('No supported item tables found in BK history')
        for table in interrupted:
            for identity in previous.get(table, {}):
                histories[identity]['coverage'] = 'incomplete'
                histories[identity]['gaps'].append(dict(event_base, reason='History ends with an unreadable snapshot or missing source table'))
        return {'schema_version': VERSION, 'source_revision': revision,
                'coverage': 'incomplete' if gaps else 'complete', 'gaps': gaps, 'items': histories}


def item_history(artifact, family, row, aliases=None):
    key = row.get('code' if family == 'base' else 'Name' if family == 'runeword' else 'index', '')
    identity = f'{family}:{key}'
    seen = set()
    while identity in (aliases or {}) and identity not in seen:
        seen.add(identity)
        identity = aliases[identity]
    return artifact['items'].get(identity) or {'id': identity, 'coverage': 'unavailable', 'events': []}
