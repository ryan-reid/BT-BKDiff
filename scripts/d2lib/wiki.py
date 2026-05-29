import json
import os
import re
import shutil
import struct
from typing import Any, Dict, List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape

from d2lib.repository import D2Repository
from d2lib.services import PropertyResolverService, BaseItemAnalyzerService, CubeAnalyzerService, MonsterAnalyzerService, MiscAnalyzerService, MechanicsAnalyzerService
from d2lib.models import BaseItemFamilyDTO, CubeRecipeGroupDTO, MonsterActGroupDTO, MiscGroupDTO, MechanicsSummaryDTO


MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(MODULE_DIR, "..", ".."))
TEMPLATE_DIR = os.path.join(MODULE_DIR, "wiki_templates")
ASSET_SOURCE_DIR = os.path.join(MODULE_DIR, "wiki_assets")
DEFAULT_RETAIL_DATA_DIR = r"E:\Games\Diablo II Resurrected\Data"
ITEM_FAMILIES = ("unique", "set", "runeword")
DAMAGE_TYPES = (
    ("physical", "ResDm(H)"),
    ("magic", "ResMa(H)"),
    ("fire", "ResFi(H)"),
    ("lightning", "ResLi(H)"),
    ("cold", "ResCo(H)"),
    ("poison", "ResPo(H)"),
)
REPORT_SOURCES = (
    {
        "title": "Item Diff: BKDiablo vs Retail",
        "description": "Item database changes comparing BKDiablo against retail data.",
        "source_dir": "item_diff_report_retail_bk",
        "output_dir": "reports/items/retail-bk",
        "source_kind": "item_diff",
    },
    {
        "title": "Item Diff: BKDiablo vs BTDiablo",
        "description": "Item database changes comparing BKDiablo against BTDiablo.",
        "source_dir": "item_diff_report_bt_bk",
        "output_dir": "reports/items/bt-bk",
        "source_kind": "item_diff",
    },
    {
        "title": "Excel Diff: BKDiablo vs Retail",
        "description": "Raw Excel table changes comparing BKDiablo against retail data.",
        "source_dir": "excel_diff_report_retail_bk",
        "output_dir": "reports/excel/retail-bk",
        "source_kind": "excel_diff",
    },
    {
        "title": "Override File Diff: BKDiablo vs Retail",
        "description": "Text and JSON override file changes comparing BKDiablo against retail files.",
        "source_dir": "file_diff_report_retail_bk",
        "output_dir": "reports/files/retail-bk",
        "source_kind": "file_diff",
    },
    {
        "title": "Excel Diff: BKDiablo vs BTDiablo",
        "description": "Raw Excel table changes comparing BKDiablo against BTDiablo.",
        "source_dir": "excel_diff_report_bt_bk",
        "output_dir": "reports/excel/bt-bk",
        "source_kind": "excel_diff",
    },
)


def _slugify(value: str) -> str:
    text = value.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-") or "untitled"


def _strip_markdown_markup(value: str) -> str:
    text = value.replace("\\+", "+")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()


class WikiRoutes:
    @staticmethod
    def home_output_path() -> str:
        return "index.html"

    @staticmethod
    def items_index_output_path() -> str:
        return "items/index.html"

    @staticmethod
    def bases_index_output_path() -> str:
        return "bases/index.html"

    @staticmethod
    def recipes_index_output_path() -> str:
        return "recipes/index.html"

    @staticmethod
    def bestiary_index_output_path() -> str:
        return "bestiary/index.html"

    @staticmethod
    def misc_index_output_path() -> str:
        return "misc/index.html"

    @staticmethod
    def mechanics_output_path() -> str:
        return "mechanics/index.html"

    @staticmethod
    def item_output_path(family: str, slug: str) -> str:
        return f"items/{family}/{slug}/index.html"

    @staticmethod
    def classes_index_output_path() -> str:
        return "classes/index.html"

    @staticmethod
    def areas_index_output_path() -> str:
        return "areas/index.html"

    @staticmethod
    def class_output_path(slug: str) -> str:
        return f"classes/{slug}/index.html"

    @staticmethod
    def patch_notes_output_path() -> str:
        return "patch-notes/full-patch-notes-draft/index.html"

    @staticmethod
    def reports_index_output_path() -> str:
        return "reports/index.html"

    @staticmethod
    def route_from_output_path(output_path: str) -> str:
        normalized = output_path.replace("\\", "/")
        if normalized == "index.html":
            return ""
        if normalized.endswith("/index.html"):
            return normalized[: -len("index.html")]
        return normalized

    @staticmethod
    def site_root_for_output_path(output_path: str) -> str:
        return "../" * output_path.replace("\\", "/").count("/")


