import csv
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HEROES_JSON = ROOT / "heroes_assets_v2.json"
ITEMS_JSON = ROOT / "items_assets_v2.json"
BASE_CSV = ROOT / "deadlock_heroes_base_growth_active.csv"
HTML_OUT = ROOT / "deadlock_hero_level_curves.html"
DATA_OUT = ROOT / "deadlock_hero_level_curves_data.json"
ABILITIES_CSV = ROOT / "deadlock_hero_abilities.csv"
ABILITIES_JSON = ROOT / "deadlock_hero_abilities_full.json"
ABILITY_EFFECTS_CSV = ROOT / "deadlock_hero_ability_stat_effects.csv"
ITEM_EFFECTS_CSV = ROOT / "deadlock_item_passive_effects.csv"


ATTRIBUTES = [
    {"id": "max_health", "label": "最大生命值", "labelEn": "Max Health", "unit": "HP", "group": "活力", "groupEn": "Vitality"},
    {"id": "health_regen", "label": "生命恢复", "labelEn": "Health Regen", "unit": "HP/s", "group": "活力", "groupEn": "Vitality"},
    {"id": "bullet_armor_pct", "label": "子弹抗性", "labelEn": "Bullet Resist", "unit": "%", "group": "活力", "groupEn": "Vitality"},
    {"id": "spirit_armor_pct", "label": "元灵抗性", "labelEn": "Spirit Resist", "unit": "%", "group": "活力", "groupEn": "Vitality"},
    {"id": "move_speed", "label": "移动速度", "labelEn": "Move Speed", "unit": "m/s", "group": "活力", "groupEn": "Vitality"},
    {"id": "sprint_speed", "label": "冲刺速度", "labelEn": "Sprint Speed", "unit": "m/s", "group": "活力", "groupEn": "Vitality"},
    {"id": "crouch_speed", "label": "蹲伏速度", "labelEn": "Crouch Speed", "unit": "m/s", "group": "活力", "groupEn": "Vitality"},
    {"id": "move_acceleration", "label": "移动加速度", "labelEn": "Move Acceleration", "unit": "", "group": "活力", "groupEn": "Vitality"},
    {"id": "stamina", "label": "耐力", "labelEn": "Stamina", "unit": "", "group": "活力", "groupEn": "Vitality"},
    {"id": "stamina_regen_per_second", "label": "耐力恢复", "labelEn": "Stamina Regen", "unit": "/s", "group": "活力", "groupEn": "Vitality"},
    {"id": "spirit_power", "label": "元灵力量", "labelEn": "Spirit Power", "unit": "", "group": "元灵", "groupEn": "Spirit"},
    {"id": "barrier_health", "label": "技能护盾", "labelEn": "Barrier Health", "unit": "HP", "group": "元灵", "groupEn": "Spirit"},
    {"id": "tech_range", "label": "技能范围倍率", "labelEn": "Ability Range Multiplier", "unit": "x", "group": "元灵", "groupEn": "Spirit"},
    {"id": "tech_duration", "label": "技能持续倍率", "labelEn": "Ability Duration Multiplier", "unit": "x", "group": "元灵", "groupEn": "Spirit"},
    {"id": "bullet_damage", "label": "子弹伤害", "labelEn": "Bullet Damage", "unit": "", "group": "武器", "groupEn": "Weapon"},
    {"id": "damage_per_shot", "label": "每发伤害", "labelEn": "Damage Per Shot", "unit": "", "group": "武器", "groupEn": "Weapon"},
    {"id": "clip_size", "label": "弹匣容量", "labelEn": "Clip Size", "unit": "", "group": "武器", "groupEn": "Weapon"},
    {"id": "shots_per_second", "label": "每秒射击次数", "labelEn": "Shots Per Second", "unit": "/s", "group": "武器", "groupEn": "Weapon"},
    {"id": "bullets_per_second", "label": "每秒子弹数", "labelEn": "Bullets Per Second", "unit": "/s", "group": "武器", "groupEn": "Weapon"},
    {"id": "weapon_dps", "label": "武器 DPS", "labelEn": "Weapon DPS", "unit": "DPS", "group": "武器", "groupEn": "Weapon"},
    {"id": "damage_per_magazine", "label": "单弹匣伤害", "labelEn": "Damage Per Magazine", "unit": "", "group": "武器", "groupEn": "Weapon"},
    {"id": "reload_duration", "label": "换弹时间", "labelEn": "Reload Time", "unit": "s", "group": "武器", "groupEn": "Weapon"},
    {"id": "reload_speed", "label": "换弹速度倍率", "labelEn": "Reload Speed Multiplier", "unit": "x", "group": "武器", "groupEn": "Weapon"},
    {"id": "bullet_speed", "label": "子弹速度", "labelEn": "Bullet Speed", "unit": "", "group": "武器", "groupEn": "Weapon"},
    {"id": "weapon_range", "label": "武器射程", "labelEn": "Weapon Range", "unit": "", "group": "武器", "groupEn": "Weapon"},
    {"id": "light_melee_damage", "label": "轻近战伤害", "labelEn": "Light Melee Damage", "unit": "", "group": "近战", "groupEn": "Melee"},
    {"id": "heavy_melee_damage", "label": "重近战伤害", "labelEn": "Heavy Melee Damage", "unit": "", "group": "近战", "groupEn": "Melee"},
    {"id": "crit_damage_received_scale", "label": "受暴击伤害倍率", "labelEn": "Crit Damage Taken Scale", "unit": "x", "group": "其他", "groupEn": "Other"},
]


# The current public data dumps in this workspace do not expose Valve localization
# tokens. Keep the Simplified Chinese labels in one table so an official
# citadel_schinese.txt export can replace them without touching rendering logic.
HERO_ZH_NAMES = {
    "Abrams": "艾布拉姆斯",
    "Apollo": "阿波罗",
    "Bebop": "比波普",
    "Billy": "比利",
    "Calico": "卡利科",
    "Celeste": "塞莱斯特",
    "Drifter": "漂泊者",
    "Dynamo": "戴纳摩",
    "Graves": "格雷夫斯",
    "Grey Talon": "灰爪",
    "Haze": "迷雾",
    "Holliday": "霍利迪",
    "Infernus": "因弗纳斯",
    "Ivy": "艾薇",
    "Kelvin": "凯尔文",
    "Lady Geist": "盖斯特夫人",
    "Lash": "拉什",
    "McGinnis": "麦金尼斯",
    "Mina": "米娜",
    "Mirage": "幻影",
    "Mo & Krill": "莫和克里尔",
    "Paige": "佩奇",
    "Paradox": "悖论",
    "Pocket": "口袋",
    "Rem": "雷姆",
    "Seven": "七号",
    "Shiv": "希夫",
    "Silver": "银狼",
    "Sinclair": "辛克莱",
    "The Doorman": "门童",
    "Venator": "维纳托",
    "Victor": "维克托",
    "Vindicta": "温蒂克塔",
    "Viscous": "粘液",
    "Vyper": "蝰蛇",
    "Warden": "典狱长",
    "Wraith": "幽灵",
    "Yamato": "大和",
}


ABILITY_ZH_NAMES = {
    "Abrams": {
        "Siphon Life": "汲取生命",
        "Shoulder Charge": "肩部冲锋",
        "Infernal Resilience": "地狱韧性",
        "Seismic Impact": "地震冲击",
    },
    "Apollo": {
        "Disengaging Sigil": "退避符印",
        "Riposte": "还击",
        "Flawless Advance": "无瑕突进",
        "Itani Lo Sahn": "伊塔尼罗桑",
    },
    "Bebop": {
        "Exploding Uppercut": "爆裂上勾拳",
        "Sticky Bomb": "黏性炸弹",
        "Grapple Arm": "钩爪臂",
        "Hyper Beam": "超级光束",
    },
    "Billy": {
        "Bashdown": "重击压制",
        "Rising Ram": "上升冲撞",
        "Blasted": "爆破",
        "Chain Gang": "锁链帮",
    },
    "Calico": {
        "Gloom Bombs": "幽影炸弹",
        "Leaping Slash": "跃斩",
        "Ava": "艾娃",
        "Return to Shadows": "归于暗影",
    },
    "Celeste": {
        "Light Eater": "噬光",
        "Dazzling Trick": "炫目戏法",
        "Radiant Daggers": "辉光匕首",
        "Shining Wonder": "闪耀奇迹",
    },
    "Drifter": {
        "Rend": "撕裂",
        "Stalker's Mark": "潜猎者印记",
        "Bloodscent": "血腥气息",
        "Eternal Night": "永夜",
    },
    "Dynamo": {
        "Kinetic Pulse": "动能脉冲",
        "Quantum Entanglement": "量子纠缠",
        "Rejuvenating Aurora": "复苏极光",
        "Singularity": "奇点",
    },
    "Graves": {
        "Jar of Dead": "死灵之罐",
        "Grasping Hands": "攫取之手",
        "Essence Theft": "精魂窃取",
        "Borrowed Decree": "借来的敕令",
    },
    "Grey Talon": {
        "Charged Shot": "蓄力射击",
        "Rain of Arrows": "箭雨",
        "Spirit Snare": "元灵陷阱",
        "Guided Owl": "制导猫头鹰",
    },
    "Haze": {
        "Sleep Dagger": "催眠匕首",
        "Smoke Bomb": "烟雾弹",
        "Fixation": "凝视",
        "Bullet Dance": "子弹之舞",
    },
    "Holliday": {
        "Powder Keg": "火药桶",
        "Bounce Pad": "弹跳垫",
        "Crackshot": "神枪手",
        "Spirit Lasso": "元灵套索",
    },
    "Infernus": {
        "Napalm": "凝固汽油弹",
        "Flame Dash": "烈焰冲刺",
        "Afterburn": "余烬灼烧",
        "Concussive Combustion": "震荡燃爆",
    },
    "Ivy": {
        "Entangling Thorns": "缠绕荆棘",
        "Kudzu Connection": "葛藤联结",
        "Stone Form": "石像形态",
        "Air Drop": "空投",
    },
    "Kelvin": {
        "Frost Grenade": "冰霜手雷",
        "Ice Path": "冰径",
        "Arctic Beam": "极寒光束",
        "Frozen Shelter": "冰封庇护",
    },
    "Lady Geist": {
        "Essence Bomb": "精魂炸弹",
        "Life Drain": "生命吸取",
        "Malice": "恶意",
        "Soul Exchange": "灵魂交换",
    },
    "Lash": {
        "Ground Strike": "地面猛击",
        "Grapple": "抓钩",
        "Flog": "鞭笞",
        "Death Slam": "死亡重摔",
    },
    "McGinnis": {
        "Mini Turret": "迷你炮塔",
        "Medicinal Specter": "治疗幽魂",
        "Spectral Wall": "幽魂墙",
        "Heavy Barrage": "重型弹幕",
    },
    "Mina": {
        "Rake": "利爪横扫",
        "Sanguine Retreat": "血色撤退",
        "Love Bites": "爱之咬",
        "Nox Nostra": "我等之夜",
    },
    "Mirage": {
        "Fire Scarabs": "火焰圣甲虫",
        "Dust Devil": "尘魔",
        "Djinn's Mark": "灯神印记",
        "Traveler": "旅者",
    },
    "Mo & Krill": {
        "Scorn": "蔑视",
        "Burrow": "潜地",
        "Sand Blast": "沙暴冲击",
        "Combo": "连击",
    },
    "Paige": {
        "Bookwyrm": "书龙",
        "Plot Armor": "剧情护甲",
        "Captivating Read": "入迷阅读",
        "Rallying Charge": "集结冲锋",
    },
    "Paradox": {
        "Pulse Grenade": "脉冲手雷",
        "Time Wall": "时间墙",
        "Kinetic Carbine": "动能卡宾枪",
        "Paradoxical Swap": "悖论置换",
    },
    "Pocket": {
        "Barrage": "弹幕",
        "Flying Cloak": "飞行斗篷",
        "Enchanter's Satchel": "附魔师挎包",
        "Affliction": "苦痛",
    },
    "Rem": {
        "Pillow Toss": "枕头投掷",
        "Tag Along": "结伴同行",
        "Lil Helpers": "小帮手",
        "Naptime": "午睡时间",
    },
    "Seven": {
        "Lightning Ball": "闪电球",
        "Static Charge": "静电充能",
        "Power Surge": "能量涌动",
        "Storm Cloud": "风暴云",
    },
    "Shiv": {
        "Serrated Knives": "锯齿飞刀",
        "Slice and Dice": "切割乱舞",
        "Bloodletting": "放血",
        "Killing Blow": "致命一击",
    },
    "Silver": {
        "Slam Fire": "猛击射击",
        "Boot Kick": "靴踢",
        "Entangling Bola": "缠绕绳索",
        "Lycan Curse": "狼人诅咒",
    },
    "Sinclair": {
        "Vexing Bolt": "恼人飞弹",
        "Spectral Assistant": "幽魂助手",
        "Rabbit Hex": "兔化咒",
        "Audience Participation": "观众参与",
    },
    "The Doorman": {
        "Call Bell": "召唤铃",
        "Doorway": "门道",
        "Luggage Cart": "行李车",
        "Hotel Guest": "住店客人",
    },
    "Venator": {
        "Consecrating Grenade": "圣化手雷",
        "Gutshot": "腹部射击",
        "Hex-Lined Snap Trap": "咒纹夹陷阱",
        "Ira Domini": "主之怒",
    },
    "Victor": {
        "Pain Battery": "痛苦电池",
        "Jumpstart": "强启",
        "Aura of Suffering": "苦痛光环",
        "Shocking Reanimation": "电击复苏",
    },
    "Vindicta": {
        "Stake": "木桩",
        "Flight": "飞行",
        "Crow Familiar": "乌鸦魔宠",
        "Assassinate": "刺杀",
    },
    "Viscous": {
        "Splatter": "飞溅",
        "The Cube": "方块",
        "Puddle Punch": "水洼重拳",
        "Goo Ball": "粘液球",
    },
    "Vyper": {
        "Screwjab Dagger": "螺旋刺匕",
        "Lethal Venom": "致命毒液",
        "Slither": "蛇行",
        "Petrifying Bola": "石化绳索",
    },
    "Warden": {
        "Alchemical Flask": "炼金烧瓶",
        "Willpower": "意志力",
        "Binding Word": "束缚之言",
        "Last Stand": "最后一搏",
    },
    "Wraith": {
        "Card Trick": "卡牌戏法",
        "Project Mind": "心灵投射",
        "Full Auto": "全自动",
        "Telekinesis": "念力移物",
    },
    "Yamato": {
        "Power Slash": "强力斩",
        "Flying Slash": "飞空斩",
        "Crimson Slash": "绯红斩",
        "Shadow Transformation": "暗影变身",
    },
}


ITEM_ZH_NAMES = {
    "Extra Charge": "额外充能",
    "Extra Spirit": "额外元灵",
    "Golden Goose Egg": "金鹅蛋",
    "Mystic Burst": "秘术爆发",
    "Mystic Expansion": "秘术扩展",
    "Mystic Regeneration": "秘术再生",
    "Rusted Barrel": "锈蚀枪管",
    "Spirit Strike": "元灵打击",
    "Arcane Surge": "奥术涌动",
    "Bullet Resist Shredder": "子弹抗性撕裂者",
    "Cold Front": "寒潮",
    "Compress Cooldown": "压缩冷却",
    "Duration Extender": "持续延长器",
    "Improved Spirit": "强化元灵",
    "Mystic Slow": "秘术减速",
    "Mystic Vulnerability": "秘术易伤",
    "Quicksilver Reload": "水银换弹",
    "Slowing Hex": "减速咒",
    "Spirit Sap": "元灵汲取",
    "Suppressor": "抑制器",
    "Decay": "腐朽",
    "Disarming Hex": "缴械咒",
    "Greater Expansion": "高级扩展",
    "Knockdown": "击倒",
    "Radiant Regeneration": "辉光再生",
    "Rapid Recharge": "快速充能",
    "Silence Wave": "沉默波",
    "Spirit Snatch": "元灵夺取",
    "Superior Cooldown": "高级冷却",
    "Superior Duration": "高级持续",
    "Surge of Power": "力量涌动",
    "Tankbuster": "坦克克星",
    "Torment Pulse": "苦痛脉冲",
    "Arctic Blast": "极寒爆裂",
    "Boundless Spirit": "无界元灵",
    "Cursed Relic": "诅咒圣物",
    "Echo Shard": "回响碎片",
    "Escalating Exposure": "递增暴露",
    "Ethereal Shift": "虚灵转移",
    "Focus Lens": "聚焦透镜",
    "Lightning Scroll": "闪电卷轴",
    "Magic Carpet": "魔毯",
    "Mercurial Magnum": "水银马格南",
    "Mystic Reverb": "秘术回响",
    "Refresher": "刷新器",
    "Scourge": "祸害",
    "Spirit Burn": "元灵灼烧",
    "Transcendent Cooldown": "超凡冷却",
    "Vortex Web": "漩涡之网",
    "Frostbite Charm": "冻伤护符",
    "Mystic Conduit": "秘术导管",
    "Mystical Piano": "神秘钢琴",
    "Omnicharge Signet": "全能充能印记",
    "Prism Blast": "棱镜爆破",
    "Shrink Ray": "缩小射线",
    "Unstable Concoction": "不稳定合剂",
    "Extra Health": "额外生命",
    "Extra Regen": "额外恢复",
    "Extra Stamina": "额外耐力",
    "Grit": "坚毅",
    "Healing Rite": "治疗仪式",
    "Melee Lifesteal": "近战吸血",
    "Rebuttal": "反驳",
    "Sprint Boots": "冲刺靴",
    "Battle Vest": "战斗背心",
    "Bullet Lifesteal": "子弹吸血",
    "Debuff Reducer": "减益削减器",
    "Enchanter's Emblem": "附魔师徽记",
    "Enduring Speed": "持久速度",
    "Guardian Ward": "守护结界",
    "Healbane": "疗愈克星",
    "Healing Booster": "治疗增幅器",
    "Reactive Barrier": "反应屏障",
    "Restorative Locket": "复苏吊坠",
    "Return Fire": "还击火力",
    "Spirit Lifesteal": "元灵吸血",
    "Spirit Shielding": "元灵护盾",
    "Trophy Collector": "战利品收藏家",
    "Weapon Shielding": "武器护盾",
    "Bullet Resilience": "子弹韧性",
    "Counterspell": "反制法术",
    "Dispel Magic": "驱散魔法",
    "Fortitude": "坚韧",
    "Fury Trance": "狂怒恍惚",
    "Healing Nova": "治疗新星",
    "Lifestrike": "生命打击",
    "Majestic Leap": "威严跃击",
    "Metal Skin": "金属皮肤",
    "Rescue Beam": "救援光束",
    "Spirit Resilience": "元灵韧性",
    "Stamina Mastery": "耐力精通",
    "Veil Walker": "帷幕行者",
    "Warp Stone": "跃迁石",
    "Cheat Death": "欺骗死亡",
    "Colossus": "巨像",
    "Divine Barrier": "神圣屏障",
    "Diviner's Kevlar": "占卜者凯夫拉",
    "Healing Tempo": "治疗节奏",
    "Indomitable": "不屈",
    "Infuser": "灌注器",
    "Inhibitor": "抑制装置",
    "Juggernaut": "主宰者",
    "Leech": "榨取",
    "Phantom Strike": "幻影打击",
    "Plated Armor": "板甲",
    "Siphon Bullets": "虹吸子弹",
    "Spellbreaker": "破法者",
    "Unstoppable": "势不可挡",
    "Vampiric Burst": "吸血爆发",
    "Witchmail": "巫术锁甲",
    "Celestial Blessing": "天界祝福",
    "Cloak of Opportunity": "机遇斗篷",
    "Electric Slippers": "电光拖鞋",
    "Eternal Gift": "永恒赠礼",
    "Nullification Burst": "无效化爆发",
    "Seraphim Wings": "炽天使之翼",
    "Shadow Strike": "暗影打击",
    "Close Quarters": "近距离作战",
    "Extended Magazine": "扩容弹匣",
    "Headshot Booster": "爆头增幅器",
    "High-Velocity Rounds": "高速弹",
    "Monster Rounds": "怪物弹",
    "Rapid Rounds": "速射弹",
    "Restorative Shot": "恢复射击",
    "Active Reload": "主动换弹",
    "Fleetfoot": "疾步",
    "Intensifying Magazine": "强化弹匣",
    "Kinetic Dash": "动能冲刺",
    "Long Range": "远距离",
    "Melee Charge": "近战充能",
    "Mystic Shot": "秘术射击",
    "Opening Rounds": "开场弹",
    "Recharging Rush": "充能冲刺",
    "Slowing Bullets": "减速子弹",
    "Spirit Shredder Bullets": "元灵撕裂弹",
    "Split Shot": "分裂射击",
    "Stalker": "潜猎者",
    "Swift Striker": "迅捷打击者",
    "Titanic Magazine": "巨型弹匣",
    "Weakening Headshot": "弱化爆头",
    "Alchemical Fire": "炼金火焰",
    "Ballistic Enchantment": "弹道附魔",
    "Berserker": "狂战士",
    "Blood Tribute": "鲜血贡品",
    "Burst Fire": "爆发射击",
    "Cultist Sacrifice": "邪教徒牺牲",
    "Escalating Resilience": "递增韧性",
    "Express Shot": "速射",
    "Headhunter": "猎头者",
    "Heroic Aura": "英雄光环",
    "Hollow Point": "空尖弹",
    "Hunter's Aura": "猎手光环",
    "Point Blank": "贴脸射击",
    "Shadow Weave": "暗影织物",
    "Sharpshooter": "神射手",
    "Spirit Rend": "元灵撕裂",
    "Tesla Bullets": "特斯拉子弹",
    "Toxic Bullets": "剧毒子弹",
    "Weighted Shots": "加重射击",
    "Armor Piercing Rounds": "穿甲弹",
    "Capacitor": "电容器",
    "Crippling Headshot": "致残爆头",
    "Crushing Fists": "粉碎之拳",
    "Frenzy": "狂热",
    "Glass Cannon": "玻璃大炮",
    "Lucky Shot": "幸运一击",
    "Ricochet": "跳弹",
    "Silencer": "消音器",
    "Spellslinger": "法术枪手",
    "Spiritual Overflow": "元灵溢流",
    "Haunting Shot": "萦魂射击",
    "Infinite Rounds": "无限弹药",
    "Runed Gauntlets": "符文护手",
}


