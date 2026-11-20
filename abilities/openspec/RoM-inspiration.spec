# Abilities inspired by A RimWorld of Magic

## Purpose

This spec describes 27 combat and support abilities for AllBambaArmors, inspired by the ones in *A RimWorld of Magic* by Torann. It covers what each ability does in game. Which armor or pawn gets which ability is in [`../ABILITY_MAP.md`](../ABILITY_MAP.md).

The starting numbers follow the original mod's base rank. Where the original has ranks (I to III), the scaling is listed. They are a starting balance, not fixed requirements.

Energy costs are a percentage of the caster's energy pool. The original uses mana or stamina; see [Open questions](#open-questions).

Status: 25 of the 27 are built on Vanilla Expanded Framework, 1.7 only, with new in-game names. Beyond Our Reach holds 22 of them, for its own armor. Shield was folded into Shield Other, which can also target the caster, and Advanced Heal covers Heal.

## Ability summary

| Ability | Target | Range | Cast time | Cooldown | Cost | Original cost to run |
|---|---|---|---|---|---|---|
| Shield | self | - | 0.2 s | 35 s | 30% | on cast |
| Shield Other | pawn (incl. self) | 30 | 0.2 s | 20 s | 25% | on cast |
| Psionic Barrier | self (channel) | - | 0.5 s | 20 s | 10% | while channeling |
| Heal | pawn (incl. self) | 12 | 0.3 s | 15 s | 20% | on cast |
| Advanced Heal | pawn (incl. self) | 25 | 2.5 s | 8 s | 28% | on cast |
| Regenerate | pawn (incl. self) | 30 | 2 s | 40 s | 40% | on cast |
| Medigel | pawn (incl. self), touch | 1 | 2 s | 10 s | 10% | on cast |
| Healing Circle | location | 30 | 4 s | 60 s | 60% | a few seconds |
| Cure Disease | pawn (incl. self) | 15 | 5 s | 60 s | 45% | on cast |
| Purify | pawn (incl. self) | 16 | 6 s | 600 s | 80% | on cast |
| Resurrection | corpse location | 6 | 10 s | 600 s | 100% | a few seconds |
| Bestow Might | pawn (incl. self) | 30 | 1 s | 60 s | 25% | on cast |
| Battle Hymn | self (toggle) | - | 1 s | 10 s | 20% + 9%/verse | while active |
| Techno-Bit | self (toggle) | - | 0.1 s | 60 s | 0% (per-action drain) | while active |
| Shadow Strike | pawn | 35 | 1.6 s | 60 s | 65% | on cast |
| Seismic Slash | location | 12 | 0.3 s | 30 s | 25% | on cast |
| Phase Strike | location | 30 | 0.3 s | 25 s | 30% | on cast |
| Anti-Armor | pawn or building | 45 | 1 s | 10 s | 30% | on cast |
| Chain Lightning | pawn or building | 50 | 0.5 s | 10 s | 40% | a few seconds |
| Psionic Blast | pawn or location | 28 | 2 s | 12 s | 15% | on cast |
| Psionic Storm | location | 36 | 0.2 s | 20 s | 30% | a few seconds |
| Ignite | location, radius 5 | 35 | 2 s | 60 s | 30% | on cast |
| EMP | location or thing | 35 | 1.3 s | 45 s | 20% | on cast |
| Sunfire | location | 50 | 3 s | 60 s | 65% | a few seconds |
| Holy Wrath | location | 45 | 2.5 s | 45 s | 50% | a few seconds |
| Explosion! | anything | 100 | 5 s | 1000 s | 100% | a few seconds |
| Create Light | location | 150 | 0.5 s | 30 s | 0% | on cast |

The last column says how long the original's version keeps doing work: once on cast, for a few seconds after, or the whole time it's switched on.

## Requirements

### Requirement: Shared casting rules

Every ability in this spec SHALL follow the same casting flow.

- The ability SHALL be unavailable while its cooldown is running, while the caster has less energy than its cost, or while the caster is downed, dead or in a mental state.
- Casting SHALL take the listed cast time, during which the caster stands still. Interrupting the cast (being downed, stunned, or ordered elsewhere) SHALL cancel it without spending energy or starting the cooldown.
- When the cast completes, the ability SHALL spend its cost and start its cooldown.
- The target SHALL be within the listed range. Abilities marked "line of sight" SHALL also need an unobstructed line to the target. Fogged cells SHALL never be valid targets.
- Abilities that deal damage SHALL count as violent: pawns incapable of violence cannot use them, and using them on non-hostiles SHALL anger that faction as normal attacks do.

