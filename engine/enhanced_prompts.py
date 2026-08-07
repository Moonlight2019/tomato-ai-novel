# enhanced_prompts.py
# -*- coding: utf-8 -*-
"""
增强版 Prompt 模板 — 融合 oh-story-claudecode 的网文方法论到 AI_NovelGenerator 的 prompt 体系。

核心改动：
1. core_seed_prompt + 都市类题材公式
2. character_dynamics_prompt + 人物设计方法论
3. chapter_blueprint_prompt + 章末钩子要求
4. first_chapter_draft_prompt + 开篇设计 + 情绪弧线
5. next_chapter_draft_prompt + 对话技巧 + 节奏控制 + 情绪弧线
"""

# =============== 题材公式库 ===============
GENRE_FORMULAS = {
    "都市": """
【都市类题材核心公式】
- 核心驱动：身份落差 × 信息差 × 资源博弈
- 情绪主线：压抑→反击→爽→更大的压抑→更大的反击→终极爽
- 必选场景：中年危机/底层困境、系统/金手指激活、隐藏实力逐步展露
- 节奏规则：前3章必须完成"惨→翻盘"的第一次循环；每5章一个小高潮
""",

    "校园": """
【校园类题材核心公式】
- 核心驱动：青春成长 × 身份反差 × 羁绊与误解
- 情绪主线：平凡→被欺负/被忽视→展露锋芒→赢得尊重/友情/爱情
- 必选场景：开学第一天、课堂上的意外、校园霸凌反击、考试/竞赛逆袭、操场/天台的对话
- 角色类型：转校生/隐藏身份、校园风云人物、默默守护的朋友、反派校霸/绿茶
- 节奏规则：每3章一个小事件，每5章一个大事件（运动会/校庆/考试）
- 对话风格：口语化、带梗、有青春期特有的别扭和真诚
""",

    "校园言情": """
【校园言情题材核心公式】
- 核心驱动：青春悸动 × 误会与和解 × 成长蜕变
- 情绪主线：相遇→误解→心动→分离→重逢→HE
- 必选场景：初遇名场面、同桌/邻座、图书馆/操场偶遇、雨中/天台告白、毕业分离
- 甜虐比例：前70%甜中带虐，后30%虐后更甜
- 对话特点：嘴硬心软、欲言又止、用行动代替告白
""",

    "玄幻": """
【玄幻类题材核心公式】
- 核心驱动：废材逆袭 × 境界突破 × 大陆争霸
- 情绪主线：被嘲笑→获得机缘→打脸→更大危机→更强突破
- 必选场景：废材被退婚/被逐出家族、觉醒/获得传承、越级战斗、拍卖会/宗门大比
- 境界体系：必须有清晰的等级划分（练气→筑基→金丹→...）
- 节奏规则：每3章突破一个小境界，每10章突破一个大境界
""",

    "仙侠": """
【仙侠类题材核心公式】
- 核心驱动：修仙问道 × 因果宿命 × 情劫
- 情绪主线：入世→历劫→悟道→飞升
- 必选场景：拜师入门、秘境探险、渡劫、心魔试炼、宗门大战
- 与玄幻区别：更重意境和哲理，不只打怪升级
""",

    "悬疑": """
【悬疑类题材核心公式】
- 核心驱动：谜题 × 线索 × 反转
- 情绪主线：好奇→困惑→恐惧→震惊→真相大白
- 必选场景：离奇死亡/失踪、误导性线索、关键证人、最终反转
- 节奏规则：每章末尾必须有新线索或新疑问；每5章一个大反转
- 写作要求：伏笔必须在前文有铺垫，不能凭空出现
""",

    "言情": """
【言情类题材核心公式】
- 核心驱动：情感纠葛 × 身份障碍 × 命运安排
- 情绪主线：相遇→心动→阻碍→分离→重逢→HE/BE
- 必选场景：初遇名场面、误会/错过、虐心分离、深情告白、大团圆
- 甜虐比例：根据子类型调整（甜宠8甜2虐，虐恋3甜7虐）
- 对话特点：含蓄与直白交替，关键时刻要有金句
""",

    "言情甜宠": """
【甜宠文题材核心公式】
- 核心驱动：双向奔赴 × 甜蜜互动 × 打脸情敌
- 情绪主线：甜→更甜→最甜→偶尔小虐→超甜
- 必选场景：壁咚/摸头杀、吃醋、官宣、撒狗粮、打脸白莲花
- 男主人设：外冷内热/霸道总裁/忠犬/病娇（选一种）
- 女主人设：不傻白甜，要有自己的事业和主见
- 节奏规则：每章至少一个甜蜜互动，每3章一个大糖
""",

    "言情虐恋": """
【虐恋文题材核心公式】
- 核心驱动：深爱却不能爱 × 误会 × 牺牲
- 情绪主线：甜→虐→更虐→最虐→和解/BE
- 必选场景：被迫分离、误会加深、雨中/雪中名场面、真相大白、最终抉择
- 虐点设计：身份误会、家族仇恨、生死抉择、第三者阴谋
- 节奏规则：虐前必先铺甜，让读者先爱上这对CP
""",

    "古言": """
【古言题材核心公式】
- 核心驱动：宅斗/宫斗 × 身份反转 × 情感博弈
- 情绪主线：隐忍→反击→碾压→最终翻身
- 必选场景：被欺负/被陷害、身份揭露、宫宴/家宴、圣旨/婚书
- 对话风格：半文半白，有古韵但不晦涩
- 角色类型：重生女主、腹黑王爷、白莲花姐妹、偏心长辈
""",

    "科幻": """
【科幻类题材核心公式】
- 核心驱动：科技变革 × 人性冲突 × 生存危机
- 情绪主线：发现→探索→危机→抉择→新秩序
- 必选场景：技术突破、伦理困境、末日危机、人类命运抉择
- 硬度控制：硬科幻重设定，软科幻重情感
""",

    "末世": """
【末世类题材核心公式】
- 核心驱动：生存 × 重建秩序 × 人性考验
- 情绪主线：灾难降临→挣扎求生→建立据点→对抗威胁→新文明
- 必选场景：末日第一天、丧尸/怪物遭遇、资源争夺、基地建设、背叛与信任
- 金手指类型：系统/异能/重生记忆/空间
""",

    "历史": """
【历史类题材核心公式】
- 核心驱动：权谋 × 家国 × 命运
- 情绪主线：入局→博弈→危机→翻盘→功成名就/悲剧收场
- 必选场景：朝堂论战、沙场点兵、阴谋揭露、帝王心术
- 对话风格：符合历史背景，有古韵
""",

    "架空历史": """
【架空历史题材核心公式】
- 核心驱动：穿越/重生 × 改变历史 × 权谋争霸
- 情绪主线：利用先知优势→逐步崛起→改变历史走向
- 必选场景：穿越初醒、初次展露才华、朝堂博弈、战争谋略
- 与纯历史区别：可以自由发挥，不必完全符合史实
""",

    "职场": """
【职场类题材核心公式】
- 核心驱动：职场逆袭 × 能力证明 × 人际博弈
- 情绪主线：被轻视→展现能力→升职加薪→巅峰对决
- 必选场景：入职第一天、被同事陷害、关键项目、升职竞争、行业峰会
- 节奏规则：每3章解决一个职场难题，每5章一次升职/突破
""",

    "系统流": """
【系统流题材核心公式】
- 核心驱动：系统任务 × 奖励机制 × 等级提升
- 情绪主线：获得系统→完成任务→升级→更强任务→终极挑战
- 必选场景：系统激活、新手礼包、任务发布、升级突破、系统升级
- 系统设计：要有独特的系统设定（签到/抽奖/模拟器/直播等）
""",

    "无限流": """
【无限流题材核心公式】
- 核心驱动：副本挑战 × 团队协作 × 真相揭露
- 情绪主线：进入副本→探索规则→生死考验→通关→下一个副本
- 必选场景：副本进入、规则解读、团队冲突、Boss战、隐藏真相
- 副本设计：每个副本要有独立的世界观和通关条件
""",

    "穿越": """
【穿越类题材核心公式】
- 核心驱动：现代知识 × 异世生存 × 命运改写
- 情绪主线：穿越初醒→适应环境→利用优势→称霸/回家
- 必选场景：穿越初醒、文化冲突、展露才华、原主恩怨
- 金手指：现代知识/系统/重生记忆/空间
""",
}

