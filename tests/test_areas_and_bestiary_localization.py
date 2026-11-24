import json
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.repository import (
    D2Repository,
    damage_type_options,
    resolve_act_name,
    resolve_element_name,
    resolve_immunity_label,
)
from d2lib.services.monsters import MonsterAnalyzerService
from d2lib.wiki.builders import (
    AreaFarmingDataBuilder,
    ItemIconExporter,
    derive_area_level_breakpoints,
    derive_item_drop_level_breakpoints,
)
from d2lib.wiki import WikiOutputWriter
from d2lib.wiki.generator import WikiGenerator
from d2lib.wiki.mediawiki import MediaWikiRenderer
from d2lib.wiki.publication import empty_wiki_site


def _write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(fieldnames) + "\n")
        for row in rows:
            f.write("\t".join(str(row.get(col, "")) for col in fieldnames) + "\n")


def _write_strings(root: Path, filename: str, entries: list[dict[str, str]]) -> None:
    str_dir = root / "data" / "local" / "lng" / "strings"
    str_dir.mkdir(parents=True, exist_ok=True)
    (str_dir / filename).write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")


def _write_ds1(path: Path, objects: list[tuple[int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ints = [18, 0, 0, 0, 0, 0, 0, 1, 0, 0, len(objects)]
    for obj_type, obj_id in objects:
        ints.extend([obj_type, obj_id, 0, 0, 0])
    path.write_bytes(struct.pack(f"<{len(ints)}i", *ints))


class _FrozenRepo:
    """Strictly in-memory frozen D2 repository with no external disk fallback."""

    def __init__(self, tables: dict[str, list[dict[str, str]]], strings: dict[str, str]) -> None:
        self._tables = tables
        self.strings = {k.lower(): v for k, v in strings.items()}

    def get_excel_table(self, table_name: str) -> list[dict[str, str]]:
        return list(self._tables.get(table_name, []))

    def get_string(self, key: str) -> str:
        return self.strings.get(str(key or "").lower(), str(key or ""))

    def load_tsv(self, file_path: str) -> list[dict[str, str]]:
        return []


def _locale_strings(locale: str) -> dict[str, str]:
    by_locale = {
        "enUS": {
            "Act1": "Act 1",
            "Act3": "Act 3",
            "Act5": "Act 5",
            "strskltree25": "Fire",
            "strskltree23": "Cold",
            "strskltree24": "Lightning",
            "strskltree17": "Poison",
            "strbsmagic": "Magic",
            "strScaryMonDesc1": "Immune to Fire",
            "strScaryMonDesc2": "Immune to Cold",
            "strScaryMonDesc3": "Immune to Lightning",
            "strScaryMonDesc4": "Immune to Poison",
            "strScaryMonDesc5": "Immune to Physical",
            "strScaryMonDesc6": "Immune to Magic",
            "Cold Cave": "Cold Cave",
            "Lower Kurast": "Lower Kurast",
            "coldbeast": "Cold Beast",
            "stonebeast": "Stone Beast",
            "chest": "Chest",
        },
        "deDE": {
            "Act1": "Akt 1",
            "Act3": "Akt 3",
            "Act5": "Akt 5",
            "strskltree25": "Feuer",
            "strskltree23": "Kälte",
            "strskltree24": "Blitz",
            "strskltree17": "Gift",
            "strbsmagic": "Magie",
            "strScaryMonDesc1": "Immun gegen Feuer",
            "strScaryMonDesc2": "Immun gegen Kälte",
            "strScaryMonDesc3": "Immun gegen Blitze",
            "strScaryMonDesc4": "Immun gegen Gift",
            "strScaryMonDesc5": "Immun gegen Körperschäden",
            "strScaryMonDesc6": "Immun gegen Magie",
            "Cold Cave": "Kalte Höhle",
            "Lower Kurast": "Unter-Kurast",
            "coldbeast": "Kältebestie",
            "stonebeast": "Steinbestie",
            "chest": "Truhe",
        },
        "koKR": {
            "Act1": "1막",
            "Act3": "3막",
            "Act5": "5막",
            "strskltree25": "화염",
            "strskltree23": "냉기",
            "strskltree24": "번개",
            "strskltree17": "독",
            "strbsmagic": "마법",
            "strScaryMonDesc1": "화염 면역",
            "strScaryMonDesc2": "냉기 면역",
            "strScaryMonDesc3": "번개 면역",
            "strScaryMonDesc4": "독 면역",
            "strScaryMonDesc5": "물리 면역",
            "strScaryMonDesc6": "마법 면역",
            "Cold Cave": "얼음 동굴",
            "Lower Kurast": "하부 쿠라스트",
            "coldbeast": "얼음 야수",
            "stonebeast": "돌 야수",
            "chest": "궤짝",
        },
    }
    return by_locale[locale]


def _frozen_tables() -> dict[str, list[dict[str, str]]]:
    return {
        "levels": [
            {
                "Id": "10",
                "Name": "Act 1 - Cold Cave",
                "LevelName": "Cold Cave",
                "Act": "0",
                "DrlgType": "1",
                "MonLvl(H)": "42",
                "MonLvlEx(H)": "68",
                "MonDen(H)": "4000",
                "MonUMin(H)": "6",
                "MonUMax(H)": "8",
                "SizeX": "80",
                "SizeY": "80",
                "nmon1": "coldbeast",
                "nmon2": "stonebeast",
            },
            {
                "Id": "88",
                "Name": "Act 3 - Kurast 1",
                "LevelName": "Lower Kurast",
                "Act": "2",
                "DrlgType": "3",
                "MonLvl(H)": "55",
                "MonLvlEx(H)": "55",
                "MonDen(H)": "1200",
                "MonUMin(H)": "2",
                "MonUMax(H)": "4",
                "SizeX": "100",
                "SizeY": "100",
                "nmon1": "stonebeast",
            },
        ],
        "monstats": [
            {
                "Id": "coldbeast",
                "NameStr": "coldbeast",
                "Level": "20",
                "Level(N)": "45",
                "Level(H)": "68",
                "MinHP(H)": "100",
                "MaxHP(H)": "150",
                "MinGrp": "2",
                "MaxGrp": "4",
                "Rarity": "1",
                "ResCo(H)": "100",
            },
            {
                "Id": "stonebeast",
                "NameStr": "stonebeast",
                "Level": "15",
                "Level(N)": "40",
                "Level(H)": "55",
                "MinHP(H)": "90",
                "MaxHP(H)": "120",
                "MinGrp": "1",
                "MaxGrp": "2",
                "Rarity": "1",
                "ResDm(H)": "105",
            },
        ],
        "weapons": [{"code": "7gm", "level": "68"}],
        "armor": [],
        "uniqueitems": [],
        "setitems": [],
        "objects": [
            {"*ID": "397", "Class": "ConsolationChest", "Name": "chest", "*Description": "sparklychest", "InitFn": "57"},
            {"*ID": "584", "Class": "PlaceUniqueChest", "Name": "chest", "*Description": "unique chest", "InitFn": "79"},
        ],
        "objpreset": [
            {"Act": "3", "Index": "2", "ObjectClass": "PlaceUniqueChest"},
        ],
        "lvlprest": [
            {"Def": "1", "LevelId": "0", "Name": "Act 3 - Slums 16x16", "File1": "Act3/Kurast/Slums16x16_1.ds1"},
        ],
        "lvlmaze": [],
        "monstats2": [],
    }


class TestAreasAndBestiaryLocalization(unittest.TestCase):
    def test_builders_module_has_no_hardcoded_local_machine_path(self):
        builders_path = Path(SCRIPT_DIR) / "d2lib" / "wiki" / "builders.py"
        content = builders_path.read_text(encoding="utf-8")
        self.assertNotIn("DEFAULT_RETAIL_DATA_DIR", content)
        self.assertNotIn("E:\\Games", content)
        self.assertNotIn("Diablo II Resurrected", content)

    def test_act_element_and_immunity_localization_helpers_across_locales(self):
        for locale, expected_act, expected_phys, expected_immune in (
            ("enUS", "Act 1", "Physical", "Immune to Physical"),
            ("deDE", "Akt 1", "Körperschäden", "Immun gegen Körperschäden"),
            ("koKR", "1막", "물리", "물리 면역"),
        ):
            repo = _FrozenRepo({}, _locale_strings(locale))
            self.assertEqual(expected_act, resolve_act_name(repo, 0))
            self.assertEqual(expected_act, resolve_act_name(repo, "0"))
            self.assertEqual("Unknown", resolve_act_name(repo, None))
            self.assertEqual(expected_phys, resolve_element_name(repo, "physical"))
            self.assertEqual(expected_phys, resolve_element_name(repo, "phys"))
            self.assertEqual(expected_immune, resolve_immunity_label(repo, "physical"))
            options = {opt["code"]: opt for opt in damage_type_options(repo)}
            self.assertEqual(expected_phys, options["physical"]["label"])
            self.assertEqual(expected_immune, options["physical"]["immunity_label"])

    def test_bestiary_uses_canonical_immunity_codes_and_localized_labels(self):
        tables = _frozen_tables()
        for locale, expected_cold, expected_phys, expected_area in (
            ("enUS", "Immune to Cold", "Immune to Physical", "Cold Cave"),
            ("deDE", "Immun gegen Kälte", "Immun gegen Körperschäden", "Kalte Höhle"),
            ("koKR", "냉기 면역", "물리 면역", "얼음 동굴"),
        ):
            repo = _FrozenRepo(tables, _locale_strings(locale))
            groups = MonsterAnalyzerService(repo).analyze_monsters()
            by_id = {m["id"]: m for m in groups[0]["monsters"]}
            self.assertEqual(["cold"], by_id["coldbeast"]["immunities_hell"])
            self.assertEqual([expected_cold], by_id["coldbeast"]["immunity_labels_hell"])
            self.assertEqual([expected_area], by_id["coldbeast"]["spawn_areas"])
            self.assertEqual(["physical"], by_id["stonebeast"]["immunities_hell"])
            self.assertEqual([expected_phys], by_id["stonebeast"]["immunity_labels_hell"])
            self.assertEqual({"physical", "magic", "fire", "lightning", "cold", "poison"}, set(by_id["coldbeast"]["resists_hell"]))

            wikitext = MediaWikiRenderer().render_page(
                {
                    "kind": "bestiary_index",
                    "title": "Bestiary",
                    "output_path": "bestiary/index.html",
                    "template_name": "bestiary_index.html",
                    "category": "index",
                    "source_files": [],
                    "payload": {"groups": groups},
                },
                empty_wiki_site("Retail", "BKDiablo", locale=locale),
            )
            self.assertIn(expected_cold, wikitext)
            self.assertIn(expected_phys, wikitext)

    def test_areas_builder_localizes_acts_immunities_and_derives_kurast_and_score_dynamically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game_dir = root / "mod"
            _write_ds1(game_dir / "data" / "global" / "tiles" / "act3" / "kurast" / "slums16x16_1.ds1", [(2, 2)])
            repo_de = _FrozenRepo(_frozen_tables(), _locale_strings("deDE"))

            builder = AreaFarmingDataBuilder(str(game_dir), repository=repo_de, retail_data_dir=str(root / "missing_retail"))
            resolved_path = builder._resolve_ds1_path("Act3/Kurast/Slums16x16_1.ds1")
            self.assertIsNotNone(resolved_path)
            self.assertTrue(resolved_path.lower().endswith("slums16x16_1.ds1"))

            areas = builder.build()
            by_id = {a["level_id"]: a for a in areas}
            self.assertEqual(0, by_id[10]["act_id"])
            self.assertEqual("Akt 1", by_id[10]["act"])
            self.assertEqual(["cold", "physical"], by_id[10]["possible_immunities"])
            self.assertEqual({"cold": "Kälte", "physical": "Körperschäden"}, by_id[10]["immunity_labels"])
            self.assertEqual(
                {"cold": "Immun gegen Kälte", "physical": "Immun gegen Körperschäden"},
                by_id[10]["immunity_descriptions"],
            )
            # Dynamic can_drop_top_tier & score on non-85+ levels (max=68)
            self.assertTrue(by_id[10]["can_drop_top_tier"])
            self.assertFalse(by_id[88]["can_drop_top_tier"])
            self.assertGreater(by_id[10]["farm_score"], by_id[88]["farm_score"])
            # Kurast Act 3 preset mapped dynamically to Id=88 from levels.txt
            self.assertEqual(2, by_id[88]["act_id"])
            self.assertEqual("Akt 3", by_id[88]["act"])
            self.assertTrue(by_id[88]["has_super_chest"])
            self.assertEqual("PlaceUniqueChest", by_id[88]["super_chest_sources"][0]["object_class"])

    def test_dynamic_level_breakpoints_and_env_configured_layout_dir(self):
        self.assertEqual([42, 55, 68], derive_area_level_breakpoints([68, 42, 55, 55, 0]))
        self.assertEqual([70, 75, 80, 85], derive_area_level_breakpoints(range(67, 86)))
        self.assertEqual([20, 40], derive_item_drop_level_breakpoints([20, 40, 0]))
        large_levels = [10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 86, 87, 88, 90, 96, 99, 110]
        self.assertEqual(
            derive_item_drop_level_breakpoints(large_levels),
            sorted(set(derive_item_drop_level_breakpoints(large_levels))),
        )
        self.assertIn(110, derive_item_drop_level_breakpoints(large_levels))
        self.assertNotIn(10, derive_item_drop_level_breakpoints(large_levels))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game_dir = root / "mod"
            ext_layout = root / "external_d2r"
            _write_ds1(ext_layout / "global" / "tiles" / "Act3" / "Kurast" / "Slums16x16_1.ds1", [(2, 2)])
            repo = _FrozenRepo(_frozen_tables(), _locale_strings("enUS"))

            prev_layout = os.environ.get("D2R_LAYOUT_DATA_DIR")
            prev_data = os.environ.get("D2R_DATA_DIR")
            try:
                os.environ.pop("D2R_LAYOUT_DATA_DIR", None)
                os.environ.pop("D2R_DATA_DIR", None)
                no_layout = {a["level_id"]: a for a in AreaFarmingDataBuilder(str(game_dir), repository=repo, retail_data_dir=str(root / "missing_retail")).build()}
                self.assertFalse(no_layout[88]["has_super_chest"])

                os.environ["D2R_LAYOUT_DATA_DIR"] = str(ext_layout)
                with_env = {a["level_id"]: a for a in AreaFarmingDataBuilder(str(game_dir), repository=repo, retail_data_dir=str(root / "missing_retail")).build()}
                self.assertTrue(with_env[88]["has_super_chest"])

                exporter = ItemIconExporter(
                    WikiOutputWriter(str(root / "wiki_out")),
                    game_data_dir=str(root / "missing_mod"),
                    retail_data_dir=str(root / "missing_retail"),
                )
                self.assertTrue(exporter.export_icon(output_key="rune-r01", item_code="r01", icon_key="r01").endswith(".png"))
            finally:
                if prev_layout is None:
                    os.environ.pop("D2R_LAYOUT_DATA_DIR", None)
                else:
                    os.environ["D2R_LAYOUT_DATA_DIR"] = prev_layout
                if prev_data is None:
                    os.environ.pop("D2R_DATA_DIR", None)
                else:
                    os.environ["D2R_DATA_DIR"] = prev_data

    def test_wiki_generator_renders_localized_areas_bestiary_and_dynamic_breakpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game_dir = root / "mod"
            retail_dir = root / "retail"
            item_db = root / "item_db"
            old_item_db = root / "old_item_db"
            skill_trees = root / "skills"
            out_dir = root / "wiki"
            excel = game_dir / "data" / "global" / "excel"
            r_excel = retail_dir / "global" / "excel"

            tables = _frozen_tables()
            _write_tsv(excel / "levels.txt", list(tables["levels"][0].keys()), tables["levels"])
            _write_tsv(excel / "monstats.txt", ["Id", "NameStr", "Level", "Level(N)", "Level(H)", "MinHP(H)", "MaxHP(H)", "MinGrp", "MaxGrp", "Rarity", "ResCo(H)", "ResDm(H)"], tables["monstats"])
            _write_tsv(r_excel / "monstats.txt", ["Id", "NameStr"], [{"Id": "coldbeast", "NameStr": "coldbeast"}])
            _write_tsv(excel / "objects.txt", ["*ID", "Class", "Name", "*Description", "InitFn"], tables["objects"])
            _write_tsv(excel / "objpreset.txt", ["Act", "Index", "ObjectClass"], tables["objpreset"])
            _write_tsv(excel / "lvlprest.txt", ["Def", "LevelId", "Name", "File1"], tables["lvlprest"])
            _write_tsv(excel / "lvlmaze.txt", ["Level"], [])
            _write_tsv(excel / "monstats2.txt", ["Id"], [])
            _write_tsv(excel / "weapons.txt", ["name", "namestr", "code", "type", "level", "levelreq", "mindam", "maxdam", "reqstr", "reqdex", "gemsockets", "normcode", "ubercode", "ultracode", "speed", "durability"], [
                {"name": "Axe", "namestr": "hax", "code": "hax", "type": "axe", "level": "52", "levelreq": "30", "mindam": "5", "maxdam": "10", "gemsockets": "2", "normcode": "hax", "ubercode": "hax", "ultracode": "hax", "speed": "0", "durability": "20"}
            ])
            _write_tsv(excel / "armor.txt", ["name", "code", "type"], [])
            _write_tsv(excel / "misc.txt", ["name", "code", "type", "cost"], [])
            _write_tsv(excel / "itemtypes.txt", ["ItemType", "Code", "Equiv1", "UICategory"], [{"ItemType": "Axe", "Code": "axe", "UICategory": "axes"}])
            _write_tsv(excel / "properties.txt", ["code", "func1"], [])
            _write_tsv(excel / "itemstatcost.txt", ["Stat", "descfunc"], [])
            _write_tsv(excel / "cubemain.txt", ["description", "enabled"], [])
            _write_tsv(excel / "skills.txt", ["skill", "charclass"], [])
            _write_tsv(excel / "missiles.txt", ["Missile"], [])
            _write_tsv(excel / "charstats.txt", ["class"], [])
            _write_tsv(excel / "gamble.txt", ["name"], [])
            _write_tsv(excel / "gems.txt", ["name", "code"], [])
            _write_tsv(excel / "sets.txt", ["index", "name", "version"], [])
            _write_tsv(excel / "setitems.txt", ["index", "set", "item", "rarity", "lvl", "spawnable"], [])
            _write_tsv(excel / "uniqueitems.txt", ["index", "code", "rarity", "lvl", "spawnable"], [])
            _write_tsv(excel / "runes.txt", ["Name", "complete"], [])
            _write_tsv(excel / "superuniques.txt", ["Name"], [])
            _write_tsv(excel / "treasureclassex.txt", ["Treasure Class"], [])
            _write_tsv(excel / "automagic.txt", ["Name", "group"], [])
            _write_tsv(excel / "magicprefix.txt", ["Name", "group", "spawnable"], [])
            _write_tsv(excel / "magicsuffix.txt", ["Name", "group", "spawnable"], [])
            _write_tsv(excel / "qualityitems.txt", ["mod1code"], [])
            _write_tsv(excel / "hireling.txt", ["Hireling", "Version", "Level"], [])
            _write_tsv(excel / "experience.txt", ["Level"], [])
            _write_tsv(excel / "difficultylevels.txt", ["Name"], [])
            for tbl in ("weapons", "armor", "misc", "skills", "missiles", "charstats", "properties", "itemstatcost", "gamble", "cubemain", "sets", "hireling", "experience", "difficultylevels", "automagic", "magicprefix", "magicsuffix"):
                _write_tsv(r_excel / f"{tbl}.txt", ["id"], [])

            ko_entries = [{"Key": k, "koKR": v} for k, v in _locale_strings("koKR").items()]
            _write_strings(game_dir, "localized.json", ko_entries)
            _write_ds1(game_dir / "data" / "global" / "tiles" / "Act3" / "Kurast" / "Slums16x16_1.ds1", [(2, 2)])

            (item_db / "uniques").mkdir(parents=True, exist_ok=True)
            (item_db / "uniques" / "axes.json").write_text(
                json.dumps([{"id": "Test Axe", "display_name": "테스트 도끼", "base_item": "Axe", "item_type": "Axe", "lvl_req": "30", "raw_row": {"code": "hax", "lvl": "52"}, "properties": []}]),
                encoding="utf-8",
            )
            (old_item_db / "uniques").mkdir(parents=True, exist_ok=True)
            skill_trees.mkdir(parents=True, exist_ok=True)

            WikiGenerator(
                str(item_db),
                str(skill_trees),
                str(out_dir),
                old_item_db_dir=str(old_item_db),
                game_data_dir=str(game_dir),
                retail_data_dir=str(retail_dir),
                locale="koKR",
            ).generate()

            areas_html = (out_dir / "areas" / "index.html").read_text(encoding="utf-8")
            self.assertIn('<option value="0">1막</option>', areas_html)
            self.assertIn('<option value="2">3막</option>', areas_html)
            self.assertIn('<option value="55">55+</option>', areas_html)
            self.assertIn('<option value="68">68+</option>', areas_html)
            self.assertNotIn('<option value="85">85+</option>', areas_html)
            self.assertIn('data-avoid-immunity="physical"><span class="dot"></span>물리', areas_html)
            self.assertIn('data-immunity-meta="', areas_html)

            bestiary_html = (out_dir / "bestiary" / "index.html").read_text(encoding="utf-8")
            self.assertIn("냉기 면역", bestiary_html)
            self.assertIn("물리 면역", bestiary_html)
            self.assertIn("얼음 동굴", bestiary_html)

            items_html = (out_dir / "items" / "index.html").read_text(encoding="utf-8")
            self.assertIn('<option value="52">52+</option>', items_html)
            self.assertNotIn('<option value="60">60+</option>', items_html)
            self.assertNotIn('<option value="85">85+</option>', items_html)
