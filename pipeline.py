# pipeline.py
# -*- coding: utf-8 -*-
"""
番茄 AI 写作整合流水线

整合 AI_NovelGenerator 的自动流水线 + oh-story-claudecode 的质量层。

工作流程：
Step 1: 生成设定（架构） — 使用增强版 prompt
Step 2: 生成章节目录 — 使用增强版 prompt（含章末钩子要求）
Step 3: 逐章生成草稿 — 使用增强版 prompt
Step 3.5: 去 AI 味处理 — 使用 7 Gate 系统
Step 3.6: 番茄平台合规检查
Step 4: 定稿 — 更新摘要、角色状态、向量库
"""

import os
import sys
import json
import logging
import argparse

# 添加 engine 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "engine"))

from engine.config_manager import load_config, save_config
from engine.llm_adapters import create_llm_adapter
from engine.embedding_adapters import create_embedding_adapter
from engine.novel_generator.architecture import Novel_architecture_generate
from engine.novel_generator.blueprint import Chapter_blueprint_generate
from engine.novel_generator.chapter import generate_chapter_draft
from engine.novel_generator.finalization import finalize_chapter, enrich_chapter_text
from engine.consistency_checker import check_consistency
from engine.enhanced_prompts import get_enhanced_prompts
from quality.deslop.deslop_engine import deslop_chapter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FanqiePipeline:
    """番茄 AI 写作整合流水线"""

    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self.config = load_config(config_path)
        genre = (self.config.get("other_params", {}) or {}).get("genre") or "都市"
        self.enhanced_prompts = get_enhanced_prompts(genre)

    def step1_generate_architecture(self):
        """
        Step 1: 生成小说设定（架构）
        使用增强版 prompt，融入都市类题材公式和人物设计方法论。
        """
        logger.info("=" * 60)
        logger.info("Step 1: 生成小说设定（架构）")
        logger.info("=" * 60)

        params = self.config.get("other_params", {})
        choose = self.config.get("choose_configs", {})
        llm_configs = self.config.get("llm_configs", {})

        # 获取架构生成用的 LLM 配置
        arch_llm_name = choose.get("architecture_llm", "")
        arch_llm = llm_configs.get(arch_llm_name, {})

        filepath = params.get("filepath", "")
        if not filepath:
            raise ValueError("请在 config 中设置 other_params.filepath（小说项目目录）")

        os.makedirs(filepath, exist_ok=True)

        # 注入与当前题材匹配的增强版 prompt（含题材公式、基调控制）
        self._patch_prompts()

        # 调用原始架构生成（架构阶段用原始 prompt，章节阶段用增强 prompt）
        Novel_architecture_generate(
            interface_format=arch_llm.get("interface_format", "openai"),
            api_key=arch_llm.get("api_key", ""),
            base_url=arch_llm.get("base_url", ""),
            llm_model=arch_llm.get("model_name", ""),
            topic=params.get("topic", ""),
            genre=params.get("genre", "都市"),
            number_of_chapters=params.get("num_chapters", 100),
            word_number=params.get("word_number", 3000),
            filepath=filepath,
            user_guidance=params.get("user_guidance", ""),
            temperature=arch_llm.get("temperature", 0.7),
            max_tokens=arch_llm.get("max_tokens", 8192),
            timeout=arch_llm.get("timeout", 600),
        )

        logger.info("Step 1 完成: 架构已生成")

    def step2_generate_blueprint(self):
        """
        Step 2: 生成章节目录（大纲）
        使用增强版 prompt，包含章末钩子要求。
        """
        logger.info("=" * 60)
        logger.info("Step 2: 生成章节目录")
        logger.info("=" * 60)

        params = self.config.get("other_params", {})
        choose = self.config.get("choose_configs", {})
        llm_configs = self.config.get("llm_configs", {})

        blueprint_llm_name = choose.get("chapter_outline_llm", "")
        blueprint_llm = llm_configs.get(blueprint_llm_name, {})

        filepath = params.get("filepath", "")

        # 注入与当前题材匹配的增强版 prompt
        self._patch_prompts()

        Chapter_blueprint_generate(
            interface_format=blueprint_llm.get("interface_format", "openai"),
            api_key=blueprint_llm.get("api_key", ""),
            base_url=blueprint_llm.get("base_url", ""),
            llm_model=blueprint_llm.get("model_name", ""),
            filepath=filepath,
            number_of_chapters=params.get("num_chapters", 100),
            user_guidance=params.get("user_guidance", ""),
            temperature=blueprint_llm.get("temperature", 0.7),
            max_tokens=blueprint_llm.get("max_tokens", 8192),
            timeout=blueprint_llm.get("timeout", 600),
        )

        logger.info("Step 2 完成: 章节目录已生成")

    def step3_generate_chapter(self, chapter_num: int):
        """
        Step 3: 生成单章草稿
        使用增强版 prompt，融入对话技巧、情绪弧线、描写多样性等。
        """
        logger.info("=" * 60)
        logger.info(f"Step 3: 生成第 {chapter_num} 章草稿")
        logger.info("=" * 60)

        params = self.config.get("other_params", {})
        choose = self.config.get("choose_configs", {})
        llm_configs = self.config.get("llm_configs", {})
        embedding_configs = self.config.get("embedding_configs", {})

        chapter_llm_name = choose.get("final_chapter_llm", "")
        chapter_llm = llm_configs.get(chapter_llm_name, {})

        embed_name = choose.get("embedding_llm", "")
        embed_cfg = embedding_configs.get(embed_name, {}) if embed_name else {}

        filepath = params.get("filepath", "")

        self._patch_prompts()

        # 注入描写多样性指令到 user_guidance
        user_guidance = params.get("user_guidance", "")
        try:
            from quality.knowledge.description_diversity import get_description_diversity_prompt
            diversity_prompt = get_description_diversity_prompt(chapter_num)
            enhanced_guidance = f"{user_guidance}\n\n{diversity_prompt}" if user_guidance else diversity_prompt
        except Exception:
            enhanced_guidance = user_guidance

        chapter_text = generate_chapter_draft(
            novel_number=chapter_num,
            word_number=params.get("word_number", 3000),
            characters_involved=params.get("characters_involved", ""),
            key_items=params.get("key_items", ""),
            user_guidance=enhanced_guidance,
            scene_location=params.get("scene_location", ""),
            time_constraint=params.get("time_constraint", ""),
            api_key=chapter_llm.get("api_key", ""),
            base_url=chapter_llm.get("base_url", ""),
            model_name=chapter_llm.get("model_name", ""),
            temperature=chapter_llm.get("temperature", 0.7),
            filepath=filepath,
            embedding_api_key=embed_cfg.get("api_key", ""),
            embedding_url=embed_cfg.get("base_url", ""),
            embedding_interface_format=embed_cfg.get("interface_format", "openai"),
            embedding_model_name=embed_cfg.get("model_name", ""),
            interface_format=chapter_llm.get("interface_format", "openai"),
            max_tokens=chapter_llm.get("max_tokens", 8192),
            timeout=chapter_llm.get("timeout", 600),
        )

        return chapter_text

    def step3_5_deslop(self, chapter_num: int):
        """
        Step 3.5: 去 AI 味处理
        使用 7 Gate 系统清理 AI 写作痕迹。
        """
        logger.info("=" * 60)
        logger.info(f"Step 3.5: 去 AI 味处理 — 第 {chapter_num} 章")
        logger.info("=" * 60)

        filepath = self.config.get("other_params", {}).get("filepath", "")
        chapters_dir = os.path.join(filepath, "chapters")
        chapter_file = os.path.join(chapters_dir, f"chapter_{chapter_num}.txt")

        if not os.path.exists(chapter_file):
            logger.warning(f"章节文件不存在: {chapter_file}")
            return

        with open(chapter_file, "r", encoding="utf-8") as f:
            chapter_text = f.read()

        if not chapter_text.strip():
            logger.warning(f"第 {chapter_num} 章为空，跳过去 AI 味处理")
            return

        # 执行去 AI 味
        gate_config = self.config.get("deslop_config", {
            "gate_a": True, "gate_b": True, "gate_c": True,
            "gate_d": True, "gate_e": True, "gate_f": True, "gate_g": True,
        })

        cleaned_text = deslop_chapter(chapter_text, gate_config)

        # 保存清理后的文本
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        logger.info(f"Step 3.5 完成: 第 {chapter_num} 章已去 AI 味")

    def step3_6_fanqie_check(self, chapter_num: int):
        """
        Step 3.6: 番茄平台合规检查
        检查字数、敏感词、格式等。
        """
        logger.info("=" * 60)
        logger.info(f"Step 3.6: 番茄合规检查 — 第 {chapter_num} 章")
        logger.info("=" * 60)

        filepath = self.config.get("other_params", {}).get("filepath", "")
        chapters_dir = os.path.join(filepath, "chapters")
        chapter_file = os.path.join(chapters_dir, f"chapter_{chapter_num}.txt")

        if not os.path.exists(chapter_file):
            return

        with open(chapter_file, "r", encoding="utf-8") as f:
            chapter_text = f.read()

        issues = []

        # 字数检查
        word_count = len(chapter_text)
        min_words = 2000
        max_words = 4000
        if word_count < min_words:
            issues.append(f"字数不足: {word_count}字 (最低{min_words}字)")
        elif word_count > max_words:
            issues.append(f"字数过多: {word_count}字 (最高{max_words}字)")

        # 标点检查
        if "——" in chapter_text or "—" in chapter_text:
            issues.append("包含破折号，番茄读者不习惯")
        if "……" in chapter_text:
            issues.append("包含省略号，建议用句号/逗号替代")

        # 段落长度检查
        paragraphs = [p for p in chapter_text.split('\n') if p.strip()]
        long_paras = [p for p in paragraphs if len(p) > 200]
        if long_paras:
            issues.append(f"有{len(long_paras)}个段落超过200字，建议拆分")

        # 报告
        if issues:
            logger.warning(f"第 {chapter_num} 章合规检查发现 {len(issues)} 个问题:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info(f"第 {chapter_num} 章合规检查通过")

        return issues

    def step4_finalize_chapter(self, chapter_num: int):
        """
        Step 4: 定稿
        更新摘要、角色状态、向量库。
        """
        logger.info("=" * 60)
        logger.info(f"Step 4: 定稿 — 第 {chapter_num} 章")
        logger.info("=" * 60)

        params = self.config.get("other_params", {})
        choose = self.config.get("choose_configs", {})
        llm_configs = self.config.get("llm_configs", {})
        embedding_configs = self.config.get("embedding_configs", {})

        final_llm_name = choose.get("final_chapter_llm", "")
        final_llm = llm_configs.get(final_llm_name, {})

        embed_name = choose.get("embedding_llm", "")
        embed_cfg = embedding_configs.get(embed_name, {}) if embed_name else {}

        filepath = params.get("filepath", "")

        finalize_chapter(
            novel_number=chapter_num,
            word_number=params.get("word_number", 3000),
            api_key=final_llm.get("api_key", ""),
            base_url=final_llm.get("base_url", ""),
            model_name=final_llm.get("model_name", ""),
            temperature=final_llm.get("temperature", 0.7),
            filepath=filepath,
            embedding_api_key=embed_cfg.get("api_key", ""),
            embedding_url=embed_cfg.get("base_url", ""),
            embedding_interface_format=embed_cfg.get("interface_format", "openai"),
            embedding_model_name=embed_cfg.get("model_name", ""),
            interface_format=final_llm.get("interface_format", "openai"),
            max_tokens=final_llm.get("max_tokens", 8192),
            timeout=final_llm.get("timeout", 600),
        )

        logger.info(f"Step 4 完成: 第 {chapter_num} 章已定稿")

    def run_full_pipeline(self, start_chapter: int = 1, end_chapter: int = None):
        """
        运行完整流水线：设定 → 目录 → 逐章生成+去AI味+合规检查+定稿
        """
        params = self.config.get("other_params", {})
        if end_chapter is None:
            end_chapter = params.get("num_chapters", 100)

        logger.info("=" * 60)
        logger.info("番茄 AI 写作流水线启动")
        logger.info(f"书名: {params.get('topic', '未设置')}")
        logger.info(f"类型: {params.get('genre', '都市')}")
        logger.info(f"章数: {start_chapter} - {end_chapter}")
        logger.info("=" * 60)

        # Step 1: 生成设定
        if start_chapter == 1:
            self.step1_generate_architecture()
            self.step2_generate_blueprint()

        # Step 3-4: 逐章生成
        for chapter_num in range(start_chapter, end_chapter + 1):
            logger.info(f"\n{'='*40}")
            logger.info(f"开始处理第 {chapter_num}/{end_chapter} 章")
            logger.info(f"{'='*40}")

            # Step 3: 生成草稿
            self.step3_generate_chapter(chapter_num)

            # Step 3.5: 去 AI 味
            self.step3_5_deslop(chapter_num)

            # Step 3.6: 番茄合规检查
            self.step3_6_fanqie_check(chapter_num)

            # Step 4: 定稿
            self.step4_finalize_chapter(chapter_num)

            logger.info(f"第 {chapter_num} 章处理完成")

        logger.info("\n" + "=" * 60)
        logger.info("流水线完成！")
        logger.info("=" * 60)

    def _patch_prompts(self):
        """
        Monkey-patch prompt_definitions 模块，注入与当前题材匹配的增强版 prompt。
        使用共享的 patch_prompt_definitions，保证 CLI 与 GUI 行为一致。
        """
        from enhanced_prompts import patch_prompt_definitions

        genre = (self.config.get("other_params", {}) or {}).get("genre") or "都市"
        patch_prompt_definitions(genre)
        self.enhanced_prompts = get_enhanced_prompts(genre)
        logger.info(f"已注入 {genre} 题材的增强版 prompt")


def main():
    parser = argparse.ArgumentParser(description="番茄 AI 写作整合流水线")
    parser.add_argument("--config", default="config/config.json", help="配置文件路径")
    parser.add_argument("--action", choices=["full", "step1", "step2", "step3", "deslop", "check", "finalize"],
                       default="full", help="执行的操作")
    parser.add_argument("--chapter", type=int, default=1, help="章节号（step3/deslop/check/finalize 时使用）")
    parser.add_argument("--start", type=int, default=1, help="起始章节号（full 时使用）")
    parser.add_argument("--end", type=int, default=None, help="结束章节号（full 时使用）")

    args = parser.parse_args()

    pipeline = FanqiePipeline(args.config)

    if args.action == "full":
        pipeline.run_full_pipeline(args.start, args.end)
    elif args.action == "step1":
        pipeline.step1_generate_architecture()
    elif args.action == "step2":
        pipeline.step2_generate_blueprint()
    elif args.action == "step3":
        pipeline.step3_generate_chapter(args.chapter)
    elif args.action == "deslop":
        pipeline.step3_5_deslop(args.chapter)
    elif args.action == "check":
        pipeline.step3_6_fanqie_check(args.chapter)
    elif args.action == "finalize":
        pipeline.step4_finalize_chapter(args.chapter)


if __name__ == "__main__":
    main()