# 默认公式（未匹配到具体题材时使用）
DEFAULT_GENRE_FORMULA = """
【通用写作公式】
- 核心驱动：主角有明确目标，遭遇阻碍，克服困难
- 情绪主线：起→承→转→合，有起伏
- 节奏规则：每3-5章一个小高潮，每10章一个大转折
- 番茄适配：短段落（1-3句为主）、对话占比50-60%、每章末尾必须有钩子
"""

# =============== 章末钩子13式速查（来自 oh-story hooks-chapter.md）==============
CHAPTER_HOOKS_13 = """
【章末钩子13式 — 每章必须选用至少1种】
1. 突然揭示：抛出改变全局的信息（"信上的日期，是他死后第七天。"）
2. 紧急危机：下章必须回应的紧迫威胁（"裂缝在扩大，灵石还差三块。"）
3. 未完成动作：动作被新变量打断（"他刚伸手，手腕忽然被人扣住。"）
4. 身份反转：身份真相偏离读者预期（"她叫林小月。但档案上写的是：林小月，已故。"）
5. 两难抉择：被迫在两个坏选项中选一个（"签了这份文件，公司保住了，但他得进去。"）
6. 神秘物品：重要但含义未知的物件（"包裹里是一把钥匙，附了张纸条：'你欠我的。'"）
7. 倒计时：时间不够用（"医生说还有三个月。那是两个月前的事了。"）
8. 承诺/威胁：有人宣布了行动意图（"今晚十二点之前，我会告诉所有人你做了什么。"）
9. 离奇消失：不可能的消失（"手铐还在，人没了。"）
10. 隐藏含义：表面正常，实际暗藏信息（"他说：'你和妹妹真像。'可她是独生女。"）
11. 意象钩子：反复出现的意象发生变化（"窗台上那盆枯了一个月的茉莉，突然冒出了花苞。"）
12. 回声钩子：章尾句呼应开头，关键细节变了
13. 留白钩子：只展示反应，不揭示发生了什么（"他看了信。脸色变了。什么也没说。"）
"""

