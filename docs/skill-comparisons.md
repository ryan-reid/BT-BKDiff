# Skill comparison cards

The wiki no longer reads generated skill-tree Markdown. Its L1/L10/L20/L20+10 estimates, effect labels, caps, and inferred synergy summaries have been removed from the class pages. The canonical rebuild no longer runs the legacy extractor. The old service and standalone CLI remain isolated for their existing snapshot tests; they do not supply wiki content.

## Presentation

Skills use the same two-column comparison and token highlighting as items. Each class page supports text search and modified, added, removed, and unchanged filters based on the displayed fields. Filters are stored in the URL and carried through the Retail and BTDiablo baseline switch. Skill anchors remain shareable. Cards are rendered in HTML so comparisons remain available without JavaScript.

Each card groups base skill information, source formulas, and synergies. Base damage and mana fields use their source values. Directly referenced parameters have separate comparison rows beneath the original expression. Synergy rows use the dedicated tooltip section, with literal values and direct parameter references displayed as the game supplies them. More complex tooltip expressions are shown as source inputs. A tooltip conflict is shown when supported server settings contradict it.

## Join map

Each baseline builds its own graph first. A changed missile reference must compare the old linked record against the new linked record, not silently reuse the current graph for both versions.

| Starting record / field | Destination | Purpose |
| --- | --- | --- |
| `skills.skilldesc` | `skilldesc.skilldesc` | Tooltip layout, description functions and expressions |
| `skilldesc` string/text keys | Resolved localization | Names, descriptions, effect and synergy wording |
| `skills.srvmissile*`, `cltmissile*` | `missiles.Missile` | Server and client projectile settings |
| `skilldesc.descmissile*` | `missiles.Missile` | Projectile values used by the tooltip; not necessarily emitted |
| Missile `SubMissile*`, `HitSubMissile*`, client variants, `ExplosionMissile` | `missiles.Missile` recursively | Secondary bolts, explosions, fragments; cycles deduplicated |
| Aura/passive/required states | `states.state` | Applied states and restrictions |
| Aura/passive stats; `stat('...')` | `itemstatcost.Stat` | Stat units, operations, localization metadata |
| Stat operation inputs and `maxstat` | `itemstatcost.Stat` | Linked stat definitions; no automatic arithmetic |
| `summon` | `monstats.Id` | Pet stats, AI, skills, missiles and resistances |
| `monstats.MonStatsEx`, `MonProp` | `monstats2.Id`, `monprop.Id` | Summon collision/animation data and assigned properties |
| Summon skills and `sumskill*` | `skills.skill` | Pet attacks and granted skills, recursively joined |
| `monprop.prop*` | `properties.code` → `itemstatcost.Stat` | Summon property definitions |
| `pettype`, `requirespettype` | `pettype.pet type` | Pet category where the table is available |
| Weapon include/exclude types and passive item type | `itemtypes.Code` and `Equiv1/2` | Equipment eligibility definitions |
| `miss('...')` expressions | `missiles.Missile` | Explicit expression dependencies |
| `skill('...')`, `sklvl('...')`, prerequisites, missile damage-source skill | Skill references, with links to class cards | Context; not automatically a synergy or recursively attributed damage |

Named references are resolved case-insensitively. Numeric references can use available ID columns. Full edge lists preserve which field supplied each connection. Missing targets are reported. Added/removed *linked records* mean graph membership changed; they do not necessarily mean the underlying game record was added/deleted.

Author comments annotate parameters but do not count as executable changes. Blank and zero remain distinct. Runtime fields, including function IDs and raw formulas, are compared without repair or evaluation. The missing closing parenthesis in Holy Bolt's current `calc1`, for example, remains visible rather than silently fixed.

## Supported behavior interpretations

For missiles using server hit function 7 and server damage function 15, `sHitPar2` decodes the full-damage monster categories and `sHitPar1` decodes ally healing. The server fields govern the overview; client fields remain separately inspectable. Every interpretation includes its source fields. Other function combinations remain raw comparisons.

The local Holy Bolt data provides a regression example: BK expands full-damage targets from demons/undead to all enemy monster categories and disables ally healing. BT keeps the monster restriction and also disables server healing. Retail enables healing. Fist of the Heavens' secondary bolts are found by traversing its delay missile's child reference. Monster-category eligibility does not establish immunity bypass, final damage, player eligibility, or actual engine behavior after code patches.

## Options explored and remaining work

| Option | Assessment |
| --- | --- |
| Diff only `skills.txt` | Insufficient: misses Holy Bolt's target change and secondary missile behavior |
| Rebuild tooltip tables from `skilldesc` | Useful for reproducing game text, but text can be stale and description codes are not execution logic |
| Join and compare source graphs | Implemented foundation; exposes real dependencies without manufacturing values |
| Interactive level/synergy calculator | Requires a separate validated evaluator and explicit build inputs; not supplied by the legacy estimates |

A future calculator needs exact integer division and rounding, fixed-point shifts, hard versus effective levels, segmented damage increments, expression precedence/ternaries, function-specific parameters, mastery and character stats, weapon inputs, summon scaling and difficulty, projectile damage ownership, and unsupported-operation reporting. It must keep raw damage, tooltip display, and post-resistance damage distinct. Start with independently verified families and label the supported scope per result.

Further graph coverage includes summon AI parameter interpretation, monlevel/difficulty scaling, equipment and proc consumers, animation breakpoints, overlay assets, aura filter decoding, and generic description/engine function registries. The snapshot lacks a pettype table; those references are shown as unresolved rather than invented. Localization uses the repository's existing mod/base/retail precedence and reports resolved keys; it does not yet provide file-level localization provenance. A change to a shared stat or inherited source record can affect multiple cards.

`tests/test_skill_comparison.py` covers missile-only changes, recursive child missiles and cycles, replacement links, missing strings, unsupported functions, summons, added/removed skills, references versus synergies, explicit zeroes, and HTML escaping.
