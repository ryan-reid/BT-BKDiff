import os
import json
import re
import difflib
import html
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
        def fmt(color, text):
            if not text: return ""
            escaped = MarkdownExporter.escape_latex(text)
            if color:
                return f"$\\color{{{color}}}{{\\text{{{escaped}}}}}$"
            return f"$\\text{{{escaped}}}$"

        if not old_s: return "", fmt("blue", new_s)
        if not new_s or new_s == "(removed)": 
            return fmt("gray", old_s), fmt("blue", "(removed)")
        
        def normalize_text(t): return re.sub(r'\s+', ' ', re.sub(r'ÿc.', '', t)).strip()
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
                    parts.append(f"\\color{{{color}}}{{\\text{{{escaped}}}}}")
                elif tag == 'equal': 
                    parts.append(f"$\text{{{escaped}}}$")
            if not parts: return ""
            return "$" + "".join(parts) + "$"
        return render(old_toks, True), render(new_toks, False)

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
            
            # Icon Integration for Codex/UI
            family = "unique" if "Unique" in title else "set" if "Set" in title else ""
            if family:
                from d2lib.services import _slugify
                icon_name = f"{family}-{_slugify(str(item.get('id', '')))}.png"
                # Path is relative to the export file. Exports are in exports/item_db/...
                # Icons are in docs/wiki/assets/item-icons/
                # Typical export path: BT-BKDiff/exports/item_db/uniques/others/helms.md
                # We need to go up 4 levels to get to BT-BKDiff/
                content += f"![{name} icon](../../../../docs/wiki/assets/item-icons/{icon_name})\n\n"

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
            if rw.get('rune_properties'):
                content += "* **Properties from Runes:**\n"
                for rune in rw['rune_properties']:
                    rune_name = self.escape_markdown(rune['rune'])
                    rune_props = '; '.join(self.escape_markdown(prop['resolved_text']) for prop in rune['properties'])
                    content += f"    * **{rune_name}:** {rune_props}\n"
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
                        f_out.write(r"- $\color{gray}{\\text{Gray text}}$: Removed/Old Value" + "\n")
                        f_out.write(r"- $\color{blue}{\\text{Blue text}}$: Added/New Value" + "\n\n")

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


