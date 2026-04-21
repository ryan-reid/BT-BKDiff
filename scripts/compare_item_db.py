import os
import re
import difflib

def parse_markdown_items(file_path):
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    items = {}
    sections = re.split(r'\n### ', content)
    for section in sections[1:]:
        lines = section.split('\n')
        name_line = lines[0].strip()
        name_match = re.match(r'(.*) \((.*)\)', name_line)
        if name_match:
            display_name = name_match.group(1).strip()
            item_id = name_match.group(2).strip()
        else:
            display_name = name_line
            item_id = name_line
            
        item_props = []
        base_item = "Unknown"
        lvl_req = "0"
        
        for line in lines[1:]:
            original_line = line
            line = line.strip()
            if line.startswith('* **Base Item:** '):
                base_item = line.replace('* **Base Item:** ', '').strip()
            elif line.startswith('* **Level Requirement:** '):
                lvl_req = line.replace('* **Level Requirement:** ', '').strip()
            elif original_line.startswith('    * '):
                item_props.append(line[2:])
            elif line.startswith('* '):
                # Header lines or unindented properties
                if '**' not in line: # Avoid bold headers like **Properties:**
                    item_props.append(line[2:])
        
        items[item_id] = {
            'display_name': display_name,
            'base_item': base_item,
            'lvl_req': lvl_req,
            'properties': item_props
        }
    return items

def escape_latex(s):
    """Escapes special LaTeX characters for GitHub MathJax. Uses double backslashes to survive Markdown pass."""
    if not s: return s
    # LaTeX special characters (need to reach MathJax as \% etc)
    # We use double backslash because GitHub Markdown eats one.
    for char in '%$#_{}&':
        s = s.replace(char, r'\\' + char)
    return s

def normalize_text(s):
    """Strips color codes, bullets, and other fluff to compare content fairly."""
    if not s: return s
    # Strip Diablo II color codes (e.g. ÿc1)
    s = re.sub(r'ÿc.', '', s)
    # Strip bullets and common "fluff" characters
    s = s.replace('•', '').replace('**', '')
    
    # Handle phrasing differences: "Physical Damage Received Reduced by 15%" -> "Damage Reduced by 15%"
    s = s.replace("Physical Damage Received Reduced by", "Damage Reduced by")

    # Treat "Original Class" and "Random Class" as the same to avoid noisy diffs
    s = re.sub(r'(Original|Random) Class', 'Random Class', s, flags=re.IGNORECASE)
    
    # Normalize whitespace
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def get_styled_diffs(old_s, new_s):
    """Surgically highlights differences between two strings using token-based diff and LaTeX for GitHub."""
    # Strip color codes for display
    old_s = re.sub(r'ÿc.', '', old_s)
    new_s = re.sub(r'ÿc.', '', new_s)

    if not old_s: 
        return "", f'$\\color{{blue}}{{\\text{{{escape_latex(new_s)}}}}}$'
    if not new_s or new_s == "(removed)": 
        return f'$\\color{{gray}}{{\\text{{{escape_latex(old_s)}}}}}$', f'$\\color{{blue}}{{\\text{{(removed)}}}}$'
    
    if normalize_text(old_s) == normalize_text(new_s):
        return old_s, new_s
    
    # Tokenize: Group numbers with ranges, signs, and percentages (e.g., +10-20%)
    def tokenize(text):
        return re.findall(r'[+-]?\d+(?:-\d+)?%?|[a-zA-Z]+|[^\w\s]|\s+', text)

    old_toks = tokenize(old_s)
    new_toks = tokenize(new_s)
    
    matcher = difflib.SequenceMatcher(None, old_toks, new_toks)
    
    def render_version(tokens, is_old):
        res = "$"
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if is_old:
                part = "".join(tokens[i1:i2])
                if tag in ['replace', 'delete']:
                    res += f'\\color{{gray}}{{\\text{{{escape_latex(part)}}}}}'
                elif tag == 'equal':
                    res += f'\\text{{{escape_latex(part)}}}'
            else:
                part = "".join(tokens[j1:j2])
                if tag in ['replace', 'insert']:
                    res += f'\\color{{blue}}{{\\text{{{escape_latex(part)}}}}}'
                elif tag == 'equal':
                    res += f'\\text{{{escape_latex(part)}}}'
        res += "$"
        return res

    return render_version(old_toks, True), render_version(new_toks, False)

