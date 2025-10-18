#!/usr/bin/env python3
"""
结构分析器测试脚本

测试StructureAnalyzer类的功能。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from book_splitter.analyzers import StructureAnalyzer


def test_structure_analyzer():
    """测试结构分析器"""
    print("测试结构分析器...")

    # 检查源文件是否存在
    if not Path("full.md").exists():
        print("⚠️  警告: full.md文件不存在，跳过结构分析测试")
        return

    try:
        # 创建分析器实例
        analyzer = StructureAnalyzer("full.md")

        # 执行结构分析
        result = analyzer.analyze_structure()

        # 获取统计信息
        stats = analyzer.get_statistics()

        # 验证结果
        chapters = result['chapters']
        sections = result['sections']

        print(f"📊 分析统计:")
        print(f"  - 总行数: {stats['total_lines']}")
        print(f"  - 章节数: {stats['chapters_count']}")
        print(f"  - 小节数: {stats['sections_count']}")
        print(f"  - 平均章节长度: {stats['average_chapter_length']:.1f} 行")
        print(f"  - 有小节的章节数: {stats['chapters_with_sections']}")

        # 显示前几个章节
        print(f"\n📖 前5个章节:")
        for i, chapter in enumerate(chapters[:5]):
            print(f"  {i+1}. {chapter.title}")
            print(f"     行号: {chapter.start_line}-{chapter.end_line} ({chapter.line_count} 行)")
            if chapter.has_sections:
                print(f"     包含 {len(chapter.sections)} 个小节")

        # 显示前几个小节
        print(f"\n📝 前5个小节:")
        for i, section in enumerate(sections[:5]):
            print(f"  {i+1}. {section.title}")
            print(f"     行号: {section.start_line}-{section.end_line} ({section.line_count} 行)")
            print(f"     级别: {section.level}, 所属章节: {section.chapter_title}")

        # 验证结构
        issues = analyzer.validate_structure()
        if issues:
            print(f"\n⚠️  发现 {len(issues)} 个结构问题:")
            for issue in issues[:5]:  # 只显示前5个问题
                print(f"  - {issue}")
        else:
            print(f"\n✅ 结构验证通过，未发现问题")

        # 基本断言
        assert len(chapters) > 0, "应该识别到章节"
        assert len(sections) > 0, "应该识别到小节"
        assert stats['total_lines'] > 0, "应该读取到文件内容"

        print(f"\n✅ 结构分析器测试通过")

    except Exception as e:
        print(f"❌ 结构分析器测试失败: {str(e)}")
        raise


def main():
    """运行测试"""
    print("开始结构分析器测试...\n")

    try:
        test_structure_analyzer()
        print("\n🎉 结构分析器测试完成!")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()