from __future__ import annotations
import re
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import D2Repository
from d2lib.models import AnalyzedItemDTO, RunewordDTO, BaseItemDTO, BaseItemFamilyDTO
from d2lib.services.resolver import PropertyResolverService

class ItemAnalyzerService:
    def __init__(self, repo: D2Repository, resolver: PropertyResolverService):
        self.repo = repo
        self.resolver = resolver
        self.armor = {row['code']: row for row in repo.get_excel_table('armor')}
        self.weapons = {row['code']: row for row in repo.get_excel_table('weapons')}
        self.misc = {row['code']: row for row in repo.get_excel_table('misc')}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}
        self.sets = {row['name']: row for row in repo.get_excel_table('sets')}
        self.gems = {row['code']: row for row in repo.get_excel_table('gems')}

    def get_item_name(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if item: return self.repo.get_string(item.get('namestr', '').strip() or item.get('name', '').strip()) or code
        return code

    def get_item_category(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if not item: return "Miscellaneous"
        type_code = item.get('type', '').strip()
        
        # Swapped types in mods: often 'helm' is renamed to 'Merc Equip' 
        # and a new 'merc' type is added for player 'Helms'.
        if type_code == "helm":
            return "Helm"
            
        item_type = self.item_types.get(type_code)
        if not item_type: return "Miscellaneous"
        
        name = self.repo.get_string(item_type.get('ItemType', 'Unknown').strip())
        if name.lower().strip() == "merc equip":
            return "Helm"
        return name

    def get_granular_group(self, category: str) -> str:
        cat_lower = category.lower()
        # Weapons
        if any(cls in cat_lower for cls in ['amazon', 'assassin', 'orb', 'hand to hand', 'grimoire']): return 'Class Weapons'
        if 'axe' in cat_lower: return 'Axes'
        if 'bow' in cat_lower: return 'Bows'
        if 'crossbow' in cat_lower: return 'Crossbows'
        if 'dagger' in cat_lower or 'knife' in cat_lower: return 'Daggers'
        if 'javelin' in cat_lower: return 'Javelins'
        if 'mace' in cat_lower or 'club' in cat_lower or 'hammer' in cat_lower: return 'Maces'
        if 'polearm' in cat_lower: return 'Polearms'
        if 'scepter' in cat_lower: return 'Scepters'
        if 'spear' in cat_lower: return 'Spears'
        if 'staff' in cat_lower: return 'Staves'
        if 'sword' in cat_lower: return 'Swords'
        if 'throwing' in cat_lower: return 'Throwing'
        if 'wand' in cat_lower: return 'Wands'

        # Others
        if any(cls in cat_lower for cls in ['voodoo', 'pelt', 'primal', 'auric']): return 'Class Armors'
        if 'amulet' in cat_lower: return 'Amulets'
        if 'ring' in cat_lower: return 'Rings'
        if 'charm' in cat_lower: return 'Charms'
        if 'jewel' in cat_lower: return 'Jewels'
        if any(h in cat_lower for h in ['helm', 'circlet', 'merc']): return 'Helms'
        if any(c in cat_lower for c in ['armor', 'tors']): return 'Chests'
        if 'shield' in cat_lower: return 'Shields'
        if 'glove' in cat_lower: return 'Gloves'
        if 'belt' in cat_lower: return 'Belts'
        if 'boot' in cat_lower: return 'Boots'

        return 'Others'

    def get_top_level_group(self, granular_group: str) -> str:
        weapons = ['Class Weapons', 'Axes', 'Bows', 'Crossbows', 'Daggers', 'Javelins', 'Maces', 'Polearms', 'Scepters', 'Spears', 'Staves', 'Swords', 'Throwing', 'Wands']
        if granular_group in weapons:
            return "Weapons"
        return "Others"

    def analyze_unique(self, row: Dict[str, str]) -> AnalyzedItemDTO:
        idx = row.get('index', '').strip()
        props = []
        for i in range(1, 13):
            code = row.get(f'prop{i}', '').strip()
            if code and code != 'xxx':
                props.append(self.resolver.resolve_property(code, row.get(f'par{i}', ''), row.get(f'min{i}', ''), row.get(f'max{i}', '')))
        return {
            "id": idx, "display_name": self.repo.get_string(idx), "base_item": self.get_item_name(row.get('code', '').strip()),
            "item_type": self.get_item_category(row.get('code', '').strip()), "lvl_req": row.get('lvl req', '0'), "properties": props, "raw_row": row
        }

    def analyze_runeword(self, row: Dict[str, str]) -> RunewordDTO:
        name = row.get('*Rune Name', row.get('Name', 'Unknown')).strip()
        runes = []
        rune_levels = []
        for i in range(1, 7):
            r_code = row.get(f'Rune{i}', '').strip()
            if r_code and r_code != 'xxx':
                clean_rune_name = self.repo.get_string(f"{r_code}L")
                runes.append(clean_rune_name or self.get_item_name(r_code))
                try:
                    rune_levels.append(int(self.misc.get(r_code, {}).get("levelreq", "") or 0))
                except ValueError:
                    pass
        props = []
        for i in range(1, 8):
            code = row.get(f'T1Code{i}', '').strip()
            if code and code != 'xxx':
                props.append(self.resolver.resolve_property(code, row.get(f'T1Param{i}', ''), row.get(f'T1Min{i}', ''), row.get(f'T1Max{i}', '')))

        itype = row.get('itype1', '').strip()
        base_items = []
        for index in range(1, 7):
            base_type = row.get(f'itype{index}', '').strip()
            if not base_type or base_type == 'xxx':
                continue
            base_items.append(self.repo.get_string(self.item_types.get(base_type, {}).get('ItemType', '')) or base_type)
        rune_properties = self._resolve_runeword_rune_properties(row, itype)

        return {
            "name": name, "runes": runes, "base_items": base_items,
            "required_level": str(max(rune_levels)) if rune_levels else "",
            "properties": props, "rune_properties": rune_properties, "raw_row": row
        }

    def _resolve_runeword_rune_properties(self, row: Dict[str, str], item_type_code: str) -> List[Dict[str, Any]]:
        socket_group = self._runeword_socket_group(item_type_code)
        if not socket_group:
            return []

        results: List[Dict[str, Any]] = []
        for i in range(1, 7):
            rune_code = row.get(f'Rune{i}', '').strip()
            if not rune_code or rune_code == 'xxx':
                continue

            gem_row = self.gems.get(rune_code)
            if not gem_row:
                continue

            properties = []
            for slot in range(1, 4):
                code = gem_row.get(f'{socket_group}Mod{slot}Code', '').strip()
                if not code or code == 'xxx':
                    continue
                properties.append(
                    self.resolver.resolve_property(
                        code,
                        gem_row.get(f'{socket_group}Mod{slot}Param', ''),
                        gem_row.get(f'{socket_group}Mod{slot}Min', ''),
                        gem_row.get(f'{socket_group}Mod{slot}Max', ''),
                    )
                )

            if properties:
                results.append(
                    {
                        "rune": self.repo.get_string(f"{rune_code}L") or self.get_item_name(rune_code),
                        "properties": properties,
                    }
                )
        return results

    def _runeword_socket_group(self, item_type_code: str) -> str:
        categories = self._item_type_runeword_categories(item_type_code)
        if categories & {"r_mel", "r_mis"}:
            return "weapon"
        if "r_off" in categories:
            return "shield"
        if categories & {"r_arm", "r_hel"}:
            return "helm"
        return ""

    def _item_type_runeword_categories(self, item_type_code: str, seen: Optional[set[str]] = None) -> set[str]:
        if not item_type_code:
            return set()
        seen = seen or set()
        if item_type_code in seen:
            return set()
        seen.add(item_type_code)

        item_type = self.item_types.get(item_type_code, {})
        categories = {
            category
            for category in [
                item_type.get('RunewordCategory1', '').strip(),
                item_type.get('RunewordCategory2', '').strip(),
            ]
            if category
        }
        for equiv_key in ['Equiv1', 'Equiv2']:
            categories.update(self._item_type_runeword_categories(item_type.get(equiv_key, '').strip(), seen))
        return categories

    def analyze_set_item(self, row: Dict[str, str]) -> AnalyzedItemDTO:
        idx = row.get('index', '').strip()
        props = []
        for i in range(1, 10):
            code = row.get(f'prop{i}', '').strip()
            if code and code != 'xxx':
                props.append(self.resolver.resolve_property(code, row.get(f'par{i}', ''), row.get(f'min{i}', ''), row.get(f'max{i}', '')))

        # Partial Set Bonuses (on the item itself)
        partial_props = []
        for i in range(1, 6):
            # i=1 -> 2 items, i=2 -> 3 items, etc.
            piece_count = i + 1
            piece_properties = []
            for suffix in ['a', 'b']:
                code = row.get(f'aprop{i}{suffix}', '').strip()
                if code and code != 'xxx' and code != '0':
                    piece_properties.append(self.resolver.resolve_property(
                        code, 
                        row.get(f'apar{i}{suffix}', ''), 
                        row.get(f'amin{i}{suffix}', ''), 
                        row.get(f'amax{i}{suffix}', '')
                    ))
            if piece_properties:
                partial_props.append({
                    "count": piece_count,
                    "properties": piece_properties
                })

        set_name = row.get('set', '').strip()
        set_info = self.sets.get(set_name, {})
        is_expansion = set_info.get('version', '0') != '0'

        item_code = row.get('item', '').strip()
        return {
            "id": idx, "display_name": self.repo.get_string(idx), "base_item": self.get_item_name(item_code),
            "item_type": self.get_item_category(item_code), "lvl_req": row.get('lvl req', '0'), 
            "properties": props,
            "partial_set_properties": partial_props if partial_props else None,
            "raw_row": {**row, "is_expansion": is_expansion}
        }

class BaseItemAnalyzerService:
    def __init__(self, repo: D2Repository, resolver: PropertyResolverService):
        self.repo = repo
        self.resolver = resolver
        self.armor = repo.get_excel_table('armor')
        self.weapons = repo.get_excel_table('weapons')
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}
        self.runeword_filter_type_codes = self._runeword_filter_type_codes(repo.get_excel_table('runes'))
        self.automagic = repo.get_excel_table('automagic')
        self.quality_items = repo.get_excel_table('qualityitems')
        self.class_names = {
            'ama': 'Amazon', 'sor': 'Sorceress', 'nec': 'Necromancer', 'pal': 'Paladin',
            'bar': 'Barbarian', 'dru': 'Druid', 'ass': 'Assassin', 'war': 'Warlock'
        }

    def analyze_base_items(self) -> List[BaseItemFamilyDTO]:
        families: List[BaseItemFamilyDTO] = []
        seen_codes = set()

        # Link families using normcode, ubercode, ultracode
        all_items = self.armor + self.weapons
        code_to_item = {row['code']: row for row in all_items if row.get('code')}

        for row in all_items:
            code = row.get('code')
            if not code or code in seen_codes: continue

            # Determine if this is a family head (Normal version)
            norm_code = row.get('normcode')
            if norm_code and norm_code != code and norm_code in code_to_item:
                continue # This is an exceptional or elite, we'll find it via its normal version

            family_members = [code]
            if row.get('ubercode') and row.get('ubercode') in code_to_item:
                family_members.append(row['ubercode'])
            if row.get('ultracode') and row.get('ultracode') in code_to_item:
                family_members.append(row['ultracode'])

            items_dto = []
            for i, m_code in enumerate(family_members):
                seen_codes.add(m_code)
                items_dto.append(self._analyze_item(code_to_item[m_code], ["Normal", "Exceptional", "Elite"][i] if i < 3 else "Unknown"))

            if items_dto:
                group = self._family_group(items_dto)
                class_tags = self._family_class_tags(items_dto)
                max_sockets = max(item["sockets"] for item in items_dto)
                families.append({
                    "name": items_dto[0]["name"],
                    "group": group,
                    "summary": self._family_summary(items_dto, group, class_tags, max_sockets),
                    "class_tags": class_tags,
                    "max_sockets": max_sockets,
                    "search_text": self._family_search_text(items_dto, group, class_tags),
                    "members": items_dto
                })

        return sorted(families, key=lambda x: x["name"])

    def _analyze_item(self, row: Dict[str, str], tier: str) -> BaseItemDTO:
        code = row['code']
        name_str = row.get('namestr') or row.get('name')
        name = self.repo.get_string(name_str) or name_str

        type_code = row.get('type', '')
        item_type = self.item_types.get(type_code, {})
        type_name = self.repo.get_string(item_type.get('ItemType', '')) or type_code
        item_type_chain = self._item_type_chain(type_code)
        type_categories = self._type_categories_for_item_type_chain(item_type_chain)
        class_restriction = self._class_restriction_for_item_type(item_type_chain)
        staffmod_class = self._staffmod_class_for_item_type(item_type_chain)

        # Sockets
        base_sockets = int(row.get('gemsockets', '0') or '0')
        type_sockets = [
            int(item_type.get('MaxSockets1', '0') or '0'),
            int(item_type.get('MaxSockets2', '0') or '0'),
            int(item_type.get('MaxSockets3', '0') or '0')
        ]
        thresholds = [
            int(item_type.get('MaxSocketsLevelThresholdOne', '25') or '25'),
            int(item_type.get('MaxSocketsLevelThresholdTwo', '40') or '40')
        ]

        max_sockets_by_ilvl = {
            f"1-{thresholds[0]}": min(base_sockets, type_sockets[0]) if type_sockets[0] > 0 else base_sockets,
            f"{thresholds[0]+1}-{thresholds[1]}": min(base_sockets, type_sockets[1]) if type_sockets[1] > 0 else base_sockets,
            f"{thresholds[1]+1}+": min(base_sockets, type_sockets[2]) if type_sockets[2] > 0 else base_sockets
        }

        # Auto Prefix
        auto_prefix_stats = []
        auto_prefix_id = row.get('auto prefix')
        if auto_prefix_id and auto_prefix_id != '0':
            prefix_rows = self._find_automagic_by_group(auto_prefix_id)
            seen_stats = set()
            for p_row in prefix_rows:
                if not self._automagic_row_applies_to_item_type(p_row, item_type_chain):
                    continue
                for i in range(1, 4):
                    p_code = p_row.get(f'mod{i}code')
                    if p_code and p_code != 'xxx':
                        res = self.resolver.resolve_property(
                            p_code,
                            p_row.get(f'mod{i}param', ''),
                            p_row.get(f'mod{i}min', ''),
                            p_row.get(f'mod{i}max', '')
                        )
                        stat_text = res['resolved_text']
                        if stat_text and stat_text not in seen_stats:
                            auto_prefix_stats.append(stat_text)
                            seen_stats.add(stat_text)

        inherent_stats = self._inherent_stats_for_item_type(item_type_chain)
        quality_bonus_stats = self._quality_bonus_stats_for_item_type(item_type_chain)
        auto_prefix_summary = self._collapse_stat_ranges(auto_prefix_stats)
        quality_bonus_summary = self._collapse_stat_ranges(quality_bonus_stats)

        def to_int(v):
            try: return int(v) if v else 0
            except: return 0

        speed = to_int(row.get('speed'))
        two_handed_only = row.get('2handed') == '1' and row.get('1or2handed') != '1'

        return {
            "code": code,
            "name": name,
            "icon_key": row.get('invfile', '').strip(),
            "icon_src": "",
            "type": type_name,
            "type_categories": type_categories,
            "level": to_int(row.get('level')),
            "level_req": to_int(row.get('levelreq')),
            "defense_min": to_int(row.get('minac')) if 'minac' in row else None,
            "defense_max": to_int(row.get('maxac')) if 'maxac' in row else None,
            "damage_min": to_int(row.get('mindam')) if 'mindam' in row else to_int(row.get('minmisdam')),
            "damage_max": to_int(row.get('maxdam')) if 'maxdam' in row else to_int(row.get('maxmisdam')),
            "two_hand_damage_min": to_int(row.get('2handmindam')) if '2handmindam' in row else None,
            "two_hand_damage_max": to_int(row.get('2handmaxdam')) if '2handmaxdam' in row else None,
            "two_handed_only": two_handed_only,
            "str_req": to_int(row.get('reqstr')),
            "dex_req": to_int(row.get('reqdex')),
            "block": to_int(row.get('block')),
            "sockets": base_sockets,
            "max_sockets_by_ilvl": max_sockets_by_ilvl,
            "class_restriction": class_restriction,
            "staffmod_class": staffmod_class,
            "magic_level": to_int(row.get('magic lvl')),
            "inherent_stats": inherent_stats,
            "auto_prefix_stats": auto_prefix_stats,
            "auto_prefix_summary": auto_prefix_summary,
            "quality_bonus_stats": quality_bonus_stats,
            "quality_bonus_summary": quality_bonus_summary,
            "speed": speed,
            "speed_label": self._weapon_speed_label(speed),
            "durability": to_int(row.get('nodurability')) if row.get('nodurability') == '1' else to_int(row.get('durability')),
            "tier": tier
        }

    def _collapse_stat_ranges(self, stats: List[str]) -> List[str]:
        groups: Dict[str, Dict[str, Any]] = {}
        passthrough: List[str] = []

        for stat in stats:
            parsed = self._stat_range_parts(stat)
            if not parsed:
                if stat not in passthrough:
                    passthrough.append(stat)
                continue

            prefix, sign, minimum, maximum, suffix = parsed
            key = f"{prefix}|{suffix}"
            if key not in groups:
                groups[key] = {"prefix": prefix, "sign": sign, "suffix": suffix, "minimum": minimum, "maximum": maximum}
            else:
                groups[key]["minimum"] = min(groups[key]["minimum"], minimum)
                groups[key]["maximum"] = max(groups[key]["maximum"], maximum)

        collapsed = [
            self._format_stat_range(group["prefix"], group["sign"], group["minimum"], group["maximum"], group["suffix"])
            for group in groups.values()
        ]
        return collapsed + passthrough

    @staticmethod
    def _stat_range_parts(stat: str) -> Optional[Tuple[str, str, int, int, str]]:
        matches = list(re.finditer(r"([+-]?\d+)(?:-([+-]?\d+))?", stat))
        if not matches:
            return None

        # Collapse simple single-stat rolls only. Hybrid superior rolls should stay explicit.
        if len(matches) > 1:
            return None

        match = matches[0]
        first_value = match.group(1)
        sign = "+" if first_value.startswith("+") else ""
        minimum = int(first_value)
        maximum = int(match.group(2) or match.group(1))
        if minimum > maximum:
            minimum, maximum = maximum, minimum
        return stat[:match.start()], sign, minimum, maximum, stat[match.end():]

    @staticmethod
    def _format_stat_range(prefix: str, sign: str, minimum: int, maximum: int, suffix: str) -> str:
        value = str(minimum) if minimum == maximum else f"{minimum}-{maximum}"
        if sign and not value.startswith(("+", "-")):
            value = f"{sign}{value}"
        return f"{prefix}{value}{suffix}"

    @staticmethod
    def _weapon_speed_label(speed: int) -> str:
        if speed <= -20:
            return "Very Fast"
        if speed <= -10:
            return "Fast"
        if speed < 10:
            return "Normal"
        if speed < 20:
            return "Slow"
        return "Very Slow"

    def _family_group(self, items: List[BaseItemDTO]) -> str:
        if any(item["class_restriction"] or item["staffmod_class"] for item in items):
            return "Class Gear"
        if any(item["defense_min"] is not None for item in items):
            return "Armor"
        return "Weapons"

    @staticmethod
    def _family_class_tags(items: List[BaseItemDTO]) -> List[str]:
        tags = {
            tag
            for item in items
            for tag in (item["class_restriction"], item["staffmod_class"])
            if tag
        }
        return sorted(tags)

    @staticmethod
    def _family_summary(
        items: List[BaseItemDTO],
        group: str,
        class_tags: List[str],
        max_sockets: int,
    ) -> str:
        tiers = " / ".join(item["name"] for item in items)
        details = [group]
        if class_tags:
            details.append(", ".join(class_tags))
        details.append(f"up to {max_sockets} socket{'s' if max_sockets != 1 else ''}")
        fastest = min((item["speed"] for item in items), default=0)
        if fastest < 0:
            details.append(f"fastest speed {fastest}")
        return f"{tiers}. {'; '.join(details)}."

    @staticmethod
    def _family_search_text(items: List[BaseItemDTO], group: str, class_tags: List[str]) -> str:
        parts: List[str] = [group, " ".join(class_tags)]
        for item in items:
            parts.extend(
                [
                    item["name"],
                    item["code"],
                    item["type"],
                    " ".join(item["type_categories"]),
                    item["tier"],
                    item["class_restriction"],
                    item["staffmod_class"],
                    "Two Handed" if item["two_handed_only"] else "",
                    str(item["level"]),
                    str(item["level_req"]),
                    str(item["sockets"]),
                    str(item["speed"]),
                    item["speed_label"],
                    " ".join(item["inherent_stats"]),
                    " ".join(item["auto_prefix_summary"]),
                    " ".join(item["quality_bonus_summary"]),
                ]
            )
        return " ".join(part for part in parts if part)

    def _find_automagic_by_group(self, group_id: str) -> List[Dict[str, str]]:
        return [row for row in self.automagic if row.get('group') == group_id]

    def _automagic_row_applies_to_item_type(self, row: Dict[str, str], item_type_chain: List[str]) -> bool:
        included_types = [row.get(f'itype{i}', '').strip() for i in range(1, 8)]
        excluded_types = [row.get(f'etype{i}', '').strip() for i in range(1, 6)]
        included_types = [code for code in included_types if code]
        excluded_types = [code for code in excluded_types if code]

        if included_types and not any(code in item_type_chain for code in included_types):
            return False
        if excluded_types and any(code in item_type_chain for code in excluded_types):
            return False
        return True

    def _item_type_chain(self, type_code: str) -> List[str]:
        chain: List[str] = []
        seen = set()

        def visit(code: str) -> None:
            code = (code or "").strip()
            if not code or code in seen:
                return
            seen.add(code)
            chain.append(code)
            item_type = self.item_types.get(code, {})
            visit(item_type.get('Equiv1', ''))
            visit(item_type.get('Equiv2', ''))

        visit(type_code)
        return chain

    def _runeword_filter_type_codes(self, runeword_rows: List[Dict[str, str]]) -> set:
        codes = set()
        for row in runeword_rows:
            for index in range(1, 7):
                type_code = row.get(f'itype{index}', '').strip()
                if type_code and type_code != 'xxx':
                    codes.update(self._item_type_chain(type_code))
        return codes

    def _type_categories_for_item_type_chain(self, item_type_chain: List[str]) -> List[str]:
        categories: List[str] = []
        seen = set()
        hidden_codes = {"ac5", "seco"}
        for code in item_type_chain:
            if code in hidden_codes:
                continue
            if self.runeword_filter_type_codes and code not in self.runeword_filter_type_codes:
                continue
            label = self._item_type_label(code)
            key = label.lower()
            if label and key not in seen:
                categories.append(label)
                seen.add(key)
        return categories

    def _item_type_label(self, type_code: str) -> str:
        row = self.item_types.get(type_code, {})
        if not row:
            return ""
        label_key = row.get('ItemType', '').strip()
        return self.repo.get_string(label_key) or label_key or type_code

    def _inherent_stats_for_item_type(self, item_type_chain: List[str]) -> List[str]:
        stats = []
        if 'blun' in item_type_chain:
            stats.append("+50% Damage to Undead")
        return stats

    def _quality_bonus_stats_for_item_type(self, item_type_chain: List[str]) -> List[str]:
        quality_columns = self._quality_columns_for_item_type(item_type_chain)
        if not quality_columns:
            return []

        stats = []
        seen_stats = set()
        for quality_row in self.quality_items:
            if not any(quality_row.get(column) == '1' for column in quality_columns):
                continue

            row_stats = []
            for i in range(1, 3):
                p_code = quality_row.get(f'mod{i}code')
                if p_code and p_code != 'xxx':
                    res = self.resolver.resolve_property(
                        p_code,
                        quality_row.get(f'mod{i}param', ''),
                        quality_row.get(f'mod{i}min', ''),
                        quality_row.get(f'mod{i}max', '')
                    )
                    stat_text = res['resolved_text']
                    if stat_text:
                        row_stats.append(stat_text)

            if not row_stats:
                continue
            combined = " / ".join(row_stats)
            if combined not in seen_stats:
                stats.append(combined)
                seen_stats.add(combined)

        return stats

    def _quality_columns_for_item_type(self, item_type_chain: List[str]) -> set:
        column_map = {
            'weap': 'weapon',
            'armo': 'armor',
            'shld': 'shield',
            'shie': 'shield',
            'ashd': 'shield',
            'scep': 'scepter',
            'wand': 'wand',
            'staf': 'staff',
            'bow': 'bow',
            'xbow': 'bow',
            'boot': 'boots',
            'glov': 'gloves',
            'belt': 'belt',
        }
        return {column for code, column in column_map.items() if code in item_type_chain}

    def _class_restriction_for_item_type(self, item_type_chain: List[str]) -> str:
        for code in item_type_chain:
            class_code = self.item_types.get(code, {}).get('Class', '').strip()
            if class_code:
                return self.class_names.get(class_code, class_code)
        return ""

    def _staffmod_class_for_item_type(self, item_type_chain: List[str]) -> str:
        for code in item_type_chain:
            staffmod_code = self.item_types.get(code, {}).get('StaffMods', '').strip()
            if staffmod_code:
                return self.class_names.get(staffmod_code, staffmod_code)
        return ""