SKILL_LABEL_ZH = {
    "Cooldown": "冷却",
    "Duration": "持续时间",
    "Damage": "伤害",
    "Damage Per Second": "每秒伤害",
    "DPS": "每秒伤害",
    "Radius": "半径",
    "Range": "范围",
    "Cast Range": "施法范围",
    "Charge Delay": "充能延迟",
    "Charges": "充能次数",
    "Heal": "治疗",
    "Heal Amount": "治疗量",
    "Health Regen": "生命恢复",
    "Max Health": "最大生命值",
    "Move Speed": "移动速度",
    "Sprint Speed": "冲刺速度",
    "Fire Rate": "射速",
    "Bullet Damage": "子弹伤害",
    "Weapon Damage": "武器伤害",
    "Spirit Damage": "元灵伤害",
    "Spirit Power": "元灵力量",
    "Bullet Resist": "子弹抗性",
    "Spirit Resist": "元灵抗性",
    "Melee Resist": "近战抗性",
    "Lifesteal": "生命偷取",
    "Bullet Lifesteal": "子弹吸血",
    "Spirit Lifesteal": "元灵吸血",
    "Melee Lifesteal": "近战吸血",
    "Stun Duration": "眩晕持续时间",
    "Silence Duration": "沉默持续时间",
    "Sleep Duration": "睡眠持续时间",
    "Slow Duration": "减速持续时间",
    "Buff Duration": "增益持续时间",
    "Debuff Duration": "减益持续时间",
    "Barrier": "屏障",
    "Barrier Duration": "屏障持续时间",
    "Explosion Damage": "爆炸伤害",
    "Explosion Radius": "爆炸半径",
    "Impact Damage": "冲击伤害",
    "Impact Radius": "冲击半径",
    "Weapon Accuracy": "武器精准度",
    "Bullet Velocity": "子弹速度",
    "Stamina": "耐力",
    "Stamina Restored": "恢复耐力",
}


SKILL_LABEL_REPLACEMENTS = [
    ("Cooldown", "冷却"),
    ("Duration", "持续时间"),
    ("Damage", "伤害"),
    ("Radius", "半径"),
    ("Range", "范围"),
    ("Health", "生命"),
    ("Heal", "治疗"),
    ("Healing", "治疗"),
    ("Bullet", "子弹"),
    ("Spirit", "元灵"),
    ("Weapon", "武器"),
    ("Melee", "近战"),
    ("Lifesteal", "生命偷取"),
    ("Resist", "抗性"),
    ("Speed", "速度"),
    ("Move", "移动"),
    ("Slow", "减速"),
    ("Stun", "眩晕"),
    ("Silence", "沉默"),
    ("Sleep", "睡眠"),
    ("Charge", "充能"),
    ("Charges", "充能次数"),
    ("Stack", "层数"),
    ("Stacks", "层数"),
    ("Max", "最大"),
    ("Min", "最小"),
    ("Bonus", "额外"),
    ("Per", "每"),
    ("Interval", "间隔"),
    ("Delay", "延迟"),
    ("Threshold", "阈值"),
    ("Lifetime", "存在时间"),
    ("Jump", "跳跃"),
    ("Dash", "冲刺"),
    ("Flight", "飞行"),
    ("Fire Rate", "射速"),
]


SKILL_LABEL_TOKEN_ZH = {
    "ability": "技能",
    "abilities": "技能",
    "accuracy": "精准度",
    "active": "主动",
    "added": "增加",
    "additional": "额外",
    "air": "空中",
    "all": "全部",
    "ally": "友军",
    "ambush": "伏击",
    "ammo": "弹药",
    "amp": "增幅",
    "amplification": "增幅",
    "amplified": "已增幅",
    "angle": "角度",
    "area": "区域",
    "arming": "启动",
    "assassination": "刺杀",
    "assistant": "助手",
    "attack": "攻击",
    "attacking": "攻击中",
    "aura": "光环",
    "auto": "自动",
    "ball": "球",
    "barrel": "枪管",
    "barrier": "屏障",
    "base": "基础",
    "battery": "电池",
    "beam": "光束",
    "before": "前",
    "bell": "铃",
    "between": "间隔",
    "blast": "爆破",
    "blasted": "爆破",
    "bleed": "流血",
    "block": "格挡",
    "blood": "鲜血",
    "bomb": "炸弹",
    "bonus": "额外",
    "boost": "增幅",
    "boss": "首领",
    "bounce": "弹跳",
    "bounty": "赏金",
    "breakable": "可破坏",
    "buff": "增益",
    "buildup": "积累",
    "bullet": "子弹",
    "bullets": "子弹",
    "burn": "灼烧",
    "burst": "爆发",
    "camera": "镜头",
    "cancel": "取消",
    "capture": "捕获",
    "card": "卡牌",
    "cart": "车",
    "cast": "施放",
    "caster": "施法者",
    "chance": "概率",
    "channel": "引导",
    "charge": "充能",
    "charged": "已充能",
    "charges": "充能次数",
    "check": "检测",
    "cleared": "清除",
    "close": "近距离",
    "club": "棍棒",
    "collection": "收集",
    "combo": "连击",
    "control": "控制",
    "copied": "复制",
    "copy": "复制",
    "cost": "消耗",
    "count": "数量",
    "create": "生成",
    "current": "当前",
    "curse": "诅咒",
    "damage": "伤害",
    "deadhead": "亡首",
    "deadheads": "亡首",
    "death": "死亡",
    "debuff": "减益",
    "decay": "衰减",
    "decaying": "衰减中",
    "deferred": "延迟",
    "deflect": "偏转",
    "delay": "延迟",
    "delayed": "延迟",
    "detonate": "引爆",
    "diamond": "钻石",
    "disable": "禁用",
    "disarm": "缴械",
    "dispel": "驱散",
    "distance": "距离",
    "djinn": "灯神",
    "doorway": "门道",
    "dragon": "龙",
    "drain": "吸取",
    "drifter": "漂泊者",
    "duration": "持续时间",
    "effectiveness": "效果",
    "enemy": "敌人",
    "ending": "结束",
    "entangle": "缠绕",
    "escape": "逃脱",
    "evasion": "闪避",
    "explode": "爆炸",
    "explosion": "爆炸",
    "extend": "延长",
    "extended": "延长",
    "extra": "额外",
    "fade": "消退",
    "fading": "消退中",
    "failed": "失败",
    "fall": "衰减",
    "faster": "更快",
    "fire": "射击",
    "flare": "耀斑",
    "fly": "飞行",
    "for": "用于",
    "form": "形态",
    "fourth": "第四",
    "friendly": "友方",
    "full": "满额",
    "gain": "获得",
    "generation": "生成",
    "ghouls": "亡灵",
    "going": "进行中",
    "grab": "抓取",
    "gravestone": "墓碑",
    "gun": "枪械",
    "headshot": "爆头",
    "heal": "治疗",
    "healing": "治疗",
    "health": "生命",
    "hear": "听觉",
    "heavy": "重型",
    "height": "高度",
    "helper": "帮手",
    "hero": "英雄",
    "heroes": "英雄",
    "hex": "咒",
    "hit": "命中",
    "hold": "按住",
    "hooking": "钩取",
    "ice": "冰",
    "imbued": "灌注",
    "immobilize": "定身",
    "immunity": "免疫",
    "impact": "冲击",
    "improve": "强化",
    "incoming": "受到",
    "infest": "侵染",
    "initial": "初始",
    "interrupt": "打断",
    "interval": "间隔",
    "invincible": "无敌",
    "invis": "隐身",
    "invisibility": "隐身",
    "isolation": "孤立",
    "item": "装备",
    "joke": "戏法",
    "jump": "跳跃",
    "kill": "击杀",
    "knife": "刀",
    "knight": "骑士",
    "knights": "骑士",
    "knockback": "击退",
    "knockup": "击飞",
    "landing": "落地",
    "lasso": "套索",
    "late": "后段",
    "leash": "牵引",
    "length": "长度",
    "life": "生命",
    "lifesteal": "吸血",
    "lift": "抬升",
    "light": "轻型",
    "limit": "上限",
    "linger": "残留",
    "low": "低生命",
    "lunge": "突刺",
    "mark": "标记",
    "marks": "标记",
    "max": "最大",
    "medium": "中等",
    "melee": "近战",
    "mess": "混乱",
    "meter": "计量",
    "min": "最小",
    "minimum": "最小",
    "missing": "缺失",
    "modifier": "修正",
    "move": "移动",
    "movement": "移动",
    "movespeed": "移动速度",
    "multi": "多重",
    "multiplier": "倍率",
    "multishot": "多重射击",
    "nearby": "附近",
    "next": "下一次",
    "no": "无",
    "non": "非",
    "on": "命中时",
    "out": "外部",
    "outgoing": "造成",
    "override": "覆盖",
    "pad": "垫",
    "parry": "招架",
    "particle": "粒子",
    "patrol": "巡逻",
    "pause": "暂停",
    "penalty": "惩罚",
    "percent": "百分比",
    "percentage": "百分比",
    "perfect": "完美",
    "permanent": "永久",
    "petrify": "石化",
    "pickup": "拾取",
    "pillow": "枕头",
    "position": "位置",
    "power": "力量",
    "priority": "优先级",
    "proc": "触发",
    "projectile": "投射物",
    "puddle": "水洼",
    "pulse": "脉冲",
    "punch": "拳击",
    "purge": "净化",
    "push": "推开",
    "radius": "半径",
    "rage": "怒气",
    "raised": "升起",
    "range": "范围",
    "rate": "速率",
    "read": "阅读",
    "rebirth": "重生",
    "recast": "再次施放",
    "recasts": "再次施放",
    "received": "受到",
    "recoil": "后坐力",
    "recovery": "恢复",
    "reduce": "降低",
    "reduced": "降低",
    "reduction": "降低",
    "refresh": "刷新",
    "refund": "返还",
    "regen": "恢复",
    "regenerated": "已恢复",
    "regeneration": "恢复",
    "released": "释放",
    "replicated": "复制",
    "required": "需求",
    "reset": "重置",
    "resist": "抗性",
    "resistance": "抗性",
    "resists": "抗性",
    "restored": "恢复",
    "restriction": "限制",
    "reveal": "显形",
    "revive": "复活",
    "ricochet": "跳弹",
    "rocket": "火箭",
    "rope": "绳索",
    "search": "搜索",
    "sec": "秒",
    "second": "第二",
    "secondary": "次要",
    "self": "自身",
    "shards": "碎片",
    "shock": "电击",
    "short": "短",
    "shot": "射击",
    "shove": "推击",
    "side": "侧向",
    "silence": "沉默",
    "singularity": "奇点",
    "skull": "骷髅",
    "slash": "斩击",
    "slide": "滑行",
    "sliding": "滑行",
    "slow": "减速",
    "souls": "魂魄",
    "spawn": "生成",
    "speed": "速度",
    "spin": "旋转",
    "spread": "扩散",
    "sprint": "冲刺",
    "stack": "层数",
    "stacking": "叠层",
    "stamina": "耐力",
    "steal": "窃取",
    "steeds": "坐骑",
    "sticky": "黏性",
    "stolen": "已窃取",
    "stomp": "践踏",
    "stop": "停止",
    "store": "储存",
    "strike": "打击",
    "summon": "召唤",
    "swap": "交换",
    "taken": "受到",
    "target": "目标",
    "targets": "目标",
    "tech": "技能",
    "teleport": "传送",
    "temporary": "临时",
    "tether": "连接",
    "third": "第三",
    "threshold": "阈值",
    "throw": "投掷",
    "time": "时间",
    "to": "转化为",
    "tornado": "龙卷",
    "toss": "投掷",
    "total": "总计",
    "toxic": "剧毒",
    "tracking": "追踪",
    "trail": "轨迹",
    "travel": "飞行",
    "trooper": "士兵",
    "turret": "炮塔",
    "unlimited": "无限",
    "unstoppable": "不可阻挡",
    "up": "向上",
    "uppercut": "上勾拳",
    "use": "使用",
    "vacuum": "真空",
    "velocity": "速度",
    "venom": "毒液",
    "visual": "视觉",
    "wake": "唤醒",
    "wall": "墙",
    "wave": "波",
    "while": "期间",
    "width": "宽度",
    "window": "窗口",
    "world": "世界",
    "wrecked": "摧毁",
    "zombie": "僵尸",
    "ai": "AI",
    "dps": "每秒伤害",
    "hp": "生命值",
    "npc": "非英雄单位",
    "pc": "玩家",
    "ps": "每秒",
    "pct": "百分比",
    "per": "每",
    "vs": "对",
    "and": "和",
    "from": "来自",
    "alt": "备用",
    "amount": "数值",
    "as": "作为",
    "away": "远离",
    "back": "向后",
    "bat": "蝙蝠",
    "bias": "偏移",
    "blessed": "祝福",
    "bosses": "首领",
    "bounces": "弹跳次数",
    "buffer": "缓冲",
    "build": "积累",
    "can": "可",
    "cap": "上限",
    "cards": "卡牌",
    "cat": "猫",
    "chain": "锁链",
    "channeling": "引导中",
    "checkout": "检出",
    "chore": "动作",
    "collision": "碰撞",
    "condition": "条件",
    "conditionally": "条件触发",
    "cone": "锥形",
    "cooldown": "冷却",
    "cooldowns": "冷却",
    "counts": "计数",
    "credit": "计入",
    "crit": "暴击",
    "cube": "方块",
    "damping": "阻尼",
    "dash": "冲刺",
    "dealt": "造成",
    "debuffs": "减益",
    "degrees": "度",
    "delta": "差值",
    "diminish": "递减",
    "down": "向下",
    "downtime": "停机时间",
    "drag": "拖拽",
    "during": "期间",
    "effect": "效果",
    "end": "结束",
    "execute": "处决",
    "falloff": "衰减",
    "far": "远距离",
    "first": "第一",
    "force": "力度",
    "forward": "向前",
    "fraction": "比例",
    "fx": "特效",
    "glub": "粘液",
    "gold": "魂魄",
    "grapple": "抓钩",
    "grenade": "手雷",
    "half": "半",
    "heart": "心脏",
    "hook": "钩爪",
    "hop": "跳跃",
    "hotel": "旅店",
    "ignore": "忽略",
    "immune": "免疫",
    "improved": "强化",
    "in": "在内",
    "internal": "内部",
    "joker": "小丑",
    "knock": "击飞",
    "land": "落地",
    "leap": "跃击",
    "lifetime": "存在时间",
    "lock": "锁定",
    "lockon": "锁定",
    "lockout": "锁定禁用",
    "los": "视线",
    "lose": "失去",
    "lost": "已失去",
    "mult": "倍率",
    "near": "附近",
    "occupied": "占用",
    "off": "关闭",
    "offset": "偏移",
    "others": "其他",
    "path": "路径",
    "post": "后置",
    "preview": "预览",
    "primary": "主要",
    "proj": "投射物",
    "prop": "属性",
    "pull": "拉拽",
    "ratio": "比例",
    "ready": "就绪",
    "reloaded": "已换弹",
    "replenish": "补充",
    "resource": "资源",
    "restore": "恢复",
    "rising": "上升",
    "roll": "翻滚",
    "s": "秒",
    "scale": "缩放",
    "shard": "碎片",
    "shooting": "射击中",
    "shred": "削减",
    "slam": "重摔",
    "sleep": "睡眠",
    "snap": "夹陷阱",
    "soft": "轻度",
    "sound": "声音",
    "spirit": "元灵",
    "splash": "溅射",
    "spill": "溢出",
    "split": "分裂",
    "spot": "标记点",
    "spotted": "已显形",
    "sprite": "精灵",
    "stakes": "木桩",
    "stacks": "层数",
    "start": "开始",
    "stored": "已储存",
    "straight": "直线",
    "stun": "眩晕",
    "sweep": "横扫",
    "takes": "受到",
    "tick": "跳数",
    "timer": "计时器",
    "track": "追踪",
    "trip": "绊倒",
    "turrets": "炮塔",
    "upward": "向上",
    "vertical": "垂直",
    "warning": "警告",
    "warp": "跃迁",
    "weapon": "武器",
    "zoomed": "开镜",
}


def split_label_tokens(label):
    text = str(label)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    text = re.sub(r"[_/+\-]+", " ", text)
    text = text.replace("%", " Percent ")
    return re.findall(r"[A-Za-z]+|\d+|[\u4e00-\u9fff]+", text)


def translate_label_tokens(label):
    words = []
    for token in split_label_tokens(label):
        if re.search(r"[\u4e00-\u9fff]", token) or token.isdigit():
            words.append(token)
            continue
        translated = SKILL_LABEL_TOKEN_ZH.get(token.lower())
        words.append(translated or "原始字段")
    if not words:
        return label
    return " ".join(words)


def hero_zh_name(name):
    return HERO_ZH_NAMES.get(name, name)


def ability_zh_name(hero_name, ability_name):
    return ABILITY_ZH_NAMES.get(hero_name, {}).get(ability_name, ability_name)


def item_zh_name(name):
    return ITEM_ZH_NAMES.get(name, name)


def skill_label_zh(label):
    if not label:
        return label
    if label in SKILL_LABEL_ZH:
        return SKILL_LABEL_ZH[label]
    out = label
    for src, dst in SKILL_LABEL_REPLACEMENTS:
        out = re.sub(rf"\b{re.escape(src)}\b", dst, out)
    if re.search(r"[A-Za-z]", out):
        out = translate_label_tokens(out)
    return out


