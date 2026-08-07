# deslop_engine.py
# -*- coding: utf-8 -*-
"""
去 AI 味引擎 v2 — 保守策略，只改确定有毒的部分，不破坏正常叙事。

核心原则：改最少，效果最大。宁可漏改，不可误改。
"""
import re
from typing import List, Tuple, Dict


# =============== Gate A: 禁词逐个替换 ===============
# 每个词条都是精确匹配，不会误伤
BANNED_REPLACEMENTS = [
    # 情态类
    ("仿佛", "像"), ("犹如", "像"), ("宛若", "像"),
    ("一丝", "一点"), ("一抹", "一点"),
    ("毫无征兆", "突然"), ("几不可闻", "几乎听不见"),
    ("微不可察", "几乎看不出来"),
    # 动作类
    ("深深地吸了一口气", ""), ("深吸一口气", ""),
    # 表情类
    ("眼中闪过", "垂下眼"), ("嘴角勾起", "嘴角一扯"),
    ("眉头微皱", "皱了皱眉"), ("瞳孔微缩", "眯起眼"),
    ("瞳孔收缩", "眯起眼"), ("瞳孔一缩", "眯起眼"),
    ("指节泛白", "攥紧了手"),
    # 心理类
    ("心中一动", ""), ("心头一震", ""), ("心下了然", ""),
    ("心中暗道", ""), ("心底泛起", ""), ("心中一凛", ""),
    # 判断类
    ("不容置疑", "肯定"), ("不容置喙", ""),
    ("不易察觉", "悄悄"), ("显而易见", "明摆着"),
    ("毫无疑问", ""), ("不可否认", ""),
    # 形容类
    ("闪烁着光芒", "亮晶晶"), ("狡黠", "鬼精"),
    # 过渡类
    ("不由自主", ""), ("情不自禁", ""), ("话锋一转", ""),
]


def _gate_a(text: str) -> Tuple[str, List[dict]]:
    """逐个替换禁词（按长度降序，避免短词先匹配）"""
    changes = []
    # 按长度降序排列
    sorted_rules = sorted(BANNED_REPLACEMENTS, key=lambda x: len(x[0]), reverse=True)
    for word, replacement in sorted_rules:
        if word in text:
            count = text.count(word)
            text = text.replace(word, replacement)
            changes.append({"gate": "A", "word": word, "to": replacement or "(删)", "count": count})
    return text, changes


# =============== Gate B: 整句有毒模式 ===============
# 只删完整句子（句号结尾），不破坏句子内部结构
TOXIC_SENTENCES = [
    # 音线描写
    (r"，语气毫无波澜", ""),
    (r"，声音平直", ""),
    (r"，平静无波地", ""),
    # 命运/升华
    (r"命运终于露出獠牙。?", ""),
    (r"属于[^的。]{1,20}的(?:反击|复仇|故事)，?才刚刚开始。?", ""),
    (r"反击才刚刚开始。?", ""),
    # 总结句式
    (r"[他她]终于明白[^。]+。", ""),
    (r"[他她]这才意识到[^。]+。", ""),
    (r"这一刻，?[他她]终于(?:明白|意识到)[^。]+。", ""),
    (r"从这一刻开始[^。]+。", ""),
    # 章末预告
    (r"[他她]不知道的是[^。]+。", ""),
]


def _gate_b(text: str) -> Tuple[str, List[dict]]:
    """删除整句有毒模式"""
    changes = []
    for pattern, replacement in TOXIC_SENTENCES:
        matches = list(re.finditer(pattern, text))
        if matches:
            for m in reversed(matches):
                text = text[:m.start()] + replacement + text[m.end():]
            changes.append({"gate": "B", "pattern": pattern, "count": len(matches)})
    return text, changes


# =============== Gate C: 对话标签简化 ===============

DIALOGUE_TAGS = [
    ("说道", "说"),
    ("问道", "问"),
    ("笑道", "笑"),
]


def _gate_c(text: str) -> Tuple[str, List[dict]]:
    """简化对话标签"""
    changes = []
    for old, new in DIALOGUE_TAGS:
        if old in text:
            count = text.count(old)
            text = text.replace(old, new)
            changes.append({"gate": "C", "from": old, "to": new, "count": count})
    return text, changes


