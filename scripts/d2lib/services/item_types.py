"""Loot-filter browsing categories and code-based runeword eligibility."""

LOOT_GROUPS = {
    "Armor": ["Helms", "Circlets", "Armor", "Shields", "Gloves", "Boots", "Belts", "Barbarian", "Druid", "Paladin", "Necromancer", "Warlock"],
    "Weapons": ["Axes", "Bows", "Crossbows", "Daggers", "Javelins", "Maces", "Polearms", "Scepters", "Spears", "Staves", "Swords", "Throwing", "Wands", "Amazon", "Assassin", "Sorceress"],
    "Accessories": ["Charms", "Amulets", "Rings", "Jewels"],
}
UI_CATEGORIES = dict(zip(
    "helms circl armor shlds glove boots belts barbh druid palad necro warlo axes bows xbows daggs javel maces poles scept spear stave sword throw wands amazo assas sorce charm amule rings jewel".split(),
    [label for labels in LOOT_GROUPS.values() for label in labels],
))
TYPE_CATEGORIES = dict(zip(
    "helm merc circ tors shie glov boot belt phlm pelt ashd head grim axe bow xbow knif jave mace club hamm pole scep spea staf swor tkni taxe wand abow aspe ajav h2h h2h2 orb char amul ring jewl".split(),
    ["Helms", "Helms", "Circlets", "Armor", "Shields", "Gloves", "Boots", "Belts", "Barbarian", "Druid", "Paladin", "Necromancer", "Warlock", "Axes", "Bows", "Crossbows", "Daggers", "Javelins", "Maces", "Maces", "Maces", "Polearms", "Scepters", "Spears", "Staves", "Swords", "Throwing", "Throwing", "Wands", "Amazon", "Amazon", "Amazon", "Assassin", "Assassin", "Sorceress", "Charms", "Amulets", "Rings", "Jewels"],
))


class ItemTypeTaxonomy:
    def __init__(self, repo):
        self.repo = repo
        self.types = {row['Code']: row for row in repo.get_excel_table('itemtypes') if row.get('Code')}
        self.bases = {row['code']: row for table in ('weapons', 'armor', 'misc') for row in repo.get_excel_table(table) if row.get('code')}

    def chain(self, *codes):
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
        return result

    def category(self, row):
        chain = self.chain(row.get('type'))
        for code in chain:
            category = UI_CATEGORIES.get(self.types.get(code, {}).get('UICategory', '').strip())
            if category:
                return category
            if code in TYPE_CATEGORIES:
                return TYPE_CATEGORIES[code]
        return 'Other'

    @staticmethod
    def group(category):
        return next((group for group, categories in LOOT_GROUPS.items() if category in categories), 'Other')

    def label(self, code):
        aliases = {'weap': 'Weapons', 'mele': 'Melee', 'miss': 'Missile', 'tors': 'Body Armour', 'shld': 'OffHand', 'seco': 'OffHand', 'helm': 'Helm'}
        key = self.types.get(code, {}).get('ItemType', code)
        return aliases.get(code) or self.repo.get_string(key) or key

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
        return [base for base in self.bases.values() if self.accepts(row, base)]

    def runeword_terms(self, row):
        codes = self.rules(row, 'itype')
        terms = {self.label(code) for code in codes}
        for base in self.matching_bases(row):
            chain = self.chain(base.get('type'), base.get('type2'))
            terms.update(self.label(code) for code in chain if code in ('tors', 'shld', 'mele', 'miss', 'weap'))
            # Specific runeword classes remain distinct even when the loot filter combines them.
            terms.add(self.label(base.get('type', '')))
        return sorted(terms)
