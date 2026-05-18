# BT-BKDiff: Diablo II Data Diff and Wiki Generator

This project compares Diablo II mod data across BKDiablo, BTDiablo, and retail data, then generates human-readable reports plus a local static wiki.

## Project Structure

```text
/
├── data/           # Retail/base data snapshots and shared config
├── docs/           # Modding references and wiki generation notes
├── exports/        # Structured item database exports used by comparisons/wiki
├── mods/           # BKDiablo and BTDiablo mod data
├── output/         # Generated comparison reports and local wiki output
├── scripts/        # CLI wrappers plus shared Python implementation
└── tests/          # Unit tests and fixtures
```

## Main Workflow

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the test suite:

```bash
python -m unittest discover -s tests
```

Rebuild all canonical generated outputs:

```bash
python scripts/generate_reports.py
```

That command exports item databases, compares BKDiablo against BTDiablo and retail, regenerates class skill trees, and writes the local wiki to `output/wiki/`.

## Canonical Outputs

- `exports/item_db/`: BKDiablo structured item export
- `exports/item_db_bt/`: BTDiablo structured item export
- `exports/item_db_retail/`: retail structured item export
- `output/item_diff_report_bt_bk/`: BKDiablo vs BTDiablo item comparison
- `output/item_diff_report_retail_bk/`: BKDiablo vs retail item comparison
- `output/excel_diff_report_bt_bk/`: BKDiablo vs BTDiablo raw Excel comparison
- `output/excel_diff_report_retail_bk/`: BKDiablo vs retail raw Excel comparison
- `output/skill_trees/`: generated class skill tree markdown
- `output/wiki/`: generated static wiki site, ignored as a local/publish artifact

Diff report directories contain structured JSON DTOs plus renderer outputs: Markdown for text review and browser-friendly HTML entry points at `index.html`. Legacy direct-command defaults such as `output/item_diff_report/` and `output/excel_diff_report/` are ignored. Prefer `scripts/generate_reports.py` for repeatable project output.

## Wiki

The wiki is a static site generated from the structured exports and skill tree markdown. Item detail pages are pre-rendered HTML, while the item index uses `output/wiki/data/items-index.json` for browser-side search and filtering.

For local viewing, serve `output/wiki/` with a simple static server after running the generator.

## Script Layout

`scripts/generate_reports.py` is the top-level rebuild command. The implementation is organized under:

- `scripts/d2lib/`: shared repository, service, exporter, and wiki generator code
- `scripts/cli/`: primary CLI implementations
- `scripts/devtools/`: development inspection utilities
