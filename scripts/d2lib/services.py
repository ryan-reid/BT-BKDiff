import os
import re
import difflib
from typing import List, Dict, Optional, Any, Tuple
from d2lib.repository import D2Repository, normalize_d2_value
from d2lib.models import PropertyDTO, AnalyzedItemDTO, RunewordDTO, ExcelDiffDTO, ExcelDiffRowDTO, CubeRecipeDTO, ItemDiffDTO, SkillTreeDTO, SkillDTO, SkillEffectDTO, SkillSynergyDTO

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
            'gelid-affix5': '(Missing Affix 5 data)',
            'incendiary-affix5': '(Missing Affix 5 data)',
            'magnetic-affix5': '(Missing Affix 5 data)',
            'virulent-affix5': '(Missing Affix 5 data)',
            'breaching-affix5': '(Missing Affix 5 data)',
            'mystical-affix5': '(Missing Affix 5 data)'
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
            # Avoid double negative if fmt_string has -%d and range_str starts with -
            if fmt_string.find("-%d") != -1 and display_range.startswith('-'):
                fmt_string = fmt_string.replace("-%d", display_range)
            else:
                fmt_string = fmt_string.replace("%d", display_range)
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
                    'bt_props': [p['resolved_text'] for p in bt['properties']],
                    'item_type': bk.get('item_type', 'Other'),
                    'raw_row': bk.get('raw_row', {})
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

