# Necromancer Skill Tree

## Amplify Damage

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{6y}$ | $\\text{24y}$ | $\\text{44y}$ | $\\text{64y}$ | $\\text{--}$ |

---

## Teeth

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{6.00}$ | $\\text{6.00}$ | $\\text{6.00}$ | $\\text{6.00}$ | $\\text{Static: 6.0}$ |
| $\\text{Magic Damage}$ | $\\text{Linear (+6)}$ | $\\text{12.00-16.00}$ | $\\text{66.00-70.00}$ | $\\text{126.00-130.00}$ | $\\text{186.00-190.00}$ | $\\text{--}$ |
| $\\text{teeth}$ | $\\text{Complex}$ | $\\text{min(3,24)}$ | $\\text{min(12,24)}$ | $\\text{min(22,24)}$ | $\\text{min(32,24)}$ | $\\text{--}$ |

### Synergies
* **Bone Spear**: \+8% Magic Damage per Level
* **Bone Spirit**: \+8% Magic Damage per Level

---

## Spike Armor

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{11.00}$ | $\\text{20.00}$ | $\\text{30.00}$ | $\\text{40.00}$ | $\\text{--}$ |
| $\\text{Absorbs damage}$ | $\\text{Complex}$ | $\\text{(20 + (blvl + blvl) * 15)}$ | $\\text{(155 + (blvl + blvl) * 15)}$ | $\\text{(305 + (blvl + blvl) * 15)}$ | $\\text{(455 + (blvl + blvl) * 15)}$ | $\\text{--}$ |

### Synergies
* **Spike Wall**: \+15% Damage per Level
* **Spike Prison**: \+15% Damage per Level

---

## Undead Mastery

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Monsters: Damage}$ | $\\text{Linear (+10\\%)}$ | $\\text{+10\\%}$ | $\\text{+100\\%}$ | $\\text{+200\\%}$ | $\\text{+300\\%}$ | $\\text{--}$ |
| $\\text{Monsters: Life}$ | $\\text{Linear (+5\\%)}$ | $\\text{+5\\%}$ | $\\text{+50\\%}$ | $\\text{+100\\%}$ | $\\text{+150\\%}$ | $\\text{--}$ |
| $\\text{Magi: Improved Missile Damage}$ | $\\text{Diminishing (+2 -> +1)}$ | $\\text{0}$ | $\\text{10}$ | $\\text{20}$ | $\\text{30}$ | $\\text{Max: 99.0}$ |
| $\\text{Magi: Life}$ | $\\text{Linear (+25)}$ | $\\text{+25}$ | $\\text{+250}$ | $\\text{+500}$ | $\\text{+750}$ | $\\text{--}$ |
| $\\text{Skeletons: Damage}$ | $\\text{Linear (+10)}$ | $\\text{+10}$ | $\\text{+100}$ | $\\text{+200}$ | $\\text{+300}$ | $\\text{--}$ |
| $\\text{Skeletons: Life}$ | $\\text{Linear (+25)}$ | $\\text{+25}$ | $\\text{+250}$ | $\\text{+500}$ | $\\text{+750}$ | $\\text{--}$ |

---

## Raise Undead

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{6.00}$ | $\\text{15.00}$ | $\\text{25.00}$ | $\\text{35.00}$ | $\\text{--}$ |
| $\\text{skeleton total}$ | $\\text{Diminishing (+1 -> +0.34) [Soft: +0.33]}$ | $\\text{1}$ | $\\text{5.33}$ | $\\text{8.67}$ | $\\text{12.00}$ | $\\text{Max: 35.0}$ |
| $\\text{Defense}$ | $\\text{Linear (+100)}$ | $\\text{105}$ | $\\text{1005}$ | $\\text{2005}$ | $\\text{3005}$ | $\\text{--}$ |
| $\\text{Damage}$ | $\\text{Complex}$ | $\\text{+( 0  if (((lvl < 4) ) else  ((lvl-3)*10)))\\%}$ | $\\text{+( 0  if (((lvl < 4) ) else  ((lvl-3)*10)))\\%}$ | $\\text{+( 0  if (((lvl < 4) ) else  ((lvl-3)*10)))\\%}$ | $\\text{+( 0  if (((lvl < 4) ) else  ((lvl-3)*10)))\\%}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+100)}$ | $\\text{105}$ | $\\text{1005}$ | $\\text{2005}$ | $\\text{3005}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Accelerating (+0 -> +50)}$ | $\\text{0}$ | $\\text{350}$ | $\\text{850}$ | $\\text{1350}$ | $\\text{--}$ |

