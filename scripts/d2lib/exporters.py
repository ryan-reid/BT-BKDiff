import os
import json
import re
import html
import difflib
from typing import List, Dict, Any, Tuple
from d2lib.models import AnalyzedItemDTO, RunewordDTO, ExcelDiffDTO, CubeRecipeDTO, ItemDiffDTO, SkillTreeDTO

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
        if not s: return ""
        s = s.replace('\\', '\\\\')
        for char in r'_*[]()#+-.!':
            s = s.replace(char, '\\' + char)
        return s

    @staticmethod
    def escape_latex(s: str) -> str:
        """Escapes text for use inside a LaTeX block on GitHub ($ ... $)."""
        if not s: return ""
        # 1. Strip D2 color codes
        s = re.sub(r'ÿc.', '', str(s))
        # 2. Simple character escaping.
        # We replace the most troublesome characters first.
        # We do NOT use \textbackslash{} for literal backslashes here to avoid parsing depth issues.
        s = s.replace('\\', '/')
        s = s.replace('{', '\\{').replace('}', '\\}')
        s = s.replace('%', '\\%')
        s = s.replace('$', '\\$')
        s = s.replace('&', '\\&')
        s = s.replace('#', '\\#')
        s = s.replace('_', '\\_')
        return s

    @staticmethod
    def escape_inline_html(s: Any) -> str:
        if s is None:
            return ""
        text = re.sub(r'Ãƒ(?:Æ’Ã‚)?Â¿c.', '', str(s))
        return html.escape(text, quote=False)

    @staticmethod
    def escape_table_cell(s: Any) -> str:
        """Escapes plain-text content for safe Markdown table rendering."""
        if s is None:
            return ""
        text = re.sub(r'Ã(?:ƒÂ)?¿c.', '', str(s))
        text = text.replace('\r', ' ').replace('\n', ' ').strip()
        return text.replace('|', '\\|')

    @staticmethod
    def format_limit_cell(limit: Any) -> str:
        if limit is None:
            return ""
        text = str(limit).strip()
        if not text or text == "--":
            return "--"
        text = re.sub(r"\bMax:\s*", "", text)
        return text

    @staticmethod
    def get_styled_diffs(old_s: str, new_s: str) -> Tuple[str, str]:
        def fmt(text: str, changed: bool = False) -> str:
            if not text:
                text = "empty"
            escaped = MarkdownExporter.escape_inline_html(text)
            if changed:
                return f"<strong><code>{escaped}</code></strong>"
            return f"<code>{escaped}</code>"

        def normalize_text(t): return re.sub(r'\s+', ' ', re.sub(r'ÿc.', '', t)).strip()

        if not old_s:
            return fmt("", changed=True), fmt(new_s, changed=True)
        if not new_s or new_s == "(removed)":
            return fmt(old_s, changed=True), fmt("(removed)", changed=True)
        if normalize_text(old_s) == normalize_text(new_s):
            return fmt(old_s), fmt(new_s)
        return fmt(old_s, changed=True), fmt(new_s, changed=True)

    def export_skill_tree(self, tree: SkillTreeDTO, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {self.escape_markdown(tree['class_name'])} Skill Tree\n\n"
        for skill in tree['skills']:
            content += f"## {self.escape_markdown(skill['name'])}\n\n"
            content += "> Work in Progress\n\n"
            content += "| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |\n"
            content += "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n"
            for effect in skill['effects']:
                row = [
                    self.escape_table_cell(effect['label']),
                    self.escape_table_cell(effect['scaling']),
                    self.escape_table_cell(effect['l1']),
                    self.escape_table_cell(effect['l10']),
                    self.escape_table_cell(effect['l20']),
                    self.escape_table_cell(effect['l30']),
                    self.escape_table_cell(self.format_limit_cell(effect['limit']))
                ]
                content += f"| {' | '.join(row)} |\n"

            if skill['synergies']:
                content += "\n### Synergies\n"
                for syn in skill['synergies']:
                    content += f"* **{self.escape_markdown(syn['name'])}**: {self.escape_markdown(syn['effect'])}\n"
            content += "\n---\n\n"
        with open(output_path, 'w', encoding='utf-8') as f: f.write(content)

    # ... (other methods)
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

        def write_category_files(items_dict, base_name, is_modified=False):
            category_dir = os.path.join(output_dir, base_name.lower())
            os.makedirs(category_dir, exist_ok=True)
            
            uniques, runewords, sets = [], [], []
            for k, item in items_dict.items():
                item['original_key'] = k
                raw_row = item.get('raw_row', {})
                if 'runes' in item or 'Rune1' in raw_row:
                    runewords.append(item)
                elif 'set' in raw_row:
                    sets.append(item)
                else:
                    uniques.append(item)

            toc = [f"# {base_name} Items Breakdown\n", "Categorized by type to ensure optimal rendering.\n"]
            
            def write_items_to_file(items_list, title, filename, sub_dir=""):
                if not items_list: return None
                full_sub_dir = os.path.join(category_dir, sub_dir)
                os.makedirs(full_sub_dir, exist_ok=True)
                path = os.path.join(full_sub_dir, filename)
                rel_path = os.path.join(base_name.lower(), sub_dir, filename).replace("\\", "/")
                
                with open(path, 'w', encoding='utf-8') as f_out:
                    f_out.write(f"# {title}\n\n")
                    if is_modified:
                        f_out.write("- `<strong><code>value</code></strong>`: Changed value\n")
                        f_out.write("- `<strong><code>empty</code></strong>`: No value on that side\n\n")

                    for item in sorted(items_list, key=lambda x: x.get('display_name') or x.get('name', '')):
                        k = item['original_key']
                        if is_modified:
                            name = self.escape_markdown(item.get('name', ''))
                            f_out.write(f"**{name}** ({self.escape_markdown(str(k))})\n\n")
                            f_out.write("| BT Diablo (Old) | BK Diablo (New) |\n| :--- | :--- |\n")
                            b_old, b_new = self.get_styled_diffs(item['bt_base'], item['bk_base'])
                            f_out.write(f"| **Base Item:** {b_old} | **Base Item:** {b_new} |\n")
                            l_old, l_new = self.get_styled_diffs(str(item['bt_lvl']), str(item['bk_lvl']))
                            f_out.write(f"| **Level Requirement:** {l_old} | **Level Requirement:** {l_new} |\n")
                            f_out.write("| **Properties:** | **Properties:** |\n")
                            
                            old_props = item['bt_props']
                            new_props = item['bk_props']
                            
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
                                f_out.write(f"| {o_fmt} | {n_fmt} |\n")
                            f_out.write("\n")
                        else:
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

            # Sub-categorize
            if uniques:
                toc.append("## Uniques\n")
                unique_groups = {}
                for item in uniques:
                    cat = item.get('item_type', 'Other')
                    if cat not in unique_groups: unique_groups[cat] = []
                    unique_groups[cat].append(item)
                for cat, items in sorted(unique_groups.items()):
                    safe_name = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                    rel = write_items_to_file(items, f"{base_name} Unique {cat}", safe_name, "uniques")
                    toc.append(f"- [{cat}]({rel})\n")

            if runewords:
                toc.append("\n## Runewords\n")
                rw_groups = {}
                for rw in runewords:
                    cat = rw.get('base_items', ['Other'])[0] if rw.get('base_items') else 'Other'
                    if cat not in rw_groups: rw_groups[cat] = []
                    rw_groups[cat].append(rw)
                for cat, items in sorted(rw_groups.items()):
                    safe_name = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                    rel = write_items_to_file(items, f"{base_name} {cat} Runewords", safe_name, "runewords")
                    toc.append(f"- [{cat}]({rel})\n")

            if sets:
                toc.append("\n## Sets\n")
                set_groups = {}
                for item in sets:
                    cat = item.get('item_type', 'Other')
                    if cat not in set_groups: set_groups[cat] = []
                    set_groups[cat].append(item)
                for cat, items in sorted(set_groups.items()):
                    safe_name = cat.lower().replace(" ", "_").replace("/", "_") + ".md"
                    rel = write_items_to_file(items, f"{base_name} Set {cat}", safe_name, "sets")
                    toc.append(f"- [{cat}]({rel})\n")

            with open(os.path.join(output_dir, f"{base_name.upper()}.md"), 'w', encoding='utf-8') as f:
                f.write("".join(toc))

        write_category_files(diff['added'], "Added")
        with open(os.path.join(output_dir, "REMOVED.md"), 'w', encoding='utf-8') as f:
            f.write("# Removed Items\n\n")
            for k, item in sorted(diff['removed'].items()):
                name = self.escape_markdown(item.get('display_name') or item.get('name'))
                f.write(f"- **{name}** ({self.escape_markdown(str(k))})\n")
        write_category_files(diff['modified'], "Modified", is_modified=True)

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
