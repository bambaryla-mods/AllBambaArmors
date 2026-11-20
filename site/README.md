# Player site

The site at https://databobek.github.io/AllBambaArmors/ shows players what Armors For All adds and what it needs. It is not part of the mod: `_PublisherPlus.xml` keeps this folder out of the Workshop upload. It runs on a trimmed copy of the Beyond Our Reach site generator.

## How it works

`build.py` reads the mod the way RimWorld does. It loads the defs from the `<v1.7>` folders in `LoadFolders.xml`, applies the patches, resolves inheritance, honors `MayRequire`, and applies the English DefInjected text. It does this three times, once per set of active mods:

| Set | Active mods | Used for |
|---|---|---|
| vanilla | all DLCs | vanilla stats |
| ce | all DLCs plus Combat Extended | Combat Extended stats |
| all | all DLCs plus Vanilla Expanded Framework | the abilities |

Every stat, icon, cost and research number on the site comes from those defs, so the tables stay correct when you rebalance. The written text lives in `content/` and has to be updated by hand when something changes.

Some of the mod's defs inherit from vanilla or Combat Extended base defs, which aren't in the repo. `gen/external_parents.xml` holds copies of those. After a game or CE update, refresh it on a machine with the game installed and commit the result:

```
python site/build.py --refresh-parents
```

## Building and previewing

```
pip install -r site/requirements.txt
python site/build.py --serve
```

Then open http://localhost:8000. The build lists problems it found, like an unknown def name, and which screenshots are still missing. It only ever deletes an output folder it created itself.

Pushing to `main` rebuilds and publishes the site through `.github/workflows/pages.yml`. One-time setup on GitHub: **Settings > Pages > Source: GitHub Actions**. Pages only works on a public repository with a free account.

The workflow builds with `--strict`, so a problem fails the run and the live site stays as it was. The site is built from what's committed, so commit new content before or together with the pages that describe it.

## Where things live

| Path | What |
|---|---|
| `content/*.md` | One Markdown file per page. Front matter sets the home page card (`summary`, `card`). |
| `build.py` | The top bar groups and page order (`NAV`), the helpers pages can call, and the page rendering. |
| `gen/defs.py` | Loading, patching, inheritance and `MayRequire`. |
| `gen/external.py`, `gen/external_parents.xml` | The vanilla, DLC and CE base defs the mod inherits from. |
| `gen/extract.py` | Turns defs into table rows. Tech level rules and stat labels are at the top. |
| `templates/` | Page layout (`base.html`, `page.html`, `home.html`) and the tables (`macros.html`). |
| `static/` | CSS, the Vanilla/CE switch script and the Audiowide font (OFL). |
| `screenshots/` | In-game screenshots, if you add any. |

## Helpers a page can call

```
{{ apparel_tables("armor") }}  armor and helmets, vanilla and CE; "apparel" for the backpacks
{{ apparel_tables("armor", "spacer") }}   one tech level only (industrial, spacer, ultra)
{{ research_tables() }}        every research project
{{ armor_abilities() }}        every ability the armor grants, with energy cost, cooldown and the armor
{{ abilities("ABT_EMP") }}     cards for named abilities
{{ things("ABT_Apparel_Ultra_Armor") }}   cards for any defs, with their costs
{{ value("ThingDef", "ABT_Apparel_Ultra_Armor", "statBases/ArmorRating_Sharp", "pct") }}
                               a number from a def, inside a sentence; fmt: num, pct, days, seconds, across
{{ def_quote("ThingDef", "ABT_Apparel_Ultra_Armor") }}   quote a def's in-game description
{{ keyed_quote("SomeKey") }}   quote an English Keyed string
{{ screenshot("name", "caption") }}   screenshots/name.png
{{ integration_list() }}       mods named in LoadFolders.xml
```

Prefer `value()` over typing a number into the text: when the def changes, the page follows.

A home page card can show item icons (`card: icon:DefA,DefB`), a texture (`card: tex:Path/To/Texture`) or a screenshot (`card: shot:<name>`).