class SkillAnalyzerService:
    def __init__(self, repo: D2Repository):
        self.repo = repo
        self.skills = {row.get('skill', '').strip().lower(): row for row in repo.get_excel_table('skills')}
        self.missiles = {row.get('Missile', '').strip().lower(): row for row in repo.get_excel_table('missiles')}
        self.skilldesc = {row.get('skilldesc', '').strip().lower(): row for row in repo.get_excel_table('skilldesc')}
        self.monstats = {row.get('Id', '').strip().lower(): row for row in repo.get_excel_table('monstats')}
        self.class_map = {"nec":"Necromancer", "bar":"Barbarian", "ama":"Amazon", "sor":"Sorceress", "pal":"Paladin", "dru":"Druid", "asn":"Assassin", "war":"Warlock"}

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

    def format_generic_label(self, s):
        if not s: return ""
        for c in ["%+d%%", "%d%%", "%+d", "%d", "%s"]: s = s.replace(c, "")
        return re.sub(r"\s+", " ", s.replace("-%d", "").replace("-%+d", "").replace("per second", "").replace("second", "").replace("yard", "")).strip(": -").strip()

    def build_effect_label(self, desc_row, line_index, raw_text, block="desc"):
        text_col = f"{block}texta{line_index}" if block != "desc" else f"desctexta{line_index}"
        text_key = desc_row.get(text_col, "")
        label = self.format_generic_label(raw_text)
        if label == "Damage" and ("percent" in raw_text.lower() or "damagepercent" in text_key.lower()):
            return "Damage %"
        if label == "Cold Length":
            return "Cold Duration"
        if label != "over":
            return label

        neighboring_labels = []
        for i in range(1, 7):
            if i == line_index:
                continue
            text_col = f"{block}texta{i}" if block != "desc" else f"desctexta{i}"
            text_key = desc_row.get(text_col, "").lower()
            text = self.repo.get_string(text_key) or desc_row.get(text_col, "")
            formatted = self.format_generic_label(text)
            if formatted:
                neighboring_labels.append(formatted.lower())

        if any("poison damage" in item for item in neighboring_labels):
            return "Poison Duration"
        if any("fire damage" in item for item in neighboring_labels):
            return "Fire Duration"
        if any("cold damage" in item for item in neighboring_labels):
            return "Cold Duration"
        return "Duration"

    def get_display_skill_level(self, skill_name: str, scenario_skill_levels: Optional[Dict[str, int]], fallback: int) -> int:
        if not scenario_skill_levels:
            return fallback
        key = re.sub(r"[\s']", "", skill_name.strip().lower())
        return int(scenario_skill_levels.get(key, fallback))

    def get_display_skill_levels(
        self,
        source_skill,
        target_skill_name: str,
        lvl: int,
        blvl: int,
        scenario_skill_levels: Optional[Dict[str, int]],
    ) -> Tuple[int, int]:
        source_names = {source_skill.get('skill', '').strip().lower()}
        desc_key = source_skill.get("skilldesc", "").lower()
        if desc_key in self.skilldesc:
            str_name_key = self.skilldesc[desc_key].get("str name", "").lower()
            display_name = (self.repo.get_string(str_name_key) or "").strip().lower()
            if display_name:
                source_names.add(display_name)

        target_name = target_skill_name.strip().lower()
        if target_name in source_names:
            return lvl, blvl

        ref_blvl = self.get_display_skill_level(target_skill_name, scenario_skill_levels, 0)
        soft_bonus = max(0, int(lvl) - int(blvl))
        return ref_blvl + soft_bonus, ref_blvl

    def get_display_damage_bonus_mult(self, skill, scenario_skill_levels: Optional[Dict[str, int]], damage_kind: str) -> float:
        if damage_kind == "physical":
            calc = skill.get('DmgSymPerCalc')
        elif damage_kind == "elemental":
            calc = skill.get('EDmgSymPerCalc') or skill.get('DmgSymPerCalc')
        else:
            calc = skill.get('EDmgSymPerCalc') or skill.get('DmgSymPerCalc')
        if not calc or calc == '0':
            return 1.0
        try:
            bonus = float(self.evaluate_display_formula(calc, skill, 1, 1, None, scenario_skill_levels, use_synergy=True))
            return 1.0 + (bonus / 100.0)
        except:
            return 1.0

    def get_summon_base_life(self, skill) -> float:
        summon_id = (skill.get('summon') or "").strip().lower()
        if not summon_id:
            return 0.0
        mon = self.monstats.get(summon_id)
        if not mon:
            return 0.0

        candidates = []
        for key in ['minHP', 'MinHP(N)', 'MinHP(H)', 'maxHP', 'MaxHP(N)', 'MaxHP(H)']:
            raw = mon.get(key, '')
            if raw in ('', '0'):
                continue
            try:
                candidates.append(float(raw))
            except ValueError:
                continue
        return max(candidates) if candidates else 0.0

    def get_display_missile(self, missile_name: str):
        key = (missile_name or "").strip().lower()
        if not key:
            return None
        row = self.missiles.get(key)
        if row:
            return row

        compact = key.replace(" ", "")
        row = self.missiles.get(compact)
        if row:
            return row

        aliases = {
            "eruption center": "coldfissure center",
        }
        alias_key = aliases.get(key)
        if alias_key:
            return self.missiles.get(alias_key)
        return None

    def get_display_synergy_bonus_mult(self, skill, scenario_skill_levels: Optional[Dict[str, int]]) -> float:
        return self.get_display_damage_bonus_mult(skill, scenario_skill_levels, "generic")

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
                if 'Immolation Arrow' in s.get('skill', ''):
                    return (self.get_display_skill_level('fire arrow', scenario_skill_levels, 0) + self.get_display_skill_level('exploding arrow', scenario_skill_levels, 0)) * 5.0
                syn_calc = s.get('EDmgSymPerCalc') or s.get('DmgSymPerCalc')
                if syn_calc:
                    return float(self.evaluate_display_formula(syn_calc, skill, 1, 1, desc_row, scenario_skill_levels, use_synergy=True))
                return 0.0
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
                    damage_kind = "elemental" if var in ['enma', 'edmn', 'exma', 'edmx', 'enms', 'exms'] else "physical"
                    res *= self.get_display_damage_bonus_mult(s, scenario_skill_levels, damage_kind)
                return res
            if var in ['edln', 'len']:
                res = self.get_display_raw_value(s, lvl, 'ELen')
                if use_synergy:
                    res *= self.get_display_elen_synergy_bonus_mult(s, scenario_skill_levels)
                return res
            if desc_row and var.startswith('m') and len(var) == 4:
                m_name = desc_row.get(f'descmissile{var[1]}')
                if m_name:
                    m = self.get_display_missile(m_name)
                    if m:
                        value_map = {'nm': 'MinDamage', 'xm': 'MaxDamage', 'eo': 'EMin', 'ey': 'EMax', 'rn': 'Range'}
                        val = self.get_display_raw_value(m, lvl, value_map.get(var[2:], ''))
                        if var[2:] == 'rn':
                            return val
                        shift = int(m.get('HitShift', '8') or '8')
                        res = val * (2.0 ** shift)
                        if use_synergy and var[2:] in ['eo', 'ey', 'nm', 'xm']:
                            damage_kind = "elemental" if var[2:] in ['eo', 'ey'] else "physical"
                            res *= self.get_display_damage_bonus_mult(s, scenario_skill_levels, damage_kind)
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
                    *self.get_display_skill_levels(skill, m.group(1), lvl, blvl, scenario_skill_levels),
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

    def calculate_display_effect_value(self, skill, desc_row, line_idx, lvl, blvl, block="", scenario_skill_levels: Optional[Dict[str, int]] = None) -> str:
        text_prefix = f"{block}texta" if block else "desctexta"
        line_prefix = f"{block}line" if block else "descline"
        calc_a_prefix = f"{block}calca" if block else "desccalca"
        calc_b_prefix = f"{block}calcb" if block else "desccalcb"

        text_raw = (self.repo.get_string(desc_row.get(text_prefix + str(line_idx), "").lower()) or "").replace('%d', '').replace('%+d', '').replace('%%', '%').strip(': ')
        c1, c2 = desc_row.get(calc_a_prefix + str(line_idx)), desc_row.get(calc_b_prefix + str(line_idx))
        is_range = ('-' in text_raw or '%d-%d' in text_raw)

        def get_val(calc):
            if not calc or calc == '':
                return 0.0
            val = self.evaluate_display_formula(calc, skill, lvl, blvl, desc_row, scenario_skill_levels, use_synergy=True)
            calc_str = str(calc).replace(' ', '')
            calc_str_lower = calc_str.lower()
            text_raw_lower = text_raw.lower()
            if '/256' not in calc_str and abs(val) > 100 and any(x in str(calc) for x in ['enma', 'exma', 'edmn', 'edmx', 'm1eo', 'm1ey', 'pnma', 'pxma', 'enms', 'exms']):
                val /= 256.0
            if (
                skill.get('skill', '').lower() == 'armageddon'
                and 'average fire damage' in text_raw_lower
                and any(token in calc_str_lower for token in ['m1eo', 'm1ey'])
            ):
                missile_name = desc_row.get('descmissile1', '')
                missile = self.get_display_missile(missile_name)
                if missile:
                    missile_range = self.get_display_raw_value(missile, lvl, 'Range')
                    if missile_range:
                        val *= (missile_range / 64.0)
            if 'poison damage' in text_raw_lower:
                elen = self.get_display_raw_value(skill, lvl, 'ELen')
                if 'm1' in str(calc):
                    m_name = desc_row.get('descmissile1')
                    m = self.get_display_missile(m_name) if m_name else None
                    if m:
                        elen = self.get_display_raw_value(m, lvl, 'ELen')
                if 'edln' not in str(calc).lower() and 'len' not in str(calc).lower():
                    val *= (elen / 256.0)
            if 'mana cost' in text_raw_lower and 'per second' in text_raw_lower:
                val *= 12.0
            line_type = desc_row.get(line_prefix + str(line_idx))
            if skill.get('skill', '').lower() == 'eruption' and 'duration' in text_raw_lower and "miss('eruptioncenter'.rang)" in calc_str_lower:
                val /= 50.0
            elif line_type in ['12', '31'] or ('second' in text_raw_lower and 'per second' not in text_raw_lower):
                if val >= 15:
                    val /= 25.0
            if line_type == '36' and any(token in text_raw_lower for token in ['radius', 'range']):
                if 'par3*2' in calc_str_lower:
                    val /= 2.0
                elif c2:
                    try:
                        divisor = float(c2)
                        if divisor:
                            val /= divisor
                    except ValueError:
                        pass
            if 'life' in text_raw_lower and line_type == '13':
                base_life = self.get_summon_base_life(skill)
                if base_life > 0 and skill.get('charclass') == 'dru':
                    val = base_life * (1.0 + (val / 100.0))
                else:
                    val = 440.0 * (1.0 + (val + 400.0) / 100.0)
            return val

        v_min = get_val(c1)
        if 'mana cost' in text_raw.lower() and 'per second' in text_raw.lower():
            if is_range and c2:
                return f"{round(v_min):.0f}-{round(get_val(c2)):.0f}"
            return f"{round(v_min):.0f}"
        if is_range and c2:
            return f"{v_min:.2f}-{get_val(c2):.2f}"
        return f"{v_min:.2f}"

    def get_skill_display_effects(self, skill_name: str, lvl: int, blvl: int, scenario_skill_levels: Optional[Dict[str, int]] = None) -> List[Dict[str, str]]:
        skill = self.skills[skill_name.lower()]
        desc_row = self.skilldesc[skill.get("skilldesc", "").lower()]
        effects = []
        for block in ["", "dsc2", "dsc3"]:
            text_prefix = f"{block}texta" if block else "desctexta"
            line_prefix = f"{block}line" if block else "descline"
            for i in range(1, 10):
                if not desc_row.get(f"{line_prefix}{i}") or desc_row.get(f"{line_prefix}{i}") == '0':
                    continue
                text_label = self.repo.get_string(desc_row.get(f"{text_prefix}{i}", "").lower()) or desc_row.get(f"{text_prefix}{i}", "")
                if not text_label:
                    continue
                label = self.build_effect_label(desc_row, i, text_label, "desc" if not block else block)
                value = self.calculate_display_effect_value(skill, desc_row, i, lvl, blvl, block, scenario_skill_levels)
                unit = "%" if "%%" in text_label or "percent" in text_label.lower() else ("s" if "second" in text_label.lower() else ("y" if "yard" in text_label.lower() else ""))
                if "mana cost" in text_label.lower() and "per second" in text_label.lower():
                    unit = ""
                elif "per second" in text_label.lower():
                    unit = " dmg/s"
                prefix = "+" if "%+" in text_label and not str(value).startswith("-") else ""
                if "%d-%d" in text_label or '-' in value[1:]:
                    formatted_value = f"{value}{unit}"
                else:
                    formatted_value = f"{prefix}{value}{unit}"
                effects.append({"label": label, "value": formatted_value, "block": block or "desc"})
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
            skill_name = self.repo.get_string(skill_name_key) or self.repo.get_string(s['skill']) or s['skill']
            
            effects = []
            for i in range(1, 7):
                if not dr.get(f"descline{i}") or dr.get(f"descline{i}") == "0": continue
                text_key = dr.get(f"desctexta{i}", "").lower()
                tl = self.repo.get_string(text_key) or dr.get(f"desctexta{i}", "")
                
                unit = "%" if "%%" in tl or "percent" in tl.lower() else ("s" if "second" in tl.lower() else ("y" if "yard" in tl.lower() else ""))
                if "per second" in tl.lower(): unit = " dmg/s"
                
                c1, c2 = dr.get(f"desccalca{i}", ""), dr.get(f"desccalcb{i}", "")
                label = self.build_effect_label(dr, i, tl)
                
                if "%d-%d" in tl:
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
                    if dr.get(f"{dsc}line{i}") in ["76", "77"]:
                        t_key = dr.get(f"{dsc}texta{i}", "").lower()
                        t = self.repo.get_string(t_key) or ""
                        sid_key = dr.get(f"{dsc}textb{i}", "").lower()
                        sid_name = self.repo.get_string(sid_key) or sid_key
                        
                        val = self.resolve_calc(dr.get(f"{dsc}calca{i}", ""), s, 1, 1, dr)
                        ut = f"+{val}% Magic Damage" if "Magic" in t else (f"+{val}% Poison Damage" if "Poison" in t else (f"+{val}% HP" if "HP" in t else f"+{val}% Damage"))
                        synergies.append({"name": sid_name, "effect": f"{ut} per Level"})
            
            skills_dto.append({
                "id": skill_id,
                "name": skill_name,
                "effects": effects,
                "synergies": synergies,
                "raw_row": s
            })
            
        return {"class_name": class_name, "skills": skills_dto}

