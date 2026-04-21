# ItemStatCost.txt

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
