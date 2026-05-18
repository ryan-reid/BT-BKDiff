import json
import os
import sys
import tempfile
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.wiki import WikiGenerator, WikiRoutes


class TestWikiGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name
        self.item_db = os.path.join(self.root, "item_db")
        self.old_item_db = os.path.join(self.root, "old_item_db")
        self.skill_trees = os.path.join(self.root, "skill_trees")
        self.output = os.path.join(self.root, "wiki")
        self._write_fixture_data()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_json(self, root, relative_path, payload):
        full_path = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def _write_fixture_data(self):
        uniques = [
            {
                "display_name": "Twin Item",
                "base_item": "First Base",
                "item_type": "Helm",
                "lvl_req": "10",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+10 Damage"}],
            },
            {
                "display_name": "Twin Item",
                "base_item": "Second Base",
                "item_type": "Helm",
                "lvl_req": "20",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+20 Damage"}],
            },
            {
                "display_name": "Twin Item",
                "base_item": "Second Base",
                "item_type": "Helm",
                "lvl_req": "30",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+30 Damage"}],
            },
        ]
        old_uniques = [
            {
                "display_name": "Twin Item",
                "base_item": "First Base",
                "item_type": "Helm",
                "lvl_req": "10",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+5 Damage"}],
            }
        ]
        sets = [
            {
                "display_name": "Set Blade",
                "base_item": "Short Sword",
                "item_type": "Sword",
                "lvl_req": "12",
                "raw_row": {"set": "Practice Set"},
                "properties": [{"code": "ias", "param": "", "resolved_text": "+10% Increased Attack Speed"}],
            }
        ]
        runewords = [
            {
                "name": "Practice",
                "runes": ["El", "Eld"],
                "base_items": ["Melee Weapon"],
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+25% Enhanced Damage"}],
                "rune_properties": [
                    {
                        "rune": "El",
                        "properties": [{"code": "att", "param": "", "resolved_text": "+50 to Attack Rating"}],
                    }
                ],
            }
        ]
        old_runewords = [
            {
                "name": "Practice",
                "runes": ["Tal", "Eth"],
                "base_items": ["Sword"],
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+20% Enhanced Damage"}],
            }
        ]

        self._write_json(self.item_db, "uniques/others/helms.json", uniques)
        self._write_json(self.old_item_db, "uniques/others/helms.json", old_uniques)
        self._write_json(self.item_db, "sets/normal/swords.json", sets)
        self._write_json(self.item_db, "runewords/weapons.json", runewords)
        self._write_json(self.old_item_db, "runewords/weapons.json", old_runewords)

        os.makedirs(self.skill_trees, exist_ok=True)
        with open(os.path.join(self.skill_trees, "amazon_skills.md"), "w", encoding="utf-8") as f:
            f.write(
                "# Amazon Skill Tree\n\n"
                "## Magic Arrow\n\n"
                "> Work in Progress\n\n"
                "| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| Damage | Linear (+1) | +1 | +10 | +20 | +30 | -- |\n"
            )

    def _generate(self):
        generator = WikiGenerator(
            self.item_db,
            self.skill_trees,
            self.output,
            old_item_db_dir=self.old_item_db,
            old_label="Retail",
            new_label="BKDiablo",
        )
        generator.generate()
        return generator

    def test_route_builder_uses_pretty_paths(self):
        self.assertEqual("items/unique/twin-item/index.html", WikiRoutes.item_output_path("unique", "twin-item"))
        self.assertEqual("items/unique/twin-item/", WikiRoutes.route_from_output_path("items/unique/twin-item/index.html"))
        self.assertEqual("../../../", WikiRoutes.site_root_for_output_path("items/unique/twin-item/index.html"))

    def test_generation_writes_pretty_routes_and_manifest(self):
        self._generate()
        expected_paths = [
            os.path.join(self.output, "items", "unique", "twin-item", "index.html"),
            os.path.join(self.output, "items", "unique", "twin-item-second-base", "index.html"),
            os.path.join(self.output, "items", "unique", "twin-item-second-base-2", "index.html"),
            os.path.join(self.output, "items", "index.html"),
            os.path.join(self.output, "classes", "amazon", "index.html"),
        ]
        for path in expected_paths:
            self.assertTrue(os.path.exists(path), path)

        with open(os.path.join(self.output, "manifest.json"), "r", encoding="utf-8") as f:
            manifest = json.load(f)
        manifest_paths = {entry["path"] for entry in manifest}
        self.assertIn("items/unique/twin-item/", manifest_paths)
        self.assertIn("items/unique/twin-item-second-base/", manifest_paths)
        self.assertIn("items/", manifest_paths)

    def test_item_index_json_schema_and_ordering(self):
        self._generate()
        with open(os.path.join(self.output, "data", "items-index.json"), "r", encoding="utf-8") as f:
            rows = json.load(f)

        self.assertEqual(["Twin Item", "Twin Item", "Twin Item", "Set Blade", "Practice"], [row["title"] for row in rows])
        self.assertEqual(
            {"title", "href", "family", "status", "item_group", "item_type", "summary", "search_text"},
            set(rows[0].keys()),
        )
        self.assertEqual("modified", rows[0]["status"])
        self.assertEqual("added", rows[1]["status"])
        self.assertEqual("items/unique/twin-item/", rows[0]["href"])

        practice = next(row for row in rows if row["title"] == "Practice")
        self.assertEqual("modified", practice["status"])

    def test_templates_render_item_and_index_pages(self):
        self._generate()
        with open(os.path.join(self.output, "items", "unique", "twin-item", "index.html"), "r", encoding="utf-8") as f:
            item_page = f.read()
        with open(os.path.join(self.output, "items", "index.html"), "r", encoding="utf-8") as f:
            items_page = f.read()

        self.assertIn("Twin Item", item_page)
        self.assertIn("Structured diff view using Retail (Old) and BKDiablo (New).", item_page)
        self.assertIn('data-item-index-url="../data/items-index.json"', items_page)

        with open(os.path.join(self.output, "items", "runeword", "practice", "index.html"), "r", encoding="utf-8") as f:
            runeword_page = f.read()
        self.assertIn("Properties from Runes", runeword_page)
        self.assertIn("+50 to Attack Rating", runeword_page)

    def test_stale_files_are_removed(self):
        os.makedirs(self.output, exist_ok=True)
        stale_path = os.path.join(self.output, "stale.html")
        with open(stale_path, "w", encoding="utf-8") as f:
            f.write("stale")
        self._generate()
        self.assertFalse(os.path.exists(stale_path))


if __name__ == "__main__":
    unittest.main()
