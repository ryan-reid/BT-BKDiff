# BT-BKWiki Known Issues and Property Parsing Backlog

This document tracks data parsing, property resolution, and display bugs discovered in the BT-BKDiff wiki generator (`scripts/d2lib/` and `output/wiki/data/items-index.json`). These issues were identified during end-to-end verification against Diablo II Resurrected save binary serialization and mod tables (`uniqueitems.txt`, `setitems.txt`, `runes.txt`, `properties.txt`, `itemstatcost.txt`).

---

## 1. Critical Parsing & Property Resolution Bugs

### ISSUE-01: `'block': 'block1'` Alias Corrupts Increased Chance of Blocking into Faster Block Rate
- **Severity**: High (Affects 28 Unique shields/items, 11 Set items, and key runewords)
- **File**: `scripts/d2lib/services/resolver.py` (line 16 in `PropertyResolverService.__init__`)
- **Problem**:
  ```python
  self.aliases: Dict[str, str] = {
      'cast': 'cast1', 'balance': 'balance1', 'move': 'move1', 'swing': 'swing1',
      'block': 'block1',  # <--- BUG
      ...
  }
  ```
- **Root Cause**:
  - In `properties.txt`, `block` is `stat1: toblock` (StatId 20: Increased Chance of Blocking).
  - In contrast, `block1`, `block2`, and `block3` are `stat1: item_fasterblockrate` (StatId 102: Faster Block Rate).
  - Shorthands like `cast`, `balance`, `move`, `swing` do not exist as independent properties without their tier suffix `1/2/3`, but `block` **is** a valid property.
  - By aliasing `'block': 'block1'`, any item with the `block` property has its Chance to Block converted into Faster Block Rate.
  - For items that legitimately feature **both** Faster Block Rate and Increased Chance of Blocking, the wiki displays duplicate "Faster Block Rate" lines instead of Chance to Block.
- **Affected Items**:
  - **28 Unique Items**:
    - *Moser's Blessed Circle*: displays `+55% Faster Block Rate` and `+60% Faster Block Rate` (should be `+55% Increased Chance of Blocking` and `+60% Faster Block Rate`).
    - *Stormshield*: displays `+30% Faster Block Rate` and `+40% Faster Block Rate` (should be `+30% Increased Chance of Blocking` and `+40% Faster Block Rate`).
    - *Herald of Zakarum*: displays `+30% Faster Block Rate` and `+30% Faster Block Rate` (should be `+30% Increased Chance of Blocking` and `+30% Faster Block Rate`).
    - *Homunculus*: displays `+40% Faster Block Rate` and `+30% Faster Block Rate` (should be `+40% Increased Chance of Blocking` and `+30% Faster Block Rate`).
    - *Guardian Angel*: displays `+30% Faster Block Rate` and `+35% Faster Block Rate` (should be `+30% Increased Chance of Blocking` and `+35% Faster Block Rate`).
    - *Swordguard*: displays `+75% Faster Block Rate` and `+75% Faster Block Rate` (should be `+75% Increased Chance of Blocking` and `+75% Faster Block Rate`).
    - Also affects: *Twitchthroe*, *Pelta Lunata*, *Umbral Disk*, *Stormguild*, *Swordback Hold*, *Steelclash*, *Bverrit Keep*, *The Ward*, *Visceratuant*, *Stormchaser*, *Kerke's Sanctuary*, *Radament's Sphere*, *Lance Guard*, *Steelshade*, *Alma Negra*, *Dragonscale*, *Spirit Ward*, *Spike Thorn*, *Elemental Union*, *Trophy of the Lich King Toudi*, *Primal Stormshield*.
  - **11 Set Items**:
    - *Civerb's Ward* (`block 20`)
    - *Isenhart's Parry* (`block 30`)
    - *Sigon's Guard* (`block 30`)
    - *Griswold's Honor* (`block 60`)
    - *Trang-Oul's Wing* (`block 30`)
    - *Horazon's Secrets* (`block 20`)
    - *Sigurd's Deflector* (`block 50`)
    - *Griswold's Pride* (`block 40`)
    - *Trang-Oul's Appendage* (`block 35`)
    - *Sandro's Skull* (`block 50`)
    - *Horazon's Sanctuary* (`block 50`)
  - **Runewords**:
    - *Rhyme* (`Shael + Eth`): displays `+20% Faster Block Rate` and `+40% Faster Block Rate` (should be `+20% Increased Chance of Blocking` and `+40% Faster Block Rate`).
    - *Knight's Vigil*: displays `+20% Faster Block Rate` instead of `+20% Increased Chance of Blocking`.
- **Suggested Fix**:
  - Remove `'block': 'block1'` from `self.aliases` in `scripts/d2lib/services/resolver.py`.

---

### ISSUE-02: Poison Damage Duration Rendered as Seconds Using Damage Number
- **Severity**: Medium
- **File**: `scripts/d2lib/services/resolver.py` (poison property resolution / `dmg-pois` handler)
- **Problem**:
  - For items with `dmg-pois`, the tooltip text renders as:
    `"Adds {min}-{max} Poison Damage Over {max} Seconds"`
    where the damage value itself is mistakenly inserted as the seconds duration.
