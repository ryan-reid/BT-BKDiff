from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

from d2lib.repository import (
    D2RepositoryProtocol,
    get_class_name_maps,
    resolve_difficulty_name,
    resolve_localized_string,
)
from d2lib.services.resolver import PropertyResolverService


class AffixTier(NamedTuple):
    properties: Tuple[str, ...]
    settings: Tuple[str, ...]
    identity: Dict[str, Any]
    item_types: Dict[str, str]
    spawnable: bool
    can_roll_on_rares: bool
    property_details: Tuple[Dict[str, Any], ...] = ()
    excludes: Optional[Dict[str, str]] = None
    setting_entries: Tuple[Tuple[str, str], ...] = ()


REFERENCE_GROUPS = [
    {
        "slug": "affixes",
        "title": "Affixes",
        "description": "Browse prefixes and suffixes by function or compare individual affix rolls.",
        "tables": [
            {"name": "magicprefix", "title": "Magic Prefixes", "fields": ["group", "level", "maxlevel", "frequency", "spawnable", "itype1", "itype2", "etype1", "etype2"], "properties": "mod"},
            {"name": "magicsuffix", "title": "Magic Suffixes", "fields": ["group", "level", "maxlevel", "frequency", "spawnable", "itype1", "itype2", "etype1", "etype2"], "properties": "mod"},
        ],
    },
    {
        "slug": "automagic",
        "title": "Automagic",
        "description": "Compare automatic item modifiers, their roll ranges, and the item types and groups they apply to.",
        "tables": [
            {"name": "automagic", "title": "Automatic Modifiers", "fields": ["group", "level", "maxlevel", "frequency", "itype1", "itype2", "etype1", "etype2"], "properties": "mod"},
        ],
    },
    {
        "slug": "monster-specials",
        "title": "Monster Specials",
        "description": "Superuniques, monster level tables, animations, unique modifiers, and monster property hooks.",
        "tables": [
            {"name": "superuniques", "title": "Superuniques", "fields": ["Name", "Class", "Mod1", "Mod2", "Mod3", "TC(H)", "TC(H) Desecrated"]},
            {"name": "monprop", "title": "Monster Properties", "fields": ["Id", "prop1", "par1", "min1", "max1", "prop2", "par2", "min2", "max2"], "properties": "prop"},
            {"name": "monai", "title": "Monster AI Parameters", "fields": ["AI", "*aip1", "*aip2", "*aip3", "*aip4", "*aip5", "*aip6", "*aip7", "*aip8"]},
            {"name": "monumod", "title": "Unique Monster Modifiers", "fields": ["uniquemod", "id", "enabled", "version", "xfer"]},
            {"name": "monlvl", "title": "Monster Levels", "fields": ["Level", "L-AC", "L-TH", "L-HP", "AC(H)", "TH(H)", "HP(H)"]},
            {"name": "monstats2", "title": "Monster Animation Data", "fields": ["Id", "Height", "OverlayHeight", "mDT", "mNU", "mWL", "mA1", "mA2", "mS1", "mS2", "mS3"]},
        ],
    },
    {
        "slug": "economy",
        "title": "Mercs, Vendors & Economy",
        "description": "Hirelings, vendor inventory flags, gambling rows, and inventory layout data.",
        "tables": [
            {"name": "hireling", "title": "Hirelings", "fields": ["Hireling", "Act", "Difficulty", "HireDesc", "Version", "Id", "Class", "Level", "Gold", "Skill1", "Skill2", "Skill3", "Skill4"]},
            {"name": "npc", "title": "NPC Vendors", "fields": ["npc", "buy mult", "sell mult", "rep mult", "questflag A", "questbuymult A", "questsellmult A"]},
            {"name": "gamble", "title": "Gambling", "fields": ["name", "code"]},
            {"name": "inventory", "title": "Inventory Layout", "fields": ["class", "invLeft", "invRight", "invTop", "invBottom", "gridX", "gridY", "gridLeft", "gridRight", "gridTop", "gridBottom"]},
        ],
    },
    {
        "slug": "states-shrines",
        "title": "States & Shrines",
        "description": "State flags, shrine effects, and overlays used by skills, monsters, and temporary buffs.",
        "tables": [
            {"name": "states", "title": "States", "fields": ["state", "*ID", "group", "remhit", "nosend", "aura", "hide", "pgsv", "overlay1", "overlay2", "stat", "setfunc", "remfunc"]},
            {"name": "shrines", "title": "Shrines", "fields": ["StringName", "StringPhrase", "*Shrine Type", "*Effect", "Code", "Arg0", "Arg1", "Duration in frames", "reset time in minutes", "rarity", "LevelMin"]},
            {"name": "overlay", "title": "Overlays", "fields": ["overlay", "Filename", "version", "*Frames", "Character", "PreDraw", "1ofN"]},
        ],
    },
    {
        "slug": "area-structure",
        "title": "Area Structure",
        "description": "Maze rules, presets, warps, monster presets, and object rows that support area route pages.",
        "tables": [
            {"name": "lvlmaze", "title": "Maze Levels", "fields": ["Name", "Level", "Rooms", "Rooms(N)", "Rooms(H)", "SizeX", "SizeY", "Merge"]},
            {"name": "lvlprest", "title": "Level Presets", "fields": ["Name", "Def", "LevelId", "Populate", "Logicals", "Outdoors", "Animate", "KillEdge"]},
            {"name": "lvlwarp", "title": "Level Warps", "fields": ["Name", "Id", "SelectX", "SelectY", "SelectDX", "SelectDY", "ExitWalkX", "ExitWalkY"]},
            {"name": "monpreset", "title": "Monster Presets", "fields": ["Act", "Place"]},
            {"name": "objects", "title": "Objects", "fields": ["Name", "*ID", "Class", "Token", "Selectable0", "SizeX", "SizeY", "FrameCnt0", "FrameCnt1"]},
        ],
    },
    {
        "slug": "skill-support",
        "title": "Skill Support Tables",
        "description": "Raw skill, skill description, missile, and monster sequence rows that explain advanced skill behavior.",
        "tables": [
            {"name": "skills", "title": "Skills", "fields": ["skill", "charclass", "skilldesc", "srvstfunc", "srvdofunc", "cltstfunc", "cltdofunc", "aurastate", "passivestate", "Param1", "calc1"]},
            {"name": "skilldesc", "title": "Skill Descriptions", "fields": ["skilldesc", "str name", "desctexta1", "desccalca1", "desctexta2", "desccalca2"]},
            {"name": "missiles", "title": "Missiles", "fields": ["Missile", "*ID", "pCltDoFunc", "pSrvDoFunc", "Vel", "MaxVel", "Range", "Skill", "HitClass"]},
            {"name": "monseq", "title": "Monster Sequences", "fields": ["sequence", "mode", "frame", "dir", "event"]},
        ],
    },
]


