import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HEROES_PATH = ROOT / "heroes_assets_v2.json"
ITEMS_PATH = ROOT / "items_assets_v2.json"

SOURCE_URLS = {
    "heroes": "https://assets.deadlock-api.com/v2/heroes",
    "items": "https://assets.deadlock-api.com/v2/items",
    "wiki_attempted": "https://deadlocked.wiki/",
}

STARTING_STAT_COLUMNS = {
    "max_health": "base_max_health",
    "base_health_regen": "base_health_regen",
    "tech_armor_damage_reduction": "base_spirit_armor_pct",
    "max_move_speed": "base_move_speed",
    "sprint_speed": "base_sprint_speed",
    "crouch_speed": "base_crouch_speed",
    "move_acceleration": "base_move_acceleration",
    "stamina": "base_stamina",
    "stamina_regen_per_second": "base_stamina_regen_per_second",
    "light_melee_damage": "base_light_melee_damage",
    "heavy_melee_damage": "base_heavy_melee_damage",
    "weapon_power": "base_weapon_power",
    "weapon_power_scale": "base_weapon_power_scale",
    "reload_speed": "base_reload_speed",
    "proc_build_up_rate_scale": "base_proc_build_up_rate_scale",
    "ability_resource_max": "base_ability_resource_max",
    "ability_resource_regen_per_second": "base_ability_resource_regen_per_second",
    "crit_damage_received_scale": "base_crit_damage_received_scale",
    "tech_duration": "base_tech_duration",
    "tech_range": "base_tech_range",
}

WEAPON_INFO_COLUMNS = {
    "bullet_damage": "base_bullet_damage",
    "damage_per_shot": "base_damage_per_shot",
    "damage_per_second": "base_weapon_dps",
    "damage_per_second_with_reload": "base_weapon_dps_with_reload",
    "damage_per_magazine": "base_damage_per_magazine",
    "clip_size": "base_clip_size",
    "bullets": "base_bullets",
    "burst_shot_count": "base_burst_shot_count",
    "shots_per_second": "base_shots_per_second",
    "bullets_per_second": "base_bullets_per_second",
    "shots_per_second_with_reload": "base_shots_per_second_with_reload",
    "bullets_per_second_with_reload": "base_bullets_per_second_with_reload",
    "cycle_time": "base_cycle_time",
    "reload_duration": "base_reload_duration",
    "bullet_speed": "base_bullet_speed",
    "range": "base_weapon_range",
    "damage_falloff_start_range": "base_damage_falloff_start_range",
    "damage_falloff_end_range": "base_damage_falloff_end_range",
    "damage_falloff_start_scale": "base_damage_falloff_start_scale",
    "damage_falloff_end_scale": "base_damage_falloff_end_scale",
    "crit_bonus_start": "base_crit_bonus_start",
    "crit_bonus_end": "base_crit_bonus_end",
    "crit_bonus_start_range": "base_crit_bonus_start_range",
    "crit_bonus_end_range": "base_crit_bonus_end_range",
}

LEVEL_GROWTH_COLUMNS = {
    "MODIFIER_VALUE_BASE_BULLET_DAMAGE_FROM_LEVEL": "growth_bullet_damage_per_level",
    "MODIFIER_VALUE_BASE_BULLET_DAMAGE_FROM_LEVEL_ALT_FIRE": "growth_bullet_damage_alt_fire_per_level",
    "MODIFIER_VALUE_BASE_HEALTH_FROM_LEVEL": "growth_health_per_level",
    "MODIFIER_VALUE_BASE_MELEE_DAMAGE_FROM_LEVEL": "growth_melee_damage_per_level",
    "MODIFIER_VALUE_BONUS_ATTACK_RANGE": "growth_bonus_attack_range_per_level",
    "MODIFIER_VALUE_BOON_COUNT": "growth_boon_count_per_level",
    "MODIFIER_VALUE_BULLET_ARMOR_DAMAGE_RESIST": "growth_bullet_armor_pct_per_level",
    "MODIFIER_VALUE_TECH_DAMAGE_MULTIPLIER": "growth_spirit_damage_multiplier_per_level",
    "MODIFIER_VALUE_TECH_POWER": "growth_spirit_power_per_level",
    "MODIFIER_VALUE_TECH_RESIST": "growth_spirit_resist_pct_per_level",
}

