# Amazon Skill Snapshot

This fixture freezes the subset of Diablo II data needed by the Amazon skill tree regression test.

- Source of truth for expected values remains [amazon_test_cases.json](E:\Games\GeminiDiff\BT-BKDiff\tests\amazon_test_cases.json)
- Fixture contents are generated from the current BKDiablo data by `scripts/devtools/build_amazon_skill_snapshot.py`
- The regression test uses this snapshot so balance/data changes in live mod files do not invalidate parser and calculation coverage

If the calculation logic changes intentionally and the fixture really must be refreshed, rebuild it from the current mod data and review the generated `manifest.json` before committing.
