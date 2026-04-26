# Skill Calculation Model

This document explains how Diablo II skill values are actually constructed in this repo.

It is intended to bridge the gap between the high-level file guide in [Diablo_II_Data_File_Guide.md](E:\Games\GeminiDiff\BT-BKDiff\docs\Diablo_II_Data_File_Guide.md) and the real behavior we need in the skill exporters, report generation, and regression tests.

## Purpose

When a skill value looks wrong in generated output, the answer is usually not in a single file.

Skill math is built from multiple layers:

- `skills.txt` defines the core mechanics
- `skillcalc.txt` defines formula aliases used by descriptions
- `skilldesc.txt` defines what the UI actually renders
- `missiles.txt` provides range, duration, and damage data for missile-driven skills
- `monstats.txt` provides summon base stats
- `states.txt` can influence passive or aura behavior in some cases

The practical rule is:

- `skills.txt` tells us what the skill does
- `skilldesc.txt` tells us what the player sees

Those are not always the same thing.

## Core Files

### `skills.txt`

This is the main mechanics table.

It contains:

- raw params like `Param1` through `Param8`
- damage fields like `MinDam`, `MaxDam`, `EMin`, `EMax`, `ELen`
- mana fields like `mana`, `lvlmana`, `manashift`
- attack rating fields like `ToHit`, `LevToHit`, `ToHitCalc`
- weapon transfer fields like `SrcDam`
- server/client function ids
- summon references
- synergy formulas
- custom calc expressions

Important detail:

- many rows in `skills.txt` are not final player-facing values
- some are internal modifiers that must still be transformed before display

### `skillcalc.txt`

This file defines shorthand expressions used by `skilldesc.txt` and sometimes by the game data model more broadly.

Examples:

- `ln12 = par1 + (lvl - 1) * par2`
- `dm12 = ((110 * lvl) * (par2 - par1)) / (100 * (lvl + 6)) + par1`
- `toht = Attack Rating Bonus`
- `mana = Mana Cost Calculation`
- `mps = Mana Cost Per Second Calculation`
- `m1en`, `m1ex`, `m1rn` = values derived from `descmissile1`

This matters because `skilldesc.txt` often uses aliases like `ln12`, `dm34`, `m1eo`, `edln`, or `toht` instead of directly embedding every formula.

If we do not expand those aliases correctly, the displayed values will be wrong even if the base `skills.txt` row is correct.

### `skilldesc.txt`

This file controls the displayed skill tooltip and is the most important file for reproducing in-game UI values.

It does not just label values. It defines:

- which rows appear
- which string keys label those rows
- which formulas calculate the shown values
- whether values come from the skill, a missile, or a linked skill
- whether the same skill has multiple display sections

The main display blocks are:

- `descline1` to `descline6`
- `dsc2line1` to `dsc2line5`
- `dsc3line1` to `dsc3line7`

Each display row has:

- a line type like `36`, `74`, `75`, `76`, or `13`
- one or two string references such as `desctexta1`, `desctextb1`
- one or two formulas such as `desccalca1`, `desccalcb1`

This is why skill display reproduction is a presentation problem layered on top of a mechanics problem.

### `missiles.txt`

Many skills are not fully described by `skills.txt` alone.

If `skilldesc.txt` uses `descmissile1`, `descmissile2`, or `descmissile3`, then displayed values may come from missile rows instead.

Common examples:

- duration from `miss('some missile'.rang)`
- range from missile fields or missile-derived aliases
- elemental damage using `m1en`, `m1ex`, `m1el`
- average-per-second formulas based on missile elemental values

Practical consequence:

- a skill can show “damage”, “duration”, or “range” in the UI even when those numbers live in `missiles.txt`, not `skills.txt`

### `monstats.txt`

Summon skills often need monster base data.

This is especially important for:

- base life
- base armor
- base attack rating
- base damage ranges

`skills.txt` often gives modifiers or scaling, but the final summon display can depend on combining those modifiers with the summoned monster’s base row from `monstats.txt`.

### `states.txt`

This file is less central for basic skill number rendering, but it still matters for:

- auras
- passive states
- curses
- hidden behavior tied to skill-applied states

It is usually not the first place to look for a wrong number, but it can matter for understanding what a skill is actually applying.

## Calculation Pipeline

When we want to reproduce a skill’s displayed values, the correct order of thought is:

1. Identify the skill row in `skills.txt`
2. Identify the display row in `skilldesc.txt`
3. Expand any `skillcalc.txt` aliases used by that display row
4. Resolve references to:
   - the current skill level
   - linked skill levels
   - missile rows
   - summon monster rows
5. Apply any unit conversions needed for presentation
6. Render the final display label and value

