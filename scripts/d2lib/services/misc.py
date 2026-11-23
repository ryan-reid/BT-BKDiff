from __future__ import annotations
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import D2Repository, D2RepositoryProtocol, resolve_localized_string
from d2lib.models import MiscItemDTO, MiscGroupDTO
from d2lib.services.item_types import ItemTypeTaxonomy
from d2lib.services.resolver import PropertyResolverService
from d2lib.services.base import _status_for_row

_SENTINEL_UI_CATEGORIES = frozenset({"", "null", "dns", "quest", "misc"})


class MiscAnalyzerService:
    CATEGORY_META: Dict[str, Dict[str, Any]] = {
        "runes": {
            "order": 10,
            "summary": "Rune progression and runeword components, including changed socket effects.",
        },
        "gems": {
            "order": 20,
            "summary": "Socketable gems, skulls, quartz, and ascended tiers with armor, helm, shield, and weapon effects.",
        },
        "crafting": {
            "order": 30,
            "summary": "Core crafting inputs such as tablets, stones, sigils, herbs, and special crafting materials.",
        },
        "terrt": {
            "order": 40,
            "summary": "Directional tokens and shards used by crafting and endgame recipe families.",
        },
        "absol": {
            "order": 50,
            "summary": "Token and essence materials used for respec and boss-derived progression recipes.",
        },
        "uberm": {
            "order": 60,
            "summary": "Pandemonium keys, organs, standards, and endgame quest materials.",
        },
        "keysr": {
            "order": 70,
            "summary": "Stackable keys and special access keys.",
        },
        "scrlt": {
            "order": 80,
            "summary": "Town portal, identify, and knowledge scroll items.",
        },
        "potis": {
            "order": 90,
            "summary": "Potions, elixirs, dyes, and consumables players may carry or convert.",
        },
        "charm": {
            "order": 100,
            "summary": "Charms surfaced in miscellaneous item data.",
        },
        "jewel": {
            "order": 102,
            "summary": "Jewels surfaced in miscellaneous item data.",
        },
        "amule": {
            "order": 104,
            "summary": "Amulets surfaced in miscellaneous item data.",
        },
        "rings": {
            "order": 106,
            "summary": "Rings surfaced in miscellaneous item data.",
        },
        "body": {
            "order": 110,
            "summary": "Body-part style drops used as recipe ingredients or progression materials.",
        },
        "ammo": {
            "order": 120,
            "summary": "Arrows, bolts, gold, torches, and other stackable utility items.",
        },
        "quest": {
            "order": 130,
            "summary": "Campaign and progression items present in miscellaneous item data.",
        },
        "other": {
            "order": 900,
            "summary": "Additional misc items that do not match a narrower category code.",
        },
    }

    def __init__(self, repo: D2RepositoryProtocol, resolver: Optional[PropertyResolverService] = None, retail_repo: Optional[D2RepositoryProtocol] = None):
        self.repo = repo
        self.resolver = resolver or PropertyResolverService(repo)
        self.retail_repo = retail_repo
        self.misc = repo.get_excel_table('misc')
        self.gems = {row.get('code', '').strip(): row for row in repo.get_excel_table('gems') if row.get('code')}
        self.retail_misc = {
            row.get('code', '').strip(): row
            for row in retail_repo.get_excel_table('misc')
        } if retail_repo else {}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes') if row.get('Code')}
        self.taxonomy = ItemTypeTaxonomy(repo)

    def analyze_misc_items(self) -> List[MiscGroupDTO]:
        items: List[MiscItemDTO] = []
        source_categories: Dict[str, set[str]] = {}
        category_labels: Dict[str, str] = {}

        for row in self.misc:
            item = self.analyze_row(row)
            if item is None:
                continue
            type_code = row.get('type', '').strip()
            uicat = row.get('UICatOverride', '').strip()
            is_rune = type_code == 'rune'
            is_gem = type_code.startswith('gem')
            is_quest = row.get('quest', '0') != '0'
            cat_key = item["category_key"]
            category_labels[cat_key] = item["category"]
            source_category = uicat or ("rune" if is_rune else "gem" if is_gem else "quest" if is_quest else type_code or "other")
            source_categories.setdefault(cat_key, set()).add(source_category)
            items.append(item)

        # Group by canonical category key
        groups: Dict[str, List[MiscItemDTO]] = {}
        for item in items:
            groups.setdefault(item["category_key"], []).append(item)

        return [
            {
                "category_key": cat_key,
                "category": category_labels[cat_key],
                "summary": self.CATEGORY_META.get(cat_key, self.CATEGORY_META["other"])["summary"],
                "order": self.CATEGORY_META.get(cat_key, {"order": 150})["order"],
                "source_categories": sorted(source_categories.get(cat_key, [])),
                "members": sorted(members, key=lambda x: (x["level"], x["name"])),
            }
            for cat_key, members in sorted(
                groups.items(),
                key=lambda entry: (
                    self.CATEGORY_META.get(entry[0], {"order": 150})["order"],
                    category_labels[entry[0]].casefold(),
                    entry[0],
                ),
            )
        ]

    def analyze_row(self, row: Dict[str, str]) -> Optional[MiscItemDTO]:
        code = row.get('code', '').strip()
        if not code or code == '0':
            return None

        # Filter: UICatOverride (BK specific) or specific types like Runes, Gems, Quest
        uicat = row.get('UICatOverride', '').strip()
        type_code = row.get('type', '').strip()
        is_rune = type_code == 'rune'
        is_gem = type_code.startswith('gem')
        is_quest = row.get('quest', '0') != '0'

        if not uicat and not is_rune and not is_gem and not is_quest:
            return None

        name_str = row.get('namestr') or row.get('name')
        name = self.repo.get_string(name_str) or name_str or code

        desc_str = row.get('description')
        description = self.repo.get_string(desc_str) if desc_str else ""
        category_key, category = self._resolve_category(row, uicat, type_code, is_rune, is_gem, is_quest)

        def to_int(v):
            try: return int(v) if v else 0
            except: return 0

        socket_effects, socket_effects_by_slot, socket_slot_labels = self._socket_effects_with_slots(code)
        return {
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
            "category_key": category_key,
            "category": category,
            "status": _status_for_row(code, row, self.retail_misc) if self.retail_repo else "unchanged",
            "socket_effects": socket_effects,
            "socket_effects_by_slot": socket_effects_by_slot,
            "socket_slot_labels": socket_slot_labels,
        }

    def _resolve_category(
        self,
        row: Dict[str, str],
        uicat: str,
        type_code: str,
        is_rune: bool,
        is_gem: bool,
        is_quest: bool,
    ) -> Tuple[str, str]:
        ui_raw = uicat.strip()
        ui = ui_raw.lower()
        type_lower = type_code.strip().lower()
        code = row.get('code', '').strip().lower()

        if ui not in _SENTINEL_UI_CATEGORIES:
            label = resolve_localized_string(self.repo, ui_raw) or self.taxonomy.category_label(ui_raw)
            return ui, label or ui_raw
        if is_rune:
            return "runes", resolve_localized_string(self.repo, "runes") or "Runes"
        if is_gem:
            return "gems", resolve_localized_string(self.repo, "gems") or "Gems"
        if type_lower == "herb" or (type_lower == "spot" and row.get("useable", "").strip() != "1"):
            return "crafting", "Crafting Materials"

        itemtype_ui = self.taxonomy.ui_category_code({"type": type_code})
        if itemtype_ui and itemtype_ui.lower() not in _SENTINEL_UI_CATEGORIES:
            return itemtype_ui, self.taxonomy.category_label(itemtype_ui)

        if type_lower in ("book", "scro"):
            return "scrlt", resolve_localized_string(self.repo, "scrlt") or "Scrolls and Tomes"
        if type_lower == "key":
            return "keysr", resolve_localized_string(self.repo, "keysr") or "Keys"
        if type_lower in ("hpot", "mpot", "wpot", "apot", "rpot", "elix"):
            return "potis", resolve_localized_string(self.repo, "potis") or "Potions"
        if type_lower in ("amul", "ring", "jewl", "cjwl", "chms", "scha", "mcha", "lcha", "csch"):
            mapped = {
                "amul": "amule",
                "ring": "rings",
                "jewl": "jewel",
                "cjwl": "jewel",
            }.get(type_lower, "charm")
            return mapped, self.taxonomy.category_label(mapped)
        if type_lower == "body":
            return "body", "Monster Parts"
        if type_lower in ("bowq", "xboq", "gold", "torc"):
            return "ammo", resolve_localized_string(self.repo, "ammo") or "Ammunition"
        if is_quest or type_lower == "ques" or code in ("box", "tr1", "mss"):
            return "quest", "Quest Items"
        return "other", "Other Materials"

    def _socket_slot_labels(self) -> Dict[str, str]:
        weapon = (resolve_localized_string(self.repo, "StrGemX3") or "Weapons").rstrip(": ").strip()
        armor = (resolve_localized_string(self.repo, "StrGemX4") or "Armor").rstrip(": ").strip()
        helm = (resolve_localized_string(self.repo, "StrGemX1") or "Helms").rstrip(": ").strip()
        shield = (resolve_localized_string(self.repo, "StrGemX2") or "Shields").rstrip(": ").strip()
        return {
            "weapon": weapon,
            "helm": f"{armor}/{helm}",
            "shield": shield,
        }

    def _socket_effects_with_slots(
        self,
        code: str,
    ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], Dict[str, str]]:
        slot_labels = self._socket_slot_labels()
        gem_row = self.gems.get(code)
        if not gem_row:
            return {}, {}, slot_labels

        slot_prefixes = (
            ("weapon", "weaponMod"),
            ("helm", "helmMod"),
            ("shield", "shieldMod"),
        )
        effects: Dict[str, List[str]] = {}
        effects_by_slot: Dict[str, List[str]] = {}
        for slot_key, prefix in slot_prefixes:
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
                effects_by_slot[slot_key] = slot_effects
                effects[slot_labels[slot_key]] = slot_effects
        return effects, effects_by_slot, slot_labels

    def _socket_effects_for_item(self, code: str) -> Dict[str, List[str]]:
        effects, _, _ = self._socket_effects_with_slots(code)
        return effects
