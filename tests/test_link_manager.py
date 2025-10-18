#!/usr/bin/env python3
"""
链接管理器测试脚本

测试LinkManager类的功能。
"""

import sys
import tempfile
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from book_splitter.managers import LinkManager
from book_splitter.models import ChapterInfo, SectionInfo
from book_splitter.config import ProcessingConfig


def test_toc_generation():
    """测试目录生成功能"""
    print("测试目录生成功能...")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 配置
            config = ProcessingConfig()
            config.output_dir = temp_dir
            config.create_sections = True
            config.generate_tags = True

            link_manager = LinkManager(config)

            # 创建测试章节
            chapters = [
                ChapterInfo(
                    title="第一章 政治学基础理论",
                    start_line=1,
                    end_line=100,
                    file_path="chapters/政治学基础理论.md"
                ),
                ChapterInfo(
                    title="第二章 政治权力分析",
                    start_line=101,
                    end_line=200,
                    file_path="chapters/政治权力分析.md"
                ),
                ChapterInfo(
                    title="第三章 政治制度研究",
                    start_line=201,
                    end_line=300,
                    file_path="chapters/政治制度研究.md"
                ),
            ]

            # 创建测试小节
            sections = [
                SectionInfo(
                    title="政治权力的概念",
                    start_line=50,
                    end_line=80,
                    chapter_title="第一章 政治学基础理论",
                    level=2,
                    file_path="sections/政治权力的概念.md"
                ),
                SectionInfo(
                    title="权力的类型",
                    start_line=81,
                    end_line=100,
                    chapter_title="第一章 政治学基础理论",
                    level=2,
                    file_path="sections/权力的类型.md"
                ),
                SectionInfo(
                    title="政治权力的特征",
                    start_line=150,
                    end_line=180,
                    chapter_title="第二章 政治权力分析",
                    level=2,
                    file_path="sections/政治权力的特征.md"
                ),
            ]

            # 生成目录
            toc_content = link_manager.generate_toc(chapters, sections)

            print(f"📋 生成的目录内容预览:")
            print(toc_content[:200] + "...")

            # 验证目录内容
            assert toc_content.startswith("# 目录"), "目录应以'# 目录'开头"
            assert "第一章 政治学基础理论" in toc_content, "应包含第一章"
            assert "第二章 政治权力分析" in toc_content, "应包含第二章"
            assert "第三章 政治制度研究" in toc_content, "应包含第三章"
            assert "政治权力的概念" in toc_content, "应包含小节"
            assert "权力的类型" in toc_content, "应包含小节"

            # 验证链接格式
            assert "[第一章 政治学基础理论](chapters/政治学基础理论.md)" in toc_content, "应包含章节链接"
            assert "[政治权力的概念](sections/政治权力的概念.md)" in toc_content, "应包含小节链接"

            print("✅ 目录生成测试通过")

        except Exception as e:
            print(f"❌ 目录生成测试失败: {str(e)}")
            raise