#### Scenario: Cast interrupted
- **WHEN** a pawn starts casting Healing Circle and is stunned 2 s into the 4 s cast
- **THEN** the cast is cancelled, no energy is spent, and the cooldown does not start

#### Scenario: Not enough energy
- **WHEN** a pawn with 20% energy tries to cast Shield (cost 30%)
- **THEN** the ability is disabled with a reason tooltip and cannot be cast

### Requirement: Ability ranks

Abilities with ranks SHALL improve as the rank rises (I, II, III), as described in each ability's requirement. A higher rank SHALL replace the lower one; a pawn never has two ranks of the same ability.

#### Scenario: Rank up
- **WHEN** a pawn's Phase Strike goes from base to rank I
- **THEN** its range becomes 35, cast time 0.2 s and cooldown 23 s, and the base version is no longer on the command bar

## Defensive

### Requirement: Shield

The caster SHALL gain a personal damage shield that absorbs incoming damage for 50 s or until it has absorbed 100 damage, whichever comes first. Damage beyond what the shield can absorb SHALL pass through to the caster.

Ranks: absorbs 125 / 135 / 150; cooldown 30 / 27 / 25 s.

#### Scenario: Shield breaks
- **WHEN** a shielded pawn with 20 absorption left takes a 35-damage hit
- **THEN** 20 is absorbed, 15 reaches the pawn, and the shield disappears

#### Scenario: Shield expires
- **WHEN** 50 s pass without the shield absorbing 100 damage
- **THEN** the shield disappears

### Requirement: Shield Other

The caster SHALL place the same kind of damage shield on a target pawn (line of sight required). It SHALL last 60 s or until it has absorbed 80 damage, plus 0.5 damage per caster level. Recasting on a pawn that already has a shield SHALL add to its remaining absorption, up to a cap.

#### Scenario: Shield an ally
- **WHEN** a level-20 caster casts Shield Other on an ally 25 cells away with clear line of sight
- **THEN** the ally gains a shield that absorbs up to 90 damage for 60 s

### Requirement: Psionic Barrier

The caster SHALL channel a barrier of radius 2.5 around themselves (+0.75 per upgrade). While channeling:
- Projectiles fired from outside the barrier that enter it SHALL be deflected and destroyed. Explosive projectiles SHALL detonate at the barrier edge.
- Projectiles fired from inside the barrier SHALL pass normally.
- The caster SHALL be unable to do anything else; giving any order ends the barrier.
- Each deflected projectile SHALL drain the caster's energy.

The barrier SHALL end after 15 s, when the caster's energy drops below 1%, or when the caster is downed or ordered to do something else. A variant of the ability MAY project the barrier at a target location instead of on the caster.

#### Scenario: Deflecting a volley
- **WHEN** enemies 20 cells away shoot at a pawn channeling Psionic Barrier
- **THEN** each bullet is destroyed at the barrier edge, and the caster's energy drops per bullet

#### Scenario: Grenade on the barrier
- **WHEN** a frag grenade reaches the barrier
- **THEN** it explodes at the barrier edge, not at its target

## Healing

### Requirement: Heal

The caster SHALL instantly restore 8 HP to each of up to 3 injuries on the target (line of sight required). It SHALL NOT restore missing body parts.

#### Scenario: Multiple wounds
- **WHEN** Heal targets a pawn with 5 bleeding cuts
- **THEN** 3 of the cuts each heal by 8 HP; the other 2 are unchanged

### Requirement: Advanced Heal

The caster SHALL instantly restore 14 HP to each of up to 3 injuries on the target, and SHALL immediately stop bleeding from missing-body-part wounds. Line of sight is not required. It SHALL NOT restore missing body parts.

#### Scenario: Lost arm
- **WHEN** Advanced Heal targets a pawn bleeding from a severed arm
- **THEN** the bleeding stops and the arm stays missing

### Requirement: Regenerate

The target SHALL gain a regeneration buff that restores 4 HP to one injury every 5 s. The buff SHALL last roughly 2.5-7 in-game hours (the duration rolls on cast). It SHALL heal physical injuries only: no diseases, no missing body parts. Recasting SHALL extend the buff. Line of sight is not required.

