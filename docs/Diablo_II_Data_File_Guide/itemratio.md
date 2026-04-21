# itemratio.txt

### Overview
Calculates the quality of items when they spawn (Unique, Set, Rare, etc.).

### Calculations
1. **Base Probability**: `( Quality - ( mlvl - ilvl ) / Divisor ) * 128`
2. **Magic Find**: Applies diminishing returns above 110% MF.
3. **Treasure Class**: Modifies probability based on TC settings.
4. **Roll**: Random roll between 0 and probability value; success if result <= 128.

---
