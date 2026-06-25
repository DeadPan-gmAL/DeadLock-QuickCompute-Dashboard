# Deadlock Hero Level Curves

This folder contains level-curve outputs for the 38 active selectable heroes.

## Main Artifact

- `deadlock_hero_level_curves.html`
  - Open this file directly in a browser.
  - The UI is Chinese-first and includes a language toggle; hero, item, skill, and effect labels are localized in Chinese while source English names remain in the data exports.
  - The header shows the data snapshot version and latest asset `update_time`.
  - Use `版本日志` to open the version/source/changelog modal.
  - Use the attribute selector to switch stats.
  - Use the hero checklist to compare subsets.
  - The crossing table shows the exact fractional level where two curves meet.
  - Use `Ability Modifiers` to set a hero's desired base skill state or T1/T2/full upgrades and recalculate curves live.
  - Use `Equipment Build` to select a level, items, and item/soul bonus toggles for the active hero.
  - Use `Skill Inspector` to inspect the active hero's four skill values under the same level, skill, equipment, soul bonus, and purchase bonus context.
  - `respect level unlocks and 1/3/5 AP costs` is enabled by default.

## Data Files

- `deadlock_hero_level_curves_data.json`: embedded chart data, base stat inputs, abilities, mapped ability effects, shop items, mapped item effects, and hero bonus tables.
  - Includes `versionInfo`, which records source files, local file timestamps, asset `update_time` range, generated counts, and the page changelog.
- `deadlock_hero_level_values_long.csv`: no-ability baseline integer level values for every hero, attribute, and level.
- `deadlock_hero_stat_intersections.csv`: no-ability baseline unique curve intersections in levels 1-36.
- `deadlock_hero_abilities_full.json`: raw full ability data for the 38 active selectable heroes.
- `deadlock_hero_abilities.csv`: one row per hero signature ability with mapped effects summarized.
- `deadlock_hero_ability_stat_effects.csv`: ability effects that can be mapped into the curve calculator. `includeInCurve=true` marks effects used by the default passive-only curve.
- `deadlock_item_passive_effects.csv`: mapped shop item effects. `includeInBuild=true` marks effects used by the default equipment build calculator.

## Formula

For each hero and attribute:

```text
t = level - 1
value = a*t^2 + b*t + c
```

Most attributes are linear. Derived weapon attributes such as `Weapon DPS` and `Damage per Magazine` can be quadratic when bullet damage, clip size, or rounds per second scale with level.

The curves include:

- direct level growth from `growth_*_per_level`
- indirect `ETechPower` scaling from `scaling_*` fields
- levels 1 through 36
- gated unconditional passive/permanent hero-panel stat grants from the ability panel

The curves and crossing table do not include equipment passives, item purchase bonuses, or soul threshold bonuses. Those only apply to the current-level `Build Calculator` and `Skill Inspector`.

`is_level_1_tie=true` means the two heroes start equal at level 1. The HTML hides these by default because they can be noisy.

## Ability Modifier Notes

Ability state options are:

```text
Off -> ignore this ability
Base -> apply mapped base ability stat effects
T1 -> Base + first upgrade
T2 -> Base + first and second upgrades
Full -> Base + all three upgrades
```

When level gating is enabled, the page uses `level_info`:

```text
Signature1/2/3/4 unlock at levels 1, 3, 5, 7 respectively
Ability points at levels 2, 4, 6, and 8-36
Upgrade costs: T1=1, T2=3, T3=5
```

Selected ability states are treated as desired targets, not as level-1 effects. A skill cannot apply its Base/T1/T2/T3 effects before its fixed slot unlock level. The default allocator spends available points tier by tier in slot order: all selected T1s, then all selected T2s, then all selected T3s.

Example: if only `signature2` is set to `Full`, it is locked at levels 1-2, reaches T1 at level 3 if the level-2 AP was saved, reaches T2 at level 8, and reaches T3 at level 13.

Enemy debuffs and pure ability damage are not folded into base-stat curves. By default, the HTML only applies mapped effects classified as `passive_unconditional`: `IntrinsicallyProvidedInAbility`, not conditional/enemy-conditional, and not stack/kill assumptions.

Active-on-cast, conditional/self-buff, enemy-applied, and stack/kill effects are still exported for inspection. They do not enter curves or curve crossings. The `include active/contextual effects in snapshot` toggle only affects the current-level snapshot and Skill Inspector context; stack/kill effects then expose a numeric assumption field and default to 0.

## Equipment Build Notes

The build calculator uses the same selected hero and skill states as the ability panel. The selected build level controls both skill gating and item budget.

The equipment panel shows the selected level's maximum usable souls and has a `Level Table` popup listing the level-by-level soul budget from `level_info.required_gold`.

Budget and bonus rules:

```text
Available item budget = level_info[level].required_gold
Selected item cost = sum(cost of checked shop items)
Build is marked over budget if selected item cost exceeds available item budget
```

The calculator still displays over-budget builds so impossible combinations are visible instead of silently dropped.

Default build effects include:

- item passive stat lines classified as `passive_unconditional`
- hero `purchase_bonuses` for every selected item, using that item's category and tier
- hero `cost_bonuses` from total souls at the selected level, using the highest unlocked threshold per category

Active/contextual item effects are exported but excluded unless `include active/contextual item effects` is enabled.

## Version Notes

The source assets do not include an official Valve patch number or Steam build id. The page therefore displays a data snapshot version based on local source file timestamps plus the `items_assets_v2.json` asset `update_time` range.

Current generated page records:

```text
Game version field: source file does not provide an official game version number
Data snapshot: shown in the page header
Latest asset update: shown in the page header
Source files: heroes_assets_v2.json, items_assets_v2.json, deadlock_heroes_base_growth_active.csv
```

## Skill Inspector Notes

`Skill Inspector` is a current-level breakpoint view, not a curve. It uses the selected hero, build level, desired skill states, gating rules, selected items, purchase bonuses, and soul threshold bonuses.

Each skill card shows:

- `Base`: skill value using the current level and skill state with soul threshold bonuses but no selected item passives or purchase bonuses.
- `Build`: skill value after selected equipment, purchase bonuses, and soul bonuses.
- `Delta`: the build value minus the base value.

Main skill values are separated from conditional/stack/contextual values. Unsupported scale functions are displayed as raw values and marked as unsupported instead of being guessed.
