import os
import re
import difflib
from typing import List, Dict, Optional, Any, Tuple
from d2_repository import D2Repository, normalize_d2_value
from d2_models import PropertyDTO, AnalyzedItemDTO, RunewordDTO, ExcelDiffDTO, ExcelDiffRowDTO, CubeRecipeDTO, ItemDiffDTO

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
        self.class_abbr_map = {'ama': 'Amazon', 'sor': 'Sorceress', 'nec': 'Necromancer', 'pal': 'Paladin', 'bar': 'Barbarian', 'dru': 'Druid', 'ass': 'Assassin', 'war': 'Warlock'}
        
        self.skill_to_class = {}
        for row in skills_data:
            s_name = row.get('skill', '').strip().lower()
            s_id = row.get('*Id') or row.get('Id') or row.get('*ID') or row.get('ID')
            charclass = row.get('charclass', '').strip().lower()
            if charclass:
                if s_name: self.skill_to_class[s_name] = charclass
                if s_id: self.skill_to_class[str(s_id).strip()] = charclass

        self.skill_tab_names = {
            '0': 'Bow and Crossbow', '1': 'Passive and Magic', '2': 'Javelin and Spear',
            '3': 'Fire', '4': 'Lightning', '5': 'Cold', '6': 'Curses', '7': 'Poison and Bone',
            '8': 'Summoning', '9': 'Combat', '10': 'Offensive Auras', '11': 'Defensive Auras',
            '12': 'Combat', '13': 'Combat Masteries', '14': 'Warcries', '15': 'Summoning',
            '16': 'Shape Shifting', '17': 'Elemental', '18': 'Traps', '19': 'Shadow Disciplines',
            '20': 'Martial Arts', '21': 'Warlock'
        }
        
        self.manual_overrides = {
            'bloody': 'Unknown property: bloody',
            'gelid-affix5': 'Unknown property: Gelid-Affix5'
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
        
        try: 
            v_min = int(min_val) if min_val else 0
            v_max = int(max_val) if max_val else 0
        except ValueError: 
            v_min, v_max = 0, 0

        # Handle descfunc 19 (By Character Level)
        desc_func = stat.get('descfunc', '0').strip()
        op_base = stat.get('op base', '').strip().lower()
        is_level_stat = op_base == 'level'
        
        if desc_func == '19' and is_level_stat:
            op_param_raw = stat.get('op param', '0').strip()
            op_param = int(op_param_raw) if op_param_raw else 0
            factor = 2 ** op_param
            
            p_min = v_min / factor
            p_max = v_max / factor
            
            p_range = f"{p_min:.1f}" if p_min == p_max else f"{p_min:.1f}-{p_max:.1f}"
            
            fmt_string = self.repo.get_string(str_pos if v_min >= 0 else str_neg)
            if not fmt_string: return None
            
            # Remove value placeholders and any leading +/- or % from the remaining string
            clean_fmt = fmt_string.replace('%+d', '').replace('%d', '').replace('%%', '').strip()
            if clean_fmt.startswith('+') or clean_fmt.startswith('-'): clean_fmt = clean_fmt[1:].strip()
            if clean_fmt.startswith('%'): clean_fmt = clean_fmt[1:].strip()
            
            # Construct (X% per clvl) prefix
            pct = "%" if '%%' in fmt_string else ""
            prefix = f"({p_range}{pct} per clvl) "
            
            res = prefix + clean_fmt
            if str_2: res += " " + self.repo.get_string(str_2)
            return res

        range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
        fmt_string = self.repo.get_string(str_pos if v_min >= 0 else str_neg)
        if not fmt_string: return None
        sign = "+" if v_min >= 0 else ""
        if "%+d" in fmt_string: 
            # Avoid double signs if range_str already has one
            display_range = range_str
            if range_str.startswith('+') or range_str.startswith('-'):
                fmt_string = fmt_string.replace("%+d", display_range)
            else:
                fmt_string = fmt_string.replace("%+d", f"{sign}{display_range}")
        elif "%d" in fmt_string: 
            fmt_string = fmt_string.replace("%d", range_str)
        fmt_string = fmt_string.replace("%%", "%")
        if str_2: fmt_string += " " + self.repo.get_string(str_2)
        return fmt_string

    def resolve_property(self, code: str, param: str, min_val: str, max_val: str) -> PropertyDTO:
        code_orig = code
        code_lower = code.strip().lower()
        
        if not code_lower or code_lower == 'xxx':
            return {"code": code, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": ""}

        if code_lower in self.aliases: code_lower = self.aliases[code_lower]
        
        # 1. Manual Overrides
        if code_lower in self.manual_overrides:
            text = self.manual_overrides[code_lower]
            range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": f"{text} ({range_str})" if range_str else text}

        # 2. Property Groups
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
            range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": f"Unknown property: {code_orig} ({range_str})"}
        
        func1 = prop.get('func1', '0').strip()
        
        # Use param if min_val is empty and it's a per-level stat (func 17)
        actual_min, actual_max = min_val, max_val
        if func1 == '17' and not actual_min and param:
            actual_min, actual_max = param, param

        range_str = f"{actual_min}" if actual_min == actual_max else f"{actual_min}-{actual_max}"

        # Check if it's a level scaling stat to prefer format_desc over tooltip
        stat1_code = prop.get('stat1', '').lower()
        stat1 = self.stats.get(stat1_code)
        is_level_stat = stat1 and stat1.get('op base', '').strip().lower() == 'level'

        tooltip = prop.get('*Tooltip', '').strip()
        if tooltip and tooltip != '0' and not is_level_stat:
            func, val1 = prop.get('func1', '0').strip(), prop.get('val1', '0').strip()
            res_text = tooltip
            # Correct D2 placeholder logic: Handle multiple '#' symbols
            if func in ['36', '14']:
                res_text = res_text.replace('#', val1)
            else:
                if res_text.count('#') > 1 and '-' in range_str:
                    parts = range_str.split('-')
                    for part in parts:
                        res_text = res_text.replace('#', part, 1)
                else:
                    res_text = res_text.replace('#', range_str)

            if '[Class Skill Tab]' in res_text: res_text = res_text.replace('[Class Skill Tab]', self.skill_tab_names.get(str(param), f"Tab {param}"))
            if '[Class]' in res_text:
                if func == '36': cls = 'Random Class' if actual_min != actual_max else self.class_names.get(actual_min, f"Class {actual_min}")
                else: 
                    set1 = prop.get('set1', '').strip()
                    cls_id = set1 if set1 and set1 != '0' else param
                    cls = self.class_names.get(str(cls_id))
                    if not cls:
                        # Try lookup by skill class
                        skill_cls_abbr = self.skill_to_class.get(str(param).strip().lower())
                        if skill_cls_abbr:
                            cls = self.class_abbr_map.get(skill_cls_abbr)
                    if not cls: cls = "Class"
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
                desc = self.format_desc(stat_code, actual_min, actual_max)
                if desc: return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": desc}
        
        # New Fallback Logic: Try resolving via the code name itself
        localized_code = self.repo.get_string(code_orig)
        if not localized_code or localized_code == code_orig:
            localized_code = self.repo.get_string(code_orig.capitalize())
        
        if localized_code and localized_code != code_orig and localized_code != code_orig.capitalize():
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": f"{localized_code}: {range_str}"}

        return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": f"Unknown property: {code_orig} ({range_str})"}

class ItemAnalyzerService:
    def __init__(self, repo: D2Repository, resolver: PropertyResolverService):
        self.repo = repo
        self.resolver = resolver
        self.armor = {row['code']: row for row in repo.get_excel_table('armor')}
        self.weapons = {row['code']: row for row in repo.get_excel_table('weapons')}
        self.misc = {row['code']: row for row in repo.get_excel_table('misc')}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}
        self.sets = {row['name']: row for row in repo.get_excel_table('sets')}

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

    def get_granular_group(self, category: str) -> str:
        cat_lower = category.lower()
        # Weapons
        if any(cls in cat_lower for cls in ['amazon', 'assassin', 'orb', 'hand to hand', 'grimoire']): return 'Class Weapons'
        if 'axe' in cat_lower: return 'Axes'
        if 'bow' in cat_lower: return 'Bows'
        if 'crossbow' in cat_lower: return 'Crossbows'
        if 'dagger' in cat_lower or 'knife' in cat_lower: return 'Daggers'
        if 'javelin' in cat_lower: return 'Javelins'
        if 'mace' in cat_lower or 'club' in cat_lower or 'hammer' in cat_lower: return 'Maces'
        if 'polearm' in cat_lower: return 'Polearms'
        if 'scepter' in cat_lower: return 'Scepters'
        if 'spear' in cat_lower: return 'Spears'
        if 'staff' in cat_lower: return 'Staves'
        if 'sword' in cat_lower: return 'Swords'
        if 'throwing' in cat_lower: return 'Throwing'
        if 'wand' in cat_lower: return 'Wands'
        
        # Others
        if any(cls in cat_lower for cls in ['voodoo', 'pelt', 'primal', 'auric']): return 'Class Armors'
        if 'amulet' in cat_lower: return 'Amulets'
        if 'ring' in cat_lower: return 'Rings'
        if 'charm' in cat_lower: return 'Charms'
        if 'jewel' in cat_lower: return 'Jewels'
        if any(h in cat_lower for h in ['helm', 'circlet', 'merc']): return 'Helms'
        if any(c in cat_lower for c in ['armor', 'tors']): return 'Chests'
        if 'shield' in cat_lower: return 'Shields'
        if 'glove' in cat_lower: return 'Gloves'
        if 'belt' in cat_lower: return 'Belts'
        if 'boot' in cat_lower: return 'Boots'
        
        return 'Others'

    def get_top_level_group(self, granular_group: str) -> str:
        weapons = ['Class Weapons', 'Axes', 'Bows', 'Crossbows', 'Daggers', 'Javelins', 'Maces', 'Polearms', 'Scepters', 'Spears', 'Staves', 'Swords', 'Throwing', 'Wands']
        if granular_group in weapons:
            return "Weapons"
        return "Others"

    def analyze_unique(self, row: Dict[str, str]) -> AnalyzedItemDTO:
        idx = row.get('index', '').strip()
        props = []
        for i in range(1, 13):
            code = row.get(f'prop{i}', '').strip()
            if code and code != 'xxx':
                props.append(self.resolver.resolve_property(code, row.get(f'par{i}', ''), row.get(f'min{i}', ''), row.get(f'max{i}', '')))
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
            if code and code != 'xxx':
                props.append(self.resolver.resolve_property(code, row.get(f'T1Param{i}', ''), row.get(f'T1Min{i}', ''), row.get(f'T1Max{i}', '')))
        
        itype = row.get('itype1', '').strip()
        base_items = [self.repo.get_string(self.item_types.get(itype, {}).get('ItemType', '')) or itype]
        
        return {
            "name": name, "runes": runes, "base_items": base_items,
            "properties": props, "raw_row": row
        }

    def analyze_set_item(self, row: Dict[str, str]) -> AnalyzedItemDTO:
        idx = row.get('index', '').strip()
        props = []
        for i in range(1, 10):
            code = row.get(f'prop{i}', '').strip()
            if code and code != 'xxx':
                props.append(self.resolver.resolve_property(code, row.get(f'par{i}', ''), row.get(f'min{i}', ''), row.get(f'max{i}', '')))
        
        set_name = row.get('set', '').strip()
        set_info = self.sets.get(set_name, {})
        is_expansion = set_info.get('version', '0') != '0'
        
        item_code = row.get('item', '').strip()
        return {
            "id": idx, "display_name": self.repo.get_string(idx), "base_item": self.get_item_name(item_code),
            "item_type": self.get_item_category(item_code), "lvl_req": row.get('lvl req', '0'), "properties": props, 
            "raw_row": {**row, "is_expansion": is_expansion}
        }

class CubeAnalyzerService:
    def __init__(self, repo: D2Repository):
        self.repo = repo
        self.armor = {row['code']: row for row in repo.get_excel_table('armor')}
        self.weapons = {row['code']: row for row in repo.get_excel_table('weapons')}
        self.misc = {row['code']: row for row in repo.get_excel_table('misc')}
        self.item_types = {row['Code']: row for row in repo.get_excel_table('itemtypes')}
        
        # Prefixes and Suffixes use row index as ID
        prefix_data = repo.get_excel_table('magicprefix')
        self.prefixes = {str(i): row for i, row in enumerate(prefix_data)}
        
        suffix_data = repo.get_excel_table('magicsuffix')
        self.suffixes = {str(i): row for i, row in enumerate(suffix_data)}

    def get_item_name(self, code: str) -> str:
        if not code: return ""
        code = code.strip()
        code_lower = code.lower()
        if code_lower == "usetype": return "Input Item Type"
        if code_lower == "useitem": return "Input Item"
        if code_lower == "any": return "Any Item"
        
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if item:
            name = self.repo.get_string(item.get('namestr', '').strip() or item.get('name', '').strip())
            return name or code
        
        # Check item types
        it = self.item_types.get(code)
        if it:
            return self.repo.get_string(it.get('ItemType', '').strip()) or code
            
        return code

    def resolve_token(self, token: str) -> str:
        if not token: return ""
        token = token.strip().strip('"')
        
        # Handle quantity: "code,qty=3"
        qty = ""
        if ",qty=" in token:
            parts = token.split(",qty=", 1)
            token = parts[0]
            qty = f" (Qty: {parts[1]})"
        
        # Handle complex codes: "amu,mag" or "rin,mag,pre=372"
        parts = token.split(',')
        base_code = parts[0]
        name = self.get_item_name(base_code)
        
        qualities = {
            "low": "Low Quality", "nor": "Normal", "hi": "Superior", "mag": "Magic",
            "set": "Set", "uni": "Unique", "rar": "Rare", "ora": "Crafted", "tmp": "Tempered"
        }
        
        mods = []
        for p in parts[1:]:
            p = p.strip().lower()
            if p in qualities:
                mods.append(qualities[p])
            elif p.startswith("pre="):
                val = p.split("=")[1]
                pre = self.prefixes.get(val)
                pre_name = self.repo.get_string(pre.get('Name', '')) if pre else val
                mods.append(f"Prefix: {pre_name} ({val})")
            elif p.startswith("suf="):
                val = p.split("=")[1]
                suf = self.suffixes.get(val)
                suf_name = self.repo.get_string(suf.get('Name', '')) if suf else val
                mods.append(f"Suffix: {suf_name} ({val})")
            else:
                mods.append(p)
                
        res = name
        if mods:
            res += f" ({', '.join(mods)})"
        return f"{res}{qty}"

    def resolve_output(self, out: str, mod_str: str = "", mod_val: str = "") -> str:
        if not out: return ""
        res = self.resolve_token(out)
        qualities = {"low": "Low Quality", "nor": "Normal", "hi": "Superior", "mag": "Magic", "set": "Set", "uni": "Unique", "rar": "Rare", "ora": "Crafted", "tmp": "Tempered"}
        extra_mods = []
        if mod_str:
            parts = mod_str.split(',')
            for p in parts:
                p = p.strip().lower()
                if p in qualities: extra_mods.append(qualities[p])
                elif p == "pre":
                    pre = self.prefixes.get(mod_val)
                    pre_name = self.repo.get_string(pre.get('Name', '')) if pre else mod_val
                    extra_mods.append(f"Prefix: {pre_name} ({mod_val})")
                elif p == "suf":
                    suf = self.suffixes.get(mod_val)
                    suf_name = self.repo.get_string(suf.get('Name', '')) if suf else mod_val
                    extra_mods.append(f"Suffix: {suf_name} ({mod_val})")
                else: extra_mods.append(p)
        if extra_mods: res += f" [Extra: {', '.join(extra_mods)}]"
        return res

    def analyze_recipe(self, row: Dict[str, str]) -> CubeRecipeDTO:
        desc = row.get('description', 'Unknown Recipe').strip()
        enabled = row.get('enabled', '1').strip() == '1'
        actual_inputs = []
        for i in range(1, 8):
            val = row.get(f'input {i}', '').strip()
            if val and val != '0': actual_inputs.append(self.resolve_token(val))
        outputs = []
        for i in range(1, 4):
            out = row.get('output' if i == 1 else f'output {i}', '').strip()
            if out and out != '0':
                mod_str = row.get(f'mod {i}', '').strip()
                mod_val = row.get(f'mod {i} param', '').strip()
                outputs.append(self.resolve_output(out, mod_str, mod_val))
        return {"id": desc, "description": desc, "enabled": enabled, "inputs": actual_inputs, "outputs": outputs, "raw_row": row}

class ItemComparisonService:
    def __init__(self):
        pass

    def normalize_text(self, s: str) -> str:
        if not s: return ""
        s = re.sub(r'ÿc.', '', s)
        s = s.replace('•', '').replace('**', '')
        s = s.replace("Physical Damage Received Reduced by", "Damage Reduced by")
        s = re.sub(r'(Original|Random) Class', 'Random Class', s, flags=re.IGNORECASE)
        s = re.sub(r'\s+', ' ', s)
        return s.strip()

    def align_properties(self, old_props: List[str], new_props: List[str]) -> List[Tuple[str, str]]:
        def get_stat_key(s):
            s = self.normalize_text(s)
            return re.sub(r'[+-]?\d+(?:-\d+)?', '', s).strip().lower()

        aligned = []
        old_used, new_used = set(), set()
        for i, op in enumerate(old_props):
            onorm = self.normalize_text(op)
            for j, np in enumerate(new_props):
                if j in new_used: continue
                if onorm == self.normalize_text(np):
                    aligned.append((op, np))
                    old_used.add(i); new_used.add(j); break
        for i, op in enumerate(old_props):
            if i in old_used: continue
            okey = get_stat_key(op)
            for j, np in enumerate(new_props):
                if j in new_used: continue
                if okey == get_stat_key(np) and okey != "":
                    aligned.append((op, np))
                    old_used.add(i); new_used.add(j); break
        for i, op in enumerate(old_props):
            if i not in old_used: aligned.append((op, "(removed)"))
        for j, np in enumerate(new_props):
            if j not in new_used: aligned.append(("", np))
        return aligned

    def compare_item_lists(self, bk_items: Dict[str, Any], bt_items: Dict[str, Any]) -> ItemDiffDTO:
        added_ids = [k for k in bk_items if k not in bt_items]
        removed_ids = [k for k in bt_items if k not in bk_items]
        modified = {}
        common = [k for k in bk_items if k in bt_items]
        for k in common:
            bk, bt = bk_items[k], bt_items[k]
            
            bk_base = bk.get('base_item') or ', '.join(bk.get('base_items', []))
            bt_base = bt.get('base_item') or ', '.join(bt.get('base_items', []))
            bk_lvl = bk.get('lvl_req', '0')
            bt_lvl = bt.get('lvl_req', '0')

            header_diff = (self.normalize_text(bk_base) != self.normalize_text(bt_base) or 
                           self.normalize_text(bk_lvl) != self.normalize_text(bt_lvl))
            
            bk_norm = sorted([self.normalize_text(p['resolved_text']) for p in bk['properties']])
            bt_norm = sorted([self.normalize_text(p['resolved_text']) for p in bt['properties']])
            if header_diff or bk_norm != bt_norm:
                modified[k] = {
                    'name': bk.get('display_name') or bk.get('name'), 
                    'bk_base': bk_base, 'bt_base': bt_base,
                    'bk_lvl': bk_lvl, 'bt_lvl': bt_lvl,
                    'bk_props': [p['resolved_text'] for p in bk['properties']],
                    'bt_props': [p['resolved_text'] for p in bt['properties']]
                }
        return {
            'added': {k: bk_items[k] for k in added_ids},
            'removed': {k: bt_items[k] for k in removed_ids},
            'modified': modified
        }

class ExcelComparisonService:
    @staticmethod
    def compare_tables(table_bk: List[Dict[str, str]], table_bt: List[Dict[str, str]], key_col: str, filename: str) -> ExcelDiffDTO:
        map_new = {str(row[key_col]).strip().lower(): row for row in table_bk if row.get(key_col)}
        map_old = {str(row[key_col]).strip().lower(): row for row in table_bt if row.get(key_col)}
        h_new = list(table_bk[0].keys()) if table_bk else []; h_old = list(table_bt[0].keys()) if table_bt else []
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
