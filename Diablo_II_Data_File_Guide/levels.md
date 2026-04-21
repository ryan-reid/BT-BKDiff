# Levels.txt

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
