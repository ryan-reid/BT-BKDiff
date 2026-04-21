# DIABLO II DATA FILE GUIDE

## Table of Contents
* [actinfo.txt](#actinfotxt)
* [armor.txt](#armortxt)
* [automagic.txt](#automagictxt)
* [AutoMap.txt](#automaptxt)
* [belts.txt](#beltstxt)
* [books.txt](#bookstxt)
* [charstats.txt](#charstatstxt)
* [cubemain.txt](#cubemaintxt)
* [difficultylevels.txt](#difficultylevelstxt)
* [experience.txt](#experiencetxt)
* [gamble.txt](#gambletxt)
* [gems.txt](#gemstxt)
* [hireling.txt](#hirelingtxt)
* [hirelingdesc.txt](#hirelingdesctxt)
* [itemratio.txt](#itemratiotxt)
* [ItemStatCost.txt](#itemstatcosttxt)
* [ItemTypes.txt](#itemtypestxt)
* [LevelGroups.txt](#levelgroupstxt)
* [Levels.txt](#levelstxt)
* [LvlMaze.txt](#lvlmazetxt)
* [LvlPrest.txt](#lvlpresttxt)
* [LvlSub.txt](#lvlsubtxt)
* [LvlTypes.txt](#lvltypestxt)
* [LvlWarp.txt](#lvlwarptxt)
* [MagicPrefix.txt](#magicprefixtxt)
* [MagicSuffix.txt](#magicsuffixtxt)
* [Missiles.txt](#missilestxt)
* [misc.txt](#misctxt)
* [monequip.txt](#monequiptxt)
* [MonLvl.txt](#monlvltxt)
* [MonPreset.txt](#monpresettxt)
* [MonProp.txt](#monproptxt)
* [monseq.txt](#monseqtxt)
* [monstats.txt](#monstatstxt)
* [monstats2.txt](#monstats2txt)
* [MonType.txt](#montypetxt)
* [monumod.txt](#monumodtxt)
* [monsounds.txt](#monsoundstxt)
* [npc.txt](#npctxt)
* [objects.txt](#objectstxt)
* [objgroup.txt](#objgrouptxt)
* [objpreset.txt](#objpresettxt)
* [Overlay.txt](#overlaytxt)
* [pettype.txt](#pettypetxt)
* [Properties.txt](#propertiestxt)
* [QualityItems.txt](#qualityitemstxt)
* [RarePrefix.txt](#rareprefixtxt)
* [RareSuffix.txt](#raresuffixtxt)
* [Runes.txt](#runestxt)
* [SetItems.txt](#setitemstxt)
* [Sets.txt](#setstxt)
* [shrines.txt](#shrinestxt)
* [skills.txt](#skillstxt)
* [skilldesc.txt](#skilldesctxt)
* [sounds.txt](#soundstxt)
* [SoundEnviron.txt](#soundenvirontxt)
* [states.txt](#statestxt)
* [SuperUniques.txt](#superuniquestxt)
* [TreasureClassEx.txt](#treasureclassextxt)
* [UniqueAppellation.txt](#uniqueappellationtxt)
* [UniqueItems.txt](#uniqueitemstxt)
* [UniquePrefix.txt](#uniqueprefixtxt)
* [UniqueSuffix.txt](#uniquesuffixtxt)
* [weapons.txt](#weaponstxt)
* [wanderingmon.txt](#wanderingmontxt)
* [Reference Data Files](#reference-data-files)

---

## actinfo.txt

### Overview
This file controls global Act functionalities including item levels, monster behaviors, and waypoints. It uses the `wanderingmon.txt` file for a modular list of potential wandering units to spawn. Any column field name starting with "*" is considered a comment field and is not used by the game.

### Data Fields
* **act**: Defines the ID for the Act.
* **town**: Uses an area level ("Name field" from `levels.txt`) to define the Act’s town area.
* **start**: Uses an area level ("Name field" from `levels.txt`) to define where the player starts in the Act.
* **maxnpcitemlevel**: Controls the maximum item level for items sold by the NPC in the Act.
* **classlevelrangestart**: Uses an area level ("Name field" from `levels.txt`) with its `MonLvl` values as a global Act minimum monster level. For example, this is used to determine chest levels in an Act.
* **classlevelrangeend**: Uses an area level ("Name field" from `levels.txt`) with its `MonLvl` values as a global Act maximum monster level. For example, this is used to determine chest levels in an Act.
* **wanderingnpcstart**: Uses an index to determine which wandering monster class to use when populating areas (See `wanderingmon.txt` for a list of possible monsters to spawn).
* **wanderingnpcrange**: This is a modifier that gets added to the "wanderingnpcstart" value to randomly select an index.
* **commonactcof**: Specifies which ".D2" file to use as for the common Act COF file. This is used to establish the seed when initializing the Act.
* **waypoint1 (to waypoint9)**: Uses an area level ("Name field" from `levels.txt`) as the designated waypoint selection in the Waypoint UI.
* **wanderingMonsterPopulateChance**: The percent chance (from 0 to 100) to spawn a wandering monster.
* **wanderingMonsterRegionTotal**: The maximum number of wandering monsters allowed at once.
* **wanderingPopulateRandomChance**: A secondary percent chance (from 0 to #) to determine whether to attempt populating with monsters. Only fails if random chance selects 0.

---

## armor.txt

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

## automagic.txt

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

## AutoMap.txt

### Overview
Controls how the Automap displays discovered areas and stores progress.

### Data Fields
* **LevelName**: String defining Act number and level type (e.g., "1 Town", "2 Desert").
* **TileName**: String codes for tile orientations (e.g., "fl" = Floor, "wl" = Left Wall).
* **Style**: Group ID for matching cells.
* **StartSequence / EndSequence / Cel1 to Cel4**: Image frame selection from `MaxiMap.dc6`.

---

## belts.txt

### Overview
Controls belt statistics and item slot layouts. Relies on the "belt" field in `armor.txt`.

### Data Fields
* **name**: Belt type.
* **numboxes**: Number of item slots.
* **box1left to box16bottom**: Pixel coordinates for UI slots.
* **defaultItemTypeCol1 to defaultItemCodeCol4**: Controller auto-use functionality defaults.

---

## books.txt

### Overview
Controls functionalities of Tomes (Identify, Town Portal) and their scroll interactions.

### Data Fields
* **Name**: Book reference name.
* **ScrollSpellCode / BookSpellCode**: Linked item codes.
* **pSpell**: Item spell function ID.

| Code | Description |
|---|---|
| 1 | Identify |
| 2 | Town Portal |
| ... | (Potions and Skills) |

---

## charstats.txt

### Overview
Controls starting stats and progression for each character class.

### Data Fields
* **class**: Class name.
* **str / dex / int / vit**: Starting attributes.
* **hpadd / ManaRegen / ToHitFactor**: Starting bonuses.
* **WalkVelocity / RunVelocity / RunDrain**: Movement stats.
* **LifePerLevel / StaminaPerLevel / ManaPerLevel**: Progression rates (Calculated in fourths/256).
* **StartSkill / Skill 1 to Skill 10**: Default and starting skills.
* **StrAllSkills / StrSkillTab1-3**: UI string keys for item bonuses.
* **baseWClass**: Default weapon class (Hand to Hand, etc.).
* **item1 to item10**: Starting inventory items.
* **item1quality to item10quality**: Quality codes (0-9).

---

## cubemain.txt

### Overview
Controls recipes for the Horadric Cube.

### Data Fields
* **description / enabled / firstLadderSeason / lastLadderSeason**: Basic recipe metadata.
* **min diff**: Difficulty requirement (0-2).
* **version**: Game version mode (Classic/Expansion).
* **op / param / value**: Advanced input requirements (e.g., player stats, time of day).
* **numinputs / input 1 to input 7**: Required items and parameters (e.g., `qty=#`, `low`, `nor`, `sock=#`).
* **output / output b / output c**: Resulting items and properties (e.g., `pre=#`, `uns`, `lvl=#`).

---

## difficultylevels.txt

### Overview
Controls global parameters for game rules across difficulty modes.

### Data Fields
* **ResistPenalty**: Baseline resistance penalty.
* **DeathExpPenalty**: Experience loss on death.
* **MonsterSkillBonus / MonsterFreezeDivisor / MonsterColdDivisor**: Monster stat scaling.
* **LifeStealDivisor / ManaStealDivisor**: Player stat scaling.
* **UniqueDamageBonus / ChampionDamageBonus**: Unique/Champion damage modifiers.
* **PlayerDamagePercentVS...**: PvP and PvE damage scaling.
* **GambleRare / GambleSet / GambleUnique / GambleUber / GambleUltra**: Gambling odds and upgrade formulas.

---

## experience.txt

### Overview
Controls experience required for each level per class.

### Data Fields
* **Level**: Target level.
* **Amazon / Sorceress / ...**: Experience values for each class.
* **ExpRatio**: Global multiplier for experience earned.

---

## gamble.txt

### Overview
Controls which item types appear in the Gambling UI.

---

## gems.txt

### Overview
Controls item modifiers of gems and runes when socketed.

### Data Fields
* **name / letter**: UI names and rune letter concatenations.
* **transform**: Color change code.
* **weaponMod# / helmMod# / shieldMod#**: Modifiers applied based on `gemapplytype`.

---

## inventory.txt

### Overview
Controls grid sizes and pixel coordinates for all inventory and equipment UI windows.

---

## itemratio.txt

### Overview
Calculates the quality of items when they spawn (Unique, Set, Rare, etc.).

### Calculations
1. **Base Probability**: `( Quality - ( mlvl - ilvl ) / Divisor ) * 128`
2. **Magic Find**: Applies diminishing returns above 110% MF.
3. **Treasure Class**: Modifies probability based on TC settings.
4. **Roll**: Random roll between 0 and probability value; success if result <= 128.

---

## ItemStatCost.txt

### Overview
Defines functionalities for every possible stat on a unit. Used as modifiers in `Properties.txt`.

### Data Fields
* **Stat**: Unique pointer.
* **Send Bits / Send Param Bits**: Client sync data.
* **Saved / CSvBits / CSvParam**: Character save data parameters.
* **Encode**: Controls how stats modify buy, sell, and repair costs (Functions 0-4).
* **ValShift**: Bitwise shift for stat values.
* **Save Bits / Save Add / Save Param Bits**: Storage parameters.
* **op**: Stat operator for advanced modifications (Functions 0-13, e.g., By Level, By Time, Energy/Vitality multipliers).
* **direct / maxstat**: Caps current stats (Life/Mana) based on max values.
* **itemevent / itemeventfunc**: Triggers functions on events (e.g., hit by missile, kill).
* **descpriority / descfunc**: Tooltip formatting and sorting.

---

## ItemTypes.txt

### Overview
Controls general statistics for each item type category.

### Data Fields
* **ItemType / Code**: Identifiers.
* **Equiv1 & Equiv2**: Parental reference for hierarchy.
* **Body / BodyLoc1 / BodyLoc2**: Equipment slot requirements.
* **Shoots / Quiver**: Ammo/Weapon pairing.
* **AutoStack / Reload / ReEquip**: QoL functionalities.
* **MaxSockets1-3 / MaxSocketsLevelThreshold1-2**: Item-level dependent socket caps.
* **StaffMods**: Class-specific skill modifier flags.

---

## hireling.txt

### Overview
Controls unit statistics for player mercenaries.

### Data Fields
* **Hireling / Class / Act / Difficulty**: Basic identification.
* **Gold**: Base cost, modified by `Cost = Gold * (100 + 15 * [Level Diff]) / 100`.
* **HP / HP/Lvl / Defense / Str / Dex / AR / Dmg / Resists**: Base stats and growth rates (often calculated in 4ths or 8ths).
* **Skill1 to Skill6**: Assigned skills from `skills.txt`.

---

## Levels.txt

### Overview
Controls area level construction, building rules, and monster/object spawning.

### Data Fields
* **Name / Id / Pal / Act**: Identification and palette.
* **QuestFlag / QuestFlagEx**: Access requirements.
* **SizeX / SizeY**: Tile dimensions per difficulty.
* **Teleport**: Ability restriction (0-2).
* **Rain / Mud / NoPer / LOSDraw**: Environmental and rendering flags.
* **DrlgType**: Dynamic Random Level Generation type.
* **SubType / SubTheme**: Tile substitution and theme groups.
* **Vis0 to Vis7 / Warp0 to Warp7**: Connections to other levels.
* **MonLvl / MonDen / MonUMin / MonUMax**: Monster level, density, and Unique spawn caps.
* **mon1 to mon25 / nmon1 to nmon25**: Specific monster IDs allowed.
* **Themes**: Summation bit mask for level room decorations (Barrels, Shrines, etc.).

---

## Missiles.txt

### Overview
Controls projectiles used for attacks, skills, and special effects.

### Data Fields
* **pCltDoFunc / pSrvDoFunc**: Client and server behavior functions (Codes 0-68 and 0-37 respectively).
* **pCltHitFunc / pSrvHitFunc**: Hit/collision logic (Codes 0-64 and 0-59 respectively).
* **pSrvDmgFunc**: Pre-damage calculation functions (Codes 0-15).
* **Vel / MaxVel / Accel**: Velocity parameters.
* **Range / LevRange**: Duration parameters.
* **Light / Red / Green / Blue**: Visual properties.
* **CollideType**: Collision mask (0-8).
* **ResultFlags / HitFlags**: Bit field flags for damage effects (Bypass Undead, No Life Steal, etc.).
* **EType / EMin / EMax / ELen**: Elemental damage properties.
* **HitClass**: Hit sound/overlay bit field.

---

## objects.txt

### Overview
Controls functionalities of all environment objects (Chests, Shrines, Doors, etc.).

### Data Fields
* **Number Object Mode Token**: 8 modes (Neutral, Operating, Opened, Special 1-5).
* **Selectable / FrameCnt / FrameDelta / CycleAnim**: Animation and interaction control per mode.
* **HasCollision / IsAttackable / IsDoor / BlocksVis**: Physic and AI flags.
* **OperateFn**: Interaction function (Codes 0-73).
* **PopulateFn**: Spawning function (Codes 0-9).
* **InitFn**: Initialization function (Codes 0-79).
* **ClientFn**: Client-side visual/audio functions (Codes 0-18).

---

## Properties.txt

### Overview
Defines how item modifiers (affixes) translate `ItemStatCost` stats into gameplay effects using functions.

### Functions (func1 to func7)
* **1 (SetValueRegular)**: Random between min/max.
* **9 (SetSingleSkill)**: Modifies a specific skill.
* **10 (SetTabSkills)**: Modifies a whole skill tab (Codes 0-20).
* **14 (SetSockets)**: Adds sockets.
* **19 (SetChargedSkill)**: Adds skill charges with complex quantity formulas.

---

## skills.txt

### Overview
Controls all skill functionalities for players and monsters.

### Data Fields
* **srvstfunc / srvdofunc / srvstopfunc**: Server start, execution, and cleanup functions (Extensive list 0-152).
* **cltstfunc / cltdofunc / cltstopfunc**: Client-side versions.
* **aurafilter**: Bit field flags for aura targeting (Find Players, No Bosses, Allies, etc.).
* **mana / lvlmana / manashift**: Mana cost calculation.
* **ToHit / LevToHit / ToHitCalc**: Attack Rating calculation.
* **HitShift**: Damage percentage modifier (Values 0-8, where 8=100%).
* **SrcDam**: Weapon damage transfer (x/128).
* **EMin / EMax / ELen**: Elemental damage and duration.
* **aitype**: AI behavior classification (Buff, Debuff, Heal, etc.).

---

## states.txt

### Overview
Defines passive behaviors and visual effects applied to units.

### Data Fields
* **transform / aura / curable / curse**: Core state flags.
* **attblue / damblue / ...**: UI color overrides.
* **life / green / pgsv / bossinv**: Gameplay mechanic flags.
* **overlay1 to overlay4**: Visual graphics linked to the state.
* **setfunc / remfunc**: Client-side functions triggered on apply/remove (Codes 0-19 and 0-12).
* **itemtrans / colorshift**: Item and unit color overrides.

---

## TreasureClassEx.txt

### Overview
Controls item drop groups and probabilities for monsters and objects.

### Data Fields
* **group / level**: TC selection logic.
* **Picks**: Number of roll attempts (positive) or guaranteed quantity (negative).
* **Unique / Set / Rare / Magic**: Drop ratio modifiers.
* **NoDrop**: Probability of no item dropping.
* **Item1 to Item10 / Prob1 to Prob10**: Linked TCs or items and their relative weights.

---

## UniqueItems.txt

### Overview
Defines specific unique items and their modifiers.

### Data Fields
* **index / enabled / rarity**: Selection parameters.
* **lvl / lvl req**: Level constraints.
* **code**: Base item reference.
* **prop1 to prop12**: Assigned properties from `Properties.txt`.

---

## weapons.txt

### Overview
Exclusive fields for weapon-type items.

### Data Fields
* **1or2handed**: Barbarian specific handling.
* **2handed**: Dual-hand flag.
* **2handmindam / 2handmaxdam**: Damage values for 2H mode.
* **wclass / 2handedwclass**: Animation class links.
* **hit class**: Sound effect category.
* **minmisdam / maxmisdam**: Damage for thrown missiles.
* **rangeadder**: Baseline melee range extension.

---

## Reference Data Files
* `ArmType.txt`
* `bodylocs.txt`
* `colors.txt`
* `compcode.txt`
* `Composit.txt`
* `cubemod.txt`
* `ElemTypes.txt`
* `events.txt`
* `HitClass.txt`
* `lowqualityitems.txt`
* `misscalc.txt`
* `MonMode.txt`
* `MonPlace.txt`
* `ObjMode.txt`
* `ObjType.txt`
* `PlayerClass.txt`
* `PlrMode.txt`
* `PlrType.txt`
* `skillcalc.txt`
* `StorePage.txt`
