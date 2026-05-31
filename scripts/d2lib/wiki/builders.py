from __future__ import annotations
import binascii
import json
import os
import re
import struct
import zlib
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

from d2lib.repository import D2Repository
from d2lib.models import BaseItemFamilyDTO, MiscGroupDTO
from d2lib.wiki.routes import DAMAGE_TYPES, WikiRoutes

DEFAULT_RETAIL_DATA_DIR = r"E:\Games\Diablo II Resurrected\Data"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

class AreaFarmingDataBuilder:
    SUPER_CHEST_TOKENS = (
        "sparklychest",
        "specialchest",
        "arcanechest",
        "travincalchest",
        "sewerchestlarge",
        "sewerchesttall",
        "tombchest",
        "forgottentowerchest",
    )
    KURAST_PRESET_LEVEL_IDS = (
        ("act3/kurast/slums", 79),
        ("act3/kurast/burbs", 80),
        ("act3/kurast/metro", 81),
    )

    def __init__(self, game_data_dir: str, layout_data_dir: Optional[str] = None):
        self.game_data_dir = game_data_dir
        self.layout_data_dir = layout_data_dir
        self.repository = D2Repository(game_data_dir)
        self.layout_roots = self._layout_roots()

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

        super_chests_by_level_id = self._super_chests_by_level_id()
        records = [self._area_record(row, monsters, super_chests_by_level_id, maze_by_level_id) for row in levels]
        records = [record for record in records if self._is_farmable_area(record)]

        if not records:
            return []

        max_density = max([record["monster_density"] for record in records] or [1])
        max_elite_avg = max([record["elite_avg"] for record in records] or [1])
        max_density = max(max_density, 1)
        max_elite_avg = max(max_elite_avg, 1)

        for record in records:
            record["farm_score"] = self._farm_score(record, max_density, max_elite_avg)

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

        area_level = self._area_level(row)
        level_id = self._to_int(row.get("Id"))
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
            "act": self._act_label(row.get("Act")),
            "area_level": area_level,
            "champion_level": area_level + 2 if area_level else 0,
            "unique_level": area_level + 3 if area_level else 0,
            "can_drop_top_tier": area_level + 3 >= 90 if area_level else False,
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
            "possible_immunities": sorted(immunity_counts),
            "immunity_counts": immunity_counts,
            "has_super_chest": len(super_chests) > 0,
            "super_chest_count": len(super_chests),
            "super_chest_sources": super_chests,
            "monster_pool": monster_pool,
            "farm_score": 0,
            "search_text": self._search_text(display_name, row, monster_pool, super_chests, maze_info),
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
        row: Dict[str, str],
        monster_pool: List[Dict[str, Any]],
        super_chests: List[Dict[str, Any]],
        maze_info: Dict[str, Any],
    ) -> str:
        monsters = " ".join(
            f"{monster['id']} {monster['name']} {' '.join(monster['immunities'])}"
            for monster in monster_pool
        )
        chest_text = " ".join(
            f"super chest {source.get('object_class', '')} {source.get('description', '')} {source.get('file', '')}"
            for source in super_chests
        )
        maze_text = (
            f"rooms {maze_info.get('rooms')} "
            f"chunk {maze_info.get('chunk_width')}x{maze_info.get('chunk_height')} "
            f"tiles {maze_info.get('estimated_area_tiles')}"
        )
        return f"{display_name} {row.get('Name', '')} {row.get('*StringName', '')} {row.get('LevelName', '')} {monsters} {chest_text} {maze_text}"

    def _layout_roots(self) -> List[str]:
        roots = []
        for candidate in (
            os.path.join(self.game_data_dir, "data", "global", "tiles"),
            os.path.join(self.game_data_dir, "global", "tiles"),
            self._tiles_root(self.layout_data_dir),
            self._tiles_root(DEFAULT_RETAIL_DATA_DIR),
            os.path.join(REPO_ROOT, "data", "retail", "global", "tiles"),
        ):
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

    def _super_chests_by_level_id(self) -> Dict[int, List[Dict[str, Any]]]:
        if not self.layout_roots:
            return {}

        objects_by_id = self._super_chest_objects()
        if not objects_by_id:
            return {}

        chests_by_level_id: Dict[int, List[Dict[str, Any]]] = {}
        seen = set()
        for row in self.repository.get_excel_table("lvlprest"):
            level_ids = self._preset_level_ids(row)
            if not level_ids:
                continue

            for ds1_file in self._preset_files(row):
                contextual_source = self._contextual_preset_super_chest(row, ds1_file)
                if contextual_source:
                    for level_id in level_ids:
                        source_key = (level_id, contextual_source["object_class"], ds1_file)
                        if source_key in seen:
                            continue
                        seen.add(source_key)
                        chests_by_level_id.setdefault(level_id, []).append(contextual_source)

                ds1_path = self._resolve_ds1_path(ds1_file)
                if not ds1_path:
                    continue
                for object_id in self._read_ds1_object_ids(ds1_path):
                    source = objects_by_id.get(object_id) or self._contextual_super_chest_object(object_id, ds1_file)
                    if not source:
                        continue
                    for level_id in level_ids:
                        source_key = (level_id, object_id, ds1_file)
                        if source_key in seen:
                            continue
                        seen.add(source_key)
                        chests_by_level_id.setdefault(level_id, []).append(
                            {
                                "object_id": object_id,
                                "object_class": source["object_class"],
                                "description": source["description"],
                                "file": ds1_file.replace("\\", "/"),
                            }
                        )

        for sources in chests_by_level_id.values():
            sources.sort(key=lambda source: (source["object_class"], source["file"]))
        return chests_by_level_id

    def _super_chest_objects(self) -> Dict[int, Dict[str, str]]:
        objects: Dict[int, Dict[str, str]] = {}
        for row in self.repository.get_excel_table("objects"):
            object_id = self._to_int(row.get("*ID"))
            object_class = str(row.get("Class", "")).strip()
            description = str(row.get("*Description", "")).strip()
            haystack = " ".join(
                [
                    object_class,
                    description,
                    str(row.get("Name", "")).strip(),
                    str(row.get("PopulateFn", "")).strip(),
                ]
            ).lower()
            if str(row.get("InitFn", "")).strip() == "57" or any(token in haystack for token in self.SUPER_CHEST_TOKENS):
                objects[object_id] = {
                    "object_class": object_class or f"Object {object_id}",
                    "description": description,
                }
        return objects

    def _contextual_preset_super_chest(self, row: Dict[str, str], ds1_file: str) -> Optional[Dict[str, Any]]:
        name = str(row.get("Name", "")).strip().lower()
        normalized_file = ds1_file.replace("\\", "/").lower()
        if "act 1 - cave treasure" not in name or not normalized_file.startswith("act1/caves/caveroom"):
            return None
        return {
            "object_id": None,
            "object_class": "Act 1 Treasure Room Super Chest",
            "description": "Fixed cave treasure-room chest",
            "file": ds1_file.replace("\\", "/"),
        }

    def _contextual_super_chest_object(self, object_id: int, ds1_file: str) -> Optional[Dict[str, str]]:
        normalized_file = ds1_file.replace("\\", "/").lower()
        if object_id not in (5, 6):
            return None
        if not any(token in normalized_file for token, _ in self.KURAST_PRESET_LEVEL_IDS):
            return None
        side = "Right" if object_id == 5 else "Left"
        return {
            "object_class": f"Kurast Super Chest {side}",
            "description": "Kurast camp preset large chest",
        }

    def _preset_level_ids(self, row: Dict[str, str]) -> List[int]:
        level_ids = []
        direct_level_id = self._to_int(row.get("LevelId"))
        if direct_level_id:
            level_ids.append(direct_level_id)

        preset_text = " ".join(self._preset_files(row)).replace("\\", "/").lower()
        for token, level_id in self.KURAST_PRESET_LEVEL_IDS:
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

    def _resolve_ds1_path(self, ds1_file: str) -> Optional[str]:
        rel_path = ds1_file.replace("/", os.sep).replace("\\", os.sep)
        for root in self.layout_roots:
            candidate = os.path.join(root, rel_path)
            if os.path.exists(candidate):
                return candidate
        return None

    @classmethod
    def _read_ds1_object_ids(cls, ds1_path: str) -> List[int]:
        try:
            with open(ds1_path, "rb") as f:
                data = f.read()
            objects = cls._read_ds1_objects(data)
            return [object_id for _, object_id, _, _, _ in objects]
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

    def _farm_score(self, record: Dict[str, Any], max_density: int, max_elite_avg: float) -> int:
        if record["unique_level"] >= 90:
            area_level_score = 40
        elif record["area_level"] >= 87:
            area_level_score = 30
        else:
            area_level_score = max(0, (record["area_level"] - 75) * 2)
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
    def _act_label(value: Optional[str]) -> str:
        text = str(value or "").strip()
        if not text:
            return "Unknown"
        act = AreaFarmingDataBuilder._to_int(text)
        return f"Act {act + 1}" if act >= 0 else "Unknown"

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
    ):
        self.writer = writer
        self.game_data_dir = game_data_dir
        self.retail_data_dir = retail_data_dir
        self.output_prefix = output_prefix
        self._written: set[str] = set()
        self._item_asset_maps = [self._load_item_asset_map(path) for path in self._hd_item_manifest_paths()]
        self._unique_asset_maps = [self._load_quality_asset_map(path) for path in self._hd_quality_manifest_paths("uniques.json")]
        self._set_asset_maps = [self._load_quality_asset_map(path) for path in self._hd_quality_manifest_paths("sets.json")]

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
            png_bytes = self._icon_png_bytes(item_code, icon_key, quality_family, quality_key)
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
    ) -> Optional[bytes]:
        hd_sprite_path = self._find_quality_hd_sprite(quality_family, quality_key, item_code)
        if not hd_sprite_path:
            hd_sprite_path = self._find_hd_sprite(item_code)
        if hd_sprite_path:
            hd_png = self._sprite_to_png(hd_sprite_path)
            if hd_png:
                return hd_png

        dc6_path = self._find_dc6(icon_key)
        if dc6_path:
            return self._dc6_to_png(dc6_path)

        sprite_path = self._find_sprite(icon_key)
        if sprite_path:
            return self._sprite_to_png(sprite_path)

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
            os.path.join(DEFAULT_RETAIL_DATA_DIR, "hd", "items", "items.json"),
        ]
        return [path for path in candidates if os.path.isfile(path)]

    def _hd_quality_manifest_paths(self, filename: str) -> List[str]:
        candidates = [
            os.path.join(self.game_data_dir, "data", "hd", "items", filename),
            os.path.join(self.retail_data_dir, "hd", "items", filename),
            os.path.join(DEFAULT_RETAIL_DATA_DIR, "hd", "items", filename),
        ]
        return [path for path in candidates if os.path.isfile(path)]

    def _hd_item_ui_roots(self) -> List[str]:
        candidates = [
            os.path.join(self.game_data_dir, "data", "hd", "global", "ui", "items"),
            os.path.join(self.retail_data_dir, "hd", "global", "ui", "items"),
            os.path.join(DEFAULT_RETAIL_DATA_DIR, "hd", "global", "ui", "items"),
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
    def _item_code_tier(item_code: str) -> str:
        code = item_code.strip().lower()
        if not code:
            return "normal"
        if code[:1] in {"7", "u", "z"}:
            return "ultra"
        if code[:1] in {"9", "x"}:
            return "uber"
        return "normal"

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
            os.path.join(DEFAULT_RETAIL_DATA_DIR, "global", "items"),
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
            os.path.join(DEFAULT_RETAIL_DATA_DIR, "global", "palette", "act1", "pal.dat"),
            os.path.join(self.retail_data_dir, "global", "palette", "act1", "pal.dat"),
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