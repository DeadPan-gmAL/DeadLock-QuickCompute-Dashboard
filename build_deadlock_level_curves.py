import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_CSV = ROOT / "deadlock_heroes_base_growth_active.csv"
HTML_OUT = ROOT / "deadlock_hero_level_curves.html"
DATA_OUT = ROOT / "deadlock_hero_level_curves_data.json"
VALUES_OUT = ROOT / "deadlock_hero_level_values_long.csv"
INTERSECTIONS_OUT = ROOT / "deadlock_hero_stat_intersections.csv"

MIN_LEVEL = 1
MAX_LEVEL = 36
EPS = 1e-9


def f(row, key, default=0.0):
    value = row.get(key, "")
    if value in ("", None):
        return default
    try:
        return float(value)
    except ValueError:
        return default


def scale(row, target):
    stat = row.get(f"scaling_{target}_stat", "")
    if stat != "ETechPower":
        return 0.0
    return f(row, f"scaling_{target}_scale", 0.0)


def lin(c, b=0.0):
    return [0.0, b, c]


def mul_linear(left, right):
    # left/right are [0, b, c]. Product is a*t^2 + b*t + c.
    _, b1, c1 = left
    _, b2, c2 = right
    return [b1 * b2, b1 * c2 + b2 * c1, c1 * c2]


def poly_value(poly, level):
    t = level - 1.0
    return poly[0] * t * t + poly[1] * t + poly[2]


def roots_in_level_range(poly_a, poly_b):
    da = poly_a[0] - poly_b[0]
    db = poly_a[1] - poly_b[1]
    dc = poly_a[2] - poly_b[2]

    if abs(da) < EPS and abs(db) < EPS and abs(dc) < EPS:
        return "coincident"
    if abs(da) < EPS:
        if abs(db) < EPS:
            return []
        roots = [-dc / db]
    else:
        disc = db * db - 4.0 * da * dc
        if disc < -EPS:
            return []
        if abs(disc) <= EPS:
            roots = [-db / (2.0 * da)]
        else:
            sqrt_disc = math.sqrt(disc)
            roots = [(-db - sqrt_disc) / (2.0 * da), (-db + sqrt_disc) / (2.0 * da)]

    levels = []
    seen = set()
    for t in roots:
        level = t + 1.0
        if MIN_LEVEL - 1e-7 <= level <= MAX_LEVEL + 1e-7:
            if abs(level - round(level)) < 1e-7:
                level = float(round(level))
            key = round(level, 7)
            if key not in seen:
                seen.add(key)
                levels.append(level)
    return sorted(levels)