---

## Dim Vision

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+50s)}$ | $\\text{175s}$ | $\\text{625s}$ | $\\text{1125s}$ | $\\text{1625s}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{8y}$ | $\\text{26y}$ | $\\text{46y}$ | $\\text{66y}$ | $\\text{--}$ |

---

## Weaken

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+60s)}$ | $\\text{350s}$ | $\\text{890s}$ | $\\text{1490s}$ | $\\text{2090s}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{18y}$ | $\\text{36y}$ | $\\text{56y}$ | $\\text{76y}$ | $\\text{--}$ |
| $\\text{Enemy Damage}$ | $\\text{Linear (-1\\%)}$ | $\\text{-33\\%}$ | $\\text{-42\\%}$ | $\\text{-52\\%}$ | $\\text{-62\\%}$ | $\\text{--}$ |

---

## Poison Strike

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Accelerating (+0.62 -> +0.63) [Soft: +0.62]}$ | $\\text{2.50}$ | $\\text{8.12}$ | $\\text{14.38}$ | $\\text{20.62}$ | $\\text{--}$ |
| $\\text{over}$ | $\\text{Linear (+30s)}$ | $\\text{50s}$ | $\\text{320s}$ | $\\text{620s}$ | $\\text{920s}$ | $\\text{--}$ |
| $\\text{Poison Damage}$ | $\\text{Variable}$ | $\\text{0.69-1.53}$ | $\\text{80.66-95.70}$ | $\\text{653.91-703.86}$ | $\\text{2472.39-2577.39}$ | $\\text{--}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+20\\%)}$ | $\\text{+30\\%}$ | $\\text{+210\\%}$ | $\\text{+410\\%}$ | $\\text{+610\\%}$ | $\\text{--}$ |
| $\\text{Uninterruptable}$ | $\\text{Linear (+0)}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{--}$ |
| $\\text{Always Hits}$ | $\\text{Linear (+0)}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{--}$ |

### Synergies
* **Poison Explosion**: \+20% Poison Damage per Level
* **Poison Nova**: \+20% Poison Damage per Level

---

## Corpse Explosion

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{15.00}$ | $\\text{24.00}$ | $\\text{34.00}$ | $\\text{44.00}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+1y)}$ | $\\text{8y}$ | $\\text{17y}$ | $\\text{27y}$ | $\\text{37y}$ | $\\text{--}$ |

---

## Clay Golem

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{Static: 15.0}$ |
| $\\text{Damage}$ | $\\text{Linear (+0)}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{--}$ |
| $\\text{Slows Enemies}$ | $\\text{Diminishing (+5 -> +1\\%)}$ | $\\text{41\\%}$ | $\\text{62\\%}$ | $\\text{68\\%}$ | $\\text{71\\%}$ | $\\text{Max: 76.0\\%}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+185)}$ | $\\text{+185}$ | $\\text{+1850}$ | $\\text{+3700}$ | $\\text{+5550}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Complex}$ | $\\text{(100+(35 * (lvl - 1)))*(100+20 + (blvl*0))/100-100}$ | $\\text{(100+(35 * (lvl - 1)))*(100+200 + (blvl*0))/100-100}$ | $\\text{(100+(35 * (lvl - 1)))*(100+400 + (blvl*0))/100-100}$ | $\\text{(100+(35 * (lvl - 1)))*(100+600 + (blvl*0))/100-100}$ | $\\text{--}$ |

