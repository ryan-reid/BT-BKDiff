# Warlock Skill Tree

## Summon Goatman

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{15.00}$ | $\\text{19.50}$ | $\\text{24.50}$ | $\\text{29.50}$ | $\\text{--}$ |
| $\\text{Defense}$ | $\\text{Linear (+35)}$ | $\\text{100}$ | $\\text{415}$ | $\\text{765}$ | $\\text{1115}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Linear (+70)}$ | $\\text{50}$ | $\\text{680}$ | $\\text{1380}$ | $\\text{2080}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+65)}$ | $\\text{+65}$ | $\\text{+650}$ | $\\text{+1300}$ | $\\text{+1950}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Complex}$ | $\\text{+min(1, 25)+(5)\\%}$ | $\\text{+min(316, 25)+(14)\\%}$ | $\\text{+min(666, 25)+(24)\\%}$ | $\\text{+min(1016, 25)+(34)\\%}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+0)}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{--}$ |

### Synergies
* **Death Mark**: \+1% Damage per Level

---

## Demonic Mastery

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Run/Walk Speed}$ | $\\text{Linear (+0\\%)}$ | $\\text{+5\\%}$ | $\\text{+5\\%}$ | $\\text{+5\\%}$ | $\\text{+5\\%}$ | $\\text{Static: 5.0\\%}$ |
| $\\text{Damage}$ | $\\text{Linear (+5\\%)}$ | $\\text{+1\\%}$ | $\\text{+46\\%}$ | $\\text{+96\\%}$ | $\\text{+146\\%}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Complex}$ | $\\text{+min(5.25)\\%}$ | $\\text{+min(14.25)\\%}$ | $\\text{+min(24.25)\\%}$ | $\\text{+min(34.25)\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+25)}$ | $\\text{+25}$ | $\\text{+250}$ | $\\text{+500}$ | $\\text{+750}$ | $\\text{--}$ |
| $\\text{Max Demons}$ | $\\text{Complex}$ | $\\text{(3 if (((lvl>=20)) else ((lvl>=10)?2:1)))}$ | $\\text{(3 if (((lvl>=20)) else ((lvl>=10)?2:1)))}$ | $\\text{(3 if (((lvl>=20)) else ((lvl>=10)?2:1)))}$ | $\\text{(3 if (((lvl>=20)) else ((lvl>=10)?2:1)))}$ | $\\text{--}$ |

---

## Death Mark

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.25)}$ | $\\text{2.25}$ | $\\text{4.50}$ | $\\text{7.00}$ | $\\text{9.50}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Linear (+13s)}$ | $\\text{125s}$ | $\\text{242s}$ | $\\text{372s}$ | $\\text{502s}$ | $\\text{--}$ |
| $\\text{Defense}$ | $\\text{Linear (-35)}$ | $\\text{-50}$ | $\\text{-365}$ | $\\text{-715}$ | $\\text{-1065}$ | $\\text{--}$ |
| $\\text{Magic Damage Increased by}$ | $\\text{Linear (+2)}$ | $\\text{5}$ | $\\text{23}$ | $\\text{43}$ | $\\text{63}$ | $\\text{--}$ |
| $\\text{Damage Increased by}$ | $\\text{Linear (+2)}$ | $\\text{5}$ | $\\text{23}$ | $\\text{43}$ | $\\text{63}$ | $\\text{--}$ |

---

## Summon Tainted

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{25.00}$ | $\\text{29.50}$ | $\\text{34.50}$ | $\\text{39.50}$ | $\\text{--}$ |
| $\\text{Defense}$ | $\\text{Linear (+20)}$ | $\\text{75}$ | $\\text{255}$ | $\\text{455}$ | $\\text{655}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Linear (+70)}$ | $\\text{50}$ | $\\text{680}$ | $\\text{1380}$ | $\\text{2080}$ | $\\text{--}$ |
| $\\text{Resist Fire}$ | $\\text{Linear (+1\\%)}$ | $\\text{+1\\%}$ | $\\text{+10\\%}$ | $\\text{+20\\%}$ | $\\text{+30\\%}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Complex}$ | $\\text{(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*1)/100))-(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*1)/100))}$ | $\\text{(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*361)/100))-(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*361)/100))}$ | $\\text{(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*761)/100))-(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*761)/100))}$ | $\\text{(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*1161)/100))-(lvl if (((lvl > 4)) else (lvl))+((((lvl > 4)?lvl:(lvl))*1161)/100))}$ | $\\text{--}$ |

