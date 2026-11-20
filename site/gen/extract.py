"""Turn resolved defs into the rows and cards the site renders.

Every number shown on the site comes from here, read out of the same XML the
game loads. Three def sets are used:
- vanilla: the mod without Combat Extended
- ce: the same with Combat Extended loaded
- all: every integration folder except CE (Vanilla Expanded Framework), for the abilities
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .defs import Def, DefDB, LoadFolder
from .textures import Textures

# Tech levels in display order, named as the mod names them.
TIERS = {
    "industrial": "Armored suits (industrial)",
    "spacer": "Advanced spacer",
    "ultra": "Glitter (ultratech)",
    "other": "General",
}
SPOILER_TIERS: frozenset[str] = frozenset()

MOD_NAMES = {
    "ludeon.rimworld.royalty": "Royalty",
    "ludeon.rimworld.ideology": "Ideology",
    "ludeon.rimworld.biotech": "Biotech",
    "ludeon.rimworld.anomaly": "Anomaly",
    "ludeon.rimworld.odyssey": "Odyssey",
    "ceteam.combatextended": "Combat Extended",
    "oskarpotocki.vanillafactionsexpanded.core": "Vanilla Expanded Framework",
    "bambaryla.bor.redux": "Beyond Our Reach",
}

# Name tokens first, then the file path.
_TIER_RULES = [
    ("ultra", re.compile(r"ultra|glitter")),
    ("spacer", re.compile(r"_as_|spacer")),
    ("industrial", re.compile(r"_ind_|industrial")),
]

# Vanilla stat names shown in effect lists. Other stats use their def labels.
STAT_LABELS = {
    "MoveSpeed": ("move speed", "abs"),
    "WorkSpeedGlobal": ("global work speed", "pct"),
    "ShootingAccuracyPawn": ("shooting accuracy", "abs"),
    "MeleeHitChance": ("melee hit chance", "abs"),
    "MeleeDodgeChance": ("melee dodge chance", "abs"),
    "AimingDelayFactor": ("aiming time", "pct"),
    "CarryingCapacity": ("carrying capacity", "abs"),
    "MedicalTendQuality": ("medical tend quality", "pct"),
    "MedicalTendSpeed": ("medical tend speed", "pct"),
    "MedicalSurgerySuccessChance": ("surgery success chance", "pct"),
    "ResearchSpeed": ("research speed", "pct"),
    "GlobalLearningFactor": ("learning rate", "pct"),
    "MiningSpeed": ("mining speed", "pct"),
    "MiningYield": ("mining yield", "pct"),
    "ConstructionSpeed": ("construction speed", "pct"),
    "ConstructSuccessChance": ("construct success chance", "pct"),
    "PlantWorkSpeed": ("plant work speed", "pct"),
    "PlantHarvestYield": ("plant harvest yield", "pct"),
    "SmeltingSpeed": ("smelting speed", "pct"),
    "GeneralLaborSpeed": ("general labor speed", "pct"),
    "SocialImpact": ("social impact", "pct"),
    "NegotiationAbility": ("negotiation ability", "pct"),
    "TradePriceImprovement": ("trade price improvement", "pct"),
    "PsychicSensitivity": ("psychic sensitivity", "pct"),
    "ToxicResistance": ("toxic resistance", "pct"),
    "ToxicEnvironmentResistance": ("toxic environment resistance", "pct"),
    "MentalBreakThreshold": ("mental break threshold", "pct"),
    "RestRateMultiplier": ("rest rate", "pct"),
    "EatingSpeed": ("eating speed", "pct"),
    "ImmunityGainSpeed": ("immunity gain speed", "pct"),
    "PainShockThreshold": ("pain shock threshold", "pct"),
    "Insulation_Cold": ("cold insulation", "temp"),
    "Insulation_Heat": ("heat insulation", "temp"),
    "ArmorRating_Sharp": ("sharp armor", "pct"),
    "ArmorRating_Blunt": ("blunt armor", "pct"),
    "ArmorRating_Heat": ("heat armor", "pct"),
    "MechBandwidth": ("mech bandwidth", "abs"),
    "MechControlGroups": ("mech control groups", "abs"),
    "MechRemoteRepairDistance": ("mech remote repair distance", "abs"),
    "MechFormingSpeed": ("mech gestation speed", "pct"),
    "MechRepairSpeed": ("mech repair speed", "pct"),
    "JumpRange": ("jump range", "abs"),
    "SlaveSuppressionOffsetWorn": ("slave suppression", "pct"),
    "VacuumResistance": ("vacuum resistance", "pct"),
    "VEF_MassCarryCapacity": ("caravan carry capacity", "abs"),
    "SlaveSuppressionOffset": ("slave suppression", "pct"),
    "CarryBulk": ("carry bulk", "abs"),
    "CarryWeight": ("carry weight", "abs"),
    "WornBulk": ("worn bulk", "abs"),
    "Suppressability": ("suppressability", "pct"),
    "SmokeSensitivity": ("smoke sensitivity", "pct"),
    "ReloadSpeed": ("reload speed", "pct"),
    "AimingAccuracy": ("aiming accuracy", "pct"),
    "MeleeCritChance": ("melee crit chance", "pct"),
    "MeleeParryChance": ("melee parry chance", "pct"),
    "MeleeDodgeChanceCE": ("melee dodge chance", "pct"),
    "NightVisionEfficiency": ("night vision", "pct"),
    "Comfort": ("comfort", "pct"),
}



def tier_of(d: Def) -> str:
    name = f"{d.def_name} {d.label}".lower()
    for tier, rx in _TIER_RULES:
        if rx.search(name):
            return tier
    path = d.file.lower()
    for tier, rx in _TIER_RULES:
        if rx.search(path):
            return tier
    return "other"


_ACRONYMS = re.compile(r"\b(dmr|lmg|smg|emp)\b")


def cap(s: str | None) -> str:
    """Capitalize like the game's UI, and fix acronyms the defs write in lower case."""
    if not s:
        return ""
    s = _ACRONYMS.sub(lambda m: m.group(1).upper(), s)
    return s[:1].upper() + s[1:]


