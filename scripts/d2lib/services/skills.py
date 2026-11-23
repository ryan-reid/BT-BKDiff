from __future__ import annotations
import re
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import (
    D2Repository,
    D2RepositoryProtocol,
    get_class_name_maps,
    resolve_canonical_string,
    resolve_element_name,
    resolve_localized_string,
)
from d2lib.models import SkillTreeDTO, SkillDTO, SkillEffectDTO, SkillSynergyDTO
from d2lib.utils import slugify, strip_markdown

_MANA_SYMBOLS = frozenset({"usmc", "mps", "manc", "manv"})
_DURATION_DESCLINES = frozenset({"12", "31"})
_RANGE_DESCLINES = frozenset({"34", "41", "75"})
_PER_SECOND_DAMAGE_KEYS = frozenset({
    "strskillfiredamageaveragepersecond",
    "strskillcolddamageaveragepersecond",
    "strskillmagicdamageaveragepersecond",
})
_DURATION_TEXT_KEYS = frozenset({
    "strskill13",
    "strskill20",
    "strskill29",
    "strskill62",
    "strskill63",
    "strskill82",
    "strskillcoldlengthsingular",
    "strskillfreezelengthsingular",
    "strskillpoisonlengthsingular",
    "strskillfiredurationsingular",
    "strskilldurationsingular",
    "strskilldurationsingular2",
    "strskilldurationrange",
    "strskillcastingdelaysingular",
    "strskillcastingdelayplural",
    "strskillblazeduration",
    "strskilleffectlengthsingular",
    "strskilleffectlength",
    "hexenemyduration",
    "shadowmasterymiasmadurationincrease",
})
_DISTANCE_TEXT_KEYS = frozenset({
    "strskill18",
    "strskill56",
    "strskill58",
    "strskillradiussingular",
    "strskillrangesingular",
    "eskillbladesofice2",
    "eskillfistsoffire2",
    "shadowmasteryabyssrangeincrease",
    "shadowmasterymiasmarangeincrease",
})
_POISON_DURATION_KEYS = frozenset({"strskillpoisonlengthsingular", "strskill63"})
_COLD_DURATION_KEYS = frozenset({"strskillcoldlengthsingular", "strskill13"})
_PRINTF_TOKEN_RE = re.compile(r"%\+?d")
_PLACEHOLDER_STRIP_RE = re.compile(r"%\+?d\s*[-~]\s*%\+?d|-%\+?d|%\+?d(?:%%|%)?|%s")


