# gui/pages/writing.py
# -*- coding: utf-8 -*-
"""
章节写作页 — 逐章生成、编辑、去AI味、定稿
"""
import os
import threading
import customtkinter as ctk
from gui.animations import AnimatedProgressBar, pulse_widget


def _get_llm_for_task(config, task_key):
    """根据任务名称获取对应的LLM配置
    task_key: architecture_llm, chapter_outline_llm, final_chapter_llm, consistency_review_llm
    """
    choose = config.get("choose_configs", {})
    model_name = choose.get(task_key, "")
    if model_name:
        llm = config.get("llm_configs", {}).get(model_name, {})
        if llm:
            return llm
    # 回退：找第一个可用的模型
    for name, cfg in config.get("llm_configs", {}).items():
        if cfg.get("api_key"):
            return cfg
    # 最后回退：返回第一个模型
    models = config.get("llm_configs", {})
    return list(models.values())[0] if models else {}


def _get_llm(config, task_key="final_chapter_llm"):
    """获取正文写作LLM（默认）"""
    return _get_llm_for_task(config, task_key)


def _get_llm_std(config):
    """获取一致性检查LLM"""
    return _get_llm_for_task(config, "consistency_review_llm")


class WritingPage(ctk.CTkFrame):
    """章节写作页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.current_chapter = 1
        self._create_header()
        self._create_toolbar()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 5))
        ctk.CTkLabel(header, text="📖 章节写作", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="逐章生成、编辑和优化", font=ctk.CTkFont(size=13), text_color="gray60").pack(side="left", padx=15)

    def _create_toolbar(self):
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 5))

        # 章节选择（可手动输入）
        ctk.CTkLabel(toolbar, text="章节:").pack(side="left", padx=(10, 5))
        self.chapter_var = ctk.StringVar(value="1")
        self.chapter_entry = ctk.CTkEntry(toolbar, textvariable=self.chapter_var, width=60)
        self.chapter_entry.pack(side="left", padx=2)
        self.chapter_entry.bind("<Return>", lambda e: self._on_chapter_select(self.chapter_var.get()))

        self.total_label = ctk.CTkLabel(toolbar, text="/ 100", text_color="gray60")
        self.total_label.pack(side="left", padx=5)

        # 批量章数设置
        ctk.CTkLabel(toolbar, text="批量:").pack(side="left", padx=(10, 2))
        self.batch_count_var = ctk.StringVar(value="10")
        ctk.CTkEntry(toolbar, textvariable=self.batch_count_var, width=40).pack(side="left", padx=2)
        ctk.CTkLabel(toolbar, text="章", text_color="gray60").pack(side="left")

        # 操作按钮
        ctk.CTkButton(toolbar, text="📝 生成本章", command=self._generate_chapter, width=100).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="✨ 去AI味", command=self._deslop_chapter, width=80).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="✅ 定稿", command=self._finalize_chapter, width=70).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="▶ 批量生成", command=self._batch_generate, width=90).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="⏸ 暂停", command=self._batch_pause, width=60).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="⏹ 取消", command=self._batch_cancel, width=60).pack(side="left", padx=2)

        # 字数统计
        self.wordcount_label = ctk.CTkLabel(toolbar, text="字数: 0", text_color="gray60")
        self.wordcount_label.pack(side="right", padx=10)

        # 进度（带动画）
        self.progress = AnimatedProgressBar(toolbar, width=120)
        self.progress.pack(side="right", padx=5)
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(toolbar, text="", text_color="gray60")
        self.status_label.pack(side="right", padx=5)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 10))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(content, font=ctk.CTkFont(size=14))
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.bind("<<Modified>>", self._on_text_modified)

    def _get_filepath(self):
        config = self.master.get_config()
        topic = config.get("other_params", {}).get("topic", "")
        if not topic:
            return None
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects", topic)

    def _get_total_chapters(self):
        """获取当前小说配置的总章数"""
        config = self.master.get_config()
        total = config.get("other_params", {}).get("num_chapters", 0)
        if not total or total < 1:
            total = 100
        return total

    def _update_chapter_list(self):
        filepath = self._get_filepath()
        if not filepath:
            return
        chapters_dir = os.path.join(filepath, "chapters")
        if not os.path.exists(chapters_dir):
            os.makedirs(chapters_dir, exist_ok=True)

        # 更新总章数显示
        total = self._get_total_chapters()
        self.total_label.configure(text=f"/ {total}")

        files = sorted([f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")])
        if files:
            nums = [f.replace("chapter_", "").replace(".txt", "") for f in files]
            # 更新下拉框（保留最近20个+当前）
            recent = nums[-20:] if len(nums) > 20 else nums
            if self.chapter_var.get() not in nums:
                self.chapter_var.set(nums[-1])

    def _load_chapter(self, chapter_num):
        filepath = self._get_filepath()
        if not filepath:
            return
        chapter_file = os.path.join(filepath, "chapters", f"chapter_{chapter_num}.txt")
        self.textbox.delete("1.0", "end")
        if os.path.exists(chapter_file):
            with open(chapter_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.textbox.insert("1.0", content)
            self.wordcount_label.configure(text=f"字数: {len(content)}")
        else:
            self.textbox.insert("1.0", f"第{chapter_num}章尚未生成。点击「生成本章」开始。")
            self.wordcount_label.configure(text="字数: 0")

    def _save_chapter(self, chapter_num):
        filepath = self._get_filepath()
        if not filepath:
            return
        chapters_dir = os.path.join(filepath, "chapters")
        os.makedirs(chapters_dir, exist_ok=True)
        chapter_file = os.path.join(chapters_dir, f"chapter_{chapter_num}.txt")
        content = self.textbox.get("1.0", "end-1c")
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(content)

    def _on_chapter_select(self, value=None):
        # 先保存当前章节
        if hasattr(self, 'current_chapter') and self.current_chapter:
            self._save_chapter(self.current_chapter)

        if value is None:
            value = self.chapter_var.get()
        try:
            chapter_num = int(value)
            # 限制在有效范围内
            total = self._get_total_chapters()
            if chapter_num < 1:
                chapter_num = 1
            elif chapter_num > total:
                chapter_num = total
            self.current_chapter = chapter_num
            self.chapter_var.set(str(chapter_num))
        except Exception:
            self.current_chapter = 1
        self._load_chapter(self.current_chapter)

    def _on_text_modified(self, event=None):
        content = self.textbox.get("1.0", "end-1c")
        self.wordcount_label.configure(text=f"字数: {len(content)}")

    def _generate_chapter(self):
        chapter_num = self.current_chapter
        self.progress.set_smooth(0.1)
        self.status_label.configure(text=f"正在生成第{chapter_num}章...", text_color="gray60")
        # 状态标签脉冲效果
        pulse_widget(self.status_label, "#3B8ED0", "#2563EB", cycles=2)

        # 先保存当前编辑
        self._save_chapter(chapter_num)

        # 使用绝对路径
        abs_filepath = self._get_filepath()

        def do_gen():
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from novel_generator.chapter import generate_chapter_draft

                config = self.master.get_config()
                params = config.get("other_params", {})
                llm = _get_llm(config)
                embed = config.get("embedding_configs", {}).get("Qwen-Embedding", {})
                filepath = abs_filepath

                # 注入与题材匹配的增强版 prompt
                from enhanced_prompts import patch_prompt_definitions
                patch_prompt_definitions(params.get("genre", "") or "都市")

                chapter_text = generate_chapter_draft(
                    api_key=llm.get("api_key", ""),
                    base_url=llm.get("base_url", ""),
                    model_name=llm.get("model_name", "mimo-v2.5-pro"),
                    filepath=filepath,
                    novel_number=chapter_num,
                    word_number=params.get("word_number", 3000),
                    temperature=llm.get("temperature", 0.7),
                    user_guidance=params.get("user_guidance", ""),
                    characters_involved=params.get("characters_involved", ""),
                    key_items=params.get("key_items", ""),
                    scene_location=params.get("scene_location", ""),
                    time_constraint=params.get("time_constraint", ""),
                    embedding_api_key=embed.get("api_key", ""),
                    embedding_url=embed.get("base_url", ""),
                    embedding_interface_format=embed.get("interface_format", "qwen"),
                    embedding_model_name=embed.get("model_name", "text-embedding-v3"),
                    interface_format=llm.get("interface_format", "mimo"),
                    max_tokens=llm.get("max_tokens", 8192),
                    timeout=llm.get("timeout", 600),
                )

                self.after(0, lambda: self._on_gen_done(chapter_num, chapter_text))
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda m=err_msg: self._on_gen_error(m))

        threading.Thread(target=do_gen, daemon=True).start()

    def _on_gen_done(self, chapter_num, text):
        self.progress.set_smooth(1.0)
        self.status_label.configure(text=f"✅ 第{chapter_num}章生成完成", text_color="green")
        # 完成时绿色脉冲
        pulse_widget(self.status_label, "#22C55E", "#16A34A", cycles=2)
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.wordcount_label.configure(text=f"字数: {len(text)}")
        self._save_chapter(chapter_num)
        self._update_chapter_list()

    def _on_gen_error(self, err):
        self.progress.set(0)
        self.status_label.configure(text=f"❌ {err[:60]}", text_color="red")

    def _deslop_chapter(self):
        content = self.textbox.get("1.0", "end-1c")
        if not content.strip():
            return
        self.status_label.configure(text="去AI味中...", text_color="gray60")

        def do_deslop():
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from quality.deslop.deslop_engine import deslop_text
                result = deslop_text(content)
                self.after(0, lambda: self._on_deslop_done(result))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {e}", text_color="red"))

        threading.Thread(target=do_deslop, daemon=True).start()

    def _on_deslop_done(self, result):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", result["text"])
        self.wordcount_label.configure(text=f"字数: {len(result['text'])}")
        self._save_chapter(self.current_chapter)
        self.status_label.configure(
            text=f"✅ 去AI味完成 | 等级:{result['severity']} | 变更:{result['summary']['total_changes']}处",
            text_color="green"
        )

    def _finalize_chapter(self):
        chapter_num = self.current_chapter
        self._save_chapter(chapter_num)
        self.status_label.configure(text=f"定稿第{chapter_num}章...", text_color="gray60")

        # 使用绝对路径
        abs_filepath = self._get_filepath()

        def do_finalize():
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from novel_generator.finalization import finalize_chapter

                config = self.master.get_config()
                params = config.get("other_params", {})
                llm = config["llm_configs"].get("mimo-standard", {})
                embed = config.get("embedding_configs", {}).get("Qwen-Embedding", {})
                filepath = abs_filepath

                # 注入与题材匹配的增强版 prompt
                from enhanced_prompts import patch_prompt_definitions
                patch_prompt_definitions(params.get("genre", "") or "都市")

                finalize_chapter(
                    novel_number=chapter_num,
                    word_number=params.get("word_number", 3000),
                    api_key=llm.get("api_key", ""),
                    base_url=llm.get("base_url", ""),
                    model_name=llm.get("model_name", "mimo-v2.5"),
                    temperature=llm.get("temperature", 0.7),
                    filepath=filepath,
                    embedding_api_key=embed.get("api_key", ""),
                    embedding_url=embed.get("base_url", ""),
                    embedding_interface_format=embed.get("interface_format", "qwen"),
                    embedding_model_name=embed.get("model_name", "text-embedding-v3"),
                    interface_format=llm.get("interface_format", "mimo"),
                    max_tokens=llm.get("max_tokens", 8192),
                    timeout=llm.get("timeout", 600),
                )

                self.after(0, lambda: self.status_label.configure(text=f"✅ 第{chapter_num}章定稿完成", text_color="green"))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {e}", text_color="red"))

        threading.Thread(target=do_finalize, daemon=True).start()

    def _batch_generate(self):
        """批量生成多章（支持断点续传）"""
        # 先保存当前编辑
        if hasattr(self, 'current_chapter') and self.current_chapter:
            self._save_chapter(self.current_chapter)

        filepath = self._get_filepath()
        if not filepath:
            self.status_label.configure(text="❌ 请先创建项目", text_color="red")
            return

        # 检查已有章节，确定起始位置
        chapters_dir = os.path.join(filepath, "chapters")
        os.makedirs(chapters_dir, exist_ok=True)
        existing = [f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")]
        existing_nums = sorted([int(f.replace("chapter_", "").replace(".txt", "")) for f in existing])

        # 检查断点文件
        checkpoint_file = os.path.join(filepath, "batch_progress.json")
        start_ch = existing_nums[-1] + 1 if existing_nums else 1

        if os.path.exists(checkpoint_file):
            import json
            with open(checkpoint_file, "r") as f:
                cp = json.load(f)
            last = cp.get("last_completed", 0)
            if last >= start_ch:
                start_ch = last + 1

        if start_ch > 1:
            # 弹窗询问续传方式
            current_ch = self.current_chapter  # 用户当前选中的章节
            dialog = ctk.CTkToplevel(self)
            dialog.title("批量生成")
            dialog.geometry("450x200")
            dialog.transient(self.master)
            dialog.grab_set()
            ctk.CTkLabel(dialog, text=f"已生成到第{start_ch - 1}章\n选择从哪里开始批量生成：",
                       font=ctk.CTkFont(size=14)).pack(pady=20)
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(pady=10)
            result = {"choice": "cancel"}
            def from_current():
                result["choice"] = "current"
                dialog.destroy()
            def from_resume():
                result["choice"] = "resume"
                dialog.destroy()
            ctk.CTkButton(btn_frame, text=f"从当前章节(第{current_ch}章)开始", command=from_current).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text=f"从第{start_ch}章继续", command=from_resume, fg_color="#2563eb").pack(side="left", padx=10)
            dialog.wait_window()
            if result["choice"] == "cancel":
                return
            elif result["choice"] == "current":
                start_ch = current_ch

        config = self.master.get_config()
        total = config.get("other_params", {}).get("num_chapters", 0)
        if not total or total < 1:
            total = 100
            # 同时修复配置文件
            config.setdefault("other_params", {})["num_chapters"] = 100
            self.master.save_config(config)
        try:
            batch_count = int(self.batch_count_var.get())
        except Exception:
            batch_count = 10
        if batch_count < 1:
            batch_count = 10
        end_ch = min(start_ch + batch_count, total + 1)

        # 确保 end_ch > start_ch
        if end_ch <= start_ch:
            end_ch = start_ch + 1

        # 初始化暂停/取消标志
        self._batch_paused = False
        self._batch_cancelled = False

        msg = f"批量生成中... (第{start_ch}-{end_ch-1}章，共{end_ch-start_ch}章)"
        self.status_label.configure(text=msg, text_color="gray60")
        self.progress.set_smooth(0)
        # 状态标签脉冲效果
        pulse_widget(self.status_label, "#3B8ED0", "#2563EB", cycles=3)

        def do_batch():
            try:
                import sys, json, time as _time
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from novel_generator.chapter import generate_chapter_draft
                from novel_generator.finalization import finalize_chapter

                params = config.get("other_params", {})
                llm = _get_llm(config)
                llm_std = _get_llm_std(config)
                embed = config.get("embedding_configs", {}).get("Qwen-Embedding", {})
                # 使用绝对路径
                fp = filepath
                # 注入与题材匹配的增强版 prompt
                from enhanced_prompts import patch_prompt_definitions
                patch_prompt_definitions(params.get("genre", "") or "都市")
                batch_cfg = config.get("batch_settings", {})
                delay = batch_cfg.get("delay_between_chapters", 2)
                max_retries = batch_cfg.get("max_retries", 3)

                for ch in range(start_ch, end_ch):
                    # 检查取消
                    if self._batch_cancelled:
                        self.after(0, lambda: self.status_label.configure(text="⚠️ 已取消", text_color="orange"))
                        return

                    # 检查暂停
                    while self._batch_paused and not self._batch_cancelled:
                        self.after(0, lambda: self.status_label.configure(text="⏸ 已暂停，点击继续", text_color="yellow"))
                        _time.sleep(1)

                    self.after(0, lambda c=ch: self.progress.set_smooth((c - start_ch) / (end_ch - start_ch)))
                    self.after(0, lambda c=ch: self.status_label.configure(text=f"生成第{c}/{total}章..."))

                    # 带重试的生成
                    success = False
                    for retry in range(max_retries):
                        try:
                            generate_chapter_draft(
                                api_key=llm.get("api_key", ""),
                                base_url=llm.get("base_url", ""),
                                model_name=llm.get("model_name", "mimo-v2.5-pro"),
                                filepath=fp, novel_number=ch,
                                word_number=params.get("word_number", 3000),
                                temperature=llm.get("temperature", 0.7),
                                user_guidance=params.get("user_guidance", ""),
                                characters_involved=params.get("characters_involved", ""),
                                key_items=params.get("key_items", ""),
                                scene_location=params.get("scene_location", ""),
                                time_constraint=params.get("time_constraint", ""),
                                embedding_api_key=embed.get("api_key", ""),
                                embedding_url=embed.get("base_url", ""),
                                embedding_interface_format=embed.get("interface_format", "qwen"),
                                embedding_model_name=embed.get("model_name", "text-embedding-v3"),
                                interface_format=llm.get("interface_format", "mimo"),
                                max_tokens=llm.get("max_tokens", 8192),
                                timeout=llm.get("timeout", 600),
                            )
                            success = True
                            break
                        except Exception as e:
                            if retry < max_retries - 1:
                                _time.sleep(5 * (retry + 1))  # 指数退避
                            else:
                                raise

                    # 定稿
                    finalize_chapter(
                        novel_number=ch, word_number=params.get("word_number", 3000),
                        api_key=llm_std.get("api_key", ""),
                        base_url=llm_std.get("base_url", ""),
                        model_name=llm_std.get("model_name", "mimo-v2.5"),
                        temperature=llm_std.get("temperature", 0.7),
                        filepath=fp,
                        embedding_api_key=embed.get("api_key", ""),
                        embedding_url=embed.get("base_url", ""),
                        embedding_interface_format=embed.get("interface_format", "qwen"),
                        embedding_model_name=embed.get("model_name", "text-embedding-v3"),
                        interface_format=llm_std.get("interface_format", "mimo"),
                        max_tokens=llm_std.get("max_tokens", 8192),
                        timeout=llm_std.get("timeout", 600),
                    )

                    # 保存断点
                    with open(checkpoint_file, "w") as f:
                        json.dump({"last_completed": ch, "timestamp": _time.strftime("%Y-%m-%d %H:%M:%S")}, f)

                    if delay > 0:
                        _time.sleep(delay)

                # 完成，删除断点文件
                if os.path.exists(checkpoint_file):
                    os.remove(checkpoint_file)

                self.after(0, lambda: self._on_batch_done(start_ch, end_ch - 1))
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda m=err_msg: self._on_gen_error(m))

        threading.Thread(target=do_batch, daemon=True).start()

    def _batch_pause(self):
        """暂停/继续批量生成"""
        if hasattr(self, '_batch_paused'):
            self._batch_paused = not self._batch_paused

    def _batch_cancel(self):
        """取消批量生成"""
        if hasattr(self, '_batch_cancelled'):
            self._batch_cancelled = True

    def _on_batch_done(self, start, end):
        self.progress.set_smooth(1.0)
        self.status_label.configure(text=f"✅ 批量完成：第{start}-{end}章", text_color="green")
        # 完成时绿色脉冲
        pulse_widget(self.status_label, "#22C55E", "#16A34A", cycles=3)
        self._update_chapter_list()

    def tkraise(self, *args):
        super().tkraise(*args)
        self._update_chapter_list()
        self._load_chapter(self.current_chapter)
