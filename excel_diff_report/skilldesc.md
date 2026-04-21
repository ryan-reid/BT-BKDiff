# Differences for skilldesc.txt

*Key column used: `skilldesc`*

## Added Rows in BK (New) (31)
- abyss
- apocalypse
- bind demon
- blade warp
- blood boil
- blood oath
- cleave
- consume
- death mark
- demonic mastery
- echoing strike
- eldritchblast
- engorge
- enhanced entropy
- flame wave
- hex bane
- hex purge
- hex siphon
- levitate
- miasma bolt
- miasma chains
- mirrored blades
- otownportal
- psychic ward
- ring of fire
- sigil death
- sigil lethargy
- sigil rancor
- summon defiler
- summon goatman
- summon tainted

## Modified Rows (38)
### berserk
- `desccalca1`: `"par4-min(((110*lvl)/(lvl+6)*(par4-par3)/100),(par4-par3))"` (Old) &rarr; **`par4-min(((110*lvl)/(lvl+6)*(par4-par3)/100),(par4-par3))` (New)**

### bone prison
- `desccalca1`: `"max(usmc, 1)"` (Old) &rarr; **`max(usmc, 1)` (New)**

### bone spear
- `desccalca3`: `min(3,1+skill('Bone Spear'.blvl)/10` (Old) &rarr; **`min(3, 1 + skill('Bone Spear'.blvl)/10) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)` (New)**
- `dsc3line3`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta3`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb3`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca3`: `par8` (Old) &rarr; **`*empty*` (New)**
- `dsc3line4`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta4`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb4`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca4`: `par8` (Old) &rarr; **`*empty*` (New)**

### bone spirit
- `dsc3line3`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta3`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb3`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca3`: `par8` (Old) &rarr; **`*empty*` (New)**
- `dsc3line5`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta5`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb5`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca5`: `par8` (Old) &rarr; **`*empty*` (New)**

### charged bolt
- `desccalca3`: `"min(24,ln12)"` (Old) &rarr; **`min(24,ln12)` (New)**

### cloak of shadows
- `desccalca2`: `"-min(ln56,95)"` (Old) &rarr; **`-min(ln56,95)` (New)**

### conviction
- `desccalca2`: `"-min(ln34,150)"` (Old) &rarr; **`-min(ln34,150)` (New)**

### dopplezon
- `desccalca1`: `"max(usmc, 1)"` (Old) &rarr; **`max(usmc, 1)` (New)**

### double swing
- `desccalca1`: `"max(0, usmc*2)"` (Old) &rarr; **`max(0, usmc*2)` (New)**
- `dsc3textb2`: `skillname126` (Old) &rarr; **`skillname147` (New)**

### energy shield
- `desccalca2`: `"min(edmn,95)"` (Old) &rarr; **`min(edmn,95)` (New)**

### exploding arrow
- `desccalca4`: `"min(1+(ln12/7),4)"` (Old) &rarr; **`min(1+(ln12/7),4)` (New)**

### fire wall
- `dsc3textb3`: `skillname41` (Old) &rarr; **`skillname46` (New)**

### freezing arrow
- `desccalca5`: `"min(1+(ln12/7),4)"` (Old) &rarr; **`min(1+(ln12/7),4)` (New)**

### frenzy
- `dsc2calca2`: `par7+skill('Increased Stamina'.blvl)*10` (Old) &rarr; **`par7+skill('Increased Endurance'.blvl)*10` (New)**

### frozen orb
- `dsc3textb4`: `skillname55` (Old) &rarr; **`skillname44` (New)**

### fury
- `desccalca3`: `"min((par5+lvl-1),par6)"` (Old) &rarr; **`min((par5+lvl-1),par6)` (New)**

### glacial spike
- `dsc3textb5`: `skillname64` (Old) &rarr; **`skillname59` (New)**

### guided arrow
- `desccalca1`: `"max(usmc, 1)"` (Old) &rarr; **`max(usmc, 1)` (New)**

