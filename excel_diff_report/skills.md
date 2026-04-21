# Differences for skills.txt

*Key column used: `skill`*

## Added Columns in BK (New)
`auraevent4, auraeventfunc4, requirespettype, requiresweapon, periodicClearAura, calc7, *calc7desc, calc8, *calc8desc, calc9, *calc9desc, calc10, *calc10desc, Param13, *Param13Description, Param14, *Param14Description, Param15, *Param15Description, Param16, *Param16Description, Param17, *Param17Description, Param18, *Param18Description, Param19, *Param19Description, Param20, *Param20Description`  

## Added Rows in BK (New) (57)
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

## Removed Rows in BK (New) (2)
- frostnovanew
- magic pierce

## Modified Rows (88)
### amplify damage
- `AttackNoMana`: ` ` (Old) &rarr; **`*empty*` (New)**

### baal inferno
- `*calc1 desc`: `"Missile Range (If 0, then use Missile Param2)"` (Old) &rarr; **`Missile Range (If 0, then use Missile Param2)` (New)**

### baal taunt
- `*calc1 desc`: `Delay in lightning ` (Old) &rarr; **`Delay in lightning` (New)**
- `*Param2 Description`: `Delay in lightning ` (Old) &rarr; **`Delay in lightning` (New)**

### bearsmite
- `calc2`: `"max(250,ln12)"` (Old) &rarr; **`max(250,ln12)` (New)**

### berserk
- `calc2`: `"par4-min(((110*lvl)/(lvl+6)*(par4-par3)/100),(par4-par3))"` (Old) &rarr; **`par4-min(((110*lvl)/(lvl+6)*(par4-par3)/100),(par4-par3))` (New)**

### blade sentinel
- `passivecalc6`: `stat('item_pierce_cold_immunity'.accr` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**

### blizzard
- `Param3`: `4` (Old) &rarr; **`2` (New)**

### blood mana
- `*Param5 Description`: `"Max HP Limit (If target HP reaches this value or lower, then remove the Curse)"` (Old) &rarr; **`Max HP Limit (If target HP reaches this value or lower, then remove the Curse)` (New)**

### bloodgolem
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**
- `sumskill1`: `*empty*` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk1calc`: `*empty*` (Old) &rarr; **`1` (New)**

### bloodlordfrenzy
- `srvstfunc`: `64` (Old) &rarr; **`67` (New)**
- `srvdofunc`: `109` (Old) &rarr; **`9` (New)**

### bone spear
- `mana`: `16` (Old) &rarr; **`15` (New)**
- `calc1`: `min(3,1+skill('Bone Spear'.blvl)/10` (Old) &rarr; **`min(3, 1 + skill('Bone Spear'.blvl)/10) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)` (New)**

### chain lightning
- `*Param5 Description`: `"Every # levels, increase target jump"` (Old) &rarr; **`Every # levels, increase target jump` (New)**

### charged bolt
- `calc1`: `"min(24,ln12)"` (Old) &rarr; **`min(24,ln12)` (New)**