def humanize(name: str) -> str:
    name = re.sub(r"^AB[AT]_", "", name)
    name = name.replace("_", " ")
    name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    return name.strip().lower()


def _f(el, path: str, default: float | None = None) -> float | None:
    if el is None:
        return default
    v = el.findtext(path)
    if v is None or not v.strip():
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _uniq(xs):
    seen, out = set(), []
    for x in xs:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


@dataclass
class Group:
    tier: str
    items: list = field(default_factory=list)
    open: bool = False  # shown expanded even if it's a spoiler tier (on its own page)

    @property
    def label(self) -> str:
        return TIERS.get(self.tier, cap(self.tier))

    @property
    def spoiler(self) -> bool:
        return self.tier in SPOILER_TIERS and not self.open


# Vanilla materials that show up in cost lists (their defs aren't in the repo).
VANILLA_MATERIALS = {
    "Steel": "steel", "Plasteel": "plasteel", "ComponentIndustrial": "components",
    "ComponentSpacer": "advanced components", "Gold": "gold", "Silver": "silver", "Uranium": "uranium",
    "Jade": "jade", "Cloth": "cloth", "Hyperweave": "hyperweave", "DevilstrandCloth": "devilstrand",
    "Synthread": "synthread", "WoodLog": "wood", "Chemfuel": "chemfuel", "Neutroamine": "neutroamine",
    "MedicineIndustrial": "medicine", "MedicineUltratech": "glitterworld medicine", "Luciferium": "luciferium",
}


def group_by_tier(items: list[dict]) -> list[Group]:
    order = list(TIERS)
    groups: dict[str, Group] = {}
    for it in items:
        groups.setdefault(it["tier"], Group(it["tier"])).items.append(it)
    for g in groups.values():
        g.items.sort(key=lambda it: it["label"].lower())
    return sorted(groups.values(), key=lambda g: order.index(g.tier) if g.tier in order else len(order))


def _range(text: str | None) -> tuple[float, float] | None:
    """A FloatRange like "1.5~2.5", or a single number."""
    if not text:
        return None
    lo, _, hi = text.partition("~")
    try:
        return float(lo), float(hi or lo)
    except ValueError:
        return None


