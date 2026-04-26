# Differences for missiles.txt

*Key column used: `Missile`*

## Added Rows (9)
- firenovaarrow
- frostnovaarrow
- poisondagger
- poisondaggeractivator
- poisondaggernova
- powerstrikenova
- proc\_splashdamage
- proc\_splashinit
- thunderstormnova
## Modified Rows (75)
### acidspray
- `Range`: $$	ext{6}$\color{gray}{\text{ +  (lvl *  2)}}$ (Old) &rarr; $$	ext{6}$$ (New)
### baal taunt lightning
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  2)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### battlecry
- `Vel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
- `MaxVel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
- `Accel`: $\color{gray}{\text{-1000}}$ (Old) &rarr; $\color{blue}{\text{-500}}$ (New)
- `Range`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
### blade creeper
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  5)}}$ (Old) &rarr; $$	ext{10}$$ (New)
- `NextDelay`: $\color{gray}{\text{25}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
### blade shield attachment
- `Range`: $$	ext{500}$\color{gray}{\text{ +  (lvl *  100)}}$ (Old) &rarr; $$	ext{500}$$ (New)
### blaze
- `Range`: $$	ext{90}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{90}$$ (New)
### bluelightmissile
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  10)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### bonespirit
- `Vel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{16}}$ (New)
- `MaxVel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{16}}$ (New)
### bonewallmaker
- `Range`: $$	ext{7}$\color{gray}{\text{ +  (lvl *  2)}}$ (Old) &rarr; $$	ext{7}$$ (New)
### catapult meteor fire
- `Range`: $$	ext{90}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{90}$$ (New)
### coldarrow
- `pCltHitFunc`:  (Old) &rarr; $\color{blue}{\text{4}}$ (New)
- `pSrvHitFunc`:  (Old) &rarr; $\color{blue}{\text{5}}$ (New)
- `sHitPar1`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `HitSubMissile1`:  (Old) &rarr; $\color{blue}{\text{frostnovaarrow}}$ (New)
- `CltHitSubMissile1`:  (Old) &rarr; $\color{blue}{\text{frostnovaarrow}}$ (New)
### coldfissure center
- `\*ID`: $\color{gray}{\text{726}}$ (Old) &rarr; $\color{blue}{\text{725}}$ (New)
### colossal throwing axe
- `\*ID`: $\color{gray}{\text{732}}$ (Old) &rarr; $\color{blue}{\text{731}}$ (New)
### colossalchargedbolt
- `\*ID`: $\color{gray}{\text{723}}$ (Old) &rarr; $\color{blue}{\text{735}}$ (New)
### countessfirewall
- `Range`: $$	ext{1000}$\color{gray}{\text{ +  (lvl *  1)}}$ (Old) &rarr; $$	ext{1000}$$ (New)
### distraction fog
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  5)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### explodingarrowexp2
- `sHitPar1`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{7}}$ (New)
### firearrow
- `pCltHitFunc`:  (Old) &rarr; $\color{blue}{\text{4}}$ (New)
- `pSrvHitFunc`:  (Old) &rarr; $\color{blue}{\text{5}}$ (New)
- `sHitPar1`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `HitSubMissile1`:  (Old) &rarr; $\color{blue}{\text{firenovaarrow}}$ (New)
- `CltHitSubMissile1`:  (Old) &rarr; $\color{blue}{\text{firenovaarrow}}$ (New)
### fireball
- `sHitPar1`: $\color{gray}{\text{0}}$ (Old) &rarr; $\color{blue}{\text{4}}$ (New)
### firemedium
- `Range`: $$	ext{90}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{90}$$ (New)
### firesmall
- `Range`: $$	ext{90}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{90}$$ (New)
### firetwister
- `\*ID`: $\color{gray}{\text{720}}$ (Old) &rarr; $\color{blue}{\text{732}}$ (New)
### firewallmaker
- `Range`: $$	ext{7}$\color{gray}{\text{ +  (lvl *  2)}}$ (Old) &rarr; $$	ext{7}$$ (New)
### fistoftheheavensbolt
- `sHitPar2`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `cHitPar1`: $\color{gray}{\text{1}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `cHitPar2`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `EDmgSymPerCalc`: $$	ext{skill('Holy Bolt'.blvl) *}$\color{gray}{\text{ 15}}$ (Old) &rarr; $$	ext{skill('Holy Bolt'.blvl) *}$\color{blue}{\text{6}}$ (New)
### frozenorb
- `Vel`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{16}}$ (New)
- `MaxVel`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{16}}$ (New)
### frozenorbbolt
- `Vel`: $\color{gray}{\text{18}}$ (Old) &rarr; $\color{blue}{\text{16}}$ (New)
- `MaxVel`: $\color{gray}{\text{18}}$ (Old) &rarr; $\color{blue}{\text{16}}$ (New)
### frozenorbnova
- `Vel`: $\color{gray}{\text{24}}$ (Old) &rarr; $\color{blue}{\text{30}}$ (New)
- `MaxVel`: $\color{gray}{\text{24}}$ (Old) &rarr; $\color{blue}{\text{30}}$ (New)
### greenlightmissile
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  10)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### grimwardscare
- `Range`: $$	ext{24}$\color{gray}{\text{ +  (lvl *  12)}}$ (Old) &rarr; $$	ext{24}$$ (New)
### guidedarrow
- `Pierce`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### healing vortex
- `Range`: $$	ext{100}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{100}$$ (New)
### holybolt
- `sHitPar1`: $\color{gray}{\text{1}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `sHitPar2`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `cHitPar1`: $\color{gray}{\text{1}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
- `cHitPar2`: $\color{gray}{\text{3}}$ (Old) &rarr; $\color{blue}{\text{0}}$ (New)
### hydra
- `Vel`: $\color{gray}{\text{16}}$ (Old) &rarr; $\color{blue}{\text{40}}$ (New)
- `MaxVel`: $\color{gray}{\text{16}}$ (Old) &rarr; $\color{blue}{\text{40}}$ (New)
### ice crack 1
- `\*ID`: $\color{gray}{\text{727}}$ (Old) &rarr; $\color{blue}{\text{726}}$ (New)
### ice crack 2
- `\*ID`: $\color{gray}{\text{728}}$ (Old) &rarr; $\color{blue}{\text{727}}$ (New)
### ice vapor 1
- `\*ID`: $\color{gray}{\text{729}}$ (Old) &rarr; $\color{blue}{\text{728}}$ (New)
### ice vapor 2
- `\*ID`: $\color{gray}{\text{730}}$ (Old) &rarr; $\color{blue}{\text{729}}$ (New)
### iceblast
- `Vel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
- `MaxVel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
### immolationfire
- `EMin`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{24}}$ (New)
- `MinELev1`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `MinELev2`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `MinELev3`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{12}}$ (New)
- `MinELev4`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{12}}$ (New)
- `MinELev5`: $\color{gray}{\text{6}}$ (Old) &rarr; $\color{blue}{\text{12}}$ (New)
- `EMax`: $\color{gray}{\text{24}}$ (Old) &rarr; $\color{blue}{\text{48}}$ (New)
- `MaxELev1`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
- `MaxELev2`: $\color{gray}{\text{5}}$ (Old) &rarr; $\color{blue}{\text{10}}$ (New)
- `MaxELev3`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{14}}$ (New)
- `MaxELev4`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{14}}$ (New)
- `MaxELev5`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{14}}$ (New)
- `EDmgSymPerCalc`: $$	ext{skill('Fire Arrow'.blvl)}$$	ext{ * 5}$$ (Old) &rarr; $\color{blue}{\text{(}}$	ext{skill('Fire Arrow'.blvl)}$\color{blue}{\text{+skill('Exploding Arrow'.blvl))}}$	ext{ * 5}$$ (New)
### mephistoflyingrocksbig
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  3)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### mephistoflyingrockssmall
- `Range`: $$	ext{5}$\color{gray}{\text{ +  (lvl *  3)}}$ (Old) &rarr; $$	ext{5}$$ (New)
### meteor
- `Range`: $\color{gray}{\text{60}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
### meteorcenter
- `CltParam1`: $\color{gray}{\text{59}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
- `Range`: $\color{gray}{\text{60}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
### meteorexplode
- `Range`: $\color{gray}{\text{16}}$ (Old) &rarr; $\color{blue}{\text{13}}$ (New)
### meteortail
- `Range`: $\color{gray}{\text{60}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
### monblizcenter
- `Range`: $$	ext{25}$\color{gray}{\text{ +  (lvl *  15)}}$ (Old) &rarr; $$	ext{25}$$ (New)
### multipleshotarrow
- `Range`: $\color{gray}{\text{50}}$ (Old) &rarr; $\color{blue}{\text{27}}$ (New)
### multipleshotbolt
- `Range`: $\color{gray}{\text{50}}$ (Old) &rarr; $\color{blue}{\text{27}}$ (New)
### phoenixtrail
- `Range`: $$	ext{90}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{90}$$ (New)
### plague vines trail
- `Range`: $$	ext{100}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{100}$$ (New)
### poisonnova
- `Vel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
- `MaxVel`: $\color{gray}{\text{12}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
### rabiesplague
- `Param1`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{1}}$ (New)
- `Param2`: $\color{gray}{\text{7}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  5)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### redlightmissile
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  10)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### ringoffireexplode
- `\*ID`: $\color{gray}{\text{731}}$ (Old) &rarr; $\color{blue}{\text{730}}$ (New)
### royalstrikechainlightning
- `pCltHitFunc`:  (Old) &rarr; $\color{blue}{\text{*16}}$ (New)
- `pSrvHitFunc`:  (Old) &rarr; $\color{blue}{\text{*12}}$ (New)
### royalstrikemeteor
- `Range`: $\color{gray}{\text{60}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
### royalstrikemeteorcenter
- `CltParam1`: $\color{gray}{\text{59}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
- `Range`: $\color{gray}{\text{60}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
- `ProgSound`:  (Old) &rarr; $\color{blue}{\text{sorceress\_meteor\_impact}}$ (New)
### royalstrikemeteorexplode
- `Range`: $\color{gray}{\text{16}}$ (Old) &rarr; $\color{blue}{\text{13}}$ (New)
### royalstrikemeteortail
- `Range`: $\color{gray}{\text{60}}$ (Old) &rarr; $\color{blue}{\text{18}}$ (New)
### sentrylightningbolt
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  2)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### sentrylightningbolt2
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  2)}}$ (Old) &rarr; $$	ext{10}$$ (New)
### sentryspikeonground
- `Range`: $$	ext{180}$\color{gray}{\text{ +  (lvl *  60)}}$ (Old) &rarr; $$	ext{180}$$ (New)
### shockwave
- `NextHit`: $\color{gray}{\text{1}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `NextDelay`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
### taintedfireball
- `\*ID`: $\color{gray}{\text{722}}$ (Old) &rarr; $\color{blue}{\text{734}}$ (New)
### taintedfirebolt
- `\*ID`: $\color{gray}{\text{721}}$ (Old) &rarr; $\color{blue}{\text{733}}$ (New)
### teeth
- `NextDelay`: $\color{gray}{\text{4}}$ (Old) &rarr; $\color{blue}{\text{(removed)}}$ (New)
- `Pierce`:  (Old) &rarr; $\color{blue}{\text{1}}$ (New)
### throwingstar
- `Range`: $$	ext{100}$\color{gray}{\text{ +  (lvl *  50)}}$ (Old) &rarr; $$	ext{100}$$ (New)
### thunderstorm1
- `pCltHitFunc`:  (Old) &rarr; $\color{blue}{\text{4}}$ (New)
- `pSrvHitFunc`:  (Old) &rarr; $\color{blue}{\text{5}}$ (New)
- `HitSubMissile1`:  (Old) &rarr; $\color{blue}{\text{thunderstormnova}}$ (New)
- `CltHitSubMissile1`:  (Old) &rarr; $\color{blue}{\text{thunderstormnova}}$ (New)
### tornado
- `Vel`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `MaxVel`: $\color{gray}{\text{8}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `NextDelay`: $\color{gray}{\text{25}}$ (Old) &rarr; $\color{blue}{\text{15}}$ (New)
### towerchestspawner
- `Range`: $$	ext{400}$\color{gray}{\text{ +  (lvl *  1)}}$ (Old) &rarr; $$	ext{400}$$ (New)
### towermistfade
- `Range`: $$	ext{128}$\color{gray}{\text{ +  (lvl *  1)}}$ (Old) &rarr; $$	ext{128}$$ (New)
### twister
- `Vel`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `MaxVel`: $\color{gray}{\text{10}}$ (Old) &rarr; $\color{blue}{\text{20}}$ (New)
- `AnimSpeed`: $\color{gray}{\text{16}}$ (Old) &rarr; $\color{blue}{\text{8}}$ (New)
### vines trail
- `Range`: $$	ext{100}$\color{gray}{\text{ +  (lvl *  25)}}$ (Old) &rarr; $$	ext{100}$$ (New)
### wake of destruction maker
- `Range`: $$	ext{25}$\color{gray}{\text{ +  (lvl *  2)}}$ (Old) &rarr; $$	ext{25}$$ (New)
### whitelightmissile
- `Range`: $$	ext{10}$\color{gray}{\text{ +  (lvl *  10)}}$ (Old) &rarr; $$	ext{10}$$ (New)
