# Deadlock Hero Base Stats and Growth Coefficients

Generated on 2026-06-25 from:

- `https://assets.deadlock-api.com/v2/heroes`
- `https://assets.deadlock-api.com/v2/items`

`deadlocked.wiki` returned HTTP 429 from the local fetch session, so the exported data uses the public structured Deadlock API asset endpoints. The raw downloaded JSON files are kept in this folder for verification.

## Files

- `deadlock_heroes_base_growth_active.csv`: 38 currently selectable, enabled heroes.
- `deadlock_heroes_base_growth_all.csv`: all 61 hero records from the source, including disabled or in-development entries.
- `deadlock_heroes_base_growth_active.json`: structured active-hero data with full nested stats.
- `deadlock_heroes_base_growth_all.json`: structured all-hero data with full nested stats.
- `deadlock_heroes_stat_scaling_active.csv`: one row per active hero stat scaling coefficient.
- `deadlock_heroes_cost_bonuses_active.csv`: active hero soul-threshold bonuses by category.
- `deadlock_heroes_purchase_bonuses_active.csv`: active hero purchase-tier bonuses by category.
- `extract_deadlock_hero_stats.py`: reproducible extraction script.

## Field Notes

- `base_*`: hero `starting_stats` plus primary weapon `weapon_info`.
- `growth_*_per_level`: `standard_level_up_upgrades`.
- `scaling_*`: hero stat scaling coefficients, usually scaling against `ETechPower`.
- `active_selectable`: `player_selectable=true` and `disabled=false`.
