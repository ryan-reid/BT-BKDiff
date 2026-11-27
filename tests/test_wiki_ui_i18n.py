import html.parser
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))
sys.path.insert(0, os.path.dirname(__file__))

from cli import generate_wiki
from d2lib.repository import D2Repository
from d2lib.wiki.generator import WikiGenerator
from d2lib.wiki.i18n import WikiTranslator, locale_display_name
from d2lib.wiki.publication import WikiSiteRecordingWriter, empty_wiki_site
from d2lib.wiki.renderers import HtmlWikiRenderer, WikiRenderer
from test_multilocale_wiki_build import _seed_frozen_dataset


class _LinkAndI18nParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.locale_links: List[Dict[str, str]] = []
        self.comparison_links: List[Dict[str, str]] = []
        self.html_lang: str = ""
        self.i18n_json: str = ""
        self._in_i18n = False

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        attr_map = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = attr_map.get("lang", "")
        elif tag == "a" and "data-locale-link" in attr_map:
            self.locale_links.append({
                "href": attr_map.get("href", ""),
                "lang": attr_map.get("lang", ""),
                "active": str("is-active" in attr_map.get("class", "")),
            })
        elif tag == "a" and "data-comparison-link" in attr_map:
            self.comparison_links.append({
                "href": attr_map.get("href", ""),
                "active": str("is-active" in attr_map.get("class", "")),
            })
        elif tag == "script" and attr_map.get("id") == "wiki-i18n":
            self._in_i18n = True

    def handle_data(self, data: str) -> None:
        if self._in_i18n:
            self.i18n_json += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_i18n:
            self._in_i18n = False


class _StubD2Repo:
    def __init__(self, strings: Dict[str, str]) -> None:
        self.strings = {k.lower(): v for k, v in strings.items()}

    def get_string(self, key: str) -> str:
        return self.strings.get(key.lower(), key)


