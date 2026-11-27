import os
import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))

from d2lib.repository import strip_d2_formatting
from d2lib.services.references import ReferenceAnalyzerService
from d2lib.services.resolver import PropertyResolverService
from d2lib.wiki.affix_functions import affix_function_groups
from d2lib.wiki.comparison import affix_card_contexts
from d2lib.wiki.generator import WikiContentBuilder


class Repository:
    def __init__(self, tables=None, strings=None, property_groups=None):
        self.tables = tables or {}
        self.strings = strings or {}
        self.property_groups = property_groups or []
        self.loaded_paths = []

    def get_excel_table(self, name):
        return self.tables.get(name, [])

    def get_string(self, key):
        return strip_d2_formatting(self.strings.get(key, key))

    def load_tsv(self, path):
        self.loaded_paths.append(path)
        return self.property_groups


def affix(name, *mods, level="1"):
    row = {
        "Name": name, "spawnable": "1", "frequency": "1", "rare": "1",
        "level": level, "itype1": "test",
    }
    for index, (code, low, high, param) in enumerate(mods, 1):
        for field, value in (("code", code), ("min", low), ("max", high), ("param", param)):
            row[f"mod{index}{field}"] = str(value)
    return row


def groups_for(rows, definitions=(), **tables):
    repo = Repository({
        "magicprefix": rows,
        "properties": list(definitions),
        **tables,
    })
    return affix_function_groups(ReferenceAnalyzerService(repo))