def build_attributes(row):
    spirit_power = lin(0.0, f(row, "growth_spirit_power_per_level"))
    bullet_damage = lin(
        f(row, "base_bullet_damage"),
        f(row, "growth_bullet_damage_per_level")
        + f(row, "growth_spirit_power_per_level") * scale(row, "EBulletDamage"),
    )
    clip_size = lin(
        f(row, "base_clip_size"),
        f(row, "growth_spirit_power_per_level") * scale(row, "EClipSize"),
    )
    shots_per_second = lin(
        f(row, "base_shots_per_second"),
        f(row, "growth_spirit_power_per_level") * scale(row, "ERoundsPerSecond"),
    )
    bullets = f(row, "base_bullets", 1.0)
    bullets_per_second = lin(
        f(row, "base_bullets_per_second"),
        f(row, "growth_spirit_power_per_level") * scale(row, "ERoundsPerSecond") * bullets,
    )
    damage_per_shot = lin(bullet_damage[2] * bullets, bullet_damage[1] * bullets)
    weapon_dps = mul_linear(bullet_damage, bullets_per_second)
    damage_per_magazine = mul_linear(lin(damage_per_shot[2], damage_per_shot[1]), clip_size)

    return {
        "max_health": lin(f(row, "base_max_health"), f(row, "growth_health_per_level")),
        "health_regen": lin(
            f(row, "base_health_regen"),
            f(row, "growth_spirit_power_per_level") * scale(row, "EBaseHealthRegen"),
        ),
        "bullet_armor_pct": lin(
            f(row, "base_bullet_armor_pct"),
            f(row, "growth_bullet_armor_pct_per_level")
            + f(row, "growth_spirit_power_per_level") * scale(row, "EBulletArmorDamageReduction"),
        ),
        "spirit_armor_pct": lin(
            f(row, "base_spirit_armor_pct"),
            f(row, "growth_spirit_resist_pct_per_level")
            + f(row, "growth_spirit_power_per_level") * scale(row, "ETechArmorDamageReduction"),
        ),
        "move_speed": lin(
            f(row, "base_move_speed"),
            f(row, "growth_spirit_power_per_level") * scale(row, "EMaxMoveSpeed"),
        ),
        "sprint_speed": lin(
            f(row, "base_sprint_speed"),
            f(row, "growth_spirit_power_per_level") * scale(row, "ESprintSpeed"),
        ),
        "crouch_speed": lin(f(row, "base_crouch_speed")),
        "move_acceleration": lin(f(row, "base_move_acceleration")),
        "stamina": lin(f(row, "base_stamina")),
        "stamina_regen_per_second": lin(f(row, "base_stamina_regen_per_second")),
        "light_melee_damage": lin(
            f(row, "base_light_melee_damage"),
            f(row, "growth_melee_damage_per_level"),
        ),
        "heavy_melee_damage": lin(
            f(row, "base_heavy_melee_damage"),
            f(row, "growth_melee_damage_per_level")
            + f(row, "growth_spirit_power_per_level") * scale(row, "EHeavyMeleeDamage"),
        ),
        "spirit_power": spirit_power,
        "bullet_damage": bullet_damage,
        "damage_per_shot": damage_per_shot,
        "clip_size": clip_size,
        "shots_per_second": shots_per_second,
        "bullets_per_second": bullets_per_second,
        "weapon_dps": weapon_dps,
        "damage_per_magazine": damage_per_magazine,
        "reload_duration": lin(f(row, "base_reload_duration")),
        "reload_speed": lin(f(row, "base_reload_speed")),
        "bullet_speed": lin(f(row, "base_bullet_speed")),
        "weapon_range": lin(f(row, "base_weapon_range"), f(row, "growth_bonus_attack_range_per_level")),
        "tech_range": lin(f(row, "base_tech_range")),
        "tech_duration": lin(f(row, "base_tech_duration")),
        "crit_damage_received_scale": lin(f(row, "base_crit_damage_received_scale")),
    }


ATTRIBUTES = [
    {"id": "max_health", "label": "Max Health", "unit": "HP", "group": "Vitality"},
    {"id": "health_regen", "label": "Health Regen", "unit": "HP/s", "group": "Vitality"},
    {"id": "bullet_armor_pct", "label": "Bullet Armor", "unit": "%", "group": "Vitality"},
    {"id": "spirit_armor_pct", "label": "Spirit Armor", "unit": "%", "group": "Vitality"},
    {"id": "move_speed", "label": "Move Speed", "unit": "m/s", "group": "Vitality"},
    {"id": "sprint_speed", "label": "Sprint Speed", "unit": "m/s", "group": "Vitality"},
    {"id": "crouch_speed", "label": "Crouch Speed", "unit": "m/s", "group": "Vitality"},
    {"id": "move_acceleration", "label": "Move Acceleration", "unit": "", "group": "Vitality"},
    {"id": "stamina", "label": "Stamina", "unit": "", "group": "Vitality"},
    {"id": "stamina_regen_per_second", "label": "Stamina Regen", "unit": "/s", "group": "Vitality"},
    {"id": "spirit_power", "label": "Spirit Power", "unit": "", "group": "Spirit"},
    {"id": "tech_range", "label": "Tech Range Multiplier", "unit": "x", "group": "Spirit"},
    {"id": "tech_duration", "label": "Tech Duration Multiplier", "unit": "x", "group": "Spirit"},
    {"id": "bullet_damage", "label": "Bullet Damage", "unit": "", "group": "Weapon"},
    {"id": "damage_per_shot", "label": "Damage per Shot", "unit": "", "group": "Weapon"},
    {"id": "clip_size", "label": "Clip Size", "unit": "", "group": "Weapon"},
    {"id": "shots_per_second", "label": "Shots per Second", "unit": "/s", "group": "Weapon"},
    {"id": "bullets_per_second", "label": "Bullets per Second", "unit": "/s", "group": "Weapon"},
    {"id": "weapon_dps", "label": "Weapon DPS", "unit": "DPS", "group": "Weapon"},
    {"id": "damage_per_magazine", "label": "Damage per Magazine", "unit": "", "group": "Weapon"},
    {"id": "reload_duration", "label": "Reload Duration", "unit": "s", "group": "Weapon"},
    {"id": "reload_speed", "label": "Reload Speed Multiplier", "unit": "x", "group": "Weapon"},
    {"id": "bullet_speed", "label": "Bullet Speed", "unit": "", "group": "Weapon"},
    {"id": "weapon_range", "label": "Weapon Range", "unit": "", "group": "Weapon"},
    {"id": "light_melee_damage", "label": "Light Melee Damage", "unit": "", "group": "Melee"},
    {"id": "heavy_melee_damage", "label": "Heavy Melee Damage", "unit": "", "group": "Melee"},
    {"id": "crit_damage_received_scale", "label": "Crit Damage Received Scale", "unit": "x", "group": "Other"},
]