class WikiRenderer:
    def __init__(self, template_dir: str = TEMPLATE_DIR):
        self.environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, **context: Any) -> str:
        return self.environment.get_template(template_name).render(**context)


class WikiOutputWriter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.generated_paths: set[str] = set()

    def write_text(self, relative_path: str, content: str) -> None:
        normalized = relative_path.replace("\\", "/")
        full_path = os.path.join(self.output_dir, normalized)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        self.generated_paths.add(normalized)

    def copy_asset(self, source_path: str, relative_path: str) -> None:
        normalized = relative_path.replace("\\", "/")
        full_path = os.path.join(self.output_dir, normalized)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        shutil.copyfile(source_path, full_path)
        self.generated_paths.add(normalized)

    def remove_stale_files(self) -> None:
        for root, dirs, files in os.walk(self.output_dir, topdown=False):
            for filename in files:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.output_dir).replace("\\", "/")
                if rel_path in self.generated_paths:
                    continue
                try:
                    os.remove(full_path)
                except OSError:
                    pass

            for dirname in dirs:
                dir_path = os.path.join(root, dirname)
                try:
                    os.rmdir(dir_path)
                except OSError:
                    pass


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


class WikiGenerator:
    def __init__(
        self,
        item_db_dir: str,
        skill_tree_dir: str,
        output_dir: str,
        old_item_db_dir: Optional[str] = None,
        old_label: str = "Retail",
        new_label: str = "BKDiablo",
        game_data_dir: Optional[str] = None,
        layout_data_dir: Optional[str] = None,
    ):
        self.item_db_dir = item_db_dir
        self.skill_tree_dir = skill_tree_dir
        self.output_dir = output_dir
        self.old_item_db_dir = old_item_db_dir
        self.old_label = old_label
        self.new_label = new_label
        self.game_data_dir = game_data_dir or os.path.join(REPO_ROOT, "mods", "BKDiablo", "bkdiablo.mpq")
        self.layout_data_dir = layout_data_dir
        self.renderer = WikiRenderer()
        self.writer = WikiOutputWriter(output_dir)
        self.manifest: List[Dict[str, Any]] = []

    def generate(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        self.manifest = []
        self.writer.generated_paths = set()

        items = self._load_items()
        old_items = (
            self._load_items(self.old_item_db_dir)
            if self.old_item_db_dir
            else {family: [] for family in ITEM_FAMILIES}
        )
        old_item_index = self._index_items(old_items)
        class_pages = self._load_class_pages()
        area_entries = self._load_area_entries()
        base_item_families = self._load_base_item_families()
        recipe_groups = self._load_recipe_groups()
        monster_groups = self._load_monster_groups()
        misc_groups = self._load_misc_groups()
        mechanics_summary = self._load_mechanics_summary()

        self._write_assets()
        item_entries = self._write_item_pages(items, old_item_index)
        class_entries = self._write_class_pages(class_pages)
        self._write_base_item_pages(base_item_families)
        self._write_recipe_pages(recipe_groups)
        self._write_bestiary_pages(monster_groups)
        self._write_misc_pages(misc_groups)
        self._write_mechanics_pages(mechanics_summary)
        report_entries = self._publish_reports()
        self._write_indexes(item_entries, class_entries, report_entries, area_entries, base_item_families, recipe_groups, monster_groups, misc_groups)
        self._write_patch_notes_draft(item_entries, class_entries)
        self._write_item_index_data(item_entries)
        self._write_area_index_data(area_entries)
        self._write_manifest()
        self.writer.remove_stale_files()

    def _load_base_item_families(self) -> List[BaseItemFamilyDTO]:
        repo = D2Repository(self.game_data_dir)
        resolver = PropertyResolverService(repo)
        service = BaseItemAnalyzerService(repo, resolver)
        return service.analyze_base_items()

    def _write_base_item_pages(self, families: List[BaseItemFamilyDTO]) -> None:
        self._write_page(
            title=f"Base Items | {self.new_label} Wiki",
            output_path=WikiRoutes.bases_index_output_path(),
            template_name="bases_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "armor.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "weapons.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "itemtypes.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "magicprefix.txt"),
            ],
            families=families,
        )

    def _load_recipe_groups(self) -> List[CubeRecipeGroupDTO]:
        repo = D2Repository(self.game_data_dir)
        service = CubeAnalyzerService(repo)
        return service.analyze_all_recipes()

    def _write_recipe_pages(self, groups: List[CubeRecipeGroupDTO]) -> None:
        self._write_page(
            title=f"Cube Recipes | {self.new_label} Wiki",
            output_path=WikiRoutes.recipes_index_output_path(),
            template_name="recipes_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "cubemain.txt"),
            ],
            groups=groups,
        )

    def _load_monster_groups(self) -> List[MonsterActGroupDTO]:
        repo = D2Repository(self.game_data_dir)
        service = MonsterAnalyzerService(repo)
        return service.analyze_monsters()

    def _write_bestiary_pages(self, groups: List[MonsterActGroupDTO]) -> None:
        self._write_page(
            title=f"Bestiary | {self.new_label} Wiki",
            output_path=WikiRoutes.bestiary_index_output_path(),
            template_name="bestiary_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "monstats.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "levels.txt"),
            ],
            groups=groups,
        )

    def _load_misc_groups(self) -> List[MiscGroupDTO]:
        repo = D2Repository(self.game_data_dir)
        service = MiscAnalyzerService(repo)
        return service.analyze_misc_items()

    def _write_misc_pages(self, groups: List[MiscGroupDTO]) -> None:
        self._write_page(
            title=f"Materials & Runes | {self.new_label} Wiki",
            output_path=WikiRoutes.misc_index_output_path(),
            template_name="misc_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "misc.txt"),
            ],
            groups=groups,
        )

    def _load_mechanics_summary(self) -> MechanicsSummaryDTO:
        repo = D2Repository(self.game_data_dir)
        retail_repo = D2Repository(os.path.join(REPO_ROOT, "data", "retail"))
        service = MechanicsAnalyzerService(repo, retail_repo)
        return service.analyze_mechanics()

    def _write_mechanics_pages(self, summary: MechanicsSummaryDTO) -> None:
        self._write_page(
            title=f"Mechanics & Progression | {self.new_label} Wiki",
            output_path=WikiRoutes.mechanics_output_path(),
            template_name="mechanics.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "experience.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "difficultylevels.txt"),
            ],
            summary=summary,
        )

    def _load_items(self, item_db_dir: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        items: Dict[str, List[Dict[str, Any]]] = {family: [] for family in ITEM_FAMILIES}
        source_dir = item_db_dir or self.item_db_dir
        if not source_dir or not os.path.isdir(source_dir):
            return items

        for root, _, files in os.walk(source_dir):
            for filename in files:
                if not filename.endswith(".json"):
                    continue

                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, source_dir).replace("\\", "/")
                with open(full_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)

                if rel_path.startswith("uniques/"):
                    family = "unique"
                elif rel_path.startswith("sets/"):
                    family = "set"
                elif rel_path.startswith("runewords/"):
                    family = "runeword"
                else:
                    continue

                for entry in payload:
                    record = dict(entry)
                    record["_source_rel_path"] = rel_path
                    if self._should_include_item(record, family):
                        items[family].append(record)

        return items

    def _index_items(self, items: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        index: Dict[str, Dict[str, Dict[str, Any]]] = {family: {} for family in ITEM_FAMILIES}
        for family, entries in items.items():
            for entry in entries:
                index[family][self._item_identity(entry, family)] = entry
        return index

    def _load_class_pages(self) -> List[Dict[str, Any]]:
        pages: List[Dict[str, Any]] = []
        if not os.path.isdir(self.skill_tree_dir):
            return pages

        for filename in sorted(os.listdir(self.skill_tree_dir)):
            if not filename.endswith("_skills.md"):
                continue

            full_path = os.path.join(self.skill_tree_dir, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            heading = content.splitlines()[0].lstrip("# ").strip() if content else filename
            class_name = heading.replace(" Skill Tree", "").strip()
            pages.append(
                {
                    "class_name": class_name,
                    "skills": self._parse_skill_tree_markdown(content),
                    "source_path": full_path,
                }
            )

        return pages

    def _load_area_entries(self) -> List[Dict[str, Any]]:
        if not os.path.isdir(self.game_data_dir):
            return []
        return AreaFarmingDataBuilder(self.game_data_dir, layout_data_dir=self.layout_data_dir).build()

    def _parse_skill_tree_markdown(self, content: str) -> List[Dict[str, Any]]:
        lines = content.splitlines()
        skills: List[Dict[str, Any]] = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line.startswith("## "):
                i += 1
                continue

            skill_name = line[3:].strip()
            i += 1
            wip = False
            table_rows: List[Dict[str, str]] = []
            synergies: List[Dict[str, str]] = []

            while i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith("## "):
                    break
                if stripped == "> Work in Progress":
                    wip = True
                    i += 1
                    continue
                if stripped.startswith("| Effect |"):
                    i += 2
                    while i < len(lines):
                        row_line = lines[i].strip()
                        if not row_line.startswith("|"):
                            break
                        parts = [part.strip() for part in row_line.strip("|").split("|")]
                        if len(parts) >= 7:
                            table_rows.append(
                                {
                                    "effect": _strip_markdown_markup(parts[0]),
                                    "scaling": _strip_markdown_markup(parts[1]),
                                    "l1": _strip_markdown_markup(parts[2]),
                                    "l10": _strip_markdown_markup(parts[3]),
                                    "l20": _strip_markdown_markup(parts[4]),
                                    "l20_soft10": _strip_markdown_markup(parts[5]),
                                    "limit": _strip_markdown_markup(parts[6]),
                                }
                            )
                        i += 1
                    continue
                if stripped == "### Synergies":
                    i += 1
                    while i < len(lines):
                        syn_line = lines[i].strip()
                        if not syn_line.startswith("* "):
                            break
                        match = re.match(r"\* \*\*(.+?)\*\*: (.+)", syn_line)
                        if match:
                            synergies.append(
                                {
                                    "name": _strip_markdown_markup(match.group(1)),
                                    "effect": _strip_markdown_markup(match.group(2)),
                                }
                            )
                        i += 1
                    continue
                i += 1

            skills.append(
                {
                    "name": skill_name,
                    "slug": _slugify(skill_name),
                    "work_in_progress": wip,
                    "effects": table_rows,
                    "synergies": synergies,
                }
            )

        return skills

    def _write_assets(self) -> None:
        for filename in sorted(os.listdir(ASSET_SOURCE_DIR)):
            source_path = os.path.join(ASSET_SOURCE_DIR, filename)
            if os.path.isfile(source_path):
                self.writer.copy_asset(source_path, f"assets/{filename}")

    def _write_item_pages(
        self,
        items: Dict[str, List[Dict[str, Any]]],
        old_item_index: Dict[str, Dict[str, Dict[str, Any]]],
    ) -> Dict[str, List[Dict[str, str]]]:
        page_entries: Dict[str, List[Dict[str, str]]] = {family: [] for family in ITEM_FAMILIES}
        used_paths: Dict[str, Dict[str, int]] = {family: {} for family in ITEM_FAMILIES}

        for family, entries in items.items():
            for entry in sorted(entries, key=self._item_sort_key):
                title = self._item_title(entry, family)
                old_entry = old_item_index.get(family, {}).get(self._item_identity(entry, family))
                status = self._item_diff_status(entry, old_entry)
                slug = self._item_slug(entry, family, title, used_paths[family])
                output_path = WikiRoutes.item_output_path(family, slug)
                href = WikiRoutes.route_from_output_path(output_path)
                page_entries[family].append(
                    {
                        "title": title,
                        "href": href,
                        "summary": self._item_summary(entry, family),
                        "search_text": self._item_search_text(entry, family),
                        "status": status,
                        "item_group": self._item_filter_group(entry, family),
                        "item_type": self._item_filter_type(entry, family),
                    }
                )

                self._write_page(
                    title=f"{title} | {family.title()} Item",
                    output_path=output_path,
                    template_name="item.html",
                    category=family,
                    source_files=[entry["_source_rel_path"]],
                    page=self._item_page_context(entry, family, title, old_entry),
                )

        return page_entries

    def _write_class_pages(self, class_pages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        entries: List[Dict[str, str]] = []
        for page in class_pages:
            title = page["class_name"]
            output_path = WikiRoutes.class_output_path(_slugify(title))
            href = WikiRoutes.route_from_output_path(output_path)
            self._write_page(
                title=f"{title} | Class Skills",
                output_path=output_path,
                template_name="class.html",
                category="class",
                source_files=[page["source_path"]],
                page=page,
            )
            entries.append(
                {
                    "title": title,
                    "href": href,
                    "summary": f"{len(page['skills'])} generated skill entries",
                    "search_text": f"{title} {' '.join(skill['name'] for skill in page['skills'])}",
                }
            )
        return entries

    def _write_indexes(
        self,
        item_entries: Dict[str, List[Dict[str, str]]],
        class_entries: List[Dict[str, str]],
        report_entries: List[Dict[str, str]],
        area_entries: List[Dict[str, Any]],
        base_item_families: List[BaseItemFamilyDTO],
        recipe_groups: List[CubeRecipeGroupDTO],
        monster_groups: List[MonsterActGroupDTO],
        misc_groups: List[MiscGroupDTO],
    ) -> None:
        self._write_page(
            title="BT Diablo Data Wiki",
            output_path=WikiRoutes.home_output_path(),
            template_name="home.html",
            category="index",
            source_files=[],
            item_counts={family: len(item_entries[family]) for family in ITEM_FAMILIES},
            class_count=len(class_entries),
            area_count=len(area_entries),
            base_family_count=len(base_item_families),
            recipe_count=sum(len(g["recipes"]) for g in recipe_groups),
            monster_count=sum(len(g["monsters"]) for g in monster_groups),
            misc_count=sum(len(g["members"]) for g in misc_groups),
            total_items=sum(len(entries) for entries in item_entries.values()),
            reports=report_entries,
        )

        group_to_types: Dict[str, set[str]] = {}
        for entries in item_entries.values():
            for entry in entries:
                group_to_types.setdefault(entry["item_group"], set()).add(entry["item_type"])

        self._write_page(
            title="All Items | BT Diablo Data Wiki",
            output_path=WikiRoutes.items_index_output_path(),
            template_name="items_index.html",
            category="index",
            source_files=[],
            family_counts={family: len(item_entries[family]) for family in ITEM_FAMILIES},
            item_groups=[
                {"name": group, "types": sorted(group_to_types[group])}
                for group in sorted(group_to_types)
            ],
        )

        self._write_page(
            title="Classes | BT Diablo Data Wiki",
            output_path=WikiRoutes.classes_index_output_path(),
            template_name="classes_index.html",
            category="index",
            source_files=[],
            classes=class_entries,
        )

        self._write_page(
            title="Areas | BT Diablo Data Wiki",
            output_path=WikiRoutes.areas_index_output_path(),
            template_name="areas_index.html",
            category="index",
            source_files=[
                os.path.join(self.game_data_dir, "data", "global", "excel", "levels.txt"),
                os.path.join(self.game_data_dir, "data", "global", "excel", "monstats.txt"),
                os.path.join(REPO_ROOT, "docs", "Diablo_II_Data_File_Guide", "levels.md"),
            ],
            area_count=len(area_entries),
        )

        self._write_page(
            title="Reports | BT Diablo Data Wiki",
            output_path=WikiRoutes.reports_index_output_path(),
            template_name="reports_index.html",
            category="index",
            source_files=[],
            reports=report_entries,
        )

    def _write_patch_notes_draft(
        self,
        item_entries: Dict[str, List[Dict[str, str]]],
        class_entries: List[Dict[str, str]],
    ) -> None:
        self._write_page(
            title="Full Patch Notes Draft | BT Diablo Data Wiki",
            output_path=WikiRoutes.patch_notes_output_path(),
            template_name="patch_notes.html",
            category="patch",
            source_files=[],
            total_items=sum(len(entries) for entries in item_entries.values()),
            class_count=len(class_entries),
        )

    def _write_item_index_data(self, item_entries: Dict[str, List[Dict[str, str]]]) -> None:
        rows = [
            {
                "title": entry["title"],
                "href": entry["href"],
                "family": family,
                "status": entry["status"],
                "item_group": entry["item_group"],
                "item_type": entry["item_type"],
                "summary": entry["summary"],
                "search_text": entry["search_text"],
            }
            for family in ITEM_FAMILIES
            for entry in item_entries[family]
        ]
        self.writer.write_text("data/items-index.json", json.dumps(rows, indent=2))

    def _write_area_index_data(self, area_entries: List[Dict[str, Any]]) -> None:
        self.writer.write_text("data/areas-index.json", json.dumps(area_entries, indent=2))

    def _publish_reports(self) -> List[Dict[str, str]]:
        reports_root = os.path.normpath(os.path.join(self.output_dir, ".."))
        entries: List[Dict[str, str]] = []
        for report in REPORT_SOURCES:
            source_dir = os.path.join(reports_root, report["source_dir"])
            if not os.path.isdir(source_dir):
                continue

            copied_files = 0
            for root, _, files in os.walk(source_dir):
                for filename in files:
                    if not filename.endswith((".html", ".css", ".json")):
                        continue
                    source_path = os.path.join(root, filename)
                    rel_source = os.path.relpath(source_path, source_dir).replace("\\", "/")
                    rel_output = f"{report['output_dir']}/{rel_source}"
                    self.writer.copy_asset(source_path, rel_output)
                    copied_files += 1

            if copied_files == 0:
                continue

            href = WikiRoutes.route_from_output_path(f"{report['output_dir']}/index.html")
            entry = {
                "title": report["title"],
                "href": href,
                "summary": report["description"],
                "source_dir": report["source_dir"],
                "source_kind": report["source_kind"],
                "file_count": str(copied_files),
            }
            entries.append(entry)
            self.manifest.append(
                {
                    "title": report["title"],
                    "path": href,
                    "category": "report",
                    "sources": [report["source_dir"]],
                }
            )
        return entries

    def _write_manifest(self) -> None:
        self.writer.write_text("manifest.json", json.dumps(self.manifest, indent=2))

    def _write_page(
        self,
        title: str,
        output_path: str,
        template_name: str,
        category: str,
        source_files: List[str],
        **context: Any,
    ) -> None:
        document = self.renderer.render(
            template_name,
            title=title,
            site_root=WikiRoutes.site_root_for_output_path(output_path),
            old_label=self.old_label,
            new_label=self.new_label,
            **context,
        )
        self.writer.write_text(output_path, document)
        self.manifest.append(
            {
                "title": title,
                "path": WikiRoutes.route_from_output_path(output_path),
                "category": category,
                "sources": source_files,
            }
        )

    def _item_page_context(
        self,
        entry: Dict[str, Any],
        family: str,
        title: str,
        old_entry: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        chips = [{"label": family.title(), "tone": "default"}, {"label": self.new_label, "tone": "accent"}]
        if family == "runeword":
            chips.append({"label": "Runeword", "tone": "accent"})
            stats = [
                {"label": "Runes", "value": " + ".join(entry.get("runes", [])) or "Unknown"},
                {"label": "Base Items", "value": ", ".join(entry.get("base_items", [])) or "Unknown"},
                {"label": "Property Count", "value": str(len(entry.get("properties", [])))},
            ]
        else:
            chips.append(
                {
                    "label": "Set Item" if family == "set" else entry.get("item_type", "Item"),
                    "tone": "accent",
                }
            )
            stats = [
                {"label": "Base Item", "value": entry.get("base_item", "Unknown")},
                {"label": "Item Type", "value": entry.get("item_type", "Unknown")},
                {"label": "Level Requirement", "value": entry.get("lvl_req", "0")},
            ]
            if family == "set" and entry.get("raw_row", {}).get("set"):
                stats.append({"label": "Set", "value": entry["raw_row"]["set"]})

        properties = [
            {
                "text": str(prop.get("resolved_text", "")),
                "is_warning": "unknown property:" in str(prop.get("resolved_text", "")).lower(),
            }
            for prop in entry.get("properties", [])
        ]
        rune_properties = [
            {
                "rune": str(rune_entry.get("rune", "")),
                "properties": [
                    {
                        "text": str(prop.get("resolved_text", "")),
                        "is_warning": "unknown property:" in str(prop.get("resolved_text", "")).lower(),
                    }
                    for prop in rune_entry.get("properties", [])
                ],
            }
            for rune_entry in entry.get("rune_properties", [])
        ]
        return {
            "title": title,
            "summary": self._item_summary(entry, family),
            "chips": chips,
            "stats": stats,
            "properties": properties,
            "rune_properties": rune_properties,
            "source_rel_path": entry.get("_source_rel_path", ""),
            "comparison": self._item_comparison_context(entry, family, old_entry),
        }

    def _item_comparison_context(
        self,
        entry: Dict[str, Any],
        family: str,
        old_entry: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if old_entry is None:
            return {"state": "added", "rows": []}

        rows: List[Tuple[str, str, str]] = []
        for label, old_value, new_value in self._comparison_stat_rows(entry, family, old_entry):
            if old_value != new_value:
                rows.append((label, old_value, new_value))
        for label, old_value, new_value in self._comparison_property_rows(entry, old_entry):
            if old_value != new_value:
                rows.append((label, old_value, new_value))
        return {
            "state": "modified" if rows else "unchanged",
            "rows": [{"label": label, "old": old_value, "new": new_value} for label, old_value, new_value in rows],
        }

    @staticmethod
    def _item_sort_key(entry: Dict[str, Any]) -> str:
        return (entry.get("display_name") or entry.get("name") or entry.get("id") or "").lower()

    @staticmethod
    def _item_identity(entry: Dict[str, Any], family: str) -> str:
        title = entry.get("display_name") or entry.get("name") or entry.get("id") or ""
        if family == "runeword":
            return title
        if family == "set":
            set_name = entry.get("raw_row", {}).get("set", "")
            return f"{title}|{entry.get('base_item', '')}|{set_name}"
        return f"{title}|{entry.get('base_item', '')}"

    @staticmethod
    def _item_diff_status(entry: Dict[str, Any], old_entry: Optional[Dict[str, Any]]) -> str:
        if old_entry is None:
            return "added"
        if WikiGenerator._entries_match(entry, old_entry):
            return "unchanged"
        return "modified"

    @staticmethod
    def _entries_match(entry: Dict[str, Any], old_entry: Dict[str, Any]) -> bool:
        keys = ["base_item", "item_type", "lvl_req"]
        if any(str(entry.get(key, "")) != str(old_entry.get(key, "")) for key in keys):
            return False
        return WikiGenerator._property_texts(entry) == WikiGenerator._property_texts(old_entry)

    @staticmethod
    def _property_texts(entry: Dict[str, Any]) -> List[str]:
        return [str(prop.get("resolved_text", "")) for prop in entry.get("properties", [])]

    @staticmethod
    def _comparison_stat_rows(
        entry: Dict[str, Any],
        family: str,
        old_entry: Dict[str, Any],
    ) -> List[Tuple[str, str, str]]:
        if family == "runeword":
            return [
                ("Runes", " + ".join(old_entry.get("runes", [])), " + ".join(entry.get("runes", []))),
                ("Base Items", ", ".join(old_entry.get("base_items", [])), ", ".join(entry.get("base_items", []))),
                ("Property Count", str(len(old_entry.get("properties", []))), str(len(entry.get("properties", [])))),
            ]

        fields = [
            ("Base Item", str(old_entry.get("base_item", "")), str(entry.get("base_item", ""))),
            ("Item Type", str(old_entry.get("item_type", "")), str(entry.get("item_type", ""))),
            ("Level Requirement", str(old_entry.get("lvl_req", "")), str(entry.get("lvl_req", ""))),
        ]
        if family == "set":
            fields.append(
                (
                    "Set",
                    str(old_entry.get("raw_row", {}).get("set", "")),
                    str(entry.get("raw_row", {}).get("set", "")),
                )
            )
        return fields

    @staticmethod
    def _comparison_property_rows(
        entry: Dict[str, Any],
        old_entry: Dict[str, Any],
    ) -> List[Tuple[str, str, str]]:
        old_props = WikiGenerator._property_occurrence_map(old_entry)
        new_props = WikiGenerator._property_occurrence_map(entry)
        all_keys = list(new_props.keys()) + [key for key in old_props.keys() if key not in new_props]
        return [
            (
                WikiGenerator._comparison_property_label(
                    old_props.get(key, ""),
                    new_props.get(key, ""),
                    key[0],
                    key[2],
                ),
                old_props.get(key, ""),
                new_props.get(key, ""),
            )
            for key in all_keys
        ]

    @staticmethod
    def _property_occurrence_map(entry: Dict[str, Any]) -> Dict[Tuple[str, str, int], str]:
        occurrences: Dict[Tuple[str, str], int] = {}
        values: Dict[Tuple[str, str, int], str] = {}
        for prop in entry.get("properties", []):
            code = str(prop.get("code", "")).strip() or "unknown"
            param = str(prop.get("param", "")).strip()
            base_key = (code, param)
            occurrences[base_key] = occurrences.get(base_key, 0) + 1
            values[(code, param, occurrences[base_key])] = str(prop.get("resolved_text", "")).strip()
        return values

    @staticmethod
    def _comparison_property_label(old_value: str, new_value: str, code: str, occurrence: int) -> str:
        old_label = WikiGenerator._comparison_text_label(old_value)
        new_label = WikiGenerator._comparison_text_label(new_value)
        if old_value and new_value:
            if old_label and old_label == new_label:
                return old_label
            if old_label and new_label:
                return f"{old_label} / {new_label}"
            return f"Changed Stat #{occurrence}"
        if new_value:
            return f"Added: {new_label or code}"
        if old_value:
            return f"Removed: {old_label or code}"
        return f"Stat #{occurrence}"

    @staticmethod
    def _comparison_text_label(value: str) -> str:
        if not value:
            return ""
        text = str(value)
        text = re.sub(r"Unknown property:\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\([^)]*\)", " ", text)
        text = re.sub(r"[-+]?\d+(?:\.\d+)?", " ", text)
        text = re.sub(r"[%#/]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" -")
        return text[:1].upper() + text[1:] if text else ""

    @staticmethod
    def _should_include_item(entry: Dict[str, Any], family: str) -> bool:
        properties = entry.get("properties", [])
        if family == "runeword":
            base_items = [str(base).strip() for base in entry.get("base_items", []) if str(base).strip()]
            runes = [str(rune).strip() for rune in entry.get("runes", []) if str(rune).strip()]
            if not properties and not runes:
                if not base_items or all(base.lower() == "expansion" for base in base_items):
                    return False
            return True

        title = str(entry.get("display_name") or entry.get("id") or entry.get("name") or "").strip()
        base_item = str(entry.get("base_item", "")).strip()
        item_type = str(entry.get("item_type", "")).strip()
        if not properties:
            if title.lower() == "blank charm":
                return False
            if base_item.lower() == "expansion" and item_type.lower() == "expansion":
                return False
        return True

    @staticmethod
    def _item_title(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            return entry.get("name", "Unknown Runeword")
        return entry.get("display_name") or entry.get("id") or entry.get("name") or "Unknown Item"

    @staticmethod
    def _item_summary(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            base_items = ", ".join(entry.get("base_items", [])) or "Unknown base"
            return f"Runeword for {base_items} with {len(entry.get('properties', []))} generated properties."
        item_type = entry.get("item_type", "Item")
        base_item = entry.get("base_item", "Unknown base")
        lvl_req = entry.get("lvl_req", "0")
        return f"{item_type} based on {base_item}. Level requirement {lvl_req}."

    @staticmethod
    def _item_search_text(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            runes = " ".join(entry.get("runes", []))
            bases = " ".join(entry.get("base_items", []))
            props = " ".join(prop.get("resolved_text", "") for prop in entry.get("properties", []))
            return f"{entry.get('name', '')} {runes} {bases} {props}"
        props = " ".join(prop.get("resolved_text", "") for prop in entry.get("properties", []))
        return (
            f"{entry.get('display_name', '')} "
            f"{entry.get('base_item', '')} "
            f"{entry.get('item_type', '')} "
            f"{entry.get('raw_row', {}).get('set', '')} "
            f"{props}"
        )

    @staticmethod
    def _item_filter_type(entry: Dict[str, Any], family: str) -> str:
        if family == "runeword":
            base_items = entry.get("base_items", [])
            return str(base_items[0]) if base_items else "Runeword"
        return str(entry.get("item_type", "")).strip() or "Item"

    @staticmethod
    def _item_filter_group(entry: Dict[str, Any], family: str) -> str:
        category = WikiGenerator._item_filter_type(entry, family).lower()
        if any(token in category for token in ["amazon", "assassin", "orb", "hand to hand", "grimoire"]):
            return "Class Weapons"
        if "axe" in category:
            return "Axes"
        if "crossbow" in category:
            return "Crossbows"
        if "bow" in category:
            return "Bows"
        if "dagger" in category or "knife" in category:
            return "Daggers"
        if "javelin" in category:
            return "Javelins"
        if "mace" in category or "club" in category or "hammer" in category:
            return "Maces"
        if "polearm" in category:
            return "Polearms"
        if "scepter" in category:
            return "Scepters"
        if "spear" in category:
            return "Spears"
        if "staff" in category:
            return "Staves"
        if "sword" in category:
            return "Swords"
        if "throwing" in category:
            return "Throwing"
        if "wand" in category:
            return "Wands"
        if any(token in category for token in ["voodoo", "pelt", "primal", "auric"]):
            return "Class Armors"
        if "amulet" in category:
            return "Amulets"
        if "ring" in category:
            return "Rings"
        if "charm" in category:
            return "Charms"
        if "jewel" in category:
            return "Jewels"
        if any(token in category for token in ["helm", "circlet", "merc"]):
            return "Helms"
        if any(token in category for token in ["armor", "tors"]):
            return "Chests"
        if "shield" in category:
            return "Shields"
        if "glove" in category:
            return "Gloves"
        if "belt" in category:
            return "Belts"
        if "boot" in category:
            return "Boots"
        return "Others"

    @staticmethod
    def _item_slug(entry: Dict[str, Any], family: str, title: str, used_paths: Dict[str, int]) -> str:
        base_slug = _slugify(title)
        if family == "runeword":
            disambiguator = entry.get("base_items", [""])[0]
        else:
            disambiguator = entry.get("base_item") or entry.get("id") or ""

        candidate = base_slug
        if candidate in used_paths:
            disambiguation_slug = _slugify(disambiguator)
            if disambiguation_slug:
                candidate = f"{base_slug}-{disambiguation_slug}"
        root_candidate = candidate
        suffix = 2
        while candidate in used_paths:
            candidate = f"{root_candidate}-{suffix}"
            suffix += 1
        used_paths[candidate] = 1
        return candidate
