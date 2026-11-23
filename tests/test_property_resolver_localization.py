import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from d2lib.repository import strip_d2_formatting
from d2lib.services.resolver import PropertyResolverService, load_property_groups


class _FakeResolverRepo:
    def __init__(self, tables=None, strings=None, locale="enUS"):
        self.mpq_path = ""
        self.locale = locale
        self._tables = tables or {}
        self.strings = {k.lower(): v for k, v in (strings or {}).items()}
        self.loaded_paths = []

    def get_excel_table(self, table_name: str):
        return list(self._tables.get(table_name, []))

    def get_string(self, key: str) -> str:
        if not key:
            return ""
        return strip_d2_formatting(self.strings.get(key.lower(), key))

    def load_tsv(self, file_path: str):
        self.loaded_paths.append(file_path)
        return []


def _base_tables():
    return {
        "charstats": [
            {
                "class": "Sorceress",
                "StrAllSkills": "ModStr3d",
                "StrClassOnly": "SorOnly",
                "StrSkillTab1": "StrSklTabItem15",
            },
            {"class": "Expansion"},
            {
                "class": "Amazon",
                "StrAllSkills": "ModStr3a",
                "StrClassOnly": "AmaOnly",
                "StrSkillTab1": "StrSklTabItem1",
            },
        ],
        "skills": [
            {"Id": "36", "skill": "Fire Bolt", "charclass": "sor", "skilldesc": "fire bolt"},
            {"Id": "47", "skill": "Fire Ball", "charclass": "sor", "skilldesc": "fire ball"},
            {"Id": "54", "skill": "Teleport", "charclass": "sor", "skilldesc": "teleport"},
            {"Id": "102", "skill": "Holy Freeze", "charclass": "pal", "skilldesc": "holy freeze"},
        ],
        "skilldesc": [
            {"skilldesc": "fire bolt", "str name": "Skillname37"},
            {"skilldesc": "fire ball", "str name": "Skillname48"},
            {"skilldesc": "teleport", "str name": "Skillname55"},
            {"skilldesc": "holy freeze", "str name": "Skillname103"},
        ],
        "monstats": [
            {"Id": "skeleton1", "*hcIdx": "1", "NameStr": "Skeleton"},
        ],
        "montype": [
            {"type": "undead", "strplur": "MonUndead", "strsing": "MonUndead"},
        ],
        "properties": [
            {"code": "ac", "func1": "1", "stat1": "armorclass", "*Tooltip": "+# Defense"},
            {"code": "pierce", "func1": "1", "stat1": "item_pierce", "*Tooltip": "Piercing Attack"},
            {"code": "red-dmg%", "func1": "1", "stat1": "damageresist", "*Tooltip": "Damage Reduced by #%"},
            {"code": "res-all", "func1": "1", "stat1": "fireresist", "stat2": "lightresist", "stat3": "coldresist", "stat4": "poisonresist", "*Tooltip": "All Resistances +#"},
            {"code": "res-all-max", "func1": "1", "stat1": "maxfireresist", "stat2": "maxlightresist", "stat3": "maxcoldresist", "stat4": "maxpoisonresist"},
            {"code": "all-stats", "func1": "1", "stat1": "strength", "stat2": "energy", "stat3": "dexterity", "stat4": "vitality", "*Tooltip": "+# to all Attributes"},
            {"code": "ac/lvl", "func1": "17", "stat1": "item_armor_perlevel", "*Tooltip": "+# Defense (Based on Character Level)"},
            {"code": "ac/time", "func1": "18", "stat1": "item_armor_bytime"},
            {"code": "howl", "func1": "1", "stat1": "item_howl", "*Tooltip": "Hit Causes Monster to Flee #%"},
            {"code": "freeze", "func1": "1", "stat1": "item_freeze", "*Tooltip": "Freezes Target +#"},
            {"code": "rep-dur", "func1": "17", "stat1": "item_replenish_durability", "*Tooltip": "Repairs 1 durability in # seconds"},
            {"code": "hit-skill", "func1": "15", "stat1": "item_skillonhit"},
            {"code": "aura", "func1": "16", "stat1": "item_aura"},
            {"code": "att-mon%", "func1": "24", "stat1": "attack_vs_montype"},
            {"code": "reanimate", "func1": "24", "stat1": "item_reanimate", "*Tooltip": "Reanimate As: [Returned]"},
            {"code": "charged", "func1": "19", "stat1": "item_charged_skill", "*Tooltip": "Level # [Skill] (#/# Charges)"},
            {"code": "skill", "func1": "22", "stat1": "item_singleskill"},
            {"code": "oskill", "func1": "22", "stat1": "item_nonclassskill"},
            {"code": "skill-rand", "func1": "12", "stat1": "item_singleskill", "*Tooltip": "+# to [Skill] ([Class] only)"},
            {"code": "randclassskill1", "func1": "36", "stat1": "item_addclassskills", "val1": "3", "*Tooltip": "+# to [Class] Skill Levels"},
            {"code": "dmg%", "func1": "7", "*Tooltip": "+#% Enhanced Damage"},
            {"code": "dmg-min", "func1": "5", "*Tooltip": "+# to Minimum Damage"},
            {"code": "dmg-max", "func1": "6", "*Tooltip": "+# to Maximum Damage"},
            {"code": "dmg-cold", "func1": "15", "stat1": "coldmindam", "stat2": "coldmaxdam", "stat3": "coldlength", "*Tooltip": "Adds #-# Cold Damage"},
            {"code": "dmg-pois", "func1": "15", "stat1": "poisonmindam", "stat2": "poisonmaxdam", "stat3": "poisonlength", "*Tooltip": "Adds #-# Poison Damage Over # Seconds"},
            {"code": "sock", "func1": "14", "stat1": "item_numsockets", "*Tooltip": "Socketed (#)"},
            {"code": "indestruct", "func1": "20", "*Tooltip": "Indestructible"},
            {"code": "ethereal", "func1": "23", "*Tooltip": "Ethereal"},
            {"code": "levelreq", "func1": "1", "stat1": "item_levelreq", "*Tooltip": "Required Level: #"},
            {"code": "bloody", "func1": "1", "stat1": "item_extrablood"},
            {"code": "abs-pois/lvl", "func1": "17", "stat1": "item_absorb_pois_perlevel", "*Tooltip": "Absorbs Poison Damage (Based on Character Level)"},
            {"code": "splash", "func1": "15", "stat1": "item_splashonhit"},
            {"code": "dex", "func1": "1", "stat1": "dexterity"},
        ],
        "itemstatcost": [
            {"Stat": "armorclass", "descfunc": "19", "descstrpos": "ModStr1i"},
            {"Stat": "item_pierce", "descfunc": "19", "descstrpos": "ModStr6g"},
            {"Stat": "damageresist", "descfunc": "29", "descstrpos": "ModStr2uPercent"},
            {"Stat": "fireresist", "descfunc": "19", "descstrpos": "ModStr1j", "dgrp": "2", "dgrpfunc": "19", "dgrpstrpos": "strModAllResistances"},
            {"Stat": "lightresist", "descfunc": "19", "descstrpos": "ModStr1l", "dgrp": "2", "dgrpfunc": "19", "dgrpstrpos": "strModAllResistances"},
            {"Stat": "coldresist", "descfunc": "19", "descstrpos": "ModStr1k", "dgrp": "2", "dgrpfunc": "19", "dgrpstrpos": "strModAllResistances"},
            {"Stat": "poisonresist", "descfunc": "19", "descstrpos": "ModStr1n", "dgrp": "2", "dgrpfunc": "19", "dgrpstrpos": "strModAllResistances"},
            {"Stat": "maxfireresist", "descfunc": "19", "descstrpos": "ModStr5u"},
            {"Stat": "maxlightresist", "descfunc": "19", "descstrpos": "ModStr5w"},
            {"Stat": "maxcoldresist", "descfunc": "19", "descstrpos": "ModStr5v"},
            {"Stat": "maxpoisonresist", "descfunc": "19", "descstrpos": "ModStr5y"},
            {"Stat": "strength", "descfunc": "19", "descstrpos": "ModStr1a", "dgrp": "1", "dgrpfunc": "19", "dgrpstrpos": "Moditem2allattrib"},
            {"Stat": "energy", "descfunc": "19", "descstrpos": "ModStr1d", "dgrp": "1", "dgrpfunc": "19", "dgrpstrpos": "Moditem2allattrib"},
            {"Stat": "dexterity", "descfunc": "19", "descval": "1", "descstrpos": "ModStr1b", "dgrp": "1", "dgrpfunc": "19", "dgrpstrpos": "Moditem2allattrib"},
            {"Stat": "vitality", "descfunc": "19", "descstrpos": "ModStr1c", "dgrp": "1", "dgrpfunc": "19", "dgrpstrpos": "Moditem2allattrib"},
            {"Stat": "item_armor_perlevel", "descfunc": "19", "op": "2", "op param": "3", "op base": "level", "descstrpos": "ModStr1i", "descstr2": "ModStre9c"},
            {"Stat": "item_armor_bytime", "descfunc": "17", "descstrpos": "ModStr1i"},
            {"Stat": "item_howl", "descfunc": "5", "descstrpos": "ModStr3u"},
            {"Stat": "item_freeze", "descfunc": "12", "descval": "2", "descstrpos": "ModStr3l"},
            {"Stat": "item_replenish_durability", "descfunc": "11", "descstrpos": "ModStre9t"},
            {"Stat": "item_skillonhit", "descfunc": "15", "descstrpos": "ItemExpansiveChanc1"},
            {"Stat": "item_aura", "descfunc": "16", "descstrpos": "ModitemAura"},
            {"Stat": "attack_vs_montype", "descfunc": "22", "descstrpos": "ModitemAttratvsM"},
            {"Stat": "item_reanimate", "descfunc": "23", "descstrpos": "Moditemreanimas"},
            {"Stat": "item_charged_skill", "descfunc": "24", "descstrpos": "ModStre10d"},
            {"Stat": "item_singleskill", "descfunc": "27", "descstrpos": "ItemModifierClassSkill"},
            {"Stat": "item_nonclassskill", "descfunc": "28", "descstrpos": "ItemModifierNonClassSkill"},
            {"Stat": "item_splashonhit", "descfunc": "15", "descstrpos": "SumSplash"},
        ],
    }


