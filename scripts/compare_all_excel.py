import os
import json
import sys
from compare_excel import compare_files

def get_key_column(filename):
    mapping = {
        'armor.txt': 'name',
        'automagic.txt': 'Name',
        'charstats.txt': 'class',
        'cubemain.txt': 'description',
        'difficultylevels.txt': 'Name',
        'experience.txt': 'Level',
        'gamble.txt': 'name',
        'gems.txt': 'name',
        'hireling.txt': 'Hireling',
        'inventory.txt': 'class',
        'itemstatcost.txt': 'Stat',
        'itemtypes.txt': 'ItemType',
        'levels.txt': 'Name',
        'lvlmaze.txt': 'Name',
        'lvlprest.txt': 'Name',
        'lvlwarp.txt': 'Name',
        'magicprefix.txt': 'Name',
        'magicsuffix.txt': 'Name',
        'misc.txt': 'name',
        'missiles.txt': 'Missile',
        'monai.txt': 'AI',
        'monlvl.txt': 'Level',
        'monprop.txt': 'Id',
        'monstats.txt': 'Id',
        'monstats2.txt': 'Id',
        'monumod.txt': 'uniquemod',
        'npc.txt': 'npc',
        'objects.txt': 'Name',
        'overlay.txt': 'overlay',
        'properties.txt': 'code',
        'runes.txt': '*Rune Name',
        'setitems.txt': 'index',
        'sets.txt': 'index',
        'shrines.txt': 'Name',
        'skilldesc.txt': 'skilldesc',
        'skills.txt': 'skill',
        'states.txt': 'state',
        'superuniques.txt': 'Superunique',
        'treasureclassex.txt': 'Treasure Class',
        'uniqueitems.txt': 'index',
        'weapons.txt': 'name',
    }
    return mapping.get(filename, 'code')

def escape_latex(s):
    """Escapes special LaTeX characters for GitHub MathJax. Uses double backslashes to survive Markdown pass."""
    if not s: return s
    chars = {
        '%': r'\\%',
        '$': r'\\$',
        '#': r'\\#',
        '_': r'\\_',
        '{': r'\\{',
        '}': r'\\}',
        '&': r'\\&',
    }
    for char, escaped in chars.items():
        s = s.replace(char, escaped)
    return s

def write_detail_markdown(report, output_path):
    name = report['filename']
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Differences for {name}\n\n")
        f.write(f"*Key column used: `{report['key_used']}`*\n\n")
        
        if report['columns']['added_in_bk']:
            f.write(f"## Added Columns in BK (New)\n")
            f.write(f"`{', '.join(report['columns']['added_in_bk'])}`  \n\n")
            
        if report['columns']['removed_in_bk']:
            f.write(f"## Removed Columns in BK (New)\n")
            f.write(f"`{', '.join(report['columns']['removed_in_bk'])}`  \n\n")
        
        if report['rows']['added_in_bk']:
            f.write(f"## Added Rows in BK (New) ({len(report['rows']['added_in_bk'])})\n")
            for item in report['rows']['added_in_bk']:
                f.write(f"- {item}\n")
            f.write("\n")

        if report['rows']['removed_in_bk']:
            f.write(f"## Removed Rows in BK (New) ({len(report['rows']['removed_in_bk'])})\n")
            for item in report['rows']['removed_in_bk']:
                f.write(f"- {item}\n")
            f.write("\n")

        if report['rows']['modified']:
            f.write(f"## Modified Rows ({len(report['rows']['modified'])})\n")
            keys = sorted(report['rows']['modified'].keys())
            for key in keys:
                f.write(f"### {key}\n")
                for col, vals in report['rows']['modified'][key].items():
                    v_new = vals['bk_new'] if vals['bk_new'] != '' else '*empty*'
                    v_old = vals['bt_old'] if vals['bt_old'] != '' else '*empty*'
                    # Use LaTeX for coloring and escape characters
                    e_new = escape_latex(str(v_new))
                    e_old = escape_latex(str(v_old))
                    f.write(f"- `{col}`: $\\color{{gray}}{{\\text{{{e_old}}}}}$ (Old) &rarr; $\\color{{blue}}{{\\text{{{e_new}}}}}$ (New)\n")
                f.write("\n")

def generate_summary(all_reports, report_dir):
    summary_path = os.path.join(report_dir, "SUMMARY.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Diablo 2 Excel Comparison: BKDiablo (New) vs BTDiablo (Old)\n\n")
        f.write("This report treats **BKDiablo** as the target (New) version and **BTDiablo** as the base (Old) version.\n\n")
        
        f.write("## File Comparison Index\n\n")
        f.write("| File | Added Cols | Rem Cols | Added Rows | Rem Rows | Mod Rows | Link |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n")
        
        for name in sorted(all_reports.keys()):
            r = all_reports[name]
            if "error" in r: continue
            
            has_diffs = (r['columns']['added_in_bk'] or r['columns']['removed_in_bk'] or 
                         r['rows']['added_in_bk'] or r['rows']['removed_in_bk'] or r['rows']['modified'])
            
            detail_link = f"[{name}]({name.replace('.txt', '.md')})" if has_diffs else "No changes"
            
            f.write(f"| {name} | {len(r['columns']['added_in_bk'])} | {len(r['columns']['removed_in_bk'])} | {len(r['rows']['added_in_bk'])} | {len(r['rows']['removed_in_bk'])} | {len(r['rows']['modified'])} | {detail_link} |\n")
        
        f.write("\n\n*Click on a file name in the 'Link' column to see detailed changes.*\n")

def main():
    bk_dir = "../mods/BKDiablo/bkdiablo.mpq/data/global/excel"
    bt_dir = "../mods/BTDiablo/btdiablo.mpq/data/global/excel"
    report_dir = "../output/excel_diff_report"
    
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    if not os.path.exists(bk_dir) or not os.path.exists(bt_dir):
        print("Error: Excel directories not found.")
        return

    files1 = {f for f in os.listdir(bk_dir) if f.endswith('.txt')}
    files2 = {f for f in os.listdir(bt_dir) if f.endswith('.txt')}
    common_files = sorted(files1 & files2)
    
    all_reports = {}
    
    print(f"Comparing {len(common_files)} files...")
    for filename in common_files:
        print(f"  Processing {filename}...")
        path_bk = os.path.join(bk_dir, filename)
        path_bt = os.path.join(bt_dir, filename)
        key = get_key_column(filename)
        
        report = compare_files(path_bk, path_bt, key)
        all_reports[filename] = report
        
        has_diffs = (report.get('columns', {}).get('added_in_bk') or 
                     report.get('columns', {}).get('removed_in_bk') or 
                     report.get('rows', {}).get('added_in_bk') or 
                     report.get('rows', {}).get('removed_in_bk') or 
                     report.get('rows', {}).get('modified'))
        
        if has_diffs:
            detail_file = filename.replace('.txt', '.md')
            write_detail_markdown(report, os.path.join(report_dir, detail_file))
    
    generate_summary(all_reports, report_dir)
    print(f"\nDone! Report generated in directory: {report_dir}")
    print(f"Main index: {os.path.join(report_dir, 'SUMMARY.md')}")

if __name__ == "__main__":
    main()