### Synergies
* **Dark Golem**: \+0% Damage per Level
* **Iron Golem**: \+0% Damage per Level
* **Fire Golem**: \+0% Damage per Level

---

## Iron Maiden

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+60s)}$ | $\\text{300s}$ | $\\text{840s}$ | $\\text{1440s}$ | $\\text{2040s}$ | $\\text{--}$ |
| $\\text{damage returned}$ | $\\text{Linear (+25\\%)}$ | $\\text{200\\%}$ | $\\text{425\\%}$ | $\\text{675\\%}$ | $\\text{925\\%}$ | $\\text{--}$ |

---

## Terror

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+25s)}$ | $\\text{200s}$ | $\\text{425s}$ | $\\text{675s}$ | $\\text{925s}$ | $\\text{--}$ |

---

## Spike Wall

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Life}$ | $\\text{Complex}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*10)}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*10)}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*10)}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*10)}$ | $\\text{--}$ |

### Synergies
* **Spike Armor**: \+10% Damage per Level
* **Spike Prison**: \+10% Damage per Level

---

## Golem Mastery

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Run/Walk Speed}$ | $\\text{Diminishing (+2 -> +1\\%)}$ | $\\text{+23\\%}$ | $\\text{+33\\%}$ | $\\text{+36\\%}$ | $\\text{+38\\%}$ | $\\text{Max: 40.0\\%}$ |
| $\\text{Attack Rating}$ | $\\text{Linear (+85)}$ | $\\text{+105}$ | $\\text{+870}$ | $\\text{+1720}$ | $\\text{+2570}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Linear (+20\\%)}$ | $\\text{+20\\%}$ | $\\text{+200\\%}$ | $\\text{+400\\%}$ | $\\text{+600\\%}$ | $\\text{--}$ |

---

## Raise Undead Mage

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+1)}$ | $\\text{8.00}$ | $\\text{17.00}$ | $\\text{27.00}$ | $\\text{37.00}$ | $\\text{--}$ |
| $\\text{undead mage}$ | $\\text{Diminishing (+1 -> +0.34) [Soft: +0.33]}$ | $\\text{1}$ | $\\text{5.33}$ | $\\text{8.67}$ | $\\text{12.00}$ | $\\text{Max: 35.0}$ |
| $\\text{Defense}$ | $\\text{Linear (+20)}$ | $\\text{20}$ | $\\text{200}$ | $\\text{400}$ | $\\text{600}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Accelerating (+0 -> +10)}$ | $\\text{0}$ | $\\text{70}$ | $\\text{170}$ | $\\text{270}$ | $\\text{--}$ |

---

## Confuse

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+50s)}$ | $\\text{250s}$ | $\\text{700s}$ | $\\text{1200s}$ | $\\text{1700s}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{12y}$ | $\\text{30y}$ | $\\text{50y}$ | $\\text{70y}$ | $\\text{--}$ |

---

## Life Tap

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+60s)}$ | $\\text{400s}$ | $\\text{940s}$ | $\\text{1540s}$ | $\\text{2140s}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{8y}$ | $\\text{26y}$ | $\\text{46y}$ | $\\text{66y}$ | $\\text{--}$ |

---

## Poison Explosion

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{over}$ | $\\text{Linear (+30s)}$ | $\\text{50s}$ | $\\text{320s}$ | $\\text{620s}$ | $\\text{920s}$ | $\\text{--}$ |
| $\\text{Poison Damage}$ | $\\text{Variable}$ | $\\text{0.31-0.92}$ | $\\text{20.51-31.45}$ | $\\text{177.10-213.43}$ | $\\text{754.13-830.49}$ | $\\text{--}$ |

### Synergies
* **Poison Strike**: \+15% Poison Damage per Level
* **Poison Nova**: \+15% Poison Damage per Level

