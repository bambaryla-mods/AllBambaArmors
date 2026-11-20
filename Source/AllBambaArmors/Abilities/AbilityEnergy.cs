using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using VEF.Abilities;
using Verse;
using Ability = VEF.Abilities.Ability;

namespace AllBambaArmors
{
    /// <summary>An energy pool for abilities. Put it on a pawn's race def or on an apparel def.</summary>
    public class CompProperties_AbilityEnergy : CompProperties
    {
        public float maxEnergy = 100f;
        /// <summary>Energy regained per game second (60 ticks).</summary>
        public float regenPerSecond = 0.5f;
        public bool startFull = true;
        /// <summary>Gizmo title. Defaults to the apparel's label, or "Energy" on a pawn.</summary>
        [MustTranslate] public string label;
        public Color barColor = new Color(0.25f, 0.45f, 0.85f);

        public CompProperties_AbilityEnergy()
        {
            compClass = typeof(CompAbilityEnergy);
        }
    }

    /// <summary>
    /// Ability energy, shown as a bar gizmo like a shield belt's. It never ticks: regeneration is worked out
    /// from the ticks elapsed whenever the value is read, so worn apparel and off-map pawns stay accurate for free.
    /// </summary>
    public class CompAbilityEnergy : ThingComp
    {
        private float stored;
        private int lastUpdateTick = -1;
        private bool initialized;

        public CompProperties_AbilityEnergy Props => (CompProperties_AbilityEnergy)props;

        public float MaxEnergy => Props.maxEnergy;

        public float Energy
        {
            get
            {
                Sync();
                return stored;
            }
        }

        public float EnergyFraction => MaxEnergy <= 0f ? 0f : Energy / MaxEnergy;

        public Pawn Holder => parent as Pawn ?? (parent as Apparel)?.Wearer;

        public string BarLabel =>
            !Props.label.NullOrEmpty() ? Props.label.CapitalizeFirst() : parent is Apparel ? parent.LabelCap : "ABT_EnergyInbuilt".Translate().Resolve();

        public bool CanPay(float amount) => amount <= 0f || Energy >= amount - 0.001f;

        public void Spend(float amount)
        {
            Sync();
            stored = Mathf.Clamp(stored - amount, 0f, MaxEnergy);
        }

        public void SetEnergy(float value)
        {
            Sync();
            stored = Mathf.Clamp(value, 0f, MaxEnergy);
        }

        private void Sync()
        {
            var now = Find.TickManager?.TicksGame ?? 0;
            if (!initialized)
            {
                initialized = true;
                stored = Props.startFull ? MaxEnergy : 0f;
                lastUpdateTick = now;
                return;
            }

            if (now > lastUpdateTick)
            {
                stored = Mathf.Min(MaxEnergy, stored + Props.regenPerSecond * (now - lastUpdateTick) / GenTicks.TicksPerRealSecond);
                lastUpdateTick = now;
            }
            stored = Mathf.Min(stored, MaxEnergy);
        }

        public override void PostPostMake()
        {
            base.PostPostMake();
            Sync();
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            foreach (var gizmo in base.CompGetGizmosExtra())
                yield return gizmo;
            if (parent is Pawn pawn && ShowGizmo(pawn))
                yield return new Gizmo_AbilityEnergy(this);
        }

        public override IEnumerable<Gizmo> CompGetWornGizmosExtra()
        {
            foreach (var gizmo in base.CompGetWornGizmosExtra())
                yield return gizmo;
            if (Holder is { } wearer && ShowGizmo(wearer))
                yield return new Gizmo_AbilityEnergy(this);
        }

        private static bool ShowGizmo(Pawn pawn) => pawn.IsColonistPlayerControlled && Find.Selector.SingleSelectedThing == pawn;

