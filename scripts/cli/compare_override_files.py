import argparse
import difflib
import hashlib
import html
import json
import os
import re
from typing import Any, Dict, List, Tuple


TEXT_EXTENSIONS = {".json", ".txt"}
MAX_DIFF_LINES = 2000


def report_filename(value: str, ext: str = ".html") -> str:
    safe = value.lower().replace("\\", "/")
    safe = re.sub(r"[^a-z0-9_.-]+", "_", safe)
    safe = safe.replace("/", "__").strip("._")
    return f"{safe or 'file'}{ext}"


def iter_text_overrides(root: str) -> List[str]:
    rels = []
    for current_root, _, files in os.walk(root):
        for filename in files:
            if os.path.splitext(filename)[1].lower() not in TEXT_EXTENSIONS:
                continue
            full_path = os.path.join(current_root, filename)
            rels.append(os.path.relpath(full_path, root).replace("\\", "/"))
    return sorted(rels)


def retail_candidates(rel_path: str) -> List[str]:
    candidates = [rel_path]
    if rel_path.startswith("data/"):
        candidates.append(rel_path[5:])
    return candidates


def find_old_path(old_root: str, rel_path: str) -> Tuple[str, str]:
    for candidate in retail_candidates(rel_path):
        path = os.path.join(old_root, candidate.replace("/", os.sep))
        if os.path.exists(path):
            return path, candidate
    return "", retail_candidates(rel_path)[-1]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read().replace("\r\n", "\n").replace("\r", "\n")


def normalize_json_text(text: str) -> str:
    data = json.loads(text)
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def comparable_text(path: str) -> str:
    text = read_text(path)
    if path.lower().endswith(".json"):
        try:
            return normalize_json_text(text)
        except json.JSONDecodeError:
            return text
    return text


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #241f19; background: #f7f5f0; }}
    .page {{ width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 56px; }}
    a {{ color: #0a5b86; }}
    table {{ width: 100%; border-collapse: collapse; background: #fffdf8; border: 1px solid #d8cfc2; margin: 16px 0; }}
    th, td {{ border-bottom: 1px solid #d8cfc2; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f0ebe1; }}
    code {{ background: #f0ebe1; border-radius: 4px; padding: 1px 4px; }}
    .muted {{ color: #6c6258; }}
    .nav {{ display: flex; gap: 8px; margin: 16px 0; }}
    .nav a {{ border: 1px solid #d8cfc2; border-radius: 999px; padding: 5px 10px; background: #fffdf8; text-decoration: none; }}
    .diff {{ overflow-x: auto; background: #fffdf8; border: 1px solid #d8cfc2; padding: 12px; }}
    pre {{ margin: 0; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.86rem; line-height: 1.45; }}
  </style>
</head>
<body><main class="page">{body}</main></body>
</html>
"""


def build_diff_page(rel_path: str, old_rel: str, old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff_lines = list(difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"Retail: {old_rel}",
        tofile=f"BKDiablo: {rel_path}",
        lineterm="",
        n=3,
    ))
    truncated = len(diff_lines) > MAX_DIFF_LINES
    if truncated:
        diff_lines = diff_lines[:MAX_DIFF_LINES]
        diff_lines.append(f"... diff truncated after {MAX_DIFF_LINES} lines ...")
    diff_html = html.escape("\n".join(diff_lines))
    truncated_note = '<p class="muted">This large diff was truncated for browser performance.</p>' if truncated else ""
    body = f"""
<nav class="nav"><a href="../index.html">Summary</a></nav>
<h1>{html.escape(rel_path)}</h1>
<p class="muted">Compared against <code>{html.escape(old_rel)}</code>.</p>
{truncated_note}
<section class="diff"><pre>{diff_html}</pre></section>
"""
    return page(rel_path, body)


def compare_files(new_root: str, old_root: str, output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    diff_dir = os.path.join(output_dir, "files")
    os.makedirs(diff_dir, exist_ok=True)

    records: List[Dict[str, Any]] = []
    for rel_path in iter_text_overrides(new_root):
        new_path = os.path.join(new_root, rel_path.replace("/", os.sep))
        old_path, old_rel = find_old_path(old_root, rel_path)
        if not old_path:
            records.append({"path": rel_path, "status": "added", "old_path": old_rel, "diff_href": ""})
            continue

        old_text = comparable_text(old_path)
        new_text = comparable_text(new_path)
        if digest(old_text) == digest(new_text):
            records.append({"path": rel_path, "status": "unchanged", "old_path": old_rel, "diff_href": ""})
            continue

        filename = report_filename(rel_path)
        diff_href = f"files/{filename}"
        write_text(os.path.join(output_dir, diff_href), build_diff_page(rel_path, old_rel, old_text, new_text))
        records.append({"path": rel_path, "status": "modified", "old_path": old_rel, "diff_href": diff_href})

    return {
        "schema": "bt-bkdiff.override-file-diff.v1",
        "new_root": new_root,
        "old_root": old_root,
        "files": records,
    }


def write_summary(report: Dict[str, Any], output_dir: str) -> None:
    counts = {status: 0 for status in ["added", "modified", "unchanged"]}
    for record in report["files"]:
        counts[record["status"]] = counts.get(record["status"], 0) + 1

    rows = []
    for record in report["files"]:
        label = html.escape(record["path"])
        if record["diff_href"]:
            file_cell = f'<a href="{html.escape(record["diff_href"])}">{label}</a>'
        else:
            file_cell = f"<code>{label}</code>"
        rows.append(
            f"<tr><td>{file_cell}</td><td>{html.escape(record['status'])}</td><td><code>{html.escape(record['old_path'])}</code></td></tr>"
        )

    body = f"""
<h1>Override File Diff: BKDiablo vs Retail</h1>
<p class="muted">Compares BKDiablo text and JSON override files against the refreshed retail extract.</p>
<table>
  <thead><tr><th>Total</th><th>Added</th><th>Modified</th><th>Unchanged</th></tr></thead>
  <tbody><tr><td>{len(report['files'])}</td><td>{counts.get('added', 0)}</td><td>{counts.get('modified', 0)}</td><td>{counts.get('unchanged', 0)}</td></tr></tbody>
</table>
<table>
  <thead><tr><th>BK Override</th><th>Status</th><th>Retail Baseline</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
"""
    write_text(os.path.join(output_dir, "index.html"), page("Override File Diff: BKDiablo vs Retail", body))
    write_text(os.path.join(output_dir, "summary.json"), json.dumps(report, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare BKDiablo override text/JSON files against a retail extract.")
    parser.add_argument("--new-root", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the new/target mod root")
    parser.add_argument("--old-root", default="../data/retail", help="Path to the old/base retail root")
    parser.add_argument("--out", default="../output/file_diff_report_retail_bk", help="Output directory for generated file diff report")
    args = parser.parse_args()

    report = compare_files(os.path.abspath(args.new_root), os.path.abspath(args.old_root), os.path.abspath(args.out))
    write_summary(report, os.path.abspath(args.out))
    print(f"File override report generated in {args.out}")


if __name__ == "__main__":
    main()
