import hashlib
import html.parser
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))

from cli import generate_wiki
from d2lib.repository import D2Repository
from d2lib.wiki.generator import WikiGenerator
from d2lib.wiki.history_comparison import write_history_comparisons
from d2lib.wiki.publication import WikiSiteRecordingWriter, empty_wiki_site


class _AssetAndTagParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang: str = ""
        self.body_attrs: Dict[str, str] = {}
        self.asset_urls: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        attr_map = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = attr_map.get("lang", "")
        elif tag == "body":
            self.body_attrs = attr_map
        elif tag == "link" and "stylesheet" in attr_map.get("rel", ""):
            if attr_map.get("href"):
                self.asset_urls.append(attr_map["href"])
        elif tag in ("script", "img") and attr_map.get("src"):
            self.asset_urls.append(attr_map["src"])


def _write_tsv(directory: str, filename: str, headers: List[str], rows: List[Dict[str, str]]) -> None:
    os.makedirs(directory, exist_ok=True)
    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(str(row.get(col, "")) for col in headers))
    Path(directory, filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_strings(strings_dir: str, entries: List[Dict[str, str]]) -> None:
    os.makedirs(strings_dir, exist_ok=True)
    Path(strings_dir, "item-names.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _seed_frozen_dataset(root: str, *, variant: str) -> None:
    """Create a self-contained frozen BK/Retail/BT dataset with enUS and koKR strings."""
    excel_dir = os.path.join(root, "data", "global", "excel")
    strings_dir = os.path.join(root, "data", "local", "lng", "strings")

    strings = [
        {"Key": "armor", "enUS": "Armor", "koKR": "갑옷"},
        {"Key": "helms", "enUS": "Helms", "koKR": "투구"},
        {"Key": "maces", "enUS": "Maces", "koKR": "철퇴"},
        {"Key": "tors_name", "enUS": "Armor", "koKR": "갑옷"},
        {"Key": "helm_name", "enUS": "Helm", "koKR": "투구"},
        {"Key": "hamm_name", "enUS": "Hammer", "koKR": "해머"},
        {"Key": "blun_name", "enUS": "Blunt", "koKR": "둔기"},
        {"Key": "mele_name", "enUS": "Melee", "koKR": "근접"},
        {"Key": "ama_cls", "enUS": "Amazon", "koKR": "아마존"},
        {"Key": "LootFilterNormalQuality", "enUS": "Normal", "koKR": "보통"},
        {"Key": "runes", "enUS": "Runes", "koKR": "룬"},
        {"Key": "gems", "enUS": "Gems", "koKR": "보석"},
        {"Key": "StrGemX1", "enUS": "Helms:", "koKR": "투구:"},
        {"Key": "StrGemX2", "enUS": "Shields:", "koKR": "방패:"},
        {"Key": "StrGemX3", "enUS": "Weapons:", "koKR": "무기:"},
        {"Key": "StrGemX4", "enUS": "Armor:", "koKR": "갑옷:"},
        {"Key": "ModStr4f", "enUS": "%+d%% Damage to Undead", "koKR": "언데드에게 주는 피해 +%d%%"},
        {"Key": "strModRedDmgPct", "enUS": "Physical Damage Received Reduced by %d%%", "koKR": "받는 물리 피해 %d%% 감소"},
        {"Key": "cap", "enUS": "Cap", "koKR": "캡"},
        {"Key": "7gm", "enUS": "Thunder Maul", "koKR": "선더 마울"},
        {"Key": "r07", "enUS": "Tal Rune", "koKR": "탈 룬"},
        {"Key": "r07L", "enUS": "Tal", "koKR": "탈"},
        {"Key": "McAuley's Folly", "enUS": "Sander's Folly", "koKR": "산더의 어리석음"},
        {"Key": "McAuley's Boots", "enUS": "Sander's Riprap", "koKR": "산더의 부츠"},
        {"Key": "Test Unique", "enUS": "Test Unique", "koKR": "테스트 고유"},
        {"Key": "Runeword4", "enUS": "Enigma", "koKR": "수수께끼"},
        {"Key": "MagicArrowName", "enUS": "Magic Arrow", "koKR": "마법 화살"},
        {"Key": "strSkillDesc", "enUS": "Fires a magic arrow", "koKR": "마법 화살 발사"},
    ]
    _write_strings(strings_dir, strings)

    _write_tsv(
        excel_dir,
        "itemtypes.txt",
        ["ItemType", "Code", "Equiv1", "StorePage", "UICategory", "MaxSockets1", "MaxSockets2", "MaxSockets3", "RunewordCategory1"],
        [
            {"ItemType": "Armor", "Code": "armo", "StorePage": "armo", "RunewordCategory1": "r_arm"},
            {"ItemType": "tors_name", "Code": "tors", "Equiv1": "armo", "StorePage": "armo", "UICategory": "helms", "RunewordCategory1": "r_arm"},
            {"ItemType": "helm_name", "Code": "helm", "Equiv1": "armo", "StorePage": "armo", "UICategory": "helms", "MaxSockets1": "2", "MaxSockets2": "2", "MaxSockets3": "2", "RunewordCategory1": "r_hel"},
            {"ItemType": "Weapon", "Code": "weap", "StorePage": "weap", "RunewordCategory1": "r_mel"},
            {"ItemType": "mele_name", "Code": "mele", "Equiv1": "weap", "StorePage": "weap", "RunewordCategory1": "r_mel"},
            {"ItemType": "blun_name", "Code": "blun", "Equiv1": "mele", "StorePage": "weap", "RunewordCategory1": "r_mel"},
            {"ItemType": "hamm_name", "Code": "hamm", "Equiv1": "blun", "StorePage": "weap", "UICategory": "maces", "MaxSockets1": "6", "MaxSockets2": "6", "MaxSockets3": "6"},
            {"ItemType": "Rune", "Code": "rune"},
        ],
    )
    _write_tsv(
        excel_dir,
        "armor.txt",
        ["name", "namestr", "code", "normcode", "type", "level", "levelreq", "reqstr", "minac", "maxac", "gemsockets", "speed"],
        [
            {"name": "Cap", "namestr": "cap", "code": "cap", "normcode": "cap", "type": "helm", "level": "1", "levelreq": "1", "minac": "3", "maxac": "5", "gemsockets": "2", "speed": "0"},
        ],
    )
    _write_tsv(
        excel_dir,
        "weapons.txt",
        ["name", "namestr", "code", "normcode", "type", "level", "levelreq", "reqstr", "mindam", "maxdam", "2handmindam", "2handmaxdam", "2handed", "gemsockets", "speed"],
        [
            {"name": "Thunder Maul", "namestr": "7gm", "code": "7gm", "normcode": "7gm", "type": "hamm", "level": "85", "levelreq": "65", "reqstr": "253", "2handmindam": "65" if variant == "bk" else "33", "2handmaxdam": "255" if variant == "bk" else "180", "2handed": "1", "gemsockets": "6", "speed": "20"},
        ],
    )
    _write_tsv(
        excel_dir,
        "misc.txt",
        ["name", "namestr", "code", "type", "level", "levelreq", "cost"],
        [
            {"name": "Tal Rune", "namestr": "r07", "code": "r07", "type": "rune", "level": "17", "levelreq": "17", "cost": "100"},
        ],
    )
    _write_tsv(
        excel_dir,
        "gems.txt",
        ["name", "code", "weaponMod1Code", "weaponMod1Min", "weaponMod1Max", "helmMod1Code", "helmMod1Min", "helmMod1Max", "shieldMod1Code", "shieldMod1Min", "shieldMod1Max"],
        [
            {"name": "Tal", "code": "r07", "weaponMod1Code": "str", "weaponMod1Min": "1", "weaponMod1Max": "1", "helmMod1Code": "str", "helmMod1Min": "1", "helmMod1Max": "1", "shieldMod1Code": "str", "shieldMod1Min": "1", "shieldMod1Max": "1"},
        ],
    )
    _write_tsv(
        excel_dir,
        "charstats.txt",
        ["class", "StrClassOnly", "StrAllSkills", "StrSkillTab1", "StrSkillTab2", "StrSkillTab3"],
        [{"class": "Amazon", "StrClassOnly": "ama_cls"}],
    )
    _write_tsv(
        excel_dir,
        "properties.txt",
        ["code", "func1", "stat1", "*Tooltip"],
        [
            {"code": "str", "func1": "1", "stat1": "strength", "*Tooltip": "+# to Strength"},
            {"code": "red-dmg%", "func1": "1", "stat1": "damageresist", "*Tooltip": "+#% DR"},
            {"code": "dmg-undead", "func1": "1", "stat1": "item_undeaddamage_percent", "*Tooltip": "+#% Damage to Undead"},
        ],
    )
    _write_tsv(
        excel_dir,
        "itemstatcost.txt",
        ["Stat", "descstrpos"],
        [
            {"Stat": "strength", "descstrpos": "strModRedDmgPct"},
            {"Stat": "damageresist", "descstrpos": "strModRedDmgPct"},
        ],
    )
    _write_tsv(
        excel_dir,
        "skilldesc.txt",
        ["skilldesc", "str name", "str short"],
        [{"skilldesc": "magic_arrow", "str name": "MagicArrowName", "str short": "strSkillDesc"}],
    )
    _write_tsv(
        excel_dir,
        "skills.txt",
        ["skill", "*Id", "charclass", "skilldesc"],
        [{"skill": "Magic Arrow", "*Id": "6", "charclass": "ama", "skilldesc": "magic_arrow"}],
    )
    _write_tsv(excel_dir, "sets.txt", ["index", "name", "version"], [{"index": "McAuley's Folly", "name": "McAuley's Folly", "version": "0"}])

    set_str_val = {"bk": "15", "bt": "10", "rt": "5"}[variant]
    _write_tsv(
        excel_dir,
        "setitems.txt",
        ["index", "set", "item", "lvl req", "prop1", "min1", "max1"],
        [{"index": "McAuley's Boots", "set": "McAuley's Folly", "item": "cap", "lvl req": "20", "prop1": "str", "min1": set_str_val, "max1": set_str_val}],
    )
    dr_val = {"bk": "20", "bt": "15", "rt": "10"}[variant]
    _write_tsv(
        excel_dir,
        "uniqueitems.txt",
        ["index", "code", "lvl", "lvl req", "prop1", "min1", "max1"],
        [{"index": "Test Unique", "code": "7gm", "lvl": "85", "lvl req": "65", "prop1": "red-dmg%", "min1": dr_val, "max1": dr_val}],
    )
    rw_str_val = {"bk": "25", "bt": "20", "rt": "15"}[variant]
    _write_tsv(
        excel_dir,
        "runes.txt",
        ["Name", "*Rune Name", "complete", "itype1", "Rune1", "T1Code1", "T1Min1", "T1Max1"],
        [{"Name": "Runeword4", "*Rune Name": "Enigma", "complete": "1", "itype1": "helm", "Rune1": "r07", "T1Code1": "str", "T1Min1": rw_str_val, "T1Max1": rw_str_val}],
    )
    for extra in (
        "automagic", "qualityitems", "magicprefix", "magicsuffix", "levels",
        "monstats", "treasureclassex", "superuniques", "cubemain",
        "experience", "difficultylevels", "missiles", "gamble",
    ):
        _write_tsv(excel_dir, f"{extra}.txt", ["col1", "col2"], [])


def _parse_html_file(path: Path) -> _AssetAndTagParser:
    parser = _AssetAndTagParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


class TestMultiLocaleWikiBuild(unittest.TestCase):
    def test_parse_locales_deduplicates_and_preserves_primary_order(self):
        self.assertEqual(["enUS"], generate_wiki.parse_locales())
        self.assertEqual(["frFR"], generate_wiki.parse_locales("frFR", " , "))
        self.assertEqual(
            ["enUS", "koKR", "deDE"],
            generate_wiki.parse_locales("enUS", " enUS, koKR , deDE, kokr "),
        )

    def test_direct_repo_multilocale_build_without_item_db_exports(self):
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
                old_item_db_dir=None,
                game_data_dir=bk_data,
                retail_data_dir=rt_data,
                locale="koKR",
            ).build_site()

            self.assertEqual("koKR", site["locale"])
            self.assertEqual("ko", site["html_lang"])

            items_json_entry = next(
                df for df in site["data_files"] if df["relative_path"] == "data/items-index.json"
            )
            items_index = json.loads(items_json_entry["content"])
            by_family = {row["family"]: row for row in items_index}
            self.assertEqual({"unique", "set", "runeword"}, set(by_family))
            self.assertEqual("테스트 고유", by_family["unique"]["title"])
            self.assertEqual("산더의 부츠", by_family["set"]["title"])
            self.assertEqual("수수께끼", by_family["runeword"]["title"])
            self.assertEqual("modified", by_family["unique"]["status"])
            self.assertEqual("modified", by_family["set"]["status"])
            self.assertEqual("modified", by_family["runeword"]["status"])

            sets_page = next(p for p in site["pages"] if p["output_path"] == "sets/index.html")
            self.assertEqual("산더의 어리석음", sets_page["payload"]["sets"][0]["name"])

    def test_multilocale_cli_run_compare_bt_shared_assets_and_pruning(self):
        with tempfile.TemporaryDirectory() as tmp:
            bk_data = os.path.join(tmp, "bk_data")
            rt_data = os.path.join(tmp, "rt_data")
            bt_data = os.path.join(tmp, "bt_data")
            out_dir = os.path.join(tmp, "wiki")
            _seed_frozen_dataset(bk_data, variant="bk")
            _seed_frozen_dataset(rt_data, variant="rt")
            _seed_frozen_dataset(bt_data, variant="bt")

            # Seed stale artifacts including a removed deDE locale folder.
            stale_paths = [
                Path(out_dir, "stale_root.html"),
                Path(out_dir, "deDE", "dropped.html"),
                Path(out_dir, "koKR", "stale_ko.html"),
                Path(out_dir, "koKR", "compare-bt", "stale_bt.html"),
            ]
            for stale in stale_paths:
                stale.parent.mkdir(parents=True, exist_ok=True)
                stale.write_text("stale", encoding="utf-8")

            generate_wiki.run(
                item_db_dir=None,
                skill_tree_dir="",
                output_dir=out_dir,
                game_data_dir=bk_data,
                retail_data_dir=rt_data,
                bt_data_dir=bt_data,
                locales=["enUS", "koKR"],
            )

            for stale in stale_paths:
                self.assertFalse(stale.exists(), f"Expected stale path pruned: {stale}")

            # Shared assets live only at the root, never duplicated under secondary locales or compare-bt.
            self.assertTrue(Path(out_dir, "assets", "site.css").is_file())
            self.assertTrue(Path(out_dir, "assets", "site.js").is_file())
            self.assertTrue(Path(out_dir, "assets", "history.js").is_file())
            self.assertFalse(Path(out_dir, "compare-bt", "assets").exists())
            self.assertFalse(Path(out_dir, "koKR", "assets").exists())
            self.assertFalse(Path(out_dir, "koKR", "compare-bt", "assets").exists())

            # Locale metadata & asset roots per published subtree.
            en_home = _parse_html_file(Path(out_dir, "index.html"))
            ko_home = _parse_html_file(Path(out_dir, "koKR", "index.html"))
            ko_items = _parse_html_file(Path(out_dir, "koKR", "items", "index.html"))
            ko_bt_home = _parse_html_file(Path(out_dir, "koKR", "compare-bt", "index.html"))
            ko_bt_items = _parse_html_file(Path(out_dir, "koKR", "compare-bt", "items", "index.html"))

            self.assertEqual("en", en_home.html_lang)
            self.assertEqual("enUS", en_home.body_attrs.get("data-locale"))
            self.assertEqual("", en_home.body_attrs.get("data-asset-root"))

            self.assertEqual("ko", ko_home.html_lang)
            self.assertEqual("koKR", ko_home.body_attrs.get("data-locale"))
            self.assertEqual("../", ko_home.body_attrs.get("data-asset-root"))
            self.assertEqual("../../", ko_items.body_attrs.get("data-asset-root"))
            self.assertEqual("../../", ko_bt_home.body_attrs.get("data-asset-root"))
            self.assertEqual("../../../", ko_bt_items.body_attrs.get("data-asset-root"))

            # Verify every local asset reference on every generated HTML page resolves to an existing file.
            out_root = Path(out_dir)
            html_files = [p for p in out_root.rglob("*.html") if "reports" not in p.relative_to(out_root).parts]
            self.assertGreater(len(html_files), 0)
            for html_file in html_files:
                parsed = _parse_html_file(html_file)
                for raw_url in parsed.asset_urls:
                    clean_url = raw_url.split("?", 1)[0].split("#", 1)[0]
                    if not clean_url or clean_url.startswith(("http://", "https://", "data:")):
                        continue
                    resolved = (html_file.parent / clean_url).resolve()
                    self.assertTrue(
                        resolved.is_file(),
                        f"Broken asset reference '{raw_url}' in {html_file} -> {resolved}",
                    )

            # Verify isolated locale item payloads between primary enUS and secondary koKR.
            en_items_index = json.loads(Path(out_dir, "data", "items-index.json").read_text(encoding="utf-8"))
            ko_items_index = json.loads(Path(out_dir, "koKR", "data", "items-index.json").read_text(encoding="utf-8"))
            ko_bt_items_index = json.loads(
                Path(out_dir, "koKR", "compare-bt", "data", "items-index.json").read_text(encoding="utf-8")
            )
            self.assertIn("Test Unique", {entry["title"] for entry in en_items_index})
            self.assertIn("테스트 고유", {entry["title"] for entry in ko_items_index})
            self.assertIn("테스트 고유", {entry["title"] for entry in ko_bt_items_index})
            self.assertIn("수수께끼", {entry["title"] for entry in ko_bt_items_index})

    def test_history_comparison_locale_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp, "cache")
            cache_dir.mkdir(parents=True, exist_ok=True)
            bk_data = os.path.join(tmp, "bk_data")
            _seed_frozen_dataset(bk_data, variant="bk")

            tables_tsv = {
                "weapons": Path(bk_data, "data", "global", "excel", "weapons.txt").read_bytes(),
                "armor": Path(bk_data, "data", "global", "excel", "armor.txt").read_bytes(),
                "misc": Path(bk_data, "data", "global", "excel", "misc.txt").read_bytes(),
                "uniqueitems": Path(bk_data, "data", "global", "excel", "uniqueitems.txt").read_bytes(),
                "setitems": Path(bk_data, "data", "global", "excel", "setitems.txt").read_bytes(),
                "sets": Path(bk_data, "data", "global", "excel", "sets.txt").read_bytes(),
                "runes": Path(bk_data, "data", "global", "excel", "runes.txt").read_bytes(),
                "itemtypes": Path(bk_data, "data", "global", "excel", "itemtypes.txt").read_bytes(),
                "gems": Path(bk_data, "data", "global", "excel", "gems.txt").read_bytes(),
                "properties": Path(bk_data, "data", "global", "excel", "properties.txt").read_bytes(),
                "itemstatcost": Path(bk_data, "data", "global", "excel", "itemstatcost.txt").read_bytes(),
                "skilldesc": Path(bk_data, "data", "global", "excel", "skilldesc.txt").read_bytes(),
                "skills": Path(bk_data, "data", "global", "excel", "skills.txt").read_bytes(),
            }
            blob_map = {name: hashlib.sha1(content).hexdigest() for name, content in tables_tsv.items()}
            blob_bytes = {blob: tables_tsv[name] for name, blob in blob_map.items()}
            sha = "abc1234"

            class _StubCollector:
                def __init__(self) -> None:
                    self.config = {"excel_path": "data/global/excel"}
                    self.excel_path = "data/global/excel"

                @staticmethod
                def canonical(identity: str) -> str:
                    return identity

                def git(self, *args: Any, binary: bool = False):
                    cmd = args[0]
                    if cmd == "rev-list":
                        return f"{sha}\n"
                    if cmd == "ls-tree":
                        return "\n".join(
                            f"100644 blob {blob}\tdata/global/excel/{name}.txt"
                            for name, blob in blob_map.items()
                        )
                    if cmd == "cat-file" and args[1] == "blob":
                        return blob_bytes[args[2]] if binary else blob_bytes[args[2]].decode("utf-8")
                    return b"" if binary else ""

                def cached(self, filename: str, builder):
                    target = cache_dir / filename
                    if target.exists():
                        return json.loads(target.read_text(encoding="utf-8"))
                    value = builder()
                    target.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
                    return value

            collector = _StubCollector()
            artifact = {
                "source_revision": sha,
                "items": {
                    "unique:Test Unique": {
                        "id": "unique:Test Unique",
                        "coverage": "full",
                        "events": [
                            {
                                "commit": sha,
                                "short_commit": sha[:7],
                                "date": "2026-01-01",
                                "timestamp": "2026-01-01T00:00:00Z",
                                "url": "",
                                "release": "",
                                "kind": "added",
                            }
                        ],
                        "gaps": [],
                    }
                },
            }

            outputs: Dict[str, Dict[str, Any]] = {}
            for locale in ("enUS", "koKR"):
                repo = D2Repository(bk_data, locale=locale)
                site = empty_wiki_site("Retail", "BKDiablo", locale=locale)
                writer = WikiSiteRecordingWriter(site)
                items = {
                    "unique": [
                        {
                            "id": "Test Unique",
                            "display_name": "Test Unique" if locale == "enUS" else "테스트 고유",
                            "raw_row": {"index": "Test Unique", "code": "7gm"},
                            "history": dict(artifact["items"]["unique:Test Unique"]),
                        }
                    ],
                    "set": [],
                    "runeword": [],
                }
                write_history_comparisons(
                    collector, artifact, repo, items,
                    {"unique": {}, "set": {}, "runeword": {}},
                    [], {}, [], {}, writer, "Retail", repo,
                )
                rev_path = items["unique"][0]["history"]["revisions_path"]
                rev_file = next(df for df in site["data_files"] if df["relative_path"] == rev_path)
                outputs[locale] = {"path": rev_path, "content": rev_file["content"]}

            self.assertTrue(outputs["enUS"]["path"].startswith("data/item-revisions/enus/"))
            self.assertTrue(outputs["koKR"]["path"].startswith("data/item-revisions/kokr/"))
            self.assertIn("테스트 고유", outputs["koKR"]["content"])
            self.assertIn("받는 물리 피해 20% 감소", outputs["koKR"]["content"])

            cache_files = sorted(p.name for p in cache_dir.glob("presentation-*.json"))
            self.assertEqual(2, len(cache_files), f"Expected separate locale presentation caches, got {cache_files}")
            self.assertTrue(any(name.startswith("presentation-enus-") for name in cache_files))
            self.assertTrue(any(name.startswith("presentation-kokr-") for name in cache_files))


if __name__ == "__main__":
    unittest.main()