class TestWikiUII18n(unittest.TestCase):
    def test_translator_reuses_d2_keys_and_falls_back_cleanly(self):
        repo = _StubD2Repo({
            "ItemStats1e": "Benötigte Stärke: %d",
            "ItemStats1h": "Verteidigung： %d",
            "ItemStats1p": "Benötigte Stufe: %d",
            "Runewords": "Runenworte",
        })
        de_tr = WikiTranslator("deDE", repo=repo)
        self.assertEqual("Benötigte Stärke", de_tr.t("stat.str_req"))
        self.assertEqual("Verteidigung", de_tr.t("stat.defense"))
        self.assertEqual("Benötigte Stufe", de_tr.stat_label({"key": "level_req", "label": "Level Requirement"}))
        self.assertEqual("Runenworte", de_tr.t("nav.runewords"))

        # Compact enUS defaults are preserved even when repo provides ItemStats keys
        en_repo = _StubD2Repo({"ItemStats1h": "Defense: %d", "ItemStats1e": "Required Strength: %d"})
        en_tr = WikiTranslator("enUS", repo=en_repo)
        self.assertEqual("Def", en_tr.stat_label({"key": "defense", "label": "Def"}))
        self.assertEqual("Level Requirement", en_tr.stat_label({"key": "level_req", "label": "Level Requirement"}))

        # Unknown locale falls back gracefully to enUS catalog + missing key stays safe
        fr_tr = WikiTranslator("frFR", repo=_StubD2Repo({}))
        self.assertEqual("Runewords", fr_tr.t("nav.runewords"))
        self.assertEqual("CustomMod Only", fr_tr.t("status.mod_only", new_label="CustomMod"))
        self.assertEqual("missing.ui.key", fr_tr.t("missing.ui.key"))
        self.assertEqual("한국어", locale_display_name("koKR"))

    def test_custom_new_label_eliminates_hardcoded_bk_strings(self):
        renderer = WikiRenderer()
        history_macro = renderer.environment.get_template("history.html").make_module({"new_label": "AscendedMod"}).item_history
        history_html = history_macro({"coverage": "unavailable"})
        self.assertIn("AscendedMod history", history_html)
        self.assertNotIn("BK history", history_html)

        revision_html = renderer.render(
            "history_revision.html",
            comparison={"stat_rows": [], "property_rows": []},
            is_first=False,
            prev_date="2026-01-01",
            this_date="2026-02-01",
            reason="Missing snapshot.",
            new_label="AscendedMod",
            old_label="Retail",
        )
        self.assertIn("AscendedMod At · 2026-02-01", revision_html)
        self.assertIn("No current AscendedMod stats have been substituted.", revision_html)
        self.assertNotIn("BK At", revision_html)
        self.assertNotIn("current BK stats", revision_html)

        with tempfile.TemporaryDirectory() as tmp:
            bk_data = os.path.join(tmp, "bk_data")
            rt_data = os.path.join(tmp, "rt_data")
            out_dir = os.path.join(tmp, "out")
            _seed_frozen_dataset(bk_data, variant="bk")
            _seed_frozen_dataset(rt_data, variant="rt")

            site = WikiGenerator(
                item_db_dir=None,
                skill_tree_dir="",
                output_dir=out_dir,
                old_label="Retail",
                new_label="AscendedMod",
                game_data_dir=bk_data,
                retail_data_dir=rt_data,
                locale="enUS",
            ).build_site()

            html_renderer = HtmlWikiRenderer()
            base_rendered = html_renderer.render_page(
                next(p for p in site["pages"] if p["output_path"] == "index.html"),
                site,
            )
            self.assertIn("Explore AscendedMod source revisions over time.", base_rendered)
            self.assertNotIn("Explore BK source revisions", base_rendered)

            affixes_page = next((p for p in site["pages"] if p["output_path"] == "references/affixes/index.html"), None)
            if affixes_page is not None:
                affixes_rendered = html_renderer.render_page(affixes_page, site)
                self.assertNotIn("rares in BKDiablo", affixes_rendered)

    def test_translated_chrome_and_js_catalog_in_kokr_and_dede(self):
        with tempfile.TemporaryDirectory() as tmp:
            bk_data = os.path.join(tmp, "bk_data")
            rt_data = os.path.join(tmp, "rt_data")
            out_dir = os.path.join(tmp, "out")
            _seed_frozen_dataset(bk_data, variant="bk")
            _seed_frozen_dataset(rt_data, variant="rt")

            html_renderer = HtmlWikiRenderer()
            for locale, expected_nav, expected_runeword_heading, expected_stat in (
                ("koKR", "사냥터", "룬어", "요구 레벨"),
                ("deDE", "Gebiete", "Runenworte", "Benötigte Stufe"),
            ):
                site = WikiGenerator(
                    item_db_dir=None,
                    skill_tree_dir="",
                    output_dir=out_dir,
                    new_label="AscendedMod",
                    game_data_dir=bk_data,
                    retail_data_dir=rt_data,
                    locale=locale,
                ).build_site()

                items_dto = next(p for p in site["pages"] if p["output_path"] == "items/index.html")
                items_html = html_renderer.render_page(items_dto, site)
                self.assertIn(expected_nav, items_html)
                self.assertIn(expected_runeword_heading, items_html)
                self.assertIn(f"<strong>{expected_stat}:</strong>", items_html)
                self.assertIn('<option value="all">', items_html)

                parsed = _LinkAndI18nParser()
                parsed.feed(items_html)
                i18n_payload = json.loads(parsed.i18n_json)
                self.assertEqual(
                    WikiTranslator(locale).t("status.mod_only", new_label="AscendedMod"),
                    i18n_payload["status.mod_only"],
                )
                self.assertIn("areas.sparkly_chest", i18n_payload)
                self.assertIn("history.dialog_title", i18n_payload)

    def test_multilocale_language_switcher_links_and_single_locale_omission(self):
        with tempfile.TemporaryDirectory() as tmp:
            bk_data = os.path.join(tmp, "bk_data")
            rt_data = os.path.join(tmp, "rt_data")
            bt_data = os.path.join(tmp, "bt_data")
            _seed_frozen_dataset(bk_data, variant="bk")
            _seed_frozen_dataset(rt_data, variant="rt")
            _seed_frozen_dataset(bt_data, variant="bt")

            # Add magicprefix row so references/affixes/index.html renders too.
            for root in (bk_data, rt_data, bt_data):
                Path(root, "data", "global", "excel", "magicprefix.txt").write_text(
                    "Name\tspawnable\tlevel\titype1\tfrequency\trare\tmod1code\tmod1min\tmod1max\n"
                    "Sturdy\t1\t5\thelm\t1\t1\tstr\t1\t3\n",
                    encoding="utf-8",
                )

            # Single-locale build omits language switcher completely.
            single_out = Path(tmp, "single_wiki")
            generate_wiki.run(
                item_db_dir=None,
                skill_tree_dir="",
                output_dir=str(single_out),
                game_data_dir=bk_data,
                retail_data_dir=rt_data,
                locales=["enUS"],
            )
            single_home = _LinkAndI18nParser()
            single_home.feed((single_out / "index.html").read_text(encoding="utf-8"))
            self.assertEqual([], single_home.locale_links)

            # Multi-locale --compare-bt build renders resolving language links everywhere.
            multi_out = Path(tmp, "multi_wiki")
            generate_wiki.run(
                item_db_dir=None,
                skill_tree_dir="",
                output_dir=str(multi_out),
                game_data_dir=bk_data,
                retail_data_dir=rt_data,
                bt_data_dir=bt_data,
                locales=["enUS", "deDE", "koKR"],
            )

            html_files = [
                p for p in multi_out.rglob("*.html")
                if "reports" not in p.relative_to(multi_out).parts
            ]
            self.assertGreater(len(html_files), 0)
            for html_file in html_files:
                parsed = _LinkAndI18nParser()
                parsed.feed(html_file.read_text(encoding="utf-8"))
                self.assertEqual(3, len(parsed.locale_links), f"Missing switcher in {html_file}")
                rel_parts = html_file.relative_to(multi_out).parts
                in_bt = "compare-bt" in rel_parts
                for entry in parsed.locale_links:
                    target = (html_file.parent / entry["href"]).resolve()
                    self.assertTrue(
                        target.is_file(),
                        f"Broken locale switcher target {entry['href']} from {html_file} -> {target}",
                    )
                    target_parts = target.relative_to(multi_out).parts
                    self.assertEqual(in_bt, "compare-bt" in target_parts, f"Baseline mismatch for {html_file} -> {target}")

            # Verify affix functions page retains switcher even when comparison_bar block is cleared.
            affix_ko = multi_out / "koKR" / "references" / "affixes" / "index.html"
            self.assertTrue(affix_ko.is_file())
            affix_parsed = _LinkAndI18nParser()
            affix_parsed.feed(affix_ko.read_text(encoding="utf-8"))
            self.assertEqual(3, len(affix_parsed.locale_links))
            self.assertEqual([], affix_parsed.comparison_links)

            # Missing counterpart page falls back to target locale's index.html.
            site_en = {"pages": [{"output_path": "index.html", "payload": {}}, {"output_path": "only-en/index.html", "payload": {}}]}
            site_ko = {"pages": [{"output_path": "index.html", "payload": {}}]}
            generate_wiki.add_locale_links([("enUS", True, False, site_en), ("koKR", False, False, site_ko)])
            only_en_opts = {opt["locale"]: opt["href"] for opt in site_en["pages"][1]["payload"]["locale_switch"]["options"]}
            self.assertEqual("../koKR/index.html", only_en_opts["koKR"])


if __name__ == "__main__":
    unittest.main()