class Extractor:
    def __init__(self, dbs: dict[str, DefDB], folders: list[LoadFolder], tex: Textures,
                 hard_deps: set[str] | frozenset[str] = frozenset()):
        self.v = dbs["vanilla"]
        self.ce = dbs["ce"]
        self.all = dbs["all"]
        self.folders = {f.path: f for f in folders}
        self.tex = tex
        self.hard_deps = {i.lower() for i in hard_deps}  # required mods never get a badge
        self._recipe_index: dict[int, tuple[dict, dict]] = {}
        self.notes: list[str] = []

    # ---------- shared helpers ----------

    def _names(self, ids) -> list[str]:
        return _uniq(MOD_NAMES.get(i, i) for i in ids if i and i not in self.hard_deps)

    def requires(self, d: Def) -> list[str]:
        """DLC/mod badges: the load folder's IfModActive (any of) and IfModActiveAll,
        and the def's own MayRequire (all of) / MayRequireAnyOf."""
        out: list[str] = []
        f = self.folders.get(d.src)
        if f:
            any_of = self._names(f.if_active)
            if any_of:
                out.append(" or ".join(any_of))
            out += self._names(f.if_active_all)
        out += self._names(i.strip().lower() for i in (d.el.get("MayRequire") or "").split(","))
        any_of = self._names(i.strip().lower() for i in (d.el.get("MayRequireAnyOf") or "").split(","))
        if any_of:
            out.append(" or ".join(any_of))
        return _uniq(out)

    def _recipes(self, db: DefDB):
        key = id(db)
        if key not in self._recipe_index:
            by_product: dict[str, list[Def]] = {}
            for r in db.all("RecipeDef"):
                products = r.node("products")
                for p in (products if products is not None else []):
                    by_product.setdefault(p.tag, []).append(r)
            users: dict[str, list[str]] = {}
            for t in db.all("ThingDef"):
                for rn in t.items("recipes"):
                    users.setdefault(rn, []).append(t.def_name)
            self._recipe_index[key] = (by_product, users)
        return self._recipe_index[key]

    def _research_label(self, db: DefDB, name: str) -> str:
        r = db.get("ResearchProjectDef", name) or self.all.get("ResearchProjectDef", name)
        return cap(r.label) if r else humanize(name)

    def _thing_label(self, db: DefDB, name: str) -> str:
        t = db.get("ThingDef", name) or self.all.get("ThingDef", name)
        return cap(t.label) if t else humanize(name)

    def making(self, d: Def, db: DefDB) -> dict:
        research: list[str] = []
        benches: list[str] = []
        if d.node("recipeMaker") is not None:
            research += [d.text("recipeMaker/researchPrerequisite")] + d.items("recipeMaker/researchPrerequisites")
            benches += d.items("recipeMaker/recipeUsers")
        by_product, users = self._recipes(db)
        for r in by_product.get(d.def_name, []):
            research += [r.text("researchPrerequisite")] + r.items("researchPrerequisites")
            benches += r.items("recipeUsers") + users.get(r.def_name, [])
        research += d.items("researchPrerequisites")
        return {
            "research": [self._research_label(db, x) for x in _uniq(research)],
            "benches": [self._thing_label(db, x) for x in _uniq(benches)],
        }

    def cost(self, d: Def, db: DefDB) -> list[str]:
        """The def's costList, e.g. ["120 plasteel", "4 advanced components"]."""
        out = []
        node = d.node("costList")
        for c in (node if node is not None else []):
            if not isinstance(c.tag, str):
                continue
            try:
                n = float((c.text or "").strip())
            except ValueError:
                continue
            thing = db.get("ThingDef", c.tag) or self.all.get("ThingDef", c.tag)
            label = thing.label if thing else VANILLA_MATERIALS.get(c.tag, humanize(c.tag))
            out.append(f"{n:g} {label}")
        stuff = d.num("costStuffCount")
        if stuff:
            cats = " or ".join(humanize(x) for x in d.items("stuffCategories")) or "material"
            out.append(f"{stuff:g} {cats}")
        return out

    def base_item(self, d: Def, db: DefDB) -> dict:
        icon = self.tex.icon(d)
        tier = tier_of(d)
        return {
            "def_name": d.def_name,
            "label": cap(d.label),
            "description": d.description,
            "spoiler_desc": False,
            "icon": icon,
            "tier": tier,
            "requires": self.requires(d),
            "cost": self.cost(d, db),
            **self.making(d, db),
        }

    def abilities(self, names: list[str]) -> list[dict]:
        """Ability cards: icon, text, cooldown (own or its group's) and the gear that grants it."""
        granted: dict[str, list[str]] = {}
        for t in self.all.all("ThingDef"):
            comps = t.node("comps")
            for li in (comps if comps is not None else []):
                given = [(x.text or "").strip() for x in li.findall("abilities/li")]
                given += [(li.findtext("abilityDef") or "").strip()]
                for a in given:
                    if a:
                        granted.setdefault(a, []).append(cap(t.label))
        out = []
        for n in names:
            d = self.all.get("AbilityDef", n)
            if d is None:
                self.notes.append(f"abilities(): no AbilityDef {n}")
                continue
            ticks = _range(d.text("cooldownTicksRange"))
            group = self.all.get("AbilityGroupDef", d.text("groupDef"))
            if ticks is None and group is not None and group.num("cooldownTicks"):
                ticks = (group.num("cooldownTicks"),) * 2
            out.append({
                "label": cap(d.label),
                "description": d.description,
                "icon": self.tex.export(self.tex.find(d.text("iconPath"))),
                "cooldown": (ticks[0] / 60, ticks[1] / 60) if ticks else None,
                "shared": group is not None,
                "granted_by": sorted(set(granted.get(n, []))),
            })
        return out

    def armor_abilities(self) -> list[dict]:
        """Every ability an armor in this mod grants: icon, text, energy cost, cooldown and the armors."""
        granted: dict[str, list[tuple[str, float]]] = {}
        for t in self.all.all("ThingDef"):
            comps = t.node("comps")
            if comps is None:
                continue
            energy = next((_f(li, "maxEnergy") for li in comps
                           if (li.get("Class") or "").endswith("CompProperties_AbilityEnergy")), None)
            for li in comps:
                if not (li.get("Class") or "").endswith("CompProperties_AbilitiesApparel"):
                    continue
                for x in li.findall("abilities/li"):
                    name = (x.text or "").strip()
                    if name:
                        granted.setdefault(name, []).append((cap(t.label), energy))
        rows = []
        for d in self.all.all("VEF.Abilities.AbilityDef"):
            if d.def_name not in granted:
                continue
            ticks = d.num("cooldownTime")
            rows.append({
                "label": cap(d.label),
                "description": d.description,
                "icon": self.tex.export(self.tex.find(d.text("iconPath"))),
                "cost": d.num("modExtensions/li[@Class='AllBambaArmors.AbilityExtension_EnergyCost']/cost"),
                "cooldown": ticks / 60 if ticks else None,
                "armors": sorted({a for a, _ in granted[d.def_name]}),
            })
        rows.sort(key=lambda r: (r["armors"][0], r["label"]))
        return rows

    def made_at(self, bench: str) -> list[dict]:
        """Everything the bench's recipes produce."""
        _, users = self._recipes(self.all)
        products = []
        for r in self.all.all("RecipeDef"):
            if bench in r.items("recipeUsers") or bench in users.get(r.def_name, []):
                node = r.node("products")
                products += [p.tag for p in (node if node is not None else []) if isinstance(p.tag, str)]
        items = []
        for name in _uniq(products):
            d = self.all.get("ThingDef", name)
            if d is not None:
                items.append(self.base_item(d, self.all))
        return sorted(items, key=lambda it: it["label"].lower())

    def stat_effects(self, d: Def, db: DefDB, path: str = "equippedStatOffsets") -> list[str]:
        node = d.node(path)
        out = []
        for st in (node if node is not None else []):
            if not isinstance(st.tag, str):
                continue
            try:
                val = float((st.text or "").strip())
            except ValueError:
                continue
            if val == 0:
                continue
            label, kind = STAT_LABELS.get(st.tag, (None, None))
            if label is None:
                sd = db.get("StatDef", st.tag) or self.all.get("StatDef", st.tag)
                label = sd.label if sd else humanize(st.tag)
                kind = "pct" if sd is not None and (sd.text("toStringStyle") or "").startswith("Percent") else "abs"
            sign = "+" if val > 0 else "−"
            if kind == "pct":
                out.append(f"{sign}{abs(val) * 100:g}% {label}")
            elif kind == "temp":
                out.append(f"{sign}{abs(val):g}°C {label}")
            else:
                out.append(f"{sign}{abs(val):g} {label}")
        return out

    # ---------- apparel ----------

    @staticmethod
    def apparel_kind(d: Def) -> str:
        f = d.file.lower()
        return "apparel" if ("statboost" in f or "belt" in f or "backpack" in f) else "armor"

    def _armor_value(self, d: Def, stat: str) -> dict | None:
        base = d.num(f"statBases/{stat}")
        stuffed = d.node("stuffCategories") is not None
        mult = d.num("statBases/StuffEffectMultiplierArmor") if stat != "ArmorRating_Heat" else None
        if stuffed and mult:
            return {"base": base or 0.0, "stuff": mult}
        if base is None:
            return None
        return {"base": base, "stuff": None}

    def _partial(self, d: Def) -> list[str]:
        """CE partial armor: each value multiplies the item's own rating on the listed parts."""
        out = []
        ext = d.node("modExtensions")
        for li in (ext if ext is not None else []):
            if li.get("Class") != "CombatExtended.PartialArmorExt":
                continue
            stats = li.find("stats")
            for s in (stats if stats is not None else []):
                parts = [humanize(p.text or "") for p in (s.find("parts") if s.find("parts") is not None else [])]
                for st in s:
                    if st.tag not in ("ArmorRating_Sharp", "ArmorRating_Blunt"):
                        continue
                    try:
                        mult = float((st.text or "").strip())
                    except ValueError:
                        continue
                    word, unit = ("sharp", "mm") if st.tag.endswith("Sharp") else ("blunt", "MPa")
                    base = d.num(f"statBases/{st.tag}")
                    value = f" = {base * mult:.3g} {unit}" if base is not None else ""
                    out.append(f"{word} ×{mult:g}{value} on {', '.join(parts)}")
        return out

    def apparel(self, kind: str) -> list[Group]:
        names = _uniq([d.def_name for d in self.v.all("ThingDef") if d.node("apparel") is not None]
                      + [d.def_name for d in self.ce.all("ThingDef") if d.node("apparel") is not None])
        rows = []
        for name in names:
            vd = self.v.get("ThingDef", name)
            cd = self.ce.get("ThingDef", name)
            d = vd or cd
            if self.apparel_kind(d) != kind:
                continue
            row = self.base_item(d, self.v if vd else self.ce)
            row["stuffed"] = d.node("stuffCategories") is not None
            if vd is not None:
                row["vanilla"] = {
                    "sharp": self._armor_value(vd, "ArmorRating_Sharp"),
                    "blunt": self._armor_value(vd, "ArmorRating_Blunt"),
                    "heat": self._armor_value(vd, "ArmorRating_Heat"),
                    "cold": vd.num("statBases/Insulation_Cold"),
                    "hot": vd.num("statBases/Insulation_Heat"),
                    "covers": _uniq(humanize(x) for x in vd.items("apparel/bodyPartGroups")),
                    "effects": self.stat_effects(vd, self.v),
                    "mass": vd.num("statBases/Mass"),
                }
            else:
                row["vanilla"] = None
            if cd is not None:
                row["ce"] = {
                    "sharp": self._armor_value(cd, "ArmorRating_Sharp"),
                    "blunt": self._armor_value(cd, "ArmorRating_Blunt"),
                    "heat": self._armor_value(cd, "ArmorRating_Heat"),
                    "bulk": cd.num("statBases/Bulk"),
                    "worn_bulk": cd.num("statBases/WornBulk"),
                    "mass": cd.num("statBases/Mass"),
                    "covers": _uniq(humanize(x) for x in cd.items("apparel/bodyPartGroups")),
                    "partial": self._partial(cd),
                    "effects": self.stat_effects(cd, self.ce),
                }
            else:
                row["ce"] = None
            rows.append(row)
        return group_by_tier(rows)

    # ---------- galleries ----------

    def _gallery(self, defs: list[Def]) -> list[Group]:
        rows = [self.base_item(d, self.all) for d in defs]
        return group_by_tier(rows)

    def things(self, names: list[str]) -> list[dict]:
        out = []
        for n in names:
            d = self.all.get("ThingDef", n) or self.ce.get("ThingDef", n)
            if d is None:
                self.notes.append(f"things(): no ThingDef {n}")
                continue
            out.append(self.base_item(d, self.all))
        return out

    # ---------- research ----------

    def research(self) -> list[Group]:
        """Every project in the vanilla set, plus the ones that only exist with CE."""
        rows = []
        vanilla_names = {d.def_name for d in self.v.all("ResearchProjectDef")}
        ce_only = [d for d in self.ce.all("ResearchProjectDef") if d.def_name not in vanilla_names]
        for d in self.v.all("ResearchProjectDef") + ce_only:
            db = self.v if d.def_name in vanilla_names else self.ce
            cost = d.num("baseCost")
            prereq = [self._research_label(db, x) for x in d.items("prerequisites") + d.items("hiddenPrerequisites")]
            special = None
            rows.append({
                "def_name": d.def_name,
                "label": cap(d.label),
                "description": d.description,
                "tier": tier_of(d),
                "cost": cost,
                "special": special,
                "prerequisites": prereq,
                "requires": self.requires(d),
            })
        groups = group_by_tier(rows)
        for g in groups:
            g.items.sort(key=lambda r: (r["special"] is not None, r["cost"] or 0, r["label"]))
        return groups
