# armor.txt

### Overview
This file controls the functionalities for armor type items. It is loaded together with other similar files in the following order: `weapons.txt`, `armor.txt`, `misc.txt`. These combined files form the items structure. Technically these files share the same fields, but some fields are exclusive for specific item types.

### Data Fields
* **name**: This is a reference field to define the item.
* **version**: Defines which game version to create this item (0 = Classic mode | 100 = Expansion mode).
* **compactsave**: Boolean Field. If equals 1, then only the item’s base stats will be stored in the character save. If equals 0, then all of the items stats will be saved.
* **rarity**: Determines the chance that the item will randomly spawn (1/#). Higher values mean rarer items.
* **spawnable**: Boolean Field. If 1, this item can be randomly spawned.
* **speed**: Affects the Walk/Run Speed reduction when wearing the armor.
* **reqstr**: Defines the amount of the Strength attribute needed to use the item.
* **reqdex**: Defines the amount of the Dexterity attribute needed to use the item.
* **durability**: Defines the base durability amount that the item will spawn with.
* **nodurability**: Boolean Field. If 1, the item will not have durability.
* **level**: Controls the base item level.
* **ShowLevel**: Boolean Field. If 1, display the item level next to the item name.
* **levelreq**: Controls the player level requirement for being able to use the item.
* **cost**: Defines the base gold cost of the item when being sold by an NPC.
* **gamble cost**: Defines the gambling gold cost of the item on the Gambling UI.
* **code**: Defines a unique 3 letter/number code for the item.
* **namestr**: String Key used for the base item name.
* **magic lvl**: Defines the magic level of the item (See `automagic.txt`).
* **auto prefix**: Automatically picks an item affix name from a designated "group" value from `automagic.txt`.
* **alternategfx**: Unique 3 letter/number code to determine in-game graphics.
* **normcode**: Links to a "code" field to determine the normal version of the item.
* **ubercode**: Links to a "code" field to determine the Exceptional version of the item.
* **ultracode**: Links to a "code" field to determine the Elite version of the item.
* **component**: Determines the layer of player animation when the item is equipped (referenced from `Composit.txt`).

| Code | Description |
|---|---|
| 0 | Head |
| 1 | Torso |
| 2 | Legs |
| 3 | Right Arm |
| 4 | Left Arm |
| 5 | Right Hand |
| 6 | Left Hand |
| 7 | Shield |
| 8-15 | Special 1-8 |
| 16 | Do not display anything |

* **invwidth & invheight**: Width and height in inventory grid cells.
* **hasinv**: Boolean Field. If 1, the item has its own inventory (socketing gems/runes/jewels).
* **gemsockets**: Maximum number of sockets allowed.
* **gemapplytype**: Determines gem effect application.

| Code | Description |
|---|---|
| 0 | Weapon |
| 1 | Armor or Helmet |
| 2 | Shield |

* **flippyfile**: DC6 file used when the item is dropped on the ground.
* **invfile**: DC6 file used for inventory graphics.
* **uniqueinvfile**: Graphics for Unique quality items.
* **setinvfile**: Graphics for Set quality items.
* **useable**: Boolean Field. If 1, usable with right-click (belts/quest items).
* **stackable**: Boolean Field. If 1, item uses quantity and handling stacking.
* **minstack / maxstack / spawnstack**: Controls minimum, maximum, and starting quantity for stackable items.
* **Transmogrify**: Boolean Field. If 1, uses transmogrify function.
* **TMogType / TMogMin / TMogMax**: Parameters for the transmogrified item.
* **type / type2**: Points to Item Type defined in `ItemTypes.txt`.
* **dropsound / dropsfxframe / usesound**: Audio parameters for dropping/moving items.
* **unique**: Boolean Field. If 1, can only spawn as Unique.
* **transparent**: Boolean Field. If 1, drawn transparent on player model.
* **transtbl**: Controls transparency type.

| Code | Description |
|---|---|
| 0-2 | Transparency at 25%, 50%, 75% |
| 3 | Black Alpha Transparency |
| 4 | White Alpha Transparency |
| 5 | No Transparency |
| 6 | Dark Transparency (Unused) |
| 7 | Highlight Transparency (mousing over) |
| 8 | Blended |

* **lightradius**: Value of light radius applied to monsters.
* **belt**: Controls which belt type entry in `belts.txt` to use.
* **quest**: Ties item to a specific quest class.

| Code | Description (Quest) |
|---|---|
| 0 | Not a quest item |
| 1 | Act 1 Prologue |
| 2 | Den of Evil |
| ... | (Full list available in guide) |
| 37 | Eve of Destruction |

* **questdiffcheck**: Boolean Field. Ties quest item to difficulty setting.
* **missiletype**: Missile used for throwing weapons.
* **durwarning / qntwarning**: Thresholds for low durability/quantity UI warnings.
* **mindam / maxdam**: Minimum/maximum physical damage.
* **StrBonus / DexBonus**: Percentage multiplier for attribute-based bonus damage.
* **gemoffset**: Starting index offset for `gems.txt`.
* **bitfield1**: Flags for Magic quality, metal, spellcaster, skill-based.
* **[NPC]Min / [NPC]Max / [NPC]Magic...**: Store availability per NPC.
* **Transform / InvTrans**: Color palette change codes for model/inventory.

---
