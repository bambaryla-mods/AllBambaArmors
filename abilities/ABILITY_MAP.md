# Ability map

New label, then the spec name.

1. project kinetic shell (Shield / Shield Other) - kwazaari mechcommander armor
2. raise psychic deflector (Psionic Barrier) - any orientis pawn
3. inject mending nanites (Advanced Heal) - kwazaari marine armor
4. seed regenerative mechanites (Regenerate) - solar deadalus armor
5. apply Solar medigel (Medigel) - solar marine armor
6. deploy restoration field (Healing Circle) - orientis light armor
7. release pathogen hunters (Cure Disease) - orientis mid armor
8. run cellular rewrite (Purify) - orientis heavy armor
9. apply resurrector nanites (Resurrection) - orientis monk bodysuit
10. transmit combat overdrive (Bestow Might) - Kwazaari Marine Armor 
11. broadcast war cadence (Battle Hymn) - Orientis Heavy Armor (rename: Archotech Fury)
12. deploy support drone (Techno-Bit) - Solar and Kwazaar BodySuits, rename: T-Petrone
13. umbral ambush (Shadow Strike) - Advanced Spacer Flanker Armor (rename: Tacskip)
14. kinetic cleave (Seismic Slash) - Badzaari Armor
15. skip strike (Phase Strike) - Solar hussar Armor
16. fire armor-breaker round (Anti-Armor) - Advanced Spacer Vanguard Armor
17. arc discharge (Chain Lightning) - Kwazaari MechCommander Armor
18. psychic bolt volley (Psionic Blast) - orientis mid armor (rename: Archotech Bolt)
19. psychic tempest dive (Psionic Storm) - orientis saladin armor (rename: Archotech Tempest)
20. induce thermal flashover (Ignite) - Solar Hussar Armor
21. EMP burst (EMP) - Advanced Spacer Breacher Armor
22. call Solar lance barrage (Sunfire) - Solar Marine Armor
23. invoke Kylar-Xar verdict (Holy Wrath) - any orientis pawn, cooldown 4 minutes (rename: Judgment of the Archotech)
24. destabilize entropy (Explosion!) - any orientis pawn, cooldown 10 minutes (rename: Wrath of the Archotech)
25. deploy glowsphere (Create Light) - any orientis pawn (rename Eye of the Archotech)

Abilities for BOR armors are MayRequire="bamba.allbambaarmors", so we dont cross-implement

The BOR-only abilities (22 of them) live in BeyondOurReach/Mods/AllBambaArmors, defs and C# (BeyondOurReachArmors.dll, namespace BeyondOurReach). This mod keeps the shared base classes, the energy system and its own abilities.

Advanced spacer armor has the least available energy
Solar has 25% more
Ultra has 25% on top of that
Kwazaari has 25% on top of that
orientis has same as kwazaari

Light armors have less energy than the medium and these have less than heavy
75-100-125% corresponds to Light-Medium-Heavy armors respectively


1.7 only!