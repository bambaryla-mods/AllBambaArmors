using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.Abilities;
using Verse;
using Ability = VEF.Abilities.Ability;
using Verse.AI;
using Verse.Sound;

namespace AllBambaArmors
{
    [DefOf]
    public static class ABT_DefOf
    {
        public static HediffDef ABT_ShadowStrikeHasteHediff;
        public static HediffDef ABT_ShadowStrikeVeilHediff;
        public static FleckDef Fleck_RadialSparks;
        public static SoundDef Explosion_Vaporize;
        public static FleckDef ElectricalSpark;

        static ABT_DefOf() => DefOfHelper.EnsureInitializedInCtor(typeof(ABT_DefOf));
    }

    // ---------------- Toggles ----------------

    /// <summary>
    /// Casting adds the ability's hediff to the caster; casting again removes it.
    /// Turning off is always allowed and keeps the cooldown that turning on started.
    /// </summary>
    public class Ability_Toggle : Ability
    {
        private HediffDef ToggleHediff => def.GetModExtension<AbilityExtension_Hediff>()?.hediff;

        public bool IsActive => ToggleHediff is { } hediff && pawn.health.hediffSet.HasHediff(hediff);

        public override bool IsEnabledForPawn(out string reason)
        {
            if (IsActive)
            {
                reason = string.Empty;
                return true;
            }
            return base.IsEnabledForPawn(out reason);
        }

        public override void Cast(params GlobalTargetInfo[] targets)
        {
            var wasActive = IsActive;
            var previousCooldown = cooldown;
            base.Cast(targets);
            if (wasActive)
                cooldown = previousCooldown;
        }

        public override void ApplyHediffs(params GlobalTargetInfo[] targetInfo)
        {
            if (pawn.health.hediffSet.GetFirstHediffOfDef(ToggleHediff) is { } active)
            {
                pawn.health.RemoveHediff(active);
                return;
            }

            base.ApplyHediffs(targetInfo);
            // Ongoing costs (per surge, per drone action) keep drawing from the pool that paid for the cast.
            if (pawn.health.hediffSet.GetFirstHediffOfDef(ToggleHediff) is HediffWithComps added)
            {
                var pool = AbilityEnergyUtility.SourceFor(this);
                foreach (var comp in added.comps)
                    (comp as IAbilityEnergyUser)?.Energy.Link(pool);
            }
        }

        public override string GetDescriptionForPawn() =>
            base.GetDescriptionForPawn() + "\n\n" + (IsActive ? "ABT_ToggleOn" : "ABT_ToggleOff").Translate().Colorize(ColoredText.SubtleGrayColor);
    }

    // ---------------- Projectiles ----------------

    /// <summary>
    /// Anti-Armor round: rolls to hit with the caster's own shot accuracy, then deals the equipped gun's damage (capped).
    /// Against armored targets it punches through, adds stun blasts and shreds worn apparel.
    /// </summary>
    public class Ability_AntiArmor : Ability_ShootProjectile
    {
        public const float DamageCap = 60f;

        protected override Projectile ShootProjectile(GlobalTargetInfo target)
        {
            var extension = def.GetModExtension<AbilityExtension_Projectile>();
            var map = pawn.Map;
            var projectile = (Projectile_AntiArmor)GenSpawn.Spawn(extension.projectile, pawn.Position, map);
            projectile.ability = this;
            projectile.weaponDamage = WeaponDamage(out projectile.weaponArmorPenetration);

            var origin = pawn.DrawPos;
            var hitChance = HitChance(target);
            if (Rand.Chance(hitChance))
            {
                if (target.HasThing)
                    projectile.Launch(pawn, origin, target.Thing, target.Thing, ProjectileHitFlags.IntendedTarget, equipment: pawn.equipment.Primary);
                else
                    projectile.Launch(pawn, origin, target.Cell, target.Cell, ProjectileHitFlags.IntendedTarget, equipment: pawn.equipment.Primary);
            }
            else
            {
                var miss = ChangeDestToMissWild(target.Cell, pawn.Position, hitChance);
                projectile.Launch(pawn, origin, miss, miss, ProjectileHitFlags.NonTargetWorld, equipment: pawn.equipment.Primary);
            }
            return projectile;
        }