def align_properties(old_props, new_props):
    def get_stat_key(s):
        s = normalize_text(s)
        # Remove numbers and ranges, but KEEP % to distinguish flat vs percentile stats
        return re.sub(r'[+-]?\d+(?:-\d+)?', '', s).strip().lower()

    aligned = []
    old_used = set()
    new_used = set()

    # Pass 1: Exact normalized match
    for i, op in enumerate(old_props):
        onorm = normalize_text(op)
        for j, np in enumerate(new_props):
            if j in new_used: continue
            nnorm = normalize_text(np)
            if onorm == nnorm:
                aligned.append((op, np))
                old_used.add(i)
                new_used.add(j)
                break

    # Pass 2: Match common stats by key
    for i, op in enumerate(old_props):
        if i in old_used: continue
        okey = get_stat_key(op)
        for j, np in enumerate(new_props):
            if j in new_used: continue
            nkey = get_stat_key(np)
            if okey == nkey and okey != "":
                aligned.append((op, np))
                old_used.add(i)
                new_used.add(j)
                break
    
    for i, op in enumerate(old_props):
        if i not in old_used:
            aligned.append((op, "(removed)"))
    for j, np in enumerate(new_props):
        if j not in new_used:
            aligned.append(("", np))
    return aligned

def compare_databases(bk_dir, bt_dir, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    types = ['uniques', 'sets', 'runewords']
    all_diffs = {t: {} for t in types}
    
    for t in types:
        bk_type_dir = os.path.join(bk_dir, t)
        bt_type_dir = os.path.join(bt_dir, t)
        for root, dirs, files in os.walk(bk_type_dir):
            rel_path = os.path.relpath(root, bk_type_dir)
            if rel_path == '.': rel_path = ''
            for file in files:
                if not file.endswith('.md'): continue
                bk_items = parse_markdown_items(os.path.join(root, file))
                bt_items = parse_markdown_items(os.path.join(bt_type_dir, rel_path, file))
                
                added = [k for k in bk_items if k not in bt_items]
                removed = [k for k in bt_items if k not in bk_items]
                modified = {}
                common = [k for k in bk_items if k in bt_items]
                for k in common:
                    bk_item = bk_items[k]
                    bt_item = bt_items[k]
                    
                    header_diff = (normalize_text(bk_item['base_item']) != normalize_text(bt_item['base_item']) or 
                                   normalize_text(bk_item['lvl_req']) != normalize_text(bt_item['lvl_req']))
                    
                    bk_norm = sorted([normalize_text(p) for p in bk_item['properties']])
                    bt_norm = sorted([normalize_text(p) for p in bt_item['properties']])
                    
                    if header_diff or bk_norm != bt_norm:
                        modified[k] = {
                            'name': bk_item['display_name'],
                            'bk_base': bk_item['base_item'],
                            'bt_base': bt_item['base_item'],
                            'bk_lvl': bk_item['lvl_req'],
                            'bt_lvl': bt_item['lvl_req'],
                            'bk_props': bk_item['properties'],
                            'bt_props': bt_item['properties']
                        }
                
                if added or removed or modified:
                    all_diffs[t][os.path.join(rel_path, file)] = {
                        'added': {k: bk_items[k] for k in added},
                        'removed': {k: bt_items[k] for k in removed},
                        'modified': modified
                    }

    # Generate Summary File
    summary_path = os.path.join(out_dir, "SUMMARY.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Item Database Comparison Summary\n\n")
        f.write("| Category | [Added](ADDED.md) | [Removed](REMOVED.md) | [Modified](MODIFIED.md) |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        
        total_added = 0
        total_removed = 0
        total_modified = 0
        
        for t in types:
            t_added = sum(len(d['added']) for d in all_diffs[t].values())
            t_removed = sum(len(d['removed']) for d in all_diffs[t].values())
            t_modified = sum(len(d['modified']) for d in all_diffs[t].values())
            f.write(f"| {t.capitalize()} | {t_added} | {t_removed} | {t_modified} |\n")
            total_added += t_added
            total_removed += t_removed
            total_modified += t_modified
            
        f.write(f"| **Total** | **{total_added}** | **{total_removed}** | **{total_modified}** |\n\n")
        f.write("Click the links in the header to see detailed breakdowns.\n")

    # Helper to generate detail files
    def write_detail_file(filename, title, key):
        path = os.path.join(out_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write("- $\\color{gray}{\\text{Gray text}}$: Removed/Old Value\n")
            f.write("- $\\color{blue}{\\text{Blue text}}$: Added/New Value\n\n")
            
            has_content = False
            for t in types:
                type_content = ""
                for file_path, diff in all_diffs[t].items():
                    items = diff[key]
                    if not items: continue
                    
                    type_content += f"### {file_path}\n\n"
                    if key == 'added':
                        for k, item in items.items():
                            type_content += f"**{item['display_name']}** ({k})\n\n"
                            type_content += "| BT Diablo (Old) | BK Diablo (New) |\n"
                            type_content += "| :--- | :--- |\n"
                            type_content += f"| | **Base Item:** {item['base_item']} |\n"
                            type_content += f"| | **Level Requirement:** {item['lvl_req']} |\n"
                            type_content += "| | **Properties:** |\n"
                            for prop in item['properties']:
                                _, new_fmt = get_styled_diffs("", prop)
                                type_content += f"| | {new_fmt} |\n"
                            type_content += "\n"
                    elif key == 'removed':
                        for k, item in items.items():
                            type_content += f"- **{item['display_name']}** ({k})\n"
                        type_content += "\n"
                    elif key == 'modified':
                        for k, mod in items.items():
                            type_content += f"**{mod['name']}** ({k})\n\n"
                            type_content += "| BT Diablo (Old) | BK Diablo (New) |\n"
                            type_content += "| :--- | :--- |\n"
                            
                            # Header fields
                            if normalize_text(mod['bt_base']) != normalize_text(mod['bk_base']):
                                b_old, b_new = get_styled_diffs(mod['bt_base'], mod['bk_base'])
                                type_content += f"| **Base Item:** {b_old} | **Base Item:** {b_new} |\n"
                            else:
                                type_content += f"| **Base Item:** {mod['bt_base']} | **Base Item:** {mod['bk_base']} |\n"
                                
                            if normalize_text(mod['bt_lvl']) != normalize_text(mod['bk_lvl']):
                                l_old, l_new = get_styled_diffs(mod['bt_lvl'], mod['bk_lvl'])
                                type_content += f"| **Level Requirement:** {l_old} | **Level Requirement:** {l_new} |\n"
                            else:
                                type_content += f"| **Level Requirement:** {mod['bt_lvl']} | **Level Requirement:** {mod['bk_lvl']} |\n"
                            
                            type_content += "| **Properties:** | **Properties:** |\n"
                            aligned = align_properties(mod['bt_props'], mod['bk_props'])
                            for old_s, new_s in aligned:
                                if normalize_text(old_s) == normalize_text(new_s):
                                    type_content += f"| {old_s} | {new_s} |\n"
                                else:
                                    old_fmt, new_fmt = get_styled_diffs(old_s, new_s)
                                    type_content += f"| {old_fmt} | {new_fmt} |\n"
                            type_content += "\n"
                
                if type_content:
                    f.write(f"## {t.capitalize()}\n\n{type_content}---\n\n")
                    has_content = True
            
            if not has_content:
                f.write("No items found in this category.\n")

    write_detail_file("ADDED.md", "Added Items", "added")
    write_detail_file("MODIFIED.md", "Modified Items", "modified")
    write_detail_file("REMOVED.md", "Removed Items", "removed")
    
    print(f"Reports generated in {out_dir}")

if __name__ == "__main__":
    compare_databases('../exports/item_db', '../exports/item_db_bt', '../output/item_diff_report')
