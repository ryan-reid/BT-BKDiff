# BK Retail Diff Map V1

This document maps the BKDiablo mod data back to retail Diablo II: Resurrected data at a high level. It is intended for player-facing wiki and report planning, not as an exhaustive row-by-row patch note.

Baseline comparison:

- BK source: `mods/BKDiablo/bkdiablo.mpq`
- Retail source: `data/retail`
- Data guide baseline: `docs/Diablo_II_Data_File_Guide/index.md`
- Existing raw reports: `output/excel_diff_report_retail_bk` and `output/file_diff_report_retail_bk`

## Inventory

BK's gameplay data mostly lives in `data/global/excel/*.txt`. BK has the same retail Excel table filenames, but 42 of the 45 Excel files under `data/global/excel` differ from retail. The differences range from simple value edits to broad generated systems.

BK file buckets under `mods/BKDiablo/bkdiablo.mpq/data`:

| Bucket | Count | Retail relationship | Player-facing role |
| --- | ---: | --- | --- |
| `global/excel` | 45 | 42 changed, 3 unchanged | Core gameplay rules: items, areas, monsters, recipes, skills, drops |
| `local/lng` | 9 | 9 changed | Names and descriptions shown to players |
| `global/ui` | 10 | 10 changed | Inventory, stash, cube, skill, and panel layout support |
| `global/tiles` | 15 | 15 BK-only | Map and area layout support |
| `hd/items` | 175 | 24 changed, 150 BK-only, 1 unchanged | Item models, sprites, icons, and presentation |
| `hd/character` | 18 | 11 changed, 7 BK-only | Player/monster animation and state presentation |
| `hd/missiles` | 5 | 5 changed | Missile visuals that support skill changes |
| `hd/vfx` | 35 | 35 BK-only | Custom VFX, including rune beams and overlays |
| Other HD/global files | 143 | Mostly changed or BK-only | Video, texture cache, room tiles, overlays |

The most useful player-facing data should come from Excel tables and localized strings. Asset/UI files should usually be summarized as support for visible features unless they directly explain gameplay.

## High-Level Gameplay Categories

| Category | Player-facing story | Primary BK data | Retail comparison |
| --- | --- | --- | --- |
| Weapons and armor bases | Base items have broad stat, socket, visibility, speed, and inherent-property changes, even when row counts match retail. | `weapons.txt`, `armor.txt`, `itemtypes.txt` | `output/excel_diff_report_retail_bk/weapons.html`, `armor.html`, `itemtypes.html` |
| Misc/base items and stackables | BK adds new misc items and stackable/crafting objects, with new base-family style columns on `misc.txt`. | `misc.txt`, `gems.txt`, `itemtypes.txt`, item strings/assets | `misc.html`, `gems.html`, `itemtypes.html` |
| Unique, set, and runeword itemization | BK expands unique and set item rows and modifies many existing item stats. Runeword data is changed even when additions are small. | `uniqueitems.txt`, `setitems.txt`, `sets.txt`, `runes.txt` | `uniqueitems.html`, `setitems.html`, `sets.html`, `runes.html` |
| Affixes and item stats | BK changes the building blocks used by items: affix availability, automagic groups, stat definitions, properties, and quality bonuses. | `magicprefix.txt`, `magicsuffix.txt`, `automagic.txt`, `qualityitems.txt`, `properties.txt`, `itemstatcost.txt` | Matching Excel reports in `output/excel_diff_report_retail_bk` |
| Cube recipes, crafting, corruption, and stacking | The cube table is one of the largest BK systems and likely drives crafting, upgrading, stacking, repair, corruption, and QOL recipes. | `cubemain.txt`, plus `misc.txt`, `properties.txt`, `itemstatcost.txt`, strings | `cubemain.html` |
| Areas, rifts, terror/endgame zones | BK adds and modifies area rows, level names, presets, warps, maze records, density, and map tile support. | `levels.txt`, `lvlmaze.txt`, `lvlprest.txt`, `lvlwarp.txt`, `monpreset.txt`, `hd/global/excel/desecratedzones.json`, `global/tiles/*` | `levels.html`, `lvlmaze.html`, `lvlprest.html`, `lvlwarp.html`, `monpreset.html`, file diff reports |
| Monster levels, density, bosses, and drops | BK changes monster stats broadly, adds monsters, changes superunique and monster property data, and rewires treasure classes. | `monstats.txt`, `monstats2.txt`, `monlvl.txt`, `superuniques.txt`, `monprop.txt`, `monumod.txt`, `treasureclassex.txt`, monster strings/assets | Matching Excel and file reports |
| Skills, classes, and mechanics | BK adds/changes skills and skill descriptions, adjusts missiles and states, changes class starts/progression, and changes difficulty/experience mechanics. | `skills.txt`, `skilldesc.txt`, `missiles.txt`, `states.txt`, `charstats.txt`, `experience.txt`, `difficultylevels.txt` | Matching Excel reports |
| Mercs, vendors, gambling, UI/QOL | BK modifies gamble availability, inventory/panel layouts, vendor caps, merc gear support, and stash/cube/player inventory presentation. | `hireling.txt`, `npc.txt`, `gamble.txt`, `inventory.txt`, `global/ui/layouts/*.json` | Matching Excel and file reports |

## Observed Diff Signals