# =============== 情绪弧线速查（来自 oh-story emotional-arc-design.md）==============
EMOTIONAL_ARCS = """
【情绪弧线设计 — 长篇选择】
- V形弧线（虐→治愈）：谷底60-70%，治愈急速回升，结尾情绪高于起点
- W形弧线（多起伏）：至少两个波峰一个波谷，每峰比前高，上限3个起伏
- 递进弧线（逐步升级）：无回落，像台阶往上，适合打脸升级流
- 延迟满足弧线：前70-80%铺垫，最后集中爆发，适合隐忍后大爆发

都市长篇推荐：W形弧线（多反转）或递进弧线（打脸升级）
"""

# =============== 对话技巧速查（来自 oh-story dialogue-mastery.md）==============
DIALOGUE_MASTERY = """
【对话写作技巧】
- 60%以上的对话不需要"说道/问道"标签，用动作替代
- 对话要有潜台词：表面谈A，实际博弈B
- 用非对称对话长度体现权力关系（强势者话短，弱势者话多或解释）
- 加入口语化语气词："行吧""嘶""靠""得了吧"
- 对话间插入小动作、环境描写，不要连续对白超过4句
- 避免每句话都带副词修饰（"冷冷地说""淡淡地回应"）
"""

# =============== 开篇设计（来自 oh-story opening-design.md）==============
OPENING_DESIGN = """
【开篇设计 — 第一章必须做到】
- 前200字内必须出现冲突或异常
- 用"未完成动作开局"或"倒计时开局"制造即时紧迫感
- 主角的困境要在前500字内让读者感知
- 系统/金手指在第一章末尾或第二章开头激活
- 第一章结尾必须是强钩子（突然揭示/紧急危机/身份反转）
"""

