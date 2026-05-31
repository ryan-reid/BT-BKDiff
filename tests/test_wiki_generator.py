import json
import os
import struct
import sys
import tempfile
import unittest


SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from d2lib.wiki import AreaFarmingDataBuilder, WikiGenerator, WikiRoutes


class TestWikiGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name
        self.item_db = os.path.join(self.root, "item_db")
        self.old_item_db = os.path.join(self.root, "old_item_db")
        self.skill_trees = os.path.join(self.root, "skill_trees")
        self.game_data = os.path.join(self.root, "mod")
        self.retail_data = os.path.join(self.root, "retail")
        self.output = os.path.join(self.root, "wiki")
        self._write_fixture_data()
        self._write_area_fixture_data()
        self._write_report_fixture_data()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_json(self, root, relative_path, payload):
        full_path = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def _write_tsv(self, root, relative_path, fieldnames, rows):
        full_path = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8", newline="") as f:
            f.write("\t".join(fieldnames) + "\n")
            for row in rows:
                f.write("\t".join(str(row.get(field, "")) for field in fieldnames) + "\n")

    def _write_ds1_with_objects(self, root, relative_path, object_ids):
        full_path = os.path.join(root, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        ints = [
            18,  # version
            0,  # stored width, actual width is +1
            0,  # stored height, actual height is +1
            0,  # act
            0,  # substitution method
            0,  # file count
            0,  # wall layers
            1,  # floor layers
            0,  # floor stream cell
            0,  # shadow stream cell
            len(object_ids),
        ]
        for object_id in object_ids:
            ints.extend([2, object_id, 0, 0, 0])
        with open(full_path, "wb") as f:
            f.write(struct.pack(f"<{len(ints)}i", *ints))

    def _write_fixture_data(self):
        uniques = [
            {
                "display_name": "Twin Item",
                "base_item": "First Base",
                "item_type": "Helm",
                "lvl_req": "10",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+10 Damage"}],
            },
            {
                "display_name": "Twin Item",
                "base_item": "Second Base",
                "item_type": "Helm",
                "lvl_req": "20",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+20 Damage"}],
            },
            {
                "display_name": "Twin Item",
                "base_item": "Second Base",
                "item_type": "Helm",
                "lvl_req": "30",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+30 Damage"}],
            },
        ]
        old_uniques = [
            {
                "display_name": "Twin Item",
                "base_item": "First Base",
                "item_type": "Helm",
                "lvl_req": "10",
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+5 Damage"}],
            }
        ]
        sets = [
            {
                "display_name": "Set Blade",
                "base_item": "Short Sword",
                "item_type": "Sword",
                "lvl_req": "12",
                "raw_row": {"set": "Practice Set"},
                "properties": [{"code": "ias", "param": "", "resolved_text": "+10% Increased Attack Speed"}],
            }
        ]
        runewords = [
            {
                "name": "Practice",
                "runes": ["Tal Rune", "Eth Rune"],
                "base_items": ["Melee Weapon"],
                "raw_row": {"Rune1": "r07", "Rune2": "r05"},
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+25% Enhanced Damage"}],
                "rune_properties": [
                    {
                        "rune": "El",
                        "properties": [{"code": "att", "param": "", "resolved_text": "+50 to Attack Rating"}],
                    }
                ],
            }
        ]
        old_runewords = [
            {
                "name": "Practice",
                "runes": ["Tal", "Eth"],
                "base_items": ["Sword"],
                "properties": [{"code": "dmg", "param": "", "resolved_text": "+20% Enhanced Damage"}],
            }
        ]

        self._write_json(self.item_db, "uniques/others/helms.json", uniques)
        self._write_json(self.old_item_db, "uniques/others/helms.json", old_uniques)
        self._write_json(self.item_db, "sets/normal/swords.json", sets)
        self._write_json(self.item_db, "runewords/weapons.json", runewords)
        self._write_json(self.old_item_db, "runewords/weapons.json", old_runewords)

        os.makedirs(self.skill_trees, exist_ok=True)
        with open(os.path.join(self.skill_trees, "amazon_skills.md"), "w", encoding="utf-8") as f:
            f.write(
                "# Amazon Skill Tree\n\n"
                "## Magic Arrow\n\n"
                "> Work in Progress\n\n"
                "| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| Damage | Linear (+1) | +1 | +10 | +20 | +30 | -- |\n"
            )

        excel_root = os.path.join(self.game_data, "data", "global", "excel")
        self._write_tsv(
            excel_root,
            "itemtypes.txt",
            ["ItemType", "Code", "Equiv1", "Equiv2", "MaxSockets1", "MaxSockets2", "MaxSockets3", "StaffMods", "Class"],
            [
                {"ItemType": "Weapon", "Code": "weap"},
                {"ItemType": "Any Armor", "Code": "armo"},
                {"ItemType": "Helm", "Code": "helm", "Equiv1": "armo"},
                {"ItemType": "Melee Weapon", "Code": "mele", "Equiv1": "weap"},
                {"ItemType": "Blunt", "Code": "blun", "Equiv1": "mele"},
                {"ItemType": "Hammer", "Code": "hamm", "Equiv1": "blun", "MaxSockets1": "3", "MaxSockets2": "4", "MaxSockets3": "6"},
                {"ItemType": "Circlet", "Code": "circ", "Equiv1": "helm"},
                {"ItemType": "Pelt", "Code": "pelt", "Equiv1": "armo", "StaffMods": "dru", "Class": "dru"},
            ],
        )
        self._write_tsv(
            excel_root,
            "runes.txt",
            ["Name", "*Rune Name", "complete", "itype1", "itype2", "Rune1", "Rune2", "T1Code1"],
            [
                {"Name": "Runeword1", "*Rune Name": "Practice", "complete": "1", "itype1": "mele", "itype2": "hamm", "Rune1": "r07", "Rune2": "r05", "T1Code1": "dmg"}
            ],
        )
        self._write_tsv(
            excel_root,
            "weapons.txt",
            [
                "name",
                "namestr",
                "code",
                "type",
                "level",
                "levelreq",
                "mindam",
                "maxdam",
                "1or2handed",
                "2handed",
                "2handmindam",
                "2handmaxdam",
                "reqstr",
                "reqdex",
                "gemsockets",
                "normcode",
                "ubercode",
                "ultracode",
                "speed",
                "durability",
                "auto prefix",
            ],
            [
                {
                    "name": "Thunder Maul",
                    "namestr": "7gm",
                    "code": "7gm",
                    "type": "hamm",
                    "level": "85",
                    "levelreq": "65",
                    "2handed": "1",
                    "2handmindam": "65",
                    "2handmaxdam": "255",
                    "reqstr": "253",
                    "gemsockets": "6",
                    "normcode": "7gm",
                    "ubercode": "7gm",
                    "ultracode": "7gm",
                    "speed": "20",
                    "durability": "60",
                }
            ],
        )
        self._write_tsv(
            excel_root,
            "qualityitems.txt",
            [
                "mod1code",
                "mod1param",
                "mod1min",
                "mod1max",
                "mod2code",
                "mod2param",
                "mod2min",
                "mod2max",
                "armor",
                "weapon",
                "shield",
                "scepter",
                "wand",
                "staff",
                "bow",
                "boots",
                "gloves",
                "belt",
            ],
            [{"mod1code": "reduce-ac", "mod1param": "0", "mod1min": "5", "mod1max": "30", "weapon": "1"}],
        )
        self._write_tsv(
            excel_root,
            "properties.txt",
            ["code", "func1", "*Tooltip"],
            [
                {"code": "reduce-ac", "func1": "1", "*Tooltip": "-#% Target Defense"},
                {"code": "cast2", "func1": "1", "*Tooltip": "+#% Faster Cast Rate"},
                {"code": "res-all", "func1": "1", "*Tooltip": "All Resistances +#"},
                {"code": "pierce", "func1": "1", "stat1": "item_pierce", "*Tooltip": "Piercing Attack", "*Min": "Min %", "*Max": "Max %"},
            ],
        )
        self._write_tsv(
            excel_root,
            "automagic.txt",
            ["Name", "group", "mod1code", "mod1min", "mod1max", "itype1"],
            [{"Name": "Piercing Test", "group": "307", "mod1code": "pierce", "mod1min": "33", "mod1max": "33", "itype1": "pelt"}],
        )
        self._write_tsv(
            excel_root,
            "armor.txt",
            [
                "name", "namestr", "code", "type", "level", "levelreq", "minac", "maxac",
                "reqstr", "reqdex", "gemsockets", "normcode", "ubercode", "ultracode",
                "durability", "auto prefix", "magic lvl"
            ],
            [
                {
                    "name": "Diadem", "namestr": "Diadem", "code": "ci3", "type": "circ",
                    "level": "85", "levelreq": "64", "minac": "50", "maxac": "60",
                    "gemsockets": "3", "normcode": "ci3", "ubercode": "ci3", "ultracode": "ci3",
                    "durability": "20", "magic lvl": "18",
                },
                {
                    "name": "Wolf Head", "namestr": "Wolf Head", "code": "dr1", "type": "pelt",
                    "level": "4", "levelreq": "3", "minac": "8", "maxac": "11",
                    "gemsockets": "3", "normcode": "dr1", "ubercode": "dr1", "ultracode": "dr1",
                    "durability": "20", "auto prefix": "307",
                },
            ],
        )
        self._write_tsv(
            excel_root,
            "misc.txt",
            ["name", "namestr", "code", "type", "level", "levelreq", "stackable", "maxstack", "cost", "description", "UICatOverride", "quest"],
            [
                {"name": "Amethyst", "namestr": "Amethyst", "code": "gsw", "type": "gem2", "level": "12", "levelreq": "0", "cost": "500"},
                {"name": "Crafting Tablet", "namestr": "Crafting Tablet", "code": "pct", "type": "misc", "level": "1", "cost": "1000", "UICatOverride": "Crafting"},
                {"name": "Standard of Heroes", "namestr": "Standard of Heroes", "code": "std", "type": "spot", "level": "1", "cost": "1000", "UICatOverride": "uberm"},
                {"name": "Brick", "namestr": "Brick", "code": "brk", "type": "spot", "level": "1", "cost": "1000", "UICatOverride": "Crafting"},
            ],
        )
        self._write_tsv(
            excel_root,
            "gems.txt",
            [
                "name", "code",
                "weaponMod1Code", "weaponMod1Param", "weaponMod1Min", "weaponMod1Max",
                "helmMod1Code", "helmMod1Param", "helmMod1Min", "helmMod1Max",
                "shieldMod1Code", "shieldMod1Param", "shieldMod1Min", "shieldMod1Max",
            ],
            [
                {
                    "name": "Amethyst", "code": "gsw",
                    "weaponMod1Code": "cast2", "weaponMod1Min": "3", "weaponMod1Max": "3",
                    "helmMod1Code": "res-all", "helmMod1Min": "12", "helmMod1Max": "12",
                    "shieldMod1Code": "reduce-ac", "shieldMod1Min": "5", "shieldMod1Max": "5",
                }
            ],
        )
        self._write_tsv(
            excel_root,
            "cubemain.txt",
            [
                "description", "enabled", "input 1", "input 2", "output", "output b",
                "mod 1", "mod 1 param", "mod 1 min", "mod 1 max",
                "mod 2", "mod 2 min", "mod 2 max", "value"
            ],
            [
                {"description": "1 magic amulet + power crafting tablet -> hit power amulet", "enabled": "1", "input 1": "amu,mag", "input 2": "pct", "output": "amu", "mod 1": "mag"},
                {"description": "1 amn + standard gem -> thul rune", "enabled": "1", "input 1": "r11", "input 2": "gsw", "output": "r10"},
                {"description": "Unique Corruptor", "enabled": "1", "input 1": "amu,uni", "input 2": "std", "output": "useitem", "output b": "std", "mod 1": "corruption2", "mod 1 min": "1", "mod 1 max": "1000", "value": "0"},
                {"description": "Brick", "enabled": "1", "input 1": "amu,uni", "input 2": "std", "output": "usetype,rar", "output b": "brk", "mod 1": "corruption2", "mod 1 min": "1001", "mod 1 max": "1001", "value": "300"},
                {"description": "Amulet", "enabled": "1", "input 1": "amu,uni", "input 2": "std", "output": "useitem", "mod 1": "corruption2", "mod 1 min": "1001", "mod 1 max": "1001", "mod 2": "sock", "mod 2 min": "1", "mod 2 max": "1", "value": "1000"},
            ],
        )
        self._write_tsv(
            os.path.join(self.retail_data, "global", "excel"),
            "misc.txt",
            ["name", "namestr", "code", "type", "level", "levelreq", "stackable", "maxstack", "cost", "description", "UICatOverride", "quest"],
            [{"name": "Amethyst", "namestr": "Amethyst", "code": "gsw", "type": "gem2", "level": "12", "cost": "300"}],
        )
        self._write_tsv(
            os.path.join(self.retail_data, "global", "excel"),
            "cubemain.txt",
            ["description", "enabled", "input 1", "input 2", "output", "mod 1", "mod 1 param"],
            [
                {"description": "1 amn + standard gem -> thul rune", "enabled": "1", "input 1": "r11", "input 2": "gsw", "output": "r10"},
                {"description": "removed retail recipe", "enabled": "1", "input 1": "amu", "output": "rin"},
            ],
        )
        self._write_tsv(
            os.path.join(self.retail_data, "global", "excel"),
            "skills.txt",
            ["skill", "Param1"],
            [{"skill": "Magic Arrow", "Param1": "1"}, {"skill": "Removed Skill", "Param1": "1"}],
        )
        self._write_tsv(
            excel_root,
            "skills.txt",
            ["skill", "Param1"],
            [{"skill": "Magic Arrow", "Param1": "2"}, {"skill": "New Skill", "Param1": "1"}],
        )
        self._write_tsv(os.path.join(self.retail_data, "global", "excel"), "missiles.txt", ["Missile", "Vel"], [{"Missile": "arrow", "Vel": "10"}])
        self._write_tsv(excel_root, "missiles.txt", ["Missile", "Vel"], [{"Missile": "arrow", "Vel": "20"}])
        self._write_tsv(os.path.join(self.retail_data, "global", "excel"), "charstats.txt", ["class", "str"], [{"class": "Amazon", "str": "20"}])
        self._write_tsv(excel_root, "charstats.txt", ["class", "str"], [{"class": "Amazon", "str": "25"}])
        self._write_tsv(os.path.join(self.retail_data, "global", "excel"), "properties.txt", ["code", "func1", "*Tooltip"], [{"code": "old-prop", "func1": "1"}])
        self._write_tsv(os.path.join(self.retail_data, "global", "excel"), "itemstatcost.txt", ["Stat", "descfunc"], [{"Stat": "old-stat", "descfunc": "1"}])
        self._write_tsv(excel_root, "itemstatcost.txt", ["Stat", "descfunc"], [{"Stat": "new-stat", "descfunc": "1"}])
        self._write_tsv(os.path.join(self.retail_data, "global", "excel"), "gamble.txt", ["name"], [{"name": "old gamble"}])
        self._write_tsv(excel_root, "gamble.txt", ["name"], [{"name": "new gamble"}])

    def _write_area_fixture_data(self):
        excel_root = os.path.join(self.game_data, "data", "global", "excel")
        level_fields = [
            "Name",
            "*StringName",
            "Id",
            "Act",
            "MonLvl(H)",
            "MonLvlEx(H)",
            "MonDen(H)",
            "MonUMin(H)",
            "MonUMax(H)",
            "SizeX",
            "SizeY",
            "NumMon",
            "nmon1",
            "nmon2",
            "LevelName",
        ]
        self._write_tsv(
            excel_root,
            "levels.txt",
            level_fields,
            [
                {
                    "Name": "Cold Cave",
                    "*StringName": "Cold Cave",
                    "Id": "10",
                    "Act": "0",
                    "MonLvl(H)": "82",
                    "MonLvlEx(H)": "87",
                    "MonDen(H)": "5000",
                    "MonUMin(H)": "10",
                    "MonUMax(H)": "12",
                    "SizeX": "200",
                    "SizeY": "200",
                    "NumMon": "2",
                    "nmon1": "coldbeast",
                    "nmon2": "firebeast",
                    "LevelName": "Cold Cave",
                },
                {
                    "Name": "Fallback Field",
                    "*StringName": "Fallback Field",
                    "Id": "11",
                    "Act": "1",
                    "MonLvl(H)": "82",
                    "MonDen(H)": "1000",
                    "MonUMin(H)": "2",
                    "MonUMax(H)": "4",
                    "SizeX": "200",
                    "SizeY": "200",
                    "NumMon": "1",
                    "nmon1": "stonebeast",
                    "LevelName": "Fallback Field",
                },
                {
                    "Name": "Act 5 - Hell 1",
                    "*StringName": "Abaddon",
                    "Id": "12",
                    "Act": "4",
                    "MonLvl(H)": "87",
                    "MonDen(H)": "900",
                    "MonUMin(H)": "4",
                    "MonUMax(H)": "4",
                    "SizeX": "40",
                    "SizeY": "40",
                    "NumMon": "1",
                    "nmon1": "firebeast",
                    "LevelName": "Hell1",
                },
                {
                    "Name": "Act 3 - Kurast 1",
                    "*StringName": "Lower Kurast",
                    "Id": "79",
                    "Act": "2",
                    "MonLvl(H)": "80",
                    "MonDen(H)": "1200",
                    "MonUMin(H)": "2",
                    "MonUMax(H)": "4",
                    "SizeX": "200",
                    "SizeY": "200",
                    "NumMon": "1",
                    "nmon1": "firebeast",
                    "LevelName": "Lower Kurast",
                },
                {
                    "Name": "Act 1 - Cave 2 Treasure",
                    "*StringName": "Cave Level 2",
                    "Id": "13",
                    "Act": "0",
                    "MonLvl(H)": "80",
                    "MonDen(H)": "900",
                    "MonUMin(H)": "1",
                    "MonUMax(H)": "2",
                    "SizeX": "24",
                    "SizeY": "24",
                    "NumMon": "1",
                    "nmon1": "stonebeast",
                    "LevelName": "Cave Level 2",
                },
            ],
        )

        monster_fields = [
            "Id",
            "NameStr",
            "MinGrp",
            "MaxGrp",
            "Rarity",
            "ResDm(H)",
            "ResMa(H)",
            "ResFi(H)",
            "ResLi(H)",
            "ResCo(H)",
            "ResPo(H)",
        ]
        self._write_tsv(
            excel_root,
            "monstats.txt",
            monster_fields,
            [
                {
                    "Id": "coldbeast",
                    "NameStr": "Cold Beast",
                    "MinGrp": "2",
                    "MaxGrp": "4",
                    "Rarity": "1",
                    "ResCo(H)": "100",
                },
                {
                    "Id": "firebeast",
                    "NameStr": "Fire Beast",
                    "MinGrp": "1",
                    "MaxGrp": "3",
                    "Rarity": "2",
                    "ResFi(H)": "115",
                },
                {
                    "Id": "stonebeast",
                    "NameStr": "Stone Beast",
                    "MinGrp": "1",
                    "MaxGrp": "2",
                    "Rarity": "1",
                    "ResDm(H)": "100",
                },
            ],
        )
        self._write_tsv(
            os.path.join(self.retail_data, "global", "excel"),
            "monstats.txt",
            monster_fields,
            [
                {
                    "Id": "coldbeast",
                    "NameStr": "Cold Beast",
                    "MinGrp": "1",
                    "MaxGrp": "2",
                    "Rarity": "1",
                    "ResCo(H)": "80",
                },
                {
                    "Id": "firebeast",
                    "NameStr": "Fire Beast",
                    "MinGrp": "1",
                    "MaxGrp": "3",
                    "Rarity": "2",
                    "ResFi(H)": "115",
                },
            ],
        )
        maze_fields = ["Name", "Level", "Rooms", "Rooms(N)", "Rooms(H)", "SizeX", "SizeY", "Merge"]
        self._write_tsv(
            excel_root,
            "lvlmaze.txt",
            maze_fields,
            [
                {
                    "Name": "Cold Cave",
                    "Level": "10",
                    "Rooms": "2",
                    "Rooms(H)": "4",
                    "SizeX": "24",
                    "SizeY": "24",
                    "Merge": "500",
                }
            ],
        )
        object_fields = ["Class", "Name", "*Description", "*ID", "InitFn", "PopulateFn"]
        self._write_tsv(
            excel_root,
            "objects.txt",
            object_fields,
            [
                {
                    "Class": "SpecialChest100",
                    "Name": "specialchest",
                    "*Description": "Super Chest",
                    "*ID": "455",
                    "InitFn": "57",
                },
                {
                    "Class": "PlainChest",
                    "Name": "chest",
                    "*Description": "Plain Chest",
                    "*ID": "100",
                    "InitFn": "0",
                },
            ],
        )
        lvlprest_fields = ["Name", "Def", "LevelId", "File1", "File2", "File3", "File4", "File5", "File6"]
        self._write_tsv(
            excel_root,
            "lvlprest.txt",
            lvlprest_fields,
            [
                {
                    "Name": "Cold Cave Chest Room",
                    "Def": "1",
                    "LevelId": "10",
                    "File1": "Act1/Test/Super.ds1",
                },
                {
                    "Name": "Fallback Plain Room",
                    "Def": "2",
                    "LevelId": "11",
                    "File1": "Act1/Test/Plain.ds1",
                },
                {
                    "Name": "Lower Kurast Camp",
                    "Def": "3",
                    "LevelId": "0",
                    "File1": "Act3/Kurast/SlumsCamp.ds1",
                },
                {
                    "Name": "Act 1 - Cave Treasure 2",
                    "Def": "4",
                    "LevelId": "13",
                    "File1": "Act1/Caves/CaveRoom2.ds1",
                },
            ],
        )
        self._write_ds1_with_objects(
            os.path.join(self.game_data, "data", "global", "tiles"),
            os.path.join("Act1", "Test", "Super.ds1"),
            [455],
        )
        self._write_ds1_with_objects(
            os.path.join(self.game_data, "data", "global", "tiles"),
            os.path.join("Act1", "Test", "Plain.ds1"),
            [100],
        )
        self._write_ds1_with_objects(
            os.path.join(self.game_data, "data", "global", "tiles"),
            os.path.join("Act3", "Kurast", "SlumsCamp.ds1"),
            [5],
        )
        self._write_ds1_with_objects(
            os.path.join(self.game_data, "data", "global", "tiles"),
            os.path.join("Act1", "Caves", "CaveRoom2.ds1"),
            [1],
        )
        self._write_json(
            self.game_data,
            "data/local/lng/strings/levels.json",
            [{"Key": "Hell1", "enUS": "Abaddon"}],
        )

    def _write_report_fixture_data(self):
        report_root = os.path.join(self.root, "item_diff_report_retail_bk")
        os.makedirs(os.path.join(report_root, "assets"), exist_ok=True)
        with open(os.path.join(report_root, "index.html"), "w", encoding="utf-8") as f:
            f.write("<!doctype html><title>Item Report</title>")
        with open(os.path.join(report_root, "diff.json"), "w", encoding="utf-8") as f:
            json.dump({"schema": "test"}, f)
        with open(os.path.join(report_root, "assets", "report.css"), "w", encoding="utf-8") as f:
            f.write("body { color: black; }")

    def _generate(self):
        generator = WikiGenerator(
            self.item_db,
            self.skill_trees,
            self.output,
            old_item_db_dir=self.old_item_db,
            old_label="Retail",
            new_label="BKDiablo",
            game_data_dir=self.game_data,
            retail_data_dir=self.retail_data,
        )
        generator.generate()
        return generator

    def test_route_builder_uses_pretty_paths(self):
        self.assertEqual("items/unique/twin-item/index.html", WikiRoutes.item_output_path("unique", "twin-item"))
        self.assertEqual("items/unique/twin-item/", WikiRoutes.route_from_output_path("items/unique/twin-item/index.html"))
        self.assertEqual("../../../", WikiRoutes.site_root_for_output_path("items/unique/twin-item/index.html"))
        self.assertEqual("runewords/index.html", WikiRoutes.runewords_index_output_path())
        self.assertEqual("areas/index.html", WikiRoutes.areas_index_output_path())
        self.assertEqual("bases/index.html", WikiRoutes.bases_index_output_path())
        self.assertEqual("recipes/index.html", WikiRoutes.recipes_index_output_path())
        self.assertEqual("bestiary/index.html", WikiRoutes.bestiary_index_output_path())
        self.assertEqual("misc/index.html", WikiRoutes.misc_index_output_path())
        self.assertEqual("gems-runes/index.html", WikiRoutes.gems_runes_index_output_path())
        self.assertEqual("mechanics/index.html", WikiRoutes.mechanics_output_path())

    def test_generation_writes_pretty_routes_and_manifest(self):
        self._generate()
        expected_paths = [
            os.path.join(self.output, "items", "unique", "twin-item", "index.html"),
            os.path.join(self.output, "items", "unique", "twin-item-second-base", "index.html"),
            os.path.join(self.output, "items", "unique", "twin-item-second-base-2", "index.html"),
            os.path.join(self.output, "items", "index.html"),
            os.path.join(self.output, "runewords", "index.html"),
            os.path.join(self.output, "classes", "amazon", "index.html"),
            os.path.join(self.output, "areas", "index.html"),
            os.path.join(self.output, "bases", "index.html"),
            os.path.join(self.output, "recipes", "index.html"),
            os.path.join(self.output, "bestiary", "index.html"),
            os.path.join(self.output, "misc", "index.html"),
            os.path.join(self.output, "gems-runes", "index.html"),
            os.path.join(self.output, "mechanics", "index.html"),
            os.path.join(self.output, "data", "areas-index.json"),
            os.path.join(self.output, "reports", "index.html"),
            os.path.join(self.output, "reports", "items", "retail-bk", "index.html"),
            os.path.join(self.output, "reports", "items", "retail-bk", "diff.json"),
            os.path.join(self.output, "reports", "items", "retail-bk", "assets", "report.css"),
        ]
        for path in expected_paths:
            self.assertTrue(os.path.exists(path), path)

        with open(os.path.join(self.output, "manifest.json"), "r", encoding="utf-8") as f:
            manifest = json.load(f)
        manifest_paths = {entry["path"] for entry in manifest}
        self.assertIn("items/unique/twin-item/", manifest_paths)
        self.assertIn("items/unique/twin-item-second-base/", manifest_paths)
        self.assertIn("items/", manifest_paths)
        self.assertIn("runewords/", manifest_paths)
        self.assertIn("areas/", manifest_paths)
        self.assertIn("bases/", manifest_paths)
        self.assertIn("recipes/", manifest_paths)
        self.assertIn("bestiary/", manifest_paths)
        self.assertIn("misc/", manifest_paths)
        self.assertIn("gems-runes/", manifest_paths)
        self.assertIn("mechanics/", manifest_paths)
        self.assertIn("reports/", manifest_paths)
        self.assertIn("reports/items/retail-bk/", manifest_paths)

    def test_area_farming_data_schema_and_calculations(self):
        rows = AreaFarmingDataBuilder(self.game_data).build()
        cold_cave = next(row for row in rows if row["display_name"] == "Cold Cave")
        fallback = next(row for row in rows if row["display_name"] == "Fallback Field")
        lower_kurast = next(row for row in rows if row["display_name"] == "Lower Kurast")
        cave_level_2 = next(row for row in rows if row["display_name"] == "Cave Level 2")

        self.assertEqual(
            {
                "display_name",
                "internal_name",
                "level_id",
                "act",
                "area_level",
                "champion_level",
                "unique_level",
                "can_drop_top_tier",
                "monster_density",
                "maze_rooms",
                "maze_chunk_width",
                "maze_chunk_height",
                "maze_chunk_tiles",
                "estimated_area_tiles",
                "maze_source",
                "elite_min",
                "elite_max",
                "elite_avg",
                "possible_immunities",
                "immunity_counts",
                "has_super_chest",
                "super_chest_count",
                "super_chest_sources",
                "monster_pool",
                "farm_score",
                "search_text",
            },
            set(cold_cave.keys()),
        )
        self.assertEqual(87, cold_cave["area_level"])
        self.assertEqual(89, cold_cave["champion_level"])
        self.assertEqual(90, cold_cave["unique_level"])
        self.assertTrue(cold_cave["can_drop_top_tier"])
        self.assertEqual(4, cold_cave["maze_rooms"])
        self.assertEqual(24, cold_cave["maze_chunk_width"])
        self.assertEqual(24, cold_cave["maze_chunk_height"])
        self.assertEqual(576, cold_cave["maze_chunk_tiles"])
        self.assertEqual(2304, cold_cave["estimated_area_tiles"])
        self.assertEqual("lvlmaze", cold_cave["maze_source"])
        self.assertEqual(40000, fallback["estimated_area_tiles"])
        self.assertEqual("levels", fallback["maze_source"])
        self.assertEqual(11, cold_cave["elite_avg"])
        self.assertEqual(["cold", "fire"], cold_cave["possible_immunities"])
        self.assertTrue(cold_cave["has_super_chest"])
        self.assertEqual(1, cold_cave["super_chest_count"])
        self.assertEqual("SpecialChest100", cold_cave["super_chest_sources"][0]["object_class"])
        self.assertFalse(fallback["has_super_chest"])
        self.assertTrue(lower_kurast["has_super_chest"])
        self.assertEqual("Kurast Super Chest Right", lower_kurast["super_chest_sources"][0]["object_class"])
        self.assertTrue(cave_level_2["has_super_chest"])
        self.assertEqual("Act 1 Treasure Room Super Chest", cave_level_2["super_chest_sources"][0]["object_class"])
        self.assertEqual(82, fallback["area_level"])
        self.assertIn("physical", fallback["possible_immunities"])
        self.assertIn("Abaddon", [row["display_name"] for row in rows])
        self.assertNotIn("Hell1", [row["display_name"] for row in rows])
        self.assertGreater(cold_cave["farm_score"], fallback["farm_score"])
        self.assertEqual(
            {"id", "name", "min_group", "max_group", "rarity", "immunities", "resistances"},
            set(cold_cave["monster_pool"][0].keys()),
        )

    def test_item_index_json_schema_and_ordering(self):
        self._generate()
        with open(os.path.join(self.output, "data", "items-index.json"), "r", encoding="utf-8") as f:
            rows = json.load(f)

        self.assertEqual(["Twin Item", "Twin Item", "Twin Item", "Set Blade"], [row["title"] for row in rows])
        self.assertEqual(
            {"title", "href", "family", "status", "item_group", "item_type", "icon_src", "summary", "search_text"},
            set(rows[0].keys()),
        )
        self.assertEqual("modified", rows[0]["status"])
        self.assertEqual("added", rows[1]["status"])
        self.assertEqual("items/unique/twin-item/", rows[0]["href"])

        self.assertNotIn("Practice", [row["title"] for row in rows])

    def test_templates_render_item_and_index_pages(self):
        self._generate()
        with open(os.path.join(self.output, "items", "unique", "twin-item", "index.html"), "r", encoding="utf-8") as f:
            item_page = f.read()
        with open(os.path.join(self.output, "items", "index.html"), "r", encoding="utf-8") as f:
            items_page = f.read()
        with open(os.path.join(self.output, "runewords", "index.html"), "r", encoding="utf-8") as f:
            runewords_index_page = f.read()

        self.assertIn("Twin Item", item_page)
        self.assertIn("Structured diff view using Retail (Old) and BKDiablo (New).", item_page)
        self.assertIn('href="../../../areas/"', item_page)
        self.assertIn('href="../../../reports/"', item_page)
        self.assertIn('data-item-index-url="../data/items-index.json"', items_page)
        self.assertNotIn('data-filter-family="runeword"', items_page)
        self.assertIn("Runewords", runewords_index_page)
        self.assertIn("Practice", runewords_index_page)
        self.assertIn("rune-chip-icon", runewords_index_page)
        self.assertIn("Tal Rune", runewords_index_page)
        self.assertIn("Eth Rune", runewords_index_page)

        with open(os.path.join(self.output, "areas", "index.html"), "r", encoding="utf-8") as f:
            areas_page = f.read()
        self.assertIn('data-area-index-url="../data/areas-index.json"', areas_page)
        self.assertIn("How This Is Calculated", areas_page)
        self.assertIn("Chunk data", areas_page)
        self.assertIn("Super chest potential", areas_page)
        with open(os.path.join(self.output, "data", "areas-index.json"), "r", encoding="utf-8") as f:
            area_rows = json.load(f)
        self.assertEqual("Cold Cave", area_rows[0]["display_name"])
        self.assertTrue(area_rows[0]["has_super_chest"])

        with open(os.path.join(self.output, "reports", "index.html"), "r", encoding="utf-8") as f:
            reports_page = f.read()
        self.assertIn("Item Diff: BKDiablo vs Retail", reports_page)
        self.assertIn("reports/items/retail-bk/", reports_page)

        with open(os.path.join(self.output, "recipes", "index.html"), "r", encoding="utf-8") as f:
            recipes_page = f.read()
        self.assertIn("BK Only", recipes_page)
        self.assertIn("Removed Retail Recipes", recipes_page)
        self.assertIn("Retail Removed", recipes_page)
        self.assertIn("Classic Crafting", recipes_page)
        self.assertIn("Material Upgrades &amp; Conversions", recipes_page)
        self.assertIn("30%", recipes_page)
        self.assertIn("70%", recipes_page)
        self.assertIn("Add 1 socket", recipes_page)

        with open(os.path.join(self.output, "misc", "index.html"), "r", encoding="utf-8") as f:
            misc_page = f.read()
        self.assertIn("Crafting Tablet", misc_page)
        self.assertIn("Crafting Tablets &amp; Materials", misc_page)
        self.assertNotIn("Gems &amp; Skulls", misc_page)

        with open(os.path.join(self.output, "gems-runes", "index.html"), "r", encoding="utf-8") as f:
            gems_runes_page = f.read()
        self.assertIn("Gems &amp; Skulls", gems_runes_page)
        self.assertIn("Amethyst", gems_runes_page)
        self.assertIn("Weapon", gems_runes_page)
        self.assertIn("+3% Faster Cast Rate", gems_runes_page)

        with open(os.path.join(self.output, "bestiary", "index.html"), "r", encoding="utf-8") as f:
            bestiary_page = f.read()
        self.assertIn("Changed", bestiary_page)
        self.assertIn("BK Only", bestiary_page)

        with open(os.path.join(self.output, "mechanics", "index.html"), "r", encoding="utf-8") as f:
            mechanics_page = f.read()
        self.assertIn("Skill & Missile Changes", mechanics_page)
        self.assertIn("magic arrow", mechanics_page)
        self.assertIn("Character, Item, And Economy Systems", mechanics_page)

        with open(os.path.join(self.output, "items", "runeword", "practice", "index.html"), "r", encoding="utf-8") as f:
            runeword_page = f.read()
        self.assertIn("Before", runeword_page)
        self.assertIn("After", runeword_page)
        self.assertIn("rune-chip-icon", runeword_page)
        self.assertIn("Tal Rune", runeword_page)
        self.assertIn("Eth Rune", runeword_page)
        self.assertIn("Bases:", runeword_page)
        self.assertIn("Rune Contributions", runeword_page)
        self.assertIn("Source & Diff", runeword_page)
        self.assertIn("Show technical retail comparison", runeword_page)
        self.assertIn('href="../../../bases/?category=Melee+Weapon&amp;minSockets=2"', runeword_page)
        self.assertIn("+50 to Attack Rating", runeword_page)

        for relative_path, expected_text in [
            (os.path.join("bases", "index.html"), "Base Items"),
            (os.path.join("recipes", "index.html"), "Cube Recipes"),
            (os.path.join("bestiary", "index.html"), "Monster Bestiary"),
            (os.path.join("misc", "index.html"), "Materials"),
            (os.path.join("gems-runes", "index.html"), "Gems &amp; Runes"),
            (os.path.join("mechanics", "index.html"), "Mechanics &amp; Progression"),
        ]:
            with open(os.path.join(self.output, relative_path), "r", encoding="utf-8") as f:
                self.assertIn(expected_text, f.read())

        with open(os.path.join(self.output, "bases", "index.html"), "r", encoding="utf-8") as f:
            bases_page = f.read()
        self.assertIn('data-base-filters', bases_page)
        self.assertIn('id="base-group-filter"', bases_page)
        self.assertIn('id="base-category-filter"', bases_page)
        self.assertIn('id="base-tier-filter"', bases_page)
        self.assertIn('id="base-min-sockets-filter"', bases_page)
        self.assertIn('id="base-roll-filter"', bases_page)
        self.assertIn('id="base-two-handed-filter"', bases_page)
        self.assertNotIn('id="base-auto-roll-filter"', bases_page)
        self.assertNotIn('id="base-superior-filter"', bases_page)
        self.assertIn('data-max-sockets="6"', bases_page)
        self.assertIn('data-type-categories="Hammer|Blunt|Melee Weapon|Weapon"', bases_page)
        self.assertIn('<option value="Hammer">Hammer</option>', bases_page)
        self.assertIn('<option value="Melee Weapon">Melee Weapon</option>', bases_page)
        self.assertIn('data-roll-search="', bases_page)
        self.assertIn("Thunder Maul", bases_page)
        self.assertIn("Two Handed", bases_page)
        self.assertIn("Dam: 65-255", bases_page)
        self.assertNotIn("Dam: 0-0", bases_page)
        self.assertIn("+50% Damage to Undead", bases_page)
        self.assertIn("-5-30% Target Defense", bases_page)
        self.assertIn("Superior", bases_page)
        self.assertIn("Druid staffmods", bases_page)
        self.assertIn("Druid only", bases_page)
        self.assertIn("33% Piercing Attack", bases_page)
        self.assertIn("+18 magic level", bases_page)
        self.assertIn("Base Lvl: 85", bases_page)
        self.assertIn("Req Lvl: 65", bases_page)
        self.assertIn("WSM: 20 (Very Slow)", bases_page)
        self.assertNotIn("<th>Speed/Block</th>", bases_page)

    def test_stale_files_are_removed(self):
        os.makedirs(self.output, exist_ok=True)
        stale_path = os.path.join(self.output, "stale.html")
        with open(stale_path, "w", encoding="utf-8") as f:
            f.write("stale")
        self._generate()
        self.assertFalse(os.path.exists(stale_path))


if __name__ == "__main__":
    unittest.main()
