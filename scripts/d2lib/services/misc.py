from __future__ import annotations
from typing import List, Dict, Optional, Any
from d2lib.repository import D2Repository
from d2lib.models import MiscItemDTO, MiscGroupDTO
from d2lib.services.resolver import PropertyResolverService
from d2lib.services.base import _status_for_row

class MiscAnalyzerService:
    CATEGORY_META = {
        "Runes": {
            "order": 10,
            "summary": "Rune progression and runeword components, including changed socket effects.",
        },
        "Gems & Skulls": {
            "order": 20,
            "summary": "Socketable gems, skulls, quartz, and ascended tiers with weapon, armor, and shield effects.",
        },
        "Crafting Tablets & Materials": {
            "order": 30,
            "summary": "Core crafting inputs such as tablets, stones, sigils, herbs, and special BK crafting materials.",
        },
        "Worldstone Shards": {
            "order": 40,
            "summary": "Directional Worldstone shards used by BK crafting and endgame recipe families.",
        },
        "Respec Essences": {
            "order": 50,
            "summary": "Token and essence materials used for respec and boss-derived progression recipes.",
        },
        "Uber & Endgame Materials": {
            "order": 60,
            "summary": "Pandemonium keys, organs, standards, and BK-specific endgame quest materials.",
        },
        "Keys": {
            "order": 70,
            "summary": "Stackable keys and special access keys.",
        },
        "Scrolls & Tomes": {
            "order": 80,
            "summary": "Town portal, identify, and knowledge scroll items.",
        },
        "Potions & Consumables": {
            "order": 90,
            "summary": "Potions, elixirs, dyes, and consumables players may carry or convert.",
        },
        "Jewelry, Charms & Jewels": {
            "order": 100,
            "summary": "Miscellaneous socketables, charms, jewels, rings, and amulets surfaced by BK data.",
        },
        "Monster Parts": {
            "order": 110,
            "summary": "Body-part style drops used as recipe ingredients or progression materials.",
        },
        "Ammunition & Stackables": {
            "order": 120,
            "summary": "Arrows, bolts, gold, torches, and other stackable utility items.",
        },
        "Quest Items": {
            "order": 130,
            "summary": "Campaign and progression items that still appear in the mod data.",
        },
        "Other Materials": {
            "order": 900,
            "summary": "Additional misc items that do not fit a clearer player-facing bucket yet.",
        },
    }

    def __init__(self, repo: D2Repository, resolver: Optional[PropertyResolverService] = None, retail_repo: Optional[D2Repository] = None):
        self.repo = repo
        self.resolver = resolver or PropertyResolverService(repo)
        self.retail_repo = retail_repo
        self.misc = repo.get_excel_table('misc')
        self.gems = {row.get('code', '').strip(): row for row in repo.get_excel_table('gems') if row.get('code')}
        self.retail_misc = {
            row.get('code', '').strip(): row
            for row in retail_repo.get_excel_table('misc')
        } if retail_repo else {}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}

    def analyze_misc_items(self) -> List[MiscGroupDTO]:
        items: List[MiscItemDTO] = []
        source_categories: Dict[str, set[str]] = {}

        for row in self.misc:
            code = row.get('code', '').strip()
            if not code or code == '0': continue

            # Filter: UICatOverride (BK specific) or specific types like Runes, Gems, Quest
            uicat = row.get('UICatOverride', '').strip()
            type_code = row.get('type', '').strip()

            is_rune = type_code == 'rune'
            is_gem = type_code.startswith('gem')
            is_quest = row.get('quest', '0') != '0'

            if not uicat and not is_rune and not is_gem and not is_quest:
                continue

            name_str = row.get('namestr') or row.get('name')
            name = self.repo.get_string(name_str) or name_str or code

            desc_str = row.get('description')
            description = self.repo.get_string(desc_str) if desc_str else ""
            category = self._player_category(row, uicat, type_code, is_rune, is_gem, is_quest, name)
            source_category = uicat or ("Rune" if is_rune else "Gem" if is_gem else "Quest" if is_quest else type_code or "Other")
            source_categories.setdefault(category, set()).add(source_category)

            def to_int(v):
                try: return int(v) if v else 0
                except: return 0

            items.append({
                "code": code,
                "name": name,
                "icon_key": row.get('invfile', '').strip(),
                "icon_src": "",
                "type": type_code,
                "level": to_int(row.get('level')),
                "level_req": to_int(row.get('levelreq')),
                "stackable": row.get('stackable') == '1',
                "max_stack": to_int(row.get('maxstack')),
                "cost": to_int(row.get('cost')),
                "description": description,
                "category": category,
                "status": _status_for_row(code, row, self.retail_misc) if self.retail_repo else "unchanged",
                "socket_effects": self._socket_effects_for_item(code),
            })

        # Group by Category
        groups: Dict[str, List[MiscItemDTO]] = {}
        for item in items:
            cat = item['category']
            if cat not in groups: groups[cat] = []
            groups[cat].append(item)

        return [
            {
                "category": name,
                "summary": self.CATEGORY_META.get(name, self.CATEGORY_META["Other Materials"])["summary"],
                "order": self.CATEGORY_META.get(name, self.CATEGORY_META["Other Materials"])["order"],
                "source_categories": sorted(source_categories.get(name, [])),
                "members": sorted(items, key=lambda x: (x["level"], x["name"])),
            }
            for name, items in sorted(
                groups.items(),
                key=lambda entry: (
                    self.CATEGORY_META.get(entry[0], self.CATEGORY_META["Other Materials"])["order"],
                    entry[0],
                ),
            )
        ]

    def _player_category(
        self,
        row: Dict[str, str],
        uicat: str,
        type_code: str,
        is_rune: bool,
        is_gem: bool,
        is_quest: bool,
        name: str,
    ) -> str:
        ui = uicat.strip().lower()
        type_lower = type_code.strip().lower()
        name_lower = name.strip().lower()
        code = row.get('code', '').strip().lower()

        ui_map = {
            "absol": "Respec Essences",
            "terrt": "Worldstone Shards",
            "uberm": "Uber & Endgame Materials",
            "keysr": "Keys",
            "scrlt": "Scrolls & Tomes",
            "dns": "Jewelry, Charms & Jewels",
            "null": "Potions & Consumables",
            "crafting": "Crafting Tablets & Materials",
        }
        if ui in ui_map:
            return ui_map[ui]
        if ui and ui not in ("quest", "misc"):
            return ui[:1].upper() + ui[1:]
        if is_rune:
            return "Runes"
        if is_gem:
            return "Gems & Skulls"
        if type_lower in ("book", "scro"):
            return "Scrolls & Tomes"
        if type_lower == "key":
            return "Keys"
        if type_lower in ("hpot", "mpot", "wpot", "apot", "rpot", "elix"):
            return "Potions & Consumables"
        if type_lower in ("amul", "ring", "jewl", "cjwl", "chms", "scha", "mcha", "lcha", "csch"):
            return "Jewelry, Charms & Jewels"
        if type_lower == "body":
            return "Monster Parts"
        if type_lower in ("bowq", "xboq", "gold", "torc"):
            return "Ammunition & Stackables"
        if type_lower in ("spot", "herb") or any(
            token in name_lower
            for token in ("tablet", "shard", "stone", "sigil", "soulstone", "ashes", "hammer", "herb", "rift")
        ):
            return "Crafting Tablets & Materials"
        if is_quest or code in ("box", "tr1", "mss"):
            return "Quest Items"
        return "Other Materials"

    def _socket_effects_for_item(self, code: str) -> Dict[str, List[str]]:
        gem_row = self.gems.get(code)
        if not gem_row:
            return {}
        slot_prefixes = {
            "Weapon": "weaponMod",
            "Armor/Helm": "helmMod",
            "Shield": "shieldMod",
        }
        effects: Dict[str, List[str]] = {}
        for slot, prefix in slot_prefixes.items():
            slot_effects = []
            for i in range(1, 4):
                prop_code = gem_row.get(f"{prefix}{i}Code", "").strip()
                if prop_code and prop_code != "0":
                    resolved = self.resolver.resolve_property(
                        prop_code,
                        gem_row.get(f"{prefix}{i}Param", ""),
                        gem_row.get(f"{prefix}{i}Min", ""),
                        gem_row.get(f"{prefix}{i}Max", ""),
                    )["resolved_text"]
                    if resolved:
                        slot_effects.append(resolved)
            if slot_effects:
                effects[slot] = slot_effects
        return effects