# =============== 增强版核心种子 Prompt ===============
enhanced_core_seed_prompt = """\
作为专业网文作家，请用"雪花写作法"第一步构建故事核心：
主题：{topic}
类型：{genre}
篇幅：约{number_of_chapters}章（每章{word_number}字）

{genre_formula}

请用单句公式概括故事本质，例如：
"当[主角]遭遇[核心事件]，必须[关键行动]，否则[灾难后果]；与此同时，[隐藏的更大危机]正在发酵。"

要求：
1. 必须包含显性冲突与潜在危机
2. 体现人物核心驱动力（都市类核心驱动：身份落差×信息差×资源博弈）
3. 暗示世界观关键矛盾
4. 使用25-100字精准表达
5. 前3章必须完成"惨→翻盘"的第一次循环

仅返回故事核心文本，不要解释任何内容。
"""

# =============== 增强版角色动力学 Prompt ===============
enhanced_character_dynamics_prompt = """\
基于以下元素：
- 内容指导：{user_guidance}
- 核心种子：{core_seed}

{dialogue_mastery}

请设计3-6个具有动态变化潜力的核心角色，每个角色需包含：

特征：
- 背景、外貌、性别、年龄、职业等
- 暗藏的秘密或潜在弱点(可与世界观或其他角色有关)
- 说话风格特征（口头禅、语气特点、用词习惯）

核心驱动力三角：
- 表面追求（物质目标）
- 深层渴望（情感需求）
- 灵魂需求（哲学层面）

角色弧线设计：
初始状态 → 触发事件 → 认知失调 → 蜕变节点 → 最终状态

关系冲突网：
- 与其他角色的关系或对立点
- 与至少两个其他角色的价值观冲突
- 一个合作纽带
- 一个隐藏的背叛可能性

都市类角色要求：
- 主角必须有明确的"惨点"（失业/离婚/被欺压/底层困境）
- 至少一个"打脸对象"（前领导/前妻/看不起主角的人）
- 至少一个"贵人/金手指提供者"

要求：
仅给出最终文本，不要解释任何内容。
"""

# =============== 增强版世界构建 Prompt ===============
enhanced_world_building_prompt = """\
基于以下元素：
- 内容指导：{user_guidance}
- 核心冲突："{core_seed}"

为服务上述内容，请构建三维交织的世界观：

1. 物理维度：
- 空间结构（都市场景：写字楼/城中村/高端会所/医院等）
- 时间轴（关键事件时间线）
- 规则体系（职场规则/商业规则/社会阶层规则）

2. 社会维度：
- 权力结构断层线（阶层/行业/资本/人脉的矛盾）
- 文化禁忌（可被打破的潜规则及其后果）
- 经济命脉（资源争夺焦点：项目/股权/流量/客户）

3. 隐喻维度：
- 贯穿全书的视觉符号系统
- 环境变化映射的心理状态
- 空间暗示的阶层困境

要求：
每个维度至少包含3个可与角色决策产生互动的动态元素。
仅给出最终文本，不要解释任何内容。
"""

# =============== 增强版情节架构 Prompt ===============
enhanced_plot_architecture_prompt = """\
基于以下元素：
- 内容指导：{user_guidance}
- 核心种子：{core_seed}
- 角色体系：{character_dynamics}
- 世界观：{world_building}

{emotional_arcs}

要求按以下结构设计：

第一幕（触发）— 前{act1_pct}章
- 日常状态中的异常征兆（3处铺垫）
- 引出故事：展示主线、暗线、副线的开端
- 关键事件：打破平衡的催化剂（需改变至少3个角色的关系）
- 错误抉择：主角的认知局限导致的错误反应
- 【都市类】前3章必须完成"惨→翻盘"第一次循环

第二幕（对抗）— 中间{act2_pct}章
- 剧情升级：主线+副线的交叉点
- 双重压力：外部障碍升级+内部挫折
- 虚假胜利：看似解决实则深化危机的转折点
- 灵魂黑夜：世界观认知颠覆时刻
- 【都市类】每5章一个小高潮，每10章一个大反转

第三幕（解决）— 最后{act3_pct}章
- 代价显现：解决危机必须牺牲的核心价值
- 嵌套转折：至少包含三层认知颠覆
- 余波：留下2个开放式悬念因子

每个阶段需包含3个关键转折点及其对应的伏笔回收方案。
仅给出最终文本，不要解释任何内容。
"""

