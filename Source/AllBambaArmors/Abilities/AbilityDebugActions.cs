using System;
using System.Linq;
using LudeonTK;
using RimWorld;
using VEF.Abilities;
using Verse;
using AbilityDef = VEF.Abilities.AbilityDef;

namespace AllBambaArmors
{
    public static class AbilityDebugActions
    {
        /// <summary>Dev tool: click a pawn to give it every VEF ability this mod defines. Already-known abilities are skipped.</summary>
        [DebugAction("Pawns", "Give all Bamba abilities", actionType = DebugActionType.ToolMapForPawns, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void GiveAllBambaAbilities(Pawn pawn)
        {
            var comp = pawn.GetComp<CompAbilities>();
            if (comp == null)
            {
                Messages.Message($"{pawn.LabelShort} cannot hold abilities.", MessageTypeDefOf.RejectInput, false);
                return;
            }

            var defs = DefDatabase<AbilityDef>.AllDefs
                .Where(d => string.Equals(d.modContentPack?.PackageId, "Bamba.AllBambaArmors", StringComparison.OrdinalIgnoreCase))
                .ToList();
            foreach (var def in defs)
                comp.GiveAbility(def);

            DebugActionsUtility.DustPuffFrom(pawn);
            Messages.Message($"Gave {pawn.LabelShort} {defs.Count} abilities.", MessageTypeDefOf.TaskCompletion, false);
        }

        /// <summary>
        /// Dev tool: attach a default 100-point energy pool to a pawn so ability costs can be tried before any def carries the comp.
        /// Comps come from the def on load, so this pool is gone after reloading.
        /// </summary>
        [DebugAction("Pawns", "Add Bamba ability energy (until reload)", actionType = DebugActionType.ToolMapForPawns, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void AddAbilityEnergy(Pawn pawn)
        {
            if (pawn.TryGetComp<CompAbilityEnergy>() != null)
            {
                Messages.Message($"{pawn.LabelShort} already has an energy pool.", MessageTypeDefOf.RejectInput, false);
                return;
            }

            var comp = new CompAbilityEnergy { parent = pawn };
            pawn.AllComps.Add(comp);
            comp.Initialize(new CompProperties_AbilityEnergy());
            comp.PostPostMake();
            DebugActionsUtility.DustPuffFrom(pawn);
        }

        [DebugAction("Pawns", "Fill Bamba ability energy", actionType = DebugActionType.ToolMapForPawns, allowedGameStates = AllowedGameStates.PlayingOnMap)]
        private static void FillAbilityEnergy(Pawn pawn)
        {
            pawn.TryGetComp<CompAbilityEnergy>()?.SetEnergy(float.MaxValue);
            foreach (var apparel in pawn.apparel?.WornApparel ?? new System.Collections.Generic.List<Apparel>())
                apparel.TryGetComp<CompAbilityEnergy>()?.SetEnergy(float.MaxValue);
            DebugActionsUtility.DustPuffFrom(pawn);
        }
    }
}