class SkillAnalyzerService:
    def __init__(self, repo: D2RepositoryProtocol):
        self.repo = repo
        self.skills = {row.get('skill', '').strip().lower(): row for row in repo.get_excel_table('skills')}
        self.missiles = {row.get('Missile', '').strip().lower(): row for row in repo.get_excel_table('missiles')}
        self.skilldesc = {row.get('skilldesc', '').strip().lower(): row for row in repo.get_excel_table('skilldesc')}
        self.monstats = {row.get('Id', '').strip().lower(): row for row in repo.get_excel_table('monstats') if row.get('Id')}
        self.monlvl = {row.get('Level', '').strip(): row for row in repo.get_excel_table('monlvl') if row.get('Level')}
        _, self.class_map = get_class_name_maps(repo)

    def get_dam_generic(self, s, lvl, prefix):
        try:
            base = int(s.get(prefix, "0") or "0")
            p_root = prefix + "Lev" if prefix.startswith("E") else prefix.replace("Dam", "LevDam")
            add = 0
            for i in range(1, lvl):
                if i < 8: add += int(s.get(f"{p_root}1", "0") or "0")
                elif i < 16: add += int(s.get(f"{p_root}2", "0") or "0")
                elif i < 22: add += int(s.get(f"{p_root}3", "0") or "0")
                elif i < 28: add += int(s.get(f"{p_root}4", "0") or "0")
                else: add += int(s.get(f"{p_root}5", "0") or "0")
            return base + add
        except: return 0

    def get_missile_dam(self, m, lvl, prefix):
        try:
            base = int(m.get(prefix, "0") or "0")
            p_root = prefix + "Lev" if prefix.startswith("E") else prefix.replace("Damage", "LevDam")
            add = 0
            for i in range(1, lvl):
                if i < 8: add += int(m.get(f"{p_root}1", "0") or "0")
                elif i < 16: add += int(m.get(f"{p_root}2", "0") or "0")
                elif i < 22: add += int(m.get(f"{p_root}3", "0") or "0")
                elif i < 28: add += int(m.get(f"{p_root}4", "0") or "0")
                else: add += int(m.get(f"{p_root}5", "0") or "0")
            return base + add
        except: return 0

    def get_synergy_mult(self, s, blvl):
        calc = s.get('DmgSymPerCalc') or s.get('EDmgSymPerCalc')
        if not calc: return 1.0
        try:
            bonus = float(self.resolve_calc(calc, s, blvl, blvl))
            return (100.0 + bonus) / 100.0
        except: return 1.0

    def get_mastery_mult(self, s, lvl):
        etype = s.get('EType', '')
        if not etype: return 1.0
        mastery = self.skills.get(f'passive_{etype}_mastery')
        if not mastery: return 1.0
        try:
            bonus = float(self.get_skill_val(mastery, lvl, lvl, 'accr'))
            return (100.0 + bonus) / 100.0
        except: return 1.0

    def get_skill_val(self, s, lvl, blvl, var, desc_row=None, depth=0):
        if depth > 15: return 0
        try:
            def p(n): return int(s.get(f"Param{n}", "0") or "0")
            ln_m = re.match(r"ln(\d+)", var)
            if ln_m:
                v = ln_m.group(1)
                p1, p2 = (int(v[0]), int(v[1:])) if len(v) >= 2 else (0,0)
                return p(p1) + (lvl - 1) * p(p2)
            dm_m = re.match(r"dm(\d+)", var)
            if dm_m:
                v = dm_m.group(1)
                p1, p2 = (int(v[0]), int(v[1:])) if len(v) >= 2 else (0,0)
                return ((110 * lvl) * (p(p2) - p(1))) // (100 * (lvl + 6)) + p(1)
            if var in ["macr","madm","math"]:
                off = 1 if var=="macr" else (3 if var=="madm" else 5)
                return p(off) + (lvl - 1) * p(off+1)
            if var == "edln":
                elen = int(s.get("ELen", "0") or "0")
                elevlen = sum([int(s.get(f"ELevLen{i}", "0") or "0") for i in range(1, 4)])
                return elen + elevlen * (lvl - 1)
            if var in ["mps", "usmc"]:
                val = max(int(s.get("minmana", "0") or "0"), int(s.get("mana", "0") or "0") + int(s.get("lvlmana", "0") or "0") * (lvl - 1))
                shift = int(s.get("manashift", "8") or "8")
                return val / (2**(8 - shift))
            if var == "toht": return int(s.get("ToHit", "0") or "0") + int(s.get("LevToHit", "0") or "0") * (lvl - 1)
            if var == "pnma": return self.get_dam_generic(s, lvl, "MinDam")
            if var == "pxma": return self.get_dam_generic(s, lvl, "MaxDam")
            if var == "edmn": return self.get_dam_generic(s, lvl, "EMin")
            if var == "edmx": return self.get_dam_generic(s, lvl, "EMax")
            if var == "enma" or var == "exma":
                base = self.get_dam_generic(s, lvl, "EMin" if var=="enma" else "EMax")
                return base * self.get_synergy_mult(s, blvl) * self.get_mastery_mult(s, lvl)
            if var in ["enms", "exms", "edns", "edxs"]:
                base = self.get_dam_generic(s, lvl, "EMin" if var in ["enms","edns"] else "EMax")
                elen = int(s.get("ELen", "0") or "0") + int(s.get("ELevLen1", "0") or "0") * (lvl - 1)
                val = (base * elen) / 256.0
                return val * self.get_synergy_mult(s, blvl) * self.get_mastery_mult(s, lvl)
            if var == "mael": return (self.get_mastery_mult(s, lvl) - 1.0) * 100.0
            if desc_row and var.startswith("m") and len(var)==4:
                m_name = desc_row.get(f"descmissile{var[1]}")
                if m_name:
                    m = self.missiles.get(m_name.lower())
                    if m:
                        m_type = var[2:]
                        if m_type == "nm": return self.get_missile_dam(m, lvl, "MinDamage")
                        if m_type == "xm": return self.get_missile_dam(m, lvl, "MaxDamage")
                        if m_type == "eo": return self.get_dam_generic(m, lvl, "EMin")
                        if m_type == "ey": return self.get_dam_generic(m, lvl, "EMax")
                        if m_type == "rn": return int(m.get("Range", "0") or "0")
            if var.startswith("clc"): return self.resolve_calc(s.get(f"calc{var[3:]}", s.get(f"cltcalc{var[3:]}", "0")), s, lvl, blvl, desc_row, depth + 1)
            if var.startswith("pst") or var.startswith("ps"): return self.resolve_calc(s.get(f"passivecalc{var[3:] if var.startswith('pst') else var[2:]}", "0"), s, lvl, blvl, desc_row, depth + 1)
            if var.startswith("ast"): return self.resolve_calc(s.get(f"aurastatcalc{var[3:]}", "0"), s, lvl, blvl, desc_row, depth + 1)
            if var.startswith("pa"): return s.get(f"Param{var[2:]}", "0")
            if var.startswith("par"): return p(var[3:])
            if var == "accr": return p(1) + (lvl - 1) * p(2)
            return var
        except: return var

    def expand_calc(self, calc, s, lvl, blvl, desc_row=None, depth=0):
        if not calc or depth > 15: return "0"
        calc = str(calc)
        if calc.count('(') > calc.count(')'):
            calc += ')' * (calc.count('(') - calc.count(')'))

        calc = re.sub(
            r"sklvl\('(.*?)'\.(.*?)\.(.*?)\)",
            lambda m: str(self.get_skill_val(
                self.skills.get(m.group(1).lower(), s),
                (lvl if m.group(3) in ["lvl", "0"] else (blvl if m.group(3) == "blvl" else int(float(self.resolve_calc(m.group(3), s, lvl, blvl, desc_row, depth + 1))))),
                (blvl if m.group(3) == "blvl" else lvl),
                m.group(2),
                None,
                depth + 1
            )),
            calc
        )
        calc = re.sub(
            r"skill\('(.*?)'\.(.*?)\)",
            lambda m: str(self.get_skill_val(self.skills.get(m.group(1).lower(), s), lvl, blvl, m.group(2), None, depth + 1)),
            calc
        )

        def missile_sub(m):
            m_row = self.missiles.get(m.group(1).lower(), {})
            prop = "Range" if m.group(2) == "rang" else m.group(2)
            res = self.resolve_calc(m_row.get(prop, "0"), s, lvl, blvl, desc_row, depth + 1)
            try:
                return str(float(res) / 25.0) if m.group(2) == "rang" else str(res)
            except:
                return "0"

        calc = re.sub(r"miss\('(.*?)'\.(.*?)\)", missile_sub, calc)
        calc = re.sub(r"stat\('(.*?)'\.(.*?)\)", "0", calc)

        B = r"\b"
        vars_to_res = [r"ln\d+", r"dm\d+", "edln", "mps", "usmc", "toht", "macr", "madm", "math", "pnma", "pxma", "edmn", "edmx", "enma", "exma", "enms", "exms", "edns", "edxs", "mael", "accr"]
        for i in range(1, 21):
            vars_to_res.extend([f"clc{i}", f"pst{i}", f"ps{i}", f"ast{i}", f"pa{i}"])
        for i in range(1, 4):
            vars_to_res.extend([f"m{i}nm", f"m{i}xm", f"m{i}eo", f"m{i}ey", f"m{i}rn"])
        vars_to_res.sort(key=lambda x: len(x.replace(r"\d+", "0")), reverse=True)

        for v in vars_to_res:
            if r"\d" in v:
                for m in set(re.findall(v, calc)):
                    calc = re.sub(B + m + B, str(self.get_skill_val(s, lvl, blvl, m, desc_row, depth + 1)), calc)
            elif v in calc:
                calc = re.sub(B + v + B, str(self.get_skill_val(s, lvl, blvl, v, desc_row, depth + 1)), calc)

        for i in range(20, 0, -1):
            if f"par{i}" in calc:
                calc = re.sub(B + "par" + str(i) + B, s.get(f"Param{i}", "0") or "0", calc)

        if "?" in calc and ":" in calc:
            calc = re.sub(r"(.*?)\?(.*?):(.*)", lambda m: f"({m.group(2)} if ({m.group(1)}) else {m.group(3)})", calc)

        calc = calc.replace("blvl", str(blvl)).replace("lvl", str(lvl))
        return calc

    def resolve_calc(self, calc, s, lvl, blvl, desc_row=None, depth=0):
        if not calc or depth > 15: return "0"
        calc = self.expand_calc(calc, s, lvl, blvl, desc_row, depth)
        try:
            ctx = {"min": min, "max": max, "lvl": lvl, "blvl": blvl}
            if re.sub(r"[\d\+\-\*\/,\(\)\.\s\?::\<\>\=\!ifels]+", "", calc.replace("min","").replace("max","").replace("lvl","").replace("blvl","")):
                return calc
            res = eval(calc, {"__builtins__": None}, ctx)
            return f"{res:.2f}" if isinstance(res, float) else str(res)
        except: return calc

    def format_generic_label(self, s: str) -> str:
        if not s:
            return ""
        text = str(s).strip()
        colon_idx = text.find(":")
        pct_idx = text.find("%")
        if colon_idx != -1 and (pct_idx == -1 or colon_idx < pct_idx):
            return re.sub(r"\s+", " ", text[:colon_idx]).strip(" :-").strip()
        cleaned = _PLACEHOLDER_STRIP_RE.sub("", text.replace("%%", "%"))
        return re.sub(r"\s+", " ", cleaned).strip(": -").strip()

    def build_effect_label(
        self,
        desc_row: Dict[str, str],
        line_index: int,
        raw_text: str,
        block: str = "desc",
        skill: Optional[Dict[str, str]] = None,
    ) -> str:
        text_col = f"{block}texta{line_index}" if block != "desc" else f"desctexta{line_index}"
        text_key_lower = str(desc_row.get(text_col, "") or "").strip().lower()
        target_skill = skill
        if target_skill is None:
            desc_name = str(desc_row.get("skilldesc", "") or "").strip().lower()
            if desc_name:
                target_skill = next(
                    (row for row in self.skills.values() if str(row.get("skilldesc", "") or "").strip().lower() == desc_name),
                    None,
                )

        if text_key_lower in _POISON_DURATION_KEYS:
            etype = str((target_skill or {}).get("EType", "") or "").strip().lower()
            duration_label = self.format_generic_label(resolve_localized_string(self.repo, "strskill20") or "Duration")
            if etype:
                return f"{resolve_element_name(self.repo, etype)} {duration_label}".strip()
            return duration_label

        if text_key_lower in _COLD_DURATION_KEYS:
            duration_label = self.format_generic_label(resolve_localized_string(self.repo, "strskill20") or "Duration")
            return f"{resolve_element_name(self.repo, 'cold')} {duration_label}".strip()

        return self.format_generic_label(raw_text)

    def get_display_skill_level(self, skill_name: str, scenario_skill_levels: Optional[Dict[str, int]], fallback: int) -> int:
        if not scenario_skill_levels:
            return fallback
        key = re.sub(r"[\s']", "", str(skill_name or "").strip().lower())
        if key in scenario_skill_levels:
            return int(scenario_skill_levels[key])

        skill_row = self.skills.get(str(skill_name or "").strip().lower())
        if skill_row:
            desc_row = self.skilldesc.get(str(skill_row.get("skilldesc", "") or "").strip().lower(), {})
            name_key = str(desc_row.get("str name", "") or "").strip()
            if name_key:
                for candidate in (
                    resolve_localized_string(self.repo, name_key),
                    resolve_canonical_string(self.repo, name_key),
                ):
                    if candidate:
                        alias_key = re.sub(r"[\s']", "", candidate.strip().lower())
                        if alias_key in scenario_skill_levels:
                            return int(scenario_skill_levels[alias_key])
        return fallback

    def get_display_synergy_bonus_mult(self, skill, scenario_skill_levels: Optional[Dict[str, int]]) -> float:
        syn_calc = skill.get('EDmgSymPerCalc') or skill.get('DmgSymPerCalc')
        if not syn_calc or syn_calc == '0':
            return 1.0
        try:
            bonus = float(self.evaluate_display_formula(syn_calc, skill, 1, 1, None, scenario_skill_levels, use_synergy=True))
            return 1.0 + (bonus / 100.0)
        except:
            return 1.0

    def get_display_elen_synergy_bonus_mult(self, skill, scenario_skill_levels: Optional[Dict[str, int]]) -> float:
        syn_calc = skill.get('ELenSymPerCalc')
        if not syn_calc or syn_calc == '0':
            return 1.0
        try:
            bonus = float(self.evaluate_display_formula(syn_calc, skill, 1, 1, None, scenario_skill_levels, use_synergy=True))
            return 1.0 + (bonus / 100.0)
        except:
            return 1.0

    def get_display_raw_value(self, row, lvl, col_prefix):
        try:
            val_raw = row.get(col_prefix, '0')
            if not val_raw:
                val_raw = '0'
            base = float(val_raw)
            add = 0.0
            for i in range(1, int(lvl)):
                idx = 1
                if i < 8:
                    idx = 1
                elif i < 16:
                    idx = 2
                elif i < 22:
                    idx = 3
                elif i < 28:
                    idx = 4
                else:
                    idx = 5

                l_val = 0.0
                found_lev = False
                for search_idx in range(idx, 0, -1):
                    possible_cols = [
                        f"Lev{col_prefix}{search_idx}",
                        f"{col_prefix}Lev{search_idx}",
                        f"Lev{col_prefix}",
                        f"{col_prefix}Lev"
                    ]
                    if col_prefix in ['MinDam', 'MinDamage']:
                        possible_cols = [f'MinLevDam{search_idx}', f'LevMinDam{search_idx}']
                    elif col_prefix in ['MaxDam', 'MaxDamage']:
                        possible_cols = [f'MaxLevDam{search_idx}', f'LevMaxDam{search_idx}']
                    elif col_prefix == 'EMin':
                        possible_cols = [f'EMinLev{search_idx}', f'MinELev{search_idx}', f'LevEMin{search_idx}']
                    elif col_prefix == 'EMax':
                        possible_cols = [f'EMaxLev{search_idx}', f'MaxELev{search_idx}', f'LevEMax{search_idx}']
                    elif col_prefix == 'ELen':
                        possible_cols = [f'ELevLen{search_idx}', f'ELenLev{search_idx}', f'LevELen{search_idx}']

                    for c in possible_cols:
                        if c in row and row.get(c, '') != '':
                            l_val = float(row.get(c, '0') or '0')
                            found_lev = True
                            break
                    if found_lev:
                        break
                add += l_val
            return base + add
        except:
            return 0.0

    def resolve_display_symbol(self, var, skill, lvl, blvl, desc_row=None, scenario_skill_levels: Optional[Dict[str, int]] = None, use_synergy=True):
        try:
            s = skill
            if var == 'lvl':
                return float(lvl)
            if var == 'blvl':
                return float(blvl)
            if var.startswith('par'):
                return float(s.get(f"Param{var[3:]}", "0") or '0')
            if var.startswith('pa'):
                return float(s.get(f"Param{var[2:]}", "0") or '0')
            ln_match = re.match(r'ln(\d+)', var)
            if ln_match:
                v = ln_match.group(1)
                p1_idx, p2_idx = int(v[0]), int(v[1:])
                p1 = float(s.get(f"Param{p1_idx}", 0) or 0)
                p2 = float(s.get(f"Param{p2_idx}", 0) or 0)
                return p1 + (lvl - 1) * p2
            dm_match = re.match(r'dm(\d+)', var)
            if dm_match:
                v = dm_match.group(1)
                p1_idx, p2_idx = int(v[0]), int(v[1:])
                p1 = float(s.get(f"Param{p1_idx}", 0) or 0)
                p2 = float(s.get(f"Param{p2_idx}", 0) or 0)
                return ((110.0 * lvl) * (p2 - p1)) / (100.0 * (lvl + 6)) + p1
            if var in ['mps', 'usmc', 'manc', 'manv']:
                m = float(s.get('mana', '0') or '0')
                lm = float(s.get('lvlmana', '0') or '0')
                shift = int(s.get('manashift', '8') or '8')
                return max(float(s.get('minmana', '0') or '0'), m + lm * (lvl - 1)) / (2.0 ** (8 - shift))
            if var == 'mael':
                syn_calc = s.get('EDmgSymPerCalc') or s.get('DmgSymPerCalc')
                eval_row = s
                if not syn_calc and desc_row:
                    m_name = desc_row.get('descmissile1', '')
                    m_row = self.missiles.get(m_name.lower()) if m_name else None
                    if m_row:
                        syn_calc = m_row.get('EDmgSymPerCalc') or m_row.get('DmgSymPerCalc')
                        eval_row = m_row
                bonus = 0.0
                if syn_calc:
                    bonus += float(self.evaluate_display_formula(syn_calc, eval_row, 1, 1, desc_row, scenario_skill_levels, use_synergy=True))
                etype = s.get('EType', '').strip().lower()
                if etype:
                    mastery = self.skills.get(f'passive_{etype}_mastery')
                    if mastery:
                        m_lvl = self.get_display_skill_level(mastery.get('skill', ''), scenario_skill_levels, 0)
                        if m_lvl > 0:
                            bonus += float(self.resolve_display_symbol('ln12', mastery, m_lvl, m_lvl, None, scenario_skill_levels, use_synergy=False))
                return bonus
            if var == 'toht':
                th = float(s.get('ToHit', '0') or '0')
                lth = float(s.get('LevToHit', '0') or '0')
                if th == 0 and lth == 0 and s.get('ToHitCalc'):
                    return float(self.evaluate_display_formula(s.get('ToHitCalc'), s, lvl, blvl, desc_row, scenario_skill_levels))
                return th + lth * (lvl - 1)
            if var == 'thtc':
                return float(self.evaluate_display_formula(s.get('ToHitCalc', '0'), s, lvl, blvl, desc_row, scenario_skill_levels))
            if var in ['enma', 'edmn', 'pnma', 'exma', 'edmx', 'pxma', 'enms', 'exms']:
                prefix = 'EMin' if 'e' in var else ('MinDam' if var == 'pnma' else 'MaxDam')
                if var in ['exma', 'edmx', 'pxma', 'exms']:
                    prefix = 'EMax' if 'e' in var else 'MaxDam'
                val = self.get_display_raw_value(s, lvl, prefix)
                shift = int(s.get('HitShift', '8') or '8')
                res = val * (2.0 ** shift)
                if use_synergy:
                    res *= self.get_display_synergy_bonus_mult(s, scenario_skill_levels)
                return res
            if var in ['edln', 'len']:
                res = self.get_display_raw_value(s, lvl, 'ELen')
                if use_synergy:
                    res *= self.get_display_elen_synergy_bonus_mult(s, scenario_skill_levels)
                return res
            if desc_row and var.startswith('m') and len(var) == 4:
                m_name = desc_row.get(f'descmissile{var[1]}')
                if m_name:
                    m = self.missiles.get(m_name.lower())
                    if m:
                        value_map = {'nm': 'MinDamage', 'xm': 'MaxDamage', 'eo': 'EMin', 'ey': 'EMax', 'rn': 'Range'}
                        val = self.get_display_raw_value(m, lvl, value_map.get(var[2:], ''))
                        if var[2:] == 'rn':
                            return val
                        shift = int(m.get('HitShift', '8') or '8')
                        res = val * (2.0 ** shift)
                        if use_synergy and var[2:] in ['eo', 'ey', 'nm', 'xm']:
                            res *= self.get_display_synergy_bonus_mult(s, scenario_skill_levels)
                        return res
            return 0.0
        except:
            return 0.0

    def evaluate_display_formula(self, formula, skill, lvl, blvl, desc_row=None, scenario_skill_levels: Optional[Dict[str, int]] = None, use_synergy=True):
        if not formula or formula == '' or formula == '0':
            return 0.0
        calc = str(formula).replace('"', '').strip()

        calc = re.sub(
            r"sklvl\('(.*?)'\.(.*?)\.(.*?)\)",
            lambda m: str(
                self.resolve_display_symbol(
                    m.group(2),
                    self.skills.get(m.group(1).lower(), skill),
                    self.get_display_skill_level(m.group(1), scenario_skill_levels, 0 if m.group(3) in ['blvl', 'lvl'] else lvl) if m.group(3) in ['blvl', 'lvl'] else lvl,
                    self.get_display_skill_level(m.group(1), scenario_skill_levels, 0),
                    None,
                    scenario_skill_levels,
                    use_synergy
                )
            ),
            calc
        )
        calc = re.sub(
            r"skill\('(.*?)'\.(.*?)\)",
            lambda m: str(
                self.resolve_display_symbol(
                    m.group(2),
                    self.skills.get(m.group(1).lower(), skill),
                    lvl,
                    self.get_display_skill_level(m.group(1), scenario_skill_levels, 0),
                    None,
                    scenario_skill_levels,
                    use_synergy
                )
            ),
            calc
        )
        calc = re.sub(
            r"miss\('(.*?)'\.(.*?)\)",
            lambda m: str(
                self.resolve_display_symbol(
                    'm1' + ('rn' if m.group(2) == 'rang' else m.group(2)),
                    skill,
                    lvl,
                    blvl,
                    {'descmissile1': m.group(1)},
                    scenario_skill_levels,
                    use_synergy
                )
            ),
            calc
        )
        if '?' in calc:
            calc = re.sub(r"(.*?)\?(.*?):(.*?)$", r"(\2 if \1 else \3)", calc)

        B = r'\b'
        symbols = [r'ln\d+', r'dm\d+', 'mps', 'usmc', 'mael', 'enma', 'exma', 'edmn', 'edmx', r'm\d[a-z]{2}', r'par\d+', r'pa\d+', 'manc', 'manv', 'edln', 'pnma', 'pxma', 'len', 'toht', 'thtc', 'enms', 'exms']
        apply_to_this_formula = use_synergy and not any(x in calc.lower() for x in ['mael', 'skill('])
        for sym_pat in symbols:
            matches = re.findall(sym_pat, calc)
            for match in set(matches):
                calc = re.sub(B + match + B, str(self.resolve_display_symbol(match, skill, lvl, blvl, desc_row, scenario_skill_levels, apply_to_this_formula)), calc)
        calc = re.sub(B + 'lvl' + B, str(lvl), calc)
        calc = re.sub(B + 'blvl' + B, str(blvl), calc)
        try:
            res = eval(calc, {"__builtins__": None}, {'min': min, 'max': max, 'float': float})
            return float(res)
        except:
            return 0.0

    def _calculate_summon_life(
        self,
        skill: Dict[str, str],
        desc_row: Dict[str, str],
        pct_bonus: float,
        flat_bonus_calc: str,
        lvl: int,
        blvl: int,
        scenario_skill_levels: Optional[Dict[str, int]] = None,
    ) -> float:
        summon_id = str(skill.get("summon", "") or "").strip().lower()
        mon = self.monstats.get(summon_id) if summon_id else None
        if not mon:
            return pct_bonus
        try:
            min_hp = float(mon.get("minHP", "0") or "0")
        except ValueError:
            min_hp = 0.0
        try:
            max_hp = float(mon.get("maxHP", "0") or "0")
        except ValueError:
            max_hp = 0.0
        if max_hp <= 0 and min_hp > 0:
            max_hp = min_hp
        base_hp = (min_hp + max_hp) / 2.0

        mon_lvl = str(mon.get("Level", "") or "").strip()
        if str(mon.get("noRatio", "") or "").strip() != "1" and mon_lvl in self.monlvl:
            try:
                lvl_mult = float(self.monlvl[mon_lvl].get("HP", "100") or "100") / 100.0
                base_hp *= lvl_mult
            except ValueError:
                pass

        if flat_bonus_calc:
            base_hp += float(self.evaluate_display_formula(flat_bonus_calc, skill, lvl, blvl, desc_row, scenario_skill_levels, use_synergy=True))
        return base_hp * (1.0 + pct_bonus / 100.0)

    def _classify_effect_unit(
        self,
        desc_row: Dict[str, str],
        line_idx: int,
        raw_template: str,
        block: str = "desc",
    ) -> str:
        line_prefix = f"{block}line" if block != "desc" else "descline"
        text_prefix = f"{block}texta" if block != "desc" else "desctexta"
        calc_a_prefix = f"{block}calca" if block != "desc" else "desccalca"
        calc_b_prefix = f"{block}calcb" if block != "desc" else "desccalcb"

        line_id = str(desc_row.get(f"{line_prefix}{line_idx}", "") or "").strip()
        text_key_lower = str(desc_row.get(f"{text_prefix}{line_idx}", "") or "").strip().lower()
        ca_norm = str(desc_row.get(f"{calc_a_prefix}{line_idx}", "") or "").lower().replace(" ", "")
        cb_str = str(desc_row.get(f"{calc_b_prefix}{line_idx}", "") or "").strip()
        try:
            cb_num: Optional[float] = float(cb_str) if cb_str else None
        except ValueError:
            cb_num = None

        if "%%" in raw_template or re.search(r"%\+?d%", raw_template):
            return "%"
        if line_id == "75" and (
            text_key_lower in _PER_SECOND_DAMAGE_KEYS
            or ("*25" in ca_norm and any(tok in ca_norm for tok in ("m1", "miss(", "enms", "exms")))
            or "*12/256" in ca_norm
        ):
            return " dmg/s"
        if (
            line_id in _DURATION_DESCLINES
            or (line_id == "36" and (cb_num in (25.0, 17.5) or text_key_lower in _DURATION_TEXT_KEYS))
            or (line_id in {"74", "75"} and ("/25" in ca_norm or text_key_lower in _DURATION_TEXT_KEYS))
        ):
            return "s"
        if (
            (line_id == "36" and (cb_num == 3.0 or text_key_lower in _DISTANCE_TEXT_KEYS))
            or (line_id == "74" and (".rad" in ca_norm or ca_norm == "rng" or text_key_lower in _DISTANCE_TEXT_KEYS))
        ):
            return "y"
        return ""

    def calculate_display_effect_value(self, skill, desc_row, line_idx, lvl, blvl, block="", scenario_skill_levels: Optional[Dict[str, int]] = None) -> str:
        text_prefix = f"{block}texta" if block else "desctexta"
        line_prefix = f"{block}line" if block else "descline"
        calc_a_prefix = f"{block}calca" if block else "desccalca"
        calc_b_prefix = f"{block}calcb" if block else "desccalcb"

        text_key = str(desc_row.get(text_prefix + str(line_idx), "") or "").strip().lower()
        raw_template = self.repo.get_string(text_key) or ""
        line_id = str(desc_row.get(line_prefix + str(line_idx), "") or "").strip()
        c1, c2 = desc_row.get(calc_a_prefix + str(line_idx), ""), desc_row.get(calc_b_prefix + str(line_idx), "")
        is_range = bool(re.search(r"%\+?d\s*[-~]\s*%\+?d", raw_template)) or (line_id in _RANGE_DESCLINES and bool(c2))

        def get_val(calc, apply_divisor: bool = True):
            if not calc or calc == '':
                return 0.0
            val = self.evaluate_display_formula(calc, skill, lvl, blvl, desc_row, scenario_skill_levels, use_synergy=True)
            calc_str = str(calc).replace(' ', '')
            calc_lower = calc_str.lower()
            if '/256' not in calc_str and abs(val) > 100 and any(x in calc_str for x in ['enma', 'exma', 'edmn', 'edmx', 'm1eo', 'm1ey', 'pnma', 'pxma', 'enms', 'exms']):
                val /= 256.0
            if line_id in _RANGE_DESCLINES and 'edln' not in calc_lower and 'len' not in calc_lower:
                etype = str(skill.get('EType', '') or '').strip().lower()
                elen = self.get_display_raw_value(skill, lvl, 'ELen')
                if 'm1' in calc_lower or 'miss(' in calc_lower:
                    m_name = desc_row.get('descmissile1', '')
                    m_row = self.missiles.get(m_name.lower()) if m_name else None
                    if m_row:
                        etype = str(m_row.get('EType', '') or etype).strip().lower()
                        elen = self.get_display_raw_value(m_row, lvl, 'ELen')
                if etype == 'pois' and elen > 0:
                    val *= (elen / 256.0)
            if line_id == '12':
                val /= 25.0
            elif line_id in {'31', '36'} and apply_divisor and c2:
                try:
                    divisor = float(c2)
                except ValueError:
                    divisor = 0.0
                if divisor > 0 and not (abs(divisor - 256.0) < 1e-9 and any(sym in calc_lower for sym in _MANA_SYMBOLS)):
                    val /= divisor
            if line_id == '13':
                val = self._calculate_summon_life(skill, desc_row, val, str(c2 or ""), lvl, blvl, scenario_skill_levels)
            return val

        if is_range and c2:
            return f"{get_val(c1, apply_divisor=False):.2f}-{get_val(c2, apply_divisor=False):.2f}"
        v_min = get_val(c1)
        return f"{v_min:.2f}"

    def get_skill_display_effects(self, skill_name: str, lvl: int, blvl: int, scenario_skill_levels: Optional[Dict[str, int]] = None) -> List[Dict[str, str]]:
        skill = self.skills[skill_name.lower()]
        desc_row = self.skilldesc[skill.get("skilldesc", "").lower()]
        effects = []
        for block in ["", "dsc2", "dsc3"]:
            text_prefix = f"{block}texta" if block else "desctexta"
            line_prefix = f"{block}line" if block else "descline"
            eff_block = block or "desc"
            for i in range(1, 10):
                if not desc_row.get(f"{line_prefix}{i}") or desc_row.get(f"{line_prefix}{i}") == '0':
                    continue
                text_label = self.repo.get_string(desc_row.get(f"{text_prefix}{i}", "").lower()) or desc_row.get(f"{text_prefix}{i}", "")
                if not text_label:
                    continue
                label = self.build_effect_label(desc_row, i, text_label, eff_block, skill=skill)
                value = self.calculate_display_effect_value(skill, desc_row, i, lvl, blvl, block, scenario_skill_levels)
                unit = self._classify_effect_unit(desc_row, i, text_label, eff_block)
                prefix = "+" if "%+" in text_label and not str(value).startswith("-") else ""
                if re.search(r"%\+?d\s*[-~]\s*%\+?d", text_label) or '-' in value[1:]:
                    formatted_value = f"{value}{unit}"
                else:
                    formatted_value = f"{prefix}{value}{unit}"
                effects.append({"label": label, "value": formatted_value, "block": eff_block})
        return effects

    def analyze_scaling(self, calc, s, unit, desc_row):
        try:
            vals = [float(self.resolve_calc(calc, s, l, bl, desc_row)) for l, bl in [(1,1),(2,2),(10,10),(11,11),(20,20),(21,20),(99,99)]]
            v1,v2,v10,v11,v20,v21,v99 = vals
            d1, d10, ds = v2-v1, v11-v10, v21-v20
            def fs(v): return f"{v:+.2f}".rstrip("0").rstrip(".")
            if abs(d1 - d10) < 0.001: sc = f"Linear ({fs(d1)}{unit})"
            elif d1 > d10: sc = f"Diminishing ({fs(d1)} -> {fs(d10)}{unit})"
            else: sc = f"Accelerating ({fs(d1)} -> {fs(d10)}{unit})"
            if abs(ds - d10) > 0.001: sc += f" [Soft: {fs(ds)}{unit}]"
            cap = f"Max: {v99}{unit}" if v99 < (v1 + (99-1)*d1) - 0.1 or abs(v99 - v20) < 0.001 and abs(v20 - v10) > 0.001 else "--"
            if v99 == v1 and v1 == v20 and v1 != 0: cap = f"Static: {v1}{unit}"
            return sc, cap
        except: return "Complex", "--"

    def analyze_range_scaling(self, c1, c2, s, unit, desc_row):
        try:
            s1, cp1 = self.analyze_scaling(c1, s, "", desc_row)
            s2, cp2 = self.analyze_scaling(c2, s, "", desc_row)
            if s1 == s2 and s1 != "Complex": return s1 + unit, (cp1 if cp1 == cp2 else f"{cp1}/{cp2}")
            if s1 != "Complex" and s2 != "Complex": return "Variable" + unit, (cp1 if cp1 == cp2 else f"{cp1}/{cp2}")
            return "Complex", "--"
        except: return "--", "--"

    def format_effect_value(self, calc, s, lvl, blvl, desc_row, unit, prefix="", show_formula=False):
        value = self.resolve_calc(calc, s, lvl, blvl, desc_row)
        if not show_formula:
            return f"{prefix}{value}{unit}"

        expanded = self.expand_calc(calc, s, lvl, blvl, desc_row)
        expanded = re.sub(r"\s+", " ", expanded).strip()
        if expanded == value:
            return f"{prefix}{value}{unit}"
        return f"{expanded} = {prefix}{value}{unit}"

    def _format_synergy_effect(self, dr: Dict[str, str], dsc: str, i: int, s: Dict[str, str]) -> Optional[Dict[str, str]]:
        line_id = str(dr.get(f"{dsc}line{i}", "") or "").strip()
        if line_id not in {"76", "77", "79"}:
            return None
        t_key = str(dr.get(f"{dsc}texta{i}", "") or "").strip()
        template = resolve_localized_string(self.repo, t_key) or t_key
        sid_key = str(dr.get(f"{dsc}textb{i}", "") or "").strip()
        sid_name = resolve_localized_string(self.repo, sid_key) or sid_key
        if not sid_name:
            return None

        ca = str(dr.get(f"{dsc}calca{i}", "") or "").strip()
        cb = str(dr.get(f"{dsc}calcb{i}", "") or "").strip()
        v_a = str(self.resolve_calc(ca, s, 1, 1, dr) or "").strip() if ca else ""
        v_b = str(self.resolve_calc(cb, s, 1, 1, dr) or "").strip() if cb else ""

        def _fmt_num(raw_num: str, include_plus: bool) -> str:
            try:
                num = float(raw_num)
            except ValueError:
                return raw_num
            if abs(num - round(num)) < 1e-6:
                txt = str(int(round(num)))
            else:
                txt = f"{num:.2f}".rstrip("0").rstrip(".")
            if include_plus and not txt.startswith(("+", "-")):
                return f"+{txt}"
            return txt

        if line_id == "79" and v_a and v_b:
            try:
                ratio = float(v_a) / float(v_b)
                values: List[str] = [_fmt_num(str(ratio), False)]
            except (ValueError, ZeroDivisionError):
                values = [v for v in (v_a, v_b) if v]
        else:
            values = [v for v in ((v_a, v_b) if line_id == "77" else (v_a,)) if v]

        clean_tpl = re.sub(r"^%s\s*:?\s*", "", template)
        slots = _PRINTF_TOKEN_RE.findall(clean_tpl)
        if slots and len(values) >= len(slots):
            vals_iter = iter(values)
            effect_text = _PRINTF_TOKEN_RE.sub(
                lambda m: _fmt_num(next(vals_iter), "+" in m.group(0)),
                clean_tpl,
            ).replace("%%", "%")
        else:
            rendered_tpl = clean_tpl.replace("%%", "%")
            clean_vals = [_fmt_num(v, False) for v in values]
            effect_text = f"{rendered_tpl} ({', '.join(clean_vals)})" if rendered_tpl and clean_vals else (rendered_tpl or ", ".join(clean_vals))

        return {"name": sid_name, "effect": effect_text.strip()}

    def generate_skill_tree(self, char_class_abbr: str) -> SkillTreeDTO:
        cc = char_class_abbr.lower()
        cs = [s for s in self.skills.values() if s.get("charclass") == cc]
        class_name = self.class_map.get(cc, cc.upper())
        skills_dto = []
        for s in cs:
            dr = self.skilldesc.get(s.get("skilldesc", "").lower())
            if not dr: continue

            skill_id = s.get("skill", "")
            skill_name_key = dr.get("str name", "").lower()
            skill_name = resolve_localized_string(self.repo, skill_name_key) or resolve_localized_string(self.repo, skill_id) or skill_id

            effects = []
            for i in range(1, 7):
                if not dr.get(f"descline{i}") or dr.get(f"descline{i}") == "0": continue
                text_key = dr.get(f"desctexta{i}", "").lower()
                tl = self.repo.get_string(text_key) or dr.get(f"desctexta{i}", "")

                unit = self._classify_effect_unit(dr, i, tl, "desc")

                c1, c2 = dr.get(f"desccalca{i}", ""), dr.get(f"desccalcb{i}", "")
                label = self.build_effect_label(dr, i, tl, "desc", skill=s)
                line_id = str(dr.get(f"descline{i}", "") or "").strip()
                is_range = bool(re.search(r"%\+?d\s*[-~]\s*%\+?d", tl)) and bool(c2)
                if not is_range and line_id in _RANGE_DESCLINES and bool(c1) and bool(c2):
                    is_range = True

                if is_range:
                    sc, cap = self.analyze_range_scaling(c1, c2, s, unit, dr)
                    show_formula = sc == "Complex"
                    v = [self.format_effect_value(c, s, l, bl, dr, "", show_formula=show_formula) for c in [c1, c2] for l, bl in [(1,1),(10,10),(20,20),(30,20)]]
                    effects.append({
                        "label": label, "scaling": sc, "l1": f"{v[0]}-{v[4]}{unit}", "l10": f"{v[1]}-{v[5]}{unit}",
                        "l20": f"{v[2]}-{v[6]}{unit}", "l30": f"{v[3]}-{v[7]}{unit}", "limit": cap
                    })
                else:
                    sc, cap = self.analyze_scaling(c1, s, unit, dr)
                    raw_values = [self.resolve_calc(c1, s, l, bl, dr) for l, bl in [(1,1),(10,10),(20,20),(30,20)]]
                    pref = "+" if "%+" in tl and not str(raw_values[0]).startswith("-") else ""
                    show_formula = sc == "Complex"
                    v = [self.format_effect_value(c1, s, l, bl, dr, unit, pref, show_formula) for l, bl in [(1,1),(10,10),(20,20),(30,20)]]
                    effects.append({
                        "label": label, "scaling": sc, "l1": v[0], "l10": v[1],
                        "l20": v[2], "l30": v[3], "limit": cap
                    })

            synergies = []
            for dsc in ["dsc2", "dsc3"]:
                for i in range(1, 8):
                    syn_entry = self._format_synergy_effect(dr, dsc, i, s)
                    if syn_entry:
                        synergies.append(syn_entry)

            skills_dto.append({
                "id": skill_id,
                "name": skill_name,
                "slug": slugify(skill_id or skill_name),
                "effects": effects,
                "synergies": synergies,
                "raw_row": s
            })

        return {"class_name": class_name, "skills": skills_dto}
