# gui/pages/analyze_page.py
# -*- coding: utf-8 -*-
"""
拆文分析页 — 分析已有小说的结构、钩子、人物、节奏
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


class AnalyzePage(ctk.CTkFrame):
    """拆文分析页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        ctk.CTkLabel(header, text="🔬 拆文分析", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="分析已有小说的写法，学习爆款套路", font=ctk.CTkFont(size=13), text_color="gray60").pack(side="left", padx=15)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # 操作区
        action_frame = ctk.CTkFrame(content)
        action_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(action_frame, text="分析类型:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5))
        self.analysis_type = ctk.StringVar(value="全文结构")
        ctk.CTkOptionMenu(action_frame, variable=self.analysis_type, values=[
            "全文结构", "黄金三章", "钩子分析", "人物分析", "节奏分析", "对话分析"
        ], width=120).pack(side="left", padx=5)

        ctk.CTkButton(action_frame, text="📂 导入文本", command=self._import_text,
                      fg_color="gray50").pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="🔍 开始分析", command=self._start_analysis,
                      fg_color="#2563eb").pack(side="left", padx=5)

        self.wordcount_label = ctk.CTkLabel(action_frame, text="字数: 0", text_color="gray60")
        self.wordcount_label.pack(side="right", padx=10)

        # 文本区（左右分栏）
        paned = ctk.CTkFrame(content, fg_color="transparent")
        paned.grid(row=1, column=0, sticky="nsew")
        paned.grid_columnconfigure(0, weight=1)
        paned.grid_columnconfigure(1, weight=1)
        paned.grid_rowconfigure(0, weight=1)

        # 左侧：原文
        left_frame = ctk.CTkFrame(paned)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(left_frame, text="📄 原文", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.input_text = ctk.CTkTextbox(left_frame, font=ctk.CTkFont(size=12))
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.input_text.insert("1.0", "在此粘贴要分析的小说文本...\n\n或点击「导入文本」从文件导入。")
        self.input_text.bind("<<Modified>>", self._on_text_modified)

        # 右侧：分析结果
        right_frame = ctk.CTkFrame(paned)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right_frame, text="📊 分析结果", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.result_text = ctk.CTkTextbox(right_frame, font=ctk.CTkFont(size=12))
        self.result_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # 状态
        self.status_label = ctk.CTkLabel(content, text="", text_color="gray60")
        self.status_label.grid(row=2, column=0, sticky="w", pady=5)

    def _on_text_modified(self, event=None):
        content = self.input_text.get("1.0", "end-1c")
        self.wordcount_label.configure(text=f"字数: {len(content)}")

    def _import_text(self):
        """从文件导入文本"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="选择小说文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.input_text.delete("1.0", "end")
                self.input_text.insert("1.0", content)
                self.status_label.configure(text=f"已导入: {os.path.basename(filepath)}", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"导入失败: {e}", text_color="red")

    def _start_analysis(self):
        """开始分析"""
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text or len(text) < 100:
            self.status_label.configure(text="请输入至少100字的文本", text_color="red")
            return

        analysis_type = self.analysis_type.get()
        self.status_label.configure(text=f"正在分析: {analysis_type}...", text_color="gray60")

        def do_analysis():
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
                    temperature=0.3, max_tokens=4000, timeout=120
                )

                # 截断过长文本
                if len(text) > 8000:
                    analysis_text = text[:4000] + "\n...\n" + text[-4000:]
                else:
                    analysis_text = text

                prompts = {
                    "全文结构": f"""请分析以下小说文本的全文结构：

{analysis_text}

分析维度：
1. 三幕结构划分（触发/对抗/解决）
2. 主要情节点和转折
3. 伏笔和回收
4. 节奏曲线（紧张/舒缓交替）
5. 核心冲突和解决方式

请用结构化的方式输出分析结果。""",

                    "黄金三章": f"""请分析以下小说文本的"黄金三章"（前三章）写法：

{analysis_text}

分析维度：
1. 开篇钩子（前200字如何吸引读者）
2. 人物出场方式
3. 核心冲突引入时机
4. 金手指/系统激活节点
5. 爽点设计和节奏
6. 可借鉴的技巧

请详细分析每个维度。""",

                    "钩子分析": f"""请分析以下小说文本中的钩子设计：

{analysis_text}

分析维度：
1. 章末钩子类型（突然揭示/紧急危机/身份反转等）
2. 章首钩子类型
3. 段落级悬念
4. 信息差制造
5. 读者期待管理

请逐章或逐段分析钩子使用情况。""",

                    "人物分析": f"""请分析以下小说文本中的人物塑造：

{analysis_text}

分析维度：
1. 主角人设（能力/性格/目标/弱点）
2. 配角功能（对手/盟友/导师）
3. 人物关系网
4. 对话风格差异
5. 人物弧光（成长变化）

请详细分析每个人物。""",

                    "节奏分析": f"""请分析以下小说文本的节奏控制：

{analysis_text}

分析维度：
1. 段落长度分布
2. 对话/叙述比例
3. 紧张/舒缓交替模式
4. 信息密度
5. 爽点间隔

请用数据和示例说明。""",

                    "对话分析": f"""请分析以下小说文本中的对话写法：

{analysis_text}

分析维度：
1. 对话标签使用（说道/问道/无标签比例）
2. 对话潜台词
3. 人物说话风格差异
4. 对话间动作描写
5. 信息传递效率

请逐项分析并给出改进建议。""",
                }

                prompt = prompts.get(analysis_type, prompts["全文结构"])
                result = adapter.invoke(prompt)
                self.after(0, lambda: self._show_result(result))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {e}", text_color="red"))

        threading.Thread(target=do_analysis, daemon=True).start()

    def _show_result(self, text):
        """显示分析结果"""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.status_label.configure(text="✅ 分析完成", text_color="green")
