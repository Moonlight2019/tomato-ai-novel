# gui/pages/deslop_page.py
# -*- coding: utf-8 -*-
"""
去AI味页 — 对比显示原文和处理后文本
"""
import os
import threading
import customtkinter as ctk


class DeslopPage(ctk.CTkFrame):
    """去AI味页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        ctk.CTkLabel(header, text="✨ 去AI味", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="粘贴文本进行去AI味处理，或处理指定章节", font=ctk.CTkFont(size=13), text_color="gray60").pack(side="left", padx=15)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # 工具栏
        toolbar = ctk.CTkFrame(content, fg_color="transparent")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(toolbar, text="章节:").pack(side="left")
        # 直达输入框：可输入任意章节号（回车加载），避免下拉随章节数无限变长
        self.chapter_entry_var = ctk.StringVar(value="")
        self.chapter_entry = ctk.CTkEntry(toolbar, textvariable=self.chapter_entry_var, width=52)
        self.chapter_entry.pack(side="left", padx=5)
        self.chapter_entry.bind("<Return>", lambda e: self._load_chapter())

        # 下拉：只放最近 N 章作快捷选择
        self.chapter_var = ctk.StringVar(value="")
        self.chapter_select = ctk.CTkOptionMenu(toolbar, variable=self.chapter_var, values=[""],
                                                width=90, command=self._on_chapter_pick)
        self.chapter_select.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(toolbar, text="(最近)", font=ctk.CTkFont(size=11), text_color="gray50").pack(side="left")

        ctk.CTkButton(toolbar, text="📂 加载章节", command=self._load_chapter, width=100).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="✨ 去AI味", command=self._run_deslop, width=100).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="💾 保存到章节", command=self._save_to_chapter, width=100).pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(toolbar, text="", text_color="gray60")
        self.status_label.pack(side="right", padx=10)

        # 左侧：原文
        left_frame = ctk.CTkFrame(content)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left_frame, text="原文", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=5)
        self.original_text = ctk.CTkTextbox(left_frame, font=ctk.CTkFont(size=13))
        self.original_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.original_text.insert("1.0", "在此粘贴文本，或从左侧加载章节...")

        # 右侧：处理后
        right_frame = ctk.CTkFrame(content)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.result_header = ctk.CTkLabel(right_frame, text="处理结果", font=ctk.CTkFont(size=14, weight="bold"))
        self.result_header.grid(row=0, column=0, padx=10, pady=5)
        self.result_text = ctk.CTkTextbox(right_frame, font=ctk.CTkFont(size=13))
        self.result_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

    def _get_filepath(self):
        config = self.master.get_config()
        topic = config.get("other_params", {}).get("topic", "")
        if not topic:
            return None
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects", topic)

    def _get_chapter_num(self):
        """取当前章节号：直达输入框优先，其次下拉。返回数字字符串或空。"""
        direct = self.chapter_entry_var.get().strip()
        ch = direct if direct else self.chapter_var.get()
        ch = (ch or "").strip()
        if not ch.isdigit():
            return ""
        return str(int(ch))

    def _on_chapter_pick(self, value):
        # 从下拉选择章节时，同步到直达输入框，保证读取源一致
        if value and value.isdigit():
            self.chapter_entry_var.set(str(int(value)))

    def _load_chapter(self):
        filepath = self._get_filepath()
        if not filepath:
            return
        ch = self._get_chapter_num()
        if not ch:
            self.status_label.configure(text="请输入有效章节号", text_color="red")
            return
        chapter_file = os.path.join(filepath, "chapters", f"chapter_{ch}.txt")
        if os.path.exists(chapter_file):
            with open(chapter_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.original_text.delete("1.0", "end")
            self.original_text.insert("1.0", content)
            self.status_label.configure(text=f"已加载第{ch}章", text_color="green")

    def _run_deslop(self):
        content = self.original_text.get("1.0", "end-1c")
        if not content.strip():
            return
        self.status_label.configure(text="处理中...", text_color="gray60")

        def do_deslop():
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "engine"))
                from quality.deslop.deslop_engine import deslop_text
                result = deslop_text(content)
                self.after(0, lambda: self._on_done(result))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"❌ {e}", text_color="red"))

        threading.Thread(target=do_deslop, daemon=True).start()

    def _on_done(self, result):
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", result["text"])
        self.result_header.configure(text=f"处理结果 | 等级:{result['severity']} | 变更:{result['summary']['total_changes']}处")
        self.status_label.configure(text="✅ 处理完成", text_color="green")

    def _save_to_chapter(self):
        filepath = self._get_filepath()
        if not filepath:
            return
        ch = self._get_chapter_num()
        if not ch:
            self.status_label.configure(text="请输入有效章节号", text_color="red")
            return
        content = self.result_text.get("1.0", "end-1c")
        if not content.strip():
            return
        chapter_file = os.path.join(filepath, "chapters", f"chapter_{ch}.txt")
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(content)
        self.status_label.configure(text=f"✅ 已保存到第{ch}章", text_color="green")

    def tkraise(self, *args):
        super().tkraise(*args)
        filepath = self._get_filepath()
        if filepath:
            chapters_dir = os.path.join(filepath, "chapters")
            if os.path.exists(chapters_dir):
                files = [f.replace("chapter_", "").replace(".txt", "") for f in os.listdir(chapters_dir) if f.startswith("chapter_")]
                # 按数字排序而不是字符串排序
                files = sorted(files, key=lambda x: int(x) if x.isdigit() else 0)
                if files:
                    # 下拉只保留最近 N 章，避免随章节数无限变长；老章节用直达输入框
                    recent = files[-50:]
                    self.chapter_select.configure(values=recent)
                    latest = files[-1]
                    self.chapter_var.set(latest)
                    if not self.chapter_entry_var.get().strip():
                        self.chapter_entry_var.set(latest)
