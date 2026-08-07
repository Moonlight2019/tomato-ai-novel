# export.py
# -*- coding: utf-8 -*-
"""
导出模块 — 将生成的小说导出为番茄小说可上传的格式
"""
import os
import re


def export_fanqie_txt(project_path: str, output_dir: str = None, book_name: str = None) -> str:
    """
    导出为番茄小说 TXT 格式（合并所有章节为一个文件）

    参数：
        project_path: 项目目录路径
        output_dir: 输出目录（默认 exports/{书名}/）
        book_name: 书名（默认从目录名取）

    返回：
        输出文件路径
    """
    if book_name is None:
        book_name = os.path.basename(project_path)
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(project_path), "exports", book_name)

    os.makedirs(output_dir, exist_ok=True)

    chapters_dir = os.path.join(project_path, "chapters")
    if not os.path.exists(chapters_dir):
        raise FileNotFoundError(f"章节目录不存在: {chapters_dir}")

    # 获取所有章节文件并排序
    chapter_files = sorted(
        [f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")],
        key=lambda x: int(re.search(r'chapter_(\d+)', x).group(1))
    )

    if not chapter_files:
        raise FileNotFoundError("没有找到章节文件")

    # 读取大纲获取章节标题
    outline_file = os.path.join(project_path, "Novel_directory.txt")
    chapter_titles = _parse_chapter_titles(outline_file)

    # 合并输出
    output_file = os.path.join(output_dir, f"{book_name}_番茄投稿.txt")
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"《{book_name}》\n\n")

        for i, cf in enumerate(chapter_files):
            chapter_num = int(re.search(r'chapter_(\d+)', cf).group(1))
            title = chapter_titles.get(chapter_num, f"第{chapter_num}章")

            # 章节标题
            out.write(f"第{chapter_num}章 {title}\n\n")

            # 章节内容
            with open(os.path.join(chapters_dir, cf), "r", encoding="utf-8") as f:
                content = f.read().strip()
            out.write(content)
            out.write("\n\n")

    return output_file


def export_chapters_txt(project_path: str, output_dir: str = None, book_name: str = None) -> str:
    """
    导出为每章单独的 TXT 文件（番茄分章上传格式）

    返回：
        输出目录路径
    """
    if book_name is None:
        book_name = os.path.basename(project_path)
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(project_path), "exports", book_name, "分章")

    os.makedirs(output_dir, exist_ok=True)

    chapters_dir = os.path.join(project_path, "chapters")
    chapter_files = sorted(
        [f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")],
        key=lambda x: int(re.search(r'chapter_(\d+)', x).group(1))
    )

    outline_file = os.path.join(project_path, "Novel_directory.txt")
    chapter_titles = _parse_chapter_titles(outline_file)

    for cf in chapter_files:
        chapter_num = int(re.search(r'chapter_(\d+)', cf).group(1))
        title = chapter_titles.get(chapter_num, f"第{chapter_num}章")

        with open(os.path.join(chapters_dir, cf), "r", encoding="utf-8") as f:
            content = f.read().strip()

        # 番茄格式：标题 + 内容
        out_file = os.path.join(output_dir, f"第{chapter_num:03d}章_{title}.txt")
        with open(out_file, "w", encoding="utf-8") as out:
            out.write(f"第{chapter_num}章 {title}\n\n")
            out.write(content)

    return output_dir


def _parse_chapter_titles(outline_file: str) -> dict:
    """从大纲文件解析章节标题"""
    titles = {}
    if not os.path.exists(outline_file):
        return titles

    with open(outline_file, "r", encoding="utf-8") as f:
        for line in f:
            # 匹配 "第N章 - 标题" 或 "第N章：标题" 或 "第N章 标题"
            m = re.match(r'第\s*(\d+)\s*章\s*[-：:]\s*(.+)', line.strip())
            if m:
                titles[int(m.group(1))] = m.group(2).strip()
            m2 = re.match(r'第\s*(\d+)\s*章\s+(.+)', line.strip())
            if m2 and not m:
                titles[int(m2.group(1))] = m2.group(2).strip()

    return titles


def get_export_stats(project_path: str) -> dict:
    """获取导出统计信息"""
    chapters_dir = os.path.join(project_path, "chapters")
    if not os.path.exists(chapters_dir):
        return {"count": 0, "total_words": 0}

    chapter_files = [f for f in os.listdir(chapters_dir) if f.startswith("chapter_") and f.endswith(".txt")]
    total_words = 0
    for cf in chapter_files:
        with open(os.path.join(chapters_dir, cf), "r", encoding="utf-8") as f:
            total_words += len(f.read())

    return {"count": len(chapter_files), "total_words": total_words}
