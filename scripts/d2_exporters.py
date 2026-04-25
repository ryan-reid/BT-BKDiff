import os
import json
import re
import difflib
from typing import List, Dict, Any, Tuple
from d2_models import AnalyzedItemDTO, RunewordDTO, ExcelDiffDTO

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
        for char in '%$#_{}&': s = s.replace(char, '\\\\' + char)
        return s

    @staticmethod
    def get_styled_diffs(old_s: str, new_s: str) -> Tuple[str, str]:
        if not old_s: return "", f'$\\color{{blue}}{{\\text{{{MarkdownExporter.escape_latex(new_s)}}}}}$'
        if not new_s or new_s == "(removed)": return f'$\\color{{gray}}{{\\text{{{MarkdownExporter.escape_latex(old_s)}}}}}$', f'$\\color{{blue}}{{\\text{{(removed)}}}}$'
        
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
                    res += f'\\\\color{{{color}}}{{\\\\text{{{MarkdownExporter.escape_latex(part)}}}}}'
                elif tag == 'equal': res += f'\\\\text{{{MarkdownExporter.escape_latex(part)}}}'
            return res + "$"
        return render(old_toks, True), render(new_toks, False)

    def export_item_db(self, items: List[AnalyzedItemDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            for item in items:
                f.write(f"### {item['display_name']} ({item['id']})\n")
                f.write(f"* **Base Item:** {item['base_item']}\n")
                f.write(f"* **Level Requirement:** {item['lvl_req']}\n")
                f.write("* **Properties:**\n")
                for prop in item['properties']:
                    f.write(f"    * {prop['resolved_text']}\n")
                f.write("\n")

    def export_runewords(self, rws: List[RunewordDTO], title: str, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        content = f"# {title}\n\n"
        rw_blocks = []
        for rw in rws:
            block = f"### {rw['name']}\n"
            block += f"* **Runes:** {' + '.join(rw['runes'])}\n"
            block += f"* **Base Items:** {', '.join(rw['base_items'])}\n"
            block += "* **Properties:**\n"
            for prop in rw['properties']:
                block += f"    * {prop['resolved_text']}\n"
            rw_blocks.append(block)
        
        content += "\n".join(rw_blocks)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content.strip() + "\n")

    def export_excel_diff(self, diff: ExcelDiffDTO, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Differences for {diff['filename']}\n\n")
            f.write(f"*Key column used: `{diff['key_used']}`*\n\n")
            if diff['added_cols']: f.write(f"## Added Columns: `{', '.join(diff['added_cols'])}`  \n\n")
            if diff['removed_cols']: f.write(f"## Removed Columns: `{', '.join(diff['removed_cols'])}`  \n\n")
            if diff['added_rows']:
                f.write(f"## Added Rows ({len(diff['added_rows'])})\n")
                for r in diff['added_rows']: f.write(f"- {r}\n")
                f.write("\n")
            if diff['removed_rows']:
                f.write(f"## Removed Rows ({len(diff['removed_rows'])})\n")
                for r in diff['removed_rows']: f.write(f"- {r}\n")
                f.write("\n")
            if diff['modified_rows']:
                f.write(f"## Modified Rows ({len(diff['modified_rows'])})\n")
                for key, row_diff in sorted(diff['modified_rows'].items()):
                    f.write(f"### {key}\n")
                    for col, vals in row_diff.items():
                        old_fmt, new_fmt = self.get_styled_diffs(str(vals['bt_old']), str(vals['bk_new']))
                        f.write(f"- `{col}`: {old_fmt} (Old) &rarr; {new_fmt} (New)\n")
                    f.write("\n")
