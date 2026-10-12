"""Render historical data through today's analyzers, with no gameplay fallback."""
from collections import defaultdict
from pathlib import Path
import json
import os

from d2lib.repository import D2Repository
from d2lib.services.items import ItemAnalyzerService, BaseItemAnalyzerService
from d2lib.services.misc import MiscAnalyzerService
from d2lib.services.resolver import PropertyResolverService
from d2lib.wiki.comparison import item_comparison_context, base_item_comparison_context, gem_rune_comparison_context, runeword_compare_rows
from d2lib.wiki.history import PRIMARY, TABLES, VERSION, Snapshot, digest, parse_table, item_history
from d2lib.wiki.item_helpers import item_identity, item_title
from d2lib.wiki.renderers import WikiRenderer


class HistoricalRepository:
    def __init__(self, tables, strings):
        self.tables = tables
        self.strings = strings

    def get_excel_table(self, name):
        return self.tables.get(name, [])

    # Current localization is presentation only; never read current gameplay data.
    get_string = D2Repository.get_string


def with_shared_set_bonuses(entry, sets, resolver):
    """Keep shared bonuses visible when they are the reason for a revision."""
    row = sets.get(entry.get('raw_row', {}).get('set'), {})
    props = list(entry.get('properties', []))
    slots = [(f'PCode{count}{suffix}', f'PParam{count}{suffix}', f'PMin{count}{suffix}', f'PMax{count}{suffix}', f'{count} pieces')
             for count in range(2, 6) for suffix in ('a', 'b')]
    slots += [(f'FCode{i}', f'FParam{i}', f'FMin{i}', f'FMax{i}', 'full set') for i in range(1, 9)]
    for code, param, minimum, maximum, label in slots:
        if row.get(code):
            prop = resolver.resolve_property(row[code], row.get(param, ''), row.get(minimum, ''), row.get(maximum, ''))
            props.append(dict(prop, code=f'shared-{code}', resolved_text=f'Shared set bonus ({label}): {prop["resolved_text"]}'))
    return dict(entry, properties=props)


def availability_rows(current, baseline, current_present=True, baseline_present=True):
    rows = []
    def add(label, old, new):
        rows.append(dict(label=label, old=old, new=new,
                         status='same' if old == new else 'changed' if old and new else 'added' if new else 'removed'))
    add('Source record', 'Present' if baseline_present else 'Not present', 'Present' if current_present else 'Not present')
    fields = [('enabled', 'Enabled'), ('disabled', 'Disabled'), ('spawnable', 'Spawnable'),
              ('complete', 'Runeword active'), ('rarity', 'Drop selection weight'),
              ('firstLadderSeason', 'First ladder season'), ('lastLadderSeason', 'Last ladder season'),
              ('disallowCraftingInLadder', 'Crafting blocked in ladder'),
              ('disallowCraftingInNonLadder', 'Crafting blocked outside ladder')]
    for field, label in fields:
        if not current.get(field, '') and not baseline.get(field, ''):
            continue
        def value(row, present):
            if not present:
                return '—'
            raw = row.get(field, '')
            if not raw:
                return 'Not specified'
            if field in ('enabled', 'disabled', 'spawnable', 'complete', 'disallowCraftingInLadder', 'disallowCraftingInNonLadder'):
                return {'1': 'Yes', '0': 'No'}.get(raw, raw)
            return raw
        add(label, value(baseline, baseline_present), value(current, current_present))
    return rows


def compare_entries(entry, old_entry, family):
    if family == 'misc':
        return gem_rune_comparison_context(entry, old_entry)
    if family == 'base':
        return base_item_comparison_context(entry, old_entry)
    comparison = item_comparison_context(entry, family, old_entry)
    if family == 'runeword':
        comparison['property_rows'] = runeword_compare_rows(entry, old_entry)
    return comparison


def comparison_has_changes(comparison, base_comparison=None, availability=None):
    def _rows(rows):
        return any(row.get('status') not in ('same', 'separator') for row in rows)
    if comparison:
        for group in ('stat_rows', 'property_rows'):
            if _rows(comparison.get(group, [])):
                return True
    if base_comparison and _rows(base_comparison.get('stat_rows', [])):
        return True
    if availability and _rows(availability):
        return True
    return False


