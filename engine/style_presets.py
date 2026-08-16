# style_presets.py
# -*- coding: utf-8 -*-
"""
风格预设库 — 为创意输入页提供可一键选用的"风格"指令包。

每个风格 = 一个会拼入 user_guidance 的指令块，覆盖：基调（触发 enhanced_prompts 的
【基调控制】）、节奏、文风、冲突类型、情感浓度。用户可在内置预设之外自定义风格，
自定义风格保存在 config/custom_styles.json（同名会覆盖内置）。
"""
import json
import os

# 自定义风格存储文件（相对项目根 config/）
CUSTOM_STYLES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "custom_styles.json"
)

BUILTIN_STYLES = [
    {
        "name": "轻松搞笑",
        "desc": "沙雕吐槽、段子频出、社死名场面，读起来轻松开心",
        "block": (
            "【风格设定·轻松搞笑】\n"
            "基调：轻松搞笑——幽默、愉快、欢乐，全文不涉及阴谋、黑暗、死亡、背叛等设定。\n"
            "节奏：明快，每3章一个爽点/笑点，段子和社死名场面密集。\n"
            "文风：口语化、接地气、带梗（行吧/嘶/靠/得了吧），吐槽和自嘲是主要笑点来源。\n"
            "冲突：生活化小麻烦、误会、花式打脸、搞笑困境，禁止生死危机。\n"
            "情感：温馨向，甜度中高，不虐。"
        ),
    },
    {
        "name": "温馨治愈",
        "desc": "温暖细腻、治愈向，人情味足，不虐不黑暗",
        "block": (
            "【风格设定·温馨治愈】\n"
            "基调：温暖、治愈、治愈系——整体舒缓明亮，不涉及阴谋、黑暗、死亡、背叛等设定。\n"
            "节奏：舒缓，重在人物互动与细水长流的温情，间以小波折。\n"
            "文风：细腻、温柔、有烟火气，少用夸张修辞。\n"
            "冲突：误会、小挫折、和解，冲突最终都以温暖方式收场。\n"
            "情感：治愈向，重视情谊与陪伴，不虐。"
        ),
    },
    {
        "name": "热血燃向",
        "desc": "打脸升级、逆境翻盘、情绪高涨，燃点密集",
        "block": (
            "【风格设定·热血燃向】\n"
            "基调：热血、燃、振奋——高潮处情绪拉满，冲突与对抗是主要驱动。\n"
            "节奏：快，爽点密集，前3章完成首次逆袭，每5章一个小高潮。\n"
            "文风：有力量感、短句加速，口号与宣言在关键处点题。\n"
            "冲突：对手打压、实力悬殊逆袭、当众打脸、荣誉之争。\n"
            "情感：燃与爽为主，可轻虐后反超大甜。"
        ),
    },
    {
        "name": "悬疑紧张",
        "desc": "谜团、线索、反转，钩子拉满，每章结尾吊胃口",
        "block": (
            "【风格设定·悬疑紧张】\n"
            "基调：悬疑、紧张、压迫感——以谜团与真相为核心驱动。\n"
            "节奏：紧凑，每章埋新线索、章末必有钩子，每5章一个大反转。\n"
            "文风：氛围感强，细节暗示，对话藏信息。\n"
            "冲突：未知威胁、误导性线索、证据与追查、身份谜团。\n"
            "情感：好奇与震惊为主，紧张-释放交替。"
        ),
    },
    {
        "name": "细腻情感",
        "desc": "心理描写细、感情戏重，甜虐比例可控",
        "block": (
            "【风格设定·细腻情感】\n"
            "基调：情感浓度高，以人物关系与内心戏为主线。\n"
            "节奏：中速，感情进展有铺垫有高潮，不突进。\n"
            "文风：细腻、敏感、多用动作与潜台词表达情绪，少直白告白。\n"
            "冲突：误会、错过、身份差距、关系进退的拉扯。\n"
            "情感：甜虐比例按剧情需要（默认甜宠为主），虐点必有情绪落点。"
        ),
    },
    {
        "name": "冷峻简洁",
        "desc": "语言精炼、克制、短句，不煽情不啰嗦",
        "block": (
            "【风格设定·冷峻简洁】\n"
            "基调：克制、冷静，情绪内敛，靠动作与事实传达。\n"
            "节奏：利落，叙事直奔重点，删减一切废话。\n"
            "文风：短句为主，描写精简，少修饰词，不煽情不总结。\n"
            "冲突：干脆利落，行动先于言语。\n"
            "情感：含蓄留白，情绪靠读者自行体会。"
        ),
    },
    {
        "name": "文艺氛围",
        "desc": "描写丰富、氛围感强、比喻克制而有意境",
        "block": (
            "【风格设定·文艺氛围】\n"
            "基调：文艺、氛围向，重意境与画面感。\n"
            "节奏：舒缓有呼吸感，情节与氛围并重。\n"
            "文风：描写细腻、用少量生活化比喻营造氛围，禁止辞藻堆砌与比喻成串。\n"
            "冲突：情绪张力与情节推进并重，矛盾带有层次。\n"
            "情感：细腻、余韵足，结局有余味。"
        ),
    },
    {
        "name": "快节奏爽文",
        "desc": "番茄平台默认风格：短段落、对话多、爽点密集、每章钩子",
        "block": (
            "【风格设定·快节奏爽文】\n"
            "基调：爽、快、信息量大，符合番茄平台阅读习惯。\n"
            "节奏：极快，1-3句一段，对话占比50-60%，每章末尾必有钩子。\n"
            "文风：口语化、直接、接地气，杜绝书面腔和慢热铺垫。\n"
            "冲突：章节内快速推进，打脸/升级/反转不拖泥带水。\n"
            "情感：情绪给足、兑现干脆，不吊太久胃口。"
        ),
    },
]


def _read_custom_styles() -> list:
    try:
        if os.path.exists(CUSTOM_STYLES_FILE):
            with open(CUSTOM_STYLES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return [s for s in data if isinstance(s, dict) and s.get("name")]
    except Exception:
        pass
    return []


def _write_custom_styles(styles: list):
    os.makedirs(os.path.dirname(CUSTOM_STYLES_FILE), exist_ok=True)
    with open(CUSTOM_STYLES_FILE, "w", encoding="utf-8") as f:
        json.dump(styles, f, ensure_ascii=False, indent=2)


def get_all_styles() -> list:
    """返回内置 + 自定义的全部风格（自定义同名覆盖内置）。"""
    by_name = {s["name"]: dict(s) for s in BUILTIN_STYLES}
    for s in _read_custom_styles():
        by_name[s["name"]] = s
    return list(by_name.values())


def get_style_block(name: str) -> str:
    for s in get_all_styles():
        if s["name"] == name:
            return (s.get("block") or "").strip()
    return ""


def compose_guidance(user_guidance: str, style_name: str) -> str:
    """把风格指令块拼进创意指导；风格为空或已存在则不重复追加。"""
    block = get_style_block(style_name)
    if not block:
        return (user_guidance or "").strip()
    base = (user_guidance or "").strip()
    if block in base:
        return base
    return f"{base}\n\n{block}" if base else block


def add_custom_style(preset: dict):
    styles = [s for s in _read_custom_styles() if s.get("name") != preset.get("name")]
    styles.append(preset)
    _write_custom_styles(styles)


def delete_custom_style(name: str):
    styles = [s for s in _read_custom_styles() if s.get("name") != name]
    _write_custom_styles(styles)