PPT_TARGETS = {
    "MODIFIER_VALUE_HEALTH_MAX": ("max_health_add", "flat"),
    "MODIFIER_VALUE_BASE_HEALTH_PERCENT": ("max_health_pct", "percent"),
    "MODIFIER_VALUE_HEALTH_MAX_PERCENT": ("max_health_pct", "percent"),
    "MODIFIER_VALUE_HEALTH_REGEN_PER_SECOND": ("health_regen_add", "flat"),
    "MODIFIER_VALUE_BULLET_ARMOR_DAMAGE_RESIST": ("bullet_armor_add", "flat"),
    "MODIFIER_VALUE_TECH_RESIST": ("spirit_armor_add", "flat"),
    "MODIFIER_VALUE_MOVEMENT_SPEED_MAX": ("move_speed_add", "flat"),
    "MODIFIER_VALUE_MOVEMENT_SPEED_MAX_PERCENT": ("move_speed_pct", "percent"),
    "MODIFIER_VALUE_SPRINT_SPEED_BONUS": ("sprint_speed_add", "flat"),
    "MODIFIER_VALUE_STAMINA": ("stamina_add", "flat"),
    "MODIFIER_VALUE_STAMINA_REGEN_PER_SECOND_PERCENTAGE": ("stamina_regen_pct", "percent"),
    "MODIFIER_VALUE_FIRE_RATE": ("fire_rate_pct", "percent"),
    "MODIFIER_VALUE_AMMO_CLIP_SIZE": ("clip_size_add", "flat"),
    "MODIFIER_VALUE_AMMO_CLIP_SIZE_PERCENT": ("clip_size_pct", "percent"),
    "MODIFIER_VALUE_FLAT_BULLET_DAMAGE_POST_SCALE": ("bullet_damage_add", "flat"),
    "MODIFIER_VALUE_WEAPON_DAMAGE_INCREASE": ("weapon_damage_pct", "percent"),
    "MODIFIER_VALUE_MELEE_DAMAGE_INCREASE": ("melee_damage_pct", "percent"),
    "MODIFIER_VALUE_TECH_POWER": ("spirit_power_add", "flat"),
    "MODIFIER_VALUE_TECH_POWER_PERCENT": ("spirit_power_pct", "percent"),
    "MODIFIER_VALUE_TECH_RANGE_PERCENT": ("tech_range_pct", "percent"),
    "MODIFIER_VALUE_TECH_RADIUS_PERCENT": ("tech_radius_pct", "percent"),
    "MODIFIER_VALUE_BONUS_ABILITY_DURATION_PERCENTAGE": ("tech_duration_pct", "percent"),
    "MODIFIER_VALUE_COOLDOWN_REDUCTION_PERCENTAGE": ("tech_cooldown_pct", "percent"),
    "MODIFIER_VALUE_COOLDOWN_BETWEEN_CHARGE_REDUCTION_PERCENTAGE": ("charge_cooldown_pct", "percent"),
    "MODIFIER_VALUE_BONUS_ABILITY_CHARGES": ("ability_charges_add", "flat"),
    "MODIFIER_VALUE_HEAL_AMP_CAST_PERCENT": ("healing_output_pct", "percent"),
    "MODIFIER_VALUE_BONUS_BULLET_SPEED_PERCENT": ("bullet_speed_pct", "percent"),
    "MODIFIER_VALUE_BONUS_ATTACK_RANGE_PERCENT": ("weapon_range_pct", "percent"),
    "MODIFIER_VALUE_BONUS_ATTACK_RANGE": ("weapon_range_add", "flat"),
    "MODIFIER_VALUE_BARRIER_HEALTH": ("barrier_add", "flat"),
}

CATEGORY_BONUS_TARGETS = {
    "vitality": ("max_health_pct", "percent"),
    "spirit": ("spirit_power_add", "flat"),
    "weapon": ("weapon_damage_pct", "percent"),
}

ITEM_EXCLUDE_PAT = re.compile(
    r"(slow|debuff|reduction|enemy|taken|incoming|receivepenalty|regenpenalty|"
    r"healamp|lifesteal|evasion|dash|slide|air|npc|nonplayer|nonhero|charged)",
    re.I,
)


EXCLUDE_PAT = re.compile(
    r"(slow|debuff|reduction|enemy|taken|incoming|receivepenalty|regenpenalty|"
    r"healamp|lifesteal|evasion|dash|slide|air|radius|duration|cooldown|damage taken)",
    re.I,
)


SKILL_CORE_PROPS = {
    "AbilityCastRange",
    "AbilityChannelTime",
    "AbilityCharges",
    "AbilityCooldown",
    "AbilityCooldownBetweenCharge",
    "AbilityDuration",
}

SKILL_DROP_PROPS = {
    "AbilityCastDelay",
    "AbilityPostCastDuration",
    "AbilityResourceCost",
    "AbilityUnitTargetLimit",
    "ChannelMoveSpeed",
    "TechPower",
    "WeaponPower",
}