---

## Bone Spear

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{15.00}$ | $\\text{Static: 15.0}$ |
| $\\text{Magic Damage}$ | $\\text{Variable}$ | $\\text{16.00-24.00}$ | $\\text{63.00-64.00}$ | $\\text{147.00-152.00}$ | $\\text{327.00-340.00}$ | $\\text{--}$ |
| $\\text{Bonespears}$ | $\\text{Complex}$ | $\\text{min(3, 1 + blvl/10) + ((lvl - blvl) / 5)}$ | $\\text{min(3, 1 + blvl/10) + ((lvl - blvl) / 5)}$ | $\\text{min(3, 1 + blvl/10) + ((lvl - blvl) / 5)}$ | $\\text{min(3, 1 + blvl/10) + ((lvl - blvl) / 5)}$ | $\\text{--}$ |

### Synergies
* **2**: \+0% Damage per Level
* **Teeth**: \+15% Magic Damage per Level

---

## Dark Golem

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{25.00}$ | $\\text{25.00}$ | $\\text{25.00}$ | $\\text{25.00}$ | $\\text{Static: 25.0}$ |
| $\\text{Damage}$ | $\\text{Linear (+0)}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{0-0}$ | $\\text{--}$ |
| $\\text{Converts damage to life}$ | $\\text{Diminishing (+9 -> +2\\%) [Soft: +1\\%]}$ | $\\text{86\\%}$ | $\\text{126\\%}$ | $\\text{138\\%}$ | $\\text{143\\%}$ | $\\text{Max: 152.0\\%}$ |
| $\\text{Life}$ | $\\text{Accelerating (+48 -> +120) [Soft: +200]}$ | $\\text{20.00}$ | $\\text{740.00}$ | $\\text{2300.00}$ | $\\text{4660.00}$ | $\\text{--}$ |

### Synergies
* **Clay Golem**: \+0% Damage per Level
* **Iron Golem**: \+0% Damage per Level
* **Fire Golem**: \+0% Damage per Level

---

## Attract

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+90s)}$ | $\\text{300s}$ | $\\text{1110s}$ | $\\text{2010s}$ | $\\text{2910s}$ | $\\text{--}$ |

---

## Decrepify

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{11.00}$ | $\\text{11.00}$ | $\\text{11.00}$ | $\\text{11.00}$ | $\\text{Static: 11.0}$ |
| $\\text{Duration}$ | $\\text{Linear (+15s)}$ | $\\text{100s}$ | $\\text{235s}$ | $\\text{385s}$ | $\\text{535s}$ | $\\text{--}$ |

---

## Spike Prison

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Complex}$ | $\\text{max(27.0, 1)}$ | $\\text{max(18.0, 1)}$ | $\\text{max(8.0, 1)}$ | $\\text{max(1.0, 1)}$ | $\\text{--}$ |
| $\\text{Life}$ | $\\text{Complex}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*8)}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*8)}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*8)}$ | $\\text{(25 * (lvl-1)) + ((blvl+blvl)*8)}$ | $\\text{--}$ |

### Synergies
* **Spike Armor**: \+8% Damage per Level
* **Spike Wall**: \+8% Damage per Level

---

## Summon Resist

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Resist All}$ | $\\text{Diminishing (+7 -> +2\\%) [Soft: +1\\%]}$ | $\\text{+28\\%}$ | $\\text{+57\\%}$ | $\\text{+66\\%}$ | $\\text{+70\\%}$ | $\\text{Max: 77.0\\%}$ |

---

## Iron Golem

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Defense}$ | $\\text{Linear (+350)}$ | $\\text{+350}$ | $\\text{+3500}$ | $\\text{+7000}$ | $\\text{+10500}$ | $\\text{--}$ |
| $\\text{damage returned}$ | $\\text{Linear (+0\\%)}$ | $\\text{0\\%}$ | $\\text{0\\%}$ | $\\text{0\\%}$ | $\\text{0\\%}$ | $\\text{--}$ |
| $\\text{Thorns damage}$ | $\\text{Linear (+0)}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{0}$ | $\\text{--}$ |