# =============== Gate D: 节奏调整 ===============

def _gate_d(text: str) -> Tuple[str, List[dict]]:
    """打破均匀节奏：拆分过长段落（6句以上）"""
    changes = []
    paragraphs = text.split('\n')
    new_paragraphs = []

    for para in paragraphs:
        if not para.strip():
            new_paragraphs.append(para)
            continue

        sentences = [s.strip() for s in re.split(r'[。！？]', para) if s.strip()]

        if len(sentences) >= 6:
            mid = len(sentences) // 2
            part1 = '。'.join(sentences[:mid]) + '。'
            part2 = '。'.join(sentences[mid:])
            if not part2.endswith(('。', '！', '？')):
                part2 += '。'
            new_paragraphs.append(part1)
            new_paragraphs.append(part2)
            changes.append({"gate": "D", "type": "拆分长段", "sentences": len(sentences)})
        else:
            new_paragraphs.append(para)

    return '\n'.join(new_paragraphs), changes


# =============== Gate E: 对话去模板化 ===============

DIALOGUE_MODIFIERS = [
    (r"[，,]?冷冷地(?:说|道)", ""),
    (r"[，,]?淡淡地(?:说|道)", ""),
    (r"[，,]?平静地(?:说|道)", ""),
    (r"[，,]?轻声(?:说|道)", ""),
    (r"[，,]?沉声(?:说|道)", ""),
    (r"[，,]?低声(?:说|道)", ""),
    (r"[，,]?厉声(?:说|道)", ""),
]


def _gate_e(text: str) -> Tuple[str, List[dict]]:
    """对话去模板化：删除过度修饰的对话标签"""
    changes = []
    for pattern, replacement in DIALOGUE_MODIFIERS:
        if re.search(pattern, text):
            count = len(re.findall(pattern, text))
            text = re.sub(pattern, replacement, text)
            changes.append({"gate": "E", "type": "对话修饰", "count": count})
    return text, changes


# =============== Gate F: 结尾去升华 ===============

ENDING_PATTERNS = [
    (r"属于[^的。]{1,20}的(?:反击|复仇|故事|人生|传奇)，?才刚刚开始。?", ""),
    (r"反击才刚刚开始。?", ""),
    (r"命运终于露出獠牙。?", ""),
    (r"命运[^。]*(?:棋局|獠牙|齿轮|安排)[^。]*。", ""),
    (r"[他她]终于明白[^。]+。", ""),
    (r"[他她]这才意识到[^。]+。", ""),
    (r"这一刻，?[他她]终于(?:明白|意识到)[^。]+。", ""),
    (r"从这一刻开始[^。]+。", ""),
]


def _gate_f(text: str) -> Tuple[str, List[dict]]:
    """结尾去升华：删除总结性/升华性结尾句"""
    changes = []
    for pattern, replacement in ENDING_PATTERNS:
        if re.search(pattern, text):
            count = len(re.findall(pattern, text))
            text = re.sub(pattern, replacement, text)
            changes.append({"gate": "F", "type": "结尾升华", "count": count})
    return text, changes


# =============== Gate G: 去解释性旁白/上帝视角 ===============

EXPLANATION_PATTERNS = [
    (r"[她他]不知道的是[^。]+。", ""),
    (r"之所以[^，]*是因为[^。]+。", ""),
    (r"演得真好", ""),
    (r"装得真像", ""),
    (r"这(?:才|就)是[^。]*真正[^。]*。", ""),
    (r"事实上，?[^。]+。", ""),
]


def _gate_g(text: str) -> Tuple[str, List[dict]]:
    """去解释性旁白：删除叙述者跳出角色的解释"""
    changes = []
    for pattern, replacement in EXPLANATION_PATTERNS:
        if re.search(pattern, text):
            count = len(re.findall(pattern, text))
            text = re.sub(pattern, replacement, text)
            changes.append({"gate": "G", "type": "解释旁白", "count": count})
    return text, changes


# =============== 标点清理 ===============

PUNCTUATION = [
    ("——", "，"),
    ("--", "，"),
]


