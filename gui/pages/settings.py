# gui/pages/settings.py
# -*- coding: utf-8 -*-
"""
设置页 — API配置、模型管理、批量设置、导出设置
"""
import customtkinter as ctk


# 预置模型配置模板（2026年8月更新）
PRESET_MODELS = {
    # ===== OpenAI (GPT-5.6系列) =====
    "OpenAI GPT-5.6 Sol": {
        "api_key": "", "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-5.6", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 128000, "timeout": 600
    },
    "OpenAI GPT-5.6 Terra": {
        "api_key": "", "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-5.6-terra", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 128000, "timeout": 600
    },
    "OpenAI GPT-5.6 Luna": {
        "api_key": "", "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-5.6-luna", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 128000, "timeout": 600
    },

    # ===== Anthropic Claude (5代) =====
    "Claude Fable 5": {
        "api_key": "", "base_url": "https://api.anthropic.com",
        "model_name": "claude-fable-5", "interface_format": "anthropic",
        "temperature": 0.7, "max_tokens": 128000, "timeout": 600
    },
    "Claude Opus 5": {
        "api_key": "", "base_url": "https://api.anthropic.com",
        "model_name": "claude-opus-5", "interface_format": "anthropic",
        "temperature": 0.7, "max_tokens": 128000, "timeout": 600
    },
    "Claude Sonnet 5": {
        "api_key": "", "base_url": "https://api.anthropic.com",
        "model_name": "claude-sonnet-5", "interface_format": "anthropic",
        "temperature": 0.7, "max_tokens": 128000, "timeout": 600
    },
    "Claude Haiku 4.5": {
        "api_key": "", "base_url": "https://api.anthropic.com",
        "model_name": "claude-haiku-4-5-20251001", "interface_format": "anthropic",
        "temperature": 0.7, "max_tokens": 64000, "timeout": 600
    },

    # ===== Google Gemini (3代) =====
    "Gemini 3.6 Flash": {
        "api_key": "", "base_url": "",
        "model_name": "gemini-3.6-flash", "interface_format": "gemini",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Gemini 3.5 Flash": {
        "api_key": "", "base_url": "",
        "model_name": "gemini-3.5-flash", "interface_format": "gemini",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Gemini 3.1 Pro": {
        "api_key": "", "base_url": "",
        "model_name": "gemini-3.1-pro-preview", "interface_format": "gemini",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Gemini 2.5 Pro": {
        "api_key": "", "base_url": "",
        "model_name": "gemini-2.5-pro", "interface_format": "gemini",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== DeepSeek (V4系列) =====
    "DeepSeek V4 Pro": {
        "api_key": "", "base_url": "https://api.deepseek.com/v1",
        "model_name": "deepseek-v4-pro", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "DeepSeek V4 Flash": {
        "api_key": "", "base_url": "https://api.deepseek.com/v1",
        "model_name": "deepseek-v4-flash", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== Grok (xAI) =====
    "Grok 4.5": {
        "api_key": "", "base_url": "https://api.x.ai/v1",
        "model_name": "grok-4.5", "interface_format": "grok",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Grok 4.3": {
        "api_key": "", "base_url": "https://api.x.ai/v1",
        "model_name": "grok-4.3", "interface_format": "grok",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== Kimi (K系列) =====
    "Kimi K3": {
        "api_key": "", "base_url": "https://api.moonshot.cn/v1",
        "model_name": "kimi-k3", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Kimi K2.7 Code": {
        "api_key": "", "base_url": "https://api.moonshot.cn/v1",
        "model_name": "kimi-k2.7-code", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Kimi K2.6": {
        "api_key": "", "base_url": "https://api.moonshot.cn/v1",
        "model_name": "kimi-k2.6", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== GLM (智谱) =====
    "GLM-5.2": {
        "api_key": "", "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_name": "glm-5.2", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "GLM-5.1": {
        "api_key": "", "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_name": "glm-5.1", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "GLM-5": {
        "api_key": "", "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_name": "glm-5", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "GLM-4.7": {
        "api_key": "", "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_name": "glm-4.7", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "GLM-4.7-Flash (免费)": {
        "api_key": "", "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model_name": "glm-4.7-flash", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== 通义千问 (Qwen) =====
    "Qwen 3.8 Max": {
        "api_key": "", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_name": "qwen3.8-max", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Qwen 3.7 Plus": {
        "api_key": "", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_name": "qwen3.7-plus", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "Qwen 3.7 Flash": {
        "api_key": "", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model_name": "qwen3.7-flash", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== 百度文心 (ERNIE) =====
    "ERNIE 5.1": {
        "api_key": "", "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
        "model_name": "ernie-5.1", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "ERNIE 5.0": {
        "api_key": "", "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
        "model_name": "ernie-5.0", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "ERNIE 4.5 Turbo": {
        "api_key": "", "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
        "model_name": "ernie-4.5-turbo-128k", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== MiniMax =====
    "MiniMax M2.5": {
        "api_key": "", "base_url": "https://api.minimax.chat/v1",
        "model_name": "MiniMax-M2.5", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== OpenRouter (集成平台，可切换任意模型) =====
    "OpenRouter Claude Sonnet 5": {
        "api_key": "", "base_url": "https://openrouter.ai/api/v1",
        "model_name": "anthropic/claude-sonnet-5", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenRouter GPT-5.6": {
        "api_key": "", "base_url": "https://openrouter.ai/api/v1",
        "model_name": "openai/gpt-5.6", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenRouter Gemini 3.6 Flash": {
        "api_key": "", "base_url": "https://openrouter.ai/api/v1",
        "model_name": "google/gemini-3.6-flash", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenRouter DeepSeek V4 Pro": {
        "api_key": "", "base_url": "https://openrouter.ai/api/v1",
        "model_name": "deepseek/deepseek-v4-pro", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenRouter Grok 4.5": {
        "api_key": "", "base_url": "https://openrouter.ai/api/v1",
        "model_name": "x-ai/grok-4.5", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenRouter Kimi K3": {
        "api_key": "", "base_url": "https://openrouter.ai/api/v1",
        "model_name": "moonshotai/kimi-k3", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== 硅基流动 (集成平台) =====
    "硅基流动 DeepSeek V4 Pro": {
        "api_key": "", "base_url": "https://api.siliconflow.cn/v1",
        "model_name": "deepseek-ai/DeepSeek-V4-Pro", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "硅基流动 GLM-5.2": {
        "api_key": "", "base_url": "https://api.siliconflow.cn/v1",
        "model_name": "zai-org/GLM-5.2", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "硅基流动 Kimi K2.6": {
        "api_key": "", "base_url": "https://api.siliconflow.cn/v1",
        "model_name": "moonshotai/Kimi-K2.6", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "硅基流动 Qwen3.6": {
        "api_key": "", "base_url": "https://api.siliconflow.cn/v1",
        "model_name": "Qwen/Qwen3.6-27B", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== 火山引擎 =====
    "火山引擎 DeepSeek V4 Pro": {
        "api_key": "", "base_url": "",
        "model_name": "deepseek-v4-pro", "interface_format": "火山引擎",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== Groq (高速推理) =====
    "Groq Llama 3.3 70B": {
        "api_key": "", "base_url": "https://api.groq.com/openai/v1",
        "model_name": "llama-3.3-70b-versatile", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== Together AI =====
    "Together AI Kimi K2": {
        "api_key": "", "base_url": "https://api.together.xyz/v1",
        "model_name": "moonshotai/Kimi-K2-Instruct", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== OpenCode Go (订阅制，$10/月，支持11个模型) =====
    "OpenCode Go - DeepSeek V4 Pro": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "deepseek-v4-pro", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - DeepSeek V4 Flash": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "deepseek-v4-flash", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - Grok 4.5": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "grok-4.5", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - Kimi K3": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "kimi-k3", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - Qwen3.8 Max": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "qwen3.8-max", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - GLM-5.2": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "glm-5.2", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - MiniMax M3": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "minimax-m3", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - GPT 5.6 Luna": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "gpt-5.6-luna", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - Qwen3.7 Plus": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "qwen3.7-plus", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "OpenCode Go - MiMo V2.5": {
        "api_key": "", "base_url": "https://api.opencode.ai/v1",
        "model_name": "mimo-v2.5", "interface_format": "openai",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },

    # ===== mimo =====
    "mimo-v2.5-pro": {
        "api_key": "", "base_url": "https://token-plan-cn.xiaomimimo.com/anthropic",
        "model_name": "mimo-v2.5-pro", "interface_format": "mimo",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
    "mimo-v2.5": {
        "api_key": "", "base_url": "https://token-plan-cn.xiaomimimo.com/anthropic",
        "model_name": "mimo-v2.5", "interface_format": "mimo",
        "temperature": 0.7, "max_tokens": 8192, "timeout": 600
    },
}


class SettingsPage(ctk.CTkFrame):
    """设置页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        ctk.CTkLabel(header, text="⚙️ 设置", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

    def _create_content(self):
        # 标签页
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)

        self._create_model_tab()
        self._create_batch_tab()
        self._create_export_tab()

    def _create_model_tab(self):
        tab = self.tabview.add("🤖 模型配置")
        tab.grid_columnconfigure(0, weight=1)

        # 一键添加预置模型（两级选择）
        preset_frame = ctk.CTkFrame(tab)
        preset_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(preset_frame, text="一键添加预置模型", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        # 构建供应商 -> 模型的映射
        self._provider_models = {}
        for name in PRESET_MODELS.keys():
            # 提取供应商名（已知供应商列表）
            provider = "其他"
            known_providers = [
                "OpenAI", "Claude", "Gemini", "DeepSeek", "Grok",
                "Kimi", "GLM", "Qwen", "ERNIE", "MiniMax",
                "OpenRouter", "硅基流动", "火山引擎", "Groq", "Together AI",
                "OpenCode Go", "mimo",
            ]
            for p in known_providers:
                if name.startswith(p):
                    provider = p
                    break
            self._provider_models.setdefault(provider, []).append(name)

        provider_names = list(self._provider_models.keys())

        # 两级选择
        select_frame = ctk.CTkFrame(preset_frame, fg_color="transparent")
        select_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(select_frame, text="提供商:").pack(side="left")
        self._provider_var = ctk.StringVar(value=provider_names[0] if provider_names else "")
        self._provider_menu = ctk.CTkOptionMenu(
            select_frame, variable=self._provider_var,
            values=provider_names, width=150,
            command=self._on_provider_change
        )
        self._provider_menu.pack(side="left", padx=5)

        ctk.CTkLabel(select_frame, text="模型:").pack(side="left", padx=(10, 0))
        self._model_var = ctk.StringVar()
        first_provider_models = self._provider_models.get(provider_names[0], []) if provider_names else []
        self._model_menu = ctk.CTkOptionMenu(
            select_frame, variable=self._model_var,
            values=first_provider_models, width=250
        )
        self._model_menu.pack(side="left", padx=5)

        ctk.CTkButton(select_frame, text="➕ 添加", width=80,
                      command=self._add_selected_preset).pack(side="left", padx=10)

        if first_provider_models:
            self._model_var.set(first_provider_models[0])

        # 当前模型列表
        list_frame = ctk.CTkFrame(tab)
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(list_frame, text="已配置的模型", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        self.model_list = ctk.CTkScrollableFrame(list_frame, height=200)
        self.model_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 任务分配
        self.task_frame = ctk.CTkFrame(tab)
        self.task_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self._build_task_assignments()

    def _create_batch_tab(self):
        tab = self.tabview.add("📝 批量生成")
        tab.grid_columnconfigure(0, weight=1)

        config = self.master.get_config()
        batch = config.get("batch_settings", {})

        ctk.CTkLabel(tab, text="批量生成设置", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=(10, 15))

        # 每章间隔
        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.grid(row=1, column=0, sticky="ew", pady=5)
        ctk.CTkLabel(row1, text="每章间隔(秒):", width=150, anchor="w").pack(side="left")
        self.delay_var = ctk.StringVar(value=str(batch.get("delay_between_chapters", 2)))
        ctk.CTkEntry(row1, textvariable=self.delay_var, width=100).pack(side="left", padx=5)

        # 失败重试
        row2 = ctk.CTkFrame(tab, fg_color="transparent")
        row2.grid(row=2, column=0, sticky="ew", pady=5)
        ctk.CTkLabel(row2, text="失败重试次数:", width=150, anchor="w").pack(side="left")
        self.retry_var = ctk.StringVar(value=str(batch.get("max_retries", 3)))
        ctk.CTkEntry(row2, textvariable=self.retry_var, width=100).pack(side="left", padx=5)

        # 自动扩写阈值
        row3 = ctk.CTkFrame(tab, fg_color="transparent")
        row3.grid(row=3, column=0, sticky="ew", pady=5)
        ctk.CTkLabel(row3, text="自动扩写阈值(%):", width=150, anchor="w").pack(side="left")
        self.enrich_var = ctk.StringVar(value=str(batch.get("enrich_threshold", 80)))
        ctk.CTkEntry(row3, textvariable=self.enrich_var, width=100).pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="字数低于目标的此比例时自动扩写", text_color="gray60").pack(side="left", padx=10)

        # 自动去AI味
        row4 = ctk.CTkFrame(tab, fg_color="transparent")
        row4.grid(row=4, column=0, sticky="ew", pady=5)
        self.auto_deslop_var = ctk.BooleanVar(value=batch.get("auto_deslop", True))
        ctk.CTkSwitch(row4, text="批量生成后自动去AI味", variable=self.auto_deslop_var).pack(side="left")

        ctk.CTkButton(tab, text="💾 保存批量设置", command=self._save_batch).grid(row=5, column=0, sticky="w", pady=20)

    def _create_export_tab(self):
        tab = self.tabview.add("📦 导出")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="导出设置", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=(10, 15))

        # 默认导出目录
        row1 = ctk.CTkFrame(tab, fg_color="transparent")
        row1.grid(row=1, column=0, sticky="ew", pady=5)
        ctk.CTkLabel(row1, text="默认导出目录:", width=150, anchor="w").pack(side="left")
        self.export_dir_var = ctk.StringVar(value="exports/")
        ctk.CTkEntry(row1, textvariable=self.export_dir_var, width=300).pack(side="left", padx=5)

        # 番茄格式说明
        info_frame = ctk.CTkFrame(tab)
        info_frame.grid(row=2, column=0, sticky="ew", pady=20)
        ctk.CTkLabel(info_frame, text="📋 番茄小说投稿格式说明", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        info_text = (
            "• 文件编码：UTF-8\n"
            "• 章节格式：第N章 标题（独占一行）\n"
            "• 章节间空两行\n"
            "• 建议每章 2000-4000 字\n"
            "• 避免使用破折号和省略号\n"
            "• 对话用中文引号"
        )
        ctk.CTkLabel(info_frame, text=info_text, justify="left", text_color="gray60").pack(anchor="w", padx=10, pady=(0, 10))

    def _on_provider_change(self, provider):
        """供应商下拉框变化时，更新模型下拉框"""
        models = self._provider_models.get(provider, [])
        self._model_menu.configure(values=models)
        if models:
            self._model_var.set(models[0])

    def _add_selected_preset(self):
        """添加当前选中的预置模型"""
        name = self._model_var.get()
        if name and name in PRESET_MODELS:
            self._add_preset_by_name(name)

    def _add_preset(self):
        name = self.preset_var.get()
        if name not in PRESET_MODELS:
            return
        self._add_preset_by_name(name)

    def _add_preset_by_name(self, name):
        """按名称添加预置模型"""
        if name not in PRESET_MODELS:
            return

        preset = PRESET_MODELS[name]
        config = self.master.get_config()
        config.setdefault("llm_configs", {})

        # 用预置名作为key
        key = name.replace(" ", "-").replace("/", "-")
        if key not in config["llm_configs"]:
            config["llm_configs"][key] = preset.copy()
            self.master.save_config(config)
            self._refresh_model_list()

            # 弹窗提示输入 API Key
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"配置 {name}")
            dialog.geometry("400x150")
            dialog.transient(self.master)
            dialog.grab_set()

            ctk.CTkLabel(dialog, text=f"已添加「{name}」\n请输入 API Key：",
                        font=ctk.CTkFont(size=13)).pack(pady=(15, 5))
            key_entry = ctk.CTkEntry(dialog, width=350, show="*")
            key_entry.pack(pady=5)

            def save_key():
                k = key_entry.get().strip()
                if k:
                    config["llm_configs"][key]["api_key"] = k
                    self.master.save_config(config)
                    self._refresh_model_list()
                    self._build_task_assignments()
                dialog.destroy()

            ctk.CTkButton(dialog, text="保存", command=save_key, fg_color="#2563eb").pack(pady=10)
        else:
            # 已存在，提示
            dialog = ctk.CTkToplevel(self)
            dialog.title("提示")
            dialog.geometry("300x100")
            dialog.transient(self.master)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text=f"「{name}」已存在", font=ctk.CTkFont(size=13)).pack(pady=20)
            ctk.CTkButton(dialog, text="确定", command=dialog.destroy).pack(pady=10)

    def _build_task_assignments(self):
        """构建任务模型分配区域（可刷新）"""
        for w in self.task_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.task_frame, text="任务模型分配", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        self.task_vars = {}
        self.task_menus = {}
        tasks = [
            ("architecture_llm", "架构生成"),
            ("chapter_outline_llm", "大纲生成"),
            ("final_chapter_llm", "正文写作"),
            ("consistency_review_llm", "一致性检查"),
        ]

        config = self.master.get_config()
        choose = config.get("choose_configs", {})
        model_names = list(config.get("llm_configs", {}).keys())

        for key, label in tasks:
            row = ctk.CTkFrame(self.task_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=f"{label}:", width=120, anchor="w").pack(side="left")
            var = ctk.StringVar(value=choose.get(key, ""))
            menu = ctk.CTkOptionMenu(row, variable=var, values=model_names, width=200)
            menu.pack(side="left", padx=5)
            self.task_vars[key] = var
            self.task_menus[key] = menu

        ctk.CTkButton(self.task_frame, text="💾 保存任务分配", command=self._save_tasks).pack(anchor="w", padx=10, pady=10)

    def _refresh_model_list(self):
        for w in self.model_list.winfo_children():
            w.destroy()

        config = self.master.get_config()
        models = config.get("llm_configs", {})

        for i, (name, cfg) in enumerate(models.items()):
            row = ctk.CTkFrame(self.model_list)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(weight="bold"), width=150, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=cfg.get("model_name", ""), text_color="gray60", width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=cfg.get("interface_format", ""), text_color="gray60", width=80, anchor="w").pack(side="left")

            has_key = "✓" if cfg.get("api_key") else "✗"
            color = "green" if cfg.get("api_key") else "red"
            ctk.CTkLabel(row, text=f"Key:{has_key}", text_color=color, width=60).pack(side="left")

            ctk.CTkButton(row, text="🗑", width=30, height=25, fg_color="#dc2626",
                         command=lambda n=name: self._delete_model(n)).pack(side="right", padx=5)

    def _delete_model(self, name):
        config = self.master.get_config()
        config.get("llm_configs", {}).pop(name, None)
        self.master.save_config(config)
        self._refresh_model_list()
        self._build_task_assignments()

    def _save_tasks(self):
        config = self.master.get_config()
        config.setdefault("choose_configs", {})
        for key, var in self.task_vars.items():
            config["choose_configs"][key] = var.get()
        self.master.save_config(config)

    def _save_batch(self):
        config = self.master.get_config()
        config["batch_settings"] = {
            "delay_between_chapters": int(self.delay_var.get()),
            "max_retries": int(self.retry_var.get()),
            "enrich_threshold": int(self.enrich_var.get()),
            "auto_deslop": self.auto_deslop_var.get(),
        }
        self.master.save_config(config)

    def tkraise(self, *args):
        super().tkraise(*args)
        self._refresh_model_list()
        config = self.master.get_config()
        model_names = list(config.get("llm_configs", {}).keys())
        for key, var in self.task_vars.items():
            pass  # values already set
