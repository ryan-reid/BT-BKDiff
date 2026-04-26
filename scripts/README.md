# Scripts Layout

This folder keeps the existing top-level script names for compatibility, but the implementation is now grouped by role:

- `d2lib/`: shared repository, model, service, and exporter code
- `cli/`: primary user-facing entrypoints
- `devtools/`: developer utilities for inspection and validation
- `legacy/`: older skill extraction prototypes and reference tooling
- `debug/`: one-off debugging helpers

Top-level wrappers are intentionally thin so existing commands like `python scripts/extract_class_skills.py` and imports like `from d2_services import ...` continue to work.
