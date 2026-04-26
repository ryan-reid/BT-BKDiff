import csv
import os
import json
import re
import sys

def load_tsv(filepath):
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

def load_all_strings(mod_path, base_strings_path):
    strings = {}
    if os.path.exists(base_strings_path):
        for filename in os.listdir(base_strings_path):
            if filename.endswith(".json"):
                with open(os.path.join(base_strings_path, filename), 'r', encoding='utf-8-sig') as f:
                    try:
                        data = json.load(f)
                        for entry in data:
                            key, val = entry.get('Key'), entry.get('enUS')
                            if key and val: strings[key.lower()] = val
                    except: continue
    mod_strings_dir = os.path.join(mod_path, "data", "local", "lng", "strings")
    if os.path.exists(mod_strings_dir):
        for filename in os.listdir(mod_strings_dir):
            if filename.endswith(".json"):
                with open(os.path.join(mod_strings_dir, filename), 'r', encoding='utf-8-sig') as f:
                    try:
                        data = json.load(f)
                        for entry in data:
                            key, val = entry.get('Key'), entry.get('enUS')
                            if key and val: strings[key.lower()] = val
                    except: continue
    return strings

def get_dam_generic(s, lvl, prefix):
    try:
        base = int(s.get(f'{prefix}', '0') or '0')
        add = 0
        for i in range(1, lvl):
            if i < 8: add += int(s.get(f'{prefix}Lev1', '0') or '0')
            elif i < 16: add += int(s.get(f'{prefix}Lev2', '0') or '0')
            elif i < 22: add += int(s.get(f'{prefix}Lev3', '0') or '0')
            elif i < 28: add += int(s.get(f'{prefix}Lev4', '0') or '0')
            else: add += int(s.get(f'{prefix}Lev5', '0') or '0')
        return base + add
    except: return 0

def get_missile_dam(m, lvl, prefix):
    try:
        base = int(m.get(prefix, '0') or '0')
        p_root = prefix
        if prefix.startswith('EMin'): p_root = 'MinE'
        elif prefix.startswith('EMax'): p_root = 'MaxE'
        elif prefix.startswith('MinDam'): p_root = 'Min'
        elif prefix.startswith('MaxDam'): p_root = 'Max'
        add = 0
        for i in range(1, lvl):
            if i < 8: add += int(m.get(f'{p_root}Lev1', '0') or '0')
            elif i < 16: add += int(m.get(f'{p_root}Lev2', '0') or '0')
            elif i < 22: add += int(m.get(f'{p_root}Lev3', '0') or '0')
            elif i < 28: add += int(m.get(f'{p_root}Lev4', '0') or '0')
            else: add += int(m.get(f'{p_root}Lev5', '0') or '0')
        return base + add
    except: return 0