def test_navigation_links():
    """测试导航链接生成"""
    print("测试导航链接生成...")

    try:
        config = ProcessingConfig()
        config.output_dir = "test_output"
        config.add_navigation = True

        link_manager = LinkManager(config)

        # 测试章节导航链接
        chapter = ChapterInfo(
            title="第一章 政治学基础理论",
            start_line=1,
            end_line=100,
            file_path="chapters/政治学基础理论.md"
        )

        prev_chapter = ChapterInfo(
            title="前言",
            start_line=1,
            end_line=50,
            file_path="chapters/前言.md"
        )

        next_chapter = ChapterInfo(
            title="第二章 政治权力分析",
            start_line=101,
            end_line=200,
            file_path="chapters/政治权力分析.md"
        )

        # 生成章节导航链接
        nav_links = link_manager._generate_chapter_navigation(chapter, prev_chapter, next_chapter)

        print(f"🔗 章节导航链接:")
        print(nav_links)

        # 验证导航链接
        assert "返回目录" in nav_links, "应包含返回目录链接"
        assert "[前言](chapters/前言.md)" in nav_links, "应包含上一章链接"
        assert "[第二章 政治权力分析](chapters/政治权力分析.md)" in nav_links, "应包含下一章链接"

        # 测试小节导航链接
        section = SectionInfo(
            title="政治权力的概念",
            start_line=50,
            end_line=80,
            chapter_title="第一章 政治学基础理论",
            level=2,
            file_path="sections/政治权力的概念.md"
        )

        prev_section = SectionInfo(
            title="政治学定义",
            start_line=30,
            end_line=49,
            chapter_title="第一章 政治学基础理论",
            level=2,
            file_path="sections/政治学定义.md"
        )

        next_section = SectionInfo(
            title="权力的类型",
            start_line=81,
            end_line=100,
            chapter_title="第一章 政治学基础理论",
            level=2,
            file_path="sections/权力的类型.md"
        )

        # 生成小节导航链接
        section_nav = link_manager._generate_section_navigation(section, prev_section, next_section)

        print(f"🔗 小节导航链接:")
        print(section_nav)

        # 验证小节导航链接
        assert "返回章节" in section_nav, "应包含返回章节链接"
        assert "[政治学定义](sections/政治学定义.md)" in section_nav, "应包含上一节链接"
        assert "[权力的类型](sections/权力的类型.md)" in section_nav, "应包含下一节链接"
        assert "第一章 政治学基础理论" in section_nav, "应包含章节标题"

        print("✅ 导航链接测试通过")

    except Exception as e:
        print(f"❌ 导航链接测试失败: {str(e)}")
        raise


def test_configuration_options():
    """测试配置选项"""
    print("测试配置选项...")

    try:
        # 测试不同配置组合
        test_cases = [
            {"add_navigation": True, "create_sections": True},
            {"add_navigation": False, "create_sections": True},
            {"add_navigation": True, "create_sections": False},
            {"add_navigation": False, "create_sections": False},
        ]

        for i, case_config in enumerate(test_cases):
            print(f"\n🧪 测试配置组合 {i+1}:")
            print(f"  - 添加导航: {case_config['add_navigation']}")
            print(f"  - 创建小节: {case_config['create_sections']}")

            config = ProcessingConfig()
            config.output_dir = "test_output"
            config.add_navigation = case_config['add_navigation']
            config.create_sections = case_config['create_sections']

            link_manager = LinkManager(config)

            # 创建测试数据
            chapters = [
                ChapterInfo(
                    title="测试章节",
                    start_line=1,
                    end_line=100,
                    file_path="chapters/测试章节.md"
                )
            ]

            sections = [
                SectionInfo(
                    title="测试小节",
                    start_line=50,
                    end_line=80,
                    chapter_title="测试章节",
                    level=2,
                    file_path="sections/测试小节.md"
                )
            ]

            # 生成目录
            toc_content = link_manager.generate_toc(chapters, sections)

            # 验证配置生效
            if case_config['create_sections']:
                assert "测试小节" in toc_content, "应包含小节"
            else:
                assert "测试小节" not in toc_content, "不应包含小节"

            # 测试导航链接生成
            chapter = chapters[0]
            nav_links = link_manager._generate_chapter_navigation(chapter, None, None)

            if case_config['add_navigation']:
                assert "返回目录" in nav_links, "应包含导航链接"
            else:
                assert "返回目录" not in nav_links, "不应包含导航链接"

            print(f"  ✅ 配置验证通过")

        print("✅ 配置选项测试通过")

    except Exception as e:
        print(f"❌ 配置选项测试失败: {str(e)}")
        raise


def test_error_handling():
    """测试错误处理"""
    print("测试错误处理...")

    try:
        config = ProcessingConfig()
        config.output_dir = "test_output"

        link_manager = LinkManager(config)

        # 测试空章节列表
        try:
            toc_content = link_manager.generate_toc([], [])
            assert toc_content.startswith("# 目录"), "空列表时应生成基本目录"
            print("✅ 空章节列表处理正确")
        except Exception as e:
            print(f"❌ 空章节列表处理失败: {str(e)}")
            raise

        # 测试无文件路径的章节
        chapter_without_path = ChapterInfo(
            title="无路径章节",
            start_line=1,
            end_line=100
        )

        try:
            nav_links = link_manager._generate_chapter_navigation(chapter_without_path, None, None)
            assert "返回目录" in nav_links, "应生成基本导航链接"
            assert "无路径章节" not in nav_links, "不应包含无路径章节的链接"
            print("✅ 无文件路径章节处理正确")
        except Exception as e:
            print(f"❌ 无文件路径章节处理失败: {str(e)}")
            raise

        print("✅ 错误处理测试通过")

    except Exception as e:
        print(f"❌ 错误处理测试失败: {str(e)}")
        raise


