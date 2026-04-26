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
- `1\.09\-Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### augmented
- `\*ID`: <del><code>363</code></del> (Old) &rarr; <ins><code>370</code></ins> (New)
### coldmindam
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### corrupted
- `\*ID`: <del><code>361</code></del> (Old) &rarr; <ins><code>368</code></ins> (New)
### corruptordesc
- `\*ID`: <del><code>362</code></del> (Old) &rarr; <ins><code>369</code></ins> (New)
### damagepercent
- `descpriority`:  (Old) &rarr; <ins><code>88</code></ins> (New)
- `descfunc`:  (Old) &rarr; <ins><code>19</code></ins> (New)
- `descstrpos`:  (Old) &rarr; <ins><code>strModEnhancedDamage</code></ins> (New)
- `descstrneg`:  (Old) &rarr; <ins><code>strModEnhancedDamage</code></ins> (New)
### damageresist
- `descfunc`: <del><code>19</code></del> (Old) &rarr; <ins><code>29</code></ins> (New)
- `descstrneg`: <code>ModStr2</code><del><code>uPercent</code></del> (Old) &rarr; <code>ModStr2</code><ins><code>uPercentNegative</code></ins> (New)
### dyeblack
- `\*ID`: <del><code>365</code></del> (Old) &rarr; <ins><code>372</code></ins> (New)
### dyewhite
- `\*ID`: <del><code>364</code></del> (Old) &rarr; <ins><code>371</code></ins> (New)
### firemindam
- `1\.09\-Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### hpregen
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
### item\_allskills
- `descpriority`: <del><code>158</code></del> (Old) &rarr; <ins><code>156</code></ins> (New)
### item\_attackertakesdamage
- `1\.09\-Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
### item\_aura
- `descpriority`: <del><code>159</code></del> (Old) &rarr; <ins><code>157</code></ins> (New)
### item\_charge\_noconsume
- `descpriority`: <del><code>159</code></del> (Old) &rarr; <ins><code>157</code></ins> (New)
### item\_kickdamage
- `1\.09\-Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
- `Save Bits`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
### item\_nonclassskill
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
### item\_pierce
- `Multiply`: <del><code>0</code></del> (Old) &rarr; <ins><code>2048</code></ins> (New)
### item\_singleskill
- `Save Bits`: <del><code>3</code></del> (Old) &rarr; <ins><code>4</code></ins> (New)
### item\_skillonattack
- `descpriority`: <del><code>160</code></del> (Old) &rarr; <ins><code>158</code></ins> (New)
### item\_skillondeath
- `descpriority`: <del><code>160</code></del> (Old) &rarr; <ins><code>158</code></ins> (New)
### item\_skillongethit
- `descpriority`: <del><code>160</code></del> (Old) &rarr; <ins><code>158</code></ins> (New)
### item\_skillonhit
- `descpriority`: <del><code>160</code></del> (Old) &rarr; <ins><code>158</code></ins> (New)
### item\_skillonkill
- `descpriority`: <del><code>160</code></del> (Old) &rarr; <ins><code>158</code></ins> (New)
### item\_skillonlevelup
- `descpriority`: <del><code>160</code></del> (Old) &rarr; <ins><code>158</code></ins> (New)
### lightmindam
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### magicmindam
- `1\.09\-Save Bits`: <del><code>6</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
- `Save Bits`: <del><code>8</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### passive\_mag\_mastery
- `descstrpos`: <del><code>ModitemdamMagsk</code></del> (Old) &rarr; <ins><code>ModStrMagMastery</code></ins> (New)
- `descstrneg`: <del><code>ModitemdamMagsk</code></del> (Old) &rarr; <ins><code>ModStrMagMastery</code></ins> (New)
### passive\_mag\_pierce
- `descstrpos`: <del><code>ModitemenresMagsk</code></del> (Old) &rarr; <ins><code>ModStrMagPierce</code></ins> (New)
- `descstrneg`: <del><code>ModitemenresMagsk</code></del> (Old) &rarr; <ins><code>ModStrMagPierce</code></ins> (New)
### passive\_mastery\_replenish\_oncrit
- `\*ID`: <del><code>206</code></del> (Old) &rarr; <ins><code>207</code></ins> (New)
### skill\_cooldown
- `Send Bits`: <del><code>32</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `Send Param Bits`: <del><code>16</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
