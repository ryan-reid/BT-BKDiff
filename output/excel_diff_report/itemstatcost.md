# Differences for itemstatcost.txt

*Key column used: `Stat`*

## Added Rows (20)
- create\_season
- customization\_index
- heraldtier
- item\_magic\_damagemax\_perlevel
- item\_pierce\_cold\_immunity
- item\_pierce\_damage\_immunity
- item\_pierce\_fire\_immunity
- item\_pierce\_light\_immunity
- item\_pierce\_magic\_immunity
- item\_pierce\_poison\_immunity
- lasthitreactframe
- missile\_thorns\_percent
- passive\_dmg\_pierce
- passive\_mastery\_item\_level\_req\_percent
- passive\_mastery\_item\_req\_percent
- psychicward
- psychicwardmax
- skill\_channeling\_tick
- ua\_defeated
- ua\_escalation
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
### armorclass\_vs\_hth
- `1\.09\-Save Bits`: $\\color{gray}{\\text{8}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{8}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
### augmented
- `\*ID`: $\\color{gray}{\\text{363}}$ (Old) &rarr; $\\color{blue}{\\text{370}}$ (New)
### coldmindam
- `1\.09\-Save Bits`: $\\color{gray}{\\text{6}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{8}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
### corrupted
- `\*ID`: $\\color{gray}{\\text{361}}$ (Old) &rarr; $\\color{blue}{\\text{368}}$ (New)
### corruptordesc
- `\*ID`: $\\color{gray}{\\text{362}}$ (Old) &rarr; $\\color{blue}{\\text{369}}$ (New)
### damagepercent
- `descpriority`:  (Old) &rarr; $\color{blue}{\\text{88}}$ (New)
- `descfunc`:  (Old) &rarr; $\color{blue}{\\text{19}}$ (New)
- `descstrpos`:  (Old) &rarr; $\color{blue}{\\text{strModEnhancedDamage}}$ (New)
- `descstrneg`:  (Old) &rarr; $\color{blue}{\\text{strModEnhancedDamage}}$ (New)
### damageresist
- `descfunc`: $\\color{gray}{\\text{19}}$ (Old) &rarr; $\\color{blue}{\\text{29}}$ (New)
- `descstrneg`: $\\text{ModStr2}\\color{gray}{\\text{uPercent}}$ (Old) &rarr; $\\text{ModStr2}\\color{blue}{\\text{uPercentNegative}}$ (New)
### dyeblack
- `\*ID`: $\\color{gray}{\\text{365}}$ (Old) &rarr; $\\color{blue}{\\text{372}}$ (New)
### dyewhite
- `\*ID`: $\\color{gray}{\\text{364}}$ (Old) &rarr; $\\color{blue}{\\text{371}}$ (New)
### firemindam
- `1\.09\-Save Bits`: $\\color{gray}{\\text{8}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{8}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
### hpregen
- `1\.09\-Save Bits`: $\\color{gray}{\\text{6}}$ (Old) &rarr; $\\color{blue}{\\text{7}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{6}}$ (Old) &rarr; $\\color{blue}{\\text{7}}$ (New)
### item\_allskills
- `descpriority`: $\\color{gray}{\\text{158}}$ (Old) &rarr; $\\color{blue}{\\text{156}}$ (New)
### item\_attackertakesdamage
- `1\.09\-Save Bits`: $\\color{gray}{\\text{7}}$ (Old) &rarr; $\\color{blue}{\\text{8}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{7}}$ (Old) &rarr; $\\color{blue}{\\text{8}}$ (New)
### item\_aura
- `descpriority`: $\\color{gray}{\\text{159}}$ (Old) &rarr; $\\color{blue}{\\text{157}}$ (New)
### item\_charge\_noconsume
- `descpriority`: $\\color{gray}{\\text{159}}$ (Old) &rarr; $\\color{blue}{\\text{157}}$ (New)
### item\_kickdamage
- `1\.09\-Save Bits`: $\\color{gray}{\\text{7}}$ (Old) &rarr; $\\color{blue}{\\text{8}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{7}}$ (Old) &rarr; $\\color{blue}{\\text{8}}$ (New)
### item\_nonclassskill
- `Save Bits`: $\\color{gray}{\\text{6}}$ (Old) &rarr; $\\color{blue}{\\text{7}}$ (New)
### item\_pierce
- `Multiply`: $\\color{gray}{\\text{0}}$ (Old) &rarr; $\\color{blue}{\\text{2048}}$ (New)
### item\_singleskill
- `Save Bits`: $\\color{gray}{\\text{3}}$ (Old) &rarr; $\\color{blue}{\\text{4}}$ (New)
### item\_skillonattack
- `descpriority`: $\\color{gray}{\\text{160}}$ (Old) &rarr; $\\color{blue}{\\text{158}}$ (New)
### item\_skillondeath
- `descpriority`: $\\color{gray}{\\text{160}}$ (Old) &rarr; $\\color{blue}{\\text{158}}$ (New)
### item\_skillongethit
- `descpriority`: $\\color{gray}{\\text{160}}$ (Old) &rarr; $\\color{blue}{\\text{158}}$ (New)
### item\_skillonhit
- `descpriority`: $\\color{gray}{\\text{160}}$ (Old) &rarr; $\\color{blue}{\\text{158}}$ (New)
### item\_skillonkill
- `descpriority`: $\\color{gray}{\\text{160}}$ (Old) &rarr; $\\color{blue}{\\text{158}}$ (New)
### item\_skillonlevelup
- `descpriority`: $\\color{gray}{\\text{160}}$ (Old) &rarr; $\\color{blue}{\\text{158}}$ (New)
### lightmindam
- `1\.09\-Save Bits`: $\\color{gray}{\\text{6}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{6}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
### magicmindam
- `1\.09\-Save Bits`: $\\color{gray}{\\text{6}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
- `Save Bits`: $\\color{gray}{\\text{8}}$ (Old) &rarr; $\\color{blue}{\\text{9}}$ (New)
### passive\_mag\_mastery
- `descstrpos`: $\\color{gray}{\\text{ModitemdamMagsk}}$ (Old) &rarr; $\\color{blue}{\\text{ModStrMagMastery}}$ (New)
- `descstrneg`: $\\color{gray}{\\text{ModitemdamMagsk}}$ (Old) &rarr; $\\color{blue}{\\text{ModStrMagMastery}}$ (New)
### passive\_mag\_pierce
- `descstrpos`: $\\color{gray}{\\text{ModitemenresMagsk}}$ (Old) &rarr; $\\color{blue}{\\text{ModStrMagPierce}}$ (New)
- `descstrneg`: $\\color{gray}{\\text{ModitemenresMagsk}}$ (Old) &rarr; $\\color{blue}{\\text{ModStrMagPierce}}$ (New)
### passive\_mastery\_replenish\_oncrit
- `\*ID`: $\\color{gray}{\\text{206}}$ (Old) &rarr; $\\color{blue}{\\text{207}}$ (New)
### skill\_cooldown
- `Send Bits`: $\color{gray}{\\text{32}}$ (Old) &rarr; $\color{blue}{\\text{(removed)}}$ (New)
- `Send Param Bits`: $\color{gray}{\\text{16}}$ (Old) &rarr; $\color{blue}{\\text{(removed)}}$ (New)