class TestAffixFunctions(unittest.TestCase):
    def test_builder_loads_new_property_groups_for_both_versions(self):
        definition = {"code": "str", "func1": "1", "stat1": "strength", "*Tooltip": "+# to Strength"}
        group = {
            "code": "future-group", "PickMode": "1",
            "Prop1": "str", "ModMin1": "2", "ModMax1": "5",
        }
        tables = {
            "properties": [definition],
            "magicprefix": [affix("Future Affix", ("future-group", 1, 1, ""))],
        }
        builder = WikiContentBuilder.__new__(WikiContentBuilder)
        builder._repo = Repository(tables, property_groups=[group])
        builder._retail_repo = Repository(tables)
        builder.new_label, builder.old_label = "BKDiablo", "Retail"
        with patch.object(builder, "_available_excel_tables", return_value=[]):
            pages, _ = builder._load_reference_pages()
        page = next(page for page in pages if page["slug"] == "affixes-by-function")
        self.assertEqual("Strength", page["sections"][0]["title"])
        self.assertEqual(("+2-5 to Strength",), page["sections"][0]["rows"][0]["roll_ranges"])
        self.assertTrue(builder._repo.loaded_paths[0].endswith("propertygroups.txt"))
        comparison = next(page for page in pages if page["slug"] == "affixes")["sections"][0]["comparison_rows"][0]
        self.assertEqual("Unchanged", comparison["status"])
        self.assertEqual(("+2-5 to Strength",), comparison["old"][0]["properties"])

    def test_unknown_numbered_properties_keep_distinct_names_and_groups(self):
        groups = groups_for([
            affix("First", ("new-stat1", 2, 5, "")),
            affix("Second", ("new-stat2", 2, 5, "")),
        ])
        self.assertEqual(
            ["Unknown property (new-stat1)", "Unknown property (new-stat2)"],
            [group["title"] for group in groups],
        )

    def test_identical_display_text_keeps_different_stats_separate(self):
        groups = groups_for(
            [
                affix("First", ("new-property1", 2, 5, "")),
                affix("Second", ("new-property2", 2, 5, "")),
            ],
            [
                {"code": "new-property1", "stat1": "first_stat", "*Tooltip": "+# Custom Bonus"},
                {"code": "new-property2", "stat1": "second_stat", "*Tooltip": "+# Custom Bonus"},
            ],
        )
        self.assertEqual(["Custom Bonus (first_stat)", "Custom Bonus (second_stat)"], [g["title"] for g in groups])
        self.assertTrue(all(len(group["rows"]) == 1 for group in groups))

    def test_minimum_only_and_maximum_only_elemental_damage_keep_their_names(self):
        groups = groups_for(
            [
                affix("Minimum", ("fire-min", 1, 5, "")),
                affix("Maximum", ("fire-max", 1, 5, "")),
                affix("Both", ("fire-min", 1, 5, ""), ("fire-max", 5, 10, "")),
            ],
            [
                {"code": "fire-min", "stat1": "firemindam", "*Tooltip": "+# to Minimum Fire Damage"},
                {"code": "fire-max", "stat1": "firemaxdam", "*Tooltip": "+# to Maximum Fire Damage"},
            ],
        )
        self.assertEqual(["Fire Damage", "Maximum Fire Damage", "Minimum Fire Damage"], [g["title"] for g in groups])

    def test_numbered_skill_names_are_preserved(self):
        groups = groups_for(
            [affix("First", ("oskill", 1, 3, "101")), affix("Second", ("oskill", 1, 3, "102"))],
            [{"code": "oskill", "stat1": "item_nonclassskill", "*Tooltip": "+# to [Skill]"}],
            skills=[{"Id": "101", "skill": "Future Skill 1"}, {"Id": "102", "skill": "Future Skill 2"}],
        )
        self.assertEqual(["Future Skill 1", "Future Skill 2"], [g["title"] for g in groups])

    def test_signed_and_decimal_ranges_sort_numerically(self):
        groups = groups_for(
            [
                affix("Positive", ("str", 3, 7, "")),
                affix("Negative Five", ("str", -5, -2, "")),
                affix("Negative Twenty", ("str", -20, -5, "")),
                affix("Decimal", ("str", 0.5, 1.5, "")),
                affix("Lower Maximum", ("str", 3, 5, ""), level="99"),
            ],
            [{"code": "str", "stat1": "strength", "*Tooltip": "# to Strength"}],
        )
        self.assertEqual(["Strength"], [g["title"] for g in groups])
        self.assertEqual(
            ["Negative Twenty", "Negative Five", "Decimal", "Lower Maximum", "Positive"],
            [row["name"] for row in groups[0]["rows"]],
        )

    def test_compound_properties_remain_alphabetical_and_sort_by_ranges(self):
        groups = groups_for(
            [
                affix("Higher", ("dmg", 1, 3, ""), ("att", 21, 48, "")),
                affix("Lower", ("dmg", 1, 3, ""), ("att", 10, 20, "")),
            ],
            [
                {"code": "att", "stat1": "tohit", "*Tooltip": "+# to Attack Rating"},
                {"code": "dmg", "stat1": "item_normaldamage", "*Tooltip": "Damage +#"},
            ],
        )
        self.assertEqual("Attack Rating + Damage", groups[0]["title"])
        self.assertEqual(["Lower", "Higher"], [row["name"] for row in groups[0]["rows"]])
        self.assertEqual(("+10-20 to Attack Rating", "Damage +1-3"), groups[0]["rows"][0]["roll_ranges"])

    def test_negative_values_resolve_from_localized_stat_formats(self):
        repo = Repository({
            "properties": [{"code": "str", "stat1": "strength"}],
            "itemstatcost": [{"Stat": "strength", "descstrpos": "positive", "descstrneg": "negative"}],
            "magicprefix": [affix("Penalty", ("str", -20, -5, ""))],
        }, {"positive": "+%d to Strength", "negative": "-%d to Strength"})
        groups = affix_function_groups(ReferenceAnalyzerService(repo))
        self.assertEqual(("-20--5 to Strength",), groups[0]["rows"][0]["roll_ranges"])

    def test_nested_property_groups_resolve(self):
        repo = Repository({
            "properties": [{"code": "str", "stat1": "strength", "*Tooltip": "+# to Strength"}],
            "magicprefix": [affix("Nested", ("outer", 1, 1, ""))],
        })
        definitions = [
            {"code": "outer", "PickMode": "1", "Prop1": "inner"},
            {"code": "inner", "PickMode": "1", "Prop1": "str", "ModMin1": "2", "ModMax1": "5"},
        ]
        resolver = PropertyResolverService(repo, definitions)
        groups = affix_function_groups(ReferenceAnalyzerService(repo, resolver))
        self.assertEqual("Strength", groups[0]["title"])
        self.assertEqual(("+2-5 to Strength",), groups[0]["rows"][0]["roll_ranges"])

    def test_incomplete_translations_retain_type_label(self):
        repo = Repository({
            "itemtypes": [{"Code": "swor", "ItemType": "Swords"}],
            "weapons": [
                {"type": "swor", "namestr": "short", "code": "ssd"},
                {"type": "swor", "namestr": "future", "code": "fsd"},
            ],
        }, {"short": "Short Sword"})
        self.assertEqual("Swords", ReferenceAnalyzerService(repo)._item_type_names()["swor"])
        repo.strings["future"] = "Future Sword"
        self.assertEqual("Swords", ReferenceAnalyzerService(repo)._item_type_names()["swor"])

    def test_unique_localized_charm_name_ignores_quest_items(self):
        repo = Repository({
            "itemtypes": [{"Code": "mcha", "ItemType": "Medium Charm"}],
            "misc": [
                {"type": "mcha", "namestr": "cm2", "code": "cm2"},
                {"type": "mcha", "namestr": "quest", "code": "qch", "quest": "1"},
            ],
        }, {"cm2": "Large Charm", "quest": "Quest Charm"})
        self.assertEqual("Large Charm", ReferenceAnalyzerService(repo)._item_type_names()["mcha"])

    def test_item_type_names_skips_loot_filter_shorthand_and_distinguishes_armo_from_tors(self):
        repo = Repository({
            "itemtypes": [
                {"Code": "armo", "ItemType": "Any Armor", "RunewordCategory1": "r_arm"},
                {"Code": "tors", "ItemType": "Armor", "Equiv1": "armo", "UICategory": "armor", "RunewordCategory1": "r_arm"},
                {"Code": "bowq", "ItemType": "Bow Quiver", "Normal": "1", "UICategory": "ammo"},
                {"Code": "xboq", "ItemType": "Crossbow Quiver", "Normal": "1", "UICategory": "ammo"},
                {"Code": "jewl", "ItemType": "Jewel", "Normal": "0", "UICategory": "jewel"},
                {"Code": "bow", "ItemType": "Bow", "UICategory": "bows"},
            ],
            "misc": [
                {"type": "bowq", "namestr": "aqv", "code": "aqv"},
                {"type": "xboq", "namestr": "cqv", "code": "cqv"},
                {"type": "jewl", "namestr": "jew", "code": "jew"},
            ],
            "weapons": [
                {"type": "bow", "namestr": "bow", "code": "bow"},
            ],
            "runes": [
                {"complete": "1", "itype1": "tors"},
            ],
        }, {
            "armor": "Armor",
            "r_arm": "Body Armor",
            "aqv": "A",
            "cqv": "B",
            "jew": "•• Jewel ••",
            "Jewel": "Jewels",
            "jewel": "Jewels",
            "bow": "활",
        })
        names = ReferenceAnalyzerService(repo)._item_type_names()
        self.assertEqual("Armor", names["armo"])
        self.assertEqual("Body Armor", names["tors"])
        self.assertEqual("Bow Quiver", names["bowq"])
        self.assertEqual("Crossbow Quiver", names["xboq"])
        self.assertEqual("Jewels", names["jewl"])
        self.assertEqual("활", names["bow"])

    def test_cold_duration_is_present_for_both_encodings_without_duplicates(self):
        groups = groups_for(
            [
                affix("Embedded", ("dmg-cold", 1, 5, "25")),
                affix("Standalone", ("dmg-cold", 1, 5, ""), ("cold-len", 25, 25, "")),
                affix("Both", ("dmg-cold", 1, 5, "25"), ("cold-len", 50, 50, "")),
                affix("Components", ("cold-min", 1, 1, ""), ("cold-max", 5, 5, ""), ("cold-len", 25, 25, "")),
                affix("Fallback", ("dmg-cold", 1, 5, "")),
            ],
            [
                {"code": "dmg-cold", "stat1": "coldmindam", "stat2": "coldmaxdam", "stat3": "coldlength", "*Tooltip": "Adds #-# Cold Damage"},
                {"code": "cold-len", "stat1": "coldlength"},
                {"code": "cold-min", "stat1": "coldmindam", "*Tooltip": "+# to Minimum Cold Damage"},
                {"code": "cold-max", "stat1": "coldmaxdam", "*Tooltip": "+# to Maximum Cold Damage"},
            ],
        )
        self.assertEqual(["Cold Damage"], [g["title"] for g in groups])
        rows = {row["name"]: " · ".join(row["roll_ranges"]) for row in groups[0]["rows"]}
        expected_durations = {
            "Embedded": "1 second (25 frames)",
            "Standalone": "1.04-1.2 seconds (26-30 frames)",
            "Both": "3 seconds (75 frames)",
            "Components": "1 second (25 frames)",
            "Fallback": "0.04-0.2 seconds (1-5 frames)",
        }
        for name, text in rows.items():
            self.assertEqual(1, text.count("Cold Duration"), name)
            self.assertIn(expected_durations[name], text)

    def test_cold_duration_respects_replacement_flags_and_modifier_order(self):
        definitions = [
            {"code": "dmg-cold", "stat1": "coldmindam", "stat2": "coldmaxdam", "stat3": "coldlength", "func3": "17"},
            {"code": "cold-len", "stat1": "coldlength", "set1": "1"},
        ]
        groups = groups_for(
            [
                affix("Replace", ("dmg-cold", 1, 5, "25"), ("cold-len", 50, 50, "")),
                affix("Add After Replace", ("cold-len", 50, 50, ""), ("dmg-cold", 1, 5, "25")),
            ],
            definitions,
        )
        rows = {row["name"]: " · ".join(row["roll_ranges"]) for row in groups[0]["rows"]}
        self.assertIn("2 seconds (50 frames)", rows["Replace"])
        self.assertIn("3 seconds (75 frames)", rows["Add After Replace"])

    def test_skill_tab_names_use_localized_class_data_and_skip_separator_rows(self):
        repo = Repository({
            "charstats": [
                {
                    "class": "Sorceress", "StrAllSkills": "sor_all", "StrClassOnly": "sor_only",
                    "StrSkillTab1": "sor_fire", "StrSkillTab2": "sor_lightning", "StrSkillTab3": "sor_cold",
                },
                {"class": "Expansion"},
                {
                    "class": "Warlock", "StrAllSkills": "war_all", "StrClassOnly": "war_only",
                    "StrSkillTab1": "war_demon", "StrSkillTab2": "war_eldritch", "StrSkillTab3": "war_chaos",
                },
            ],
            "properties": [
                {"code": "skilltab", "stat1": "item_addskill_tab", "*Tooltip": "+# to [Class Skill Tab] Skills"},
                {"code": "war", "stat1": "item_addclassskills", "func1": "21", "val1": "1", "*Tooltip": "+# to Outdated Name"},
            ],
            "magicprefix": [
                affix("Fiendish", ("skilltab", 1, 1, "3")),
                affix("Sullied", ("skilltab", 1, 1, "4")),
                affix("Chaotic", ("skilltab", 1, 1, "5")),
                affix("Devil", ("war", 1, 1, "")),
            ],
        }, {
            "sor_all": "%+d to Sorceress Skill Levels", "sor_only": "(Sorceress Only)",
            "sor_fire": "%+d to Fire Skills", "sor_lightning": "%+d to Lightning Skills",
            "sor_cold": "%+d to Cold Skills", "war_all": "+%d to Warlock Skills",
            "war_only": "(Warlock Only)", "war_demon": "+%d to Demon Skills",
            "war_eldritch": "+%d to Eldritch Skills", "war_chaos": "+%d to Chaos Skills",
        })
        groups = affix_function_groups(ReferenceAnalyzerService(repo))
        self.assertEqual(
            ["Chaos Skills", "Demon Skills", "Eldritch Skills", "Warlock Skills"],
            [group["title"] for group in groups],
        )
        self.assertEqual(("+1 to Warlock Skills",), groups[-1]["rows"][0]["roll_ranges"])
        repo.strings["war_demon"] = "+%d to Renamed Demon Skills"
        updated = affix_function_groups(ReferenceAnalyzerService(repo))
        self.assertIn("Renamed Demon Skills", [group["title"] for group in updated])

    def test_shared_tab_names_use_localized_class_qualifiers(self):
        repo = Repository({
            "charstats": [
                {"class": "Necromancer", "StrAllSkills": "nec_all", "StrClassOnly": "nec_only", "StrSkillTab1": "summon"},
                {"class": "Druid", "StrAllSkills": "dru_all", "StrClassOnly": "dru_only", "StrSkillTab1": "summon"},
            ],
            "properties": [{"code": "skilltab", "stat1": "item_addskill_tab", "*Tooltip": "+# to [Class Skill Tab] Skills"}],
            "magicprefix": [affix("Graverobber", ("skilltab", 1, 1, "0")), affix("Trainer", ("skilltab", 1, 1, "3"))],
        }, {
            "summon": "%+d to Summoning Skills",
            "nec_only": "(Necromancer Only)", "dru_only": "(Druid Only)",
        })
        groups = affix_function_groups(ReferenceAnalyzerService(repo))
        self.assertEqual(
            ["Summoning Skills (Druid Only)", "Summoning Skills (Necromancer Only)"],
            [group["title"] for group in groups],
        )

    def test_unknown_tab_preserves_its_number(self):
        groups = groups_for(
            [affix("Future Tab", ("skilltab", 1, 1, "99"))],
            [{"code": "skilltab", "stat1": "item_addskill_tab", "*Tooltip": "+# to [Class Skill Tab] Skills"}],
        )
        self.assertEqual("Tab 99 Skills", groups[0]["title"])

    def test_socket_counts_use_affix_ranges_and_fixed_parameters(self):
        groups = groups_for(
            [
                affix("Mechanist", ("sock", 1, 2, "")),
                affix("Artificer", ("sock", "", "", "3")),
                affix("Jeweler", ("sock", "", "", "4")),
            ],
            [{"code": "sock", "func1": "14", "stat1": "item_numsockets", "*Tooltip": "Socketed (#)", "val1": ""}],
        )
        self.assertEqual(["Socketed"], [group["title"] for group in groups])
        self.assertEqual(
            [("Socketed (1-2)",), ("Socketed (3)",), ("Socketed (4)",)],
            [row["roll_ranges"] for row in groups[0]["rows"]],
        )

    def test_affix_groups_localize_class_restriction_from_charstats(self):
        prefix_rows = [
            dict(affix("Sorceress Only", ("str", 1, 2, "")), **{"class": "sor"}),
            dict(affix("Cleric Only", ("str", 3, 4, "")), **{"class": "cle"}),
            dict(affix("Unknown Class", ("str", 5, 6, "")), **{"class": "xyz"}),
        ]
        repo = Repository(
            {
                "charstats": [
                    {"class": "Sorceress"},
                    {"class": "Expansion"},
                    {"class": "Cleric"},
                ],
                "properties": [{"code": "str", "stat1": "strength", "*Tooltip": "+# to Strength"}],
                "magicprefix": prefix_rows,
            },
            {"Sorceress": "원소술사", "Cleric": "Kleriker"},
        )
        groups = ReferenceAnalyzerService(repo).affix_groups("magicprefix")
        self.assertIn("Class 원소술사", groups["sorceress only"][1][0].settings)
        self.assertEqual("sor", groups["sorceress only"][1][0].identity["class"])
        self.assertIn("Class Kleriker", groups["cleric only"][1][0].settings)
        self.assertIn("Class xyz", groups["unknown class"][1][0].settings)

    def test_structured_affix_grouping_and_cards_work_across_non_english_locales(self):
        tables = {
            "itemtypes": [
                {"Code": "swor", "ItemType": "TypeSword"},
                {"Code": "amul", "ItemType": "TypeAmulet"},
            ],
            "properties": [
                {"code": "fire-min", "func1": "1", "stat1": "firemindam"},
                {"code": "fire-max", "func1": "1", "stat1": "firemaxdam"},
                {"code": "dmg-cold", "func1": "15", "stat1": "coldmindam", "stat2": "coldmaxdam", "stat3": "coldlength"},
                {"code": "cold-len", "func1": "1", "stat1": "coldlength"},
                {"code": "ac/lvl", "func1": "17", "stat1": "item_armor_perlevel"},
            ],
            "itemstatcost": [
                {"Stat": "firemindam", "descfunc": "19", "descstrpos": "ModStr1p"},
                {"Stat": "firemaxdam", "descfunc": "19", "descstrpos": "ModStr1o"},
                {"Stat": "item_armor_perlevel", "descfunc": "19", "op": "2", "op param": "3", "op base": "level", "descstrpos": "ModStr1i", "descstr2": "ModStre9c"},
            ],
            "magicprefix": [
                dict(affix("FieryMin", ("fire-min", 2, 4, ""), level="1"), etype1="amul", group="7", version="100"),
                dict(affix("FieryMax", ("fire-max", 8, 12, ""), level="3"), itype1="swor", etype1="amul"),
                dict(affix("FieryBoth", ("fire-min", 1, 3, ""), ("fire-max", 5, 10, ""), level="5"), itype1="swor"),
                dict(affix("Frost", ("dmg-cold", 1, 4, "25"), ("cold-len", 50, 50, ""), level="7"), itype1="swor"),
                dict(affix("FoolDef", ("ac/lvl", 8, 16, ""), level="9"), itype1="swor"),
            ],
        }
        strings_by_locale = {
            "deDE": {
                "TypeSword": "Schwerter",
                "TypeAmulet": "Amulett",
                "ModStr1p": "%+d zu min. Feuerschaden",
                "ModStr1o": "%+d zu max. Feuerschaden",
                "strModFireDamage": "%+d Feuerschaden",
                "strModColdDamageRange": "Fügt %d-%d Kälteschaden hinzu",
                "strModColdDamage": "%+d Kälteschaden",
                "strskill13": "Dauer der Kälte: %d Sek.",
                "ModStr1i": "%+d Verteidigung",
                "ModStre9c": "(Basierend auf Charakterstufe)",
                "FieryMin": "Feuriger Minimal",
                "FieryMax": "Feuriger Maximal",
                "FieryBoth": "Feuriger",
                "Frost": "Frostiger",
                "FoolDef": "Robuster",
            },
            "koKR": {
                "TypeSword": "검",
                "TypeAmulet": "목걸이",
                "ModStr1p": "최소 화염 피해 %+d",
                "ModStr1o": "최대 화염 피해 %+d",
                "strModFireDamage": "화염 피해 %+d",
                "strModColdDamageRange": "냉기 피해 %d - %d 추가",
                "strModColdDamage": "냉기 피해 %+d",
                "strskill13": "냉기 지속시간: %d초",
                "ModStr1i": "방어력 %+d",
                "ModStre9c": "(캐릭터 레벨에 비례)",
                "FieryMin": "타오르는 최소",
                "FieryMax": "타오르는 최대",
                "FieryBoth": "타오르는",
                "Frost": "서리의",
                "FoolDef": "견고한",
            },
        }
        expected_titles = {
            "deDE": ["Feuerschaden", "Kälteschaden", "Max. Feuerschaden", "Min. Feuerschaden", "Verteidigung (Basierend auf Charakterstufe)"],
            "koKR": ["냉기 피해", "방어력 (캐릭터 레벨에 비례)", "최대 화염 피해", "최소 화염 피해", "화염 피해"],
        }

        for locale, strings in strings_by_locale.items():
            repo = Repository(tables, strings)
            svc = ReferenceAnalyzerService(repo)
            groups = affix_function_groups(svc)
            self.assertEqual([g["title"] for g in groups], expected_titles[locale], locale)
            fire_min_row = next(g for g in groups if "Min" in g["title"] or "최소" in g["title"])["rows"][0]
            self.assertEqual(fire_min_row["excludes"], f"Excludes · {strings['TypeAmulet']} (amul)")
            # Structured dmg-cold split + cold-len accumulation still merges into a single cold duration entry
            cold_row = next(g for g in groups if g["title"] in {"Kälteschaden", "냉기 피해"})["rows"][0]
            self.assertEqual(len(cold_row["roll_ranges"]), 2)
            self.assertTrue(any("3" in part for part in cold_row["roll_ranges"]))

            # Affix card settings exclude group & version via structured setting_entries (no English prefix match)
            comparison = svc.build_pages(["magicprefix"], baseline=svc)[0]["sections"][0]["comparison_rows"]
            entry = next(r for r in comparison if r["label"] == strings["FieryMin"])
            entry["old"][0]["settings"] = tuple(f"Gruppe 7" if s.startswith("Group") else f"Version 100" for s in entry["old"][0]["settings"])
            card, = affix_card_contexts(entry)
            self.assertFalse(any("Gruppe 7" in r["old"] or "Version 100" in r["old"] for r in card["stat_rows"]))


if __name__ == "__main__":
    unittest.main()
