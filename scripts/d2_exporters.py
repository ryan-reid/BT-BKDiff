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
    def escape_latex(s: str) -> str:
        if not s: return ""
        for char in '%$#_{}&': s = s.replace(char, '\\' + char)
        return s

    @staticmethod
    def get_styled_diffs(old_s: str, new_s: str) -> Tuple[str, str]:
        def fmt(color, text):
            return r"$\color{" + color + r"}{\text{" + MarkdownExporter.escape_latex(text) + r"}}$"

        if not old_s: return "", fmt("blue", new_s)
        if not new_s or new_s == "(removed)": 
            return fmt("gray", old_s), fmt("blue", "(removed)")
        
        def normalize_text(t):
            return re.sub(r'\s+', ' ', re.sub(r'ÿc.', '', t)).strip()

        if normalize_text(old_s) == normalize_text(new_s):
            return old_s, new_s

        def tokenize(text: str) -> List[str]:
            return re.findall(r'[+-]?\d+(?:-\d+)?%?|[a-zA-Z]+|[^\w\s]|\s+', text)

        old_toks, new_toks = tokenize(old_s), tokenize(new_s)
        matcher = difflib.SequenceMatcher(None, old_toks, new_toks)
        
        def render(tokens: List[str], is_old: bool) -> str:
            res = "$"
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                part = "".join(tokens[i1:i2] if is_old else tokens[j1:j2])
                if (is_old and tag in ['replace', 'delete']) or (not is_old and tag in ['replace', 'insert']):
                    color = 'gray' if is_old else 'blue'
                    res += r"\color{" + color + r"}{\text{" + MarkdownExporter.escape_latex(part) + r"}}"
                elif tag == 'equal': 
                    res += r"\text{" + MarkdownExporter.escape_latex(part) + r"}}"
            return res + "$"
        return render(old_toks, True), render(new_toks, False)

    def export_item_db(self, items: List[AnalyzedItemDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {title}\n\n"
        blocks = []
        for item in items:
            block = f"### {item['display_name']} ({item['id']})\n"
            block += f"* **Base Item:** {item['base_item']}\n"
            block += f"* **Level Requirement:** {item['lvl_req']}\n"
            block += "* **Properties:**\n"
            for prop in item['properties']:
                block += f"    * {prop['resolved_text']}\n"
            blocks.append(block)
        content += "\n".join(blocks)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + "\n")

    def export_runewords(self, rws: List[RunewordDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {title}\n\n"
        blocks = []
        for rw in rws:
            block = f"### {rw['name']}\n"
            block += f"* **Runes:** {' + '.join(rw['runes'])}\n"
            block += f"* **Base Items:** {', '.join(rw['base_items'])}\n"
            block += "* **Properties:**\n"
            for prop in rw['properties']:
                block += f"    * {prop['resolved_text']}\n"
            blocks.append(block)
        content += "\n".join(blocks)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + "\n")

    def export_cube_recipes(self, recipes: List[CubeRecipeDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {title}\n\n"
        blocks = []
        for r in recipes:
            block = f"## {r['description']}\n\n"
            block += f"**Inputs:** {' + '.join([f'**{inp}**' for inp in r['inputs']])}\n\n"
            block += f"**Outputs:** {', '.join([f'**{out}**' for out in r['outputs']])}\n\n"
            block += "---\n"
            blocks.append(block)
        content += "\n".join(blocks)
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
            f.write("Click the links in the header to see detailed breakdowns.\n")

        # 2. ADDED.md
        with open(os.path.join(output_dir, "ADDED.md"), 'w', encoding='utf-8') as f:
            f.write("# Added Items\n\n")
            for k, item in sorted(diff['added'].items()):
                name = item.get('display_name') or item.get('name')
                base = item.get('base_item') or ', '.join(item.get('base_items', []))
                lvl = item.get('lvl_req', '0')
                
                f.write(f"**{name}** ({k})\n\n")
                f.write("| BT Diablo (Old) | BK Diablo (New) |\n| :--- | :--- |\n")
                f.write(f"| | **Base Item:** {base} |\n")
                f.write(f"| | **Level Requirement:** {lvl} |\n")
                f.write("| | **Properties:** |\n")
                for prop in item['properties']:
                    _, new_fmt = self.get_styled_diffs("", prop['resolved_text'])
                    f.write(f"| | {new_fmt} |\n")
                f.write("\n")

        # 3. REMOVED.md
        with open(os.path.join(output_dir, "REMOVED.md"), 'w', encoding='utf-8') as f:
            f.write("# Removed Items\n\n")
            for k, item in sorted(diff['removed'].items()):
                name = item.get('display_name') or item.get('name')
                f.write(f"- **{name}** ({k})\n")

        # 4. MODIFIED.md
        with open(os.path.join(output_dir, "MODIFIED.md"), 'w', encoding='utf-8') as f:
            f.write("# Modified Items\n\n")
            f.write(r"- $\color{gray}{\text{Gray text}}$: Removed/Old Value" + "\n")
            f.write(r"- $\color{blue}{\text{Blue text}}$: Added/New Value" + "\n\n")
            for k, mod in sorted(diff['modified'].items()):
                f.write(f"**{mod['name']}** ({k})\n\n")
                f.write("| BT Diablo (Old) | BK Diablo (New) |\n| :--- | :--- |\n")
                b_old, b_new = self.get_styled_diffs(mod['bt_base'], mod['bk_base'])
                f.write(f"| **Base Item:** {b_old} | **Base Item:** {b_new} |\n")
                l_old, l_new = self.get_styled_diffs(mod['bt_lvl'], mod['bk_lvl'])
                f.write(f"| **Level Requirement:** {l_old} | **Level Requirement:** {l_new} |\n")
                f.write("| **Properties:** | **Properties:** |\n")
                
                # Align properties for display
                old_props = mod['bt_props']
                new_props = mod['bk_props']
                
                def get_stat_key(s):
                    s = re.sub(r'\s+', ' ', re.sub(r'ÿc.', '', s)).strip()
                    return re.sub(r'[+-]?\d+(?:-\d+)?', '', s).strip().lower()

                aligned = []
                old_used, new_used = set(), set()
                for i, op in enumerate(old_props):
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
        lines = [f"# Differences for {diff['filename']}\n", f"*Key column used: `{diff['key_used']}`*\n"]
        if diff['added_cols']: lines.append(f"## Added Columns: `{', '.join(diff['added_cols'])}`  \n")
        if diff['removed_cols']: lines.append(f"## Removed Columns: `{', '.join(diff['removed_cols'])}`  \n")
        if diff['added_rows']:
            lines.append(f"## Added Rows ({len(diff['added_rows'])})")
            for r in diff['added_rows']: lines.append(f"- {r}")
            lines.append("")
        if diff['removed_rows']:
            lines.append(f"## Removed Rows ({len(diff['removed_rows'])})")
            for r in diff['removed_rows']: lines.append(f"- {r}")
            lines.append("")
        if diff['modified_rows']:
            lines.append(f"## Modified Rows ({len(diff['modified_rows'])})")
            for key, row_diff in sorted(diff['modified_rows'].items()):
                lines.append(f"### {key}")
                for col, vals in row_diff.items():
                    old_fmt, new_fmt = self.get_styled_diffs(str(vals['bt_old']), str(vals['bk_new']))
                    lines.append(f"- `{col}`: {old_fmt} (Old) &rarr; {new_fmt} (New)")
                lines.append("")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines).strip() + "\n")
