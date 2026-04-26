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
- `1\.09\-Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### attackrate
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>30</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### coldmindam
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### curse\_resistance
- `Signed`:  (Old) &rarr; <ins><code>1</code></ins> (New)
- `descpriority`:  (Old) &rarr; <ins><code>36</code></ins> (New)
- `descfunc`:  (Old) &rarr; <ins><code>19</code></ins> (New)
- `descval`:  (Old) &rarr; <ins><code>1</code></ins> (New)
- `descstrpos`:  (Old) &rarr; <ins><code>StrSkill85</code></ins> (New)
- `descstrneg`:  (Old) &rarr; <ins><code>StrSkill85</code></ins> (New)
### damagepercent
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### firemindam
- `1\.09\-Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### hpregen
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
### item\_allskills
- `Save Bits`: <del><code>3</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>64</code></ins> (New)
### item\_attackertakesdamage
- `1\.09\-Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
### item\_elemskill
- `descpriority`: <del><code>155</code></del> (Old) &rarr; <ins><code>1</code></ins> (New)
- `descfunc`: <del><code>19</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `descstrpos`: <del><code>ModStr3i</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `descstrneg`: <del><code>ModStr3i</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
### item\_fasterattackrate
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>20</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_fastercastrate
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>20</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_fastergethitrate
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>20</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_fastermovevelocity
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>20</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_goldbonus
- `Save Bits`: <del><code>9</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>100</code></del> (Old) &rarr; <ins><code>300</code></ins> (New)
### item\_healafterkill
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>300</code></ins> (New)
### item\_hp\_perlevel
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_kickdamage
- `1\.09\-Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
### item\_levelreqpct
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
### item\_lightradius
- `Save Bits`: <del><code>4</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>4</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_magicbonus
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>100</code></del> (Old) &rarr; <ins><code>300</code></ins> (New)
### item\_mana\_perlevel
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_manaafterkill
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>300</code></ins> (New)
### item\_maxdamage\_percent
- `Save Bits`: <del><code>9</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
### item\_maxdamage\_percent\_perlevel
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_maxdamage\_perlevel
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_mindamage\_percent
- `Save Bits`: <del><code>9</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
### item\_nonclassskill
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
### item\_singleskill
- `Save Bits`: <del><code>3</code></del> (Old) &rarr; <ins><code>4</code></ins> (New)
### item\_throw\_maxdamage
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_throw\_mindamage
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_tohit\_perlevel
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### item\_tohitpercent\_perlevel
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### lightmindam
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### magicmindam
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### maxdamage
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### mindamage
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### passive\_mastery\_item\_req\_percent
- `1\.09\-Save Bits`:  (Old) &rarr; <ins><code>21</code></ins> (New)
- `1\.09\-Save Add`:  (Old) &rarr; <ins><code>0</code></ins> (New)
### secondary\_maxdamage
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### secondary\_mindamage
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>0</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### velocitypercent
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Save Add`: <del><code>30</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
