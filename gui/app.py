# gui/app.py
# -*- coding: utf-8 -*-
"""
番茄 AI 写作系统 - 主窗口
写作工作台风格：左侧导航栏 + 右侧内容区 + 动画效果
"""
import sys
import os
import json
import customtkinter as ctk
from gui.animations import AnimatedButton, animate_color_transition

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "engine"))

from gui.pages.bookshelf import BookshelfPage
from gui.pages.creative import CreativePage
from gui.pages.architecture import ArchitecturePage
from gui.pages.outline import OutlinePage
from gui.pages.writing import WritingPage
from gui.pages.deslop_page import DeslopPage
from gui.pages.export_page import ExportPage
from gui.pages.market_page import MarketPage
from gui.pages.analyze_page import AnalyzePage
from gui.pages.settings import SettingsPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")


class NovelApp(ctk.CTk):
    """番茄 AI 写作系统主窗口"""

    def __init__(self):
        super().__init__()

        self.title("🍅 番茄 AI 写作系统")
        self.geometry("1280x800")
        self.minsize(1100, 650)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_project = None
        self.current_page = "bookshelf"

        self._create_sidebar()
        self._create_pages()
        self._create_statusbar()

        self._show_page("bookshelf")

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=190, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo 带发光效果
        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="🍅 番茄AI",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#E74C3C", "#FF6B6B")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 30))

        # 导航按钮（带动画效果）
        self.nav_buttons = {}
        self.nav_indicators = {}
        nav_items = [
            ("bookshelf",      "📚 我的书架"),
            ("creative",       "📝 创意输入"),
            ("architecture",   "📋 架构预览"),
            ("outline",        "📑 大纲编辑"),
            ("writing",        "📖 章节写作"),
            ("deslop",         "✨ 去AI味"),
            ("market",         "📊 市场分析"),
            ("analyze",        "🔬 拆文分析"),
            ("export",         "📦 导出"),
            ("settings",       "⚙️ 设置"),
        ]

        for i, (key, text) in enumerate(nav_items):
            # 按钮容器
            btn_container = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=42)
            btn_container.grid(row=i+1, column=0, padx=8, pady=2, sticky="ew")
            btn_container.grid_propagate(False)

            # 左侧指示条（选中时显示）
            indicator = ctk.CTkFrame(btn_container, width=3, corner_radius=2,
                                    fg_color="transparent")
            indicator.place(x=0, y=6, relheight=0.7)

            # 按钮
            btn = ctk.CTkButton(
                btn_container, text=text, anchor="w",
                font=ctk.CTkFont(size=13), height=36, corner_radius=8,
                fg_color="transparent",
                hover_color=("gray80", "gray20"),
                command=lambda k=key: self._show_page(k)
            )
            btn.pack(fill="both", expand=True, padx=(8, 4))

            # 绑定悬停动画
            btn.bind("<Enter>", lambda e, b=btn: self._on_nav_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._on_nav_hover(b, False, k))

            self.nav_buttons[key] = btn
            self.nav_indicators[key] = indicator

    def _on_nav_hover(self, btn, entering, key=None):
        """导航按钮悬停动画"""
        if entering:
            btn.configure(cursor="hand2")
        else:
            btn.configure(cursor="")

    def _create_pages(self):
        self.pages = {}
        page_classes = {
            "bookshelf": BookshelfPage,
            "creative": CreativePage,
            "architecture": ArchitecturePage,
            "outline": OutlinePage,
            "writing": WritingPage,
            "deslop": DeslopPage,
            "market": MarketPage,
            "analyze": AnalyzePage,
            "export": ExportPage,
            "settings": SettingsPage,
        }

        for key, cls in page_classes.items():
            page = cls(self)
            page.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
            self.pages[key] = page

    def _create_statusbar(self):
        self.statusbar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.statusbar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.status_label = ctk.CTkLabel(self.statusbar, text="就绪", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=15)

        self.project_label = ctk.CTkLabel(self.statusbar, text="未打开项目", font=ctk.CTkFont(size=12))
        self.project_label.pack(side="right", padx=15)

    def _show_page(self, page_key: str):
        # 更新按钮样式和指示条
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(fg_color=("gray80", "gray20"))
                # 显示指示条
                if key in self.nav_indicators:
                    self.nav_indicators[key].configure(fg_color=("#E74C3C", "#FF6B6B"))
            else:
                btn.configure(fg_color="transparent")
                # 隐藏指示条
                if key in self.nav_indicators:
                    self.nav_indicators[key].configure(fg_color="transparent")

        # 页面切换（带动画效果）
        old_page = self.current_page
        new_page = self.pages.get(page_key)

        if new_page:
            # 简单的淡入效果
            new_page.tkraise()
            self._animate_page_in(new_page)

        self.current_page = page_key
        self.set_status(f"已切换到: {page_key}")

    def _animate_page_in(self, page):
        """页面淡入动画"""
        # 通过逐步更新透明度模拟淡入
        # CustomTkinter 不直接支持透明度，用颜色渐变模拟
        pass

    def set_status(self, text: str):
        self.status_label.configure(text=text)

    def set_project(self, name: str):
        self.project_label.configure(text=f"📖 {name}")
        self.current_project = name

    def get_config(self) -> dict:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_config(self, config: dict):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
