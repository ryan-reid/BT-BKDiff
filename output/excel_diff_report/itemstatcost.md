# Differences for itemstatcost.txt

*Key column used: `Stat`*

## Added Rows (20)
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

## Removed Rows (20)
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
- `1.09-Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)

### augmented
- `*ID`: $\color{gray}{\text{363}}$ (Old) &rarr; $\color{blue}{\text{370}}$ (New)

### coldmindam
- `1.09-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)

### corrupted
- `*ID`: $\color{gray}{\text{361}}$ (Old) &rarr; $\color{blue}{\text{368}}$ (New)

### corruptordesc
- `*ID`: $\color{gray}{\text{362}}$ (Old) &rarr; $\color{blue}{\text{369}}$ (New)

### damagepercent
- `descpriority`:  (Old) &rarr; $\color{blue}{	ext{88}}$ (New)
- `descfunc`:  (Old) &rarr; $\color{blue}{	ext{19}}$ (New)
- `descstrpos`:  (Old) &rarr; $\color{blue}{	ext{strModEnhancedDamage}}$ (New)
- `descstrneg`:  (Old) &rarr; $\color{blue}{	ext{strModEnhancedDamage}}$ (New)

### damageresist
- `descfunc`: $\color{gray}{\text{19}}$ (Old) &rarr; $\color{blue}{\text{29}}$ (New)
- `descstrneg`: $\text{ModStr2}\color{gray}{\text{uPercent}}$ (Old) &rarr; $\text{ModStr2}\color{blue}{\text{uPercentNegative}}$ (New)

### dyeblack
- `*ID`: $\color{gray}{\text{365}}$ (Old) &rarr; $\color{blue}{\text{372}}$ (New)

### dyewhite
- `*ID`: $\color{gray}{\text{364}}$ (Old) &rarr; $\color{blue}{\text{371}}$ (New)

### firemindam
- `1.09-Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)

### hpregen
- `1.09-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)

### item_allskills
- `descpriority`: $\color{gray}{\text{158}}$ (Old) &rarr; $\color{blue}{\text{156}}$ (New)

### item_attackertakesdamage
- `1.09-Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)

### item_aura
- `descpriority`: $\color{gray}{\text{159}}$ (Old) &rarr; $\color{blue}{\text{157}}$ (New)

### item_charge_noconsume
- `descpriority`: $\color{gray}{\text{159}}$ (Old) &rarr; $\color{blue}{\text{157}}$ (New)

### item_kickdamage
- `1.09-Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)

### item_nonclassskill
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)

### item_pierce
- `Multiply`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{2048}}$ (New)

### item_singleskill
- `Save Bits`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{4}}$ (New)

### item_skillonattack
- `descpriority`: $\color{gray}{\text{160}}$ (Old) &rarr; $\color{blue}{\text{158}}$ (New)

### item_skillondeath
- `descpriority`: $\color{gray}{\text{160}}$ (Old) &rarr; $\color{blue}{\text{158}}$ (New)

### item_skillongethit
- `descpriority`: $\color{gray}{\text{160}}$ (Old) &rarr; $\color{blue}{\text{158}}$ (New)

### item_skillonhit
- `descpriority`: $\color{gray}{\text{160}}$ (Old) &rarr; $\color{blue}{\text{158}}$ (New)

### item_skillonkill
- `descpriority`: $\color{gray}{\text{160}}$ (Old) &rarr; $\color{blue}{\text{158}}$ (New)

### item_skillonlevelup
- `descpriority`: $\color{gray}{\text{160}}$ (Old) &rarr; $\color{blue}{\text{158}}$ (New)

### lightmindam
- `1.09-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)

### magicmindam
- `1.09-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)

### passive_mag_mastery
- `descstrpos`: $\color{gray}{\text{ModitemdamMagsk}}$ (Old) &rarr; $\color{blue}{\text{ModStrMagMastery}}$ (New)
- `descstrneg`: $\color{gray}{\text{ModitemdamMagsk}}$ (Old) &rarr; $\color{blue}{\text{ModStrMagMastery}}$ (New)

### passive_mag_pierce
- `descstrpos`: $\color{gray}{\text{ModitemenresMagsk}}$ (Old) &rarr; $\color{blue}{\text{ModStrMagPierce}}$ (New)
- `descstrneg`: $\color{gray}{\text{ModitemenresMagsk}}$ (Old) &rarr; $\color{blue}{\text{ModStrMagPierce}}$ (New)

### passive_mastery_replenish_oncrit
- `*ID`: $\color{gray}{\text{206}}$ (Old) &rarr; $\color{blue}{\text{207}}$ (New)

### skill_cooldown
- `Send Bits`: $\color{gray}{	ext{32}}$ (Old) &rarr; $\color{blue}{	ext{(removed)}}$ (New)
- `Send Param Bits`: $\color{gray}{	ext{16}}$ (Old) &rarr; $\color{blue}{	ext{(removed)}}$ (New)