def get_skill_val(s, lvl, blvl, var, skill_map, missile_map, desc_row=None, depth=0):
    if depth > 15: return 0
    try:
        def p(n): return int(s.get(f"Param{n}", "0") or "0")
        ln_match = re.match(r'ln(\d+)', var)
        if ln_match:
            v = ln_match.group(1)
            if len(v) >= 2:
                p1, p2 = int(v[0]), int(v[1:])
                return p(p1) + (lvl - 1) * p(p2)
        dm_match = re.match(r'dm(\d+)', var)
        if dm_match:
            v = dm_match.group(1)
            if len(v) >= 2:
                p1, p2 = int(v[0]), int(v[1:])
                return ((110 * lvl) * (p(p2) - p(1))) // (100 * (lvl + 6)) + p(1)
        if var == 'macr': return p(1) + (lvl - 1) * p(2)
        if var == 'madm': return p(3) + (lvl - 1) * p(4)
        if var == 'math': return p(5) + (lvl - 1) * p(6)
        if var == 'edln': 
            elen = int(s.get('ELen', '0') or '0')
            elevlen = sum([int(s.get(f'ELevLen{i}', '0') or '0') for i in range(1, 4)])
            return elen + elevlen * (lvl - 1)
        if var in ['mps', 'usmc']:
            m, lm = int(s.get('mana', '0') or '0'), int(s.get('lvlmana', '0') or '0')
            min_m = int(s.get('minmana', '0') or '0')
            val = max(min_m, m + lm * (lvl - 1))
            shift = int(s.get('manashift', '8') or '8')
            return val / (2**(8 - shift))
        if var == 'toht': return int(s.get('ToHit', '0') or '0') + int(s.get('LevToHit', '0') or '0') * (lvl - 1)
        if var == 'pnma' or var == 'edmn': return get_dam_generic(s, lvl, 'MinDam')
        if var == 'pxma' or var == 'edmx': return get_dam_generic(s, lvl, 'MaxDam')
        if var == 'enma': return get_dam_generic(s, lvl, 'EMin')
        if var == 'exma': return get_dam_generic(s, lvl, 'EMax')
        if var == 'mael':
             m_name = f'passive_{s.get("EType", "")}_mastery'
             mastery = skill_map.get(m_name)
             if mastery: return get_skill_val(mastery, lvl, blvl, 'accr', skill_map, missile_map, None, depth+1)
             return 0
        if desc_row and var.startswith('m') and len(var) == 4:
            m_idx, m_type = var[1], var[2:]
            m_name = desc_row.get(f'descmissile{m_idx}')
            if m_name:
                m = missile_map.get(m_name.lower())
                if m:
                    if m_type == 'nm': return get_missile_dam(m, lvl, 'MinDamage')
                    elif m_type == 'xm': return get_missile_dam(m, lvl, 'MaxDamage')
                    elif m_type == 'eo': return get_missile_dam(m, lvl, 'EMin')
                    elif m_type == 'ey': return get_missile_dam(m, lvl, 'EMax')
        if var in ['enms', 'exms', 'edns', 'edxs']:
            base_col = 'EMin' if (var == 'enms' or var == 'edns') else 'EMax'
            val = get_dam_generic(s, lvl, base_col)
            elen = int(s.get('ELen', '0') or '0') + int(s.get('ELevLen1', '0') or '0') * (lvl - 1)
            return (val * elen) / 256
        if var.startswith('clc'):
            expr = s.get(f'calc{var[3:]}', s.get(f'cltcalc{var[3:]}', '0'))
            return resolve_calc(expr, s, lvl, blvl, skill_map, missile_map, desc_row, depth + 1)
        if var.startswith('pst'):
            expr = s.get(f'passivecalc{var[3:]}', '0')
            return resolve_calc(expr, s, lvl, blvl, skill_map, missile_map, desc_row, depth + 1)
        if var.startswith('ps'):
             expr = s.get(f'passivecalc{var[2:]}', '0')
             return resolve_calc(expr, s, lvl, blvl, skill_map, missile_map, desc_row, depth + 1)
        if var.startswith('ast'):
             expr = s.get(f'aurastatcalc{var[3:]}', '0')
             return resolve_calc(expr, s, lvl, blvl, skill_map, missile_map, desc_row, depth + 1)
        if var.startswith('pa'):
            return s.get(f'Param{var[2:]}', '0')
        if var.startswith('par'): return p(var[3:])
        if var == 'accr': return p(1) + (lvl - 1) * p(2)
        return var
    except: return var