        public override string CompInspectStringExtra() =>
            "ABT_EnergyInspect".Translate(Energy.ToString("F0"), MaxEnergy.ToString("F0"));

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref stored, "abilityEnergy");
            Scribe_Values.Look(ref lastUpdateTick, "abilityEnergyTick", -1);
            Scribe_Values.Look(ref initialized, "abilityEnergyInit");
        }
    }

    /// <summary>Energy bar gizmo, laid out like vanilla's shield belt status gizmo.</summary>
    [StaticConstructorOnStartup]
    public class Gizmo_AbilityEnergy : Gizmo
    {
        private static readonly Texture2D EmptyBarTex = SolidColorMaterials.NewSolidColorTexture(Color.clear);
        private static readonly Dictionary<Color, Texture2D> BarTexByColor = new Dictionary<Color, Texture2D>();

        private readonly CompAbilityEnergy energy;

        public Gizmo_AbilityEnergy(CompAbilityEnergy energy)
        {
            this.energy = energy;
            Order = -99f;
        }

        public override float GetWidth(float maxWidth) => 140f;

        public override GizmoResult GizmoOnGUI(Vector2 topLeft, float maxWidth, GizmoRenderParms parms)
        {
            var rect = new Rect(topLeft.x, topLeft.y, GetWidth(maxWidth), 75f);
            var inner = rect.ContractedBy(6f);
            Widgets.DrawWindowBackground(rect);

            var labelRect = inner;
            labelRect.height = rect.height / 2f;
            Text.Font = GameFont.Tiny;
            Widgets.Label(labelRect, energy.BarLabel);

            var barRect = inner;
            barRect.yMin = inner.y + inner.height / 2f;
            Widgets.FillableBar(barRect, energy.EnergyFraction, BarTex(energy.Props.barColor), EmptyBarTex, false);
            Text.Font = GameFont.Small;
            Text.Anchor = TextAnchor.MiddleCenter;
            Widgets.Label(barRect, energy.Energy.ToString("F0") + " / " + energy.MaxEnergy.ToString("F0"));
            Text.Anchor = TextAnchor.UpperLeft;

            TooltipHandler.TipRegion(inner, "ABT_EnergyTip".Translate(energy.Props.regenPerSecond.ToString("0.##")));
            return new GizmoResult(GizmoState.Clear);
        }

        // Textures can only be made on the main thread, which GizmoOnGUI runs on.
        private static Texture2D BarTex(Color color)
        {
            if (!BarTexByColor.TryGetValue(color, out var tex))
                BarTexByColor[color] = tex = SolidColorMaterials.NewSolidColorTexture(color);
            return tex;
        }
    }

    public static class AbilityEnergyUtility
    {
        /// <summary>
        /// The pool that pays for an ability. Granted by apparel: that apparel's pool, else the wearer's (see <see cref="SourceFor(Pawn)"/>).
        /// Held by the pawn itself (e.g. Orientis abilities): only the pawn's own pool, never the apparel's.
        /// Null means no pool, so only the cooldown limits the ability.
        /// </summary>
        public static CompAbilityEnergy SourceFor(Ability ability)
        {
            if (ability.holder is Apparel apparel)
                return apparel.TryGetComp<CompAbilityEnergy>() ?? SourceFor(ability.pawn);
            return ability.pawn?.TryGetComp<CompAbilityEnergy>();
        }

        public static CompAbilityEnergy SourceFor(Pawn pawn)
        {
            if (pawn == null)
                return null;
            if (pawn.TryGetComp<CompAbilityEnergy>() is { } inbuilt)
                return inbuilt;

            // A bodysuit under heavy armor should not be the one paying, so take the biggest pool worn.
            CompAbilityEnergy best = null;
            var worn = pawn.apparel?.WornApparel;
            if (worn != null)
            {
                for (var i = 0; i < worn.Count; i++)
                {
                    if (worn[i].TryGetComp<CompAbilityEnergy>() is { } pool && (best == null || pool.MaxEnergy > best.MaxEnergy))
                        best = pool;
                }
            }
            return best;
        }

        /// <summary>Pays <paramref name="amount"/> from <paramref name="pool"/>. True when paid, or when there is no pool at all.</summary>
        public static bool TryPay(CompAbilityEnergy pool, float amount)
        {
            if (amount <= 0f || pool == null)
                return true;
            if (!pool.CanPay(amount))
                return false;
            pool.Spend(amount);
            return true;
        }
    }

    /// <summary>
    /// For effects that keep spending after the cast (toggle hediffs): remembers which pool the cast used,
    /// so an armor-granted toggle keeps draining that armor and a pawn-held one never touches apparel.
    /// </summary>
    public class AbilityEnergyLink : IExposable
    {
        private Thing holder;
        private bool linked;

        public void Link(CompAbilityEnergy pool)
        {
            holder = pool?.parent;
            linked = true;
        }

        /// <summary>The linked pool; null when the cast was free. Unlinked (older saves) falls back to the pawn's pools.</summary>
        public CompAbilityEnergy Pool(Pawn pawn) => linked ? holder?.TryGetComp<CompAbilityEnergy>() : AbilityEnergyUtility.SourceFor(pawn);

        public void ExposeData()
        {
            Scribe_References.Look(ref holder, "energyHolder");
            Scribe_Values.Look(ref linked, "energyLinked");
        }
    }

    public interface IAbilityEnergyUser
    {
        AbilityEnergyLink Energy { get; }
    }

    /// <summary>
    /// Energy cost, paid when the cast completes. Pawns with no energy pool ignore it and are limited by cooldown only.
    /// Turning a toggle off is free.
    /// </summary>
    public class AbilityExtension_EnergyCost : AbilityExtension_AbilityMod
    {
        public float cost;
        /// <summary>Needs a full pool and empties it (Explosion!).</summary>
        public bool drainAll;

        private float CostFor(CompAbilityEnergy pool) => drainAll ? pool.MaxEnergy : cost;

        private static bool TurningOff(Ability ability) => ability is Ability_Toggle { IsActive: true };

        public override bool IsEnabledForPawn(Ability ability, out string reason)
        {
            reason = string.Empty;
            if (TurningOff(ability) || AbilityEnergyUtility.SourceFor(ability) is not { } pool)
                return true;

            var needed = CostFor(pool);
            if (pool.CanPay(needed))
                return true;

            reason = "ABT_NotEnoughEnergy".Translate(needed.ToString("F0"), pool.Energy.ToString("F0"));
            return false;
        }

        public override void Cast(GlobalTargetInfo[] targets, Ability ability)
        {
            base.Cast(targets, ability);
            if (TurningOff(ability) || AbilityEnergyUtility.SourceFor(ability) is not { } pool)
                return;
            pool.Spend(drainAll ? pool.Energy : cost);
        }

        public override string GetDescription(Ability ability) =>
            (drainAll ? "ABT_EnergyCostAll".Translate() : "ABT_EnergyCost".Translate(cost.ToString("0"))).Colorize(new Color(0.45f, 0.7f, 1f));
    }
}
