import os
import sys
import tempfile
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.exporters import HtmlReportExporter


class TestHtmlReportExporter(unittest.TestCase):
    def test_exports_item_diff_pages(self):
        diff = {
            "added": {
                "new-sword": {
                    "display_name": "New Sword",
                    "base_item": "Sword",
                    "item_type": "Sword",
                    "lvl_req": "12",
                    "properties": [{"resolved_text": "+10 to Strength"}],
                    "raw_row": {},
                }
            },
            "removed": {},
            "modified": {
                "old-helm": {
                    "name": "Old Helm",
                    "bt_base": "Cap",
                    "bk_base": "War Hat",
                    "bt_lvl": "3",
                    "bk_lvl": "12",
                    "bt_props": ["+5 to Life"],
                    "bk_props": ["+15 to Life"],
                    "item_type": "Helm",
                    "raw_row": {},
                }
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            HtmlReportExporter().export_item_diff(
                diff,
                temp_dir,
                type_counts={"uniques": {"added": 1, "removed": 0, "modified": 1}},
            )

            index_path = os.path.join(temp_dir, "index.html")
            added_path = os.path.join(temp_dir, "added", "uniques", "sword.html")
            modified_path = os.path.join(temp_dir, "modified", "uniques", "helm.html")

            self.assertTrue(os.path.exists(index_path))
            self.assertTrue(os.path.exists(added_path))
            self.assertTrue(os.path.exists(modified_path))

            with open(modified_path, "r", encoding="utf-8") as f:
                modified_html = f.read()
            self.assertIn("Old Helm", modified_html)
            self.assertIn("diff-old", modified_html)
            self.assertIn("diff-new", modified_html)

    def test_exports_excel_diff_pages(self):
        diff = {
            "filename": "gems.txt",
            "key_used": "name",
            "added_cols": ["newCol"],
            "removed_cols": [],
            "added_rows": ["new rune"],
            "removed_rows": [],
            "modified_rows": {
                "ber rune": {
                    "weaponMod1Code": {"bt_old": "crush", "bk_new": "addxp"},
                }
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = HtmlReportExporter()
            report_path = os.path.join(temp_dir, "gems.html")
            exporter.export_excel_diff(diff, report_path)
            exporter.export_excel_summary(
                [
                    {
                        "filename": "gems.txt",
                        "report_name": "gems.html",
                        "added_cols": 1,
                        "removed_cols": 0,
                        "added_rows": 1,
                        "removed_rows": 0,
                        "modified_rows": 1,
                    }
                ],
                os.path.join(temp_dir, "index.html"),
            )

            with open(report_path, "r", encoding="utf-8") as f:
                report_html = f.read()
            self.assertIn("Differences for gems.txt", report_html)
            self.assertIn("diff-old", report_html)
            self.assertIn("diff-new", report_html)

            with open(os.path.join(temp_dir, "index.html"), "r", encoding="utf-8") as f:
                index_html = f.read()
            self.assertIn('href="gems.html"', index_html)


if __name__ == "__main__":
    unittest.main()
