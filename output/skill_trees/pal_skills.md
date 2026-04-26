# Paladin Skill Tree

## Life Contributor

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Damage}$ | $\\text{Complex}$ | $\\text{+180+blvl*15+blvl*5\\%}$ | $\\text{+315+blvl*15+blvl*5\\%}$ | $\\text{+465+blvl*15+blvl*5\\%}$ | $\\text{+615+blvl*15+blvl*5\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+7\\%)}$ | $\\text{+20\\%}$ | $\\text{+83\\%}$ | $\\text{+153\\%}$ | $\\text{+223\\%}$ | $\\text{--}$ |

### Synergies
* **Redemption**: \+15% Damage per Level
* **Fanaticism**: \+5% Damage per Level

---

## Smite

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Stun Length}$ | $\\text{Complex}$ | $\\text{min(250,15)s}$ | $\\text{min(250,60)s}$ | $\\text{min(250,110)s}$ | $\\text{min(250,160)s}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+15\\%)}$ | $\\text{+15\\%}$ | $\\text{+150\\%}$ | $\\text{+300\\%}$ | $\\text{+450\\%}$ | $\\text{--}$ |

---

## Might

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+10\\%)}$ | $\\text{+40\\%}$ | $\\text{+130\\%}$ | $\\text{+230\\%}$ | $\\text{+330\\%}$ | $\\text{--}$ |

---

## Prayer

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0 dmg/s)}$ | $\\text{0.00 dmg/s}$ | $\\text{0.00 dmg/s}$ | $\\text{0.00 dmg/s}$ | $\\text{0.00 dmg/s}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Heals}$ | $\\text{Linear (+1) [Soft: +2]}$ | $\\text{+2}$ | $\\text{+11}$ | $\\text{+25}$ | $\\text{+47}$ | $\\text{--}$ |

---

## Resist Fire

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Maximum Fire Resist: + (Passive)}$ | $\\text{Complex}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{--}$ |
| $\\text{Maximum Fire Resist: + (Active)}$ | $\\text{Complex}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{--}$ |
| $\\text{Resist Fire}$ | $\\text{Diminishing (+15 -> +3\\%) [Soft: +1\\%]}$ | $\\text{+37\\%}$ | $\\text{+108\\%}$ | $\\text{+129\\%}$ | $\\text{+138\\%}$ | $\\text{Max: 154.0\\%}$ |

---

## Holy Bolt

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.06)}$ | $\\text{2.00}$ | $\\text{2.56}$ | $\\text{3.19}$ | $\\text{3.81}$ | $\\text{--}$ |
| $\\text{Heals}$ | $\\text{Complex}$ | $\\text{1 * (100 + blvl * 20) / 100-1 * (100 + blvl * 20) / 100}$ | $\\text{1 * (100 + blvl * 20) / 100-37 * (100 + blvl * 20) / 100}$ | $\\text{1 * (100 + blvl * 20) / 100-77 * (100 + blvl * 20) / 100}$ | $\\text{1 * (100 + blvl * 20) / 100-117 * (100 + blvl * 20) / 100}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Variable}$ | $\\text{8.00-16.00}$ | $\\text{84.00-94.00}$ | $\\text{196.00-220.00}$ | $\\text{358.00-404.00}$ | $\\text{--}$ |
| $\\text{Holy Bolts}$ | $\\text{Complex}$ | $\\text{min(5,1+blvl/5)}$ | $\\text{min(5,1+blvl/5)}$ | $\\text{min(5,1+blvl/5)}$ | $\\text{min(5,1+blvl/5)}$ | $\\text{--}$ |

### Synergies
* **Fist of the Heavens**: \+15% Magic Damage per Level
* **Prayer**: \+20% Damage per Level

---

## Holy Fire

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{12y}$ | $\\text{30y}$ | $\\text{50y}$ | $\\text{70y}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Variable}$ | $\\text{2.00-12.00}$ | $\\text{17.00-60.00}$ | $\\text{65.00-176.00}$ | $\\text{135.00-336.00}$ | $\\text{--}$ |
| $\\text{Fire Damage: - to your attack}$ | $\\text{Linear (+0)}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{--}$ |

