# Deadlock Hero Stat Console

Deadlock hero stat comparison tool generated from local Deadlock API asset snapshots.

Open `index.html` or `deadlock_hero_level_curves.html` directly in a browser to use the current Chinese-first UI. The page keeps an English toggle, shows the local data snapshot/version notes, compares hero stat curves, calculates current-level hero snapshots, and inspects skill values under the same build context.

## What Is Included

- `index.html` - small redirect entry for GitHub Pages and local browsing.
- `deadlock_hero_level_curves.html` - self-contained interactive page.
- `deadlock_hero_level_curves_data.json` - data embedded into the page, useful for external checks.
- `build_deadlock_level_curves_with_abilities.py` - main generator for the HTML, JSON, and CSV exports.
- `extract_deadlock_hero_stats.py` - base hero stat extraction script.
- `heroes_assets_v2.json` and `items_assets_v2.json` - local source asset snapshots used by the generator.
- `assets/fonts/` - bundled Chinese webfont files used by the HTML.
- `render-check/` - Playwright-based smoke test for desktop/mobile rendering and language switching.
- `scratch/` - original fetch/debug artifacts that are not needed by the generator.
- `deadlock_hero_*.csv`, `deadlock_item_passive_effects.csv`, `deadlock_heroes_*.csv/json` - exported verification tables.

## Quick Start

```powershell
python build_deadlock_level_curves_with_abilities.py
```

Then open:

```text
index.html
```

or:

```text
deadlock_hero_level_curves.html
```

The HTML does not require a dev server.

## Render Check

Install dependencies once:

```powershell
cd render-check
npm install
```

Run the smoke test from the repository root:

```powershell
node render-check/render_html.js
```

The test opens the generated HTML with Playwright, checks Chinese default text, English toggle behavior, chart rendering, skill cards, version modal, and mobile layout.

## Data Notes

- The source assets currently do not include an official Valve patch number or Steam build id. The page records a local data snapshot timestamp and source asset update range instead.
- Chinese hero, item, skill, and field labels are maintained in the generator so the HTML can remain fully Chinese while preserving English source names in the data files.
- Skill and item effects are classified conservatively. Curve values include level growth and unconditional/passive hero-panel skill effects. Equipment, purchase bonuses, and soul threshold bonuses are reserved for current-level snapshot and skill inspector views.

## Repository Hygiene

Do not commit:

- `render-check/node_modules/`
- `__pycache__/`
- generated Playwright screenshots unless you intentionally want them in documentation
- local logs, temp files, or OS/editor metadata