def resolve_calc(calc, s, lvl, blvl, skill_map, missile_map, desc_row=None, depth=0):
    if not calc or depth > 15: return "0"
    calc = str(calc)
    
    def resolve_ternary(match): 
        cond, v1, v2 = match.group(1), match.group(2), match.group(3)
        return f"({v1} if ({cond}) else {v2})"
    
    if '?' in calc and ':' in calc:
        calc = re.sub(r"\((.*?)\)\s*\?\s*(.*?)\s*:\s*(.*?)$", resolve_ternary, calc)
        if '?' in calc and ':' in calc: # Check again for non-parenthesized
             calc = re.sub(r"(.*?)\s*\?\s*(.*?)\s*:\s*(.*?)$", resolve_ternary, calc)

    calc = re.sub(r"sklvl\('(.*?)'\.(.*?)\.(.*?)\)", lambda m: str(get_skill_val(skill_map.get(m.group(1).lower(), s), (lvl if m.group(3) in ['lvl','0'] else (blvl if m.group(3)=='blvl' else int(float(resolve_calc(m.group(3), s, lvl, blvl, skill_map, missile_map, desc_row, depth+1))))), (blvl if m.group(3)=='blvl' else lvl), m.group(2), skill_map, missile_map, None, depth+1)), calc)
    calc = re.sub(r"skill\('(.*?)'\.(.*?)\)", lambda m: str(get_skill_val(skill_map.get(m.group(1).lower(), s), lvl, blvl, m.group(2), skill_map, missile_map, None, depth+1)), calc)
    calc = re.sub(r"miss\('(.*?)'\.(.*?)\)", lambda m: (str(float(resolve_calc(missile_map.get(m.group(1).lower(),{}).get('Range' if m.group(2)=='rang' else m.group(2), '0'), s, lvl, blvl, skill_map, missile_map, desc_row, depth+1))/25) if m.group(2)=='rang' else str(resolve_calc(missile_map.get(m.group(1).lower(),{}).get(m.group(2), '0'), s, lvl, blvl, skill_map, missile_map, desc_row, depth+1))), calc)
    calc = re.sub(r"stat\('(.*?)'\.(.*?)\)", "0", calc)
    
    B = r'\b'
    vars_to_res = [r'ln\d+', r'dm\d+', 'edln', 'mps', 'usmc', 'toht', 'macr', 'madm', 'math', 'pnma', 'pxma', 'edmn', 'edmx', 'enma', 'exma', 'enms', 'exms', 'edns', 'edxs', 'mael', 'accr']
    for i in range(1, 21): vars_to_res.extend([f'clc{i}', f'pst{i}', f'ps{i}', f'ast{i}', f'pa{i}'])
    for i in range(1, 4):
        for t in ['nm', 'xm', 'eo', 'ey']: vars_to_res.append(f'm{i}{t}')
    vars_to_res.sort(key=lambda x: len(x.replace(r'\d+', '0')), reverse=True)
    for v in vars_to_res:
        if r'\d' in v:
            matches = re.findall(v, calc)
            for m in set(matches):
                val = get_skill_val(s, lvl, blvl, m, skill_map, missile_map, desc_row, depth + 1)
                calc = re.sub(B + m + B, str(val), calc)
        elif v in calc:
            val = get_skill_val(s, lvl, blvl, v, skill_map, missile_map, desc_row, depth + 1)
            calc = re.sub(B + v + B, str(val), calc)
    for i in range(20, 0, -1):
        p_var = 'par' + str(i)
        if p_var in calc: calc = re.sub(B + p_var + B, s.get(f"Param{i}", "0") or "0", calc)
    
    if 'if' in calc and 'else' in calc: # Python ternary
         pass
    elif '?' in calc and ':' in calc: # Should have been resolved
         calc = re.sub(r'(.*?)\?(.*?):(.*)', r'(\2 if \1 else \3)', calc)

    calc = calc.replace('min(', 'min(').replace('max(', 'max(')
    try:
        context = {'min': min, 'max': max, 'lvl': lvl, 'blvl': blvl}
        check_str = re.sub(r'[\d\+\-\*\/\(\)\.\s\?:\,\<\>\=\!]', '', calc.replace('min', '').replace('max', '').replace('lvl', '').replace('blvl', '').replace('if', '').replace('else', ''))
        if check_str: return calc
        res = eval(calc, {"__builtins__": None}, context)
        return f"{res:.1f}" if isinstance(res, float) else str(res)
    except: return calc

