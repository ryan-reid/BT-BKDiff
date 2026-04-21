# Differences for skills.txt

*Key column used: `skill`*

## Added Columns in BK (New)
`auraevent4, auraeventfunc4, requirespettype, requiresweapon, periodicClearAura, calc7, *calc7desc, calc8, *calc8desc, calc9, *calc9desc, calc10, *calc10desc, Param13, *Param13Description, Param14, *Param14Description, Param15, *Param15Description, Param16, *Param16Description, Param17, *Param17Description, Param18, *Param18Description, Param19, *Param19Description, Param20, *Param20Description`  

## Added Rows in BK (New) (56)
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

## Removed Rows in BK (New) (2)
- frostnovanew
- magic pierce

## Modified Rows (38)
### berserk
- `Param1`: `500` (Old) &rarr; **`150` (New)**

### blade sentinel
- `passivecalc6`: `stat('item_pierce_cold_immunity'.accr` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**

### bloodgolem
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**

### bloodlordfrenzy
- `srvstfunc`: `64` (Old) &rarr; **`67` (New)**
- `srvdofunc`: `109` (Old) &rarr; **`9` (New)**

### bone spear
- `calc1`: `min(3,1+skill('Bone Spear'.blvl)/10` (Old) &rarr; **`min(3, 1 + skill('Bone Spear'.blvl)/10) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)` (New)**

### clay golem
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**

### death sentry
- `passivestat6`: `*empty*` (Old) &rarr; **`passive_ltng_mastery` (New)**
- `passivecalc6`: `*empty*` (Old) &rarr; **`stat('passive_ltng_mastery'.accr)` (New)**
- `passivestat7`: `*empty*` (Old) &rarr; **`passive_fire_mastery` (New)**
- `passivecalc7`: `*empty*` (Old) &rarr; **`stat('passive_fire_mastery'.accr)` (New)**

### double swing
- `calc1`: `skill('Frenzy'.blvl)*par8` (Old) &rarr; **`skill('Bash'.blvl)*par8` (New)**

### dragon claw
- `Param1`: `100` (Old) &rarr; **`50` (New)**
- `Param2`: `20` (Old) &rarr; **`15` (New)**
- `Param7`: `5` (Old) &rarr; **`4` (New)**

### eruption
- `Param8`: `10` (Old) &rarr; **`15` (New)**

### fire trauma
- `Param8`: `18` (Old) &rarr; **`10` (New)**

### firegolem
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**

### frenzy
- `auralencalc`: `par7+skill('Increased Stamina'.blvl)*10` (Old) &rarr; **`par7+skill('Increased Endurance'.blvl)*10` (New)**

### holy bolt
- `calc1`: `min(3,1+skill('Holy Bolt'.blvl)/10` (Old) &rarr; **`min(5,1+skill('Holy Bolt'.blvl)/5` (New)**

### hydra
- `passivestat3`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc3`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**
- `Param1`: `250` (Old) &rarr; **`10` (New)**
- `Param2`: `0` (Old) &rarr; **`1` (New)**

### increased endurance
- `passivestate`: `increasedstamina` (Old) &rarr; **`increasedendurance` (New)**

### increased speed
- `reqskill1`: `Increased Stamina` (Old) &rarr; **`Increased Endurance` (New)**

### irongolem
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**

### magic conviction
- `*Id`: `376` (Old) &rarr; **`431` (New)**
- `aurastatcalc1`: `-(lvl*5+15)-stat('passive_mag_pierce'.accr)` (Old) &rarr; **`-min(ln34,150)` (New)**
- `Param3`: `0` (Old) &rarr; **`20` (New)**
- `Param4`: `0` (Old) &rarr; **`5` (New)**

### monfrenzy
- `srvstfunc`: `64` (Old) &rarr; **`67` (New)**
- `srvdofunc`: `109` (Old) &rarr; **`9` (New)**

### plague poppy
- `passivestat1`: `*empty*` (Old) &rarr; **`item_pierce_poison_immunity` (New)**
- `passivecalc1`: `*empty*` (Old) &rarr; **`stat('item_pierce_poison_immunity'.accr)` (New)**

### poison dagger
- `manashift`: `6` (Old) &rarr; **`4` (New)**
- `mana`: `10` (Old) &rarr; **`40` (New)**
- `lvlmana`: `-1` (Old) &rarr; **`10` (New)**

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
- `passivestat2`: `mindamage` (Old) &rarr; **`item_normaldamage` (New)**
- `passivestat3`: `maxdamage` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc3`: `skill('Skeleton Mastery'.lvl) * skill('Skeleton Mastery'.par2) + edmn` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**

### raven
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**

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

### shadow master
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**

### shadow warrior
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**

### splash
- `*Id`: `375` (Old) &rarr; **`430` (New)**
- `itypea2`: `miss` (Old) &rarr; **`*empty*` (New)**

### summon fenris
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**

### summon grizzly
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_damage_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_damage_immunity'.accr)` (New)**

### summon spirit wolf
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**

### summon splash
- `*Id`: `378` (Old) &rarr; **`432` (New)**

### unused0001
- `*Id`: `374` (Old) &rarr; **`429` (New)**

### valkyrie
- `passivestat3`: `*empty*` (Old) &rarr; **`item_pierce_cold_immunity` (New)**
- `passivecalc3`: `*empty*` (Old) &rarr; **`stat('item_pierce_cold_immunity'.accr)` (New)**
- `passivestat4`: `*empty*` (Old) &rarr; **`item_pierce_fire_immunity` (New)**
- `passivecalc4`: `*empty*` (Old) &rarr; **`stat('item_pierce_fire_immunity'.accr)` (New)**
- `passivestat5`: `*empty*` (Old) &rarr; **`item_pierce_light_immunity` (New)**
- `passivecalc5`: `*empty*` (Old) &rarr; **`stat('item_pierce_light_immunity'.accr)` (New)**
- `passivestat6`: `*empty*` (Old) &rarr; **`item_pierce_poison_immunity` (New)**

### vengeance
- `Param1`: `500` (Old) &rarr; **`100` (New)**
- `Param2`: `25` (Old) &rarr; **`10` (New)**
- `Param7`: `15` (Old) &rarr; **`5` (New)**
- `Param8`: `20` (Old) &rarr; **`15` (New)**

### war cry
- `DmgSymPerCalc`: `(skill('Battle Orders'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8` (Old) &rarr; **`(skill('Howl'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8` (New)**

### wearwolf
- `Param1`: `25` (Old) &rarr; **`100` (New)**