### Synergies
* **Blood Boil**: \+0% Damage per Level

---

## Summon Defiler

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{35.00}$ | $\\text{39.50}$ | $\\text{44.50}$ | $\\text{49.50}$ | $\\text{--}$ |
| $\\text{Defense}$ | $\\text{Linear (+20)}$ | $\\text{125}$ | $\\text{305}$ | $\\text{505}$ | $\\text{705}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Linear (+70)}$ | $\\text{50}$ | $\\text{680}$ | $\\text{1380}$ | $\\text{2080}$ | $\\text{--}$ |
| $\\text{Damage Shared Between Bound Targets}$ | $\\text{Linear (+1\\%)}$ | $\\text{1.00\\%}$ | $\\text{10.00\\%}$ | $\\text{20.00\\%}$ | $\\text{30.00\\%}$ | $\\text{--}$ |
| $\\text{Max Bound Souls}$ | $\\text{Linear (+1)}$ | $\\text{1.00}$ | $\\text{10.00}$ | $\\text{20.00}$ | $\\text{30.00}$ | $\\text{--}$ |

---

## Blood Oath

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Damage Taken Goes To your demon}$ | $\\text{Linear (+2\\%)}$ | $\\text{+5\\%}$ | $\\text{+23\\%}$ | $\\text{+43\\%}$ | $\\text{+63\\%}$ | $\\text{--}$ |
| $\\text{Physical Damage to your demon Reduced by}$ | $\\text{Linear (+0\\%)}$ | $\\text{5\\%}$ | $\\text{5\\%}$ | $\\text{5\\%}$ | $\\text{5\\%}$ | $\\text{Static: 5.0\\%}$ |
| $\\text{Resist All for your demon}$ | $\\text{Diminishing (+9 -> +2\\%) [Soft: +1\\%]}$ | $\\text{+16\\%}$ | $\\text{+55\\%}$ | $\\text{+67\\%}$ | $\\text{+72\\%}$ | $\\text{Max: 81.0\\%}$ |
| $\\text{Life of your demon}$ | $\\text{Linear (+35\\%)}$ | $\\text{+50\\%}$ | $\\text{+365\\%}$ | $\\text{+715\\%}$ | $\\text{+1065\\%}$ | $\\text{--}$ |

---

## Engorge

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.25)}$ | $\\text{3.00}$ | $\\text{5.25}$ | $\\text{7.75}$ | $\\text{10.25}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Linear (+75s)}$ | $\\text{125s}$ | $\\text{800s}$ | $\\text{1550s}$ | $\\text{2300s}$ | $\\text{--}$ |
| $\\text{Life Steal}$ | $\\text{Linear (+15\\%)}$ | $\\text{+1\\%}$ | $\\text{+136\\%}$ | $\\text{+286\\%}$ | $\\text{+436\\%}$ | $\\text{--}$ |
| $\\text{Heal Demon's Life}$ | $\\text{Linear (+1\\%)}$ | $\\text{+30\\%}$ | $\\text{+39\\%}$ | $\\text{+49\\%}$ | $\\text{+59\\%}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Complex}$ | $\\text{+min(15, 35)\\%}$ | $\\text{+min(24, 35)\\%}$ | $\\text{+min(34, 35)\\%}$ | $\\text{+min(44, 35)\\%}$ | $\\text{--}$ |

### Synergies
* **Blood Oath**: \+25% Damage per Level
* **Blood Oath**: \+5% Damage per Level

---

## Blood Boil

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.25)}$ | $\\text{3.75}$ | $\\text{6.00}$ | $\\text{8.50}$ | $\\text{11.00}$ | $\\text{--}$ |
| $\\text{Demon's Life Cost}$ | $\\text{Complex}$ | $\\text{max(15, 5)\\%}$ | $\\text{max(6, 5)\\%}$ | $\\text{max(-4, 5)\\%}$ | $\\text{max(-14, 5)\\%}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+1y)}$ | $\\text{12y}$ | $\\text{21y}$ | $\\text{31y}$ | $\\text{41y}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Variable}$ | $\\text{10.00-20.00}$ | $\\text{86.00-114.00}$ | $\\text{194.00-258.00}$ | $\\text{354.00-510.00}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Variable}$ | $\\text{10-20}$ | $\\text{86-114}$ | $\\text{194-258}$ | $\\text{354-510}$ | $\\text{--}$ |

### Synergies
* **Blood Oath**: \+20% Damage per Level
* **Engorge**: \+20% Damage per Level

---

## Consume

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{25.00}$ | $\\text{34.00}$ | $\\text{44.00}$ | $\\text{54.00}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Linear (+500s)}$ | $\\text{1000s}$ | $\\text{5500s}$ | $\\text{10500s}$ | $\\text{15500s}$ | $\\text{--}$ |
| $\\text{Run/Walk Speed}$ | $\\text{Accelerating (-113 -> -24\\%) [Soft: -9\\%]}$ | $\\text{+850\\%}$ | $\\text{+344\\%}$ | $\\text{+192\\%}$ | $\\text{+125\\%}$ | $\\text{--}$ |
| $\\text{Max Life}$ | $\\text{Linear (+1\\%)}$ | $\\text{+5\\%}$ | $\\text{+14\\%}$ | $\\text{+24\\%}$ | $\\text{+34\\%}$ | $\\text{--}$ |