def analyze_revision(tables, strings, identity, canonical, context=None, property_groups=None):
    matches = [(table, row) for table, (family, key) in PRIMARY.items()
               for row in tables.get(table, [])
               if row.get(key) and canonical(f'{family}:{row[key]}') == identity]
    if not matches:
        return {'status': 'absent', 'reason': 'This item is not present in this source revision.'}
    if len(matches) != 1:
        return {'status': 'unavailable', 'reason': 'This revision contains duplicate item identities.'}
    table, row = matches[0]
    try:
        if context is None:
            repo = HistoricalRepository(tables, strings)
            resolver = PropertyResolverService(repo, property_groups)
            context = (Snapshot(tables), ItemAnalyzerService(repo, resolver), BaseItemAnalyzerService(repo, resolver), MiscAnalyzerService(repo, resolver))
        snapshot, service, base_service, misc_service = context
        try:
            snapshot.state(table, row)
        except (ValueError, KeyError, TypeError, IndexError):
            # Dependency validation is advisory for rendering: the entry analysis
            # below is already lenient (unknown properties resolve to "Unknown
            # property", missing bases fall back to the raw code). A commit whose
            # dependency tables are temporarily inconsistent should still render.
            pass
        if table == 'misc':
            entry = misc_service.analyze_row(row)
            if entry is None:
                return {'status': 'unavailable', 'reason': 'This misc item is not surfaced in the comparison.'}
        elif identity.startswith('base:'):
            entry = base_service._analyze_item(row, '')
        else:
            method = {'uniqueitems': service.analyze_unique, 'setitems': service.analyze_set_item,
                      'runes': service.analyze_runeword}[table]
            entry = method(row)
            if table == 'setitems':
                entry = with_shared_set_bonuses(entry, service.sets, service.resolver)
            if table in ('uniqueitems', 'setitems'):
                code = row.get('code' if table == 'uniqueitems' else 'item')
                base = service.weapons.get(code) or service.armor.get(code) or service.misc.get(code)
                if base:
                    entry['history_base'] = base_service._analyze_item(base, '')
        return {'status': 'available', 'entry': entry, 'source_row': row}
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        return {'status': 'unavailable', 'reason': f'Stats cannot be reconstructed for this revision: {exc}'}


