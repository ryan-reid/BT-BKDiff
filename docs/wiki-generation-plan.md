# Wiki Generation Plan

This document defines the first-pass wiki generation strategy for the project.

## Goals

- Recreate the parts of the BTD wiki that are driven directly by Diablo II data files.
- Keep generated wiki output deterministic and reproducible from repo data.
- Route all deliverable generation through `scripts/generate_reports.py`.

## Source-of-Truth Mapping

### Items

- `uniqueitems.txt`: unique item definitions
- `setitems.txt`: set item definitions
- `sets.txt`: set metadata
- `runes.txt`: runeword definitions
- `armor.txt`, `weapons.txt`, `misc.txt`: base item metadata
- `itemtypes.txt`: item type grouping
- `properties.txt`, `itemstatcost.txt`: property text resolution

### Skills And Classes

- `skills.txt`: core skill mechanics
- `skillcalc.txt`: alias formulas used by skill calculations
- `skilldesc.txt`: displayed tooltip rows and labels
- `missiles.txt`: missile-backed durations, ranges, and damage displays
- `monstats.txt`: summon-backed stat displays
- `charstats.txt`: class metadata

### Patch And System Pages

- Excel diff DTOs and rendered outputs from `scripts/cli/compare_all_excel.py`
- Item diff DTOs and rendered outputs from `scripts/cli/compare_item_db.py`

## First Milestone

The first milestone focuses on the page families that are already well-supported by the current data pipeline:

- `Main Page`
- `All Items`
- `Classes`
- `Items/Unique/*`
- `Items/Set/*`
- `Items/Runeword/*`
- `Classes/*`
- `Patch Notes/Full Patch Notes Draft`

## Output Layout

Generated wiki site content should live under `output/wiki/`.

- `output/wiki/index.html`
- `output/wiki/items/index.html`
- `output/wiki/items/.../index.html`
- `output/wiki/classes/index.html`
- `output/wiki/classes/.../index.html`
- `output/wiki/patch-notes/.../index.html`
- `output/wiki/data/items-index.json`
- `output/wiki/assets/site.css`
- `output/wiki/assets/site.js`
- `output/wiki/manifest.json`

## Generator Rules

- Prefer structured JSON exports over reparsing Markdown where possible.
- Prefer existing analyzer and skill export outputs over duplicating business logic.
- Use a static HTML/CSS/JS site as the primary generated presentation layer.
- Keep item detail pages pre-rendered while using compact JSON indexes for browser-side search and filtering where useful.
- Keep a manifest so future MediaWiki export or publishing automation can target the same page graph.
- Keep page titles stable so we can diff wiki output between runs.
- Record generated page metadata in `manifest.json` for future publishing automation.

## Future Milestones

### Skill Pages

- Generate one page per skill from the skill tree DTOs rather than the current class-level tables.
- Include effect tables, synergy sections, and calculation notes where available.

### Patch Notes

- Convert diff reports into draft patch note pages grouped by items, skills, systems, and tables.
- Keep generated notes factual and data-driven; narrative summaries can remain human-edited.

### MediaWiki Export

- Add a second exporter that serializes the same page manifest into MediaWiki-ready text.
- Preserve the same page hierarchy so Git-based review remains straightforward.

### Public Hosting

- Publish `output/wiki/` through GitHub Pages from a dedicated GitHub Actions workflow.
- Keep generated site files as build artifacts rather than tracked repository content.