#### Scenario: Long recovery
- **WHEN** a pawn with 40 HP of injuries is Regenerated and rests
- **THEN** one injury heals by 4 HP every 5 s until all injuries are healed or the buff ends

### Requirement: Medigel

The caster SHALL apply a gel to an adjacent target, giving a buff that lasts about 6 in-game hours and:
- speeds up wound healing,
- slows infection progress on infected wounds,
- reduces pain by 20%.

#### Scenario: Infection risk
- **WHEN** Medigel is applied to a pawn with a fresh, untended wound
- **THEN** the wound heals faster and its infection chance is reduced while the buff lasts

### Requirement: Healing Circle

The caster SHALL create a circle of light (radius 3) at the target location for 20 s. While it lasts, it SHALL repeatedly pulse, and each pulse SHALL heal one injury by 10 HP on every eligible pawn standing inside. Eligible pawns are the caster's faction, prisoners, factionless pawns, and any pawn not hostile to the caster. It SHALL NOT restore missing body parts.

Ranks: radius 4 / 5.5 / 7; range 35 / 40 / 45. Upgrades extend the duration by 3 s each.

#### Scenario: Hostile inside the circle
- **WHEN** a raider and a colonist both stand in an active Healing Circle
- **THEN** only the colonist is healed

### Requirement: Cure Disease

The caster SHALL attempt to remove one disease from the target per cast. At base rank the attempt SHALL succeed 75% of the time; on failure, nothing is removed and a failure message is shown.

What can be cured depends on upgrades:

| Level | Removable conditions |
|---|---|
| Base | Wound infections, flu (incl. animal flu), plague |
| +1 | Gut worms, malaria, food poisoning |
| +2 | Sleeping sickness, muscle parasites |
| +3 | Any other bad sickness except abasia; blood rot is tended instead of removed |

At higher power upgrades, the target SHALL also gain temporary disease immunity.

#### Scenario: Two diseases
- **WHEN** a pawn has both flu and an infection and is cured successfully
- **THEN** exactly one of them is removed; a second cast is needed for the other

#### Scenario: Not curable yet
- **WHEN** a base-rank caster targets a pawn whose only disease is malaria
- **THEN** the cast fails with a "cannot cure this disease" message and malaria stays

### Requirement: Purify

The caster SHALL heal long-term conditions on the target (line of sight required). Each cast SHALL fix a limited number of conditions (1 at base, more with upgrades), chosen in this order:
1. Scars and permanent injuries: each fixed scar heals by 2 HP (+2 per upgrade). Brain scars need at least one power upgrade.
2. Chronic illnesses: reduces cataracts, hearing loss, toxic buildup, blindness, asthma (removed outright), cirrhosis, frailty, bad back, carcinoma, dementia, Alzheimer's and artery blockage. Each cast reduces severity; it does not always cure in one cast.
3. Addictions: reduces alcohol and smokeleaf addiction; go-juice and wake-up with upgrades; luciferium at higher levels.

#### Scenario: Old soldier
- **WHEN** Purify targets a pawn with a scarred leg and a bad back, at base rank
- **THEN** only the scar is reduced this cast, and the bad back is left for a later cast

### Requirement: Resurrection

The caster SHALL target a cell holding a recently dead humanlike corpse within 6 cells. After the 10 s cast, a 20 s ritual SHALL begin at that spot. When it finishes:
- the corpse SHALL be brought back to life,
- the revived pawn SHALL get a "resurrected" weakness for several days (+50-100% hunger and rest need, −20 to −40% moving and manipulation, worse mental break threshold),
- the revived pawn SHALL lose up to 35% of their skill levels and MAY gain lasting bad health conditions (e.g. resurrection psychosis; upgrades lower the chance),
- the caster SHALL also be weakened for several days,
- a holy shockwave (radius 10-16) SHALL hit undead in the area.

A corpse that is too decayed SHALL make the cast fail with a message.

#### Scenario: Dead colonist
- **WHEN** Resurrection targets a colonist who died 2 hours ago
- **THEN** after 30 s total the colonist is alive, weakened, and has lost some skill levels

#### Scenario: Rotten corpse
- **WHEN** the target corpse is rotten
- **THEN** the ritual is refused with a "target expired" message

## Buffs and support

### Requirement: Bestow Might

