# gui/pages/creative.py
# -*- coding: utf-8 -*-
"""
创意输入页 — 输入想法/摘要/开头，生成架构
"""
import os
import json
import threading
import customtkinter as ctk
from gui.animations import LoadingSpinner, pulse_widget


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


def _get_llm(config, task_key="architecture_llm"):
    """获取LLM配置"""
    return _get_llm_for_task(config, task_key)


class CreativePage(ctk.CTkFrame):
    """创意输入页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 标题区
        self._create_header()

        # 内容区
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        ctk.CTkLabel(
            header, text="📝 创意输入",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="输入你的想法、摘要或开头，AI帮你构建完整小说",
            font=ctk.CTkFont(size=13), text_color="gray60"
        ).pack(side="left", padx=15)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        # 历史记录栏
        history_frame = ctk.CTkFrame(content, fg_color="transparent")
        history_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        ctk.CTkLabel(history_frame, text="📜 历史创意:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.history_var = ctk.StringVar(value="")
        self.history_menu = ctk.CTkOptionMenu(history_frame, variable=self.history_var,
                                              values=[""], width=300, command=self._load_history)
        self.history_menu.pack(side="left", padx=5)
        ctk.CTkButton(history_frame, text="🔄", width=30, command=self._refresh_history).pack(side="left")
        ctk.CTkButton(history_frame, text="🗑 删除选中", width=80, command=self._delete_history).pack(side="left", padx=5)

        # 参数区
        params_frame = ctk.CTkFrame(content)
        params_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # 使用grid布局避免堆叠
        params_frame.grid_columnconfigure(1, weight=1)
        params_frame.grid_columnconfigure(3, weight=1)

        # 书名
        ctk.CTkLabel(params_frame, text="书名:").grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        self.title_var = ctk.StringVar(value="都市逆袭")
        ctk.CTkEntry(params_frame, textvariable=self.title_var, width=250).grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        # 类型
        ctk.CTkLabel(params_frame, text="类型:").grid(row=0, column=2, padx=(15, 5), pady=8, sticky="w")
        self.genre_var = ctk.StringVar(value="都市")
        self.genre_menu = ctk.CTkOptionMenu(
            params_frame, variable=self.genre_var,
            values=[
                "都市", "都市重生", "都市系统", "都市商战",
                "校园", "校园言情", "校园悬疑",
                "玄幻", "玄幻重生", "仙侠",
                "悬疑", "悬疑推理", "悬疑惊悚",
                "言情", "言情虐恋", "言情甜宠", "古言",
                "科幻", "末世", "游戏",
                "历史", "架空历史", "年代",
                "职场", "官场", "军事",
                "无限流", "系统流", "穿越",
            ],
            width=120
        )
        self.genre_menu.grid(row=0, column=3, padx=5, pady=8, sticky="w")

        # 章数 + 字数
        ctk.CTkLabel(params_frame, text="章数:").grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        self.chapters_var = ctk.StringVar(value="100")
        ctk.CTkEntry(params_frame, textvariable=self.chapters_var, width=80).grid(row=1, column=1, padx=5, pady=8, sticky="w")

        ctk.CTkLabel(params_frame, text="每章字数:").grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")
        self.wordcount_var = ctk.StringVar(value="3000")
        ctk.CTkEntry(params_frame, textvariable=self.wordcount_var, width=80).grid(row=1, column=3, padx=5, pady=8, sticky="w")

        # 文本输入区
        self.input_text = ctk.CTkTextbox(content, font=ctk.CTkFont(size=14))
        self.input_text.grid(row=2, column=0, sticky="nsew")
        self.input_text.insert("1.0",
            "在此输入你的创意、想法、摘要或小说开头...\n\n"
            "示例：\n"
            "一个35岁的中年男人被公司裁员，妻子提出离婚，父母重病住院。\n"
            "在他人生最低谷的时候，一个神秘的商业系统激活了...\n\n"
            "写作要求：\n"
            "1. 前3章完成惨→翻盘循环\n"
            "2. 每5章一个小高潮\n"
            "3. 对话口语化，避免AI味"
        )

        # 按钮区
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        self.suggest_btn = ctk.CTkButton(
            btn_frame, text="💡 AI创意建议", font=ctk.CTkFont(size=13),
            height=35, corner_radius=8, width=120,
            command=self._suggest_ideas
        )
        self.suggest_btn.pack(side="left")

        self.generate_btn = ctk.CTkButton(
            btn_frame, text="🚀 生成架构", font=ctk.CTkFont(size=15, weight="bold"),
            height=45, corner_radius=10,
            command=self._on_generate
        )
        self.generate_btn.pack(side="left", padx=10)

        self.synopsis_btn = ctk.CTkButton(
            btn_frame, text="📝 生成简介", font=ctk.CTkFont(size=13),
            height=35, corner_radius=8, width=100,
            command=self._generate_synopsis
        )
        self.synopsis_btn.pack(side="left", padx=5)

        self.progress = ctk.CTkProgressBar(btn_frame, width=200)
        self.progress.pack(side="left", padx=10)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(btn_frame, text="", text_color="gray60")
        self.status_label.pack(side="left")

        # 简介显示区
        synopsis_frame = ctk.CTkFrame(content)
        synopsis_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        ctk.CTkLabel(synopsis_frame, text="📖 小说简介", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.synopsis_text = ctk.CTkTextbox(synopsis_frame, height=120, font=ctk.CTkFont(size=13))
        self.synopsis_text.pack(fill="x", padx=10, pady=(0, 10))
        self.synopsis_text.insert("1.0", "点击「生成简介」按钮，AI将根据架构内容生成番茄小说简介...")
        self.synopsis_text.configure(state="disabled")

        # 初始化历史
        self.creatives_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "creatives.json")
        self._refresh_history()

    def _load_creatives(self) -> list:
        if os.path.exists(self.creatives_path):
            with open(self.creatives_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_creatives(self, data):
        os.makedirs(os.path.dirname(self.creatives_path), exist_ok=True)
        with open(self.creatives_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _refresh_history(self):
        import time
        creatives = self._load_creatives()
        labels = [f"[{c.get('time', '')[:10]}] {c.get('title', '未命名')}" for c in creatives]
        labels = [""] + labels
        self.history_menu.configure(values=labels if labels else [""])

    def _load_history(self, value):
        if not value:
            return
        creatives = self._load_creatives()
        idx = 0
        for i, label in enumerate([f"[{c.get('time', '')[:10]}] {c.get('title', '未命名')}" for c in creatives]):
            if label == value:
                idx = i
                break
        if idx < len(creatives):
            c = creatives[idx]
            self.title_var.set(c.get("title", ""))
            self.genre_var.set(c.get("genre", "都市"))
            self.chapters_var.set(str(c.get("chapters", 100)))
            self.wordcount_var.set(str(c.get("wordcount", 3000)))
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", c.get("text", ""))

    def _delete_history(self):
        """删除选中的历史创意"""
        value = self.history_var.get()
        if not value:
            return
        creatives = self._load_creatives()
        labels = [f"[{c.get('time', '')[:10]}] {c.get('title', '未命名')}" for c in creatives]
        if value in labels:
            idx = labels.index(value)
            creatives.pop(idx)
            self._save_creatives(creatives)
            self._refresh_history()
            self.history_var.set("")

    def _save_to_history(self, title, genre, chapters, wordcount, text):
        import time
        creatives = self._load_creatives()
        creatives.insert(0, {
            "title": title, "genre": genre, "chapters": chapters,
            "wordcount": wordcount, "text": text,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        # 只保留最近50条
        self._save_creatives(creatives[:50])
        self._refresh_history()

    def _generate_synopsis(self):
        """生成番茄小说简介"""
        filepath = self._get_filepath()
        if not filepath:
            self.status_label.configure(text="请先生成架构", text_color="red")
            return

        # 读取架构文件
        arch_file = os.path.join(filepath, "Novel_architecture.txt")
        if not os.path.exists(arch_file):
            self.status_label.configure(text="请先生成架构", text_color="red")
            return

        with open(arch_file, "r", encoding="utf-8") as f:
            architecture = f.read()

        topic = self.title_var.get().strip()
        genre = self.genre_var.get()

        self.synopsis_btn.configure(state="disabled", text="生成中...")
        self.status_label.configure(text="正在生成简介...", text_color="gray60")

        def do_synopsis():
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
                    temperature=0.7,
                    max_tokens=500,
                    timeout=60
                )

                prompt = f"""你是一个番茄小说平台的资深编辑。请根据以下小说架构，生成一段适合番茄平台的小说简介。