- **Examples**:
  - *Atma's Scarab* (`dmg-pois`: `par=100, min=102, max=102`): displays *"Adds 102-102 Poison Damage Over 102 Seconds"*.
  - *Rainbow Facet (Poison)* (`par=100, min=187, max=187`): displays *"Adds 187-187 Poison Damage Over 187 Seconds"*.
  - *Blackbog's Sharp*, *Blacktongue*, *Hellplague*, etc.
- **Root Cause & Fix**:
  - In Diablo II, `par` defines duration in game frames (100 frames = 4.0 seconds at 25 fps, encoded as StatId 59 `poisonlength`).
  - The duration formula must compute seconds from `param / 25.0` (e.g. `100 / 25 = 4 seconds`), not from `max_val`.

---

### ISSUE-03: Ormus' Robes `skill-rand` Rendered as `+36-60 to Unsummon (Paladin only)`
- **Severity**: Medium
- **File**: `scripts/d2lib/services/resolver.py` (handling of `func 12` / `skill-rand`)
- **Problem**:
  - Ormus' Robes property row displays: `+36-60 to Unsummon (Paladin only)`.
- **Root Cause**:
  - In `uniqueitems.txt`, Ormus' Robes has `prop: skill-rand, par: 3, min: 36, max: 60`.
  - `par: 3` is the skill level bonus (+3).
  - `min: 36, max: 60` is the range of Sorceress Skill IDs in `skills.txt` (ID 36 is `Fire Bolt`, ID 60 is `Frozen Orb`).
  - The resolver treated `min` and `max` as a rolled level range (`36-60`) rather than skill ID bounds, and misresolved ID 36 into the wrong skill name and class constraint.
- **Suggested Fix**:
  - For `func 12` (`skill-rand`), treat `par` as the bonus level and `[min, max]` as the permissible skill ID range.
  - Render as `+3 to [Random Sorceress Skill]` (or enumerate the allowable skill range from `skills.txt`).

---

### ISSUE-04: Sunder Charm Affix 5 Rendered as `(Missing Affix 5 data)`
- **Severity**: Low
- **File**: `scripts/d2lib/services/resolver.py` (lines 55–60)
- **Problem**:
  - Sunder charms on the wiki display `(Missing Affix 5 data)`:
    ```python
    self.manual_overrides = {
        'gelid-affix5': '(Missing Affix 5 data)',
        'incendiary-affix5': '(Missing Affix 5 data)',
        'magnetic-affix5': '(Missing Affix 5 data)',
        'virulent-affix5': '(Missing Affix 5 data)',
        'breaching-affix5': '(Missing Affix 5 data)',
        'mystical-affix5': '(Missing Affix 5 data)'
    }
    ```
- **Root Cause & Fix**:
  - Sunder charms in BKDiablo utilize `propertygroups.txt`.
  - The 5th sub-property in each sunder group corresponds to the negative player resistance penalty (e.g., `-70% to -90% to Cold Resist`).
  - Rather than hardcoding placeholder strings, parse `propertygroups.txt` dynamically and resolve the 5th sub-property to its corresponding player resistance stat.

---

### ISSUE-05: Guardian Angel Blank Min/Max Yields Blank Negative Monster Defense
- **Severity**: Low
- **File**: `scripts/d2lib/services/resolver.py`
- **Problem**:
  - Guardian Angel displays `'- to Monster Defense Per Hit'` with no numeric value.
- **Root Cause**:
  - In `uniqueitems.txt`, Guardian Angel specifies `prop5: dmg-ac, par5: 100, min5: , max5: `.
  - Because `min5` and `max5` are blank, the resolver inserts an empty range string into the template `-%d to Monster Defense Per Hit`.
- **Suggested Fix**:
  - If `min_val` and `max_val` are empty but `param` is non-empty for `dmg-ac`, fall back to `param` to render `-100 to Monster Defense Per Hit`.

---

## 2. Catalog & Slug Collision Issues

### ISSUE-06: Blank Charm (Unique ID 440) Missing from Index
- **File**: `output/wiki/data/items-index.json`
- **Problem**: Blank Charm (Unique ID 440, item code `mfd`) is missing from the generated unique item wiki index.

### ISSUE-07: Duplicate Item Name URL Collisions
- **Problem**:
  - When multiple unique items share the same display name:
    - *Azurewrath* (ID 29 Crystal Sword vs ID 301 Phase Blade)
    - *Rainbow Facet* (10 distinct variants: 4 elements x [Die, Level-Up] + 2 Magic variants)
  - The wiki generates arbitrary suffix slugs (`azurewrath-phase-blade`, `rainbow-facet-jewel-2`, etc.) without clear element or trigger metadata in the index title or summary cards.
- **Suggested Fix**:
  - Disambiguate index titles or tags with base item and variant info (e.g. *"Rainbow Facet (5/5 Cold Die)"* or *"Azurewrath (Phase Blade)"*).

