# gui/pages/outline.py
# -*- coding: utf-8 -*-
"""
大纲编辑页 — 查看和编辑章节目录，可重新生成
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


class OutlinePage(ctk.CTkFrame):
    """大纲编辑页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        ctk.CTkLabel(header, text="📑 大纲编辑", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="查看和编辑章节目录大纲", font=ctk.CTkFont(size=13), text_color="gray60").pack(side="left", padx=15)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(content, font=ctk.CTkFont(size=13))
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.insert("1.0", "尚未生成大纲。请先在「创意输入」页生成架构。")

        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        ctk.CTkButton(btn_frame, text="🔄 重新加载", command=self._reload).pack(side="left")
        self.gen_btn = ctk.CTkButton(btn_frame, text="📝 生成大纲", command=self._regenerate, fg_color="#2563eb")
        self.gen_btn.pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="💾 保存修改", command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="← 上一步", command=lambda: self.master._show_page("architecture")).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="下一步 →", command=lambda: self.master._show_page("writing")).pack(side="right")

        self.progress = ctk.CTkProgressBar(btn_frame, width=150)
        self.progress.pack(side="left", padx=15)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(btn_frame, text="", text_color="gray60")
        self.status_label.pack(side="left")

    def _get_filepath(self):
        config = self.master.get_config()
        topic = config.get("other_params", {}).get("topic", "")
        if not topic:
            return None
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects", topic)

    def _reload(self):
        filepath = self._get_filepath()
        if not filepath:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", "请先在「创意输入」页创建项目并生成架构。")
            return
        outline_file = os.path.join(filepath, "Novel_directory.txt")
        if os.path.exists(outline_file):
            with open(outline_file, "r", encoding="utf-8") as f:
                content = f.read()
            if content.strip():
                self.textbox.delete("1.0", "end")
                self.textbox.insert("1.0", content)
                self.status_label.configure(text="已加载", text_color="green")
            else:
                self.textbox.delete("1.0", "end")
                self.textbox.insert("1.0", "大纲文件为空。请点击「📝 生成大纲」按钮生成。")
                self.status_label.configure(text="大纲为空，请生成", text_color="orange")
        else:
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", "大纲文件不存在。\n\n请先在「创意输入」页完成创意生成（会自动生成架构和大纲），\n或点击下方「📝 生成大纲」按钮手动生成。")
            self.status_label.configure(text="大纲不存在", text_color="orange")

    def _save(self):
        filepath = self._get_filepath()
        if not filepath:
            return
        outline_file = os.path.join(filepath, "Novel_directory.txt")
        with open(outline_file, "w", encoding="utf-8") as f:
            f.write(self.textbox.get("1.0", "end-1c"))
        self.status_label.configure(text="已保存", text_color="green")

    def _regenerate(self):
        self.progress.set(0.1)
        self.status_label.configure(text="正在重新生成大纲...", text_color="gray60")

        def do_gen():
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from novel_generator.blueprint import Chapter_blueprint_generate

                config = self.master.get_config()
                params = config.get("other_params", {})
                llm = _get_llm(config)
                filepath = params.get("filepath", "")

                Chapter_blueprint_generate(
                    interface_format=llm.get("interface_format", "mimo"),
                    api_key=llm.get("api_key", ""),
                    base_url=llm.get("base_url", ""),
                    llm_model=llm.get("model_name", "mimo-v2.5-pro"),
                    filepath=filepath,
                    number_of_chapters=params.get("num_chapters", 100),
                    user_guidance=params.get("user_guidance", ""),
                    temperature=llm.get("temperature", 0.7),
                    max_tokens=llm.get("max_tokens", 8192),
                    timeout=llm.get("timeout", 600),
                )

                self.after(0, self._on_done)
            except Exception as e:
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=do_gen, daemon=True).start()

    def _on_done(self):
        self.progress.set(1.0)
        self.status_label.configure(text="✅ 大纲生成完成", text_color="green")
        self._reload()

    def _on_error(self, err):
        self.progress.set(0)
        self.status_label.configure(text=f"❌ {err[:50]}", text_color="red")

    def tkraise(self, *args):
        super().tkraise(*args)
        self._reload()
