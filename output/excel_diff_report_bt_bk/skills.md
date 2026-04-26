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
- `Param1`: <strong><code>150</code></strong> (Old) &rarr; <strong><code>500</code></strong> (New)
### blade sentinel
- `passivecalc6`: <strong><code>stat('item_pierce_cold_immunity'.accr</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_cold_immunity'.accr)</code></strong> (New)
### blizzard
- `Param3`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>2</code></strong> (New)
### bloodgolem
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_damage_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_damage_immunity'.accr)</code></strong> (New)
- `sumskill1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk1calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### bloodlordfrenzy
- `srvstfunc`: <strong><code>64</code></strong> (Old) &rarr; <strong><code>67</code></strong> (New)
- `srvdofunc`: <strong><code>109</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
### bone spear
- `mana`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
- `calc1`: <strong><code>min(3,1+skill('Bone Spear'.blvl)/10</code></strong> (Old) &rarr; <strong><code>min(5, 1 + skill('Bone Spear'.blvl)/10) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)</code></strong> (New)
### clay golem
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_damage_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_damage_immunity'.accr)</code></strong> (New)
- `sumskill1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk1calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### cold mastery
- `Param2`: <strong><code>2</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
### death sentry
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>passive_ltng_mastery</code></strong> (New)
- `passivecalc6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('passive_ltng_mastery'.accr)</code></strong> (New)
- `passivestat7`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>passive_fire_mastery</code></strong> (New)
- `passivecalc7`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('passive_fire_mastery'.accr)</code></strong> (New)
### decrepify
- `Param1`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>3</code></strong> (New)
- `Param2`: <strong><code>0</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### double throw
- `Param1`: <strong><code>20</code></strong> (Old) &rarr; <strong><code>40</code></strong> (New)
### dragon claw
- `Param1`: <strong><code>50</code></strong> (Old) &rarr; <strong><code>100</code></strong> (New)
- `Param2`: <strong><code>15</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
- `Param7`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
### eruption
- `Param8`: <strong><code>15</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### fire ball
- `calc1`: <strong><code>min(3,1+skill('Fire Ball'.blvl)/10</code></strong> (Old) &rarr; <strong><code>min(5,1+skill('Fire Ball'.blvl)/5</code></strong> (New)
### fire wall
- `Param7`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
- `EDmgSymPerCalc`: <strong><code>(skill('Warmth'.blvl)*par8+skill('Inferno'.blvl)*par7</code></strong> (Old) &rarr; <strong><code>(skill('Warmth'.blvl)*par8+skill('Blaze'.blvl)*par7</code></strong> (New)
### firegolem
- `passivestat4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
- `passivecalc4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_fire_immunity'.accr)</code></strong> (New)
### freezing arrow
- `Param8`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>3</code></strong> (New)
### frenzy
- `auralencalc`: <strong><code>par7+skill('Increased Stamina'.blvl)*10</code></strong> (Old) &rarr; <strong><code>par7+skill('Increased Endurance'.blvl)*10</code></strong> (New)
- `Param1`: <strong><code>90</code></strong> (Old) &rarr; <strong><code>100</code></strong> (New)
- `Param2`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
- `Param8`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
### frost nova
- `Param8`: <strong><code>20</code></strong> (Old) &rarr; <strong><code>22</code></strong> (New)
### frozen orb
- `Param8`: <strong><code>2</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `EDmgSymPerCalc`: <strong><code>(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('Glacial Spike'.blvl))*par8</code></strong> (Old) &rarr; <strong><code>(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('Frost Nova'.blvl))*par8</code></strong> (New)
### glacial spike
- `srvdofunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
- `srvmissile`: <strong><code>glacialspike</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `srvmissilea`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>glacialspike</code></strong> (New)
- `srvmissileb`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>glacialspike</code></strong> (New)
- `cltdofunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>17</code></strong> (New)
- `cltmissile`: <strong><code>glacialspike</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `cltmissilea`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>glacialspike</code></strong> (New)
- `cltmissileb`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>glacialspike</code></strong> (New)
- `calc1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>min(5,1+skill('Glacial Spike'.blvl)/5</code></strong> (New)
- `\*calc1 desc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code># of Missiles created</code></strong> (New)
- `calc2`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `\*calc2 desc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Missile Activation Frame</code></strong> (New)
- `calc3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `Param5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>2</code></strong> (New)
- `\*Param5 Description`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code># of Missiles created baseline</code></strong> (New)
- `Param6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `\*Param6 Description`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code># of Missiles created per level</code></strong> (New)
- `EDmgSymPerCalc`: <strong><code>(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('Frozen Orb'.blvl))*par8</code></strong> (Old) &rarr; <strong><code>(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('Blizzard'.blvl))*par8</code></strong> (New)
### holy bolt
- `Param8`: <strong><code>20</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
### hurricane
- `Param3`: <strong><code>15</code></strong> (Old) &rarr; <strong><code>12</code></strong> (New)
- `Param4`: <strong><code>1</code></strong> (Old) &rarr; <strong><code>2</code></strong> (New)
- `Param8`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>2</code></strong> (New)
- `EDmgSymPerCalc`: <strong><code>skill('Cyclone Armor'.blvl)*par8</code></strong> (Old) &rarr; <strong><code>(skill('Cyclone Armor'.blvl)+skill('Twister'.blvl)+skill('Tornado'.blvl)+skill('Oak Sage'.blvl))*par8</code></strong> (New)
### hydra
- `passivestat3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
- `passivecalc3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_fire_immunity'.accr)</code></strong> (New)
### ice blast
- `EDmgSymPerCalc`: <strong><code>(skill('Ice Bolt'.blvl)+skill('Blizzard'.blvl)+skill('Frozen Orb'.blvl))*par8</code></strong> (Old) &rarr; <strong><code>(skill('Ice Bolt'.blvl)+skill('Glacial Spike'.blvl)+skill('Blizzard'.blvl))*par8</code></strong> (New)
### immolation arrow
- `Param8`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
### increased endurance
- `passivestate`: <strong><code>increasedstamina</code></strong> (Old) &rarr; <strong><code>increasedendurance</code></strong> (New)
### increased speed
- `reqskill1`: <strong><code>Increased Stamina</code></strong> (Old) &rarr; <strong><code>Increased Endurance</code></strong> (New)
### irongolem
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_cold_immunity'.accr)</code></strong> (New)
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
- `sumskill1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk1calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### lightning
- `Param8`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### magic conviction
- `\*Id`: <strong><code>376</code></strong> (Old) &rarr; <strong><code>431</code></strong> (New)
- `aurastatcalc1`: <strong><code>-(lvl*5+15)-stat('passive_mag_pierce'.accr)</code></strong> (Old) &rarr; <strong><code>-min(ln34,150)</code></strong> (New)
- `Param3`: <strong><code>0</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
- `Param4`: <strong><code>0</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
### meteor
- `Param1`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
- `Param4`: <strong><code>15</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `Param8`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
### monfrenzy
- `srvstfunc`: <strong><code>64</code></strong> (Old) &rarr; <strong><code>67</code></strong> (New)
- `srvdofunc`: <strong><code>109</code></strong> (Old) &rarr; <strong><code>9</code></strong> (New)
### multiple shot
- `Param4`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
### nova
- `Param8`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>4</code></strong> (New)
### plague poppy
- `passivestat1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_poison_immunity</code></strong> (New)
- `passivecalc1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_poison_immunity'.accr)</code></strong> (New)
### poison dagger
- `srvmissile`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>poisondagger</code></strong> (New)
- `cltmissile`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>poisondagger</code></strong> (New)
- `itypea1`: <strong><code>knif</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `manashift`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>4</code></strong> (New)
- `mana`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>40</code></strong> (New)
- `lvlmana`: <strong><code>-1</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### raise skeletal mage
- `passivestat2`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `passivecalc2`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_cold_immunity'.accr)</code></strong> (New)
- `passivestat3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
- `passivecalc3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_fire_immunity'.accr)</code></strong> (New)
- `passivestat4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_light_immunity</code></strong> (New)
- `passivecalc4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_light_immunity'.accr)</code></strong> (New)
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_poison_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_poison_immunity'.accr)</code></strong> (New)
### raise skeleton
- `passivestat3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_damage_immunity</code></strong> (New)
- `passivecalc3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_damage_immunity'.accr)</code></strong> (New)
- `sumskill1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk1calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### raven
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `sumskill1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk1calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### revive
- `passivestat2`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `passivecalc2`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_cold_immunity'.accr)</code></strong> (New)
- `passivestat3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
- `passivecalc3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_fire_immunity'.accr)</code></strong> (New)
- `passivestat4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_light_immunity</code></strong> (New)
- `passivecalc4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_light_immunity'.accr)</code></strong> (New)
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_poison_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_poison_immunity'.accr)</code></strong> (New)
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_damage_immunity</code></strong> (New)
### shadow master
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_cold_immunity'.accr)</code></strong> (New)
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
### shadow warrior
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_cold_immunity'.accr)</code></strong> (New)
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
### shout
- `Param1`: <strong><code>100</code></strong> (Old) &rarr; <strong><code>200</code></strong> (New)
### splash
- `\*Id`: <strong><code>375</code></strong> (Old) &rarr; <strong><code>430</code></strong> (New)
### summon fenris
- `passivestat4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_damage_immunity</code></strong> (New)
- `passivecalc4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_damage_immunity'.accr)</code></strong> (New)
- `sumskill1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk1calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### summon grizzly
- `passivestat4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_damage_immunity</code></strong> (New)
- `passivecalc4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_damage_immunity'.accr)</code></strong> (New)
### summon spirit wolf
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `sumskill1`: <strong><code>Thorns</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk1calc`: <strong><code>lvl</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `sumskill2`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Thorns</code></strong> (New)
- `sumsk2calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>lvl</code></strong> (New)
### summon splash
- `\*Id`: <strong><code>378</code></strong> (Old) &rarr; <strong><code>432</code></strong> (New)
### teeth
- `manashift`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
- `mana`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `lvlmana`: <strong><code>1</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `Param1`: <strong><code>2</code></strong> (Old) &rarr; <strong><code>3</code></strong> (New)
- `EMinLev1`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMinLev2`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMinLev3`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMinLev4`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMinLev5`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMaxLev1`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMaxLev2`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMaxLev3`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMaxLev4`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
- `EMaxLev5`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
### thorns
- `Param3`: <strong><code>250</code></strong> (Old) &rarr; <strong><code>500</code></strong> (New)
- `Param4`: <strong><code>40</code></strong> (Old) &rarr; <strong><code>30</code></strong> (New)
- `EMin`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
- `EMinLev1`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
- `EMinLev2`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
- `EMinLev3`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
- `EMinLev4`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
- `EMinLev5`: <strong><code>20</code></strong> (Old) &rarr; <strong><code>25</code></strong> (New)
### throwing mastery
- `Param3`: <strong><code>32</code></strong> (Old) &rarr; <strong><code>40</code></strong> (New)
- `Param5`: <strong><code>0</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `Param6`: <strong><code>40</code></strong> (Old) &rarr; <strong><code>50</code></strong> (New)
### valkyrie
- `passivestat3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_cold_immunity</code></strong> (New)
- `passivecalc3`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_cold_immunity'.accr)</code></strong> (New)
- `passivestat4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_fire_immunity</code></strong> (New)
- `passivecalc4`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_fire_immunity'.accr)</code></strong> (New)
- `passivestat5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_light_immunity</code></strong> (New)
- `passivecalc5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>stat('item_pierce_light_immunity'.accr)</code></strong> (New)
- `passivestat6`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>item_pierce_poison_immunity</code></strong> (New)
- `sumskill5`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>Summon Splash</code></strong> (New)
- `sumsk5calc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### vengeance
- `\*Id`: <strong><code>374</code></strong> (Old) &rarr; <strong><code>111</code></strong> (New)
- `charclass`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>pal</code></strong> (New)
- `srvstfunc`: <strong><code>37</code></strong> (Old) &rarr; <strong><code>35</code></strong> (New)
- `srvdofunc`: <strong><code>13</code></strong> (Old) &rarr; <strong><code>2</code></strong> (New)
- `cltstfunc`: <strong><code>53</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `cltdofunc`: <strong><code>21</code></strong> (Old) &rarr; <strong><code>34</code></strong> (New)
- `calc4`: <strong><code>"min((par5 + lvl -1), par6)"</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `\*calc4 desc`: <strong><code># of hits</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `Param1`: <strong><code>100</code></strong> (Old) &rarr; <strong><code>500</code></strong> (New)
- `Param2`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>25</code></strong> (New)
- `Param3`: <strong><code>100</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `\*Param3 Description`: <strong><code>% Anim frame rollback</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `Param5`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `\*Param5 Description`: <strong><code># of hits Min</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `Param6`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `\*Param6 Description`: <strong><code># of hits Max</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `Param7`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
- `Param8`: <strong><code>15</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
### war cry
- `DmgSymPerCalc`: <strong><code>(skill('Howl'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8</code></strong> (Old) &rarr; <strong><code>(skill('Battle Orders'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8</code></strong> (New)
### wearwolf
- `Param1`: <strong><code>25</code></strong> (Old) &rarr; <strong><code>100</code></strong> (New)
### zeal
- `Param3`: <strong><code>0</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
- `Param4`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
