import csv, os, json, re, sys

def load_tsv(filepath):
    if not os.path.exists(filepath): return []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        if not lines: return []
        header = [h.strip() for h in lines[0].split('\t')]
        return [dict(zip(header, [v.strip() for v in l.split('\t')])) for l in lines[1:] if len(l.split('\t')) >= len(header)]

def load_all_strings(mod_path, base_strings_path):
    strings = {}
    paths = [base_strings_path, os.path.join(mod_path, "data/local/lng/strings")]
    for p in paths:
        if os.path.exists(p):
            for f in os.listdir(p):
                if f.endswith(".json"):
                    with open(os.path.join(p, f), 'r', encoding='utf-8-sig') as f:
                        try:
                            for entry in json.load(f):
                                k, v = entry.get('Key'), entry.get('enUS')
                                if k and v: strings[k.lower()] = v
                        except: continue
    return strings

def get_dam_generic(s, lvl, prefix):
    try:
        base = int(s.get(prefix, '0') or '0')
        p_root = prefix
        for r in ['EMin','EMax','MinDam','MaxDam']:
             if prefix.startswith(r):
                  p_root = r.replace('EMin','MinE').replace('EMax','MaxE').replace('MinDam','Min').replace('MaxDam','Max')
                  break
        add = 0
        for i in range(1, lvl):
            if i < 8: add += int(s.get(f'{p_root}Lev1', '0') or '0')
            elif i < 16: add += int(s.get(f'{p_root}Lev2', '0') or '0')
            elif i < 22: add += int(s.get(f'{p_root}Lev3', '0') or '0')
            elif i < 28: add += int(s.get(f'{p_root}Lev4', '0') or '0')
            else: add += int(s.get(f'{p_root}Lev5', '0') or '0')
        return base + add
    except: return 0

def get_skill_val(s, lvl, blvl, var, skill_map, missile_map, desc_row=None, depth=0):
    if depth > 15: return 0
    try:
        def p(n): return int(s.get(f"Param{n}", "0") or "0")
        if re.match(r'ln\d+', var):
            v = re.match(r'ln(\d+)', var).group(1)
            return p(int(v[0])) + (lvl - 1) * p(int(v[1:]))
        if re.match(r'dm\d+', var):
            v = re.match(r'dm(\d+)', var).group(1)
            p1, p2 = int(v[0]), int(v[1:])
            return ((110 * lvl) * (p(p2) - p(1))) // (100 * (lvl + 6)) + p(1)
        if var in ['macr','madm','math']:
            off = 1 if var=='macr' else (3 if var=='madm' else 5)
            return p(off) + (lvl - 1) * p(off+1)
        if var == 'edln':
            elen = int(s.get('ELen', '0') or '0')
            elevlen = sum([int(s.get(f'ELevLen{i}', '0') or '0') for i in range(1, 4)])
            return elen + elevlen * (lvl - 1)
        if var in ['mps', 'usmc']:
            val = max(int(s.get('minmana', '0') or '0'), int(s.get('mana', '0') or '0') + int(s.get('lvlmana', '0') or '0') * (lvl - 1))
            shift = int(s.get('manashift', '8') or '8')
            return val / (2**shift) if shift != 8 else val
        if var == 'toht': return int(s.get('ToHit', '0') or '0') + int(s.get('LevToHit', '0') or '0') * (lvl - 1)
        if var in ['pnma','edmn']: return get_dam_generic(s, lvl, 'MinDam')
        if var in ['pxma','edmx']: return get_dam_generic(s, lvl, 'MaxDam')
        if var == 'enma': return get_dam_generic(s, lvl, 'EMin')
        if var == 'exma': return get_dam_generic(s, lvl, 'EMax')
        if var == 'mael':
             m = skill_map.get(f'passive_{s.get(