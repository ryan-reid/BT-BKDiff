import html.parser
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))

from d2lib.services.comparison import ItemComparisonService
from d2lib.services.items import ItemAnalyzerService
from d2lib.services.resolver import PropertyResolverService
from d2lib.utils import normalize_d2_text
from d2lib.wiki.comparison import (
    base_item_comparison_context,
    entries_match,
    gem_rune_comparison_context,
    item_comparison_context,
)
from d2lib.wiki.generator import WikiContentBuilder, WikiGenerator
from d2lib.wiki.item_helpers import item_slug, set_item_anchor, should_include_item
from d2lib.wiki.mediawiki import MediaWikiRenderer


class _HtmlMetadataParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hash_hrefs: list[str] = []
        self.selects: dict[str, list[dict[str, str]]] = {}
        self.optgroups: list[dict[str, str]] = []
        self.data_attrs: list[dict[str, str]] = []
        self._current_select: str | None = None
        self._current_option: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: (v or "") for k, v in attrs}
        if "id" in attr_map and attr_map["id"]:
            self.ids.append(attr_map["id"])
        if tag == "a" and attr_map.get("href", "").startswith("#"):
            self.hash_hrefs.append(attr_map["href"][1:])
        if tag == "select" and attr_map.get("id"):
            self._current_select = attr_map["id"]
            self.selects.setdefault(self._current_select, [])
        if tag == "optgroup":
            self.optgroups.append(
                {
                    "select": self._current_select or "",
                    "label": attr_map.get("label", ""),
                    "group_code": attr_map.get("data-group-code", ""),
                }
            )
        if tag == "option" and self._current_select:
            self._current_option = {"value": attr_map.get("value", ""), "label": ""}
        filter_data = {
            k: v
            for k, v in attr_map.items()
            if k in {
                "data-item-group",
                "data-item-type",
                "data-base-group",
                "data-base-classes",
                "data-loot-category",
                "data-type-codes",
                "data-tier",
                "data-speed",
                "data-base-items",
                "data-rune-codes",
            }
        }
        if filter_data:
            self.data_attrs.append(filter_data)

    def handle_data(self, data: str) -> None:
        if self._current_option is not None:
            self._current_option["label"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "option" and self._current_option is not None and self._current_select:
            self._current_option["label"] = self._current_option["label"].strip()
            self.selects[self._current_select].append(self._current_option)
            self._current_option = None
        if tag == "select":
            self._current_select = None


def _parse_html(path: str) -> _HtmlMetadataParser:
    parser = _HtmlMetadataParser()
    parser.feed(Path(path).read_text(encoding="utf-8"))
    return parser


def _write_tsv(directory: str, filename: str, headers: list[str], rows: list[dict[str, str]]) -> None:
    os.makedirs(directory, exist_ok=True)
    lines = ["\t".join(headers)]
    for row in rows:
        lines.append("\t".join(str(row.get(col, "")) for col in headers))
    Path(directory, filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_strings(strings_dir: str, entries: list[dict[str, str]]) -> None:
    os.makedirs(strings_dir, exist_ok=True)
    Path(strings_dir, "item-names.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )


class TestStableIdentifiersAndDiffMatching(unittest.TestCase):
    def test_normalize_d2_text_does_not_rewrite_english_phrases(self):
        self.assertEqual(
            "Physical Damage Received Reduced by 10%",
            normalize_d2_text("ÿc3Physical Damage Received Reduced by  10%"),
        )
        self.assertEqual(
            "Original Class Skill",
            normalize_d2_text("[ms]Original **Class** Skill"),
        )

    def test_item_slug_and_set_item_anchor_prefer_canonical_identifiers_across_locales(self):
        set_en = {
            "id": "McAuley's Boots",
            "display_name": "Sander's Riprap",
            "base_item": "Heavy Boots",
            "raw_row": {"index": "McAuley's Boots", "set": "McAuley's Folly", "item": "vbt"},
        }
        set_ko = {
            "id": "McAuley's Boots",
            "display_name": "산더의 부츠",
            "base_item": "헤비 부츠",
            "raw_row": {"index": "McAuley's Boots", "set": "McAuley's Folly", "item": "vbt"},
        }
        self.assertEqual("mcauleys-folly-mcauleys-boots", set_item_anchor(set_en))
        self.assertEqual(set_item_anchor(set_en), set_item_anchor(set_ko))

        slug_en = item_slug(set_en, "set", set_en["display_name"], {})
        slug_ko = item_slug(set_ko, "set", set_ko["display_name"], {})
        self.assertEqual("mcauleys-boots", slug_en)
        self.assertEqual(slug_en, slug_ko)

        rw_en = {
            "id": "Runeword4",
            "name": "Enigma",
            "base_items": ["Body Armor"],
            "raw_row": {"Name": "Runeword4", "itype1": "tors"},
        }
        rw_ko = {
            "id": "Runeword4",
            "name": "수수께끼",
            "base_items": ["갑옷"],
            "raw_row": {"Name": "Runeword4", "itype1": "tors"},
        }
        self.assertEqual("runeword4", item_slug(rw_en, "runeword", rw_en["name"], {}))
        self.assertEqual(
            item_slug(rw_en, "runeword", rw_en["name"], {}),
            item_slug(rw_ko, "runeword", rw_ko["name"], {}),
        )

    def test_should_include_item_uses_raw_source_identifiers_even_when_localized(self):
        self.assertFalse(
            should_include_item(
                {
                    "id": "Charm Blank",
                    "display_name": "빈 부적",
                    "base_item": "작은 부적",
                    "item_type": "부적",
                    "properties": [],
                    "raw_row": {"index": "Charm Blank", "code": "mfd"},
                },
                "unique",
            )
        )
        self.assertFalse(
            should_include_item(
                {
                    "id": "Runeword56",
                    "name": "복수",
                    "base_items": ["확장팩"],
                    "runes": [],
                    "properties": [],
                    "raw_row": {"Name": "Runeword56", "itype1": "", "Rune1": "", "T1Code1": ""},
                },
                "runeword",
            )
        )
        self.assertTrue(
            should_include_item(
                {
                    "id": "Vampire Gaze",
                    "display_name": "흡혈귀의 눈길",
                    "base_item": "그림 헬름",
                    "item_type": "투구",
                    "properties": [],
                    "raw_row": {"index": "Vampire Gaze", "code": "xh9"},
                },
                "unique",
            )
        )

    def test_entries_match_and_comparison_service_ignore_display_wording_differences(self):
        old_unique = {
            "id": "Stormshield",
            "display_name": "Stormshield",
            "base_item": "Monarch",
            "item_type": "Shields",
            "lvl_req": "73",
            "raw_row": {"index": "Stormshield", "code": "uit", "lvl req": "73"},
            "properties": [
                {
                    "code": "red-dmg%",
                    "canonical_code": "red-dmg%",
                    "param": "",
                    "parameter_key": "",
                    "min_val": "35",
                    "max_val": "35",
                    "resolved_text": "Damage Reduced by 35%",
                }
            ],
        }
        new_unique_ko = {
            "id": "Stormshield",
            "display_name": "폭풍방패",
            "base_item": "모너크",
            "item_type": "방패",
            "lvl_req": "73",
            "raw_row": {"index": "Stormshield", "code": "uit", "lvl req": "73"},
            "properties": [
                {
                    "code": "red-dmg%",
                    "canonical_code": "red-dmg%",
                    "param": "",
                    "parameter_key": "",
                    "min_val": "35",
                    "max_val": "35",
                    "resolved_text": "받는 물리 피해 35% 감소",
                }
            ],
        }
        self.assertTrue(entries_match(new_unique_ko, old_unique))
        self.assertEqual("unchanged", item_comparison_context(new_unique_ko, "unique", old_unique)["state"])

        changed_unique = {
            **new_unique_ko,
            "properties": [
                {
                    "code": "red-dmg%",
                    "canonical_code": "red-dmg%",
                    "param": "",
                    "parameter_key": "",
                    "min_val": "40",
                    "max_val": "40",
                    "resolved_text": "받는 물리 피해 40% 감소",
                }
            ],
        }
        self.assertFalse(entries_match(changed_unique, old_unique))
        self.assertEqual("modified", item_comparison_context(changed_unique, "unique", old_unique)["state"])

        svc = ItemComparisonService()
        diff_same = svc.compare_item_lists({"storm": new_unique_ko}, {"storm": old_unique})
        self.assertEqual({}, diff_same["modified"])
        diff_changed = svc.compare_item_lists({"storm": changed_unique}, {"storm": old_unique})
        self.assertIn("storm", diff_changed["modified"])

    def test_stat_row_canonical_keys_drive_generator_and_mediawiki_regardless_of_labels(self):
        old_base = {
            "level": 10, "level_req": 5, "str_req": 20, "dex_req": 0, "sockets": 3,
            "defense_min": 100, "defense_max": 120, "block": 0, "speed": 0,
            "damage_min": None, "damage_max": None,
            "two_hand_damage_min": None, "two_hand_damage_max": None,
            "throw_damage_min": None, "throw_damage_max": None,
            "two_handed_only": False,
        }
        new_base = {**old_base, "defense_max": 150, "sockets": 4}
        base_ctx = base_item_comparison_context(new_base, old_base)
        keys = [r["key"] for r in base_ctx["stat_rows"]]
        self.assertEqual(["defense", "level", "level_req", "str_req", "dex_req", "max_sockets"], keys)

        builder = WikiContentBuilder.__new__(WikiContentBuilder)
        subset = builder._base_comparison_rows(new_base, old_base)
        self.assertEqual(["defense", "max_sockets"], [r["key"] for r in subset])
        self.assertEqual(["Def", "Max Sockets"], [r["label"] for r in subset])

        gem_ctx = gem_rune_comparison_context(
            {"level": 18, "level_req": 25, "cost": 500, "socket_effects": {"Weapon": ["+5 Damage"]}},
            {"level": 18, "level_req": 20, "cost": 500, "socket_effects": {"Weapon": ["+3 Damage"]}},
        )
        self.assertEqual(["level", "level_req", "cost"], [r["key"] for r in gem_ctx["stat_rows"]])
        self.assertEqual(["weapon", "helm", "shield"], [r["key"] for r in gem_ctx["property_rows"]])

        renderer = MediaWikiRenderer()
        localized_entry = {
            "title": "Enigma",
            "status": "modified",
            "properties": ["+2 to All Skills"],
            "stat_rows": [
                {"key": "runes", "label": "룬", "old": "Jah + Ith + Ber", "new": "Jah + Ith + Ber", "status": "same"},
                {"key": "base_items", "label": "기본 아이템", "old": "갑옷", "new": "갑옷, 투구", "status": "changed"},
                {"key": "required_level", "label": "요구 레벨", "old": "65", "new": "65", "status": "same"},
            ],
            "property_rows": [],
        }
        page = renderer._entry_page(localized_entry, "runeword")
        identity = renderer._identity_compare_row("Enigma", page, page["comparison"])
        self.assertIn("Base Type: 갑옷", identity["old"])
        self.assertIn("Base Type: 갑옷, 투구", identity["new"])
        self.assertEqual("changed", identity["status"])
        _, stats_new, _ = renderer._stats_compare_blocks(page, page["comparison"])
        self.assertNotIn("룬:", stats_new)
        self.assertNotIn("기본 아이템:", stats_new)
        self.assertIn("요구 레벨: 65", stats_new)

    def test_multilocale_wiki_generation_has_identical_routes_anchors_filters_and_diff_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            bk_data = os.path.join(tmp, "bk_data")
            rt_data = os.path.join(tmp, "rt_data")
            bk_excel = os.path.join(bk_data, "data", "global", "excel")
            rt_excel = os.path.join(rt_data, "data", "global", "excel")
            bk_strings_dir = os.path.join(bk_data, "data", "local", "lng", "strings")
            rt_strings_dir = os.path.join(rt_data, "data", "local", "lng", "strings")

            strings = [
                {"Key": "armor", "enUS": "Armor", "deDE": "Rüstung", "koKR": "갑옷"},
                {"Key": "StrGemX3", "enUS": "Weapons:", "deDE": "Waffen:", "koKR": "무기:"},
                {"Key": "accessories", "enUS": "Accessories", "deDE": "Accessoires", "koKR": "장신구"},
                {"Key": "helms", "enUS": "Helms", "deDE": "Helme", "koKR": "투구"},
                {"Key": "maces", "enUS": "Maces", "deDE": "Streitkolben", "koKR": "철퇴"},
                {"Key": "tors_name", "enUS": "Armor", "deDE": "Rüstung", "koKR": "갑옷"},
                {"Key": "helm_name", "enUS": "Helm", "deDE": "Helm", "koKR": "투구"},
                {"Key": "hamm_name", "enUS": "Hammer", "deDE": "Hammer", "koKR": "해머"},
                {"Key": "blun_name", "enUS": "Blunt", "deDE": "Stumpf", "koKR": "둔기"},
                {"Key": "mele_name", "enUS": "Melee", "deDE": "Nahkampf", "koKR": "근접"},
                {"Key": "dru_cls", "enUS": "Druid", "deDE": "Druide", "koKR": "드루이드"},
                {"Key": "ama_cls", "enUS": "Amazon", "deDE": "Amazone", "koKR": "아마존"},
                {"Key": "LootFilterNormalQuality", "enUS": "Normal", "deDE": "Normal", "koKR": "보통"},
                {"Key": "runes", "enUS": "Runes", "deDE": "Runen", "koKR": "룬"},
                {"Key": "gems", "enUS": "Gems", "deDE": "Edelsteine", "koKR": "보석"},
                {"Key": "uberm", "enUS": "Uber Materials", "deDE": "Über-Materialien", "koKR": "우버 재료"},
                {"Key": "StrGemX1", "enUS": "Helms:", "deDE": "Helme:", "koKR": "투구:"},
                {"Key": "StrGemX2", "enUS": "Shields:", "deDE": "Schilde:", "koKR": "방패:"},
                {"Key": "StrGemX4", "enUS": "Armor:", "deDE": "Rüstung:", "koKR": "갑옷:"},
                {"Key": "ModStr4f", "enUS": "%+d%% Damage to Undead", "deDE": "%+d%% Schaden an Untoten", "koKR": "언데드에게 주는 피해 +%d%%"},
                {"Key": "strModRedDmgPct", "enUS": "Physical Damage Received Reduced by %d%%", "deDE": "Physischer Schaden reduziert um %d%%", "koKR": "받는 물리 피해 %d%% 감소"},
                {"Key": "cap", "enUS": "Cap", "deDE": "Kappe", "koKR": "캡"},
                {"Key": "pelt", "enUS": "Wolf Head", "deDE": "Wolfskopf", "koKR": "늑대 머리"},
                {"Key": "7gm", "enUS": "Thunder Maul", "deDE": "Donnerhammer", "koKR": "선더 마울"},
                {"Key": "r07", "enUS": "Tal Rune", "deDE": "Tal-Rune", "koKR": "탈 룬"},
                {"Key": "r07L", "enUS": "Tal", "deDE": "Tal", "koKR": "탈"},
                {"Key": "gcv", "enUS": "Chipped Amethyst", "deDE": "Schlechter Amethyst", "koKR": "최하급 자수정"},
                {"Key": "pk1", "enUS": "Key of Terror", "deDE": "Schlüssel des Terrors", "koKR": "공포의 열쇠"},
                {"Key": "McAuley's Folly", "enUS": "Sander's Folly", "deDE": "Sanders Dummheit", "koKR": "산더의 어리석음"},
                {"Key": "McAuley's Boots", "enUS": "Sander's Riprap", "deDE": "Sanders Riprap", "koKR": "산더의 부츠"},
                {"Key": "Test Unique", "enUS": "Test Unique", "deDE": "Test-Unikat", "koKR": "테스트 고유"},
                {"Key": "Charm Blank", "enUS": "Blank Charm", "deDE": "Leerer Zauber", "koKR": "빈 부적"},
                {"Key": "Runeword4", "enUS": "Enigma", "deDE": "Rätsel", "koKR": "수수께끼"},
                {"Key": "Runeword56", "enUS": "Revenge", "deDE": "Rache", "koKR": "복수"},
                {"Key": "MagicArrowName", "enUS": "Magic Arrow", "deDE": "Magischer Pfeil", "koKR": "마법 화살"},
                {"Key": "strSkillDesc", "enUS": "Fires a magic arrow", "deDE": "Feuert einen magischen Pfeil", "koKR": "마법 화살 발사"},
            ]
            _write_strings(bk_strings_dir, strings)
            _write_strings(rt_strings_dir, strings)

            for excel_dir in (bk_excel, rt_excel):
                _write_tsv(
                    excel_dir,
                    "itemtypes.txt",
                    ["ItemType", "Code", "Equiv1", "Equiv2", "StorePage", "UICategory", "Class", "StaffMods", "MaxSockets1", "MaxSockets2", "MaxSockets3", "RunewordCategory1", "RunewordCategory2"],
                    [
                        {"ItemType": "Armor", "Code": "armo", "StorePage": "armo", "RunewordCategory1": "r_arm"},
                        {"ItemType": "tors_name", "Code": "tors", "Equiv1": "armo", "StorePage": "armo", "UICategory": "helms", "RunewordCategory1": "r_arm"},
                        {"ItemType": "helm_name", "Code": "helm", "Equiv1": "armo", "StorePage": "armo", "UICategory": "helms", "MaxSockets1": "2", "MaxSockets2": "2", "MaxSockets3": "2", "RunewordCategory1": "r_hel"},
                        {"ItemType": "Druid Pelt", "Code": "pelt", "Equiv1": "helm", "StorePage": "armo", "Class": "dru", "StaffMods": "dru"},
                        {"ItemType": "Weapon", "Code": "weap", "StorePage": "weap", "RunewordCategory1": "r_mis", "RunewordCategory2": "r_mel"},
                        {"ItemType": "mele_name", "Code": "mele", "Equiv1": "weap", "StorePage": "weap", "RunewordCategory1": "r_mel"},
                        {"ItemType": "blun_name", "Code": "blun", "Equiv1": "mele", "StorePage": "weap", "RunewordCategory1": "r_mel"},
                        {"ItemType": "hamm_name", "Code": "hamm", "Equiv1": "blun", "StorePage": "weap", "UICategory": "maces", "MaxSockets1": "6", "MaxSockets2": "6", "MaxSockets3": "6"},
                        {"ItemType": "Rune", "Code": "rune"},
                        {"ItemType": "Amethyst", "Code": "gema"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "armor.txt",
                    ["name", "namestr", "code", "normcode", "ubercode", "ultracode", "type", "level", "levelreq", "reqstr", "minac", "maxac", "gemsockets", "speed"],
                    [
                        {"name": "Cap", "namestr": "cap", "code": "cap", "normcode": "cap", "type": "helm", "level": "1", "levelreq": "1", "minac": "3", "maxac": "5", "gemsockets": "2", "speed": "0"},
                        {"name": "Wolf Head", "namestr": "pelt", "code": "dr1", "normcode": "dr1", "type": "pelt", "level": "5", "levelreq": "3", "minac": "8", "maxac": "11", "gemsockets": "2", "speed": "0"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "weapons.txt",
                    ["name", "namestr", "code", "normcode", "type", "level", "levelreq", "reqstr", "mindam", "maxdam", "2handmindam", "2handmaxdam", "2handed", "gemsockets", "speed"],
                    [
                        {"name": "Thunder Maul", "namestr": "7gm", "code": "7gm", "normcode": "7gm", "type": "hamm", "level": "85", "levelreq": "65", "reqstr": "253", "2handmindam": "65" if excel_dir == bk_excel else "33", "2handmaxdam": "255" if excel_dir == bk_excel else "180", "2handed": "1", "gemsockets": "6", "speed": "20"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "misc.txt",
                    ["name", "namestr", "code", "type", "level", "levelreq", "cost", "UICatOverride", "quest", "stackable", "maxstack"],
                    [
                        {"name": "Tal Rune", "namestr": "r07", "code": "r07", "type": "rune", "level": "17", "levelreq": "17", "cost": "100"},
                        {"name": "Chipped Amethyst", "namestr": "gcv", "code": "gcv", "type": "gema", "level": "1", "levelreq": "1", "cost": "50"},
                        {"name": "Key of Terror", "namestr": "pk1", "code": "pk1", "type": "ques", "level": "1", "levelreq": "0", "cost": "1", "UICatOverride": "uberm", "quest": "1", "stackable": "1", "maxstack": "10"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "gems.txt",
                    ["name", "code", "weaponMod1Code", "weaponMod1Min", "weaponMod1Max", "helmMod1Code", "helmMod1Min", "helmMod1Max", "shieldMod1Code", "shieldMod1Min", "shieldMod1Max"],
                    [
                        {"name": "Tal", "code": "r07", "weaponMod1Code": "str", "weaponMod1Min": "1", "weaponMod1Max": "1", "helmMod1Code": "str", "helmMod1Min": "1", "helmMod1Max": "1", "shieldMod1Code": "str", "shieldMod1Min": "1", "shieldMod1Max": "1"},
                        {"name": "Chipped Amethyst", "code": "gcv", "weaponMod1Code": "str", "weaponMod1Min": "3", "weaponMod1Max": "3", "helmMod1Code": "str", "helmMod1Min": "3", "helmMod1Max": "3", "shieldMod1Code": "str", "shieldMod1Min": "3", "shieldMod1Max": "3"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "charstats.txt",
                    ["class", "StrClassOnly", "StrAllSkills", "StrSkillTab1", "StrSkillTab2", "StrSkillTab3"],
                    [
                        {"class": "Amazon", "StrClassOnly": "ama_cls"},
                        {"class": "Druid", "StrClassOnly": "dru_cls"},
                    ],
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
                _write_tsv(
                    excel_dir,
                    "sets.txt",
                    ["index", "name", "version"],
                    [{"index": "McAuley's Folly", "name": "McAuley's Folly", "version": "0"}],
                )
                _write_tsv(
                    excel_dir,
                    "setitems.txt",
                    ["index", "set", "item", "lvl req", "prop1", "min1", "max1"],
                    [
                        {"index": "McAuley's Boots", "set": "McAuley's Folly", "item": "cap", "lvl req": "20", "prop1": "str", "min1": "5" if excel_dir == rt_excel else "10", "max1": "5" if excel_dir == rt_excel else "10"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "uniqueitems.txt",
                    ["index", "code", "lvl", "lvl req", "prop1", "min1", "max1"],
                    [
                        {"index": "Test Unique", "code": "7gm", "lvl": "85", "lvl req": "65", "prop1": "red-dmg%", "min1": "10", "max1": "10"},
                        {"index": "Charm Blank", "code": "mfd", "lvl": "1", "lvl req": "0"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "runes.txt",
                    ["Name", "*Rune Name", "complete", "itype1", "Rune1", "T1Code1", "T1Min1", "T1Max1"],
                    [
                        {"Name": "Runeword4", "*Rune Name": "Enigma", "complete": "1", "itype1": "helm", "Rune1": "r07", "T1Code1": "str", "T1Min1": "15", "T1Max1": "15"},
                        {"Name": "Runeword56", "*Rune Name": "Revenge", "complete": "1", "itype1": "", "Rune1": "", "T1Code1": ""},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "magicprefix.txt",
                    ["Name", "spawnable", "level", "itype1", "frequency", "rare", "mod1code", "mod1min", "mod1max"],
                    [
                        {"Name": "Sturdy", "spawnable": "1", "level": "5", "itype1": "helm", "frequency": "1", "rare": "1", "mod1code": "str", "mod1min": "1", "mod1max": "3"},
                    ],
                )
                for extra in ("automagic", "qualityitems", "magicsuffix", "levels", "monstats", "treasureclassex", "superuniques", "cubemain", "experience", "difficultylevels", "missiles", "gamble"):
                    _write_tsv(excel_dir, f"{extra}.txt", ["col1", "col2"], [])

            results = {}
            for locale in ("enUS", "deDE", "koKR"):
                from d2lib.repository import D2Repository

                bk_repo = D2Repository(bk_data, locale=locale)
                rt_repo = D2Repository(rt_data, locale=locale)
                bk_res = PropertyResolverService(bk_repo)
                rt_res = PropertyResolverService(rt_repo)
                bk_items_svc = ItemAnalyzerService(bk_repo, bk_res)
                rt_items_svc = ItemAnalyzerService(rt_repo, rt_res)

                item_db = os.path.join(tmp, locale, "item_db")
                old_item_db = os.path.join(tmp, locale, "old_item_db")
                for sub_dir, svc in ((item_db, bk_items_svc), (old_item_db, rt_items_svc)):
                    os.makedirs(os.path.join(sub_dir, "uniques"), exist_ok=True)
                    os.makedirs(os.path.join(sub_dir, "sets"), exist_ok=True)
                    os.makedirs(os.path.join(sub_dir, "runewords"), exist_ok=True)
                    Path(sub_dir, "uniques", "all.json").write_text(
                        json.dumps([svc.analyze_unique(r) for r in svc.repo.get_excel_table("uniqueitems")], ensure_ascii=False),
                        encoding="utf-8",
                    )
                    Path(sub_dir, "sets", "all.json").write_text(
                        json.dumps([svc.analyze_set_item(r) for r in svc.repo.get_excel_table("setitems")], ensure_ascii=False),
                        encoding="utf-8",
                    )
                    Path(sub_dir, "runewords", "all.json").write_text(
                        json.dumps([svc.analyze_runeword(r) for r in svc.repo.get_excel_table("runes") if r.get("complete") == "1"], ensure_ascii=False),
                        encoding="utf-8",
                    )

                skill_tree_dir = os.path.join(tmp, locale, "skill_trees")
                os.makedirs(skill_tree_dir, exist_ok=True)
                out_dir = os.path.join(tmp, locale, "out")
                WikiGenerator(
                    item_db_dir=item_db,
                    skill_tree_dir=skill_tree_dir,
                    output_dir=out_dir,
                    old_item_db_dir=old_item_db,
                    old_label="Retail",
                    new_label="BKDiablo",
                    game_data_dir=bk_data,
                    retail_data_dir=rt_data,
                    locale=locale,
                ).generate()

                manifest = json.loads(Path(out_dir, "manifest.json").read_text(encoding="utf-8"))
                items_index = json.loads(Path(out_dir, "data", "items-index.json").read_text(encoding="utf-8"))
                items_parsed = _parse_html(os.path.join(out_dir, "items", "index.html"))
                bases_parsed = _parse_html(os.path.join(out_dir, "bases", "index.html"))
                rw_parsed = _parse_html(os.path.join(out_dir, "runewords", "index.html"))
                sets_parsed = _parse_html(os.path.join(out_dir, "sets", "index.html"))
                gems_parsed = _parse_html(os.path.join(out_dir, "gems-runes", "index.html"))
                misc_parsed = _parse_html(os.path.join(out_dir, "misc", "index.html"))
                affix_parsed = _parse_html(os.path.join(out_dir, "references", "affixes", "index.html"))
                cls_parsed = _parse_html(os.path.join(out_dir, "classes", "amazon", "index.html"))

                results[locale] = {
                    "routes": sorted(entry["path"] for entry in manifest),
                    "item_statuses": [(row["family"], row["href"], row["status"]) for row in items_index],
                    "item_select_values": {k: [o["value"] for o in v] for k, v in items_parsed.selects.items()},
                    "item_select_labels": {k: [o["label"] for o in v] for k, v in items_parsed.selects.items()},
                    "item_optgroup_codes": [g["group_code"] for g in items_parsed.optgroups if g["select"] == "item-type-filter"],
                    "item_data_attrs": items_parsed.data_attrs,
                    "base_select_values": {k: [o["value"] for o in v] for k, v in bases_parsed.selects.items()},
                    "base_select_labels": {k: [o["label"] for o in v] for k, v in bases_parsed.selects.items()},
                    "base_data_attrs": bases_parsed.data_attrs,
                    "rw_select_values": {k: [o["value"] for o in v] for k, v in rw_parsed.selects.items()},
                    "rw_data_attrs": rw_parsed.data_attrs,
                    "set_ids": sets_parsed.ids,
                    "gem_ids": gems_parsed.ids,
                    "gem_hrefs": gems_parsed.hash_hrefs,
                    "misc_ids": misc_parsed.ids,
                    "misc_hrefs": misc_parsed.hash_hrefs,
                    "affix_ids": [i for i in affix_parsed.ids if i.startswith("affix-function-")],
                    "cls_ids": cls_parsed.ids,
                    "sets_html": Path(out_dir, "sets", "index.html").read_text(encoding="utf-8"),
                    "items_html": Path(out_dir, "items", "index.html").read_text(encoding="utf-8"),
                    "bases_html": Path(out_dir, "bases", "index.html").read_text(encoding="utf-8"),
                }

            def _sorted_attrs(items_list: list[dict[str, str]]) -> list[tuple[tuple[str, str], ...]]:
                return sorted(tuple(sorted(d.items())) for d in items_list)

            base_locale = results["enUS"]
            for other in ("deDE", "koKR"):
                cur = results[other]
                self.assertEqual(base_locale["routes"], cur["routes"])
                self.assertEqual(set(base_locale["item_statuses"]), set(cur["item_statuses"]))
                self.assertEqual(
                    {k: set(v) for k, v in base_locale["item_select_values"].items()},
                    {k: set(v) for k, v in cur["item_select_values"].items()},
                )
                self.assertEqual(base_locale["item_optgroup_codes"], cur["item_optgroup_codes"])
                self.assertEqual(_sorted_attrs(base_locale["item_data_attrs"]), _sorted_attrs(cur["item_data_attrs"]))
                self.assertEqual(
                    {k: set(v) for k, v in base_locale["base_select_values"].items()},
                    {k: set(v) for k, v in cur["base_select_values"].items()},
                )
                self.assertEqual(_sorted_attrs(base_locale["base_data_attrs"]), _sorted_attrs(cur["base_data_attrs"]))
                self.assertEqual(
                    {k: set(v) for k, v in base_locale["rw_select_values"].items()},
                    {k: set(v) for k, v in cur["rw_select_values"].items()},
                )
                self.assertEqual(_sorted_attrs(base_locale["rw_data_attrs"]), _sorted_attrs(cur["rw_data_attrs"]))
                self.assertEqual(set(base_locale["set_ids"]), set(cur["set_ids"]))
                self.assertEqual(base_locale["gem_ids"], cur["gem_ids"])
                self.assertEqual(base_locale["gem_hrefs"], cur["gem_hrefs"])
                self.assertEqual(base_locale["misc_ids"], cur["misc_ids"])
                self.assertEqual(base_locale["misc_hrefs"], cur["misc_hrefs"])
                self.assertEqual(set(base_locale["affix_ids"]), set(cur["affix_ids"]))
                self.assertEqual(base_locale["cls_ids"], cur["cls_ids"])

            # Dummy Charm Blank & Runeword56 must be excluded even in Korean
            self.assertEqual(3, len(base_locale["item_statuses"]))
            self.assertNotIn("빈 부적", results["koKR"]["items_html"])
            self.assertNotIn("복수", results["koKR"]["items_html"])

            # Visible labels and anchors preserve Korean localization while IDs stay ASCII/canonical
            self.assertIn("산더의 부츠", results["koKR"]["sets_html"])
            self.assertIn("id=\"mcauleys-folly-mcauleys-boots\"", results["koKR"]["sets_html"])
            self.assertIn("드루이드", results["koKR"]["base_select_labels"]["base-class-filter"])
            self.assertIn("dru", results["koKR"]["base_select_values"]["base-class-filter"])
            self.assertNotIn("드루이드", results["koKR"]["base_select_values"]["base-class-filter"])
            for anchor in (*base_locale["set_ids"], *base_locale["gem_ids"], *base_locale["misc_ids"]):
                self.assertRegex(anchor, r"^[a-z0-9-]+$")

    def test_redundant_root_type_codes_excludes_inherited_merc_and_avoids_duplicate_base_filter_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            bk_data = os.path.join(tmp, "bk_data")
            rt_data = os.path.join(tmp, "rt_data")
            bk_excel = os.path.join(bk_data, "data", "global", "excel")
            rt_excel = os.path.join(rt_data, "data", "global", "excel")
            bk_strings_dir = os.path.join(bk_data, "data", "local", "lng", "strings")
            rt_strings_dir = os.path.join(rt_data, "data", "local", "lng", "strings")

            strings = [
                {"Key": "armor", "enUS": "Armor", "deDE": "Rüstung", "koKR": "갑옷"},
                {"Key": "StrGemX3", "enUS": "Weapons:", "deDE": "Waffen:", "koKR": "무기:"},
                {"Key": "helms", "enUS": "Helms", "deDE": "Helme", "koKR": "투구"},
                {"Key": "belts", "enUS": "Belts", "deDE": "Gürtel", "koKR": "벨트"},
                {"Key": "r_hel", "enUS": "Helmet", "deDE": "Helm", "koKR": "투구"},
                {"Key": "r_arm", "enUS": "Body Armor", "deDE": "Körperrüstung", "koKR": "갑옷"},
                {"Key": "Belts", "enUS": "Belts", "deDE": "Gürtel", "koKR": "벨트"},
                {"Key": "LootFilterNormalQuality", "enUS": "Normal", "deDE": "Normal", "koKR": "보통"},
                {"Key": "cap", "enUS": "Cap", "deDE": "Kappe", "koKR": "캡"},
                {"Key": "lbl", "enUS": "Sash", "deDE": "Schärpe", "koKR": "새시"},
                {"Key": "ModStr4f", "enUS": "%+d%% Damage to Undead", "deDE": "%+d%% Schaden an Untoten", "koKR": "언데드 피해 +%d%%"},
            ]
            _write_strings(bk_strings_dir, strings)
            _write_strings(rt_strings_dir, strings)

            for excel_dir in (bk_excel, rt_excel):
                _write_tsv(
                    excel_dir,
                    "itemtypes.txt",
                    ["ItemType", "Code", "Equiv1", "Equiv2", "StorePage", "UICategory", "MaxSockets1", "MaxSockets2", "MaxSockets3", "RunewordCategory1", "RunewordCategory2"],
                    [
                        {"ItemType": "Any Armor", "Code": "armo", "StorePage": "armo", "RunewordCategory1": "r_arm"},
                        {"ItemType": "Armor", "Code": "tors", "Equiv1": "armo", "StorePage": "armo", "RunewordCategory1": "r_arm"},
                        {"ItemType": "Helm", "Code": "merc", "RunewordCategory1": "r_hel"},
                        {"ItemType": "Merc Equip", "Code": "helm", "Equiv1": "armo", "Equiv2": "merc", "StorePage": "armo", "UICategory": "helms", "MaxSockets1": "2", "MaxSockets2": "2", "MaxSockets3": "2"},
                        {"ItemType": "Belts", "Code": "belt", "Equiv1": "armo", "Equiv2": "merc", "StorePage": "armo", "UICategory": "belts"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "armor.txt",
                    ["name", "namestr", "code", "normcode", "type", "level", "levelreq", "reqstr", "minac", "maxac", "gemsockets", "speed"],
                    [
                        {"name": "Cap", "namestr": "cap", "code": "cap", "normcode": "cap", "type": "helm", "level": "1", "levelreq": "1", "minac": "3", "maxac": "5", "gemsockets": "2", "speed": "0"},
                        {"name": "Sash", "namestr": "lbl", "code": "lbl", "normcode": "lbl", "type": "belt", "level": "3", "levelreq": "1", "minac": "2", "maxac": "3", "gemsockets": "0", "speed": "0"},
                    ],
                )
                _write_tsv(
                    excel_dir,
                    "runes.txt",
                    ["Name", "*Rune Name", "complete", "itype1", "itype2", "Rune1", "T1Code1", "T1Min1", "T1Max1"],
                    [
                        {"Name": "Runeword1", "*Rune Name": "Lore", "complete": "1", "itype1": "helm", "itype2": "tors", "Rune1": "r09", "T1Code1": "str", "T1Min1": "1", "T1Max1": "1"},
                    ],
                )
                for extra in ("weapons", "misc", "gems", "charstats", "properties", "itemstatcost", "skilldesc", "skills", "sets", "setitems", "uniqueitems", "automagic", "qualityitems", "magicprefix", "magicsuffix", "levels", "monstats", "treasureclassex", "superuniques", "cubemain", "experience", "difficultylevels", "missiles", "gamble"):
                    _write_tsv(excel_dir, f"{extra}.txt", ["col1", "col2"], [])

            from d2lib.repository import D2Repository
            from d2lib.services.item_types import ItemTypeTaxonomy

            option_values_by_locale = {}
            for locale in ("enUS", "deDE", "koKR"):
                repo = D2Repository(bk_data, locale=locale)
                taxonomy = ItemTypeTaxonomy(repo)
                self.assertEqual({"armo", "merc"}, taxonomy.redundant_root_type_codes())

                idb = os.path.join(tmp, locale, "idb")
                st = os.path.join(tmp, locale, "st")
                out = os.path.join(tmp, locale, "out")
                os.makedirs(idb, exist_ok=True)
                os.makedirs(st, exist_ok=True)
                WikiGenerator(idb, st, out, game_data_dir=bk_data, retail_data_dir=rt_data, locale=locale).generate()
                parsed = _parse_html(os.path.join(out, "bases", "index.html"))
                options = parsed.selects["base-category-filter"]
                labels = [opt["label"] for opt in options]
                self.assertEqual(len(labels), len(set(labels)), f"Duplicate labels in {locale}: {labels}")
                values = [opt["value"] for opt in options]
                self.assertNotIn("merc", values)
                self.assertNotIn("armo", values)
                self.assertIn("helm", values)
                option_values_by_locale[locale] = set(values)

            self.assertEqual(option_values_by_locale["enUS"], option_values_by_locale["deDE"])
            self.assertEqual(option_values_by_locale["enUS"], option_values_by_locale["koKR"])


if __name__ == "__main__":
    unittest.main()
