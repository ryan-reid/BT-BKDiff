# Differences for itemstatcost.txt

*Key column used: `Stat`*

## Added Rows in BK (New) (20)
- create_season
- customization_index
- heraldtier
- item_magic_damagemax_perlevel
- item_pierce_cold_immunity
- item_pierce_damage_immunity
- item_pierce_fire_immunity
- item_pierce_light_immunity
- item_pierce_magic_immunity
- item_pierce_poison_immunity
- lasthitreactframe
- missile_thorns_percent
- passive_dmg_pierce
- passive_mastery_item_level_req_percent
- passive_mastery_item_req_percent
- psychicward
- psychicwardmax
- skill_channeling_tick
- ua_defeated
- ua_escalation

## Removed Rows in BK (New) (20)
- dyecblue
- dyecred
- dyedarkpurple
- dyedarkyellow
- dyelightgreen
- dyelightpurple
- dyeorange
- unused183
- unused184
- unused187
- unused189
- unused190
- unused191
- unused192
- unused193
- unused203
- unused208
- unused209
- unused210
- unused211

## Modified Rows (31)
### armorclass_vs_hth
- `1.09-Save Bits`: `8` (Old) &rarr; **`9` (New)**
- `Save Bits`: `8` (Old) &rarr; **`9` (New)**

### augmented
- `*ID`: `363` (Old) &rarr; **`370` (New)**

### coldmindam
- `1.09-Save Bits`: `6` (Old) &rarr; **`9` (New)**
- `Save Bits`: `8` (Old) &rarr; **`9` (New)**

### corrupted
- `*ID`: `361` (Old) &rarr; **`368` (New)**

### corruptordesc
- `*ID`: `362` (Old) &rarr; **`369` (New)**

### damagepercent
- `descpriority`: `*empty*` (Old) &rarr; **`88` (New)**
- `descfunc`: `*empty*` (Old) &rarr; **`19` (New)**
- `descstrpos`: `*empty*` (Old) &rarr; **`strModEnhancedDamage` (New)**
- `descstrneg`: `*empty*` (Old) &rarr; **`strModEnhancedDamage` (New)**

### damageresist
- `descfunc`: `19` (Old) &rarr; **`29` (New)**
- `descstrneg`: `ModStr2uPercent` (Old) &rarr; **`ModStr2uPercentNegative` (New)**

### dyeblack
- `*ID`: `365` (Old) &rarr; **`372` (New)**

### dyewhite
- `*ID`: `364` (Old) &rarr; **`371` (New)**
- `descval`: ` ` (Old) &rarr; **`*empty*` (New)**

### firemindam
- `1.09-Save Bits`: `8` (Old) &rarr; **`9` (New)**
- `Save Bits`: `8` (Old) &rarr; **`9` (New)**

### hpregen
- `1.09-Save Bits`: `6` (Old) &rarr; **`7` (New)**
- `Save Bits`: `6` (Old) &rarr; **`7` (New)**

### item_allskills
- `descpriority`: `158` (Old) &rarr; **`156` (New)**

### item_attackertakesdamage
- `1.09-Save Bits`: `7` (Old) &rarr; **`8` (New)**
- `Save Bits`: `7` (Old) &rarr; **`8` (New)**

### item_aura
- `descpriority`: `159` (Old) &rarr; **`157` (New)**

### item_charge_noconsume
- `descpriority`: `159` (Old) &rarr; **`157` (New)**

### item_kickdamage
- `1.09-Save Bits`: `7` (Old) &rarr; **`8` (New)**
- `Save Bits`: `7` (Old) &rarr; **`8` (New)**

### item_nonclassskill
- `Save Bits`: `6` (Old) &rarr; **`7` (New)**

### item_pierce
- `Multiply`: `0` (Old) &rarr; **`2048` (New)**

### item_singleskill
- `Save Bits`: `3` (Old) &rarr; **`4` (New)**

### item_skillonattack
- `descpriority`: `160` (Old) &rarr; **`158` (New)**

### item_skillondeath
- `descpriority`: `160` (Old) &rarr; **`158` (New)**

### item_skillongethit
- `descpriority`: `160` (Old) &rarr; **`158` (New)**

### item_skillonhit
- `descpriority`: `160` (Old) &rarr; **`158` (New)**

### item_skillonkill
- `descpriority`: `160` (Old) &rarr; **`158` (New)**

### item_skillonlevelup
- `descpriority`: `160` (Old) &rarr; **`158` (New)**

### lightmindam
- `1.09-Save Bits`: `6` (Old) &rarr; **`9` (New)**
- `Save Bits`: `6` (Old) &rarr; **`9` (New)**

### magicmindam
- `1.09-Save Bits`: `6` (Old) &rarr; **`9` (New)**
- `Save Bits`: `8` (Old) &rarr; **`9` (New)**

### passive_mag_mastery
- `descstrpos`: `ModitemdamMagsk` (Old) &rarr; **`ModStrMagMastery` (New)**
- `descstrneg`: `ModitemdamMagsk` (Old) &rarr; **`ModStrMagMastery` (New)**

### passive_mag_pierce
- `descstrpos`: `ModitemenresMagsk` (Old) &rarr; **`ModStrMagPierce` (New)**
- `descstrneg`: `ModitemenresMagsk` (Old) &rarr; **`ModStrMagPierce` (New)**

### passive_mastery_replenish_oncrit
- `*ID`: `206` (Old) &rarr; **`207` (New)**

### skill_cooldown
- `Send Bits`: `32` (Old) &rarr; **`*empty*` (New)**
- `Send Param Bits`: `16` (Old) &rarr; **`*empty*` (New)**