The target SHALL gain a 30-40 s combat buff: +40% moving and manipulation, +10% consciousness and blood pumping, −50% pain, +10 melee dodge, faster aiming, and higher mental break resistance. It SHALL also make the target 20% hungrier and 50% more tired while it lasts. Line of sight is not required.

Ranks: 50-60 s at +60%; 50-60 s at +80%; 100-115 s at about +100% (pain reduction scales up to −70%).

#### Scenario: Buff a melee fighter
- **WHEN** Bestow Might is cast on an ally before a melee charge
- **THEN** the ally moves and attacks faster and ignores more pain for the next 30-40 s

### Requirement: Battle Hymn

Battle Hymn SHALL be a toggle. Casting it SHALL start the hymn; casting again SHALL stop it. While active:
- Every 5 s (one "verse"), each humanlike pawn of the caster's faction within 15 cells SHALL gain a stack of the Battle Hymn buff. Upgrades: radius +3 each, verse interval −0.5 s each.
- The buff SHALL stack through 4+ stages. Per stage: +10/15/20/25% moving, manipulation and blood pumping; −30/40/50/53% pain; +3/5/7/9 dodge; faster aiming; slower fatigue. It SHALL fade quickly once verses stop.
- Each verse SHALL cost 9% energy (upgrades reduce it). If the caster can't pay, the hymn SHALL stop.
- Each ally hit by a verse SHALL have a 4% chance to gain a combat inspiration.

#### Scenario: Out of energy
- **WHEN** the caster has 5% energy at the next verse
- **THEN** the hymn stops and no buff is applied

#### Scenario: Ally walks out of range
- **WHEN** an ally leaves the 15-cell radius
- **THEN** they stop getting new stacks and their buff fades on its own

### Requirement: Techno-Bit

Techno-Bit SHALL be a toggle that summons a small floating orb next to the caster. While it's on:
- Undrafted, crafting or building: when the caster works within 2 cells of the work target and has ≥90% energy, the orb SHALL boost the caster's manipulation (+50% to +80% by rank) for a short time, about every 10 s.
- Repair: the orb SHALL repair nearby damaged buildings and mechanical pawns by 8-12 HP: about every 2.7 s while drafted, every 10 s while undrafted. This part can be toggled separately.
- Drafted and attacking: while the caster aims at a target in line of sight and has ≥10% energy, the orb SHALL fire micro-lasers at that target, with a periodic heavier burst (about every 3 s).
- Each orb action SHALL drain a small amount of energy.

#### Scenario: Combat support
- **WHEN** a drafted caster with the orb on shoots at a raider 20 cells away
- **THEN** the orb also fires lasers at that raider

## Melee and mobility

### Requirement: Shadow Strike

The caster SHALL vanish and reappear behind the target pawn (line of sight required), then:
- hit it 4 times with stab damage based on their weapon; each hit has a chance to crit for 3× damage (lower with heavier weapons, never with ranged weapons),
- gain 5 s of haste (double attack speed),
- become invisible for 2-3 s,
- release a short-lived smoke cloud (radius 2) that poisons nearby enemies with a toxin.

After 5 s, the caster SHALL be returned to where the attack started.

#### Scenario: Assassination
- **WHEN** Shadow Strike targets a sniper behind cover 30 cells away
- **THEN** the caster appears behind the sniper, strikes 4 times, and is back at the starting point 5 s later

### Requirement: Seismic Slash

The caster SHALL need a melee weapon equipped; otherwise the cast SHALL be refused with "must have a melee weapon". The slash SHALL travel in a straight line from the caster to the target cell (line of sight required). Each pawn on the line, or on 2 cells beside it, that is not of the caster's faction SHALL take cut damage of about 70% of the caster's melee damage output (±30%, +10% per upgrade). Upgrades widen the line.

#### Scenario: Line of enemies
- **WHEN** three raiders stand in a row toward the target cell
- **THEN** all three take cut damage

#### Scenario: Neutral in the path
- **WHEN** a visiting trader stands on the slash line
- **THEN** the trader is hit as well, since they are not of the caster's faction

### Requirement: Phase Strike

The caster SHALL need a melee weapon. The caster SHALL teleport to the target cell (line of sight not required) and strike every pawn not of the caster's faction within 2 cells (+0.5 per upgrade). Each hit SHALL deal 50-150% of the caster's weapon damage, with a 10% (+15% per upgrade) chance to crit for 3×.

