import csv
import os
import json
import re
import sys

# Global map for synergy levels provided via CLI
SYNERGY_MAP = {}

class D2Data:
    def __init__(self, mod_path, retail_path):
        self.mod_path = mod_path
        self.retail_path = retail_path
        self.skills = self.load_data("skills.txt")
        self.missiles = self.load_data("missiles.txt")
        self.skilldescs = self.load_data("skilldesc.txt")
        self.charstats = self.load_data("charstats.txt")
        self.monstats = self.load_data("monstats.txt")
        self.strings = self.load_strings()
        
        self.skill_map = {s['skill'].lower(): s for s in self.skills}
        self.missile_map = {m['Missile'].lower(): m for m in self.missiles}
        self.desc_map = {d['skilldesc'].lower(): d for d in self.skilldescs}
        self.mon_map = {m['Id'].lower(): m for m in self.monstats}
        
        for s in self.skills:
            dr = self.desc_map.get(s['skilldesc'].lower())
            if dr:
                n = self.strings.get(dr.get('skillname', '').lower())
                if n: self.skill_map[n.lower()] = s

    def load_tsv(self, filepath):
        if not os.path.exists(filepath): return []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            if not lines: return []
            header = [h.strip() for h in lines[0].split('\t')]
            data = []
            for line in lines[1:]:
                row = [v.strip() for v in line.split('\t')]
                if len(row) < len(header): continue
                data.append(dict(zip(header, row)))
        return data

    def load_data(self, filename):
        path = os.path.join(self.mod_path, "data/global/excel", filename)
        data = self.load_tsv(path)
        if not data and self.retail_path:
            data = self.load_tsv(os.path.join(self.retail_path, "excel", filename))
        return data

    def load_strings(self):
        strings = {}
        paths = [
            os.path.join(os.path.dirname(self.mod_path), "../../data/base/strings"),
            os.path.join(self.retail_path, "../local/lng/strings"),
            os.path.join(self.mod_path, "data/local/lng/strings")
        ]
        for p in paths:
            if os.path.exists(p):
                for f in os.listdir(p):
                    if f.endswith(".json"):
                        with open(os.path.join(p, f), 'r', encoding='utf-8-sig') as file:
                            try:
                                for entry in json.load(file):
                                    k, v = entry.get('Key'), entry.get('enUS')
                                    if k and v: strings[k.lower()] = v
                            except: continue
        return strings

