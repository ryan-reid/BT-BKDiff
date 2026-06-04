import os
import sys
import unittest

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.wiki.comparison import (
    item_comparison_context,
    comparison_summary_context,
    entries_match,
    property_occurrence_map,
    rune_property_occurrence_map,
    runeword_compare_rows,
    align_set_member_comparisons,
    base_item_comparison_context,
    gem_rune_comparison_context,
)
from d2lib.wiki.item_helpers import (
    item_slug,
    item_identity,
    item_filter_group,
    item_filter_type,
    should_include_item,
    item_title,
    item_summary,
)
from d2lib.utils import item_category_to_group


class TestItemCategoryToGroup(unittest.TestCase):
    def test_crossbow_before_bow(self):
        # 'crossbow' contains 'bow' — must not be classified as Bows.
        self.assertEqual("Crossbows", item_category_to_group("Crossbow"))
        self.assertEqual("Bows", item_category_to_group("Bow"))

    def test_weapons(self):
        self.assertEqual("Axes", item_category_to_group("Axe"))
        self.assertEqual("Swords", item_category_to_group("Sword"))
        self.assertEqual("Maces", item_category_to_group("Mace"))
        self.assertEqual("Maces", item_category_to_group("War Hammer"))
        self.assertEqual("Maces", item_category_to_group("Club"))
        self.assertEqual("Staves", item_category_to_group("Staff"))
        self.assertEqual("Daggers", item_category_to_group("Dagger"))
        self.assertEqual("Daggers", item_category_to_group("Knife"))
        self.assertEqual("Wands", item_category_to_group("Wand"))
        self.assertEqual("Scepters", item_category_to_group("Scepter"))
        self.assertEqual("Javelins", item_category_to_group("Javelin"))
        self.assertEqual("Spears", item_category_to_group("Spear"))
        self.assertEqual("Polearms", item_category_to_group("Polearm"))
        self.assertEqual("Throwing", item_category_to_group("Throwing"))
        self.assertEqual("Axes", item_category_to_group("Throwing Axe"))   # 'axe' matched before 'throwing'
        self.assertEqual("Daggers", item_category_to_group("Throwing Knife"))  # 'knife' matched before 'throwing'

    def test_armor(self):
        self.assertEqual("Helms", item_category_to_group("Helm"))
        self.assertEqual("Helms", item_category_to_group("Circlet"))
        self.assertEqual("Chests", item_category_to_group("Body Armor"))
        self.assertEqual("Shields", item_category_to_group("Shield"))
        self.assertEqual("Gloves", item_category_to_group("Gloves"))
        self.assertEqual("Belts", item_category_to_group("Belt"))
        self.assertEqual("Boots", item_category_to_group("Boots"))

    def test_jewelry(self):
        self.assertEqual("Amulets", item_category_to_group("Amulet"))
        self.assertEqual("Rings", item_category_to_group("Ring"))
        self.assertEqual("Charms", item_category_to_group("Charm"))
        self.assertEqual("Jewels", item_category_to_group("Jewel"))

    def test_class_gear(self):
        self.assertEqual("Class Weapons", item_category_to_group("Amazon Bow"))
        self.assertEqual("Class Weapons", item_category_to_group("Assassin Claw"))
        self.assertEqual("Class Armors", item_category_to_group("Druid Pelt"))
        self.assertEqual("Class Armors", item_category_to_group("Necromancer Primal"))

    def test_unknown(self):
        self.assertEqual("Others", item_category_to_group(""))
        self.assertEqual("Others", item_category_to_group("Unknown Type"))


class TestEntriesMatch(unittest.TestCase):
    def _entry(self, base="Sword", type_="Weapon", lvl="20", props=None):
        return {
            "base_item": base,
            "item_type": type_,
            "lvl_req": lvl,
            "properties": props or [{"resolved_text": "+10 str"}],
        }

    def test_identical(self):
        e = self._entry()
        self.assertTrue(entries_match(e, e))

    def test_different_base(self):
        self.assertFalse(entries_match(self._entry(base="Sword"), self._entry(base="Axe")))

    def test_different_lvl(self):
        self.assertFalse(entries_match(self._entry(lvl="20"), self._entry(lvl="30")))

    def test_different_props(self):
        a = self._entry(props=[{"resolved_text": "+10 str"}])
        b = self._entry(props=[{"resolved_text": "+20 str"}])
        self.assertFalse(entries_match(a, b))


