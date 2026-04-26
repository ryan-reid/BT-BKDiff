import os
import json
import re
import difflib
from typing import List, Dict, Any, Tuple
from d2_models import AnalyzedItemDTO, RunewordDTO, ExcelDiffDTO, CubeRecipeDTO, ItemDiffDTO

class BaseExporter:
    def export(self, data: Any, output_path: str):
        raise NotImplementedError

class JsonExporter(BaseExporter):
    def export(self, data: Any, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

class MarkdownExporter(BaseExporter):
    @staticmethod
    def escape_markdown(s: str) -> str:
        """Surgical escaping for Markdown special characters."""
        if not s: return ""
        # 1. Escape literal backslashes
        s = s.replace('\\', '\\\\')
        # 2. Escape these characters: _, *, [, ], (, ), #, +, -, ., !
        for char in r'_*[]()#+-.!':
            s = s.replace(char, '\\' + char)
        return s

    @staticmethod
    def escape_latex(s: str) -> str:
        """Escapes text for use inside a LaTeX block on GitHub ($ ... $)."""
        if not s: return ""
        # 0. Remove D2 color codes
        s = re.sub(r'ÿc.', '', s)
        # 1. Escape literal backslashes
        s = s.replace('\\', r'\\textbackslash ')
        # 2. Escape { } $ % & # _ with double backslash
        for char in r'{}$%&#_':
            s = s.replace(char, r'\\' + char)
        # 3. Special commands
        s = s.replace('^', r'\\textasciicircum ')
        s = s.replace('~', r'\\textasciitilde ')
        s = s.replace('|', r'\\vert ')
        return s

    @staticmethod
    def get_styled_diffs(old_s: str, new_s: str) -> Tuple[str, str]:
        """Generates color-coded LaTeX diffs for two strings."""
        def fmt(color, text):
            if not text: return ""
            escaped = MarkdownExporter.escape_latex(text)
            if color:
                return r"$\color{" + color + r"}{\\text{" + escaped + r"}}$"
            return r"$\text{" + escaped + r"}$"

        if not old_s: return "", fmt("blue", new_s)
        if not new_s or new_s == "(removed)": 
            return fmt("gray", old_s), fmt("blue", "(removed)")
        
        def normalize_text(t):
            return re.sub(r'\s+', ' ', re.sub(r'ÿc.', '', t)).strip()

        if normalize_text(old_s) == normalize_text(new_s):
            return fmt("", old_s), fmt("", new_s)

        def tokenize(text: str) -> List[str]:
            return re.findall(r'[+-]?\d+(?:-\d+)?%?|[a-zA-Z]+|[^\w\s]|\s+', text)

        old_toks, new_toks = tokenize(old_s), tokenize(new_s)
        matcher = difflib.SequenceMatcher(None, old_toks, new_toks)
        
        def render(tokens: List[str], is_old: bool) -> str:
            parts = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                part = "".join(tokens[i1:i2] if is_old else tokens[j1:j2])
                if not part: continue
                escaped = MarkdownExporter.escape_latex(part)
                if (is_old and tag in ['replace', 'delete']) or (not is_old and tag in ['replace', 'insert']):
                    color = 'gray' if is_old else 'blue'
                    parts.append(r"\\color{" + color + r"}{\\text{" + escaped + r"}}")
                elif tag == 'equal': 
                    parts.append(r"\\text{" + escaped + r"}")
            if not parts: return ""
            return "$" + "".join(parts) + "$"
        return render(old_toks, True), render(new_toks, False)

    def export_item_db(self, items: List[AnalyzedItemDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {title}\n\n"
        for item in items:
            name = self.escape_markdown(item.get('display_name') or item.get('name'))
            item_id = self.escape_markdown(str(item.get('id', '')))
            content += f"### {name} ({item_id})\n"
            content += f"* **Base Item:** {self.escape_markdown(item.get('base_item', ''))}\n"
            content += f"* **Level Requirement:** {item.get('lvl_req', '0')}\n"
            content += "* **Properties:**\n"
            for prop in item['properties']:
                content += f"    * {self.escape_markdown(prop['resolved_text'])}\n"
            content += "\n"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + "\n")

    def export_runewords(self, rws: List[RunewordDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {title}\n\n"
        for rw in rws:
            name = self.escape_markdown(rw['name'])
            content += f"### {name}\n"
            runes_str = ' + '.join([self.escape_markdown(r) for r in rw['runes']])
            content += f"* **Runes:** {runes_str}\n"
            bases_str = ', '.join([self.escape_markdown(bi) for bi in rw['base_items']])
            content += f"* **Base Items:** {bases_str}\n"
            content += "* **Properties:**\n"
            for prop in rw['properties']:
                content += f"    * {self.escape_markdown(prop['resolved_text'])}\n"
            content += "\n"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + "\n")

    def export_cube_recipes(self, recipes: List[CubeRecipeDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {title}\n\n"
        for r in recipes:
            content += f"## {self.escape_markdown(r['description'])}\n\n"
            inputs_str = ' + '.join([f"**{self.escape_markdown(inp)}**" for inp in r['inputs']])
            content += f"**Inputs:** {inputs_str}\n\n"
            outputs_str = ', '.join([f"**{self.escape_markdown(out)}**" for out in r['outputs']])
            content += f"**Outputs:** {outputs_str}\n\n"
            content += "---\n"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + "\n")

    def export_item_diff(self, diff: ItemDiffDTO, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. SUMMARY.md
        with open(os.path.join(output_dir, "SUMMARY.md"), 'w', encoding='utf-8') as f:
            f.write("# Item Database Comparison Summary\n\n")
            f.write("| Type | [Added](ADDED.md) | [Removed](REMOVED.md) | [Modified](MODIFIED.md) |\n")
            f.write("| :--- | :---: | :---: | :---: |\n")
            f.write(f"| All Items | {len(diff['added'])} | {len(diff['removed'])} | {len(diff['modified'])} |\n\n")

        # 2. Split Added Items into categories
        added_dir = os.path.join(output_dir, "added")
        os.makedirs(added_dir, exist_ok=True)
        
        uniques, runewords, sets = [], [], []
        for k, item in diff['added'].items():
            if 'runes' in item or (item.get('raw_row') and 'Rune1' in item['raw_row']):
                runewords.append(item)
            elif item.get('raw_row') and 'set' in item['raw_row']:
                sets.append(item)
            else:
                uniques.append(item)

        added_toc = ["# Added Items Breakdown\n", "New items categorized by type to ensure optimal rendering.\n"]
        
        def write_items_to_file(items_list, title, filename, sub_dir=""):
            if not items_list: return None
            full_sub_dir = os.path.join(added_dir, sub_dir)
            os.makedirs(full_sub_dir, exist_ok=True)
            path = os.path.join(full_sub_dir, filename)
            rel_path = os.path.join("added", sub_dir, filename).replace("\\", "/")
            
            with open(path, 'w', encoding='utf-8') as f_out:
                f_out.write(f"# {title}\n\n")
                for item in sorted(items_list, key=lambda x: x.get('display_name') or x.get('name', '')):
                    name = self.escape_markdown(item.get('display_name') or item.get('name'))
                    base = self.escape_markdown(item.get('base_item', '') or ', '.join(item.get('base_items', [])))
                    item_id = self.escape_markdown(str(item.get('id', item.get('name', ''))))
                    
                    f_out.write(f"**{name}** ({item_id})\n\n")
                    f_out.write("| BT Diablo (Old) | BK Diablo (New) |\n| :--- | :--- |\n")
                    f_out.write(f"| | **Base Item:** {base} |\n")
                    f_out.write(f"| | **Level Requirement:** {item.get('lvl_req', '0')} |\n")
                    f_out.write("| | **Properties:** |\n")
                    for prop in item['properties']:
                        _, new_fmt = self.get_styled_diffs("", prop['resolved_text'])
                        f_out.write(f"| | {new_fmt} |\n")
                    f_out.write("\n")
            return rel_path

        # Sub-categorize Uniques
        if uniques:
            added_toc.append("## Uniques\n")
            unique_groups = {}
            for item in uniques:
                cat = item.get('item_type', 'Other')
                if cat not in unique_groups: unique_groups[cat] = []
                unique_groups[cat].append(item)
            
            for cat, items in sorted(unique_groups.items()):
                safe_name = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                rel = write_items_to_file(items, f"Added Unique {cat}", safe_name, "uniques")
                added_toc.append(f"- [{cat}]({rel})\n")

        # Sub-categorize Runewords
        if runewords:
            added_toc.append("\n## Runewords\n")
            rw_groups = {}
            for rw in runewords:
                cat = rw.get('base_items', ['Other'])[0] if rw.get('base_items') else 'Other'
                if cat not in rw_groups: rw_groups[cat] = []
                rw_groups[cat].append(rw)
            
            for cat, items in sorted(rw_groups.items()):
                safe_name = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                rel = write_items_to_file(items, f"Added {cat} Runewords", safe_name, "runewords")
                added_toc.append(f"- [{cat}]({rel})\n")

        # Sub-categorize Sets
        if sets:
            added_toc.append("\n## Sets\n")
            set_groups = {}
            for item in sets:
                cat = item.get('item_type', 'Other')
                if cat not in set_groups: set_groups[cat] = []
                set_groups[cat].append(item)
                
            for cat, items in sorted(set_groups.items()):
                safe_name = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                rel = write_items_to_file(items, f"Added Set {cat}", safe_name, "sets")
                added_toc.append(f"- [{cat}]({rel})\n")

        with open(os.path.join(output_dir, "ADDED.md"), 'w', encoding='utf-8') as f:
            f.write("".join(added_toc))

        # 3. REMOVED.md
        with open(os.path.join(output_dir, "REMOVED.md"), 'w', encoding='utf-8') as f:
            f.write("# Removed Items\n\n")
            for k, item in sorted(diff['removed'].items()):
                name = self.escape_markdown(item.get('display_name') or item.get('name'))
                f.write(f"- **{name}** ({self.escape_markdown(str(k))})\n")

        # 4. MODIFIED.md
        with open(os.path.join(output_dir, "MODIFIED.md"), 'w', encoding='utf-8') as f:
            f.write("# Modified Items\n\n")
            f.write(r"- $\color{gray}{\\text{Gray text}}$: Removed/Old Value" + "\n")
            f.write(r"- $\color{blue}{\\text{Blue text}}$: Added/New Value" + "\n\n")
            for k, mod in sorted(diff['modified'].items()):
                f.write(f"**{self.escape_markdown(mod['name'])}** ({self.escape_markdown(str(k))})\n\n")
                f.write("| BT Diablo (Old) | BK Diablo (New) |\n| :--- | :--- |\n")
                b_old, b_new = self.get_styled_diffs(mod['bt_base'], mod['bk_base'])
                f.write(f"| **Base Item:** {b_old} | **Base Item:** {b_new} |\n")
                l_old, l_new = self.get_styled_diffs(str(mod['bt_lvl']), str(mod['bk_lvl']))
                f.write(f"| **Level Requirement:** {l_old} | **Level Requirement:** {l_new} |\n")
                f.write("| **Properties:** | **Properties:** |\n")
                
                old_props = mod['bt_props']
                new_props = mod['bk_props']
                
                def get_stat_key(s):
                    s = re.sub(r'\s+', ' ', re.sub(r'ÿc.', '', s)).strip()
                    return re.sub(r'[+-]?\d+(?:-\d+)?', '', s).strip().lower()

                aligned = []
                old_used, new_used = set(), set()
                for i, op in enumerate(old_props):
                    for j, np in enumerate(new_props):
                        if j not in new_used and op == np:
                            aligned.append((op, np))
                            old_used.add(i); new_used.add(j); break
                for i, op in enumerate(old_props):
                    if i in old_used: continue
                    for j, np in enumerate(new_props):
                        if j not in new_used and get_stat_key(op) == get_stat_key(np):
                            aligned.append((op, np))
                            old_used.add(i); new_used.add(j); break
                for i, op in enumerate(old_props):
                    if i not in old_used: aligned.append((op, "(removed)"))
                for j, np in enumerate(new_props):
                    if j not in new_used: aligned.append(("", np))

                for old_s, new_s in aligned:
                    o_fmt, n_fmt = self.get_styled_diffs(old_s, new_s)
                    f.write(f"| {o_fmt} | {n_fmt} |\n")
                f.write("\n")

    def export_excel_diff(self, diff: ExcelDiffDTO, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        lines = [f"# Differences for {diff['filename']}\n", f"*Key column used: `{self.escape_markdown(diff['key_used'])}`*\n"]
        if diff['added_cols']: lines.append(f"## Added Columns: `{', '.join([self.escape_markdown(c) for c in diff['added_cols']])}`  \n")
        if diff['removed_cols']: lines.append(f"## Removed Columns: `{', '.join([self.escape_markdown(c) for c in diff['removed_cols']])}`  \n")
        if diff['added_rows']: 
            lines.append(f"## Added Rows ({len(diff['added_rows'])})")
            for r in diff['added_rows']: lines.append(f"- {self.escape_markdown(r)}")
        if diff['removed_rows']:
            lines.append(f"## Removed Rows ({len(diff['removed_rows'])})")
            for r in diff['removed_rows']: lines.append(f"- {self.escape_markdown(r)}")
        if diff['modified_rows']:
            lines.append(f"## Modified Rows ({len(diff['modified_rows'])})")
            for key, row_diff in sorted(diff['modified_rows'].items()):
                lines.append(f"### {self.escape_markdown(key)}")
                for col, vals in row_diff.items():
                    old_fmt, new_fmt = self.get_styled_diffs(str(vals['bt_old']), str(vals['bk_new']))
                    lines.append(f"- `{self.escape_markdown(col)}`: {old_fmt} (Old) &rarr; {new_fmt} (New)")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines).strip() + "\n")
