# Differences for skills.txt

*Key column used: `skill`*

## Added Columns: `auraevent4, auraeventfunc4, requirespettype, requiresweapon, periodicClearAura, calc7, \*calc7desc, calc8, \*calc8desc, calc9, \*calc9desc, calc10, \*calc10desc, Param13, \*Param13Description, Param14, \*Param14Description, Param15, \*Param15Description, Param16, \*Param16Description, Param17, \*Param17Description, Param18, \*Param18Description, Param19, \*Param19Description, Param20, \*Param20Description`  

## Added Rows (57)
- abyss
- apocalypse
- bind demon
- blade warp
- blood boil
- blood oath
- charged bolt disk
- cleave
- cold enchant
- cold fissure
- colossal thunder storm
- colossal volcano
- consume
- death mark
- demonic mastery
- echoing strike
- eldritch blast
- engorge
- enhanced entropy
- fire twisters
- flame wave
- goatman berserk
- goatman cleave
- goatman frenzy
- goatman stun
- health link
- heraldthorns
- hex bane
- hex purge
- hex purge explosion
- hex siphon
- korlic's bash
- korlic's cold pierce
- korlic's leap attack
- levitate
- lightning enchant
- madawc's lightning pierce
- miasma bolt
- miasma chains
- mirrored blades
- psychic ward
- ring of fire
- sigil death
- sigil death explosion
- sigil lethargy
- sigil rancor
- summon defiler
- summon goatman
- summon tainted
- tainted fire ball
- tainted fire bolt
- tainted resist fire
- talic's fire pierce
- talic's whirlwind
- townportal o skill
- uberancientsheal
- unused0001
## Removed Rows (2)
- frostnovanew
- magic pierce
## Modified Rows (57)
### berserk
- `Param1`: <del><code>150</code></del> (Old) &rarr; <ins><code>500</code></ins> (New)
### blade sentinel
- `passivecalc6`: <code>stat('itempiercecoldimmunity'.accr</code> (Old) &rarr; <code>stat('itempiercecoldimmunity'.accr</code><ins><code>)</code></ins> (New)
### blizzard
- `Param3`: <del><code>4</code></del> (Old) &rarr; <ins><code>2</code></ins> (New)
### bloodgolem
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_damage_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_damage_immunity'.accr)</code></ins> (New)
- `sumskill1`:  (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk1calc`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### bloodlordfrenzy
- `srvstfunc`: <del><code>64</code></del> (Old) &rarr; <ins><code>67</code></ins> (New)
- `srvdofunc`: <del><code>109</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### bone spear
- `mana`: <del><code>16</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
- `calc1`: <code>min(</code><del><code>3</code></del><code>,</code><code>1</code><code>+</code><code>skill('Bone Spear'.blvl)/10</code> (Old) &rarr; <code>min(</code><ins><code>5</code></ins><code>,</code><ins><code> </code></ins><code>1</code><ins><code> </code></ins><code>+</code><ins><code> </code></ins><code>skill('Bone Spear'.blvl)/10</code><ins><code>) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)</code></ins> (New)
### clay golem
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_damage_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_damage_immunity'.accr)</code></ins> (New)
- `sumskill1`:  (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk1calc`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### cold mastery
- `Param2`: <del><code>2</code></del> (Old) &rarr; <ins><code>5</code></ins> (New)
### death sentry
- `passivestat6`:  (Old) &rarr; <ins><code>passive_ltng_mastery</code></ins> (New)
- `passivecalc6`:  (Old) &rarr; <ins><code>stat('passive_ltng_mastery'.accr)</code></ins> (New)
- `passivestat7`:  (Old) &rarr; <ins><code>passive_fire_mastery</code></ins> (New)
- `passivecalc7`:  (Old) &rarr; <ins><code>stat('passive_fire_mastery'.accr)</code></ins> (New)
### decrepify
- `Param1`: <del><code>6</code></del> (Old) &rarr; <ins><code>3</code></ins> (New)
- `Param2`: <del><code>0</code></del> (Old) &rarr; <ins><code>1</code></ins> (New)
### double throw
- `Param1`: <del><code>20</code></del> (Old) &rarr; <ins><code>40</code></ins> (New)
### dragon claw
- `Param1`: <del><code>50</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
- `Param2`: <del><code>15</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
- `Param7`: <del><code>4</code></del> (Old) &rarr; <ins><code>5</code></ins> (New)
### eruption
- `Param8`: <del><code>15</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
### fire ball
- `calc1`: <code>min(</code><del><code>3</code></del><code>,1+skill('Fire Ball'.blvl)/</code><del><code>10</code></del> (Old) &rarr; <code>min(</code><ins><code>5</code></ins><code>,1+skill('Fire Ball'.blvl)/</code><ins><code>5</code></ins> (New)
### fire wall
- `Param7`: <del><code>3</code></del> (Old) &rarr; <ins><code>5</code></ins> (New)
- `EDmgSymPerCalc`: <code>(skill('Warmth'.blvl)*par8+skill('</code><del><code>Inferno</code></del><code>'.blvl)*par7</code> (Old) &rarr; <code>(skill('Warmth'.blvl)*par8+skill('</code><ins><code>Blaze</code></ins><code>'.blvl)*par7</code> (New)
### firegolem
- `passivestat4`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
- `passivecalc4`:  (Old) &rarr; <ins><code>stat('item_pierce_fire_immunity'.accr)</code></ins> (New)
### freezing arrow
- `Param8`: <del><code>4</code></del> (Old) &rarr; <ins><code>3</code></ins> (New)
### frenzy
- `auralencalc`: <code>par7+skill('Increased </code><del><code>Stamina</code></del><code>'.blvl)*10</code> (Old) &rarr; <code>par7+skill('Increased </code><ins><code>Endurance</code></ins><code>'.blvl)*10</code> (New)
- `Param1`: <del><code>90</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
- `Param2`: <del><code>5</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Param8`: <del><code>8</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
### frost nova
- `Param8`: <del><code>20</code></del> (Old) &rarr; <ins><code>22</code></ins> (New)
### frozen orb
- `Param8`: <del><code>2</code></del> (Old) &rarr; <ins><code>1</code></ins> (New)
- `EDmgSymPerCalc`: <code>(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('</code><del><code>Glacial</code></del><code> </code><del><code>Spike</code></del><code>'.blvl))*par8</code> (Old) &rarr; <code>(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('</code><ins><code>Frost</code></ins><code> </code><ins><code>Nova</code></ins><code>'.blvl))*par8</code> (New)
### glacial spike
- `srvdofunc`:  (Old) &rarr; <ins><code>8</code></ins> (New)
- `srvmissile`: <del><code>glacialspike</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `srvmissilea`:  (Old) &rarr; <ins><code>glacialspike</code></ins> (New)
- `srvmissileb`:  (Old) &rarr; <ins><code>glacialspike</code></ins> (New)
- `cltdofunc`:  (Old) &rarr; <ins><code>17</code></ins> (New)
- `cltmissile`: <del><code>glacialspike</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `cltmissilea`:  (Old) &rarr; <ins><code>glacialspike</code></ins> (New)
- `cltmissileb`:  (Old) &rarr; <ins><code>glacialspike</code></ins> (New)
- `calc1`:  (Old) &rarr; <ins><code>min(5,1+skill('Glacial Spike'.blvl)/5</code></ins> (New)
- `\*calc1 desc`:  (Old) &rarr; <ins><code># of Missiles created</code></ins> (New)
- `calc2`:  (Old) &rarr; <ins><code>1</code></ins> (New)
- `\*calc2 desc`:  (Old) &rarr; <ins><code>Missile Activation Frame</code></ins> (New)
- `calc3`:  (Old) &rarr; <ins><code>0</code></ins> (New)
- `Param5`:  (Old) &rarr; <ins><code>2</code></ins> (New)
- `\*Param5 Description`:  (Old) &rarr; <ins><code># of Missiles created baseline</code></ins> (New)
- `Param6`:  (Old) &rarr; <ins><code>1</code></ins> (New)
- `\*Param6 Description`:  (Old) &rarr; <ins><code># of Missiles created per level</code></ins> (New)
- `EDmgSymPerCalc`: <code>(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('</code><del><code>Frozen Orb</code></del><code>'.blvl))*par8</code> (Old) &rarr; <code>(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('</code><ins><code>Blizzard</code></ins><code>'.blvl))*par8</code> (New)
### holy bolt
- `Param8`: <del><code>20</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
### hurricane
- `Param3`: <del><code>15</code></del> (Old) &rarr; <ins><code>12</code></ins> (New)
- `Param4`: <del><code>1</code></del> (Old) &rarr; <ins><code>2</code></ins> (New)
- `Param8`: <del><code>10</code></del> (Old) &rarr; <ins><code>2</code></ins> (New)
- `EDmgSymPerCalc`: <code>skill('Cyclone Armor'.blvl)</code><code>*par8</code> (Old) &rarr; <ins><code>(</code></ins><code>skill('Cyclone Armor'.blvl)</code><ins><code>+skill('Twister'.blvl)+skill('Tornado'.blvl)+skill('Oak Sage'.blvl))</code></ins><code>*par8</code> (New)
### hydra
- `passivestat3`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
- `passivecalc3`:  (Old) &rarr; <ins><code>stat('item_pierce_fire_immunity'.accr)</code></ins> (New)
### ice blast
- `EDmgSymPerCalc`: <code>(skill('Ice Bolt'.blvl)+skill('</code><del><code>Blizzard</code></del><code>'.blvl)+skill('</code><del><code>Frozen Orb</code></del><code>'.blvl))*par8</code> (Old) &rarr; <code>(skill('Ice Bolt'.blvl)+skill('</code><ins><code>Glacial Spike</code></ins><code>'.blvl)+skill('</code><ins><code>Blizzard</code></ins><code>'.blvl))*par8</code> (New)
### immolation arrow
- `Param8`: <del><code>8</code></del> (Old) &rarr; <ins><code>5</code></ins> (New)
### increased endurance
- `passivestate`: <del><code>increasedstamina</code></del> (Old) &rarr; <ins><code>increasedendurance</code></ins> (New)
### increased speed
- `reqskill1`: <code>Increased </code><del><code>Stamina</code></del> (Old) &rarr; <code>Increased </code><ins><code>Endurance</code></ins> (New)
### irongolem
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_cold_immunity'.accr)</code></ins> (New)
- `passivestat6`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
- `sumskill1`:  (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk1calc`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### lightning
- `Param8`: <del><code>8</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
### magic conviction
- `\*Id`: <del><code>376</code></del> (Old) &rarr; <ins><code>431</code></ins> (New)
- `aurastatcalc1`: <code>-</code><code>(</code><del><code>lvl*5+15</code></del><code>)</code><del><code>-stat('passivemagpierce'.accr)</code></del> (Old) &rarr; <code>-</code><ins><code>min</code></ins><code>(</code><ins><code>ln34,150</code></ins><code>)</code> (New)
- `Param3`: <del><code>0</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
- `Param4`: <del><code>0</code></del> (Old) &rarr; <ins><code>5</code></ins> (New)
### meteor
- `Param1`: <del><code>6</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
- `Param4`: <del><code>15</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `Param8`: <del><code>5</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
### monfrenzy
- `srvstfunc`: <del><code>64</code></del> (Old) &rarr; <ins><code>67</code></ins> (New)
- `srvdofunc`: <del><code>109</code></del> (Old) &rarr; <ins><code>9</code></ins> (New)
### multiple shot
- `Param4`: <del><code>10</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
### nova
- `Param8`: <del><code>5</code></del> (Old) &rarr; <ins><code>4</code></ins> (New)
### plague poppy
- `passivestat1`:  (Old) &rarr; <ins><code>item_pierce_poison_immunity</code></ins> (New)
- `passivecalc1`:  (Old) &rarr; <ins><code>stat('item_pierce_poison_immunity'.accr)</code></ins> (New)
### poison dagger
- `srvmissile`:  (Old) &rarr; <ins><code>poisondagger</code></ins> (New)
- `cltmissile`:  (Old) &rarr; <ins><code>poisondagger</code></ins> (New)
- `itypea1`: <del><code>knif</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `manashift`: <del><code>6</code></del> (Old) &rarr; <ins><code>4</code></ins> (New)
- `mana`: <del><code>10</code></del> (Old) &rarr; <ins><code>40</code></ins> (New)
- `lvlmana`: <del><code>-1</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
### raise skeletal mage
- `passivestat2`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `passivecalc2`:  (Old) &rarr; <ins><code>stat('item_pierce_cold_immunity'.accr)</code></ins> (New)
- `passivestat3`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
- `passivecalc3`:  (Old) &rarr; <ins><code>stat('item_pierce_fire_immunity'.accr)</code></ins> (New)
- `passivestat4`:  (Old) &rarr; <ins><code>item_pierce_light_immunity</code></ins> (New)
- `passivecalc4`:  (Old) &rarr; <ins><code>stat('item_pierce_light_immunity'.accr)</code></ins> (New)
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_poison_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_poison_immunity'.accr)</code></ins> (New)
### raise skeleton
- `passivestat3`:  (Old) &rarr; <ins><code>item_pierce_damage_immunity</code></ins> (New)
- `passivecalc3`:  (Old) &rarr; <ins><code>stat('item_pierce_damage_immunity'.accr)</code></ins> (New)
- `sumskill1`:  (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk1calc`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### raven
- `passivestat6`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `sumskill1`:  (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk1calc`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### revive
- `passivestat2`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `passivecalc2`:  (Old) &rarr; <ins><code>stat('item_pierce_cold_immunity'.accr)</code></ins> (New)
- `passivestat3`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
- `passivecalc3`:  (Old) &rarr; <ins><code>stat('item_pierce_fire_immunity'.accr)</code></ins> (New)
- `passivestat4`:  (Old) &rarr; <ins><code>item_pierce_light_immunity</code></ins> (New)
- `passivecalc4`:  (Old) &rarr; <ins><code>stat('item_pierce_light_immunity'.accr)</code></ins> (New)
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_poison_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_poison_immunity'.accr)</code></ins> (New)
- `passivestat6`:  (Old) &rarr; <ins><code>item_pierce_damage_immunity</code></ins> (New)
### shadow master
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_cold_immunity'.accr)</code></ins> (New)
- `passivestat6`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
### shadow warrior
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_cold_immunity'.accr)</code></ins> (New)
- `passivestat6`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
### shout
- `Param1`: <del><code>100</code></del> (Old) &rarr; <ins><code>200</code></ins> (New)
### splash
- `\*Id`: <del><code>375</code></del> (Old) &rarr; <ins><code>430</code></ins> (New)
### summon fenris
- `passivestat4`:  (Old) &rarr; <ins><code>item_pierce_damage_immunity</code></ins> (New)
- `passivecalc4`:  (Old) &rarr; <ins><code>stat('item_pierce_damage_immunity'.accr)</code></ins> (New)
- `sumskill1`:  (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk1calc`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### summon grizzly
- `passivestat4`:  (Old) &rarr; <ins><code>item_pierce_damage_immunity</code></ins> (New)
- `passivecalc4`:  (Old) &rarr; <ins><code>stat('item_pierce_damage_immunity'.accr)</code></ins> (New)
### summon spirit wolf
- `passivestat6`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `sumskill1`: <del><code>Thorns</code></del> (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk1calc`: <del><code>lvl</code></del> (Old) &rarr; <ins><code>1</code></ins> (New)
- `sumskill2`:  (Old) &rarr; <ins><code>Thorns</code></ins> (New)
- `sumsk2calc`:  (Old) &rarr; <ins><code>lvl</code></ins> (New)
### summon splash
- `\*Id`: <del><code>378</code></del> (Old) &rarr; <ins><code>432</code></ins> (New)
### teeth
- `manashift`: <del><code>7</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
- `mana`: <del><code>5</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `lvlmana`: <del><code>1</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `Param1`: <del><code>2</code></del> (Old) &rarr; <ins><code>3</code></ins> (New)
- `EMinLev1`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMinLev2`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMinLev3`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMinLev4`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMinLev5`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMaxLev1`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMaxLev2`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMaxLev3`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMaxLev4`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
- `EMaxLev5`: <del><code>4</code></del> (Old) &rarr; <ins><code>6</code></ins> (New)
### thorns
- `Param3`: <del><code>250</code></del> (Old) &rarr; <ins><code>500</code></ins> (New)
- `Param4`: <del><code>40</code></del> (Old) &rarr; <ins><code>30</code></ins> (New)
- `EMin`: <del><code>4</code></del> (Old) &rarr; <ins><code>5</code></ins> (New)
- `EMinLev1`: <del><code>4</code></del> (Old) &rarr; <ins><code>5</code></ins> (New)
- `EMinLev2`: <del><code>8</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `EMinLev3`: <del><code>12</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
- `EMinLev4`: <del><code>16</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
- `EMinLev5`: <del><code>20</code></del> (Old) &rarr; <ins><code>25</code></ins> (New)
### throwing mastery
- `Param3`: <del><code>32</code></del> (Old) &rarr; <ins><code>40</code></ins> (New)
- `Param5`: <del><code>0</code></del> (Old) &rarr; <ins><code>1</code></ins> (New)
- `Param6`: <del><code>40</code></del> (Old) &rarr; <ins><code>50</code></ins> (New)
### valkyrie
- `passivestat3`:  (Old) &rarr; <ins><code>item_pierce_cold_immunity</code></ins> (New)
- `passivecalc3`:  (Old) &rarr; <ins><code>stat('item_pierce_cold_immunity'.accr)</code></ins> (New)
- `passivestat4`:  (Old) &rarr; <ins><code>item_pierce_fire_immunity</code></ins> (New)
- `passivecalc4`:  (Old) &rarr; <ins><code>stat('item_pierce_fire_immunity'.accr)</code></ins> (New)
- `passivestat5`:  (Old) &rarr; <ins><code>item_pierce_light_immunity</code></ins> (New)
- `passivecalc5`:  (Old) &rarr; <ins><code>stat('item_pierce_light_immunity'.accr)</code></ins> (New)
- `passivestat6`:  (Old) &rarr; <ins><code>item_pierce_poison_immunity</code></ins> (New)
- `sumskill5`:  (Old) &rarr; <ins><code>Summon Splash</code></ins> (New)
- `sumsk5calc`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### vengeance
- `\*Id`: <del><code>374</code></del> (Old) &rarr; <ins><code>111</code></ins> (New)
- `charclass`:  (Old) &rarr; <ins><code>pal</code></ins> (New)
- `srvstfunc`: <del><code>37</code></del> (Old) &rarr; <ins><code>35</code></ins> (New)
- `srvdofunc`: <del><code>13</code></del> (Old) &rarr; <ins><code>2</code></ins> (New)
- `cltstfunc`: <del><code>53</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `cltdofunc`: <del><code>21</code></del> (Old) &rarr; <ins><code>34</code></ins> (New)
- `calc4`: <del><code>"min((par5 + lvl -1), par6)"</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `\*calc4 desc`: <del><code># of hits</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `Param1`: <del><code>100</code></del> (Old) &rarr; <ins><code>500</code></ins> (New)
- `Param2`: <del><code>10</code></del> (Old) &rarr; <ins><code>25</code></ins> (New)
- `Param3`: <del><code>100</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `\*Param3 Description`: <del><code>% Anim frame rollback</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `Param5`: <del><code>3</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `\*Param5 Description`: <del><code># of hits Min</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `Param6`: <del><code>3</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `\*Param6 Description`: <del><code># of hits Max</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `Param7`: <del><code>5</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
- `Param8`: <del><code>15</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
### war cry
- `DmgSymPerCalc`: <code>(skill('</code><del><code>Howl</code></del><code>'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8</code> (Old) &rarr; <code>(skill('</code><ins><code>Battle Orders</code></ins><code>'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8</code> (New)
### wearwolf
- `Param1`: <del><code>25</code></del> (Old) &rarr; <ins><code>100</code></ins> (New)
### zeal
- `Param3`: <del><code>0</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `Param4`: <del><code>6</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
