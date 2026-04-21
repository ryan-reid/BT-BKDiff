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
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('* '):
                item_props.append(line[2:])
            elif line.startswith('    * '):
                item_props.append(line[6:])
        
        items[item_id] = {
            'display_name': display_name, 
            'properties': item_props
        }
    return items

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
    """Surgically highlights differences between two strings using token-based diff."""
    if not old_s: 
        return "", f'**<span style="color: #3366cc;">{new_s}</span>**'
    if not new_s or new_s == "(removed)": 
        return f'<span style="color: #999999;">{old_s}</span>', f'<span style="color: #3366cc;">(removed)</span>'
    
    if normalize_text(old_s) == normalize_text(new_s):
        return old_s, new_s
    
    # Tokenize: Group numbers with ranges, signs, and percentages (e.g., +10-20%)
    def tokenize(text):
        return re.findall(r'[+-]?\d+(?:-\d+)?%?|[a-zA-Z]+|[^\w\s]|\s+', text)

    old_toks = tokenize(old_s)
    new_toks = tokenize(new_s)
    
    s = difflib.SequenceMatcher(None, old_toks, new_toks)
    old_styled_parts = []
    new_styled_parts = []
    
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        old_part = "".join(old_toks[i1:i2])
        new_part = "".join(new_toks[j1:j2])
        
        if tag == 'equal':
            old_styled_parts.append(('equal', old_part))
            new_styled_parts.append(('equal', new_part))
        elif tag == 'replace':
            if old_part: old_styled_parts.append(('removed', old_part))
            if new_part: new_styled_parts.append(('added', new_part))
        elif tag == 'delete':
            old_styled_parts.append(('removed', old_part))
        elif tag == 'insert':
            new_styled_parts.append(('added', new_part))
            
    def render(parts):
        res = ""
        last_type = None
        current_text = ""
        
        def flush():
            nonlocal res, current_text, last_type
            if not current_text: return
            if last_type == 'added':
                res += f'**<span style="color: #3366cc;">{current_text}</span>**'
            elif last_type == 'removed':
                res += f'<span style="color: #999999;">{current_text}</span>'
            else:
                res += current_text
            current_text = ""

        for type, text in parts:
            if type != last_type:
                flush()
                last_type = type
            current_text += text
        flush()
        return res

    return render(old_styled_parts), render(new_styled_parts)

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
                    bk_norm = [normalize_text(p) for p in bk_items[k]['properties']]
                    bt_norm = [normalize_text(p) for p in bt_items[k]['properties']]
                    if bk_norm != bt_norm:
                        modified[k] = {'name': bk_items[k]['display_name'], 'bk_props': bk_items[k]['properties'], 'bt_props': bt_items[k]['properties']}
                
                if added or removed or modified:
                    all_diffs[t][os.path.join(rel_path, file)] = {'added': {k: bk_items[k] for k in added}, 'removed': {k: bt_items[k] for k in removed}, 'modified': modified}

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
            f.write("- <span style=\"color: #999999;\">Gray text</span>: Removed/Old Value\n")
            f.write("- <span style=\"color: #3366cc;\">Blue text</span>: Added/New Value\n\n")
            
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