### Synergies
* **Resist Fire**: \+21% Damage per Level
* **Salvation**: \+10% Damage per Level

---

## Thorns

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Attacker Takes Damage of}$ | $\\text{Accelerating (+5 -> +10) [Soft: +15]}$ | $\\text{5.00}$ | $\\text{60.00}$ | $\\text{180.00}$ | $\\text{380.00}$ | $\\text{--}$ |
| $\\text{damage returned}$ | $\\text{Linear (+30\\%)}$ | $\\text{500\\%}$ | $\\text{770\\%}$ | $\\text{1070\\%}$ | $\\text{1370\\%}$ | $\\text{--}$ |

---

## Defiance

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Defense}$ | $\\text{Linear (+10\\%)}$ | $\\text{+70\\%}$ | $\\text{+160\\%}$ | $\\text{+260\\%}$ | $\\text{+360\\%}$ | $\\text{--}$ |

---

## Resist Cold

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Maximum Cold Resist: + (Passive)}$ | $\\text{Complex}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{--}$ |
| $\\text{Maximum Cold Resist: + (Active)}$ | $\\text{Complex}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{--}$ |
| $\\text{Resist Cold}$ | $\\text{Diminishing (+15 -> +3\\%) [Soft: +1\\%]}$ | $\\text{+37\\%}$ | $\\text{+108\\%}$ | $\\text{+129\\%}$ | $\\text{+138\\%}$ | $\\text{Max: 154.0\\%}$ |

---

## Zeal

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Damage}$ | $\\text{Complex}$ | $\\text{+( 0  if (((lvl < 5) ) else  ((lvl-4) * 10) )+blvl*12)\\%}$ | $\\text{+( 0  if (((lvl < 5) ) else  ((lvl-4) * 10) )+blvl*12)\\%}$ | $\\text{+( 0  if (((lvl < 5) ) else  ((lvl-4) * 10) )+blvl*12)\\%}$ | $\\text{+( 0  if (((lvl < 5) ) else  ((lvl-4) * 10) )+blvl*12)\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+10\\%)}$ | $\\text{+10\\%}$ | $\\text{+100\\%}$ | $\\text{+200\\%}$ | $\\text{+300\\%}$ | $\\text{--}$ |
| $\\text{hits}$ | $\\text{Complex}$ | $\\text{min((3 + lvl -1), 3)}$ | $\\text{min((3 + lvl -1), 3)}$ | $\\text{min((3 + lvl -1), 3)}$ | $\\text{min((3 + lvl -1), 3)}$ | $\\text{--}$ |

### Synergies
* **Life Contributor**: \+12% Damage per Level

---

## Charge

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Damage}$ | $\\text{Complex}$ | $\\text{+100+(blvl+blvl)*20\\%}$ | $\\text{+325+(blvl+blvl)*20\\%}$ | $\\text{+575+(blvl+blvl)*20\\%}$ | $\\text{+825+(blvl+blvl)*20\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+15\\%)}$ | $\\text{+50\\%}$ | $\\text{+185\\%}$ | $\\text{+335\\%}$ | $\\text{+485\\%}$ | $\\text{--}$ |

### Synergies
* **Vigor**: \+20% Damage per Level
* **Might**: \+20% Damage per Level

---

## Concentration

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+15\\%)}$ | $\\text{+60\\%}$ | $\\text{+195\\%}$ | $\\text{+345\\%}$ | $\\text{+495\\%}$ | $\\text{--}$ |

---

## Cleansing

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Duration reduced by}$ | $\\text{Diminishing (+9 -> +2\\%) [Soft: +1\\%]}$ | $\\text{27\\%}$ | $\\text{66\\%}$ | $\\text{78\\%}$ | $\\text{83\\%}$ | $\\text{Max: 92.0\\%}$ |

### Synergies
* **Prayer**: \+2% Damage per Level

---