class TestPropertyOccurrenceMap(unittest.TestCase):
    def test_single_property(self):
        entry = {"properties": [{"code": "str", "param": "", "resolved_text": "+10 Strength"}]}
        result = property_occurrence_map(entry)
        self.assertEqual({("str", "", 1): "+10 Strength"}, result)

    def test_duplicate_property_codes(self):
        entry = {
            "properties": [
                {"code": "dmg", "param": "", "resolved_text": "+5 Damage"},
                {"code": "dmg", "param": "", "resolved_text": "+10 Damage"},
            ]
        }
        result = property_occurrence_map(entry)
        self.assertIn(("dmg", "", 1), result)
        self.assertIn(("dmg", "", 2), result)

    def test_partial_set_bonuses(self):
        entry = {
            "properties": [],
            "partial_set_properties": [
                {"count": 2, "properties": [{"code": "str", "param": "", "resolved_text": "+5 Strength"}]}
            ],
        }
        result = property_occurrence_map(entry)
        key = ("partial-2-str", "", 1)
        self.assertIn(key, result)
        self.assertIn("With 2 Items", result[key])

    def test_empty_entry(self):
        self.assertEqual({}, property_occurrence_map({}))


class TestItemComparisonContext(unittest.TestCase):
    def _entry(self, base="Sword", type_="Weapon", lvl="20", props=None):
        return {
            "base_item": base,
            "item_type": type_,
            "lvl_req": lvl,
            "properties": props or [],
        }

    def test_new_item_is_added(self):
        result = item_comparison_context(self._entry(), "unique", None)
        self.assertEqual("added", result["state"])

    def test_unchanged_item(self):
        e = self._entry(props=[{"code": "str", "param": "", "resolved_text": "+10 str"}])
        result = item_comparison_context(e, "unique", e)
        self.assertEqual("unchanged", result["state"])

    def test_modified_lvl(self):
        old = self._entry(lvl="20")
        new = self._entry(lvl="30")
        result = item_comparison_context(new, "unique", old)
        self.assertEqual("modified", result["state"])
        labels = [r["label"] for r in result["stat_rows"]]
        self.assertIn("Level Requirement", labels)

    def test_added_property(self):
        old = self._entry(props=[])
        new = self._entry(props=[{"code": "str", "param": "", "resolved_text": "+10 Strength"}])
        result = item_comparison_context(new, "unique", old)
        self.assertEqual("modified", result["state"])
        added_rows = [r for r in result["property_rows"] if r["status"] == "added"]
        self.assertEqual(1, len(added_rows))

    def test_runeword_family(self):
        entry = {
            "runes": ["El", "Eld"],
            "base_items": ["Swords"],
            "required_level": "11",
            "properties": [],
        }
        result = item_comparison_context(entry, "runeword", None)
        self.assertEqual("added", result["state"])

    def test_set_family_includes_set_row(self):
        entry = self._entry()
        entry["raw_row"] = {"set": "Vidala's Rig"}
        old = self._entry()
        old["raw_row"] = {"set": "Vidala's Rig"}
        result = item_comparison_context(entry, "set", old)
        labels = [r["label"] for r in result["stat_rows"]]
        self.assertIn("Set", labels)

    def test_rows_only_contains_non_same(self):
        old = self._entry(lvl="20")
        new = self._entry(lvl="30")
        result = item_comparison_context(new, "unique", old)
        self.assertTrue(all(r["status"] != "same" for r in result["rows"]))


class TestComparisonSummaryContext(unittest.TestCase):
    def test_uses_status_field(self):
        comparison = {
            "rows": [
                {"label": "Base Item", "old": "Sword", "new": "Axe", "status": "changed"},
                {"label": "Level Requirement", "old": "", "new": "20", "status": "added"},
                {"label": "Item Type", "old": "Weapon", "new": "", "status": "removed"},
                {"label": "Same Thing", "old": "x", "new": "x", "status": "same"},
            ]
        }
        result = comparison_summary_context(comparison)
        self.assertEqual(1, len(result["changed"]))
        self.assertEqual("Base Item", result["changed"][0]["label"])
        self.assertEqual(1, len(result["added"]))
        self.assertEqual(1, len(result["removed"]))
        self.assertTrue(result["has_changes"])

    def test_no_changes(self):
        comparison = {"rows": [{"label": "Base Item", "old": "Sword", "new": "Sword", "status": "same"}]}
        result = comparison_summary_context(comparison)
        self.assertFalse(result["has_changes"])

    def test_empty_rows(self):
        result = comparison_summary_context({})
        self.assertFalse(result["has_changes"])


