using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using VEF.Abilities;
using Verse;
using Ability = VEF.Abilities.Ability;

namespace AllBambaArmors
{
    // Composable ability pieces. VEF runs every AbilityExtension_AbilityMod on a def, so one ability can stack several of these in XML.

    /// <summary>
    /// On an apparel def: the abilities it grants only work for a wearer with <see cref="requiredHediff"/>
    /// (e.g. BOR's Orientis armor needs the BOR_Orientis hediff). Checked by <see cref="AbilityExtension_CastingRules"/>.
    /// </summary>
    public class ApparelAbilityRestriction : DefModExtension
    {
        public HediffDef requiredHediff;
        /// <summary>Shown on the disabled gizmo. Empty: a generic "only a pawn with ..." line.</summary>
        [MustTranslate] public string reason;
    }

    /// <summary>
    /// Shared casting rules from the spec that VEF does not enforce: no casting while downed,
    /// and abilities marked violent are unavailable to pawns incapable of violence.
    /// </summary>
    public class AbilityExtension_CastingRules : AbilityExtension_AbilityMod
    {
        public bool violent;

        public override bool IsEnabledForPawn(Ability ability, out string reason)
        {
            var pawn = ability.pawn;
            if (pawn.Downed)
            {
                reason = "ABT_CasterDowned".Translate(pawn.LabelShort);
                return false;
            }
            if (violent && pawn.WorkTagIsDisabled(WorkTags.Violent))
            {
                reason = "IsIncapableOfViolenceLower".Translate(pawn.LabelShort, pawn);
                return false;
            }
            if (ability.holder?.def.GetModExtension<ApparelAbilityRestriction>() is { requiredHediff: { } required } restriction && !pawn.health.hediffSet.HasHediff(required))
            {
                reason = restriction.reason.NullOrEmpty() ? "ABT_RequiresHediff".Translate(required.label).Resolve() : restriction.reason;
                return false;
            }

            reason = string.Empty;
            return true;
        }
    }

    /// <summary>
    /// Lowest armor penetration a weapon-based ability hits with, whatever the weapon. Separate values because
    /// Combat Extended rates armor in mm, where a weapon-strength cut cannot touch power armor.
    /// </summary>
    public class AbilityExtension_MinPenetration : DefModExtension
    {
        public float vanilla;
        public float combatExtended;

        public float For() => AbilityUtility.CombatExtendedActive ? combatExtended : vanilla;
    }

    /// <summary>Disables the ability unless the caster holds a melee (or ranged) weapon.</summary>
    public class AbilityExtension_RequiresWeapon : AbilityExtension_AbilityMod
    {
        public bool melee = true;

        public override bool IsEnabledForPawn(Ability ability, out string reason)
        {
            var pawn = ability.pawn;
            var ok = melee ? AbilityUtility.HasMeleeWeapon(pawn) : AbilityUtility.HasRangedWeapon(pawn);
            reason = ok ? string.Empty : (melee ? "ABT_MustHaveMeleeWeapon" : "ABT_MustHaveRangedWeapon").Translate(pawn.LabelShort);
            return ok;
        }
    }

}