These are coarse signals from BK vs retail data shape, useful for prioritizing deeper review:

| File | Retail rows | BK rows | Signal |
| --- | ---: | ---: | --- |
| `cubemain.txt` | 227 | 1540 | Major recipe/crafting/corruption/stacking expansion |
| `itemtypes.txt` | 110 | 25667 | Generated item type system; likely supports skill/CTC itemization |
| `misc.txt` | 170 | 204 | New stackables, keys, crafting materials, and misc items |
| `levels.txt` | 139 | 148 | Added/changed areas and endgame/rift routing |
| `monstats.txt` | 752 | 797 | Added monsters and broad monster stat changes |
| `treasureclassex.txt` | 1345 | 1326 | Drop tables are substantially rearranged |
| `uniqueitems.txt` | 439 | 508 | Many added uniques and many modified existing uniques |
| `setitems.txt` | 141 | 216 | Expanded set itemization |
| `sets.txt` | 36 | 55 | Added set groups and set bonus changes |
| `automagic.txt` | 44 | 74 | Expanded automagic/inherent item modifier support |
| `gems.txt` | 69 | 76 | Added gem-like socketables and changed socket effects |
| `skills.txt` | 429 | 433 | New and modified skills, with supporting string/description changes |
| `experience.txt` | 101 | 127 | Extended level progression beyond retail |

Many files with unchanged row counts still have broad value changes. For example, `weapons.txt` and `armor.txt` keep retail row counts, but nearly every row is modified.

## BK-Only Guide Gaps

The local Diablo II Data File Guide is the baseline for retail table meanings, but BK adds patterns the guide does not fully explain.

Known gaps to handle explicitly:

- `itemtypes.txt` adds BK-only columns `*skillID` and `*CTC`.
- `itemtypes.txt` grows from 110 retail rows to 25,667 BK rows. Many rows appear generated, with codes such as `M636` and CTC-style descriptors like `id 400 lev56`.
- `misc.txt` adds `normcode`, `ubercode`, `ultracode`, and `auto prefix`, making misc items behave more like base item families and automagic-capable items.
- `misc.txt` does not currently have a modular guide page under `docs/Diablo_II_Data_File_Guide`, so its use should be documented locally as BK behavior is understood.
- `UICatOverride` is used by the current analyzer as a practical grouping signal for BK misc items, but it is not part of the guide-derived baseline.
- HD assets, UI layout JSON, tile files, and VFX files connect to gameplay by file path, item code, monster code, string key, or visual reference rather than by the Excel relationships described in the guide.

For player-facing output, generated rows and BK-only technical columns should be summarized by the feature they enable instead of listed verbatim.

## Data Suitable For User-Facing Presentation

High-value wiki/report surfaces:

- Cube recipes grouped by recipe purpose: crafting, corruption, stacking, repair, upgrades, keys, and endgame materials.
- Items grouped as uniques, sets, runewords, bases, gems/socketables, misc/stackables, and crafting materials.
- Area and rift pages showing area level, difficulty behavior, density, exits, monsters, and notable drops when derivable.
- Bestiary pages showing BK-added monsters, boss/unique changes, level/HP/resistance changes, spawn areas, and drop-table links.
- Skill/class pages showing added skills, changed effects, tooltip changes, missiles, and class progression.
- Mechanics pages for difficulty penalties, experience/level cap, monster level scaling, loot systems, gambling, vendors, and inventory/cube/stash QOL.

Supporting but usually not standalone:

- String diffs that provide names/descriptions for new or renamed things.
- Item/monster/missile visuals that make a page more understandable.
- UI layout changes when explaining inventory, stash, cube, merc gear, or skill tree QOL.

Technical-only by default:

- Raw generated `itemtypes.txt` expansion rows.
- Low-level animation state-machine changes.
- Texture caches and raw model/sprite/particle manifests.
- Full raw Excel diffs unless linked as drilldown reports.

## Relationship Map

At a high level, retail-to-BK interpretation should follow this flow:

1. Start with the retail table meaning from the data guide.
2. Compare BK and retail table shape: added columns, added rows, removed rows, and modified rows.
3. Resolve player-facing labels through BK strings, falling back to retail/base strings where the repository loader does.
4. Join supporting tables before presenting a feature:
   - Item rows use base item tables, item types, properties, item stat costs, and strings.
   - Recipes use inputs/outputs from `cubemain.txt`, then item/property/string lookups.
   - Areas use level rows, presets/warps/maze rows, monster spawn columns, level strings, and optional tile files.
   - Monsters use stats, monster level tables, superunique rows, treasure classes, strings, and visual assets.
   - Skills use `skills.txt`, `skilldesc.txt`, `missiles.txt`, `states.txt`, formulas, and strings.
5. Present the result as a gameplay category first, with raw reports linked as technical drilldown.

## Next Refinement Targets

- Split cube recipes into player-meaningful groups and identify which groups are new to BK.
- Explain the generated `itemtypes.txt` system well enough to summarize it without exposing thousands of synthetic rows.
- Add a category-level summary generator later if this document becomes too manual to keep fresh.
- Decide which asset links are valuable on wiki pages, especially for new misc items, keys, gems, monsters, rune beams, and rift/area visuals.
- Validate the current wiki pages against this map and list missing player-facing coverage.