Ranks: range 35 / 40 / 45; cast time 0.2 / 0.1 / 0 s; cooldown 23 / 21 / 20 s.

#### Scenario: Behind a wall
- **WHEN** the target cell is behind a wall, 25 cells away
- **THEN** the caster appears there and hits everyone in the radius

## Ranged attacks

### Requirement: Anti-Armor

The caster SHALL fire a special round at a pawn or building. Whether it hits SHALL use the caster's shooting accuracy.
- Against armored targets (any mechanoid, any non-flesh pawn, or a pawn with overall sharp armor above 100%): heavy armor-piercing damage, plus a bonus that grows with power upgrades, a short chain of small explosions with stun, and 50-150 HP of damage to each of up to 4 worn apparel pieces.
- Against soft targets: normal weapon damage only.

Base damage SHALL be capped at 60.

#### Scenario: Centipede
- **WHEN** Anti-Armor hits a centipede
- **THEN** it takes bonus damage and is briefly stunned by follow-up blasts

#### Scenario: Unarmored raider
- **WHEN** it hits a raider in a parka
- **THEN** the raider takes only regular weapon damage

### Requirement: Chain Lightning

The caster SHALL strike the target pawn or building with lightning. The bolt SHALL then jump in waves: each struck point forks up to 2 times to a random pawn or building within about 4 cells further in the bolt's direction, for 4 waves in total (+1 per upgrade). Rules:
- The same thing SHALL never be hit twice by one cast.
- Damage SHALL drop with each wave. Buildings that belong to a faction SHALL take double damage.
- Each wave also throws 1-3 small stray bolts that explode for minor damage nearby.
- The chain SHALL stop early if the caster is downed or dies.
- Forks SHALL pick targets regardless of faction, so allies can be hit.

#### Scenario: Packed raiders
- **WHEN** Chain Lightning hits the first of five raiders standing close together
- **THEN** the bolt jumps through several of them in waves, each taking less damage than the last

#### Scenario: Friendly fire
- **WHEN** a colonist is standing in melee with the target
- **THEN** the colonist can be picked by a fork and hit

### Requirement: Psionic Blast

The caster SHALL fire a burst of psionic bolts at a pawn or location. Each bolt SHALL land with spread that grows with distance and explode in radius 2 for 12 psionic damage. The first bolt is always fired. Up to 4 more SHALL follow, each one using extra psionic energy and only if enough remains.

Ranks: range 34 / 40 / 46; cast time 1.6 / 1.2 / 0.8 s; cooldown 10 / 8 / 6 s.

#### Scenario: Low psionic energy
- **WHEN** the caster has almost no psionic energy left
- **THEN** only the first bolt is fired

### Requirement: Psionic Storm

The caster SHALL launch into the air and circle the target area (about 10 cells across) in several passes. During the passes they SHALL repeatedly fire psionic bolts down at the area every 10-40 ticks (faster with upgrades), then land at the target. Afterward the caster SHALL be exhausted: unable to use psionic abilities for a while.

#### Scenario: After the storm
- **WHEN** the storm finishes
- **THEN** the caster lands and their psionic abilities are disabled until the exhaustion wears off

## Area attacks

### Requirement: Ignite

