# Warlock Skill Tree

## Summon Goatman

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 15.00 | 19.50 | 24.50 | 29.50 | -- |
| Defense | Linear (+35) | 100 | 415 | 765 | 1115 | -- |
| Life | Linear (+70) | 50 | 680 | 1380 | 2080 | -- |
| Attack Rating | Linear (+65) | +65 | +650 | +1300 | +1950 | -- |
| Attack Speed | Diminishing (+25 -> +1%) | +6% | +39% | +49% | +59% | 128.0% |
| Damage | Linear (+0) | 0-0 | 0-0 | 0-0 | 0-0 | -- |

### Synergies
* **Death Mark**: \+1% Damage per Level

---

## Demonic Mastery

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Run/Walk Speed | Linear (+0%) | +5% | +5% | +5% | +5% | Static: 5.0% |
| Damage | Linear (+5%) | +1% | +46% | +96% | +146% | -- |
| Attack Speed | Complex | +min(5.25)% | +min(14.25)% | +min(24.25)% | +min(34.25)% | -- |
| Attack Rating | Linear (+25) | +25 | +250 | +500 | +750 | -- |
| Max Demons | Complex | (3 if (((1>=20)) else ((1>=10)?2:1))) | (3 if (((10>=20)) else ((10>=10)?2:1))) | (3 if (((20>=20)) else ((20>=10)?2:1))) | (3 if (((30>=20)) else ((30>=10)?2:1))) | -- |

---

## Death Mark

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.25) | 2.25 | 4.50 | 7.00 | 9.50 | -- |
| Duration | Linear (+13s) | 125s | 242s | 372s | 502s | -- |
| Defense | Linear (-35) | -50 | -365 | -715 | -1065 | -- |
| Magic Damage Increased by | Linear (+2) | 5 | 23 | 43 | 63 | -- |
| Damage Increased by | Linear (+2) | 5 | 23 | 43 | 63 | -- |

---

## Summon Tainted

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 25.00 | 29.50 | 34.50 | 39.50 | -- |
| Defense | Linear (+20) | 75 | 255 | 455 | 655 | -- |
| Life | Linear (+70) | 50 | 680 | 1380 | 2080 | -- |
| Resist Fire | Linear (+1%) | +1% | +10% | +20% | +30% | -- |
| Fire Damage | Complex | (1 if (((1 > 4)) else (1))+((((1 > 4)?1:(1))*1)/100))-(1 if (((1 > 4)) else (1))+((((1 > 4)?1:(1))*1)/100)) | (10 if (((10 > 4)) else (10))+((((10 > 4)?10:(10))*361)/100))-(10 if (((10 > 4)) else (10))+((((10 > 4)?10:(10))*361)/100)) | (20 if (((20 > 4)) else (20))+((((20 > 4)?20:(20))*761)/100))-(20 if (((20 > 4)) else (20))+((((20 > 4)?20:(20))*761)/100)) | (30 if (((30 > 4)) else (30))+((((30 > 4)?30:(30))*1161)/100))-(30 if (((30 > 4)) else (30))+((((30 > 4)?30:(30))*1161)/100)) | -- |

### Synergies
* **Blood Boil**: \+0% Damage per Level

---

## Summon Defiler

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 35.00 | 39.50 | 44.50 | 49.50 | -- |
| Defense | Linear (+20) | 125 | 305 | 505 | 705 | -- |
| Life | Linear (+70) | 50 | 680 | 1380 | 2080 | -- |
| Damage Shared Between Bound Targets | Linear (+1%) | 1.00% | 10.00% | 20.00% | 30.00% | -- |
| Max Bound Souls | Linear (+1) | 1.00 | 10.00 | 20.00 | 30.00 | -- |

---

## Blood Oath

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Damage Taken Goes To your demon | Linear (+2%) | +5% | +23% | +43% | +63% | -- |
| Physical Damage to your demon Reduced by | Linear (+0%) | 5% | 5% | 5% | 5% | Static: 5.0% |
| Resist All for your demon | Diminishing (+9 -> +2%) [Soft: +1%] | +16% | +55% | +67% | +72% | 81.0% |
| Life of your demon | Linear (+35%) | +50% | +365% | +715% | +1065% | -- |

---

## Engorge

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.25) | 3.00 | 5.25 | 7.75 | 10.25 | -- |
| Duration | Linear (+75s) | 125s | 800s | 1550s | 2300s | -- |
| Life Steal | Linear (+15%) | +1% | +136% | +286% | +436% | -- |
| Heal Demon's Life | Linear (+1%) | +30% | +39% | +49% | +59% | -- |
| Attack Speed | Linear (+1%) | +15% | +24% | +34% | +35% | 35.0% |

### Synergies
* **Blood Oath**: \+25% Damage per Level
* **Blood Oath**: \+5% Damage per Level