class Evaluator:
    def __init__(self, data):
        self.data = data

    def get_blvl(self, skill_name, use_synergy=True):
        if not use_synergy: return 0.0
        name_clean = skill_name.lower().strip().replace(' ', '').replace("'", "")
        if name_clean in SYNERGY_MAP: return float(SYNERGY_MAP[name_clean])
        sk = self.data.skill_map.get(name_clean)
        if sk: return float(SYNERGY_MAP.get(sk['skill'].lower().replace(' ',''), 0.0))
        return 0.0

    def get_synergy_bonus(self, skill):
        syn_calc = skill.get('EDmgSymPerCalc') or skill.get('DmgSymPerCalc')
        if not syn_calc or syn_calc == '0': return 1.0
        try:
             res = float(self.evaluate(syn_calc, skill, 1, 1, use_synergy=True))
             return 1.0 + (res / 100.0)
        except: return 1.0

    def get_elen_synergy_bonus(self, skill):
        syn_calc = skill.get('ELenSymPerCalc')
        if not syn_calc or syn_calc == '0': return 1.0
        try:
             res = float(self.evaluate(syn_calc, skill, 1, 1, use_synergy=True))
             return 1.0 + (res / 100.0)
        except: return 1.0

    def get_raw_value(self, row, lvl, col_prefix):
        try:
            val_raw = row.get(col_prefix, '0')
            if not val_raw or val_raw == '': val_raw = '0'
            base = float(val_raw)
            add = 0.0
            for i in range(1, int(lvl)):
                idx = 1
                if i < 8: idx = 1
                elif i < 16: idx = 2
                elif i < 22: idx = 3
                elif i < 28: idx = 4
                else: idx = 5
                
                l_val = 0.0
                found_lev = False
                for search_idx in range(idx, 0, -1):
                    # Possible leveling column names
                    possible_cols = [
                        f"Lev{col_prefix}{search_idx}",
                        f"{col_prefix}Lev{search_idx}",
                        f"Lev{col_prefix}",
                        f"{col_prefix}Lev"
                    ]
                    if col_prefix == 'MinDam' or col_prefix == 'MinDamage':
                        possible_cols = [f'MinLevDam{search_idx}', f'LevMinDam{search_idx}']
                    elif col_prefix == 'MaxDam' or col_prefix == 'MaxDamage':
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
                    if found_lev: break
                add += l_val
            return base + add
        except: return 0.0

    def resolve_symbol(self, var, skill, lvl, blvl, desc_row=None, apply_syn=False):
        try:
            s = skill
            if var == 'lvl': return float(lvl)
            if var == 'blvl': return float(blvl)
            if var.startswith('par'): return float(s.get(f"Param{var[3:]}", "0") or '0')
            if var.startswith('pa'): return float(s.get(f"Param{var[2:]}", "0") or '0')
            ln_match = re.match(r'ln(\d+)', var)
            if ln_match:
                v = ln_match.group(1); p1_idx, p2_idx = int(v[0]), int(v[1:])
                p1, p2 = float(s.get(f"Param{p1_idx}", 0)), float(s.get(f"Param{p2_idx}", 0))
                return p1 + (lvl - 1) * p2
            dm_match = re.match(r'dm(\d+)', var)
            if dm_match:
                v = dm_match.group(1); p1_idx, p2_idx = int(v[0]), int(v[1:])
                p1, p2 = float(s.get(f"Param{p1_idx}", 0)), float(s.get(f"Param{p2_idx}", 0))
                return ((110.0 * lvl) * (p2 - p1)) / (100.0 * (lvl + 6)) + p1
            if var in ['mps', 'usmc', 'manc', 'manv']:
                m, lm, shift = float(s.get('mana', '0')), float(s.get('lvlmana', '0')), int(s.get('manashift', '8'))
                return max(float(s.get('minmana', '0')), m + lm * (lvl - 1)) / (2.0**(8 - shift))
            if var == 'mael':
                if 'Immolation Arrow' in s.get('skill', ''): return (self.get_blvl('fire arrow') + self.get_blvl('exploding arrow')) * 5.0
                syn_calc = s.get('EDmgSymPerCalc') or s.get('DmgSymPerCalc')
                if syn_calc: return float(self.evaluate(syn_calc, skill, 1, 1, use_synergy=True))
                return 0.0
            if var == 'toht':
                th, lth = float(s.get('ToHit', '0') or '0'), float(s.get('LevToHit', '0') or '0')
                if th == 0 and lth == 0 and s.get('ToHitCalc'): return float(self.evaluate(s.get('ToHitCalc'), s, lvl, blvl))
                return th + lth * (lvl - 1)
            if var == 'thtc': return float(self.evaluate(s.get('ToHitCalc', '0'), s, lvl, blvl))
            if var in ['enma', 'edmn', 'pnma', 'exma', 'edmx', 'pxma', 'enms', 'exms']:
                prefix = 'EMin' if 'e' in var else ('MinDam' if 'pnma' == var else 'MaxDam')
                if 'exma' in var or 'edmx' in var or 'pxma' == var or 'exms' == var: prefix = 'EMax' if 'e' in var else 'MaxDam'
                val, shift = self.get_raw_value(s, lvl, prefix), int(s.get('HitShift', '8'))
                res = val * (2.0**shift)
                if apply_syn: res *= self.get_synergy_bonus(s)
                return res
            if var in ['edln', 'len']:
                res = self.get_raw_value(s, lvl, 'ELen')
                if apply_syn: res *= self.get_elen_synergy_bonus(s)
                return res
            if desc_row and var.startswith('m') and len(var) == 4:
                m_idx, m_type, m_name = var[1], var[2:], desc_row.get(f'descmissile{var[1]}')
                if m_name:
                    m = self.data.missile_map.get(m_name.lower())
                    if m:
                        cm = {'nm': 'MinDamage', 'xm': 'MaxDamage', 'eo': 'EMin', 'ey': 'EMax', 'rn': 'Range'}
                        val = self.get_raw_value(m, lvl, cm.get(m_type))
                        if m_type == 'rn': return val
                        shift = int(m.get('HitShift', '8'))
                        res = val * (2.0**shift)
                        if apply_syn and m_type in ['eo', 'ey', 'nm', 'xm']: res *= self.get_synergy_bonus(s)
                        return res
            return 0.0
        except: return 0.0

    def evaluate(self, formula, skill, lvl, blvl, desc_row=None, use_synergy=True):
        if not formula or formula == '' or formula == '0': return 0.0
        calc = str(formula).replace('"', '').strip()
        calc = re.sub(r"sklvl\('(.*?)'\.(.*?)\.(.*?)\)", lambda m: str(self.resolve_symbol(m.group(2), self.data.skill_map.get(m.group(1).lower(), skill), self.get_blvl(m.group(1), use_synergy) if m.group(3) == 'blvl' else lvl, self.get_blvl(m.group(1), use_synergy))), calc)
        calc = re.sub(r"skill\('(.*?)'\.(.*?)\)", lambda m: str(self.resolve_symbol(m.group(2), self.data.skill_map.get(m.group(1).lower(), skill), lvl, self.get_blvl(m.group(1), use_synergy))), calc)
        calc = re.sub(r"miss\('(.*?)'\.(.*?)\)", lambda m: str(self.resolve_symbol('m1' + ('rn' if m.group(2)=='rang' else m.group(2)), skill, lvl, blvl, {'descmissile1': m.group(1)})), calc)
        if '?' in calc: calc = re.sub(r"(.*?)\?(.*?):(.*?)$", r"(\2 if \1 else \3)", calc)
        B = r'\b'; symbols = [r'ln\d+', r'dm\d+', 'mps', 'usmc', 'mael', 'enma', 'exma', 'edmn', 'edmx', r'm\d[a-z]{2}', r'par\d+', r'pa\d+', 'manc', 'manv', 'edln', 'pnma', 'pxma', 'len', 'toht', 'thtc', 'enms', 'exms']
        # Determine if automatic synergy should be applied to symbols in this formula
        # Skip automatic synergy if explicit synergy (mael) or skill reference is present in the formula
        apply_to_this_formula = use_synergy and not any(x in calc.lower() for x in ['mael', 'skill('])
        for sym_pat in symbols:
            matches = re.findall(sym_pat, calc)
            for m in set(matches): calc = re.sub(B + m + B, str(self.resolve_symbol(m, skill, lvl, blvl, desc_row, apply_syn=apply_to_this_formula)), calc)
        calc = re.sub(B + 'lvl' + B, str(lvl), calc); calc = re.sub(B + 'blvl' + B, str(blvl), calc)
        if 'mael' in formula.lower():
            print(f"          EVAL_DEBUG: '{formula}' -> '{calc}'")
        try:
            res = eval(calc, {"__builtins__": None}, {'min': min, 'max': max, 'float': float})
            return float(res)
        except: return 0.0

    def calculate(self, skill, dr, line_idx, lvl, blvl, block=""):
        text_prefix = f"{block}texta" if block else "desctexta"
        line_prefix = f"{block}line" if block else "descline"
        calc_a_prefix = f"{block}calca" if block else "desccalca"
        calc_b_prefix = f"{block}calcb" if block else "desccalcb"
        
        text_raw = self.data.strings.get(dr.get(text_prefix + str(line_idx), "").lower(), "").replace('%d', '').replace('%+d', '').replace('%%', '%').strip(': ')
        syn = self.get_synergy_bonus(skill)
        c1, c2 = dr.get(calc_a_prefix + str(line_idx)), dr.get(calc_b_prefix + str(line_idx))
        is_range = ('-' in text_raw or '%d-%d' in text_raw)
        
        def get_val(calc):
            if not calc or calc == '': return 0.0
            val = self.evaluate(calc, skill, lvl, blvl, dr, use_synergy=True)
            if '/256' not in str(calc).replace(' ','') and abs(val) > 100:
                 if any(x in str(calc) for x in ['enma','exma','edmn','edmx','m1eo','m1ey','pnma','pxma','enms','exms']): val /= 256.0
            if 'poison damage' in text_raw.lower():
                elen = self.get_raw_value(skill, lvl, 'ELen')
                if 'm1' in str(calc):
                    m_name = dr.get('descmissile1'); m = self.data.missile_map.get(m_name.lower())
                    if m: elen = self.get_raw_value(m, lvl, 'ELen')
                # If formula doesn't have duration already, multiply by it
                if 'edln' not in str(calc).lower() and 'len' not in str(calc).lower():
                    val *= (elen / 256.0)
            if dr.get(line_prefix + str(line_idx)) in ['12', '31'] or ('second' in text_raw.lower() and 'per second' not in text_raw.lower()):
                 if val > 15: val /= 25.0
            if dr.get(line_prefix + str(line_idx)) == '36' and 'radius' in text_raw.lower():
                 if c2 == '3': val /= 3.0
            # Synergy is now applied inside evaluate() via resolve_symbol(apply_syn=True)
            if 'life' in text_raw.lower() and dr.get(line_prefix + str(line_idx)) == '13': val = 440.0 * (1.0 + (val+400.0) / 100.0)
            return val
        v_min = get_val(c1)
        if is_range and c2: return f"{v_min:.1f}-{get_val(c2):.1f}"
        return f"{v_min:.1f}"

