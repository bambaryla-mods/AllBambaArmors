"""
Generates the armor ability and energy patches for AllBambaArmors and Beyond Our Reach from one table.
Who gets what comes from abilities/ABILITY_MAP.md. Edit the tables below, then run:

    python abilities/make_armor_patches.py

It overwrites 1.7/VEF/Patches/ArcaneArmorAbilities.xml here and Mods/AllBambaArmors/Patches/ArmorAbilities.xml
in the sibling BeyondOurReach folder (loaded only with this mod and VEF), so do not hand-edit those two files.
"""
import os

BASE = 100.0  # Advanced Spacer medium armor
TIER = {"spacer": 1.0, "solar": 1.25, "ultra": 1.25 ** 2, "kwazaari": 1.25 ** 3, "orientis": 1.25 ** 3}
WEIGHT = {"light": 0.75, "medium": 1.0, "heavy": 1.25}
COLOR = {
    "spacer": "(0.3, 0.55, 0.95)",
    "solar": "(0.95, 0.75, 0.25)",
    "ultra": "(0.85, 0.45, 0.9)",
    "kwazaari": "(0.25, 0.8, 0.75)",
    "orientis": "(0.95, 0.85, 0.5)",
}
REFILL_SECONDS = 200.0
MAY_REQUIRE = ' MayRequire="bamba.allbambaarmors"'

# (defName, label for the comment, tier, weight, abilities, note)
ABT = [
    ("ABT_Apparel_AS_ReconArmor", "flanker armor", "spacer", "light", ["ABT_ShadowStrike"], ""),
    ("ABT_Apparel_AS_MarineArmor", "vanguard armor", "spacer", "medium", ["ABT_AntiArmor"], ""),
    ("ABT_Apparel_AS_PrestigeMarineArmor", "prestige vanguard armor (Royalty)", "spacer", "medium", ["ABT_AntiArmor"], "same as vanguard"),
    ("ABT_Apparel_AS_CataphractArmor", "breacher armor", "spacer", "heavy", ["ABT_EMP"], ""),
    ("ABT_Apparel_Ultra_Armor", "glitter suit", "ultra", "medium", [], "abilities in UltraArmorAbilities.xml"),
    ("ABT_Apparel_Ultra_PrestigeArmor", "prestige glitter suit (Royalty)", "ultra", "medium", [], "abilities in UltraArmorAbilities.xml"),
]

BOR = [
    ("BOR_Quasar_Apparel_ArmorHelmetMechCommander", "kwazaari mechcommander helmet (Biotech)", "kwazaari", "medium",
     ["ABT_Shield", "ABT_ChainLightning"], "no mechcommander body armor exists, so the helmet carries them"),
    ("BOR_Quasar_Apparel_PowerArmor", "kwazaari marine armor", "kwazaari", "medium", ["ABT_AdvancedHeal", "ABT_BestowMight"], ""),
    ("BOR_Quasar_Carbonsuit", "kwazaari bodysuit", "kwazaari", "light", ["ABT_TechnoBit"], ""),
    ("BOR_Solar_Apparel_PowerArmor", "solar marine armor", "solar", "medium", ["ABT_Medigel", "ABT_Sunfire"], ""),
    ("BOR_Solar_Apparel_ArchangelArmor", "solar daedalus armor (Royalty)", "solar", "light", ["ABT_Regenerate"], ""),
    ("BOR_Solar_Apparel_ArmorRecon", "solar recon (hussar) armor", "solar", "light", ["ABT_PhaseStrike", "ABT_Ignite"], ""),
    ("BOR_Solar_Carbonsuit", "solar bodysuit", "solar", "light", ["ABT_TechnoBit"], ""),
    ("BOR_Badzaari_Apparel_HeavyArmor", "badzaari plate harness", "kwazaari", "heavy", ["ABT_SeismicSlash"], ""),
    ("BOR_Orientis_SaladinArmor", "saladin armor (orientis light)", "orientis", "light", ["ABT_HealingCircle", "ABT_PsionicStorm"], ""),
    ("BOR_Orientis_TemplarArmor", "templar armor (orientis mid)", "orientis", "medium", ["ABT_CureDisease", "ABT_PsionicBlast"], ""),
    ("BOR_Orientis_MonkBodysuit", "monk bodysuit (orientis)", "orientis", "light", ["ABT_Resurrection"], ""),
    ("BOR_Orientis_BlackTemplarArmor", "black templar armor (orientis heavy)", "orientis", "heavy", ["ABT_Purify", "ABT_BattleHymn"], ""),
]

