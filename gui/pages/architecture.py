# gui/pages/architecture.py
# -*- coding: utf-8 -*-
"""
架构预览页 — 查看和编辑生成的小说架构
"""
import os
import customtkinter as ctk


class ArchitecturePage(ctk.CTkFrame):
    """架构预览页"""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_content()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        ctk.CTkLabel(header, text="📋 架构预览", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(header, text="查看和编辑AI生成的小说架构", font=ctk.CTkFont(size=13), text_color="gray60").pack(side="left", padx=15)

    def _create_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # 文本编辑区
        self.textbox = ctk.CTkTextbox(content, font=ctk.CTkFont(size=13))
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.insert("1.0", "尚未生成架构。请先在「创意输入」页生成。")

        # 按钮区
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        ctk.CTkButton(btn_frame, text="🔄 重新加载", command=self._reload).pack(side="left")
        ctk.CTkButton(btn_frame, text="💾 保存修改", command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="下一步 →", command=self._go_outline).pack(side="right")

        self.status_label = ctk.CTkLabel(btn_frame, text="", text_color="gray60")
        self.status_label.pack(side="left", padx=15)

    def _get_filepath(self):
        config = self.master.get_config()
        topic = config.get("other_params", {}).get("topic", "")
        if not topic:
            return None
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects", topic)

    def _reload(self):
        filepath = self._get_filepath()
        if not filepath:
            self.status_label.configure(text="请先创建项目", text_color="red")
            return
        arch_file = os.path.join(filepath, "Novel_architecture.txt")
        if os.path.exists(arch_file):
            with open(arch_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", content)
            self.status_label.configure(text="已加载", text_color="green")
        else:
            self.status_label.configure(text="架构文件不存在", text_color="red")

    def _save(self):
        filepath = self._get_filepath()
        if not filepath:
            return
        arch_file = os.path.join(filepath, "Novel_architecture.txt")
        content = self.textbox.get("1.0", "end-1c")
        with open(arch_file, "w", encoding="utf-8") as f:
            f.write(content)
        self.status_label.configure(text="已保存", text_color="green")

    def _go_outline(self):
        self.master._show_page("outline")

    def tkraise(self, *args):
        super().tkraise(*args)
        self._reload()