SCALING_TARGETS = [
    "EBaseHealthRegen",
    "EBulletArmorDamageReduction",
    "EBulletDamage",
    "EClipSize",
    "EFireRate",
    "EHeavyMeleeDamage",
    "EMaxMoveSpeed",
    "ERoundsPerSecond",
    "ESprintSpeed",
    "ETechArmorDamageReduction",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def stat_value(stats, key, default=None):
    item = stats.get(key)
    if isinstance(item, dict) and "value" in item:
        return item["value"]
    return default


def compact_json(value):
    if value in (None, {}, []):
        return ""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def build_rows(include_inactive=False):
    heroes = load_json(HEROES_PATH)
    items = load_json(ITEMS_PATH)
    items_by_class = {item.get("class_name"): item for item in items}

    rows = []
    structured = []
    scaling_rows = []
    cost_rows = []
    purchase_rows = []

    for hero in sorted(heroes, key=lambda h: h.get("name", "").lower()):
        active = bool(hero.get("player_selectable")) and not bool(hero.get("disabled"))
        if not include_inactive and not active:
            continue

        starting_stats = hero.get("starting_stats", {})
        level_growth = hero.get("standard_level_up_upgrades", {})
        scaling_stats = hero.get("scaling_stats", {})
        weapon_class = hero.get("items", {}).get("weapon_primary")
        weapon = items_by_class.get(weapon_class, {})
        weapon_info = weapon.get("weapon_info", {})

        row = {
            "hero_id": hero.get("id"),
            "hero_name": hero.get("name"),
            "class_name": hero.get("class_name"),
            "active_selectable": active,
            "player_selectable": hero.get("player_selectable"),
            "disabled": hero.get("disabled"),
            "in_development": hero.get("in_development"),
            "needs_testing": hero.get("needs_testing"),
            "hero_type": hero.get("hero_type"),
            "complexity": hero.get("complexity"),
            "gun_tag": hero.get("gun_tag"),
            "weapon_class_name": weapon_class,
            "weapon_name": weapon.get("name"),
            "base_bullet_armor_pct": stat_value(starting_stats, "bullet_armor_damage_reduction", 0),
            "base_spirit_armor_pct": stat_value(starting_stats, "tech_armor_damage_reduction", 0),
        }

        for source_key, output_key in STARTING_STAT_COLUMNS.items():
            if output_key not in row:
                row[output_key] = stat_value(starting_stats, source_key)

        for source_key, output_key in WEAPON_INFO_COLUMNS.items():
            row[output_key] = weapon_info.get(source_key)

        for source_key, output_key in LEVEL_GROWTH_COLUMNS.items():
            row[output_key] = level_growth.get(source_key)

        for target in SCALING_TARGETS:
            scaling = scaling_stats.get(target, {})
            row[f"scaling_{target}_stat"] = scaling.get("scaling_stat", "")
            row[f"scaling_{target}_scale"] = scaling.get("scale", "")

        row["scaling_stats_json"] = compact_json(scaling_stats)
        row["cost_bonuses_json"] = compact_json(hero.get("cost_bonuses"))
        row["purchase_bonuses_json"] = compact_json(hero.get("purchase_bonuses"))
        rows.append(row)

        structured.append(
            {
                "hero_id": hero.get("id"),
                "hero_name": hero.get("name"),
                "class_name": hero.get("class_name"),
                "active_selectable": active,
                "flags": {
                    "player_selectable": hero.get("player_selectable"),
                    "disabled": hero.get("disabled"),
                    "in_development": hero.get("in_development"),
                    "needs_testing": hero.get("needs_testing"),
                    "prerelease_only": hero.get("prerelease_only"),
                    "limited_testing": hero.get("limited_testing"),
                },
                "hero_type": hero.get("hero_type"),
                "complexity": hero.get("complexity"),
                "gun_tag": hero.get("gun_tag"),
                "weapon": {
                    "class_name": weapon_class,
                    "name": weapon.get("name"),
                    "weapon_info": weapon_info,
                },
                "starting_stats": {
                    key: stat_value(starting_stats, key)
                    for key in sorted(starting_stats.keys())
                },
                "standard_level_up_upgrades": level_growth,
                "scaling_stats": scaling_stats,
                "cost_bonuses": hero.get("cost_bonuses", {}),
                "purchase_bonuses": hero.get("purchase_bonuses", {}),
            }
        )

        for target, scaling in sorted(scaling_stats.items()):
            scaling_rows.append(
                {
                    "hero_id": hero.get("id"),
                    "hero_name": hero.get("name"),
                    "target_stat": target,
                    "scaling_stat": scaling.get("scaling_stat"),
                    "scale": scaling.get("scale"),
                    "active_selectable": active,
                }
            )

        for category, bonuses in sorted((hero.get("cost_bonuses") or {}).items()):
            for bonus in bonuses:
                cost_rows.append(
                    {
                        "hero_id": hero.get("id"),
                        "hero_name": hero.get("name"),
                        "category": category,
                        "gold_threshold": bonus.get("gold_threshold"),
                        "bonus": bonus.get("bonus"),
                        "percent_on_graph": bonus.get("percent_on_graph"),
                        "active_selectable": active,
                    }
                )

        for category, bonuses in sorted((hero.get("purchase_bonuses") or {}).items()):
            for bonus in bonuses:
                purchase_rows.append(
                    {
                        "hero_id": hero.get("id"),
                        "hero_name": hero.get("name"),
                        "category": category,
                        "tier": bonus.get("tier"),
                        "value_type": bonus.get("value_type"),
                        "value": bonus.get("value"),
                        "active_selectable": active,
                    }
                )

    return rows, structured, scaling_rows, cost_rows, purchase_rows


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"No rows for {path}")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, data, active_only):
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": SOURCE_URLS,
        "active_only": active_only,
        "record_count": len(data),
        "notes": [
            "active_selectable means player_selectable=true and disabled=false.",
            "base_* columns come from hero starting_stats plus primary weapon weapon_info.",
            "growth_* columns come from standard_level_up_upgrades.",
            "scaling_* columns and scaling_stats_json are hero stat scaling coefficients, usually against ETechPower.",
        ],
        "heroes": data,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    active_rows, active_structured, active_scaling, active_costs, active_purchases = build_rows(False)
    all_rows, all_structured, all_scaling, all_costs, all_purchases = build_rows(True)

    write_csv(ROOT / "deadlock_heroes_base_growth_active.csv", active_rows)
    write_csv(ROOT / "deadlock_heroes_base_growth_all.csv", all_rows)
    write_csv(ROOT / "deadlock_heroes_stat_scaling_active.csv", active_scaling)
    write_csv(ROOT / "deadlock_heroes_cost_bonuses_active.csv", active_costs)
    write_csv(ROOT / "deadlock_heroes_purchase_bonuses_active.csv", active_purchases)

    write_json(ROOT / "deadlock_heroes_base_growth_active.json", active_structured, True)
    write_json(ROOT / "deadlock_heroes_base_growth_all.json", all_structured, False)

    print(f"active heroes: {len(active_rows)}")
    print(f"all heroes: {len(all_rows)}")
    print("wrote:")
    for name in [
        "deadlock_heroes_base_growth_active.csv",
        "deadlock_heroes_base_growth_all.csv",
        "deadlock_heroes_stat_scaling_active.csv",
        "deadlock_heroes_cost_bonuses_active.csv",
        "deadlock_heroes_purchase_bonuses_active.csv",
        "deadlock_heroes_base_growth_active.json",
        "deadlock_heroes_base_growth_all.json",
    ]:
        print(f"- {name}")


if __name__ == "__main__":
    main()