### Synergies
* **Clay Golem**: \+0% Damage per Level
* **Dark Golem**: \+0% Damage per Level
* **Fire Golem**: \+0% Damage per Level

---

## Lower Resist

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Duration}$ | $\\text{Linear (+50s)}$ | $\\text{500s}$ | $\\text{950s}$ | $\\text{1450s}$ | $\\text{1950s}$ | $\\text{--}$ |
| $\\text{Radius}$ | $\\text{Linear (+2y)}$ | $\\text{14y}$ | $\\text{32y}$ | $\\text{52y}$ | $\\text{72y}$ | $\\text{--}$ |
| $\\text{Resist All}$ | $\\text{Accelerating (-8 -> -1\\%) [Soft: +0\\%]}$ | $\\text{-16\\%}$ | $\\text{-50\\%}$ | $\\text{-60\\%}$ | $\\text{-64\\%}$ | $\\text{--}$ |

---

## Poison Nova

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{over}$ | $\\text{Linear (+0s)}$ | $\\text{50s}$ | $\\text{50s}$ | $\\text{50s}$ | $\\text{50s}$ | $\\text{Static: 50.0s}$ |
| $\\text{Poison Damage}$ | $\\text{Variable}$ | $\\text{0.61-1.11}$ | $\\text{2.14-2.63}$ | $\\text{4.88-5.38}$ | $\\text{9.99-10.49}$ | $\\text{--}$ |

### Synergies
* **Poison Strike**: \+15% Poison Damage per Level
* **Poison Explosion**: \+15% Poison Damage per Level

---

## Bone Spirit

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0.5)}$ | $\\text{5.00}$ | $\\text{9.50}$ | $\\text{14.50}$ | $\\text{19.50}$ | $\\text{--}$ |
| $\\text{Magic Damage}$ | $\\text{Linear (+20)}$ | $\\text{20.00-32.00}$ | $\\text{200.00-212.00}$ | $\\text{400.00-412.00}$ | $\\text{600.00-612.00}$ | $\\text{--}$ |

### Synergies
* **2**: \+0% Damage per Level
* **Teeth**: \+35% Magic Damage per Level

---

## Fire Golem

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Mana Cost}$ | $\\text{Linear (+0)}$ | $\\text{20.00}$ | $\\text{20.00}$ | $\\text{20.00}$ | $\\text{20.00}$ | $\\text{Static: 20.0}$ |
| $\\text{Holy Fire}$ | $\\text{Variable}$ | $\\text{906-5368.36}$ | $\\text{9206-24320.36}$ | $\\text{19606-47804.36}$ | $\\text{31606-74584.36}$ | $\\text{--}$ |
| $\\text{Fire Damage}$ | $\\text{Variable}$ | $\\text{1002046-2882263}$ | $\\text{10181929-13057555}$ | $\\text{21684433-25666069}$ | $\\text{34956553-40044199}$ | $\\text{--}$ |
| $\\text{Absorbs fire damage}$ | $\\text{Diminishing (+9 -> +2\\%) [Soft: +1\\%]}$ | $\\text{36\\%}$ | $\\text{76\\%}$ | $\\text{88\\%}$ | $\\text{93\\%}$ | $\\text{Max: 102.0\\%}$ |

### Synergies
* **Clay Golem**: \+0% Damage per Level
* **Dark Golem**: \+0% Damage per Level
* **Iron Golem**: \+0% Damage per Level

---

## Revive

| Effect | Scaling | L1 | L10 | L20 | L30 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| $\\text{Monsters}$ | $\\text{Linear (+1)}$ | $\\text{1}$ | $\\text{10}$ | $\\text{20}$ | $\\text{30}$ | $\\text{--}$ |

---

