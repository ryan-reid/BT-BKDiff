import os
import json
import csv
import argparse
from typing import Dict, List, Optional

class D2DataLoader:
    def __init__(self, mpq_path: str):
        self.mpq_path = mpq_path
        self.strings: Dict[str, str] = {}
        self.excel_data: Dict[str, List[Dict]] = {}
        self._load_strings()

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
        
        # Increase field size limit for large skill files
        csv.field_size_limit(1000000)
        
        table = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                table.append(row)
        
        self.excel_data[table_name] = table
        return table

    def get_string(self, key: str) -> str:
        return self.strings.get(key, key)

class PropertyResolver:
    def __init__(self, loader: D2DataLoader):
        self.loader = loader
        self.properties = {row['code']: row for row in loader.get_excel_data('properties')}
        self.stats = {row['Stat']: row for row in loader.get_excel_data('itemstatcost')}
        self.skills = {row['skill']: row for row in loader.get_excel_data('skills')}
        self.skills_by_id = {row['*Id']: row for row in loader.get_excel_data('skills')}
        self.skill_desc = {row['skilldesc']: row for row in loader.get_excel_data('skilldesc')}

    def resolve_skill_name(self, skill_name_or_id: str) -> str:
        skill = self.skills.get(skill_name_or_id)
        if not skill:
            skill = self.skills_by_id.get(skill_name_or_id)
        
        if skill:
            desc_key = skill.get('skilldesc')
            if desc_key and desc_key in self.skill_desc:
                str_name_key = self.skill_desc[desc_key].get('str name')
                if str_name_key:
                    return self.loader.get_string(str_name_key)
            return skill.get('skill', skill_name_or_id)
        return skill_name_or_id

    def format_desc(self, stat_code: str, min_val: str, max_val: str) -> Optional[str]:
        stat = self.stats.get(stat_code)
        if not stat:
            return None
        
        desc_func = stat.get('descfunc')
        str_pos = stat.get('descstrpos')
        str_neg = stat.get('descstrneg')
        str_2 = stat.get('descstr2', '')
        
        if not str_pos:
            return None

        val = int(min_val) if min_val else 0
        range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
        
        fmt_string = self.loader.get_string(str_pos if val >= 0 else str_neg)
        
        # Simple placeholder replacement
        if "%+d" in fmt_string:
            # Handle the %+d manually or via string formatting if we know it's always numeric
            sign = "+" if val >= 0 else ""
            fmt_string = fmt_string.replace("%+d", f"{sign}{range_str}")
        elif "%d%%" in fmt_string:
            fmt_string = fmt_string.replace("%d%%", f"{range_str}%")
        elif "%d" in fmt_string:
            fmt_string = fmt_string.replace("%d", f"{range_str}")
            
        if str_2:
            fmt_string += " " + self.loader.get_string(str_2)
            
        return fmt_string

    def resolve_property(self, code: str, param: str, min_val: str, max_val: str) -> str:
        prop = self.properties.get(code)
        if not prop:
            return f"Unknown Prop: {code} ({param}, {min_val}-{max_val})"
        
        if code == 'oskill':
            skill_name = self.resolve_skill_name(param)
            return f"+{min_val} to {skill_name}"
        elif code == 'aura':
            skill_name = self.resolve_skill_name(param)
            return f"Level {min_val} {skill_name} Aura When Equipped"
        elif code == 'hit-skill':
            skill_name = self.resolve_skill_name(param)
            return f"{min_val}% Chance to cast Level {max_val} {skill_name} on striking"
        
        # Try to resolve via stats
        for i in range(1, 8):
            stat_code = prop.get(f'stat{i}')
            if stat_code:
                desc = self.format_desc(stat_code, min_val, max_val)
                if desc:
                    return desc
        
        # Fallback to internal name
        stat_name = prop.get('stat1', code)
        range_str = f"{min_val}" if min_val == max_val else f"{min_val}-{max_val}"
        return f"{stat_name}: {range_str} (param: {param})"

