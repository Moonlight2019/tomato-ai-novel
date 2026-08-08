# gui/pages/export_page.py
# -*- coding: utf-8 -*-
"""
导出页 — 导出小说为番茄投稿格式
"""
import os
import threading
import customtkinter as ctk


class ExportPage(ctk.CTkFrame):
    """导出页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self._create_header()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        ctk.CTkLabel(header, text="📦 导出小说", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="导出为番茄小说可上传的格式", font=ctk.CTkFont(size=13), text_color="gray60").pack(side="left", padx=15)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)

        # 统计信息
        self.stats_frame = ctk.CTkFrame(content)
        self.stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.stats_label = ctk.CTkLabel(self.stats_frame, text="请先打开一个项目",
                                        font=ctk.CTkFont(size=14))
        self.stats_label.pack(padx=20, pady=15)

        # 导出选项
        options_frame = ctk.CTkFrame(content)
        options_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(options_frame, text="导出格式", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        # 合并TXT
        opt1 = ctk.CTkFrame(options_frame, fg_color="transparent")
        opt1.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(opt1, text="📄 合并TXT", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(opt1, text="所有章节合并为一个TXT文件，适合直接复制粘贴到番茄后台",
                    font=ctk.CTkFont(size=12), text_color="gray60").pack(side="left", padx=20)
        ctk.CTkButton(opt1, text="导出", width=80, command=self._export_merged).pack(side="right")

        # 分章TXT
        opt2 = ctk.CTkFrame(options_frame, fg_color="transparent")
        opt2.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkLabel(opt2, text="📑 分章TXT", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkLabel(opt2, text="每章单独一个TXT文件，适合番茄分章上传",
                    font=ctk.CTkFont(size=12), text_color="gray60").pack(side="left", padx=20)
        ctk.CTkButton(opt2, text="导出", width=80, command=self._export_chapters).pack(side="right")

        # 状态
        self.status_label = ctk.CTkLabel(content, text="", text_color="gray60")
        self.status_label.grid(row=2, column=0, sticky="w")

        # 输出路径
        self.path_label = ctk.CTkLabel(content, text="", text_color="gray60", font=ctk.CTkFont(size=12))
        self.path_label.grid(row=3, column=0, sticky="w", pady=5)

    def _get_project(self):
        config = self.master.get_config()
        params = config.get("other_params", {})
        topic = params.get("topic", "")
        filepath = params.get("filepath", "")
        if not filepath:
            base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects")
            filepath = os.path.join(base, topic)
        return filepath, topic

    def _update_stats(self):
        filepath, topic = self._get_project()
        if not topic or not os.path.exists(filepath):
            self.stats_label.configure(text="请先在「创意输入」或「书架」中打开一个项目")
            return
        from export import get_export_stats
        stats = get_export_stats(filepath)
        self.stats_label.configure(
            text=f"📖 《{topic}》 | 已生成 {stats['count']} 章 | 总字数 {stats['total_words']:,}"
        )

    def _export_merged(self):
        filepath, topic = self._get_project()
        if not topic:
            self.status_label.configure(text="❌ 请先打开项目", text_color="red")
            return
        self.status_label.configure(text="导出中...", text_color="gray60")

        def do_export():
            try:
                from export import export_fanqie_txt
                out = export_fanqie_txt(filepath, book_name=topic)
                self.after(0, lambda: self._on_done(out))
            except Exception as e:
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=do_export, daemon=True).start()

    def _export_chapters(self):
        filepath, topic = self._get_project()
        if not topic:
            self.status_label.configure(text="❌ 请先打开项目", text_color="red")
            return
        self.status_label.configure(text="导出中...", text_color="gray60")

        def do_export():
            try:
                from export import export_chapters_txt
                out = export_chapters_txt(filepath, book_name=topic)
                self.after(0, lambda: self._on_done(out))
            except Exception as e:
                self.after(0, lambda m=str(e): self._on_error(m))

        threading.Thread(target=do_export, daemon=True).start()

    def _on_done(self, path):
        self.status_label.configure(text="✅ 导出完成！", text_color="green")
        self.path_label.configure(text=f"输出路径: {path}")

    def _on_error(self, err):
        self.status_label.configure(text=f"❌ {err}", text_color="red")

    def tkraise(self, *args):
        super().tkraise(*args)
        self._update_stats()
