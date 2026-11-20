using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace AllBambaArmors
{
    /// <summary>Helpers shared by every ability in the mod: healing, ally checks, weapon damage, teleport and visuals.</summary>
    public static class AbilityUtility
    {
        private static List<Hediff_Injury> tmpInjuries = new List<Hediff_Injury>();
        private static readonly List<Pawn> tmpPawns = new List<Pawn>();

        // ---- Healing ----

        /// <summary>Heals up to <paramref name="count"/> of the worst healable injuries by <paramref name="amount"/> each. Missing parts are never restored.</summary>
        public static int HealInjuries(Pawn pawn, int count, float amount)
        {
            if (pawn?.health?.hediffSet == null || count <= 0)
                return 0;

            tmpInjuries.Clear();
            pawn.health.hediffSet.GetHediffs(ref tmpInjuries, h => !h.IsPermanent() && h.Severity > 0f);
            tmpInjuries.SortByDescending(h => h.Severity);

            var healed = Mathf.Min(count, tmpInjuries.Count);
            for (var i = 0; i < healed; i++)
                tmpInjuries[i].Heal(amount);

            tmpInjuries.Clear();
            if (healed > 0 && pawn.Spawned)
                FleckMaker.ThrowMetaIcon(pawn.Position, pawn.Map, FleckDefOf.HealingCross);
            return healed;
        }

        public static bool HasHealableInjury(Pawn pawn) =>
            pawn?.health?.hediffSet?.hediffs.Any(h => h is Hediff_Injury injury && !injury.IsPermanent()) ?? false;

        /// <summary>Stops bleeding from fresh missing-part wounds. The parts stay missing.</summary>
        public static int StopMissingPartBleeding(Pawn pawn)
        {
            var stopped = 0;
            foreach (var hediff in pawn.health.hediffSet.hediffs)
            {
                if (hediff is Hediff_MissingPart missing && missing.IsFresh)
                {
                    missing.IsFresh = false;
                    stopped++;
                }
            }

            if (stopped > 0)
                pawn.health.Notify_HediffChanged(null);
            return stopped;
        }

        public static bool HasBleedingMissingPart(Pawn pawn) =>
            pawn.health.hediffSet.hediffs.Any(h => h is Hediff_MissingPart missing && missing.IsFresh && missing.BleedRate > 0f);

        // ---- Who counts as a friend ----

        /// <summary>Caster's faction, prisoners, factionless pawns and anyone not hostile to the caster.</summary>
        public static bool IsFriendly(Pawn caster, Pawn other)
        {
            if (other == caster)
                return true;
            if (other.Faction == null || other.Faction == caster.Faction)
                return true;
            if (other.IsPrisonerOfColony && caster.Faction == Faction.OfPlayer)
                return true;
            return !other.HostileTo(caster);
        }

        /// <summary>Spawned pawns within <paramref name="radius"/> of <paramref name="center"/>. The returned list is reused; copy it before calling again.</summary>
        public static List<Pawn> PawnsInRadius(IntVec3 center, Map map, float radius)
        {
            tmpPawns.Clear();
            foreach (var thing in GenRadial.RadialDistinctThingsAround(center, map, radius, true))
            {
                if (thing is Pawn pawn && pawn.Spawned && !pawn.Dead)
                    tmpPawns.Add(pawn);
            }
            return tmpPawns;
        }

        // ---- Combat Extended ----

        /// <summary>CE measures sharp penetration in mm against armor in mm, so fixed vanilla-scale values (0-2) bounce off.</summary>
        public static readonly bool CombatExtendedActive = ModsConfig.IsActive("CETeam.CombatExtended");

        /// <summary>
        /// Sharp penetration of a projectile: CE's own armorPenetrationSharp field when CE is loaded
        /// (read by reflection so the mod has no CE dependency), else the vanilla value.
        /// </summary>
        public static float ProjectileSharpPenetration(ThingDef projectile, Thing weapon)
        {
            var props = projectile?.projectile;
            if (props == null)
                return 0f;

            if (CombatExtendedActive && props.GetType().GetField("armorPenetrationSharp") is { } field && field.GetValue(props) is float sharp)
                return sharp;

            return props.GetArmorPenetration(weapon);
        }

        // ---- Weapons ----

        public static bool HasMeleeWeapon(Pawn pawn) => pawn.equipment?.Primary is { } weapon && weapon.def.IsMeleeWeapon;

        public static bool HasRangedWeapon(Pawn pawn) => pawn.equipment?.Primary is { } weapon && weapon.def.IsRangedWeapon;

        /// <summary>The caster's strongest melee hit: from the equipped weapon's melee tools, or the pawn's own attacks when unarmed.</summary>
        public static MeleeHit BestMeleeHit(Pawn pawn)
        {
            var best = new MeleeHit { amount = 5f, damageDef = DamageDefOf.Blunt, armorPenetration = 0f };
            var verbs = pawn.equipment?.Primary?.GetComp<CompEquippable>()?.AllVerbs ?? pawn.meleeVerbs?.GetUpdatedAvailableVerbsList(false).Select(v => v.verb).ToList();
            if (verbs == null)
                return best;

            var found = false;
            foreach (var verb in verbs)
            {
                if (!verb.IsMeleeAttack || verb.tool == null)
                    continue;

                var amount = verb.verbProps.AdjustedMeleeDamageAmount(verb, pawn);
                if (found && amount <= best.amount)
                    continue;

                found = true;
                best.amount = amount;
                best.damageDef = verb.GetDamageDef() ?? DamageDefOf.Blunt;
                best.sharpPenetration = best.bluntPenetration = verb.verbProps.AdjustedArmorPenetration(verb, pawn);

                // CE rates sharp and blunt separately on its own scale (mm / MPa); its melee verb exposes both.
                if (CombatExtendedActive && verb.GetType().GetProperty("ArmorPenetrationSharp") is { } sharp && verb.GetType().GetProperty("ArmorPenetrationBlunt") is { } blunt)
                {
                    best.sharpPenetration = (float)sharp.GetValue(verb);
                    best.bluntPenetration = (float)blunt.GetValue(verb);
                }
                best.armorPenetration = best.PenetrationFor(best.damageDef);
            }

            return best;
        }

        public struct MeleeHit
        {
            public float amount;
            public DamageDef damageDef;
            /// <summary>Penetration for <see cref="damageDef"/>.</summary>
            public float armorPenetration;
            public float sharpPenetration;
            public float bluntPenetration;

            /// <summary>Penetration when this hit is dealt as another damage type (e.g. a cleave that always cuts).</summary>
            public float PenetrationFor(DamageDef def) =>
                def?.armorCategory == DamageArmorCategoryDefOf.Sharp ? sharpPenetration : bluntPenetration;
        }

        /// <summary>Deals one ability hit. Crits multiply damage. Returns true on a crit.</summary>
        public static bool Strike(Pawn caster, Thing victim, float amount, DamageDef damageDef, float armorPenetration, float critChance = 0f, float critMultiplier = 3f)
        {
            var crit = critChance > 0f && Rand.Chance(critChance);
            if (crit)
                amount *= critMultiplier;

            var angle = (victim.Position - caster.Position).AngleFlat;
            var dinfo = new DamageInfo(damageDef, Mathf.Max(1f, amount), armorPenetration, angle, caster);
            victim.TakeDamage(dinfo);

            if (crit && victim.Spawned)
                MoteMaker.ThrowText(victim.DrawPos, victim.Map, "ABT_Crit".Translate(), Color.yellow);
            return crit;
        }

        // ---- Movement ----

        public static bool IsFreeStandCell(IntVec3 cell, Map map) =>
            map != null && cell.InBounds(map) && !cell.Fogged(map) && cell.Standable(map) && cell.GetFirstPawn(map) == null;

        public static void Teleport(Pawn pawn, IntVec3 destination, bool effects = true)
        {
            var map = pawn.Map;
            if (effects)
                SkipFlash(pawn.Position, map);

            pawn.Position = destination;
            pawn.pather?.StopDead();
            pawn.Notify_Teleported(true, true);

            if (effects)
                SkipFlash(destination, map);
        }

        private static void SkipFlash(IntVec3 cell, Map map)
        {
            FleckMaker.ThrowLightningGlow(cell.ToVector3Shifted(), map, 1.2f);
            FleckMaker.ThrowDustPuffThick(cell.ToVector3Shifted(), map, 1.2f, Color.white);
        }

        // ---- Visuals ----

        /// <summary>A crackling line of sparks between two points. Cheap: one fleck per cell of distance.</summary>
        public static void ArcBetween(Vector3 from, Vector3 to, Map map)
        {
            var delta = to - from;
            var steps = Mathf.Max(1, Mathf.CeilToInt(delta.MagnitudeHorizontal()));
            for (var i = 0; i <= steps; i++)
            {
                var point = from + delta * (i / (float)steps);
                point.x += Rand.Range(-0.15f, 0.15f);
                point.z += Rand.Range(-0.15f, 0.15f);
                FleckMaker.Static(point, map, ABT_DefOf.ElectricalSpark, Rand.Range(0.6f, 1f));
            }

            FleckMaker.ThrowLightningGlow(to, map, 1.5f);
        }

        public static void SkyBolt(IntVec3 cell, Map map)
        {
            map.weatherManager.eventHandler.AddEvent(new WeatherEvent_Bolt(map, cell));
        }

        public static void PlayAt(SoundDef sound, IntVec3 cell, Map map) =>
            sound?.PlayOneShot(new TargetInfo(cell, map));
    }

    /// <summary>A lightning bolt from the sky with flash and thunder, but no damage of its own (vanilla strikes add a flame explosion).</summary>
    [StaticConstructorOnStartup]
    public class WeatherEvent_Bolt : WeatherEvent_LightningFlash
    {
        private static readonly Material LightningMat = MatLoader.LoadMat("Weather/LightningBolt");

        private readonly IntVec3 strikeLoc;
        private Mesh boltMesh;

        public WeatherEvent_Bolt(Map map, IntVec3 strikeLoc) : base(map)
        {
            this.strikeLoc = strikeLoc;
        }

        public override void FireEvent()
        {
            base.FireEvent();
            boltMesh = LightningBoltMeshPool.RandomBoltMesh;
            var loc = strikeLoc.ToVector3Shifted();
            FleckMaker.ThrowMicroSparks(loc, map);
            FleckMaker.ThrowLightningGlow(loc, map, 2f);
            SoundDefOf.Thunder_OnMap.PlayOneShot(new TargetInfo(strikeLoc, map));
        }

        public override void WeatherEventDraw()
        {
            if (boltMesh != null)
                Graphics.DrawMesh(boltMesh, strikeLoc.ToVector3ShiftedWithAltitude(AltitudeLayer.Weather), Quaternion.identity,
                    FadedMaterialPool.FadedVersionOf(LightningMat, LightningBrightness), 0);
        }
    }
}