def format_generic_label(s):
    if not s: return ""
    label = s
    for code in ['%+d%%', '%d%%', '%+d', '%d', '%s']: label = label.replace(code, "")
    label = label.replace("-%d", "").replace("-%+d", "")
    label = label.replace("per second", "").replace("second", "").replace("yard", "")
    return re.sub(r'\s+', ' ', label).strip(': -').strip()

def analyze_scaling(calc, s, unit, skill_map, missile_map, desc_row):
    try:
        v1 = float(resolve_calc(calc, s, 1, 1, skill_map, missile_map, desc_row))
        v2 = float(resolve_calc(calc, s, 2, 2, skill_map, missile_map, desc_row))
        v10 = float(resolve_calc(calc, s, 10, 10, skill_map, missile_map, desc_row))
        v11 = float(resolve_calc(calc, s, 11, 11, skill_map, missile_map, desc_row))
        v20 = float(resolve_calc(calc, s, 20, 20, skill_map, missile_map, desc_row))
        v21 = float(resolve_calc(calc, s, 21, 20, skill_map, missile_map, desc_row))
        v99 = float(resolve_calc(calc, s, 99, 99, skill_map, missile_map, desc_row))
        d1, d10, ds = v2 - v1, v11 - v10, v21 - v20
        def fs(v): return f"{v:+.1f}".rstrip('0').rstrip('.')
        if abs(d1 - d10) < 0.01: scaling = f"Linear ({fs(d1)}{unit})"
        elif d1 > d10: scaling = f"Diminishing ({fs(d1)} -> {fs(d10)}{unit})"
        else: scaling = f"Accelerating ({fs(d1)} -> {fs(d10)}{unit})"
        if abs(ds - d10) > 0.01: scaling += f" [Soft: {fs(ds)}{unit}]"
        cap = f"Max: {v20}{unit}" if abs(v99 - v20) < 0.01 and abs(v20 - v10) > 0.01 else (f"Static: {v1}{unit}" if v99 == v1 and v1 == v20 and v1 != 0 else "--")
        return scaling, cap
    except: return "Complex", "--"

def analyze_range_scaling(c1, c2, s, unit, skill_map, missile_map, desc_row):
    try:
        s1, cap1 = analyze_scaling(c1, s, "", skill_map, missile_map, desc_row)
        s2, cap2 = analyze_scaling(c2, s, "", skill_map, missile_map, desc_row)
        if s1 == s2 and s1 != "Complex": return s1 + unit, (cap1 if cap1 == cap2 else f"{cap1}/{cap2}")
        return "Variable" + unit, "--"
    except: return "--", "--"