If we skip step 2 and try to render directly from `skills.txt`, many tooltip values will be wrong or incomplete.

## Level Semantics

For this repo, we use:

- `blvl` = hard points
- `lvl` = displayed skill level after soft bonuses

This distinction matters because some formulas depend on:

- the visible skill level
- hard-point-only synergies
- linked skills using either `lvl` or `blvl`

If a test fixture mixes these up, the generated values can look like calculator bugs even when the evaluator is correct.

## Synergies

Synergies are not always simple “add X per level” rows.

They can appear as:

- direct expressions in `skills.txt`
- linked-skill formulas inside `skilldesc.txt`
- damage modifiers that apply only to one part of the display

Important rules:

- synergy inputs should generally use hard points unless the data explicitly implies otherwise
- not every displayed damage field shares the same synergy path
- physical, elemental, average-per-second, and summon-derived values can each scale differently

This is one of the most common reasons a skill has “one line correct, one line wrong”.

## Display Values Are Not Always Raw Engine Values

The UI often shows transformed values instead of raw stored values.

Common transforms include:

- frames to seconds
- 256-based internal values to human-readable damage
- radius conversion
- range conversion
- per-second or average damage conversions
- final summon totals instead of percent modifiers

Examples:

- `ELen` is stored in frames and often needs division by `25`
- poison and fire averages may be derived from 256-based elemental values
- missile `Range` often behaves as a duration field
- summon rows can show final life or damage while the skill row only stores modifiers

## Hidden and Linked Skill Dependencies

Some displayed values depend on other skills even when the dependency is easy to miss.

Patterns to watch for:

- `skill('SomeSkill'.lvl)`
- `skill('SomeSkill'.blvl)`
- `skill('SomeSkill'.par#)`
- `skill('SomeSkill'.ln##)`
- `sksrc('SomeSkill'.blvl)`

These can affect:

- synergies
- summon life
- passive bonuses
- average damage displays
- duration or radius displays

If a linked skill level is evaluated incorrectly, the result can be drastically wrong while still looking superficially plausible.

## Summon Skills Need Special Care

Summon skills are one of the hardest categories to model correctly.

There are two broad display styles:

1. Modifier displays
   - percent damage bonus
   - percent defense bonus
   - attack rating bonus

2. Final creature displays
   - actual damage range
   - actual life
   - actual final combat stats

These are not interchangeable.

A summon row may show:

- a percent modifier in one line
- a final range in another line
- a monster-base-derived life value in a third line

That is why summon skills often need both `skills.txt` and `monstats.txt`, and sometimes linked-skill context too.

## Common Failure Modes

These are the mistakes most likely to create bad output in this repo.

### 1. Treating `skills.txt` as the final UI source

This works for some simple skills and fails badly for many others.

### 2. Ignoring `skillcalc.txt` aliases

If `ln12`, `dm34`, `mps`, or `m1rn` are not resolved exactly, the displayed numbers drift quickly.

### 3. Missing missile lookups

If a skill uses missile-based display rows, the exported value may be zero, doubled, or missing entirely when missile references are not resolved.

### 4. Mixing up `lvl` and `blvl`

This is especially dangerous in regression fixtures where a captured value might reflect soft points but the scenario was recorded as hard points only.

### 5. Reusing one synergy multiplier for all damage lines

Many skills have separate display paths for:

- physical damage
- elemental damage
- average-per-second damage
- summon-derived damage

One generic multiplier is often wrong.

### 6. Confusing modifier rows with final rows

A label like `Damage` or `Defense` may refer to:

- a percent bonus
- a flat bonus
- a final displayed stat

The line type and the formula matter more than the label text alone.

### 7. Forgetting unit conversions

Many values are internally stored in frames, 256ths, half-ranges, or monster-base-relative terms.

## Guidance For This Repo

When implementing or debugging skill output here:

- use `skills.txt` to understand mechanics
- use `skilldesc.txt` to determine what must be shown
- use `skillcalc.txt` to expand formula aliases
- use `missiles.txt` whenever a display row references a missile
- use `monstats.txt` for summon base stats
- treat test fixtures as display expectations, not direct engine rows

If a generated value is wrong:

1. verify the display row being matched is the correct one
2. verify the formula aliases are expanded correctly
3. verify linked skill references use the correct level type
4. verify missile or summon dependencies are included
5. verify the final presentation conversion is correct

## What This Means For Tests

Regression tests for skill displays should validate the final rendered values against frozen source snapshots, not against live mod files.

Those tests should be interpreted carefully:

- a near miss may indicate rounding or fixture level drift
- a huge miss usually indicates the wrong formula, wrong linked-skill context, or missing supporting data

The goal of these tests is to verify parsing and display calculation behavior, not to lock the project to whatever the current live mod values happen to be.
