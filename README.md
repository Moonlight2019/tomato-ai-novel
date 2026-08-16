# 番茄 AI 写作系统

这是一个完全使用AI完成的项目，如果有帮助到你那是我的荣幸，如果使用时出现任何问题，我推荐你直接AI修复而不是提Issue，那样会更有效率。

首先非常感谢**AI_NovelGenerator**和**oh-story-claudecode**项目，本项目完全基于这两个项目拼接而来，仅仅是做了一个GUI。并没有做出什么很有价值的贡献。

以下完全由AI生成

结合 [AI_NovelGenerator](https://github.com/YILING0013/AI_NovelGenerator) 的自动流水线与 [oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) 的网文方法论，专为番茄小说平台打造的 AI 写作工具。

## 核心特性

- **四步自动流水线**：设定 → 大纲 → 章节草稿 → 定稿，全程自动化
- **增强版 Prompt**：注入 18 种题材公式、13 种章末钩子、6 种情绪弧线、对话技巧
- **风格预设 + 基调控制**：8 种内置风格一键选用（轻松搞笑/温馨治愈/热血燃向等），支持自定义与 AI 推荐；自动识别内容指导中的基调要求，轻松向作品不再被"阴谋/黑暗"带偏
- **7 Gate 去 AI 味**：禁词替换、句式去模板化、心理描写外化、节奏调整、对话去模板化、结尾去升华、去解释性旁白
- **番茄平台适配**：字数检查、标点规范、段落长度控制
- **向量检索上下文**：ChromaDB 向量库维持长篇小说的一致性
- **多模型路由**：不同任务用不同模型（便宜的写大纲，贵的写正文）
- **GUI 工作台**：可视化操作，书架管理、创意输入（含风格预设）、章节写作、去 AI 味、市场分析、导出

## 快速开始

### 1. 安装依赖

```bash
pip install -r engine/requirements.txt
```

### 2. 配置 API

复制配置模板并填入你的 API Key：

```bash
cp config/config.example.json config/config.json
```

编辑 `config/config.json`，在 `llm_configs` 中填入 API Key。

支持的模型提供商：

| 提供商 | 模型示例 | 接口格式 |
|--------|---------|---------|
| OpenAI | GPT-5.6 Sol / Terra / Luna | openai |
| Claude | Fable 5 / Opus 5 / Sonnet 5 | anthropic |
| DeepSeek | V4 Pro / V4 Flash | openai |
| Gemini | 3.6 Flash / 3.5 Flash / 2.5 Pro | gemini |
| Grok | 4.5 / 4.3 | grok |
| Kimi | K3 / K2.7 Code / K2.6 | openai |
| GLM | 5.2 / 5.1 / 4.7 | openai |
| Qwen | 3.8 Max / 3.7 Plus | openai |
| ERNIE | 5.1 / 5.0 / 4.5 Turbo | openai |
| mimo | mimo-v2.5-pro / mimo-v2.5 | mimo |

集成平台：OpenRouter、硅基流动、火山引擎、OpenCode Go、Groq、Together AI

### 3. 启动 GUI

```bash
python run_gui.py
```

### 4. 或使用命令行

```bash
# 完整流水线
python pipeline.py --action full

# 生成单章
python pipeline.py --action step3 --chapter 5

# 去 AI 味
python pipeline.py --action deslop --chapter 5

# 批量生成
python pipeline.py --action full --start 10 --end 20
```

## 项目结构

```
├── engine/                    # 核心引擎
│   ├── novel_generator/       # 四步流水线
│   ├── llm_adapters.py        # LLM 抽象层（15+ 适配器）
│   ├── embedding_adapters.py  # Embedding 抽象层
│   ├── enhanced_prompts.py    # 增强版 Prompt（含基调控制）
│   ├── style_presets.py       # 风格预设库（内置 8 种 + 自定义）
│   └── config_manager.py      # 配置管理
│
├── quality/                   # 质量层
│   ├── deslop/                # 去 AI 味引擎（7 Gate）
│   └── knowledge/             # 网文方法论知识库（40+ 文档）
│
├── gui/                       # GUI 工作台
│   ├── app.py                 # 主窗口
│   └── pages/                 # 各功能页面
│
├── config/                    # 配置文件
│   ├── config.example.json    # 配置模板
│   └── fanqie_rules.json      # 番茄平台规则
│
├── pipeline.py                # 命令行流水线
├── export.py                  # 导出模块
└── run_gui.py                 # GUI 启动入口
```

## 去 AI 味系统（7 Gate）

| Gate | 功能 | 示例 |
|------|------|------|
| A | 禁词替换 | "眼中闪过一丝" → "垂下眼" |
| B | 有毒句式 | "命运终于露出獠牙" → 删除 |
| C | 对话标签 | "说道/问道" → 用动作替代 |
| D | 节奏调整 | 拆分 6 句以上长段落 |
| E | 对话修饰 | "冷冷地说道" → "说" |
| F | 结尾升华 | "属于他的反击才刚刚开始" → 删除 |
| G | 解释旁白 | "她不知道的是" → 删除 |

## 支持题材

都市、校园、玄幻、仙侠、悬疑、言情、科幻、末世、历史、职场、系统流、无限流、穿越等 18 种题材，每种配有专属写作公式。

## 风格预设

在「创意输入」页选择一种风格，即可一键作用于整本书（设定、大纲、正文统一），无需每次手动在创意里写风格要求。

| 风格 | 说明 |
|------|------|
| 轻松搞笑 | 沙雕吐槽、段子频出、社死名场面 |
| 温馨治愈 | 温暖细腻、治愈向，不虐不黑暗 |
| 热血燃向 | 打脸升级、逆境翻盘，燃点密集 |
| 悬疑紧张 | 谜团线索、反转，钩子拉满 |
| 细腻情感 | 心理描写细、感情戏重，甜虐可控 |
| 冷峻简洁 | 语言精炼、克制短句，不煽情 |
| 文艺氛围 | 描写丰富、氛围感强，有意境 |
| 快节奏爽文 | 番茄平台默认：短段落、对话多、爽点密集 |

- 支持**自定义风格**（存于 `config/custom_styles.json`，同名覆盖内置）
- 支持**「AI 推荐风格」**：根据创意文本自动匹配最合适的风格
- 风格会与全局**「基调控制」**联动：内容指导若要求"轻松/愉快"，自动禁止阴谋、黑暗、死亡等设定；要求"黑暗/虐/权谋"则正常使用高强度冲突

## 致谢

- [AI_NovelGenerator](https://github.com/YILING0013/AI_NovelGenerator) — 核心流水线引擎
- [oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) — 网文方法论知识库

## 许可证

MIT License
