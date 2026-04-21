# objects.txt

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