---

## Blood Boil

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.25) | 3.75 | 6.00 | 8.50 | 11.00 | -- |
| Demon's Life Cost | Linear (-1%) [Soft: +0%] | 15% | 6% | 5% | 5% | 5.0% |
| Radius | Linear (+1y) | 12y | 21y | 31y | 41y | -- |
| Fire Damage | Variable | 12.00-24.00 | 258.00-342.00 | 970.00-1290.00 | 1770.00-2550.00 | -- |
| Damage | Variable | 10-20 | 86-114 | 194-258 | 354-510 | -- |

### Synergies
* **Blood Oath**: \+20% Damage per Level
* **Engorge**: \+20% Damage per Level

---

## Consume

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+1) | 25.00 | 34.00 | 44.00 | 54.00 | -- |
| Duration | Linear (+500s) | 1000s | 5500s | 10500s | 15500s | -- |
| Run/Walk Speed | Accelerating (-113 -> -24%) [Soft: -9%] | +850% | +344% | +192% | +125% | -- |
| Max Life | Linear (+1%) | +5% | +14% | +24% | +34% | -- |

---

## Bind Demon

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+1) | 25.00 | 34.00 | 44.00 | 54.00 | -- |
| Chance to Bind | Diminishing (+4 -> +2%) [Soft: +0%] | 5.00% | 29.00% | 44.00% | 46.00% | 129.0% |
| Life of your demon | Linear (+0%) | +0% | +0% | +0% | +0% | -- |
| Damage | Linear (+29) | +7 | +268 | +558 | +848 | -- |
| Damage | Linear (+10%) | +76% | +166% | +266% | +366% | -- |

### Synergies
* **Death Mark**: \+1\.00% Damage per Level

---

## Levitation Mastery

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Weapon Requirements | Complex | +mair% | +mair% | +mair% | +mair% | -- |
| Critical Strike Chance | Diminishing (+4 -> +0%) | +5% | +24% | +29% | +32% | 36.0% |
| Attack Rating | Linear (+5%) | +40% | +85% | +135% | +185% | -- |
| Damage | Linear (+4%) | +25% | +61% | +101% | +141% | -- |

---

## Eldritch Blast

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 5.50 | 10.00 | 15.00 | 20.00 | -- |
| Mana Steal | Linear (+1%) [Soft: +0%] | +5% | +14% | +20% | +20% | 20.0% |
| Life Steal | Linear (+1%) [Soft: +0%] | +5% | +14% | +20% | +20% | 20.0% |
| Magic Damage | Variable | 4.00-12.00 | 385.00-429.00 | 2247.00-2331.00 | 5229.00-5313.00 | -- |

### Synergies
* **Hex: Purge**: \+50% Magic Damage per Level
* **Blade Warp**: \+50% Magic Damage per Level
* **Psychic Ward**: \+2\.00% Damage per Level

---

## Hex: Bane

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 6.00 | 10.50 | 15.50 | 20.50 | -- |
| Duration | Complex | lens | lens | lens | lens | -- |
| [PH] Effect Length | Linear (+0s) | 0s | 0s | 0s | 0s | -- |
| Magic Damage | Variable | 18.45-32.80 | 506.00-793.50 | 2860.00-3850.00 | 6160.00-7590.00 | -- |
| Attack Rating | Linear (+9%) | +20% | +101% | +191% | +281% | -- |

### Synergies
* **Mirrored Blades**: \+35% Magic Damage per Level
* **Hex: Purge**: \+35% Magic Damage per Level
* **Consume**: \+35% Magic Damage per Level

---

## Hex: Siphon

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 12.50 | 17.00 | 22.00 | 27.00 | -- |
| Duration | Complex | lens | lens | lens | lens | -- |
| Life After Each Kill | Linear (+2) [Soft: +1] | +2 | +20 | +40 | +50 | -- |
| Mana After Each Kill | Linear (+2) [Soft: +1] | +2 | +20 | +40 | +50 | -- |
| Attack Rating | Linear (+9%) | +20% | +101% | +191% | +281% | -- |

### Synergies
* **Engorge**: \+1% Damage per Level

---

## Psychic Ward

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+2) | 20.00 | 38.00 | 58.00 | 78.00 | -- |
| Stun Length | Diminishing (+6 -> +1s) | 44s | 70s | 77s | 81s | 86.0s |
| Absorbs damage | Linear (+40) [Soft: +10] | 45 | 405 | 805 | 905 | -- |

### Synergies
* **Cleave**: \+15% Damage per Level
* **Levitation Mastery**: \+15% Damage per Level

---