class HtmlReportExporter(BaseExporter):
    """Writes browser-friendly versions of the generated diff reports."""

    REPORT_CSS = """
    :root {
      color-scheme: light;
      --bg: #f7f5f0;
      --surface: #fffdf8;
      --surface-2: #f0ebe1;
      --text: #241f19;
      --muted: #6c6258;
      --line: #d8cfc2;
      --old: #7a7168;
      --old-bg: #ebe6df;
      --new: #075c8f;
      --new-bg: #dceefa;
      --accent: #8c4b2f;
    }
    * { box-sizing: border-box; }
    html { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: var(--bg); color: var(--text); line-height: 1.5; }
    .page { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 56px; }
    header { border-bottom: 1px solid var(--line); margin-bottom: 24px; padding-bottom: 18px; }
    h1 { margin: 0 0 8px; font-size: clamp(1.8rem, 4vw, 3rem); line-height: 1.05; }
    h2 { margin: 28px 0 12px; font-size: 1.2rem; }
    h3 { margin: 22px 0 10px; font-size: 1rem; color: var(--accent); }
    a { color: #0a5b86; text-decoration-thickness: 1px; text-underline-offset: 3px; }
    .muted { color: var(--muted); margin: 0; }
    .nav { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 0; }
    .nav a, .pill { border: 1px solid var(--line); border-radius: 999px; padding: 5px 10px; background: var(--surface); font-size: .9rem; text-decoration: none; }
    .card { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 16px; margin: 14px 0; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    .stat { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px; }
    .stat strong { display: block; font-size: 1.6rem; }
    table { width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--line); margin: 12px 0 18px; }
    th, td { border-bottom: 1px solid var(--line); padding: 9px 10px; text-align: left; vertical-align: top; }
    th { background: var(--surface-2); font-size: .86rem; color: var(--muted); }
    tr:last-child td { border-bottom: 0; }
    code { background: var(--surface-2); border-radius: 4px; padding: 1px 4px; }
    .diff-old { color: var(--old); background: var(--old-bg); border-radius: 4px; padding: 1px 3px; }
    .diff-new { color: var(--new); background: var(--new-bg); border-radius: 4px; padding: 1px 3px; }
    .empty { color: var(--muted); font-style: italic; }
    .item-title { font-weight: 700; margin: 0 0 8px; }
    .properties { margin: 8px 0 0; padding-left: 20px; }
    .properties li { margin: 3px 0; }
    @media (max-width: 720px) {
      .page { width: min(100% - 20px, 1180px); padding-top: 18px; }
      th, td { padding: 8px; }
      table { display: block; overflow-x: auto; }
    }
    """

    def export(self, data: Any, output_path: str):
        raise NotImplementedError

    @staticmethod
    def escape(value: Any) -> str:
        if value is None:
            return ""
        text = re.sub(r'Ã¿c.', '', str(value))
        return html.escape(text, quote=True)

    @staticmethod
    def report_filename(value: str, ext: str = ".html") -> str:
        safe = str(value).lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe = re.sub(r"[^a-z0-9_.-]+", "_", safe).strip("._")
        return f"{safe or 'other'}{ext}"

    @staticmethod
    def _stat_key(text: str) -> str:
        text = re.sub(r'\s+', ' ', re.sub(r'Ã¿c.', '', text or '')).strip()
        return re.sub(r'[+-]?\d+(?:-\d+)?', '', text).strip().lower()

    def _ensure_assets(self, output_dir: str) -> None:
        assets_dir = os.path.join(output_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        with open(os.path.join(assets_dir, "report.css"), "w", encoding="utf-8") as f:
            f.write(self.REPORT_CSS.strip() + "\n")

    def _page(self, title: str, body: str, subtitle: str = "", css_href: str = "assets/report.css") -> str:
        subtitle_html = f'<p class="muted">{self.escape(subtitle)}</p>' if subtitle else ""
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{self.escape(title)}</title>
  <link rel="stylesheet" href="{self.escape(css_href)}">
</head>
<body>
  <main class="page">
    <header>
      <h1>{self.escape(title)}</h1>
      {subtitle_html}
    </header>
    {body}
  </main>
</body>
</html>
"""

    def _write_page(self, path: str, title: str, body: str, subtitle: str = "", css_href: str = "assets/report.css") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._page(title, body, subtitle, css_href))

    def _diff_pair(self, old_s: Any, new_s: Any) -> Tuple[str, str]:
        old_text = "" if old_s is None else str(old_s)
        new_text = "" if new_s is None else str(new_s)
        if not old_text and not new_text:
            return '<span class="empty">blank</span>', '<span class="empty">blank</span>'
        if not old_text:
            return '<span class="empty">blank</span>', f'<span class="diff-new">{self.escape(new_text)}</span>'
        if not new_text or new_text == "(removed)":
            return f'<span class="diff-old">{self.escape(old_text)}</span>', '<span class="diff-new">(removed)</span>'

        def normalize(text: str) -> str:
            return re.sub(r'\s+', ' ', re.sub(r'Ã¿c.', '', text)).strip()

        if normalize(old_text) == normalize(new_text):
            escaped = self.escape(old_text)
            return escaped, escaped

        token_pattern = r'[+-]?\d+(?:-\d+)?%?|[a-zA-Z]+|[^\w\s]|\s+'
        old_tokens = re.findall(token_pattern, old_text)
        new_tokens = re.findall(token_pattern, new_text)
        matcher = difflib.SequenceMatcher(None, old_tokens, new_tokens)

        def render(tokens: List[str], is_old: bool) -> str:
            parts = []
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                part = "".join(tokens[i1:i2] if is_old else tokens[j1:j2])
                if not part:
                    continue
                escaped = self.escape(part)
                changed = (is_old and tag in ["replace", "delete"]) or (not is_old and tag in ["replace", "insert"])
                if changed:
                    css = "diff-old" if is_old else "diff-new"
                    parts.append(f'<span class="{css}">{escaped}</span>')
                elif tag == "equal":
                    parts.append(escaped)
            return "".join(parts) or '<span class="empty">blank</span>'

        return render(old_tokens, True), render(new_tokens, False)

    def _align_properties(self, old_props: List[str], new_props: List[str]) -> List[Tuple[str, str]]:
        aligned = []
        old_used, new_used = set(), set()
        for i, old_prop in enumerate(old_props):
            for j, new_prop in enumerate(new_props):
                if j not in new_used and old_prop == new_prop:
                    aligned.append((old_prop, new_prop))
                    old_used.add(i)
                    new_used.add(j)
                    break
        for i, old_prop in enumerate(old_props):
            if i in old_used:
                continue
            old_key = self._stat_key(old_prop)
            for j, new_prop in enumerate(new_props):
                if j not in new_used and old_key and old_key == self._stat_key(new_prop):
                    aligned.append((old_prop, new_prop))
                    old_used.add(i)
                    new_used.add(j)
                    break
        for i, old_prop in enumerate(old_props):
            if i not in old_used:
                aligned.append((old_prop, "(removed)"))
        for j, new_prop in enumerate(new_props):
            if j not in new_used:
                aligned.append(("", new_prop))
        return aligned

    def export_item_diff(self, diff: ItemDiffDTO, output_dir: str, type_counts: Dict[str, Dict[str, int]] | None = None) -> None:
        os.makedirs(output_dir, exist_ok=True)
        self._ensure_assets(output_dir)
        type_counts = type_counts or {}

        def count_for(key: str, bucket: str) -> int:
            return int(type_counts.get(key, {}).get(bucket, 0))

        rows = []
        for key, label in [("uniques", "Uniques"), ("sets", "Sets"), ("runewords", "Runewords")]:
            rows.append(
                f"<tr><td>{label}</td><td>{count_for(key, 'added')}</td><td>{count_for(key, 'removed')}</td><td>{count_for(key, 'modified')}</td></tr>"
            )
        rows.append(
            f"<tr><th>Total</th><th>{len(diff['added'])}</th><th>{len(diff['removed'])}</th><th>{len(diff['modified'])}</th></tr>"
        )
        summary_body = f"""
<nav class="nav">
  <a href="ADDED.html">Added</a>
  <a href="REMOVED.html">Removed</a>
  <a href="MODIFIED.html">Modified</a>
</nav>
<table>
  <thead><tr><th>Category</th><th>Added</th><th>Removed</th><th>Modified</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
"""
        self._write_page(os.path.join(output_dir, "index.html"), "Item Database Comparison Summary", summary_body)

        def classify(item: Dict[str, Any]) -> str:
            raw_row = item.get("raw_row", {})
            if "runes" in item or "Rune1" in raw_row:
                return "runewords"
            if "set" in raw_row:
                return "sets"
            return "uniques"

        def title_for(item: Dict[str, Any]) -> str:
            return str(item.get("display_name") or item.get("name") or item.get("id") or "Unknown")

        def base_for(item: Dict[str, Any]) -> str:
            return str(item.get("base_item", "") or ", ".join(item.get("base_items", [])))

        def group_for(item: Dict[str, Any], family: str) -> str:
            if family == "runewords":
                bases = item.get("base_items", [])
                return str(bases[0] if bases else "Other")
            return str(item.get("item_type", "Other"))

        def write_toc(items_dict: Dict[str, Dict[str, Any]], base_name: str, is_modified: bool = False) -> None:
            family_groups: Dict[str, Dict[str, List[Dict[str, Any]]]] = {"uniques": {}, "sets": {}, "runewords": {}}
            for key, item in items_dict.items():
                item_copy = dict(item)
                item_copy["original_key"] = key
                family = classify(item_copy)
                group = group_for(item_copy, family)
                family_groups[family].setdefault(group, []).append(item_copy)

            toc_parts = ['<nav class="nav"><a href="index.html">Summary</a></nav>']
            family_labels = {"uniques": "Uniques", "runewords": "Runewords", "sets": "Sets"}
            for family in ["uniques", "runewords", "sets"]:
                groups = family_groups[family]
                if not groups:
                    continue
                toc_parts.append(f"<h2>{family_labels[family]}</h2><ul>")
                for group, grouped_items in sorted(groups.items()):
                    filename = self.report_filename(group)
                    rel = f"{base_name.lower()}/{family}/{filename}"
                    self._write_item_group_page(
                        grouped_items,
                        os.path.join(output_dir, base_name.lower(), family, filename),
                        f"{base_name} {family_labels[family][:-1] if family != 'runewords' else group} {group if family != 'runewords' else 'Runewords'}",
                        is_modified,
                    )
                    toc_parts.append(f'<li><a href="{self.escape(rel)}">{self.escape(group)}</a> ({len(grouped_items)})</li>')
                toc_parts.append("</ul>")
            if len(toc_parts) == 1:
                toc_parts.append('<p class="muted">No items in this bucket.</p>')
            self._write_page(os.path.join(output_dir, f"{base_name.upper()}.html"), f"{base_name} Items Breakdown", "\n".join(toc_parts))

        write_toc(diff["added"], "Added")
        removed_cards = ['<nav class="nav"><a href="index.html">Summary</a></nav>']
        if diff["removed"]:
            removed_cards.append("<ul>")
            for key, item in sorted(diff["removed"].items()):
                removed_cards.append(f"<li><strong>{self.escape(title_for(item))}</strong> <code>{self.escape(key)}</code></li>")
            removed_cards.append("</ul>")
        else:
            removed_cards.append('<p class="muted">No removed items.</p>')
        self._write_page(os.path.join(output_dir, "REMOVED.html"), "Removed Items", "\n".join(removed_cards))
        write_toc(diff["modified"], "Modified", is_modified=True)

    def _write_item_group_page(self, items: List[Dict[str, Any]], path: str, title: str, is_modified: bool) -> None:
        cards = ['<nav class="nav"><a href="../../index.html">Summary</a></nav>']
        for item in sorted(items, key=title_for_item):
            key = item.get("original_key", "")
            if is_modified:
                base_old, base_new = self._diff_pair(item.get("bt_base", ""), item.get("bk_base", ""))
                lvl_old, lvl_new = self._diff_pair(item.get("bt_lvl", ""), item.get("bk_lvl", ""))
                prop_rows = []
                for old_prop, new_prop in self._align_properties(item.get("bt_props", []), item.get("bk_props", [])):
                    old_html, new_html = self._diff_pair(old_prop, new_prop)
                    prop_rows.append(f"<tr><td>{old_html}</td><td>{new_html}</td></tr>")
                cards.append(f"""
<section class="card">
  <p class="item-title">{self.escape(item.get('name', 'Unknown'))} <code>{self.escape(key)}</code></p>
  <table>
    <thead><tr><th>Old</th><th>New</th></tr></thead>
    <tbody>
      <tr><td><strong>Base Item:</strong> {base_old}</td><td><strong>Base Item:</strong> {base_new}</td></tr>
      <tr><td><strong>Level Requirement:</strong> {lvl_old}</td><td><strong>Level Requirement:</strong> {lvl_new}</td></tr>
      <tr><th>Properties</th><th>Properties</th></tr>
      {''.join(prop_rows)}
    </tbody>
  </table>
</section>
""")
            else:
                props = "".join(f"<li>{self.escape(prop.get('resolved_text', ''))}</li>" for prop in item.get("properties", []))
                cards.append(f"""
<section class="card">
  <p class="item-title">{self.escape(item.get('display_name') or item.get('name') or 'Unknown')} <code>{self.escape(key)}</code></p>
  <p><strong>Base Item:</strong> {self.escape(item.get('base_item', '') or ', '.join(item.get('base_items', [])))}</p>
  <p><strong>Level Requirement:</strong> {self.escape(item.get('lvl_req', '0'))}</p>
  <ul class="properties">{props}</ul>
</section>
""")
        self._write_page(path, title, "\n".join(cards), css_href="../../assets/report.css")

    def export_excel_diff(self, diff: ExcelDiffDTO, output_path: str) -> None:
        self._ensure_assets(os.path.dirname(output_path))
        nav = '<nav class="nav"><a href="index.html">Summary</a></nav>'
        sections = [nav, f'<p class="muted">Key column used: <code>{self.escape(diff["key_used"])}</code></p>']
        if diff["added_cols"]:
            sections.append(f"<h2>Added Columns</h2><p>{self.escape(', '.join(diff['added_cols']))}</p>")
        if diff["removed_cols"]:
            sections.append(f"<h2>Removed Columns</h2><p>{self.escape(', '.join(diff['removed_cols']))}</p>")
        if diff["added_rows"]:
            rows = "".join(f"<li><code>{self.escape(row)}</code></li>" for row in diff["added_rows"])
            sections.append(f"<h2>Added Rows ({len(diff['added_rows'])})</h2><ul>{rows}</ul>")
        if diff["removed_rows"]:
            rows = "".join(f"<li><code>{self.escape(row)}</code></li>" for row in diff["removed_rows"])
            sections.append(f"<h2>Removed Rows ({len(diff['removed_rows'])})</h2><ul>{rows}</ul>")
        if diff["modified_rows"]:
            sections.append(f"<h2>Modified Rows ({len(diff['modified_rows'])})</h2>")
            for key, row_diff in sorted(diff["modified_rows"].items()):
                rows = []
                for col, values in row_diff.items():
                    old_html, new_html = self._diff_pair(values["bt_old"], values["bk_new"])
                    rows.append(f"<tr><td><code>{self.escape(col)}</code></td><td>{old_html}</td><td>{new_html}</td></tr>")
                sections.append(f"""
<section class="card">
  <h3>{self.escape(key)}</h3>
  <table>
    <thead><tr><th>Column</th><th>Old</th><th>New</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</section>
""")
        self._write_page(output_path, f"Differences for {diff['filename']}", "\n".join(sections))

    def export_excel_summary(self, summary_rows: List[Dict[str, Any]], output_path: str) -> None:
        self._ensure_assets(os.path.dirname(output_path))
        rows = []
        for row in summary_rows:
            html_report = str(row["report_name"])
            if html_report.endswith(".md"):
                html_report = html_report[:-3] + ".html"
            rows.append(
                f"<tr><td><a href=\"{self.escape(html_report)}\">{self.escape(row['filename'])}</a></td>"
                f"<td>{row['added_cols']}</td><td>{row['removed_cols']}</td>"
                f"<td>{row['added_rows']}</td><td>{row['removed_rows']}</td><td>{row['modified_rows']}</td></tr>"
            )
        totals = {
            "added_cols": sum(row["added_cols"] for row in summary_rows),
            "removed_cols": sum(row["removed_cols"] for row in summary_rows),
            "added_rows": sum(row["added_rows"] for row in summary_rows),
            "removed_rows": sum(row["removed_rows"] for row in summary_rows),
            "modified_rows": sum(row["modified_rows"] for row in summary_rows),
        }
        rows.append(
            f"<tr><th>Total</th><th>{totals['added_cols']}</th><th>{totals['removed_cols']}</th>"
            f"<th>{totals['added_rows']}</th><th>{totals['removed_rows']}</th><th>{totals['modified_rows']}</th></tr>"
        )
        body = f"""
<table>
  <thead><tr><th>File</th><th>Added Cols</th><th>Removed Cols</th><th>Added Rows</th><th>Removed Rows</th><th>Modified Rows</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
"""
        self._write_page(output_path, "Excel Diff Summary", body)


def title_for_item(item: Dict[str, Any]) -> str:
    return str(item.get("display_name") or item.get("name") or "")
