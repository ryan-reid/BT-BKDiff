# Druid Skill Mismatch Report

Generated from `tests.test_druid_skill_tree_service` against the current Druid skill evaluator.

## Summary

| Count | Skill | Field | Kind |
|---:|---|---|---|
| 3 | Armageddon | Average Fire Damage | range_delta |
| 3 | Summon Grizzly | Life | scalar_delta |
| 3 | Werebear | Max Life | scalar_delta |
| 3 | Werewolf | Max Life | scalar_delta |
| 2 | Molten Boulder | Average Fire Damage | range_delta |
| 2 | Poison Creeper | Life | scalar_delta |
| 2 | Summon Dire Wolf | Damage | range_delta |
| 1 | Feral Rage | Run/Walk Speed | range_delta |
| 1 | Maul | Damage | range_delta |
| 1 | Poison Creeper | Poison Damage | range_delta |
| 1 | Rabies | Attack Rating | scalar_delta |
| 1 | Rabies | Poison Damage | range_delta |
| 1 | Shock Wave | Stun Length | scalar_delta |
| 1 | Summon Spirit Wolf | Cold Damage | range_delta |

# Summoning


## Poison Creeper

### L1/1
Best candidate: `L2/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Life | 50 | 75.00 | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Poison Duration | 4.00s | desc |
| Poison Damage | 75.00-93.75 | desc |
| Life | 75.00 | desc |
| Mana Cost | 8.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Poison Damage per Level | +3.91% | dsc3 |

### L30/20
Best candidate: `L34/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Poison Damage | 3022-3266 | 3075.00-3300.00 | range_delta |
| Life | 775 | 875.00 | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Poison Duration | 4.00s | desc |
| Poison Damage | 3075.00-3300.00 | desc |
| Life | 875.00 | desc |
| Mana Cost | 8.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Poison Damage per Level | +3.91% | dsc3 |


## Summon Spirit Wolf

### L30/20
Best candidate: `L30/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Cold Damage | 245-254 | 203.94-211.86 | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Defense | +340.00% | desc |
| Attack Rating | +775.00% | desc |
| Max Wolves | 1.00 | desc |
| Cold Damage | 203.94-211.86 | desc |
| Life | 676.00 | desc |
| Mana Cost | 15.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Life per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |


## Summon Dire Wolf

### L1/1
Best candidate: `L1/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Damage | 45-79 | 47.12-80.78 | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Defense | +204.00% | desc |
| Max Life | +50.00% | desc |
| Max Wolves | 1.00 | desc |
| Damage | 47.12-80.78 | desc |
| Life | 345.60 | desc |
| Attack Rating | +500.00% | dsc2 |
| Mana Cost | 20.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Attack Rating per Level | +25.00% | dsc3 |
| Defense per Level | +10.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |

### L20/20
Best candidate: `L20/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Damage | 572-732 | 572.22-733.79 | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Defense | +280.00% | desc |
| Max Life | +126.00% | desc |
| Max Wolves | 5.00 | desc |
| Damage | 572.22-733.79 | desc |
| Life | 920.16 | desc |
| Attack Rating | +500.00% | dsc2 |
| Mana Cost | 20.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Attack Rating per Level | +25.00% | dsc3 |
| Defense per Level | +10.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |


## Summon Grizzly

### L1/1
Best candidate: `L11/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Life | 2288 | 2640.00 | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Damage % | +62.00% | desc |
| Damage | 798.66-963.90 | desc |
| Life | 2640.00 | desc |
| Defense | +300.00% | dsc2 |
| Attack Rating | +750.00% | dsc2 |
| Mana Cost | 40.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Attack Rating per Level | +25.00% | dsc3 |
| Defense per Level | +10.00% | dsc3 |
| Life per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |

### L20/20
Best candidate: `L20/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Life | 2730 | 3150.00 | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Damage % | +98.00% | desc |
| Damage | 2019.60-2221.56 | desc |
| Life | 3150.00 | desc |
| Defense | +200.00% | dsc2 |
| Attack Rating | +500.00% | dsc2 |
| Mana Cost | 40.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Attack Rating per Level | +25.00% | dsc3 |
| Defense per Level | +10.00% | dsc3 |
| Life per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |

### L30/20
Best candidate: `L30/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Life | 3770 | 4350.00 | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Damage % | +138.00% | desc |
| Damage | 4499.15-4741.91 | desc |
| Life | 4350.00 | desc |
| Defense | +300.00% | dsc2 |
| Attack Rating | +750.00% | dsc2 |
| Mana Cost | 40.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Attack Rating per Level | +25.00% | dsc3 |
| Defense per Level | +10.00% | dsc3 |
| Life per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |
| Damage per Level | +4.00% | dsc3 |


# Shape Shifting


## Werewolf

### L1/1
Best candidate: `L1/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Max Life | 25 | +43.00% | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Attack Speed | +21.00% | desc |
| Attack Rating | +50.00% | desc |
| Mana Cost | 15.00 | dsc2 |
| Casting Delay | 1.00s | dsc2 |
| Max Life | +43.00% | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Lycanthropy | 0.00 | dsc3 |

### L20/20
Best candidate: `L20/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Max Life | 25 | +43.00% | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Attack Speed | +69.23% | desc |
| Attack Rating | +335.00% | desc |
| Mana Cost | 15.00 | dsc2 |
| Casting Delay | 1.00s | dsc2 |
| Max Life | +43.00% | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Lycanthropy | 0.00 | dsc3 |