书名：《{topic}》
类型：{genre}

小说架构：
{architecture[:3000]}

简介要求：
1. 字数控制在80-150字
2. 第一句话必须有钩子，吸引读者点击
3. 突出主角的困境和金手指/系统
4. 暗示爽点（逆袭、打脸、升级）
5. 不要剧透结局
6. 语言口语化，不要文绉绉
7. 番茄平台风格：直接、有悬念、有爽点

请直接输出简介文本，不要加任何解释。"""

                result = adapter.invoke(prompt)

                # 保存简介到文件
                synopsis_file = os.path.join(filepath, "synopsis.txt")
                with open(synopsis_file, "w", encoding="utf-8") as f:
                    f.write(result)

                self.after(0, lambda: self._on_synopsis_done(result))
            except Exception as e:
                err_msg = str(e)[:60]
                self.after(0, lambda m=err_msg: self.status_label.configure(text=f"❌ {m}", text_color="red"))
                self.after(0, lambda: self.synopsis_btn.configure(state="normal", text="📝 生成简介"))

        threading.Thread(target=do_synopsis, daemon=True).start()

    def _on_synopsis_done(self, synopsis):
        """简介生成完成"""
        self.synopsis_btn.configure(state="normal", text="📝 生成简介")
        self.synopsis_text.configure(state="normal")
        self.synopsis_text.delete("1.0", "end")
        self.synopsis_text.insert("1.0", synopsis)
        self.synopsis_text.configure(state="disabled")
        self.status_label.configure(text="✅ 简介生成完成", text_color="green")

    def _get_filepath(self):
        """获取当前项目路径"""
        config = self.master.get_config()
        topic = config.get("other_params", {}).get("topic", "")
        if not topic:
            return None
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects", topic)

    def _suggest_ideas(self):
        """AI 生成创意建议"""
        genre = self.genre_var.get()
        self.suggest_btn.configure(state="disabled", text="💡 生成中...")
        self.status_label.configure(text="AI正在生成创意建议...", text_color="gray60")
        # 脉冲效果
        pulse_widget(self.status_label, "#3B8ED0", "#2563EB", cycles=3)

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
                    temperature=0.9,  # 高一点更有创意
                    max_tokens=2000,
                    timeout=60
                )

                prompt = f"""你是一个网文创意策划专家。请为「{genre}」类型的小说生成5个创意建议。

