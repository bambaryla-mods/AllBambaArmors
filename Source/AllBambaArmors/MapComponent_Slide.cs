using System.Collections.Generic;
using Verse;

namespace AllBambaArmors
{
    public class MapComponent_Slide : MapComponent
    {
        private const int TicksPerStep = 2;

        private class ActiveSlide
        {
            public Pawn Pawn;
            public UnityEngine.Vector3 Origin;
            public UnityEngine.Vector3 Direction;
            public int Step;
            public int MaxSteps;
        }

        private readonly List<ActiveSlide> slides = new List<ActiveSlide>();

        public MapComponent_Slide(Map map) : base(map)
        {
        }

        public static void Start(Pawn pawn, UnityEngine.Vector3 direction, int steps)
        {
            var comp = pawn.MapHeld?.GetComponent<MapComponent_Slide>();
            if (comp == null)
                return;

            comp.slides.RemoveAll(s => s.Pawn == pawn);
            pawn.pather?.StopDead();
            comp.slides.Add(new ActiveSlide
            {
                Pawn = pawn,
                Origin = pawn.Position.ToVector3(),
                Direction = direction,
                Step = 0,
                MaxSteps = steps
            });
        }

        public override void MapComponentTick()
        {
            if (slides.Count == 0 || Find.TickManager.TicksGame % TicksPerStep != 0)
                return;

            for (var i = slides.Count - 1; i >= 0; i--)
            {
                var slide = slides[i];
                if (!Advance(slide))
                    slides.RemoveAt(i);
            }
        }

        private bool Advance(ActiveSlide slide)
        {
            var pawn = slide.Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Map != map || slide.Step >= slide.MaxSteps)
                return false;

            slide.Step++;
            var next = (slide.Origin + slide.Direction * slide.Step).ToIntVec3();
            if (next == pawn.Position)
                return true;

            if (!next.InBounds(map) || !next.Walkable(map))
                return false;

            pawn.Position = next;
            pawn.pather?.StopDead();
            return slide.Step < slide.MaxSteps;
        }
    }
}