_STRINGS_BY_LOCALE = {
    "enUS": {
        "Sorceress": "Sorceress",
        "Amazon": "Amazon",
        "ModStr3d": "%+d to Sorceress Skill Levels",
        "SorOnly": "(Sorceress Only)",
        "Skillname37": "Fire Bolt",
        "Skillname48": "Fire Ball",
        "Skillname55": "Teleport",
        "Skillname103": "Holy Freeze",
        "Skeleton": "Skeleton",
        "MonUndead": "Undead",
        "ModStr1i": "%+d Defense",
        "ModStr6g": "%+d%% Piercing Attack",
        "ModStr2uPercent": "Physical Damage Received Reduced by %d%%",
        "strModAllResistances": "All Resistances %+d",
        "Moditem2allattrib": "%+d to all Attributes",
        "ModStr5u": "%+d%% to Maximum Fire Resist",
        "ModStr5w": "%+d%% to Maximum Lightning Resist",
        "ModStr5v": "%+d%% to Maximum Cold Resist",
        "ModStr5y": "%+d%% to Maximum Poison Resist",
        "ModStr1b": "%+d to Dexterity",
        "ModStre9c": "(Based on Character Level)",
        "ModStre9d": "%s (Increases During Nighttime)",
        "ModStr3u": "Hit Causes Monster to Flee %+d%%",
        "ModStr3l": "Freezes target",
        "ModStre9t": "Repairs %d durability per second",
        "ModStre9u": "Repairs %d durability in %d seconds",
        "ItemExpansiveChanc1": "%d%% Chance to cast level %d %s on striking",
        "ModitemAura": "Level %d %s Aura When Equipped",
        "ModitemAttratvsM": "%d%% to Attack Rating versus",
        "Moditemreanimas": "%0%% Reanimate as: %1",
        "ModStre10d": "Level %d %s (%d/%d Charges)",
        "ItemModifierClassSkill": "%+d to %s %s",
        "ItemModifierNonClassSkill": "%+d to %s",
        "chronicleItemModifierClassSkillRandom": "%+d to a random %s Skill %s",
        "chronicleRandomClassSkillLevel": "%+d to a Random Class' Skill Levels",
        "chroniclePropertyGroupListHeader": "%s of the following:",
        "strModEnhancedDamage": "%+d%% Enhanced Damage",
        "ModStr1g": "%+d to Minimum Damage",
        "ModStr1f": "%+d to Maximum Damage",
        "strModColdDamage": "%+d cold damage",
        "strModColdDamageRange": "Adds %d-%d cold damage",
        "strskillcoldlengthsingular": "Cold Length: %d second",
        "strskill13": "Cold Length: %d seconds",
        "strModPoisonDamage": "%+d poison damage over %d seconds",
        "strModPoisonDamageRange": "Adds %d-%d poison damage over %d seconds",
        "Socketable": "Socketed (%i)",
        "ModStre9s": "Indestructible",
        "Strethereal": "Ethereal (Cannot be Repaired)",
        "ItemStats1p": "Required Level: %d",
        "ModStr5p": "Extra Bloody",
        "ModStre9r": "%+d Absorbs Poison Damage",
        "SumSplash": "Melee Splash Damage",
    },
    "deDE": {
        "Sorceress": "Zauberin",
        "Amazon": "Amazone",
        "ModStr3d": "%+d zu Zauberinnenfertigkeiten",
        "SorOnly": "(Nur Zauberin)",
        "Skillname37": "Feuerblitz",
        "Skillname48": "Feuerball",
        "Skillname55": "Teleportieren",
        "Skillname103": "Heiliger Frost",
        "Skeleton": "Skelett",
        "MonUndead": "Untote",
        "ModStr1i": "%+d Verteidigung",
        "ModStr6g": "%+d%% durchbohrender Angriff",
        "ModStr2uPercent": "Erlittener physischer Schaden um %d%% verringert",
        "strModAllResistances": "Alle Widerstände %+d",
        "Moditem2allattrib": "%+d zu allen Attributen",
        "ModStr5u": "%+d%% zu max. Feuerwiderstand",
        "ModStr5w": "%+d%% zu max. Blitzwiderstand",
        "ModStr5v": "%+d%% zu max. Kältewiderstand",
        "ModStr5y": "%+d%% zu max. Giftwiderstand",
        "ModStr1b": "%+d zu Geschicklichkeit",
        "ModStre9c": "(Basierend auf Charakterstufe)",
        "ModStre9d": "%s (Nimmt während der Nacht zu.)",
        "ModStr3u": "Treffer schlägt Monster in die Flucht %+d%%",
        "ModStr3l": "Friert das Ziel ein",
        "ModStre9t": "Repariert %d Haltbarkeit pro Sekunde",
        "ModStre9u": "Repariert %d Haltbarkeit alle %d Sek.",
        "ItemExpansiveChanc1": "%d%% Chance, bei einem Angriff Stufe %d %s auszulösen",
        "ModitemAura": "Stufe %d der %s-Aura, wenn getragen.",
        "ModitemAttratvsM": "%d%% zu Angriffswert gegen",
        "Moditemreanimas": "%0%% Wiederbeleben als: %1",
        "ModStre10d": "Stufe %d %s (%d/%d Ladungen)",
        "ItemModifierClassSkill": "%+d zu %s %s",
        "ItemModifierNonClassSkill": "%+d zu %s",
        "chronicleItemModifierClassSkillRandom": "%+d zu einer zufällige %s-Fertigkeit %s",
        "chronicleRandomClassSkillLevel": "%+d zu Fertigkeitsstufen einer zufälligen Klasse",
        "chroniclePropertyGroupListHeader": "%s der Folgenden:",
        "strModEnhancedDamage": "%+d%% erhöhter Schaden",
        "ModStr1g": "%+d zu min. Schaden",
        "ModStr1f": "%+d zu max. Schaden",
        "strModColdDamage": "%+d Kälteschaden",
        "strModColdDamageRange": "Fügt %d-%d Kälteschaden hinzu",
        "strskillcoldlengthsingular": "Dauer der Kälte: %d Sekunde",
        "strskill13": "Dauer der Kälte: %d Sek.",
        "strModPoisonDamage": "%+d Giftschaden über %d Sek.",
        "strModPoisonDamageRange": "Fügt %d-%d Giftschaden über %d Sek. hinzu",
        "Socketable": "Gesockelt (%i)",
        "ModStre9s": "Unzerstörbar",
        "Strethereal": "Ätherisch (Reparatur nicht möglich.)",
        "ItemStats1p": "Benötigte Stufe: %d",
        "ModStr5p": "Besonders blutig",
        "ModStre9r": "%+d absorbiert Giftschaden",
        "SumSplash": "Nahkampfschaden",
    },
    "koKR": {
        "Sorceress": "원소술사",
        "Amazon": "아마존",
        "ModStr3d": "원소술사 기술 레벨 %+d",
        "SorOnly": "(원소술사 전용)",
        "Skillname37": "화염탄",
        "Skillname48": "화염구",
        "Skillname55": "순간이동",
        "Skillname103": "신성한 빙결",
        "Skeleton": "해골",
        "MonUndead": "언데드",
        "ModStr1i": "방어력 %+d",
        "ModStr6g": "관통 공격 %+d%%",
        "ModStr2uPercent": "받는 물리 피해 %d%% 감소",
        "strModAllResistances": "모든 저항 %+d",
        "Moditem2allattrib": "모든 능력치 %+d",
        "ModStr5u": "최대 화염 저항 %+d%%",
        "ModStr5w": "최대 번개 저항 %+d%%",
        "ModStr5v": "최대 냉기 저항 %+d%%",
        "ModStr5y": "최대 독 저항 %+d%%",
        "ModStr1b": "민첩 %+d",
        "ModStre9c": "(캐릭터 레벨에 비례)",
        "ModStre9d": "%s (밤에 증가)",
        "ModStr3u": "적중 시 괴물 도주 %+d%%",
        "ModStr3l": "대상 빙결",
        "ModStre9t": "내구도 %d 회복 (매초)",
        "ModStre9u": "내구도 %d 회복 (%d초마다)",
        "ItemExpansiveChanc1": "타격 시 %d%% 확률로 %d 레벨 %s 시전",
        "ModitemAura": "장착 시 %d 레벨 %s 오라 효과 적용",
        "ModitemAttratvsM": "명중률 %d%% 증가 / 대상 한정:",
        "Moditemreanimas": "처치 시 %0%% 확률로 %1 소생",
        "ModStre10d": "%d 레벨 %s (충전 %d/%d회)",
        "ItemModifierClassSkill": "%+d %s %s",
        "ItemModifierNonClassSkill": "%+d %s",
        "chronicleItemModifierClassSkillRandom": "무작위 %s 기술 %s %+d",
        "chronicleRandomClassSkillLevel": "무작위 직업의 기술 레벨 %+d",
        "chroniclePropertyGroupListHeader": "다음의 %s:",
        "strModEnhancedDamage": "피해 %+d%% 증가",
        "ModStr1g": "최소 피해 %+d",
        "ModStr1f": "최대 피해 %+d",
        "strModColdDamage": "냉기 피해 %+d",
        "strModColdDamageRange": "냉기 피해 %d - %d 추가",
        "strskillcoldlengthsingular": "냉기 지속시간: %d초",
        "strskill13": "냉기 지속시간: %d초",
        "strModPoisonDamage": "독 피해 %+d (%d초에 걸쳐)",
        "strModPoisonDamageRange": "독 피해 %d - %d 추가 (%d초에 걸쳐)",
        "Socketable": "홈 있음 (%i)",
        "ModStre9s": "파괴 불가",
        "Strethereal": "무형 (수리 불가)",
        "ItemStats1p": "요구 레벨: %d",
        "ModStr5p": "잔인한 공격",
        "ModStre9r": "독 피해 흡수 %+d",
        "SumSplash": "근접 스플래시 손상",
    },
}