SKILL_KEYWORDS = re.compile(
    r"(damage|dps|heal|health|barrier|shield|radius|range|duration|cooldown|charge|"
    r"slow|stun|immobil|silence|sleep|root|disarm|debuff|resist|armor|move|speed|"
    r"fire ?rate|bullet|melee|ammo|clip|stack|kill)",
    re.I,
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_base_rows():
    with BASE_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fmt_time(ts):
    if not ts:
        return ""
    return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")


def file_mtime(path):
    return fmt_time(path.stat().st_mtime) if path.exists() else ""


def update_times(rows):
    values = []
    for row in rows:
        value = row.get("update_time") if isinstance(row, dict) else None
        if value:
            values.append(num(value))
    return [value for value in values if value > 0]


def num(value, default=0.0):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("m", "")
    if text == "":
        return default
    try:
        return float(text)
    except ValueError:
        return default


def color_for_index(index):
    hue = (index * 137.508) % 360
    return f"hsl({hue:.1f}, 68%, 56%)"


def is_per_unit(name, label):
    text = f"{name} {label}".lower()
    return any(x in text for x in ["perstack", "per stack", "stack", "perkill", "per kill", "kill", "stolen"])


def classify_effect(prop, per_unit):
    usage_flags = prop.get("usage_flags") or []
    conditional = any(flag in usage_flags for flag in ("ConditionallyApplied", "ConditionallyEnemyApplied"))
    intrinsic = "IntrinsicallyProvidedInAbility" in usage_flags
    if conditional:
        application = "conditional_active"
    elif per_unit:
        application = "stack_or_kill_assumption"
    elif intrinsic:
        application = "passive_unconditional"
    else:
        application = "active_or_contextual"
    return {
        "usageFlags": "|".join(usage_flags),
        "conditional": conditional,
        "intrinsic": intrinsic,
        "application": application,
        "includeInCurve": application == "passive_unconditional",
    }


def target_from_property(name, prop):
    ppt = prop.get("provided_property_type")
    label = prop.get("label") or prop.get("postvalue_label") or ""
    text = f"{name} {label} {ppt or ''}"

    if ppt in PPT_TARGETS:
        if EXCLUDE_PAT.search(text) and name not in {"BonusMoveSpeed", "MovementSpeedBonus"}:
            return None
        return PPT_TARGETS[ppt]

    lowered = text.lower()
    if name in {"BonusMoveSpeed", "MovementSpeedBonus", "SpeedOnLand", "InvisMoveSpeedMod"}:
        return ("sprint_speed_add" if "sprint" in lowered else "move_speed_add", "flat")
    if name == "BonusSprintSpeed":
        return ("sprint_speed_add", "flat")
    if name in {"MoveSpeedBonusPct", "BonusMoveSpeedPercent", "MoveSpeedPercent", "MaxBonusMoveSpeedPercent"}:
        return ("move_speed_pct", "percent")
    if name in {"BonusFireRate", "FireRatePerStack"}:
        return ("fire_rate_pct", "percent")
    if name in {"BonusBullets"}:
        return ("clip_size_add", "flat")
    if name in {"BonusClipSizePercent"}:
        return ("clip_size_pct", "percent")
    if name in {"BonusBulletSpeedPercent"}:
        return ("bullet_speed_pct", "percent")
    if name in {"BonusHealth", "BonusMaxHealth"}:
        return ("max_health_add", "flat")
    if name in {"HealthRegen", "BonusHealthRegen", "TotalHealthRegen"}:
        return ("health_regen_add", "flat")
    if name == "Stamina":
        return ("stamina_add", "flat")
    if name in {"DamageBonusFixedPerStack"}:
        return ("bullet_damage_add", "flat")
    if name in {"BaseAttackDamagePercent", "BuffBaseWeaponPct", "WeaponDamageBonusPerKill"}:
        return ("weapon_damage_pct", "percent")
    if name in {"BuffMeleeDamage"}:
        return ("melee_damage_pct", "percent")
    return None


def target_from_item_property(name, prop):
    ppt = prop.get("provided_property_type")
    label = prop.get("label") or prop.get("postvalue_label") or ""
    text = f"{name} {label} {ppt or ''}"
    if ppt in {
        "MODIFIER_VALUE_COOLDOWN_REDUCTION_PERCENTAGE",
        "MODIFIER_VALUE_COOLDOWN_BETWEEN_CHARGE_REDUCTION_PERCENTAGE",
        "MODIFIER_VALUE_BONUS_ABILITY_CHARGES",
        "MODIFIER_VALUE_HEAL_AMP_CAST_PERCENT",
    }:
        return PPT_TARGETS[ppt]
    if name in {"CooldownReduction"}:
        return ("tech_cooldown_pct", "percent")
    if name in {"CooldownBetweenChargeReduction"}:
        return ("charge_cooldown_pct", "percent")
    if name in {"BonusAbilityCharges"}:
        return ("ability_charges_add", "flat")
    if name in {"HealAmpCastPercent"}:
        return ("healing_output_pct", "percent")
    if ITEM_EXCLUDE_PAT.search(text):
        return None
    if ppt in PPT_TARGETS:
        return PPT_TARGETS[ppt]

    if name in {"TechPower", "SpiritPower", "SpiritPowerInnate", "BonusSpirit"}:
        return ("spirit_power_add", "flat")
    if name in {"TechPowerPercent"}:
        return ("spirit_power_pct", "percent")
    if name in {"BonusHealth", "BonusMaxHealth"}:
        return ("max_health_add", "flat")
    if name in {"MaxHealthLossPercent"}:
        return ("max_health_pct", "percent")
    if name in {"BonusHealthRegen", "HealthRegen", "TotalHealthRegen"}:
        return ("health_regen_add", "flat")
    if name in {"BaseAttackDamagePercent", "BaseAttackDamagePercentBonus"}:
        return ("weapon_damage_pct", "percent")
    if name in {"BonusFireRate"}:
        return ("fire_rate_pct", "percent")
    if name in {"BonusClipSizePercent"}:
        return ("clip_size_pct", "percent")
    if name in {"BonusBullets"}:
        return ("clip_size_add", "flat")
    if name in {"BonusBulletSpeedPercent"}:
        return ("bullet_speed_pct", "percent")
    if name in {"BonusSprintSpeed"}:
        return ("sprint_speed_add", "flat")
    if name in {"BonusMoveSpeed", "MovementSpeedBonus"}:
        return ("move_speed_add", "flat")
    if name in {"Stamina"}:
        return ("stamina_add", "flat")
    if name in {"StaminaCooldownReduction"}:
        return ("stamina_regen_pct", "percent")
    if name in {"BonusMeleeDamagePercent", "BuffMeleeDamage"}:
        return ("melee_damage_pct", "percent")
    if name in {"TechRangeMultiplier", "StackingTechRangeMultiplier"}:
        return ("tech_range_pct", "percent")
    if name in {"TechRadiusMultiplier"}:
        return ("tech_radius_pct", "percent")
    if name in {"BonusAbilityDurationPercent"}:
        return ("tech_duration_pct", "percent")
    if name in {"BonusAttackRangePercent"}:
        return ("weapon_range_pct", "percent")
    return None


def is_shop_item(item):
    return (
        item.get("type") == "upgrade"
        and item.get("shopable") is True
        and item.get("disabled") is not True
        and item.get("item_slot_type") in {"weapon", "vitality", "spirit"}
        and item.get("cost")
    )


def classify_item_effect(item, prop, per_unit):
    usage_flags = prop.get("usage_flags") or []
    conditional = any(flag in usage_flags for flag in ("ConditionallyApplied", "ConditionallyEnemyApplied"))
    intrinsic = "IntrinsicallyProvidedInAbility" in usage_flags
    section = prop.get("tooltip_section") or ""
    active_section = section == "active"
    if conditional:
        application = "conditional_active"
    elif per_unit:
        application = "stack_or_kill_assumption"
    elif active_section:
        application = "active_or_contextual"
    elif section in ("", "innate") or intrinsic:
        application = "passive_unconditional"
    else:
        application = "active_or_contextual"
    return {
        "usageFlags": "|".join(usage_flags),
        "tooltipSection": section,
        "conditional": conditional,
        "intrinsic": intrinsic,
        "application": application,
        "includeInBuild": application == "passive_unconditional",
    }


def item_effect_from_property(item, prop_name, prop):
    target = target_from_item_property(prop_name, prop)
    if not target:
        return None
    value = num(prop.get("value"))
    if abs(value) < 1e-9:
        return None
    label = prop.get("label") or prop.get("postvalue_label") or prop_name
    per_unit = is_per_unit(prop_name, label)
    class_info = classify_item_effect(item, prop, per_unit)
    target_id, mode = target
    return {
        "id": f"{item['id']}:{prop_name}",
        "itemId": str(item["id"]),
        "itemName": item.get("name"),
        "itemNameZh": item_zh_name(item.get("name") or ""),
        "itemClass": item.get("class_name"),
        "slot": item.get("item_slot_type"),
        "tier": item.get("item_tier"),
        "cost": item.get("cost"),
        "activation": item.get("activation") or "",
        "source": "Item",
        "property": prop_name,
        "label": label,
        "labelZh": skill_label_zh(label),
        "target": target_id,
        "mode": mode,
        "value": value,
        "scaleWithSpirit": 0.0,
        "perUnit": per_unit,
        "unitLabel": "stack/kill" if per_unit else "",
        **class_info,
        "providedPropertyType": prop.get("provided_property_type", ""),
    }


def effect_from_upgrade(hero, ability, slot, upgrade_index, prop_name, prop, up):
    target = target_from_property(prop_name, prop)
    if not target:
        return None
    target_id, mode = target
    label = prop.get("label") or prop.get("postvalue_label") or prop_name
    value = num(up.get("bonus"))
    scale = 0.0
    if up.get("upgrade_type") == "EAddToScale" and (up.get("scale_stat_filter") in ("ETechPower", None, "")):
        scale = value
        value = 0.0
    per_unit = is_per_unit(prop_name, label)
    class_info = classify_effect(prop, per_unit)
    return {
        "id": f"{hero['id']}:{slot}:u{upgrade_index}:{prop_name}:{len(str(up))}",
        "heroId": str(hero["id"]),
        "heroName": hero["name"],
        "heroNameZh": hero_zh_name(hero["name"]),
        "slot": slot,
        "abilityName": ability.get("name"),
        "abilityNameZh": ability_zh_name(hero["name"], ability.get("name") or ""),
        "abilityClass": ability.get("class_name"),
        "requiredState": upgrade_index + 1,
        "source": f"T{upgrade_index}",
        "property": prop_name,
        "label": label,
        "labelZh": skill_label_zh(label),
        "target": target_id,
        "mode": mode,
        "value": value,
        "scaleWithSpirit": scale,
        "perUnit": per_unit,
        "unitLabel": "stack/kill" if per_unit else "",
        **class_info,
        "providedPropertyType": prop.get("provided_property_type", ""),
        "upgradeType": up.get("upgrade_type", ""),
        "scaleStatFilter": up.get("scale_stat_filter", ""),
    }


def effect_from_base(hero, ability, slot, prop_name, prop):
    target = target_from_property(prop_name, prop)
    if not target:
        return None
    target_id, mode = target
    label = prop.get("label") or prop.get("postvalue_label") or prop_name
    value = num(prop.get("value"))
    if abs(value) < 1e-9:
        return None
    if EXCLUDE_PAT.search(f"{prop_name} {label}") and prop_name not in {"BonusMoveSpeed", "MovementSpeedBonus"}:
        return None
    per_unit = is_per_unit(prop_name, label)
    class_info = classify_effect(prop, per_unit)
    return {
        "id": f"{hero['id']}:{slot}:base:{prop_name}",
        "heroId": str(hero["id"]),
        "heroName": hero["name"],
        "heroNameZh": hero_zh_name(hero["name"]),
        "slot": slot,
        "abilityName": ability.get("name"),
        "abilityNameZh": ability_zh_name(hero["name"], ability.get("name") or ""),
        "abilityClass": ability.get("class_name"),
        "requiredState": 1,
        "source": "Base",
        "property": prop_name,
        "label": label,
        "labelZh": skill_label_zh(label),
        "target": target_id,
        "mode": mode,
        "value": value,
        "scaleWithSpirit": 0.0,
        "perUnit": per_unit,
        "unitLabel": "stack/kill" if per_unit else "",
        **class_info,
        "providedPropertyType": prop.get("provided_property_type", ""),
        "upgradeType": "",
        "scaleStatFilter": "",
    }


def skill_property_group(name, label):
    text = f"{name} {label}".lower()
    if name in {"AbilityCooldown", "AbilityCooldownBetweenCharge", "AbilityCharges"}:
        return "cooldown_charge"
    if name in {"AbilityCastRange"} or "range" in text or "radius" in text:
        return "range_area"
    if name in {"AbilityDuration", "AbilityChannelTime"} or "duration" in text:
        return "duration"
    if any(word in text for word in ["damage", "dps", "bullet", "melee"]):
        return "damage"
    if any(word in text for word in ["heal", "health", "barrier", "shield"]):
        return "healing_shield"
    if any(word in text for word in ["slow", "stun", "immobil", "silence", "sleep", "root", "disarm", "debuff", "resist", "armor"]):
        return "control_debuff"
    if any(word in text for word in ["move", "speed", "dash"]):
        return "mobility"
    return "other"


def skill_property_context(name, label, prop):
    usage_flags = prop.get("usage_flags") or []
    text = f"{name} {label}".lower()
    if any(flag in usage_flags for flag in ("ConditionallyApplied", "ConditionallyEnemyApplied")):
        return "conditional"
    if is_per_unit(name, label) or any(word in text for word in ["perstack", "per stack", "stack", "perkill", "per kill", "on kill"]):
        return "stack"
    if any(word in text for word in ["enemy", "target", "victim"]):
        return "contextual"
    return "main"


def skill_property_relevant(name, prop, upgrades):
    if name in SKILL_DROP_PROPS:
        return False
    label = prop.get("label") or prop.get("postvalue_label") or name
    value = num(prop.get("value"))
    has_upgrades = bool(upgrades)
    scale_function = prop.get("scale_function") or {}
    has_scale = bool(
        scale_function.get("class_name")
        or scale_function.get("specific_stat_scale_type")
        or scale_function.get("scaling_stats")
        or abs(num(scale_function.get("stat_scale"))) > 1e-9
    )

    if name in SKILL_CORE_PROPS:
        if name in {"AbilityCharges", "AbilityCooldownBetweenCharge"}:
            return value > 0 or has_upgrades
        return abs(value) > 1e-9 or has_upgrades

    text = f"{name} {label} {prop.get('postfix') or ''}"
    if not (SKILL_KEYWORDS.search(text) or has_upgrades or has_scale):
        return False
    return abs(value) > 1e-9 or has_upgrades or has_scale


def skill_property_from_property(prop_name, prop, upgrades):
    label = prop.get("label") or prop.get("postvalue_label") or prop_name
    scale_function = prop.get("scale_function") or {}
    return {
        "name": prop_name,
        "label": label,
        "labelZh": skill_label_zh(label),
        "postfix": prop.get("postfix") or "",
        "displayUnits": prop.get("display_units") or "",
        "cssClass": prop.get("css_class") or "",
        "value": num(prop.get("value")),
        "rawValue": prop.get("value"),
        "disableValue": prop.get("disable_value"),
        "group": skill_property_group(prop_name, label),
        "context": skill_property_context(prop_name, label, prop),
        "usageFlags": "|".join(prop.get("usage_flags") or []),
        "providedPropertyType": prop.get("provided_property_type", ""),
        "scaleClass": scale_function.get("class_name") or "",
        "scaleSubclass": scale_function.get("subclass_name") or "",
        "specificStat": scale_function.get("specific_stat_scale_type") or "",
        "statScale": num(scale_function.get("stat_scale")),
        "scalingStats": scale_function.get("scaling_stats") or [],
        "upgrades": upgrades,
    }


def skill_card_from_ability(hero, ability, slot, index):
    props = ability.get("properties") or {}
    upgrades_by_prop = {}
    for upgrade_index, upgrade in enumerate(ability.get("upgrades") or [], start=1):
        for up in upgrade.get("property_upgrades") or []:
            prop_name = up.get("name")
            if not prop_name:
                continue
            upgrades_by_prop.setdefault(prop_name, []).append(
                {
                    "requiredState": upgrade_index + 1,
                    "source": f"T{upgrade_index}",
                    "bonus": num(up.get("bonus")),
                    "rawBonus": up.get("bonus"),
                    "upgradeType": up.get("upgrade_type", ""),
                    "scaleStatFilter": up.get("scale_stat_filter", ""),
                }
            )

    properties = []
    core_order = {name: i for i, name in enumerate(["AbilityCooldown", "AbilityCharges", "AbilityCooldownBetweenCharge", "AbilityCastRange", "AbilityDuration", "AbilityChannelTime"])}
    for prop_name, prop in props.items():
        upgrades = upgrades_by_prop.get(prop_name, [])
        if skill_property_relevant(prop_name, prop, upgrades):
            properties.append(skill_property_from_property(prop_name, prop, upgrades))

    properties.sort(key=lambda p: (core_order.get(p["name"], 100), p["group"], p["label"].lower()))
    return {
        "heroId": str(hero["id"]),
        "heroName": hero["name"],
        "heroNameZh": hero_zh_name(hero["name"]),
        "slot": slot,
        "slotIndex": index,
        "abilityClass": ability.get("class_name"),
        "abilityName": ability.get("name"),
        "abilityNameZh": ability_zh_name(hero["name"], ability.get("name") or ""),
        "abilityType": ability.get("ability_type", ""),
        "description": ability.get("description", ""),
        "image": ability.get("image") or "",
        "imageWebp": ability.get("image_webp") or "",
        "properties": properties,
    }


def build_ability_data(heroes, items_by_class, active_ids):
    abilities = []
    effects = []
    full_abilities = []
    skill_inspector = {}
    for hero in sorted([h for h in heroes if str(h["id"]) in active_ids], key=lambda h: h["name"].lower()):
        for index, slot in enumerate(["signature1", "signature2", "signature3", "signature4"], start=1):
            ability_class = hero.get("items", {}).get(slot)
            ability = items_by_class.get(ability_class)
            if not ability:
                continue
            full_abilities.append(
                {
                    "heroId": str(hero["id"]),
                    "heroName": hero["name"],
                    "heroNameZh": hero_zh_name(hero["name"]),
                    "slot": slot,
                    "slotIndex": index,
                    "ability": ability,
                }
            )
            skill_inspector.setdefault(str(hero["id"]), []).append(skill_card_from_ability(hero, ability, slot, index))
            props = ability.get("properties") or {}
            upgrades = ability.get("upgrades") or []
            ability_row = {
                "heroId": str(hero["id"]),
                "heroName": hero["name"],
                "heroNameZh": hero_zh_name(hero["name"]),
                "slot": slot,
                "slotIndex": index,
                "abilityClass": ability.get("class_name"),
                "abilityName": ability.get("name"),
                "abilityNameZh": ability_zh_name(hero["name"], ability.get("name") or ""),
                "abilityType": ability.get("ability_type", ""),
                "description": ability.get("description", ""),
                "upgradeCount": len(upgrades),
            }
            ability_row["effects"] = []
            abilities.append(ability_row)
            for prop_name, prop in props.items():
                eff = effect_from_base(hero, ability, slot, prop_name, prop)
                if eff:
                    effects.append(eff)
                    ability_row["effects"].append(eff["id"])
            for upgrade_index, upgrade in enumerate(upgrades, start=1):
                for up in upgrade.get("property_upgrades") or []:
                    prop_name = up.get("name")
                    prop = props.get(prop_name, {})
                    eff = effect_from_upgrade(hero, ability, slot, upgrade_index, prop_name, prop, up)
                    if eff:
                        effects.append(eff)
                        ability_row["effects"].append(eff["id"])
    return abilities, effects, full_abilities, skill_inspector


def build_item_data(items):
    shop_items = []
    item_effects = []
    for item in sorted(
        [item for item in items if is_shop_item(item)],
        key=lambda item: (item.get("item_slot_type") or "", item.get("cost") or 0, item.get("name") or ""),
    ):
        effects = []
        for prop_name, prop in (item.get("properties") or {}).items():
            eff = item_effect_from_property(item, prop_name, prop)
            if eff:
                item_effects.append(eff)
                effects.append(eff["id"])
        shop_items.append(
            {
                "id": str(item["id"]),
                "className": item.get("class_name"),
                "name": item.get("name"),
                "nameZh": item_zh_name(item.get("name") or ""),
                "slot": item.get("item_slot_type"),
                "tier": item.get("item_tier"),
                "cost": item.get("cost"),
                "activation": item.get("activation") or "",
                "image": item.get("image") or "",
                "imageWebp": item.get("image_webp") or "",
                "effects": effects,
            }
        )
    return shop_items, item_effects


def build_hero_bonus_data(heroes, active_ids):
    bonuses = {}
    for hero in heroes:
        if str(hero.get("id")) not in active_ids:
            continue
        bonuses[str(hero["id"])] = {
            "cost": hero.get("cost_bonuses") or {},
            "purchase": hero.get("purchase_bonuses") or {},
        }
    return bonuses


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_version_info(heroes_json, items, rows, abilities, effects, shop_items, item_effects, skill_inspector):
    item_updates = update_times(items)
    latest_update = max(item_updates) if item_updates else None
    earliest_update = min(item_updates) if item_updates else None
    latest_items = [
        item.get("name") or item.get("class_name") or str(item.get("id"))
        for item in items
        if latest_update and abs(num(item.get("update_time")) - latest_update) < 1e-6
    ][:8]
    source_files = [
        {
            "name": HEROES_JSON.name,
            "role": "英雄基础属性、成长、魂魄等级表、购买奖励",
            "roleEn": "Hero base stats, growth, soul level table, purchase bonuses",
            "records": len(heroes_json),
            "modifiedAt": file_mtime(HEROES_JSON),
            "assetUpdateRange": "无 update_time 字段",
            "assetUpdateRangeEn": "No update_time field",
        },
        {
            "name": ITEMS_JSON.name,
            "role": "技能、装备、装备属性、技能属性与升级",
            "roleEn": "Abilities, items, item stats, ability properties and upgrades",
            "records": len(items),
            "modifiedAt": file_mtime(ITEMS_JSON),
            "assetUpdateRange": f"{fmt_time(earliest_update)} ~ {fmt_time(latest_update)}" if item_updates else "无 update_time 字段",
            "assetUpdateRangeEn": f"{fmt_time(earliest_update)} ~ {fmt_time(latest_update)}" if item_updates else "No update_time field",
        },
        {
            "name": BASE_CSV.name,
            "role": "已筛选 selectable 英雄基础/成长曲线输入",
            "roleEn": "Filtered selectable hero base/growth curve input",
            "records": len(rows),
            "modifiedAt": file_mtime(BASE_CSV),
            "assetUpdateRange": "由 heroes_assets_v2.json 派生",
            "assetUpdateRangeEn": "Derived from heroes_assets_v2.json",
        },
    ]
    generated_counts = {
        "selectableHeroes": len(rows),
        "abilities": len(abilities),
        "curveEffects": len(effects),
        "shopItems": len(shop_items),
        "itemEffects": len(item_effects),
        "skillCards": sum(len(cards) for cards in skill_inspector.values()),
        "skillProperties": sum(len(card["properties"]) for cards in skill_inspector.values() for card in cards),
    }
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_timestamp = max(file_mtime(HEROES_JSON), file_mtime(ITEMS_JSON), file_mtime(BASE_CSV))
    data_version = f"本地快照 {data_timestamp}"
    data_version_en = f"Local Snapshot {data_timestamp}"
    changelog = [
        {
            "date": generated_at,
            "title": "本页重新生成",
            "items": [
                f"可选英雄 {generated_counts['selectableHeroes']} 个，技能卡 {generated_counts['skillCards']} 张。",
                f"装备 {generated_counts['shopItems']} 件，映射装备被动/面板效果 {generated_counts['itemEffects']} 条。",
                f"技能检查器属性 {generated_counts['skillProperties']} 条，曲线可映射技能面板效果 {generated_counts['curveEffects']} 条。",
            ],
        },
        {
            "date": fmt_time(latest_update) or "未知",
            "title": "源资产最新 update_time",
            "items": [
                "源文件没有提供官方补丁号或 Steam build id；页面使用本地源文件快照和资产 update_time 做版本核对。",
                f"items_assets_v2.json update_time 范围：{fmt_time(earliest_update)} ~ {fmt_time(latest_update)}。" if item_updates else "items_assets_v2.json 未提供 update_time。",
                f"最新 update_time 对应条目：{', '.join(latest_items)}。" if latest_items else "没有可列出的最新条目。",
            ],
        },
        {
            "date": generated_at,
            "title": "计算规则说明",
            "items": [
                "曲线与交叉点只叠加技能的无条件被动/永久英雄面板效果，不叠加装备、魂魄加成或购买加成。",
                "英雄断点面板与技能检查器使用同一配装上下文：等级、技能加点、装备、魂魄阈值、购买加成。",
                "无法可靠解释的技能 scale function 在技能检查器中以 raw/unsupported 分组显示，不猜测计算。",
            ],
        },
    ]
    changelog_en = [
        {
            "date": generated_at,
            "title": "Page Regenerated",
            "items": [
                f"Selectable heroes: {generated_counts['selectableHeroes']}; skill cards: {generated_counts['skillCards']}.",
                f"Items: {generated_counts['shopItems']}; mapped item passive/panel effects: {generated_counts['itemEffects']}.",
                f"Skill Inspector properties: {generated_counts['skillProperties']}; curve-mapped skill panel effects: {generated_counts['curveEffects']}.",
            ],
        },
        {
            "date": fmt_time(latest_update) or "Unknown",
            "title": "Latest Source Asset update_time",
            "items": [
                "The source files do not include an official patch name or Steam build id; this page uses the local source snapshot and asset update_time for version checks.",
                f"items_assets_v2.json update_time range: {fmt_time(earliest_update)} ~ {fmt_time(latest_update)}." if item_updates else "items_assets_v2.json does not provide update_time.",
                f"Entries with the latest update_time: {', '.join(latest_items)}." if latest_items else "No latest entries can be listed.",
            ],
        },
        {
            "date": generated_at,
            "title": "Calculation Rules",
            "items": [
                "Curves and crossing points only include unconditional passive/permanent hero panel effects from abilities; items, soul bonuses, and purchase bonuses are excluded.",
                "Hero Snapshot and Skill Inspector use the same build context: level, ability points, items, soul thresholds, and purchase bonuses.",
                "Unsupported scale functions are shown as raw/unsupported in Skill Inspector instead of being guessed.",
            ],
        },
    ]
    return {
        "gameVersion": "源文件未提供官方游戏版本号",
        "gameVersionEn": "Official game version is not provided by the source files",
        "dataVersion": data_version,
        "dataVersionEn": data_version_en,
        "generatedAt": generated_at,
        "latestAssetUpdate": fmt_time(latest_update) if latest_update else "未知",
        "latestAssetUpdateEn": fmt_time(latest_update) if latest_update else "Unknown",
        "sourceFiles": source_files,
        "generatedCounts": generated_counts,
        "latestItems": latest_items,
        "changelog": changelog,
        "changelogEn": changelog_en,
        "notes": [
            "这里的版本用于核对本页数据快照，不等同于 Valve 官方补丁名称。",
            "如果之后重新拉取 heroes_assets_v2.json / items_assets_v2.json，需要重新运行生成脚本刷新本页版本信息。",
        ],
        "notesEn": [
            "This version block identifies the data snapshot used by this page; it is not a Valve official patch name.",
            "After refreshing heroes_assets_v2.json / items_assets_v2.json, rerun the generator to update this page version.",
        ],
    }


def build_payload():
    heroes_json = load_json(HEROES_JSON)
    items = load_json(ITEMS_JSON)
    items_by_class = {item.get("class_name"): item for item in items}
    rows = load_base_rows()
    active_ids = {row["hero_id"] for row in rows}
    abilities, effects, full_abilities, skill_inspector = build_ability_data(heroes_json, items_by_class, active_ids)
    shop_items, item_effects = build_item_data(items)
    hero_bonuses = build_hero_bonus_data(heroes_json, active_ids)

    heroes = []
    base = {}
    for i, row in enumerate(rows):
        hero_id = row["hero_id"]
        heroes.append(
            {
                "id": hero_id,
                "name": row["hero_name"],
                "nameZh": hero_zh_name(row["hero_name"]),
                "heroType": row["hero_type"],
                "gunTag": row["gun_tag"],
                "color": color_for_index(i),
            }
        )
        keys = [
            "base_max_health", "growth_health_per_level", "base_health_regen",
            "base_bullet_armor_pct", "growth_bullet_armor_pct_per_level",
            "base_spirit_armor_pct", "growth_spirit_resist_pct_per_level",
            "base_move_speed", "base_sprint_speed", "base_crouch_speed",
            "base_move_acceleration", "base_stamina", "base_stamina_regen_per_second",
            "base_light_melee_damage", "base_heavy_melee_damage",
            "growth_melee_damage_per_level", "growth_spirit_power_per_level",
            "base_tech_range", "base_tech_duration", "base_bullet_damage",
            "growth_bullet_damage_per_level", "base_bullets", "base_clip_size",
            "base_shots_per_second", "base_bullet_speed", "base_weapon_range",
            "growth_bonus_attack_range_per_level", "base_reload_duration",
            "base_reload_speed", "base_crit_damage_received_scale",
            "scaling_EBaseHealthRegen_scale", "scaling_EBulletArmorDamageReduction_scale",
            "scaling_ETechArmorDamageReduction_scale", "scaling_EMaxMoveSpeed_scale",
            "scaling_ESprintSpeed_scale", "scaling_EBulletDamage_scale",
            "scaling_EClipSize_scale", "scaling_ERoundsPerSecond_scale",
            "scaling_EFireRate_scale", "scaling_EHeavyMeleeDamage_scale",
        ]
        base[hero_id] = {k: num(row.get(k)) for k in keys}

    level_source = next(h for h in heroes_json if str(h["id"]) in active_ids)
    levels = {}
    unlocks = 0
    ability_points = 0
    for level in range(1, 37):
        info = level_source.get("level_info", {}).get(str(level), {})
        currencies = info.get("bonus_currencies") or []
        if "EAbilityUnlocks" in currencies:
            unlocks += 1
        if "EAbilityPoints" in currencies:
            ability_points += 1
        levels[str(level)] = {
            "requiredSouls": info.get("required_gold", 0),
            "bonusCurrencies": currencies,
            "cumulativeUnlocks": unlocks,
            "cumulativeAbilityPoints": ability_points,
        }

    payload = {
        "source": {
            "heroes": HEROES_JSON.name,
            "items": ITEMS_JSON.name,
            "baseStats": BASE_CSV.name,
        },
        "minLevel": 1,
        "maxLevel": 36,
        "attributes": ATTRIBUTES,
        "heroes": heroes,
        "base": base,
        "levelInfo": {
            "upgradeCosts": {"T1": 1, "T2": 3, "T3": 5},
            "slotUnlockLevels": {"signature1": 1, "signature2": 3, "signature3": 5, "signature4": 7},
            "levels": levels,
        },
        "abilities": abilities,
        "effects": effects,
        "skillInspector": skill_inspector,
        "items": shop_items,
        "itemEffects": item_effects,
        "heroBonuses": hero_bonuses,
        "versionInfo": build_version_info(heroes_json, items, rows, abilities, effects, shop_items, item_effects, skill_inspector),
        "fullAbilities": full_abilities,
        "notes": [
            "技能状态：0=关闭，1=基础，2=T1，3=T1+T2，4=T1+T2+T3。",
            "开启等级门槛时，技能解锁与技能点来自 level_info，升级成本为 1/3/5。",
            "映射效果保守限定为自身面板属性；敌方减益和纯技能伤害只导出，不默认进入曲线。",
            "默认曲线只应用 passive_unconditional：IntrinsicallyProvidedInAbility、非条件、非叠层/击杀假设。",
            "条件、主动/上下文、叠层/击杀效果导出但不进入曲线；开关只影响断点与技能检查器上下文。",
            "断点面板的装备预算由所选等级 required_gold 限制。",
            "魂魄加成使用英雄 cost_bonuses 阈值；购买加成使用所选装备类别和 tier。",
            "技能检查器使用与断点面板相同的英雄、等级、技能、装备、购买加成和魂魄加成上下文。",
            "未支持的技能 scale function 显示为原始值，不猜测计算。",
        ],
    }
    return payload


def export_tables(payload):
    ability_rows = []
    effects_by_id = {effect["id"]: effect for effect in payload["effects"]}
    for ability in payload["abilities"]:
        ability_rows.append(
            {
                **ability,
                "effectsJson": json.dumps([effects_by_id[eid] for eid in ability["effects"]], ensure_ascii=False),
            }
        )
    write_csv(
        ABILITIES_CSV,
        ability_rows,
        ["heroId", "heroName", "heroNameZh", "slot", "slotIndex", "abilityClass", "abilityName", "abilityNameZh", "abilityType", "description", "upgradeCount", "effectsJson"],
    )
    write_csv(
        ABILITY_EFFECTS_CSV,
        payload["effects"],
        [
            "id", "heroId", "heroName", "heroNameZh", "slot", "abilityName", "abilityNameZh", "abilityClass", "requiredState",
            "source", "property", "label", "labelZh", "target", "mode", "value", "scaleWithSpirit",
            "perUnit", "unitLabel", "conditional", "intrinsic", "application", "includeInCurve",
            "usageFlags", "providedPropertyType", "upgradeType", "scaleStatFilter",
        ],
    )
    write_csv(
        ITEM_EFFECTS_CSV,
        payload["itemEffects"],
        [
            "id", "itemId", "itemName", "itemNameZh", "itemClass", "slot", "tier", "cost", "activation",
            "source", "property", "label", "labelZh", "target", "mode", "value", "scaleWithSpirit",
            "perUnit", "unitLabel", "conditional", "intrinsic", "application", "includeInBuild",
            "usageFlags", "tooltipSection", "providedPropertyType",
        ],
    )
    ABILITIES_JSON.write_text(
        json.dumps(
            {
                "source": {"heroes": HEROES_JSON.name, "items": ITEMS_JSON.name},
                "recordCount": len(payload["fullAbilities"]),
                "abilities": payload["fullAbilities"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def write_html(payload):
    html_payload = {k: v for k, v in payload.items() if k != "fullAbilities"}
    html = HTML_TEMPLATE.replace("__PAYLOAD_JSON__", json.dumps(html_payload, ensure_ascii=False, separators=(",", ":")))
    HTML_OUT.write_text(html, encoding="utf-8")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Deadlock 英雄数值控制台</title>
<style>
@font-face{font-family:"Deadlock WenKai";font-style:normal;font-weight:400;font-display:swap;src:url("assets/fonts/lxgw-wenkai-500.woff2") format("woff2")}
@font-face{font-family:"Deadlock WenKai";font-style:normal;font-weight:500;font-display:swap;src:url("assets/fonts/lxgw-wenkai-500.woff2") format("woff2")}
@font-face{font-family:"Deadlock WenKai";font-style:normal;font-weight:700;font-display:swap;src:url("assets/fonts/lxgw-wenkai-700.woff2") format("woff2")}
:root{--bg:#0b0d0c;--panel:#151918;--panel2:#1d2422;--ink:#f2eadc;--muted:#a89f91;--line:#33403b;--accent:#d8ad4d;--accent2:#54b39d;--blood:#ba4e3c;--warn:#d86752;--good:#5cb58a;--font:"Deadlock WenKai",serif;--mono:"Deadlock WenKai",monospace}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:linear-gradient(115deg,rgba(216,173,77,.08) 0 1px,transparent 1px 68px) 0 0/96px 96px,linear-gradient(90deg,rgba(84,179,157,.055) 1px,transparent 1px) 0 0/42px 42px,linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px) 0 0/42px 42px,radial-gradient(circle at 12% -10%,rgba(186,78,60,.16),transparent 26%),var(--bg);color:var(--ink);font-family:var(--font);font-weight:500;letter-spacing:0;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background:linear-gradient(135deg,transparent 0 48%,rgba(216,173,77,.12) 48% 48.4%,transparent 48.4%),linear-gradient(45deg,transparent 0 63%,rgba(84,179,157,.08) 63% 63.35%,transparent 63.35%);mix-blend-mode:screen;opacity:.5;z-index:0}
header{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px 22px;border-bottom:1px solid rgba(216,173,77,.22);background:linear-gradient(90deg,rgba(11,13,12,.98),rgba(21,25,24,.96));position:sticky;top:0;z-index:4;box-shadow:0 14px 32px rgba(0,0,0,.32)}h1{margin:0;font-size:21px;font-weight:700}.brand{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:center}.brand-mark{width:34px;height:34px;border:1px solid rgba(216,173,77,.55);background:linear-gradient(135deg,rgba(216,173,77,.2),rgba(84,179,157,.12));clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%);position:relative}.brand-mark:after{content:"";position:absolute;inset:9px;border:1px solid rgba(242,234,220,.55);clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}.meta{color:var(--muted);font-size:12px;margin-top:3px}.version-strip{display:grid;grid-template-columns:auto auto auto auto;gap:8px;align-items:center}.version-pill{border:1px solid rgba(216,173,77,.32);background:rgba(216,173,77,.08);border-radius:6px;padding:6px 8px;font-size:11px;color:var(--ink)}.version-pill span{display:block;color:var(--muted);font-size:10px}.version-pill b{font-family:var(--mono)}.lang-btn{min-width:74px;border-color:rgba(84,179,157,.4);background:linear-gradient(180deg,rgba(84,179,157,.15),rgba(18,24,23,.92));color:#d9fff5}.app{display:grid;grid-template-columns:360px minmax(0,1fr);min-height:calc(100vh - 67px);position:relative;z-index:1}aside{border-right:1px solid var(--line);background:linear-gradient(180deg,rgba(21,25,24,.97),rgba(12,15,14,.96));padding:16px;overflow:auto;max-height:calc(100vh - 67px);position:sticky;top:67px}main{min-width:0;padding:16px 18px 24px}
label{display:block;color:var(--muted);font-size:11px;font-weight:700;margin-bottom:6px}select,input{width:100%;border:1px solid var(--line);background:#101514;color:var(--ink);border-radius:6px;padding:8px 9px;font:13px var(--font);outline:none}select:focus,input:focus{border-color:var(--accent);box-shadow:0 0 0 2px rgba(216,173,77,.1)}
.control{margin-bottom:13px}.row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px}button{border:1px solid var(--line);background:linear-gradient(180deg,var(--panel2),#121817);color:var(--ink);border-radius:6px;padding:8px 10px;font:12px var(--font);cursor:pointer}button:hover{border-color:var(--accent);box-shadow:0 0 0 1px rgba(216,173,77,.12) inset}
.list{max-height:280px;overflow:auto;border:1px solid var(--line);border-radius:8px;background:#101313}.check{display:flex;align-items:center;gap:8px;padding:6px 4px;border-bottom:1px solid rgba(255,255,255,.035);font-size:12px}.check input{width:auto;margin:0;accent-color:var(--accent)}.swatch{width:10px;height:10px;border-radius:2px;flex:0 0 auto}
.panel{border:1px solid var(--line);background:linear-gradient(180deg,#111615,#0d1110);border-radius:8px;padding:10px;margin-top:12px;box-shadow:0 10px 24px rgba(0,0,0,.18)}.panel h2{font-size:13px;margin:0 0 9px;color:var(--accent)}.ability{display:grid;grid-template-columns:1fr 104px;gap:8px;align-items:center;padding:7px 0;border-top:1px solid rgba(255,255,255,.045)}.ability:first-of-type{border-top:0}.ability b{font-size:12px}.ability small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.unit{display:grid;grid-template-columns:1fr 72px;gap:8px;align-items:center;padding:6px 0;border-top:1px solid rgba(255,255,255,.045)}.unit span{font-size:12px}.unit em{display:block;color:var(--muted);font-style:normal;font-size:10px}
.item-filters{display:grid;grid-template-columns:1fr 92px;gap:8px}.soul-strip{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center;border:1px solid rgba(214,179,90,.28);border-radius:8px;background:rgba(214,179,90,.075);padding:9px;margin:0 0 12px}.soul-strip span{display:block;color:var(--muted);font-size:10px;text-transform:uppercase}.soul-strip b{display:block;color:var(--accent);font:20px var(--mono);margin-top:2px}.soul-strip button{height:34px;padding:0 10px}.item-list{max-height:330px;overflow:auto;border:1px solid var(--line);border-radius:8px;background:#101313}.item{display:grid;grid-template-columns:auto 1fr auto;gap:8px;align-items:center;padding:7px 6px;border-bottom:1px solid rgba(255,255,255,.04);font-size:12px}.item input{width:auto;margin:0;accent-color:var(--accent)}.item b{display:block;font-size:12px}.item small{display:block;color:var(--muted);font:10px var(--mono);margin-top:2px}.item .cost{color:var(--accent);font:11px var(--mono)}.item.off{opacity:.48}.mini{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin:10px 0}.mini div{border:1px solid rgba(255,255,255,.06);border-radius:6px;padding:7px;background:#0d1010}.mini b{display:block;font:14px var(--mono);color:var(--accent)}.mini span{color:var(--muted);font-size:10px;text-transform:uppercase}.budget-bad b{color:var(--warn)}.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.chip{border:1px solid rgba(214,179,90,.35);border-radius:999px;padding:4px 8px;color:var(--ink);background:rgba(214,179,90,.08);font:11px var(--mono)}
.chart-card,.table-card,.build-card,.skill-card{border:1px solid var(--line);background:linear-gradient(180deg,rgba(21,25,24,.96),rgba(13,16,15,.94));border-radius:8px;overflow:hidden;box-shadow:0 18px 42px rgba(0,0,0,.24);position:relative}.chart-card:before,.build-card:before,.skill-card:before,.table-card:before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2),var(--blood));opacity:.75}.head{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line)}.title{font-size:15px;font-weight:700}.subtitle{color:var(--muted);font:12px var(--mono);margin-top:2px}
#chart{width:100%;height:560px;display:block;background:linear-gradient(180deg,rgba(255,255,255,.018),transparent),linear-gradient(90deg,rgba(216,173,77,.045) 1px,transparent 1px) 0 0/84px 84px}.axis text{fill:var(--muted);font:11px var(--mono)}.axis line,.axis path,.grid line{stroke:var(--line);stroke-width:1}.curve{fill:none;stroke-width:1.7;opacity:.78;filter:drop-shadow(0 0 4px rgba(216,173,77,.08))}.curve.dim{opacity:.13}.curve.hot{stroke-width:3.2;opacity:1}.dot{fill:var(--accent);opacity:.8}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:14px 0}.stat{border:1px solid var(--line);border-radius:8px;background:linear-gradient(180deg,rgba(28,35,33,.95),rgba(14,18,17,.95));padding:10px 12px}.stat b{display:block;font:18px var(--mono);color:var(--accent);margin-bottom:3px}.stat span{color:var(--muted);font-size:11px}
.table-card,.build-card,.skill-card{margin-top:14px}.toggle{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:12px;user-select:none}.toggle input{width:auto;accent-color:var(--accent)}table{width:100%;border-collapse:collapse;font-size:12px}th,td{border-bottom:1px solid rgba(255,255,255,.055);padding:8px 10px;text-align:left;white-space:nowrap}th{color:var(--muted);font-size:10px;text-transform:uppercase;background:#111414;position:sticky;top:0;z-index:1}tbody tr:hover{background:rgba(214,179,90,.08)}.scroll{max-height:380px;overflow:auto}.delta-pos{color:var(--good)}.delta-neg{color:var(--warn)}.build-body{padding:12px 14px}.build-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-bottom:12px}.build-grid .stat{margin:0}.build-table{max-height:430px;overflow:auto}
.skill-body{padding:12px 14px}.skill-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.skill-panel{border:1px solid rgba(255,255,255,.07);border-radius:8px;background:#101313;overflow:hidden}.skill-top{display:grid;grid-template-columns:44px 1fr auto;gap:10px;align-items:center;padding:10px 11px;border-bottom:1px solid rgba(255,255,255,.055)}.skill-top img{width:44px;height:44px;object-fit:cover;border-radius:6px;background:#0b0d0d}.skill-top b{display:block;font-size:13px}.skill-top small{display:block;color:var(--muted);font:10px var(--mono);margin-top:2px}.skill-state{border:1px solid rgba(214,179,90,.32);border-radius:999px;padding:4px 8px;color:var(--accent);font:11px var(--mono);white-space:nowrap}.skill-section{padding:9px 11px;border-top:1px solid rgba(255,255,255,.045)}.skill-section:first-of-type{border-top:0}.skill-section h3{margin:0 0 7px;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:0}.skill-row{display:grid;grid-template-columns:minmax(130px,1.2fr) repeat(3,minmax(56px,.6fr));gap:8px;align-items:center;padding:5px 0;border-top:1px solid rgba(255,255,255,.035);font:12px var(--mono)}.skill-row:first-of-type{border-top:0}.skill-row .name{font:12px var(--font);color:var(--ink);min-width:0;overflow:hidden;text-overflow:ellipsis}.skill-row .name small{display:block;color:var(--muted);font:10px var(--mono);margin-top:2px;overflow:hidden;text-overflow:ellipsis}.skill-row .muted{color:var(--muted)}.skill-row.unsupported{opacity:.78}.skill-tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}.skill-tag{border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:3px 7px;color:var(--muted);font:10px var(--mono);background:rgba(255,255,255,.025)}.empty-skill{color:var(--muted);padding:14px;font-size:12px}
.note{margin-top:12px;padding:10px;border:1px solid rgba(214,179,90,.28);background:rgba(214,179,90,.075);border-radius:8px;color:var(--muted);font-size:12px;line-height:1.45}.tooltip{position:fixed;pointer-events:none;background:#090b0b;border:1px solid var(--line);border-radius:8px;padding:9px 10px;color:var(--ink);font:12px var(--mono);max-width:330px;box-shadow:0 14px 28px rgba(0,0,0,.35);display:none;z-index:9}.modal{position:fixed;inset:0;background:rgba(0,0,0,.66);display:flex;align-items:center;justify-content:center;padding:22px;z-index:12}.modal[hidden]{display:none}.modal-box{width:min(620px,100%);max-height:min(720px,88vh);border:1px solid var(--line);border-radius:8px;background:linear-gradient(180deg,#111615,#0b0f0e);box-shadow:0 24px 60px rgba(0,0,0,.55);overflow:hidden}.modal-box.wide{width:min(860px,100%)}.modal-head{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line)}.modal-head b{font-size:14px}.modal-body{max-height:620px;overflow:auto}.modal table tr.current{background:rgba(214,179,90,.12)}.modal table tr.current td:first-child{color:var(--accent);font-weight:700}.version-body{padding:14px}.version-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-bottom:12px}.version-card{border:1px solid rgba(216,173,77,.24);border-radius:8px;background:rgba(216,173,77,.055);padding:10px}.version-card span{display:block;color:var(--muted);font-size:11px}.version-card b{display:block;margin-top:4px;font:13px var(--mono);color:var(--ink)}.log-entry{border-top:1px solid rgba(255,255,255,.06);padding:12px 0}.log-entry:first-of-type{border-top:0}.log-entry h3{margin:0 0 6px;font-size:13px;color:var(--accent)}.log-entry small{display:block;color:var(--muted);font:11px var(--mono);margin-bottom:8px}.log-entry ul{margin:0;padding-left:18px;color:var(--ink);line-height:1.55;font-size:12px}.source-table{margin-top:10px;border:1px solid rgba(255,255,255,.06);border-radius:8px;overflow:hidden}
@media(max-width:980px){.app{grid-template-columns:1fr}aside{position:static;max-height:none;border-right:0;border-bottom:1px solid var(--line)}.stats,.build-grid,.skill-grid,.version-summary{grid-template-columns:repeat(2,minmax(0,1fr))}header{align-items:flex-start;flex-direction:column}.version-strip{grid-template-columns:repeat(2,minmax(0,auto))}}
@media(max-width:680px){.skill-grid,.version-summary{grid-template-columns:1fr}.skill-row{grid-template-columns:minmax(120px,1fr) repeat(3,minmax(52px,.55fr));gap:6px}.version-strip{grid-template-columns:1fr;width:100%}}
</style>
</head>
<body>
<header>
  <div class="brand"><div class="brand-mark"></div><div><h1 data-i18n="appTitle">Deadlock 英雄数值控制台</h1><div class="meta" data-i18n="appMeta">1-36级曲线 · 技能加点 · 装备断点 · 技能检查器</div></div></div>
  <div class="version-strip">
    <div class="version-pill"><span data-i18n="dataVersion">数据版本</span><b id="versionLabel">-</b></div>
    <div class="version-pill"><span data-i18n="latestAssetUpdate">最新资产更新</span><b id="versionLatest">-</b></div>
    <button id="openVersionLog" type="button" data-i18n="versionLog">版本日志</button>
    <button id="langToggle" class="lang-btn" type="button">English</button>
  </div>
</header>
<div class="app">
<aside>
  <div class="control"><label for="attribute" data-i18n="attribute">属性</label><select id="attribute"></select></div>
  <div class="control"><label for="heroSearch" data-i18n="filterHero">筛选英雄</label><input id="heroSearch" data-i18n-placeholder="heroSearchPlaceholder" placeholder="输入英雄名" /></div>
  <div class="row"><button id="allBtn" data-i18n="selectAll">全选</button><button id="noneBtn" data-i18n="clear">清空</button><button id="topBtn" data-i18n="topEight">前8</button></div>
  <div class="list" id="heroList"></div>
  <div class="panel">
    <h2 data-i18n="abilityMods">技能加点</h2>
    <label class="toggle"><input type="checkbox" id="respectGating" checked /> <span data-i18n="respectGating">遵守技能解锁与 1/3/5 AP 成本</span></label>
    <label class="toggle"><input type="checkbox" id="includeContextual" /> <span data-i18n="includeContextual">断点/技能检查器纳入条件效果</span></label>
    <div class="control"><label for="abilityHero" data-i18n="currentHero">当前英雄</label><select id="abilityHero"></select></div>
    <div class="row"><button id="offSkills" data-i18n="off">关闭</button><button id="baseSkills" data-i18n="base">基础</button><button id="fullSkills" data-i18n="maxed">点满</button></div>
    <div id="abilityControls"></div>
    <div id="unitControls"></div>
  </div>
  <div class="panel">
    <h2 data-i18n="equipmentBuild">装备配装</h2>
    <div class="control"><label for="buildLevel" data-i18n="snapshotLevel">断点等级</label><input id="buildLevel" type="number" min="1" max="36" step="1" value="36" /></div>
    <div class="soul-strip"><div><span data-i18n="availableSoulsAtLevel">该等级最多可用魂魄</span><b id="panelBudgetSouls">0</b></div><button id="openSoulTable" type="button" data-i18n="levelSoulTable">等级魂魄表</button></div>
    <label class="toggle"><input type="checkbox" id="includeSoulBonuses" checked /> <span data-i18n="includeSoulBonuses">纳入魂魄阈值加成</span></label>
    <label class="toggle"><input type="checkbox" id="includePurchaseBonuses" checked /> <span data-i18n="includePurchaseBonuses">纳入装备购买加成</span></label>
    <label class="toggle"><input type="checkbox" id="includeActiveItems" /> <span data-i18n="includeActiveItems">纳入主动/条件装备效果</span></label>
    <div class="item-filters">
      <div class="control"><label for="itemSearch" data-i18n="filterItem">筛选装备</label><input id="itemSearch" data-i18n-placeholder="itemSearchPlaceholder" placeholder="输入装备名" /></div>
      <div class="control"><label for="itemSlot" data-i18n="slot">槽位</label><select id="itemSlot"><option value="all" data-i18n="all">全部</option><option value="weapon" data-i18n="weapon">武器</option><option value="vitality" data-i18n="vitality">活力</option><option value="spirit" data-i18n="spirit">元灵</option></select></div>
    </div>
    <div class="row"><button id="clearItems" data-i18n="clear">清空</button><button id="cheapItems" data-i18n="tier800">800档</button><button id="passiveItems" data-i18n="allPassives">全部被动</button></div>
    <div class="item-list" id="itemList"></div>
  </div>
  <div class="note" data-i18n="curveNote">曲线只叠加所选技能带来的无条件被动/永久英雄面板属性。主动开启、条件触发、敌方效果、叠层/击杀假设不会进入曲线；条件效果开关只影响断点面板和技能检查器。开启门槛时，1/2/3/4技能分别在1/3/5/7级解锁，T1/T2/T3按1/3/5点逐层消耗。</div>
</aside>
<main>
  <section class="chart-card"><div class="head"><div><div class="title" id="chartTitle"></div><div class="subtitle" id="chartSubtitle"></div></div><label class="toggle"><input type="checkbox" id="highlightCrossings" checked /> <span data-i18n="markCrossings">标记交叉点</span></label></div><svg id="chart"></svg></section>
  <section class="stats"><div class="stat"><b id="selectedCount">0</b><span data-i18n="selectedHeroes">已选英雄</span></div><div class="stat"><b id="crossingCount">0</b><span data-i18n="visibleCrossings">可见交叉点</span></div><div class="stat"><b id="hiddenLevelOne">0</b><span data-i18n="hiddenLevelOne">已隐藏1级并列</span></div><div class="stat"><b id="modifiedCount">0</b><span data-i18n="heroesWithSkillChanges">有技能修改的英雄</span></div></section>
  <section class="build-card">
    <div class="head"><div><div class="title" id="buildTitle">英雄断点面板</div><div class="subtitle" id="buildSubtitle"></div></div><div class="chips" id="selectedItemChips"></div></div>
    <div class="build-body">
      <div class="build-grid">
        <div class="stat"><b id="budgetSouls">0</b><span data-i18n="levelSouls">等级魂魄</span></div>
        <div class="stat" id="itemCostBox"><b id="itemCost">0</b><span data-i18n="itemSpend">装备花费</span></div>
        <div class="stat"><b id="remainingSouls">0</b><span data-i18n="remainingSouls">剩余魂魄</span></div>
        <div class="stat"><b id="purchaseBonusCount">0</b><span data-i18n="purchaseBonus">购买加成</span></div>
        <div class="stat"><b id="passiveItemCount">0</b><span data-i18n="itemPassiveEffects">装备被动效果</span></div>
      </div>
      <div class="build-table"><table><thead><tr><th data-i18n="attribute">属性</th><th data-i18n="withoutItems">无装备</th><th data-i18n="afterBuild">配装后</th><th data-i18n="delta">变化</th></tr></thead><tbody id="buildRows"></tbody></table></div>
    </div>
  </section>
  <section class="skill-card">
    <div class="head"><div><div class="title" data-i18n="skillInspector">技能检查器</div><div class="subtitle" id="skillSubtitle"></div></div></div>
    <div class="skill-body"><div class="skill-grid" id="skillInspector"></div></div>
  </section>
  <section class="table-card"><div class="head"><div><div class="title" data-i18n="crossings">交叉点</div><div class="subtitle" data-i18n="crossingsSubtitle">交叉点跟随曲线逻辑：包含技能被动面板加成，不包含装备、魂魄或购买加成。</div></div><label class="toggle"><input type="checkbox" id="includeLevelOne" /> <span data-i18n="showLevelOneTies">显示1级并列</span></label></div><div class="scroll"><table><thead><tr><th data-i18n="level">等级</th><th data-i18n="interval">区间</th><th data-i18n="value">数值</th><th data-i18n="heroA">英雄A</th><th data-i18n="heroB">英雄B</th></tr></thead><tbody id="crossingRows"></tbody></table></div></section>
</main>
</div>
<div class="tooltip" id="tooltip"></div>
<div class="modal" id="soulModal" hidden>
  <div class="modal-box">
    <div class="modal-head"><b data-i18n="levelSoulBudget">等级魂魄预算</b><button id="closeSoulTable" type="button" data-i18n="close">关闭</button></div>
    <div class="modal-body"><table><thead><tr><th data-i18n="level">等级</th><th data-i18n="maxAvailableSouls">最多可用魂魄</th><th data-i18n="cumulativeUnlocks">累计解锁</th><th data-i18n="cumulativeAbilityPoints">累计技能点</th></tr></thead><tbody id="soulRows"></tbody></table></div>
  </div>
</div>
<div class="modal" id="versionModal" hidden>
  <div class="modal-box wide">
    <div class="modal-head"><b data-i18n="versionAndChangelog">版本与更新日志</b><button id="closeVersionLog" type="button" data-i18n="close">关闭</button></div>
    <div class="modal-body"><div class="version-body" id="versionBody"></div></div>
  </div>
</div>
<script>
const DATA=__PAYLOAD_JSON__;
const $=id=>document.getElementById(id);
const I18N={
  zh:{
    docTitle:"Deadlock 英雄数值控制台",appTitle:"Deadlock 英雄数值控制台",appMeta:"1-36级曲线 · 技能加点 · 装备断点 · 技能检查器",
    dataVersion:"数据版本",latestAssetUpdate:"最新资产更新",versionLog:"版本日志",attribute:"属性",filterHero:"筛选英雄",heroSearchPlaceholder:"输入英雄名",
    selectAll:"全选",clear:"清空",topEight:"前8",abilityMods:"技能加点",respectGating:"遵守技能解锁与 1/3/5 AP 成本",includeContextual:"断点/技能检查器纳入条件效果",
    currentHero:"当前英雄",off:"关闭",base:"基础",maxed:"点满",equipmentBuild:"装备配装",snapshotLevel:"断点等级",availableSoulsAtLevel:"该等级最多可用魂魄",
    levelSoulTable:"等级魂魄表",includeSoulBonuses:"纳入魂魄阈值加成",includePurchaseBonuses:"纳入装备购买加成",includeActiveItems:"纳入主动/条件装备效果",
    filterItem:"筛选装备",itemSearchPlaceholder:"输入装备名",slot:"槽位",all:"全部",weapon:"武器",vitality:"活力",spirit:"元灵",tier800:"800档",allPassives:"全部被动",
    curveNote:"曲线只叠加所选技能带来的无条件被动/永久英雄面板属性。主动开启、条件触发、敌方效果、叠层/击杀假设不会进入曲线；条件效果开关只影响断点面板和技能检查器。开启门槛时，1/2/3/4技能分别在1/3/5/7级解锁，T1/T2/T3按1/3/5点逐层消耗。",
    markCrossings:"标记交叉点",selectedHeroes:"已选英雄",visibleCrossings:"可见交叉点",hiddenLevelOne:"已隐藏1级并列",heroesWithSkillChanges:"有技能修改的英雄",
    levelSouls:"等级魂魄",itemSpend:"装备花费",remainingSouls:"剩余魂魄",purchaseBonus:"购买加成",itemPassiveEffects:"装备被动效果",
    withoutItems:"无装备",afterBuild:"配装后",delta:"变化",skillInspector:"技能检查器",crossings:"交叉点",crossingsSubtitle:"交叉点跟随曲线逻辑：包含技能被动面板加成，不包含装备、魂魄或购买加成。",
    showLevelOneTies:"显示1级并列",level:"等级",interval:"区间",value:"数值",heroA:"英雄A",heroB:"英雄B",levelSoulBudget:"等级魂魄预算",
    maxAvailableSouls:"最多可用魂魄",cumulativeUnlocks:"累计解锁",cumulativeAbilityPoints:"累计技能点",versionAndChangelog:"版本与更新日志",close:"关闭",
    unrecorded:"未记录",unknown:"未知",sourceMissing:"源文件未提供",officialGameVersion:"官方游戏版本",dataSnapshot:"数据快照",generatedAt:"生成时间",
    selectableHeroes:"可选英雄",items:"装备",skillProperties:"技能属性",sourceFile:"来源文件",usage:"用途",records:"记录数",fileTime:"文件时间",assetUpdateTime:"资产更新时间",
    sourceFiles:"源文件",heroCount:"英雄",itemCount:"装备",respectGateOn:"遵守门槛",respectGateOff:"不限制门槛",skillPassivePanel:"技能被动面板加成",skillPassiveOn:"已启用",skillPassiveOff:"未启用",
    noItemSoul:"不含装备/魂魄加成",currentLevel:"级",overBudget:"超出预算",withinBudget:"预算内",skillGateNote:"技能遵守当前解锁/技能点门槛",
    stackAssumption:"叠层 / 击杀假设",purchaseBonusSource:"购买加成",soulBonusSource:"魂魄加成",passive:"被动",mappedPassive:"条已映射被动",itemWouldOverBudget:"添加后会超出当前等级魂魄预算",
    heroSnapshot:"英雄断点面板",sameBuildContext:"使用同一技能/装备/魂魄/购买加成上下文",target:"目标",unlock:"解锁",effective:"当前生效",needsUnlock:"需解锁或当前关闭",
    noSkillRows:"该分组没有可显示数值。",emptySkill:"该技能没有可检查数值。",emptyHeroSkills:"该英雄没有技能数据。",rowValue:"数值",baseline:"基准",build:"配装",
    unsupported:"不支持",rawValue:"原始值",notUnlocked:"未解锁",notSelectedOrLocked:"未选择或未达到解锁等级",upgradeBase:"基础",spiritPower:"元灵力量",
    spiritScaling:"元灵缩放",spiritHealingScaling:"元灵治疗缩放",duration:"持续",range:"范围",radius:"半径",cooldown:"冷却",chargeCooldown:"充能冷却",extraCharges:"额外充能",
    healingOutput:"治疗输出",originalValue:"原始值",noCrossings:"当前选择在1-36级内没有唯一交叉点。",hidden:"已隐藏"
  },
  en:{
    docTitle:"Deadlock Hero Stat Console",appTitle:"Deadlock Hero Stat Console",appMeta:"Levels 1-36 · Ability Points · Item Snapshot · Skill Inspector",
    dataVersion:"Data Version",latestAssetUpdate:"Latest Asset Update",versionLog:"Version Log",attribute:"Attribute",filterHero:"Filter Heroes",heroSearchPlaceholder:"Hero name",
    selectAll:"All",clear:"Clear",topEight:"Top 8",abilityMods:"Ability Points",respectGating:"Respect unlock levels and 1/3/5 AP costs",includeContextual:"Include conditional effects in Snapshot/Skill Inspector",
    currentHero:"Current Hero",off:"Off",base:"Base",maxed:"Maxed",equipmentBuild:"Item Build",snapshotLevel:"Snapshot Level",availableSoulsAtLevel:"Max souls available at this level",
    levelSoulTable:"Level Soul Table",includeSoulBonuses:"Include soul threshold bonuses",includePurchaseBonuses:"Include item purchase bonuses",includeActiveItems:"Include active/conditional item effects",
    filterItem:"Filter Items",itemSearchPlaceholder:"Item name",slot:"Slot",all:"All",weapon:"Weapon",vitality:"Vitality",spirit:"Spirit",tier800:"800 Tier",allPassives:"All Passives",
    curveNote:"Curves only include unconditional passive/permanent hero panel stats from selected abilities. Active, conditional, enemy-side, stack, and kill assumptions are excluded from curves; the conditional toggle only affects Hero Snapshot and Skill Inspector. With gating enabled, abilities 1/2/3/4 unlock at levels 1/3/5/7, and T1/T2/T3 cost 1/3/5 points in order.",
    markCrossings:"Mark Crossings",selectedHeroes:"Selected Heroes",visibleCrossings:"Visible Crossings",hiddenLevelOne:"Hidden Level 1 Ties",heroesWithSkillChanges:"Heroes With Skill Changes",
    levelSouls:"Level Souls",itemSpend:"Item Spend",remainingSouls:"Remaining Souls",purchaseBonus:"Purchase Bonuses",itemPassiveEffects:"Item Passive Effects",
    withoutItems:"No Items",afterBuild:"After Build",delta:"Delta",skillInspector:"Skill Inspector",crossings:"Crossings",crossingsSubtitle:"Crossing points follow curve logic: ability passive panel effects are included; items, souls, and purchase bonuses are excluded.",
    showLevelOneTies:"Show Level 1 Ties",level:"Level",interval:"Interval",value:"Value",heroA:"Hero A",heroB:"Hero B",levelSoulBudget:"Level Soul Budget",
    maxAvailableSouls:"Max Available Souls",cumulativeUnlocks:"Cumulative Unlocks",cumulativeAbilityPoints:"Cumulative Ability Points",versionAndChangelog:"Version and Changelog",close:"Close",
    unrecorded:"Unrecorded",unknown:"Unknown",sourceMissing:"Not provided by source files",officialGameVersion:"Official Game Version",dataSnapshot:"Data Snapshot",generatedAt:"Generated At",
    selectableHeroes:"Selectable Heroes",items:"Items",skillProperties:"Skill Properties",sourceFile:"Source File",usage:"Usage",records:"Records",fileTime:"File Time",assetUpdateTime:"Asset Update Time",
    sourceFiles:"Source Files",heroCount:"Heroes",itemCount:"Items",respectGateOn:"Gated",respectGateOff:"Ungated",skillPassivePanel:"Ability passive panel bonuses",skillPassiveOn:"Enabled",skillPassiveOff:"Disabled",
    noItemSoul:"No item/soul bonuses",currentLevel:"Level",overBudget:"Over Budget",withinBudget:"Within Budget",skillGateNote:"Abilities respect current unlock/AP gates",
    stackAssumption:"Stack / Kill Assumptions",purchaseBonusSource:"Purchase Bonus",soulBonusSource:"Soul Bonus",passive:"Passive",mappedPassive:"mapped passives",itemWouldOverBudget:"Adding this would exceed the soul budget for the current level",
    heroSnapshot:"Hero Snapshot",sameBuildContext:"Same ability/item/soul/purchase bonus context",target:"Target",unlock:"Unlock",effective:"Effective",needsUnlock:"Needs unlock or currently off",
    noSkillRows:"No values in this group.",emptySkill:"No inspectable values for this ability.",emptyHeroSkills:"No skill data for this hero.",rowValue:"Value",baseline:"Baseline",build:"Build",
    unsupported:"Unsupported",rawValue:"Raw Value",notUnlocked:"Locked",notSelectedOrLocked:"Not selected or not yet unlocked",upgradeBase:"Base",spiritPower:"Spirit Power",
    spiritScaling:"Spirit Scaling",spiritHealingScaling:"Spirit Healing Scaling",duration:"Duration",range:"Range",radius:"Radius",cooldown:"Cooldown",chargeCooldown:"Recharge Cooldown",extraCharges:"Extra Charges",
    healingOutput:"Healing Output",originalValue:"Original Value",noCrossings:"No unique crossing point in levels 1-36 for the current selection.",hidden:"Hidden"
  }
};
const LANGUAGE_KEY="deadlock-level-tool-language";
function savedLanguage(){try{return localStorage.getItem(LANGUAGE_KEY)}catch(e){return null}}
function saveLanguage(){try{localStorage.setItem(LANGUAGE_KEY,lang)}catch(e){}}
let lang=savedLanguage()==="en"?"en":"zh";
function t(key){return (I18N[lang]&&I18N[lang][key])||I18N.zh[key]||key}
function applyStaticText(){
  document.documentElement.lang=lang==="zh"?"zh-CN":"en";
  document.title=t("docTitle");
  document.querySelectorAll("[data-i18n]").forEach(el=>{el.textContent=t(el.dataset.i18n)});
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el=>{el.placeholder=t(el.dataset.i18nPlaceholder)});
  $("langToggle").textContent=lang==="zh"?"English":"中文";
}
function attrLabel(a){return lang==="en"?(a.labelEn||a.label):a.label}
function attrGroup(a){return lang==="en"?(a.groupEn||a.group):a.group}
function localized(primary,zh){return lang==="zh"?(zh||primary):primary}
function heroName(h){return localized(h?.name||"",h?.nameZh)}
function heroNameById(id){return heroName(heroById(id))}
function abilityName(a){return localized(a?.abilityName||"",a?.abilityNameZh)}
function itemName(item){return localized(item?.name||"",item?.nameZh)}
function propLabel(prop){return localized(prop?.label||prop?.name||"",prop?.labelZh)}
function effectLabel(effect){return localized(effect?.label||effect?.property||"",effect?.labelZh)}
function matchLocalized(query,...values){let q=String(query||"").trim().toLowerCase();if(!q)return true;return values.some(v=>String(v||"").toLowerCase().includes(q))}
const SLOT_NAMES={zh:{weapon:"武器",vitality:"活力",spirit:"元灵",all:"全部"},en:{weapon:"Weapon",vitality:"Vitality",spirit:"Spirit",all:"All"}};
function slotName(slot){return (SLOT_NAMES[lang]||SLOT_NAMES.zh)[slot]||slot}
function activationLabel(value){let raw=String(value||"");let lower=raw.toLowerCase();if(!raw||raw==="被动"||lower.includes("passive"))return t("passive");return raw}
const STATE_LABELS={zh:{0:"关闭",1:"基础",2:"T1",3:"T2",4:"T3"},en:{0:"Off",1:"Base",2:"T1",3:"T2",4:"T3"}};
function stateLabel(v){return (STATE_LABELS[lang]||STATE_LABELS.zh)[v]||String(v)}
const ABILITY_SLOT_LABELS={zh:{signature1:"1技能",signature2:"2技能",signature3:"3技能",signature4:"4技能"},en:{signature1:"Ability 1",signature2:"Ability 2",signature3:"Ability 3",signature4:"Ability 4"}};
function abilitySlotLabel(slot){return (ABILITY_SLOT_LABELS[lang]||ABILITY_SLOT_LABELS.zh)[slot]||slot}
const SKILL_SECTION_LABELS={zh:{main:"主要数值",contextual:"条件 / 叠层",unsupported:"未支持 / 原始值"},en:{main:"Main Values",contextual:"Conditional / Stacks",unsupported:"Unsupported / Raw"}};
function skillSectionLabel(name){return (SKILL_SECTION_LABELS[lang]||SKILL_SECTION_LABELS.zh)[name]||name}
function levelText(level){return lang==="zh"?`${level}级`:`Level ${level}`}
function setLanguage(next){lang=next==="en"?"en":"zh";saveLanguage();applyStaticText();renderAttributeOptions();renderAbilityHeroOptions();renderAll()}
const selected=new Set(DATA.heroes.map(h=>h.id));
const selectedItems=new Set();
const skillState={}; const effectUnits={}; let hotHeroes=new Set();
const SLOT_ORDER=["signature1","signature2","signature3","signature4"];
const TIER_COST={2:DATA.levelInfo.upgradeCosts.T1,3:DATA.levelInfo.upgradeCosts.T2,4:DATA.levelInfo.upgradeCosts.T3};
const SLOT_UNLOCK=DATA.levelInfo.slotUnlockLevels;
const BONUS_TARGETS={"MODIFIER_VALUE_BASE_HEALTH_PERCENT":["max_health_pct","percent"],"MODIFIER_VALUE_HEALTH_MAX_PERCENT":["max_health_pct","percent"],"MODIFIER_VALUE_TECH_POWER":["spirit_power_add","flat"],"MODIFIER_VALUE_TECH_POWER_PERCENT":["spirit_power_pct","percent"],"MODIFIER_VALUE_WEAPON_DAMAGE_INCREASE":["weapon_damage_pct","percent"]};
const CATEGORY_TARGETS={vitality:["max_health_pct","percent"],spirit:["spirit_power_add","flat"],weapon:["weapon_damage_pct","percent"]};
for(const h of DATA.heroes){skillState[h.id]={}; for(const a of DATA.abilities.filter(x=>x.heroId===h.id)) skillState[h.id][a.slot]=0}
for(const e of DATA.effects) if(e.perUnit) effectUnits[e.id]=0;
function n(v){if(Number.isFinite(v))return v;let x=Number(String(v??"").replace("m",""));return Number.isFinite(x)?x:0}
function fmt(v){if(!Number.isFinite(v))return"";let a=Math.abs(v);if(a>=1000)return v.toFixed(0);if(a>=100)return v.toFixed(1);if(a>=10)return v.toFixed(2);return v.toFixed(3).replace(/0+$/,"").replace(/\.$/,"")}
function currentAttr(){return DATA.attributes.find(a=>a.id===$("attribute").value)}
function heroById(id){return DATA.heroes.find(h=>h.id===id)}
function levelGate(level){let l=Math.max(DATA.minLevel,Math.min(DATA.maxLevel,Math.floor(level+1e-7)));return DATA.levelInfo.levels[String(l)]}
function renderVersionSummary(){
  const v=DATA.versionInfo||{},counts=v.generatedCounts||{};
  $("versionLabel").textContent=(lang==="en"?(v.dataVersionEn||v.dataVersion):v.dataVersion)||t("unrecorded");
  $("versionLatest").textContent=(lang==="en"?(v.latestAssetUpdateEn||v.latestAssetUpdate):v.latestAssetUpdate)||t("unknown");
  $("openVersionLog").title=`${t("sourceFiles")} ${v.sourceFiles?.length||0} · ${t("heroCount")} ${counts.selectableHeroes||0} · ${t("itemCount")} ${counts.shopItems||0}`;
}
function renderVersionLog(){
  const v=DATA.versionInfo||{},counts=v.generatedCounts||{};
  const cards=[
    [t("officialGameVersion"),(lang==="en"?(v.gameVersionEn||v.gameVersion):v.gameVersion)||t("sourceMissing")],
    [t("dataSnapshot"),(lang==="en"?(v.dataVersionEn||v.dataVersion):v.dataVersion)||t("unrecorded")],
    [t("generatedAt"),v.generatedAt||t("unrecorded")],
    [t("selectableHeroes"),counts.selectableHeroes??"-"],
    [t("items"),counts.shopItems??"-"],
    [t("skillProperties"),counts.skillProperties??"-"],
  ];
  const summary=`<div class="version-summary">${cards.map(([k,val])=>`<div class="version-card"><span>${k}</span><b>${esc(val)}</b></div>`).join("")}</div>`;
  const notes=(lang==="en"?(v.notesEn||v.notes):v.notes||[]).map(x=>`<li>${esc(x)}</li>`).join("");
  const logEntries=lang==="en"?(v.changelogEn||v.changelog):v.changelog||[];
  const logs=logEntries.map(entry=>`<div class="log-entry"><h3>${esc(entry.title)}</h3><small>${esc(entry.date)}</small><ul>${(entry.items||[]).map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`).join("");
  const sources=`<div class="source-table"><table><thead><tr><th>${t("sourceFile")}</th><th>${t("usage")}</th><th>${t("records")}</th><th>${t("fileTime")}</th><th>${t("assetUpdateTime")}</th></tr></thead><tbody>${(v.sourceFiles||[]).map(s=>`<tr><td>${esc(s.name)}</td><td>${esc(lang==="en"?(s.roleEn||s.role):s.role)}</td><td>${esc(s.records)}</td><td>${esc(s.modifiedAt)}</td><td>${esc(lang==="en"?(s.assetUpdateRangeEn||s.assetUpdateRange):s.assetUpdateRange)}</td></tr>`).join("")}</tbody></table></div>`;
  $("versionBody").innerHTML=summary+(notes?`<div class="note"><ul>${notes}</ul></div>`:"")+logs+sources;
}
function openVersionLog(){renderVersionLog();$("versionModal").hidden=false}
function closeVersionLog(){$("versionModal").hidden=true}
function effectiveStates(heroId,level){
  const desired=skillState[heroId]||{};
  if(!$("respectGating")||!$("respectGating").checked)return {...desired};
  const gate=levelGate(level);
  let points=gate.cumulativeAbilityPoints,state={};
  for(const slot of SLOT_ORDER){
    state[slot]=0;
    if(level>=SLOT_UNLOCK[slot]&&(desired[slot]||0)>=1)state[slot]=1;
  }
  for(const tier of [2,3,4])for(const slot of SLOT_ORDER){
    if(level>=SLOT_UNLOCK[slot]&&(desired[slot]||0)>=tier&&state[slot]===tier-1&&points>=TIER_COST[tier]){
      state[slot]=tier;
      points-=TIER_COST[tier];
    }
  }
  return state;
}
function curveSkillEffects(heroId,level){const state=effectiveStates(heroId,level);return DATA.effects.filter(e=>e.heroId===heroId && e.includeInCurve && (state[e.slot]||0)>=e.requiredState && (!e.perUnit || n(effectUnits[e.id])!==0))}
function snapshotSkillEffects(heroId,level){const state=effectiveStates(heroId,level),ctx=$("includeContextual")?.checked;return DATA.effects.filter(e=>e.heroId===heroId && (e.includeInCurve||ctx) && (state[e.slot]||0)>=e.requiredState && (!e.perUnit || n(effectUnits[e.id])!==0))}
function effectAmount(e,spirit){let units=e.perUnit?n(effectUnits[e.id]):1;return (n(e.value)+n(e.scaleWithSpirit)*spirit)*units}
function baseValuesAt(heroId,level,effects=[]){
  const r=DATA.base[heroId],t=level-1,effs=effects||[];
  let techAdd=0,techPct=0;
  for(const e of effs){if(e.target==="spirit_power_add")techAdd+=effectAmount(e,0); if(e.target==="spirit_power_pct")techPct+=effectAmount(e,0)}
  let spirit=(n(r.growth_spirit_power_per_level)*t+techAdd)*(1+techPct/100);
  let m={max_health_add:0,max_health_pct:0,health_regen_add:0,bullet_armor_add:0,spirit_armor_add:0,move_speed_add:0,move_speed_pct:0,sprint_speed_add:0,stamina_add:0,stamina_regen_pct:0,bullet_damage_add:0,weapon_damage_pct:0,clip_size_add:0,clip_size_pct:0,fire_rate_pct:0,bullet_speed_pct:0,melee_damage_pct:0,barrier_add:0,tech_range_pct:0,tech_radius_pct:0,tech_duration_pct:0,tech_cooldown_pct:0,charge_cooldown_pct:0,ability_charges_add:0,healing_output_pct:0,weapon_range_add:0,weapon_range_pct:0};
  for(const e of effs){if(e.target in m)m[e.target]+=effectAmount(e,spirit)}
  let max_health=(n(r.base_max_health)+n(r.growth_health_per_level)*t+m.max_health_add)*(1+m.max_health_pct/100);
  let health_regen=n(r.base_health_regen)+n(r.scaling_EBaseHealthRegen_scale)*spirit+m.health_regen_add;
  let bullet_armor_pct=n(r.base_bullet_armor_pct)+n(r.growth_bullet_armor_pct_per_level)*t+n(r.scaling_EBulletArmorDamageReduction_scale)*spirit+m.bullet_armor_add;
  let spirit_armor_pct=n(r.base_spirit_armor_pct)+n(r.growth_spirit_resist_pct_per_level)*t+n(r.scaling_ETechArmorDamageReduction_scale)*spirit+m.spirit_armor_add;
  let move_speed=(n(r.base_move_speed)+n(r.scaling_EMaxMoveSpeed_scale)*spirit+m.move_speed_add)*(1+m.move_speed_pct/100);
  let sprint_speed=n(r.base_sprint_speed)+n(r.scaling_ESprintSpeed_scale)*spirit+m.sprint_speed_add;
  let stamina=n(r.base_stamina)+m.stamina_add;
  let stamina_regen_per_second=n(r.base_stamina_regen_per_second)*(1+m.stamina_regen_pct/100);
  let baseBullet=n(r.base_bullet_damage)+n(r.growth_bullet_damage_per_level)*t+n(r.scaling_EBulletDamage_scale)*spirit;
  let bullet_damage=baseBullet*(1+m.weapon_damage_pct/100)+m.bullet_damage_add;
  let bullets=Math.max(1,n(r.base_bullets)||1);
  let damage_per_shot=bullet_damage*bullets;
  let clip_size=(n(r.base_clip_size)+n(r.scaling_EClipSize_scale)*spirit+m.clip_size_add)*(1+m.clip_size_pct/100);
  let rps=n(r.base_shots_per_second)+n(r.scaling_ERoundsPerSecond_scale)*spirit;
  let firePct=n(r.scaling_EFireRate_scale)*spirit+m.fire_rate_pct;
  let shots_per_second=rps*(1+firePct/100);
  let bullets_per_second=shots_per_second*bullets;
  let weapon_dps=bullet_damage*bullets_per_second;
  let damage_per_magazine=damage_per_shot*clip_size;
  let light_melee_damage=(n(r.base_light_melee_damage)+n(r.growth_melee_damage_per_level)*t)*(1+m.melee_damage_pct/100);
  let heavy_melee_damage=(n(r.base_heavy_melee_damage)+n(r.growth_melee_damage_per_level)*t+n(r.scaling_EHeavyMeleeDamage_scale)*spirit)*(1+m.melee_damage_pct/100);
  let weapon_range=(n(r.base_weapon_range)+n(r.growth_bonus_attack_range_per_level)*t+m.weapon_range_add)*(1+m.weapon_range_pct/100);
  return {max_health,health_regen,bullet_armor_pct,spirit_armor_pct,move_speed,sprint_speed,crouch_speed:n(r.base_crouch_speed),move_acceleration:n(r.base_move_acceleration),stamina,stamina_regen_per_second,spirit_power:spirit,barrier_health:m.barrier_add,tech_range:n(r.base_tech_range)*(1+m.tech_range_pct/100),tech_radius:1*(1+m.tech_radius_pct/100),tech_duration:n(r.base_tech_duration)*(1+m.tech_duration_pct/100),tech_cooldown_pct:m.tech_cooldown_pct,charge_cooldown_pct:m.charge_cooldown_pct,ability_charges_add:m.ability_charges_add,healing_output_pct:m.healing_output_pct,bullet_damage,damage_per_shot,clip_size,shots_per_second,bullets_per_second,weapon_dps,damage_per_magazine,reload_duration:n(r.base_reload_duration),reload_speed:n(r.base_reload_speed),bullet_speed:n(r.base_bullet_speed)*(1+m.bullet_speed_pct/100),weapon_range,light_melee_damage,heavy_melee_damage,crit_damage_received_scale:n(r.base_crit_damage_received_scale)}
}
function curveValuesAt(heroId,level){return baseValuesAt(heroId,level,curveSkillEffects(heroId,level))}
function heroSnapshotValuesAt(heroId,level,buildContext={}){const extraEffects=Array.isArray(buildContext)?buildContext:(buildContext.extraEffects||[]),skills=buildContext.includeContextual===false?curveSkillEffects(heroId,level):snapshotSkillEffects(heroId,level);return baseValuesAt(heroId,level,skills.concat(extraEffects||[]))}
function valueAt(heroId,attr,level){return curveValuesAt(heroId,level)[attr]??0}
function renderAttributeOptions(){let current=$("attribute").value||"max_health",groups=new Map();for(const a of DATA.attributes){let g=attrGroup(a);if(!groups.has(g))groups.set(g,[]);groups.get(g).push(a)}$("attribute").innerHTML="";for(const [g,attrs] of groups){let og=document.createElement("optgroup");og.label=g;for(const a of attrs){let o=document.createElement("option");o.value=a.id;o.textContent=attrLabel(a);og.appendChild(o)}$("attribute").appendChild(og)}$("attribute").value=DATA.attributes.some(a=>a.id===current)?current:"max_health"}
function initAttributes(){renderAttributeOptions()}
function renderHeroList(){let q=$("heroSearch").value;$("heroList").innerHTML="";for(const h of DATA.heroes.filter(h=>matchLocalized(q,h.name,h.nameZh))){let lab=document.createElement("label");lab.className="check";let cb=document.createElement("input");cb.type="checkbox";cb.checked=selected.has(h.id);cb.onchange=()=>{cb.checked?selected.add(h.id):selected.delete(h.id);renderAll()};let sw=document.createElement("span");sw.className="swatch";sw.style.background=h.color;let tx=document.createElement("span");let mod=Object.values(skillState[h.id]||{}).some(v=>v>0)?" *":"";tx.textContent=heroName(h)+mod;lab.append(cb,sw,tx);$("heroList").appendChild(lab)}}
function renderAbilityHeroOptions(){let current=$("abilityHero").value;$("abilityHero").innerHTML="";for(const h of DATA.heroes){let o=document.createElement("option");o.value=h.id;o.textContent=heroName(h);$("abilityHero").appendChild(o)}$("abilityHero").value=DATA.heroes.some(h=>h.id===current)?current:(DATA.heroes[0]?.id||"")}
function initAbilityHero(){renderAbilityHeroOptions()}
function renderAbilityControls(){let id=$("abilityHero").value,abs=DATA.abilities.filter(a=>a.heroId===id);$("abilityControls").innerHTML="";for(const a of abs){let div=document.createElement("div");div.className="ability";let name=document.createElement("div");name.innerHTML=`<b>${abilityName(a)}</b><small>${abilitySlotLabel(a.slot)}</small>`;let sel=document.createElement("select");[["0",t("off")],["1",t("base")],["2","T1"],["3","T2"],["4",t("maxed")]].forEach(([v,l])=>{let o=document.createElement("option");o.value=v;o.textContent=l;sel.appendChild(o)});sel.value=skillState[id][a.slot]||0;sel.onchange=()=>{skillState[id][a.slot]=Number(sel.value);renderAll()};div.append(name,sel);$("abilityControls").appendChild(div)}renderUnitControls()}
function renderUnitControls(){let id=$("abilityHero").value,ctx=$("includeContextual")?.checked,effs=DATA.effects.filter(e=>e.heroId===id&&e.perUnit&&(e.includeInCurve||ctx)&&((skillState[id]?.[e.slot]||0)>=e.requiredState));let wrap=$("unitControls");wrap.innerHTML="";if(!effs.length)return;let title=document.createElement("h2");title.textContent=t("stackAssumption");wrap.appendChild(title);for(const e of effs){let div=document.createElement("div");div.className="unit";let span=document.createElement("span");span.innerHTML=`${abilityName(e)}: ${effectLabel(e)}<em>${e.source} · ${e.mode} ${fmt(e.value||e.scaleWithSpirit)}</em>`;let inp=document.createElement("input");inp.type="number";inp.min="0";inp.step="1";inp.value=effectUnits[e.id]||0;inp.oninput=()=>{effectUnits[e.id]=Number(inp.value||0);renderAll()};div.append(span,inp);wrap.appendChild(div)}}
function buildLevel(){let v=Math.round(n($("buildLevel")?.value||DATA.maxLevel));return Math.max(DATA.minLevel,Math.min(DATA.maxLevel,v))}
function selectedItemRows(){return DATA.items.filter(i=>selectedItems.has(i.id))}
function itemSpend(){return selectedItemRows().reduce((s,i)=>s+n(i.cost),0)}
function itemEffectsForBuild(){let ctx=$("includeActiveItems")?.checked;return DATA.itemEffects.filter(e=>selectedItems.has(e.itemId)&&(e.includeInBuild||ctx)&&!e.perUnit)}
function bonusEffect(id,target,mode,value,source,label){return {id,source,label,target,mode,value:n(value),scaleWithSpirit:0,perUnit:false}}
function renderSoulBudget(){
  const level=buildLevel(),budget=n(levelGate(level).requiredSouls);
  $("panelBudgetSouls").textContent=fmt(budget);
}
function renderSoulRows(){
  const level=buildLevel();
  $("soulRows").innerHTML=Array.from({length:DATA.maxLevel-DATA.minLevel+1},(_,i)=>DATA.minLevel+i).map(l=>{
    const gate=levelGate(l),curr=l===level?" class=\"current\"":"";
    return `<tr${curr}><td>${l}</td><td>${fmt(n(gate.requiredSouls))}</td><td>${gate.cumulativeUnlocks}</td><td>${gate.cumulativeAbilityPoints}</td></tr>`;
  }).join("");
}
function openSoulTable(){renderSoulRows();$("soulModal").hidden=false}
function closeSoulTable(){$("soulModal").hidden=true}
function purchaseBonusEffects(heroId){
  if(!$("includePurchaseBonuses")?.checked)return [];
  const bonuses=DATA.heroBonuses[heroId]?.purchase||{},out=[];
  for(const item of selectedItemRows()){
    const row=(bonuses[item.slot]||[]).find(b=>n(b.tier)===n(item.tier));
    const target=row&&(BONUS_TARGETS[row.value_type]||CATEGORY_TARGETS[item.slot]);
    if(target)out.push(bonusEffect(`purchase:${item.id}`,target[0],target[1],row.value,t("purchaseBonusSource"),`${itemName(item)} T${item.tier} ${slotName(item.slot)}`));
  }
  return out;
}
function soulBonusEffects(heroId,level){
  if(!$("includeSoulBonuses")?.checked)return [];
  const total=n(levelGate(level).requiredSouls),costs=DATA.heroBonuses[heroId]?.cost||{},out=[];
  for(const cat of Object.keys(CATEGORY_TARGETS)){
    let rows=(costs[cat]||[]).filter(b=>n(b.gold_threshold)<=total).sort((a,b)=>n(a.gold_threshold)-n(b.gold_threshold));
    let best=rows[rows.length-1],target=CATEGORY_TARGETS[cat];
    if(best)out.push(bonusEffect(`soul:${cat}:${best.gold_threshold}`,target[0],target[1],best.bonus,t("soulBonusSource"),`${slotName(cat)} ${best.gold_threshold}`));
  }
  return out;
}
function buildExtraEffects(heroId,level){return soulBonusEffects(heroId,level).concat(itemEffectsForBuild(),purchaseBonusEffects(heroId))}
function buildBaselineEffects(heroId,level){return soulBonusEffects(heroId,level)}
function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]))}
function one(v){let x=n(v);return Math.abs(x)<1e-9?1:x}
function skillPostfix(prop){return prop.postfix||""}
function formatSkillValue(calc,prop){if(calc.locked)return t("notUnlocked");if(!Number.isFinite(calc.value))return"";return `${fmt(calc.value)}${skillPostfix(prop)}`}
function skillDelta(base,build,prop){if(base.locked||build.locked||!Number.isFinite(base.value)||!Number.isFinite(build.value))return"";let d=build.value-base.value;return `${d>=0?"+":""}${fmt(d)}${skillPostfix(prop)}`}
function applySkillUpgrades(prop,state){
  let base=n(prop.value),scale=n(prop.statScale),sources=[],unsupported=[];
  for(const up of prop.upgrades||[]){
    if(state<n(up.requiredState))continue;
    const bonus=n(up.bonus),type=up.upgradeType||"";
    sources.push(`${up.source} ${type||t("upgradeBase")} ${fmt(bonus)}`);
    if(!type||type==="EAddToBase")base+=bonus;
    else if(type==="EAddToScale")scale+=bonus;
    else if(type==="EMultiplyBase")base*=bonus;
    else if(type==="EMultiplyScale")scale*=bonus;
    else unsupported.push(type);
  }
  return {base,scale,sources,unsupported};
}
function calcSkillPropValue(prop,stats,state){
  if(state<1)return {locked:true,value:null,sources:[t("notSelectedOrLocked")],unsupported:[]};
  const prep=applySkillUpgrades(prop,state);
  let value=prep.base,sources=prep.sources.slice(),unsupported=prep.unsupported.slice();
  const cls=prop.scaleClass||"",stat=prop.specificStat||"",scale=n(prep.scale),text=`${prop.name} ${prop.label}`.toLowerCase();
  const addSpirit=label=>{if(Math.abs(scale)>1e-9){value+=scale*n(stats.spirit_power);sources.push(`${label} ${fmt(scale)}*${t("spiritPower")}`)}};
  const mul=(label,amount)=>{let mult=one(amount);value*=mult;if(Math.abs(mult-1)>1e-9)sources.push(`${label} ${fmt(mult)}x`)};
  const cooldown=(label,amount)=>{let pct=n(amount);value=Math.max(0,value*(1-pct/100));if(Math.abs(pct)>1e-9)sources.push(`${label} -${fmt(pct)}%`)};
  const healing=()=>{if(text.includes("heal")){let pct=n(stats.healing_output_pct);value*=1+pct/100;if(Math.abs(pct)>1e-9)sources.push(`${t("healingOutput")} +${fmt(pct)}%`)}};
  if(!cls){
    if(Math.abs(scale)>1e-9)unsupported.push("missing scale_function");
  }else if(cls==="scale_function_tech_damage"){
    addSpirit(t("spiritScaling"));
  }else if(cls==="scale_function_healing_spirit_scale"){
    addSpirit(t("spiritHealingScaling"));healing();
  }else if(cls==="scale_function_tech_duration"){
    mul(t("duration"),stats.tech_duration);
  }else if(cls==="scale_function_tech_range"){
    mul(t("range"),stats.tech_range);
  }else if(cls==="scale_function_ability_charges"){
    let extra=n(stats.ability_charges_add);value+=extra;if(Math.abs(extra)>1e-9)sources.push(`${t("extraCharges")} +${fmt(extra)}`);
  }else if(cls==="scale_function_ability_recharge_time"){
    cooldown(t("chargeCooldown"),stats.charge_cooldown_pct);
  }else if(cls==="scale_function_single_stat"){
    if(stat==="ETechPower")addSpirit(t("spiritScaling"));
    else if(stat==="ETechRange")mul(t("range"),stats.tech_range);
    else if(stat==="ETechRadius")mul(t("radius"),stats.tech_radius);
    else if(stat==="ETechDuration"||stat==="EChannelDuration")mul(t("duration"),stats.tech_duration);
    else if(stat==="ETechCooldown")cooldown(t("cooldown"),stats.tech_cooldown_pct);
    else if(stat==="EHealingOutput")healing();
    else if(stat==="ELightMeleeDamage"){value+=scale*n(stats.light_melee_damage);sources.push(`${stat} ${fmt(scale)}x`)}
    else if(stat==="EHeavyMeleeDamage"){value+=scale*n(stats.heavy_melee_damage);sources.push(`${stat} ${fmt(scale)}x`)}
    else unsupported.push(`${cls}:${stat||"no stat"}`);
  }else if(cls==="scale_function_multi_stats"){
    const statsList=prop.scalingStats||[],known=new Set(["ETechPower","ETechDuration","EChannelDuration","ETechRange","ETechRadius"]);
    if(statsList.includes("ETechPower"))addSpirit(t("spiritScaling"));
    if(statsList.includes("ETechDuration")||statsList.includes("EChannelDuration"))mul(t("duration"),stats.tech_duration);
    if(statsList.includes("ETechRange"))mul(t("range"),stats.tech_range);
    if(statsList.includes("ETechRadius"))mul(t("radius"),stats.tech_radius);
    for(const s of statsList)if(!known.has(s))unsupported.push(`${cls}:${s}`);
    if(!statsList.length)unsupported.push(cls);
  }else{
    unsupported.push(cls);
  }
  return {locked:false,value,sources:sources.length?sources:[t("originalValue")],unsupported};
}
function skillValuesAt(heroId,level,buildContext={}){
  const baselineStats=buildContext.baselineStats||heroSnapshotValuesAt(heroId,level,{extraEffects:buildBaselineEffects(heroId,level)});
  const buildStats=buildContext.buildStats||heroSnapshotValuesAt(heroId,level,{extraEffects:buildExtraEffects(heroId,level)});
  const states=effectiveStates(heroId,level),desired=skillState[heroId]||{};
  return (DATA.skillInspector[heroId]||[]).map(card=>{
    const state=states[card.slot]||0,wanted=desired[card.slot]||0,unlock=SLOT_UNLOCK[card.slot]||1;
    const rows=(card.properties||[]).map(prop=>{
      const base=calcSkillPropValue(prop,baselineStats,state),build=calcSkillPropValue(prop,buildStats,state);
      const unsupported=[...base.unsupported,...build.unsupported],section=unsupported.length?"unsupported":(prop.context==="main"?"main":"contextual");
      return {prop,base,build,section,unsupported,sources:[...new Set([...base.sources,...build.sources])]};
    });
    return {...card,state,wanted,unlock,rows};
  });
}
function renderSkillRows(rows){
  if(!rows.length)return `<div class="empty-skill">${t("noSkillRows")}</div>`;
  return `<div class="skill-row muted"><span class="name">${t("rowValue")}</span><span>${t("baseline")}</span><span>${t("build")}</span><span>${t("delta")}</span></div>`+rows.map(row=>{
    const d=row.base.locked||row.build.locked?0:(row.build.value-row.base.value),cls=d>1e-7?"delta-pos":d<-1e-7?"delta-neg":"muted";
    const source=row.sources.slice(0,3).join(" | ")+(row.sources.length>3?" | ...":"");
    const title=row.unsupported.length?`${t("unsupported")}: ${row.unsupported.join(", ")}`:source;
    return `<div class="skill-row ${row.section==="unsupported"?"unsupported":""}" title="${esc(title)}"><span class="name">${esc(propLabel(row.prop))}<small>${esc(source)}</small></span><span>${formatSkillValue(row.base,row.prop)}</span><span>${formatSkillValue(row.build,row.prop)}</span><span class="${cls}">${skillDelta(row.base,row.build,row.prop)}</span></div>`;
  }).join("");
}
function renderSkillSection(name,rows){if(!rows.length)return"";return `<div class="skill-section"><h3>${skillSectionLabel(name)}</h3>${renderSkillRows(rows)}</div>`}
function renderSkillCard(card){
  const img=card.imageWebp||card.image||"",currentState=stateLabel(card.state),wanted=stateLabel(card.wanted);
  const locked=card.state<1?`${levelText(card.unlock)} ${t("needsUnlock")}`:`${t("effective")} ${currentState}`;
  const sections=["main","contextual","unsupported"].map(name=>renderSkillSection(name,card.rows.filter(r=>r.section===name))).join("");
  const tags=[`${abilitySlotLabel(card.slot)}`,`${t("target")} ${wanted}`,locked,`${t("unlock")} L${card.unlock}`];
  return `<div class="skill-panel"><div class="skill-top">${img?`<img src="${esc(img)}" alt="">`:`<span></span>`}<div><b>${esc(abilityName(card))}</b><small>${esc(tags.join(" · "))}</small></div><span class="skill-state">${esc(currentState)}</span></div>${sections||`<div class="empty-skill">${t("emptySkill")}</div>`}</div>`;
}
function renderSkillInspector(){
  const heroId=$("abilityHero").value,level=buildLevel(),budget=n(levelGate(level).requiredSouls),spent=itemSpend();
  const cards=skillValuesAt(heroId,level);
  $("skillSubtitle").textContent=`${heroNameById(heroId)} · ${levelText(level)} · ${t("sameBuildContext")} · ${spent>budget?t("overBudget"):t("withinBudget")}`;
  $("skillInspector").innerHTML=cards.map(renderSkillCard).join("")||`<div class="empty-skill">${t("emptyHeroSkills")}</div>`;
}
function renderItemList(){
  let q=($("itemSearch")?.value||"").trim().toLowerCase(),slot=$("itemSlot")?.value||"all",budget=n(levelGate(buildLevel()).requiredSouls),spent=itemSpend();
  $("itemList").innerHTML="";
  for(const item of DATA.items.filter(i=>(slot==="all"||i.slot===slot)&&matchLocalized(q,i.name,i.nameZh))){
    const effects=DATA.itemEffects.filter(e=>e.itemId===item.id&&e.includeInBuild).length;
    let lab=document.createElement("label");lab.className=`item ${!effects?"off":""}`;
    let cb=document.createElement("input");cb.type="checkbox";cb.checked=selectedItems.has(item.id);cb.onchange=()=>{cb.checked?selectedItems.add(item.id):selectedItems.delete(item.id);renderAll()};
    let text=document.createElement("span");text.innerHTML=`<b>${itemName(item)}</b><small>${slotName(item.slot)} · T${item.tier} · ${activationLabel(item.activation)} · ${effects} ${t("mappedPassive")}</small>`;
    let cost=document.createElement("span");cost.className="cost";cost.textContent=n(item.cost);
    lab.title=selectedItems.has(item.id)||spent+n(item.cost)<=budget?"":t("itemWouldOverBudget");
    lab.append(cb,text,cost);$("itemList").appendChild(lab);
  }
}
function renderBuild(){
  const heroId=$("abilityHero").value,level=buildLevel(),budget=n(levelGate(level).requiredSouls),spent=itemSpend(),remaining=budget-spent;
  renderSoulBudget();
  $("buildTitle").textContent=`${heroNameById(heroId)} ${t("heroSnapshot")}`;
  $("buildSubtitle").textContent=`${levelText(level)} · ${spent>budget?t("overBudget"):t("withinBudget")} · ${t("skillGateNote")}`;
  $("budgetSouls").textContent=fmt(budget);$("itemCost").textContent=fmt(spent);$("remainingSouls").textContent=fmt(remaining);
  $("itemCostBox").classList.toggle("budget-bad",spent>budget);
  $("purchaseBonusCount").textContent=purchaseBonusEffects(heroId).length;
  $("passiveItemCount").textContent=itemEffectsForBuild().filter(e=>e.includeInBuild).length;
  $("selectedItemChips").innerHTML=selectedItemRows().slice(0,8).map(i=>`<span class="chip">${itemName(i)}</span>`).join("")+(selectedItems.size>8?`<span class="chip">+${selectedItems.size-8}</span>`:"");
  const base=heroSnapshotValuesAt(heroId,level,{extraEffects:buildBaselineEffects(heroId,level)}),build=heroSnapshotValuesAt(heroId,level,{extraEffects:buildExtraEffects(heroId,level)});
  $("buildRows").innerHTML=DATA.attributes.map(a=>{let d=(build[a.id]??0)-(base[a.id]??0),cls=d>1e-7?"delta-pos":d<-1e-7?"delta-neg":"";return `<tr><td>${attrLabel(a)}</td><td>${fmt(base[a.id]??0)}</td><td>${fmt(build[a.id]??0)}</td><td class="${cls}">${d>=0?"+":""}${fmt(d)}</td></tr>`}).join("");
}
function xscale(level,m,w){return m.l+(level-DATA.minLevel)/(DATA.maxLevel-DATA.minLevel)*(w-m.l-m.r)}
function renderChart(){let attr=currentAttr(),heroes=DATA.heroes.filter(h=>selected.has(h.id)),svg=$("chart"),rect=svg.getBoundingClientRect(),w=Math.max(760,rect.width||1000),hgt=560,m={t:22,r:32,b:46,l:72};svg.setAttribute("viewBox",`0 0 ${w} ${hgt}`);svg.innerHTML="";let vals=[];for(const h of heroes)for(let l=DATA.minLevel;l<=DATA.maxLevel;l++)vals.push(valueAt(h.id,attr.id,l));let min=Math.min(...vals),max=Math.max(...vals);if(!Number.isFinite(min)){min=0;max=1}if(Math.abs(max-min)<1e-7){min-=1;max+=1}let pad=(max-min)*.08;min-=pad;max+=pad;let iw=w-m.l-m.r,ih=hgt-m.t-m.b,ys=v=>m.t+(max-v)/(max-min)*ih,xs=l=>xscale(l,m,w);let mk=(tag,at={})=>{let e=document.createElementNS("http://www.w3.org/2000/svg",tag);for(const[k,v]of Object.entries(at))e.setAttribute(k,v);return e};let grid=mk("g",{class:"grid"});for(let l=1;l<=36;l+=5)grid.appendChild(mk("line",{x1:xs(l),y1:m.t,x2:xs(l),y2:hgt-m.b}));for(let i=0;i<=5;i++){let y=m.t+ih*i/5;grid.appendChild(mk("line",{x1:m.l,y1:y,x2:w-m.r,y2:y}))}svg.appendChild(grid);let axis=mk("g",{class:"axis"});axis.appendChild(mk("line",{x1:m.l,y1:hgt-m.b,x2:w-m.r,y2:hgt-m.b}));axis.appendChild(mk("line",{x1:m.l,y1:m.t,x2:m.l,y2:hgt-m.b}));for(let l=1;l<=36;l+=5){let x=xs(l);axis.appendChild(mk("line",{x1:x,y1:hgt-m.b,x2:x,y2:hgt-m.b+5}));let tx=mk("text",{x:x,y:hgt-16,"text-anchor":"middle"});tx.textContent=l;axis.appendChild(tx)}for(let i=0;i<=5;i++){let yv=max-(max-min)*i/5,y=m.t+ih*i/5;axis.appendChild(mk("line",{x1:m.l-5,y1:y,x2:m.l,y2:y}));let tx=mk("text",{x:m.l-10,y:y+4,"text-anchor":"end"});tx.textContent=fmt(yv);axis.appendChild(tx)}svg.appendChild(axis);
for(const hero of heroes){let d=[];for(let i=0;i<=220;i++){let l=DATA.minLevel+(DATA.maxLevel-DATA.minLevel)*i/220;d.push(`${i?"L":"M"}${xs(l).toFixed(2)},${ys(valueAt(hero.id,attr.id,l)).toFixed(2)}`)}let p=mk("path",{class:`curve ${hotHeroes.size&&!hotHeroes.has(hero.id)?"dim":""} ${hotHeroes.has(hero.id)?"hot":""}`,d:d.join(" "),stroke:hero.color});p.onmouseenter=()=>{hotHeroes=new Set([hero.id]);renderChart()};p.onmouseleave=()=>{hotHeroes=new Set();renderChart()};svg.appendChild(p)}
if($("highlightCrossings").checked){for(const row of visibleIntersections(attr.id).slice(0,450)){svg.appendChild(mk("circle",{class:"dot",cx:xs(row.level),cy:ys(row.value),r:row.level===1?2.1:3.1}))}}
let overlay=mk("rect",{x:m.l,y:m.t,width:iw,height:ih,fill:"transparent"});overlay.onmousemove=ev=>{let pt=svg.createSVGPoint();pt.x=ev.clientX;pt.y=ev.clientY;let cur=pt.matrixTransform(svg.getScreenCTM().inverse());let lvl=Math.round(Math.max(DATA.minLevel,Math.min(DATA.maxLevel,DATA.minLevel+(cur.x-m.l)/iw*(DATA.maxLevel-DATA.minLevel))));let rows=heroes.map(hero=>({hero,v:valueAt(hero.id,attr.id,lvl)})).sort((a,b)=>b.v-a.v).slice(0,10);$("tooltip").style.display="block";$("tooltip").style.left=`${ev.clientX+14}px`;$("tooltip").style.top=`${ev.clientY+14}px`;$("tooltip").innerHTML=`<b>${attrLabel(attr)} · ${levelText(lvl)}</b><br>`+rows.map(r=>`<span style="color:${r.hero.color}">■</span> ${heroName(r.hero)}: ${fmt(r.v)}`).join("<br>")};overlay.onmouseleave=()=>$("tooltip").style.display="none";svg.appendChild(overlay)}
function bisect(a,b,fn){let fa=fn(a);for(let i=0;i<42;i++){let mid=(a+b)/2,fm=fn(mid);if(Math.abs(fm)<1e-8)return mid;if(Math.sign(fa)===Math.sign(fm)){a=mid;fa=fm}else b=mid}return(a+b)/2}
function visibleIntersections(attrId){let heroes=DATA.heroes.filter(h=>selected.has(h.id)),rows=[];for(let i=0;i<heroes.length;i++)for(let j=i+1;j<heroes.length;j++){let A=heroes[i],B=heroes[j],fn=l=>valueAt(A.id,attrId,l)-valueAt(B.id,attrId,l),roots=[],same=true,last=fn(1);for(let l=2;l<=36;l++){let d=fn(l);if(Math.abs(d-last)>1e-6)same=false;last=d}if(same&&Math.abs(fn(1))<1e-6)continue;for(let l=1;l<36;l++){let d1=fn(l),d2=fn(l+1);if(Math.abs(d1)<1e-7)roots.push(l);if(d1*d2<0)roots.push(bisect(l,l+1,fn))}if(Math.abs(fn(36))<1e-7)roots.push(36);let seen=new Set();for(let level of roots){level=Math.abs(level-Math.round(level))<1e-6?Math.round(level):level;let key=level.toFixed(5);if(seen.has(key))continue;seen.add(key);if(level===1&&!$("includeLevelOne").checked)continue;rows.push({level,value:valueAt(A.id,attrId,level),hero_a:heroName(A),hero_b:heroName(B),hero_a_id:A.id,hero_b_id:B.id,between:Number.isInteger(level)?String(level):`${Math.floor(level)}-${Math.ceil(level)}`})}}return rows.sort((a,b)=>a.level-b.level||a.hero_a.localeCompare(b.hero_a)||a.hero_b.localeCompare(b.hero_b))}
function renderTable(){let attr=currentAttr(),rows=visibleIntersections(attr.id);$("crossingRows").innerHTML=rows.slice(0,700).map(r=>`<tr data-a="${r.hero_a_id}" data-b="${r.hero_b_id}"><td>${Number(r.level).toFixed(3).replace(/\.000$/,"")}</td><td>${r.between}</td><td>${fmt(r.value)}</td><td>${r.hero_a}</td><td>${r.hero_b}</td></tr>`).join("")||`<tr><td colspan="5">${t("noCrossings")}</td></tr>`;document.querySelectorAll("#crossingRows tr[data-a]").forEach(tr=>{tr.onmouseenter=()=>{hotHeroes=new Set([tr.dataset.a,tr.dataset.b]);renderChart()};tr.onmouseleave=()=>{hotHeroes=new Set();renderChart()}});$("crossingCount").textContent=rows.length;$("hiddenLevelOne").textContent=$("includeLevelOne").checked?0:t("hidden")}
function modifiedHeroes(){return DATA.heroes.filter(h=>Object.values(skillState[h.id]||{}).some(v=>v>0)).length}
function renderHeader(){let attr=currentAttr(),cnt=DATA.heroes.filter(h=>selected.has(h.id)).length,gated=$("respectGating")?.checked?t("respectGateOn"):t("respectGateOff");$("chartTitle").textContent=attrLabel(attr);$("chartSubtitle").textContent=`${attrGroup(attr)}${attr.unit?" · "+attr.unit:""} · ${cnt} ${t("heroCount")} · ${t("skillPassivePanel")} ${modifiedHeroes()?t("skillPassiveOn"):t("skillPassiveOff")} · ${gated} · ${t("noItemSoul")}`;$("selectedCount").textContent=cnt;$("modifiedCount").textContent=modifiedHeroes();renderVersionSummary()}
function renderAll(){renderHeader();renderHeroList();renderAbilityControls();renderItemList();renderBuild();renderSkillInspector();renderChart();renderTable()}
$("allBtn").onclick=()=>{DATA.heroes.forEach(h=>selected.add(h.id));renderAll()};$("noneBtn").onclick=()=>{selected.clear();renderAll()};$("topBtn").onclick=()=>{let attr=currentAttr(),top=DATA.heroes.map(h=>({h,v:valueAt(h.id,attr.id,DATA.maxLevel)})).sort((a,b)=>b.v-a.v).slice(0,8).map(x=>x.h.id);selected.clear();top.forEach(id=>selected.add(id));renderAll()};
$("offSkills").onclick=()=>{let id=$("abilityHero").value;for(const k of Object.keys(skillState[id]))skillState[id][k]=0;renderAll()};$("baseSkills").onclick=()=>{let id=$("abilityHero").value;for(const k of Object.keys(skillState[id]))skillState[id][k]=1;renderAll()};$("fullSkills").onclick=()=>{let id=$("abilityHero").value;for(const k of Object.keys(skillState[id]))skillState[id][k]=4;renderAll()};
$("clearItems").onclick=()=>{selectedItems.clear();renderAll()};$("cheapItems").onclick=()=>{selectedItems.clear();DATA.items.filter(i=>n(i.cost)===800).forEach(i=>selectedItems.add(i.id));renderAll()};$("passiveItems").onclick=()=>{selectedItems.clear();let ids=new Set(DATA.itemEffects.filter(e=>e.includeInBuild).map(e=>e.itemId));DATA.items.filter(i=>ids.has(i.id)).forEach(i=>selectedItems.add(i.id));renderAll()};
$("openSoulTable").onclick=openSoulTable;$("closeSoulTable").onclick=closeSoulTable;$("soulModal").onclick=e=>{if(e.target===$("soulModal"))closeSoulTable()};
$("openVersionLog").onclick=openVersionLog;$("closeVersionLog").onclick=closeVersionLog;$("versionModal").onclick=e=>{if(e.target===$("versionModal"))closeVersionLog()};
$("langToggle").onclick=()=>setLanguage(lang==="zh"?"en":"zh");
window.addEventListener("keydown",e=>{if(e.key==="Escape"){if(!$("soulModal").hidden)closeSoulTable();if(!$("versionModal").hidden)closeVersionLog()}});
for(const id of ["attribute","includeLevelOne","highlightCrossings","respectGating","includeContextual","includeSoulBonuses","includePurchaseBonuses","includeActiveItems","itemSlot","buildLevel"])$(id).onchange=renderAll;$("buildLevel").oninput=renderAll;$("heroSearch").oninput=renderHeroList;$("itemSearch").oninput=renderItemList;$("abilityHero").onchange=renderAll;window.onresize=renderChart;
applyStaticText();initAttributes();initAbilityHero();renderAll();
</script>
</body>
</html>
"""


def main():
    payload = build_payload()
    export_tables(payload)
    data_payload = {k: v for k, v in payload.items() if k != "fullAbilities"}
    DATA_OUT.write_text(json.dumps(data_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_html(payload)
    print(f"heroes: {len(payload['heroes'])}")
    print(f"abilities: {len(payload['abilities'])}")
    print(f"mapped ability effects: {len(payload['effects'])}")
    print(f"shop items: {len(payload['items'])}")
    print(f"mapped item effects: {len(payload['itemEffects'])}")
    print(f"wrote: {HTML_OUT.name}")
    print(f"wrote: {DATA_OUT.name}")
    print(f"wrote: {ABILITIES_CSV.name}")
    print(f"wrote: {ABILITIES_JSON.name}")
    print(f"wrote: {ABILITY_EFFECTS_CSV.name}")
    print(f"wrote: {ITEM_EFFECTS_CSV.name}")


if __name__ == "__main__":
    main()
