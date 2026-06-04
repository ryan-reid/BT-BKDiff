from __future__ import annotations
import re
from typing import List, Dict, Optional, Any
from d2lib.repository import D2RepositoryProtocol
from d2lib.models import PropertyDTO

class PropertyResolverService:
    def __init__(self, repo: D2RepositoryProtocol, property_groups: Optional[List[Dict[str, str]]] = None):
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

        if code_lower in {"cold-len", "pois-len"}:
            element = "Cold" if code_lower == "cold-len" else "Poison"
            return {"code": code_orig, "param": param, "min_val": min_val, "max_val": max_val, "resolved_text": f"{element} Duration: {self._format_frame_duration(actual_min, actual_max)}"}

        # Check if it's a level scaling stat to prefer format_desc over tooltip
        stat1_code = prop.get('stat1', '').lower()
        stat1 = self.stats.get(stat1_code)
        is_level_stat = stat1 and stat1.get('op base', '').strip().lower() == 'level'

        tooltip = prop.get('*Tooltip', '').strip()
        if tooltip and tooltip != '0' and not is_level_stat:
            func, val1 = prop.get('func1', '0').strip(), prop.get('val1', '0').strip()
            res_text = tooltip
            display_range = range_str
            if "-#" in res_text:
                try:
                    display_min = str(abs(int(actual_min))) if actual_min else actual_min
                    display_max = str(abs(int(actual_max))) if actual_max else actual_max
                    display_range = display_min if display_min == display_max else f"{display_min}-{display_max}"
                except ValueError:
                    display_range = range_str
            # Correct D2 placeholder logic: Handle multiple '#' symbols
            if func in ['36', '14']:
                res_text = res_text.replace('#', val1)
            else:
                if res_text.count('#') > 1 and '-' in display_range:
                    parts = display_range.split('-')
                    for part in parts:
                        res_text = res_text.replace('#', part, 1)
                else:
                    res_text = res_text.replace('#', display_range)

            if code_lower == "pierce" and "#" not in tooltip and display_range:
                res_text = f"{display_range}% {res_text}"

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

    def _format_frame_duration(self, min_val: str, max_val: str) -> str:
        def parse_frames(raw: str) -> Optional[int]:
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None

        min_frames = parse_frames(min_val)
        max_frames = parse_frames(max_val)
        if min_frames is None and max_frames is None:
            return f"{min_val}-{max_val} frames" if min_val != max_val else f"{min_val} frames"
        if max_frames is None:
            max_frames = min_frames
        if min_frames is None:
            min_frames = max_frames

        def seconds_text(frames: int) -> str:
            seconds = frames / 25
            return str(int(seconds)) if seconds.is_integer() else f"{seconds:.1f}".rstrip("0").rstrip(".")

        if min_frames == max_frames:
            unit = "second" if min_frames == 25 else "seconds"
            return f"{seconds_text(min_frames)} {unit} ({min_frames} frames)"
        return f"{seconds_text(min_frames)}-{seconds_text(max_frames)} seconds ({min_frames}-{max_frames} frames)"