def main():
    if len(sys.argv) < 2: return
    class_code = sys.argv[1].lower()
    if len(sys.argv) > 2:
        for pair in sys.argv[2].split(','):
            if '=' in pair:
                n, v = pair.split('='); SYNERGY_MAP[n.strip().lower().replace(' ', '')] = int(v.strip())
    script_dir = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(script_dir)
    data = D2Data(os.path.join(root, "mods/BKDiablo/bkdiablo.mpq"), os.path.join(root, "data/retail")); ev = Evaluator(data)
    class_skills = [s for s in data.skills if s.get('charclass') == class_code]
    output = f"# {class_code.upper()} Skill Trees (BKDiablo)\n\n"
    for page in ['1', '2', '3']:
        page_skills = [(s, data.desc_map[s['skilldesc'].lower()]) for s in class_skills if s['skilldesc'].lower() in data.desc_map and data.desc_map[s['skilldesc'].lower()].get('SkillPage') == page]
        if not page_skills: continue
        output += f"# Tree {page}\n\n"
        for s, dr in page_skills:
            name = data.strings.get(dr.get('skillname', '').lower(), s['skill'])
            output += f"## {name}\n\n| Effect | L1 | L10 | L20 | L20+10 |\n| :--- | :---: | :---: | :---: | :---: |\n"
            for i in range(1, 10):
                if not dr.get(f"descline{i}") or dr.get(f"descline{i}") == '0': continue
                text = data.strings.get(dr.get(f"desctexta{i}", "").lower(), "").replace('%d', '').replace('%+d', '').replace('%%', '%').strip(': ')
                def get_row(idx): return [ev.calculate(s, dr, idx, l, bl) for l, bl in [(1,1),(10,10),(20,20),(30,20)]]
                r = get_row(i); output += f"| {text} | {r[0]} | {r[1]} | {r[2]} | {r[3]} |\n"
            output += "\n"
    out_path = os.path.join(root, f"output/skill_trees/{class_code}_skills.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"Exported to {out_path}")
if __name__ == "__main__": main()