---

## Bind Demon

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{25.00}$ | $\\text{34.00}$ | $\\text{44.00}$ | $\\text{54.00}$ | $\\text{--}$ |
| $\\text{Chance to Bind}$ | $\\text{Complex}$ | $\\text{4+((blvl*100)/100)\\%}$ | $\\text{19+((blvl*100)/100)\\%}$ | $\\text{24+((blvl*100)/100)\\%}$ | $\\text{26+((blvl*100)/100)\\%}$ | $\\text{--}$ |
| $\\text{Life of your demon}$ | $\\text{Linear (+0\\%)}$ | $\\text{+0\\%}$ | $\\text{+0\\%}$ | $\\text{+0\\%}$ | $\\text{+0\\%}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+29)}$ | $\\text{+7}$ | $\\text{+268}$ | $\\text{+558}$ | $\\text{+848}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+10\\%)}$ | $\\text{+76\\%}$ | $\\text{+166\\%}$ | $\\text{+266\\%}$ | $\\text{+366\\%}$ | $\\text{--}$ |

### Synergies
* **Death Mark**: \+1\.00% Damage per Level

---

## Levitation Mastery

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Weapon Requirements}$ | $\\text{Complex}$ | $\\text{+mair\\%}$ | $\\text{+mair\\%}$ | $\\text{+mair\\%}$ | $\\text{+mair\\%}$ | $\\text{--}$ |
| $\\text{Critical Strike Chance}$ | $\\text{Diminishing (+4 -> +0\\%)}$ | $\\text{+5\\%}$ | $\\text{+24\\%}$ | $\\text{+29\\%}$ | $\\text{+32\\%}$ | $\\text{Max: 36.0\\%}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+5\\%)}$ | $\\text{+40\\%}$ | $\\text{+85\\%}$ | $\\text{+135\\%}$ | $\\text{+185\\%}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+4\\%)}$ | $\\text{+25\\%}$ | $\\text{+61\\%}$ | $\\text{+101\\%}$ | $\\text{+141\\%}$ | $\\text{--}$ |

---

## Eldritch Blast

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{5.50}$ | $\\text{10.00}$ | $\\text{15.00}$ | $\\text{20.00}$ | $\\text{--}$ |
| $\\text{Mana Steal}$ | $\\text{Complex}$ | $\\text{+min(5, 20)\\%}$ | $\\text{+min(14, 20)\\%}$ | $\\text{+min(24, 20)\\%}$ | $\\text{+min(34, 20)\\%}$ | $\\text{--}$ |
| $\\text{Life Steal}$ | $\\text{Complex}$ | $\\text{+min(5, 20)\\%}$ | $\\text{+min(14, 20)\\%}$ | $\\text{+min(24, 20)\\%}$ | $\\text{+min(34, 20)\\%}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Accelerating (+3 -> +6) [Soft: +9]}$ | $\\text{2.00-6.00}$ | $\\text{35.00-39.00}$ | $\\text{107.00-111.00}$ | $\\text{249.00-253.00}$ | $\\text{--}$ |