ORIENTIS_PAWN = ["ABT_PsionicBarrier", "ABT_HolyWrath", "ABT_Explosion", "ABT_CreateLight"]

# Apparel whose abilities only work for an Orientis wearer (the BOR_Orientis hediff).
ORIENTIS_ONLY = ["BOR_Orientis_SaladinArmor", "BOR_Orientis_TemplarArmor", "BOR_Orientis_BlackTemplarArmor", "BOR_Orientis_MonkBodysuit"]


EYE_AURA = """
	<!--
		Eye of the archotech (AllBambaArmors): Orientis in its light are blessed; Tenebral and Umbral pawns are seared.
		"Dark" matches BOR's MeditationShield.IsDark: Umbral, Tenebral parts, Tenebral psychosis, or the Tenebrites faction.
		Skipped quietly without AllBambaArmors, since the eye will not exist.
	-->
	<Operation Class="PatchOperationConditional">
		<xpath>Defs/ThingDef[defName="ABT_LightOrb"]/comps/li[@Class="BeyondOurReach.CompProperties_MoodAura"]/entries</xpath>
		<match Class="PatchOperationAdd">
			<xpath>Defs/ThingDef[defName="ABT_LightOrb"]/comps/li[@Class="BeyondOurReach.CompProperties_MoodAura"]/entries</xpath>
			<value>
				<li>
					<thought>ABT_ArchotechEyeBlessing</thought>
					<hediffs>
						<li>BOR_Orientis</li>
					</hediffs>
					<xenotypes>
						<li MayRequire="Ludeon.RimWorld.Biotech">BOR_OrientisXenotype</li>
					</xenotypes>
				</li>
				<li>
					<thought>ABT_ArchotechEyeSearing</thought>
					<hediffs>
						<li>BOR_Umbral</li>
						<li>BOR_Crystallized</li>
						<li>BOR_TenebralPsychosis</li>
					</hediffs>
					<hediffExtension>BeyondOurReach.DefModExtension_TenebralImplant</hediffExtension>
					<xenotypes>
						<li MayRequire="Ludeon.RimWorld.Biotech">BOR_UmbralXenotype</li>
					</xenotypes>
					<factions>
						<li>BOR_Tenebrites</li>
					</factions>
				</li>
			</value>
		</match>
	</Operation>
"""


def orientis_only_operation(def_name):
    path = f'Defs/ThingDef[defName="{def_name}"]'
    return f"""
	<!-- {def_name}: its abilities only work for an Orientis wearer -->
	<Operation Class="PatchOperationConditional">
		<xpath>{path}</xpath>
		<match Class="PatchOperationAddModExtension">
			<xpath>{path}</xpath>
			<value>
				<li Class="AllBambaArmors.ApparelAbilityRestriction"{MAY_REQUIRE}>
					<requiredHediff>BOR_Orientis</requiredHediff>
					<reason>Only an Orientis can call on this armor's gifts.</reason>
				</li>
			</value>
		</match>
	</Operation>
"""


def energy(tier, weight):
    max_energy = round(BASE * TIER[tier] * WEIGHT[weight])
    return max_energy, round(max_energy / REFILL_SECONDS, 3)


def list_block(cls, mr, abilities, indent):
    t = "\t" * indent
    lines = [f'{t}<li Class="{cls}"{mr}>', f"{t}\t<abilities>"]
    lines += [f"{t}\t\t<li>{a}</li>" for a in abilities]
    lines += [f"{t}\t</abilities>", f"{t}</li>"]
    return lines


def comps_items(entry, mr, indent):
    _, _, tier, weight, abilities, _ = entry
    max_energy, regen = energy(tier, weight)
    t = "\t" * indent
    lines = list_block("VEF.Abilities.CompProperties_AbilitiesApparel", mr, abilities, indent) if abilities else []
    lines += [
        f'{t}<li Class="AllBambaArmors.CompProperties_AbilityEnergy"{mr}>',
        f"{t}\t<maxEnergy>{max_energy}</maxEnergy>",
        f"{t}\t<regenPerSecond>{regen}</regenPerSecond>",
        f"{t}\t<barColor>{COLOR[tier]}</barColor>",
        f"{t}</li>",
    ]
    return "\n".join(lines)


