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
- `Param1`: $\color{gray}{\text{150}}$ (Old) &rarr; $\color{blue}{\text{500}}$ (New)
### blade sentinel
- `passivecalc6`: $$	ext{stat('itempiercecoldimmunity'.accr}$$ (Old) &rarr; $$	ext{stat('itempiercecoldimmunity'.accr}$\color{blue}{\text{)}}$ (New)
### blizzard
- `Param3`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{2}}$ (New)
### bloodgolem
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)
- `sumskill1`:  (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk1calc`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### bloodlordfrenzy
- `srvstfunc`: $\color{gray}{\text{64}}$ (Old) &rarr; $\color{blue}{\text{67}}$ (New)
- `srvdofunc`: $\color{gray}{\text{109}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
### bone spear
- `mana`: $\color{gray}{\text{16}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
- `calc1`: $$	ext{min(}$\color{gray}{\text{3}}$	ext{,}$$	ext{1}$$	ext{+}$$	ext{skill('Bone Spear'.blvl)/10}$$ (Old) &rarr; $$	ext{min(}$\color{blue}{\text{5}}$	ext{,}$\color{blue}{\text{ }}$	ext{1}$\color{blue}{\text{ }}$	ext{+}$\color{blue}{\text{ }}$	ext{skill('Bone Spear'.blvl)/10}$\color{blue}{\text{) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)}}$ (New)
### clay golem
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)
- `sumskill1`:  (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk1calc`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### cold mastery
- `Param2`: $\color{gray}{\text{2}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)
### death sentry
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{passive\_ltng\_mastery}}$ (New)
- `passivecalc6`:  (Old) &rarr; $\color{blue}{\text{stat('passive\_ltng\_mastery'.accr)}}$ (New)
- `passivestat7`:  (Old) &rarr; $\color{blue}{\text{passive\_fire\_mastery}}$ (New)
- `passivecalc7`:  (Old) &rarr; $\color{blue}{\text{stat('passive\_fire\_mastery'.accr)}}$ (New)
### decrepify
- `Param1`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{3}}$ (New)
- `Param2`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### double throw
- `Param1`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{40}}$ (New)
### dragon claw
- `Param1`: $\color{gray}{\text{50}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
- `Param2`: $\color{gray}{\text{15}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `Param7`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)
### eruption
- `Param8`: $\color{gray}{\text{15}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
### fire ball
- `calc1`: $$	ext{min(}$\color{gray}{\text{3}}$	ext{,1+skill('Fire Ball'.blvl)/}$\color{gray}{\text{10}}$ (Old) &rarr; $$	ext{min(}$\color{blue}{\text{5}}$	ext{,1+skill('Fire Ball'.blvl)/}$\color{blue}{\text{5}}$ (New)
### fire wall
- `Param7`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)
- `EDmgSymPerCalc`: $$	ext{(skill('Warmth'.blvl)*par8+skill('}$\color{gray}{\text{Inferno}}$	ext{'.blvl)*par7}$$ (Old) &rarr; $$	ext{(skill('Warmth'.blvl)*par8+skill('}$\color{blue}{\text{Blaze}}$	ext{'.blvl)*par7}$$ (New)
### firegolem
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)
### freezing arrow
- `Param8`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{3}}$ (New)
### frenzy
- `auralencalc`: $$	ext{par7+skill('Increased }$\color{gray}{\text{Stamina}}$	ext{'.blvl)*10}$$ (Old) &rarr; $$	ext{par7+skill('Increased }$\color{blue}{\text{Endurance}}$	ext{'.blvl)*10}$$ (New)
- `Param1`: $\color{gray}{\text{90}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
- `Param2`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Param8`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
### frost nova
- `Param8`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{22}}$ (New)
### frozen orb
- `Param8`: $\color{gray}{\text{2}}$ (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `EDmgSymPerCalc`: $$	ext{(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('}$\color{gray}{\text{Glacial}}$	ext{ }$\color{gray}{\text{Spike}}$	ext{'.blvl))*par8}$$ (Old) &rarr; $$	ext{(skill('Ice Bolt'.blvl)+skill('Frozen Armor'.blvl)+skill('}$\color{blue}{\text{Frost}}$	ext{ }$\color{blue}{\text{Nova}}$	ext{'.blvl))*par8}$$ (New)
### glacial spike
- `srvdofunc`:  (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `srvmissile`: $\color{gray}{\text{glacialspike}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `srvmissilea`:  (Old) &rarr; $\color{blue}{\text{glacialspike}}$ (New)
- `srvmissileb`:  (Old) &rarr; $\color{blue}{\text{glacialspike}}$ (New)
- `cltdofunc`:  (Old) &rarr; $\color{blue}{\text{17}}$ (New)
- `cltmissile`: $\color{gray}{\text{glacialspike}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `cltmissilea`:  (Old) &rarr; $\color{blue}{\text{glacialspike}}$ (New)
- `cltmissileb`:  (Old) &rarr; $\color{blue}{\text{glacialspike}}$ (New)
- `calc1`:  (Old) &rarr; $\color{blue}{\text{min(5,1+skill('Glacial Spike'.blvl)/5}}$ (New)
- `\*calc1 desc`:  (Old) &rarr; $\color{blue}{\text{\# of Missiles created}}$ (New)
- `calc2`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `\*calc2 desc`:  (Old) &rarr; $\color{blue}{\text{Missile Activation Frame}}$ (New)
- `calc3`:  (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `Param5`:  (Old) &rarr; $\color{blue}{\text{2}}$ (New)
- `\*Param5 Description`:  (Old) &rarr; $\color{blue}{\text{\# of Missiles created baseline}}$ (New)
- `Param6`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `\*Param6 Description`:  (Old) &rarr; $\color{blue}{\text{\# of Missiles created per level}}$ (New)
- `EDmgSymPerCalc`: $$	ext{(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('}$\color{gray}{\text{Frozen Orb}}$	ext{'.blvl))*par8}$$ (Old) &rarr; $$	ext{(skill('Ice Bolt'.blvl)+skill('Ice Blast'.blvl)+skill('}$\color{blue}{\text{Blizzard}}$	ext{'.blvl))*par8}$$ (New)
### holy bolt
- `Param8`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
### hurricane
- `Param3`: $\color{gray}{\text{15}}$ (Old) &rarr; $\color{blue}{\text{12}}$ (New)
- `Param4`: $\color{gray}{\text{1}}$ (Old) &rarr; $\color{blue}{\text{2}}$ (New)
- `Param8`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{2}}$ (New)
- `EDmgSymPerCalc`: $$	ext{skill('Cyclone Armor'.blvl)}$$	ext{*par8}$$ (Old) &rarr; $\color{blue}{\text{(}}$	ext{skill('Cyclone Armor'.blvl)}$\color{blue}{\text{+skill('Twister'.blvl)+skill('Tornado'.blvl)+skill('Oak Sage'.blvl))}}$	ext{*par8}$$ (New)
### hydra
- `passivestat3`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc3`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)
### ice blast
- `EDmgSymPerCalc`: $$	ext{(skill('Ice Bolt'.blvl)+skill('}$\color{gray}{\text{Blizzard}}$	ext{'.blvl)+skill('}$\color{gray}{\text{Frozen Orb}}$	ext{'.blvl))*par8}$$ (Old) &rarr; $$	ext{(skill('Ice Bolt'.blvl)+skill('}$\color{blue}{\text{Glacial Spike}}$	ext{'.blvl)+skill('}$\color{blue}{\text{Blizzard}}$	ext{'.blvl))*par8}$$ (New)
### immolation arrow
- `Param8`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)
### increased endurance
- `passivestate`: $\color{gray}{\text{increasedstamina}}$ (Old) &rarr; $\color{blue}{\text{increasedendurance}}$ (New)
### increased speed
- `reqskill1`: $$	ext{Increased }$\color{gray}{\text{Stamina}}$ (Old) &rarr; $$	ext{Increased }$\color{blue}{\text{Endurance}}$ (New)
### irongolem
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `sumskill1`:  (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk1calc`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### lightning
- `Param8`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
### magic conviction
- `\*Id`: $\color{gray}{\text{376}}$ (Old) &rarr; $\color{blue}{\text{431}}$ (New)
- `aurastatcalc1`: $$	ext{-}$$	ext{(}$\color{gray}{\text{lvl*5+15}}$	ext{)}$\color{gray}{\text{-stat('passivemagpierce'.accr)}}$ (Old) &rarr; $$	ext{-}$\color{blue}{\text{min}}$	ext{(}$\color{blue}{\text{ln34,150}}$	ext{)}$$ (New)
- `Param3`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `Param4`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)
### meteor
- `Param1`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
- `Param4`: $\color{gray}{\text{15}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `Param8`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
### monfrenzy
- `srvstfunc`: $\color{gray}{\text{64}}$ (Old) &rarr; $\color{blue}{\text{67}}$ (New)
- `srvdofunc`: $\color{gray}{\text{109}}$ (Old) &rarr; $\color{blue}{\text{9}}$ (New)
### multiple shot
- `Param4`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
### nova
- `Param8`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{4}}$ (New)
### plague poppy
- `passivestat1`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_poison\_immunity}}$ (New)
- `passivecalc1`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_poison\_immunity'.accr)}}$ (New)
### poison dagger
- `srvmissile`:  (Old) &rarr; $\color{blue}{\text{poisondagger}}$ (New)
- `cltmissile`:  (Old) &rarr; $\color{blue}{\text{poisondagger}}$ (New)
- `itypea1`: $\color{gray}{\text{knif}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
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
- `passivestat3`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc3`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)
- `sumskill1`:  (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk1calc`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### raven
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `sumskill1`:  (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk1calc`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
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
### shout
- `Param1`: $\color{gray}{\text{100}}$ (Old) &rarr; $\color{blue}{\text{200}}$ (New)
### splash
- `\*Id`: $\color{gray}{\text{375}}$ (Old) &rarr; $\color{blue}{\text{430}}$ (New)
### summon fenris
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)
- `sumskill1`:  (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk1calc`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### summon grizzly
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_damage\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_damage\_immunity'.accr)}}$ (New)
### summon spirit wolf
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `sumskill1`: $\color{gray}{\text{Thorns}}$ (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk1calc`: $\color{gray}{\text{lvl}}$ (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `sumskill2`:  (Old) &rarr; $\color{blue}{\text{Thorns}}$ (New)
- `sumsk2calc`:  (Old) &rarr; $\color{blue}{\text{lvl}}$ (New)
### summon splash
- `\*Id`: $\color{gray}{\text{378}}$ (Old) &rarr; $\color{blue}{\text{432}}$ (New)
### teeth
- `manashift`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `mana`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `lvlmana`: $\color{gray}{\text{1}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `Param1`: $\color{gray}{\text{2}}$ (Old) &rarr; $\color{blue}{\text{3}}$ (New)
- `EMinLev1`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMinLev2`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMinLev3`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMinLev4`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMinLev5`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMaxLev1`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMaxLev2`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMaxLev3`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMaxLev4`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
- `EMaxLev5`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{6}}$ (New)
### thorns
- `Param3`: $\color{gray}{\text{250}}$ (Old) &rarr; $\color{blue}{\text{500}}$ (New)
- `Param4`: $\color{gray}{\text{40}}$ (Old) &rarr; $\color{blue}{\text{30}}$ (New)
- `EMin`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)
- `EMinLev1`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)
- `EMinLev2`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `EMinLev3`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
- `EMinLev4`: $\color{gray}{\text{16}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `EMinLev5`: $\color{gray}{\text{20}}$ (Old) &rarr; $\color{blue}{\text{25}}$ (New)
### throwing mastery
- `Param3`: $\color{gray}{\text{32}}$ (Old) &rarr; $\color{blue}{\text{40}}$ (New)
- `Param5`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `Param6`: $\color{gray}{\text{40}}$ (Old) &rarr; $\color{blue}{\text{50}}$ (New)
### valkyrie
- `passivestat3`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_cold\_immunity}}$ (New)
- `passivecalc3`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_cold\_immunity'.accr)}}$ (New)
- `passivestat4`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_fire\_immunity}}$ (New)
- `passivecalc4`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_fire\_immunity'.accr)}}$ (New)
- `passivestat5`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_light\_immunity}}$ (New)
- `passivecalc5`:  (Old) &rarr; $\color{blue}{\text{stat('item\_pierce\_light\_immunity'.accr)}}$ (New)
- `passivestat6`:  (Old) &rarr; $\color{blue}{\text{item\_pierce\_poison\_immunity}}$ (New)
- `sumskill5`:  (Old) &rarr; $\color{blue}{\text{Summon Splash}}$ (New)
- `sumsk5calc`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### vengeance
- `\*Id`: $\color{gray}{\text{374}}$ (Old) &rarr; $\color{blue}{\text{111}}$ (New)
- `charclass`:  (Old) &rarr; $\color{blue}{\text{pal}}$ (New)
- `srvstfunc`: $\color{gray}{\text{37}}$ (Old) &rarr; $\color{blue}{\text{35}}$ (New)
- `srvdofunc`: $\color{gray}{\text{13}}$ (Old) &rarr; $\color{blue}{\text{2}}$ (New)
- `cltstfunc`: $\color{gray}{\text{53}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `cltdofunc`: $\color{gray}{\text{21}}$ (Old) &rarr; $\color{blue}{\text{34}}$ (New)
- `calc4`: $\color{gray}{\text{"min((par5 + lvl -1), par6)"}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `\*calc4 desc`: $\color{gray}{\text{\# of hits}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `Param1`: $\color{gray}{\text{100}}$ (Old) &rarr; $\color{blue}{\text{500}}$ (New)
- `Param2`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{25}}$ (New)
- `Param3`: $\color{gray}{\text{100}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `\*Param3 Description`: $\color{gray}{\text{\% Anim frame rollback}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `Param5`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `\*Param5 Description`: $\color{gray}{\text{\# of hits Min}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `Param6`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `\*Param6 Description`: $\color{gray}{\text{\# of hits Max}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `Param7`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
- `Param8`: $\color{gray}{\text{15}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
### war cry
- `DmgSymPerCalc`: $$	ext{(skill('}$\color{gray}{\text{Howl}}$	ext{'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8}$$ (Old) &rarr; $$	ext{(skill('}$\color{blue}{\text{Battle Orders}}$	ext{'.blvl)+skill('Taunt'.blvl)+skill('Battle Cry'.blvl))*par8}$$ (New)
### wearwolf
- `Param1`: $\color{gray}{\text{25}}$ (Old) &rarr; $\color{blue}{\text{100}}$ (New)
### zeal
- `Param3`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `Param4`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