### hurricane
- `descline2`: `74` (Old) &rarr; **`*empty*` (New)**
- `desctexta2`: `StrSkill20` (Old) &rarr; **`*empty*` (New)**
- `desccalca2`: `par1` (Old) &rarr; **`*empty*` (New)**
- `dsc3line3`: `*empty*` (Old) &rarr; **`76` (New)**
- `dsc3texta3`: `*empty*` (Old) &rarr; **`Damplev` (New)**
- `dsc3textb3`: `*empty*` (Old) &rarr; **`Skillname227` (New)**
- `dsc3calca3`: `*empty*` (Old) &rarr; **`par8` (New)**
- `dsc3line4`: `*empty*` (Old) &rarr; **`76` (New)**
- `dsc3texta4`: `*empty*` (Old) &rarr; **`Damplev` (New)**
- `dsc3textb4`: `*empty*` (Old) &rarr; **`Skillname241` (New)**
- `dsc3calca4`: `*empty*` (Old) &rarr; **`par8` (New)**
- `dsc3line5`: `*empty*` (Old) &rarr; **`76` (New)**
- `dsc3texta5`: `*empty*` (Old) &rarr; **`Damplev` (New)**
- `dsc3textb5`: `*empty*` (Old) &rarr; **`Skillname246` (New)**
- `dsc3calca5`: `*empty*` (Old) &rarr; **`par8` (New)**

### ice blast
- `dsc3textb5`: `skillname64` (Old) &rarr; **`skillname55` (New)**

### magic arrow
- `desccalca1`: `"max(usmc, 0)"` (Old) &rarr; **`max(usmc, 0)` (New)**

### maul
- `desccalca1`: `"min(250,dm56)"` (Old) &rarr; **`min(250,dm56)` (New)**

### mind blast
- `desccalca2`: `"min(250,edln)"` (Old) &rarr; **`min(250,edln)` (New)**

### multiple shot
- `ddam calc1`: `skill('Guided Arrow'.blvl) * par4` (Old) &rarr; **`*empty*` (New)**
- `desccalca2`: `"min(24,ln12)"` (Old) &rarr; **`min(24,ln12)` (New)**
- `dsc2calca1`: `(96*100/128)+(skill('Guided Arrow'.blvl)*par4)` (Old) &rarr; **`96*100/128` (New)**

### poison dagger
- `dsc2line1`: `*empty*` (Old) &rarr; **`36` (New)**
- `dsc2texta1`: `*empty*` (Old) &rarr; **`StrSkillRadiusSingular` (New)**
- `dsc2calca1`: `*empty*` (Old) &rarr; **`5` (New)**

### raven
- `desccalca1`: `"min(lvl,par2)"` (Old) &rarr; **`min(lvl,par2)` (New)**

### sacrifice
- `dsc2calca1`: `"max(par6, par5-lvl/par3)"` (Old) &rarr; **`max(par6, par5-lvl/par3)` (New)**

### smite
- `desccalca1`: `"min(250,ln12)"` (Old) &rarr; **`min(250,ln12)` (New)**

### strafe
- `ddam calc1`: `ln12 + (skill('Guided Arrow'.blvl)*par8) + (skill('Multiple Shot'.blvl)*par9)` (Old) &rarr; **`*empty*` (New)**
- `desccalca1`: `ln12 + (skill('Guided Arrow'.blvl)*par8) + (skill('Multiple Shot'.blvl)*par9)` (Old) &rarr; **`ln12` (New)**
- `desccalca2`: `"min(lvl+par3,par4)"` (Old) &rarr; **`min(lvl+par3,par4)` (New)**

### stun
- `desccalca1`: `"min(250,edln)"` (Old) &rarr; **`min(250,edln)` (New)**

### summon fenris
- `desccalca3`: `"min(lvl,par3)"` (Old) &rarr; **`min(lvl,par3)` (New)**

### summon spirit wolf
- `desccalca3`: `"min(lvl,par3)"` (Old) &rarr; **`min(lvl,par3)` (New)**

### teeth
- `desccalca3`: `"min(ln12,24)"` (Old) &rarr; **`min(ln12,24)` (New)**
- `dsc3line2`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta2`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb2`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca2`: `par8` (Old) &rarr; **`*empty*` (New)**
- `dsc3line4`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta4`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb4`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca4`: `par8` (Old) &rarr; **`*empty*` (New)**

### teleport
- `desccalca1`: `"max(usmc, 1)"` (Old) &rarr; **`max(usmc, 1)` (New)**

### vengeance
- `desccalca6`: `"min((par5 + lvl -1), par6)"` (Old) &rarr; **`min((par5 + lvl -1), par6)` (New)**

### war cry
- `desccalca2`: `"min(250,ln12)"` (Old) &rarr; **`min(250,ln12)` (New)**
- `dsc3textb2`: `skillname130` (Old) &rarr; **`skillname149` (New)**

### wearwolf
- `dsc2calca3`: `par2+skill('shape shifting'.ln34)` (Old) &rarr; **`par2+skill('Shape Shifting'.ln34)` (New)**

### zeal
- `desccalca3`: `"min((par5 + lvl -1), par6)"` (Old) &rarr; **`min((par5 + lvl -1), par6)` (New)**

