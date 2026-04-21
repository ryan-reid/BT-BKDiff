# Missiles.txt

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