def test_link_formatting():
    """测试链接格式化"""
    print("测试链接格式化...")

    try:
        config = ProcessingConfig()
        config.output_dir = "test_output"

        link_manager = LinkManager(config)

        # 测试各种链接格式化情况
        test_cases = [
            ("chapters/政治学基础理论.md", "第一章 政治学基础理论", "[第一章 政治学基础理论](chapters/政治学基础理论.md)"),
            ("sections/政治权力的概念.md", "政治权力的概念", "[政治权力的概念](sections/政治权力的概念.md)"),
            ("", "无链接标题", "无链接标题"),
            (None, "空链接标题", "空链接标题"),
        ]

        print("🔗 链接格式化测试:")
        for file_path, title, expected_pattern in test_cases:
            formatted_link = link_manager._format_link(file_path, title)
            print(f"  '{file_path}', '{title}' -> '{formatted_link}'")

            # 基本验证
            if file_path and title:
                assert formatted_link.startswith("["), "应包含链接格式"
                assert formatted_link.endswith(")"), "应包含链接格式"
                assert title in formatted_link, "应包含标题"
                assert file_path in formatted_link, "应包含文件路径"
            else:
                assert formatted_link == title, "无链接时应返回原始标题"

        print("✅ 链接格式化测试通过")

    except Exception as e:
        print(f"❌ 链接格式化测试失败: {str(e)}")
        raise


def test_special_characters():
    """测试特殊字符处理"""
    print("测试特殊字符处理...")

    try:
        config = ProcessingConfig()
        config.output_dir = "test_output"

        link_manager = LinkManager(config)

        # 测试包含特殊字符的标题
        special_chapters = [
            ChapterInfo(
                title="Chapter 1: Introduction",
                start_line=1,
                end_line=100,
                file_path="chapters/introduction.md"
            ),
            ChapterInfo(
                title="政治学/社会学 交叉研究",
                start_line=101,
                end_line=200,
                file_path="chapters/交叉研究.md"
            ),
            ChapterInfo(
                title="权力&制衡理论",
                start_line=201,
                end_line=300,
                file_path="chapters/权力制衡理论.md"
            ),
            ChapterInfo(
                title="**重要**章节",
                start_line=301,
                end_line=400,
                file_path="chapters/重要章节.md"
            ),
        ]

        # 生成目录
        toc_content = link_manager.generate_toc(special_chapters, [])

        print(f"🔤 特殊字符处理预览:")
        print(toc_content[:300] + "...")

        # 验证特殊字符处理
        assert "Chapter 1: Introduction" in toc_content, "应包含英文标题"
        assert "政治学/社会学 交叉研究" in toc_content, "应包含斜杠标题"
        assert "权力&制衡理论" in toc_content, "应包含&符号标题"
        assert "**重要**章节" in toc_content, "应包含星号标题"

        # 验证链接格式正确
        assert "[Chapter 1: Introduction](chapters/introduction.md)" in toc_content, "英文链接格式正确"
        assert "[政治学/社会学 交叉研究](chapters/交叉研究.md)" in toc_content, "斜杠链接格式正确"

        print("✅ 特殊字符处理测试通过")

    except Exception as e:
        print(f"❌ 特殊字符处理测试失败: {str(e)}")
        raise


def main():
    """运行所有测试"""
    print("开始链接管理器测试...\n")

    try:
        test_toc_generation()
        print()
        test_navigation_links()
        print()
        test_configuration_options()
        print()
        test_error_handling()
        print()
        test_link_formatting()
        print()
        test_special_characters()

        print("\n🎉 所有链接管理器测试通过!")
        print("链接管理器功能已正确实现。")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()