### L30/20
Best candidate: `L30/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Max Life | 103 | +63.00% | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Attack Speed | +74.17% | desc |
| Attack Rating | +485.00% | desc |
| Mana Cost | 15.00 | dsc2 |
| Casting Delay | 1.00s | dsc2 |
| Max Life | +63.00% | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Lycanthropy | 0.00 | dsc3 |


## Werebear

### L1/1
Best candidate: `L1/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Max Life | 108 | +68.00% | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Defense | +40.00% | desc |
| Damage % | +55.00% | desc |
| Mana Cost | 15.00 | dsc2 |
| Casting Delay | 1.00s | dsc2 |
| Max Life | +68.00% | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Lycanthropy | 0.00 | dsc3 |

### L16/16
Best candidate: `L16/16`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Max Life | 108 | +68.00% | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Defense | +190.00% | desc |
| Damage % | +280.00% | desc |
| Mana Cost | 15.00 | dsc2 |
| Casting Delay | 1.00s | dsc2 |
| Max Life | +68.00% | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Lycanthropy | 0.00 | dsc3 |

### L26/16
Best candidate: `L26/16`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Max Life | 128 | +88.00% | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Defense | +290.00% | desc |
| Damage % | +430.00% | desc |
| Mana Cost | 15.00 | dsc2 |
| Casting Delay | 1.00s | dsc2 |
| Max Life | +88.00% | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Lycanthropy | 0.00 | dsc3 |


## Feral Rage

### L1/1
Best candidate: `L1/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Run/Walk Speed | 19-32 | 19.00-34.32% | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Damage % | +50.00% | desc |
| Life Steal | 4.00-12.00% | desc |
| Run/Walk Speed | 19.00-34.32% | desc |
| Attack Rating | +20.00% | desc |
| Duration | 30.00s | dsc2 |
| Mana Cost | 3.00 | dsc2 |


## Maul

### L1/1
Best candidate: `L1/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Damage | 30-90 | 30.00-105.00% | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Stun Length | 0.97s | desc |
| Damage % | 30.00-105.00% | desc |
| Attack Speed | 3.00-10.50% | desc |
| Attack Rating | +40.00% | desc |
| Duration | 20.00s | dsc2 |
| Mana Cost | 3.00 | dsc2 |


## Rabies

### L30/20
Best candidate: `L34/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Poison Damage | 19820-20561 | 19807.50-20377.50 | range_delta |
| Attack Rating | 340 | +380.00% | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Poison Duration | 8.00s | desc |
| Poison Damage | 19807.50-20377.50 | desc |
| Attack Rating | +380.00% | desc |
| Mana Cost | 10.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Poison Damage per Level | +20.31% | dsc3 |
| Poison Damage per Level | +20.31% | dsc3 |


## Shock Wave

### L5/1
Best candidate: `L5/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Stun Length | .2 | 5.00s | scalar_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Stun Length | 5.00s | desc |
| Damage | 255.20-371.20 | desc |
| Mana Cost | 15.00 | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Damage per Level | +8.00% | dsc3 |
| Damage per Level | +8.00% | dsc3 |
| Damage per Level | +8.00% | dsc3 |


# Elemental


## Molten Boulder

### L5/1
Best candidate: `L5/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Average Fire Damage | 103-114 | 103.59-115.78 dmg/s | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Mana Cost | 12.00 | desc |
| Average Fire Damage | 103.59-115.78 dmg/s | desc |
| Fire Damage | 57.20-83.20 | desc |
| Damage | 74.80-108.80 | desc |
| Casting Delay | 1.00s | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Damage per Level | +12.00% | dsc3 |
| Fire Damage per Level | +8.00% | dsc3 |

### L24/20
Best candidate: `L24/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Average Fire Damage | 529-541 | 530.16-542.34 dmg/s | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Mana Cost | 21.50 | desc |
| Average Fire Damage | 530.16-542.34 dmg/s | desc |
| Fire Damage | 457.60-533.00 | desc |
| Damage | 598.40-697.00 | desc |
| Casting Delay | 1.00s | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Damage per Level | +12.00% | dsc3 |
| Fire Damage per Level | +8.00% | dsc3 |


## Armageddon

### L5/1
Best candidate: `L5/1`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Average Fire Damage | 151-168 | 152.03-169.91 dmg/s | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Average Fire Damage | 152.03-169.91 dmg/s | desc |
| Fire Damage | 561.00-917.40 | desc |
| Damage | 266.80-322.00 | desc |
| Mana Cost | 35.00 | dsc2 |
| Radius | 12.00y | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Fire Damage per Level | +14.00% | dsc3 |
| Fire Damage per Level | +14.00% | dsc3 |
| Damage per Level | +18.00% | dsc3 |

### L24/20
Best candidate: `L24/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Average Fire Damage | 774-792 | 778.03-795.92 dmg/s | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Average Fire Damage | 778.03-795.92 dmg/s | desc |
| Fire Damage | 3313.20-3913.80 | desc |
| Damage | 1426.00-1568.60 | desc |
| Mana Cost | 35.00 | dsc2 |
| Radius | 12.00y | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Fire Damage per Level | +14.00% | dsc3 |
| Fire Damage per Level | +14.00% | dsc3 |
| Damage per Level | +18.00% | dsc3 |

### L30/20
Best candidate: `L30/20`

| Field | Expected | Actual | Kind |
|---|---:|---:|---|
| Average Fire Damage | 1024-1041 | 1028.43-1046.32 dmg/s | range_delta |

Available effects:

| Label | Value | Block |
|---|---:|---|
| Average Fire Damage | 1028.43-1046.32 dmg/s | desc |
| Fire Damage | 4633.20-5339.40 | desc |
| Damage | 1959.60-2129.80 | desc |
| Mana Cost | 35.00 | dsc2 |
| Radius | 12.00y | dsc2 |
| Receives Bonuses From | 2.00 | dsc3 |
| Fire Damage per Level | +14.00% | dsc3 |
| Fire Damage per Level | +14.00% | dsc3 |
| Damage per Level | +18.00% | dsc3 |
