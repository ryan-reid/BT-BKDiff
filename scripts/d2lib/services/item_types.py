"""Loot-filter browsing categories and code-based runeword eligibility."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Sequence, Set, Union

from d2lib.repository import resolve_localized_string

LOOT_GROUP_UI_CODES: Dict[str, tuple[str, ...]] = {
    "armor": ("helms", "circl", "armor", "shlds", "glove", "boots", "belts", "barbh", "druid", "palad", "necro", "warlo"),
    "weapons": ("axes", "bows", "xbows", "daggs", "javel", "maces", "poles", "scept", "spear", "stave", "sword", "throw", "wands", "amazo", "assas", "sorce"),
    "accessories": ("charm", "amule", "rings", "jewel"),
}

_UI_CATEGORY_FALLBACKS: Dict[str, str] = {
    "helms": "Helms",
    "circl": "Circlets",
    "armor": "Armor",
    "shlds": "Shields",
    "glove": "Gloves",
    "boots": "Boots",
    "belts": "Belts",
    "barbh": "Barbarian",
    "druid": "Druid",
    "palad": "Paladin",
    "necro": "Necromancer",
    "warlo": "Warlock",
    "axes": "Axes",
    "bows": "Bows",
    "xbows": "Crossbows",
    "daggs": "Daggers",
    "javel": "Javelins",
    "maces": "Maces",
    "poles": "Polearms",
    "scept": "Scepters",
    "spear": "Spears",
    "stave": "Staves",
    "sword": "Swords",
    "throw": "Throwing",
    "wands": "Wands",
    "amazo": "Amazon",
    "assas": "Assassin",
    "sorce": "Sorceress",
    "charm": "Charms",
    "amule": "Amulets",
    "rings": "Rings",
    "jewel": "Jewels",
    "scrlt": "Scrolls and Tomes",
    "potis": "Potions",
    "ammo": "Ammunition",
    "runes": "Runes",
    "gems": "Gems",
    "keysr": "Keys",
}

_TYPE_TO_UI_CATEGORY: Dict[str, str] = {
    "helm": "helms", "merc": "helms", "circ": "circl", "tors": "armor", "shie": "shlds",
    "glov": "glove", "boot": "boots", "belt": "belts", "phlm": "barbh", "pelt": "druid",
    "ashd": "palad", "head": "necro", "grim": "warlo", "axe": "axes", "bow": "bows",
    "xbow": "xbows", "knif": "daggs", "jave": "javel", "mace": "maces", "club": "maces",
    "hamm": "maces", "pole": "poles", "scep": "scept", "spea": "spear", "staf": "stave",
    "swor": "sword", "tkni": "throw", "taxe": "throw", "tpot": "throw", "wand": "wands",
    "abow": "amazo", "aspe": "amazo", "ajav": "amazo", "h2h": "assas", "h2h2": "assas",
    "orb": "sorce", "char": "charm", "scha": "charm", "mcha": "charm", "lcha": "charm",
    "amul": "amule", "ring": "rings", "jewl": "jewel",
}

_CLASS_UI_CATEGORIES: frozenset[str] = frozenset({
    "amazo", "assas", "barbh", "druid", "necro", "palad", "sorce", "warlo",
})

_RUNEWORD_CATEGORY_FALLBACKS: Dict[str, str] = {
    "r_arm": "Body Armor",
    "r_hel": "Helm",
    "r_mel": "Melee",
    "r_mis": "Missile",
    "r_off": "Offhand",
}

_GROUP_FALLBACKS: Dict[str, str] = {
    "armor": "Armor",
    "weapons": "Weapons",
    "accessories": "Accessories",
    "other": "Other",
}

# Backwards-compatible static view derived from canonical codes (callers should prefer taxonomy.loot_groups()).
LOOT_GROUPS: Dict[str, List[str]] = {
    _GROUP_FALLBACKS[group_code]: [_UI_CATEGORY_FALLBACKS[code] for code in ui_codes]
    for group_code, ui_codes in LOOT_GROUP_UI_CODES.items()
}


class ItemTypeTaxonomy:
    def __init__(self, repo):
        self.repo = repo
        self.types = {row['Code']: row for row in repo.get_excel_table('itemtypes') if row.get('Code')}
        self.bases = {row['code']: row for table in ('weapons', 'armor', 'misc') for row in repo.get_excel_table(table) if row.get('code')}
        self._chain_cache: dict[tuple, list] = {}
        self._ui_cat_code_counts = Counter(
            row.get('UICategory', '').strip()
            for row in self.types.values()
            if row.get('UICategory', '').strip()
        )
        self._ui_to_group: Dict[str, str] = {
            ui_code: group_code
            for group_code, ui_codes in LOOT_GROUP_UI_CODES.items()
            for ui_code in ui_codes
        }
        for row in self.types.values():
            ui_code = row.get('UICategory', '').strip()
            code = row.get('Code', '').strip()
            if ui_code and ui_code not in self._ui_to_group and code:
                self._ui_to_group[ui_code] = self.group_code_for_ui_code(ui_code, self.chain(code))

        self._label_to_group_code: Dict[str, str] = {}
        for ui_code, group_code in self._ui_to_group.items():
            for lbl in (self.category_label(ui_code), _UI_CATEGORY_FALLBACKS.get(ui_code, "")):
                if lbl:
                    self._label_to_group_code.setdefault(lbl.casefold(), group_code)

    def chain(self, *codes):
        key = tuple(codes)
        cached = self._chain_cache.get(key)
        if cached is not None:
            return cached
        result = []

        def visit(code):
            code = (code or '').strip()
            if not code or code in result:
                return
            result.append(code)
            row = self.types.get(code, {})
            visit(row.get('Equiv1'))
            visit(row.get('Equiv2'))

        for code in codes:
            visit(code)
        # Callers only read this list; it is shared and must not be mutated.
        self._chain_cache[key] = result
        return result

    def ui_category_code(self, row: Optional[Dict[str, str]]) -> str:
        if not row:
            return ''
        chain = self.chain(row.get('type'), row.get('type2'))
        for code in chain:
            ui_cat = self.types.get(code, {}).get('UICategory', '').strip()
            if ui_cat:
                return ui_cat
            if code in _TYPE_TO_UI_CATEGORY:
                return _TYPE_TO_UI_CATEGORY[code]
        return ''

    def category_label(self, ui_code: str) -> str:
        clean = (ui_code or '').strip()
        if not clean:
            return _GROUP_FALLBACKS["other"]
        localized = resolve_localized_string(self.repo, clean)
        if localized:
            return localized
        return _UI_CATEGORY_FALLBACKS.get(clean, clean)

    def category(self, row: Dict[str, str]) -> str:
        ui_code = self.ui_category_code(row)
        return self.category_label(ui_code) if ui_code else _GROUP_FALLBACKS["other"]

    def group_code_for_ui_code(self, ui_code: str, type_chain: Sequence[str] = ()) -> str:
        clean = (ui_code or '').strip()
        if clean in self._ui_to_group:
            return self._ui_to_group[clean]
        chain_set = set(type_chain)
        if 'weap' in chain_set:
            return 'weapons'
        if 'armo' in chain_set:
            return 'armor'
        if chain_set & {'char', 'amul', 'ring', 'jewl'}:
            return 'accessories'
        return 'other'

    def group_code(self, row: Optional[Dict[str, str]]) -> str:
        if not row:
            return 'other'
        ui_code = self.ui_category_code(row)
        chain = self.chain(row.get('type'), row.get('type2'))
        return self.group_code_for_ui_code(ui_code, chain)

    def group_label(self, group_code: str) -> str:
        clean = (group_code or 'other').strip().lower()
        if clean == 'armor':
            return resolve_localized_string(self.repo, 'armor') or _GROUP_FALLBACKS['armor']
        if clean == 'weapons':
            weapons_lbl = resolve_localized_string(self.repo, 'StrGemX3').rstrip(': ').strip()
            return weapons_lbl or _GROUP_FALLBACKS['weapons']
        if clean == 'accessories':
            return resolve_localized_string(self.repo, 'accessories') or _GROUP_FALLBACKS['accessories']
        return _GROUP_FALLBACKS.get(clean, clean)

    def group(self, category_or_code: Union[str, Dict[str, str]]) -> str:
        if isinstance(category_or_code, dict):
            return self.group_label(self.group_code(category_or_code))
        clean = (category_or_code or '').strip()
        if not clean:
            return self.group_label('other')
        if clean in self._ui_to_group:
            return self.group_label(self._ui_to_group[clean])
        if clean in self.types:
            return self.group_label(self.group_code({"type": clean}))
        group_code = self._label_to_group_code.get(clean.casefold())
        if group_code:
            return self.group_label(group_code)
        return self.group_label('other')

    def loot_groups(self, include_accessories: bool = True) -> Dict[str, List[str]]:
        group_codes = ('armor', 'weapons', 'accessories') if include_accessories else ('armor', 'weapons')
        extra_by_group: Dict[str, List[str]] = {g: [] for g in group_codes}
        known_ui_codes = {code for codes in LOOT_GROUP_UI_CODES.values() for code in codes}
        for row in self.types.values():
            ui_code = row.get('UICategory', '').strip()
            code = row.get('Code', '').strip()
            if not ui_code or ui_code in known_ui_codes or ui_code in {'scrlt', 'potis', 'ammo', 'runes', 'gems', 'keysr'}:
                continue
            g_code = self.group_code_for_ui_code(ui_code, self.chain(code))
            if g_code in extra_by_group and ui_code not in extra_by_group[g_code]:
                extra_by_group[g_code].append(ui_code)

        result: Dict[str, List[str]] = {}
        for g_code in group_codes:
            labels: List[str] = []
            seen: Set[str] = set()
            for ui_code in (*LOOT_GROUP_UI_CODES[g_code], *extra_by_group[g_code]):
                lbl = self.category_label(ui_code)
                if lbl and lbl not in seen:
                    seen.add(lbl)
                    labels.append(lbl)
            result[self.group_label(g_code)] = labels
        return result

    def label(self, code: str) -> str:
        clean = (code or '').strip()
        if not clean:
            return ''
        row = self.types.get(clean, {})
        raw_item_type = row.get('ItemType', '').strip()

        if clean == 'weap':
            weapons_lbl = resolve_localized_string(self.repo, 'StrGemX3').rstrip(': ').strip()
            return weapons_lbl or resolve_localized_string(self.repo, raw_item_type) or 'Weapons'

        if clean in {'tors', 'shld', 'seco', 'mele', 'miss', 'armo', 'merc'}:
            rw1 = row.get('RunewordCategory1', '').strip()
            if rw1:
                resolved = resolve_localized_string(self.repo, rw1)
                if resolved:
                    return resolved
                if rw1 in _RUNEWORD_CATEGORY_FALLBACKS:
                    return _RUNEWORD_CATEGORY_FALLBACKS[rw1]
            return resolve_localized_string(self.repo, raw_item_type) or raw_item_type or clean

        equiv2 = row.get('Equiv2', '').strip()
        ui_cat = row.get('UICategory', '').strip()
        if clean == 'helm' or (equiv2 == 'merc' and ui_cat == 'helms'):
            equiv2_row = self.types.get(equiv2, {}) if equiv2 else {}
            rw1 = row.get('RunewordCategory1', '').strip() or equiv2_row.get('RunewordCategory1', '').strip()
            if rw1:
                resolved = resolve_localized_string(self.repo, rw1)
                if resolved:
                    return resolved
                if rw1 in _RUNEWORD_CATEGORY_FALLBACKS:
                    return _RUNEWORD_CATEGORY_FALLBACKS[rw1]
            if ui_cat:
                resolved_ui = resolve_localized_string(self.repo, ui_cat)
                if resolved_ui:
                    return resolved_ui
            equiv2_item_type = equiv2_row.get('ItemType', '').strip()
            if equiv2_item_type:
                resolved_eq2 = resolve_localized_string(self.repo, equiv2_item_type)
                if resolved_eq2:
                    return resolved_eq2
                if equiv2_item_type.casefold() != 'merc equip':
                    return equiv2_item_type
            return _RUNEWORD_CATEGORY_FALLBACKS['r_hel']

        if raw_item_type:
            resolved_type = resolve_localized_string(self.repo, raw_item_type)
            if resolved_type:
                return resolved_type

        if ui_cat and ui_cat not in _CLASS_UI_CATEGORIES and self._ui_cat_code_counts.get(ui_cat, 0) == 1:
            resolved_ui = resolve_localized_string(self.repo, ui_cat)
            if resolved_ui:
                return resolved_ui

        return raw_item_type or clean

    def runeword_category_codes(self, code: str) -> Set[str]:
        categories: Set[str] = set()
        for chain_code in self.chain(code):
            type_row = self.types.get(chain_code, {})
            for col in ('RunewordCategory1', 'RunewordCategory2'):
                val = type_row.get(col, '').strip()
                if val:
                    categories.add(val)
        return categories

    @staticmethod
    def rules(row, prefix):
        return [value.strip() for key, value in row.items() if key.startswith(prefix) and key[len(prefix):].isdigit() and value.strip() not in ('', 'xxx')]

    def accepts(self, runeword, base):
        chain = set(self.chain(base.get('type'), base.get('type2')))
        included = self.rules(runeword, 'itype')
        excluded = self.rules(runeword, 'etype')
        sockets = sum(bool(runeword.get(f'Rune{i}', '').strip() not in ('', 'xxx')) for i in range(1, 7))
        type_row = self.types.get(base.get('type'), {})
        caps = [int(type_row.get(f'MaxSockets{i}', '') or 0) for i in range(1, 4)]
        base_cap = int(base.get('gemsockets', '') or 0)
        capacity = min(base_cap, max(caps)) if max(caps) else base_cap
        return bool(chain.intersection(included)) and not chain.intersection(excluded) and capacity >= sockets

    def matching_bases(self, row):
        included = set(self.rules(row, 'itype'))
        excluded = set(self.rules(row, 'etype'))
        sockets = sum(bool(row.get(f'Rune{i}', '').strip() not in ('', 'xxx')) for i in range(1, 7))
        result = []
        for base in self.bases.values():
            chain = set(self.chain(base.get('type'), base.get('type2')))
            type_row = self.types.get(base.get('type'), {})
            caps = [int(type_row.get(f'MaxSockets{i}', '') or 0) for i in range(1, 4)]
            base_cap = int(base.get('gemsockets', '') or 0)
            capacity = min(base_cap, max(caps)) if max(caps) else base_cap
            if bool(chain & included) and not (chain & excluded) and capacity >= sockets:
                result.append(base)
        return result

    def runeword_terms(self, row):
        codes = self.rules(row, 'itype')
        terms = {self.label(code) for code in codes if self.label(code)}
        for base in self.matching_bases(row):
            chain = self.chain(base.get('type'), base.get('type2'))
            terms.update(self.label(code) for code in chain if code in ('tors', 'shld', 'mele', 'miss', 'weap', 'helm') and self.label(code))
            base_type_lbl = self.label(base.get('type', ''))
            if base_type_lbl:
                terms.add(base_type_lbl)
        return sorted(terms)
