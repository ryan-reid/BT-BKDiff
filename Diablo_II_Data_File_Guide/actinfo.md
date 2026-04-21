# actinfo.txt

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
