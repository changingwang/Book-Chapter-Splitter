"""
文件名清理功能测试模块

测试FileGenerator类中的文件名清理功能，包括：
- 基本文件名清理
- 特殊字符处理
- 长度限制
- 中文标点符号处理
- 集成测试
"""

import os
import re
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_generator import FileGenerator
from src.config import ProcessingConfig


class TestFilenameCleaning:
    """文件名清理功能测试类"""

    def setup_method(self):
        """测试初始化"""
        config = ProcessingConfig()
        config.output_dir = "test_output"
        self.file_generator = FileGenerator(config)

    def test_basic_filename_cleaning(self):
        """测试基本文件名清理功能"""
        test_cases = [
            # 基本清理
            ("chapter 1", "chapter_1"),
            ("section 1.1", "section_1.1"),
            
            # 特殊字符清理
            ("chapter*1", "chapter_1"),
            ("section/1.1", "section_1.1"),
            ("file:name", "file_name"),
            ("question?mark", "question_mark"),
            
            # 中文标点清理
            ("第一章：引言", "第一章_引言"),
            ("第一节，概述", "第一节_概述"),
            ("标题（带括号）", "标题_带括号"),
            
            # 连续特殊字符处理
            ("file**name", "file_name"),
            ("chapter--1", "chapter_1"),
            
            # 开头结尾特殊字符
            ("-chapter-", "chapter"),
            ("_section_", "section"),
        ]
        
        for input_name, expected in test_cases:
            result = self.file_generator._clean_filename(input_name)
            assert result == expected, f"基本清理测试失败: '{input_name}' -> '{result}', 期望 '{expected}'"

    def test_chinese_punctuation_cleaning(self):
        """测试中文标点符号清理"""
        test_cases = [
            # 中文标点
            ("第一章：政治学导论", "第一章_政治学导论"),
            ("第一节，基本概念", "第一节_基本概念"),
            ("标题（包含说明）", "标题_包含说明"),
            ("小节"内容"", "小节_内容"),
            ("问题？答案！", "问题_答案"),
            
            # 混合标点
            ("Chapter 1: Introduction", "Chapter_1_Introduction"),
            ("Section 1.1, Overview", "Section_1.1_Overview"),
        ]
        
        for input_name, expected in test_cases:
            result = self.file_generator._clean_filename(input_name)
            assert result == expected, f"中文标点清理测试失败: '{input_name}' -> '{result}', 期望 '{expected}'"

    def test_length_limitation(self):
        """测试文件名长度限制"""
        # 超长文件名
        long_title = "A" * 200
        result = self.file_generator._clean_filename(long_title)
        
        # 应该被截断到合理长度
        assert len(result) <= 100, f"长度限制测试失败: {len(result)}"
        assert result.startswith("A"), "超长文件名开头部分应该保留"

    def test_empty_and_whitespace_cases(self):
        """测试空值和空白情况"""
        test_cases = [
            ("", "untitled"),
            ("   ", "untitled"),
            ("\t\n", "untitled"),
        ]
        
        for input_name, expected in test_cases:
            result = self.file_generator._clean_filename(input_name)
            assert result == expected, f"空值处理测试失败: '{input_name}' -> '{result}', 期望 '{expected}'"

    def test_new_format_cleaning(self):
        """测试新格式的文件名清理"""
        test_cases = [
            # 新格式章节标题
            ("第1章 政治学基础", "第1章_政治学基础"),
            ("第2章：权力理论", "第2章_权力理论"),
            ("第3章 国家与政府（上）", "第3章_国家与政府_上"),
            
            # 新格式小节标题
            ("1.1 基本概念", "1.1_基本概念"),
            ("2.1：权力定义", "2.1_权力定义"),
            ("3.1 国家理论（第一部分）", "3.1_国家理论_第一部分"),
            
            # 混合格式
            ("第一章 1.1 小节", "第一章_1.1_小节"),
        ]
        
        for input_name, expected in test_cases:
            result = self.file_generator._clean_filename(input_name)
            assert result == expected, f"新格式清理测试失败: '{input_name}' -> '{result}', 期望 '{expected}'"


def test_filename_cleaning_integration():
    """集成测试：文件名清理功能"""
    print("运行文件名清理功能集成测试...")

    config = ProcessingConfig()
    config.output_dir = "test_output"
    file_generator = FileGenerator(config)

    # 测试各种复杂情况
    complex_cases = [
        # 复杂章节标题
        ("第一章 政治学基础理论：概念与方法", "第一章_政治学基础理论概念与方法"),    

        # 复杂小节标题
        ("一、马克思主义政治学的基本特点", "01_马克思主义政治学的基本特点"),
        ("(1)政治形成一定的社会关系", "01_政治形成一定的社会关系"),

        # 包含多种特殊字符
        ("第二章：权力*理论*与**实践**", "第二章_权力理论与实践"),

        # 超长标题处理
        ("第三章 " + "政治学理论研究" * 10, None),  # 会被截断
    ]

    for input_title, expected in complex_cases:
        if "第" in input_title:
            result = file_generator._create_chapter_filename(input_title)
        else:
            result = file_generator._create_section_filename(input_title)

        if expected:
            assert result == expected, f"复杂情况测试失败: '{input_title}' -> '{result}'"
        else:
            # 验证长度限制
            assert len(result) <= 100, f"长度限制测试失败: {len(result)}"

        print(f"  ✓ '{input_title[:50]}...' -> '{result}'")

    print("✅ 文件名清理功能集成测试通过")


if __name__ == "__main__":
    # 运行集成测试
    test_filename_cleaning_integration()

    # 运行pytest测试
    pytest.main([__file__, "-v"])