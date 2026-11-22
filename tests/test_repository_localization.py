import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.repository import D2Repository, locale_to_html_lang, resolve_difficulty_name
from d2lib.utils import normalize_d2_text, strip_d2_formatting
from d2lib.wiki.publication import empty_wiki_site
from d2lib.wiki.renderers import HtmlWikiRenderer, highlight_comparison


def _write_strings(root: Path, filename: str, entries: list) -> None:
    string_dir = root / "data" / "local" / "lng" / "strings"
    string_dir.mkdir(parents=True, exist_ok=True)
    (string_dir / filename).write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")


class TestD2RepositoryLocalization(unittest.TestCase):
    def _build_isolated_repo(self, temp_dir: str, mod_entries: list, retail_entries: list, base_entries: list | None = None, locale: str = "enUS") -> D2Repository:
        root = Path(temp_dir)
        mod_dir = root / "mod"
        fake_repo_root = root / "repo_root"
        retail_dir = fake_repo_root / "data" / "retail"
        _write_strings(mod_dir, "item-names.json", mod_entries)

        retail_strings = retail_dir / "local" / "lng" / "strings"
        retail_strings.mkdir(parents=True, exist_ok=True)
        (retail_strings / "item-names.json").write_text(json.dumps(retail_entries, ensure_ascii=False), encoding="utf-8")

        if base_entries is not None:
            base_strings = fake_repo_root / "data" / "base" / "strings"
            base_strings.mkdir(parents=True, exist_ok=True)
            (base_strings / "skills.json").write_text(json.dumps(base_entries, ensure_ascii=False), encoding="utf-8")

        repo = D2Repository.__new__(D2Repository)
        repo.mpq_path = str(mod_dir)
        repo.locale = locale
        repo.repo_root = str(fake_repo_root)
        repo.supplemental_path = str(retail_dir)
        repo.strings = {}
        repo.excel_cache = {}
        repo.excel_sources = {}
        repo._load_strings()
        return repo

    def test_strip_d2_formatting_handles_color_and_grammar_tags(self):
        self.assertEqual(strip_d2_formatting("ÿc8[fs]Jah-Rune ÿc9(ÿc;31ÿc9)"), "Jah-Rune (31)")
        self.assertEqual(strip_d2_formatting("ÿc;•••ÿc8[fs]Jah-Runeÿc;•••"), "•••Jah-Rune•••")
        self.assertEqual(strip_d2_formatting("[pl]Helme"), "Helme")
        # Multi-form inflections must select one form, not concatenate all forms together
        self.assertEqual(
            strip_d2_formatting("[ms]maudit[fs]maudite[mp]maudits[fp]maudites"),
            "maudit",
        )
        self.assertEqual(
            strip_d2_formatting("[ms]отверженный[fs]отверженная[ns]отверженное[pl]отверженные"),
            "отверженный",
        )
        self.assertEqual(
            strip_d2_formatting("[ms]Arcydiabelski[fs]Arcydiabelska[ns]Arcydiabelskie[p]Arcydiabelskie"),
            "Arcydiabelski",
        )
        self.assertEqual(
            strip_d2_formatting("Line 1 [ms]foo[fs]fooe\n[pl]Bar [1-5]"),
            "Line 1 foo\nBar [1-5]",
        )
        self.assertEqual(normalize_d2_text("ÿc3[ms]Heavy  Boots"), "Heavy Boots")

    def test_multi_locale_loading_per_key_fallback_and_strict_precedence(self):
        mod_entries = [
            {"Key": "ModRenamed", "enUS": "Poison Strike"},
            {"Key": "FullItem", "enUS": "Eagle Horn", "deDE": "[fs]Adlerhorn", "koKR": "독수리 뿔"},
            {"Key": "BlankTarget", "enUS": "Fallback Sword", "deDE": "   ", "koKR": ""},
        ]
        retail_entries = [
            # Stale Retail translation must NEVER override Mod-updated key
            {"Key": "ModRenamed", "enUS": "Poison Dagger", "deDE": "Giftdolch", "koKR": "포이즌 대거"},
            {"Key": "RetailOnly", "enUS": "Quilted Armor", "deDE": "[fs]Stepp-Rüstung", "koKR": "누비 갑옷"},
            {"Key": "EnglishOnlyRetail", "enUS": "Cap"},
        ]
        base_entries = [
            {"Key": "LegacyBaseShadow", "enUS": "Should Not Load", "deDE": "Altlast"},
            {"Key": "RetailOnly", "enUS": "Shadowed Armor", "deDE": "Altlast Rüstung"},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_en = self._build_isolated_repo(temp_dir, mod_entries, retail_entries, base_entries, locale="enUS")
            repo_de = self._build_isolated_repo(temp_dir, mod_entries, retail_entries, base_entries, locale="deDE")
            repo_ko = self._build_isolated_repo(temp_dir, mod_entries, retail_entries, base_entries, locale="koKR")

            self.assertEqual(repo_en.get_string("FullItem"), "Eagle Horn")
            self.assertEqual(repo_de.get_string("FullItem"), "Adlerhorn")
            self.assertEqual(repo_ko.get_string("FullItem"), "독수리 뿔")

            # Missing or blank target locale on a Mod key falls back to Mod enUS, NOT Retail target locale
            self.assertEqual(repo_de.get_string("ModRenamed"), "Poison Strike")
            self.assertEqual(repo_ko.get_string("ModRenamed"), "Poison Strike")
            self.assertEqual(repo_de.get_string("BlankTarget"), "Fallback Sword")

            # Retail supplemental fallback works when key is absent in Mod strings
            self.assertEqual(repo_de.get_string("RetailOnly"), "Stepp-Rüstung")
            self.assertEqual(repo_ko.get_string("RetailOnly"), "누비 갑옷")
            self.assertEqual(repo_ko.get_string("EnglishOnlyRetail"), "Cap")

            # Stale data/base/strings directory must not be loaded
            self.assertEqual(repo_de.get_string("LegacyBaseShadow"), "LegacyBaseShadow")

    def test_difficulty_resolution_uses_strcreategame_keys_with_fallback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self._build_isolated_repo(
                temp_dir,
                mod_entries=[
                    {"Key": "strCreateGameNormalText", "enUS": "Pain", "deDE": "Schmerz"},
                    {"Key": "strCreateGameNightmareText", "enUS": "Agony", "deDE": "Qual"},
                    {"Key": "strCreateGameHellText", "enUS": "Insanity", "deDE": "Wahnsinn"},
                ],
                retail_entries=[],
                locale="deDE",
            )
            self.assertEqual(resolve_difficulty_name(repo, "1"), "Schmerz")
            self.assertEqual(resolve_difficulty_name(repo, "Normal"), "Schmerz")
            self.assertEqual(resolve_difficulty_name(repo, "2"), "Qual")
            self.assertEqual(resolve_difficulty_name(repo, "3"), "Wahnsinn")

            empty_repo = self._build_isolated_repo(temp_dir, [], [], locale="enUS")
            self.assertEqual(resolve_difficulty_name(empty_repo, "1"), "Normal")
            self.assertEqual(resolve_difficulty_name(empty_repo, "nightmare"), "Nightmare")
            self.assertEqual(resolve_difficulty_name(empty_repo, "Hell"), "Hell")

    def test_locale_to_html_lang_and_rendered_html_lang_attribute(self):
        self.assertEqual(locale_to_html_lang("enUS"), "en")
        self.assertEqual(locale_to_html_lang("deDE"), "de")
        self.assertEqual(locale_to_html_lang("koKR"), "ko")
        self.assertEqual(locale_to_html_lang("zhCN"), "zh-Hans")
        self.assertEqual(locale_to_html_lang("zhTW"), "zh-Hant")
        self.assertEqual(locale_to_html_lang("ptBR"), "pt-BR")

        site = empty_wiki_site("Retail", "BKDiablo", locale="koKR")
        page = {
            "kind": "mechanics",
            "title": "Mechanics | BKDiablo Wiki",
            "output_path": "mechanics/index.html",
            "template_name": "mechanics.html",
            "category": "index",
            "source_files": [],
            "payload": {"summary": {"difficulty_changes": [], "experience_changes": []}},
        }
        rendered = HtmlWikiRenderer().render_page(page, site)
        self.assertIn('<html lang="ko">', rendered)
        self.assertIn('data-locale="koKR"', rendered)

    def test_unicode_diff_highlighting_keeps_whole_words(self):
        hangul_old = str(highlight_comparison("화염 피해 10", "화염 피해 25", "old"))
        self.assertIn('<mark class="diff-token diff-token-old">10</mark>', hangul_old)
        self.assertNotIn("<mark", hangul_old.split("피해")[0])

        umlaut_new = str(highlight_comparison("Größter Schutz", "Größter Schaden", "new"))
        self.assertEqual(
            umlaut_new,
            'Größter <mark class="diff-token diff-token-new">Schutz</mark>',
        )

        cyrillic_new = str(highlight_comparison("Ледяной шар 5", "Огненный шар 5", "new"))
        self.assertEqual(
            cyrillic_new,
            '<mark class="diff-token diff-token-new">Ледяной</mark> шар 5',
        )


if __name__ == "__main__":
    unittest.main()