        private float HitChance(GlobalTargetInfo target)
        {
            var verb = pawn.equipment?.PrimaryEq?.PrimaryVerb;
            var localTarget = target.HasThing ? new LocalTargetInfo(target.Thing) : new LocalTargetInfo(target.Cell);
            if (verb != null)
                return ShotReport.HitReportFor(pawn, verb, localTarget).TotalEstimatedHitChance;

            return Mathf.Pow(pawn.GetStatValue(StatDefOf.ShootingAccuracyPawn), pawn.Position.DistanceTo(target.Cell));
        }

        private float WeaponDamage(out float armorPenetration)
        {
            armorPenetration = 0.5f;
            var weapon = pawn.equipment?.Primary;
            // The verb's projectile follows the loaded ammo under CE; fall back to the def's default projectile.
            var projectileDef = (pawn.equipment?.PrimaryEq?.PrimaryVerb as Verb_LaunchProjectile)?.Projectile
                                ?? weapon?.def.Verbs.FirstOrDefault(v => v.defaultProjectile != null)?.defaultProjectile;
            if (projectileDef?.projectile == null)
                return 10f;

            armorPenetration = AbilityUtility.ProjectileSharpPenetration(projectileDef, weapon);
            return Mathf.Min(DamageCap, projectileDef.projectile.GetDamageAmount(weapon));
        }
    }

    public class Projectile_AntiArmor : AbilityProjectile
    {
        public float weaponDamage = 10f;
        public float weaponArmorPenetration = 0.5f;

        private const float ArmoredMultiplier = 2f;
        private const float ArmoredBonus = 10f;
        private const float ArmoredPenetration = 1.5f;
        private const float CePenetration = 40f;
        private const int ApparelHits = 4;
        private static readonly FloatRange ApparelDamage = new FloatRange(50f, 150f);
        private const int StunBlasts = 3;

        protected override void DoImpact(Thing hitThing, Map map)
        {
            if (hitThing == null)
            {
                FleckMaker.Static(ExactPosition, map, FleckDefOf.ShotHit_Dirt);
                return;
            }

            var caster = launcher as Pawn;
            if (!IsArmored(hitThing))
            {
                hitThing.TakeDamage(new DamageInfo(DamageDefOf.Bullet, weaponDamage, weaponArmorPenetration, ExactRotation.eulerAngles.y, launcher, null, equipmentDef));
                return;
            }

            // Vanilla armor tops out near 2, so 1.5 goes through nearly everything; CE armor is in mm, so pierce at least 40 mm there.
            var penetration = AbilityUtility.CombatExtendedActive ? Mathf.Max(CePenetration, weaponArmorPenetration * 3f) : ArmoredPenetration;
            hitThing.TakeDamage(new DamageInfo(DamageDefOf.Bullet, weaponDamage * ArmoredMultiplier + ArmoredBonus, penetration, ExactRotation.eulerAngles.y, launcher, null, equipmentDef));

            var center = hitThing.Position;
            for (var i = 0; i < StunBlasts; i++)
            {
                var cell = center + GenAdj.AdjacentCellsAndInside[Rand.Range(0, 9)];
                if (cell.InBounds(map))
                    GenExplosion.DoExplosion(cell, map, 0.9f, DamageDefOf.Stun, caster, 12, doSoundEffects: i == 0, screenShakeFactor: 0.3f);
            }

            if (hitThing is Pawn pawn && pawn.apparel != null)
            {
                foreach (var apparel in pawn.apparel.WornApparel.InRandomOrder().Take(ApparelHits).ToList())
                    apparel.HitPoints = Mathf.Max(1, apparel.HitPoints - Mathf.RoundToInt(ApparelDamage.RandomInRange));
            }
        }

        /// <summary>Mechs, non-flesh pawns, buildings, or pawns whose overall sharp armor is above 100%.</summary>
        public static bool IsArmored(Thing thing)
        {
            if (thing is not Pawn pawn)
                return thing is Building;
            if (pawn.RaceProps.IsMechanoid || !pawn.RaceProps.IsFlesh)
                return true;
            return OverallSharpArmor(pawn) > 1f;
        }

