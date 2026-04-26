# Differences for skills.txt

*Key column used: `skill`*

## Added Columns: `auraevent4, auraeventfunc4, requirespettype, requiresweapon, periodicClearAura, calc7, *calc7desc, calc8, *calc8desc, calc9, *calc9desc, calc10, *calc10desc, Param13, *Param13Description, Param14, *Param14Description, Param15, *Param15Description, Param16, *Param16Description, Param17, *Param17Description, Param18, *Param18Description, Param19, *Param19Description, Param20, *Param20Description`  

## Added Rows (56)
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

## Removed Rows (2)
- frostnovanew
- magic pierce

## Modified Rows (34)
### blade sentinel
- `passivecalc6`: $\text{stat('itempiercecoldimmunity'.accr}}$ (Old) &rarr; $\text{stat('itempiercecoldimmunity'.accr}}\color{blue}{\text{)}}$ (New)

### bloodgolem
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)

### bloodlordfrenzy
- `srvstfunc`: $\color{gray}{\text{64}}$ (Old) &rarr; $\color{blue}{\text{67}}$ (New)
- `srvdofunc`: $\color{gray}{\text{109}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)

### bone spear
- `calc1`: $\text{min(}}\color{gray}{\text{3}}\text{,}}\text{1}}\text{+}}\text{skill('Bone Spear'.blvl)/10}}$ (Old) &rarr; $\text{min(}}\color{blue}{\text{5}}\text{,}}\color{blue}{\text{ }}\text{1}}\color{blue}{\text{ }}\text{+}}\color{blue}{\text{ }}\text{skill('Bone Spear'.blvl)/10}}\color{blue}{\text{) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)}}$ (New)

### clay golem
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)

### death sentry
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{passive\_ltng\_mastery}}$ (New)
- `passivecalc6`:  (Old) &rarr; $\color{blue}{\text{stat('passive\_ltng\_mastery'.accr)}}$ (New)
- `passivestat7`:  (Old) &rarr; $\color{blue}{\text{passive\_fire\_mastery}}$ (New)
- `passivecalc7`:  (Old) &rarr; $\color{blue}{\text{stat('passive\_fire\_mastery'.accr)}}$ (New)

### double swing
- `calc1`: $\text{skill('}}\color{gray}{\text{Frenzy}}\text{'.blvl)*par8}}$ (Old) &rarr; $\text{skill('}}\color{blue}{\text{Bash}}\text{'.blvl)*par8}}$ (New)

### fire ball
- `calc1`: $\text{min(}}\color{gray}{\text{3}}\text{,1+skill('Fire Ball'.blvl)/}}\color{gray}{\text{10}}$ (Old) &rarr; $\text{min(}}\color{blue}{\text{5}}\text{,1+skill('Fire Ball'.blvl)/}}\color{blue}{\text{5}}$ (New)

### firegolem
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)

### frenzy
- `auralencalc`: $\text{par7+skill('Increased }}\color{gray}{\text{Stamina}}\text{'.blvl)*10}}$ (Old) &rarr; $\text{par7+skill('Increased }}\color{blue}{\text{Endurance}}\text{'.blvl)*10}}$ (New)

### glacial spike
- `calc1`: $\text{min(}}\color{gray}{\text{3}}\text{,1+skill('Glacial Spike'.blvl)/}}\color{gray}{\text{10}}$ (Old) &rarr; $\text{min(}}\color{blue}{\text{5}}\text{,1+skill('Glacial Spike'.blvl)/}}\color{blue}{\text{5}}$ (New)

### holy bolt
- `calc1`: $\text{min(}}\color{gray}{\text{3}}\text{,1+skill('Holy Bolt'.blvl)/}}\color{gray}{\text{10}}$ (Old) &rarr; $\text{min(}}\color{blue}{\text{5}}\text{,1+skill('Holy Bolt'.blvl)/}}\color{blue}{\text{5}}$ (New)

### hydra
- `passivestat3`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc3`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)
- `Param2`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{25}}$ (New)

### increased endurance
- `passivestate`: $\color{gray}{\text{increasedstamina}}$ (Old) &rarr; $\color{blue}{\text{increasedendurance}}$ (New)

### increased speed
- `reqskill1`: $\text{Increased }}\color{gray}{\text{Stamina}}$ (Old) &rarr; $\text{Increased }}\color{blue}{\text{Endurance}}$ (New)

### irongolem
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)

### magic conviction
- `*Id`: $\color{gray}{\text{376}}$ (Old) &rarr; $\color{blue}{\text{431}}$ (New)
- `aurastatcalc1`: $\text{-}}\text{(}}\color{gray}{\text{lvl*5+15}}\text{)}}\color{gray}{\text{-stat('passivemagpierce'.accr)}}$ (Old) &rarr; $\text{-}}\color{blue}{\text{min}}\text{(}}\color{blue}{\text{ln34,150}}\text{)}}$ (New)
- `Param3`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `Param4`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)

### monfrenzy
- `srvstfunc`: $\color{gray}{\text{64}}$ (Old) &rarr; $\color{blue}{\text{67}}$ (New)
- `srvdofunc`: $\color{gray}{\text{109}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)

### plague poppy
- `passivestat1`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_poison\_immunity}}$ (New)
- `passivecalc1`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_poison\_immunity'.accr)}}$ (New)

### poison dagger
- `manashift`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{4}}$ (New)
- `mana`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{40}}$ (New)
- `lvlmana`: $\color{gray}{\text{-1}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)

### raise skeletal mage
- `passivestat2`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc2`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat3`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc3`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_light\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_light\_immunity'.accr)}}$ (New)
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_poison\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_poison\_immunity'.accr)}}$ (New)

### raise skeleton
- `passivestat2`: $\color{gray}{\text{mindamage}}$ (Old) &rarr; $\color{blue}{\text{itemnormaldamage}}$ (New)
- `passivestat3`: $\color{gray}{\text{maxdamage}}$ (Old) &rarr; $\color{blue}{\text{itempiercedamageimmunity}}$ (New)
- `passivecalc3`: $\color{gray}{\text{skill}}\text{('}}\color{gray}{\text{Skeleton Mastery}}\text{'.}}\color{gray}{\text{lvl}}\text{)}}\color{gray}{\text{ * skill('Skeleton Mastery'.par2) + edmn}}$ (Old) &rarr; $\color{blue}{\text{stat}}\text{('}}\color{blue}{\text{itempiercedamageimmunity}}\text{'.}}\color{blue}{\text{accr}}\text{)}}$ (New)

### raven
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)

### revive
- `passivestat2`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc2`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat3`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc3`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_light\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_light\_immunity'.accr)}}$ (New)
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_poison\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_poison\_immunity'.accr)}}$ (New)
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)

### shadow master
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)

### shadow warrior
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)

### splash
- `*Id`: $\color{gray}{\text{375}}$ (Old) &rarr; $\color{blue}{\text{430}}$ (New)

### summon fenris
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)

### summon grizzly
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)

### summon spirit wolf
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)

### summon splash
- `*Id`: $\color{gray}{\text{378}}$ (Old) &rarr; $\color{blue}{\text{432}}$ (New)

### unused0001
- `*Id`: $\color{gray}{\text{374}}$ (Old) &rarr; $\color{blue}{\text{429}}$ (New)

### valkyrie
- `passivestat3`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc3`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_light\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_light\_immunity'.accr)}}$ (New)
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_poison\_immunity}}$ (New)

### wearwolf
- `Param1`: $\color{gray}{\text{25}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