### Synergies
* **Hex: Purge**: \+50% Magic Damage per Level
* **Blade Warp**: \+50% Magic Damage per Level
* **Psychic Ward**: \+2\.00% Damage per Level

---

## Hex: Bane

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{6.00}$ | $\\text{10.50}$ | $\\text{15.50}$ | $\\text{20.50}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Complex}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{--}$ |
| $\\text{[PH] Effect Length}$ | $\\text{Complex}$ | $\\text{min(250,0)s}$ | $\\text{min(250,0)s}$ | $\\text{min(250,0)s}$ | $\\text{min(250,0)s}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Variable}$ | $\\text{9.00-16.00}$ | $\\text{44.00-69.00}$ | $\\text{130.00-175.00}$ | $\\text{280.00-345.00}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+9\\%)}$ | $\\text{+20\\%}$ | $\\text{+101\\%}$ | $\\text{+191\\%}$ | $\\text{+281\\%}$ | $\\text{--}$ |

### Synergies
* **Mirrored Blades**: \+35% Magic Damage per Level
* **Hex: Purge**: \+35% Magic Damage per Level
* **Consume**: \+35% Magic Damage per Level

---

## Hex: Siphon

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{12.50}$ | $\\text{17.00}$ | $\\text{22.00}$ | $\\text{27.00}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Complex}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{--}$ |
| $\\text{Life After Each Kill}$ | $\\text{Complex}$ | $\\text{+1+(((blvl) *1))}$ | $\\text{+10+(((blvl) *1))}$ | $\\text{+20+(((blvl) *1))}$ | $\\text{+30+(((blvl) *1))}$ | $\\text{--}$ |
| $\\text{Mana After Each Kill}$ | $\\text{Complex}$ | $\\text{+1+(((blvl) *1))}$ | $\\text{+10+(((blvl) *1))}$ | $\\text{+20+(((blvl) *1))}$ | $\\text{+30+(((blvl) *1))}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+9\\%)}$ | $\\text{+20\\%}$ | $\\text{+101\\%}$ | $\\text{+191\\%}$ | $\\text{+281\\%}$ | $\\text{--}$ |

### Synergies
* **Engorge**: \+1% Damage per Level

---

## Psychic Ward

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+2)}$ | $\\text{20.00}$ | $\\text{38.00}$ | $\\text{58.00}$ | $\\text{78.00}$ | $\\text{--}$ |
| $\\text{Stun Length}$ | $\\text{Diminishing (+6 -> +1s)}$ | $\\text{44s}$ | $\\text{70s}$ | $\\text{77s}$ | $\\text{81s}$ | $\\text{Max: 86.0s}$ |
| $\\text{Absorbs damage}$ | $\\text{Complex}$ | $\\text{(15 + (blvl + blvl) * 15)}$ | $\\text{(105 + (blvl + blvl) * 15)}$ | $\\text{(205 + (blvl + blvl) * 15)}$ | $\\text{(305 + (blvl + blvl) * 15)}$ | $\\text{--}$ |

### Synergies
* **Cleave**: \+15% Damage per Level
* **Levitation Mastery**: \+15% Damage per Level

---