        /// <summary>Coverage-weighted sharp armor across outer body parts, the same way the gear tab sums it.</summary>
        private static float OverallSharpArmor(Pawn pawn)
        {
            var natural = Mathf.Clamp01(pawn.GetStatValue(StatDefOf.ArmorRating_Sharp) / 2f);
            var total = 0f;
            var parts = pawn.RaceProps.body.AllParts;
            var worn = pawn.apparel?.WornApparel;
            foreach (var part in parts)
            {
                if (part.depth != BodyPartDepth.Outside || part.coverageAbs <= 0f)
                    continue;

                var remaining = 1f - natural;
                if (worn != null)
                {
                    foreach (var apparel in worn)
                    {
                        if (apparel.def.apparel.CoversBodyPart(part))
                            remaining *= 1f - Mathf.Clamp01(apparel.GetStatValue(StatDefOf.ArmorRating_Sharp) / 2f);
                    }
                }
                total += part.coverageAbs * (1f - remaining) * 2f;
            }
            return total;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref weaponDamage, "weaponDamage", 10f);
            Scribe_Values.Look(ref weaponArmorPenetration, "weaponArmorPenetration", 0.5f);
        }
    }

    // ---------------- Area ----------------

    // ---------------- Melee ----------------

    /// <summary>
    /// Shadow Strike (tacskip): skip behind the target, stab four times, leave a toxic cloud there, and skip straight back.
    /// The haste and the brief veil apply once the caster is home.
    /// </summary>
    public class Ability_ShadowStrike : Ability
    {
        private const int Hits = 4;
        private const float CritMultiplier = 3f;
        private const float BaseCritChance = 0.4f;
        private const float CritLossPerKg = 0.08f;
        private const float CloudRadius = 2f;
        private const float ToxinSeverity = 0.15f;

        public override void Cast(params GlobalTargetInfo[] targets)
        {
            base.Cast(targets);
            if (targets[0].Thing is not Pawn victim || !victim.Spawned)
                return;

            var map = pawn.Map;
            var origin = pawn.Position;
            var behind = CellBehind(victim);
            if (!behind.IsValid)
                return;

            AbilityUtility.Teleport(pawn, behind);
            pawn.rotationTracker.FaceTarget(victim);

            var hit = AbilityUtility.BestMeleeHit(pawn);
            var weapon = pawn.equipment?.Primary;
            var critChance = weapon != null && weapon.def.IsRangedWeapon ? 0f : Mathf.Max(0f, BaseCritChance - CritLossPerKg * (weapon?.GetStatValue(StatDefOf.Mass) ?? 0f));
            for (var i = 0; i < Hits && !victim.Dead; i++)
                AbilityUtility.Strike(pawn, victim, hit.amount, DamageDefOf.Stab,
                    AbilityUtility.CombatExtendedActive ? hit.PenetrationFor(DamageDefOf.Stab) : Rand.Range(0f, 0.5f), critChance, CritMultiplier);

            ToxicCloud(map);

            var home = AbilityUtility.IsFreeStandCell(origin, map) ? origin : CellFinder.StandableCellNear(origin, map, 3f);
            if (home.IsValid)
                AbilityUtility.Teleport(pawn, home);

            pawn.health.AddHediff(ABT_DefOf.ABT_ShadowStrikeHasteHediff);
            pawn.health.AddHediff(ABT_DefOf.ABT_ShadowStrikeVeilHediff);
        }

        private IntVec3 CellBehind(Pawn victim)
        {
            var map = victim.Map;
            var away = (victim.Position - pawn.Position).ToVector3();
            away.y = 0f;
            var behind = (victim.Position.ToVector3Shifted() + away.normalized).ToIntVec3();
            if (AbilityUtility.IsFreeStandCell(behind, map))
                return behind;

            foreach (var cell in GenAdj.CellsAdjacent8Way(victim).InRandomOrder())
            {
                if (AbilityUtility.IsFreeStandCell(cell, map))
                    return cell;
            }
            return IntVec3.Invalid;
        }

        private void ToxicCloud(Map map)
        {
            for (var i = 0; i < 6; i++)
                FleckMaker.ThrowSmoke(pawn.DrawPos + new Vector3(Rand.Range(-1f, 1f), 0f, Rand.Range(-1f, 1f)), map, 1.5f);

            foreach (var enemy in AbilityUtility.PawnsInRadius(pawn.Position, map, CloudRadius).ToList())
            {
                if (enemy != pawn && enemy.HostileTo(pawn) && enemy.RaceProps.IsFlesh)
                    HealthUtility.AdjustSeverity(enemy, HediffDefOf.ToxicBuildup, ToxinSeverity * Rand.Range(0.7f, 1.3f));
            }
        }
    }

    // ---------------- Utility ----------------

    // ---------------- Psionic Storm ----------------

}