## Echoing Strike

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 7.00 | 11.50 | 16.50 | 21.50 | -- |
| Attack Rating | Linear (+0%) | +0% | +0% | +0% | +0% | -- |
| Damage | Complex | 8*(((((100+(30+clc0))/1.20)/2)*1.20*2)-1)/100-12*(((((100+(30+clc0))/1.20)/2)*1.20*2)-1)/100 | 37*(((((100+(75+clc0))/3.00)/2)*3.00*2)-1)/100-59*(((((100+(75+clc0))/3.00)/2)*3.00*2)-1)/100 | 85*(((((100+(125+clc0))/5.00)/2)*5.00*2)-1)/100-131*(((((100+(125+clc0))/5.00)/2)*5.00*2)-1)/100 | 145*(((((100+(175+clc0))/5.00)/2)*5.00*2)-1)/100-221*(((((100+(175+clc0))/5.00)/2)*5.00*2)-1)/100 | -- |
| Damage: + | Complex | 30+clc0% | 75+clc0% | 125+clc0% | 175+clc0% | -- |

### Synergies
* **Mirrored Blades**: \+1% Damage per Level
* **Mirrored Blades**: \+5% Damage per Level
* **Blade Warp**: \+5% Damage per Level

---

## Hex: Purge

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+1) | 25.00 | 34.00 | 44.00 | 54.00 | -- |
| Duration | Complex | lens | lens | lens | lens | -- |
| Magic Explosion Damage | Variable | 12.00-18.00 | 162.00-231.00 | 710.00-925.00 | 1410.00-1725.00 | -- |
| Attack Speed | Linear (+1%) | +10% | +19% | +29% | +30% | 30.0% |
| Attack Rating | Linear (+9%) | +20% | +101% | +191% | +281% | -- |

### Synergies
* **Hex: Bane**: \+10% Magic Damage per Level
* **Eldritch Blast**: \+10% Magic Damage per Level
* **Sigil: Death**: \+1\.00% Damage per Level

---

## Blade Warp

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0) | 15.00 | 15.00 | 15.00 | 15.00 | Static: 15.0 |
| Radius: s | Complex | leny | leny | leny | leny | -- |
| Magic Damage | Variable | 11.84-14.80 | 226.20-237.80 | 1070.60-1091.80 | 1918.60-1939.80 | -- |

### Synergies
* **Mirrored Blades**: \+24% Magic Damage per Level
* **Echoing Strike**: \+24% Magic Damage per Level

---

## Cleave

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0) | 3.00 | 3.00 | 3.00 | 3.00 | Static: 3.0 |
| Cleave Arc: Degrees | Linear (+12) [Soft: +0] | 132 | 240 | 240 | 240 | 240.0 |
| Damage | Linear (+35%) [Soft: +5%] | +50% | +365% | +715% | +765% | -- |
| Attack Speed | Linear (+1%) [Soft: +0%] | +21% | +26% | +28% | +29% | 30.0% |
| Attack Rating | Linear (+7%) | +50% | +113% | +183% | +253% | -- |

### Synergies
* **Mirrored Blades**: \+10% Damage per Level
* **Hex: Purge**: \+10% Damage per Level
* **Eldritch Blast**: \+10% Damage per Level

---

## Mirrored Blades

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 5.00 | 9.50 | 14.50 | 19.50 | -- |
| Attack Speed | Accelerating (-2 -> -1%) | +46% | +36% | +33% | +31% | -- |
| Mirrored Blade Damage | Diminishing (+8 -> +1%) [Soft: +0%] | 61% | 98% | 109% | 114% | 122.0% |

---

## Sigil: Lethargy

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0) | 4.00 | 4.00 | 4.00 | 4.00 | Static: 4.0 |
| Duration | Linear (+1s) | 5.00s | 14.00s | 24.00s | 34.00s | -- |
| Radius: s | Complex | rngy | rngy | rngy | rngy | -- |
| Enemy Defense | Linear (-1%) | -33% | -42% | -52% | -62% | -- |
| Damage Taken | Linear (+1%) | +20% | +29% | +39% | +49% | -- |

---

## Ring of Fire

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 8.00 | 12.50 | 17.50 | 22.50 | -- |
| Fire Damage | Variable | 9.00-18.00 | 384.00-474.00 | 1672.00-1991.00 | 2882.00-3575.00 | -- |

### Synergies
* **Flame Wave**: \+25% Damage per Level
* **Apocalypse**: \+25% Damage per Level

---

## Miasma Bolt

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 2.00 | 6.50 | 11.50 | 16.50 | -- |
| Average Magic Damage | Linear (+0) dmg/s | 0-0 dmg/s | 0-0 dmg/s | 0-0 dmg/s | 0-0 dmg/s | -- |
| Magic Damage | Variable | 1.20-3.60 | 36.00-69.00 | 180.00-265.00 | 340.00-455.00 | -- |