## Resist Lightning

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Maximum Lightning Resist: + (Passive)}$ | $\\text{Complex}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{--}$ |
| $\\text{Maximum Lightning Resist: + (Active)}$ | $\\text{Complex}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{( 1  if ((blvl < 1) ) else  blvl)\\%}$ | $\\text{--}$ |
| $\\text{Resist Lightning}$ | $\\text{Diminishing (+15 -> +3\\%) [Soft: +1\\%]}$ | $\\text{+37\\%}$ | $\\text{+108\\%}$ | $\\text{+129\\%}$ | $\\text{+138\\%}$ | $\\text{Max: 154.0\\%}$ |

---

## Vengeance

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.25)}$ | $\\text{1.00}$ | $\\text{3.25}$ | $\\text{5.75}$ | $\\text{8.25}$ | $\\text{--}$ |
| $\\text{Lightning Damage}$ | $\\text{Complex}$ | $\\text{+500+blvl*20+blvl*15\\%}$ | $\\text{+725+blvl*20+blvl*15\\%}$ | $\\text{+975+blvl*20+blvl*15\\%}$ | $\\text{+1225+blvl*20+blvl*15\\%}$ | $\\text{--}$ |
| $\\text{Cold Length}$ | $\\text{Linear (+45s)}$ | $\\text{30s}$ | $\\text{435s}$ | $\\text{885s}$ | $\\text{1335s}$ | $\\text{--}$ |
| $\\text{Cold Damage}$ | $\\text{Complex}$ | $\\text{+500+blvl*20+blvl*15\\%}$ | $\\text{+725+blvl*20+blvl*15\\%}$ | $\\text{+975+blvl*20+blvl*15\\%}$ | $\\text{+1225+blvl*20+blvl*15\\%}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Complex}$ | $\\text{+500+blvl*20+blvl*15\\%}$ | $\\text{+725+blvl*20+blvl*15\\%}$ | $\\text{+975+blvl*20+blvl*15\\%}$ | $\\text{+1225+blvl*20+blvl*15\\%}$ | $\\text{--}$ |
| $\\text{hits}$ | $\\text{Complex}$ | $\\text{min((0 + lvl -1), 0)}$ | $\\text{min((0 + lvl -1), 0)}$ | $\\text{min((0 + lvl -1), 0)}$ | $\\text{min((0 + lvl -1), 0)}$ | $\\text{--}$ |

### Synergies
* **Resist Fire**: \+20% Damage per Level
* **Resist Cold**: \+20% Damage per Level
* **Resist Lightning**: \+20% Damage per Level
* **Conviction**: \+15% Damage per Level

---

## Blessed Hammer

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.25)}$ | $\\text{5.00}$ | $\\text{7.25}$ | $\\text{9.75}$ | $\\text{12.25}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Accelerating (+8 -> +10) [Soft: +12]}$ | $\\text{12.00-16.00}$ | $\\text{88.00-92.00}$ | $\\text{196.00-200.00}$ | $\\text{326.00-330.00}$ | $\\text{--}$ |

### Synergies
* **Blessed Aim**: \+14% Magic Damage per Level
* **Vigor**: \+14% Magic Damage per Level

---

## Blessed Aim

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Attack Rating: + (Passive)}$ | $\\text{Complex}$ | $\\text{( 5  if ((blvl < 1) ) else  blvl * 5)\\%}$ | $\\text{( 5  if ((blvl < 1) ) else  blvl * 5)\\%}$ | $\\text{( 5  if ((blvl < 1) ) else  blvl * 5)\\%}$ | $\\text{( 5  if ((blvl < 1) ) else  blvl * 5)\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating: + (Active)}$ | $\\text{Linear (+15\\%)}$ | $\\text{75\\%}$ | $\\text{210\\%}$ | $\\text{360\\%}$ | $\\text{510\\%}$ | $\\text{--}$ |

---

