# Data Manifest

This repository keeps both source snapshots and generated exports so the HTML can be audited without rerunning the scraper.

## Primary App

- `deadlock_hero_level_curves.html`
- `deadlock_hero_level_curves_data.json`
- `assets/fonts/lxgw-wenkai-500.woff2`
- `assets/fonts/lxgw-wenkai-700.woff2`

## Generators

- `build_deadlock_level_curves_with_abilities.py`
- `build_deadlock_level_curves.py`
- `extract_deadlock_hero_stats.py`

## Source Snapshots

- `heroes_assets_v2.json`
- `items_assets_v2.json`
- `deadlock_heroes_base_growth_active.csv`
- `deadlock_heroes_base_growth_active.json`
- `deadlock_heroes_base_growth_all.csv`
- `deadlock_heroes_base_growth_all.json`
- `deadlock_heroes_stat_scaling_active.csv`
- `deadlock_heroes_cost_bonuses_active.csv`
- `deadlock_heroes_purchase_bonuses_active.csv`

## Generated Ability / Item Exports

- `deadlock_hero_abilities.csv`
- `deadlock_hero_abilities_full.json`
- `deadlock_hero_ability_stat_effects.csv`
- `deadlock_item_passive_effects.csv`
- `ability_effect_summary.tsv`
- `ability_passive_effect_summary.tsv`
- `ability_stat_upgrade_candidates.tsv`
- `item_passive_effect_summary.tsv`
- `ability_provided_property_types.txt`

## Earlier Curve Exports

- `deadlock_hero_level_values_long.csv`
- `deadlock_hero_stat_intersections.csv`
- `deadlock_hero_level_curves_README.md`
- `deadlock_heroes_stats_README.md`

## Scratch / Fetch Artifacts

These files are useful only as evidence of the original fetch attempts and can be omitted from a polished public release if desired:

- `scratch/deadlocked_app.html`
- `scratch/deadlocked_headers.txt`
- `scratch/deadlocked_heroes.html`
- `scratch/deadlocked_root.html`
- `scratch/deadlock_api_root.html`
- `scratch/heroes_api_v1.json`
- `scratch/weapons_assets_v2.json`
