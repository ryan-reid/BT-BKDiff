from __future__ import annotations
import re
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import (
    D2Repository,
    D2RepositoryProtocol,
    get_class_name_maps,
    resolve_localized_string,
)
from d2lib.models import AnalyzedItemDTO, RunewordDTO, BaseItemDTO, BaseItemFamilyDTO
from d2lib.services.resolver import PropertyResolverService
from d2lib.services.item_types import ItemTypeTaxonomy


class ItemAnalyzerService:
    def __init__(self, repo: D2RepositoryProtocol, resolver: PropertyResolverService):
        self.repo = repo
        self.resolver = resolver
        self.armor = {row['code']: row for row in repo.get_excel_table('armor')}
        self.weapons = {row['code']: row for row in repo.get_excel_table('weapons')}
        self.misc = {row['code']: row for row in repo.get_excel_table('misc')}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}
        self.taxonomy = ItemTypeTaxonomy(repo)
        self.sets: Dict[str, Dict[str, str]] = {}
        for row in repo.get_excel_table('sets'):
            index_key = str(row.get('index', '')).strip()
            name_key = str(row.get('name', '')).strip()
            if index_key and index_key not in self.sets:
                self.sets[index_key] = row
            if name_key and name_key not in self.sets:
                self.sets[name_key] = row
        self.gems = {row['code']: row for row in repo.get_excel_table('gems')}

    def _resolve_runeword_name(self, rw_key: str, comment_name: str) -> str:
        return resolve_localized_string(self.repo, rw_key) or comment_name or rw_key or "Unknown"

    def get_set_display_name(self, set_id: str) -> str:
        clean_id = str(set_id or '').strip()
        if not clean_id:
            return ''
        set_info = self.sets.get(clean_id, {})
        name_key = str(set_info.get('name') or clean_id).strip()
        return resolve_localized_string(self.repo, name_key) or name_key or clean_id

    def get_item_name(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if item: return self.repo.get_string(item.get('namestr', '').strip() or item.get('name', '').strip()) or code
        return code

    def get_item_category(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if not item:
            return "Miscellaneous"
        type_code = item.get('type', '').strip()
        if not type_code or type_code not in self.item_types:
            return "Miscellaneous"
        return self.taxonomy.label(type_code) or "Miscellaneous"

    def get_unique_export_groups(self, raw_row: Dict[str, str]) -> Tuple[str, str, str]:
        """Returns (group_code, granular_code, granular_label) using itemtypes.txt codes."""
        item_code = str(raw_row.get('code', '') or '').strip()
        base = self.armor.get(item_code) or self.weapons.get(item_code) or self.misc.get(item_code) or {}
        if not base:
            return "other", "other", "Other"
        ui_code = self.taxonomy.ui_category_code(base)
        group_code = self.taxonomy.group_code(base)
        granular_code = ui_code or base.get('type', '').strip() or "other"
        granular_label = self.taxonomy.category_label(ui_code) if ui_code else self.get_item_category(item_code)
        return group_code, granular_code, granular_label

    def get_runeword_export_group(self, raw_row: Dict[str, str]) -> Tuple[str, str, str]:
        """Returns (bucket_key, base_code, base_label) dynamically from itemtypes.txt RunewordCategory1/Equiv."""
        itype1 = str(raw_row.get('itype1', '') or '').strip()
        if not itype1 or itype1 == 'xxx':
            return "other", "other", "Other"
        return self.taxonomy.runeword_export_bucket(itype1), itype1.lower(), self.taxonomy.label(itype1)

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
        rw_key = str(row.get('Name', '')).strip()
        comment_name = str(row.get('*Rune Name', '')).strip()
        name = self._resolve_runeword_name(rw_key, comment_name)
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
            base_items.append(self._runeword_base_item_label(base_type))
        rune_properties = self._resolve_runeword_rune_properties(row, itype)

        return {
            "id": rw_key or name,
            "name": name, "runes": runes, "base_items": base_items,
            "required_level": str(max(rune_levels)) if rune_levels else "",
            "properties": props, "rune_properties": rune_properties, "raw_row": row
        }

    def _runeword_base_item_label(self, type_code: str) -> str:
        return self.taxonomy.label(type_code)

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

        set_id = row.get('set', '').strip()
        set_info = self.sets.get(set_id, {})
        is_expansion = set_info.get('version', '0') != '0'

        item_code = row.get('item', '').strip()
        return {
            "id": idx, "display_name": self.repo.get_string(idx), "base_item": self.get_item_name(item_code),
            "item_type": self.get_item_category(item_code), "lvl_req": row.get('lvl req', '0'),
            "properties": props,
            "partial_set_properties": partial_props if partial_props else None,
            "set_name": self.get_set_display_name(set_id),
            "is_expansion": is_expansion,
            "raw_row": row,
        }

class BaseItemAnalyzerService:
    TIER_STRING_KEYS: Dict[str, str] = {
        "normal": "LootFilterNormalQuality",
        "exceptional": "LootFilterExceptionalQuality",
        "elite": "LootFilterEliteQuality",
    }

    def __init__(self, repo: D2RepositoryProtocol, resolver: PropertyResolverService):
        self.repo = repo
        self.resolver = resolver
        self.armor = repo.get_excel_table('armor')
        self.weapons = repo.get_excel_table('weapons')
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}
        self.taxonomy = ItemTypeTaxonomy(repo)
        self.automagic = repo.get_excel_table('automagic')
        self.quality_items = repo.get_excel_table('qualityitems')
        _, self.class_names = get_class_name_maps(repo)

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
                tier_key = ("normal", "exceptional", "elite")[i] if i < 3 else "unknown"
                items_dto.append(self._analyze_item(code_to_item[m_code], tier_key))

            if items_dto:
                group_key = self._family_group_key(items_dto)
                group = self.taxonomy.group_label(group_key)
                class_codes = self._family_class_codes(items_dto)
                class_tags = self._family_class_tags(items_dto)
                max_sockets = max(item["sockets"] for item in items_dto)
                families.append({
                    "name": items_dto[0]["name"],
                    "group": group,
                    "group_key": group_key,
                    "summary": self._family_summary(items_dto, group, class_tags, max_sockets),
                    "class_tags": class_tags,
                    "class_codes": class_codes,
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
        type_name = self.taxonomy.label(type_code) if type_code else ''
        item_type_chain = self.taxonomy.chain(type_code, row.get('type2', ''))
        type_categories = self._type_categories_for_item_type_chain(item_type_chain)
        loot_category_key = self.taxonomy.ui_category_code(row) or "other"
        class_restriction_code = self._class_restriction_code_for_item_type(item_type_chain)
        class_restriction = self.class_names.get(class_restriction_code, class_restriction_code) if class_restriction_code else ""
        staffmod_class_code = self._staffmod_class_code_for_item_type(item_type_chain)
        staffmod_class = self.class_names.get(staffmod_class_code, staffmod_class_code) if staffmod_class_code else ""

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
        tier_key = str(tier or "normal").strip().lower()
        tier_label = self.tier_label(self.repo, tier_key)

        return {
            "code": code,
            "name": name,
            "icon_key": row.get('invfile', '').strip(),
            "icon_src": "",
            "type": type_name,
            "loot_category_key": loot_category_key,
            "loot_category": self.taxonomy.category(row),
            "type_codes": item_type_chain,
            "type_categories": type_categories,
            "level": to_int(row.get('level')),
            "level_req": to_int(row.get('levelreq')),
            "defense_min": to_int(row.get('minac')) if 'minac' in row else None,
            "defense_max": to_int(row.get('maxac')) if 'maxac' in row else None,
            # Keep melee and missile ranges separate; absent modes are not zero-damage attacks.
            "damage_min": to_int(row['mindam']) if row.get('mindam', '').strip() and not two_handed_only else None,
            "damage_max": to_int(row['maxdam']) if row.get('maxdam', '').strip() and not two_handed_only else None,
            "two_hand_damage_min": to_int(row['2handmindam']) if row.get('2handmindam', '').strip() else None,
            "two_hand_damage_max": to_int(row['2handmaxdam']) if row.get('2handmaxdam', '').strip() else None,
            "throw_damage_min": to_int(row['minmisdam']) if row.get('minmisdam', '').strip() else None,
            "throw_damage_max": to_int(row['maxmisdam']) if row.get('maxmisdam', '').strip() else None,
            "two_handed_only": two_handed_only,
            "str_req": to_int(row.get('reqstr')),
            "dex_req": to_int(row.get('reqdex')),
            "block": to_int(row.get('block')),
            "sockets": max(max_sockets_by_ilvl.values()),
            "max_sockets_by_ilvl": max_sockets_by_ilvl,
            "class_restriction_code": class_restriction_code,
            "class_restriction": class_restriction,
            "staffmod_class_code": staffmod_class_code,
            "staffmod_class": staffmod_class,
            "magic_level": to_int(row.get('magic lvl')),
            "inherent_stats": inherent_stats,
            "auto_prefix_stats": auto_prefix_stats,
            "auto_prefix_summary": auto_prefix_summary,
            "quality_bonus_stats": quality_bonus_stats,
            "quality_bonus_summary": quality_bonus_summary,
            "speed": speed,
            "durability": to_int(row.get('nodurability')) if row.get('nodurability') == '1' else to_int(row.get('durability')),
            "tier_key": tier_key,
            "tier": tier_label,
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
    def is_weapon_item(item: BaseItemDTO) -> bool:
        return item.get("defense_min") is None

    @classmethod
    def tier_label(cls, repo: D2RepositoryProtocol, tier_key: str) -> str:
        clean = str(tier_key or "normal").strip().lower()
        str_key = cls.TIER_STRING_KEYS.get(clean)
        if str_key:
            resolved = resolve_localized_string(repo, str_key)
            if resolved:
                return resolved
        return clean.title() if clean else ""

    @classmethod
    def tier_options(cls, families: List[BaseItemFamilyDTO]) -> List[Dict[str, str]]:
        present: Dict[str, str] = {}
        for family in families:
            for item in family["members"]:
                key = str(item.get("tier_key") or item.get("tier") or "").strip().lower()
                if not key:
                    continue
                label = str(item.get("tier") or key).strip()
                if key not in present or label:
                    present[key] = label or key
        order = {key: idx for idx, key in enumerate(cls.TIER_STRING_KEYS)}
        return [
            {"key": key, "label": present[key]}
            for key in sorted(present, key=lambda k: (order.get(k, len(order)), k))
        ]

    @classmethod
    def speed_options(cls, families: List[BaseItemFamilyDTO]) -> List[Dict[str, str]]:
        speeds = sorted(
            {
                int(item["speed"])
                for family in families
                for item in family["members"]
                if cls.is_weapon_item(item)
            }
        )
        return [{"key": str(speed), "label": str(speed)} for speed in speeds]

    @staticmethod
    def _family_group_key(items: List[BaseItemDTO]) -> str:
        if any(item["defense_min"] is not None for item in items):
            return "armor"
        return "weapons"

    def _family_group(self, items: List[BaseItemDTO]) -> str:
        return self.taxonomy.group_label(self._family_group_key(items))

    @staticmethod
    def _family_class_codes(items: List[BaseItemDTO]) -> List[str]:
        codes = {
            code
            for item in items
            for code in (item.get("class_restriction_code", ""), item.get("staffmod_class_code", ""))
            if code
        }
        return sorted(codes)

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

    def _type_categories_for_item_type_chain(self, item_type_chain: List[str]) -> List[str]:
        categories: List[str] = []
        seen = set()
        hidden_codes = {"ac5", "clas"}
        for code in item_type_chain:
            if code in hidden_codes:
                continue
            label = self.taxonomy.label(code)
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
        stats: List[str] = []
        if 'blun' in item_type_chain:
            undead_text = ""
            if self.resolver is not None:
                res = self.resolver.resolve_property("dmg-undead", "", "50", "50")
                candidate = str(res.get("resolved_text", "") or "").strip()
                if candidate and not candidate.startswith("Unknown property"):
                    undead_text = candidate
            if not undead_text:
                mod_str = resolve_localized_string(self.repo, "ModStr4f")
                if mod_str:
                    undead_text = mod_str.replace("%+d", "+50").replace("%d", "50").replace("%%", "%")
            stats.append(undead_text or "+50% Damage to Undead")
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

    def _class_restriction_code_for_item_type(self, item_type_chain: List[str]) -> str:
        for code in item_type_chain:
            class_code = self.item_types.get(code, {}).get('Class', '').strip()
            if class_code:
                return class_code.casefold()
        return ""

    def _class_restriction_for_item_type(self, item_type_chain: List[str]) -> str:
        class_code = self._class_restriction_code_for_item_type(item_type_chain)
        return self.class_names.get(class_code, class_code) if class_code else ""

    def _staffmod_class_code_for_item_type(self, item_type_chain: List[str]) -> str:
        for code in item_type_chain:
            staffmod_code = self.item_types.get(code, {}).get('StaffMods', '').strip()
            if staffmod_code:
                return staffmod_code.casefold()
        return ""

    def _staffmod_class_for_item_type(self, item_type_chain: List[str]) -> str:
        staffmod_code = self._staffmod_class_code_for_item_type(item_type_chain)
        return self.class_names.get(staffmod_code, staffmod_code) if staffmod_code else ""
