# run_gui.py
# -*- coding: utf-8 -*-
"""
番茄 AI 写作系统 - GUI 启动入口
"""
import sys
import os

# 确保能找到 engine 和 gui 模块
sys.path.insert(0, os.path.dirname(__file__))

from gui.app import NovelApp

if __name__ == "__main__":
    app = NovelApp()
    app.mainloop()
