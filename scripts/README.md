# Scripts Layout

This folder keeps `generate_reports.py` as the top-level rebuild command, with implementation code grouped by role:

- `d2lib/`: shared repository, model, service, and exporter code
- `cli/`: primary user-facing entrypoints
- `devtools/`: developer utilities for inspection and validation

Run focused tools with module commands from this directory, such as `python -m cli.compare_item_db` or `python -m cli.generate_wiki`.

Deliverable generators should be wired into `scripts/generate_reports.py` so a single entrypoint can rebuild the canonical outputs, including the generated wiki site under `output/wiki/`.
