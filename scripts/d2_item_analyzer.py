import os
import json
import csv
import argparse
import sys
from typing import Dict, List, Optional

# Increase CSV field size limit for large skill files
csv.field_size_limit(1000000)

class D2DataLoader:
    def __init__(self, mpq_path: str):
        self.mpq_path = mpq_path
        self.strings: Dict[str, str] = {}
        self.excel_data: Dict[str, List[Dict]] = {}
        self._load_strings()

    def load_external_table(self, filepath: str) -> List[Dict]:
        if not os.path.exists(filepath):
            return []

        table = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                if not lines:
                    return []
                if lines[0].startswith('\ufeff'):
                    lines[0] = lines[0][1:]

                reader = csv.DictReader(lines, delimiter='\t', quoting=csv.QUOTE_NONE)
                reader.fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
                for row in reader:
                    clean_row = {k.strip() if k else k: v.strip() if v else v for k, v in row.items()}
                    table.append(clean_row)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []
        return table

    def _load_strings(self):

        string_dir = os.path.join(self.mpq_path, "data", "local", "lng", "strings")
        if not os.path.exists(string_dir):
            return
        
        for filename in os.listdir(string_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(string_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8-sig') as f:
                        data = json.load(f)
                        for entry in data:
                            if "Key" in entry and "enUS" in entry:
                                self.strings[entry["Key"]] = entry["enUS"]
                except Exception as e:
                    print(f"Error loading strings from {filename}: {e}")

    def get_excel_data(self, table_name: str) -> List[Dict]:
        if table_name in self.excel_data:
            return self.excel_data[table_name]
        
        filepath = os.path.join(self.mpq_path, "data", "global", "excel", f"{table_name}.txt")
        if not os.path.exists(filepath):
            return []
        
        table = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                # Read all lines to handle potential issues
                lines = f.readlines()
                if not lines:
                    return []
                
                # Strip BOM if present manually just in case
                if lines[0].startswith('\ufeff'):
                    lines[0] = lines[0][1:]
                
                reader = csv.DictReader(lines, delimiter='\t', quoting=csv.QUOTE_NONE)
                # Normalize field names: strip and lower
                reader.fieldnames = [f.strip() for f in reader.fieldnames] if reader.fieldnames else []
                
                for row in reader:
                    # Strip values as well
                    clean_row = {k.strip() if k else k: v.strip() if v else v for k, v in row.items()}
                    table.append(clean_row)
        except Exception as e:
            print(f"Error reading {table_name}: {e}")
            return []
        
        self.excel_data[table_name] = table
        return table

    def get_string(self, key: str) -> str:
        if not key: return ""
        return self.strings.get(key, key)

class PropertyResolver:
    def __init__(self, loader: D2DataLoader, property_groups: Optional[List[Dict]] = None):
        self.loader = loader
        # Use lowercase keys for all lookups to handle casing inconsistencies
        self.property_groups = {row['code'].strip().lower(): row for row in property_groups} if property_groups else {}
        
        # Property aliases for common inconsistencies
        self.aliases = {
            'cast': 'cast1',
            'balance': 'balance1',
            'move': 'move1',
            'swing': 'swing1',
            'block': 'block1',
            'cold-res': 'res-cold',
            'fire-res': 'res-fire',
            'ltng-res': 'res-ltng',
            'pois-res': 'res-pois',
            'all-res': 'res-all',
            'ern%': 'enr%',
            'res-poi-len': 'res-pois-len',
            'get-hit-skill': 'gethit-skill'
        }

        self.properties = {}
        for row in loader.get_excel_data('properties'):
            code = row.get('code', '').strip().lower()
            if code:
                self.properties[code] = row

        self.stats = {}
        for row in loader.get_excel_data('itemstatcost'):
            stat = row.get('Stat', '').strip().lower()
            if stat:
                self.stats[stat] = row
        
        # Robust skill loading
        skills_data = loader.get_excel_data('skills')
        self.skills = {}
        self.skills_by_id = {}
        for row in skills_data:
            s_name = row.get('skill', '').strip().lower()
            if s_name:
                self.skills[s_name] = row
            
            s_id = row.get('*Id') or row.get('Id') or row.get('*ID') or row.get('ID')
            if s_id:
                self.skills_by_id[str(s_id).strip()] = row

        self.skill_desc = {}
        for row in loader.get_excel_data('skilldesc'):
            sd_key = row.get('skilldesc', '').strip().lower()
            if sd_key:
                self.skill_desc[sd_key] = row

        self.class_names = {
            '0': 'Amazon',
            '1': 'Sorceress',
            '2': 'Necromancer',
            '3': 'Paladin',
            '4': 'Barbarian',
            '5': 'Druid',
            '6': 'Assassin',
            '7': 'Warlock'
        }

        self.skill_tab_names = {
            '0': 'Bow and Crossbow',
            '1': 'Passive and Magic',
            '2': 'Javelin and Spear',
            '3': 'Fire',
            '4': 'Lightning',
            '5': 'Cold',
            '6': 'Curses',
            '7': 'Poison and Bone',
            '8': 'Summoning',
            '9': 'Combat',
            '10': 'Offensive Auras',
            '11': 'Defensive Auras',
            '12': 'Combat',
            '13': 'Combat Masteries',
            '14': 'Warcries',
            '15': 'Summoning',
            '16': 'Shape Shifting',
            '17': 'Elemental',
            '18': 'Traps',
            '19': 'Shadow Disciplines',
            '20': 'Martial Arts',
            '21': 'Warlock'
        }

    def resolve_skill_name(self, skill_name_or_id: str) -> str:
        skill_name_or_id = str(skill_name_or_id).strip()
        if not skill_name_or_id or skill_name_or_id == '0':
            return skill_name_or_id

        # Try ID first if it's numeric
        if skill_name_or_id.isdigit():
            skill = self.skills_by_id.get(skill_name_or_id)
        else:
            skill = self.skills.get(skill_name_or_id.lower())
            
        if skill:
            desc_key = skill.get('skilldesc', '').strip().lower()
            if desc_key and desc_key in self.skill_desc:
                str_name_key = self.skill_desc[desc_key].get('str name', '').strip()
                if str_name_key:
                    resolved = self.loader.get_string(str_name_key)
                    if resolved: return resolved
            
            # Fallback to internal name
            internal_name = skill.get('skill', '').strip()
            if internal_name: return internal_name
            
        return skill_name_or_id

    def format_desc(self, stat_code: str, min_val: str, max_val: str) -> Optional[str]:
        stat = self.stats.get(stat_code.lower())
        if not stat:
            return None
        
        str_pos = stat.get('descstrpos', '').strip()
        str_neg = stat.get('descstrneg', '').strip()
        str_2 = stat.get('descstr2', '').strip()
        
        if not str_pos:
            return None

        try:
            val = int(min_val) if min_val and min_val != '' else 0
        except ValueError:
            val = 0
            
        range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
        
        fmt_string = self.loader.get_string(str_pos if val >= 0 else str_neg)
        if not fmt_string: return None
        
        sign = "+" if val >= 0 else ""
        
        if "%+d" in fmt_string:
            fmt_string = fmt_string.replace("%+d", f"{sign}{range_str}")
        elif "%d" in fmt_string:
            fmt_string = fmt_string.replace("%d", f"{range_str}")

        fmt_string = fmt_string.replace("%%", "%")
            
        if str_2:
            fmt_string += " " + self.loader.get_string(str_2)
            
        return fmt_string

    def resolve_property(self, code: str, param: str, min_val: str, max_val: str) -> str:
        code_lower = code.strip().lower()
        
        # Apply alias
        if code_lower in self.aliases:
            code_lower = self.aliases[code_lower]
        
        # Check property groups first
        if code_lower in self.property_groups:
            group = self.property_groups[code_lower]
            pick_mode = group.get('PickMode', '1')
            options = []
            for i in range(1, 9):
                p_code = group.get(f'Prop{i}', '').strip()
                if p_code and p_code != 'xxx':
                    p_min = group.get(f'ModMin{i}', '').strip()
                    p_max = group.get(f'ModMax{i}', '').strip()
                    p_param = group.get(f'ParMin{i}', '').strip()
                    resolved = self.resolve_property(p_code, p_param, p_min, p_max)
                    options.append(resolved)
            
            if pick_mode == '1':
                return " / ".join(options)
            else:
                return " (Random: " + " OR ".join(options) + ")"

        prop = self.properties.get(code_lower)
        if not prop:
            return f"Unknown Prop: {code} ({param}, {min_val}-{max_val})"
        
        range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"

        # 1. Try *Tooltip from properties.txt (modded files often have this)
        tooltip = prop.get('*Tooltip', '').strip()
        if tooltip and tooltip != '0':
            func = prop.get('func1', '0').strip()
            val1 = prop.get('val1', '0').strip()
            res_text = tooltip
            
            # Handle # placeholder
            if func == '36': # Random class skill function
                res_text = res_text.replace('#', val1)
            else:
                res_text = res_text.replace('#', range_str)
            
            # Handle [Class Skill Tab] placeholder
            if '[Class Skill Tab]' in res_text:
                res_text = res_text.replace('[Class Skill Tab]', self.skill_tab_names.get(param, f"Tab {param}"))

            # Handle [Class] placeholder
            if '[Class]' in res_text:
                if func == '36':
                    if min_val == '0' and max_val == '7':
                        res_text = res_text.replace('[Class]', 'Random Class')
                    elif min_val == '0' and max_val == '6':
                        res_text = res_text.replace('[Class]', 'Original Class')
                    elif min_val == max_val:
                        res_text = res_text.replace('[Class]', self.class_names.get(min_val, f"Class {min_val}"))
                    else:
                        res_text = res_text.replace('[Class]', 'Random Class')
                else:
                    set1 = prop.get('set1', '').strip()
                    class_id = set1 if set1 and set1 != '0' else param
                    res_text = res_text.replace('[Class]', self.class_names.get(class_id, f"Class {class_id}"))

            # Handle [Skill] placeholder
            if '[Skill]' in res_text or '%s' in res_text:
                skill_name = self.resolve_skill_name(param)
                res_text = res_text.replace('[Skill]', skill_name).replace('%s', skill_name)
            
            return res_text

        # 2. Skill-related codes (fallback)
        skill_codes = ['oskill', 'skill', 'att-skill', 'hit-skill', 'gethit-skill', 'kill-skill', 'death-skill', 'level-skill', 'aura']
        if code in skill_codes:
            skill_name = self.resolve_skill_name(param)
            
            if code == 'oskill':
                return f"+{range_str} to {skill_name}"
            elif code == 'skill':
                return f"+{range_str} to {skill_name}"
            elif code == 'aura':
                return f"Level {range_str} {skill_name} Aura When Equipped"
            elif code in ['hit-skill', 'att-skill']:
                return f"{min_val}% Chance to cast Level {max_val} {skill_name} on striking"
            elif code == 'gethit-skill':
                return f"{min_val}% Chance to cast Level {max_val} {skill_name} when struck"
            elif code == 'kill-skill':
                return f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Kill an Enemy"
            elif code == 'death-skill':
                return f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Die"
            elif code == 'level-skill':
                return f"{min_val}% Chance to cast Level {max_val} {skill_name} when you Level-Up"
        
        # Priority: Check if the property itself has a specific description format
        for i in range(1, 8):
            desc_fmt = prop.get(f'val{i}', '').strip()
            if desc_fmt and any(x in desc_fmt for x in ['+#', '#%', '# ', '%s']):
                res_text = desc_fmt.replace('+#', f'+{range_str}').replace('#', range_str)
                if '[Skill]' in res_text or '%s' in res_text:
                    skill_name = self.resolve_skill_name(param)
                    res_text = res_text.replace('[Skill]', skill_name).replace('%s', skill_name)
                return res_text

        # Try to resolve via stats
        for i in range(1, 8):
            stat_code = prop.get(f'stat{i}', '').strip()
            if stat_code:
                desc = self.format_desc(stat_code, min_val, max_val)
                if desc:
                    return desc
        
        # Fallback to internal name
        stat_name = prop.get('stat1', code).strip()
        if not stat_name: stat_name = code
        return f"{stat_name}: {range_str} (param: {param})"

class ItemAnalyzer:
    def __init__(self, mpq_path: str, property_groups: Optional[List[Dict]] = None):
        self.loader = D2DataLoader(mpq_path)
        self.resolver = PropertyResolver(self.loader, property_groups)
        self.armor = {row['code']: row for row in self.loader.get_excel_data('armor')}
        self.weapons = {row['code']: row for row in self.loader.get_excel_data('weapons')}
        self.misc = {row['code']: row for row in self.loader.get_excel_data('misc')}
        self.item_types = {row['Code']: row for row in self.loader.get_excel_data('itemtypes')}

    def resolve_base_item(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if item:
            name_key = item.get('namestr', '').strip() or item.get('name', '').strip()
            if name_key:
                return self.loader.get_string(name_key)
            return item.get('name', code)
        return code

    def get_item_category(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if not item:
            return "Miscellaneous"
        
        type_code = item.get('type', '').strip()
        item_type = self.item_types.get(type_code)
        if item_type:
            return self.loader.get_string(item_type.get('ItemType', 'Unknown').strip())
        return "Miscellaneous"

    def get_runeword_category(self, itype_code: str) -> str:
        itype_code = itype_code.strip()
        item_type = self.item_types.get(itype_code)
        if item_type:
            return self.loader.get_string(item_type.get('ItemType', 'Unknown').strip())
        return itype_code

    def analyze_runeword(self, row: Dict) -> str:
        name = row.get('*Rune Name', row.get('Name', 'Unknown')).strip()
        output = f"### {name}\n"
        
        rune_names = []
        for i in range(1, 7):
            rune_code = row.get(f'Rune{i}', '').strip()
            if rune_code and rune_code != 'xxx':
                rune_item = self.misc.get(rune_code)
                rune_names.append(rune_item['name'].strip() if rune_item else rune_code)
        
        output += f"* **Runes:** {' + '.join(rune_names)}\n"
        output += f"* **Base Items:** {self.resolve_base_item(row.get('itype1', '').strip())}\n"
        output += "* **Properties:**\n"
        
        for i in range(1, 8):
            code = row.get(f'T1Code{i}', '').strip()
            if code and code != 'xxx':
                prop_str = self.resolver.resolve_property(
                    code, 
                    row.get(f'T1Param{i}', ''), 
                    row.get(f'T1Min{i}', ''), 
                    row.get(f'T1Max{i}', '')
                )
                output += f"    * {prop_str}\n"
        return output

    def analyze_unique(self, row: Dict) -> str:
        index = row.get('index', '').strip()
        localized_name = self.loader.get_string(index)
        output = f"### {localized_name} ({index})\n"
        output += f"* **Base Item:** {self.resolve_base_item(row.get('code', '').strip())}\n"
        output += f"* **Level Requirement:** {row.get('lvl req', '0')}\n"
        output += "* **Properties:**\n"
        
        for i in range(1, 13):
            code = row.get(f'prop{i}', '').strip()
            if code and code != 'xxx':
                prop_str = self.resolver.resolve_property(
                    code, 
                    row.get(f'par{i}', ''), 
                    row.get(f'min{i}', ''), 
                    row.get(f'max{i}', '')
                )
                output += f"    * {prop_str}\n"
        return output

    def analyze_set_item(self, row: Dict) -> str:
        index = row.get('index', '').strip()
        localized_name = self.loader.get_string(index)
        output = f"### {localized_name} ({index})\n"
        output += f"* **Set:** {row.get('set', '').strip()}\n"
        output += f"* **Base Item:** {self.resolve_base_item(row.get('item', '').strip())}\n"
        output += "* **Properties:**\n"
        
        for i in range(1, 13):
            code = row.get(f'prop{i}', '').strip()
            if code and code != 'xxx':
                prop_str = self.resolver.resolve_property(
                    code, 
                    row.get(f'par{i}', ''), 
                    row.get(f'min{i}', ''), 
                    row.get(f'max{i}', '')
                )
                output += f"    * {prop_str}\n"
        return output

    def get_group_for_category(self, category: str) -> str:
        category_lower = category.lower()
        if category_lower in ['expansion', 'other']:
            return 'other'
        
        # Weapons
        if any(w in category_lower for w in ['axe', 'bow', 'club', 'crossbow', 'hammer', 'javelin', 'knife', 'mace', 'polearm', 'scepter', 'spear', 'staff', 'sword', 'throwing', 'wand', 'weapon']):
            return 'weapons'
        
        # Armor
        if any(a in category_lower for a in ['armor', 'belt', 'boots', 'gloves', 'circlet', 'helm', 'shield', 'merc', 'equip']):
            return 'armor'
            
        # Accessories
        if any(acc in category_lower for acc in ['amulet', 'ring', 'charm', 'jewel']):
            return 'accessories'
            
        # Class Specific
        if any(cls in category_lower for cls in ['amazon', 'auric', 'grimoire', 'hand to hand', 'orb', 'pelt', 'primal', 'voodoo']):
            return 'class_specific'
            
        return 'other'

    def export_all(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        groups = ['weapons', 'armor', 'accessories', 'class_specific']

        # 1. Uniques
        uniques_dir = os.path.join(output_dir, "uniques")
        unique_data = {g: {} for g in groups}
        for row in self.loader.get_excel_data('uniqueitems'):
            if row.get('disabled') == '1': continue
            cat = self.get_item_category(row.get('code', '').strip())
            if cat.lower() == 'expansion': continue
            group = self.get_group_for_category(cat)
            if group == 'other': group = 'weapons' # Fallback
            
            if cat not in unique_data[group]: unique_data[group][cat] = []
            unique_data[group][cat].append(self.analyze_unique(row))
        
        for group in groups:
            group_dir = os.path.join(uniques_dir, group)
            os.makedirs(group_dir, exist_ok=True)
            for cat, items in unique_data[group].items():
                filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                with open(os.path.join(group_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(f"# Unique {cat}\n\n")
                    f.write("\n".join(items))

        # 2. Sets
        sets_dir = os.path.join(output_dir, "sets")
        set_data = {g: {} for g in groups}
        for row in self.loader.get_excel_data('setitems'):
            if row.get('disabled') == '1': continue
            cat = self.get_item_category(row.get('item', '').strip())
            if cat.lower() == 'expansion': continue
            group = self.get_group_for_category(cat)
            if group == 'other': group = 'weapons' # Fallback
            
            if cat not in set_data[group]: set_data[group][cat] = []
            set_data[group][cat].append(self.analyze_set_item(row))
        
        for group in groups:
            group_dir = os.path.join(sets_dir, group)
            os.makedirs(group_dir, exist_ok=True)
            for cat, items in set_data[group].items():
                filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                with open(os.path.join(group_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(f"# Set {cat}\n\n")
                    f.write("\n".join(items))

        # 3. Runewords
        runes_dir = os.path.join(output_dir, "runewords")
        # Special groups for runewords
        rw_groups_map = {'weapons': 'weapons', 'armor': 'chests', 'helm': 'helms', 'shield': 'shields'}
        rune_data = {g: {} for g in rw_groups_map.values()}
        
        for row in self.loader.get_excel_data('runes'):
            if row.get('complete') != '1': continue
            cat = self.get_runeword_category(row.get('itype1', '').strip())
            if cat.lower() == 'expansion': continue
            
            # Map category to group
            group = 'weapons'
            cat_lower = cat.lower()
            if 'shield' in cat_lower: group = 'shields'
            elif 'helm' in cat_lower: group = 'helms'
            elif 'armor' in cat_lower: group = 'chests'
            
            if cat not in rune_data[group]: rune_data[group][cat] = []
            rune_data[group][cat].append(self.analyze_runeword(row))
            
        for group in rune_data:
            group_dir = os.path.join(runes_dir, group)
            os.makedirs(group_dir, exist_ok=True)
            for cat, items in rune_data[group].items():
                filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                with open(os.path.join(group_dir, filename), 'w', encoding='utf-8') as f:
                    display_cat = "Chests" if group == 'chests' else cat
                    f.write(f"# Runewords for {display_cat}\n\n")
                    f.write("\n".join(items))

        # 4. Index
        with open(os.path.join(output_dir, "index.md"), 'w', encoding='utf-8') as f:
            f.write("# Diablo II Item Database\n\n")
            
            f.write("## Unique Items\n\n")
            group_titles = {'weapons': 'Unique Weapons', 'armor': 'Unique Armor', 'accessories': 'Unique Accessories', 'class_specific': 'Class Specific Uniques'}
            for group in groups:
                if unique_data[group]:
                    f.write(f"### [{group_titles[group]}](uniques/{group}/)\n")
                    for cat in sorted(unique_data[group].keys()):
                        filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                        f.write(f"* [Unique {cat}](uniques/{group}/{filename})\n")
                    f.write("\n")

            f.write("## Set Items\n\n")
            group_titles_sets = {'weapons': 'Set Weapons', 'armor': 'Set Armor', 'accessories': 'Set Accessories', 'class_specific': 'Class Specific Sets'}
            for group in groups:
                if set_data[group]:
                    f.write(f"### [{group_titles_sets[group]}](sets/{group}/)\n")
                    for cat in sorted(set_data[group].keys()):
                        filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                        f.write(f"* [Set {cat}](sets/{group}/{filename})\n")
                    f.write("\n")

            f.write("## Runewords\n\n")
            rw_titles = {'weapons': 'Runeword Weapons', 'chests': 'Runeword Chests', 'helms': 'Runeword Helms', 'shields': 'Runeword Shields'}
            for group in ['weapons', 'chests', 'helms', 'shields']:
                if rune_data[group]:
                    f.write(f"### [{rw_titles[group]}](runewords/{group}/)\n")
                    for cat in sorted(rune_data[group].keys()):
                        filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                        link_name = f"{cat} Runewords" if "Shield" in cat or "Armor" in cat else f"{cat} Runewords"
                        if group == 'chests': link_name = "Chests Runewords"
                        f.write(f"* [{link_name}](runewords/{group}/{filename})\n")
                    f.write("\n")

def main():
    parser = argparse.ArgumentParser(description="Diablo II Item Analyzer")
    parser.add_argument("--mpq", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the MPQ data directory")
    parser.add_argument("--type", choices=["runeword", "unique", "export"], required=True, help="Item type to analyze or 'export' all")
    parser.add_argument("--name", help="Name of the item to search for (ignored if type is export)")
    parser.add_argument("--out", default="../exports/item_db", help="Output directory for export")
    
    args = parser.parse_args()
    loader = D2DataLoader(args.mpq)
    property_groups = loader.load_external_table("../data/propertygroups.txt")
    analyzer = ItemAnalyzer(args.mpq, property_groups)
    
    if args.type == "export":
        analyzer.export_all(args.out)
        print(f"Export complete to {args.out}")
    elif args.type == "runeword":
        runes_table = analyzer.loader.get_excel_data('runes')
        for row in runes_table:
            r_name = row.get('*Rune Name', row.get('Name', '')).strip()
            if args.name.lower() in r_name.lower():
                print(analyzer.analyze_runeword(row))
                return
        print(f"Runeword '{args.name}' not found.")
    elif args.type == "unique":
        uniques = analyzer.loader.get_excel_data('uniqueitems')
        for row in uniques:
            u_index = row.get('index', '').strip()
            if args.name.lower() in u_index.lower():
                print(analyzer.analyze_unique(row))
                return
        print(f"Unique item '{args.name}' not found.")

if __name__ == "__main__":
    main()