## Echoing Strike

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{7.00}$ | $\\text{11.50}$ | $\\text{16.50}$ | $\\text{21.50}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+0\\%)}$ | $\\text{+0\\%}$ | $\\text{+0\\%}$ | $\\text{+0\\%}$ | $\\text{+0\\%}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Complex}$ | $\\text{8*(((((100+(30+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100-12*(((((100+(30+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100}$ | $\\text{37*(((((100+(75+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100-59*(((((100+(75+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100}$ | $\\text{85*(((((100+(125+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100-131*(((((100+(125+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100}$ | $\\text{145*(((((100+(175+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100-221*(((((100+(175+clc0))/( (1+(blvl/5))  if ((blvl > 0) ) else  1))/2)*( (1+(blvl/5))  if ((blvl > 0) ) else  1)*2)-1)/100}$ | $\\text{--}$ |
| $\\text{Damage: +}$ | $\\text{Complex}$ | $\\text{30+clc0\\%}$ | $\\text{75+clc0\\%}$ | $\\text{125+clc0\\%}$ | $\\text{175+clc0\\%}$ | $\\text{--}$ |

### Synergies
* **Mirrored Blades**: \+1% Damage per Level
* **Mirrored Blades**: \+5% Damage per Level
* **Blade Warp**: \+5% Damage per Level

---

## Hex: Purge

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{25.00}$ | $\\text{34.00}$ | $\\text{44.00}$ | $\\text{54.00}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Complex}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{lens}$ | $\\text{--}$ |
| $\\text{Magic Explosion Damage}$ | $\\text{Variable}$ | $\\text{10.00-15.00}$ | $\\text{54.00-77.00}$ | $\\text{142.00-185.00}$ | $\\text{282.00-345.00}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Complex}$ | $\\text{+min(30, 10)\\%}$ | $\\text{+min(30, 19)\\%}$ | $\\text{+min(30, 29)\\%}$ | $\\text{+min(30, 39)\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+9\\%)}$ | $\\text{+20\\%}$ | $\\text{+101\\%}$ | $\\text{+191\\%}$ | $\\text{+281\\%}$ | $\\text{--}$ |

### Synergies
* **Hex: Bane**: \+10% Magic Damage per Level
* **Eldritch Blast**: \+10% Magic Damage per Level
* **Sigil: Death**: \+1\.00% Damage per Level

---

## Blade Warp

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{Static: 15.0}$ |
| $\\text{Radius: s}$ | $\\text{Complex}$ | $\\text{leny}$ | $\\text{leny}$ | $\\text{leny}$ | $\\text{leny}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Accelerating (+3 -> +5) [Soft: +8]}$ | $\\text{8.00-10.00}$ | $\\text{39.00-41.00}$ | $\\text{101.00-103.00}$ | $\\text{181.00-183.00}$ | $\\text{--}$ |

### Synergies
* **Mirrored Blades**: \+24% Magic Damage per Level
* **Echoing Strike**: \+24% Magic Damage per Level

---

## Cleave

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{3.00}$ | $\\text{3.00}$ | $\\text{3.00}$ | $\\text{3.00}$ | $\\text{Static: 3.0}$ |
| $\\text{Cleave Arc: Degrees}$ | $\\text{Linear (+12) [Soft: +0]}$ | $\\text{132}$ | $\\text{240}$ | $\\text{240}$ | $\\text{240}$ | $\\text{Max: 240.0}$ |
| $\\text{Damage}$ | $\\text{Complex}$ | $\\text{+20+((blvl+blvl+blvl)*10)\\%}$ | $\\text{+65+((blvl+blvl+blvl)*10)\\%}$ | $\\text{+115+((blvl+blvl+blvl)*10)\\%}$ | $\\text{+165+((blvl+blvl+blvl)*10)\\%}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Linear (+1\\%) [Soft: +0\\%]}$ | $\\text{+21\\%}$ | $\\text{+26\\%}$ | $\\text{+28\\%}$ | $\\text{+29\\%}$ | $\\text{Max: 30.0\\%}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+7\\%)}$ | $\\text{+50\\%}$ | $\\text{+113\\%}$ | $\\text{+183\\%}$ | $\\text{+253\\%}$ | $\\text{--}$ |

### Synergies
* **Mirrored Blades**: \+10% Damage per Level
* **Hex: Purge**: \+10% Damage per Level
* **Eldritch Blast**: \+10% Damage per Level

---

## Mirrored Blades

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{5.00}$ | $\\text{9.50}$ | $\\text{14.50}$ | $\\text{19.50}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Accelerating (-2 -> -1\\%)}$ | $\\text{+46\\%}$ | $\\text{+36\\%}$ | $\\text{+33\\%}$ | $\\text{+31\\%}$ | $\\text{--}$ |
| $\\text{Mirrored Blade Damage}$ | $\\text{Diminishing (+8 -> +1\\%) [Soft: +0\\%]}$ | $\\text{61\\%}$ | $\\text{98\\%}$ | $\\text{109\\%}$ | $\\text{114\\%}$ | $\\text{Max: 122.0\\%}$ |

---

## Sigil: Lethargy

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{4.00}$ | $\\text{4.00}$ | $\\text{4.00}$ | $\\text{4.00}$ | $\\text{Static: 4.0}$ |
| $\\text{Duration}$ | $\\text{Linear (+1s)}$ | $\\text{5.00s}$ | $\\text{14.00s}$ | $\\text{24.00s}$ | $\\text{34.00s}$ | $\\text{--}$ |
| $\\text{Radius: s}$ | $\\text{Complex}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{--}$ |
| $\\text{Enemy Defense}$ | $\\text{Linear (-1\\%)}$ | $\\text{-33\\%}$ | $\\text{-42\\%}$ | $\\text{-52\\%}$ | $\\text{-62\\%}$ | $\\text{--}$ |
| $\\text{Damage Taken}$ | $\\text{Linear (+1\\%)}$ | $\\text{+20\\%}$ | $\\text{+29\\%}$ | $\\text{+39\\%}$ | $\\text{+49\\%}$ | $\\text{--}$ |

---

## Ring of Fire

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{8.00}$ | $\\text{12.50}$ | $\\text{17.50}$ | $\\text{22.50}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Variable}$ | $\\text{6.00-12.00}$ | $\\text{64.00-79.00}$ | $\\text{152.00-181.00}$ | $\\text{262.00-325.00}$ | $\\text{--}$ |

### Synergies
* **Flame Wave**: \+25% Damage per Level
* **Apocalypse**: \+25% Damage per Level

---

## Miasma Bolt

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{2.00}$ | $\\text{6.50}$ | $\\text{11.50}$ | $\\text{16.50}$ | $\\text{--}$ |
| $\\text{Average Magic Damage}$ | $\\text{Linear (+0) dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Variable}$ | $\\text{1.00-3.00}$ | $\\text{12.00-23.00}$ | $\\text{36.00-53.00}$ | $\\text{68.00-91.00}$ | $\\text{--}$ |

### Synergies
* **Miasma Chain**: \+10% Magic Damage per Level
* **Miasma Chain**: \+20% Magic Damage per Level
* **Abyss**: \+10% Magic Damage per Level
* **Abyss**: \+20% Magic Damage per Level

---

## Sigil: Rancor

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{12.00}$ | $\\text{12.00}$ | $\\text{12.00}$ | $\\text{12.00}$ | $\\text{Static: 12.0}$ |
| $\\text{Duration}$ | $\\text{Linear (+1s)}$ | $\\text{5.00s}$ | $\\text{14.00s}$ | $\\text{24.00s}$ | $\\text{34.00s}$ | $\\text{--}$ |
| $\\text{Radius: s}$ | $\\text{Complex}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{--}$ |
| $\\text{Attack Speed}$ | $\\text{Linear (+1\\%)}$ | $\\text{+5\\%}$ | $\\text{+14\\%}$ | $\\text{+24\\%}$ | $\\text{+34\\%}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Linear (+5\\%)}$ | $\\text{+50\\%}$ | $\\text{+95\\%}$ | $\\text{+145\\%}$ | $\\text{+195\\%}$ | $\\text{--}$ |

---

## Enhanced Entropy

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Bonus Abyss Radius: + Yards}$ | $\\text{Linear (+1y)}$ | $\\text{1y}$ | $\\text{10y}$ | $\\text{20y}$ | $\\text{30y}$ | $\\text{--}$ |
| $\\text{+ Seconds to Miasma Duration}$ | $\\text{Complex}$ | $\\text{min(lvl*5,100)s}$ | $\\text{min(lvl*5,100)s}$ | $\\text{min(lvl*5,100)s}$ | $\\text{min(lvl*5,100)s}$ | $\\text{--}$ |
| $\\text{Miasma Radius: Yards}$ | $\\text{Complex}$ | $\\text{(4 if ((lvl >= 10)) else ((lvl>=5)?3:2))y}$ | $\\text{(4 if ((lvl >= 10)) else ((lvl>=5)?3:2))y}$ | $\\text{(4 if ((lvl >= 10)) else ((lvl>=5)?3:2))y}$ | $\\text{(4 if ((lvl >= 10)) else ((lvl>=5)?3:2))y}$ | $\\text{--}$ |

---

## Flame Wave

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{7.00}$ | $\\text{11.50}$ | $\\text{16.50}$ | $\\text{21.50}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Linear (+0s)}$ | $\\text{0.28s}$ | $\\text{0.28s}$ | $\\text{0.28s}$ | $\\text{0.28s}$ | $\\text{Static: 0.28s}$ |
| $\\text{Width: s}$ | $\\text{Diminishing (+2 -> +0y)}$ | $\\text{11y}$ | $\\text{17y}$ | $\\text{19y}$ | $\\text{19y}$ | $\\text{Max: 21.0y}$ |
| $\\text{Average Fire Damage}$ | $\\text{Complex}$ | $\\text{m1en-m1ex dmg/s}$ | $\\text{m1en-m1ex dmg/s}$ | $\\text{m1en-m1ex dmg/s}$ | $\\text{m1en-m1ex dmg/s}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Variable}$ | $\\text{15.00-20.00}$ | $\\text{106.00-129.00}$ | $\\text{270.00-309.00}$ | $\\text{486.00-543.00}$ | $\\text{--}$ |

### Synergies
* **Ring of Fire**: \+25% Damage per Level
* **Ring of Fire**: \+15% Damage per Level
* **Apocalypse**: \+25% Damage per Level
* **Apocalypse**: \+15% Damage per Level

---

## Miasma Chain

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{4.50}$ | $\\text{9.00}$ | $\\text{14.00}$ | $\\text{19.00}$ | $\\text{--}$ |
| $\\text{Average Magic Damage}$ | $\\text{Linear (+0) dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{0-0 dmg/s}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Accelerating (+2 -> +3)}$ | $\\text{6.00-9.00}$ | $\\text{26.00-29.00}$ | $\\text{56.00-59.00}$ | $\\text{94.00-97.00}$ | $\\text{--}$ |
| $\\text{hits}$ | $\\text{Linear (+0)}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{--}$ |

### Synergies
* **Miasma Bolt**: \+10% Magic Damage per Level
* **Miasma Bolt**: \+20% Magic Damage per Level
* **Abyss**: \+10% Magic Damage per Level
* **Abyss**: \+20% Magic Damage per Level

---

## Sigil: Death

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{10.00}$ | $\\text{14.50}$ | $\\text{19.50}$ | $\\text{24.50}$ | $\\text{--}$ |
| $\\text{Duration}$ | $\\text{Linear (+1s)}$ | $\\text{5.00s}$ | $\\text{14.00s}$ | $\\text{24.00s}$ | $\\text{34.00s}$ | $\\text{--}$ |
| $\\text{Radius: s}$ | $\\text{Complex}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{--}$ |

---

## Apocalypse

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{32.00}$ | $\\text{41.00}$ | $\\text{51.00}$ | $\\text{61.00}$ | $\\text{--}$ |
| $\\text{Radius: s}$ | $\\text{Complex}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{rngy}$ | $\\text{--}$ |
| $\\text{Resist Fire}$ | $\\text{Complex}$ | $\\text{-min(5,40)\\%}$ | $\\text{-min(14,40)\\%}$ | $\\text{-min(24,40)\\%}$ | $\\text{-min(34,40)\\%}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Variable}$ | $\\text{80.00-100.00}$ | $\\text{333.00-375.00}$ | $\\text{885.00-975.00}$ | $\\text{1663.00-1925.00}$ | $\\text{--}$ |

### Synergies
* **Ring of Fire**: \+20% Damage per Level
* **Flame Wave**: \+20% Damage per Level

---

## Abyss

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{23.00}$ | $\\text{32.00}$ | $\\text{42.00}$ | $\\text{52.00}$ | $\\text{--}$ |
| $\\text{Average Magic Damage}$ | $\\text{Complex}$ | $\\text{(0*25)/0-(0*25)/0 dmg/s}$ | $\\text{(0*25)/0-(0*25)/0 dmg/s}$ | $\\text{(0*25)/0-(0*25)/0 dmg/s}$ | $\\text{(0*25)/0-(0*25)/0 dmg/s}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Variable}$ | $\\text{20.00-40.00}$ | $\\text{53.00-84.00}$ | $\\text{125.00-180.00}$ | $\\text{245.00-340.00}$ | $\\text{--}$ |

### Synergies
* **Miasma Bolt**: \+14% Magic Damage per Level
* **Miasma Bolt**: \+14% Magic Damage per Level
* **Miasma Chain**: \+14% Magic Damage per Level
* **Miasma Chain**: \+14% Magic Damage per Level

---

