using RimWorld;
using RimWorld.Planet;
using Verse;

namespace AllBambaArmors
{
    public class Ability_Warp : VEF.Abilities.Ability
    {
        public override bool CanAutoCast => false;

        public override void Cast(params GlobalTargetInfo[] targets)
        {
            base.Cast(targets);

            if (targets.Length == 0 || pawn.MapHeld is not { } map)
                return;

            var destination = targets[0].Cell;
            if (!AbilityUtility.IsFreeStandCell(destination, map) || !pawn.Spawned)
                return;

            AbilityUtility.Teleport(pawn, destination, effects: false);
        }

        public override bool ValidateTarget(LocalTargetInfo target, bool showMessages = true)
        {
            if (!AbilityUtility.IsFreeStandCell(target.Cell, pawn.MapHeld))
            {
                if (showMessages)
                    Messages.Message("ABT_WarpInvalidDestination".Translate(), MessageTypeDefOf.RejectInput, false);
                return false;
            }

            return base.ValidateTarget(target, showMessages);
        }
    }
}
