import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from d2lib.repository import strip_d2_formatting
from d2lib.services.mechanics import MechanicsAnalyzerService
from d2lib.services.references import REFERENCE_GROUPS, ReferenceAnalyzerService
from d2lib.services.resolver import PropertyResolverService


class _FakeRepo:
    def __init__(self, tables: dict, strings: dict | None = None):
        self.mpq_path = ""
        self._tables = tables
        self.strings = {k.lower(): v for k, v in (strings or {}).items()}

    def get_excel_table(self, table_name: str):
        return list(self._tables.get(table_name, []))

    def get_string(self, key: str) -> str:
        if not key:
            return ""
        return strip_d2_formatting(self.strings.get(key.lower(), key))

    def load_tsv(self, file_path: str):
        return []


class TestReferenceAndMechanicsLocalization(unittest.TestCase):
    def test_fixed_reference_columns_and_localization(self):
        tables = {
            "charstats": [
                {"class": "Amazon", "StrAllSkills": "ModStr3a", "StrClassOnly": "AmaOnly"},
                {"class": "Sorceress", "StrAllSkills": "ModStr3d", "StrClassOnly": "SorOnly"},
            ],
            "monstats": [
                {"Id": "roguehire", "*hcIdx": "271", "NameStr": "Rogue", "MonStatsEx": "rogue1", "MonProp": ""},
                {"Id": "fallenshaman1", "*hcIdx": "18", "NameStr": "FallenShaman", "MonStatsEx": "fallshaman", "MonProp": "FallenShaman"},
            ],
            "weapons": [
                {"code": "hbw", "name": "Hunter's Bow", "namestr": "hbw"},
            ],
            "armor": [],
            "misc": [
                {"code": "rin", "name": "Ring", "namestr": "rin"},
            ],
            "skills": [
                {"skill": "Fire Arrow", "charclass": "ama", "skilldesc": "fire arrow", "srvstfunc": "1"},
            ],
            "skilldesc": [
                {"skilldesc": "fire arrow", "str name": "Skillname8", "desctexta1": "StrSkill1", "desccalca1": "10", "desctexta2": "StrSkill2", "desccalca2": "20"},
            ],
            "shrines": [
                {
                    "Name": "Gem Shrine",
                    "*Shrine Type": "Gem",
                    "*Effect": "Upgrade a gem",
                    "Code": "18",
                    "Arg0": "1",
                    "Arg1": "2",
                    "Duration in frames": "3000",
                    "reset time in minutes": "5",
                    "rarity": "3",
                    "StringName": "ShrId18",
                    "StringPhrase": "ShrMsg18",
                    "LevelMin": "1",
                }
            ],
            "hireling": [
                {
                    "Hireling": "Rogue Scout",
                    "Act": "1",
                    "Difficulty": "2",
                    "HireDesc": "strhirespecial1",
                    "Version": "100",
                    "Id": "2",
                    "Class": "271",
                    "Level": "36",
                    "Gold": "1500",
                    "Skill1": "Fire Arrow",
                }
            ],
            "monlvl": [
                {"Level": "85", "L-AC": "10", "L-TH": "20", "L-HP": "30", "AC(H)": "100", "TH(H)": "200", "HP(H)": "300"},
            ],
            "npc": [
                {"npc": "Charsi", "buy mult": "100", "sell mult": "50", "rep mult": "25"},
            ],
            "gamble": [
                {"name": "ring", "code": "rin"},
            ],
            "inventory": [
                {"class": "Amazon", "invLeft": "320"},
            ],
            "states": [
                {"state": "freeze", "*ID": "1", "group": "2"},
            ],
            "overlay": [
                {"overlay": "frozen", "Filename": "frz", "version": "100", "*Frames": "16"},
            ],
            "monpreset": [
                {"Act": "1", "Place": "fallenshaman1"},
            ],
            "objects": [
                {"Name": "CairnStone", "*ID": "17", "Class": "CairnStone", "Token": "C0"},
            ],
            "missiles": [
                {"Missile": "firearrow", "*ID": "9", "Skill": "Fire Arrow"},
            ],
            "monseq": [
                {"sequence": "bearattack", "mode": "A1", "frame": "4", "dir": "1", "event": "1"},
            ],
            "superuniques": [
                {"Name": "Bishibosh", "Class": "fallenshaman1", "Mod1": "8"},
            ],
            "monstats2": [
                {"Id": "fallshaman", "Height": "3"},
            ],
            "monprop": [
                {"Id": "FallenShaman", "prop1": "res-fire", "min1": "25", "max1": "25"},
            ],
        }
        strings_de = {
            "Amazon": "Amazone",
            "Sorceress": "Zauberin",
            "Rogue": "[fs]Jägerin",
            "FallenShaman": "Gefallenen-Schamane",
            "rin": "Der Ring",
            "ShrId18": "Edelstein-Schrein",
            "ShrMsg18": "Ein wundervoller Edelstein!",
            "Skillname8": "Feuerpfeil",
            "StrSkill1": "Feuerschaden",
            "StrSkill2": "Angriffswert",
            "strhirespecial1": "Feuerpfeil",
            "strCreateGameNightmareText": "Qual",
            "Bishibosh": "Bishibosh DE",
            "res-fire": "Feuer-Widerstand",
            "ModStr1a": "%+d%% Feuer-Widerstand",
        }
        repo = _FakeRepo(tables, strings_de)
        service = ReferenceAnalyzerService(repo, PropertyResolverService(repo))
        pages = {page["slug"]: page for page in service.build_pages(tables.keys())}

        shrines_row = next(s for s in pages["states-shrines"]["sections"] if s["table"] == "shrines")["rows"][0]
        self.assertEqual(shrines_row["label"], "Edelstein-Schrein")
        shrine_fields = {f["label"]: f["value"] for f in shrines_row["fields"]}
        self.assertEqual(shrine_fields["StringName"], "Edelstein-Schrein")
        self.assertEqual(shrine_fields["StringPhrase"], "Ein wundervoller Edelstein!")
        self.assertEqual(shrine_fields["Duration in frames"], "3000")
        self.assertIn("ShrId18", shrines_row["search_text"])

        states_fields = {f["label"]: f["value"] for f in next(s for s in pages["states-shrines"]["sections"] if s["table"] == "states")["rows"][0]["fields"]}
        self.assertEqual(states_fields["*ID"], "1")
        overlay_fields = {f["label"]: f["value"] for f in next(s for s in pages["states-shrines"]["sections"] if s["table"] == "overlay")["rows"][0]["fields"]}
        self.assertEqual(overlay_fields["*Frames"], "16")

        economy = {s["table"]: s["rows"][0] for s in pages["economy"]["sections"]}
        self.assertEqual(economy["hireling"]["label"], "Jägerin · Feuerpfeil · Qual")
        hire_fields = {f["label"]: f["value"] for f in economy["hireling"]["fields"]}
        self.assertEqual(hire_fields["Hireling"], "Jägerin")
        self.assertEqual(hire_fields["Difficulty"], "Qual")
        self.assertEqual(hire_fields["Skill1"], "Feuerpfeil")
        self.assertEqual({f["label"]: f["value"] for f in economy["npc"]["fields"]}["buy mult"], "100")
        self.assertEqual(economy["gamble"]["label"], "Der Ring")
        self.assertEqual(economy["inventory"]["label"], "Amazone")

        monsters = {s["table"]: s["rows"][0] for s in pages["monster-specials"]["sections"] if s["rows"]}
        self.assertEqual({f["label"]: f["value"] for f in monsters["monlvl"]["fields"]}["AC(H)"], "100")
        self.assertEqual(monsters["superuniques"]["label"], "Bishibosh DE")
        self.assertEqual(monsters["monstats2"]["label"], "Gefallenen-Schamane")
        self.assertEqual(monsters["monprop"]["label"], "Gefallenen-Schamane")

        areas = {s["table"]: s["rows"][0] for s in pages["area-structure"]["sections"] if s["rows"]}
        self.assertEqual(areas["monpreset"]["label"], "Act 1 · Gefallenen-Schamane")
        self.assertEqual({f["label"]: f["value"] for f in areas["objects"]["fields"]}["*ID"], "17")

        skills_support = {s["table"]: s["rows"][0] for s in pages["skill-support"]["sections"] if s["rows"]}
        self.assertEqual(skills_support["skills"]["label"], "Feuerpfeil")
        self.assertEqual({f["label"]: f["value"] for f in skills_support["skills"]["fields"]}["charclass"], "Amazone")
        self.assertEqual(skills_support["skilldesc"]["label"], "Feuerpfeil")
        self.assertEqual({f["label"]: f["value"] for f in skills_support["missiles"]["fields"]}["*ID"], "9")
        self.assertEqual({f["label"]: f["value"] for f in skills_support["missiles"]["fields"]}["Skill"], "Feuerpfeil")
        self.assertEqual(skills_support["monseq"]["label"], "bearattack")
        self.assertEqual({f["label"]: f["value"] for f in skills_support["monseq"]["fields"]}["frame"], "4")

        # Sanity check that every table config in REFERENCE_GROUPS was exercised
        configured = {t["name"] for g in REFERENCE_GROUPS for t in g["tables"]}
        self.assertTrue({"shrines", "hireling", "monlvl", "npc", "gamble", "states", "overlay", "monpreset", "objects", "missiles", "monseq"} <= configured)

    def test_mechanics_localizes_difficulty_names_with_fallback(self):
        bk_tables = {
            "experience": [],
            "difficultylevels": [{"Name": "Normal", "ResistPenalty": "0"}, {"Name": "Hell", "ResistPenalty": "-140"}],
        }
        rt_tables = {
            "experience": [],
            "difficultylevels": [{"Name": "Normal", "ResistPenalty": "0"}, {"Name": "Hell", "ResistPenalty": "-100"}],
        }
        bk_repo = _FakeRepo(
            bk_tables,
            {
                "strCreateGameNormalText": "Pain",
                "strCreateGameNightmareText": "Agony",
                "strCreateGameHellText": "Insanity",
            },
        )
        rt_repo = _FakeRepo(rt_tables, {})
        summary = MechanicsAnalyzerService(bk_repo, rt_repo).analyze_mechanics()
        self.assertEqual(len(summary["difficulty_changes"]), 1)
        self.assertEqual(summary["difficulty_changes"][0]["difficulty"], "Insanity")
        self.assertEqual(summary["difficulty_changes"][0]["difficulty_id"], "hell")

        # Falls back cleanly when strCreateGame*Text keys are absent
        fallback_repo = _FakeRepo(bk_tables, {})
        fallback_summary = MechanicsAnalyzerService(fallback_repo, rt_repo).analyze_mechanics()
        self.assertEqual(fallback_summary["difficulty_changes"][0]["difficulty"], "Hell")


if __name__ == "__main__":
    unittest.main()
