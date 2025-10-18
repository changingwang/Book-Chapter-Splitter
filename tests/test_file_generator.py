#!/usr/bin/env python3
"""
文件生成器测试脚本

测试FileGenerator类的功能。
"""

import sys
import tempfile
import shutil
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from book_splitter.generators import FileGenerator
from book_splitter.models import ChapterInfo, SectionInfo
from book_splitter.config import ProcessingConfig


def test_filename_sanitization():
    """测试文件名清理功能"""
    print("测试文件名清理功能...")
    
    try:
        # 创建临时配置
        config = ProcessingConfig()
        config.output_dir = "test_output"
        
        file_generator = FileGenerator(config)
        
        # 测试各种文件名清理情况
        test_cases = [
            ("第一章 政治学基础理论", "政治学基础理论"),
            ("第1章 民主与权力", "民主与权力"),
            ("**重要章节**：权力分析", "重要章节权力分析"),
            ("政治*理论*研究", "政治理论研究"),
            ("第二节 国际关系", "国际关系"),
            ("一、基本概念", "基本概念"),
            ("(1) 核心要素", "核心要素"),
            ("政治学/社会学", "政治学社会学"),
            ("权力&制衡", "权力制衡"),
            ("", "untitled"),
            ("   ", "untitled"),
            ("123数字开头", "file_123数字开头"),
        ]
        
        print("📝 文件名清理测试:")
        for original, expected_pattern in test_cases:
            sanitized = file_generator.sanitize_filename(original)
            print(f"  '{original}' -> '{sanitized}'")
            
            # 基本验证
            assert sanitized, "清理后的文件名不应为空"
            assert len(sanitized) <= 100, "文件名长度应在限制内"
            assert not sanitized.startswith('_'), "文件名不应以下划线开头"
            assert not sanitized.endswith('_'), "文件名不应以下划线结尾"
        
        print("✅ 文件名清理测试通过")
        
    except Exception as e:
        print(f"❌ 文件名清理测试失败: {str(e)}")
        raise


def test_unique_filename_generation():
    """测试唯一文件名生成"""
    print("测试唯一文件名生成...")
    
    try:
        config = ProcessingConfig()
        config.output_dir = "test_output"
        
        file_generator = FileGenerator(config)
        
        # 测试重复文件名处理
        base_name = "政治学理论"
        
        # 生成多个相同基础名的文件名
        filenames = []
        for i in range(5):
            unique_name = file_generator._ensure_unique_filename(base_name)
            filenames.append(unique_name)
            print(f"  第{i+1}次: {unique_name}")
        
        # 验证唯一性
        assert len(set(filenames)) == len(filenames), "所有文件名应该是唯一的"
        assert filenames[0] == "政治学理论.md", "第一个文件名应该是原始名称"
        
        # 验证后续文件名包含数字后缀
        for i, filename in enumerate(filenames[1:], 2):
            assert f"_{i}.md" in filename, f"第{i}个文件名应包含数字后缀"
        
        print("✅ 唯一文件名生成测试通过")
        
    except Exception as e:
        print(f"❌ 唯一文件名生成测试失败: {str(e)}")
        raise