# =============== 增强版章节目录 Prompt ===============
enhanced_chapter_blueprint_prompt = """\
基于以下元素：
- 内容指导：{user_guidance}
- 小说架构：
{novel_architecture}

{chapter_hooks}

设计{number_of_chapters}章的节奏分布：

1. 章节集群划分：
- 每3-5章构成一个悬念单元，包含完整的小高潮
- 单元之间设置"认知过山车"（连续2章紧张→1章缓冲）
- 关键转折章需预留多视角铺垫
- 【都市类】前3章完成第一次"爽点循环"，之后每5章一个小高潮

2. 每章需明确：
- 章节定位（角色/事件/主题等）
- 核心悬念类型（信息差/道德困境/时间压力等）
- 情感基调迁移（如从怀疑→恐惧→决绝）
- 伏笔操作（埋设/强化/回收）
- 认知颠覆强度（1-5级）
- 【必选】章末钩子类型（从13式中选择，标注具体钩子）

输出格式示例：
第n章 - [标题]
本章定位：[角色/事件/主题/...]
核心作用：[推进/转折/揭示/...]
悬念密度：[紧凑/渐进/爆发/...]
伏笔操作：埋设(A线索)→强化(B矛盾)...
认知颠覆：★☆☆☆☆
章末钩子：[钩子类型] - [具体钩子内容]
本章简述：[一句话概括]

要求：
- 使用精炼语言描述，每章字数控制在100字以内。
- 合理安排节奏，确保整体悬念曲线的连贯性。
- 在生成{number_of_chapters}章前不要出现结局章节。
- 每章必须标注章末钩子类型。

仅给出最终文本，不要解释任何内容。
"""

# =============== 增强版第一章草稿 Prompt ===============
# 注意：只使用原始代码传递的占位符，不添加额外占位符
enhanced_first_chapter_draft_prompt = """\
即将创作：第 {novel_number} 章《{chapter_title}》
本章定位：{chapter_role}
核心作用：{chapter_purpose}
悬念密度：{suspense_level}
伏笔操作：{foreshadowing}
认知颠覆：{plot_twist_level}
本章简述：{chapter_summary}

可用元素：
- 核心人物(可能未指定)：{characters_involved}
- 关键道具(可能未指定)：{key_items}
- 空间坐标(可能未指定)：{scene_location}
- 时间压力(可能未指定)：{time_constraint}

参考文档：
- 小说设定：
{novel_setting}

【开篇设计要求】
- 前200字内必须出现冲突或异常
- 用"未完成动作开局"或"倒计时开局"制造即时紧迫感
- 主角的困境要在前500字内让读者感知

【对话写作技巧】
- 60%以上的对话不需要"说道/问道"标签，用动作替代
- 对话要有潜台词：表面谈A，实际博弈B
- 用非对称对话长度体现权力关系
- 加入口语化语气词："行吧""嘶""靠""得了吧"
- 对话间插入小动作、环境描写，不要连续对白超过4句

完成第 {novel_number} 章的正文，字数要求{word_number}字。

写作要求：
1. 前200字内必须出现冲突或异常
2. 至少设计2个具有动态张力的场景：
   - 对话场景：潜台词冲突（表面谈A，实际博弈B），60%以上对话不用"说道/问道"
   - 动作场景：环境交互细节（至少3个感官描写），短句加速+比喻减速
   - 心理场景：用动作/行为展示，不用"他感到/他意识到"
3. 章末必须使用强钩子（突然揭示/紧急危机/身份反转/两难抉择）
4. 段落以1-3句为主，避免每段4-6句的均匀节奏
5. 加入口语化语气词，避免书面腔

格式要求：
- 仅返回章节正文文本；
- 不使用分章节小标题；
- 不要使用markdown格式。

额外指导(可能未指定)：{user_guidance}
"""