### Synergies
* **Miasma Chain**: \+10% Magic Damage per Level
* **Miasma Chain**: \+20% Magic Damage per Level
* **Abyss**: \+10% Magic Damage per Level
* **Abyss**: \+20% Magic Damage per Level

---

## Sigil: Rancor

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0) | 12.00 | 12.00 | 12.00 | 12.00 | Static: 12.0 |
| Duration | Linear (+1s) | 5.00s | 14.00s | 24.00s | 34.00s | -- |
| Radius: s | Complex | rngy | rngy | rngy | rngy | -- |
| Attack Speed | Linear (+1%) | +5% | +14% | +24% | +34% | -- |
| Damage | Linear (+5%) | +50% | +95% | +145% | +195% | -- |

---

## Enhanced Entropy

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Bonus Abyss Radius: + Yards | Linear (+1y) | 1y | 10y | 20y | 30y | -- |
| + Seconds to Miasma Duration | Linear (+5s) [Soft: +0s] | 5s | 50s | 100s | 100s | 100.0s |
| Miasma Radius: Yards | Complex | (4 if ((1 >= 10)) else ((1>=5)?3:2))y | (4 if ((10 >= 10)) else ((10>=5)?3:2))y | (4 if ((20 >= 10)) else ((20>=5)?3:2))y | (4 if ((30 >= 10)) else ((30>=5)?3:2))y | -- |

---

## Flame Wave

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 7.00 | 11.50 | 16.50 | 21.50 | -- |
| Duration | Linear (+0s) | 0.28s | 0.28s | 0.28s | 0.28s | Static: 0.28s |
| Width: s | Diminishing (+2 -> +0y) | 11y | 17y | 19y | 19y | 21.0y |
| Average Fire Damage | Complex | m1en-m1ex dmg/s | m1en-m1ex dmg/s | m1en-m1ex dmg/s | m1en-m1ex dmg/s | -- |
| Fire Damage | Variable | 22.50-30.00 | 636.00-774.00 | 2970.00-3399.00 | 5346.00-5973.00 | -- |

### Synergies
* **Ring of Fire**: \+25% Damage per Level
* **Ring of Fire**: \+15% Damage per Level
* **Apocalypse**: \+25% Damage per Level
* **Apocalypse**: \+15% Damage per Level

---

## Miasma Chain

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 4.50 | 9.00 | 14.00 | 19.00 | -- |
| Average Magic Damage | Linear (+0) dmg/s | 0-0 dmg/s | 0-0 dmg/s | 0-0 dmg/s | 0-0 dmg/s | -- |
| Magic Damage | Variable | 7.20-10.80 | 78.00-87.00 | 280.00-295.00 | 470.00-485.00 | -- |
| hits | Linear (+0) | 0 | 0 | 0 | 0 | -- |

### Synergies
* **Miasma Bolt**: \+10% Magic Damage per Level
* **Miasma Bolt**: \+20% Magic Damage per Level
* **Abyss**: \+10% Magic Damage per Level
* **Abyss**: \+20% Magic Damage per Level

---

## Sigil: Death

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+0.5) | 10.00 | 14.50 | 19.50 | 24.50 | -- |
| Duration | Linear (+1s) | 5.00s | 14.00s | 24.00s | 34.00s | -- |
| Radius: s | Complex | rngy | rngy | rngy | rngy | -- |

---

## Apocalypse

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+1) | 32.00 | 41.00 | 51.00 | 61.00 | -- |
| Radius: s | Complex | rngy | rngy | rngy | rngy | -- |
| Resist Fire | Linear (-1%) | -5% | -14% | -24% | -34% | -- |
| Fire Damage | Variable | 112.00-140.00 | 1665.00-1875.00 | 7965.00-8775.00 | 14967.00-17325.00 | -- |

### Synergies
* **Ring of Fire**: \+20% Damage per Level
* **Flame Wave**: \+20% Damage per Level

---

## Abyss

> Work in Progress

| Effect | Scaling | L1 | L10 | L20 | L20+10 | Limit |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Mana Cost | Linear (+1) | 23.00 | 32.00 | 42.00 | 52.00 | -- |
| Average Magic Damage | Complex | (0*25)/0-(0*25)/0 dmg/s | (0*25)/0-(0*25)/0 dmg/s | (0*25)/0-(0*25)/0 dmg/s | (0*25)/0-(0*25)/0 dmg/s | -- |
| Magic Damage | Variable | 20.00-40.00 | 53.00-84.00 | 125.00-180.00 | 245.00-340.00 | -- |

### Synergies
* **Miasma Bolt**: \+14% Magic Damage per Level
* **Miasma Bolt**: \+14% Magic Damage per Level
* **Miasma Chain**: \+14% Magic Damage per Level
* **Miasma Chain**: \+14% Magic Damage per Level

---