def main():
    if len(sys.argv) < 2: return
    class_code = sys.argv[1].lower()
    mod_path, base_strings_path = "mods/BKDiablo/bkdiablo.mpq", "data/base/strings"
    strings = load_all_strings(mod_path, base_strings_path)
    skills = load_tsv(os.path.join(mod_path, "data/global/excel/skills.txt"))
    skilldescs = load_tsv(os.path.join(mod_path, "data/global/excel/skilldesc.txt"))
    missiles = load_tsv(os.path.join(mod_path, "data/global/excel/missiles.txt"))
    skill_map, missile_map, desc_map = {s['skill'].lower(): s for s in skills}, {m['Missile'].lower(): m for m in missiles}, {d['skilldesc']: d for d in skilldescs}
    class_mapping = {'nec':"Necromancer", 'bar':"Barbarian", 'ama':"Amazon", 'sor':"Sorceress", 'pal':"Paladin", 'dru':"Druid", 'asn':"Assassin", 'war':"Warlock"}
    class_skills = [s for s in skills if s.get('charclass') == class_code]
    output = f"# {class_mapping.get(class_code, class_code.upper())} Skill Tree (BKDiablo)\n\n"
    for s in class_skills:
        desc_row = desc_map.get(s['skilldesc'])
        if not desc_row: continue
        real_name = strings.get(desc_row.get('skillname', '').lower(), s['skill'])
        output += f"## {real_name}\n\n| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |\n| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n"
        for i in range(1, 7):
            if not desc_row.get(f"descline{i}") or desc_row.get(f"descline{i}") == '0': continue
            text_label = strings.get(desc_row.get(f"desctexta{i}", "").lower(), desc_row.get(f"desctexta{i}", ""))
            unit = "%" if "%%" in text_label or "percent" in text_label.lower() else ("s" if "second" in text_label.lower() else ("y" if "yard" in text_label.lower() else ""))
            if "per second" in text_label.lower(): unit = " dmg/s"
            c1, c2 = desc_row.get(f"desccalca{i}", ""), desc_row.get(f"desccalcb{i}", "")
            label = format_generic_label(text_label)
            if "%d-%d" in text_label:
                scaling, cap = analyze_range_scaling(c1, c2, s, unit, skill_map, missile_map, desc_row)
                v1, v10, v20, v30 = resolve_calc(c1, s, 1, 1, skill_map, missile_map, desc_row), resolve_calc(c1, s, 10, 10, skill_map, missile_map, desc_row), resolve_calc(c1, s, 20, 20, skill_map, missile_map, desc_row), resolve_calc(c1, s, 30, 20, skill_map, missile_map, desc_row)
                v1b, v10b, v20b, v30b = resolve_calc(c2, s, 1, 1, skill_map, missile_map, desc_row), resolve_calc(c2, s, 10, 10, skill_map, missile_map, desc_row), resolve_calc(c2, s, 20, 20, skill_map, missile_map, desc_row), resolve_calc(c2, s, 30, 20, skill_map, missile_map, desc_row)
                output += f"| {label} | {scaling} | {v1}-{v1b}{unit} | {v10}-{v10b}{unit} | {v20}-{v20b}{unit} | {v30}-{v30b}{unit} | {cap} |\n"
            else:
                scaling, cap = analyze_scaling(c1, s, unit, skill_map, missile_map, desc_row)
                v1, v10, v20, v30 = resolve_calc(c1, s, 1, 1, skill_map, missile_map, desc_row), resolve_calc(c1, s, 10, 10, skill_map, missile_map, desc_row), resolve_calc(c1, s, 20, 20, skill_map, missile_map, desc_row), resolve_calc(c1, s, 30, 20, skill_map, missile_map, desc_row)
                prefix = "+" if "%+" in text_label and not str(v1).startswith('-') else ""
                output += f"| {label} | {scaling} | {prefix}{v1}{unit} | {prefix}{v10}{unit} | {prefix}{v20}{unit} | {prefix}{v30}{unit} | {cap} |\n"
        synergies = []
        for dsc in ['dsc2', 'dsc3']:
            for i in range(1, 8):
                if desc_row.get(f"{dsc}line{i}") in ['76', '77']:
                    text_id = desc_row.get(f"{dsc}texta{i}", "").lower()
                    label_t, syn_id = strings.get(text_id, ""), desc_row.get(f"{dsc}textb{i}", "").lower()
                    syn_n = strings.get(syn_id, syn_id)
                    val = resolve_calc(desc_row.get(f"{dsc}calca{i}", ""), s, 1, 1, skill_map, missile_map, desc_row)
                    output_syn = f"+{val}% Damage per Level"
                    if "Magic" in label_t: output_syn = f"+{val}% Magic Damage per Level"
                    elif "Poison" in label_t: output_syn = f"+{val}% Poison Damage per Level"
                    elif "HP" in label_t: output_syn = f"+{val}% HP per Level"
                    synergies.append(f"* **{syn_n}**: {output_syn}")
        if synergies: output += "\n### Synergies\n" + "\n".join(synergies) + "\n"
        output += "\n---\n\n"
    with open(f"{class_code}_skills.md", "w", encoding='utf-8') as f: f.write(output)
    print(f"Exported to {class_code}_skills.md")

if __name__ == "__main__": main()