class TestPropertyResolverLocalization(unittest.TestCase):
    def test_itemstatcost_overrides_english_tooltip_across_locales(self):
        tables = _base_tables()
        expectations = {
            "enUS": {
                "ac": "+150 Defense",
                "pierce": "+33% Piercing Attack",
                "red-dmg%": "Physical Damage Received Reduced by 8%",
                "all-stats": "+10 to all Attributes",
                "res-all": "All Resistances +20",
                "res-all-max": "+5% to Maximum Fire Resist / +5% to Maximum Lightning Resist / +5% to Maximum Cold Resist / +5% to Maximum Poison Resist",
                "ac/lvl": "+1.5 Defense (Based on Character Level)",
                "ac/time": "+12 Defense (Increases During Nighttime)",
                "howl": "Hit Causes Monster to Flee +50%",
                "freeze": "Freezes target +3",
                "rep-dur": "Repairs 1 durability in 20 seconds",
                "hit-skill": "15% Chance to cast level 10 Fire Ball on striking",
                "aura": "Level 12 Holy Freeze Aura When Equipped",
                "att-mon%": "120% to Attack Rating versus Undead",
                "reanimate": "10-50% Reanimate as: Skeleton",
                "charged": "Level 20 Teleport (25/25 Charges)",
                "skill": "+3 to Fire Ball (Sorceress Only)",
                "oskill": "+1 to Teleport",
                "skill-rand": "+3 to a random Sorceress Skill (Sorceress Only)",
                "randclassskill1": "+3 to a Random Class' Skill Levels",
                "dmg%": "+200% Enhanced Damage",
                "cold": "Adds 1-5 cold damage · Cold Length: 1 second",
                "pois": "Adds 10-20 poison damage over 2 seconds",
                "sock": "Socketed (3)",
                "indestruct": "Indestructible",
                "ethereal": "Ethereal (Cannot be Repaired)",
                "levelreq": "Required Level: 65",
                "bloody": "Extra Bloody",
                "abs-pois/lvl": "+0.5 Absorbs Poison Damage (Based on Character Level)",
                "splash": "Melee Splash Damage",
            },
            "deDE": {
                "ac": "+150 Verteidigung",
                "pierce": "+33% durchbohrender Angriff",
                "red-dmg%": "Erlittener physischer Schaden um 8% verringert",
                "all-stats": "+10 zu allen Attributen",
                "res-all": "Alle Widerstände +20",
                "ac/lvl": "+1.5 Verteidigung (Basierend auf Charakterstufe)",
                "howl": "Treffer schlägt Monster in die Flucht +50%",
                "rep-dur": "Repariert 1 Haltbarkeit alle 20 Sek.",
                "reanimate": "10-50% Wiederbeleben als: Skelett",
                "skill": "+3 zu Feuerball (Nur Zauberin)",
                "oskill": "+1 zu Teleportieren",
                "dmg%": "+200% erhöhter Schaden",
                "cold": "Fügt 1-5 Kälteschaden hinzu · Dauer der Kälte: 1 Sekunde",
                "pois": "Fügt 10-20 Giftschaden über 2 Sek. hinzu",
                "sock": "Gesockelt (3)",
                "indestruct": "Unzerstörbar",
                "ethereal": "Ätherisch (Reparatur nicht möglich.)",
                "levelreq": "Benötigte Stufe: 65",
                "bloody": "Besonders blutig",
            },
            "koKR": {
                "ac": "방어력 +150",
                "pierce": "관통 공격 +33%",
                "red-dmg%": "받는 물리 피해 8% 감소",
                "all-stats": "모든 능력치 +10",
                "res-all": "모든 저항 +20",
                "ac/lvl": "방어력 +1.5 (캐릭터 레벨에 비례)",
                "howl": "적중 시 괴물 도주 +50%",
                "rep-dur": "내구도 1 회복 (20초마다)",
                "reanimate": "처치 시 10-50% 확률로 해골 소생",
                "skill": "+3 화염구 (원소술사 전용)",
                "oskill": "+1 순간이동",
                "dmg%": "피해 +200% 증가",
                "cold": "냉기 피해 1 - 5 추가 · 냉기 지속시간: 1초",
                "pois": "독 피해 10 - 20 추가 (2초에 걸쳐)",
                "sock": "홈 있음 (3)",
                "indestruct": "파괴 불가",
                "ethereal": "무형 (수리 불가)",
                "levelreq": "요구 레벨: 65",
                "bloody": "잔인한 공격",
            },
        }
        calls = {
            "ac": ("ac", "", "150", "150"),
            "pierce": ("pierce", "", "33", "33"),
            "red-dmg%": ("red-dmg%", "", "8", "8"),
            "all-stats": ("all-stats", "", "10", "10"),
            "res-all": ("res-all", "", "20", "20"),
            "res-all-max": ("res-all-max", "", "5", "5"),
            "ac/lvl": ("ac/lvl", "", "12", "12"),
            "ac/time": ("ac/time", "2", "12", "12"),
            "howl": ("howl", "", "64", "64"),
            "freeze": ("freeze", "", "3", "3"),
            "rep-dur": ("rep-dur", "5", "", ""),
            "hit-skill": ("hit-skill", "Fire Ball", "15", "10"),
            "aura": ("aura", "Holy Freeze", "12", "12"),
            "att-mon%": ("att-mon%", "undead", "120", "120"),
            "reanimate": ("reanimate", "1", "50", "10"),
            "charged": ("charged", "Teleport", "25", "20"),
            "skill": ("skill", "47", "3", "3"),
            "oskill": ("oskill", "Teleport", "1", "1"),
            "skill-rand": ("skill-rand", "3", "36", "36"),
            "randclassskill1": ("randclassskill1", "", "0", "7"),
            "dmg%": ("dmg%", "", "200", "200"),
            "cold": ("dmg-cold", "25", "1", "5"),
            "pois": ("dmg-pois", "50", "10", "20"),
            "sock": ("sock", "3", "", ""),
            "indestruct": ("indestruct", "", "1", "1"),
            "ethereal": ("ethereal", "", "1", "1"),
            "levelreq": ("levelreq", "", "65", "65"),
            "bloody": ("bloody", "", "1", "1"),
            "abs-pois/lvl": ("abs-pois/lvl", "", "4", "4"),
            "splash": ("splash", "", "1", "1"),
        }

        for locale, expected in expectations.items():
            resolver = PropertyResolverService(_FakeResolverRepo(tables, _STRINGS_BY_LOCALE[locale], locale=locale))
            for case_name, expected_text in expected.items():
                args = calls[case_name]
                actual = resolver.resolve_property(*args)["resolved_text"]
                self.assertEqual(actual, expected_text, f"{locale} {case_name}")

    def test_per_repo_propertygroups_and_localized_group_header(self):
        tables = _base_tables()
        tables["propertygroups"] = [
            {"code": "custom-group", "PickMode": "2", "Prop1": "ac", "ModMin1": "10", "ModMax1": "10", "Prop2": "dmg%", "ModMin2": "25", "ModMax2": "25"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            fallback = os.path.join(tmp, "propertygroups.txt")
            Path(fallback).write_text(
                "code\tPickMode\tProp1\tModMin1\tModMax1\ncustom-group\t1\tdex\t5\t5\n",
                encoding="utf-8",
            )
            repo_with_table = _FakeResolverRepo(tables, _STRINGS_BY_LOCALE["koKR"], locale="koKR")
            groups = load_property_groups(repo_with_table, fallback)
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0]["Prop1"], "ac")
            resolver = PropertyResolverService(repo_with_table, groups)
            dto = resolver.resolve_property("custom-group", "", "1", "1")
            self.assertEqual(dto["resolved_text"], "다음의 1: 방어력 +10 / 피해 +25% 증가")

    def test_tooltip_remains_as_last_resort_fallback_when_itemstatcost_absent(self):
        repo = _FakeResolverRepo(
            tables={"properties": [{"code": "custom-mod", "func1": "1", "*Tooltip": "+# Custom Bonus"}]},
            strings={},
        )
        resolver = PropertyResolverService(repo)
        dto = resolver.resolve_property("custom-mod", "", "5", "10")
        self.assertEqual(dto["resolved_text"], "+5-10 Custom Bonus")
        self.assertEqual(dto["label"], "Custom Bonus")


if __name__ == "__main__":
    unittest.main()
