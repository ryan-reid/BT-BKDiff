# Game data and UI labels

- Derive gameplay values and user-facing game names from the source data and its English (enUS) localization files. Follow the file relationships that the game uses.
- Do not introduce hardcoded affix names, class or skill-tab names, item-type labels, roll ranges, socket counts, or parallel rename tables.
- A UI-only naming override is permitted solely for a verified mismatch between an internal name and the intended display name. First investigate the source records and localization keys for a canonical mapping. Document the mismatch and why the override is still needed.
- Keep source identifiers for grouping and matching. Use localized labels to distinguish similarly named effects in the UI. Preserve identifiable fallbacks when a translation is missing.
- Read modifier values from their min, max, and parameter fields according to the property definition. Preserve the property's add or replace behavior.
- Cover changes to data resolution with regression tests that include new records, missing localization, and similarly named properties.
