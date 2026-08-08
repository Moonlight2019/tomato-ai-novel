# gui/pages/market_page.py
# -*- coding: utf-8 -*-
"""
市场分析页 — 番茄小说趋势分析和选题建议
"""
import os

def _get_llm_for_task(config, task_key):
    """根据任务名称获取对应的LLM配置"""
    choose = config.get("choose_configs", {})
    model_name = choose.get(task_key, "")
    if model_name:
        llm = config.get("llm_configs", {}).get(model_name, {})
        if llm:
            return llm
    for name, cfg in config.get("llm_configs", {}).items():
        if cfg.get("api_key"):
            return cfg
    models = config.get("llm_configs", {})
    return list(models.values())[0] if models else {}


def _get_llm(config, task_key="final_chapter_llm"):
    """获取LLM配置"""
    return _get_llm_for_task(config, task_key)
import threading

def _get_llm_for_task(config, task_key):
    """根据任务名称获取对应的LLM配置"""
    choose = config.get("choose_configs", {})
    model_name = choose.get(task_key, "")
    if model_name:
        llm = config.get("llm_configs", {}).get(model_name, {})
        if llm:
            return llm
    for name, cfg in config.get("llm_configs", {}).items():
        if cfg.get("api_key"):
            return cfg
    models = config.get("llm_configs", {})
    return list(models.values())[0] if models else {}


def _get_llm(config, task_key="final_chapter_llm"):
    """获取LLM配置"""
    return _get_llm_for_task(config, task_key)
import customtkinter as ctk

def _get_llm_for_task(config, task_key):
    """根据任务名称获取对应的LLM配置"""
    choose = config.get("choose_configs", {})
    model_name = choose.get(task_key, "")
    if model_name:
        llm = config.get("llm_configs", {}).get(model_name, {})
        if llm:
            return llm
    for name, cfg in config.get("llm_configs", {}).items():
        if cfg.get("api_key"):
            return cfg
    models = config.get("llm_configs", {})
    return list(models.values())[0] if models else {}


def _get_llm(config, task_key="final_chapter_llm"):
    """获取LLM配置"""
    return _get_llm_for_task(config, task_key)


class MarketPage(ctk.CTkFrame):
    """市场分析页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        ctk.CTkLabel(header, text="📊 市场分析", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="分析番茄小说热门趋势，获取选题建议", font=ctk.CTkFont(size=13), text_color="gray60").pack(side="left", padx=15)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # 操作区
        action_frame = ctk.CTkFrame(content)
        action_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(action_frame, text="题材:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5))
        self.genre_var = ctk.StringVar(value="都市")
        ctk.CTkOptionMenu(action_frame, variable=self.genre_var, values=[
            "都市", "校园", "玄幻", "仙侠", "悬疑", "言情", "科幻", "历史", "系统流", "无限流"
        ], width=120).pack(side="left", padx=5)

        ctk.CTkButton(action_frame, text="🔍 AI趋势分析", command=self._analyze_trends,
                      fg_color="#2563eb").pack(side="left", padx=15)
        ctk.CTkButton(action_frame, text="💡 选题建议", command=self._suggest_topics).pack(side="left", padx=5)

        # 结果区
        self.result_text = ctk.CTkTextbox(content, font=ctk.CTkFont(size=13))
        self.result_text.grid(row=1, column=0, sticky="nsew")
        self.result_text.insert("1.0",
            "点击上方按钮开始分析...\n\n"
            "📊 AI趋势分析：基于当前题材分析热门方向、读者偏好、写作要点\n"
            "💡 选题建议：生成3-5个有潜力的选题方案"
        )

        # 状态
        self.status_label = ctk.CTkLabel(content, text="", text_color="gray60")
        self.status_label.grid(row=2, column=0, sticky="w", pady=5)

    def _analyze_trends(self):
        """AI分析市场趋势"""
        genre = self.genre_var.get()
        self.status_label.configure(text="分析中...", text_color="gray60")

        def do_analyze():
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from llm_adapters import create_llm_adapter

                config = self.master.get_config()
                llm = _get_llm(config)
                adapter = create_llm_adapter(
                    interface_format=llm.get("interface_format", "mimo"),
                    base_url=llm.get("base_url", ""),
                    model_name=llm.get("model_name", "mimo-v2.5-pro"),
                    api_key=llm.get("api_key", ""),
                    temperature=0.7, max_tokens=3000, timeout=120
                )

                prompt = f"""你是番茄小说平台的资深运营专家。请分析「{genre}」题材的当前市场趋势。

请从以下维度分析：

1. **热门方向**：当前{genre}类最火的3-5个细分方向
2. **读者画像**：这类读者的核心需求和阅读偏好
3. **爆款特征**：近期热门作品的共同特点
4. **写作要点**：新人写{genre}类最容易犯的错误和成功关键
5. **避坑指南**：哪些套路已经过时、哪些题材敏感

请用简洁的要点形式输出，每个维度3-5条。"""

                result = adapter.invoke(prompt)
                self.after(0, lambda: self._show_result(f"📊 {genre}类市场趋势分析\n\n{result}"))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {e}", text_color="red"))

        threading.Thread(target=do_analyze, daemon=True).start()

    def _suggest_topics(self):
        """AI选题建议"""
        genre = self.genre_var.get()
        self.status_label.configure(text="生成选题建议...", text_color="gray60")

        def do_suggest():
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from llm_adapters import create_llm_adapter

                config = self.master.get_config()
                llm = _get_llm(config)
                adapter = create_llm_adapter(
                    interface_format=llm.get("interface_format", "mimo"),
                    base_url=llm.get("base_url", ""),
                    model_name=llm.get("model_name", "mimo-v2.5-pro"),
                    api_key=llm.get("api_key", ""),
                    temperature=0.9, max_tokens=3000, timeout=120
                )

                prompt = f"""你是番茄小说平台的选题专家。请为「{genre}」题材生成5个有潜力的选题方案。

每个选题包含：
1. 书名（10字以内，有悬念感）
2. 核心设定（一句话）
3. 目标读者
4. 预期爽点
5. 可行性评分（1-5星）

要求：
- 设定新颖，避免同质化
- 适合番茄平台（免费阅读、快节奏）
- 有明确的商业潜力
- 每个选题之间有差异性

输出格式：
---
**选题1：《书名》**
- 核心设定：...
- 目标读者：...
- 预期爽点：...
- 可行性：⭐⭐⭐⭐⭐
---"""

                result = adapter.invoke(prompt)
                self.after(0, lambda: self._show_result(f"💡 {genre}类选题建议\n\n{result}"))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {e}", text_color="red"))

        threading.Thread(target=do_suggest, daemon=True).start()

    def _show_result(self, text):
        """显示结果"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.status_label.configure(text="✅ 分析完成", text_color="green")
