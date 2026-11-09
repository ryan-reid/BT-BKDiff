import copy
import os
import sys
import unittest
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))
from d2lib.services.skill_comparison import SkillComparisonService
from d2lib.wiki.comparison import skill_card_context
from d2lib.wiki.renderers import WikiRenderer
from d2lib.wiki.generator import WikiContentBuilder
from d2lib.repository import D2Repository


class Repository:
    def __init__(self, tables, strings=None):
        self.tables = tables
        self.strings = strings or {}

    def get_excel_table(self, name):
        return self.tables.get(name, [])

    def get_string(self, key):
        return self.strings.get(key.lower(), key)


class TestSkillComparison(unittest.TestCase):
    def setUp(self):
        self.tables = {
            "skills": [{"skill": "Holy Bolt", "*Id": "101", "charclass": "pal", "skilldesc": "holy bolt",
                        "srvmissile": "holybolt", "reqlevel": "6", "maxlvl": "20",
                        "EDmgSymPerCalc": "skill('Other Skill'.blvl)*par8", "Param8": "50"},
                       {"skill": "Other Skill", "charclass": "pal", "Param1": "4"}],
            "skilldesc": [{"skilldesc": "holy bolt", "str long": "holy_desc", "str name": "holy_name",
                           "dsc3texta1": "Sksyn", "dsc3line2": "76", "dsc3texta2": "MagicSynergy",
                           "dsc3textb2": "other_name", "dsc3calca2": "par8"}],
            "missiles": [{"Missile": "holybolt", "*ID": "55", "pSrvHitFunc": "7", "pSrvDmgFunc": "15",
                          "sHitPar1": "1", "sHitPar2": "3", "HitSubMissile1": "child"},
                         {"Missile": "child", "SubMissile1": "holybolt", "Vel": "10"}],
        }
        self.strings = {"holy_desc": "Damages demons and undead or heals allies", "holy_name": "Holy Bolt",
                        "other_name": "Other Skill", "magicsynergy": "%s: %+d%% Magic Damage per Level"}

    def service(self, current=None, strings=None):
        return SkillComparisonService(Repository(current or self.tables, strings or self.strings),
                                      Repository(self.tables, self.strings))

    def test_missile_only_change_is_readable_and_marks_skill_modified(self):
        current = copy.deepcopy(self.tables)
        current["missiles"][0].update(sHitPar1="0", sHitPar2="0")
        card = self.service(current).compare("holy bolt")
        target = next(f for f in card["facts"] if "targets" in f["label"])
        self.assertEqual(("Demons and undead", "All enemy monster types"), (target["old"], target["new"]))
        self.assertEqual("modified", card["status"])
        self.assertTrue(any("healing" in w["text"] for w in card["warnings"]))

    def test_recursive_missile_diff_and_cycle_termination(self):
        current = copy.deepcopy(self.tables)
        current["missiles"][1]["Vel"] = "22"
        card = self.service(current).compare("holy bolt")
        child = next(r for r in card["records"] if r["id"] == "missiles:child")
        self.assertEqual("modified", child["status"])
        self.assertEqual(1, sum(r["id"] == "missiles:holybolt" for r in card["records"]))
        self.assertEqual(1, card["changed_fields"])

    def test_replacement_links_are_joined_independently(self):
        current = copy.deepcopy(self.tables)
        current["skills"][0]["srvmissile"] = "replacement"
        current["missiles"].append({"Missile": "replacement", "Vel": "5"})
        card = self.service(current).compare("holy bolt")
        rows = {r["id"]: r for r in card["records"]}
        self.assertEqual("added", rows["missiles:replacement"]["status"])
        self.assertEqual("removed", rows["missiles:holybolt"]["status"])

    def test_comment_changes_are_not_gameplay_and_unknown_functions_are_not_decoded(self):
        current = copy.deepcopy(self.tables)
        current["skills"][0]["*calc1 desc"] = "Changed author comment"
        self.assertEqual("unchanged", self.service(current).compare("holy bolt")["status"])
        current["missiles"][0]["pSrvHitFunc"] = "999"
        card = self.service(current).compare("holy bolt")
        target = next(f for f in card["facts"] if "targets" in f["label"])
        self.assertEqual("", target["new"])

    def test_strings_change_without_skilldesc_change_and_missing_strings_are_reported(self):
        card = self.service(strings=dict(self.strings, holy_desc="Damages enemies")).compare("holy bolt")
        self.assertEqual("modified", card["status"])
        self.assertEqual("Damages enemies", card["tooltip"]["new"])
        repo = Repository(self.tables, {"holy_name": "Holy Bolt"})
        card = SkillComparisonService(repo, repo).compare("holy bolt")
        self.assertTrue(any("strings:holy_desc" in m for m in card["new_missing"]))
        self.assertEqual("", card["tooltip"]["new"])

    def test_references_are_not_assumed_to_be_synergies_or_joined_as_damage_sources(self):
        current = copy.deepcopy(self.tables)
        current["skills"][1]["Param1"] = "999"
        card = self.service(current).compare("holy bolt")
        self.assertEqual("unchanged", card["status"])
        self.assertEqual("Other Skill", card["references"][0]["name"])
        self.assertNotIn("skills:other skill", [r["id"] for r in card["records"]])

    def test_summons_stats_and_states_are_joined(self):
        current = copy.deepcopy(self.tables)
        current["skills"][0].update(summon="pet", passivestate="aura", passivestat1="maxhp")
        current.update(monstats=[{"Id": "pet", "MonStatsEx": "petex", "Skill1": "Other Skill"}],
                       monstats2=[{"Id": "petex", "SizeX": "2"}],
                       states=[{"state": "aura", "stat": "maxhp"}],
                       itemstatcost=[{"Stat": "maxhp", "ValShift": "8"}])
        ids = {r["id"] for r in self.service(current).compare("holy bolt")["records"]}
        self.assertTrue({"monstats:pet", "monstats2:petex", "states:aura", "itemstatcost:maxhp", "skills:other skill"} <= ids)

    def test_added_removed_skills_and_zero_are_not_lost(self):
        current = copy.deepcopy(self.tables)
        current["skills"] = [dict(current["skills"][0], mana="0"), {"skill": "New Skill", "charclass": "pal"}]
        pages = self.service(current).class_pages()
        cards = {s["name"]: s for s in pages[0]["skills"]}
        self.assertEqual("removed", cards["Other Skill"]["status"])
        self.assertEqual("added", cards["New Skill"]["status"])
        row = next(r for r in cards["Holy Bolt"]["records"][0]["rows"] if r["label"] == "mana")
        self.assertEqual("0", row["new"])

    def test_card_rendering_escapes_source_and_has_no_legacy_scaling(self):
        card = self.service(strings=dict(self.strings, holy_desc="<script>alert(1)</script>")).compare("holy bolt")
        rendered = WikiRenderer().render("class.html", page={"class_name": "Paladin", "skills": [card]},
                                         item_entries={"skill": [skill_card_context(card)]},
                                         item_section_titles={"skill": "Skills"},
                                         old_label="Retail", new_label="BK", site_root="../../")
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>alert", rendered)
        self.assertNotIn("L20+10", rendered)
        self.assertIn(">Base skill information</div>", rendered)
        self.assertIn(">Formulas</div>", rendered)
        self.assertIn(">Synergies</div>", rendered)
        self.assertNotIn("Source comparison", rendered)
        self.assertIn("data-skill-explorer", rendered)
        self.assertIn('class="family-items-grid"', rendered)
        self.assertIn('class="base-item-card item-index-card"', rendered)
        self.assertIn('id="holy-bolt" data-skill-card', rendered)

    def test_synergies_compare_source_parameters_and_preserve_removals(self):
        current = copy.deepcopy(self.tables)
        current["skills"][0].update(Param8="15", mana="0")
        card = self.service(current).compare("holy bolt")
        self.assertEqual("modified", card["display_status"])
        self.assertIn({"label": "Other Skill", "old": "+50% Magic Damage per Level",
                       "new": "+15% Magic Damage per Level", "status": "changed"}, card["synergy_rows"])
        self.assertEqual("0", next(r["new"] for r in card["facts"] if r["label"].startswith("Base mana")))
        formula, parameter = card["formula_rows"]
        self.assertEqual((formula["old_note"], formula["new_note"]), ("", ""))
        self.assertEqual("unchanged", formula["status"])
        self.assertEqual((parameter["label"], parameter["old"], parameter["new"], parameter["status"]),
                         ("par8", "50", "15", "changed"))
        current["skilldesc"][0].pop("dsc3line2")
        removed = self.service(current).compare("holy bolt")["synergy_rows"][0]
        self.assertEqual((removed["old"], removed["new"]), ("+50% Magic Damage per Level", ""))

    def test_notes_preserve_different_parameter_meanings_on_each_side(self):
        self.tables["skills"][0].update(calc1="ln12", **{"*calc1 desc": "Healing"})
        current = copy.deepcopy(self.tables)
        current["skills"][0].update(calc1="min(5,1+blvl/5", **{"*calc1 desc": "Projectile count"})
        card = self.service(current).compare("holy bolt")
        row = next(r for r in card["formula_rows"] if r["label"] == "calc1")
        self.assertEqual("Healing", row["old_note"])
        self.assertEqual("Projectile count", row["new_note"])
        self.assertEqual("min(5,1+blvl/5", row["new"])

    def test_numeric_links_use_ids_and_legacy_markdown_is_not_read(self):
        self.tables["skills"][0]["srvmissile"] = "55"
        repo = Repository(self.tables, self.strings)
        builder = WikiContentBuilder("unused", "this-path-does-not-exist", "unused")
        builder._repo = repo
        builder._retail_repo = repo
        pages = builder._load_class_pages()
        card = pages[0]["skills"][0]
        self.assertIn("missiles:holybolt", [r["id"] for r in card["records"]])
        self.assertNotIn("effects", card)

    def test_source_provenance_tracks_actual_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            mod = Path(folder, "mod")
            retail = Path(folder, "retail")
            Path(mod, "data/global/excel").mkdir(parents=True)
            Path(retail, "global/excel").mkdir(parents=True)
            Path(mod, "data/global/excel/skills.txt").write_text("", encoding="utf-8")
            source = Path(retail, "global/excel/skills.txt")
            source.write_text("skill\tcharclass\nHoly Bolt\tpal\n", encoding="utf-8")
            repo = D2Repository(str(mod))
            repo.supplemental_path = str(retail)
            service = SkillComparisonService(repo, repo)
            self.assertEqual(str(source).replace("\\", "/"), service.current.sources["skills"])


if __name__ == "__main__":
    unittest.main()
