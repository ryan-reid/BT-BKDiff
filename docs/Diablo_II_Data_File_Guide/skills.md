# skills.txt

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
