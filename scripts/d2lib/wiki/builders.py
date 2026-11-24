from __future__ import annotations
import binascii
import csv
import json
import os
import re
import struct
import zlib
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlencode

from d2lib.repository import (
    DAMAGE_TYPES,
    D2Repository,
    D2RepositoryProtocol,
    resolve_act_name,
    resolve_element_name,
    resolve_immunity_label,
    resolve_localized_string,
)
from d2lib.models import BaseItemFamilyDTO, MiscGroupDTO

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _configured_data_dirs(*env_vars: str) -> List[str]:
    """Returns deduplicated D2R data directories explicitly configured via environment variables."""
    dirs: List[str] = []
    seen = set()
    for var in env_vars:
        value = os.environ.get(var, "").strip()
        if not value:
            continue
        norm = os.path.normcase(os.path.abspath(value))
        if norm not in seen:
            seen.add(norm)
            dirs.append(value)
    return dirs


def _nearest_breakpoint_value(target: int, distinct: List[int]) -> int:
    multiples = [value for value in distinct if value % 5 == 0]
    snap = min(multiples, key=lambda value: (abs(value - target), value), default=None)
    if snap is not None and abs(snap - target) <= 5:
        return snap
    return min(distinct, key=lambda value: (abs(value - target), value))


def derive_area_level_breakpoints(area_levels: Iterable[int], *, max_options: int = 8) -> List[int]:
    """Derives dynamic area minimum-level filter breakpoints from levels.txt."""
    distinct = sorted({int(value) for value in area_levels if int(value) > 0})
    if not distinct or len(distinct) <= max_options:
        return distinct

    multiples5 = [value for value in distinct if value % 5 == 0]
    if distinct[-1] not in multiples5:
        multiples5.append(distinct[-1])
    if 2 <= len(multiples5) <= max_options:
        return sorted(multiples5)

    multiples10 = [value for value in distinct if value % 10 == 0]
    if distinct[-1] not in multiples10:
        multiples10.append(distinct[-1])
    if 2 <= len(multiples10) <= max_options:
        return sorted(multiples10)

    step = max(1, (len(distinct) - 1) // max(1, max_options - 1))
    return sorted({distinct[index] for index in range(0, len(distinct), step)} | {distinct[-1]})


def derive_item_drop_level_breakpoints(drop_levels: Iterable[int], *, max_dense_options: int = 8) -> List[int]:
    """Derives dynamic item drop-level filter breakpoints from analyzed unique and set items."""
    values = sorted(int(value) for value in drop_levels if int(value) > 0)
    distinct = sorted(set(values))
    if not distinct or len(distinct) <= max_dense_options:
        return distinct

    count = len(values)
    p50 = values[int((count - 1) * 0.50)]
    p75 = values[int((count - 1) * 0.75)]
    p90 = values[int((count - 1) * 0.90)]
    p75_tail = [value for value in distinct if value >= p75]
    tail_start = p75 if len(p75_tail) <= max_dense_options else p90
    tail = [value for value in distinct if value >= tail_start]
    anchor_targets = [p50, (p50 + tail_start) // 2] if tail_start == p75 else [p50, p75]
    anchors = [
        candidate
        for candidate in (_nearest_breakpoint_value(target, distinct) for target in anchor_targets)
        if candidate < tail_start - 4
    ]
    return sorted(set(anchors + tail))


class AreaFarmingDataBuilder:
    _KURAST_PRESET_PATHS = (
        ("1", "act3/kurast/slums"),
        ("2", "act3/kurast/burbs"),
        ("3", "act3/kurast/metro"),
    )

    def __init__(
        self,
        game_data_dir: str,
        layout_data_dir: Optional[str] = None,
        repository: Optional[D2RepositoryProtocol] = None,
        retail_data_dir: Optional[str] = None,
    ):
        self.game_data_dir = game_data_dir
        self.layout_data_dir = layout_data_dir
        self.retail_data_dir = retail_data_dir
        self.repository: D2RepositoryProtocol = repository or D2Repository(game_data_dir)
        self.layout_roots = self._layout_roots()
        self._ds1_index: Optional[Dict[str, str]] = None

    def build(self) -> List[Dict[str, Any]]:
        levels = self.repository.get_excel_table("levels")
        monsters = {
            str(row.get("Id", "")).strip(): row
            for row in self.repository.get_excel_table("monstats")
            if str(row.get("Id", "")).strip()
        }
        maze_by_level_id = {
            self._to_int(row.get("Level")): row
            for row in self.repository.get_excel_table("lvlmaze")
            if self._to_int(row.get("Level"))
        }

        immunity_element_labels = {
            damage_type: resolve_element_name(self.repository, damage_type)
            for damage_type, _ in DAMAGE_TYPES
        }
        immunity_descriptions = {
            damage_type: resolve_immunity_label(self.repository, damage_type)
            for damage_type, _ in DAMAGE_TYPES
        }
        super_chests_by_level_id = self._super_chests_by_level_id(levels)
        records = [
            self._area_record(
                row,
                monsters,
                super_chests_by_level_id,
                maze_by_level_id,
                immunity_element_labels,
                immunity_descriptions,
            )
            for row in levels
        ]
        records = [record for record in records if self._is_farmable_area(record)]

        if not records:
            return []

        min_area_level = min(record["area_level"] for record in records)
        max_area_level = max(record["area_level"] for record in records)
        max_unique_level = max(record["unique_level"] for record in records)
        top_tier_level = self._derive_top_tier_level(max_unique_level)
        max_density = max([record["monster_density"] for record in records] or [1])
        max_elite_avg = max([record["elite_avg"] for record in records] or [1])
        max_density = max(max_density, 1)
        max_elite_avg = max(max_elite_avg, 1)

        for record in records:
            record["can_drop_top_tier"] = bool(record["unique_level"] >= top_tier_level) if top_tier_level else False
            record["farm_score"] = self._farm_score(
                record,
                min_area_level,
                max_area_level,
                max_density,
                max_elite_avg,
            )

        return sorted(
            records,
            key=lambda record: (
                -record["farm_score"],
                -record["area_level"],
                -record["monster_density"],
                record["display_name"].lower(),
            ),
        )

    def _area_record(
        self,
        row: Dict[str, str],
        monsters: Dict[str, Dict[str, str]],
        super_chests_by_level_id: Dict[int, List[Dict[str, Any]]],
        maze_by_level_id: Dict[int, Dict[str, str]],
        immunity_element_labels: Dict[str, str],
        immunity_descriptions: Dict[str, str],
    ) -> Dict[str, Any]:
        monster_pool = [
            self._monster_record(monsters[monster_id])
            for monster_id in self._monster_pool_ids(row)
            if monster_id in monsters
        ]
        immunity_counts: Dict[str, int] = {damage_type: 0 for damage_type, _ in DAMAGE_TYPES}
        for monster in monster_pool:
            for immunity in monster["immunities"]:
                immunity_counts[immunity] += 1
        immunity_counts = {key: value for key, value in immunity_counts.items() if value}
        possible_immunities = sorted(immunity_counts)
        area_immunity_labels = {
            code: immunity_element_labels[code]
            for code in possible_immunities
            if code in immunity_element_labels
        }
        area_immunity_descriptions = {
            code: immunity_descriptions[code]
            for code in possible_immunities
            if code in immunity_descriptions
        }

        area_level = self._area_level(row)
        level_id = self._to_int(row.get("Id"))
        act_id = self._parse_act_id(row.get("Act"))
        act_label = self._act_label(act_id)
        elite_min = self._to_int(row.get("MonUMin(H)"))
        elite_max = self._to_int(row.get("MonUMax(H)"))
        elite_avg = (elite_min + elite_max) / 2
        display_name = self._level_display_name(row)
        super_chests = super_chests_by_level_id.get(level_id, [])
        maze_info = self._maze_info(row, maze_by_level_id.get(level_id))

        return {
            "display_name": display_name,
            "internal_name": str(row.get("Name", "")).strip(),
            "level_id": level_id,
            "act_id": act_id,
            "act": act_label,
            "area_level": area_level,
            "champion_level": area_level + 2 if area_level else 0,
            "unique_level": area_level + 3 if area_level else 0,
            "can_drop_top_tier": False,
            "monster_density": self._to_int(row.get("MonDen(H)")),
            "maze_rooms": maze_info["rooms"],
            "maze_chunk_width": maze_info["chunk_width"],
            "maze_chunk_height": maze_info["chunk_height"],
            "maze_chunk_tiles": maze_info["chunk_tiles"],
            "estimated_area_tiles": maze_info["estimated_area_tiles"],
            "maze_source": maze_info["source"],
            "elite_min": elite_min,
            "elite_max": elite_max,
            "elite_avg": elite_avg,
            "possible_immunities": possible_immunities,
            "immunity_counts": immunity_counts,
            "immunity_labels": area_immunity_labels,
            "immunity_descriptions": area_immunity_descriptions,
            "has_super_chest": len(super_chests) > 0,
            "super_chest_count": len(super_chests),
            "super_chest_sources": super_chests,
            "monster_pool": monster_pool,
            "farm_score": 0,
            "search_text": self._search_text(
                display_name,
                act_label,
                row,
                monster_pool,
                area_immunity_labels,
                area_immunity_descriptions,
                super_chests,
                maze_info,
            ),
        }

    def _monster_record(self, row: Dict[str, str]) -> Dict[str, Any]:
        resistances = {damage_type: self._to_int(row.get(column)) for damage_type, column in DAMAGE_TYPES}
        immunities = [damage_type for damage_type, value in resistances.items() if value >= 100]
        name_key = str(row.get("NameStr", "")).strip()
        display_name = self.repository.get_string(name_key) if name_key else ""
        if not display_name or display_name == name_key:
            display_name = name_key or str(row.get("Id", "")).strip()
        return {
            "id": str(row.get("Id", "")).strip(),
            "name": display_name,
            "min_group": self._to_int(row.get("MinGrp")),
            "max_group": self._to_int(row.get("MaxGrp")),
            "rarity": self._to_int(row.get("Rarity")),
            "immunities": immunities,
            "resistances": resistances,
        }

    def _area_level(self, row: Dict[str, str]) -> int:
        return self._to_int(row.get("MonLvlEx(H)")) or self._to_int(row.get("MonLvl(H)"))

    def _maze_info(self, level_row: Dict[str, str], maze_row: Optional[Dict[str, str]]) -> Dict[str, Any]:
        if maze_row:
            rooms = self._to_int(maze_row.get("Rooms(H)")) or self._to_int(maze_row.get("Rooms"))
            chunk_width = self._to_int(maze_row.get("SizeX"))
            chunk_height = self._to_int(maze_row.get("SizeY"))
            chunk_tiles = chunk_width * chunk_height if chunk_width and chunk_height else 0
            estimated_area_tiles = rooms * chunk_tiles if rooms and chunk_tiles else 0
            return {
                "rooms": rooms,
                "chunk_width": chunk_width,
                "chunk_height": chunk_height,
                "chunk_tiles": chunk_tiles,
                "estimated_area_tiles": estimated_area_tiles,
                "source": "lvlmaze",
            }

        width = self._to_int(level_row.get("SizeX(H)")) or self._to_int(level_row.get("SizeX"))
        height = self._to_int(level_row.get("SizeY(H)")) or self._to_int(level_row.get("SizeY"))
        chunk_tiles = width * height if width and height else 0
        return {
            "rooms": 1 if chunk_tiles else 0,
            "chunk_width": width,
            "chunk_height": height,
            "chunk_tiles": chunk_tiles,
            "estimated_area_tiles": chunk_tiles,
            "source": "levels",
        }

    def _level_display_name(self, row: Dict[str, str]) -> str:
        for column in ("LevelName", "*StringName", "Name"):
            key = str(row.get(column, "")).strip()
            if not key:
                continue
            resolved = self.repository.get_string(key)
            if resolved and resolved != key:
                return resolved
            if column != "LevelName":
                return key
        return str(row.get("LevelName", "")).strip() or "Unknown Area"

    def _monster_pool_ids(self, row: Dict[str, str]) -> List[str]:
        ids: List[str] = []
        prefixes = ("nmon", "umon") if any(str(row.get(f"nmon{index}", "")).strip() for index in range(1, 26)) else ("mon", "umon")
        for prefix in prefixes:
            for index in range(1, 26):
                monster_id = str(row.get(f"{prefix}{index}", "")).strip()
                if monster_id and monster_id not in ids:
                    ids.append(monster_id)
        return ids

    def _search_text(
        self,
        display_name: str,
        act_label: str,
        row: Dict[str, str],
        monster_pool: List[Dict[str, Any]],
        immunity_labels: Dict[str, str],
        immunity_descriptions: Dict[str, str],
        super_chests: List[Dict[str, Any]],
        maze_info: Dict[str, Any],
    ) -> str:
        monsters = " ".join(
            f"{monster['id']} {monster['name']} {' '.join(monster['immunities'])}"
            for monster in monster_pool
        )
        immunity_terms = " ".join([*immunity_labels.values(), *immunity_descriptions.values()])
        chest_text = " ".join(
            f"{'sparkly chest' if source.get('chest_kind') == 'sparkly' else 'super chest'} {source.get('object_name', '')} {source.get('object_class', '')} {source.get('description', '')} {source.get('file', '')}"
            for source in super_chests
        )
        maze_text = (
            f"rooms {maze_info.get('rooms')} "
            f"chunk {maze_info.get('chunk_width')}x{maze_info.get('chunk_height')} "
            f"tiles {maze_info.get('estimated_area_tiles')}"
        )
        return (
            f"{display_name} {act_label} {row.get('Name', '')} {row.get('*StringName', '')} "
            f"{row.get('LevelName', '')} {monsters} {immunity_terms} {chest_text} {maze_text}"
        )

    def _layout_roots(self) -> List[str]:
        roots = []
        candidates = [
            os.path.join(self.game_data_dir, "data", "global", "tiles"),
            os.path.join(self.game_data_dir, "global", "tiles"),
            self._tiles_root(self.layout_data_dir),
            *[self._tiles_root(path) for path in _configured_data_dirs("D2R_LAYOUT_DATA_DIR", "D2R_DATA_DIR")],
            self._tiles_root(self.retail_data_dir)
            if self.retail_data_dir
            else os.path.join(REPO_ROOT, "data", "retail", "global", "tiles"),
        ]
        for candidate in candidates:
            if candidate and os.path.isdir(candidate):
                normalized = os.path.normcase(os.path.abspath(candidate))
                if normalized not in {os.path.normcase(os.path.abspath(root)) for root in roots}:
                    roots.append(candidate)
        return roots

    @staticmethod
    def _tiles_root(path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        if os.path.basename(os.path.normpath(path)).lower() == "tiles":
            return path
        return os.path.join(path, "global", "tiles")

    def _super_chests_by_level_id(self, levels: List[Dict[str, str]]) -> Dict[int, List[Dict[str, Any]]]:
        if not self.layout_roots:
            return {}

        objects_by_class, objects_by_id = self._super_chest_objects()
        if not objects_by_class and not objects_by_id:
            return {}

        preset_map = self._objpreset_map()
        kurast_preset_ids = self._dynamic_kurast_preset_level_ids(levels)
        level_act_by_id: Dict[int, int] = {}
        for level_row in levels:
            level_id = self._to_int(level_row.get("Id"))
            act_id = self._parse_act_id(level_row.get("Act"))
            if level_id > 0 and act_id is not None:
                level_act_by_id[level_id] = act_id

        chests_by_level_id: Dict[int, List[Dict[str, Any]]] = {}
        seen = set()
        for row in self.repository.get_excel_table("lvlprest"):
            level_ids = self._preset_level_ids(row, kurast_preset_ids)
            if not level_ids:
                continue

            for ds1_file in self._preset_files(row):
                ds1_path = self._resolve_ds1_path(ds1_file)
                if not ds1_path:
                    continue
                for object_type, ds1_object_id in self._read_ds1_typed_objects(ds1_path):
                    if object_type != 2:
                        continue
                    for level_id in level_ids:
                        source = self._resolve_preset_super_chest_object(
                            ds1_object_id,
                            level_act_by_id.get(level_id),
                            preset_map,
                            objects_by_class,
                            objects_by_id,
                        )
                        if not source:
                            continue
                        source_key = (level_id, source["object_id"], ds1_file)
                        if source_key in seen:
                            continue
                        seen.add(source_key)
                        chests_by_level_id.setdefault(level_id, []).append(
                            {
                                "object_id": source["object_id"],
                                "object_class": source["object_class"],
                                "object_name": source["object_name"],
                                "chest_kind": source["chest_kind"],
                                "description": source["description"],
                                "file": ds1_file.replace("\\", "/"),
                            }
                        )

        for sources in chests_by_level_id.values():
            sources.sort(key=lambda source: (source["object_class"], source["file"]))
        return chests_by_level_id

    def _objpreset_map(self) -> Dict[Tuple[int, int], str]:
        mapping: Dict[Tuple[int, int], str] = {}
        for row in self.repository.get_excel_table("objpreset"):
            act = self._to_int(row.get("Act"))
            index_raw = str(row.get("Index", "")).strip()
            object_class = str(row.get("ObjectClass", "")).strip().lower()
            if act <= 0 or not index_raw.isdigit() or not object_class:
                continue
            mapping[(act, int(index_raw))] = object_class
        return mapping

    def _dynamic_kurast_preset_level_ids(self, levels: List[Dict[str, str]]) -> List[Tuple[str, int]]:
        """Derives Act 3 outdoor Kurast preset level IDs dynamically from levels.txt."""
        by_slot: Dict[str, int] = {}
        for row in levels:
            if str(row.get("Act", "")).strip() != "2":
                continue
            drlg_type = str(row.get("DrlgType", "")).strip()
            if drlg_type and drlg_type != "3":
                continue
            match = re.search(r"\bkurast\s+([123])\b", str(row.get("Name", "")).strip(), re.IGNORECASE)
            if not match:
                continue
            level_id = self._to_int(row.get("Id"))
            if level_id > 0:
                by_slot.setdefault(match.group(1), level_id)
        return [(path, by_slot[slot]) for slot, path in self._KURAST_PRESET_PATHS if slot in by_slot]

    def _super_chest_objects(self) -> Tuple[Dict[str, Dict[str, Any]], Dict[int, Dict[str, Any]]]:
        """Identifies engine-true sparkly/special chests from objects.txt via InitFn=57 or PlaceUniqueChest."""
        by_class: Dict[str, Dict[str, Any]] = {}
        by_id: Dict[int, Dict[str, Any]] = {}
        for row in self.repository.get_excel_table("objects"):
            object_class = str(row.get("Class", "")).strip()
            init_fn = str(row.get("InitFn", "")).strip()
            if init_fn != "57" and object_class.lower() != "placeuniquechest":
                continue
            object_id = self._to_int(row.get("*ID"))
            class_label = object_class or f"Object {object_id}"
            raw_name = str(row.get("Name", "")).strip()
            object_name = (resolve_localized_string(self.repository, raw_name) if raw_name else "") or class_label
            entry: Dict[str, Any] = {
                "object_id": object_id,
                "object_class": class_label,
                "object_name": object_name,
                "chest_kind": "sparkly" if (object_id == 397 or object_class.lower() == "consolationchest") else "super",
                "description": str(row.get("*Description", "")).strip().strip('"'),
            }
            if object_class:
                by_class[object_class.lower()] = entry
            if object_id > 0:
                by_id[object_id] = entry
        return by_class, by_id

    @staticmethod
    def _resolve_preset_super_chest_object(
        ds1_object_id: int,
        act_id: Optional[int],
        preset_map: Dict[Tuple[int, int], str],
        objects_by_class: Dict[str, Dict[str, Any]],
        objects_by_id: Dict[int, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if act_id is not None and preset_map:
            key = (act_id + 1, ds1_object_id)
            if key in preset_map:
                return objects_by_class.get(preset_map[key])
        return objects_by_id.get(ds1_object_id)

    def _preset_level_ids(self, row: Dict[str, str], kurast_preset_ids: List[Tuple[str, int]]) -> List[int]:
        level_ids = []
        direct_level_id = self._to_int(row.get("LevelId"))
        if direct_level_id:
            level_ids.append(direct_level_id)

        preset_text = " ".join(self._preset_files(row)).replace("\\", "/").lower()
        for token, level_id in kurast_preset_ids:
            if token in preset_text and level_id not in level_ids:
                level_ids.append(level_id)
        return level_ids

    @staticmethod
    def _preset_files(row: Dict[str, str]) -> List[str]:
        files = []
        for index in range(1, 7):
            filename = str(row.get(f"File{index}", "")).strip()
            if filename:
                files.append(filename)
        return files

    def _build_ds1_index(self) -> Dict[str, str]:
        index: Dict[str, str] = {}
        for root in self.layout_roots:
            for current_root, _, files in os.walk(root):
                for filename in files:
                    if not filename.lower().endswith(".ds1"):
                        continue
                    full_path = os.path.join(current_root, filename)
                    rel_path = os.path.relpath(full_path, root).replace("\\", "/").lower()
                    index.setdefault(rel_path, full_path)
        return index

    def _resolve_ds1_path(self, ds1_file: str) -> Optional[str]:
        if self._ds1_index is None:
            self._ds1_index = self._build_ds1_index()
        key = ds1_file.replace("\\", "/").lstrip("/").lower()
        return self._ds1_index.get(key)

    @classmethod
    def _read_ds1_object_ids(cls, ds1_path: str) -> List[int]:
        return [object_id for _, object_id in cls._read_ds1_typed_objects(ds1_path)]

    @classmethod
    def _read_ds1_typed_objects(cls, ds1_path: str) -> List[Tuple[int, int]]:
        try:
            with open(ds1_path, "rb") as f:
                data = f.read()
            objects = cls._read_ds1_objects(data)
            return [(object_type, object_id) for object_type, object_id, _, _, _ in objects]
        except (OSError, ValueError, struct.error):
            return []

    @staticmethod
    def _read_ds1_objects(data: bytes) -> List[Tuple[int, int, int, int, int]]:
        def read_int(offset: int) -> Tuple[int, int]:
            return struct.unpack_from("<i", data, offset)[0], offset + 4

        def read_cstr(offset: int) -> int:
            end = data.index(0, offset)
            return end + 1

        offset = 0
        version, offset = read_int(offset)
        width, offset = read_int(offset)
        height, offset = read_int(offset)
        width += 1
        height += 1

        if version >= 8:
            _, offset = read_int(offset)

        subst_method = 0
        if version >= 10:
            subst_method, offset = read_int(offset)

        if version >= 3:
            file_count, offset = read_int(offset)
            for _ in range(file_count):
                offset = read_cstr(offset)

        if 9 <= version <= 13:
            offset += 8

        num_walls = 0
        num_floors = 1
        if version >= 4:
            num_walls, offset = read_int(offset)
            if version >= 16:
                num_floors, offset = read_int(offset)

        num_shadows = 1
        num_substitutions = 1 if version >= 10 and subst_method in (1, 2) else 0
        stream_count = num_walls * 2 + num_floors + num_shadows + num_substitutions if version >= 4 else 5
        offset += stream_count * width * height * 4

        objects = []
        if version >= 3 and offset + 4 <= len(data):
            object_count, offset = read_int(offset)
            for _ in range(object_count):
                object_type, offset = read_int(offset)
                object_id, offset = read_int(offset)
                x, offset = read_int(offset)
                y, offset = read_int(offset)
                flags, offset = read_int(offset)
                objects.append((object_type, object_id, x, y, flags))
        return objects

    def _derive_top_tier_level(self, max_unique_level: int) -> int:
        if max_unique_level <= 0:
            return 0
        candidates: List[int] = []
        for table_name in ("weapons", "armor"):
            for row in self.repository.get_excel_table(table_name):
                level = self._to_int(row.get("level"))
                if 0 < level <= max_unique_level:
                    candidates.append(level)
        for table_name in ("uniqueitems", "setitems"):
            for row in self.repository.get_excel_table(table_name):
                if str(row.get("disabled", "")).strip() in {"1", "true", "TRUE"}:
                    continue
                if str(row.get("spawnable", "1")).strip() == "0":
                    continue
                if str(row.get("enabled", "1")).strip() == "0":
                    continue
                level = self._to_int(row.get("lvl"))
                if 0 < level <= max_unique_level:
                    candidates.append(level)
        return max(candidates) if candidates else max_unique_level

    def _farm_score(
        self,
        record: Dict[str, Any],
        min_area_level: int,
        max_area_level: int,
        max_density: int,
        max_elite_avg: float,
    ) -> int:
        if max_area_level > min_area_level:
            area_level_score = 40.0 * (record["area_level"] - min_area_level) / (max_area_level - min_area_level)
        else:
            area_level_score = 40.0
        density_score = 35 * record["monster_density"] / max_density
        elite_score = 25 * record["elite_avg"] / max_elite_avg
        immunity_penalty = 3 * len(record["possible_immunities"])
        return round(area_level_score + density_score + elite_score - immunity_penalty)

    @staticmethod
    def _is_farmable_area(record: Dict[str, Any]) -> bool:
        return (
            record["level_id"] > 0
            and record["area_level"] > 0
            and (
                record["monster_density"] > 0
                or record["elite_max"] > 0
                or len(record["monster_pool"]) > 0
            )
        )

    @staticmethod
    def _parse_act_id(value: Optional[str]) -> Optional[int]:
        text = str(value or "").strip()
        if not text:
            return None
        try:
            act = int(text)
        except ValueError:
            return None
        return act if act >= 0 else None

    def _act_label(self, act_id: Optional[int]) -> str:
        if act_id is None or act_id < 0:
            return "Unknown"
        return resolve_act_name(self.repository, act_id)

    @staticmethod
    def _to_int(value: Optional[str]) -> int:
        try:
            return int(str(value or "").strip())
        except ValueError:
            return 0


class ItemIconExporter:
    def __init__(
        self,
        writer: Any, # WikiOutputWriter
        game_data_dir: str,
        retail_data_dir: str,
        output_prefix: str = "assets/item-icons",
        repository: Optional[D2RepositoryProtocol] = None,
    ):
        self.writer = writer
        self.game_data_dir = game_data_dir
        self.retail_data_dir = retail_data_dir
        self.output_prefix = output_prefix
        self._written: set[str] = set()
        self._item_asset_maps = [self._load_item_asset_map(path) for path in self._hd_item_manifest_paths()]
        self._unique_asset_maps = [self._load_quality_asset_map(path) for path in self._hd_quality_manifest_paths("uniques.json")]
        self._set_asset_maps = [self._load_quality_asset_map(path) for path in self._hd_quality_manifest_paths("sets.json")]
        self._item_tiers = self._load_item_tiers(repository)

    def attach_base_item_icons(self, families: List[BaseItemFamilyDTO]) -> None:
        for family in families:
            for item in family["members"]:
                item["icon_src"] = self.export_icon(
                    output_key=str(item.get("code", "") or item.get("icon_key", "")),
                    item_code=str(item.get("code", "")),
                    icon_key=str(item.get("icon_key", "")),
                )

    def attach_misc_item_icons(self, groups: List[MiscGroupDTO]) -> None:
        for group in groups:
            for item in group["members"]:
                item["icon_src"] = self.export_icon(
                    output_key=str(item.get("code", "") or item.get("icon_key", "")),
                    item_code=str(item.get("code", "")),
                    icon_key=str(item.get("icon_key", "")),
                )

    def export_entry_icon(self, entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            return ""

        raw_row = entry.get("raw_row", {})
        item_code = str(raw_row.get("item" if family == "set" else "code", "")).strip()
        icon_key = str(raw_row.get("invfile", "")).strip()
        quality_key = str(raw_row.get("index", "") or entry.get("display_name", "")).strip()
        return self.export_icon(
            output_key=f"{family}-{quality_key or item_code or icon_key}",
            item_code=item_code,
            icon_key=icon_key,
            quality_family=family,
            quality_key=quality_key,
        )

    def export_icon(
        self,
        output_key: str,
        item_code: str = "",
        icon_key: str = "",
        quality_family: str = "",
        quality_key: str = "",
    ) -> str:
        item_code = item_code.strip()
        icon_key = icon_key.strip()
        quality_family = quality_family.strip()
        quality_key = quality_key.strip()
        if not output_key and not item_code and not icon_key and not quality_key:
            return ""

        relative_path = f"{self.output_prefix}/{self._safe_icon_name(output_key or item_code or icon_key or quality_key)}.png"
        if relative_path not in self._written:
            png_bytes = self._icon_png_bytes(item_code, icon_key, quality_family, quality_key, output_key=output_key)
            if not png_bytes:
                return ""
            self.writer.write_bytes(relative_path, png_bytes)
            self._written.add(relative_path)

        return relative_path

    def _icon_png_bytes(
        self,
        item_code: str,
        icon_key: str,
        quality_family: str = "",
        quality_key: str = "",
        output_key: str = "",
    ) -> Optional[bytes]:
        # Priority 1: Check for pre-existing icons in the repo (docs/wiki/assets/item-icons/)
        # This ensures GitHub Actions builds use the high-quality icons we've tracked.
        repo_icon_name = self._safe_icon_name(output_key or item_code or icon_key or quality_key)
        repo_icon_path = os.path.join(REPO_ROOT, "docs", "wiki", "assets", "item-icons", f"{repo_icon_name}.png")
        if os.path.isfile(repo_icon_path):
            try:
                with open(repo_icon_path, "rb") as f:
                    return f.read()
            except OSError:
                pass

        # Priority 2: Try to decode from HD game assets
        hd_sprite_path = self._find_quality_hd_sprite(quality_family, quality_key, item_code)
        if not hd_sprite_path:
            hd_sprite_path = self._find_hd_sprite(item_code)
        if hd_sprite_path:
            hd_png = self._sprite_to_png(hd_sprite_path)
            if hd_png:
                return hd_png

        # Priority 3: Try to decode from classic DC6 assets
        dc6_path = self._find_dc6(icon_key)
        if dc6_path:
            return self._dc6_to_png(dc6_path)

        # Priority 4: Try to decode from standard sprite assets
        sprite_path = self._find_sprite(icon_key)
        if sprite_path:
            return self._sprite_to_png(sprite_path)

        # Priority 5: Procedural fallback for runes
        if re.fullmatch(r"r\d{2}", item_code.lower()):
            return self._fallback_rune_png(item_code)

        return None

    def _fallback_rune_png(self, rune_code: str) -> bytes:
        number = int(rune_code[1:]) if rune_code[1:].isdigit() else 0
        width = 34
        height = 34
        pixels = bytearray(width * height * 4)
        bg = (255, 255, 255, 0)
        edge = (54, 51, 48, 255)
        stone = (145, 142, 136, 255)
        light = (188, 185, 178, 255)
        shadow = (84, 80, 76, 255)
        mark = (43, 42, 40, 255)

        for y in range(height):
            for x in range(width):
                index = (y * width + x) * 4
                color = bg
                cx = abs(x - 16.5)
                cy = abs(y - 16.5)
                if (cx / 14.5) + (cy / 15.5) <= 1:
                    color = stone
                    if x + y < 24:
                        color = light
                    if x + y > 42:
                        color = shadow
                if (cx / 15.5) + (cy / 16.5) <= 1 and (cx / 13.5) + (cy / 14.5) > 1:
                    color = edge
                pixels[index : index + 4] = bytes(color)

        strokes = [
            ((16, 8), (16, 26)),
            ((10, 14), (23, 14)),
            ((11, 22), (23, 10)),
            ((10, 10), (24, 24)),
            ((9, 20), (16, 10)),
            ((17, 10), (25, 20)),
        ]
        for bit, stroke in enumerate(strokes):
            if number & (1 << bit):
                self._draw_line_rgba(pixels, width, height, stroke[0], stroke[1], mark)

        return self._png_rgba(width, height, bytes(pixels))

    @staticmethod
    def _draw_line_rgba(
        pixels: bytearray,
        width: int,
        height: int,
        start: Tuple[int, int],
        end: Tuple[int, int],
        color: Tuple[int, int, int, int],
    ) -> None:
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    x = x0 + ox
                    y = y0 + oy
                    if 0 <= x < width and 0 <= y < height:
                        index = (y * width + x) * 4
                        if pixels[index + 3]:
                            pixels[index : index + 4] = bytes(color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def _find_quality_hd_sprite(self, family: str, quality_key: str, item_code: str) -> Optional[str]:
        family = family.strip().lower()
        quality_key = self._quality_asset_key(quality_key)
        if not family or not quality_key:
            return None

        maps = self._unique_asset_maps if family == "unique" else self._set_asset_maps if family == "set" else []
        for asset_map in maps:
            variants = asset_map.get(quality_key, {})
            if not variants:
                continue

            tier = self._item_code_tier(item_code)
            for variant in [tier, "normal", "uber", "ultra"]:
                asset = variants.get(variant, "").strip()
                if not asset:
                    continue
                sprite_path = self._find_hd_sprite_by_asset(asset)
                if sprite_path:
                    return sprite_path
        return None

    def _find_hd_sprite(self, item_code: str) -> Optional[str]:
        item_code = item_code.lower().strip()
        if not item_code:
            return None

        for asset_map in self._item_asset_maps:
            asset = asset_map.get(item_code, "").strip()
            if not asset:
                continue
            sprite_path = self._find_hd_sprite_by_asset(asset)
            if sprite_path:
                return sprite_path
        return None

    def _find_hd_sprite_by_asset(self, asset: str) -> Optional[str]:
        asset_parts = [part for part in asset.replace("\\", "/").split("/") if part]
        for ui_root in self._hd_item_ui_roots():
            for group in ("weapon", "armor", "misc"):
                candidate = os.path.join(ui_root, group, *asset_parts) + ".sprite"
                if os.path.isfile(candidate):
                    return candidate
        return None

    def _hd_item_manifest_paths(self) -> List[str]:
        candidates = [
            os.path.join(self.game_data_dir, "data", "hd", "items", "items.json"),
            os.path.join(self.retail_data_dir, "hd", "items", "items.json"),
            *[
                os.path.join(data_dir, "hd", "items", "items.json")
                for data_dir in _configured_data_dirs("D2R_RETAIL_DATA_DIR", "D2R_DATA_DIR")
            ],
        ]
        return [path for path in candidates if os.path.isfile(path)]

    def _hd_quality_manifest_paths(self, filename: str) -> List[str]:
        candidates = [
            os.path.join(self.game_data_dir, "data", "hd", "items", filename),
            os.path.join(self.retail_data_dir, "hd", "items", filename),
            *[
                os.path.join(data_dir, "hd", "items", filename)
                for data_dir in _configured_data_dirs("D2R_RETAIL_DATA_DIR", "D2R_DATA_DIR")
            ],
        ]
        return [path for path in candidates if os.path.isfile(path)]

    def _hd_item_ui_roots(self) -> List[str]:
        candidates = [
            os.path.join(self.game_data_dir, "data", "hd", "global", "ui", "items"),
            os.path.join(self.retail_data_dir, "hd", "global", "ui", "items"),
            *[
                os.path.join(data_dir, "hd", "global", "ui", "items")
                for data_dir in _configured_data_dirs("D2R_RETAIL_DATA_DIR", "D2R_DATA_DIR")
            ],
        ]
        return [path for path in candidates if os.path.isdir(path)]

    @staticmethod
    def _load_item_asset_map(path: str) -> Dict[str, str]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                rows = json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

        assets: Dict[str, str] = {}
        if not isinstance(rows, list):
            return assets

        for row in rows:
            if not isinstance(row, dict):
                continue
            for code, payload in row.items():
                if isinstance(payload, dict):
                    asset = str(payload.get("asset", "")).strip()
                    if asset:
                        assets[str(code).lower()] = asset
        return assets

    @staticmethod
    def _load_quality_asset_map(path: str) -> Dict[str, Dict[str, str]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                rows = json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

        assets: Dict[str, Dict[str, str]] = {}
        if not isinstance(rows, list):
            return assets

        for row in rows:
            if not isinstance(row, dict):
                continue
            for key, payload in row.items():
                if not isinstance(payload, dict):
                    continue
                variants = {
                    variant: str(payload.get(variant, "")).strip()
                    for variant in ("normal", "uber", "ultra")
                    if str(payload.get(variant, "")).strip()
                }
                if variants:
                    assets[ItemIconExporter._quality_asset_key(str(key))] = variants
        return assets

    @staticmethod
    def _quality_asset_key(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

    @staticmethod
    def _read_excel_rows(path: str) -> List[Dict[str, str]]:
        csv.field_size_limit(1000000)
        try:
            with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
                return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
        except OSError:
            return []

    def _load_item_table_rows(self, table_name: str, repository: Optional[D2RepositoryProtocol]) -> List[Dict[str, str]]:
        if repository is not None:
            return list(repository.get_excel_table(table_name))
        candidates = [
            os.path.join(self.game_data_dir, "data", "global", "excel", f"{table_name}.txt"),
            os.path.join(self.retail_data_dir, "global", "excel", f"{table_name}.txt"),
            *[
                os.path.join(data_dir, "global", "excel", f"{table_name}.txt")
                for data_dir in _configured_data_dirs("D2R_RETAIL_DATA_DIR", "D2R_DATA_DIR")
            ],
        ]
        for path in candidates:
            if os.path.isfile(path):
                return self._read_excel_rows(path)
        return []

    def _load_item_tiers(self, repository: Optional[D2RepositoryProtocol]) -> Dict[str, str]:
        rows: List[Dict[str, str]] = []
        for table_name in ("weapons", "armor"):
            rows.extend(self._load_item_table_rows(table_name, repository))

        tiers: Dict[str, str] = {}
        # Pass 1: infer tier from normcode / ubercode / ultracode relationships.
        for row in rows:
            norm = str(row.get("normcode") or "").strip().lower()
            uber = str(row.get("ubercode") or "").strip().lower()
            ultra = str(row.get("ultracode") or "").strip().lower()
            if norm:
                tiers.setdefault(norm, "normal")
            if uber and uber != norm:
                tiers[uber] = "uber"
            if ultra and ultra != norm and ultra != uber:
                tiers[ultra] = "ultra"

        # Pass 2: each row's own code takes precedence for standalone items (norm == uber == ultra).
        for row in rows:
            code = str(row.get("code") or "").strip().lower()
            if not code:
                continue
            norm = str(row.get("normcode") or "").strip().lower()
            uber = str(row.get("ubercode") or "").strip().lower()
            ultra = str(row.get("ultracode") or "").strip().lower()
            if norm and code == norm:
                tiers[code] = "normal"
            elif ultra and code == ultra:
                tiers[code] = "ultra"
            elif uber and code == uber:
                tiers[code] = "uber"
        return tiers

    def _item_code_tier(self, item_code: str) -> str:
        code = item_code.strip().lower()
        if not code:
            return "normal"
        return self._item_tiers.get(code, "normal")

    def _find_dc6(self, icon_key: str) -> Optional[str]:
        filename = f"{icon_key.lower()}.dc6"
        for item_dir in self._classic_item_dirs():
            candidate = os.path.join(item_dir, filename)
            if os.path.isfile(candidate):
                return candidate
        return None

    def _classic_item_dirs(self) -> List[str]:
        candidates = [
            os.path.join(self.game_data_dir, "data", "global", "items"),
            os.path.join(self.retail_data_dir, "global", "items"),
            *[
                os.path.join(data_dir, "global", "items")
                for data_dir in _configured_data_dirs("D2R_RETAIL_DATA_DIR", "D2R_DATA_DIR")
            ],
        ]
        return [path for path in candidates if os.path.isdir(path)]

    def _find_sprite(self, icon_key: str) -> Optional[str]:
        filename = f"{icon_key.lower()}.sprite"
        roots = [
            os.path.join(self.game_data_dir, "data", "hd", "global", "ui", "items"),
            os.path.join(self.retail_data_dir, "hd", "global", "ui", "items"),
        ]
        for root in roots:
            if not os.path.isdir(root):
                continue
            for current_root, _, files in os.walk(root):
                lower_files = {filename.lower(): filename for filename in files}
                if filename in lower_files:
                    return os.path.join(current_root, lower_files[filename])
        return None

    def _dc6_to_png(self, path: str) -> Optional[bytes]:
        try:
            with open(path, "rb") as f:
                data = f.read()
            if len(data) < 60:
                return None

            directions, frames = struct.unpack_from("<2I", data, 16)
            if directions < 1 or frames < 1:
                return None

            frame_offset = struct.unpack_from("<I", data, 24)[0]
            if frame_offset + 32 > len(data):
                return None

            _, width, height, _, _, _, _, encoded_length = struct.unpack_from("<8I", data, frame_offset)
            if width <= 0 or height <= 0:
                return None

            palette = self._palette_bytes(path)
            if not palette:
                return None

            pixels = bytearray(width * height * 4)
            x = 0
            y = height - 1
            pos = frame_offset + 32
            end = min(len(data), pos + encoded_length)

            while pos < end and y >= 0:
                command = data[pos]
                pos += 1

                if command == 0x80:
                    x = 0
                    y -= 1
                elif command & 0x80:
                    x += command & 0x7F
                else:
                    count = command
                    for color_index in data[pos : pos + count]:
                        if x < width and y >= 0:
                            palette_index = color_index * 3
                            pixel_index = (y * width + x) * 4
                            pixels[pixel_index] = palette[palette_index + 2]
                            pixels[pixel_index + 1] = palette[palette_index + 1]
                            pixels[pixel_index + 2] = palette[palette_index]
                            pixels[pixel_index + 3] = 255
                        x += 1
                    pos += count

            trimmed_width, trimmed_height, trimmed_pixels = self._trim_transparent_rgba(width, height, bytes(pixels))
            return self._png_rgba(trimmed_width, trimmed_height, trimmed_pixels)
        except (OSError, struct.error, IndexError, ValueError):
            return None

    def _palette_bytes(self, dc6_path: str) -> Optional[bytes]:
        item_dir = os.path.dirname(dc6_path)
        candidates = [
            os.path.join(self.retail_data_dir, "global", "palette", "act1", "pal.dat"),
            *[
                os.path.join(data_dir, "global", "palette", "act1", "pal.dat")
                for data_dir in _configured_data_dirs("D2R_RETAIL_DATA_DIR", "D2R_DATA_DIR")
            ],
            os.path.join(item_dir, "..", "palette", "grey.dat"),
        ]
        for candidate in candidates:
            normalized = os.path.abspath(candidate)
            if os.path.isfile(normalized):
                with open(normalized, "rb") as f:
                    palette = f.read(768)
                if len(palette) == 768:
                    return palette
        return None

    def _sprite_to_png(self, path: str) -> Optional[bytes]:
        try:
            with open(path, "rb") as f:
                data = f.read()
            if len(data) < 40 or data[:4] != b"SpA1":
                return None
            width = int.from_bytes(data[6:8], "little")
            height = int.from_bytes(data[12:16], "little")
            cell_height = int.from_bytes(data[8:10], "little")
            if width <= 0 or height <= 0:
                height = cell_height
            pixel_count = width * height * 4
            if width <= 0 or height <= 0 or len(data) < 40 + pixel_count:
                return None
            trimmed_width, trimmed_height, trimmed_pixels = self._trim_transparent_rgba(
                width,
                height,
                data[40 : 40 + pixel_count],
            )
            return self._png_rgba(trimmed_width, trimmed_height, trimmed_pixels)
        except OSError:
            return None

    @staticmethod
    def _trim_transparent_rgba(width: int, height: int, rgba: bytes, padding: int = 2) -> Tuple[int, int, bytes]:
        min_x = width
        min_y = height
        max_x = -1
        max_y = -1

        for y in range(height):
            for x in range(width):
                if rgba[((y * width + x) * 4) + 3] == 0:
                    continue
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        if max_x < min_x or max_y < min_y:
            return width, height, rgba

        min_x = max(0, min_x - padding)
        min_y = max(0, min_y - padding)
        max_x = min(width - 1, max_x + padding)
        max_y = min(height - 1, max_y + padding)
        trimmed_width = max_x - min_x + 1
        trimmed_height = max_y - min_y + 1
        trimmed = bytearray(trimmed_width * trimmed_height * 4)

        for y in range(trimmed_height):
            src_start = (((min_y + y) * width) + min_x) * 4
            src_end = src_start + (trimmed_width * 4)
            dest_start = y * trimmed_width * 4
            trimmed[dest_start : dest_start + (trimmed_width * 4)] = rgba[src_start:src_end]

        return trimmed_width, trimmed_height, bytes(trimmed)

    @staticmethod
    def _png_rgba(width: int, height: int, rgba: bytes) -> bytes:
        def chunk(kind: bytes, payload: bytes) -> bytes:
            crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
            return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)

        rows = []
        stride = width * 4
        for row_index in range(height):
            start = row_index * stride
            rows.append(b"\x00" + rgba[start : start + stride])

        header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
            + chunk(b"IEND", b"")
        )

    @staticmethod
    def _safe_icon_name(icon_key: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", icon_key.strip().lower()).strip("-") or "item"