class TestItemSlug(unittest.TestCase):
    def test_basic_slug(self):
        entry = {"display_name": "Arkaine's Valor", "base_item": "Balrog Skin"}
        used: dict = {}
        slug = item_slug(entry, "unique", "Arkaine's Valor", used)
        self.assertEqual("arkaines-valor", slug)  # apostrophe stripped, not doubled
        self.assertIn(slug, used)

    def test_dedup_same_title(self):
        entry_a = {"display_name": "Twin Item", "base_item": "First Base"}
        entry_b = {"display_name": "Twin Item", "base_item": "Second Base"}
        used: dict = {}
        slug_a = item_slug(entry_a, "unique", "Twin Item", used)
        slug_b = item_slug(entry_b, "unique", "Twin Item", used)
        self.assertNotEqual(slug_a, slug_b)
        self.assertIn("twin-item", slug_a)

    def test_numeric_suffix_after_disambiguation(self):
        entry_a = {"display_name": "Twin Item", "base_item": "Shared Base"}
        entry_b = {"display_name": "Twin Item", "base_item": "Shared Base"}
        entry_c = {"display_name": "Twin Item", "base_item": "Shared Base"}
        used: dict = {}
        slug_a = item_slug(entry_a, "unique", "Twin Item", used)
        slug_b = item_slug(entry_b, "unique", "Twin Item", used)
        slug_c = item_slug(entry_c, "unique", "Twin Item", used)
        slugs = {slug_a, slug_b, slug_c}
        self.assertEqual(3, len(slugs))

    def test_runeword_uses_first_base(self):
        entry = {"name": "Spirit", "base_items": ["Swords", "Shields"]}
        used: dict = {}
        slug = item_slug(entry, "runeword", "Spirit", used)
        self.assertIn("spirit", slug)


class TestItemIdentity(unittest.TestCase):
    def test_uses_id_when_present(self):
        entry = {"id": "runeword_spirit_sword", "display_name": "Spirit", "base_item": "", "item_type": "", "lvl_req": ""}
        identity = item_identity(entry, "runeword")
        self.assertIn("runeword_spirit_sword", identity)
        self.assertTrue(identity.startswith("runeword|"))

    def test_fallback_uses_display_name(self):
        entry = {"display_name": "My Item", "base_item": "Sword", "item_type": "Weapon", "lvl_req": "20"}
        identity = item_identity(entry, "unique")
        self.assertTrue(identity.startswith("unique|"))
        self.assertIn("my-item", identity)

    def test_same_entry_gives_same_identity(self):
        entry = {"id": "abc123"}
        self.assertEqual(item_identity(entry, "unique"), item_identity(entry, "unique"))

    def test_family_prefix(self):
        entry = {"id": "x"}
        self.assertTrue(item_identity(entry, "set").startswith("set|"))
        self.assertTrue(item_identity(entry, "unique").startswith("unique|"))


class TestShouldIncludeItem(unittest.TestCase):
    def test_include_normal_unique(self):
        entry = {"display_name": "Real Item", "base_item": "Sword", "item_type": "Weapon", "properties": [{"resolved_text": "+10 str"}]}
        self.assertTrue(should_include_item(entry, "unique"))

    def test_exclude_blank_charm(self):
        entry = {"display_name": "Blank Charm", "base_item": "Small Charm", "item_type": "Charm", "properties": []}
        self.assertFalse(should_include_item(entry, "unique"))

    def test_exclude_expansion_placeholder(self):
        entry = {"display_name": "Something", "base_item": "Expansion", "item_type": "Expansion", "properties": []}
        self.assertFalse(should_include_item(entry, "unique"))

    def test_include_item_with_properties_despite_expansion_base(self):
        entry = {"display_name": "Something", "base_item": "Expansion", "item_type": "Expansion", "properties": [{"resolved_text": "+5 str"}]}
        self.assertTrue(should_include_item(entry, "unique"))

    def test_runeword_excluded_if_no_content(self):
        entry = {"base_items": ["Expansion"], "runes": [], "properties": []}
        self.assertFalse(should_include_item(entry, "runeword"))

    def test_runeword_included_if_has_runes(self):
        entry = {"base_items": [], "runes": ["El"], "properties": []}
        self.assertTrue(should_include_item(entry, "runeword"))


