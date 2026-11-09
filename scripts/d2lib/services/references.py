from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

from d2lib.repository import D2RepositoryProtocol
from d2lib.services.resolver import PropertyResolverService


class AffixTier(NamedTuple):
    properties: Tuple[str, ...]
    settings: Tuple[str, ...]
    identity: Dict[str, Any]


REFERENCE_GROUPS = [
    {
        "slug": "affixes",
        "title": "Affixes",
        "description": "Compare magic prefixes and suffixes, their roll ranges, and the items they can appear on.",
        "tables": [
            {"name": "magicprefix", "title": "Magic Prefixes", "fields": ["group", "level", "maxlevel", "frequency", "spawnable", "itype1", "itype2", "etype1", "etype2"], "properties": "mod"},
            {"name": "magicsuffix", "title": "Magic Suffixes", "fields": ["group", "level", "maxlevel", "frequency", "spawnable", "itype1", "itype2", "etype1", "etype2"], "properties": "mod"},
            {"name": "qualityitems", "title": "Quality Item Modifiers", "fields": ["armor", "weapon", "shield", "scepter", "wand", "staff", "bow", "boots", "gloves", "belt"], "properties": "mod"},
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
            {"name": "monlvl", "title": "Monster Levels", "fields": ["Level", "L-AC", "L-TH", "L-HP", "H-AC", "H-TH", "H-HP"]},
            {"name": "monstats2", "title": "Monster Animation Data", "fields": ["Id", "Height", "OverlayHeight", "mDT", "mNU", "mWL", "mA1", "mA2", "mS1", "mS2", "mS3"]},
        ],
    },
    {
        "slug": "economy",
        "title": "Mercs, Vendors & Economy",
        "description": "Hirelings, vendor inventory flags, gambling rows, and inventory layout data.",
        "tables": [
            {"name": "hireling", "title": "Hirelings", "fields": ["Hireling", "SubType", "Version", "Id", "Class", "Level", "Gold", "Skill1", "Skill2", "Skill3", "Skill4"]},
            {"name": "npc", "title": "NPC Vendors", "fields": ["npc", "sellmult", "buymult", "questflag A", "questbuymult A", "questsellmult A"]},
            {"name": "gamble", "title": "Gambling", "fields": ["name", "code", "rarity", "level"]},
            {"name": "inventory", "title": "Inventory Layout", "fields": ["class", "invLeft", "invRight", "invTop", "invBottom", "gridX", "gridY", "gridLeft", "gridRight", "gridTop", "gridBottom"]},
        ],
    },
    {
        "slug": "states-shrines",
        "title": "States & Shrines",
        "description": "State flags, shrine effects, and overlays used by skills, monsters, and temporary buffs.",
        "tables": [
            {"name": "states", "title": "States", "fields": ["state", "id", "group", "remhit", "nosend", "aura", "hide", "pgsv", "overlay1", "overlay2", "stat", "setfunc", "remfunc"]},
            {"name": "shrines", "title": "Shrines", "fields": ["Shrine Type", "Name", "Effect", "Code", "Arg0", "Arg1", "duration in frames", "reset time in minutes"]},
            {"name": "overlay", "title": "Overlays", "fields": ["overlay", "Filename", "Version", "Frames", "Character", "PreDraw", "1ofN"]},
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
            {"name": "monpreset", "title": "Monster Presets", "fields": ["Act", "Place", "Mon1", "Mon2", "Mon3", "Mon4", "Mon5"]},
            {"name": "objects", "title": "Objects", "fields": ["Name", "Id", "Token", "Selectable0", "TrapProb", "SizeX", "SizeY", "FrameCnt0", "FrameCnt1"]},
        ],
    },
    {
        "slug": "skill-support",
        "title": "Skill Support Tables",
        "description": "Raw skill, skill description, missile, and monster sequence rows that explain advanced skill behavior.",
        "tables": [
            {"name": "skills", "title": "Skills", "fields": ["skill", "charclass", "skilldesc", "srvstfunc", "srvdofunc", "cltstfunc", "cltdofunc", "aurastate", "passivestate", "Param1", "calc1"]},
            {"name": "skilldesc", "title": "Skill Descriptions", "fields": ["skilldesc", "str name", "desctexta1", "desccalca1", "desctexta2", "desccalca2"]},
            {"name": "missiles", "title": "Missiles", "fields": ["Missile", "Id", "pCltDoFunc", "pSrvDoFunc", "Vel", "MaxVel", "Range", "Skill", "HitClass"]},
            {"name": "monseq", "title": "Monster Sequences", "fields": ["Sequence", "Mode", "Frame1", "Frame2", "Frame3", "Dir", "Event"]},
        ],
    },
]