The caster SHALL release a burst of heat at the target cell (line of sight required, radius 5):
- a large amount of heat SHALL be added to the room or area (more if the caster has a fire-related trait),
- non-mechanoid pawns in the radius SHALL catch fire, with a chance that drops with distance from the center (resisted by the target's magic resistance),
- corpses in the radius SHALL always catch fire,
- plants SHALL catch fire with a distance-based chance (trees half as likely),
- snow in the radius SHALL melt, producing smoke.

Ignite SHALL affect friend and foe alike.

#### Scenario: Indoors
- **WHEN** Ignite is cast inside a closed room
- **THEN** the room's temperature jumps sharply, on top of any fires

### Requirement: EMP

The caster SHALL fire an EMP that bursts in radius 7 for 100 EMP damage. It SHALL stun mechanoids and disable shields, turrets and other electrical devices, as vanilla EMP does. With the relevant upgrade, each mechanical pawn hit SHALL have a 40% chance to also be sabotaged (malfunction or shutdown).

#### Scenario: Mech cluster
- **WHEN** EMP hits a group of scythers
- **THEN** they are stunned for the vanilla EMP duration

### Requirement: Sunfire

The caster SHALL rain 13 burning beams of light across the target area (radius 5) over about 10 s. Each beam SHALL sweep a short path and burn pawns it crosses (burning-light damage) and deal 4× damage to buildings, with a 2% chance per hit to start a fire. If the caster has stored light energy, the cast SHALL use 25 of it to empower the beams.

Ranks: radius 6 / 7 / 8; beams 14 / 15 / 16; range 55 / 60 / 65; cooldown 55 / 50 / 45 s.

#### Scenario: Entrenched raiders
- **WHEN** Sunfire is cast on raiders behind sandbags
- **THEN** beams sweep the area for ~10 s, burning the raiders and damaging the sandbags

### Requirement: Holy Wrath

The caster SHALL mark an area (radius 6) at the target location. After a 6 s delay, a series of holy strikes SHALL land across the area:
- each strike explodes (radius 3), damaging and stunning enemies,
- undead in the area take extra holy damage,
- pawns of the caster's faction inside the area SHALL instead become briefly invulnerable, have injuries healed, and gain Bestow Might.

#### Scenario: Mixed fight
- **WHEN** colonists and raiders melee inside the marked area when it fires
- **THEN** raiders take strike damage while colonists become invulnerable, healed and buffed

#### Scenario: Enemies walk out
- **WHEN** raiders leave the marked area during the 6 s delay
- **THEN** they are not hit

### Requirement: Explosion!

The caster SHALL call down one massive explosion. After the 5 s cast, a 6 s sequence SHALL play at the target: magic rings form, then a blast expands outward to radius 12 with repeated bomb explosions, flame damage and a large heat spike. Base damage is 50 per blast, scaled by the caster's power. It SHALL hit everything in the radius, including allies and the caster's own buildings. Cost: the full energy pool. Cooldown: 1000 s (~17 minutes).

#### Scenario: Last resort
- **WHEN** Explosion! is cast on a siege camp 80 cells away
- **THEN** after 11 s total the camp is engulfed in a radius-12 blast

#### Scenario: Allies too close
- **WHEN** a colonist is 8 cells from the target
- **THEN** the colonist takes blast damage too

### Requirement: Create Light

The caster SHALL create a lasting light source at the target location (any distance up to 150, no line of sight needed). It SHALL stay until the caster casts Create Light again at any location, which dismisses it. While the light exists, the caster's light energy SHALL regenerate 70% slower. In the original this light comes from a "Spirit of Light" companion (see [Open questions](#open-questions)).

#### Scenario: Night farming
- **WHEN** Create Light is cast over a field at night
- **THEN** the field stays lit until the light is dismissed

## Open questions

Some of the original's behavior depends on systems this mod doesn't have. Each needs a decision:

1. **Energy resource.** The original splits costs between mana (magic abilities) and stamina (fighter abilities: Shadow Strike, Seismic Slash, Phase Strike, Anti-Armor, Medigel, the psionic abilities). Use one shared pool, two pools, or something else?
2. **Psionic energy.** Psionic Blast extra bolts, Psionic Barrier upkeep and Psionic Storm exhaustion use a separate psionic energy pool. Keep it, or fold it into the main pool?
3. **Light energy.** Sunfire's empowerment and Create Light depend on stored light and the Spirit of Light companion (not in this spec). Drop the dependency, or add a light resource?
4. **Weapon-based damage.** Shadow Strike, Seismic Slash, Phase Strike and Anti-Armor scale off the caster's weapon damage and a fighter "power" stat. Decide the formula without the original's level system.
5. **Upgrades.** Many values scale with "upgrades" (the original's power/versatility/efficiency skill points). Decide whether to keep a point system, tie it to apparel quality, or fix the values.
6. **Friendly fire.** Chain Lightning, Ignite and Explosion! hit allies, and Seismic/Phase Strike hit neutrals. Keep that as a balancing cost, or filter it out?

## Implementation notes (performance)

The original is slow in a few places. Do these differently:

- **Chain Lightning** and **Ignite** search every thing on the map to find targets. Use a radius lookup around the impact cell instead.
- **Battle Hymn** loops every pawn on the map each verse. Loop only the caster's faction pawns within range.
- **Psionic Barrier** scans its cells every tick while channeling. Scanning every 2-3 ticks is enough to catch projectiles.
- **Sunfire, Healing Circle, Holy Wrath, Explosion!** are multi-second effects with heavy visual effects; keep the per-tick work small and act on intervals.