def load_rows():
    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as csvfile:
        return list(csv.DictReader(csvfile))


def color_for_index(index, total):
    hue = (index * 137.508) % 360
    return f"hsl({hue:.1f}, 68%, 56%)"


def format_between(level):
    if abs(level - round(level)) < 1e-7:
        return str(int(round(level)))
    low = math.floor(level)
    high = math.ceil(level)
    if low < MIN_LEVEL:
        return f"<{high}"
    if high > MAX_LEVEL:
        return f"{low}+"
    return f"{low}-{high}"


def build_payload():
    rows = load_rows()
    heroes = []
    curves = {}
    for idx, row in enumerate(rows):
        hero_id = row["hero_id"]
        attrs = build_attributes(row)
        heroes.append(
            {
                "id": hero_id,
                "name": row["hero_name"],
                "heroType": row["hero_type"],
                "gunTag": row["gun_tag"],
                "color": color_for_index(idx, len(rows)),
            }
        )
        curves[hero_id] = {
            attr["id"]: [round(v, 12) for v in attrs[attr["id"]]]
            for attr in ATTRIBUTES
        }

    intersections = []
    coincident = []
    for attr in ATTRIBUTES:
        attr_id = attr["id"]
        for i, hero_a in enumerate(heroes):
            for hero_b in heroes[i + 1 :]:
                poly_a = curves[hero_a["id"]][attr_id]
                poly_b = curves[hero_b["id"]][attr_id]
                levels = roots_in_level_range(poly_a, poly_b)
                if levels == "coincident":
                    coincident.append(
                        {
                            "attribute_id": attr_id,
                            "attribute": attr["label"],
                            "hero_a": hero_a["name"],
                            "hero_b": hero_b["name"],
                        }
                    )
                    continue
                for level in levels:
                    value = poly_value(poly_a, level)
                    intersections.append(
                        {
                            "attribute_id": attr_id,
                            "attribute": attr["label"],
                            "hero_a_id": hero_a["id"],
                            "hero_a": hero_a["name"],
                            "hero_b_id": hero_b["id"],
                            "hero_b": hero_b["name"],
                            "level": round(level, 6),
                            "between_levels": format_between(level),
                            "value": round(value, 6),
                            "is_level_1_tie": abs(level - 1.0) < 1e-7,
                        }
                    )

    return {
        "source": SOURCE_CSV.name,
        "minLevel": MIN_LEVEL,
        "maxLevel": MAX_LEVEL,
        "formula": "t=level-1; value=a*t*t+b*t+c. Direct level growth and ETechPower stat scaling are included where source columns exist.",
        "attributes": ATTRIBUTES,
        "heroes": heroes,
        "curves": curves,
        "intersections": intersections,
        "coincident": coincident,
    }


