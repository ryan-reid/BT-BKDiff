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
- `Range`: <code>6</code><del><code> +  (lvl *  2)</code></del> (Old) &rarr; <code>6</code> (New)
### baal taunt lightning
- `Range`: <code>10</code><del><code> +  (lvl *  2)</code></del> (Old) &rarr; <code>10</code> (New)
### battlecry
- `Vel`: <del><code>12</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
- `MaxVel`: <del><code>12</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
- `Accel`: <del><code>-1000</code></del> (Old) &rarr; <ins><code>-500</code></ins> (New)
- `Range`: <del><code>12</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
### blade creeper
- `Range`: <code>10</code><del><code> +  (lvl *  5)</code></del> (Old) &rarr; <code>10</code> (New)
- `NextDelay`: <del><code>25</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
### blade shield attachment
- `Range`: <code>500</code><del><code> +  (lvl *  100)</code></del> (Old) &rarr; <code>500</code> (New)
### blaze
- `Range`: <code>90</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>90</code> (New)
### bluelightmissile
- `Range`: <code>10</code><del><code> +  (lvl *  10)</code></del> (Old) &rarr; <code>10</code> (New)
### bonespirit
- `Vel`: <del><code>12</code></del> (Old) &rarr; <ins><code>16</code></ins> (New)
- `MaxVel`: <del><code>12</code></del> (Old) &rarr; <ins><code>16</code></ins> (New)
### bonewallmaker
- `Range`: <code>7</code><del><code> +  (lvl *  2)</code></del> (Old) &rarr; <code>7</code> (New)
### catapult meteor fire
- `Range`: <code>90</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>90</code> (New)
### coldarrow
- `pCltHitFunc`:  (Old) &rarr; <ins><code>4</code></ins> (New)
- `pSrvHitFunc`:  (Old) &rarr; <ins><code>5</code></ins> (New)
- `sHitPar1`:  (Old) &rarr; <ins><code>1</code></ins> (New)
- `HitSubMissile1`:  (Old) &rarr; <ins><code>frostnovaarrow</code></ins> (New)
- `CltHitSubMissile1`:  (Old) &rarr; <ins><code>frostnovaarrow</code></ins> (New)
### coldfissure center
- `\*ID`: <del><code>726</code></del> (Old) &rarr; <ins><code>725</code></ins> (New)
### colossal throwing axe
- `\*ID`: <del><code>732</code></del> (Old) &rarr; <ins><code>731</code></ins> (New)
### colossalchargedbolt
- `\*ID`: <del><code>723</code></del> (Old) &rarr; <ins><code>735</code></ins> (New)
### countessfirewall
- `Range`: <code>1000</code><del><code> +  (lvl *  1)</code></del> (Old) &rarr; <code>1000</code> (New)
### distraction fog
- `Range`: <code>10</code><del><code> +  (lvl *  5)</code></del> (Old) &rarr; <code>10</code> (New)
### explodingarrowexp2
- `sHitPar1`: <del><code>5</code></del> (Old) &rarr; <ins><code>7</code></ins> (New)
### firearrow
- `pCltHitFunc`:  (Old) &rarr; <ins><code>4</code></ins> (New)
- `pSrvHitFunc`:  (Old) &rarr; <ins><code>5</code></ins> (New)
- `sHitPar1`:  (Old) &rarr; <ins><code>1</code></ins> (New)
- `HitSubMissile1`:  (Old) &rarr; <ins><code>firenovaarrow</code></ins> (New)
- `CltHitSubMissile1`:  (Old) &rarr; <ins><code>firenovaarrow</code></ins> (New)
### fireball
- `sHitPar1`: <del><code>0</code></del> (Old) &rarr; <ins><code>4</code></ins> (New)
### firemedium
- `Range`: <code>90</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>90</code> (New)
### firesmall
- `Range`: <code>90</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>90</code> (New)
### firetwister
- `\*ID`: <del><code>720</code></del> (Old) &rarr; <ins><code>732</code></ins> (New)
### firewallmaker
- `Range`: <code>7</code><del><code> +  (lvl *  2)</code></del> (Old) &rarr; <code>7</code> (New)
### fistoftheheavensbolt
- `sHitPar2`: <del><code>3</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `cHitPar1`: <del><code>1</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `cHitPar2`: <del><code>3</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `EDmgSymPerCalc`: <code>skill('Holy Bolt'.blvl) *</code><del><code> 15</code></del> (Old) &rarr; <code>skill('Holy Bolt'.blvl) *</code><ins><code>6</code></ins> (New)
### frozenorb
- `Vel`: <del><code>10</code></del> (Old) &rarr; <ins><code>16</code></ins> (New)
- `MaxVel`: <del><code>10</code></del> (Old) &rarr; <ins><code>16</code></ins> (New)
### frozenorbbolt
- `Vel`: <del><code>18</code></del> (Old) &rarr; <ins><code>16</code></ins> (New)
- `MaxVel`: <del><code>18</code></del> (Old) &rarr; <ins><code>16</code></ins> (New)
### frozenorbnova
- `Vel`: <del><code>24</code></del> (Old) &rarr; <ins><code>30</code></ins> (New)
- `MaxVel`: <del><code>24</code></del> (Old) &rarr; <ins><code>30</code></ins> (New)
### greenlightmissile
- `Range`: <code>10</code><del><code> +  (lvl *  10)</code></del> (Old) &rarr; <code>10</code> (New)
### grimwardscare
- `Range`: <code>24</code><del><code> +  (lvl *  12)</code></del> (Old) &rarr; <code>24</code> (New)
### guidedarrow
- `Pierce`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### healing vortex
- `Range`: <code>100</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>100</code> (New)
### holybolt
- `sHitPar1`: <del><code>1</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `sHitPar2`: <del><code>3</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `cHitPar1`: <del><code>1</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
- `cHitPar2`: <del><code>3</code></del> (Old) &rarr; <ins><code>0</code></ins> (New)
### hydra
- `Vel`: <del><code>16</code></del> (Old) &rarr; <ins><code>40</code></ins> (New)
- `MaxVel`: <del><code>16</code></del> (Old) &rarr; <ins><code>40</code></ins> (New)
### ice crack 1
- `\*ID`: <del><code>727</code></del> (Old) &rarr; <ins><code>726</code></ins> (New)
### ice crack 2
- `\*ID`: <del><code>728</code></del> (Old) &rarr; <ins><code>727</code></ins> (New)
### ice vapor 1
- `\*ID`: <del><code>729</code></del> (Old) &rarr; <ins><code>728</code></ins> (New)
### ice vapor 2
- `\*ID`: <del><code>730</code></del> (Old) &rarr; <ins><code>729</code></ins> (New)
### iceblast
- `Vel`: <del><code>12</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
- `MaxVel`: <del><code>12</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
### immolationfire
- `EMin`: <del><code>12</code></del> (Old) &rarr; <ins><code>24</code></ins> (New)
- `MinELev1`: <del><code>4</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
- `MinELev2`: <del><code>5</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `MinELev3`: <del><code>6</code></del> (Old) &rarr; <ins><code>12</code></ins> (New)
- `MinELev4`: <del><code>6</code></del> (Old) &rarr; <ins><code>12</code></ins> (New)
- `MinELev5`: <del><code>6</code></del> (Old) &rarr; <ins><code>12</code></ins> (New)
- `EMax`: <del><code>24</code></del> (Old) &rarr; <ins><code>48</code></ins> (New)
- `MaxELev1`: <del><code>4</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
- `MaxELev2`: <del><code>5</code></del> (Old) &rarr; <ins><code>10</code></ins> (New)
- `MaxELev3`: <del><code>7</code></del> (Old) &rarr; <ins><code>14</code></ins> (New)
- `MaxELev4`: <del><code>7</code></del> (Old) &rarr; <ins><code>14</code></ins> (New)
- `MaxELev5`: <del><code>7</code></del> (Old) &rarr; <ins><code>14</code></ins> (New)
- `EDmgSymPerCalc`: <code>skill('Fire Arrow'.blvl)</code><code> * 5</code> (Old) &rarr; <ins><code>(</code></ins><code>skill('Fire Arrow'.blvl)</code><ins><code>+skill('Exploding Arrow'.blvl))</code></ins><code> * 5</code> (New)
### mephistoflyingrocksbig
- `Range`: <code>10</code><del><code> +  (lvl *  3)</code></del> (Old) &rarr; <code>10</code> (New)
### mephistoflyingrockssmall
- `Range`: <code>5</code><del><code> +  (lvl *  3)</code></del> (Old) &rarr; <code>5</code> (New)
### meteor
- `Range`: <del><code>60</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
### meteorcenter
- `CltParam1`: <del><code>59</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
- `Range`: <del><code>60</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
### meteorexplode
- `Range`: <del><code>16</code></del> (Old) &rarr; <ins><code>13</code></ins> (New)
### meteortail
- `Range`: <del><code>60</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
### monblizcenter
- `Range`: <code>25</code><del><code> +  (lvl *  15)</code></del> (Old) &rarr; <code>25</code> (New)
### multipleshotarrow
- `Range`: <del><code>50</code></del> (Old) &rarr; <ins><code>27</code></ins> (New)
### multipleshotbolt
- `Range`: <del><code>50</code></del> (Old) &rarr; <ins><code>27</code></ins> (New)
### phoenixtrail
- `Range`: <code>90</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>90</code> (New)
### plague vines trail
- `Range`: <code>100</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>100</code> (New)
### poisonnova
- `Vel`: <del><code>12</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
- `MaxVel`: <del><code>12</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
### rabiesplague
- `Param1`: <del><code>4</code></del> (Old) &rarr; <ins><code>1</code></ins> (New)
- `Param2`: <del><code>7</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
- `Range`: <code>10</code><del><code> +  (lvl *  5)</code></del> (Old) &rarr; <code>10</code> (New)
### redlightmissile
- `Range`: <code>10</code><del><code> +  (lvl *  10)</code></del> (Old) &rarr; <code>10</code> (New)
### ringoffireexplode
- `\*ID`: <del><code>731</code></del> (Old) &rarr; <ins><code>730</code></ins> (New)
### royalstrikechainlightning
- `pCltHitFunc`:  (Old) &rarr; <ins><code>*16</code></ins> (New)
- `pSrvHitFunc`:  (Old) &rarr; <ins><code>*12</code></ins> (New)
### royalstrikemeteor
- `Range`: <del><code>60</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
### royalstrikemeteorcenter
- `CltParam1`: <del><code>59</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
- `Range`: <del><code>60</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
- `ProgSound`:  (Old) &rarr; <ins><code>sorceress_meteor_impact</code></ins> (New)
### royalstrikemeteorexplode
- `Range`: <del><code>16</code></del> (Old) &rarr; <ins><code>13</code></ins> (New)
### royalstrikemeteortail
- `Range`: <del><code>60</code></del> (Old) &rarr; <ins><code>18</code></ins> (New)
### sentrylightningbolt
- `Range`: <code>10</code><del><code> +  (lvl *  2)</code></del> (Old) &rarr; <code>10</code> (New)
### sentrylightningbolt2
- `Range`: <code>10</code><del><code> +  (lvl *  2)</code></del> (Old) &rarr; <code>10</code> (New)
### sentryspikeonground
- `Range`: <code>180</code><del><code> +  (lvl *  60)</code></del> (Old) &rarr; <code>180</code> (New)
### shockwave
- `NextHit`: <del><code>1</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `NextDelay`: <del><code>4</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
### taintedfireball
- `\*ID`: <del><code>722</code></del> (Old) &rarr; <ins><code>734</code></ins> (New)
### taintedfirebolt
- `\*ID`: <del><code>721</code></del> (Old) &rarr; <ins><code>733</code></ins> (New)
### teeth
- `NextDelay`: <del><code>4</code></del> (Old) &rarr; <ins><code>(removed)</code></ins> (New)
- `Pierce`:  (Old) &rarr; <ins><code>1</code></ins> (New)
### throwingstar
- `Range`: <code>100</code><del><code> +  (lvl *  50)</code></del> (Old) &rarr; <code>100</code> (New)
### thunderstorm1
- `pCltHitFunc`:  (Old) &rarr; <ins><code>4</code></ins> (New)
- `pSrvHitFunc`:  (Old) &rarr; <ins><code>5</code></ins> (New)
- `HitSubMissile1`:  (Old) &rarr; <ins><code>thunderstormnova</code></ins> (New)
- `CltHitSubMissile1`:  (Old) &rarr; <ins><code>thunderstormnova</code></ins> (New)
### tornado
- `Vel`: <del><code>8</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
- `MaxVel`: <del><code>8</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
- `NextDelay`: <del><code>25</code></del> (Old) &rarr; <ins><code>15</code></ins> (New)
### towerchestspawner
- `Range`: <code>400</code><del><code> +  (lvl *  1)</code></del> (Old) &rarr; <code>400</code> (New)
### towermistfade
- `Range`: <code>128</code><del><code> +  (lvl *  1)</code></del> (Old) &rarr; <code>128</code> (New)
### twister
- `Vel`: <del><code>10</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
- `MaxVel`: <del><code>10</code></del> (Old) &rarr; <ins><code>20</code></ins> (New)
- `AnimSpeed`: <del><code>16</code></del> (Old) &rarr; <ins><code>8</code></ins> (New)
### vines trail
- `Range`: <code>100</code><del><code> +  (lvl *  25)</code></del> (Old) &rarr; <code>100</code> (New)
### wake of destruction maker
- `Range`: <code>25</code><del><code> +  (lvl *  2)</code></del> (Old) &rarr; <code>25</code> (New)
### whitelightmissile
- `Range`: <code>10</code><del><code> +  (lvl *  10)</code></del> (Old) &rarr; <code>10</code> (New)