### clay golem
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**
- `sumskill1`: `*empty*` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk1calc`: `*empty*` (Old) &rarr; **`1` (New)**

### cold mastery
- `Param2`: `2` (Old) &rarr; **`5` (New)**

### conversion
- `*Param5 Description`: `"Use sumskill1 on convert expire? (0 = Off | 1 = On) (If 1, then it needs to have ItemEffect=1)"` (Old) &rarr; **`Use sumskill1 on convert expire? (0 = Off | 1 = On) (If 1, then it needs to have ItemEffect=1)` (New)**

### corpse explosion
- `*Param1 Description`: `Damage % of base HP for enemy Min ` (Old) &rarr; **`Damage % of base HP for enemy Min` (New)**

### death sentry
- `passivestat6`: `*empty*` (Old) &rarr; **`passive_ltng_mastery` (New)**
- `passivecalc6`: `*empty*` (Old) &rarr; **`stat('passive_ltng_mastery'.accr)` (New)**
- `passivestat7`: `*empty*` (Old) &rarr; **`passive_fire_mastery` (New)**
- `passivecalc7`: `*empty*` (Old) &rarr; **`stat('passive_fire_mastery'.accr)` (New)**

### decrepify
- `Param1`: `6` (Old) &rarr; **`3` (New)**
- `Param2`: `0` (Old) &rarr; **`1` (New)**

### diablight
- `*calc1 desc`: `"Missile Range (If 0, then use Missile Param2)"` (Old) &rarr; **`Missile Range (If 0, then use Missile Param2)` (New)**

### double throw
- `Param1`: `20` (Old) &rarr; **`40` (New)**

### energy shield
- `calc1`: `"min(edmn,95)"` (Old) &rarr; **`min(edmn,95)` (New)**

### fetishinferno
- `*calc1 desc`: `"Missile Range (If 0, then use Missile Param2)"` (Old) &rarr; **`Missile Range (If 0, then use Missile Param2)` (New)**

### fire trauma
- `Param8`: `18` (Old) &rarr; **`10` (New)**

### fire wall
- `Param7`: `3` (Old) &rarr; **`5` (New)**
- `EDmgSymPerCalc`: `(skill('Warmth'.blvl)*par8+skill('Inferno'.blvl)*par7` (Old) &rarr; **`(skill('Warmth'.blvl)*par8+skill('Blaze'.blvl)*par7` (New)**

### firegolem
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**
- `sumsk1calc`: `"min(ln56,30)"` (Old) &rarr; **`min(ln56,30)` (New)**

### freezing arrow
- `calc1`: `"min(1+(ln12/7),4)"` (Old) &rarr; **`min(1+(ln12/7),4)` (New)**
- `Param8`: `4` (Old) &rarr; **`3` (New)**

### frenzy
- `auralencalc`: `par7+skill('Increased Stamina'.blvl)*10` (Old) &rarr; **`par7+skill('Increased Endurance'.blvl)*10` (New)**
- `Param1`: `90` (Old) &rarr; **`100` (New)**
- `Param2`: `5` (Old) &rarr; **`10` (New)**
- `Param8`: `8` (Old) &rarr; **`15` (New)**

### frost nova
- `Param8`: `20` (Old) &rarr; **`22` (New)**

### frozen orb
- `Param8`: `2` (Old) &rarr; **`1` (New)**
- `EDmgSymPerCalc`: `(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('Glacial Spike'.blvl))*par8` (Old) &rarr; **`(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('Frost Nova'.blvl))*par8` (New)**

### fury
- `calc1`: `"min((par5 + lvl -1), par6)"` (Old) &rarr; **`min((par5 + lvl -1), par6)` (New)**

### glacial spike
- `srvdofunc`: `*empty*` (Old) &rarr; **`8` (New)**
- `srvmissile`: `glacialspike` (Old) &rarr; **`*empty*` (New)**
- `srvmissilea`: `*empty*` (Old) &rarr; **`glacialspike` (New)**
- `srvmissileb`: `*empty*` (Old) &rarr; **`glacialspike` (New)**
- `cltdofunc`: `*empty*` (Old) &rarr; **`17` (New)**
- `cltmissile`: `glacialspike` (Old) &rarr; **`*empty*` (New)**
- `cltmissilea`: `*empty*` (Old) &rarr; **`glacialspike` (New)**
- `cltmissileb`: `*empty*` (Old) &rarr; **`glacialspike` (New)**
- `calc1`: `*empty*` (Old) &rarr; **`min(3,1+skill('Glacial Spike'.blvl)/10` (New)**
- `*calc1 desc`: `*empty*` (Old) &rarr; **`# of Missiles created` (New)**
- `calc2`: `*empty*` (Old) &rarr; **`1` (New)**
- `*calc2 desc`: `*empty*` (Old) &rarr; **`Missile Activation Frame` (New)**
- `calc3`: `*empty*` (Old) &rarr; **`0` (New)**
- `Param5`: `*empty*` (Old) &rarr; **`2` (New)**
- `*Param5 Description`: `*empty*` (Old) &rarr; **`# of Missiles created baseline` (New)**
- `Param6`: `*empty*` (Old) &rarr; **`1` (New)**
- `*Param6 Description`: `*empty*` (Old) &rarr; **`# of Missiles created per level` (New)**
- `EDmgSymPerCalc`: `(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('Frozen Orb'.blvl))*par8` (Old) &rarr; **`(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('Blizzard'.blvl))*par8` (New)**

### holy bolt
- `Param8`: `20` (Old) &rarr; **`15` (New)**

### holy fire
- `*Param6 Description`: `"Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)"` (Old) &rarr; **`Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)` (New)**

### holy freeze
- `*Param6 Description`: `"Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)"` (Old) &rarr; **`Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)` (New)**

### holy shock
- `*Param6 Description`: `"Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)"` (Old) &rarr; **`Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)` (New)**

### horror arctic blast
- `*calc1 desc`: `"Missile Range (If 0, then use Missile Param2)"` (Old) &rarr; **`Missile Range (If 0, then use Missile Param2)` (New)**

### howl
- `*Param1 Description`: `"Missile Velocity baseline (Should match howl Missile Vel value, used for negation)"` (Old) &rarr; **`Missile Velocity baseline (Should match howl Missile Vel value, used for negation)` (New)**

### hurricane
- `Param3`: `15` (Old) &rarr; **`12` (New)**
- `Param4`: `1` (Old) &rarr; **`2` (New)**
- `Param8`: `10` (Old) &rarr; **`2` (New)**
- `EDmgSymPerCalc`: `skill('Cyclone Armor'.blvl)*par8` (Old) &rarr; **`(skill('Cyclone Armor'.blvl)+skill('Twister'.blvl)+skill('Tornado'.blvl)+skill('Oak Sage'.blvl))*par8` (New)**

### hydra
- `passivestat3`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc3`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**
- `Param2`: `25` (Old) &rarr; **`0` (New)**

### ice blast
- `EDmgSymPerCalc`: `(skill('Ice Bolt'.blvl)+skill('Blizzard'.blvl)+skill('Frozen Orb'.blvl))*par8` (Old) &rarr; **`(skill('Ice Bolt'.blvl)+skill('Glacial Spike'.blvl)+skill('Blizzard'.blvl))*par8` (New)**

### immolation arrow
- `Param8`: `8` (Old) &rarr; **`5` (New)**

### imp inferno
- `calc1`: `"rand(par3,par4)"` (Old) &rarr; **`rand(par3,par4)` (New)**

### increased endurance
- `passivestate`: `increasedstamina` (Old) &rarr; **`increasedendurance` (New)**

### increased speed
- `reqskill1`: `Increased Stamina` (Old) &rarr; **`Increased Endurance` (New)**

### irongolem
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `sumskill1`: `*empty*` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk1calc`: `*empty*` (Old) &rarr; **`1` (New)**

### lightning
- `Param8`: `8` (Old) &rarr; **`10` (New)**

### lightning strike
- `cltdofunc`: `  ` (Old) &rarr; **`*empty*` (New)**

### maggotegg
- `scroll`: ` ` (Old) &rarr; **`*empty*` (New)**
- `calc1`: `"(lvl < 5) ? lvl : min(12,5+(lvl-5)/3)"` (Old) &rarr; **`(lvl < 5) ? lvl : min(12,5+(lvl-5)/3)` (New)**

### magic conviction
- `*Id`: `376` (Old) &rarr; **`431` (New)**
- `aurastatcalc1`: `-(lvl*5+15)-stat('passive_mag_pierce'.accr)` (Old) &rarr; **`-min(ln34,150)` (New)**
- `Param3`: `0` (Old) &rarr; **`20` (New)**
- `Param4`: `0` (Old) &rarr; **`5` (New)**

### megademoninferno
- `*calc1 desc`: `"Missile Range (If 0, then use Missile Param2)"` (Old) &rarr; **`Missile Range (If 0, then use Missile Param2)` (New)**

### meteor
- `Param1`: `6` (Old) &rarr; **`7` (New)**
- `Param4`: `15` (Old) &rarr; **`0` (New)**
- `Param8`: `5` (Old) &rarr; **`7` (New)**

### mon death sentry
- `*Param1 Description`: `Damage % of base HP for enemy Min ` (Old) &rarr; **`Damage % of base HP for enemy Min` (New)**

### mon inferno sentry
- `*calc1 desc`: `"Missile Range (If 0, then use Missile Param2)"` (Old) &rarr; **`Missile Range (If 0, then use Missile Param2)` (New)**

### monfrenzy
- `srvstfunc`: `64` (Old) &rarr; **`67` (New)**
- `srvdofunc`: `109` (Old) &rarr; **`9` (New)**

### monholyfreeze
- `*Param6 Description`: `"Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)"` (Old) &rarr; **`Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)` (New)**

### multiple shot
- `calc1`: `"min(ln12,24)"` (Old) &rarr; **`min(ln12,24)` (New)**
- `Param4`: `10` (Old) &rarr; **`8` (New)**

### nihlathakcorpseexplosion
- `*Param1 Description`: `Damage % of base HP for enemy Min ` (Old) &rarr; **`Damage % of base HP for enemy Min` (New)**

### nova
- `Param8`: `5` (Old) &rarr; **`4` (New)**

### penetrate
- `*Param5 Description`: `"Replenish Quantity on crit? (0=disabled, 1=enabled)"` (Old) &rarr; **`Replenish Quantity on crit? (0=disabled, 1=enabled)` (New)**

### plague poppy
- `passivestat1`: `*empty*` (Old) &rarr; **`item_pierce_poison_immunity` (New)**
- `passivecalc1`: `*empty*` (Old) &rarr; **`stat('item_pierce_poison_immunity'.accr)` (New)**

### poison dagger
- `srvmissile`: `*empty*` (Old) &rarr; **`poisondagger` (New)**
- `cltmissile`: `*empty*` (Old) &rarr; **`poisondagger` (New)**
- `itypea1`: `knif` (Old) &rarr; **`*empty*` (New)**
- `manashift`: `6` (Old) &rarr; **`4` (New)**
- `mana`: `10` (Old) &rarr; **`40` (New)**
- `lvlmana`: `-1` (Old) &rarr; **`10` (New)**

### primepoisonball
- `calc1`: `"min(ln12,24)"` (Old) &rarr; **`min(ln12,24)` (New)**

### raise skeletal mage
- `passivestat2`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc2`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat3`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc3`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_light_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_light_immunity'.accr)` (New)**
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_poison_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_poison_immunity'.accr)` (New)**

### raise skeleton
- `passivestat3`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc3`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**
- `sumskill1`: `*empty*` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk1calc`: `*empty*` (Old) &rarr; **`1` (New)**

### raven
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `petmax`: `"min(lvl,par2)"` (Old) &rarr; **`min(lvl,par2)` (New)**
- `sumskill1`: `*empty*` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk1calc`: `*empty*` (Old) &rarr; **`1` (New)**

### revive
- `passivestat2`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc2`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat3`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc3`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_light_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_light_immunity'.accr)` (New)**
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_poison_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_poison_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**

### royal strike
- `*Param6 Description`: `"Chain Lightning Missiles Created Modifier (used as 64/#=Total Chain Lightning Missiles created) (if <=0, then use AuraRangeCalc)"` (Old) &rarr; **`Chain Lightning Missiles Created Modifier (used as 64/#=Total Chain Lightning Missiles created) (if <=0, then use AuraRangeCalc)` (New)**

### sacrifice
- `calc2`: `"max(par6, par5-lvl/par3)"` (Old) &rarr; **`max(par6, par5-lvl/par3)` (New)**

### sanctuary
- `*Param7 Description`: `"Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)"` (Old) &rarr; **`Area Damage % Range Scaling (from 100% to 100+X% damage, based on how close the enemy position is to the caster)` (New)**

### shadow master
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**

### shadow warrior
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**

### shout
- `Param1`: `100` (Old) &rarr; **`200` (New)**

### smite
- `calc2`: `"min(ln12,250)"` (Old) &rarr; **`min(ln12,250)` (New)**

### splash
- `*Id`: `375` (Old) &rarr; **`430` (New)**
- `itypea2`: `miss` (Old) &rarr; **`*empty*` (New)**

### strafe
- `calc1`: `"min(par3 + lvl - 1, par4)"` (Old) &rarr; **`min(par3 + lvl - 1, par4)` (New)**

### summon fenris
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**
- `petmax`: `"min(lvl,par3)"` (Old) &rarr; **`min(lvl,par3)` (New)**
- `sumskill1`: `*empty*` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk1calc`: `*empty*` (Old) &rarr; **`1` (New)**

### summon grizzly
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**

### summon spirit wolf
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `petmax`: `"min(lvl,par3)"` (Old) &rarr; **`min(lvl,par3)` (New)**
- `sumskill1`: `Thorns` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk1calc`: `lvl` (Old) &rarr; **`1` (New)**
- `sumskill2`: `*empty*` (Old) &rarr; **`Thorns` (New)**
- `sumsk2calc`: `*empty*` (Old) &rarr; **`lvl` (New)**

### summon splash
- `*Id`: `378` (Old) &rarr; **`432` (New)**

### teeth
- `manashift`: `7` (Old) &rarr; **`8` (New)**
- `mana`: `5` (Old) &rarr; **`6` (New)**
- `lvlmana`: `1` (Old) &rarr; **`0` (New)**
- `calc1`: `"min(ln12,24)"` (Old) &rarr; **`min(ln12,24)` (New)**
- `Param1`: `2` (Old) &rarr; **`3` (New)**
- `EMinLev1`: `4` (Old) &rarr; **`6` (New)**
- `EMinLev2`: `4` (Old) &rarr; **`6` (New)**
- `EMinLev3`: `4` (Old) &rarr; **`6` (New)**
- `EMinLev4`: `4` (Old) &rarr; **`6` (New)**
- `EMinLev5`: `4` (Old) &rarr; **`6` (New)**
- `EMaxLev1`: `4` (Old) &rarr; **`6` (New)**
- `EMaxLev2`: `4` (Old) &rarr; **`6` (New)**
- `EMaxLev3`: `4` (Old) &rarr; **`6` (New)**
- `EMaxLev4`: `4` (Old) &rarr; **`6` (New)**
- `EMaxLev5`: `4` (Old) &rarr; **`6` (New)**

### thorns
- `Param3`: `250` (Old) &rarr; **`500` (New)**
- `Param4`: `40` (Old) &rarr; **`30` (New)**
- `EMin`: `4` (Old) &rarr; **`5` (New)**
- `EMinLev1`: `4` (Old) &rarr; **`5` (New)**
- `EMinLev2`: `8` (Old) &rarr; **`10` (New)**
- `EMinLev3`: `12` (Old) &rarr; **`15` (New)**
- `EMinLev4`: `16` (Old) &rarr; **`20` (New)**
- `EMinLev5`: `20` (Old) &rarr; **`25` (New)**

### throwing mastery
- `Param3`: `32` (Old) &rarr; **`40` (New)**
- `Param5`: `0` (Old) &rarr; **`1` (New)**
- `Param6`: `40` (Old) &rarr; **`50` (New)**
- `*Param11 Description`: `"Replenish Quantity on crit? (0=disabled, 1=enabled)"` (Old) &rarr; **`Replenish Quantity on crit? (0=disabled, 1=enabled)` (New)**

### valkyrie
- `passivestat3`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc3`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_light_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_light_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_poison_immunity` (New)**
- `sumskill5`: `*empty*` (Old) &rarr; **`Summon Splash` (New)**
- `sumsk5calc`: `*empty*` (Old) &rarr; **`1` (New)**

### vengeance
- `*Id`: `374` (Old) &rarr; **`111` (New)**
- `charclass`: `*empty*` (Old) &rarr; **`pal` (New)**
- `srvstfunc`: `37` (Old) &rarr; **`35` (New)**
- `srvdofunc`: `13` (Old) &rarr; **`2` (New)**
- `cltstfunc`: `53` (Old) &rarr; **`*empty*` (New)**
- `cltdofunc`: `21` (Old) &rarr; **`34` (New)**
- `calc4`: `"min((par5 + lvl -1), par6)"` (Old) &rarr; **`*empty*` (New)**
- `*calc4 desc`: `# of hits` (Old) &rarr; **`*empty*` (New)**
- `Param3`: `100` (Old) &rarr; **`*empty*` (New)**
- `*Param3 Description`: `% Anim frame rollback` (Old) &rarr; **`*empty*` (New)**
- `Param5`: `3` (Old) &rarr; **`*empty*` (New)**
- `*Param5 Description`: `# of hits Min` (Old) &rarr; **`*empty*` (New)**
- `Param6`: `3` (Old) &rarr; **`*empty*` (New)**
- `*Param6 Description`: `# of hits Max` (Old) &rarr; **`*empty*` (New)**

### vine attack
- `cltcalc1`: `"min(ln12,12)"` (Old) &rarr; **`min(ln12,12)` (New)**
- `calc1`: `"min(ln12,24)"` (Old) &rarr; **`min(ln12,24)` (New)**

### wearwolf
- `Param1`: `25` (Old) &rarr; **`100` (New)**

### zeal
- `calc1`: `"min((par5 + lvl -1), par6)"` (Old) &rarr; **`min((par5 + lvl -1), par6)` (New)**
- `Param3`: `0` (Old) &rarr; **`10` (New)**
- `Param4`: `6` (Old) &rarr; **`10` (New)**