每个创意包含：
1. 一句话核心设定（20字以内）
2. 简要描述（50-100字）

要求：
- 设定新颖，避免老套
- 有明确的爽点和冲突
- 适合番茄小说平台连载
- 每个创意之间有差异性

输出格式：
1. 【核心设定】描述
2. 【核心设定】描述
3. 【核心设定】描述
4. 【核心设定】描述
5. 【核心设定】描述"""

                result = adapter.invoke(prompt)
                self.after(0, lambda: self._show_suggestions(result))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {e}", text_color="red"))
                self.after(0, lambda: self.suggest_btn.configure(state="normal", text="💡 AI创意建议"))

        threading.Thread(target=do_suggest, daemon=True).start()

    def _show_suggestions(self, suggestions):
        """显示创意建议弹窗"""
        self.suggest_btn.configure(state="normal", text="💡 AI创意建议")
        self.status_label.configure(text="✅ 创意建议已生成", text_color="green")

        dialog = ctk.CTkToplevel(self)
        dialog.title("💡 AI 创意建议")
        dialog.geometry("600x500")
        dialog.transient(self.master)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="选择一个创意填入输入框", font=ctk.CTkFont(size=14)).pack(pady=10)

        textbox = ctk.CTkTextbox(dialog, font=ctk.CTkFont(size=13))
        textbox.pack(fill="both", expand=True, padx=15, pady=5)
        textbox.insert("1.0", suggestions)
        textbox.configure(state="disabled")

        def use_suggestion():
            # 获取选中的文本或全部
            try:
                selected = textbox.get("sel.first", "sel.last")
            except Exception:
                selected = textbox.get("1.0", "end-1c")
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", selected)
            dialog.destroy()

        def refresh():
            dialog.destroy()
            self._suggest_ideas()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="使用选中内容", command=use_suggestion, fg_color="#2563eb").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="🔄 换一批", command=refresh).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="关闭", command=dialog.destroy, fg_color="gray50").pack(side="left", padx=10)

    def _on_generate(self):
        """生成架构"""
        topic = self.title_var.get().strip()
        genre = self.genre_var.get()
        num_chapters = int(self.chapters_var.get())
        word_number = int(self.wordcount_var.get())
        user_guidance = self.input_text.get("1.0", "end-1c").strip()

        if not topic:
            self.status_label.configure(text="请输入书名", text_color="red")
            return

        # 保存到历史
        self._save_to_history(topic, genre, num_chapters, word_number, user_guidance)

        self.generate_btn.configure(state="disabled", text="生成中...")
        self.progress.set(0.1)
        self.status_label.configure(text="正在生成架构...", text_color="gray60")

        def do_generate():
            try:
                import sys, os
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from config_manager import load_config
                from novel_generator.architecture import Novel_architecture_generate

                config = self.master.get_config()
                params = config.get("other_params", {})
                params["topic"] = topic
                params["genre"] = genre
                params["num_chapters"] = num_chapters
                params["word_number"] = word_number
                params["user_guidance"] = user_guidance
                params["filepath"] = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "projects", topic
                )
                config["other_params"] = params
                self.master.save_config(config)

                llm = _get_llm(config)
                filepath = params["filepath"]
                os.makedirs(filepath, exist_ok=True)

                Novel_architecture_generate(
                    interface_format=llm.get("interface_format", "mimo"),
                    api_key=llm.get("api_key", ""),
                    base_url=llm.get("base_url", ""),
                    llm_model=llm.get("model_name", "mimo-v2.5-pro"),
                    topic=topic, genre=genre,
                    number_of_chapters=num_chapters,
                    word_number=word_number,
                    filepath=filepath,
                    user_guidance=user_guidance,
                    temperature=llm.get("temperature", 0.7),
                    max_tokens=llm.get("max_tokens", 8192),
                    timeout=llm.get("timeout", 600),
                )

                self.after(0, lambda: self._on_generate_done(topic))
            except Exception as e:
                self.after(0, lambda m=str(e): self._on_generate_error(m))

        threading.Thread(target=do_generate, daemon=True).start()

    def _on_generate_done(self, topic):
        self.generate_btn.configure(state="normal", text="🚀 生成架构")
        self.progress.set(0.9)
        self.status_label.configure(text="✅ 架构完成，正在生成大纲...", text_color="green")
        self.master.set_project(topic)
        self.master.set_status("架构完成，正在生成大纲...")

        # 自动继续生成章节目录
        threading.Thread(target=self._generate_blueprint, daemon=True).start()

    def _generate_blueprint(self):
        """架构完成后自动生成章节目录"""
        try:
            import sys, os
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

            self.after(0, self._on_blueprint_done)
        except Exception as e:
            self.after(0, lambda m=str(e): self._on_blueprint_error(m))

    def _on_blueprint_done(self):
        self.progress.set(1.0)
        self.status_label.configure(text="✅ 架构+大纲完成，正在生成简介...", text_color="green")
        self.master.set_status("架构和大纲生成完成")
        # 自动生成简介
        self._generate_synopsis()

    def _on_blueprint_error(self, err):
        self.progress.set(1.0)
        self.status_label.configure(text=f"⚠️ 架构完成，大纲生成失败: {err[:40]}", text_color="orange")

    def _on_generate_error(self, error):
        self.generate_btn.configure(state="normal", text="🚀 生成架构")
        self.progress.set(0)
        self.status_label.configure(text=f"❌ {error[:50]}", text_color="red")