class ItemAnalyzer:
    def __init__(self, mpq_path: str):
        self.loader = D2DataLoader(mpq_path)
        self.resolver = PropertyResolver(self.loader)
        self.armor = {row['code']: row for row in self.loader.get_excel_data('armor')}
        self.weapons = {row['code']: row for row in self.loader.get_excel_data('weapons')}
        self.misc = {row['code']: row for row in self.loader.get_excel_data('misc')}
        self.item_types = {row['Code']: row for row in self.loader.get_excel_data('itemtypes')}

    def resolve_base_item(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if item:
            name_key = item.get('namestr') or item.get('name')
            if name_key:
                return self.loader.get_string(name_key)
            return item.get('name', code)
        return code

    def get_item_category(self, code: str) -> str:
        item = self.armor.get(code) or self.weapons.get(code) or self.misc.get(code)
        if not item:
            return "Miscellaneous"
        
        type_code = item.get('type')
        item_type = self.item_types.get(type_code)
        if item_type:
            return self.loader.get_string(item_type.get('ItemType', 'Unknown'))
        return "Miscellaneous"

    def get_runeword_category(self, itype_code: str) -> str:
        item_type = self.item_types.get(itype_code)
        if item_type:
            return self.loader.get_string(item_type.get('ItemType', 'Unknown'))
        return itype_code

    def analyze_runeword(self, row: Dict) -> str:
        output = f"### {row['*Rune Name']}\n"
        
        rune_names = []
        for i in range(1, 7):
            rune_code = row.get(f'Rune{i}')
            if rune_code and rune_code != 'xxx' and rune_code != '':
                rune_item = self.misc.get(rune_code)
                rune_names.append(rune_item['name'] if rune_item else rune_code)
        
        output += f"* **Runes:** {' + '.join(rune_names)}\n"
        output += f"* **Base Items:** {self.resolve_base_item(row['itype1'])}\n"
        output += "* **Properties:**\n"
        
        for i in range(1, 8):
            code = row.get(f'T1Code{i}')
            if code and code != 'xxx' and code != '':
                prop_str = self.resolver.resolve_property(
                    code, 
                    row.get(f'T1Param{i}', ''), 
                    row.get(f'T1Min{i}', ''), 
                    row.get(f'T1Max{i}', '')
                )
                output += f"    * {prop_str}\n"
        return output

    def analyze_unique(self, row: Dict) -> str:
        localized_name = self.loader.get_string(row['index'])
        output = f"### {localized_name} ({row['index']})\n"
        output += f"* **Base Item:** {self.resolve_base_item(row['code'])}\n"
        output += f"* **Level Requirement:** {row['lvl req']}\n"
        output += "* **Properties:**\n"
        
        for i in range(1, 13):
            code = row.get(f'prop{i}')
            if code and code != 'xxx' and code != '':
                prop_str = self.resolver.resolve_property(
                    code, 
                    row.get(f'par{i}', ''), 
                    row.get(f'min{i}', ''), 
                    row.get(f'max{i}', '')
                )
                output += f"    * {prop_str}\n"
        return output

    def analyze_set_item(self, row: Dict) -> str:
        localized_name = self.loader.get_string(row['index'])
        output = f"### {localized_name} ({row['index']})\n"
        output += f"* **Set:** {row['set']}\n"
        output += f"* **Base Item:** {self.resolve_base_item(row['item'])}\n"
        output += "* **Properties:**\n"
        
        for i in range(1, 13):
            code = row.get(f'prop{i}')
            if code and code != 'xxx' and code != '':
                prop_str = self.resolver.resolve_property(
                    code, 
                    row.get(f'par{i}', ''), 
                    row.get(f'min{i}', ''), 
                    row.get(f'max{i}', '')
                )
                output += f"    * {prop_str}\n"
        return output

    def export_all(self, output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 1. Uniques
        uniques_dir = os.path.join(output_dir, "uniques")
        os.makedirs(uniques_dir, exist_ok=True)
        unique_categories = {}
        for row in self.loader.get_excel_data('uniqueitems'):
            if row.get('disabled') == '1': continue
            cat = self.get_item_category(row['code'])
            if cat not in unique_categories: unique_categories[cat] = []
            unique_categories[cat].append(self.analyze_unique(row))
        
        for cat, items in unique_categories.items():
            filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
            with open(os.path.join(uniques_dir, filename), 'w', encoding='utf-8') as f:
                f.write(f"# Unique {cat}\n\n")
                f.write("\n".join(items))

        # 2. Sets
        sets_dir = os.path.join(output_dir, "sets")
        os.makedirs(sets_dir, exist_ok=True)
        set_categories = {}
        for row in self.loader.get_excel_data('setitems'):
            if row.get('disabled') == '1': continue
            cat = self.get_item_category(row['item'])
            if cat not in set_categories: set_categories[cat] = []
            set_categories[cat].append(self.analyze_set_item(row))
        
        for cat, items in set_categories.items():
            filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
            with open(os.path.join(sets_dir, filename), 'w', encoding='utf-8') as f:
                f.write(f"# Set {cat}\n\n")
                f.write("\n".join(items))

        # 3. Runewords
        runes_dir = os.path.join(output_dir, "runewords")
        os.makedirs(runes_dir, exist_ok=True)
        rune_categories = {}
        for row in self.loader.get_excel_data('runes'):
            if row.get('complete') != '1': continue
            cat = self.get_runeword_category(row['itype1'])
            if cat not in rune_categories: rune_categories[cat] = []
            rune_categories[cat].append(self.analyze_runeword(row))
            
        for cat, items in rune_categories.items():
            filename = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
            with open(os.path.join(runes_dir, filename), 'w', encoding='utf-8') as f:
                f.write(f"# Runewords for {cat}\n\n")
                f.write("\n".join(items))

        # 4. Index
        with open(os.path.join(output_dir, "index.md"), 'w', encoding='utf-8') as f:
            f.write("# Diablo II Item Database\n\n")
            f.write("## Unique Items\n")
            for cat in sorted(unique_categories.keys()):
                f.write(f"* [Unique {cat}](uniques/{cat.lower().replace(' ', '_').replace('/', '_')}.md)\n")
            f.write("\n## Set Items\n")
            for cat in sorted(set_categories.keys()):
                f.write(f"* [Set {cat}](sets/{cat.lower().replace(' ', '_').replace('/', '_')}.md)\n")
            f.write("\n## Runewords\n")
            for cat in sorted(rune_categories.keys()):
                f.write(f"* [{cat} Runewords](runewords/{cat.lower().replace(' ', '_').replace('/', '_')}.md)\n")

def main():
    parser = argparse.ArgumentParser(description="Diablo II Item Analyzer")
    parser.add_argument("--mpq", default="bkdiablo.mpq", help="Path to the MPQ data directory")
    parser.add_argument("--type", choices=["runeword", "unique", "export"], required=True, help="Item type to analyze or 'export' all")
    parser.add_argument("--name", help="Name of the item to search for (ignored if type is export)")
    parser.add_argument("--out", default="item_db", help="Output directory for export")
    
    args = parser.parse_args()
    analyzer = ItemAnalyzer(args.mpq)
    
    if args.type == "export":
        analyzer.export_all(args.out)
        print(f"Export complete to {args.out}")
    elif args.type == "runeword":
        # Note: Logic updated to reuse analyze_runeword with a search
        runes_table = analyzer.loader.get_excel_data('runes')
        for row in runes_table:
            if args.name.lower() in row.get('*Rune Name', '').lower() or args.name.lower() in row.get('Name', '').lower():
                print(analyzer.analyze_runeword(row))
                return
        print(f"Runeword '{args.name}' not found.")
    elif args.type == "unique":
        uniques = analyzer.loader.get_excel_data('uniqueitems')
        for row in uniques:
            if args.name.lower() in row.get('index', '').lower():
                print(analyzer.analyze_unique(row))
                return
        print(f"Unique item '{args.name}' not found.")

if __name__ == "__main__":
    main()
