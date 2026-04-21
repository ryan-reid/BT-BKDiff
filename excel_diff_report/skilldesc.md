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

## Modified Rows (15)
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

### double swing
- `dsc3textb2`: `skillname126` (Old) &rarr; **`skillname147` (New)**

### fire wall
- `dsc3textb3`: `skillname41` (Old) &rarr; **`skillname46` (New)**

### frenzy
- `dsc2calca2`: `par7+skill('Increased Stamina'.blvl)*10` (Old) &rarr; **`par7+skill('Increased Endurance'.blvl)*10` (New)**

### frozen orb
- `dsc3textb4`: `skillname55` (Old) &rarr; **`skillname44` (New)**

### glacial spike
- `dsc3textb5`: `skillname64` (Old) &rarr; **`skillname59` (New)**

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

### multiple shot
- `ddam calc1`: `skill('Guided Arrow'.blvl) * par4` (Old) &rarr; **`*empty*` (New)**
- `dsc2calca1`: `(96*100/128)+(skill('Guided Arrow'.blvl)*par4)` (Old) &rarr; **`96*100/128` (New)**

### poison dagger
- `dsc2line1`: `*empty*` (Old) &rarr; **`36` (New)**
- `dsc2texta1`: `*empty*` (Old) &rarr; **`StrSkillRadiusSingular` (New)**
- `dsc2calca1`: `*empty*` (Old) &rarr; **`5` (New)**

### strafe
- `ddam calc1`: `ln12 + (skill('Guided Arrow'.blvl)*par8) + (skill('Multiple Shot'.blvl)*par9)` (Old) &rarr; **`*empty*` (New)**
- `desccalca1`: `ln12 + (skill('Guided Arrow'.blvl)*par8) + (skill('Multiple Shot'.blvl)*par9)` (Old) &rarr; **`ln12` (New)**

### teeth
- `dsc3line2`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta2`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb2`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca2`: `par8` (Old) &rarr; **`*empty*` (New)**
- `dsc3line4`: `76` (Old) &rarr; **`*empty*` (New)**
- `dsc3texta4`: `Magdplev` (Old) &rarr; **`*empty*` (New)**
- `dsc3textb4`: `skillname` (Old) &rarr; **`*empty*` (New)**
- `dsc3calca4`: `par8` (Old) &rarr; **`*empty*` (New)**

### war cry
- `dsc3textb2`: `skillname130` (Old) &rarr; **`skillname149` (New)**

### wearwolf
- `dsc2calca3`: `par2+skill('shape shifting'.ln34)` (Old) &rarr; **`par2+skill('Shape Shifting'.ln34)` (New)**