class ReferenceAnalyzerService:
    def __init__(self, repo: D2RepositoryProtocol, resolver: Optional[PropertyResolverService] = None):
        self.repo = repo
        self.resolver = resolver or PropertyResolverService(repo)

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
                    "changed": remaining[signature] <= 0,
                })
                remaining[signature] -= 1
            return result

        item_types = {
            row["Code"]: row["ItemType"]
            for repo in (baseline.repo, self.repo)
            for row in repo.get_excel_table("itemtypes")
            if row.get("Code") and row.get("ItemType")
        }
        current = self._affix_groups(table, item_types)
        old = baseline._affix_groups(table, item_types)
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

    def _affix_groups(self, table: str, item_types: Dict[str, str]) -> Dict[str, Tuple[str, List[AffixTier]]]:
        groups: Dict[str, Tuple[str, List[AffixTier]]] = {}
        for row in self.repo.get_excel_table(table):
            name = row.get("Name", "")
            properties = tuple(sorted(prop["text"] for prop in self._properties(row, "mod")))
            if not name or not properties:
                continue

            settings = []
            identity = {field: row.get(field, "") for field in (
                "version", "group", "level", "levelreq", "class", "spawnable",
            )}
            identity["properties"] = sorted({row.get(f"mod{i}code", "") for i in range(1, 4)} - {""})
            for prefix, count, label in (("itype", 7, "Item types"), ("etype", 5, "Excludes")):
                codes = sorted({row.get(f"{prefix}{i}", "") for i in range(1, count + 1)} - {""})
                identity[prefix] = codes
                if codes:
                    names = [f"{item_types[code]} ({code})" if code in item_types else code for code in codes]
                    settings.append(f"{label} · {', '.join(names)}")
            spawn = row.get("spawnable", "")
            spawn_label = {"1": "Spawnable", "0": "Disabled", "": "Disabled"}.get(spawn, f"Spawn flag {spawn}")
            settings.append(spawn_label)
            if row.get("rare") == "1":
                settings.append("Can roll on rares")
            elif spawn == "1":
                settings.append("No rare rolls")
            for field, label in (
                ("level", "Affix level"), ("maxlevel", "Max affix level"), ("levelreq", "Required level"),
                ("class", "Class"), ("classlevelreq", "Class required level"), ("frequency", "Weight"),
                ("group", "Group"), ("version", "Version"),
            ):
                if row.get(field):
                    settings.append(f"{label} {row[field]}")
            _, tiers = groups.setdefault(name.casefold(), (self.repo.get_string(name) or name, []))
            tiers.append(AffixTier(properties, tuple(settings), identity))
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
        label = self._label(raw, config)
        fields = self._fields(raw, config.get("fields", []))
        properties = self._properties(raw, config.get("properties", ""))
        search_parts = [label, table_name]
        search_parts.extend(field["value"] for field in fields)
        search_parts.extend(prop["text"] for prop in properties)
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

    def _label(self, row: Dict[str, str], config: Dict[str, Any]) -> str:
        for key in (
            "Name",
            "name",
            "skill",
            "skilldesc",
            "state",
            "Shrine Type",
            "Id",
            "id",
            "Missile",
            "Sequence",
            "Hireling",
            "npc",
            "overlay",
            "Class",
            "Level",
        ):
            value = str(row.get(key, "")).strip()
            if value:
                return self.repo.get_string(value) or value
        return config["title"]

    @staticmethod
    def _fields(row: Dict[str, str], field_names: List[str]) -> List[Dict[str, str]]:
        fields: List[Dict[str, str]] = []
        seen: Set[str] = set()
        for name in field_names:
            if name in seen:
                continue
            seen.add(name)
            value = str(row.get(name, "")).strip()
            if value and value != "0":
                fields.append({"label": name, "value": value})
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
    ) -> List[Dict[str, str]]:
        properties: List[Dict[str, str]] = []
        for index in range(1, count + 1):
            code_key = f"{prefix}{index}{code_suffix}"
            code = str(row.get(code_key, "")).strip()
            if not code:
                continue
            param = str(row.get(f"{prefix}{index}{param_suffix}", "")).strip()
            min_val = str(row.get(f"{prefix}{index}{min_suffix}", "")).strip()
            max_val = str(row.get(f"{prefix}{index}{max_suffix}", "")).strip()
            text = self.resolver.resolve_property(code, param, min_val, max_val).get("resolved_text", "")
            properties.append({"code": code, "text": text or code})
        return properties
