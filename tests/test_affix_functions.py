import os
import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))

from d2lib.services.references import ReferenceAnalyzerService
from d2lib.services.resolver import PropertyResolverService
from d2lib.wiki.affix_functions import affix_function_groups
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
        return self.strings.get(key, key)

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
            ["Unknown property: new-stat1", "Unknown property: new-stat2"],
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


if __name__ == "__main__":
    unittest.main()
