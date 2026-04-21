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

## Modified Rows (10)
### bone spear
- `desccalca3`: $\color{gray}{\text{min(3,1+lvl/10)}}$ (Old) &rarr; $\color{blue}{\text{min(3, 1 + skill('Bone Spear'.blvl)/10) + ((skill('Bone Spear'.lvl) - skill('Bone Spear'.blvl)) / 5)}}$ (New)
- `dsc3line3`: $\color{gray}{\text{76}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3texta3`: $\color{gray}{\text{Magdplev}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3textb3`: $\color{gray}{\text{skillname}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3calca3`: $\color{gray}{\text{par8}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3line4`: $\color{gray}{\text{76}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3texta4`: $\color{gray}{\text{Magdplev}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3textb4`: $\color{gray}{\text{skillname}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3calca4`: $\color{gray}{\text{par8}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)

### bone spirit
- `dsc3line3`: $\color{gray}{\text{76}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3texta3`: $\color{gray}{\text{Magdplev}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3textb3`: $\color{gray}{\text{skillname}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3calca3`: $\color{gray}{\text{par8}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3line5`: $\color{gray}{\text{76}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3texta5`: $\color{gray}{\text{Magdplev}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3textb5`: $\color{gray}{\text{skillname}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3calca5`: $\color{gray}{\text{par8}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)

### fire ball
- `desccalca3`: $\color{gray}{\text{min(3,1+lvl/10)}}$ (Old) &rarr; $\color{blue}{\text{min(3,1+skill('Fire Ball'.blvl)/10}}$ (New)

### frenzy
- `dsc2calca2`: $\color{gray}{\text{par7+skill('Increased Stamina'.blvl)*10}}$ (Old) &rarr; $\color{blue}{\text{par7+skill('Increased Endurance'.blvl)*10}}$ (New)

### holy bolt
- `desccalca5`: $\color{gray}{\text{min(3,1+lvl/10)}}$ (Old) &rarr; $\color{blue}{\text{min(5,1+skill('Holy Bolt'.blvl)/5}}$ (New)

### multiple shot
- `ddam calc1`: $\color{gray}{\text{skill('Guided Arrow'.blvl) * par4}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc2calca1`: $\color{gray}{\text{(96*100/128)+(skill('Guided Arrow'.blvl)*par4)}}$ (Old) &rarr; $\color{blue}{\text{96*100/128}}$ (New)

### poison dagger
- `dsc2line1`: $\color{gray}{\text{*empty*}}$ (Old) &rarr; $\color{blue}{\text{36}}$ (New)
- `dsc2texta1`: $\color{gray}{\text{*empty*}}$ (Old) &rarr; $\color{blue}{\text{StrSkillRadiusSingular}}$ (New)
- `dsc2calca1`: $\color{gray}{\text{*empty*}}$ (Old) &rarr; $\color{blue}{\text{5}}$ (New)

### strafe
- `ddam calc1`: $\color{gray}{\text{ln12 + (skill('Guided Arrow'.blvl)*par8) + (skill('Multiple Shot'.blvl)*par9)}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `desccalca1`: $\color{gray}{\text{ln12 + (skill('Guided Arrow'.blvl)*par8) + (skill('Multiple Shot'.blvl)*par9)}}$ (Old) &rarr; $\color{blue}{\text{ln12}}$ (New)

### teeth
- `dsc3line2`: $\color{gray}{\text{76}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3texta2`: $\color{gray}{\text{Magdplev}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3textb2`: $\color{gray}{\text{skillname}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3calca2`: $\color{gray}{\text{par8}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3line4`: $\color{gray}{\text{76}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3texta4`: $\color{gray}{\text{Magdplev}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3textb4`: $\color{gray}{\text{skillname}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)
- `dsc3calca4`: $\color{gray}{\text{par8}}$ (Old) &rarr; $\color{blue}{\text{*empty*}}$ (New)

### wearwolf
- `dsc2calca3`: $\color{gray}{\text{par2+skill('shape shifting'.ln34)}}$ (Old) &rarr; $\color{blue}{\text{par2+skill('Shape Shifting'.ln34)}}$ (New)