# =============== 增强版后续章节草稿 Prompt ===============
# 注意：只使用原始代码传递的占位符，不添加额外占位符
enhanced_next_chapter_draft_prompt = """\
参考文档：
└── 前文摘要：
    {global_summary}

└── 前章结尾段：
    {previous_chapter_excerpt}

└── 用户指导：
    {user_guidance}

└── 角色状态：
    {character_state}

└── 当前章节摘要：
    {short_summary}

当前章节信息：
第{novel_number}章《{chapter_title}》：
├── 章节定位：{chapter_role}
├── 核心作用：{chapter_purpose}
├── 悬念密度：{suspense_level}
├── 伏笔设计：{foreshadowing}
├── 转折程度：{plot_twist_level}
├── 章节简述：{chapter_summary}
├── 字数要求：{word_number}字
├── 核心人物：{characters_involved}
├── 关键道具：{key_items}
├── 场景地点：{scene_location}
└── 时间压力：{time_constraint}

下一章节目录
第{next_chapter_number}章《{next_chapter_title}》：
├── 章节定位：{next_chapter_role}
├── 核心作用：{next_chapter_purpose}
├── 悬念密度：{next_chapter_suspense_level}
├── 伏笔设计：{next_chapter_foreshadowing}
├── 转折程度：{next_chapter_plot_twist_level}
└── 章节简述：{next_chapter_summary}

知识库参考：（按优先级应用）
{filtered_context}

【对话写作技巧】
- 60%以上的对话不需要"说道/问道"标签，用动作替代
- 对话要有潜台词：表面谈A，实际博弈B
- 加入口语化语气词："行吧""嘶""靠""得了吧"
- 对话间插入小动作、环境描写，连续对白不超过4句

【情绪弧线设计】
- 都市长篇推荐：W形弧线（多反转）或递进弧线（打脸升级）
- 每5章一个小高潮，每10章一个大反转

🎯 写作核心要求：
1. 与前文摘要、前章结尾段衔接流畅
2. 章末必须使用钩子（突然揭示/紧急危机/身份反转/两难抉择等）
3. 段落以1-3句为主，避免均匀节奏
4. 60%以上对话不用"说道/问道"标签，用动作替代
5. 用动作展示情绪，不用"他感到/他意识到/心中涌起"
6. 避免AI常见句式："不是A，而是B"、"带着……"万能状语、"眼中闪过一丝"
7. 加入口语化语气词（行吧/嘶/靠/得了吧），避免书面腔
8. 对话间插入小动作、环境描写，连续对白不超过4句

知识库应用规则：
- 禁止直接复制已有章节的情节模式
- 历史章节内容仅允许参照叙事节奏（不超过20%相似度）
- 写作技法类知识优先用于增强场景表现力

依据前面所有设定，开始完成第 {novel_number} 章的正文，字数要求{word_number}字。

格式要求：
- 仅返回章节正文文本；
- 不使用分章节小标题；
- 不要使用markdown格式。
"""