---

---

### ISSUE-08: Chinese Censorship Overlay Hijacking Skill & Item Strings ("Life Contributor") [RESOLVED]
- **Severity**: Critical (Affected all skill 96 instances including *Last Wish*, skill 68 instances, and ~120 item/skill names)
- **File**: `scripts/d2lib/repository.py` (`D2Repository._load_strings`)
- **Problem**:
  - *Last Wish* runeword displayed `+11 to Life Contributor` instead of `+11 to Sacrifice`.
  - *Rainbow Facet (Magic Level-Up)* displayed `Level 51 Spike Armor` instead of `Bone Armor`.
  - Unique items like *Wormskull* rendered as *Wormsteel*, *Skull Collector* as *Soul Collector*, etc.
- **Root Cause**:
  - `data/retail/local/lng/strings/chinese-overlay.json` contains Blizzard Chinese censorship overrides extracted from D2R retail files (replacing words like "Sacrifice" with "Life Contributor", "Bone/Skull" with "Spike/Steel/Soul").
  - `_load_strings()` in `repository.py` had an inverted directory loading hierarchy that loaded retail strings before mod strings, and did not exclude overlay files.
  - This allowed `chinese-overlay.json` to load first and lock in 119 censored strings into `self.strings`.
- **Resolution**:
  - Enforced strict hierarchical directory priority: `Mod strings > Base strings > Retail strings`.
  - Explicitly excluded `*overlay*.json` files during string ingestion.
  - Verified: *Last Wish* now correctly displays `+11 to Sacrifice`, and all 119 original English strings are restored.

---

### ISSUE-09: Missing Property Aliases in Table Ingestion [RESOLVED]
- **Severity**: Medium (Affected unique, set, and affix tables)
- **File**: `scripts/d2lib/services/resolver.py`
- **Problem**:
  - *Tancred's Crowbill* displayed `Unknown property: hitskill (15-10)`.
  - *Death's Touch* displayed `Unknown property: attskill (20-10)`.
  - *Primal Sickle of Perseus* displayed `Unknown property: ar% (200)`.
  - Rainbow Facet / level-up items displayed raw fallback strings.
- **Root Cause**:
  - Mod text tables contained human abbreviations and typos for valid property codes:
    - `attskill` (Death's Touch) -> `att-skill`
    - `hitskill` (Tancred's Crowbill) -> `hit-skill`
    - `ar%` (Primal Sickle of Perseus) -> `att%`
    - `level-skill` -> `levelup-skill`
- **Resolution**:
  - Added `'ar%': 'att%'`, `'attskill': 'att-skill'`, `'hitskill': 'hit-skill'`, and `'level-skill': 'levelup-skill'` to `self.aliases` in `resolver.py`.
  - Set items and uniques now resolve smoothly to their Chance to Cast and Attack Rating bonus lines.

---

### ISSUE-10: Commented & Visual Table Properties [RESOLVED]
- **Severity**: Low
- **File**: `scripts/d2lib/services/resolver.py`
- **Problem**:
  - *Ironstone* displayed `Unknown property: *enr (-5)`.
  - *Blacktongue* displayed `Unknown property: *hp (-10)`.
  - *Gorefoot* and *Swordback Hold* displayed `Unknown property: bloody (3-5)`.
- **Root Cause**:
  - Properties starting with `*` are designer comments/disabled stats in Blizzard spreadsheet tables.
  - `bloody` is a valid visual effect property (`item_extrablood`, StatId 140) without a string description table entry.
- **Resolution**:
  - `resolve_property()` now silently ignores codes starting with `*` (`code_lower.startswith('*')`).
  - Added clean manual override for `bloody` rendering as `Extra Blood`.

---

## 3. Resolution Status Summary
- **ISSUE-01 (Block vs Block1)**: RESOLVED in `resolver.py`.
- **ISSUE-02 (Poison Duration Calculation)**: RESOLVED in `resolver.py`.
- **ISSUE-03 (Ormus' Robes Random Skill Range)**: RESOLVED in `resolver.py`.
- **ISSUE-04 (Sunder Affix 5 Resolution)**: RESOLVED via `propertygroups.txt`.
- **ISSUE-05 (Guardian Angel Blank Min/Max)**: RESOLVED in `resolver.py`.
- **ISSUE-08 (Life Contributor / Chinese Overlay)**: RESOLVED in `repository.py`.
- **ISSUE-09 (Missing Property Aliases)**: RESOLVED in `resolver.py`.
- **ISSUE-10 (Commented & Visual Properties)**: RESOLVED in `resolver.py`.

---

## 4. Reference Implementation
A verified, production-tested reference parser addressing all of the above issues is implemented in `d2sitems`:
- Core property & group resolver: `E:\Games\d2sitems\PropertyRangeCatalog.cs`
- Verified test harness: `E:\Games\d2sitems\tests\engine_regressions\Program.cs`
- Dual-mode WebAssembly / local server parity tests passing across all fixtures.
