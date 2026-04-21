# automagic.txt

### Overview
Controls item affixes (modifiers) automatically applied to items regardless of quality (e.g., class-based items like Paladin shields).

### Data Fields
* **Name**: Affix name.
* **version**: Game version requirement.
* **spawnable / rare**: Randomizer flags.
* **level / maxlevel / levelreq**: Level requirements.
* **classspecific**: Class restriction.

| Code | Description |
|---|---|
| (empty) | Any Class |
| ama | Amazon |
| bar | Barbarian |
| ... | (Other class codes) |

* **frequency**: Probability of appearing.
* **group**: Conflict prevention group.
* **mod1code to mod3code**: Property codes from `Properties.txt`.
* **transformcolor**: Item color change after spawning.
* **itype1 to itype7 / etype1 to etype5**: Allowed/forbidden item types.
* **multiply / add**: Buy/sell cost modifiers.

---
