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
- `Range`: <strong><code>6 +  (lvl *  2)</code></strong> (Old) &rarr; <strong><code>6</code></strong> (New)
### baal taunt lightning
- `Range`: <strong><code>10 +  (lvl *  2)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### battlecry
- `Vel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
- `MaxVel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
- `Accel`: <strong><code>-1000</code></strong> (Old) &rarr; <strong><code>-500</code></strong> (New)
- `Range`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
### blade creeper
- `Range`: <strong><code>10 +  (lvl *  5)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
- `NextDelay`: <strong><code>25</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
### blade shield attachment
- `Range`: <strong><code>500 +  (lvl *  100)</code></strong> (Old) &rarr; <strong><code>500</code></strong> (New)
### blaze
- `Range`: <strong><code>90 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>90</code></strong> (New)
### bluelightmissile
- `Range`: <strong><code>10 +  (lvl *  10)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### bonespirit
- `Vel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>16</code></strong> (New)
- `MaxVel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>16</code></strong> (New)
### bonewallmaker
- `Range`: <strong><code>7 +  (lvl *  2)</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
### catapult meteor fire
- `Range`: <strong><code>90 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>90</code></strong> (New)
### coldarrow
- `pCltHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>4</code></strong> (New)
- `pSrvHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
- `sHitPar1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `HitSubMissile1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>frostnovaarrow</code></strong> (New)
- `CltHitSubMissile1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>frostnovaarrow</code></strong> (New)
### coldfissure center
- `\*ID`: <strong><code>726</code></strong> (Old) &rarr; <strong><code>725</code></strong> (New)
### colossal throwing axe
- `\*ID`: <strong><code>732</code></strong> (Old) &rarr; <strong><code>731</code></strong> (New)
### colossalchargedbolt
- `\*ID`: <strong><code>723</code></strong> (Old) &rarr; <strong><code>735</code></strong> (New)
### countessfirewall
- `Range`: <strong><code>1000 +  (lvl *  1)</code></strong> (Old) &rarr; <strong><code>1000</code></strong> (New)
### distraction fog
- `Range`: <strong><code>10 +  (lvl *  5)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### explodingarrowexp2
- `sHitPar1`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
### firearrow
- `pCltHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>4</code></strong> (New)
- `pSrvHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
- `sHitPar1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `HitSubMissile1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>firenovaarrow</code></strong> (New)
- `CltHitSubMissile1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>firenovaarrow</code></strong> (New)
### fireball
- `sHitPar1`: <strong><code>0</code></strong> (Old) &rarr; <strong><code>4</code></strong> (New)
### firemedium
- `Range`: <strong><code>90 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>90</code></strong> (New)
### firesmall
- `Range`: <strong><code>90 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>90</code></strong> (New)
### firetwister
- `\*ID`: <strong><code>720</code></strong> (Old) &rarr; <strong><code>732</code></strong> (New)
### firewallmaker
- `Range`: <strong><code>7 +  (lvl *  2)</code></strong> (Old) &rarr; <strong><code>7</code></strong> (New)
### fistoftheheavensbolt
- `sHitPar2`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `cHitPar1`: <strong><code>1</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `cHitPar2`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `EDmgSymPerCalc`: <strong><code>skill('Holy Bolt'.blvl) * 15</code></strong> (Old) &rarr; <strong><code>skill('Holy Bolt'.blvl) *6</code></strong> (New)
### frozenorb
- `Vel`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>16</code></strong> (New)
- `MaxVel`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>16</code></strong> (New)
### frozenorbbolt
- `Vel`: <strong><code>18</code></strong> (Old) &rarr; <strong><code>16</code></strong> (New)
- `MaxVel`: <strong><code>18</code></strong> (Old) &rarr; <strong><code>16</code></strong> (New)
### frozenorbnova
- `Vel`: <strong><code>24</code></strong> (Old) &rarr; <strong><code>30</code></strong> (New)
- `MaxVel`: <strong><code>24</code></strong> (Old) &rarr; <strong><code>30</code></strong> (New)
### greenlightmissile
- `Range`: <strong><code>10 +  (lvl *  10)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### grimwardscare
- `Range`: <strong><code>24 +  (lvl *  12)</code></strong> (Old) &rarr; <strong><code>24</code></strong> (New)
### guidedarrow
- `Pierce`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### healing vortex
- `Range`: <strong><code>100 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>100</code></strong> (New)
### holybolt
- `sHitPar1`: <strong><code>1</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `sHitPar2`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `cHitPar1`: <strong><code>1</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
- `cHitPar2`: <strong><code>3</code></strong> (Old) &rarr; <strong><code>0</code></strong> (New)
### hydra
- `Vel`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>40</code></strong> (New)
- `MaxVel`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>40</code></strong> (New)
### ice crack 1
- `\*ID`: <strong><code>727</code></strong> (Old) &rarr; <strong><code>726</code></strong> (New)
### ice crack 2
- `\*ID`: <strong><code>728</code></strong> (Old) &rarr; <strong><code>727</code></strong> (New)
### ice vapor 1
- `\*ID`: <strong><code>729</code></strong> (Old) &rarr; <strong><code>728</code></strong> (New)
### ice vapor 2
- `\*ID`: <strong><code>730</code></strong> (Old) &rarr; <strong><code>729</code></strong> (New)
### iceblast
- `Vel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
- `MaxVel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
### immolationfire
- `EMin`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>24</code></strong> (New)
- `MinELev1`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
- `MinELev2`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
- `MinELev3`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>12</code></strong> (New)
- `MinELev4`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>12</code></strong> (New)
- `MinELev5`: <strong><code>6</code></strong> (Old) &rarr; <strong><code>12</code></strong> (New)
- `EMax`: <strong><code>24</code></strong> (Old) &rarr; <strong><code>48</code></strong> (New)
- `MaxELev1`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
- `MaxELev2`: <strong><code>5</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
- `MaxELev3`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>14</code></strong> (New)
- `MaxELev4`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>14</code></strong> (New)
- `MaxELev5`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>14</code></strong> (New)
- `EDmgSymPerCalc`: <strong><code>skill('Fire Arrow'.blvl) * 5</code></strong> (Old) &rarr; <strong><code>(skill('Fire Arrow'.blvl)+skill('Exploding Arrow'.blvl)) * 5</code></strong> (New)
### mephistoflyingrocksbig
- `Range`: <strong><code>10 +  (lvl *  3)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### mephistoflyingrockssmall
- `Range`: <strong><code>5 +  (lvl *  3)</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
### meteor
- `Range`: <strong><code>60</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
### meteorcenter
- `CltParam1`: <strong><code>59</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
- `Range`: <strong><code>60</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
### meteorexplode
- `Range`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>13</code></strong> (New)
### meteortail
- `Range`: <strong><code>60</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
### monblizcenter
- `Range`: <strong><code>25 +  (lvl *  15)</code></strong> (Old) &rarr; <strong><code>25</code></strong> (New)
### multipleshotarrow
- `Range`: <strong><code>50</code></strong> (Old) &rarr; <strong><code>27</code></strong> (New)
### multipleshotbolt
- `Range`: <strong><code>50</code></strong> (Old) &rarr; <strong><code>27</code></strong> (New)
### phoenixtrail
- `Range`: <strong><code>90 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>90</code></strong> (New)
### plague vines trail
- `Range`: <strong><code>100 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>100</code></strong> (New)
### poisonnova
- `Vel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
- `MaxVel`: <strong><code>12</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
### rabiesplague
- `Param1`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
- `Param2`: <strong><code>7</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
- `Range`: <strong><code>10 +  (lvl *  5)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### redlightmissile
- `Range`: <strong><code>10 +  (lvl *  10)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### ringoffireexplode
- `\*ID`: <strong><code>731</code></strong> (Old) &rarr; <strong><code>730</code></strong> (New)
### royalstrikechainlightning
- `pCltHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>*16</code></strong> (New)
- `pSrvHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>*12</code></strong> (New)
### royalstrikemeteor
- `Range`: <strong><code>60</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
### royalstrikemeteorcenter
- `CltParam1`: <strong><code>59</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
- `Range`: <strong><code>60</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
- `ProgSound`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>sorceress_meteor_impact</code></strong> (New)
### royalstrikemeteorexplode
- `Range`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>13</code></strong> (New)
### royalstrikemeteortail
- `Range`: <strong><code>60</code></strong> (Old) &rarr; <strong><code>18</code></strong> (New)
### sentrylightningbolt
- `Range`: <strong><code>10 +  (lvl *  2)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### sentrylightningbolt2
- `Range`: <strong><code>10 +  (lvl *  2)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
### sentryspikeonground
- `Range`: <strong><code>180 +  (lvl *  60)</code></strong> (Old) &rarr; <strong><code>180</code></strong> (New)
### shockwave
- `NextHit`: <strong><code>1</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `NextDelay`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
### taintedfireball
- `\*ID`: <strong><code>722</code></strong> (Old) &rarr; <strong><code>734</code></strong> (New)
### taintedfirebolt
- `\*ID`: <strong><code>721</code></strong> (Old) &rarr; <strong><code>733</code></strong> (New)
### teeth
- `NextDelay`: <strong><code>4</code></strong> (Old) &rarr; <strong><code>(removed)</code></strong> (New)
- `Pierce`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>1</code></strong> (New)
### throwingstar
- `Range`: <strong><code>100 +  (lvl *  50)</code></strong> (Old) &rarr; <strong><code>100</code></strong> (New)
### thunderstorm1
- `pCltHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>4</code></strong> (New)
- `pSrvHitFunc`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>5</code></strong> (New)
- `HitSubMissile1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>thunderstormnova</code></strong> (New)
- `CltHitSubMissile1`: <strong><code>empty</code></strong> (Old) &rarr; <strong><code>thunderstormnova</code></strong> (New)
### tornado
- `Vel`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
- `MaxVel`: <strong><code>8</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
- `NextDelay`: <strong><code>25</code></strong> (Old) &rarr; <strong><code>15</code></strong> (New)
### towerchestspawner
- `Range`: <strong><code>400 +  (lvl *  1)</code></strong> (Old) &rarr; <strong><code>400</code></strong> (New)
### towermistfade
- `Range`: <strong><code>128 +  (lvl *  1)</code></strong> (Old) &rarr; <strong><code>128</code></strong> (New)
### twister
- `Vel`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
- `MaxVel`: <strong><code>10</code></strong> (Old) &rarr; <strong><code>20</code></strong> (New)
- `AnimSpeed`: <strong><code>16</code></strong> (Old) &rarr; <strong><code>8</code></strong> (New)
### vines trail
- `Range`: <strong><code>100 +  (lvl *  25)</code></strong> (Old) &rarr; <strong><code>100</code></strong> (New)
### wake of destruction maker
- `Range`: <strong><code>25 +  (lvl *  2)</code></strong> (Old) &rarr; <strong><code>25</code></strong> (New)
### whitelightmissile
- `Range`: <strong><code>10 +  (lvl *  10)</code></strong> (Old) &rarr; <strong><code>10</code></strong> (New)