def add_comps(path, items, nested, outer_indent):
    """Conditional add: into existing comps, or a new comps node."""
    t = "\t" * outer_indent
    return f"""{t}<xpath>{path}/comps</xpath>
{t}<match Class="PatchOperationAdd">
{t}	<xpath>{path}/comps</xpath>
{t}	<value>
{items}
{t}	</value>
{t}</match>
{t}<nomatch Class="PatchOperationAdd">
{t}	<xpath>{path}</xpath>
{t}	<value>
{t}		<comps>
{nested}
{t}		</comps>
{t}	</value>
{t}</nomatch>"""


def operation(entry, mr):
    def_name, label, tier, weight, abilities, note = entry
    path = f'Defs/ThingDef[defName="{def_name}"]'
    max_energy, _ = energy(tier, weight)
    comment = f"{label}: {tier} {weight}, {max_energy} energy" + (f"; {note}" if note else "")
    body = add_comps(path, comps_items(entry, mr, 5), comps_items(entry, mr, 6), 3)
    # Outer conditional: skip quietly when the def does not exist (DLC-only armor).
    return f"""
	<!-- {comment} -->
	<Operation Class="PatchOperationConditional">
		<xpath>{path}</xpath>
		<match Class="PatchOperationConditional">
{body}
		</match>
	</Operation>
"""


def orientis_operation():
    path = 'Defs/HediffDef[defName="BOR_Orientis"]'
    cls = "BeyondOurReach.HediffCompProperties_GrantAbilities"
    body = add_comps(path, "\n".join(list_block(cls, MAY_REQUIRE, ORIENTIS_PAWN, 4)),
                     "\n".join(list_block(cls, MAY_REQUIRE, ORIENTIS_PAWN, 5)), 2)
    return f"""
	<!-- Every Orientis pawn (the BOR_Orientis hediff marks them, with or without Biotech). They pay from their largest worn pool; with none, only cooldowns apply. -->
	<Operation Class="PatchOperationConditional">
{body}
	</Operation>
"""


HEADER = '<?xml version="1.0" encoding="utf-8"?>\n<Patch>\n'

abt = HEADER + """
	<!--
		Arcane abilities and energy pools on this mod's armor (abilities/ABILITY_MAP.md).
		Energy: Advanced Spacer medium = 100; Solar x1.25, Ultra x1.25 more, Kwazaari x1.25 more; light/medium/heavy x0.75/1/1.25.
		Each pool refills from empty in 200 seconds. Missing defs (Royalty-only prestige) are skipped quietly.
	-->
""" + "".join(operation(e, "") for e in ABT) + "\n</Patch>\n"

bor = HEADER + """
	<!--
		Abilities and energy pools from "Armors For All Post-Medieval Tech Levels" (bamba.allbambaarmors), which defines them.
		Every entry has MayRequire, so nothing here applies without that mod.
		Energy uses the same scale as that mod: Advanced Spacer medium = 100; Solar x1.25, Ultra x1.25 more, Kwazaari and Orientis x1.25 more;
		light/medium/heavy x0.75/1/1.25. Each pool refills from empty in 200 seconds.
		This folder loads last (LoadFolders.xml), so it runs after EquipmentBadzaar.xml, which adds the badzaari armor outside Combat Extended.
		Royalty- and Biotech-only armor is skipped quietly when the DLC is off.
	-->
""" + "".join(operation(e, MAY_REQUIRE) for e in BOR) + orientis_operation() + "".join(orientis_only_operation(d) for d in ORIENTIS_ONLY) + EYE_AURA + "\n</Patch>\n"

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOR_DIR = os.path.join(os.path.dirname(MOD), "BeyondOurReach")
with open(os.path.join(MOD, "1.7", "VEF", "Patches", "ArcaneArmorAbilities.xml"), "w", encoding="utf-8") as f:
    f.write(abt)
with open(os.path.join(BOR_DIR, "Mods", "AllBambaArmors", "Patches", "ArmorAbilities.xml"), "w", encoding="utf-8") as f:
    f.write(bor)

for e in ABT + BOR:
    print(e[0], energy(e[2], e[3]))
