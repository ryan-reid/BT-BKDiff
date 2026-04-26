# Differences for monai.txt

*Key column used: `AI`*

## Modified Rows (2)
### shadowmaster
- `\*aip1`: <code>Approach </code><del><code>Enemy </code></del><code>Range</code><del><code> Squared</code></del><code>/Melee Bonus </code><del><code>Chance</code></del><code>/Progressive </code><del><code>Skill </code></del><code>Bonus </code><del><code>Chance</code></del> (Old) &rarr; <code>Approach </code><code>Range</code><code>/Melee Bonus </code><ins><code>Rating</code></ins><code>/Progressive </code><code>Bonus </code><ins><code>Rating</code></ins> (New)
- `\*aip2`: <code>Random Skill </code><del><code>Bonus</code></del><code> </code><del><code>Chance/Target Max</code></del><code> Range/</code><del><code>Boss</code></del><code> Leash Range</code><del><code> Squared</code></del> (Old) &rarr; <code>Random Skill </code><ins><code>Pick/Enemy</code></ins><code> </code><ins><code>Awareness</code></ins><code> Range/</code><ins><code>Caster</code></ins><code> Leash Range</code> (New)
- `\*aip3`: <del><code>"Basic </code></del><code>Attack </code><code>% Chance</code><del><code> (minus max(summoning skill level, 1</code></del><code>)</code><del><code>*2)"</code></del> (Old) &rarr; <code>Attack </code><ins><code>(</code></ins><code>% Chance</code><code>)</code> (New)
- `\*aip8`: <del><code>Summoning</code></del><code> Skill</code><del><code> ID</code></del> (Old) &rarr; <ins><code>Summon</code></ins><code> Skill</code> (New)
### shadowmasternoinit
- `\*aip1`: <code>Approach Enemy </code><del><code>Max </code></del><code>Range</code><del><code> Squared</code></del><code>/Melee </code><del><code>Bonus</code></del><code> </code><del><code>Chance</code></del><code>/Progressive </code><del><code>Skill</code></del><code> </code><del><code>Bonus Chance</code></del> (Old) &rarr; <code>Approach Enemy </code><code>Range</code><code>/Melee </code><ins><code>bonus</code></ins><code> </code><ins><code>rating</code></ins><code>/Progressive </code><ins><code>bonus</code></ins><code> </code><ins><code>rating</code></ins> (New)
- `\*aip2`: <del><code>Random Skill Bonus Chance/Target Max Range/Boss</code></del><code> Leash Range</code><del><code> Squared</code></del> (Old) &rarr; <ins><code>Caster</code></ins><code> Leash Range</code> (New)
- `\*aip3`: <del><code>"Basic </code></del><code>Attack </code><code>% Chance</code><del><code> (minus max(summoning skill * 2, 1</code></del><code>)</code><del><code>)"</code></del> (Old) &rarr; <code>Attack </code><ins><code>(</code></ins><code>% Chance</code><code>)</code> (New)
- `\*aip8`: <del><code>Summoning</code></del><code> </code><del><code>Skill ID</code></del> (Old) &rarr; <ins><code>summoning</code></ins><code> </code><ins><code>skill</code></ins> (New)