def write_values(payload):
    with VALUES_OUT.open("w", encoding="utf-8-sig", newline="") as csvfile:
        fieldnames = ["attribute_id", "attribute", "hero_id", "hero_name", "level", "value"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        attr_by_id = {attr["id"]: attr for attr in payload["attributes"]}
        hero_by_id = {hero["id"]: hero for hero in payload["heroes"]}
        for attr_id, attr in attr_by_id.items():
            for hero_id, hero in hero_by_id.items():
                poly = payload["curves"][hero_id][attr_id]
                for level in range(MIN_LEVEL, MAX_LEVEL + 1):
                    writer.writerow(
                        {
                            "attribute_id": attr_id,
                            "attribute": attr["label"],
                            "hero_id": hero_id,
                            "hero_name": hero["name"],
                            "level": level,
                            "value": round(poly_value(poly, level), 6),
                        }
                    )


def write_intersections(payload):
    with INTERSECTIONS_OUT.open("w", encoding="utf-8-sig", newline="") as csvfile:
        fieldnames = [
            "attribute_id",
            "attribute",
            "hero_a_id",
            "hero_a",
            "hero_b_id",
            "hero_b",
            "level",
            "between_levels",
            "value",
            "is_level_1_tie",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(
            payload["intersections"],
            key=lambda r: (r["attribute"], r["level"], r["hero_a"], r["hero_b"]),
        ):
            writer.writerow(row)


def write_html(payload):
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    html = HTML_TEMPLATE.replace("__PAYLOAD_JSON__", payload_json)
    HTML_OUT.write_text(html, encoding="utf-8")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Deadlock Hero Level Curves</title>
  <style>
    :root {
      --bg: #0d0f0f;
      --panel: #151818;
      --panel-2: #1c2020;
      --ink: #f0ece2;
      --muted: #a49e91;
      --line: #303635;
      --accent: #d6b35a;
      --danger: #d86752;
      --good: #5cb58a;
      --font: "Aptos", "Segoe UI", sans-serif;
      --mono: "Cascadia Mono", "Consolas", monospace;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px) 0 0 / 42px 42px,
        linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px) 0 0 / 42px 42px,
        var(--bg);
      color: var(--ink);
      font-family: var(--font);
      letter-spacing: 0;
    }
    header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 22px 14px;
      border-bottom: 1px solid var(--line);
      background: rgba(13, 15, 15, .96);
      position: sticky;
      top: 0;
      z-index: 4;
    }
    h1 {
      margin: 0;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: .02em;
    }
    .meta {
      color: var(--muted);
      font-size: 12px;
      font-family: var(--mono);
      white-space: nowrap;
    }
    .app {
      display: grid;
      grid-template-columns: 330px minmax(0, 1fr);
      min-height: calc(100vh - 57px);
    }
    aside {
      border-right: 1px solid var(--line);
      background: rgba(21, 24, 24, .94);
      padding: 16px;
      overflow: auto;
      max-height: calc(100vh - 57px);
      position: sticky;
      top: 57px;
    }
    main {
      min-width: 0;
      padding: 16px 18px 24px;
    }
    label {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      margin-bottom: 6px;
      text-transform: uppercase;
    }
    select, input {
      width: 100%;
      border: 1px solid var(--line);
      background: #101313;
      color: var(--ink);
      border-radius: 6px;
      padding: 9px 10px;
      font: 13px var(--font);
      outline: none;
    }
    select:focus, input:focus { border-color: var(--accent); }
    .control { margin-bottom: 14px; }
    .button-row {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 12px;
    }
    button {
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: var(--ink);
      border-radius: 6px;
      padding: 8px 10px;
      font: 12px var(--font);
      cursor: pointer;
    }
    button:hover { border-color: var(--accent); }
    .check {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 4px;
      border-bottom: 1px solid rgba(255,255,255,.035);
      font-size: 12px;
    }
    .check input {
      width: auto;
      margin: 0;
      accent-color: var(--accent);
    }
    .swatch {
      width: 10px;
      height: 10px;
      border-radius: 2px;
      flex: 0 0 auto;
    }
    .hero-list {
      max-height: 410px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #101313;
    }
    .chart-card, .table-card {
      border: 1px solid var(--line);
      background: rgba(21, 24, 24, .92);
      border-radius: 8px;
      overflow: hidden;
    }
    .chart-head, .table-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
    }
    .title {
      font-size: 15px;
      font-weight: 700;
    }
    .subtitle {
      color: var(--muted);
      font-size: 12px;
      font-family: var(--mono);
      margin-top: 2px;
    }
    #chart {
      width: 100%;
      height: 560px;
      display: block;
      background: linear-gradient(180deg, rgba(255,255,255,.018), transparent);
    }
    .axis text {
      fill: var(--muted);
      font: 11px var(--mono);
    }
    .axis line, .axis path, .grid line {
      stroke: var(--line);
      stroke-width: 1;
    }
    .grid line { opacity: .72; }
    .curve {
      fill: none;
      stroke-width: 1.6;
      opacity: .78;
    }
    .curve.dim { opacity: .13; }
    .curve.hot {
      stroke-width: 3.1;
      opacity: 1;
    }
    .tooltip {
      position: fixed;
      pointer-events: none;
      background: #090b0b;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 10px;
      color: var(--ink);
      font: 12px var(--mono);
      max-width: 310px;
      box-shadow: 0 14px 28px rgba(0,0,0,.35);
      display: none;
      z-index: 9;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 14px 0;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(28,32,32,.92);
      padding: 10px 12px;
    }
    .stat b {
      display: block;
      font: 18px var(--mono);
      color: var(--accent);
      margin-bottom: 3px;
    }
    .stat span {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
    }
    .table-card { margin-top: 14px; }
    .toggle {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      user-select: none;
    }
    .toggle input { width: auto; accent-color: var(--accent); }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    th, td {
      border-bottom: 1px solid rgba(255,255,255,.055);
      padding: 8px 10px;
      text-align: left;
      white-space: nowrap;
    }
    th {
      color: var(--muted);
      font-size: 10px;
      text-transform: uppercase;
      background: #111414;
      position: sticky;
      top: 0;
      z-index: 1;
    }
    tbody tr:hover { background: rgba(214,179,90,.08); }
    .scroll-table {
      max-height: 430px;
      overflow: auto;
    }
    .note {
      margin-top: 14px;
      padding: 11px 12px;
      border: 1px solid rgba(214,179,90,.28);
      background: rgba(214,179,90,.075);
      border-radius: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }
    @media (max-width: 980px) {
      .app { grid-template-columns: 1fr; }
      aside {
        position: static;
        max-height: none;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }
      .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      header { align-items: flex-start; flex-direction: column; }
      .meta { white-space: normal; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Deadlock Selectable Hero Level Curves</h1>
    <div class="meta">Levels 1-36 · active selectable heroes · direct growth + ETechPower stat scaling</div>
  </header>
  <div class="app">
    <aside>
      <div class="control">
        <label for="attribute">Attribute</label>
        <select id="attribute"></select>
      </div>
      <div class="control">
        <label for="heroSearch">Filter Heroes</label>
        <input id="heroSearch" placeholder="type a hero name" />
      </div>
      <div class="button-row">
        <button id="allBtn">All</button>
        <button id="noneBtn">None</button>
        <button id="topBtn">Top 8</button>
      </div>
      <div class="hero-list" id="heroList"></div>
      <div class="note">
        Formula: value = a*t^2 + b*t + c, t = level - 1. Most curves are linear. Derived weapon attributes can become quadratic when damage, clip size, or rounds/sec scale.
      </div>
    </aside>
    <main>
      <section class="chart-card">
        <div class="chart-head">
          <div>
            <div class="title" id="chartTitle"></div>
            <div class="subtitle" id="chartSubtitle"></div>
          </div>
          <label class="toggle"><input type="checkbox" id="highlightCrossings" checked /> mark crossings</label>
        </div>
        <svg id="chart" role="img" aria-label="Hero level curves"></svg>
      </section>
      <section class="stats">
        <div class="stat"><b id="selectedCount">0</b><span>Selected heroes</span></div>
        <div class="stat"><b id="crossingCount">0</b><span>Visible crossings</span></div>
        <div class="stat"><b id="hiddenLevelOne">0</b><span>Level 1 ties hidden</span></div>
        <div class="stat"><b id="coincidentCount">0</b><span>Identical full curves</span></div>
      </section>
      <section class="table-card">
        <div class="table-head">
          <div>
            <div class="title">Crossing Points</div>
            <div class="subtitle">Fractional levels show exact curve intersections; "between" shows the adjacent integer levels.</div>
          </div>
          <label class="toggle"><input type="checkbox" id="includeLevelOne" /> include level 1 ties</label>
        </div>
        <div class="scroll-table">
          <table>
            <thead>
              <tr>
                <th>Level</th>
                <th>Between</th>
                <th>Value</th>
                <th>Hero A</th>
                <th>Hero B</th>
              </tr>
            </thead>
            <tbody id="crossingRows"></tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
  <div class="tooltip" id="tooltip"></div>
  <script>
    const DATA = __PAYLOAD_JSON__;
    const attrSelect = document.getElementById("attribute");
    const heroSearch = document.getElementById("heroSearch");
    const heroList = document.getElementById("heroList");
    const svg = document.getElementById("chart");
    const tooltip = document.getElementById("tooltip");
    const includeLevelOne = document.getElementById("includeLevelOne");
    const highlightCrossings = document.getElementById("highlightCrossings");
    const selected = new Set(DATA.heroes.map(h => h.id));
    let hotHeroes = new Set();

    function value(poly, level) {
      const t = level - 1;
      return poly[0] * t * t + poly[1] * t + poly[2];
    }

    function fmt(v) {
      if (!Number.isFinite(v)) return "";
      const abs = Math.abs(v);
      if (abs >= 1000) return v.toFixed(0);
      if (abs >= 100) return v.toFixed(1);
      if (abs >= 10) return v.toFixed(2);
      return v.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
    }

    function currentAttr() {
      return DATA.attributes.find(a => a.id === attrSelect.value);
    }

    function initAttributes() {
      const groups = new Map();
      DATA.attributes.forEach(attr => {
        if (!groups.has(attr.group)) groups.set(attr.group, []);
        groups.get(attr.group).push(attr);
      });
      groups.forEach((attrs, group) => {
        const og = document.createElement("optgroup");
        og.label = group;
        attrs.forEach(attr => {
          const opt = document.createElement("option");
          opt.value = attr.id;
          opt.textContent = attr.label;
          og.appendChild(opt);
        });
        attrSelect.appendChild(og);
      });
      attrSelect.value = "max_health";
    }

    function renderHeroList() {
      const query = heroSearch.value.trim().toLowerCase();
      heroList.innerHTML = "";
      DATA.heroes
        .filter(hero => hero.name.toLowerCase().includes(query))
        .forEach(hero => {
          const label = document.createElement("label");
          label.className = "check";
          const cb = document.createElement("input");
          cb.type = "checkbox";
          cb.checked = selected.has(hero.id);
          cb.addEventListener("change", () => {
            cb.checked ? selected.add(hero.id) : selected.delete(hero.id);
            renderAll();
          });
          const swatch = document.createElement("span");
          swatch.className = "swatch";
          swatch.style.background = hero.color;
          const name = document.createElement("span");
          name.textContent = hero.name;
          label.append(cb, swatch, name);
          heroList.appendChild(label);
        });
    }

    function visibleHeroes() {
      return DATA.heroes.filter(hero => selected.has(hero.id));
    }

    function pathFor(poly, xScale, yScale) {
      const parts = [];
      const steps = 220;
      for (let i = 0; i <= steps; i++) {
        const level = DATA.minLevel + (DATA.maxLevel - DATA.minLevel) * i / steps;
        const x = xScale(level);
        const y = yScale(value(poly, level));
        parts.push(`${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`);
      }
      return parts.join(" ");
    }

    function makeSvg(tag, attrs = {}) {
      const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
      Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
      return el;
    }

    function renderChart() {
      const attr = currentAttr();
      const heroes = visibleHeroes();
      const rect = svg.getBoundingClientRect();
      const width = Math.max(760, rect.width || 1000);
      const height = 560;
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
      svg.innerHTML = "";

      const margin = { top: 22, right: 32, bottom: 46, left: 72 };
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;
      const allValues = [];
      heroes.forEach(hero => {
        const poly = DATA.curves[hero.id][attr.id];
        for (let level = DATA.minLevel; level <= DATA.maxLevel; level++) {
          allValues.push(value(poly, level));
        }
      });
      let minY = Math.min(...allValues);
      let maxY = Math.max(...allValues);
      if (!Number.isFinite(minY) || !Number.isFinite(maxY)) {
        minY = 0; maxY = 1;
      }
      if (Math.abs(maxY - minY) < 1e-7) {
        minY -= 1; maxY += 1;
      }
      const pad = (maxY - minY) * 0.08;
      minY -= pad; maxY += pad;
      const xScale = level => margin.left + (level - DATA.minLevel) / (DATA.maxLevel - DATA.minLevel) * innerW;
      const yScale = y => margin.top + (maxY - y) / (maxY - minY) * innerH;

      const grid = makeSvg("g", { class: "grid" });
      for (let level = 1; level <= 36; level += 5) {
        const x = xScale(level);
        grid.appendChild(makeSvg("line", { x1: x, y1: margin.top, x2: x, y2: height - margin.bottom }));
      }
      for (let i = 0; i <= 5; i++) {
        const y = margin.top + innerH * i / 5;
        grid.appendChild(makeSvg("line", { x1: margin.left, y1: y, x2: width - margin.right, y2: y }));
      }
      svg.appendChild(grid);

      const axis = makeSvg("g", { class: "axis" });
      axis.appendChild(makeSvg("line", { x1: margin.left, y1: height - margin.bottom, x2: width - margin.right, y2: height - margin.bottom }));
      axis.appendChild(makeSvg("line", { x1: margin.left, y1: margin.top, x2: margin.left, y2: height - margin.bottom }));
      for (let level = 1; level <= 36; level += 5) {
        const x = xScale(level);
        axis.appendChild(makeSvg("line", { x1: x, y1: height - margin.bottom, x2: x, y2: height - margin.bottom + 5 }));
        const text = makeSvg("text", { x, y: height - 16, "text-anchor": "middle" });
        text.textContent = level;
        axis.appendChild(text);
      }
      for (let i = 0; i <= 5; i++) {
        const yVal = maxY - (maxY - minY) * i / 5;
        const y = margin.top + innerH * i / 5;
        axis.appendChild(makeSvg("line", { x1: margin.left - 5, y1: y, x2: margin.left, y2: y }));
        const text = makeSvg("text", { x: margin.left - 10, y: y + 4, "text-anchor": "end" });
        text.textContent = fmt(yVal);
        axis.appendChild(text);
      }
      svg.appendChild(axis);

      heroes.forEach(hero => {
        const poly = DATA.curves[hero.id][attr.id];
        const path = makeSvg("path", {
          class: `curve ${hotHeroes.size && !hotHeroes.has(hero.id) ? "dim" : ""} ${hotHeroes.has(hero.id) ? "hot" : ""}`,
          d: pathFor(poly, xScale, yScale),
          stroke: hero.color,
          "data-hero": hero.id,
        });
        path.addEventListener("mouseenter", () => {
          hotHeroes = new Set([hero.id]);
          renderChart();
        });
        path.addEventListener("mouseleave", () => {
          hotHeroes = new Set();
          renderChart();
        });
        svg.appendChild(path);
      });

      if (highlightCrossings.checked) {
        getVisibleIntersections(attr.id).slice(0, 450).forEach(row => {
          const cx = xScale(row.level);
          const cy = yScale(row.value);
          const dot = makeSvg("circle", {
            cx,
            cy,
            r: row.is_level_1_tie ? 2.2 : 3.2,
            fill: row.is_level_1_tie ? "var(--muted)" : "var(--accent)",
            opacity: row.is_level_1_tie ? .42 : .8,
          });
          svg.appendChild(dot);
        });
      }

      const overlay = makeSvg("rect", {
        x: margin.left,
        y: margin.top,
        width: innerW,
        height: innerH,
        fill: "transparent",
      });
      overlay.addEventListener("mousemove", event => {
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const cursor = pt.matrixTransform(svg.getScreenCTM().inverse());
        const level = Math.max(DATA.minLevel, Math.min(DATA.maxLevel, DATA.minLevel + (cursor.x - margin.left) / innerW * (DATA.maxLevel - DATA.minLevel)));
        const nearest = Math.round(level);
        const rows = heroes.map(hero => {
          const v = value(DATA.curves[hero.id][attr.id], nearest);
          return { hero, v };
        }).sort((a, b) => b.v - a.v).slice(0, 10);
        tooltip.style.display = "block";
        tooltip.style.left = `${event.clientX + 14}px`;
        tooltip.style.top = `${event.clientY + 14}px`;
        tooltip.innerHTML = `<b>${attr.label} · Level ${nearest}</b><br>` + rows.map(r => `<span style="color:${r.hero.color}">■</span> ${r.hero.name}: ${fmt(r.v)}`).join("<br>");
      });
      overlay.addEventListener("mouseleave", () => tooltip.style.display = "none");
      svg.appendChild(overlay);
    }

    function getVisibleIntersections(attrId) {
      return DATA.intersections
        .filter(row => row.attribute_id === attrId)
        .filter(row => selected.has(row.hero_a_id) && selected.has(row.hero_b_id))
        .filter(row => includeLevelOne.checked || !row.is_level_1_tie)
        .sort((a, b) => a.level - b.level || a.hero_a.localeCompare(b.hero_a) || a.hero_b.localeCompare(b.hero_b));
    }

    function renderTable() {
      const attr = currentAttr();
      const rows = getVisibleIntersections(attr.id);
      const hidden = DATA.intersections
        .filter(row => row.attribute_id === attr.id && row.is_level_1_tie)
        .filter(row => selected.has(row.hero_a_id) && selected.has(row.hero_b_id)).length;
      const coincident = DATA.coincident
        .filter(row => row.attribute_id === attr.id)
        .filter(row => {
          const a = DATA.heroes.find(h => h.name === row.hero_a);
          const b = DATA.heroes.find(h => h.name === row.hero_b);
          return a && b && selected.has(a.id) && selected.has(b.id);
        }).length;
      document.getElementById("crossingRows").innerHTML = rows.slice(0, 700).map(row => `
        <tr data-a="${row.hero_a_id}" data-b="${row.hero_b_id}">
          <td>${Number(row.level).toFixed(3).replace(/\.000$/, "")}</td>
          <td>${row.between_levels}</td>
          <td>${fmt(row.value)}</td>
          <td>${row.hero_a}</td>
          <td>${row.hero_b}</td>
        </tr>
      `).join("") || `<tr><td colspan="5">No unique crossing points in levels 1-36 for the current selection.</td></tr>`;
      document.querySelectorAll("#crossingRows tr[data-a]").forEach(tr => {
        tr.addEventListener("mouseenter", () => {
          hotHeroes = new Set([tr.dataset.a, tr.dataset.b]);
          renderChart();
        });
        tr.addEventListener("mouseleave", () => {
          hotHeroes = new Set();
          renderChart();
        });
      });
      document.getElementById("crossingCount").textContent = rows.length;
      document.getElementById("hiddenLevelOne").textContent = includeLevelOne.checked ? 0 : hidden;
      document.getElementById("coincidentCount").textContent = coincident;
    }

    function renderHeader() {
      const attr = currentAttr();
      const heroCount = visibleHeroes().length;
      document.getElementById("chartTitle").textContent = attr.label;
      document.getElementById("chartSubtitle").textContent = `${attr.group}${attr.unit ? " · " + attr.unit : ""} · ${heroCount} heroes`;
      document.getElementById("selectedCount").textContent = heroCount;
    }

    function renderAll() {
      renderHeader();
      renderHeroList();
      renderChart();
      renderTable();
    }

    document.getElementById("allBtn").addEventListener("click", () => {
      DATA.heroes.forEach(hero => selected.add(hero.id));
      renderAll();
    });
    document.getElementById("noneBtn").addEventListener("click", () => {
      selected.clear();
      renderAll();
    });
    document.getElementById("topBtn").addEventListener("click", () => {
      const attr = currentAttr();
      const top = DATA.heroes
        .map(hero => ({ hero, v: value(DATA.curves[hero.id][attr.id], DATA.maxLevel) }))
        .sort((a, b) => b.v - a.v)
        .slice(0, 8)
        .map(x => x.hero.id);
      selected.clear();
      top.forEach(id => selected.add(id));
      renderAll();
    });
    attrSelect.addEventListener("change", renderAll);
    heroSearch.addEventListener("input", renderHeroList);
    includeLevelOne.addEventListener("change", renderAll);
    highlightCrossings.addEventListener("change", renderChart);
    window.addEventListener("resize", renderChart);

    initAttributes();
    renderAll();
  </script>
</body>
</html>
"""


def main():
    payload = build_payload()
    write_values(payload)
    write_intersections(payload)
    DATA_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_html(payload)
    print(f"heroes: {len(payload['heroes'])}")
    print(f"attributes: {len(payload['attributes'])}")
    print(f"intersections: {len(payload['intersections'])}")
    print(f"coincident curves: {len(payload['coincident'])}")
    print(f"wrote: {HTML_OUT.name}")
    print(f"wrote: {VALUES_OUT.name}")
    print(f"wrote: {INTERSECTIONS_OUT.name}")


if __name__ == "__main__":
    main()