def _fix_punctuation(text: str) -> Tuple[str, List[dict]]:
    changes = []
    for old, new in PUNCTUATION:
        if old in text:
            count = text.count(old)
            text = text.replace(old, new)
            changes.append({"gate": "标点", "from": old, "to": new, "count": count})
    return text, changes


# =============== 后处理 ===============

def _cleanup(text: str) -> str:
    """清理替换产生的痕迹"""
    # 连续标点
    text = re.sub(r'。。+', '。', text)
    text = re.sub(r'，，+', '，', text)
    text = re.sub(r'，。', '。', text)
    text = re.sub(r'。，', '。', text)
    # 开头多余逗号（句首不应有逗号）
    text = re.sub(r'^[，,]+', '', text, flags=re.MULTILINE)
    # 删除后留下孤立主语+逗号 → 删掉逗号
    text = re.sub(r'([他她它我你])，\s*([。“”‘’\n])', r'\1\2', text)
    # 句首 "他，垂下" → "他垂下" (删除动作后残留的逗号)
    text = re.sub(r'([他她它我你])，(\s*[^“”])', r'\1\2', text)
    # 连续空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# =============== 主函数 ===============

def deslop_text(text: str, gates: Dict[str, bool] = None) -> Dict:
    """
    对文本执行去 AI 味处理（7 Gate）。
    策略：保守、精确，只改确定有毒的部分。
    """
    if gates is None:
        gates = {f"gate_{chr(97+i)}": True for i in range(7)}

    all_changes = []

    # 标点清理（始终执行）
    text, ch = _fix_punctuation(text)
    all_changes.extend(ch)

    # Gate A: 禁词替换
    if gates.get("gate_a", True):
        text, ch = _gate_a(text)
        all_changes.extend(ch)

    # Gate B: 有毒句式
    if gates.get("gate_b", True):
        text, ch = _gate_b(text)
        all_changes.extend(ch)

    # Gate C: 对话标签简化
    if gates.get("gate_c", True):
        text, ch = _gate_c(text)
        all_changes.extend(ch)

    # Gate D: 节奏调整
    if gates.get("gate_d", True):
        text, ch = _gate_d(text)
        all_changes.extend(ch)

    # Gate E: 对话去模板化
    if gates.get("gate_e", True):
        text, ch = _gate_e(text)
        all_changes.extend(ch)

    # Gate F: 结尾去升华
    if gates.get("gate_f", True):
        text, ch = _gate_f(text)
        all_changes.extend(ch)

    # Gate G: 去解释性旁白
    if gates.get("gate_g", True):
        text, ch = _gate_g(text)
        all_changes.extend(ch)

    # 后处理
    text = _cleanup(text)

    severity = _evaluate_severity(all_changes)

    return {
        "text": text,
        "changes": all_changes,
        "severity": severity,
        "summary": _summarize(all_changes),
    }


def _evaluate_severity(changes: list) -> str:
    gate_a = sum(c.get("count", 0) for c in changes if c.get("gate") == "A")
    gate_b = sum(c.get("count", 0) for c in changes if c.get("gate") == "B")
    # 统计涉及的 Gate 数量
    gates_hit = len(set(c.get("gate", "") for c in changes if c.get("gate")))
    total = sum(c.get("count", 0) for c in changes)
    if gate_a > 15 or gate_b >= 3 or gates_hit >= 5:
        return "重度"
    elif gate_a > 6 or gate_b >= 1 or gates_hit >= 3:
        return "中度"
    return "轻度"


def _summarize(changes: list) -> dict:
    s = {"total_changes": len(changes), "by_gate": {}}
    for c in changes:
        g = c.get("gate", "?")
        s["by_gate"][g] = s["by_gate"].get(g, 0) + 1
    return s


def deslop_chapter(chapter_text: str, config: dict = None) -> str:
    """章节级去 AI 味接口（默认启用全部7个Gate）"""
    if config is None:
        config = {f"gate_{chr(97+i)}": True for i in range(7)}
    result = deslop_text(chapter_text, config)
    print(f"\n{'='*50}")
    print(f"去AI味 | 等级:{result['severity']} | 变更:{result['summary']['total_changes']}处")
    for g, c in result['summary']['by_gate'].items():
        print(f"  {g}: {c}处")
    print(f"{'='*50}\n")
    return result["text"]
