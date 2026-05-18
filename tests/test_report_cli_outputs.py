import os
import json
import sys
import tempfile
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from cli import compare_all_excel, compare_item_db


def run_cli(main_func, args):
    old_argv = sys.argv[:]
    try:
        sys.argv = [main_func.__module__] + args
        main_func()
    finally:
        sys.argv = old_argv


def markdown_files_under(root):
    found = []
    for current_root, _, files in os.walk(root):
        for filename in files:
            if filename.lower().endswith(".md"):
                found.append(os.path.relpath(os.path.join(current_root, filename), root))
    return found


class TestReportCliOutputs(unittest.TestCase):
    def test_excel_comparison_exports_json_and_html_without_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            old_dir = os.path.join(temp_dir, "old")
            new_dir = os.path.join(temp_dir, "new")
            out_dir = os.path.join(temp_dir, "report")
            os.makedirs(old_dir)
            os.makedirs(new_dir)
            os.makedirs(out_dir)

            with open(os.path.join(out_dir, "SUMMARY.md"), "w", encoding="utf-8") as f:
                f.write("stale markdown")
            with open(os.path.join(old_dir, "gems.txt"), "w", encoding="utf-8") as f:
                f.write("name\tweaponMod1Code\nBer Rune\tdmg-undead\n")
            with open(os.path.join(new_dir, "gems.txt"), "w", encoding="utf-8") as f:
                f.write("name\tweaponMod1Code\nBer Rune\tdmg-norm\n")

            run_cli(
                compare_all_excel.main,
                ["--new-dir", new_dir, "--old-dir", old_dir, "--out", out_dir],
            )

            self.assertTrue(os.path.exists(os.path.join(out_dir, "gems.html")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "gems.json")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "summary.json")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "index.html")))
            self.assertEqual([], markdown_files_under(out_dir))

            with open(os.path.join(out_dir, "summary.json"), "r", encoding="utf-8") as f:
                summary = json.load(f)
            self.assertEqual("gems.html", summary["files"][0]["report_name"])

    def test_item_comparison_exports_json_and_html_without_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            old_db = os.path.join(temp_dir, "old_db")
            new_db = os.path.join(temp_dir, "new_db")
            out_dir = os.path.join(temp_dir, "report")
            os.makedirs(os.path.join(old_db, "uniques"))
            os.makedirs(os.path.join(new_db, "uniques"))
            os.makedirs(os.path.join(out_dir, "nested"))

            with open(os.path.join(out_dir, "SUMMARY.md"), "w", encoding="utf-8") as f:
                f.write("stale markdown")
            with open(os.path.join(out_dir, "nested", "old.md"), "w", encoding="utf-8") as f:
                f.write("stale markdown")

            old_item = {
                "id": "sample-helm",
                "name": "Sample Helm",
                "display_name": "Sample Helm",
                "base_item": "Cap",
                "item_type": "Helm",
                "lvl_req": "3",
                "properties": [{"resolved_text": "+5 to Life"}],
                "raw_row": {},
            }
            new_item = dict(old_item)
            new_item["lvl_req"] = "12"
            new_item["properties"] = [{"resolved_text": "+15 to Life"}]

            with open(os.path.join(old_db, "uniques", "helms.json"), "w", encoding="utf-8") as f:
                json.dump([old_item], f)
            with open(os.path.join(new_db, "uniques", "helms.json"), "w", encoding="utf-8") as f:
                json.dump([new_item], f)

            run_cli(
                compare_item_db.main,
                ["--new-db", new_db, "--old-db", old_db, "--out", out_dir],
            )

            self.assertTrue(os.path.exists(os.path.join(out_dir, "diff.json")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "index.html")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "ADDED.html")))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "MODIFIED.html")))
            self.assertEqual([], markdown_files_under(out_dir))


if __name__ == "__main__":
    unittest.main()
