from __future__ import annotations

import os
import sys
import tempfile
import unittest
from typing import Dict, List

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from d2lib.services.recipes import CubeAnalyzerService, RecipePresentationBuilder
from d2lib.wiki.mediawiki import MediaWikiRenderer


class FrozenRecipeRepo:
    """In-memory D2RepositoryProtocol fake backed purely by frozen test tables and strings."""

    def __init__(self, tables: Dict[str, List[Dict[str, str]]], strings: Dict[str, str], locale: str = "enUS"):
        self._tables = tables
        self.locale = locale
        self.strings = {k.lower(): v for k, v in strings.items()}

    def get_excel_table(self, table_name: str) -> List[Dict[str, str]]:
        return self._tables.get(table_name, [])

    def get_string(self, key: str) -> str:
        if not key:
            return ""
        return self.strings.get(key.lower(), key)

    def load_tsv(self, _file_path: str) -> List[Dict[str, str]]:
        return []


def _frozen_tables() -> Dict[str, List[Dict[str, str]]]:
    return {
        "itemtypes": [
            {"ItemType": "Weapon", "Code": "weap", "RunewordCategory1": "r_mis", "RunewordCategory2": "r_mel"},
            {"ItemType": "Melee Weapon", "Code": "mele", "Equiv1": "weap", "RunewordCategory1": "r_mel"},
            {"ItemType": "Sword", "Code": "swor", "Equiv1": "mele", "UICategory": "sword"},
            {"ItemType": "Bow", "Code": "bow", "Equiv1": "weap", "UICategory": "bows"},
            {"ItemType": "Crossbow", "Code": "xbow", "Equiv1": "weap", "UICategory": "xbows"},
            {"ItemType": "2Handed Melee Weapon", "Code": "2han", "BodyLoc1": "rarm"},
            {"ItemType": "Any Armor", "Code": "armo", "RunewordCategory1": "r_arm"},
            {"ItemType": "Body Armor", "Code": "tors", "Equiv1": "armo", "UICategory": "armor"},
            {"ItemType": "Boots", "Code": "boot", "Equiv1": "armo", "UICategory": "boots"},
            {"ItemType": "Gloves", "Code": "glov", "Equiv1": "armo", "UICategory": "glove"},
            {"ItemType": "Any Shield", "Code": "shld", "Equiv1": "armo", "Equiv2": "seco", "RunewordCategory1": "r_off"},
            {"ItemType": "Miscellaneous", "Code": "misc"},
            {"ItemType": "Merc Equip", "Code": "merc", "Equiv1": "armo", "RunewordCategory1": "r_hel"},
            {"ItemType": "Amulet", "Code": "amul", "Equiv1": "misc", "Equiv2": "merc", "UICategory": "amule"},
            {"ItemType": "Ring", "Code": "ring", "Equiv1": "misc", "Equiv2": "merc", "UICategory": "rings"},
            {"ItemType": "Charm", "Code": "char", "Equiv1": "misc", "UICategory": "charm"},
            {"ItemType": "Small Charm", "Code": "scha", "Equiv1": "char", "UICategory": "charm"},
            {"ItemType": "Large Charm", "Code": "mcha", "Equiv1": "char", "UICategory": "charm"},
            {"ItemType": "Grand Charm", "Code": "lcha", "Equiv1": "char", "UICategory": "charm"},
            {"ItemType": "Socket Filler", "Code": "sock"},
            {"ItemType": "Gem", "Code": "gem", "Equiv1": "sock"},
            {"ItemType": "Ruby Gem", "Code": "gemr", "Equiv1": "gem"},
            {"ItemType": "Emerald Gem", "Code": "geme", "Equiv1": "gem"},
            {"ItemType": "Jewel", "Code": "jewl", "Equiv1": "sock"},
            {"ItemType": "Rune", "Code": "rune", "Equiv1": "sock"},
            {"ItemType": "Special Item", "Code": "spot", "Equiv1": "misc"},
            {"ItemType": "Potion", "Code": "poti", "Equiv1": "misc"},
        ],
        "weapons": [
            {"name": "Two-Handed Sword", "namestr": "2hs", "code": "2hs", "type": "swor", "type2": "2han", "level": "10", "levelreq": "0"},
        ],
        "runes": [
            {"Name": "Runeword1", "complete": "1", "itype1": "shld"},
        ],
        "armor": [
            {"name": "Breast Plate", "namestr": "brs", "code": "brs", "type": "tors", "level": "18", "levelreq": "0"},
        ],
        "misc": [
            {"name": "Amulet", "namestr": "amu", "code": "amu", "type": "amul", "level": "1", "levelreq": "0"},
            {"name": "Ring", "namestr": "rin", "code": "rin", "type": "ring", "level": "1", "levelreq": "0"},
            {"name": "Small Charm", "namestr": "cm1", "code": "cm1", "type": "scha", "level": "1", "levelreq": "0"},
            {"name": "Grand Charm", "namestr": "cm3", "code": "cm3", "type": "lcha", "level": "1", "levelreq": "0"},
            {"name": "Jewel", "namestr": "jew", "code": "jew", "type": "jewl", "level": "1", "levelreq": "0"},
            {"name": "Eth Rune", "namestr": "r05", "code": "r05", "type": "rune", "level": "15", "levelreq": "15"},
            {"name": "Ral Rune", "namestr": "r08", "code": "r08", "type": "rune", "level": "19", "levelreq": "19"},
            {"name": "Amn Rune", "namestr": "r11", "code": "r11", "type": "rune", "level": "25", "levelreq": "25"},
            {"name": "Thul Rune", "namestr": "r10", "code": "r10", "type": "rune", "level": "23", "levelreq": "23"},
            {"name": "Lem Rune", "namestr": "r20", "code": "r20", "type": "rune", "level": "43", "levelreq": "43"},
            {"name": "Perfect Ruby", "namestr": "gpr", "code": "gpr", "type": "gemr", "level": "18", "levelreq": "18"},
            {"name": "Ascended Ruby", "namestr": "gar", "code": "gar", "type": "gemr", "level": "60", "levelreq": "60"},
            {"name": "Standard of Heroes", "namestr": "std", "code": "std", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Divine Standard", "namestr": "dsd", "code": "dsd", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Hellfire Ashes", "namestr": "tds", "code": "tds", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Brick", "namestr": "brk", "code": "brk", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Larzuk Hammer", "namestr": "lmr", "code": "lmr", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Charsi Malus", "namestr": "mls", "code": "mls", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Blood Tablet", "namestr": "bct", "code": "bct", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Thawing Potion", "namestr": "wms", "code": "wms", "type": "poti", "level": "1", "levelreq": "0"},
            {"name": "Eastern Shard", "namestr": "xa2", "code": "xa2", "type": "spot", "level": "1", "levelreq": "0"},
            {"name": "Staff of Kings", "namestr": "msf", "code": "msf", "type": "spot", "quest": "2"},
            {"name": "Horadric Staff", "namestr": "hst", "code": "hst", "type": "spot", "quest": "2"},
        ],
        "uniqueitems": [
            {"index": "Annihilus", "code": "cm1", "prop1": "allskills", "min1": "1", "max1": "1"},
            {"index": "PreCrafted Cold Rupture", "code": "cm3", "prop1": "pierce-immunity-cold", "min1": "300", "max1": "300"},
            {
                "index": "Crafted Cold Rupture",
                "code": "cm3",
                "prop1": "pierce-immunity-cold",
                "min1": "300",
                "max1": "300",
                "prop2": "res-cold",
                "min2": "-70",
                "max2": "-70",
                "prop3": "Gelid-Affix1",
                "min3": "1",
                "max3": "1",
            },
        ],
        "magicprefix": [
            {"Name": "Unused"},
            {"Name": "Gelid", "mod1code": "pierce-cold", "mod1min": "1", "mod1max": "3"},
        ],
        "magicsuffix": [{"Name": "Unused"}],
        "properties": [
            {"code": "lifesteal", "func1": "1", "stat1": "lifedrainmindam"},
            {"code": "red-dmg%", "func1": "1", "stat1": "damageresist"},
            {"code": "res-curse", "func1": "1", "stat1": "curse_resistance"},
            {"code": "hp%", "func1": "1", "stat1": "item_maxhp_percent"},
            {"code": "res-all", "func1": "1", "stat1": "fireresist"},
            {"code": "ethereal", "func1": "1", "stat1": "ethereal"},
            {"code": "sock", "func1": "14", "stat1": "item_numsockets", "*Tooltip": "Socketed (#)"},
            {"code": "corruption1", "func1": "1", "stat1": "corrupted"},
            {"code": "corruption2", "func1": "1", "stat1": "corruptordesc"},
            {"code": "augmented1", "func1": "1", "stat1": "augmented"},
            {"code": "mag%", "func1": "1", "stat1": "item_magicbonus"},
            {"code": "gold%", "func1": "1", "stat1": "item_goldbonus"},
            {"code": "pierce-cold", "func1": "1", "stat1": "passive_cold_pierce"},
            {"code": "pierce-dmg", "func1": "1", "stat1": "passive_dmg_pierce"},
            {"code": "pierce-immunity-cold", "func1": "1", "stat1": "item_pierce_cold_immunity"},
            {"code": "res-cold", "func1": "1", "stat1": "coldresist"},
            {"code": "rep-dur", "func1": "17", "stat1": "item_replenish_durability"},
        ],
        "itemstatcost": [
            {"Stat": "lifedrainmindam", "descfunc": "7", "descval": "1", "descstrpos": "ModStr2l", "descstrneg": "ModStr2l"},
            {"Stat": "damageresist", "descfunc": "2", "descval": "1", "descstrpos": "ModStr2u", "descstrneg": "ModStr2u"},
            {"Stat": "curse_resistance", "descfunc": "2", "descval": "2", "descstrpos": "ModCurseRes", "descstrneg": "ModCurseRes"},
            {"Stat": "item_maxhp_percent", "descfunc": "2", "descval": "1", "descstrpos": "ModMaxLifePct", "descstrneg": "ModMaxLifePct"},
            {"Stat": "fireresist", "descfunc": "2", "descval": "1", "descstrpos": "ModStr2x", "descstrneg": "ModStr2x"},
            {"Stat": "item_magicbonus", "descfunc": "2", "descval": "1", "descstrpos": "ModStr2m", "descstrneg": "ModStr2m"},
            {"Stat": "item_goldbonus", "descfunc": "2", "descval": "1", "descstrpos": "ModStr2n", "descstrneg": "ModStr2n"},
            {"Stat": "passive_cold_pierce", "descfunc": "2", "descval": "1", "descstrpos": "Moditemenrescoldsk", "descstrneg": "Moditemenrescoldsk"},
            {"Stat": "passive_dmg_pierce", "descfunc": "2", "descval": "1", "descstrpos": "ModStrDamPierce", "descstrneg": "ModStrDamPierce"},
            {"Stat": "item_pierce_cold_immunity", "descfunc": "3", "descval": "0", "descstrpos": "ModColdSunder", "descstrneg": "ModColdSunder"},
            {"Stat": "coldresist", "descfunc": "2", "descval": "1", "descstrpos": "ModStrColdRes", "descstrneg": "ModStrColdRes"},
            {"Stat": "item_replenish_durability", "descfunc": "1", "descval": "1", "descstrpos": "ModStre9t", "descstrneg": "ModStre9t"},
            {"Stat": "ethereal"},
            {"Stat": "augmented"},
        ],
        "charstats": [{"class": "Amazon", "str": "20"}],
        # Opaque row IDs (`row_01`, ...) guarantee zero classification reliance on English descriptions.
        "cubemain": [
            {
                "description": "row_01_sup_sock",
                "enabled": "1",
                "input 1": "weap,hiq,nos",
                "input 2": "lmr",
                "output": "useitem",
                "mod 1": "sock",
                "mod 1 min": "4",
                "mod 1 max": "4",
            },
            {
                "description": "row_02_hi_sock",
                "enabled": "1",
                "input 1": "tors,hi,nos",
                "input 2": "lmr",
                "output": "useitem",
                "mod 1": "sock",
                "mod 1 min": "3",
                "mod 1 max": "3",
            },
            {
                "description": "row_03_asc_safety_missing_gem",
                "enabled": "1",
                "input 1": "tors,mag,noe",
                "input 2": "jew",
                "input 3": "r20",
                "input 4": "geg",
                "output": "usetype,crf",
                "mod 1": "hp%",
                "mod 1 min": "10",
                "mod 1 max": "20",
                "mod 2": "res-curse",
                "mod 2 min": "10",
                "mod 2 max": "10",
                "mod 3": "red-dmg%",
                "mod 3 min": "5",
                "mod 3 max": "15",
            },
            {
                "description": "row_04_asc_blood_with_pierce_dmg",
                "enabled": "1",
                "input 1": "weap,mag,noe",
                "input 2": "jew",
                "input 3": "r20",
                "input 4": "gar",
                "input 5": "r05",
                "input 6": "mls",
                "output": "usetype,crf",
                "mod 1": "lifesteal",
                "mod 1 min": "3",
                "mod 1 max": "6",
                "mod 2": "pierce-dmg",
                "mod 2 min": "2",
                "mod 2 max": "5",
                "mod 3": "ethereal",
                "mod 3 min": "1",
                "mod 3 max": "1",
            },
            {
                "description": "row_05_tablet_blood",
                "enabled": "1",
                "input 1": "amul,mag",
                "input 2": "bct",
                "output": "usetype,crf",
                "mod 1": "lifesteal",
                "mod 1 min": "2",
                "mod 1 max": "4",
            },
            {
                "description": "row_06_pierce_mod",
                "enabled": "1",
                "input 1": "ring,mag",
                "input 2": "r20",
                "input 3": "gpr",
                "input 4": "xa2",
                "output": "useitem,pre=1",
                "mod 1": "pierce-cold",
                "mod 1 min": "1",
                "mod 1 max": "3",
            },
            {
                "description": "row_07_pierce_sunder",
                "enabled": "1",
                "input 1": "PreCrafted Cold Rupture",
                "input 2": "r20",
                "input 3": "gpr",
                "input 4": "xa2",
                "output": "Crafted Cold Rupture",
            },
            {
                "description": "row_08_corrupt_2han_parent_brick",
                "enabled": "1",
                "input 1": "weap,rar",
                "input 2": "std",
                "output": "usetype,rar",
                "output b": "brk",
                "mod 1": "corruption1",
                "value": "300",
            },
            {
                "description": "row_09_corrupt_2han_sock",
                "enabled": "1",
                "input 1": "2han,rar",
                "input 2": "std",
                "output": "useitem",
                "mod 1": "corruption2",
                "mod 2": "sock",
                "mod 2 min": "2",
                "mod 2 max": "2",
                "value": "1000",
            },
            {
                "description": "row_10_corrupt_shld_std_brick",
                "enabled": "1",
                "input 1": "shld,uni",
                "input 2": "std",
                "output": "usetype,rar",
                "output b": "brk",
                "mod 1": "corruption2",
                "value": "300",
            },
            {
                "description": "row_10_corrupt_shld_std",
                "enabled": "1",
                "input 1": "shld,uni",
                "input 2": "std",
                "output": "useitem",
                "mod 1": "corruption2",
                "mod 2": "sock",
                "mod 2 min": "1",
                "mod 2 max": "1",
                "value": "1000",
            },
            {
                "description": "row_11_corrupt_shld_dsd_brick",
                "enabled": "1",
                "input 1": "shld,uni",
                "input 2": "dsd",
                "output": "usetype,rar",
                "output b": "dsd",
                "mod 1": "corruption2",
                "value": "300",
            },
            {
                "description": "row_11_corrupt_shld_dsd",
                "enabled": "1",
                "input 1": "shld,uni",
                "input 2": "dsd",
                "output": "useitem",
                "mod 1": "corruption2",
                "mod 2": "sock",
                "mod 2 min": "1",
                "mod 2 max": "1",
                "value": "1000",
            },
            {
                "description": "row_12_corrupt_anni_tds_multi",
                "enabled": "1",
                "input 1": "Annihilus",
                "input 2": "tds",
                "output": "useitem",
                "mod 1": "corruption2",
                "mod 2": "mag%",
                "mod 2 min": "7",
                "mod 2 max": "7",
                "mod 4": "gold%",
                "mod 4 min": "10",
                "mod 4 max": "10",
                "value": "1000",
            },
            {
                "description": "row_13_upgrade_tier",
                "enabled": "1",
                "input 1": "weap,bas,uni",
                "input 2": "mls",
                "output": "useitem,mod,exc",
            },
            {
                "description": "row_14_rune_ladder_eth_potion",
                "enabled": "1",
                "input 1": "r05,qty=3",
                "input 2": "wms",
                "output": "r08",
            },
            {
                "description": "row_15_quest_op28",
                "enabled": "1",
                "input 1": "msf",
                "output": "hst",
                "op": "28",
            },
            {
                "description": "row_16_repair",
                "enabled": "1",
                "input 1": "weap,noe",
                "input 2": "r08",
                "output": "useitem,rep,qty=500",
            },
            {
                "description": "row_17_augment",
                "enabled": "1",
                "input 1": "tors",
                "input 2": "std",
                "output": "useitem",
                "mod 1": "augmented1",
                "mod 2": "mag%",
                "mod 2 min": "15",
                "mod 2 max": "15",
                "mod 3": "gold%",
                "mod 3 min": "30",
                "mod 3 max": "30",
            },
        ],
    }


def _locale_strings(locale: str) -> Dict[str, str]:
    catalogs = {
        "enUS": {
            "LootFilterInferiorRarity": "Inferior",
            "LootFilterNormalQuality": "Normal",
            "LootFilterExceptionalQuality": "Exceptional",
            "LootFilterEliteQuality": "Elite",
            "LootFilterSuperiorRarity": "Superior",
            "LootFilterMagicRarity": "Magic",
            "LootFilterRareRarity": "Rare",
            "LootFilterSetRarity": "Set",
            "LootFilterUniqueRarity": "Unique",
            "strethereal": "Ethereal (Cannot be Repaired)",
            "Socketable": "Socketed (%i)",
            "StrGemX3": "Weapons:",
            "armor": "Armor",
            "shlds": "Shields",
            "r_arm": "Body Armor",
            "r_off": "Offhand",
            "amule": "Amulets",
            "rings": "Rings",
            "charm": "Charms",
            "2han": "2Handed",
            "r05": "Eth Rune",
            "r08": "Ral Rune",
            "r20": "Lem Rune",
            "gpr": "Perfect Ruby",
            "gar": "Ascended Ruby",
            "std": "Standard of Heroes",
            "dsd": "The Divine Standard",
            "tds": "Hellfire Ashes",
            "brk": "Brick",
            "lmr": "Larzuk's Hammer",
            "mls": "Charsi's Malus",
            "bct": "Blood Crafting Tablet",
            "wms": "Thawing Potion",
            "xa2": "Eastern Shard",
            "msf": "Staff of Kings",
            "hst": "Horadric Staff",
            "PreCrafted Cold Rupture": "PreCrafted Cold Rupture",
            "Crafted Cold Rupture": "Crafted Cold Rupture",
            "Annihilus": "Annihilus",
            "Gelid": "Gelid",
            "ModStr2l": "Life Stolen Per Hit",
            "ModStr2u": "Damage Reduced",
            "ModCurseRes": "Curse Resistance",
            "ModMaxLifePct": "Increase Maximum Life",
            "ModStr2x": "All Resistances",
            "ModStr2m": "Better Chance of Getting Magic Items",
            "ModStr2n": "Extra Gold from Monsters",
            "Moditemenrescoldsk": "to Enemy Cold Resistance",
            "ModStrDamPierce": "to Enemy Physical Resistance",
            "ModColdSunder": "Monster Cold Immunity is Sundered",
            "ModStrColdRes": "Cold Resist",
            "ModStre9t": "Repairs Durability",
        },
        "deDE": {
            "LootFilterInferiorRarity": "Minderwertig",
            "LootFilterNormalQuality": "Normal",
            "LootFilterExceptionalQuality": "Außergewöhnlich",
            "LootFilterEliteQuality": "Elite",
            "LootFilterSuperiorRarity": "Hochwertig",
            "LootFilterMagicRarity": "Magisch",
            "LootFilterRareRarity": "Selten",
            "LootFilterSetRarity": "Set",
            "LootFilterUniqueRarity": "Einzigartig",
            "strethereal": "Ätherisch (Reparatur nicht möglich.)",
            "Socketable": "Gesockelt (%i)",
            "StrGemX3": "Waffen:",
            "armor": "Rüstung",
            "shlds": "Schilde",
            "r_arm": "Körperschutz",
            "r_off": "Nebenhand",
            "amule": "Amulette",
            "rings": "Ringe",
            "charm": "Zauber",
            "2han": "Zweihändig",
            "r05": "Eth-Rune",
            "r08": "Ral-Rune",
            "r20": "Lem-Rune",
            "gpr": "Perfekter Rubin",
            "gar": "Aufgestiegener Rubin",
            "std": "Standarte der Helden",
            "dsd": "Der göttliche Standard",
            "tds": "Höllenfeuer Asche",
            "brk": "Ziegel",
            "lmr": "Larzuks Hammer",
            "mls": "Charsis Malus",
            "bct": "Blut-Handwerkstafel",
            "wms": "Auftauelixier",
            "xa2": "Östlicher Splitter",
            "msf": "Stab der Könige",
            "hst": "Horadrim-Stab",
            "PreCrafted Cold Rupture": "Vorgefertigter Kältebruch",
            "Crafted Cold Rupture": "Gefertigter Kältebruch",
            "Annihilus": "Vernichtikus",
            "Gelid": "Eisig",
            "ModStr2l": "Abgesaugtes Leben pro Treffer",
            "ModStr2u": "Schaden reduziert",
            "ModCurseRes": "Fluchwiderstand",
            "ModMaxLifePct": "Maximales Leben erhöhen",
            "ModStr2x": "Alle Widerstände",
            "ModStr2m": "Bessere Chance, magischen Gegenstand zu erhalten",
            "ModStr2n": "Extragold von Monstern",
            "Moditemenrescoldsk": "zu Kältewiderstand des Feindes",
            "ModStrDamPierce": "zu physischem Widerstand des Feindes",
            "ModColdSunder": "Kälteimmunität durchbrochen",
            "ModStrColdRes": "Kältewiderstand",
            "ModStre9t": "Repariert Haltbarkeit",
        },
        "koKR": {
            "LootFilterInferiorRarity": "저급",
            "LootFilterNormalQuality": "보통",
            "LootFilterExceptionalQuality": "특급",
            "LootFilterEliteQuality": "정예",
            "LootFilterSuperiorRarity": "고급",
            "LootFilterMagicRarity": "마법",
            "LootFilterRareRarity": "희귀",
            "LootFilterSetRarity": "세트",
            "LootFilterUniqueRarity": "고유",
            "strethereal": "무형 (수리 불가)",
            "Socketable": "홈 있음 (%i)",
            "StrGemX3": "무기:",
            "armor": "갑옷",
            "shlds": "방패",
            "r_arm": "갑옷",
            "r_off": "보조 무기",
            "amule": "목걸이",
            "rings": "반지",
            "charm": "부적",
            "2han": "양손 무기",
            "r05": "에드 룬",
            "r08": "랄 룬",
            "r20": "렘 룬",
            "gpr": "최상급 루비",
            "gar": "승천한 루비",
            "std": "영웅들의 깃발",
            "dsd": "신성한 표준",
            "tds": "지옥 파이어 재",
            "brk": "벽돌",
            "lmr": "라르주크 망치",
            "mls": "찰시의 말루스",
            "bct": "혈액 제작 석판",
            "wms": "해빙 물약",
            "xa2": "동쪽 조각",
            "msf": "왕의 지팡이",
            "hst": "호라드림의 지팡이",
            "PreCrafted Cold Rupture": "제작 전 냉기 파괴",
            "Crafted Cold Rupture": "제작된 냉기 파괴",
            "Annihilus": "애니힐러스",
            "Gelid": "혹한의",
            "ModStr2l": "적중당 생명력 훔침",
            "ModStr2u": "피해 감소",
            "ModCurseRes": "저주 저항",
            "ModMaxLifePct": "최대 생명력 증가",
            "ModStr2x": "모든 저항",
            "ModStr2m": "마법 아이템 발견 확률 증가",
            "ModStr2n": "괴물에게서 얻는 금화 증가",
            "Moditemenrescoldsk": "적의 냉기 저항 감소",
            "ModStrDamPierce": "적의 물리 저항 감소",
            "ModColdSunder": "괴물의 냉기 면역이 파괴됨",
            "ModStrColdRes": "냉기 저항",
            "ModStre9t": "내구도 회복",
        },
    }
    return catalogs[locale]


class TestRecipesServiceMultiLocale(unittest.TestCase):
    def _build_bundle(self, locale: str):
        repo = FrozenRecipeRepo(_frozen_tables(), _locale_strings(locale), locale=locale)
        analyzer = CubeAnalyzerService(repo)
        raw = analyzer.analyze_raw_recipes(include_removed=False)
        groups = analyzer.analyze_all_recipes()
        pages = RecipePresentationBuilder(analyzer, raw, groups).build()
        return analyzer, raw, groups, pages

    def test_unified_qualifier_hi_hiq_and_misc_item_type_names(self):
        for locale, sup_label, amul_label, ring_label in (
            ("enUS", "Superior", "Amulets", "Rings"),
            ("deDE", "Hochwertig", "Amulette", "Ringe"),
            ("koKR", "고급", "목걸이", "반지"),
        ):
            repo = FrozenRecipeRepo(_frozen_tables(), _locale_strings(locale), locale=locale)
            analyzer = CubeAnalyzerService(repo)
            self.assertEqual(analyzer.resolve_token("weap,hiq,nos"), f"{analyzer.get_item_name('weap')} ({sup_label}, unsocketed)")
            self.assertEqual(analyzer.resolve_token("tors,hi,nos"), f"{analyzer.get_item_name('tors')} ({sup_label}, unsocketed)")
            self.assertEqual(amul_label, analyzer.get_item_name("amul"))
            self.assertEqual(ring_label, analyzer.get_item_name("ring"))
            self.assertIn("mele", analyzer._item_type_ancestors("2han"))
            self.assertIn("weap", analyzer._item_type_ancestors("2han"))

    def test_code_driven_classification_and_cross_locale_invariance(self):
        baseline_counts = None
        for locale in ("enUS", "deDE", "koKR"):
            analyzer, raw, groups, pages = self._build_bundle(locale)
            group_by_id = {g["id"]: g for g in groups}

            # Every group and card count is identical across enUS/deDE/koKR.
            snapshot = (
                {g["id"]: len(g["recipes"]) for g in groups},
                [(s["id"], len(s["rows"])) for s in pages["crafting"]["sections"]],
                [(s["id"], len(s["summaries"])) for s in pages["corruptions"]["sections"]],
                [(f["filter_tags"], f["id"]) for f in pages["pierce"]["families"]],
                [(s["id"], len(s["rows"])) for s in pages["reforge_upgrade"]["sections"]],
            )
            if baseline_counts is None:
                baseline_counts = snapshot
            else:
                self.assertEqual(baseline_counts, snapshot)

            # Ascended Safety with missing gem code 'geg' still classifies under Ascended Safety, NOT Jewel.
            craft_titles = [s["title"] for s in pages["crafting"]["sections"]]
            self.assertIn("Ascended Safety", craft_titles)
            self.assertIn("Ascended Blood", craft_titles)
            self.assertIn("Tablet Blood", craft_titles)
            self.assertFalse(any("Jewel" in t for t in craft_titles))

            # Ascended Blood with pierce-dmg goes to ascended-crafting, NOT pierce-amulets; Ethereal variant from mod.
            self.assertEqual(2, len(group_by_id["ascended-crafting"]["recipes"]))
            self.assertEqual(2, len(group_by_id["pierce-amulets"]["recipes"]))
            asc_blood = next(s for s in pages["crafting"]["sections"] if s["title"] == "Ascended Blood")
            eth_variant = asc_blood["rows"][0]["variants"][0]["variant"]
            self.assertIn(analyzer.state_label("eth"), eth_variant)

            # Eth rune + potion ladder classifies into runes (never false-matched by 'eth').
            self.assertEqual(1, len(group_by_id["runes"]["recipes"]))
            # Quest op=28 classifies into portals-quests.
            self.assertEqual(1, len(group_by_id["portals-quests"]["recipes"]))

            # Raw descriptions remain opaque keys on raw_page, while player pages render generated localized titles.
            self.assertIn("row_14_rune_ladder_eth_potion", [r["description"] for r in pages["raw"]["rows"]])
            rune_row = next(s["rows"][0] for s in pages["materials"]["sections"] if s["id"] == "rune-ladders")
            self.assertNotIn("row_14_rune_ladder_eth_potion", rune_row["description"])
            self.assertIn("\u2192", rune_row["description"])

    def test_corruptions_sections_tags_and_multimod_localization(self):
        expected_sections = {
            "enUS": ("Standard of Heroes or The Divine Standard", "Standard of Heroes", "Hellfire Ashes", "Brick", "Socketed (2)", "Offhand"),
            "deDE": ("Standarte der Helden / Der göttliche Standard", "Standarte der Helden", "Höllenfeuer Asche", "Ziegel", "Gesockelt (2)", "Nebenhand"),
            "koKR": ("영웅들의 깃발 / 신성한 표준", "영웅들의 깃발", "지옥 파이어 재", "벽돌", "홈 있음 (2)", "보조 무기"),
        }
        for locale, (comb_title, std_title, tds_title, brick_lbl, sock2_lbl, offhand_lbl) in expected_sections.items():
            _analyzer, _raw, _groups, pages = self._build_bundle(locale)
            corruptions = pages["corruptions"]
            sections_by_id = {s["id"]: s for s in corruptions["sections"]}
            self.assertIn("either-standard-corruptions", sections_by_id)
            self.assertIn("standard-corruptions", sections_by_id)
            self.assertIn("material-tds", sections_by_id)

            self.assertEqual(comb_title, sections_by_id["either-standard-corruptions"]["title"])
            self.assertEqual(std_title, sections_by_id["standard-corruptions"]["title"])
            self.assertEqual(tds_title, sections_by_id["material-tds"]["title"])

            # shld (Offhand/Nebenhand/보조 무기) must tag as 'shields', NOT 'named-uniques', and merge std+dsd brick details.
            offhand_card = sections_by_id["either-standard-corruptions"]["summaries"][0]
            self.assertIn(offhand_lbl, offhand_card["title"])
            self.assertIn("shields", offhand_card["filter_tags"].split("|"))
            self.assertNotIn("named-uniques", offhand_card["filter_tags"].split("|"))
            brick_detail = offhand_card["outcomes"][0]["detail"]
            self.assertNotIn("corruption2", brick_detail)
            self.assertIn(brick_lbl, brick_detail)
            self.assertIn(_locale_strings(locale)["dsd"], brick_detail)

            # 2han inherits parent Brick from weap via dynamically inferred parents + shows localized Brick & Socketed(2).
            std_card = sections_by_id["standard-corruptions"]["summaries"][0]
            outcome_labels = [o["label"] for o in std_card["outcomes"]]
            self.assertIn(brick_lbl, outcome_labels)
            self.assertIn(sock2_lbl, outcome_labels)

            # tdS Annihilus card tagged as 'charms' and includes BOTH mod 2 (mag%) AND mod 4 (gold%) localized.
            tds_card = sections_by_id["material-tds"]["summaries"][0]
            self.assertIn("charms", tds_card["filter_tags"].split("|"))
            tds_label = tds_card["outcomes"][0]["label"]
            self.assertIn(_locale_strings(locale)["ModStr2m"], tds_label)
            self.assertIn(_locale_strings(locale)["ModStr2n"], tds_label)

            # MediaWiki renderer outputs dynamic localized corruption sections including Hellfire Ashes.
            mw_text = "\n".join(MediaWikiRenderer()._render_recipes_corruptions({"page": corruptions}, {}))
            self.assertIn(f"== {tds_title} ==", mw_text)
            self.assertIn(brick_lbl, mw_text)

    def test_pierce_unique_sunder_and_augment_titles_localized(self):
        for locale in ("enUS", "deDE", "koKR"):
            _analyzer, _raw, _groups, pages = self._build_bundle(locale)
            pierce_rows = pages["pierce"]["families"]
            self.assertEqual(2, len(pierce_rows))
            for row in pierce_rows:
                self.assertEqual("gelid", row["filter_tags"])
                self.assertEqual(_locale_strings(locale)["Gelid"], row["family"])
                self.assertNotIn("Unknown property", row["property"])
            sunder_row = next(r for r in pierce_rows if _locale_strings(locale)["Crafted Cold Rupture"] in r["result"])
            self.assertIn(_locale_strings(locale)["ModColdSunder"], sunder_row["property"])
            self.assertIn(_locale_strings(locale)["ModStrColdRes"], sunder_row["property"])

            # Augments appear condensed in augments section and not duplicated into reforge section.
            sec_by_id = {s["id"]: s for s in pages["reforge_upgrade"]["sections"]}
            self.assertIn("augments", sec_by_id)
            self.assertNotIn("reforge", sec_by_id)
            aug_title = sec_by_id["augments"]["rows"][0]["description"]
            self.assertNotIn("row_17_augment", aug_title)
            self.assertIn(_locale_strings(locale)["ModStr2m"], aug_title)


if __name__ == "__main__":
    unittest.main()