## Holy Freeze

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{12y}$ | $\\text{30y}$ | $\\text{50y}$ | $\\text{70y}$ | $\\text{--}$ |
| $\\text{Enemies slowed}$ | $\\text{Diminishing (+6 -> +1\\%)}$ | $\\text{14\\%}$ | $\\text{43\\%}$ | $\\text{51\\%}$ | $\\text{55\\%}$ | $\\text{Max: 62.0\\%}$ |
| $\\text{Cold Damage}$ | $\\text{Variable}$ | $\\text{2.00-6.00}$ | $\\text{13.00-28.00}$ | $\\text{37.00-76.00}$ | $\\text{77.00-156.00}$ | $\\text{--}$ |
| $\\text{Cold Damage: - to your attack}$ | $\\text{Linear (+0)}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{--}$ |

### Synergies
* **Resist Cold**: \+15% Damage per Level
* **Salvation**: \+7% Damage per Level

---

## Vigor

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+6y)}$ | $\\text{32y}$ | $\\text{86y}$ | $\\text{146y}$ | $\\text{206y}$ | $\\text{--}$ |
| $\\text{Stamina Recovery Rate}$ | $\\text{Linear (+25\\%)}$ | $\\text{+50\\%}$ | $\\text{+275\\%}$ | $\\text{+525\\%}$ | $\\text{+775\\%}$ | $\\text{--}$ |
| $\\text{Run/Walk Speed}$ | $\\text{Diminishing (+4 -> +1\\%)}$ | $\\text{+21\\%}$ | $\\text{+39\\%}$ | $\\text{+44\\%}$ | $\\text{+47\\%}$ | $\\text{Max: 51.0\\%}$ |

---

## Conversion

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Chance to convert}$ | $\\text{Accelerating (-37 -> -7\\%) [Soft: -3\\%]}$ | $\\text{351\\%}$ | $\\text{186\\%}$ | $\\text{137\\%}$ | $\\text{115\\%}$ | $\\text{--}$ |

---

## Holy Shield

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Successful Blocking}$ | $\\text{Accelerating (-117852 -> -24264\\%) [Soft: -9401\\%]}$ | $\\text{+842862\\%}$ | $\\text{+312527\\%}$ | $\\text{+153879\\%}$ | $\\text{+83369\\%}$ | $\\text{--}$ |
| $\\text{Defense}$ | $\\text{Complex}$ | $\\text{+25+blvl*15\\%}$ | $\\text{+160+blvl*15\\%}$ | $\\text{+310+blvl*15\\%}$ | $\\text{+460+blvl*15\\%}$ | $\\text{--}$ |
| $\\text{Smite Damage}$ | $\\text{Accelerating (+2 -> +3) [Soft: +4]}$ | $\\text{+3}$ | $\\text{+23}$ | $\\text{+57}$ | $\\text{+97}$ | $\\text{--}$ |

### Synergies
* **Defiance**: \+15% Damage per Level

---

## Holy Shock

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{12y}$ | $\\text{30y}$ | $\\text{50y}$ | $\\text{70y}$ | $\\text{--}$ |
| $\\text{Lightning Damage}$ | $\\text{Variable}$ | $\\text{1.00-20.00}$ | $\\text{1.00-136.00}$ | $\\text{1.00-312.00}$ | $\\text{1.00-556.00}$ | $\\text{Static: 1.0/--}$ |
| $\\text{Lightning Damage: - to your attack}$ | $\\text{Linear (+0)}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{0.00-0.00}$ | $\\text{--}$ |

### Synergies
* **Resist Lightning**: \+12% Damage per Level
* **Salvation**: \+4% Damage per Level

---

## Sanctuary

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{16y}$ | $\\text{34y}$ | $\\text{54y}$ | $\\text{74y}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Variable}$ | $\\text{8.00-32.00}$ | $\\text{44.00-108.00}$ | $\\text{88.00-216.00}$ | $\\text{140.00-340.00}$ | $\\text{--}$ |
| $\\text{Damage to Undead}$ | $\\text{Linear (+50\\%)}$ | $\\text{+200\\%}$ | $\\text{+650\\%}$ | $\\text{+1150\\%}$ | $\\text{+1650\\%}$ | $\\text{--}$ |

