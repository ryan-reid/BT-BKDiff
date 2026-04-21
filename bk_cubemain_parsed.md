# Horadric Cube Recipes (BK Diablo)

This file contains the parsed Horadric Cube recipes from the BK Diablo mod.

| Description | Inputs | Output | Enabled |
| :--- | :--- | :--- | :---: |
| 1 mana potion | `mpot` | `-` | ❌ |
| ,qty= | `hpot` | `-` | ❌ |
| ,uni | `apot` | `-` | ❌ |
| ,set | `mpot,qty=2` | `-` | ❌ |
| ,mag | `hpot,qty=2` | `-` | ❌ |
| Staff of Kings + Amulet of the Viper -> Horadric Staff | `msf` + `vip` | `hst` | ✅ |
| Khalim's Flail + Khalim's Heart + Khalim's Eye + Khalim's Brain -> Khalim's Will | `qf1` + `qhr` + `qey` + `qbr` | `qf2` | ✅ |
| Wirt's Leg  -> Portal to The Secret Cow Level | `leg` | `Cow Portal` <br>+ `leg` | ✅ |
| 3 Healing Potions (Any) + 3 Mana Potions (Any) + 1 Standard Gem (Any) -> Full Rejuvenation Potion | `hpot,qty=3` + `mpot,qty=3` + `gem2` | `rvl` | ❌ |
| 3 Healing Potions (Any) + 3 Mana Potions (Any)  + 1 Chipped Gem (Any) -> Rejuvenation Potion | `hpot,qty=3` + `mpot,qty=3` + `gem0` | `rvs` | ❌ |
| 3 Rejuvenation Potions -> Full Rejuvenation Potion | `rvs,qty=3` | `rvl` | ✅ |
| 6 Perfect Gems (1 of each type) + 1 Magic Amulet -> Prismatic Amulet | `amu,mag` + `gpv` + `gpy` + `gpb` + `gpg` + `gpr` + `gpw` | `amu,mag,pre=331` | ✅ |
| 1 Magic Ring + 1 Standard Ruby + 1 Healing Potion -> Garnet Ring | `rin,mag` + `gpr` + `hpot` | `rin,mag,pre=372` | ✅ |
| 1 Magic Ring + 1 Standard Sapphire + 1 Thawing Potion -> Cobalt Ring | `rin,mag` + `gpb` + `wms` | `rin,mag,pre=353` | ✅ |
| 1 Magic Ring + 1 Standard Topaz + 1 Rejuvenation Potion -> Coral Ring | `rin,mag` + `gpy` + `rvs` | `rin,mag,pre=392` | ✅ |
| 1 Magic Ring + 1 Standard Emerald + 1 Antidote Potion -> Jade Ring | `rin,mag` + `gpg` + `yps` | `rin,mag,pre=412` | ✅ |
| 1 Axe (Any) + 1 Dagger (Any) -> Throwing Axe | `axe` + `knif` | `tax,nor` | ✅ |
| 1 Spear (Any) + 1 Arrows -> Javelins | `spea` + `aqv` | `jav,nor` | ✅ |
| 3 Magic Rings -> Magic Amulet | `rin,mag,qty=3` | `amu,mag` | ✅ |
| 3 Magic Amulets -> Magic Ring | `amu,mag,qty=3` | `rin,mag` | ✅ |
| 3 Standard Gems + 1 Socketed Weapon ->  Socketed Magic Weapon | `weap,sock` + `gem2,qty=3` | `usetype,mag` <br><small>sock (1-2)</small> | ❌ |
| 3 Flawless Gems + 1 Magic Weapon -> Socketed Magic Weapon | `weap,mag` + `gem3,qty=3` | `usetype,mag` <br><small>sock (1-2)</small> | ❌ |
| 1 Magic Shield + 1 Spiked Club + 2 Skulls (Any) -> Magic Shield of Spikes | `shld,mag` + `gemz,qty=2` + `spc` | `usetype,mag,suf=162` | ❌ |
| 4 Healing Potions (Any) + 1 Perfect Ruby + 1 Magic Sword -> Sword of the Leech | `swor,mag` + `gpr` + `hpot,qty=4` | `usetype,mag,suf=352` | ❌ |
| 1 Perfect Diamond + 1 Kris + 1 Staff + 1 Belt -> Savage Polearm | `kri` + `gpw` + `staf` + `belt` | `pole,mag,pre=191` | ❌ |
| 1 Strangling Gas Potion + 1 Healing Potion (Any) -> Antidote Potion | `gpl` + `hpot` | `yps` | ✅ |
| WIP 2 Arrows -> Bolts with MF + Sockets | `aqv,qty=2` | `cqv` <br><small>mag%/lvl (4), sock (1-3)</small> | ✅ |
| WIP 2 Bolts -> Arrows with MF + Sockets | `cqv,qty=2` | `aqv` <br><small>mag%/lvl (4), sock (1-3)</small> | ✅ |
| 3 Perfect Gems (Any) + 1 Magic Item -> Re-rolled Magic Item | `any,mag` + `gem4,qty=3` | `usetype,mag` | ✅ |
| 6 Perfect Skulls + 1 Rare Item -> 1 Low Quality Rare Item | `any,rar` + `skz,qty=6` | `usetype,rar` | ✅ |
| 1 Perfect Skull + 1 Rare Item + 1 Stone of Jordan -> 1 High Quality Rare Item | `any,rar` + `skz` + `The Stone of Jordan` | `usetype,rar` | ✅ |
| 1 Eld Rune + 1 Chipped Gem (Any) + 1 Low Quality Weapon -> Normal Weapon | `weap,low` + `r02` + `gem0` | `usetype,nor` | ❌ |
| 1 El Rune + 1 Chipped Gem (Any) + 1 Low Quality Armor -> Normal Armor | `armo,low` + `r01` + `gem0` | `usetype,nor` | ❌ |
| 1 Hel Rune + Scroll of Town Portal + 1 Socketed Item -> Clear Sockets on Item | `any,sock` + `r15` + `tsc` | `useitem,uns` | ✅ |
| 1 Uber Ancient Summon Material from Act 1 + Act2 + Act3 + Act 4 + Act 5 -> Portal to Colossal Summit | `ua1` + `ua2` + `ua3` + `ua4` + `ua5` | `Red Portal,lvl=137,qty=1` | ✅ |
| 3 Perfect Skull + 1 Rare Item + 1 Stone of Jordan -> Add 3 Socket to Rare Item | `any,rar,nos` + `skz,qty=3` + `The Stone of Jordan` | `useitem,sock=3` | ✅ |
| 2 Unique Jewerly = SOH | `jwly,uni,qty=2` + `wms` | `std` | ✅ |
| Seasonal Gift | `gft` | `r15g` <br>+ `r01g,qty=5` <br>+ `gem,qty=5` | ❌ |
| Infernal Mawstone + Item --> Rerolls Ethereal Set ; Potential Upgrade or Downgrade | `any,set,eth` + `rrr` | `usetype,set` <br><small>ethereal (1)</small> | ✅ |
| Infernal Mawstone + Item --> Rerolls Set; Potential Upgrade or Downgrade | `any,set,noe` + `rrr` | `usetype,set` | ✅ |
| Infernal Mawstone + Item --> Rerolls Ethereal Unique ; Potential Upgrade or Downgrade | `any,uni,eth` + `rrr` | `usetype,uni` <br><small>ethereal (1)</small> | ✅ |
| Infernal Mawstone + Item --> Rerolls Unique ; Potential Upgrade or Downgrade | `any,uni,noe` + `rrr` | `usetype,uni` | ✅ |
| Fracture Halo --> Return Base + Socketed Items | `any,sock` + `rtr` | `useitem,rem` | ✅ |
| 1 Thaw for Blank Charm | `wms` | `mfd` <br>+ `mfd` <br>+ `mfd` | ✅ |
| 2 Thaw for Modifiers Charm | `wms,qty=2` | `Charm Modifiers` | ✅ |
| 3 Thaw for Level Reward Charm | `wms,qty=3` | `Charm Level Reward` | ✅ |
| Wand of Lower Res | `wand,mag` + `voa` + `mpot` | `usetype,mag` <br><small>oskill (1)</small> | ✅ |
| Wand of Life Tap | `wand,mag` + `voa` + `hpot` | `usetype,mag` <br><small>oskill (1)</small> | ✅ |
| Staff of Teleportation | `staf,mag` + `bgn` | `usetype,mag` <br><small>charged (33-1)</small> | ✅ |
| Replenishing TP Book | `tbk` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Replenishing ID Book | `ibk` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Throwing Knife | `tkni` + `std` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Throwing Axe | `taxe` + `std` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Javelin | `jave` + `std` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Magic Item | `any,mag` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Rare Item | `any,rar` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Set Armor | `armo,set` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Set Weapon | `weap,set` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Unique Armor | `armo,uni` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Unique Weapon | `weap,uni` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Crafted Item | `any,crf` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Block Bows | `bow` + `fel` | `useitem` <br>+ `fel` | ✅ |
| Weapon + Flask = Ethereal Weapon | `weap,noe` + `fel` | `useitem` <br><small>ethereal (1)</small> | ✅ |
| Armor + Flask = Ethereal Armor | `armo,noe` + `fel` | `useitem` <br><small>ethereal (1)</small> | ✅ |
| MF + GF on Helm | `helm` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Weapon | `weap` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Amulet | `amu` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Shield | `shld` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Ring | `ring` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Gloves | `glov` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Boots | `boot` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Armor | `tors` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Belt | `belt` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| Melee Augment on Helm | `helm` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Weapon | `weap` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Amulet | `amu` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Shield | `shld` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Ring | `ring` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Gloves | `glov` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Boots | `boot` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Armor | `tors` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Belt | `belt` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Teleport + MF + GF on Armor | `tors` + `r33` + `r29` + `The Stone of Jordan` + `std` + `mls` | `useitem` <br><small>oskill (1), augmented1 (1), mag%/lvl (), gold%/lvl (), addxp (2)</small> | ✅ |
| Break Down Hellfire Torch -> 1 Hellfire Ashes | `Hellfire Torch` + `mls` | `tds` | ✅ |
| Hellfire Ash + Stamina Potion -> 2 Standard of Heroes | `tds` + `wms` | `std` <br>+ `std` | ✅ |
| Break Down Annihilus -> 3 Standard of Heroes | `Annihilus` + `mls` | `std` <br>+ `std` <br>+ `std` | ✅ |
| Break Down Gheed's Fortune -> 3 MF Potions | `Gheed's Fortune` + `mls` | `mfp` <br>+ `mfp` <br>+ `mfp` | ✅ |
| 1 Ort Rune + 1 Weapon -> Fully Repaired Weapon | `weap,noe` + `r09` | `useitem,rep,rch,qty=500` | ✅ |
| 1 Ral Rune + 1 Armor -> Fully Repaired Armor | `armo,noe` + `r08` | `useitem,rep,rch,qty=500` | ✅ |
| 1 Ort Rune + 1 Chipped Gem (Any) + 1 Weapon -> Fully Repaired and Recharged Weapon | `weap,noe` + `r09` + `gem0` | `useitem,rep,rch,qty=500` | ✅ |
| 1 Ral Rune + 1 Flawed Gem (Any) + 1 Armor -> Fully Repaired and Recharged Armor | `armo,noe` + `r08` + `gem1` | `useitem,rep,rch,qty=500` | ✅ |
| 3 pk1 = Matrons Den | `pk1,qty=3` | `Red Portal,qty=133` | ✅ |
| 2 pk1 + 1 pk2 = Matrons Den | `pk1,qty=2` + `pk2,qty=1` | `Red Portal,qty=133` | ✅ |
| 2 pk1 + 1 pk3 = Matrons Den | `pk1,qty=2` + `pk3,qty=1` | `Red Portal,qty=133` | ✅ |
| 3 pk2 = Forgotten Sands | `pk2,qty=3` | `Red Portal,qty=134` | ✅ |
| 2 pk2 + 1 pk1 = Forgotten Sands | `pk2,qty=2` + `pk1,qty=1` | `Red Portal,qty=134` | ✅ |
| 2 pk2 + 1 pk3 = Forgotten Sands | `pk2,qty=2` + `pk3,qty=1` | `Red Portal,qty=134` | ✅ |
| 3 pk3 = Furnace of pain | `pk3,qty=3` | `Red Portal,qty=135` | ✅ |
| 2 pk3 + 1 pk1 = Furnace of pain | `pk3,qty=2` + `pk1,qty=1` | `Red Portal,qty=135` | ✅ |
| 2 pk3 + 1 pk2 = Furnace of pain | `pk3,qty=2` + `pk2,qty=1` | `Red Portal,qty=135` | ✅ |
| pk1 + pk2 + pk3 = Random Uber | `pk1` + `pk2` + `pk3` | `Pandemonium Portal` | ✅ |
| 1 Diablo's Horn + 1 Baal's Eye + 1 Mephisto's Brain -> Portal to Tristram (Pandemonium Finale) | `dhn` + `bey` + `mbr` | `Pandemonium Finale Portal` | ✅ |
| 1 Twisted Essence of Suffering + 1 Charged Essence of Hatred + 1 Burning Essence of Terror + 1 Festering Essence of Destruction -> Uber Keys | `tes` + `ceh` + `bet` + `fed` | `pk1` <br>+ `pk2` <br>+ `pk3` | ✅ |
| 3 Twisted Essence of Suffering -> 1 Charged Essence of Hatred | `tes,qty=3` | `ceh` | ✅ |
| 3 Charged Essence of Hatred -> 1 Burning Essence of Terror | `ceh,qty=3` | `bet` | ✅ |
| 3 Burning Essence of Terror -> 1 Festering Essence of Destruction | `bet,qty=3` | `fed` | ✅ |
| 3 Festering Essence of Destruction -> Twisted Essence of Suffering | `fed,qty=3` | `tes,qty=3` | ✅ |
| 35 Standard of Heroes + Thawing Potion = Flask of Etheric Light | `std,qty=35` + `wms` | `fel` | ✅ |
| 35 Bricks + Thawing Potion = The Divine Standard | `brk,qty=35` + `wms` | `dsd` | ✅ |
| 35 Bricks + TP Scroll = Cham Rune | `brk,qty=35` + `tsc` | `r32` | ✅ |
| 35 Perfect Diamonds + Thawing Potion = Diablo's Soulstone | `gpw,qty=35` + `wms` | `dss` | ✅ |
| 35 Perfect Amethysts + Thawing Potion = 2 Unique Amulets | `gpv,qty=35` + `wms` | `amu,uni` <br>+ `amu,uni` | ✅ |
| 35 Perfect Rubies + Thawing Potion = 2 Unique Rings | `gpr,qty=35` + `wms` | `rin,uni` <br>+ `rin,uni` | ✅ |
| 35 Perfect Sapphires + Thawing Potion = Jewel | `gpb,qty=35` + `wms` | `jew,uni` | ✅ |
| 35 Perfect Emeralds + Thawing Potion = Gheed | `gpg,qty=35` + `wms` | `Gheed's Fortune` | ✅ |
| 35 Perfect Topazes + Thawing Potion = Vex Rune | `gpy,qty=35` + `wms` | `r24` | ✅ |
| 35 Perfect Skulls + Thawing Potion = Fracture Halo + Infernal Maw | `skz,qty=35` + `wms` | `rrr` <br>+ `rtr` | ✅ |
| 9 Pskulls + 3 Hellfire Ash + Larzuk's Forging Hammer + Unique Jewel = Random Unique Jewel | `skz,qty=9` + `lmr` + `jew,uni` + `tds,qty=3` | `jew,uni` | ✅ |
| 3 Chipped Amethysts -> Flawed Amethyst | `gcv,qty=3` | `gfv` | ✅ |
| 3 Flawed Amethysts -> Standard Amethyst | `gfv,qty=3` | `gsv` | ✅ |
| 3 Standard Amethysts -> Flawless Amethyst | `gsv,qty=3` | `gzv` | ✅ |
| 3 Flawless Amethysts -> Perfect Amethyst | `gzv,qty=3` | `gpv` | ✅ |
| 3 Chipped Rubies -> Flawed Ruby | `gcr,qty=3` | `gfr` | ✅ |
| 3 Flawed Rubies -> Standard Ruby | `gfr,qty=3` | `gsr` | ✅ |
| 3 Standard Rubies -> Flawless Ruby | `gsr,qty=3` | `glr` | ✅ |
| 3 Flawless Rubies -> Perfect Ruby | `glr,qty=3` | `gpr` | ✅ |
| 3 Chipped Sapphires -> Flawed Sapphire | `gcb,qty=3` | `gfb` | ✅ |
| 3 Flawed Sapphires -> Standard Sapphire | `gfb,qty=3` | `gsb` | ✅ |
| 3 Standard Sapphires -> Flawless Sapphire | `gsb,qty=3` | `glb` | ✅ |
| 3 Flawless Sapphires -> Perfect Sapphire | `glb,qty=3` | `gpb` | ✅ |
| 3 Chipped Topazes -> Flawed Topaz | `gcy,qty=3` | `gfy` | ✅ |
| 3 Flawed Topazes -> Standard Topaz | `gfy,qty=3` | `gsy` | ✅ |
| 3 Standard Topazes -> Flawless Topaz | `gsy,qty=3` | `gly` | ✅ |
| 3 Flawless Topazes -> Perfect Topaz | `gly,qty=3` | `gpy` | ✅ |
| 3 Chipped Emeralds -> Flawed Emerald | `gcg,qty=3` | `gfg` | ✅ |
| 3 Flawed Emeralds -> Standard Emerald | `gfg,qty=3` | `gsg` | ✅ |
| 3 Standard Emeralds -> Flawless Emerald | `gsg,qty=3` | `glg` | ✅ |
| 3 Flawless Emeralds -> Perfect Emerald | `glg,qty=3` | `gpg` | ✅ |
| 3 Chipped Diamonds -> Flawed Diamond | `gcw,qty=3` | `gfw` | ✅ |
| 3 Flawed Diamonds -> Standard Diamond | `gfw,qty=3` | `gsw` | ✅ |
| 3 Standard Diamonds -> Flawless Diamond | `gsw,qty=3` | `glw` | ✅ |
| 3 Flawless Diamonds -> Perfect Diamond | `glw,qty=3` | `gpw` | ✅ |
| 3 Chipped Skulls -> Flawed Skull | `skc,qty=3` | `skf` | ✅ |
| 3 Flawed Skulls -> Standard Skull | `skf,qty=3` | `sku` | ✅ |
| 3 Standard Skulls -> Flawless Skull | `sku,qty=3` | `skl` | ✅ |
| 3 Flawless Skulls -> Perfect Skull | `skl,qty=3` | `skz` | ✅ |
| 9 Chipped Amethysts -> 3 Flawed Amethyst | `gcv,qty=9` | `gfv` <br>+ `gfv` <br>+ `gfv` | ✅ |
| 9 Flawed Amethysts -> 3 Standard Amethyst | `gfv,qty=9` | `gsv` <br>+ `gsv` <br>+ `gsv` | ✅ |
| 9 Standard Amethysts -> 3 Flawless Amethyst | `gsv,qty=9` | `gzv` <br>+ `gzv` <br>+ `gzv` | ✅ |
| 9 Flawless Amethysts -> 3 Perfect Amethyst | `gzv,qty=9` | `gpv` <br>+ `gpv` <br>+ `gpv` | ✅ |
| 9 Chipped Rubies -> 3 Flawed Ruby | `gcr,qty=9` | `gfr` <br>+ `gfr` <br>+ `gfr` | ✅ |
| 9 Flawed Rubies -> 3 Standard Ruby | `gfr,qty=9` | `gsr` <br>+ `gsr` <br>+ `gsr` | ✅ |
| 9 Standard Rubies -> 3 Flawless Ruby | `gsr,qty=9` | `glr` <br>+ `glr` <br>+ `glr` | ✅ |
| 9 Flawless Rubies -> 3 Perfect Ruby | `glr,qty=9` | `gpr` <br>+ `gpr` <br>+ `gpr` | ✅ |
| 9 Chipped Sapphires -> 3 Flawed Sapphire | `gcb,qty=9` | `gfb` <br>+ `gfb` <br>+ `gfb` | ✅ |
| 9 Flawed Sapphires -> 3 Standard Sapphire | `gfb,qty=9` | `gsb` <br>+ `gsb` <br>+ `gsb` | ✅ |
| 9 Standard Sapphires -> 3 Flawless Sapphire | `gsb,qty=9` | `glb` <br>+ `glb` <br>+ `glb` | ✅ |
| 9 Flawless Sapphires -> 3 Perfect Sapphire | `glb,qty=9` | `gpb` <br>+ `gpb` <br>+ `gpb` | ✅ |
| 9 Chipped Topazes -> 3 Flawed Topaz | `gcy,qty=9` | `gfy` <br>+ `gfy` <br>+ `gfy` | ✅ |
| 9 Flawed Topazes -> 3 Standard Topaz | `gfy,qty=9` | `gsy` <br>+ `gsy` <br>+ `gsy` | ✅ |
| 9 Standard Topazes -> 3 Flawless Topaz | `gsy,qty=9` | `gly` <br>+ `gly` <br>+ `gly` | ✅ |
| 9 Flawless Topazes -> 3 Perfect Topaz | `gly,qty=9` | `gpy` <br>+ `gpy` <br>+ `gpy` | ✅ |
| 9 Chipped Emeralds -> 3 Flawed Emerald | `gcg,qty=9` | `gfg` <br>+ `gfg` <br>+ `gfg` | ✅ |
| 9 Flawed Emeralds -> 3 Standard Emerald | `gfg,qty=9` | `gsg` <br>+ `gsg` <br>+ `gsg` | ✅ |
| 9 Standard Emeralds -> 3 Flawless Emerald | `gsg,qty=9` | `glg` <br>+ `glg` <br>+ `glg` | ✅ |
| 9 Flawless Emeralds -> 3 Perfect Emerald | `glg,qty=9` | `gpg` <br>+ `gpg` <br>+ `gpg` | ✅ |
| 9 Chipped Diamonds -> 3 Flawed Diamond | `gcw,qty=9` | `gfw` <br>+ `gfw` <br>+ `gfw` | ✅ |
| 9 Flawed Diamonds -> 3 Standard Diamond | `gfw,qty=9` | `gsw` <br>+ `gsw` <br>+ `gsw` | ✅ |
| 9 Standard Diamonds -> 3 Flawless Diamond | `gsw,qty=9` | `glw` <br>+ `glw` <br>+ `glw` | ✅ |
| 9 Flawless Diamonds -> 3 Perfect Diamond | `glw,qty=9` | `gpw` <br>+ `gpw` <br>+ `gpw` | ✅ |
| 9 Chipped Skulls -> 3 Flawed Skull | `skc,qty=9` | `skf` <br>+ `skf` <br>+ `skf` | ✅ |
| 9 Flawed Skulls -> 3 Standard Skull | `skf,qty=9` | `sku` <br>+ `sku` <br>+ `sku` | ✅ |
| 9 Standard Skulls -> 3 Flawless Skull | `sku,qty=9` | `skl` <br>+ `skl` <br>+ `skl` | ✅ |
| 9 Flawless Skulls -> 3 Perfect Skull | `skl,qty=9` | `skz` <br>+ `skz` <br>+ `skz` | ✅ |
| 3 Perfect Gems + Thawing Potion + 1 Standard Amethyst -> 3 Perfect Amethyst | `gem4,qty=3` + `wms` + `gsv` | `gpv` <br>+ `gpv` <br>+ `gpv` | ✅ |
| 3 Perfect Gems + Thawing Potion + 1 Standard Diamond -> 3 Perfect Diamonds | `gem4,qty=3` + `wms` + `gsw` | `gpw` <br>+ `gpw` <br>+ `gpw` | ✅ |
| 3 Perfect Gems + Thawing Potion + 1 Standard Emerald -> 3 Perfect Emeralds | `gem4,qty=3` + `wms` + `gsg` | `gpg` <br>+ `gpg` <br>+ `gpg` | ✅ |
| 3 Perfect Gems + Thawing Potion + 1 Standard Ruby -> 3 Perfect Rubies | `gem4,qty=3` + `wms` + `gsr` | `gpr` <br>+ `gpr` <br>+ `gpr` | ✅ |
| 3 Perfect Gems + Thawing Potion + 1 Standard Sapphire -> 3 Perfect Sapphires | `gem4,qty=3` + `wms` + `gsb` | `gpb` <br>+ `gpb` <br>+ `gpb` | ✅ |
| 3 Perfect Gems + Thawing Potion + 1 Standard Topaz -> 3 Perfect Topazes | `gem4,qty=3` + `wms` + `gsy` | `gpy` <br>+ `gpy` <br>+ `gpy` | ✅ |
| 3 Perfect Gems + Thawing Potion + 1 Standard Skull -> 3 Perfect Skulls | `gem4,qty=3` + `wms` + `sku` | `skz` <br>+ `skz` <br>+ `skz` | ✅ |
| 1 Zod + Standard Gem -> Cham Rune | `r33,qty=1` + `gem2` | `r32` | ✅ |
| 1 Cham + Standard Gem -> Jah Rune | `r32,qty=1` + `gem2` | `r31` | ✅ |
| 1 Jah + Standard Gem -> Ber Rune | `r31,qty=1` + `gem2` | `r30` | ✅ |
| 1 Ber + Standard Gem -> Sur Rune | `r30,qty=1` + `gem2` | `r29` | ✅ |
| 1 Sur + Standard Gem -> Lo  Rune | `r29,qty=1` + `gem2` | `r28` | ✅ |
| 1 Lo + Standard Gem -> Ohm Rune | `r28,qty=1` + `gem2` | `r27` | ✅ |
| 1 Ohm + Standard Gem -> Vex Rune | `r27,qty=1` + `gem2` | `r26` | ✅ |
| 1 Vex + Standard Gem -> Gul Rune | `r26,qty=1` + `gem2` | `r25` | ✅ |
| 1 Gul + Standard Gem -> Ist Rune | `r25,qty=1` + `gem2` | `r24` | ✅ |
| 1 Ist + Standard Gem -> Mal Rune | `r24,qty=1` + `gem2` | `r23` | ✅ |
| 1 Mal + Standard Gem -> Um Rune | `r23,qty=1` + `gem2` | `r22` | ✅ |
| 1 Um + Standard Gem -> Pul Rune | `r22,qty=1` + `gem2` | `r21` | ✅ |
| 1 Pul + Standard Gem -> Lem Rune | `r21,qty=1` + `gem2` | `r20` | ✅ |
| 1 Lem + Standard Gem -> Fal Rune | `r20,qty=1` + `gem2` | `r19` | ✅ |
| 1 Fal + Standard Gem -> Ko Rune | `r19,qty=1` + `gem2` | `r18` | ✅ |
| 1 Ko + Standard Gem -> Lum Rune | `r18,qty=1` + `gem2` | `r17` | ✅ |
| 1 Lum + Standard Gem -> Io Rune | `r17,qty=1` + `gem2` | `r16` | ✅ |
| 1 Io + Standard Gem -> Hel Rune | `r16,qty=1` + `gem2` | `r15` | ✅ |
| 1 Hel + Standard Gem -> Dol  Rune | `r15,qty=1` + `gem2` | `r14` | ✅ |
| 1 Dol + Standard Gem -> Shael Rune | `r14,qty=1` + `gem2` | `r13` | ✅ |
| 1 Shael + Standard Gem -> Sol Rune | `r13,qty=1` + `gem2` | `r12` | ✅ |
| 1 Sol + Standard Gem -> Amn Rune | `r12,qty=1` + `gem2` | `r11` | ✅ |
| 1 Amn + Standard Gem -> Thul Rune | `r11,qty=1` + `gem2` | `r10` | ✅ |
| 1 Thul + Standard Gem -> Ort Rune | `r10,qty=1` + `gem2` | `r09` | ✅ |
| 1 Ort + Standard Gem -> Ral Rune | `r09,qty=1` + `gem2` | `r08` | ✅ |
| 1 Ral + Standard Gem -> Tal Rune | `r08,qty=1` + `gem2` | `r07` | ✅ |
| 1 Tal + Standard Gem -> Ith Rune | `r07,qty=1` + `gem2` | `r06` | ✅ |
| 1 Ith + Standard Gem -> Eth Rune | `r06,qty=1` + `gem2` | `r05` | ✅ |
| 1 Eth + Standard Gem -> Nef Rune | `r05,qty=1` + `gem2` | `r04` | ✅ |
| 1 Nef + Standard Gem -> Tir Rune | `r04,qty=1` + `gem2` | `r03` | ✅ |
| 1 Tir + Standard Gem -> Eld Rune | `r03,qty=1` + `gem2` | `r02` | ✅ |
| 1 Eld + Standard Gem -> El Rune | `r02,qty=1` + `gem2` | `r01` | ✅ |
| 1 El + Standard Gem -> Rejuv | `r01,qty=1` + `gem2` | `rvl` | ✅ |
| 3 El Runes -> Eld Rune | `r01,qty=3` | `r02` | ✅ |
| 3 Eld Runes -> Tir Rune | `r02,qty=3` | `r03` | ✅ |
| 3 Tir Runes -> Nef Rune | `r03,qty=3` | `r04` | ✅ |
| 3 Nef Runes -> Eth Rune | `r04,qty=3` | `r05` | ✅ |
| 3 Eth Runes -> Ith Rune | `r05,qty=3` | `r06` | ✅ |
| 3 Ith Runes -> Tal Rune | `r06,qty=3` | `r07` | ✅ |
| 3 Tal Runes -> Ral Rune | `r07,qty=3` | `r08` | ✅ |
| 3 Ral Runes -> Ort Rune | `r08,qty=3` | `r09` | ✅ |
| 3 Ort Runes -> Thul Rune | `r09,qty=3` | `r10` | ✅ |
| 3 Thul Runes -> Amn Rune | `r10,qty=3` | `r11` | ✅ |
| 3 Amn Runes -> Sol Rune | `r11,qty=3` | `r12` | ✅ |
| 3 Sol Runes -> Shael Rune | `r12,qty=3` | `r13` | ✅ |
| 3 Shael Runes  -> Dol Rune | `r13,qty=3` | `r14` | ✅ |
| 3 Dol Runes  -> Hel Rune | `r14,qty=3` | `r15` | ✅ |
| 3 Hel Runes -> Io Rune | `r15,qty=3` | `r16` | ✅ |
| 3 Io Runes -> Lum Rune | `r16,qty=3` | `r17` | ✅ |
| 3 Lum Runes  -> Ko Rune | `r17,qty=3` | `r18` | ✅ |
| 3 Ko Runes -> Fal Rune | `r18,qty=3` | `r19` | ✅ |
| 3 Fal Runes -> Lem Rune | `r19,qty=3` | `r20` | ✅ |
| 3 Lem Runes -> Pul Rune | `r20,qty=3` | `r21` | ✅ |
| 2 Pul Runes -> Um Rune | `r21,qty=2` + `wms` | `r22` | ✅ |
| 2 Um Runes -> Mal Rune | `r22,qty=2` + `wms` | `r23` | ✅ |
| 2 Mal Runes -> Ist Rune | `r23,qty=2` + `wms` | `r24` | ✅ |
| 2 Ist Runes -> Gul Rune | `r24,qty=2` + `wms` | `r25` | ✅ |
| 2 Gul Runes -> Vex Rune | `r25,qty=2` + `wms` | `r26` | ✅ |
| 2 Vex Runes -> Ohm Rune | `r26,qty=2` + `wms` | `r27` | ✅ |
| 2 Ohm Runes -> Lo Rune | `r27,qty=2` + `wms` | `r28` | ✅ |
| 2 Lo Runes -> Sur Rune | `r28,qty=2` + `wms` | `r29` | ✅ |
| 2 Sur Runes -> Ber Rune | `r29,qty=2` + `wms` | `r30` | ✅ |
| 2 Ber Runes -> Jah Rune | `r30,qty=2` + `wms` | `r31` | ✅ |
| 2 Jah Runes  -> Cham Rune | `r31,qty=2` + `wms` | `r32` | ✅ |
| 2 Cham Runes -> Zod Rune | `r32,qty=2` + `wms` | `r33` | ✅ |
| 9 El Runes -> 3 Eld Rune | `r01,qty=9` | `r02` <br>+ `r02` <br>+ `r02` | ✅ |
| 9 Eld Runes -> 3 Tir Rune | `r02,qty=9` | `r03` <br>+ `r03` <br>+ `r03` | ✅ |
| 9 Tir Runes -> 3 Nef Rune | `r03,qty=9` | `r04` <br>+ `r04` <br>+ `r04` | ✅ |
| 9 Nef Runes -> 3 Eth Rune | `r04,qty=9` | `r05` <br>+ `r05` <br>+ `r05` | ✅ |
| 9 Eth Runes -> 3 Ith Rune | `r05,qty=9` | `r06` <br>+ `r06` <br>+ `r06` | ✅ |
| 9 Ith Runes -> 3 Tal Rune | `r06,qty=9` | `r07` <br>+ `r07` <br>+ `r07` | ✅ |
| 9 Tal Runes -> 3 Ral Rune | `r07,qty=9` | `r08` <br>+ `r08` <br>+ `r08` | ✅ |
| 9 Ral Runes -> 3 Ort Rune | `r08,qty=9` | `r09` <br>+ `r09` <br>+ `r09` | ✅ |
| 9 Ort Runes -> 3 Thul Rune | `r09,qty=9` | `r10` <br>+ `r10` <br>+ `r10` | ✅ |
| 9 Thul Runes -> 3 Amn Rune | `r10,qty=9` | `r11` <br>+ `r11` <br>+ `r11` | ✅ |
| 9 Amn Runes -> 3 Sol Rune | `r11,qty=9` | `r12` <br>+ `r12` <br>+ `r12` | ✅ |
| 9 Sol Runes -> 3 Shael Rune | `r12,qty=9` | `r13` <br>+ `r13` <br>+ `r13` | ✅ |
| 9 Shael Runes -> 3 Dol Rune | `r13,qty=9` | `r14` <br>+ `r14` <br>+ `r14` | ✅ |
| 9 Dol Runes -> 3 Hel Rune | `r14,qty=9` | `r15` <br>+ `r15` <br>+ `r15` | ✅ |
| 9 Hel Runes -> 3 Io Rune | `r15,qty=9` | `r16` <br>+ `r16` <br>+ `r16` | ✅ |
| 9 Io Runes -> 3 Lum Rune | `r16,qty=9` | `r17` <br>+ `r17` <br>+ `r17` | ✅ |
| 9 Lum Runes -> 3 Ko Rune | `r17,qty=9` | `r18` <br>+ `r18` <br>+ `r18` | ✅ |
| 9 Ko Runes -> 3 Fal Rune | `r18,qty=9` | `r19` <br>+ `r19` <br>+ `r19` | ✅ |
| 9 Fal Runes -> 3 Lem Rune | `r19,qty=9` | `r20` <br>+ `r20` <br>+ `r20` | ✅ |
| 9 Lem Runes -> 3 Pul Rune | `r20,qty=9` | `r21` <br>+ `r21` <br>+ `r21` | ✅ |
| 6 Pul Runes -> 3 Um Rune | `r21,qty=6` + `wms` | `r22` <br>+ `r22` <br>+ `r22` | ✅ |
| 6 Um Runes -> 3 Mal Rune | `r22,qty=6` + `wms` | `r23` <br>+ `r23` <br>+ `r23` | ✅ |
| 6 Mal Runes -> 3 Ist Rune | `r23,qty=6` + `wms` | `r24` <br>+ `r24` <br>+ `r24` | ✅ |
| 6 Ist Runes -> 3 Gul Rune | `r24,qty=6` + `wms` | `r25` <br>+ `r25` <br>+ `r25` | ✅ |
| 6 Gul Runes -> 3 Vex Rune | `r25,qty=6` + `wms` | `r26` <br>+ `r26` <br>+ `r26` | ✅ |
| 6 Vex Runes -> 3 Ohm Rune | `r26,qty=6` + `wms` | `r27` <br>+ `r27` <br>+ `r27` | ✅ |
| 6 Ohm Runes -> 3 Lo Rune | `r27,qty=6` + `wms` | `r28` <br>+ `r28` <br>+ `r28` | ✅ |
| 6 Lo Runes -> 3 Sur Rune | `r28,qty=6` + `wms` | `r29` <br>+ `r29` <br>+ `r29` | ✅ |
| 6 Sur Runes -> 3 Ber Rune | `r29,qty=6` + `wms` | `r30` <br>+ `r30` <br>+ `r30` | ✅ |
| 6 Ber Runes -> 3 Jah Rune | `r30,qty=6` + `wms` | `r31` <br>+ `r31` <br>+ `r31` | ✅ |
| 6 Jah Runes -> 3 Cham Rune | `r31,qty=6` + `wms` | `r32` <br>+ `r32` <br>+ `r32` | ✅ |
| 6 Cham Runes -> 3 Zod Rune | `r32,qty=6` + `wms` | `r33` <br>+ `r33` <br>+ `r33` | ✅ |
| 1 Magic Full Helm + 1 Jewel + 1 Ith Rune + 1 Perfect Sapphire -> Hit Power Helm | `helm,mag,noe` + `jew` + `r06` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), att (150-200)</small> | ✅ |
| 1 Magic Full Helm + 1 Jewel + 1 Ith Rune + 1 Perfect Sapphire + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Helm | `helm,mag,noe` + `jew` + `r06` + `gpb` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), att (150-200), ethereal (1)</small> | ✅ |
| 1 Magic Full Helm + 1 Jewel + 1 Ith Rune + 1 Perfect Sapphire -> Hit Power Helm | `helm,mag,eth` + `jew` + `r06` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), att (150-200), ethereal (1)</small> | ✅ |
| 1 Magic Chain Boots + 1 Jewel + 1 Ral Rune + 1 Perfect Sapphire -> Hit Power Boots | `boot,mag,noe` + `jew` + `r08` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (10), dex (10-15)</small> | ✅ |
| 1 Magic Chain Boots + 1 Jewel + 1 Ral Rune + 1 Perfect Sapphire + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Boots | `boot,mag,noe` + `jew` + `r08` + `gpb` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (10), dex (10-15), ethereal (1)</small> | ✅ |
| 1 Magic Chain Boots + 1 Jewel + 1 Ral Rune + 1 Perfect Sapphire -> Hit Power Boots | `boot,mag,eth` + `jew` + `r08` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (10), dex (10-15), ethereal (1)</small> | ✅ |
| 1 Magic Chain Gloves + 1 Jewel + 1 Ort Rune + 1 Perfect Sapphire -> Hit Power Gloves | `glov,mag,noe` + `jew` + `r09` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), knock (1)</small> | ✅ |
| 1 Magic Chain Gloves + 1 Jewel + 1 Ort Rune + 1 Perfect Sapphire + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Gloves | `glov,mag,noe` + `jew` + `r09` + `gpb` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), knock (1), ethereal (1)</small> | ✅ |
| 1 Magic Chain Gloves + 1 Jewel + 1 Ort Rune + 1 Perfect Sapphire -> Hit Power Gloves | `glov,mag,eth` + `jew` + `r09` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), knock (1), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Belt + 1 Jewel + 1 Tal Rune + 1 Perfect Sapphire -> Hit Power Belt | `belt,mag,noe` + `jew` + `r07` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), dmg-to-mana (20)</small> | ✅ |
| 1 Magic Heavy Belt + 1 Jewel + 1 Tal Rune + 1 Perfect Sapphire + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Belt | `belt,mag,noe` + `jew` + `r07` + `gpb` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), dmg-to-mana (20), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Belt + 1 Jewel + 1 Tal Rune + 1 Perfect Sapphire -> Hit Power Belt | `belt,mag,eth` + `jew` + `r07` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), dmg-to-mana (20), ethereal (1)</small> | ✅ |
| 1 Magic Gothic Shield + 1 Jewel + 1 Eth Rune + 1 Perfect Sapphire -> Hit Power Shield | `shld,mag,noe` + `jew` + `r05` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), block1 (30), block (20)</small> | ✅ |
| 1 Magic Gothic Shield + 1 Jewel + 1 Eth Rune + 1 Perfect Sapphire + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Shield | `shld,mag,noe` + `jew` + `r05` + `gpb` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), block1 (30), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Gothic Shield + 1 Jewel + 1 Eth Rune + 1 Perfect Sapphire -> Hit Power Shield | `shld,mag,eth` + `jew` + `r05` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), block1 (30), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Field Plate + 1 Jewel + 1 Nef Rune + 1 Perfect Sapphire -> Hit Power Body | `tors,mag,noe` + `jew` + `r04` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), dmg% (35-60), balance1 (30-40)</small> | ✅ |
| 1 Magic Field Plate + 1 Jewel + 1 Nef Rune + 1 Perfect Sapphire + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Body | `tors,mag,noe` + `jew` + `r04` + `gpb` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), dmg% (35-60), balance1 (30-40), ethereal (1)</small> | ✅ |
| 1 Magic Field Plate + 1 Jewel + 1 Nef Rune + 1 Perfect Sapphire -> Hit Power Body | `tors,mag,eth` + `jew` + `r04` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), dmg% (35-60), balance1 (30-40), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + 1 Jewel + Thul Rune + 1 Perfect Sapphire -> Hit Power Amulet | `amul,mag` + `jew` + `r10` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), att (200-250), balance1 (15-20)</small> | ✅ |
| 1 Magic Ring + 1 Jewel + 1 Amn Rune + 1 Perfect Sapphire -> Hit Power Ring | `ring,mag` + `jew` + `r11` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), dmg-max (3-5), dex (5-10)</small> | ✅ |
| 1 Magic Blunt Weapon + 1 Jewel + 1 Tir Rune + 1 Perfect Sapphire -> Hit Power Weapon | `weap,mag,noe` + `jew` + `r03` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), dmg% (50-80)</small> | ✅ |
| 1 Magic Blunt Weapon + 1 Jewel + 1 Tir Rune + 1 Perfect Sapphire + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Weapon | `weap,mag,noe` + `jew` + `r03` + `gpb` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Blunt Weapon + 1 Jewel + 1 Tir Rune + 1 Perfect Sapphire -> Hit Power Weapon | `weap,mag,eth` + `jew` + `r03` + `gpb` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Helm + 1 Jewel + 1 Ral Rune + 1 Perfect Ruby -> Blood Helm | `helm,mag,noe` + `jew` + `r08` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), deadly (15-20)</small> | ✅ |
| 1 Magic Helm + 1 Jewel + 1 Ral Rune + 1 Perfect Ruby  + 1 Eth Rune + 1 Chasi's Malus -> Blood Helm | `helm,mag,noe` + `jew` + `r08` + `gpr` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), deadly (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Helm + 1 Jewel + 1 Ral Rune + 1 Perfect Ruby -> Blood Helm | `helm,mag,eth` + `jew` + `r08` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), deadly (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Light Plated Boots + 1 Jewel + 1 Eth Rune + 1 Perfect Ruby -> Blood Boots | `boot,mag,noe` + `jew` + `r05` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), heal-kill (3-6)</small> | ✅ |
| 1 Magic Light Plated Boots + 1 Jewel + 1 Eth Rune + 1 Perfect Ruby + 1 Eth Rune + 1 Chasi's Malus -> Blood Boots | `boot,mag,noe` + `jew` + `r05` + `gpr` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Light Plated Boots + 1 Jewel + 1 Eth Rune + 1 Perfect Ruby -> Blood Boots | `boot,mag,eth` + `jew` + `r05` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Gloves + 1 Jewel + 1 Nef Rune + 1 Perfect Ruby -> Blood Gloves | `glov,mag,noe` + `jew` + `r04` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), crush (5-10)</small> | ✅ |
| 1 Magic Heavy Gloves + 1 Jewel + 1 Nef Rune + 1 Perfect Ruby + 1 Eth Rune + 1 Chasi's Malus -> Blood Gloves | `glov,mag,noe` + `jew` + `r04` + `gpr` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), crush (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Gloves + 1 Jewel + 1 Nef Rune + 1 Perfect Ruby -> Blood Gloves | `glov,mag,eth` + `jew` + `r04` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), crush (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Belt + 1 Jewel + 1 Tal Rune + 1 Perfect Ruby -> Blood Belt | `belt,mag,noe` + `jew` + `r07` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), openwounds (15-20)</small> | ✅ |
| 1 Magic Belt + 1 Jewel + 1 Tal Rune + 1 Perfect Ruby + 1 Eth Rune + 1 Chasi's Malus -> Blood Belt | `belt,mag,noe` + `jew` + `r07` + `gpr` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), openwounds (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Belt + 1 Jewel + 1 Tal Rune + 1 Perfect Ruby -> Blood Belt | `belt,mag,eth` + `jew` + `r07` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), openwounds (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Spiked Shield + 1 Jewel + 1 Ith Rune + 1 Perfect Ruby -> Blood Shield | `shld,mag,noe` + `jew` + `r06` + `gpr` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), block (20)</small> | ✅ |
| 1 Magic Spiked Shield + 1 Jewel + 1 Ith Rune + 1 Perfect Ruby + 1 Eth Rune + 1 Chasi's Malus -> Blood Shield | `shld,mag,noe` + `jew` + `r06` + `gpr` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Spiked Shield + 1 Jewel + 1 Ith Rune + 1 Perfect Ruby -> Blood Shield | `shld,mag,eth` + `jew` + `r06` + `gpr` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Plate Mail + 1 Jewel + 1 Thul Rune + 1 Perfect Ruby -> Blood Body | `tors,mag,noe` + `jew` + `r10` + `gpr` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), heal-kill (3-6)</small> | ✅ |
| 1 Magic Plate Mail + 1 Jewel + 1 Thul Rune + 1 Perfect Ruby + 1 Eth Rune + 1 Chasi's Malus -> Blood Body | `tors,mag,noe` + `jew` + `r10` + `gpr` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Plate Mail + 1 Jewel + 1 Thul Rune + 1 Perfect Ruby -> Blood Body | `tors,mag,eth` + `jew` + `r10` + `gpr` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + 1 Jewel + 1 Amn Rune + 1 Perfect Ruby -> Blood Amulet | `amul,mag` + `jew` + `r11` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), move1 (10)</small> | ✅ |
| 1 Magic Ring + 1 Jewel + 1 Sol Rune + 1 Perfect Ruby -> Blood Ring | `ring,mag` + `jew` + `r12` + `gpr` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), str (5-10)</small> | ✅ |
| 1 Magic Axe + 1 Jewel + Ort Rune + 1 Perfect Ruby -> Blood Weapon | `weap,mag,noe` + `jew` + `r09` + `gpr` | `usetype,crf` <br><small>lifesteal (3-6), hp (30-40), dmg% (50-80)</small> | ✅ |
| 1 Magic Axe + 1 Jewel + Ort Rune + 1 Perfect Ruby + 1 Eth Rune + 1 Chasi's Malus -> Blood Weapon | `weap,mag,noe` + `jew` + `r09` + `gpr` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (3-6), hp (30-40), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Axe + 1 Jewel + Ort Rune + 1 Perfect Ruby -> Blood Weapon | `weap,mag,eth` + `jew` + `r09` + `gpr` | `usetype,crf` <br><small>lifesteal (3-6), hp (30-40), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Mask + 1 Jewel + Nef Rune + 1 Perfect Amethyst -> Caster Helm | `helm,mag,noe` + `jew` + `r04` + `gpv` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10)</small> | ✅ |
| 1 Magic Mask + 1 Jewel + Nef Rune + 1 Perfect Amethyst + 1 Eth Rune + 1 Chasi's Malus -> Caster Helm | `helm,mag,noe` + `jew` + `r04` + `gpv` + `r05` + `mls` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Mask + 1 Jewel + Nef Rune + 1 Perfect Amethyst -> Caster Helm | `helm,mag,eth` + `jew` + `r04` + `gpv` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Boots + 1 Jewel + Thul Rune + 1 Perfect Amethyst -> Caster Boots | `boot,mag,noe` + `jew` + `r10` + `gpv` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), mana% (5-10)</small> | ✅ |
| 1 Magic Boots + 1 Jewel + Thul Rune + 1 Perfect Amethyst + 1 Eth Rune + 1 Chasi's Malus -> Caster Boots | `boot,mag,noe` + `jew` + `r10` + `gpv` + `r05` + `mls` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), mana% (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Boots + 1 Jewel + Thul Rune + 1 Perfect Amethyst -> Caster Boots | `boot,mag,eth` + `jew` + `r10` + `gpv` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), mana% (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Leather Gloves + 1 Jewel + Ort Rune + 1 Perfect Amethyst -> Caster Gloves | `glov,mag,noe` + `jew` + `r09` + `gpv` | `usetype,crf` <br><small>mana-kill (1-3), mana (10-20), cast1 (10)</small> | ✅ |
| 1 Magic Leather Gloves + 1 Jewel + Ort Rune + 1 Perfect Amethyst + 1 Eth Rune + 1 Chasi's Malus -> Caster Gloves | `glov,mag,noe` + `jew` + `r09` + `gpv` + `r05` + `mls` | `usetype,crf` <br><small>mana-kill (1-3), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Leather Gloves + 1 Jewel + Ort Rune + 1 Perfect Amethyst -> Caster Gloves | `glov,mag,eth` + `jew` + `r09` + `gpv` | `usetype,crf` <br><small>mana-kill (1-3), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Light Belt + 1 Jewel + Ith Rune + 1 Perfect Amethyst -> Caster Belt | `belt,mag,noe` + `jew` + `r06` + `gpv` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10)</small> | ✅ |
| 1 Magic Light Belt + 1 Jewel + Ith Rune + 1 Perfect Amethyst + 1 Eth Rune + 1 Chasi's Malus -> Caster Belt | `belt,mag,noe` + `jew` + `r06` + `gpv` + `r05` + `mls` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Light Belt + 1 Jewel + Ith Rune + 1 Perfect Amethyst -> Caster Belt | `belt,mag,eth` + `jew` + `r06` + `gpv` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Small Shield + 1 Jewel + 1 Eth Rune + 1 Perfect Amethyst -> Caster Shield | `shld,mag,noe` + `jew` + `r05` + `gpv` | `usetype,crf` <br><small>cast1 (10), mana (10-20), block (20), allskills (1)</small> | ✅ |
| 1 Magic Small Shield + 1 Jewel + 1 Eth Rune + 1 Perfect Amethyst + 1 Eth Rune + 1 Chasi's Malus -> Caster Shield | `shld,mag,noe` + `jew` + `r05,qty=2` + `gpv` + `mls` | `usetype,crf` <br><small>cast1 (15), mana (10-20), block (20), ethereal (1), allskills (1)</small> | ✅ |
| 1 Magic Small Shield + 1 Jewel + 1 Eth Rune + 1 Perfect Amethyst -> Caster Shield | `shld,mag,eth` + `jew` + `r05` + `gpv` | `usetype,crf` <br><small>cast1 (15), mana (10-20), block (20), ethereal (1), allskills (1)</small> | ✅ |
| 1 Magic Light Plate + 1 Jewel + 1 Tal Rune + 1 Perfect Amethyst -> Caster Body | `tors,mag,noe` + `jew` + `r07` + `gpv` | `usetype,crf` <br><small>cast1 (20), mana (10-20), mana-kill (5-8)</small> | ✅ |
| 1 Magic Light Plate + 1 Jewel + 1 Tal Rune + 1 Perfect Amethyst + 1 Eth Rune + 1 Chasi's Malus -> Caster Body | `tors,mag,noe` + `jew` + `r07` + `gpv` + `r05` + `mls` | `usetype,crf` <br><small>cast1 (20), mana (10-20), mana-kill (5-8), ethereal (1)</small> | ✅ |
| 1 Magic Light Plate + 1 Jewel + 1 Tal Rune + 1 Perfect Amethyst -> Caster Body | `tors,mag,eth` + `jew` + `r07` + `gpv` | `usetype,crf` <br><small>cast1 (20), mana (10-20), mana-kill (5-8), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + 1 Jewel + 1 Ral Rune + 1 Perfect Amethyst -> Caster Amulet | `amul,mag` + `jew` + `r08` + `gpv` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (5-10)</small> | ✅ |
| 1 Magic Ring + 1 Jewel + 1 Amn Rune + 1 Perfect Amethyst -> Caster Ring | `ring,mag` + `jew` + `r11` + `gpv` | `usetype,crf` <br><small>mana-kill (1-2), mana (10-20), enr (5-10)</small> | ✅ |
| 1 Magic Rod + 1 Jewel + 1 Tir Rune + 1 Perfect Amethyst -> Caster Weapon | `weap,mag,noe` + `jew` + `r03` + `gpv` | `usetype,crf` <br><small>allskills (1), mana (10-20), cast1 (10-20)</small> | ✅ |
| 1 Magic Rod + 1 Jewel + 1 Tir Rune + 1 Perfect Amethyst + 1 Eth Rune + 1 Chasi's Malus -> Caster Weapon | `weap,mag,noe` + `jew` + `r03` + `gpv` + `r05` + `mls` | `usetype,crf` <br><small>allskills (1), mana (10-20), cast1 (10-20), ethereal (1)</small> | ✅ |
| 1 Magic Rod + 1 Jewel + 1 Tir Rune + 1 Perfect Amethyst -> Caster Weapon | `weap,mag,eth` + `jew` + `r03` + `gpv` | `usetype,crf` <br><small>allskills (1), mana (10-20), cast1 (10-20), ethereal (1)</small> | ✅ |
| 1 Magic Crown + 1 Jewel + 1 Ith Rune + 1 Perfect Emerald -> Safety Helm | `helm,mag,noe` + `jew` + `r06` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-ltng (10-20), ac% (50-60)</small> | ✅ |
| 1 Magic Crown + 1 Jewel + 1 Ith Rune + 1 Perfect Emerald + 1 Eth Rune + 1 Chasi's Malus -> Safety Helm | `helm,mag,noe` + `jew` + `r06` + `gpg` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-ltng (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Crown + 1 Jewel + 1 Ith Rune + 1 Perfect Emerald -> Safety Helm | `helm,mag,eth` + `jew` + `r06` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-ltng (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Plated Boots + 1 Jewel + 1 Ort Rune + 1 Perfect Emerald -> Safety Boots | `boot,mag,noe` + `jew` + `r09` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-fire (10-20), ac% (50-60)</small> | ✅ |
| 1 Magic Plated Boots + 1 Jewel + 1 Ort Rune + 1 Perfect Emerald + 1 Eth Rune + 1 Chasi's Malus -> Safety Boots | `boot,mag,noe` + `jew` + `r09` + `gpg` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-fire (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Plated Boots + 1 Jewel + 1 Ort Rune + 1 Perfect Emerald -> Safety Boots | `boot,mag,eth` + `jew` + `r09` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-fire (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Gauntlets + 1 Jewel + 1 Ral Rune + 1 Perfect Emerald -> Safety Gloves | `glov,mag,noe` + `jew` + `r08` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-cold (10-20), ac% (10-30)</small> | ✅ |
| 1 Magic Gauntlets + 1 Jewel + 1 Ral Rune + 1 Perfect Emerald + 1 Eth Rune + 1 Chasi's Malus -> Safety Gloves | `glov,mag,noe` + `jew` + `r08` + `gpg` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-cold (10-20), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Gauntlets + 1 Jewel + 1 Ral Rune + 1 Perfect Emerald -> Safety Gloves | `glov,mag,eth` + `jew` + `r08` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-cold (10-20), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Sash + 1 Jewel + 1 Tal Rune + 1 Perfect Emerald -> Safety Belt | `belt,mag,noe` + `jew` + `r07` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-pois-len (75-100), ac% (10-30)</small> | ✅ |
| 1 Magic Sash + 1 Jewel + 1 Tal Rune + 1 Perfect Emerald + 1 Eth Rune + 1 Chasi's Malus -> Safety Belt | `belt,mag,noe` + `jew` + `r07` + `gpg` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-pois-len (75-100), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Sash + 1 Jewel + 1 Tal Rune + 1 Perfect Emerald -> Safety Belt | `belt,mag,eth` + `jew` + `r07` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-pois-len (75-100), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Kite Shield + 1 Jewel + 1 Nef Rune + 1 Perfect Emerald -> Safety Shield | `shld,mag,noe` + `jew` + `r04` + `gpg` | `usetype,crf` <br><small>red-dmg% (5-10), res-mag (10-20), ac% (50-60)</small> | ✅ |
| 1 Magic Kite Shield + 1 Jewel + 1 Nef Rune + 1 Perfect Emerald + 1 Eth Rune + 1 Chasi's Malus -> Safety Shield | `shld,mag,noe` + `jew` + `r04` + `gpg` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg% (5-10), res-mag (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Kite Shield + 1 Jewel + 1 Nef Rune + 1 Perfect Emerald -> Safety Shield | `shld,mag,eth` + `jew` + `r04` + `gpg` | `usetype,crf` <br><small>red-dmg% (5-10), res-mag (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Breast Plate + 1 Jewel + 1 Eth Rune + 1 Perfect Emerald -> Safety Body | `tors,mag,noe` + `jew` + `r05` + `gpg` | `usetype,crf` <br><small>red-dmg% (5-10), ac (25-50), half-freeze (1), ac% (50-60)</small> | ✅ |
| 1 Magic Breast Plate + 1 Jewel + 1 Eth Rune + 1 Perfect Emerald + 1 Eth Rune + 1 Chasi's Malus -> Safety Body | `tors,mag,noe` + `jew` + `r05,qty=2` + `gpg` + `mls` | `usetype,crf` <br><small>red-dmg% (5-10), ac (25-50), half-freeze (1), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Breast Plate + 1 Jewel + 1 Eth Rune + 1 Perfect Emerald -> Safety Body | `tors,mag,eth` + `jew` + `r05` + `gpg` | `usetype,crf` <br><small>red-dmg% (5-10), ac (25-50), half-freeze (1), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + 1 Jewel + 1 Thul Rune + 1 Perfect Emerald -> Safety Amulet | `amul,mag` + `jew` + `r10` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), block (10), ac% (10-20)</small> | ✅ |
| 1 Magic Ring + 1 Jewel + 1 Amn Rune + 1 Perfect Emerald -> Safety Ring | `ring,mag` + `jew` + `r11` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), vit (5-10), ac% (10-20)</small> | ✅ |
| 1 Magic Spear + 1 Jewel + 1 Sol Rune + 1 Perfect Emerald -> Safety Weapon | `weap,mag,noe` + `jew` + `r12` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), swing3 (10-20), dmg% (30-50)</small> | ✅ |
| 1 Magic Spear + 1 Jewel + 1 Sol Rune + 1 Perfect Emerald + 1 Eth Rune + 1 Chasi's Malus -> Safety Weapon | `weap,mag,noe` + `jew` + `r12` + `gpg` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), swing3 (10-20), dmg% (30-50), ethereal (1)</small> | ✅ |
| 1 Magic Spear + 1 Jewel + 1 Sol Rune + 1 Perfect Emerald -> Safety Weapon | `weap,mag,eth` + `jew` + `r12` + `gpg` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), swing3 (10-20), dmg% (30-50), ethereal (1)</small> | ✅ |
| 1 Magic Full Helm + Power Crafting Tablet  -> Hit Power Helm | `helm,mag,noe` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), att (150-200)</small> | ✅ |
| 1 Magic Full Helm + Power Crafting Tablet  + 1 Eth Rune + 1 Chasi's Malus  -> Hit Power Helm | `helm,mag,noe` + `pct` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), att (150-200), ethereal (1)</small> | ✅ |
| 1 Magic Full Helm + Power Crafting Tablet  -> Hit Power Helm | `helm,mag,eth` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), att (150-200), ethereal (1)</small> | ✅ |
| 1 Magic Chain Boots + Power Crafting Tablet -> Hit Power Boots | `boot,mag,noe` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (10), dex (10-15)</small> | ✅ |
| 1 Magic Chain Boots + Power Crafting Tablet  + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Boots | `boot,mag,noe` + `pct` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (10), dex (10-15), ethereal (1)</small> | ✅ |
| 1 Magic Chain Boots + Power Crafting Tablet -> Hit Power Boots | `boot,mag,eth` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (10), dex (10-15), ethereal (1)</small> | ✅ |
| 1 Magic Chain Gloves +  Power Crafting Tablet  -> Hit Power Gloves | `glov,mag,noe` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), knock (1)</small> | ✅ |
| 1 Magic Chain Gloves +  Power Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus  -> Hit Power Gloves | `glov,mag,noe` + `pct` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), knock (1), ethereal (1)</small> | ✅ |
| 1 Magic Chain Gloves +  Power Crafting Tablet  -> Hit Power Gloves | `glov,mag,eth` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), knock (1), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Belt + Power Crafting Tablet -> Hit Power Belt | `belt,mag,noe` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), dmg-to-mana (20)</small> | ✅ |
| 1 Magic Heavy Belt + Power Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Belt | `belt,mag,noe` + `pct` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), dmg-to-mana (20), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Belt + Power Crafting Tablet -> Hit Power Belt | `belt,mag,eth` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), balance1 (20), dmg-to-mana (20), ethereal (1)</small> | ✅ |
| 1 Magic Gothic Shield + Power Crafting Tablet -> Hit Power Shield | `shld,mag,noe` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), block1 (30), block (20)</small> | ✅ |
| 1 Magic Gothic Shield + Power Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Shield | `shld,mag,noe` + `pct` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), block1 (30), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Gothic Shield + Power Crafting Tablet -> Hit Power Shield | `shld,mag,eth` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), block1 (30), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Field Plate + Power Crafting Tablet -> Hit Power Body | `tors,mag,noe` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), dmg% (35-60), balance1 (30-40)</small> | ✅ |
| 1 Magic Field Plate + Power Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Body | `tors,mag,noe` + `pct` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), dmg% (35-60), balance1 (30-40), ethereal (1)</small> | ✅ |
| 1 Magic Field Plate + Power Crafting Tablet -> Hit Power Body | `tors,mag,eth` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), dmg% (35-60), balance1 (30-40), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + Power Crafting Tablet -> Hit Power Amulet | `amul,mag` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), att (200-250), balance1 (15-20)</small> | ✅ |
| 1 Magic Ring + Power Crafting Tablet  -> Hit Power Ring | `ring,mag` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), dmg-max (3-5), dex (5-10)</small> | ✅ |
| 1 Magic Blunt Weapon + Power Crafting Tablet -> Hit Power Weapon | `weap,mag,noe` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), dmg% (50-80)</small> | ✅ |
| 1 Magic Blunt Weapon + Power Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Hit Power Weapon | `weap,mag,noe` + `pct` + `r05` + `mls` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Blunt Weapon + Power Crafting Tablet -> Hit Power Weapon | `weap,mag,eth` + `pct` | `usetype,crf` <br><small>gethit-skill (5-4), reduce-ac (15-20), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Helm + Blood Crafting Tablet -> Blood Helm | `helm,mag,noe` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), deadly (15-20)</small> | ✅ |
| 1 Magic Helm + Blood Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Blood Helm | `helm,mag,noe` + `bct` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), deadly (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Helm + Blood Crafting Tablet -> Blood Helm | `helm,mag,eth` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), deadly (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Light Plated Boots + Blood Crafting Tablet -> Blood Boots | `boot,mag,noe` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), heal-kill (3-6)</small> | ✅ |
| 1 Magic Light Plated Boots + Blood Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Blood Boots | `boot,mag,noe` + `bct` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Light Plated Boots + Blood Crafting Tablet -> Blood Boots | `boot,mag,eth` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Gloves + Blood Crafting Tablet -> Blood Gloves | `glov,mag,noe` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), crush (5-10)</small> | ✅ |
| 1 Magic Heavy Gloves + Blood Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Blood Gloves | `glov,mag,noe` + `bct` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), crush (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Heavy Gloves + Blood Crafting Tablet -> Blood Gloves | `glov,mag,eth` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), crush (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Belt + Blood Crafting Tablet -> Blood Belt | `belt,mag,noe` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), openwounds (15-20)</small> | ✅ |
| 1 Magic Belt + Blood Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Blood Belt | `belt,mag,noe` + `bct` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), openwounds (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Belt + Blood Crafting Tablet -> Blood Belt | `belt,mag,eth` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), openwounds (15-20), ethereal (1)</small> | ✅ |
| 1 Magic Spiked Shield + Blood Crafting Tablet  -> Blood Shield | `shld,mag,noe` + `bct` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), block (20)</small> | ✅ |
| 1 Magic Spiked Shield + Blood Crafting Tablet  + 1 Eth Rune + 1 Chasi's Malus -> Blood Shield | `shld,mag,noe` + `bct` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Spiked Shield + Blood Crafting Tablet  -> Blood Shield | `shld,mag,eth` + `bct` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), block (20), ethereal (1)</small> | ✅ |
| 1 Magic Plate Mail + Blood Crafting Tablet  -> Blood Body | `tors,mag,noe` + `bct` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), heal-kill (3-6)</small> | ✅ |
| 1 Magic Plate Mail + Blood Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus  -> Blood Body | `tors,mag,noe` + `bct` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Plate Mail + Blood Crafting Tablet  -> Blood Body | `tors,mag,eth` + `bct` | `usetype,crf` <br><small>lifesteal (3-6), hp (50-60), heal-kill (3-6), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + Blood Crafting Tablet -> Blood Amulet | `amul,mag` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), move1 (10)</small> | ✅ |
| 1 Magic Ring + Blood Crafting Tablet -> Blood Ring | `ring,mag` + `bct` | `usetype,crf` <br><small>lifesteal (2-4), hp (30-40), str (5-10)</small> | ✅ |
| 1 Magic Axe + Blood Crafting Tablet -> Blood Weapon | `weap,mag,noe` + `bct` | `usetype,crf` <br><small>lifesteal (3-6), hp (30-40), dmg% (50-80)</small> | ✅ |
| 1 Magic Axe + Blood Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Blood Weapon | `weap,mag,noe` + `bct` + `r05` + `mls` | `usetype,crf` <br><small>lifesteal (3-6), hp (30-40), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Axe + Blood Crafting Tablet -> Blood Weapon | `weap,mag,eth` + `bct` | `usetype,crf` <br><small>lifesteal (3-6), hp (30-40), dmg% (50-80), ethereal (1)</small> | ✅ |
| 1 Magic Mask + Caster Crafting Tablet -> Caster Helm | `helm,mag,noe` + `cct` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10)</small> | ✅ |
| 1 Magic Mask + Caster Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Caster Helm | `helm,mag,noe` + `cct` + `r05` + `mls` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Mask + Caster Crafting Tablet -> Caster Helm | `helm,mag,eth` + `cct` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Boots + Caster Crafting Tablet  -> Caster Boots | `boot,mag,noe` + `cct` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), mana% (5-10)</small> | ✅ |
| 1 Magic Boots + Caster Crafting Tablet  + 1 Eth Rune + 1 Chasi's Malus -> Caster Boots | `boot,mag,noe` + `cct` + `r05` + `mls` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), mana% (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Boots + Caster Crafting Tablet  -> Caster Boots | `boot,mag,eth` + `cct` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), mana% (5-10), ethereal (1)</small> | ✅ |
| 1 Magic Leather Gloves + Caster Crafting Tablet -> Caster Gloves | `glov,mag,noe` + `cct` | `usetype,crf` <br><small>mana-kill (1-3), mana (10-20), cast1 (10)</small> | ✅ |
| 1 Magic Leather Gloves + Caster Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Caster Gloves | `glov,mag,noe` + `cct` + `r05` + `mls` | `usetype,crf` <br><small>mana-kill (1-3), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Leather Gloves + Caster Crafting Tablet -> Caster Gloves | `glov,mag,eth` + `cct` | `usetype,crf` <br><small>mana-kill (1-3), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Light Belt + Caster Crafting Tablet -> Caster Belt | `belt,mag,noe` + `cct` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10)</small> | ✅ |
| 1 Magic Light Belt + Caster Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Caster Belt | `belt,mag,noe` + `cct` + `r05` + `mls` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Light Belt + Caster Crafting Tablet -> Caster Belt | `belt,mag,eth` + `cct` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (10), ethereal (1)</small> | ✅ |
| 1 Magic Small Shield + Caster Crafting Tablet -> Caster Shield | `shld,mag,noe` + `cct` | `usetype,crf` <br><small>cast1 (10), mana (10-20), block (20), allskills (1)</small> | ✅ |
| 1 Magic Small Shield + Caster Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Caster Shield | `shld,mag,noe` + `cct` + `r05` + `mls` | `usetype,crf` <br><small>cast1 (15), mana (10-20), block (20), ethereal (1), allskills (1)</small> | ✅ |
| 1 Magic Small Shield + Caster Crafting Tablet -> Caster Shield | `shld,mag,eth` + `cct` | `usetype,crf` <br><small>cast1 (15), mana (10-20), block (20), ethereal (1), allskills (1)</small> | ✅ |
| 1 Magic Light Plate + Caster Crafting Tablet -> Caster Body | `tors,mag,noe` + `cct` | `usetype,crf` <br><small>cast1 (20), mana (10-20), mana-kill (5-8)</small> | ✅ |
| 1 Magic Light Plate + Caster Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Caster Body | `tors,mag,noe` + `cct` + `r05` + `mls` | `usetype,crf` <br><small>cast1 (20), mana (10-20), mana-kill (5-8), ethereal (1)</small> | ✅ |
| 1 Magic Light Plate + Caster Crafting Tablet -> Caster Body | `tors,mag,eth` + `cct` | `usetype,crf` <br><small>cast1 (20), mana (10-20), mana-kill (5-8), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + Caster Crafting Tablet -> Caster Amulet | `amul,mag` + `cct` | `usetype,crf` <br><small>regen-mana (4-10), mana (10-20), cast1 (5-10)</small> | ✅ |
| 1 Magic Ring + Caster Crafting Tablet -> Caster Ring | `ring,mag` + `cct` | `usetype,crf` <br><small>mana-kill (1-2), mana (10-20), enr (5-10)</small> | ✅ |
| 1 Magic Rod + Caster Crafting Tablet -> Caster Weapon | `weap,mag,noe` + `cct` | `usetype,crf` <br><small>allskills (1), mana (10-20), cast1 (10-20)</small> | ✅ |
| 1 Magic Rod + Caster Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Caster Weapon | `weap,mag,noe` + `cct` + `r05` + `mls` | `usetype,crf` <br><small>allskills (1), mana (10-20), cast1 (10-20), ethereal (1)</small> | ✅ |
| 1 Magic Rod + Caster Crafting Tablet -> Caster Weapon | `weap,mag,eth` + `cct` | `usetype,crf` <br><small>allskills (1), mana (10-20), cast1 (10-20), ethereal (1)</small> | ✅ |
| 1 Magic Crown + Saftey Crafting Tablet -> Safety Helm | `helm,mag,noe` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-ltng (10-20), ac% (50-60)</small> | ✅ |
| 1 Magic Crown + Saftey Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Safety Helm | `helm,mag,noe` + `sct` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-ltng (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Crown + Saftey Crafting Tablet -> Safety Helm | `helm,mag,eth` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-ltng (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Plated Boots + Saftey Crafting Tablet -> Safety Boots | `boot,mag,noe` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-fire (10-20), ac% (50-60)</small> | ✅ |
| 1 Magic Plated Boots + Saftey Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Safety Boots | `boot,mag,noe` + `sct` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-fire (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Plated Boots + Saftey Crafting Tablet -> Safety Boots | `boot,mag,eth` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-fire (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Gauntlets + Saftey Crafting Tablet -> Safety Gloves | `glov,mag,noe` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-cold (10-20), ac% (10-30)</small> | ✅ |
| 1 Magic Gauntlets + Saftey Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Safety Gloves | `glov,mag,noe` + `sct` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-cold (10-20), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Gauntlets + Saftey Crafting Tablet -> Safety Gloves | `glov,mag,eth` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-cold (10-20), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Sash + Saftey Crafting Tablet -> Safety Belt | `belt,mag,noe` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-pois-len (75-100), ac% (10-30)</small> | ✅ |
| 1 Magic Sash + Saftey Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Safety Belt | `belt,mag,noe` + `sct` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-pois-len (75-100), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Sash + Saftey Crafting Tablet -> Safety Belt | `belt,mag,eth` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), res-pois-len (75-100), ac% (10-30), ethereal (1)</small> | ✅ |
| 1 Magic Kite Shield + Saftey Crafting Tablet -> Safety Shield | `shld,mag,noe` + `sct` | `usetype,crf` <br><small>red-dmg% (5-10), res-mag (10-20), ac% (50-60)</small> | ✅ |
| 1 Magic Kite Shield + Saftey Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Safety Shield | `shld,mag,noe` + `sct` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg% (5-10), res-mag (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Kite Shield + Saftey Crafting Tablet -> Safety Shield | `shld,mag,eth` + `sct` | `usetype,crf` <br><small>red-dmg% (5-10), res-mag (10-20), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Breast Plate + Saftey Crafting Tablet -> Safety Body | `tors,mag,noe` + `sct` | `usetype,crf` <br><small>red-dmg% (5-10), ac (25-50), half-freeze (1), ac% (50-60)</small> | ✅ |
| 1 Magic Breast Plate + Saftey Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Safety Body | `tors,mag,noe` + `sct` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg% (5-10), ac (25-50), half-freeze (1), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Breast Plate + Saftey Crafting Tablet -> Safety Body | `tors,mag,eth` + `sct` | `usetype,crf` <br><small>red-dmg% (5-10), ac (25-50), half-freeze (1), ac% (50-60), ethereal (1)</small> | ✅ |
| 1 Magic Amulet + Saftey Crafting Tablet -> Safety Amulet | `amul,mag` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), block (10), ac% (10-20)</small> | ✅ |
| 1 Magic Ring + Saftey Crafting Tablet -> Safety Ring | `ring,mag` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), vit (5-10), ac% (10-20)</small> | ✅ |
| 1 Magic Spear + Saftey Crafting Tablet -> Safety Weapon | `weap,mag,noe` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), swing3 (10-20), dmg% (30-50)</small> | ✅ |
| 1 Magic Spear + Saftey Crafting Tablet + 1 Eth Rune + 1 Chasi's Malus -> Safety Weapon | `weap,mag,noe` + `sct` + `r05` + `mls` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), swing3 (10-20), dmg% (30-50), ethereal (1)</small> | ✅ |
| 1 Magic Spear + Saftey Crafting Tablet -> Safety Weapon | `weap,mag,eth` + `sct` | `usetype,crf` <br><small>red-dmg (3-5), red-mag (3-5), swing3 (10-20), dmg% (30-50), ethereal (1)</small> | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ith Rune + 1 Perfect Emerald -> Safety Helm | `circ,mag,noe` + `jew` + `r06` + `gpg` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ith Rune + 1 Perfect Emerald -> Safety Helm | `circ,mag,noe` + `jew` + `r06` + `gpg` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ith Rune + 1 Perfect Emerald -> Safety Helm | `circ,mag,eth` + `jew` + `r06` + `gpg` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + Nef Rune + 1 Perfect Amethyst -> Caster Helm | `circ,mag,noe` + `jew` + `r04` + `gpv` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + Nef Rune + 1 Perfect Amethyst -> Caster Helm | `circ,mag,noe` + `jew` + `r04` + `gpv` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + Nef Rune + 1 Perfect Amethyst -> Caster Helm | `circ,mag,eth` + `jew` + `r04` + `gpv` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ral Rune + 1 Perfect Ruby -> Blood Helm | `circ,mag,noe` + `jew` + `r08` + `gpr` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ral Rune + 1 Perfect Ruby -> Blood Helm | `circ,mag,noe` + `jew` + `r08` + `gpr` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ral Rune + 1 Perfect Ruby -> Blood Helm | `circ,mag,eth` + `jew` + `r08` + `gpr` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ith Rune + 1 Perfect Sapphire -> Hit Power Helm | `circ,mag,noe` + `jew` + `r06` + `gpb` | `-` | ✅ |
| 1 Magic Circlet+ 1 Jewel + 1 Ith Rune + 1 Perfect Sapphire -> Hit Power Helm | `circ,mag,noe` + `jew` + `r06` + `gpb` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + 1 Jewel + 1 Ith Rune + 1 Perfect Sapphire -> Hit Power Helm | `circ,mag,eth` + `jew` + `r06` + `gpb` | `-` | ✅ |
| 1 Magic Circlet + Saftey Crafting Tablet  ->  Safety Helm | `circ,mag,noe` + `sct` | `-` | ✅ |
| 1 Magic Circlet + Saftey Crafting Tablet  -> Safety Helm | `circ,mag,noe` + `sct` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + Saftey Crafting Tablet  -> Safety Helm | `circ,mag,eth` + `sct` | `-` | ✅ |
| 1 Magic Circlet + Caster Crafting Tablet  -> Caster Helm | `circ,mag,noe` + `cct` | `-` | ✅ |
| 1 Magic Circlet + Caster  Crafting Tablet  -> Caster Helm | `circ,mag,noe` + `cct` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + Caster Crafting Tablet  -> Caster Helm | `circ,mag,eth` + `cct` | `-` | ✅ |
| 1 Magic Circlet + Blood Crafting Tablet  -> Blood Helm | `circ,mag,noe` + `bct` | `-` | ✅ |
| 1 Magic Circlet + Blood  Crafting Tablet  ->  Blood Helm | `circ,mag,noe` + `bct` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + Blood  Crafting Tablet  -> Blood Helm | `circ,mag,eth` + `bct` | `-` | ✅ |
| 1 Magic Circlet + Hit Power Crafting Tablet  -> Hit Power Helm | `circ,mag,noe` + `pct` | `-` | ✅ |
| 1 Magic Circlet + Hit Power Crafting Tablet  -> Hit Power Helm | `circ,mag,noe` + `pct` + `r05` + `mls` | `-` | ✅ |
| 1 Magic Circlet + Hit Power Crafting Tablet  -> Hit Power Helm | `circ,mag,eth` + `pct` | `-` | ✅ |
| Charsi Hammer + Larzuk Hammer + 1 Normal Unique Weapon -> Exceptional Unique Weapon | `weap,bas,uni` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer + 1 Normal Unique Armor -> Exceptional Unique Armor | `armo,bas,uni` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer  + Standard of Heros + 1 Exceptional Unique Weapon -> Elite Unique Weapon | `weap,exc,uni` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| Charsi Hammer + Larzuk Hammer  + Standard of Heros + 1 Exceptional Unique Armor -> Elite Unique Armor | `armo,exc,uni` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| Charsi Hammer + Larzuk Hammer  + 1 Normal Rare Weapon -> Exceptional Rare Weapon | `weap,bas,rar` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer  + 1 Normal Crafted Weapon -> Exceptional Crafted Weapon | `weap,bas,crf` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer  + 1 Normal Rare Armor -> Exceptional Rare Armor | `armo,bas,rar` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer  + 1 Normal Crafted Armor -> Exceptional Crafted Armor | `armo,bas,crf` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer  + Standard of Heros + 1 Exceptional Rare Weapon -> Elite Rare Weapon | `weap,exc,rar` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| Charsi Hammer + Larzuk Hammer  + Standard of Heros + 1 Exceptional Crafted Weapon -> Elite Crafted Weapon | `weap,exc,crf` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| Charsi Hammer + Larzuk Hammer +  Standard of Heros + 1 Exceptional Rare Armor -> Elite Rare Armor | `armo,exc,rar` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| Charsi Hammer + Larzuk Hammer  + Standard of Heros + 1 Exceptional Crafted Armor -> Elite Crafted Armor | `armo,exc,crf` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| Charsi Hammer + Larzuk Hammer + 1 Normal Set Weapon -> Exceptional Set Weapon | `weap,bas,set` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer + 1 Normal Set Armor -> Exceptional Set Armor | `armo,bas,set` + `mls` + `lmr` | `useitem,mod,exc` | ✅ |
| Charsi Hammer + Larzuk Hammer  +  Standard of Heros + 1 Exceptional Set Weapon -> Elite Set Weapon | `weap,exc,set` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| Charsi Hammer + Larzuk Hammer  +  Standard of Heros + 1 Exceptional Set Armor -> Elite Set Armor | `armo,exc,set` + `mls` + `lmr` + `std` | `useitem,mod,eli` | ✅ |
| 1 Ral Rune + 1 Sol Rune + 1 Perfect Emerald + 1 Normal Set Weapon -> Exceptional Set Weapon | `weap,bas,set` + `r08` + `r12` + `gpg` | `useitem,mod,exc` <br><small>levelreq (5)</small> | ❌ |
| 1 Tal Rune + 1 Shael Rune + 1 Perfect Diamond + 1 Normal Set Armor -> Exceptional Set Armor | `armo,bas,set` + `r07` + `r13` + `gpw` | `useitem,mod,exc` <br><small>levelreq (5)</small> | ❌ |
| 1 Lum Rune + 1 Pul Rune + 1 Perfect Emerald + 1 Exceptional Set Weapon -> Elite Set Weapon | `weap,exc,set` + `r17` + `r21` + `gpg` | `useitem,mod,eli` <br><small>levelreq (7)</small> | ❌ |
| 1 Ko Rune + 1 Lem Rune + 1 Perfect Diamond + 1 Exceptional Set Armor -> Elite Set Armor | `armo,exc,set` + `r18` + `r20` + `gpw` | `useitem,mod,eli` <br><small>levelreq (7)</small> | ❌ |
| 1 Ral Rune + 1 Sol Rune + 1 Perfect Emerald + 1 Normal Unique Weapon -> Exceptional Unique Weapon | `weap,bas,uni` + `r08` + `r12` + `gpg` | `useitem,mod,exc` <br><small>levelreq (5)</small> | ❌ |
| 1 Tal Rune + 1 Shael Rune + 1 Perfect Diamond + 1 Normal Unique Armor -> Exceptional Unique Armor | `armo,bas,uni` + `r07` + `r13` + `gpw` | `useitem,mod,exc` <br><small>levelreq (5)</small> | ❌ |
| 1 Lum Rune + 1 Pul Rune + 1 Perfect Emerald + 1 Exceptional Unique Weapon -> Elite Unique Weapon | `weap,exc,uni` + `r17` + `r21` + `gpg` | `useitem,mod,eli` <br><small>levelreq (7)</small> | ❌ |
| 1 Ko Rune + 1 Lem Rune + 1 Perfect Diamond + 1 Exceptional Unique Armor -> Elite Unique Armor | `armo,exc,uni` + `r18` + `r20` + `gpw` | `useitem,mod,eli` <br><small>levelreq (7)</small> | ❌ |
| 1 Ort Rune + 1 Amn Rune + 1 Perfect Sapphire + 1 Normal Rare Weapon -> Exceptional Rare Weapon | `weap,bas,rar` + `r09` + `r11` + `gpb` | `useitem,mod,exc` <br><small>levelreq (5)</small> | ❌ |
| 1 Ral Rune + 1 Thul Rune + 1 Perfect Amethyst + 1 Normal Rare Armor -> Exceptional Rare Armor | `armo,bas,rar` + `r08` + `r10` + `gpv` | `useitem,mod,exc` <br><small>levelreq (5)</small> | ❌ |
| 1 Fal Rune + 1 Um Rune + 1 Perfect Sapphire + 1 Exceptional Rare Weapon -> Elite Rare Weapon | `weap,exc,rar` + `r19` + `r22` + `gpb` | `useitem,mod,eli` <br><small>levelreq (7)</small> | ❌ |
| 1 Ko Rune + 1 Pul Rune + 1 Perfect Amethyst + 1 Exceptional Rare Armor -> Elite Rare Armor | `armo,exc,rar` + `r18` + `r21` + `gpv` | `useitem,mod,eli` <br><small>levelreq (7)</small> | ❌ |
| 1 Ral Rune + 1 Jewel + 1 Superior Armor -> Tempered Armor | `armo,hiq,nos` + `jew` + `r08` | `useitem,tmp` | ✅ |
| 1 Ral Rune + 1 Jewel + 1 Superior Weapon -> Tempered Weapon | `weap,hiq,nos` + `jew` + `r08` | `useitem,tmp` | ✅ |
| 1 Ral Rune + 1 Jewel + Magic Ring -> Tempered Ring | `ring,mag` + `jew` + `r08` | `usetype,tmp` <br><small>levelreq (3)</small> | ✅ |
| 1 Ral Rune + 1 Jewel + 1 Magic Amulet -> Tempered Amulet | `amu,mag` + `jew` + `r08` | `usetype,tmp` <br><small>levelreq (5)</small> | ✅ |
| 1 El Rune + 1 Chipped Gem (Any) + 1 Tempered Weapon -> Weapon With Extra Attack Rating | `weap,tmp` + `r01` + `gcv` | `useitem` <br><small>levelreq (2), att (30-50)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Amulet -> Virulent Amulet | `amu,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=674` <br><small>pierce-pois (1-3)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Ring -> Virulent Ring | `ring,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=673` <br><small>pierce-pois (1-2)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Helm -> Virulent Helm | `helm,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=674` <br><small>pierce-pois (1-3)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Boots -> Virulent Boots | `boot,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=674` <br><small>pierce-pois (1-3)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Gloves -> Virulent Gloves | `glov,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=674` <br><small>pierce-pois (1-3)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Armor -> Virulent Armor | `tors,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=676` <br><small>pierce-pois (2-8)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Weapon -> Virulent Weapon | `weap,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=675` <br><small>pierce-pois (1-4)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Magic Shield -> Virulent Shield | `shie,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=675` <br><small>pierce-pois (1-4)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Small Charm -> Virulent Small Charm | `scha,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=671` <br><small>pierce-pois (1)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Western Worldstone Shard + 1 Large Charm -> Virulent Large Charm | `mcha,mag` + `r18` + `gpg` + `xa1` | `useitem,pre=673` <br><small>pierce-pois (1-2)</small> | ✅ |
| 1 Ko Rune + 1 Perfect Emerald + 1 Uber Ancient Summon Material Act1 + 1 Rotting Fissure -> Virulent Rotting Fissure | `PreCrafted Rotting Fissure` + `r18` + `gpg` + `xa1` | `Crafted Rotting Fissure` | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Amulet -> Gelid Amulet | `amu,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=684` <br><small>pierce-cold (1-3)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Ring -> Gelid Ring | `ring,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=683` <br><small>pierce-cold (1-2)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Helm -> Gelid Helm | `helm,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=684` <br><small>pierce-cold (1-3)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Boots -> Gelid Boots | `boot,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=684` <br><small>pierce-cold (1-3)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Gloves -> Gelid Gloves | `glov,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=684` <br><small>pierce-cold (1-3)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Armor -> Gelid Armor | `tors,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=686` <br><small>pierce-cold (2-8)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Weapon -> Gelid Weapon | `weap,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=685` <br><small>pierce-cold (1-4)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Magic Shield -> Gelid Shield | `shie,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=685` <br><small>pierce-cold (1-4)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Small Charm -> Gelid Small Charm | `scha,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=682` <br><small>pierce-cold (1)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Large Charm -> Gelid Large Charm | `mcha,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=683` <br><small>pierce-cold (1-2)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Eastern Worldstone Shard + 1 Grand Charm -> Gelid Grand Charm | `lcha,mag` + `r17` + `gpb` + `xa2` | `useitem,pre=684` <br><small>pierce-cold (1-3)</small> | ✅ |
| 1 Lum Rune + 1 Perfect Sapphire + 1 Uber Ancient Summon Material Act2 + 1 Cold Rupture -> Gelid Cold Rupture | `PreCrafted Cold Rupture` + `r17` + `gpb` + `xa2` | `Crafted Cold Rupture` | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Amulet -> Magnetic Amulet | `amu,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=689` <br><small>pierce-ltng (1-3)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Ring -> Magnetic Ring | `ring,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=688` <br><small>pierce-ltng (1-2)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Helm -> Magnetic Helm | `helm,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=689` <br><small>pierce-ltng (1-3)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Boots -> Magnetic Boots | `boot,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=689` <br><small>pierce-ltng (1-3)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Gloves -> Magnetic Gloves | `glov,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=689` <br><small>pierce-ltng (1-3)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Armor -> Magnetic Armor | `tors,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=691` <br><small>pierce-ltng (2-8)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Weapon -> Magnetic Weapon | `weap,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=690` <br><small>pierce-ltng (1-4)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Magic Shield -> Magnetic Shield | `shie,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=690` <br><small>pierce-ltng (1-4)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Small Charm -> Magnetic Small Charm | `scha,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=687` <br><small>pierce-ltng (1)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Large Charm -> Magnetic Large Charm | `mcha,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=688` <br><small>pierce-ltng (1-2)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Southern Worldstone Shard + 1 Grand Charm -> Magnetic Grand Charm | `lcha,mag` + `r19` + `gpy` + `xa3` | `useitem,pre=689` <br><small>pierce-ltng (1-3)</small> | ✅ |
| 1 Fal Rune + 1 Perfect Topaz + 1 Uber Ancient Summon Material Act3 + 1 Crack of the Heavens -> Magnetic Crack of the Heavens | `PreCrafted Crack of the Heavens` + `r19` + `gpy` + `xa3` | `Crafted Crack of the Heavens` | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Amulet -> Incendiary Amulet | `amu,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=679` <br><small>pierce-fire (1-3)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Ring -> Incendiary Ring | `ring,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=678` <br><small>pierce-fire (1-2)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Helm -> Incendiary Helm | `helm,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=679` <br><small>pierce-fire (1-3)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Boots -> Incendiary Boots | `boot,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=679` <br><small>pierce-fire (1-3)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Gloves -> Incendiary Gloves | `glov,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=679` <br><small>pierce-fire (1-3)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Armor -> Incendiary Armor | `tors,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=681` <br><small>pierce-fire (2-8)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Weapon -> Incendiary Weapon | `weap,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=680` <br><small>pierce-fire (1-4)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Magic Shield -> Incendiary Shield | `shie,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=680` <br><small>pierce-fire (1-4)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Small Charm -> Incendiary Small Charm | `scha,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=677` <br><small>pierce-fire (1)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Large Charm -> Incendiary Large Charm | `mcha,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=678` <br><small>pierce-fire (1-2)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Deep Worldstone Shard + 1 Grand Charm -> Incendiary Grand Charm | `lcha,mag` + `r16` + `gpr` + `xa4` | `useitem,pre=679` <br><small>pierce-fire (1-3)</small> | ✅ |
| 1 Io Rune + 1 Perfect Ruby + 1 Uber Ancient Summon Material Act4 + 1 Flame Rift -> Incendiary Flame Rift | `PreCrafted Flame Rift` + `r16` + `gpr` + `xa4` | `Crafted Flame Rift` | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Amulet -> Breaching Amulet | `amu,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=699` <br><small>pierce-dmg (1-3)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Ring -> Breaching Ring | `ring,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=698` <br><small>pierce-dmg (1-2)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Helm -> Breaching Helm | `helm,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=699` <br><small>pierce-dmg (1-3)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Boots -> Breaching Boots | `boot,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=699` <br><small>pierce-dmg (1-3)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Gloves -> Breaching Gloves | `glov,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=699` <br><small>pierce-dmg (1-3)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Armor -> Breaching Armor | `tors,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=701` <br><small>pierce-dmg (1-8)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Weapon -> Breaching Weapon | `weap,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=700` <br><small>pierce-dmg (1-4)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Magic Shield -> Breaching Shield | `shie,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=700` <br><small>pierce-dmg (1-4)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Small Charm -> Breaching Small Charm | `scha,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=697` <br><small>pierce-dmg (1)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Large Charm -> Breaching Large Charm | `mcha,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=698` <br><small>pierce-dmg (1-2)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Northern Worldstone Shard + 1 Grand Charm -> Breaching Grand Charm | `lcha,mag` + `r21` + `gpv` + `xa5` | `useitem,pre=699` <br><small>pierce-dmg (1-3)</small> | ✅ |
| 1 Pul Rune + 1 Perfect Amethyst + 1 Uber Ancient Summon Material Act5 + 1 Bone Break -> Breaching Bone Break | `PreCrafted Bone Break` + `r21` + `gpv` + `xa5` | `Crafted Bone Break` | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Amulet -> Mystical Amulet | `amu,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=694` <br><small>pierce-mag (1-3)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Ring -> Mystical Ring | `ring,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=693` <br><small>pierce-mag (1-2)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Helm -> Mystical Helm | `helm,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=694` <br><small>pierce-mag (1-3)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Boots -> Mystical Boots | `boot,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=694` <br><small>pierce-mag (1-3)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Gloves -> Mystical Gloves | `glov,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=694` <br><small>pierce-mag (1-3)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Armor -> Mystical Armor | `tors,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=696` <br><small>pierce-mag (2-8)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Weapon -> Mystical Weapon | `weap,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=695` <br><small>pierce-mag (1-4)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Magic Shield -> Mystical Shield | `shie,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=695` <br><small>pierce-mag (1-4)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Small Charm -> Mystical Small Charm | `scha,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=692` <br><small>pierce-mag (1)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Large Charm -> Mystical Large Charm | `mcha,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=693` <br><small>pierce-mag (1-2)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Northern Worldstone Shard + 1 Grand Charm -> Mystical Grand Charm | `lcha,mag` + `r23` + `gpw` + `xa5` | `useitem,pre=694` <br><small>pierce-mag (1-3)</small> | ✅ |
| 1 Mal Rune + 1 Perfect Diamond + 1 Uber Ancient Summon Material Act5 + 1 Black Cleft -> Mystical Black Cleft | `PreCrafted Black Cleft` + `r23` + `gpw` + `xa3` + `xa4` + `xa5` | `Crafted Black Cleft` | ✅ |
| 9 Magic Jewels + Charsi's Malus = 1 Rare Jewel | `jew,qty=9` + `mls` | `usetype,rar` | ✅ |
| Helm | `helm,nor,nos` + `mls` | `usetype,rar` | ✅ |
| Helm Inf | `helm,low` + `mls` | `usetype,rar` | ✅ |
| Helm Sup | `helm,hiq,noe,nos` + `mls` | `usetype,rar` | ✅ |
| Helm Eth | `helm,nor,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| circ Eth | `circ,nor,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Helm Eth Sup | `helm,hiq,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| circ Eth Sup | `circ,hiq,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Weapon | `weap,nor,noe,nos` + `mls` | `usetype,rar` | ✅ |
| Weapon Inf | `weap,low` + `mls` | `usetype,rar` | ✅ |
| Weapon Sup | `weap,hiq,noe,nos` + `mls` | `usetype,rar` | ✅ |
| Weapon Eth | `weap,nor,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Weapon Eth Sup | `weap,hiq,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Armor | `tors,nor,noe,nos` + `mls` | `usetype,rar` | ✅ |
| Armor Inf | `tors,low` + `mls` | `usetype,rar` | ✅ |
| Armor Sup | `tors,hiq,noe,nos` + `mls` | `usetype,rar` | ✅ |
| Armor Eth | `tors,nor,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Armor Eth Sup | `tors,hiq,eth,nos` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Shield | `shld,nor,noe` + `mls` | `usetype,rar` | ✅ |
| Shield Inf | `shld,low` + `mls` | `usetype,rar` | ✅ |
| Shield Sup | `shld,hiq,noe` + `mls` | `usetype,rar` | ✅ |
| Shield Eth | `shld,nor,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Shield Eth Sup | `shld,hiq,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Gloves | `glov,nor,noe` + `mls` | `usetype,rar` | ✅ |
| Gloves Inf | `glov,low` + `mls` | `usetype,rar` | ✅ |
| Gloves Sup | `glov,hiq,noe` + `mls` | `usetype,rar` | ✅ |
| Gloves Eth | `glov,nor,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Gloves Eth Sup | `glov,hiq,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Belt | `belt,nor,noe` + `mls` | `usetype,rar` | ✅ |
| Belt Inf | `belt,low` + `mls` | `usetype,rar` | ✅ |
| Belt Sup | `belt,hiq,noe` + `mls` | `usetype,rar` | ✅ |
| Belt Eth | `belt,nor,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Belt Eth Sup | `belt,hiq,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Boots | `boot,nor,noe` + `mls` | `usetype,rar` | ✅ |
| Boots Inf | `boot,low` + `mls` | `usetype,rar` | ✅ |
| Boots Sup | `boot,hiq,noe` + `mls` | `usetype,rar` | ✅ |
| Boots Eth | `boot,nor,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| Boots Eth Sup | `boot,hiq,eth` + `mls` | `usetype,rar` <br><small>ethereal (1)</small> | ✅ |
| SUP 1 Tal Rune + 1 Thul Rune + 1 Perfect Topaz + 1 Normal Torso Armor -> Socketed Torso Armor | `tors,hiq,nos` + `r07` + `r10` + `gpy` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| 1 Tal Rune + 1 Thul Rune + 1 Perfect Topaz + 1 Normal Torso Armor -> Socketed Torso Armor | `tors,nor,nos` + `r07` + `r10` + `gpy` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| SUP 1 Ral Rune + 1 Amn Rune + 1 Perfect Amethyst + 1 Normal Weapon -> Socketed Weapon | `weap,hiq,nos` + `r08` + `r11` + `gpv` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| 1 Ral Rune + 1 Amn Rune + 1 Perfect Amethyst + 1 Normal Weapon -> Socketed Weapon | `weap,nor,nos` + `r08` + `r11` + `gpv` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| SUP 1 Ral Rune + 1 Thul Rune + 1 Perfect Sapphire + 1 Normal Helm -> Socketed Helm | `helm,hiq,nos` + `r08` + `r10` + `gpb` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| 1 Ral Rune + 1 Thul Rune + 1 Perfect Sapphire + 1 Normal Helm -> Socketed Helm | `helm,nor,nos` + `r08` + `r10` + `gpb` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| SUP 1 Tal Rune + 1 Amn Rune + 1 Perfect Ruby + 1 Normal Shield -> Socketed Shield | `shld,hiq,nos` + `r07` + `r11` + `gpr` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| 1 Tal Rune + 1 Amn Rune + 1 Perfect Ruby + 1 Normal Shield -> Socketed Shield | `shld,nor,nos` + `r07` + `r11` + `gpr` | `useitem` <br><small>sock (1-6)</small> | ✅ |
| Arrows | `aqv` + `tsc` | `aqv` <br><small>sock (1-3), mag%/lvl (4)</small> | ✅ |
| Bolts | `cqv` + `tsc` | `cqv` <br><small>sock (1-3), mag%/lvl (4)</small> | ✅ |
| Helm | `helm,nor,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Helm Inf | `helm,low` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Helm Sup | `helm,hiq,noe,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Helm Eth | `helm,nor,eth,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Helm Eth Sup | `helm,hiq,eth,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Weapon | `weap,nor,noe,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Weapon Inf | `weap,low` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Weapon Sup | `weap,hiq,noe,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Weapon Eth | `weap,nor,eth,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Weapon Eth Sup | `weap,hiq,eth,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Armor | `tors,nor,noe,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Armor Inf | `tors,low` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Armor Sup | `tors,hiq,noe,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Armor Eth | `tors,nor,eth,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Armor Eth Sup | `tors,hiq,eth,nos` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Shield | `shld,nor,noe` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Shield Inf | `shld,low` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Shield Sup | `shld,hiq,noe` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Shield Eth | `shld,nor,eth` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Shield Eth Sup | `shld,hiq,eth` + `lmr` | `useitem` <br><small>sock (6)</small> | ✅ |
| Helm | `helm,mag,nos` + `lmr` | `useitem` <br><small>sock (1-2)</small> | ✅ |
| Weapon | `weap,mag,nos` + `lmr` | `useitem` <br><small>sock (1-2)</small> | ✅ |
| Armor | `tors,mag,nos` + `lmr` | `useitem` <br><small>sock (1-2)</small> | ✅ |
| Shield | `shld,mag,nos` + `lmr` | `useitem` <br><small>sock (1-2)</small> | ✅ |
| Throwing Knives | `tkni,mag,nos` + `lmr` | `useitem` <br><small>sock (1-2)</small> | ✅ |
| Throwing Axes | `taxe,mag,nos` + `lmr` | `useitem` <br><small>sock (1-2)</small> | ✅ |
| Throwing Javelins | `jave,mag,nos` + `lmr` | `useitem` <br><small>sock (1-2)</small> | ✅ |
| Helm | `helm,rar,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Weapon | `weap,rar,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Armor | `tors,rar,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Shield | `shld,rar,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Knives | `tkni,rar,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Axes | `taxe,rar,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Javelins | `jave,rar,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Helm | `helm,set,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Weapon | `weap,set,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Armor | `tors,set,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Shield | `shld,set,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Knives | `tkni,set,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Axes | `taxe,set,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Javelins | `jave,set,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Helm | `helm,uni,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Weapon | `weap,uni,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Armor | `tors,uni,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Shield | `shld,uni,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Knives | `tkni,uni,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Axes | `taxe,uni,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Javelins | `jave,uni,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Helm | `helm,crf,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Weapon | `weap,crf,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Armor | `tors,crf,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Shield | `shld,crf,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Knives | `tkni,crf,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Axes | `taxe,crf,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Throwing Javelins | `jave,crf,nos` + `lmr` | `useitem` <br><small>sock (1)</small> | ✅ |
| Block Bows | `bow` + `fel` | `useitem` <br>+ `fel` | ✅ |
| Weapon + Flask = Ethereal Weapon | `weap,noe` + `fel` | `useitem` <br><small>ethereal (1)</small> | ✅ |
| Armor + Flask = Ethereal Armor | `armo,noe` + `fel` | `useitem` <br><small>ethereal (1)</small> | ✅ |
| MF + GF on Helm | `helm` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Weapon | `weap` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Amulet | `amu` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Shield | `shld` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Ring | `ring` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Gloves | `glov` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Boots | `boot` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Armor | `tors` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| MF + GF on Belt | `belt` + `r32` + `r24` + `r20` + `std` + `mls` | `useitem` <br><small>augmented1 (1), mag% (50), gold% (100), addxp (2)</small> | ✅ |
| Melee Augment on Helm | `helm` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Weapon | `weap` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Amulet | `amu` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Shield | `shld` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Ring | `ring` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Gloves | `glov` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Boots | `boot` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Armor | `tors` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Melee Augment on Belt | `belt` + `r25` + `r19` + `std` + `mls` | `useitem` <br><small>augmented1 (1), att (200), att% (10)</small> | ✅ |
| Teleport + MF + GF on Armor | `tors` + `r33` + `r29` + `The Stone of Jordan` + `std` + `mls` | `useitem` <br><small>oskill (1), augmented1 (1), mag%/lvl (), gold%/lvl (), addxp (2)</small> | ✅ |
| Break Down Hellfire Torch -> 1 Hellfire Ashes | `Hellfire Torch` + `mls` | `tds` | ✅ |
| Hellfire Ash + Stamina Potion -> 2 Standard of Heroes | `tds` + `wms` | `std` <br>+ `std` | ✅ |
| Break Down Annihilus -> 3 Standard of Heroes | `Annihilus` + `mls` | `std` <br>+ `std` <br>+ `std` | ✅ |
| Break Down Gheed's Fortune -> 3 MF Potions | `Gheed's Fortune` + `mls` | `mfp` <br>+ `mfp` <br>+ `mfp` | ✅ |
| Replenishing TP Book | `tbk` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Replenishing ID Book | `ibk` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Throwing Knife | `tkni` + `std` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Throwing Axe | `taxe` + `std` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Javelin | `jave` + `std` + `hsm` | `useitem` <br><small>rep-quant ()</small> | ✅ |
| Repair Augment on Magic Item | `any,mag` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Rare Item | `any,rar` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Set Armor | `armo,set` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Set Weapon | `weap,set` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Unique Armor | `armo,uni` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Unique Weapon | `weap,uni` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| Repair Augment on Crafted Item | `any,crf` + `std` + `hsm` | `useitem` <br><small>rep-dur ()</small> | ✅ |
| BLOCK CHARMS | `cm1,mag` + `std` | `useitem` <br>+ `std` | ✅ |
| BLOCK CHARMS | `cm2,mag` + `std` | `useitem` <br>+ `std` | ✅ |
| BLOCK CHARMS | `cm3,mag` + `std` | `useitem` <br>+ `std` | ✅ |
| BLOCK JEWELS | `jew` + `std` | `useitem` <br>+ `std` | ✅ |
| Magic Corruptor | `any,mag` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Brick | `any,mag` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `bow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `bow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `bow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `bow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `bow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `xbow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `xbow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `xbow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `xbow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `xbow,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `2han,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `2han,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `2han,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `2han,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `2han,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| Amulet | `amu,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `belt,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `glov,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `glov,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `boot,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `boot,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `helm,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `helm,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `tors,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `tors,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `shld,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `shld,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `weap,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `weap,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `weap,mag` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| RARE CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Rare Corruptor | `any,rar` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Brick | `any,rar` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `bow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `bow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `bow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `bow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `bow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `xbow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `xbow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `xbow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `xbow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `xbow,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `2han,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `2han,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `2han,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `2han,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `2han,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| Amulet | `amu,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `belt,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `glov,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `glov,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `boot,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `boot,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `helm,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `helm,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `tors,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `tors,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `shld,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `shld,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `weap,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `weap,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `weap,rar` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| SET CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Set Corruptor | `any,set` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Brick | `any,set` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `bow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `bow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `bow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `bow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `bow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `xbow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `xbow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `xbow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `xbow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `xbow,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `2han,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `2han,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `2han,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `2han,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `2han,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| Amulet | `amu,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `belt,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `glov,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `glov,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `boot,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `boot,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `helm,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `helm,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `tors,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `tors,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `shld,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `shld,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `weap,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `weap,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `weap,set` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| UNIQUE CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Unique Corruptor | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `tds` | ✅ |
| Unique Corruptor | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `tds` <br>+ `tds` | ✅ |
| Unique Corruptor | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `tds` | ✅ |
| Unique Corruptor | `armo,uni` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Unique Corruptor | `weap,uni` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Unique Corruptor | `ring,uni` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Unique Corruptor | `amul,uni` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Brick | `Gheed's Fortune` + `tds` | `usetype,mag` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| Brick | `armo,uni` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| Brick | `weap,uni` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| Brick | `ring,uni` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| Brick | `amul,uni` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| Annihilus |  | `-` | ❌ |
| MF +  GF | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), gold% (10), corruption1 (1), mag% (7)</small> | ✅ |
| FHR+ FRW | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), balance2 (5), corruption1 (1), move2 (5)</small> | ✅ |
| Attributes | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), all-stats (5), corruption1 (1)</small> | ✅ |
| Life + Mana | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), hp (20), corruption1 (1), mana (17)</small> | ✅ |
| Increased Attack Speed | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), swing3 (5-10), corruption1 (1)</small> | ✅ |
| Faster Cast Rate | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), cast2 (5-10), corruption1 (1)</small> | ✅ |
| All Resistance | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), res-all (5), corruption1 (1)</small> | ✅ |
| Experience | `Annihilus` + `tds` | `useitem` <br><small>corruption2 (1001), addxp (5), corruption1 (1)</small> | ✅ |
| Hellfire Torch |  | `-` | ❌ |
| Amplify Damage | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (40-22), corruption1 (1)</small> | ✅ |
| Lower Resist | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (75-18), corruption1 (1)</small> | ✅ |
| Life Tap | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (25-21), corruption1 (1)</small> | ✅ |
| Weaken | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (50-18), corruption1 (1)</small> | ✅ |
| Decrepify | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (60-20), corruption1 (1)</small> | ✅ |
| Bone Armor | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (60-21), corruption1 (1)</small> | ✅ |
| Cyclone Armor | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (60-21), corruption1 (1)</small> | ✅ |
| Static | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (60-20), corruption1 (1)</small> | ✅ |
| Frost Nova | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), gethit-skill (75-24), corruption1 (1)</small> | ✅ |
| Prayer | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), aura (31), corruption1 (1)</small> | ✅ |
| Blessed Aim | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), aura (10), corruption1 (1)</small> | ✅ |
| Vigor | `Hellfire Torch` + `tds,qty=2` | `useitem` <br><small>corruption2 (1001), aura (10), corruption1 (1)</small> | ✅ |
| Gheed's Fortune |  | `-` | ❌ |
| Gheed's Blessing | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), gold% (20-40), corruption1 (1), mag% (5-10), cheap (5)</small> | ✅ |
| Faster Hit Recovery | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), balance2 (12), corruption1 (1)</small> | ✅ |
| All Resistances | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), res-all (15), corruption1 (1)</small> | ✅ |
| Faster Run/Walk | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), move2 (7), corruption1 (1)</small> | ✅ |
| Maximum Damage and AR | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), att (76), dmg-max (10), corruption1 (1)</small> | ✅ |
| Bow and Crossbow | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Passive and Magic | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Jav and Spear | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Traps | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Martial Arts | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Shadow Disciplines | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Curses | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Necro Summoning Skills | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Poison and Bone | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Masteries | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Barb Combat | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Warcries | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Offensive Auras | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Defensive Auras | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Pally Combat | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Fire Skills | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Lightning Skills | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Cold Skills | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Druid Summoning | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Elemental Skills | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Shapeshifting Skills | `Gheed's Fortune` + `tds` | `useitem` <br><small>corruption2 (1001), skilltab (1), corruption1 (1)</small> | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `bow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `bow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `bow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `bow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `bow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `xbow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `xbow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `xbow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `xbow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `xbow,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `2han,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `2han,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `2han,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `2han,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `2han,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| Amulet | `amu,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `belt,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `glov,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `glov,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `boot,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `boot,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `helm,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `helm,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `tors,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `tors,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `shld,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `shld,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `weap,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `weap,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `weap,uni` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| CRAFT CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Craft Corruptor | `any,crf` + `std` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `std` | ✅ |
| Brick | `any,crf` + `std` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `brk` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `bow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `bow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `bow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `bow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `bow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `xbow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `xbow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `xbow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `xbow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `xbow,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `2han,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `2han,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `2han,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| 5 Socket | `2han,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> | ✅ |
| 6 Socket | `2han,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| Amulet | `amu,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `belt,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `glov,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `glov,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `boot,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `boot,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `helm,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `helm,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `tors,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `tors,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `shld,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `shld,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> | ✅ |
| 2 Socket | `weap,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> | ✅ |
| 3 Socket | `weap,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> | ✅ |
| 4 Socket | `weap,crf` + `std` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| DIVINE CORRUPTIONS |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| MAGIC CORRUPTIONS |  | `-` | ❌ |
| BLOCK CHARMS | `cm1,mag` + `dsd` | `useitem` <br>+ `dsd` | ✅ |
| BLOCK CHARMS | `cm2,mag` + `dsd` | `useitem` <br>+ `dsd` | ✅ |
| BLOCK CHARMS | `cm3,mag` + `dsd` | `useitem` <br>+ `dsd` | ✅ |
| BLOCK JEWELS | `jew` + `dsd` | `useitem` <br>+ `dsd` | ✅ |
| Magic Corruptor | `any,mag` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Brick | `any,mag` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `bow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `bow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `bow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `bow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `bow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `xbow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `xbow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `xbow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `xbow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `xbow,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `2han,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `2han,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `2han,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `2han,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `2han,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Amulet | `amu,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `belt,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `glov,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `glov,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `boot,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `boot,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `helm,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `helm,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `tors,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `tors,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `shld,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `shld,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `weap,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `weap,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `weap,mag` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| RARE CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Rare Corruptor | `any,rar` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Brick | `any,rar` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `bow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `bow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `bow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `bow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `bow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `xbow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `xbow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `xbow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `xbow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `xbow,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `2han,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `2han,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `2han,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `2han,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `2han,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Amulet | `amu,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `belt,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `glov,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `glov,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `boot,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `boot,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `helm,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `helm,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `tors,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `tors,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `shld,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `shld,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `weap,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `weap,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `weap,rar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| SET CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Set Corruptor | `any,set` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Brick | `any,set` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `bow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `bow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `bow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `bow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `bow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `xbow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `xbow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `xbow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `xbow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `xbow,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `2han,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `2han,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `2han,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `2han,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `2han,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Amulet | `amu,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `belt,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `glov,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `glov,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `boot,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `boot,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `helm,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `helm,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `tors,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `tors,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `shld,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `shld,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `weap,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `weap,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `weap,set` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| UNIQUE CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Unique Corruptor | `armo,uni` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Unique Corruptor | `weap,uni` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Unique Corruptor | `ring,uni` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Unique Corruptor | `amul,uni` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Brick | `armo,uni` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Brick | `weap,uni` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Brick | `ring,uni` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Brick | `amul,uni` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| Dragonscale | `Dragonscale` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Spirit Ward | `Spirit Ward` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Ravenlore | `Ravenlore` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Steel Carapace | `Steel Carapice` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Stone Crusher | `Stone Crusher` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Schaefer's Hammer | `Schaefer's Hammer` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Fleshripper | `Fleshripper` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Gut Siphon | `Gutsiphon` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Frostwind | `Frostwind` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Messerschmidt's Reaver | `Messerschmidt's Reaver` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Giant Skull | `Giantskull` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Gargoyle's Bite | `Gargoyle's Bite` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Steel Pillar | `Steelpillar` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Death's Web | `Deaths's Web` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Earth Shifter | `Earthshifter` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| The Cranium Basher | `Dragonscale` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Templar's Might | `Templar's Might` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Tyrael's Might | `Tyrael's Might` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Steelrend | `Steelrend` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Shadow Dancer | `Shadowdancer` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Ghostflame | `Ghostflame` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Windforce | `Windforce` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Executioner's Justice | `Executioner's Justice` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Stormspire | `Stormspire` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Death's Fathom | `Fathom` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Griffon's Eye | `Griffon's Eye` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Crown of Ages | `Crown of Ages` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| The Grandfather | `The Grandfather` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Astreon's Iron Ward | `Ironward` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Darkforce Spawn | `Darkforge Spawn` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Death Cleaver | `Deathcleaver` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Mang Song's Lesson | `Mang Song's Lesson` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` <br>+ `r33` | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `bow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `bow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `bow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `bow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `bow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `xbow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `xbow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `xbow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `xbow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `xbow,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `2han,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `2han,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `2han,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `2han,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `2han,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Amulet | `amu,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `belt,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `glov,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `glov,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `boot,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `boot,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `helm,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `helm,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `tors,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `tors,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `shld,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `shld,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `weap,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `weap,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `weap,uni` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| CRAFT CORRUPTIONS ---------------- |  | `-` | ❌ |
| Unknown Recipe |  | `-` | ❌ |
| Craft Corruptor | `any,crf` + `dsd` | `useitem` <br><small>corruption2 (1-1000)</small> <br>+ `dsd` | ✅ |
| Brick | `any,crf` + `dsd` | `usetype,rar` <br><small>corruption2 (1001), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Bows |  | `-` | ❌ |
| 1 Socket | `bow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `bow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `bow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `bow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `bow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `bow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket Crossbows |  | `-` | ❌ |
| 1 Socket | `xbow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `xbow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `xbow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `xbow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `xbow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `xbow,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Handed Sockets |  | `-` | ❌ |
| 1 Socket | `2han,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `2han,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `2han,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `2han,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 5 Socket | `2han,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (5), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 6 Socket | `2han,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (6), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 1 Socket |  | `-` | ❌ |
| Rings | `ring,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Amulet | `amu,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket Belts |  | `-` | ❌ |
| 1 Socket | `belt,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `belt,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Gloves |  | `-` | ❌ |
| 1 Socket | `glov,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `glov,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `glov,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Boots |  | `-` | ❌ |
| 1 Socket | `boot,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `boot,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `boot,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Helm |  | `-` | ❌ |
| 1 Socket | `helm,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `helm,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `helm,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Chest |  | `-` | ❌ |
| 1 Socket | `tors,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `tors,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `tors,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket Shield |  | `-` | ❌ |
| 1 Socket | `shld,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `shld,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `shld,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket Weapons |  | `-` | ❌ |
| 1 Socket | `weap,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (1), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 2 Socket | `weap,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (2), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 3 Socket | `weap,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (3), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| 4 Socket | `weap,crf` + `dsd` | `useitem` <br><small>corruption2 (1001), sock (4), corruption1 (1)</small> <br>+ `dsd` | ✅ |
| Unknown Recipe |  | `-` | ❌ |
| TRANSMOGIFY |  | `-` | ❌ |
| White | `tors` + `dw1` | `useitem` <br><small>state (1), dyewhite1 (1), dyed1 (1)</small> | ✅ |
| Black | `tors` + `db1` | `useitem` <br><small>state (1), dyeblack1 (1), dyed1 (1)</small> | ✅ |
| Remove White | `tors` + `1dr` | `useitem` <br><small>state (-1), dyewhite1 (-1), dyed1 (-1)</small> | ✅ |
| Remove Black | `tors` + `1dr` | `useitem` <br><small>state (-1), dyeblack1 (-1), dyed1 (-1)</small> | ✅ |
| White | `helm` + `dw1` | `useitem` <br><small>state (1), dyewhite1 (1), dyed1 (1)</small> | ✅ |
| Black | `helm` + `db1` | `useitem` <br><small>state (1), dyeblack1 (1), dyed1 (1)</small> | ✅ |
| Remove White | `helm` + `1dr` | `useitem` <br><small>state (-1), dyewhite1 (-1), dyed1 (-1)</small> | ✅ |
| Remove Black | `helm` + `1dr` | `useitem` <br><small>state (-1), dyeblack1 (-1), dyed1 (-1)</small> | ✅ |
| White | `shld` + `dw1` | `useitem` <br><small>state (1), dyewhite1 (1), dyed1 (1)</small> | ✅ |
| Black | `shld` + `db1` | `useitem` <br><small>state (1), dyeblack1 (1), dyed1 (1)</small> | ✅ |
| Remove White | `shld` + `1dr` | `useitem` <br><small>state (-1), dyewhite1 (-1), dyed1 (-1)</small> | ✅ |
| Remove Black | `shld` + `1dr` | `useitem` <br><small>state (-1), dyeblack1 (-1), dyed1 (-1)</small> | ✅ |
| White | `weap` + `dw1` | `useitem` <br><small>state (1), dyewhite1 (1), dyed1 (1)</small> | ✅ |
| Black | `weap` + `db1` | `useitem` <br><small>state (1), dyeblack1 (1), dyed1 (1)</small> | ✅ |
| Remove White | `weap` + `1dr` | `useitem` <br><small>state (-1), dyewhite1 (-1), dyed1 (-1)</small> | ✅ |
| Remove Black | `weap` + `1dr` | `useitem` <br><small>state (-1), dyeblack1 (-1), dyed1 (-1)</small> | ✅ |
| SPLASH CHARM UPGRADES WIP |  | `-` | ❌ |
| UPGRADE SPLASH CHARM TIER - T1 Splash Charm & El-Rune = T2 Splash Charm | `Ravaging T1` + `r01` | `Ravaging T2` <br>+ `Ravaging T2` | ❌ |
| UPGRADE SPLASH CHARM TIER - T2 Splash Charm & Nef-Rune  = T3 Splash Charm | `Ravaging T2` + `r04` | `Ravaging T3` <br>+ `Ravaging T3` | ❌ |
| UPGRADE SPLASH CHARM TIER - T3 Splash Charm & Sol-Rune & Flawless Skull = T4 Splash Charm | `Ravaging T3` + `r12` + `1kl` | `Ravaging T4` <br>+ `Ravaging T4` | ❌ |
| UPGRADE SPLASH CHARM TIER - T4 Splash Charm & Hel-Rune & Flawless Skull = T5 Splash Charm | `Ravaging T4` + `r15` + `1kl` | `Ravaging T5` <br>+ `Ravaging T5` | ❌ |
| UPGRADE SPLASH CHARM TIER - T5 Splash Charm & Fal-Rune & Perfect Skull = T6 Splash Charm | `Ravaging T5` + `r19` + `1kz` | `Ravaging T6` <br>+ `Ravaging T6` | ❌ |
| UPGRADE SPLASH CHARM TIER - T6 Splash Charm & Pul-Rune & Eth-Rune & Perfect Skull = T7 Splash Charm | `Ravaging T6` + `r21` + `r05` | `Ravaging T7` <br>+ `Ravaging T7` | ❌ |
| UPGRADE SPLASH CHARM TIER - T7 Splash Charm & Mal-Rune & Tal-Rune & Perfect Skull = T8 Splash Charm | `Ravaging T7` + `r23` + `r07` | `Ravaging T8` <br>+ `Ravaging T8` | ❌ |
| UPGRADE SPLASH CHARM TIER - T8 Splash Charm & Ohm-Rune & Ral-Rune & Charsi Malus & Larzuk Malus = T9 Splash Charm | `Ravaging T8` + `r27` + `r08` + `mls` + `lmr` | `Ravaging T9` <br>+ `Ravaging T9` | ❌ |
