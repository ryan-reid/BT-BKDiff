import argparse
import difflib
import hashlib
import html
import json
import os
import re
from typing import Any, Dict, List, Tuple


TEXT_EXTENSIONS = {".json"}
MAX_DIFF_LINES = 2000
LARGE_JSON_DIFF_BYTES = 5_000_000
STRUCTURED_OMIT_FIELDS = {"thumbnailBase64", "thumbnailMip"}


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
    .removed {{ background: #ffebe9; color: #82071e; }}
    .added {{ background: #dafbe1; color: #116329; }}
    .hunk {{ background: #ddf4ff; color: #0550ae; }}
    .diff-table {{ width: max-content; min-width: 100%; margin: 0; }}
    .diff-table td {{ padding: 2px 8px; border-bottom: 0; }}
    .number {{ color: #6c6258; text-align: right; user-select: none; }}
    .diff-table pre {{ white-space: pre; }}
    .nav {{ flex-wrap: wrap; }}
    pre {{ margin: 0; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.86rem; line-height: 1.45; }}
  </style>
</head>
<body><main class="page">{body}</main></body>
</html>
"""


def build_diff_page(rel_path: str, old_rel: str, old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    rows = []
    truncated = False
    for group in difflib.SequenceMatcher(None, old_lines, new_lines).get_grouped_opcodes(3):
        rows.append('<tr class="hunk"><td colspan="4">Changed section</td></tr>')
        for tag, i1, i2, j1, j2 in group:
            entries = []
            if tag == "equal":
                entries = [("context", i + 1, j + 1, " ", old_lines[i]) for i, j in zip(range(i1, i2), range(j1, j2))]
            else:
                if tag in {"replace", "delete"}:
                    entries.extend(("removed", i + 1, "", "-", old_lines[i]) for i in range(i1, i2))
                if tag in {"replace", "insert"}:
                    entries.extend(("added", "", j + 1, "+", new_lines[j]) for j in range(j1, j2))
            for kind, old_no, new_no, sign, line in entries:
                if len(rows) >= MAX_DIFF_LINES:
                    truncated = True
                    break
                rows.append(f'<tr class="{kind}"><td class="number">{old_no}</td><td class="number">{new_no}</td><td>{sign}</td><td><pre>{html.escape(line)}</pre></td></tr>')
            if truncated:
                break
        if truncated:
            break
    note = '<p>Large diff: showing the first 2,000 display rows.</p>' if truncated else ""
    missing = '<p>No matching Retail baseline; all lines are BK additions.</p>' if not old_text else ""
    body = f"""
<nav class="nav"><a href="../index.html">JSON report summary</a></nav>
<h1>{html.escape(rel_path)}</h1>
<p><strong>Retail (Old / Base) &rarr; BKDiablo (New)</strong></p>
<p><span class="removed">- Removed from Retail</span> &nbsp; <span class="added">+ Added in BK</span>. Unchanged context appears around each change.</p>
<p class="muted">JSON keys are sorted and formatting normalized before comparison. Line numbers refer to this normalized JSON.</p>
{missing}{note}
<section class="diff"><table class="diff-table"><thead><tr><th>Retail line</th><th>BK line</th><th></th><th>JSON</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
"""
    return page(rel_path, body)


def collect_structured_changes(old: Any, new: Any, path: str = "", changes: List[Tuple[str, str, Any, Any]] | None = None) -> List[Tuple[str, str, Any, Any]]:
    changes = [] if changes is None else changes
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old) | set(new)):
            if key in STRUCTURED_OMIT_FIELDS:
                continue
            current_path = f"{path}.{key}" if path else key
            if key not in old:
                changes.append((current_path, "added", "", new[key]))
            elif key not in new:
                changes.append((current_path, "removed", old[key], ""))
            else:
                collect_structured_changes(old[key], new[key], current_path, changes)
    elif isinstance(old, list) and isinstance(new, list):
        for index, (old_value, new_value) in enumerate(zip(old, new)):
            collect_structured_changes(old_value, new_value, f"{path}[{index}]", changes)
        if len(old) != len(new):
            changes.append((path, "length", len(old), len(new)))
    elif old != new:
        changes.append((path, "changed", old, new))
    return changes


def build_structured_diff_page(rel_path: str, old_text: str, new_text: str) -> str:
    old_data = json.loads(old_text)
    new_data = json.loads(new_text)
    changes = collect_structured_changes(old_data, new_data)
    rows = []
    for path, kind, old_value, new_value in changes[:MAX_DIFF_LINES]:
        rows.append(
            f'<tr><td><code>{html.escape(path)}</code></td>'
            f'<td>{html.escape(kind)}</td>'
            f'<td><pre>{html.escape(str(old_value))}</pre></td>'
            f'<td><pre>{html.escape(str(new_value))}</pre></td></tr>'
        )
    note = '<p>Large diff: showing the first 2,000 field changes.</p>' if len(changes) > MAX_DIFF_LINES else ""
    body = f"""
<nav class="nav"><a href="../index.html">JSON report summary</a></nav>
<h1>{html.escape(rel_path)}</h1>
<p><strong>Retail (Old / Base) &rarr; BKDiablo (New)</strong></p>
<p>This oversized JSON file uses a structured field diff. Binary thumbnail payload fields are omitted.</p>
<p class="muted">{len(changes)} meaningful field changes. {note}</p>
<table><thead><tr><th>Path</th><th>Change</th><th>Retail</th><th>BKDiablo</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
"""
    return page(rel_path, body)


def compare_files(new_root: str, old_root: str, output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    diff_dir = os.path.join(output_dir, "files")
    os.makedirs(diff_dir, exist_ok=True)
    # Remove obsolete table reports from the former text/JSON report scope.
    for filename in os.listdir(diff_dir):
        if filename.endswith(".txt.html"):
            os.remove(os.path.join(diff_dir, filename))

    records: List[Dict[str, Any]] = []
    for rel_path in iter_text_overrides(new_root):
        new_path = os.path.join(new_root, rel_path.replace("/", os.sep))
        old_path, old_rel = find_old_path(old_root, rel_path)
        old_text = comparable_text(old_path) if old_path else ""
        new_text = comparable_text(new_path)
        if digest(old_text) == digest(new_text):
            records.append({"path": rel_path, "status": "unchanged", "old_path": old_rel, "diff_href": ""})
            continue

        filename = report_filename(rel_path)
        diff_href = f"files/{filename}"
        if old_path and new_path.lower().endswith(".json") and os.path.getsize(new_path) >= LARGE_JSON_DIFF_BYTES:
            diff_page = build_structured_diff_page(rel_path, old_text, new_text)
        else:
            diff_page = build_diff_page(rel_path, old_rel, old_text, new_text)
        write_text(os.path.join(output_dir, diff_href), diff_page)
        records.append({"path": rel_path, "status": "modified" if old_path else "added", "old_path": old_rel, "diff_href": diff_href})

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
    for record in sorted(report["files"], key=lambda r: ({"modified": 0, "added": 1, "unchanged": 2}[r["status"]], r["path"])):
        label = html.escape(record["path"])
        if record["diff_href"]:
            file_cell = f'<a href="{html.escape(record["diff_href"])}">{label}</a>'
        else:
            file_cell = f"<code>{label}</code>"
        baseline = "No matching Retail file" if record["status"] == "added" else record["old_path"]
        rows.append(
            f"<tr><td>{file_cell}</td><td>{html.escape(record['status'])}</td><td><code>{html.escape(baseline)}</code></td></tr>"
        )

    body = f"""
<h1>JSON Override Diff: BKDiablo vs Retail</h1>
<p class="muted">JSON overrides only. Retail is Old / Base; BKDiablo is New. Modified files appear first, then BK-only files, then unchanged files. Raw .txt tables are covered by the Excel reports.</p>
<table>
  <thead><tr><th>Total</th><th>Added</th><th>Modified</th><th>Unchanged</th></tr></thead>
  <tbody><tr><td>{len(report['files'])}</td><td>{counts.get('added', 0)}</td><td>{counts.get('modified', 0)}</td><td>{counts.get('unchanged', 0)}</td></tr></tbody>
</table>
<table>
  <thead><tr><th>BK Override</th><th>Status</th><th>Retail Baseline</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
"""
    write_text(os.path.join(output_dir, "index.html"), page("JSON Override Diff: BKDiablo vs Retail", body))
    write_text(os.path.join(output_dir, "summary.json"), json.dumps(report, indent=2) + "\n")


def run(new_root: str, old_root: str, out_dir: str):
    report = compare_files(os.path.abspath(new_root), os.path.abspath(old_root), os.path.abspath(out_dir))
    write_summary(report, os.path.abspath(out_dir))
    print(f"File override report generated in {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare BKDiablo JSON override files against a retail extract.")
    parser.add_argument("--new-root", default="../mods/BKDiablo/bkdiablo.mpq", help="Path to the new/target mod root")
    parser.add_argument("--old-root", default="../data/retail", help="Path to the old/base retail root")
    parser.add_argument("--out", default="../output/file_diff_report_retail_bk", help="Output directory for generated file diff report")
    args = parser.parse_args()

    run(args.new_root, args.old_root, args.out)


if __name__ == "__main__":
    main()