### Synergies
* **Cleansing**: \+35% Magic Damage per Level
* **Fist of the Heavens**: \+35% Magic Damage per Level

---

## Meditation

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Mana Recovery Rate}$ | $\\text{Complex}$ | $\\text{+In34\\%}$ | $\\text{+In34\\%}$ | $\\text{+In34\\%}$ | $\\text{+In34\\%}$ | $\\text{--}$ |

### Synergies
* **Prayer**: \+2% Damage per Level

---

## Fist of the Heavens

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Holy Bolt Damage}$ | $\\text{Complex}$ | $\\text{m1en-m1ex}$ | $\\text{m1en-m1ex}$ | $\\text{m1en-m1ex}$ | $\\text{m1en-m1ex}$ | $\\text{--}$ |
| $\\text{Lightning Damage}$ | $\\text{Accelerating (+15 -> +30) [Soft: +45]}$ | $\\text{150.00-200.00}$ | $\\text{315.00-365.00}$ | $\\text{675.00-725.00}$ | $\\text{1225.00-1275.00}$ | $\\text{--}$ |

### Synergies
* **Holy Bolt**: \+9% Damage per Level
* **Holy Shock**: \+7% Damage per Level

---

## Fanaticism

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{22y}$ | $\\text{40y}$ | $\\text{60y}$ | $\\text{80y}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Diminishing (+3 -> +1\\%) [Soft: +0\\%]}$ | $\\text{+15\\%}$ | $\\text{+30\\%}$ | $\\text{+35\\%}$ | $\\text{+37\\%}$ | $\\text{Max: 41.0\\%}$ |
| $\\text{Party Damage}$ | $\\text{Linear (+8.5\\%)}$ | $\\text{+25.00\\%}$ | $\\text{+101.50\\%}$ | $\\text{+186.50\\%}$ | $\\text{+271.50\\%}$ | $\\text{--}$ |
| $\\text{Your Damage}$ | $\\text{Linear (+17\\%)}$ | $\\text{+50\\%}$ | $\\text{+203\\%}$ | $\\text{+373\\%}$ | $\\text{+543\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+5\\%)}$ | $\\text{+40\\%}$ | $\\text{+85\\%}$ | $\\text{+135\\%}$ | $\\text{+185\\%}$ | $\\text{--}$ |

---

## Conviction

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+0y)}$ | $\\text{40y}$ | $\\text{40y}$ | $\\text{40y}$ | $\\text{40y}$ | $\\text{Static: 40.0y}$ |
| $\\text{Resist All}$ | $\\text{Complex}$ | $\\text{-min(30,150)\\%}$ | $\\text{-min(75,150)\\%}$ | $\\text{-min(125,150)\\%}$ | $\\text{-min(175,150)\\%}$ | $\\text{--}$ |
| $\\text{Defense}$ | $\\text{Accelerating (-10 -> -1\\%)}$ | $\\text{-32\\%}$ | $\\text{-75\\%}$ | $\\text{-87\\%}$ | $\\text{-93\\%}$ | $\\text{--}$ |

---

## Redemption

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Life/Mana Recovered}$ | $\\text{Linear (+5)}$ | $\\text{25}$ | $\\text{70}$ | $\\text{120}$ | $\\text{170}$ | $\\text{--}$ |
| $\\text{Chance to redeem soul}$ | $\\text{Diminishing (+10 -> +2\\%) [Soft: +0\\%]}$ | $\\text{29\\%}$ | $\\text{73\\%}$ | $\\text{87\\%}$ | $\\text{93\\%}$ | $\\text{Max: 103.0\\%}$ |

---

## Salvation

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+4y)}$ | $\\text{32y}$ | $\\text{68y}$ | $\\text{108y}$ | $\\text{148y}$ | $\\text{--}$ |
| $\\text{Resist All}$ | $\\text{Diminishing (+12 -> +3\\%) [Soft: +0\\%]}$ | $\\text{+32\\%}$ | $\\text{+87\\%}$ | $\\text{+104\\%}$ | $\\text{+111\\%}$ | $\\text{Max: 123.0\\%}$ |

---