def write_history_comparisons(collector, artifact, repo, items, old_index, bases, old_bases, misc_groups, retail_misc, writer, old_label, baseline_repo):
    if not artifact.get('items'):
        return
    property_groups = repo.load_tsv(os.path.join(repo.repo_root, "data", "propertygroups.txt"))
    targets = {}
    baseline_sets = {row['name']: row for row in baseline_repo.get_excel_table('sets')}
    baseline_resolver = PropertyResolverService(baseline_repo, property_groups)
    baseline_base_service = BaseItemAnalyzerService(baseline_repo, baseline_resolver)
    baseline_base_rows = {row['code']: row for table in ('weapons', 'armor', 'misc')
                          for row in baseline_repo.get_excel_table(table) if row.get('code')}
    for family, entries in items.items():
        for entry in entries:
            record = entry['history']
            if record.get('events'):
                baseline = old_index.get(family, {}).get(item_identity(entry, family))
                if baseline and family == 'set':
                    baseline = with_shared_set_bonuses(baseline, baseline_sets, baseline_resolver)
                if baseline and family in ('unique', 'set'):
                    row = baseline.get('raw_row', {})
                    base = baseline_base_rows.get(row.get('code' if family == 'unique' else 'item'))
                    if base:
                        baseline = dict(baseline, history_base=baseline_base_service._analyze_item(base, ''))
                targets[record['id']] = (record, family, item_title(entry, family), baseline)
    for group in bases:
        for entry in group['members']:
            record = item_history(artifact, 'base', entry, collector.config.get('aliases'))
            if record.get('events'):
                targets[record['id']] = (record, 'base', entry['name'], old_bases.get(entry['code']))
    for group in misc_groups:
        for entry in group['members']:
            record = entry.get('history') or item_history(artifact, 'base', entry, collector.config.get('aliases'))
            if record.get('events'):
                targets[record['id']] = (record, 'misc', entry['name'], retail_misc.get(entry['code']))

    # Include each change, gap, and the exact build revision, coalescing same-commit events.
    requests = defaultdict(set)
    revisions = {}
    for identity, (record, _, _, _) in targets.items():
        by_commit = {}
        for event in record['events'] + record.get('gaps', []):
            sha = event['commit']
            point = by_commit.setdefault(sha, {k: event.get(k) for k in ('commit', 'short_commit', 'date', 'timestamp', 'url', 'release')})
            point.setdefault('kinds', [])
            kind = event.get('kind', 'source_gap')
            if kind not in point['kinds']:
                point['kinds'].append(kind)
        # Commit traversal order, not committer timestamps (which can move backwards).
        revisions[identity] = by_commit
        for sha in by_commit:
            requests[sha].add(identity)

    order = collector.git('rev-list', '--first-parent', artifact['source_revision']).splitlines()
    source_files = [Path(__file__), Path(__file__).with_name('history.py')]
    source_files += list(Path(__file__).parents[1].joinpath('services').glob('*.py'))
    analyzer_version = digest([p.read_text(encoding='utf-8') for p in sorted(source_files)])
    strings_version = digest(repo.strings)
    rendered = defaultdict(list)
    renderer = WikiRenderer()
    # Analyze every requested commit first so consecutive revisions can be diffed.
    analyzed_by_sha = {}
    for sha in order:
        if sha not in requests:
            continue
        identities = sorted(requests[sha])
        cache_key = digest([sha, identities, analyzer_version, strings_version, collector.config])
        def build():
            tables = {}
            for line in collector.git('ls-tree', '-r', sha, '--', collector.excel_path).splitlines():
                name = Path(line.split('\t', 1)[1]).stem
                if name in TABLES or name == 'skilldesc':
                    blob = line.split()[2]
                    tables[name] = collector.cached(f'table-{VERSION}-{blob}.json',
                        lambda b=blob: parse_table(collector.git('cat-file', 'blob', b, binary=True)))
            historical_repo = HistoricalRepository(tables, repo.strings)
            resolver = PropertyResolverService(historical_repo, property_groups)
            context = (Snapshot(tables), ItemAnalyzerService(historical_repo, resolver),
                       BaseItemAnalyzerService(historical_repo, resolver), MiscAnalyzerService(historical_repo, resolver))
            return {identity: analyze_revision(tables, repo.strings, identity, collector.canonical, context) for identity in identities}
        try:
            analyzed_by_sha[sha] = collector.cached(f'presentation-{cache_key}.json', build)
        except (ValueError, UnicodeError) as exc:
            analyzed_by_sha[sha] = {identity: {'status': 'unavailable', 'reason': str(exc)} for identity in identities}

    for identity, (record, family, title, _) in targets.items():
        # `order` is newest → oldest; walk it backwards to get oldest → newest.
        chronological = [sha for sha in reversed(order) if sha in revisions[identity]]
        points = []
        prev_available = None
        prev_available_sha = None
        for sha in chronological:
            result = analyzed_by_sha.get(sha, {}).get(identity, {'status': 'unavailable', 'reason': 'Not analyzed.'})
            comparison = None
            base_comparison = None
            availability = []
            is_first = False
            this_date = revisions[identity][sha].get('date', '')
            prev_date = ''
            if result['status'] == 'available':
                entry = result['entry']
                if prev_available is None:
                    is_first = True
                    comparison = compare_entries(entry, {}, family)
                else:
                    prev_entry = prev_available['entry']
                    prev_date = revisions[identity][prev_available_sha].get('date', '')
                    comparison = compare_entries(entry, prev_entry, family)
                    if entry.get('history_base') and prev_entry.get('history_base'):
                        base_comparison = base_item_comparison_context(entry['history_base'], prev_entry['history_base'])
                    availability = availability_rows(result['source_row'], prev_available['source_row'], current_present=True, baseline_present=True)
                    if not comparison_has_changes(comparison, base_comparison, availability):
                        continue
                prev_available = result
                prev_available_sha = sha
            point = dict(revisions[identity][sha])
            point['html'] = renderer.render('history_revision.html', comparison=comparison,
                base_comparison=base_comparison, availability=availability,
                reason=result.get('reason'), is_first=is_first, this_date=this_date, prev_date=prev_date)
            point['status'] = result['status']
            points.append(point)
        rendered[identity] = points  # oldest → newest

    for identity, (record, family, title, _) in targets.items():
        path = f'data/item-revisions/{digest(identity)[:24]}.json'
        record['revisions_path'] = path
        writer.write_text(path, json.dumps(dict(title=title, family=family, old_label=old_label,
            revisions=rendered[identity]), ensure_ascii=True))