def test_chapter_file_creation():
    """测试章节文件创建"""
    print("测试章节文件创建...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 配置
            config = ProcessingConfig()
            config.output_dir = temp_dir
            config.generate_tags = True
            config.add_navigation = True
            
            file_generator = FileGenerator(config)
            
            # 创建章节信息
            chapter = ChapterInfo(
                title="第一章 政治学基础理论",
                start_line=1,
                end_line=100
            )
            
            # 章节内容
            content = """
# 第一章 政治学基础理论

政治学是研究政治现象的学科。本章将介绍政治学的基本概念、
研究方法和理论框架。

## 1.1 政治学的定义

政治学是一门社会科学，主要研究政治权力的分配、行使和制约。

## 1.2 研究方法

政治学采用多种研究方法，包括比较分析、案例研究等。
            """
            
            # 标签
            tags = ["政治学", "理论", "基础概念", "研究方法"]
            
            # 创建文件
            file_path = file_generator.create_chapter_file(chapter, content, tags)
            
            print(f"📄 章节文件已创建: {file_path}")
            
            # 验证文件存在
            assert Path(file_path).exists(), "章节文件应该存在"
            
            # 验证文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # 检查YAML前置元数据
            assert file_content.startswith("---"), "应包含YAML前置元数据"
            assert "tags:" in file_content, "应包含标签"
            assert "政治学" in file_content, "应包含标签内容"
            
            # 检查导航链接
            assert "返回目录" in file_content, "应包含导航链接"
            
            # 检查章节信息更新
            assert chapter.file_path, "章节信息应包含文件路径"
            
            print(f"  - 文件路径: {chapter.file_path}")
            print(f"  - 文件大小: {len(file_content)} 字符")
            
            print("✅ 章节文件创建测试通过")
            
        except Exception as e:
            print(f"❌ 章节文件创建测试失败: {str(e)}")
            raise


def test_section_file_creation():
    """测试小节文件创建"""
    print("测试小节文件创建...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 配置
            config = ProcessingConfig()
            config.output_dir = temp_dir
            config.generate_tags = True
            config.add_navigation = True
            
            file_generator = FileGenerator(config)
            
            # 创建小节信息
            section = SectionInfo(
                title="政治权力的概念",
                start_line=50,
                end_line=80,
                chapter_title="第一章 政治学基础理论",
                level=2
            )
            
            # 小节内容
            content = """
## 政治权力的概念

政治权力是政治学的核心概念，指在社会关系中影响他人行为的能力。

### 权力的特征

1. 强制性
2. 合法性
3. 相对性

### 权力的类型

- 政治权力
- 经济权力
- 文化权力
            """
            
            # 标签
            tags = ["政治权力", "权力概念", "政治学"]
            
            # 创建文件
            file_path = file_generator.create_section_file(section, content, tags)
            
            print(f"📄 小节文件已创建: {file_path}")
            
            # 验证文件存在
            assert Path(file_path).exists(), "小节文件应该存在"
            
            # 验证文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # 检查YAML前置元数据
            assert file_content.startswith("---"), "应包含YAML前置元数据"
            assert "tags:" in file_content, "应包含标签"
            assert "政治权力" in file_content, "应包含标签内容"
            
            # 检查导航链接
            assert "返回章节" in file_content, "应包含导航链接"
            assert "第一章 政治学基础理论" in file_content, "应包含章节标题"
            
            # 检查小节信息更新
            assert section.file_path, "小节信息应包含文件路径"
            
            print(f"  - 文件路径: {section.file_path}")
            print(f"  - 文件大小: {len(file_content)} 字符")
            
            print("✅ 小节文件创建测试通过")
            
        except Exception as e:
            print(f"❌ 小节文件创建测试失败: {str(e)}")
            raise


def test_file_content_generation():
    """测试文件内容生成"""
    print("测试文件内容生成...")
    
    try:
        config = ProcessingConfig()
        config.output_dir = "test_output"
        config.generate_tags = True
        config.add_navigation = True
        
        file_generator = FileGenerator(config)
        
        # 测试内容生成
        title = "测试标题"
        content = "这是测试内容"
        tags = ["测试", "标签"]
        
        # 生成文件内容
        generated_content = file_generator._generate_file_content(title, content, tags)
        
        print(f"📄 生成的文件内容预览:")
        print(generated_content[:200] + "...")
        
        # 验证内容结构
        assert generated_content.startswith("---"), "应包含YAML前置元数据"
        assert "title:" in generated_content, "应包含标题"
        assert "tags:" in generated_content, "应包含标签"
        assert "这是测试内容" in generated_content, "应包含内容"
        assert "返回目录" in generated_content, "应包含导航链接"
        
        # 测试无标签情况
        content_no_tags = file_generator._generate_file_content(title, content, [])
        assert "tags:" not in content_no_tags, "无标签时不应包含标签部分"
        
        # 测试无导航情况
        config.add_navigation = False
        content_no_nav = file_generator._generate_file_content(title, content, tags)
        assert "返回目录" not in content_no_nav, "无导航时不应包含导航链接"
        
        print("✅ 文件内容生成测试通过")
        
    except Exception as e:
        print(f"❌ 文件内容生成测试失败: {str(e)}")
        raise


def test_configuration_options():
    """测试配置选项"""
    print("测试配置选项...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 测试不同配置组合
            test_cases = [
                {"generate_tags": True, "add_navigation": True},
                {"generate_tags": False, "add_navigation": True},
                {"generate_tags": True, "add_navigation": False},
                {"generate_tags": False, "add_navigation": False},
            ]
            
            for i, case_config in enumerate(test_cases):
                print(f"\n🧪 测试配置组合 {i+1}:")
                print(f"  - 生成标签: {case_config['generate_tags']}")
                print(f"  - 添加导航: {case_config['add_navigation']}")
                
                config = ProcessingConfig()
                config.output_dir = temp_dir
                config.generate_tags = case_config['generate_tags']
                config.add_navigation = case_config['add_navigation']
                
                file_generator = FileGenerator(config)
                
                # 创建测试文件
                chapter = ChapterInfo(title="测试章节", start_line=1, end_line=10)
                content = "测试内容"
                tags = ["测试"]
                
                file_path = file_generator.create_chapter_file(chapter, content, tags)
                
                # 验证文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # 验证配置生效
                if case_config['generate_tags']:
                    assert "tags:" in file_content, "应包含标签"
                else:
                    assert "tags:" not in file_content, "不应包含标签"
                
                if case_config['add_navigation']:
                    assert "返回目录" in file_content, "应包含导航链接"
                else:
                    assert "返回目录" not in file_content, "不应包含导航链接"
                
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
        config.output_dir = "/invalid/path"  # 无效路径
        
        file_generator = FileGenerator(config)
        
        # 测试无效路径处理
        chapter = ChapterInfo(title="测试", start_line=1, end_line=10)
        
        try:
            file_generator.create_chapter_file(chapter, "内容")
            assert False, "应该在无效路径时抛出异常"
        except (OSError, IOError):
            print("✅ 无效路径错误处理正确")
        
        # 测试空内容处理
        config.output_dir = "test_output"
        file_path = file_generator.create_chapter_file(chapter, "")
        assert Path(file_path).exists(), "空内容文件应该被创建"
        
        print("✅ 错误处理测试通过")
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {str(e)}")
        raise


def main():
    """运行所有测试"""
    print("开始文件生成器测试...\n")
    
    try:
        test_filename_sanitization()
        print()
        test_unique_filename_generation()
        print()
        test_chapter_file_creation()
        print()
        test_section_file_creation()
        print()
        test_file_content_generation()
        print()
        test_configuration_options()
        print()
        test_error_handling()
        
        print("\n🎉 所有文件生成器测试通过!")
        print("文件生成器功能已正确实现。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()