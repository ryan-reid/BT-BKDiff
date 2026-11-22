import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from d2lib.repository import strip_d2_formatting
from d2lib.wiki.generator import WikiContentBuilder
from d2lib.wiki.renderers import HtmlWikiRenderer


class _FakeMercRepo:
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


class TestMercenaryProgression(unittest.TestCase):
    def test_growth_units_and_rounding(self):
        source = {
            "Level": "67",
            "HP": "900",
            "HP/Lvl": "30",
            "Defense": "744",
            "Def/Lvl": "23",
            "Dmg-Min": "30",
            "Dmg/Lvl": "6",
            "ResistFire": "100",
            "ResistFire/Lvl": "5",
            "Skill1": "Fire Arrow",
            "Level1": "22",
            "LvlPerLvl1": "10",
            "Chance1": "25",
            "ChancePerLvl1": "2",
        }
        result = WikiContentBuilder._mercenary_stats_at_level(source, 80)
        for field, expected in {
            "HP": "1290",
            "Defense": "1043",
            "Dmg-Min": "39",
            "ResistFire": "116",
            "Level1": "26",
            "Chance1": "31",
        }.items():
            self.assertEqual(result[field], expected)
        self.assertEqual(source["HP"], "900")
        self.assertEqual(WikiContentBuilder._mercenary_stats_at_level({}, 80), {})

    def test_classic_rows_do_not_leak_into_expansion(self):
        builder = WikiContentBuilder("", "", "")
        rows = [
            {
                "Hireling": "Rogue Scout",
                "*SubType": "Fire - Normal",
                "Class": "271",
                "Act": "1",
                "Difficulty": "1",
                "HireDesc": "strhirespecial1",
                "Level": "25",
                "Version": "0",
                "HP": "221",
            },
            {
                "Hireling": "Rogue Scout",
                "*SubType": "Fire - Normal",
                "Class": "271",
                "Act": "1",
                "Difficulty": "1",
                "HireDesc": "strhirespecial1",
                "Level": "67",
                "Version": "100",
                "HP": "900",
            },
        ]
        repo = _FakeMercRepo({"hireling": rows})
        builder._repo = repo
        builder._retail_repo = repo
        data = builder._load_mercenary_data()
        self.assertEqual(len(data["rows"]), 1)
        self.assertEqual(data["rows"][0]["level"], "67")

    def test_growth_only_changes_are_counted(self):
        builder = WikiContentBuilder("", "", "")
        base = {
            "Hireling": "Rogue Scout",
            "*SubType": "Fire - Normal",
            "Class": "271",
            "Act": "1",
            "Difficulty": "1",
            "HireDesc": "strhirespecial1",
            "Level": "67",
            "Version": "100",
            "HP": "900",
            "HP/Lvl": "30",
        }
        builder._repo = _FakeMercRepo({"hireling": [dict(base, **{"HP/Lvl": "40"})]})
        builder._retail_repo = _FakeMercRepo({"hireling": [base]})
        data = builder._load_mercenary_data()
        self.assertEqual(data["rows"][0]["status"], "changed")
        self.assertEqual(data["rows"][0]["changed_fields"], ["HP/Lvl"])

    def test_structured_grouping_unifies_act2_dedupes_act5_and_localizes_ui(self):
        monstats = [
            {"*hcIdx": "271", "NameStr": "Rogue"},
            {"*hcIdx": "338", "NameStr": "DesertMerc"},
            {"*hcIdx": "359", "NameStr": "Iron Wolf"},
            {"*hcIdx": "560", "NameStr": "Barbarian"},
            {"*hcIdx": "561", "NameStr": "Barbarian"},
        ]
        skills = [
            {"skill": "Fire Arrow", "skilldesc": "fire arrow"},
            {"skill": "Jab", "skilldesc": "jab"},
            {"skill": "Prayer", "skilldesc": "prayer"},
            {"skill": "Fire Bolt", "skilldesc": "fire bolt"},
            {"skill": "Bash", "skilldesc": "bash"},
            {"skill": "Frenzy", "skilldesc": "frenzy"},
        ]
        skilldesc = [
            {"skilldesc": "fire arrow", "str name": "Skillname8"},
            {"skilldesc": "jab", "str name": "Skillname11"},
            {"skilldesc": "prayer", "str name": "Skillname100"},
            {"skilldesc": "fire bolt", "str name": "Skillname37"},
            {"skilldesc": "bash", "str name": "Skillname127"},
            {"skilldesc": "frenzy", "str name": "Skillname148"},
        ]
        hireling_rows = [
            # Intentionally unordered + corrupted *SubType comments to prove comment-agnostic grouping
            {
                "Hireling": "Barbarian",
                "*SubType": "Garbage Comment Alpha",
                "Version": "100",
                "Id": "24",
                "Class": "561",
                "Act": "5",
                "Difficulty": "1",
                "Level": "58",
                "HP": "1020",
                "HP/Lvl": "20",
                "Defense": "500",
                "Def/Lvl": "10",
                "Str": "100",
                "Str/Lvl": "8",
                "Dex": "80",
                "Dex/Lvl": "8",
                "AR": "500",
                "AR/Lvl": "10",
                "Dmg-Min": "39",
                "Dmg-Max": "43",
                "Dmg/Lvl": "8",
                "ResistFire": "100",
                "ResistFire/Lvl": "4",
                "ResistCold": "100",
                "ResistCold/Lvl": "4",
                "ResistLightning": "100",
                "ResistLightning/Lvl": "4",
                "ResistPoison": "100",
                "ResistPoison/Lvl": "4",
                "HireDesc": "",
                "Skill1": "Bash",
                "Level1": "10",
                "LvlPerLvl1": "0",
                "Chance1": "50",
                "ChancePerLvl1": "0",
            },
            # Duplicate Act 5 male/female NPC variant with identical stats (Id=25) -> must collapse
            {
                "Hireling": "Barbarian",
                "*SubType": "Garbage Comment Beta",
                "Version": "100",
                "Id": "25",
                "Class": "561",
                "Act": "5",
                "Difficulty": "1",
                "Level": "58",
                "HP": "1020",
                "HP/Lvl": "20",
                "Defense": "500",
                "Def/Lvl": "10",
                "Str": "100",
                "Str/Lvl": "8",
                "Dex": "80",
                "Dex/Lvl": "8",
                "AR": "500",
                "AR/Lvl": "10",
                "Dmg-Min": "39",
                "Dmg-Max": "43",
                "Dmg/Lvl": "8",
                "ResistFire": "100",
                "ResistFire/Lvl": "4",
                "ResistCold": "100",
                "ResistCold/Lvl": "4",
                "ResistLightning": "100",
                "ResistLightning/Lvl": "4",
                "ResistPoison": "100",
                "ResistPoison/Lvl": "4",
                "HireDesc": "",
                "Skill1": "Bash",
                "Level1": "10",
                "LvlPerLvl1": "0",
                "Chance1": "50",
                "ChancePerLvl1": "0",
            },
            # Act 5 Frenzy without HireDesc
            {
                "Hireling": "Barbarian",
                "*SubType": "Ignored",
                "Version": "100",
                "Id": "36",
                "Class": "560",
                "Act": "5",
                "Difficulty": "1",
                "Level": "58",
                "HP": "1020",
                "HP/Lvl": "20",
                "Defense": "500",
                "Def/Lvl": "10",
                "Str": "100",
                "Str/Lvl": "8",
                "Dex": "80",
                "Dex/Lvl": "8",
                "AR": "500",
                "AR/Lvl": "10",
                "Dmg-Min": "39",
                "Dmg-Max": "43",
                "Dmg/Lvl": "8",
                "ResistFire": "100",
                "ResistFire/Lvl": "4",
                "ResistCold": "100",
                "ResistCold/Lvl": "4",
                "ResistLightning": "100",
                "ResistLightning/Lvl": "4",
                "ResistPoison": "100",
                "ResistPoison/Lvl": "4",
                "HireDesc": "",
                "Skill1": "Frenzy",
                "Level1": "10",
                "LvlPerLvl1": "0",
                "Chance1": "50",
                "ChancePerLvl1": "0",
            },
            # Act 3 misspelled Hireling="Eastern Sorceror" must resolve from monstats NameStr="Iron Wolf"
            {
                "Hireling": "Eastern Sorceror",
                "*SubType": "Corrupted*Comment",
                "Version": "100",
                "Id": "15",
                "Class": "359",
                "Act": "3",
                "Difficulty": "1",
                "Level": "49",
                "HP": "534",
                "HP/Lvl": "15",
                "Defense": "400",
                "Def/Lvl": "10",
                "Str": "80",
                "Str/Lvl": "8",
                "Dex": "90",
                "Dex/Lvl": "8",
                "AR": "400",
                "AR/Lvl": "10",
                "Dmg-Min": "18",
                "Dmg-Max": "24",
                "Dmg/Lvl": "8",
                "ResistFire": "100",
                "ResistFire/Lvl": "4",
                "ResistCold": "100",
                "ResistCold/Lvl": "4",
                "ResistLightning": "100",
                "ResistLightning/Lvl": "4",
                "ResistPoison": "100",
                "ResistPoison/Lvl": "4",
                "HireDesc": "strhirespecial7",
                "Skill1": "Fire Bolt",
                "Level1": "10",
                "LvlPerLvl1": "0",
                "Chance1": "50",
                "ChancePerLvl1": "0",
            },
            # Act 2 Normal + Hell Combat/Prayer sharing HireDesc=skillname99 despite different *SubType names
            {
                "Hireling": "Desert Mercenary",
                "*SubType": "Prayer-Normal",
                "Version": "100",
                "Id": "6",
                "Class": "338",
                "Act": "2",
                "Difficulty": "1",
                "Level": "75",
                "HP": "1430",
                "HP/Lvl": "10",
                "Defense": "600",
                "Def/Lvl": "10",
                "Str": "150",
                "Str/Lvl": "8",
                "Dex": "120",
                "Dex/Lvl": "8",
                "AR": "800",
                "AR/Lvl": "10",
                "Dmg-Min": "48",
                "Dmg-Max": "55",
                "Dmg/Lvl": "8",
                "ResistFire": "100",
                "ResistFire/Lvl": "4",
                "ResistCold": "100",
                "ResistCold/Lvl": "4",
                "ResistLightning": "100",
                "ResistLightning/Lvl": "4",
                "ResistPoison": "100",
                "ResistPoison/Lvl": "4",
                "HireDesc": "skillname99",
                "Skill1": "Jab",
                "Skill2": "Prayer",
                "Level1": "10",
                "LvlPerLvl1": "0",
                "Chance1": "50",
                "ChancePerLvl1": "0",
                "Level2": "12",
                "LvlPerLvl2": "0",
                "Chance2": "50",
                "ChancePerLvl2": "0",
            },
            {
                "Hireling": "Desert Mercenary",
                "*SubType": "Comb-Hell",
                "Version": "100",
                "Id": "12",
                "Class": "338",
                "Act": "2",
                "Difficulty": "3",
                "Level": "75",
                "HP": "1430",
                "HP/Lvl": "10",
                "Defense": "600",
                "Def/Lvl": "10",
                "Str": "150",
                "Str/Lvl": "8",
                "Dex": "120",
                "Dex/Lvl": "8",
                "AR": "800",
                "AR/Lvl": "10",
                "Dmg-Min": "48",
                "Dmg-Max": "55",
                "Dmg/Lvl": "8",
                "ResistFire": "100",
                "ResistFire/Lvl": "4",
                "ResistCold": "100",
                "ResistCold/Lvl": "4",
                "ResistLightning": "100",
                "ResistLightning/Lvl": "4",
                "ResistPoison": "100",
                "ResistPoison/Lvl": "4",
                "HireDesc": "skillname99",
                "Skill1": "Jab",
                "Skill2": "Prayer",
                "Level1": "10",
                "LvlPerLvl1": "0",
                "Chance1": "50",
                "ChancePerLvl1": "0",
                "Level2": "12",
                "LvlPerLvl2": "0",
                "Chance2": "50",
                "ChancePerLvl2": "0",
            },
            # Act 1 Rogue
            {
                "Hireling": "Rogue Scout",
                "*SubType": "Unused-Comment",
                "Version": "100",
                "Id": "0",
                "Class": "271",
                "Act": "1",
                "Difficulty": "1",
                "Level": "67",
                "HP": "900",
                "HP/Lvl": "10",
                "Defense": "744",
                "Def/Lvl": "10",
                "Str": "100",
                "Str/Lvl": "8",
                "Dex": "130",
                "Dex/Lvl": "8",
                "AR": "900",
                "AR/Lvl": "10",
                "Dmg-Min": "25",
                "Dmg-Max": "27",
                "Dmg/Lvl": "8",
                "ResistFire": "100",
                "ResistFire/Lvl": "4",
                "ResistCold": "100",
                "ResistCold/Lvl": "4",
                "ResistLightning": "100",
                "ResistLightning/Lvl": "4",
                "ResistPoison": "100",
                "ResistPoison/Lvl": "4",
                "HireDesc": "strhirespecial1",
                "Skill1": "Fire Arrow",
                "Level1": "20",
                "LvlPerLvl1": "0",
                "Chance1": "50",
                "ChancePerLvl1": "0",
            },
        ]
        strings_de = {
            "Rogue": "[fs]Jägerin",
            "DesertMerc": "Wüstensöldner",
            "Iron Wolf": "Eisenwolf",
            "Barbarian": "Barbar",
            "strhirespecial1": "Feuerpfeil",
            "strhirespecial7": "Feuer",
            "skillname99": "Gebet",
            "Skillname8": "Feuerpfeil",
            "Skillname11": "Stoß",
            "Skillname100": "Gebet",
            "Skillname37": "Feuerblitz",
            "Skillname127": "Hieb",
            "Skillname148": "Raserei",
            "strCreateGameNormalText": "Schmerz",
            "strCreateGameNightmareText": "Qual",
            "strCreateGameHellText": "Wahnsinn",
        }

        tables = {"hireling": hireling_rows, "monstats": monstats, "skills": skills, "skilldesc": skilldesc}
        repo = _FakeMercRepo(tables, strings_de)
        builder = WikiContentBuilder("", "", "", locale="deDE")
        builder._repo = repo
        builder._retail_repo = repo
        data = builder._load_mercenary_data()
        # 7 input rows collapse to 6 unique rows (Id=24 & Id=25 merged)
        self.assertEqual(len(data["rows"]), 6)

        builder._write_mercenary_pages(data)
        merc_index = next(p for p in builder.site["pages"] if p["output_path"] == "mercenaries/index.html")
        groups = merc_index["payload"]["groups"]
        # Act 1 -> Act 2 -> Act 3 -> Act 5 order with localized names
        self.assertEqual([g["name"] for g in groups], ["Jägerin", "Wüstensöldner", "Eisenwolf", "Barbar"])
        self.assertEqual([g["act"] for g in groups], [1, 2, 3, 5])

        entries = merc_index["payload"]["entries"]
        # 5 types total: Prayer Normal + Comb-Hell unified under one Act 2 card; Bash + Frenzy separate; 1 Rogue; 1 Iron Wolf
        self.assertEqual(len(entries), 5)

        act2 = next(e for e in entries if e["name"] == "Wüstensöldner")
        self.assertEqual(act2["variant"], "Gebet")
        self.assertEqual(act2["slug"], "desertmerc-skillname99")
        self.assertEqual([o["difficulty"] for o in act2["offers"]], ["Schmerz", "Wahnsinn"])
        # Highest difficulty (3 = Wahnsinn) is selected numerically for preview
        self.assertEqual(act2["preview"]["difficulty"], "Wahnsinn")
        self.assertEqual(act2["preview"]["current_skills"]["Skill1"], "Stoß")
        self.assertEqual(act2["preview"]["current_skills"]["Skill2"], "Gebet")

        act5_variants = [e["variant"] for e in entries if e["name"] == "Barbar"]
        self.assertEqual(sorted(act5_variants), ["Hieb", "Raserei"])

        rendered_index = HtmlWikiRenderer().render_page(merc_index, builder.site)
        self.assertIn("Eisenwolf", rendered_index)
        self.assertNotIn("Eastern Sorceror", rendered_index)
        self.assertIn("Feuerblitz", rendered_index)
        self.assertIn("Schmerz", rendered_index)

        act2_detail = next(
            p for p in builder.site["pages"] if p["output_path"] == "mercenaries/desertmerc-skillname99/index.html"
        )
        rendered_detail = HtmlWikiRenderer().render_page(act2_detail, builder.site)
        # Canonical anchors remain English/difficulty-slug stable across locales
        self.assertIn('id="normal-level-75"', rendered_detail)
        self.assertIn('id="hell-level-75"', rendered_detail)
        self.assertIn("Stoß", rendered_detail)
        self.assertIn("Gebet", rendered_detail)


if __name__ == "__main__":
    unittest.main()
