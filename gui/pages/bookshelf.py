# gui/pages/bookshelf.py
# -*- coding: utf-8 -*-
"""
书籍管理页 — 管理多个小说项目
"""
import os
import json
import time
import customtkinter as ctk


class BookshelfPage(ctk.CTkFrame):
    """书籍管理页"""

    REGISTRY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "books_registry.json")

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._create_header()
        self._create_content()
        self._load_books()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        ctk.CTkLabel(header, text="📚 我的书架", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="➕ 新建书籍", command=self._new_book, fg_color="#2563eb").pack(side="right")

    def _create_content(self):
        # 滚动容器
        self.scroll = ctk.CTkScrollableFrame(self, label_text="项目列表")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        self.scroll.grid_columnconfigure(0, weight=1)

    def _load_registry(self) -> dict:
        if os.path.exists(self.REGISTRY_PATH):
            with open(self.REGISTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"books": []}

    def _save_registry(self, data: dict):
        os.makedirs(os.path.dirname(self.REGISTRY_PATH), exist_ok=True)
        with open(self.REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_books(self):
        # 清空
        for w in self.scroll.winfo_children():
            w.destroy()

        self._scan_existing_projects()
        registry = self._load_registry()

        # 更新total_chapters
        config = self.master.get_config()
        current_topic = config.get("other_params", {}).get("topic", "")
        current_num = config.get("other_params", {}).get("num_chapters", 100)

        updated = False
        for book in registry.get("books", []):
            # 如果是当前打开的项目，更新total_chapters
            if book["name"] == current_topic and current_num and current_num > 0:
                if book.get("total_chapters", 0) != current_num:
                    book["total_chapters"] = current_num
                    updated = True
            # 如果total_chapters为0，设置默认值
            if not book.get("total_chapters") or book["total_chapters"] < 1:
                book["total_chapters"] = 100
                updated = True

        if updated:
            self._save_registry(registry)

        if not registry.get("books"):
            ctk.CTkLabel(self.scroll, text="还没有书籍，点击右上角「新建书籍」开始",
                        font=ctk.CTkFont(size=14), text_color="gray60").grid(row=0, column=0, pady=50)
            return

        for i, book in enumerate(registry["books"]):
            self._create_book_card(i, book)

    def _create_book_card(self, index, book):
        card = ctk.CTkFrame(self.scroll)
        card.grid(row=index, column=0, sticky="ew", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)

        # 左侧图标
        icon_label = ctk.CTkLabel(card, text="📖", font=ctk.CTkFont(size=28))
        icon_label.grid(row=0, column=0, rowspan=2, padx=15, pady=10)

        # 中间信息
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=(10, 0))

        title_label = ctk.CTkLabel(info_frame, text=book.get("name", "未命名"),
                                   font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        title_label.pack(side="left")

        genre_label = ctk.CTkLabel(info_frame, text=f"[{book.get('genre', '未分类')}]",
                                   font=ctk.CTkFont(size=12), text_color="gray60")
        genre_label.pack(side="left", padx=10)

        # 进度信息
        progress_frame = ctk.CTkFrame(card, fg_color="transparent")
        progress_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10))

        chapters = book.get("chapters_generated", 0)
        total = book.get("total_chapters", 0)
        progress_text = f"已生成 {chapters}/{total} 章" if total > 0 else "未开始"
        ctk.CTkLabel(progress_frame, text=progress_text, font=ctk.CTkFont(size=12), text_color="gray60").pack(side="left")

        if total > 0:
            progress_bar = ctk.CTkProgressBar(progress_frame, width=150, height=12)
            progress_bar.pack(side="left", padx=10)
            progress_bar.set(chapters / total if total > 0 else 0)

        created = book.get("created", "")[:10]
        ctk.CTkLabel(progress_frame, text=f"创建: {created}", font=ctk.CTkFont(size=11), text_color="gray50").pack(side="right")

        # 右侧按钮
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=2, padx=15, pady=10)

        ctk.CTkButton(btn_frame, text="打开", width=70, height=30,
                      command=lambda: self._open_book(book)).pack(pady=2)
        ctk.CTkButton(btn_frame, text="编辑", width=70, height=30,
                      command=lambda: self._edit_book(book)).pack(pady=2)
        ctk.CTkButton(btn_frame, text="删除", width=70, height=30,
                      fg_color="#dc2626", hover_color="#b91c1c",
                      command=lambda: self._delete_book(book)).pack(pady=2)

    def _new_book(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("新建书籍")
        dialog.geometry("450x400")
        dialog.transient(self.master)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="新建书籍", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="x", padx=30)

        ctk.CTkLabel(form, text="书名:").pack(anchor="w")
        name_entry = ctk.CTkEntry(form, width=350)
        name_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="类型:").pack(anchor="w")
        genre_var = ctk.StringVar(value="都市")
        genre_menu = ctk.CTkOptionMenu(form, variable=genre_var, values=[
            "都市", "校园", "玄幻", "仙侠", "悬疑", "言情", "科幻", "历史", "职场", "系统流", "无限流", "穿越"
        ], width=350)
        genre_menu.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="总章数:").pack(anchor="w")
        chapters_entry = ctk.CTkEntry(form, width=350)
        chapters_entry.insert(0, "100")
        chapters_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="简介:").pack(anchor="w")
        desc_text = ctk.CTkTextbox(form, height=80, width=350)
        desc_text.pack(fill="x", pady=(0, 15))

        def confirm():
            name = name_entry.get().strip()
            if not name:
                return
            genre = genre_var.get()
            try:
                total = int(chapters_entry.get())
            except Exception:
                total = 0
            if total < 1:
                total = 100
            desc = desc_text.get("1.0", "end-1c").strip()

            registry = self._load_registry()
            # 检查重名
            if any(b["name"] == name for b in registry.get("books", [])):
                name = f"{name}_{int(time.time())}"

            book = {
                "name": name,
                "genre": genre,
                "total_chapters": total,
                "chapters_generated": 0,
                "description": desc,
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "modified": time.strftime("%Y-%m-%d %H:%M:%S"),
                "filepath": os.path.join("projects", name),
            }
            registry.setdefault("books", []).append(book)
            self._save_registry(registry)

            # 创建项目目录
            base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects", name)
            os.makedirs(os.path.join(base, "chapters"), exist_ok=True)

            dialog.destroy()
            self._load_books()

        ctk.CTkButton(dialog, text="创建", command=confirm, fg_color="#2563eb").pack(pady=10)

    def _open_book(self, book):
        """打开书籍，切换到写作页面"""
        config = self.master.get_config()
        config.setdefault("other_params", {})
        config["other_params"]["topic"] = book["name"]
        config["other_params"]["genre"] = book.get("genre", "都市")
        config["other_params"]["num_chapters"] = book.get("total_chapters", 100)
        config["other_params"]["filepath"] = book.get("filepath", os.path.join("projects", book["name"]))
        self.master.save_config(config)
        self.master.set_project(book["name"])
        self.master._show_page("writing")

    def _edit_book(self, book):
        """编辑书籍信息"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"编辑 - {book['name']}")
        dialog.geometry("400x250")
        dialog.transient(self.master)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"编辑「{book['name']}」", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="x", padx=30)

        ctk.CTkLabel(form, text="总章数:").pack(anchor="w")
        chapters_entry = ctk.CTkEntry(form, width=350)
        chapters_entry.insert(0, str(book.get("total_chapters", 100)))
        chapters_entry.pack(fill="x", pady=(0, 15))

        def save():
            try:
                total = int(chapters_entry.get())
            except Exception:
                total = 100
            if total < 1:
                total = 100

            # 更新registry
            registry = self._load_registry()
            for b in registry.get("books", []):
                if b["name"] == book["name"]:
                    b["total_chapters"] = total
                    break
            self._save_registry(registry)

            # 如果是当前打开的项目，也更新config
            config = self.master.get_config()
            if config.get("other_params", {}).get("topic") == book["name"]:
                config["other_params"]["num_chapters"] = total
                self.master.save_config(config)

            dialog.destroy()
            self._load_books()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="取消", command=dialog.destroy, fg_color="gray50").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="保存", command=save, fg_color="#2563eb").pack(side="left", padx=10)

    def _delete_book(self, book):
        """删除书籍，可选是否删除本地文件"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("确认删除")
        dialog.geometry("400x200")
        dialog.transient(self.master)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"确定删除「{book['name']}」？",
                    font=ctk.CTkFont(size=14)).pack(pady=(20, 10))

        # 是否删除本地文件选项
        delete_files_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(dialog, text="同时删除本地项目文件（不可恢复）",
                       variable=delete_files_var).pack(pady=5)

        def confirm():
            registry = self._load_registry()
            registry["books"] = [b for b in registry.get("books", []) if b["name"] != book["name"]]
            self._save_registry(registry)

            # 如果勾选了删除本地文件
            if delete_files_var.get():
                import shutil
                filepath = book.get("filepath", "")
                if filepath:
                    abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), filepath)
                    if os.path.exists(abs_path):
                        shutil.rmtree(abs_path)

            dialog.destroy()
            self._load_books()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="取消", command=dialog.destroy, fg_color="gray50").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="删除", command=confirm, fg_color="#dc2626").pack(side="left", padx=10)

    def _scan_existing_projects(self):
        """扫描已有项目目录，自动注册"""
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "projects")
        if not os.path.exists(base):
            return
        registry = self._load_registry()
        existing_names = {b["name"] for b in registry.get("books", [])}

        # 读取当前config获取num_chapters
        config = self.master.get_config()
        current_topic = config.get("other_params", {}).get("topic", "")
        current_num = config.get("other_params", {}).get("num_chapters", 100)

        for name in os.listdir(base):
            proj_path = os.path.join(base, name)
            if os.path.isdir(proj_path) and name not in existing_names:
                chapters_dir = os.path.join(proj_path, "chapters")
                chapters = len([f for f in os.listdir(chapters_dir) if f.startswith("chapter_")]) if os.path.exists(chapters_dir) else 0

                # 尝试从config获取该书的num_chapters
                total = 100
                if name == current_topic:
                    total = current_num if current_num and current_num > 0 else 100

                registry.setdefault("books", []).append({
                    "name": name,
                    "genre": "未分类",
                    "total_chapters": total,
                    "chapters_generated": chapters,
                    "description": "",
                    "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "modified": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "filepath": os.path.join("projects", name),
                })
        self._save_registry(registry)

    def tkraise(self, *args):
        super().tkraise(*args)
        self._scan_existing_projects()
        self._load_books()