class TestAlignSetMemberComparisons(unittest.TestCase):
    def test_pads_shorter_members(self):
        members = [
            {"comparison": {"stat_rows": [{"label": "A", "old": "1", "new": "2", "status": "changed"}], "property_rows": []}},
            {"comparison": {"stat_rows": [], "property_rows": []}},
        ]
        align_set_member_comparisons(members)
        self.assertEqual(1, len(members[0]["comparison"]["aligned_stat_rows"]))
        self.assertEqual(1, len(members[1]["comparison"]["aligned_stat_rows"]))
        self.assertTrue(members[1]["comparison"]["aligned_stat_rows"][0]["is_spacer"])

    def test_row_count_consistent(self):
        members = [
            {"comparison": {"stat_rows": [{"label": "X", "old": "", "new": "v", "status": "added"}] * 3, "property_rows": []}},
            {"comparison": {"stat_rows": [], "property_rows": []}},
        ]
        align_set_member_comparisons(members)
        self.assertEqual(members[0]["comparison"]["row_count"], members[1]["comparison"]["row_count"])


class TestBaseItemComparisonContext(unittest.TestCase):
    def _item(self, level=10, level_req=5, str_req=20, dex_req=10, sockets=2,
               defense_min=10, defense_max=30, block=0, speed=0, speed_label="Normal",
               damage_min=None, damage_max=None, two_handed_only=False,
               inherent_stats=None, auto_prefix_summary=None, quality_bonus_summary=None):
        return {
            "level": level, "level_req": level_req, "str_req": str_req, "dex_req": dex_req,
            "sockets": sockets, "defense_min": defense_min, "defense_max": defense_max,
            "block": block, "speed": speed, "speed_label": speed_label,
            "damage_min": damage_min, "damage_max": damage_max,
            "two_hand_damage_min": None, "two_hand_damage_max": None,
            "two_handed_only": two_handed_only,
            "inherent_stats": inherent_stats or [],
            "auto_prefix_summary": auto_prefix_summary or [],
            "quality_bonus_summary": quality_bonus_summary or [],
        }

    def test_added_when_no_old(self):
        result = base_item_comparison_context(self._item(), None)
        self.assertEqual("added", result["state"])

    def test_unchanged_when_identical(self):
        item = self._item()
        result = base_item_comparison_context(item, item)
        self.assertEqual("unchanged", result["state"])

    def test_modified_stat(self):
        old = self._item(level_req=5)
        new = self._item(level_req=10)
        result = base_item_comparison_context(new, old)
        self.assertEqual("modified", result["state"])
        changed = [r for r in result["stat_rows"] if r["status"] == "changed"]
        self.assertTrue(any(r["label"] == "Req Lvl" for r in changed))


class TestGemRuneComparisonContext(unittest.TestCase):
    def _item(self, level=10, level_req=5, cost=1000, socket_effects=None):
        return {"level": level, "level_req": level_req, "cost": cost, "socket_effects": socket_effects or {}}

    def test_added(self):
        result = gem_rune_comparison_context(self._item(), None)
        self.assertEqual("added", result["state"])

    def test_unchanged(self):
        item = self._item()
        result = gem_rune_comparison_context(item, item)
        self.assertEqual("unchanged", result["state"])

    def test_socket_effect_change(self):
        old = self._item(socket_effects={"Weapon": ["+5 Damage"]})
        new = self._item(socket_effects={"Weapon": ["+10 Damage"]})
        result = gem_rune_comparison_context(new, old)
        self.assertEqual("modified", result["state"])
        weapon_row = next(r for r in result["property_rows"] if r["label"] == "Weapon")
        self.assertEqual("changed", weapon_row["status"])


if __name__ == "__main__":
    unittest.main()
