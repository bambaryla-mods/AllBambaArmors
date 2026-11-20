using System.Collections.Generic;
using System.Linq;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace AllBambaArmors
{
    public class Ability_FlareBurst : VEF.Abilities.Ability_Explode
    {
        private const float PushDistance = 4f;

        public override void Cast(params GlobalTargetInfo[] targets)
        {
            var map = pawn.MapHeld;
            var origin = pawn.Position;
            var radius = def.radius;

            base.Cast(targets);

            if (map == null)
                return;

            var victims = GenRadial.RadialDistinctThingsAround(origin, map, radius, true)
                .OfType<Pawn>()
                .Where(p => p != pawn && p.Spawned)
                .ToList();

            foreach (var victim in victims)
                Push(victim, origin, map);
        }

        private static void Push(Pawn victim, IntVec3 origin, Map map)
        {
            var direction = (victim.Position - origin).ToVector3();
            direction.y = 0f;
            if (direction.sqrMagnitude < 0.01f)
                direction = Rand.UnitVector3;
            direction.y = 0f;
            direction.Normalize();

            MapComponent_Slide.Start(victim, direction, Mathf.RoundToInt(PushDistance));
        }
    }
}
