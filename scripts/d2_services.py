import os
from typing import List, Dict, Optional, Any
from d2_repository import D2Repository, normalize_d2_value
from d2_models import PropertyDTO, AnalyzedItemDTO, RunewordDTO, ExcelDiffDTO, ExcelDiffRowDTO

class PropertyResolverService:
    def __init__(self, repo: D2Repository, property_groups: Optional[List[Dict[str, str]]] = None):
        self.repo: D2Repository = repo
        self.property_groups: Dict[str, Dict[str, str]] = {
            row['code'].strip().lower(): row for row in property_groups
        } if property_groups else {}
        
        self.aliases: Dict[str, str] = {
            'cast': 'cast1', 'balance': 'balance1', 'move': 'move1', 'swing': 'swing1',
            'block': 'block1', 'cold-res': 'res-cold', 'fire-res': 'res-fire',
            'ltng-res': 'res-ltng', 'pois-res': 'res-pois', 'all-res': 'res-all',
            'ern%': 'enr%', 'res-poi-len': 'res-pois-len', 'get-hit-skill': 'gethit-skill'
        }

        self.properties = {row.get('code', '').strip().lower(): row for row in repo.get_excel_table('properties')}
        self.stats = {row.get('Stat', '').strip().lower(): row for row in repo.get_excel_table('itemstatcost')}
        
        skills_data = repo.get_excel_table('skills')
        self.skills = {row.get('skill', '').strip().lower(): row for row in skills_data}
        self.skills_by_id = {}
        for row in skills_data:
            s_id = row.get('*Id') or row.get('Id') or row.get('*ID') or row.get('ID')
            if s_id: self.skills_by_id[str(s_id).strip()] = row

        self.skill_desc = {row.get('skilldesc', '').strip().lower(): row for row in repo.get_excel_table('skilldesc')}
        self.class_names = {'0': 'Amazon', '1': 'Sorceress', '2': 'Necromancer', '3': 'Paladin', '4': 'Barbarian', '5': 'Druid', '6': 'Assassin', '7': 'Warlock'}
        self.skill_tab_names = {
            '0': 'Bow and Crossbow', '1': 'Passive and Magic', '2': 'Javelin and Spear',
            '3': 'Fire', '4': 'Lightning', '5': 'Cold', '6': 'Curses', '7': 'Poison and Bone',
            '8': 'Summoning', '9': 'Combat', '10': 'Offensive Auras', '11': 'Defensive Auras',
            '12': 'Combat', '13': 'Combat Masteries', '14': 'Warcries', '15': 'Summoning',
            '16': 'Shape Shifting', '17': 'Elemental', '18': 'Traps', '19': 'Shadow Disciplines',
            20: 'Martial Arts', '21': 'Warlock'
        }

    def resolve_skill_name(self, skill_name_or_id: str) -> str:
        skill_name_or_id = str(skill_name_or_id).strip()
        if not skill_name_or_id or skill_name_or_id == '0': return skill_name_or_id
        skill = self.skills_by_id.get(skill_name_or_id) if skill_name_or_id.isdigit() else self.skills.get(skill_name_or_id.lower())
        if skill:
            desc_key = skill.get('skilldesc', '').strip().lower()
            if desc_key in self.skill_desc:
                str_name_key = self.skill_desc[desc_key].get('str name', '').strip()
                resolved = self.repo.get_string(str_name_key)
                if resolved: return resolved
            return skill.get('skill', '').strip()
        return skill_name_or_id

    def format_desc(self, stat_code: str, min_val: str, max_val: str) -> Optional[str]:
        stat = self.stats.get(stat_code.lower())
        if not stat: return None
        str_pos, str_neg, str_2 = stat.get('descstrpos', '').strip(), stat.get('descstrneg', '').strip(), stat.get('descstr2', '').strip()
        if not str_pos: return None
        try: val = int(min_val) if min_val else 0
        except ValueError: val = 0
        range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
        fmt_string = self.repo.get_string(str_pos if val >= 0 else str_neg)
        if not fmt_string: return None
        sign = "+" if val >= 0 else ""
        if "%+d" in fmt_string: fmt_string = fmt_string.replace("%+d", f"{sign}{range_str}")
        elif "%d" in fmt_string: fmt_string = fmt_string.replace("%d", f"{range_str}")
        fmt_string = fmt_string.replace("%%", "%")
        if str_2: fmt_string += " " + self.repo.get_string(str_2)
        return fmt_string

    def resolve_property(self, code: str, param: str, min_val: str, max_val: str) -> PropertyDTO:
        code_orig = code
        code_lower = code.strip().lower()
        if not code_lower or code_lower == 'xxx':
            return {"code": code, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": ""}

        if code_lower in self.aliases: code_lower = self.aliases[code_lower]
        
        if code_lower in self.property_groups:
            group = self.property_groups[code_lower]
            pick_mode = group.get('PickMode', '1')
            options = []
            for i in range(1, 9):
                p_code = group.get(f'Prop{i}', '').strip()
                if p_code and p_code != 'xxx':
                    res = self.resolve_property(p_code, group.get(f'ParMin{i}', ''), group.get(f'ModMin{i}', ''), group.get(f'ModMax{i}', ''))
                    options.append(res['resolved_text'])
            text = " / ".join(options) if pick_mode == '1' else f" (Random: {' OR '.join(options)})"
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": text}

        prop = self.properties.get(code_lower)
        if not prop:
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": f"Unknown Prop: {code}"}
        
        range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
        tooltip = prop.get('*Tooltip', '').strip()
        if tooltip and tooltip != '0':
            func, val1 = prop.get('func1', '0').strip(), prop.get('val1', '0').strip()
            res_text = tooltip.replace('#', val1 if func in ['36', '14'] else range_str)
            if '[Class Skill Tab]' in res_text: res_text = res_text.replace('[Class Skill Tab]', self.skill_tab_names.get(param, f"Tab {param}"))
            if '[Class]' in res_text:
                if func == '36': cls = 'Random Class' if min_val != max_val else self.class_names.get(min_val, f"Class {min_val}")
                else: 
                    set1 = prop.get('set1', '').strip()
                    cls = self.class_names.get(set1 if set1 and set1 != '0' else param, "Class")
                res_text = res_text.replace('[Class]', cls)
            if '[Skill]' in res_text or '%s' in res_text:
                skill_name = self.resolve_skill_name(param)
                res_text = res_text.replace('[Skill]', skill_name).replace('%s', skill_name)
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": res_text}

        skill_codes = ['oskill', 'skill', 'att-skill', 'hit-skill', 'gethit-skill', 'kill-skill', 'death-skill', 'level-skill', 'aura']
        if code_lower in skill_codes:
            skill_name = self.resolve_skill_name(param)
            templates = {'oskill': f"+{range_str} to {skill_name}", 'skill': f"+{range_str} to {skill_name}", 'aura': f"Level {range_str} {skill_name} Aura When Equipped", 'hit-skill': f"{min_val}% Chance to cast Level {max_val} {skill_name} on striking", 'att-skill': f"{min_val}% Chance to cast Level {max_val} {skill_name} on striking", 'gethit-skill': f"{min_val}% Chance to cast Level {max_val} {skill_name} when struck", 'kill-skill': f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Kill an Enemy", 'death-skill': f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Die", 'level-skill': f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Level-Up"}
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": templates.get(code_lower, "")}

        for i in range(1, 8):
            stat_code = prop.get(f'stat{i}', '').strip()
            if stat_code:
                desc = self.format_desc(stat_code, min_val, max_val)
                if desc: return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": desc}
        
        return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": f"{prop.get('stat1', code_lower)}: {range_str}"}

class ItemAnalyzerService:
    def __init__(self, repo: D2Repository, resolver: PropertyResolverService):
        self.repo = repo
        self.resolver = resolver
        self.armor = {row['code']: row for row in repo.get_excel_table('armor')}
        self.weapons = {row['code']: row for row in repo.get_excel_table('weapons')}
        self.misc = {row['code']: row for row in repo.get_excel_table('misc')}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}

    def get_item_name(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if item: return self.repo.get_string(item.get('namestr', '').strip() or item.get('name', '').strip()) or code
        return code

    def get_item_category(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if not item: return "Miscellaneous"
        type_code = item.get('type', '').strip()
        item_type = self.item_types.get(type_code)
        return self.repo.get_string(item_type.get('ItemType', 'Unknown').strip()) if item_type else "Miscellaneous"

    def analyze_unique(self, row: Dict[str, str]) -> AnalyzedItemDTO:
        idx = row.get('index', '').strip()
        props = []
        for i in range(1, 13):
            code = row.get(f'prop{i}', '').strip()
            if code and code != 'xxx': props.append(self.resolver.resolve_property(code, row.get(f'par{i}', ''), row.get(f'min{i}', ''), row.get(f'max{i}', '')))
        return {
            "id": idx, "display_name": self.repo.get_string(idx), "base_item": self.get_item_name(row.get('code', '').strip()),
            "item_type": self.get_item_category(row.get('code', '').strip()), "lvl_req": row.get('lvl req', '0'), "properties": props, "raw_row": row
        }

    def analyze_runeword(self, row: Dict[str, str]) -> RunewordDTO:
        name = row.get('*Rune Name', row.get('Name', 'Unknown')).strip()
        runes = []
        for i in range(1, 7):
            r_code = row.get(f'Rune{i}', '').strip()
            if r_code and r_code != 'xxx': runes.append(self.get_item_name(r_code))
        props = []
        for i in range(1, 8):
            code = row.get(f'T1Code{i}', '').strip()
            if code and code != 'xxx': props.append(self.resolver.resolve_property(code, row.get(f'T1Param{i}', ''), row.get(f'T1Min{i}', ''), row.get(f'T1Max{i}', '')))
        return {
            "name": name, "runes": runes, "base_items": [self.repo.get_string(self.item_types.get(row.get('itype1', '').strip(), {}).get('ItemType', '')) or row.get('itype1', '')],
            "properties": props, "raw_row": row
        }

class ExcelComparisonService:
    @staticmethod
    def compare_tables(table_bk: List[Dict[str, str]], table_bt: List[Dict[str, str]], key_col: str, filename: str) -> ExcelDiffDTO:
        map_new = {str(row[key_col]).strip().lower(): row for row in table_bk if row.get(key_col)}
        map_old = {str(row[key_col]).strip().lower(): row for row in table_bt if row.get(key_col)}
        h_new = list(table_bk[0].keys()) if table_bk else []
        h_old = list(table_bt[0].keys()) if table_bt else []
        common_cols = [c for c in h_new if c in h_old]
        all_keys = sorted(set(map_new.keys()) | set(map_old.keys()))
        diff = {
            "filename": filename, "key_used": key_col, "added_cols": [c for c in h_new if c not in h_old],
            "removed_cols": [c for c in h_old if c not in h_new], "added_rows": [], "removed_rows": [], "modified_rows": {}
        }
        for key in all_keys:
            if key not in map_old: diff["added_rows"].append(key)
            elif key not in map_new: diff["removed_rows"].append(key)
            else:
                row_diff = {}
                for col in common_cols:
                    if normalize_d2_value(map_new[key][col]) != normalize_d2_value(map_old[key][col]):
                        row_diff[col] = {"bk_new": map_new[key][col], "bt_old": map_old[key][col]}
                if row_diff: diff["modified_rows"][key] = row_diff
        return diff
