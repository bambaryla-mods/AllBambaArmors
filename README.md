# Armors For All Post-Medieval Tech Levels

A RimWorld mod that adds seven armor sets with matching helmets across three tech levels: industrial armored suits, advanced spacer armor and glitter armor. It also adds three backpacks and research for each craftable set, with stats for both vanilla and Combat Extended.

See everything the mod adds, with stats: https://databobek.github.io/AllBambaArmors/

Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3787547731

## Requirements

RimWorld 1.6 or 1.7. Nothing else is required. Combat Extended, Vanilla Expanded Framework (armor abilities), Royalty (prestige armor) and Beyond Our Reach add to it when loaded; the site's [requirements page](https://databobek.github.io/AllBambaArmors/requirements.html) says what each one adds.

## Repository layout

| Path | What |
|---|---|
| `1.6/`, `1.7/` | Defs and patches per game version, with `CE`, `Vanilla` and `VEF` subfolders picked by `LoadFolders.xml` |
| `Source/` | C# for the armor abilities (builds into `1.7/VEF/Assemblies`) |
| `abilities/` | The ability spec, the armor-to-ability map and the script that generates the ability patches |
| `site/` | The player site generator; see [site/README.md](site/README.md) |

## License

[CC BY-NC-SA 4.0](LICENSE).
