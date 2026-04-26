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
- `1\.09\-Save Bits`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
- `Save Bits`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
### augmented
- `\*ID`: <strong><code>363</code></strong> (Old) &rarr; <strong><code>370</code></strong> (New)
### coldmindam
- `1\.09\-Save Bits`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
- `Save Bits`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
### corrupted
- `\*ID`: <strong><code>361</code></strong> (Old) &rarr; <strong><code>368</code></strong> (New)
### corruptordesc
- `\*ID`: <strong><code>362</code></strong> (Old) &rarr; <strong><code>369</code></strong> (New)
### damagepercent
- `descpriority`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>88</code></strong> (New)
- `descfunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>19</code></strong> (New)
- `descstrpos`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>strModEnhancedDamage</code></strong> (New)
- `descstrneg`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>strModEnhancedDamage</code></strong> (New)
### damageresist
- `descfunc`: <strong><code>19</code></strong> (Old) &rarr; <strong><code>29</code></strong> (New)
- `descstrneg`: <strong><code>ModStr2uPercent</code></strong> (Old) &rarr; <strong><code>ModStr2uPercentNegative</code></strong> (New)
### dyeblack
- `\*ID`: <strong><code>365</code></strong> (Old) &rarr; <strong><code>372</code></strong> (New)
### dyewhite
- `\*ID`: <strong><code>364</code></strong> (Old) &rarr; <strong><code>371</code></strong> (New)
### firemindam
- `1\.09\-Save Bits`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
- `Save Bits`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
### hpregen
- `1\.09\-Save Bits`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
- `Save Bits`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
### item\_allskills
- `descpriority`: <strong><code>158</code></strong> (Old) &rarr; <strong><code>156</code></strong> (New)
### item\_attackertakesdamage
- `1\.09\-Save Bits`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
- `Save Bits`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
### item\_aura
- `descpriority`: <strong><code>159</code></strong> (Old) &rarr; <strong><code>157</code></strong> (New)
### item\_charge\_noconsume
- `descpriority`: <strong><code>159</code></strong> (Old) &rarr; <strong><code>157</code></strong> (New)
### item\_kickdamage
- `1\.09\-Save Bits`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
- `Save Bits`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
### item\_nonclassskill
- `Save Bits`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
### item\_pierce
- `Multiply`: <strong><code>0</code></strong> (Old) &rarr; <strong><code>2048</code></strong> (New)
### item\_singleskill
- `Save Bits`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>4</code></strong> (New)
### item\_skillonattack
- `descpriority`: <strong><code>160</code></strong> (Old) &rarr; <strong><code>158</code></strong> (New)
### item\_skillondeath
- `descpriority`: <strong><code>160</code></strong> (Old) &rarr; <strong><code>158</code></strong> (New)
### item\_skillongethit
- `descpriority`: <strong><code>160</code></strong> (Old) &rarr; <strong><code>158</code></strong> (New)
### item\_skillonhit
- `descpriority`: <strong><code>160</code></strong> (Old) &rarr; <strong><code>158</code></strong> (New)
### item\_skillonkill
- `descpriority`: <strong><code>160</code></strong> (Old) &rarr; <strong><code>158</code></strong> (New)
### item\_skillonlevelup
- `descpriority`: <strong><code>160</code></strong> (Old) &rarr; <strong><code>158</code></strong> (New)
### lightmindam
- `1\.09\-Save Bits`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
- `Save Bits`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
### magicmindam
- `1\.09\-Save Bits`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
- `Save Bits`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
### passive\_mag\_mastery
- `descstrpos`: <strong><code>ModitemdamMagsk</code></strong> (Old) &rarr; <strong><code>ModStrMagMastery</code></strong> (New)
- `descstrneg`: <strong><code>ModitemdamMagsk</code></strong> (Old) &rarr; <strong><code>ModStrMagMastery</code></strong> (New)
### passive\_mag\_pierce
- `descstrpos`: <strong><code>ModitemenresMagsk</code></strong> (Old) &rarr; <strong><code>ModStrMagPierce</code></strong> (New)
- `descstrneg`: <strong><code>ModitemenresMagsk</code></strong> (Old) &rarr; <strong><code>ModStrMagPierce</code></strong> (New)
### passive\_mastery\_replenish\_oncrit
- `\*ID`: <strong><code>206</code></strong> (Old) &rarr; <strong><code>207</code></strong> (New)
### skill\_cooldown
- `Send Bits`: <strong><code>32</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `Send Param Bits`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