class ReferenceAnalyzerService:
    def __init__(self, repo: D2RepositoryProtocol, resolver: Optional[PropertyResolverService] = None):
        self.repo = repo
        self.resolver = resolver or PropertyResolverService(repo)
        _, self.class_names = get_class_name_maps(repo)
        self._monstats_by_hcidx: Dict[str, str] = {}
        self._monstats_by_id: Dict[str, str] = {}
        self._monstats_by_ex: Dict[str, str] = {}
        self._monstats_by_prop: Dict[str, str] = {}
        self._base_item_by_code: Dict[str, str] = {}
        self._build_reference_lookups()

    def _build_reference_lookups(self) -> None:
        for row in self.repo.get_excel_table("monstats"):
            namestr = str(row.get("NameStr", "")).strip()
            localized = resolve_localized_string(self.repo, namestr) or namestr
            if not localized:
                continue
            hcidx = str(row.get("*hcIdx", "")).strip()
            mon_id = str(row.get("Id", "")).strip().casefold()
            mon_ex = str(row.get("MonStatsEx", "")).strip().casefold()
            mon_prop = str(row.get("MonProp", "")).strip().casefold()
            if hcidx and hcidx not in self._monstats_by_hcidx:
                self._monstats_by_hcidx[hcidx] = localized
            if mon_id and mon_id not in self._monstats_by_id:
                self._monstats_by_id[mon_id] = localized
            if mon_ex and mon_ex not in self._monstats_by_ex:
                self._monstats_by_ex[mon_ex] = localized
            if mon_prop and mon_prop not in self._monstats_by_prop:
                self._monstats_by_prop[mon_prop] = localized

        for table in ("weapons", "armor", "misc"):
            for row in self.repo.get_excel_table(table):
                code = str(row.get("code", "")).strip().casefold()
                if not code or code in self._base_item_by_code:
                    continue
                namestr = str(row.get("namestr", "")).strip()
                raw_name = str(row.get("name", "")).strip()
                localized = (
                    resolve_localized_string(self.repo, namestr)
                    or resolve_localized_string(self.repo, raw_name)
                    or raw_name
                    or namestr
                )
                if localized:
                    self._base_item_by_code[code] = localized

    def build_pages(
        self,
        available_tables: Optional[Iterable[str]] = None,
        baseline: Optional[ReferenceAnalyzerService] = None,
    ) -> List[Dict[str, Any]]:
        available = set(available_tables or [])
        pages: List[Dict[str, Any]] = []
        for group in REFERENCE_GROUPS:
            sections = [self._section(config) for config in group["tables"]]
            if baseline is not None:
                for section in sections:
                    if section["table"] in {"magicprefix", "magicsuffix", "automagic"}:
                        section["comparison_rows"] = self._compare_affixes(section["table"], baseline)
            row_count = sum(section["row_count"] for section in sections)
            present_tables = [
                section["table"]
                for section in sections
                if section["row_count"] or not available or section["table"] in available
            ]
            pages.append(
                {
                    "slug": group["slug"],
                    "title": group["title"],
                    "description": group["description"],
                    "sections": sections,
                    "row_count": row_count,
                    "source_tables": present_tables,
                    "search_text": f"{group['title']} {group['description']} " + " ".join(present_tables),
                }
            )
        return pages

    def _compare_affixes(self, table: str, baseline: ReferenceAnalyzerService) -> List[Dict[str, Any]]:
        def display_tiers(tiers: List[AffixTier], shared: Counter) -> List[Dict[str, Any]]:
            remaining = shared.copy()
            result = []
            for tier in tiers:
                signature = (tier.properties, tier.settings)
                result.append({
                    "properties": tier.properties, "settings": tier.settings, "identity": tier.identity,
                    "item_types": tier.item_types,
                    "excludes": dict(tier.excludes or {}),
                    "setting_entries": list(tier.setting_entries),
                    "spawnable": tier.spawnable,
                    "can_roll_on_rares": tier.can_roll_on_rares,
                    "changed": remaining[signature] <= 0,
                })
                remaining[signature] -= 1
            return result

        item_types = {**baseline._item_type_names(), **self._item_type_names()}
        class_names = {**baseline.class_names, **self.class_names}
        current = self.affix_groups(table, item_types, class_names=class_names)
        old = baseline.affix_groups(table, item_types, class_names=class_names)
        rows = []
        for key in sorted(old.keys() | current.keys()):
            label, new_tiers = current.get(key, ("", []))
            old_label, old_tiers = old.get(key, ("", []))
            # A name can have multiple tiers and the source tables lack a stable
            # tier ID. Compare their contents as a multiset, independent of order.
            shared = Counter(tier[:2] for tier in old_tiers) & Counter(tier[:2] for tier in new_tiers)
            status = (
                "Added" if not old_tiers else "Removed" if not new_tiers
                else "Unchanged" if len(old_tiers) == len(new_tiers) == shared.total()
                else "Changed"
            )

            rows.append({
                "label": label or old_label,
                "status": status,
                "old": display_tiers(old_tiers, shared),
                "new": display_tiers(new_tiers, shared),
                "search_text": " ".join([
                    label, old_label, key, status,
                    *(part for tier in old_tiers + new_tiers for part in (*tier.properties, *tier.settings)),
                ]),
            })
        return sorted(rows, key=lambda row: row["label"].casefold())

    def _item_type_names(self) -> Dict[str, str]:
        from d2lib.services.item_types import ItemTypeTaxonomy, is_loot_filter_shorthand

        taxonomy = ItemTypeTaxonomy(self.repo)
        names = {
            row["Code"]: taxonomy.label(row["Code"])
            for row in self.repo.get_excel_table("itemtypes")
            if row.get("Code")
        }
        base_names: Dict[str, Set[str]] = {}
        unresolved_types: Set[str] = set()
        for table in ("misc", "armor", "weapons"):
            for row in self.repo.get_excel_table(table):
                if row.get("quest") not in (None, "", "0"):
                    continue
                code = row.get("type", "")
                key = row.get("namestr", "")
                display_name = self.repo.get_string(key)
                if not code:
                    continue
                if not key or not display_name or display_name == key:
                    unresolved_types.add(code)
                else:
                    base_names.setdefault(code, set()).add(display_name)
        # Broad categories contain several base items and retain their type label.
        for code, display_names in base_names.items():
            if len(display_names) == 1 and code not in unresolved_types:
                candidate = next(iter(display_names))
                if not is_loot_filter_shorthand(candidate):
                    names[code] = candidate
        return names

    def affix_groups(
        self,
        table: str,
        item_types: Optional[Dict[str, str]] = None,
        class_names: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Tuple[str, List[AffixTier]]]:
        if item_types is None:
            item_types = self._item_type_names()
        resolved_classes = self.class_names if class_names is None else class_names
        groups: Dict[str, Tuple[str, List[AffixTier]]] = {}
        for row in self.repo.get_excel_table(table):
            name = row.get("Name", "")
            property_details = self._properties(row, "mod")
            properties = tuple(sorted(prop["text"] for prop in property_details))
            if not name or not properties:
                continue

            settings: List[str] = []
            setting_entries: List[Tuple[str, str]] = []

            def add_setting(entry_key: str, text_value: str) -> None:
                settings.append(text_value)
                setting_entries.append((entry_key, text_value))

            identity = {field: row.get(field, "") for field in (
                "version", "group", "level", "levelreq", "class", "spawnable",
            )}
            identity["properties"] = sorted({row.get(f"mod{i}code", "") for i in range(1, 4)} - {""})
            type_labels: Dict[str, str] = {}
            excludes_labels: Dict[str, str] = {}
            for prefix, count, label in (("itype", 7, "Item types"), ("etype", 5, "Excludes")):
                codes = sorted({row.get(f"{prefix}{i}", "") for i in range(1, count + 1)} - {""})
                identity[prefix] = codes
                names = {code: f"{item_types[code]} ({code})" if code in item_types else code for code in codes}
                if prefix == "itype":
                    type_labels = names
                else:
                    excludes_labels = names
                if names:
                    add_setting(prefix, f"{label} · {', '.join(names.values())}")
            spawn = row.get("spawnable", "")
            spawn_label = {"1": "Spawnable", "0": "Disabled", "": "Disabled"}.get(spawn, f"Spawn flag {spawn}")
            if spawn == "1" and row.get("frequency") in ("", "0"):
                spawn_label = "Disabled (zero weight)"
            add_setting("spawnable", spawn_label)
            spawnable = spawn_label == "Spawnable"
            can_roll_on_rares = spawnable and row.get("rare") == "1"
            if spawnable:
                add_setting("rare", "Can roll on rares" if can_roll_on_rares else "No rare rolls")
            for field, label in (
                ("level", "Affix level"), ("maxlevel", "Max affix level"), ("levelreq", "Required level"),
                ("class", "Class"), ("classlevelreq", "Class required level"), ("frequency", "Weight"),
                ("group", "Group"), ("version", "Version"),
            ):
                if row.get(field):
                    display_value = (
                        resolved_classes.get(row[field].strip().casefold(), row[field])
                        if field == "class" else row[field]
                    )
                    add_setting(field, f"{label} {display_value}")
            _, tiers = groups.setdefault(name.casefold(), (self.repo.get_string(name) or name, []))
            tiers.append(AffixTier(
                properties, tuple(settings), identity, type_labels, spawnable, can_roll_on_rares,
                tuple(property_details), excludes_labels, tuple(setting_entries),
            ))
        return groups

    def build_coverage(
        self,
        pages: List[Dict[str, Any]],
        available_tables: Iterable[str],
        extra_coverage: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        covered: Dict[str, str] = dict(extra_coverage or {})
        for page in pages:
            for table in page["source_tables"]:
                covered[table] = page["title"]

        rows = []
        for table in sorted(set(available_tables)):
            table_rows = self.repo.get_excel_table(table)
            rows.append(
                {
                    "table": table,
                    "row_count": len(table_rows),
                    "coverage": covered.get(table, "Not yet mapped"),
                    "status": "covered" if table in covered else "unmapped",
                    "search_text": f"{table} {covered.get(table, 'Not yet mapped')}",
                }
            )
        return {
            "summary": {
                "table_count": len(rows),
                "covered_count": sum(1 for row in rows if row["status"] == "covered"),
                "unmapped_count": sum(1 for row in rows if row["status"] == "unmapped"),
            },
            "rows": rows,
        }

    def _section(self, config: Dict[str, Any]) -> Dict[str, Any]:
        table_name = config["name"]
        rows = [
            self._row(table_name, raw, config)
            for raw in self.repo.get_excel_table(table_name)
            if self._has_display_content(raw)
        ]
        return {
            "table": table_name,
            "title": config["title"],
            "rows": rows,
            "row_count": len(rows),
        }

    def _row(self, table_name: str, raw: Dict[str, str], config: Dict[str, Any]) -> Dict[str, Any]:
        field_names = config.get("fields", [])
        label = self._label(table_name, raw, config)
        fields = self._fields(table_name, raw, field_names)
        properties = self._properties(raw, config.get("properties", ""))
        search_parts = [label, table_name]
        search_parts.extend(field["value"] for field in fields)
        search_parts.extend(prop["text"] for prop in properties)
        # Preserve raw identifiers alongside localized values for searchability.
        raw_candidates = [raw.get(name, "") for name in field_names]
        raw_candidates.extend(
            raw.get(key, "")
            for key in ("StringName", "Name", "name", "skill", "skilldesc", "HireDesc", "Skill1", "Id", "Class", "code")
        )
        seen_terms = {part.casefold() for part in search_parts if part}
        for candidate in raw_candidates:
            clean = str(candidate or "").strip()
            if clean and clean != "0" and clean.casefold() not in seen_terms:
                seen_terms.add(clean.casefold())
                search_parts.append(clean)
        return {
            "label": label,
            "fields": fields,
            "properties": properties,
            "search_text": " ".join(part for part in search_parts if part),
        }

    @staticmethod
    def _has_display_content(row: Dict[str, str]) -> bool:
        for key, value in row.items():
            if key.lower().endswith("eol"):
                continue
            text = str(value).strip()
            if text and text != "0":
                return True
        return False

    def _resolve_monster_name(self, key: str) -> str:
        clean = str(key or "").strip()
        if not clean:
            return ""
        cf = clean.casefold()
        return (
            self._monstats_by_id.get(cf)
            or self._monstats_by_ex.get(cf)
            or self._monstats_by_prop.get(cf)
            or resolve_localized_string(self.repo, clean)
            or clean
        )

    def _label(self, table_name: str, row: Dict[str, str], config: Dict[str, Any]) -> str:
        if table_name == "shrines":
            for key in ("StringName", "Name", "*Shrine Type"):
                value = str(row.get(key, "")).strip()
                if value:
                    return resolve_localized_string(self.repo, value) or value
        elif table_name == "hireling":
            class_id = str(row.get("Class", "")).strip()
            group_name = self._monstats_by_hcidx.get(class_id) or str(row.get("Hireling", "")).strip()
            group_name = resolve_localized_string(self.repo, group_name) or group_name
            hire_desc = str(row.get("HireDesc", "")).strip()
            skill1 = str(row.get("Skill1", "")).strip()
            variant = (
                (resolve_localized_string(self.repo, hire_desc) or hire_desc)
                if hire_desc
                else ((self.resolver.resolve_skill_name(skill1) or skill1) if skill1 else "")
            )
            diff = resolve_difficulty_name(self.repo, row.get("Difficulty", ""))
            parts = [part for part in (group_name, variant, diff) if part]
            if parts:
                return " · ".join(parts)
        elif table_name == "skills":
            raw_skill = str(row.get("skill", "")).strip()
            if raw_skill:
                return self.resolver.resolve_skill_name(raw_skill) or raw_skill
        elif table_name == "skilldesc":
            str_name = str(row.get("str name", "")).strip()
            if str_name:
                resolved = resolve_localized_string(self.repo, str_name)
                if resolved:
                    return resolved
        elif table_name == "superuniques":
            raw_name = str(row.get("Name", "")).strip()
            if raw_name:
                return resolve_localized_string(self.repo, raw_name) or raw_name
        elif table_name == "gamble":
            code = str(row.get("code", "")).strip().casefold()
            raw_name = str(row.get("name", "")).strip()
            localized = self._base_item_by_code.get(code) or resolve_localized_string(self.repo, raw_name) or raw_name
            if localized:
                return localized
        elif table_name in {"monstats2", "monprop"}:
            mon_id = str(row.get("Id", "")).strip()
            if mon_id:
                return self._resolve_monster_name(mon_id)
        elif table_name == "monpreset":
            act = str(row.get("Act", "")).strip()
            place = str(row.get("Place", "")).strip()
            if act and place:
                return f"Act {act} · {self._resolve_monster_name(place)}"
        elif table_name == "inventory":
            cls = str(row.get("class", "")).strip()
            if cls:
                return resolve_localized_string(self.repo, cls) or cls

        for key in (
            "Name",
            "name",
            "StringName",
            "skill",
            "skilldesc",
            "state",
            "Shrine Type",
            "Id",
            "id",
            "Missile",
            "Sequence",
            "sequence",
            "Hireling",
            "npc",
            "overlay",
            "Class",
            "class",
            "Level",
        ):
            value = str(row.get(key, "")).strip()
            if value:
                return resolve_localized_string(self.repo, value) or value
        return config["title"]

    def _format_field_value(self, table_name: str, field_name: str, value: str, row: Dict[str, str]) -> str:
        if table_name == "shrines" and field_name in {"StringName", "StringPhrase"}:
            return resolve_localized_string(self.repo, value) or value
        if table_name == "hireling":
            if field_name == "Hireling":
                class_id = str(row.get("Class", "")).strip()
                return self._monstats_by_hcidx.get(class_id) or resolve_localized_string(self.repo, value) or value
            if field_name == "Difficulty":
                return resolve_difficulty_name(self.repo, value)
            if field_name == "HireDesc":
                return resolve_localized_string(self.repo, value) or value
            if field_name.startswith("Skill"):
                return self.resolver.resolve_skill_name(value) or value
        if table_name == "skills":
            if field_name == "skill":
                return self.resolver.resolve_skill_name(value) or value
            if field_name == "charclass":
                return self.class_names.get(value.casefold(), value)
        if table_name == "skilldesc" and field_name in {"str name", "desctexta1", "desctexta2"}:
            return resolve_localized_string(self.repo, value) or value
        if table_name == "missiles" and field_name == "Skill":
            return self.resolver.resolve_skill_name(value) or value
        if table_name == "superuniques":
            if field_name == "Name":
                return resolve_localized_string(self.repo, value) or value
            if field_name == "Class":
                return self._monstats_by_id.get(value.casefold(), value)
        if table_name == "gamble" and field_name == "name":
            code = str(row.get("code", "")).strip().casefold()
            return self._base_item_by_code.get(code) or resolve_localized_string(self.repo, value) or value
        if table_name == "inventory" and field_name == "class":
            return resolve_localized_string(self.repo, value) or value
        return value

    def _fields(self, table_name: str, row: Dict[str, str], field_names: List[str]) -> List[Dict[str, str]]:
        fields: List[Dict[str, str]] = []
        seen: Set[str] = set()
        for name in field_names:
            if name in seen:
                continue
            seen.add(name)
            value = str(row.get(name, "")).strip()
            if value and value != "0":
                fields.append({"label": name, "value": self._format_field_value(table_name, name, value, row)})
        return fields

    def _properties(self, row: Dict[str, str], mode: str) -> List[Dict[str, str]]:
        if mode == "mod":
            return self._property_series(row, "mod", "code", "param", "min", "max", 6)
        if mode == "prop":
            return self._monster_property_series(row)
        return []

    def _monster_property_series(self, row: Dict[str, str]) -> List[Dict[str, str]]:
        properties: List[Dict[str, str]] = []
        for index in range(1, 7):
            code = str(row.get(f"prop{index}", "")).strip()
            if not code:
                continue
            param = str(row.get(f"par{index}", "")).strip()
            min_val = str(row.get(f"min{index}", "")).strip()
            max_val = str(row.get(f"max{index}", "")).strip()
            text = self.resolver.resolve_property(code, param, min_val, max_val).get("resolved_text", "")
            properties.append({"code": code, "text": text or code})
        return properties

    def _property_series(
        self,
        row: Dict[str, str],
        prefix: str,
        code_suffix: str,
        param_suffix: str,
        min_suffix: str,
        max_suffix: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        properties: List[Dict[str, Any]] = []
        cold_duration = None
        for index in range(1, count + 1):
            code_key = f"{prefix}{index}{code_suffix}"
            code = str(row.get(code_key, "")).strip()
            if not code:
                continue
            param = str(row.get(f"{prefix}{index}{param_suffix}", "")).strip()
            min_val = str(row.get(f"{prefix}{index}{min_suffix}", "")).strip()
            max_val = str(row.get(f"{prefix}{index}{max_suffix}", "")).strip()
            prop_dto = self.resolver.resolve_property(code, param, min_val, max_val)
            text = prop_dto.get("resolved_text", "")
            normalized_code = prop_dto.get("canonical_code") or code.lower()
            duration = self.resolver.cold_duration(normalized_code, param, min_val, max_val)
            if duration:
                low, high, replaces = duration
                if cold_duration is None or replaces:
                    cold_duration = (low, high)
                else:
                    cold_duration = (cold_duration[0] + low, cold_duration[1] + high)
            if normalized_code == "cold-len" and duration:
                continue
            if normalized_code == "dmg-cold":
                text = prop_dto.get("base_text") or text
            properties.append({
                "code": code,
                "canonical_code": normalized_code,
                "text": text or code,
                "param": param,
                "min_val": min_val,
                "max_val": max_val,
                "stats": tuple(prop_dto.get("stats") or ()),
                "label": prop_dto.get("label") or "",
                "numeric_values": tuple(prop_dto.get("numeric_values") or ()),
                "parameter_key": prop_dto.get("parameter_key") or "",
                "is_unknown": bool(prop_dto.get("is_unknown", False)),
            })
        if cold_duration is not None:
            low, high = (str(value) for value in cold_duration)
            cold_dto = self.resolver.resolve_property("cold-len", "", low, high)
            properties.append({
                "code": "cold-len",
                "canonical_code": "cold-len",
                "text": cold_dto.get("resolved_text", ""),
                "param": "",
                "min_val": low,
                "max_val": high,
                "stats": tuple(cold_dto.get("stats") or ("coldlength",)),
                "label": cold_dto.get("label") or "",
                "numeric_values": tuple(cold_dto.get("numeric_values") or ()),
                "parameter_key": cold_dto.get("parameter_key") or "",
                "is_unknown": bool(cold_dto.get("is_unknown", False)),
            })
        return properties