def get_enhanced_prompts(genre: str = "都市") -> dict:
    """
    根据题材返回增强版 prompt 模板字典。
    将 oh-story 的方法论注入到 AI_NovelGenerator 的 prompt 体系中。
    """
    # 精确匹配 → 前缀匹配 → 默认公式
    genre_formula = GENRE_FORMULAS.get(genre)
    if genre_formula is None:
        for key in GENRE_FORMULAS:
            if genre.startswith(key) or key.startswith(genre):
                genre_formula = GENRE_FORMULAS[key]
                break
    if genre_formula is None:
        genre_formula = DEFAULT_GENRE_FORMULA
    chapter_hooks = CHAPTER_HOOKS_13
    emotional_arcs = EMOTIONAL_ARCS
    dialogue_mastery = DIALOGUE_MASTERY
    opening_design = OPENING_DESIGN

    return {
        "core_seed_prompt": enhanced_core_seed_prompt.format(
            topic="{topic}",
            genre="{genre}",
            number_of_chapters="{number_of_chapters}",
            word_number="{word_number}",
            genre_formula=genre_formula,
        ),
        "character_dynamics_prompt": enhanced_character_dynamics_prompt.format(
            user_guidance="{user_guidance}",
            core_seed="{core_seed}",
            dialogue_mastery=dialogue_mastery,
        ),
        "world_building_prompt": enhanced_world_building_prompt.format(
            user_guidance="{user_guidance}",
            core_seed="{core_seed}",
        ),
        "plot_architecture_prompt": enhanced_plot_architecture_prompt.format(
            user_guidance="{user_guidance}",
            core_seed="{core_seed}",
            character_dynamics="{character_dynamics}",
            world_building="{world_building}",
            emotional_arcs=emotional_arcs,
            act1_pct="{act1_pct}",
            act2_pct="{act2_pct}",
            act3_pct="{act3_pct}",
        ),
        "chapter_blueprint_prompt": enhanced_chapter_blueprint_prompt.format(
            user_guidance="{user_guidance}",
            novel_architecture="{novel_architecture}",
            chapter_hooks=chapter_hooks,
            number_of_chapters="{number_of_chapters}",
        ),
        "first_chapter_draft_prompt": enhanced_first_chapter_draft_prompt.format(
            novel_number="{novel_number}",
            chapter_title="{chapter_title}",
            chapter_role="{chapter_role}",
            chapter_purpose="{chapter_purpose}",
            suspense_level="{suspense_level}",
            foreshadowing="{foreshadowing}",
            plot_twist_level="{plot_twist_level}",
            chapter_summary="{chapter_summary}",
            characters_involved="{characters_involved}",
            key_items="{key_items}",
            scene_location="{scene_location}",
            time_constraint="{time_constraint}",
            novel_setting="{novel_setting}",
            word_number="{word_number}",
            opening_design=opening_design,
            dialogue_mastery=dialogue_mastery,
            user_guidance="{user_guidance}",
        ),
        "next_chapter_draft_prompt": enhanced_next_chapter_draft_prompt.format(
            global_summary="{global_summary}",
            previous_chapter_excerpt="{previous_chapter_excerpt}",
            user_guidance="{user_guidance}",
            character_state="{character_state}",
            short_summary="{short_summary}",
            novel_number="{novel_number}",
            chapter_title="{chapter_title}",
            chapter_role="{chapter_role}",
            chapter_purpose="{chapter_purpose}",
            suspense_level="{suspense_level}",
            foreshadowing="{foreshadowing}",
            plot_twist_level="{plot_twist_level}",
            chapter_summary="{chapter_summary}",
            word_number="{word_number}",
            characters_involved="{characters_involved}",
            key_items="{key_items}",
            scene_location="{scene_location}",
            time_constraint="{time_constraint}",
            chapter_hook="{chapter_hook}",
            next_chapter_number="{next_chapter_number}",
            next_chapter_title="{next_chapter_title}",
            next_chapter_role="{next_chapter_role}",
            next_chapter_purpose="{next_chapter_purpose}",
            next_chapter_suspense_level="{next_chapter_suspense_level}",
            next_chapter_foreshadowing="{next_chapter_foreshadowing}",
            next_chapter_plot_twist_level="{next_chapter_plot_twist_level}",
            next_chapter_summary="{next_chapter_summary}",
            filtered_context="{filtered_context}",
            dialogue_mastery=dialogue_mastery,
            emotional_arcs=emotional_arcs,
        ),
        # 保留原有不变的 prompt
        "summarize_recent_chapters_prompt": None,  # 使用原始
        "knowledge_search_prompt": None,
        "knowledge_filter_prompt": None,
        "summary_prompt": None,
        "create_character_state_prompt": None,
        "update_character_state_prompt": None,
        "enrich_prompt": None,
        "Character_Import_Prompt": None,
    }
