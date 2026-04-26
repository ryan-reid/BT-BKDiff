# Differences for itemstatcost.txt

*Key column used: `Stat`*

## Added Rows (17)
- augmented
- corrupted
- corruptordesc
- dyeblack
- dyed
- dyewhite
- hit\_skill\_splash
- item\_dex\_percent
- item\_elemskill\_cold
- item\_elemskill\_fire
- item\_elemskill\_lightning
- item\_elemskill\_magic
- item\_elemskill\_poison
- item\_enr\_percent
- item\_splashonhit
- item\_str\_percent
- item\_vit\_percent
## Modified Rows (41)
### armorclass\_vs\_hth
- `1\.09\-Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
### attackrate
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{30}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### coldmindam
- `1\.09\-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
### curse\_resistance
- `Signed`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `descpriority`:  (Old) &rarr; $\color{blue}{\text{36}}$ (New)
- `descfunc`:  (Old) &rarr; $\color{blue}{\text{19}}$ (New)
- `descval`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `descstrpos`:  (Old) &rarr; $\color{blue}{\text{StrSkill85}}$ (New)
- `descstrneg`:  (Old) &rarr; $\color{blue}{\text{StrSkill85}}$ (New)
### damagepercent
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### firemindam
- `1\.09\-Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
### hpregen
- `1\.09\-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
### item\_allskills
- `Save Bits`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{64}}$ (New)
### item\_attackertakesdamage
- `1\.09\-Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
### item\_elemskill
- `descpriority`: $\color{gray}{\text{155}}$ (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `descfunc`: $\color{gray}{\text{19}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `descstrpos`: $\color{gray}{\text{ModStr3i}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `descstrneg`: $\color{gray}{\text{ModStr3i}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
### item\_fasterattackrate
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_fastercastrate
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_fastergethitrate
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_fastermovevelocity
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_goldbonus
- `Save Bits`: $\color{gray}{\text{9}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{100}}$ (Old) &rarr; $\color{blue}{\text{300}}$ (New)
### item\_healafterkill
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{300}}$ (New)
### item\_hp\_perlevel
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_kickdamage
- `1\.09\-Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
### item\_levelreqpct
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
### item\_lightradius
- `Save Bits`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_magicbonus
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{100}}$ (Old) &rarr; $\color{blue}{\text{300}}$ (New)
### item\_mana\_perlevel
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_manaafterkill
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{300}}$ (New)
### item\_maxdamage\_percent
- `Save Bits`: $\color{gray}{\text{9}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
### item\_maxdamage\_percent\_perlevel
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_maxdamage\_perlevel
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_mindamage\_percent
- `Save Bits`: $\color{gray}{\text{9}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
### item\_nonclassskill
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
### item\_singleskill
- `Save Bits`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{4}}$ (New)
### item\_throw\_maxdamage
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_throw\_mindamage
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_tohit\_perlevel
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### item\_tohitpercent\_perlevel
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### lightmindam
- `1\.09\-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
### magicmindam
- `1\.09\-Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
- `Save Bits`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
### maxdamage
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### mindamage
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### passive\_mastery\_item\_req\_percent
- `1\.09\-Save Bits`:  (Old) &rarr; $\color{blue}{\text{21}}$ (New)
- `1\.09\-Save Add`:  (Old) &rarr; $\color{blue}{\text{0}}$ (New)
### secondary\_maxdamage
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### secondary\_mindamage
- `Save Bits`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### velocitypercent
- `Save Bits`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Save Add`: $\color{gray}{\text{30}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
