# Repo Health Roadmap

This document tracks the cleanup and architecture work discovered during the repo review. It is meant to be burned down iteratively in small pull requests, with each milestone leaving the generator and local wiki in a working state.

## Goals

- Keep source control focused on source data, code, tests, and docs.
- Treat generated reports, exports, and wiki pages as reproducible build artifacts.
- Keep display layers separate from data parsing and business logic.
- Make every user-facing report reachable from the local/GitHub Pages wiki when it is worth keeping.
- Remove stale scripts, stale docs, and renderer paths that no longer match the project direction.

## Working Rules

- Prefer one narrow branch per milestone.
- Keep `scripts/generate_reports.py` as the top-level rebuild command.
- Keep tests passing with `python -m unittest discover -s tests`.
- Run a full local smoke build with `python scripts/generate_reports.py` before merging generator changes.
- Do not delete a script until either its replacement path exists or the feature is intentionally retired.

## Milestone 1: Source-Control Hygiene And Docs

Purpose: make the repo match the build-artifact model before deeper refactors.

- [x] Add ignore rules for generated canonical outputs:
  - [x] `exports/item_db/`
  - [x] `exports/item_db_bt/`
  - [x] `exports/item_db_retail/`
  - [x] `output/item_diff_report_bt_bk/`
  - [x] `output/item_diff_report_retail_bk/`
  - [x] `output/excel_diff_report_bt_bk/`
  - [x] `output/excel_diff_report_retail_bk/`
  - [x] `output/skill_trees/`
- [x] Remove currently tracked generated files from git while preserving local generation behavior.
- [x] Keep test fixtures and intentional documentation sources tracked.
- [x] Fix README mojibake in the project tree.
- [x] Update README language so `exports/` and `output/` are described as generated local artifacts, not long-term tracked source.
- [x] Update README script layout now that top-level compatibility wrappers are gone.
- [x] Update the patch notes page copy so it points readers toward the generated Reports section.
- [x] Decide whether the large source PDF in `docs/` should stay, be renamed with context, or be replaced by the extracted markdown guide. Decision: keep it for traceability for now; the extracted Markdown guide remains the easier day-to-day reference.

Acceptance checks:

- [x] `git ls-files exports output` returns no generated report/export/wiki files.
- [x] `python -m unittest discover -s tests` passes.
- [x] `python scripts/generate_reports.py` recreates the local generated outputs.
- [x] README accurately describes the current workflow.

## Milestone 2: Markdown Report Decision

Purpose: stop carrying a broken renderer as an implied deliverable.

- [ ] Decide whether Markdown diff reports are still needed.
- [ ] If Markdown stays:
  - [ ] Replace LaTeX/color formatting in `MarkdownExporter.get_styled_diffs` with plain Markdown-safe text.
  - [ ] Add tests for mixed unchanged/changed token diffs such as `dmg-undead` -> `dmg-norm`.
  - [ ] Verify generated Markdown renders cleanly in GitHub.
- [ ] If Markdown goes:
  - [ ] Remove Markdown report outputs from the canonical generator.
  - [ ] Keep JSON DTOs and HTML reports as the supported outputs.
  - [ ] Update docs and tests to reflect the supported renderer set.

Acceptance checks:

- [ ] No generated Markdown report contains malformed `$`, `\text`, or tab-expanded `ext{...}` fragments.
- [ ] HTML report generation remains unchanged for readers.

## Milestone 3: Report Templates And Assets

Purpose: bring report rendering in line with the wiki template architecture.

- [ ] Move report CSS out of `HtmlReportExporter.REPORT_CSS` into a checked-in asset file.
- [ ] Move report HTML shell/layout into Jinja2 templates.
- [ ] Keep report-specific rendering helpers small and data-oriented.
- [ ] Share common visual language with the wiki where practical without forcing report tables into the wiki page templates.
- [ ] Keep report pages copyable into `output/wiki/reports/`.

Acceptance checks:

- [ ] Report CSS exists as a real source file.
- [ ] Report HTML is rendered through templates, not large Python string literals.
- [ ] Existing report exporter tests still pass.
- [ ] Browser smoke check confirms report pages still load with styled diffs.

## Milestone 4: Class Pages Off Markdown

Purpose: make class pages consume structured data instead of reparsing generated Markdown.

- [ ] Add a structured skill/class DTO export from the skill analyzer.
- [ ] Generate JSON skill/class output alongside or instead of `output/skill_trees/*.md`.
- [ ] Update `WikiGenerator` to load class data from DTO JSON.
- [ ] Remove `_parse_skill_tree_markdown` once no wiki path depends on it.
- [ ] Decide whether class Markdown exports should remain as optional human-readable artifacts.

Acceptance checks:

- [ ] Wiki class pages render from structured data.
- [ ] Tests cover representative class DTO loading and template rendering.
- [ ] The wiki no longer reparses Markdown as a data source.

## Milestone 5: Orphaned Displays And Scripts

Purpose: either promote useful tools into the main pipeline or retire them.

- [ ] Review `scripts/cli/d2_cube_analyzer.py`.
  - [ ] If useful, add cube recipe DTO/HTML/wiki pages.
  - [ ] If not useful, remove it and any unused cube-only exporter methods.
- [ ] Review `scripts/cli/compare_excel.py`.
  - [ ] If useful, document it as a debug tool.
  - [ ] If redundant with `compare_all_excel.py`, remove it.
- [ ] Review `scripts/devtools/` and add short file-level comments or docs for tools worth keeping.
- [ ] Remove local stale `__pycache__/` directories from the workspace.

Acceptance checks:

- [ ] Every kept script has a clear purpose.
- [ ] Every deliverable display path is either linked from the wiki or explicitly marked as a dev-only output.
- [ ] No obsolete generated files are tracked.

## Milestone 6: Publishing Hardening

Purpose: make Pages/local hosting less dependent on default folder assumptions.

- [ ] Add an explicit `--reports-root` option to `cli.generate_wiki`.
- [ ] Update `WikiGenerator._publish_reports` to use the explicit reports root.
- [ ] Add tests for non-default wiki output paths that still publish reports correctly.
- [ ] Revisit whether copied report JSON DTOs should be public on GitHub Pages or kept local-only.
- [ ] Confirm GitHub Pages workflow triggers cover the files that should rebuild the site.

Acceptance checks:

- [ ] A temp-dir wiki build can publish reports from an explicit reports root.
- [ ] GitHub Pages workflow remains simple: install, test, generate, upload `output/wiki`.
- [ ] Public report artifacts are intentional and documented.

## Open Questions

- Should Markdown reports be supported long term, or should HTML plus JSON become the only canonical report outputs?
- Should the extracted Diablo II data guide replace the source PDF in `docs/`, or should both remain for traceability?
- Should cube recipes become a first-class wiki section?
- Should report DTO JSON files be published publicly, or are they only intermediate/local artifacts?
- How much historical compatibility do we want for direct CLI defaults outside `scripts/generate_reports.py`?
