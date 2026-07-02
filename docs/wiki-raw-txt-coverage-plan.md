# Wiki Raw TXT Coverage Expansion Plan

This branch is an experimental expansion of the generated wiki from broad page families into deeper player-facing coverage of the raw `data/global/excel/*.txt` systems. The work should remain easy to evaluate and discard: each phase adds one coherent wiki surface, tests it, rebuilds the generated wiki, and verifies the rendered output before moving on.

## Ground Rules

- Keep generated `output/` out of commits unless explicitly requested.
- Do not modify `mods/BKDiablo` submodule contents as part of this branch.
- Prefer extending the existing generator, DTO-style page payloads, templates, and search/filter helpers.
- Each new page needs source-file attribution in the manifest and a focused test in `tests/test_wiki_generator.py`.
- Each phase should end with:
  - `python -m unittest tests.test_wiki_generator`
  - `python -m unittest discover -s tests`
  - `python scripts/generate_reports.py`
  - served-page smoke checks on `http://127.0.0.1:8765/`

## Phase 1: Real Drop Sources

Goal: let players move beyond conditional unique/set base weighting and inspect the actual treasure-class graph that controls where drops can come from.

Raw tables:
- `treasureclassex.txt`
- `monstats.txt`
- `superuniques.txt`
- `levels.txt`
- `objects.txt` later for chest/object sources
- `uniqueitems.txt`, `setitems.txt`, `weapons.txt`, `armor.txt`, `misc.txt` for item-code labeling

Implementation steps:
1. Add a `DropSourceAnalyzerService` or wiki builder that parses `treasureclassex.txt`.
2. Resolve each TC row into:
   - treasure class name, group, level, picks, no-drop, quality weights
   - child treasure classes
   - direct item-code drops with display labels
   - parent treasure classes that reference it
   - monster and superunique source references where derivable
3. Add `data/drop-sources.json`.
4. Add `drops/sources/index.html` with search and filters for TC/item/source names.
5. Link the new page from `drops/index.html` and home/drop portal copy.
6. Tests:
   - fixture TC graph with direct item and nested TC rows
   - generated JSON schema
   - rendered page link and search payload

Acceptance:
- A player can search an item code/name or treasure class and see direct TC relationships.
- The existing conditional unique/set weighting page still works.

## Phase 2: Affixes and Automagic

Goal: explain what magic, rare, crafted, and inherent modifiers can roll and where.

Raw tables:
- `magicprefix.txt`
- `magicsuffix.txt`
- `automagic.txt`
- `qualityitems.txt`
- `properties.txt`
- `itemstatcost.txt`
- `itemtypes.txt`

Implementation steps:
1. Add an affix analyzer that normalizes prefix/suffix/automagic rows into one DTO.
2. Resolve property columns through `PropertyResolverService`.
3. Resolve item-type applicability using `itemtypes.txt`.
4. Add `affixes/index.html` or `items/affixes/index.html` with filters:
   - Prefix/Suffix/Automagic/Quality
   - required level
   - item group/type
   - property text/stat
5. Link from Items, Bases, and Mechanics.

Acceptance:
- A player can answer "what can roll on this item type?" and "which affixes grant this stat?"

## Phase 3: Monster Special Coverage

Goal: upgrade the Bestiary from basic monster stats to monster identity, special modifiers, superuniques, and level scaling.

Raw tables:
- `monstats.txt`
- `monstats2.txt`
- `monlvl.txt`
- `superuniques.txt`
- `monprop.txt`
- `monumod.txt`
- `monai.txt` as supporting detail only

Implementation steps:
1. Extend `MonsterAnalyzerService` with monstats2 visuals/flags and monlvl scaling.
2. Add a superunique analyzer and `bestiary/superuniques/`.
3. Join superuniques to area names where possible.
4. Resolve `MonProp` and `monumod` into readable tags.
5. Add Bestiary filters for boss/superunique/immunity/area.

Acceptance:
- A player can find BK bosses/superuniques, their area, immunities, and special traits.

## Phase 4: Mercs, Vendors, Gambling, and Inventory QOL

Goal: cover systems that change how players equip, buy, gamble, hire, and store items.

Raw tables:
- `hireling.txt`
- `npc.txt`
- `gamble.txt`
- `inventory.txt`
- UI layout JSON as supporting source where useful

Implementation steps:
1. Add `systems/mercenaries/` from `hireling.txt`.
2. Add `systems/vendors/` from `npc.txt` and `gamble.txt`.
3. Add `systems/inventory/` from `inventory.txt` plus relevant layout summaries.
4. Link these from Mechanics and Home.

Acceptance:
- A player can see merc progression/equipment signals, gamble availability changes, and inventory/stash/cube QOL changes.

## Phase 5: States and Shrines

Goal: expose temporary buffs/debuffs and shrine effects instead of leaving them buried in raw tables.

Raw tables:
- `states.txt`
- `shrines.txt`
- `overlay.txt`
- `skills.txt`, `skilldesc.txt` as cross-links

Implementation steps:
1. Add a state analyzer with flags, groups, overlays, and known skill/property references.
2. Add shrine analyzer with effect references and changed fields.
3. Add `mechanics/states/` and `mechanics/shrines/`.
4. Cross-link skills and item properties where exact references are available.

Acceptance:
- A player can look up a visible buff/debuff/shrine and understand the gameplay effect or at least its source table meaning.

## Phase 6: Area Routes, Presets, Objects, and Rifts

Goal: enrich Areas with exits, level connections, presets, special objects, and better rift descriptions.

Raw tables:
- `levels.txt`
- `lvlmaze.txt`
- `lvlprest.txt`
- `lvlwarp.txt`
- `monpreset.txt`
- `objects.txt`

Implementation steps:
1. Extend `AreaFarmingDataBuilder` with warp/exits from `lvlwarp.txt`.
2. Surface object and preset hits beyond super chests.
3. Add area detail drilldowns or expandable details for routes/presets/objects.
4. Add rift-specific grouping if BK data identifies rifts reliably.

Acceptance:
- A player can inspect how an area is connected and what important objects/presets are present.

## Phase 7: Skill Support Tables

Goal: make class pages less isolated from the support systems that make skills work.

Raw tables:
- `skills.txt`
- `skilldesc.txt`
- `missiles.txt`
- `states.txt`
- `monseq.txt` only if it can be summarized usefully

Implementation steps:
1. Add skill support sections for missile, state, and summon references.
2. Add `classes/skills-index/` or an all-skills search page.
3. Add warnings for unresolved formulas/data rather than hiding them.

Acceptance:
- A player can search across all skills and understand major missile/state dependencies.

## Phase 8: Raw Coverage Dashboard

Goal: make future gaps visible.

Implementation steps:
1. Generate a `data/raw-txt-coverage.json` summary:
   - BK row count
   - retail row count
   - analyzer/page coverage status
   - source pages that cite each file
2. Add `reports/raw-coverage/` or a Mechanics subpage.
3. Use it as a maintenance checklist after each new page family.

Acceptance:
- New or uncovered `.txt` tables are visible without manually auditing source code.
