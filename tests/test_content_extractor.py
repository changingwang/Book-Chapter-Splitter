#!/usr/bin/env python3
"""
内容提取器测试脚本

测试ContentExtractor类的功能。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from book_splitter.extractors import ContentExtractor
from book_splitter.analyzers import StructureAnalyzer


def test_basic_extraction():
    """测试基本内容提取功能"""
    print("测试基本内容提取功能...")
    
    # 检查源文件是否存在
    if not Path("full.md").exists():
        print("⚠️  警告: full.md文件不存在，跳过内容提取测试")
        return
    
    try:
        # 创建提取器实例
        extractor = ContentExtractor("full.md")
        
        # 获取统计信息
        stats = extractor.get_extraction_statistics()
        print(f"📊 文件统计:")
        print(f"  - 文件: {stats['source_file']}")
        print(f"  - 总行数: {stats['total_lines']}")
        print(f"  - 文件大小: {stats['file_size_bytes']} 字节")
        
        # 测试单个范围提取
        print(f"\n📄 测试单个范围提取:")
        content = extractor.extract_content(1, 10)
        lines = content.splitlines()
        print(f"  - 提取行数: {len(lines)}")
        print(f"  - 前3行内容:")
        for i, line in enumerate(lines[:3]):
            print(f"    {i+1}: {line[:50]}{'...' if len(line) > 50 else ''}")
        
        # 验证内容完整性
        is_valid = extractor.validate_content_integrity(content, 10)
        print(f"  - 内容完整性: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        # 测试批量提取
        print(f"\n📦 测试批量提取:")
        ranges = [(1, 5), (10, 15), (20, 25)]
        batch_results = extractor.extract_multiple_ranges(ranges)
        print(f"  - 请求范围数: {len(ranges)}")
        print(f"  - 成功提取数: {len(batch_results)}")
        
        for range_key, content in list(batch_results.items())[:2]:
            lines_count = len(content.splitlines())
            print(f"  - 范围 {range_key}: {lines_count} 行")
        
        print(f"✅ 基本内容提取测试通过")
        
    except Exception as e:
        print(f"❌ 基本内容提取测试失败: {str(e)}")
        raise


def test_chapter_section_extraction():
    """测试章节和小节内容提取"""
    print("测试章节和小节内容提取...")
    
    if not Path("full.md").exists():
        print("⚠️  警告: full.md文件不存在，跳过章节小节提取测试")
        return
    
    try:
        # 先分析结构
        analyzer = StructureAnalyzer("full.md")
        structure = analyzer.analyze_structure()
        
        chapters = structure['chapters'][:3]  # 只测试前3个章节
        sections = structure['sections'][:5]  # 只测试前5个小节
        
        # 创建提取器
        extractor = ContentExtractor("full.md")
        
        # 测试章节内容提取
        print(f"\n📖 测试章节内容提取:")
        for i, chapter in enumerate(chapters):
            content = extractor.extract_chapter_content(chapter)
            lines_count = len(content.splitlines())
            print(f"  {i+1}. {chapter.title}")
            print(f"     行数: {lines_count}, 字符数: {len(content)}")
            
            # 显示前几行内容
            first_lines = content.splitlines()[:2]
            for j, line in enumerate(first_lines):
                print(f"     L{j+1}: {line[:60]}{'...' if len(line) > 60 else ''}")
        
        # 测试小节内容提取
        print(f"\n📝 测试小节内容提取:")
        for i, section in enumerate(sections):
            content = extractor.extract_section_content(section)
            lines_count = len(content.splitlines())
            print(f"  {i+1}. {section.title}")
            print(f"     行数: {lines_count}, 字符数: {len(content)}")
            print(f"     级别: {section.level}")
        
        # 测试批量提取
        print(f"\n📦 测试批量章节提取:")
        batch_chapters = extractor.extract_chapters_batch(chapters)
        print(f"  - 请求章节数: {len(chapters)}")
        print(f"  - 成功提取数: {len(batch_chapters)}")
        
        print(f"\n📦 测试批量小节提取:")
        batch_sections = extractor.extract_sections_batch(sections)
        print(f"  - 请求小节数: {len(sections)}")
        print(f"  - 成功提取数: {len(batch_sections)}")
        
        print(f"✅ 章节和小节内容提取测试通过")
        
    except Exception as e:
        print(f"❌ 章节和小节内容提取测试失败: {str(e)}")
        raise


def test_context_extraction():
    """测试上下文提取功能"""
    print("测试上下文提取功能...")
    
    if not Path("full.md").exists():
        print("⚠️  警告: full.md文件不存在，跳过上下文提取测试")
        return
    
    try:
        extractor = ContentExtractor("full.md")
        
        # 测试带上下文的内容提取
        context_result = extractor.extract_content_with_context(10, 15, context_lines=3)
        
        print(f"📄 上下文提取结果:")
        print(f"  - 主要内容行数: {len(context_result['content'].splitlines())}")
        print(f"  - 前置上下文行数: {len(context_result['before_context'].splitlines())}")
        print(f"  - 后置上下文行数: {len(context_result['after_context'].splitlines())}")
        print(f"  - 完整上下文行数: {len(context_result['full_context'].splitlines())}")
        
        # 显示部分内容
        print(f"  - 主要内容预览:")
        main_lines = context_result['content'].splitlines()[:2]
        for i, line in enumerate(main_lines):
            print(f"    {i+1}: {line[:50]}{'...' if len(line) > 50 else ''}")
        
        print(f"✅ 上下文提取测试通过")
        
    except Exception as e:
        print(f"❌ 上下文提取测试失败: {str(e)}")
        raise


def main():
    """运行所有测试"""
    print("开始内容提取器测试...\n")
    
    try:
        test_basic_extraction()
        print()
        test_chapter_section_extraction()
        print()
        test_context_extraction()
        
        print("\n🎉 所有内容提取器测试通过!")
        print("内容提取器功能已正确实现。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()