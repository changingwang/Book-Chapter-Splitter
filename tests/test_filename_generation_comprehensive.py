"""
综合文件名生成测试模块

测试FileGenerator类中的综合文件名生成功能，包括：
- 章节文件名生成
- 小节文件名生成  
- 唯一性保证
- 真实场景测试
"""

import os
import re
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_generator import FileGenerator
from src.config import ProcessingConfig


class TestComprehensiveFilenameGeneration:
    """综合文件名生成测试类"""

    def setup_method(self):
        """测试初始化"""
        config = ProcessingConfig()
        config.output_dir = "test_output"
        self.file_generator = FileGenerator(config)

    def test_chapter_filename_generation(self):
        """测试章节文件名生成"""
        test_cases = [
            # 传统格式
            ("第一章 政治学导论", "第一章_政治学导论"),
            ("第二章：权力理论", "第二章_权力理论"),
            ("第三章 国家与政府", "第三章_国家与政府"),
            
            # 新格式
            ("第1章 政治学基础", "第1章_政治学基础"),
            ("第2章：研究方法", "第2章_研究方法"),
            ("第3章 政治文化", "第3章_政治文化"),
            
            # 包含特殊内容
            ("第四章 政治参与（上）", "第四章_政治参与_上"),
            ("第五章：利益集团*理论", "第五章_利益集团理论"),
            ("第六章 政党制度/选举制度", "第六章_政党制度选举制度"),
            
            # 超长标题
            ("第七章 " + "政治学理论" * 5, None),  # 会被截断
        ]
        
        for input_title, expected in test_cases:
            result = self.file_generator._create_chapter_filename(input_title)
            
            if expected:
                assert result == expected, f"章节文件名生成失败: '{input_title}' -> '{result}', 期望 '{expected}'"
            else:
                # 验证长度限制
                assert len(result) <= 100, f"长度限制测试失败: {len(result)}"

    def test_section_filename_generation(self):
        """测试小节文件名生成"""
        test_cases = [
            # 传统格式 - 中文数字
            ("一、政治的本质", 1, 1, "11_一政治的本质"),
            ("二、政治的特征", 1, 2, "12_二政治的特征"),
            ("三、政治的功能", 1, 3, "13_三政治的功能"),
            
            # 传统格式 - 带括号
            ("(一)政治权力", 2, 1, "21_一政治权力"),
            ("(二)政治权利", 2, 2, "22_二政治权利"),
            ("(三)政治权威", 2, 3, "23_三政治权威"),
            
            # 数字格式
            ("1、基本概念", 3, 1, "31_1基本概念"),
            ("2、理论框架", 3, 2, "32_2理论框架"),
            ("3、研究方法", 3, 3, "33_3研究方法"),
            
            # 新格式
            ("1.1 政治学定义", 1, 1, "11_1.1_政治学定义"),
            ("1.2：研究范围", 1, 2, "12_1.2_研究范围"),
            ("1.3 学科特点", 1, 3, "13_1.3_学科特点"),
            
            # 包含特殊内容
            ("一、马克思主义*政治学", 4, 1, "41_一马克思主义政治学"),
            ("二、行为主义/政治学", 4, 2, "42_二行为主义政治学"),
            ("三、制度分析（新制度主义）", 4, 3, "43_三制度分析新制度主义"),
        ]
        
        for input_title, chapter_num, section_num, expected in test_cases:
            result = self.file_generator._create_section_filename(input_title, chapter_num, section_num)
            assert result == expected, f"小节文件名生成失败: '{input_title}' -> '{result}', 期望 '{expected}'"

    def test_filename_uniqueness(self):
        """测试文件名唯一性保证"""
        base_name = "test_chapter"
        
        # 模拟多次生成相同基础文件名
        generated_names = []
        for i in range(5):
            unique_name = self.file_generator._ensure_unique_filename(base_name)
            generated_names.append(unique_name)
            
            # 验证格式
            if i == 0:
                assert unique_name == base_name, "第一次生成应该使用基础名称"
            else:
                assert unique_name.startswith(base_name + "_"), f"重复文件名格式错误: {unique_name}"
                assert unique_name.endswith(str(i)), f"重复文件名序号错误: {unique_name}"
        
        # 验证所有生成的文件名都是唯一的
        assert len(set(generated_names)) == len(generated_names), "生成的文件名应该都是唯一的"

    def test_edge_cases(self):
        """测试边界情况"""
        # 空标题
        result = self.file_generator._create_chapter_filename("")
        assert result.startswith("untitled"), "空标题应该生成默认文件名"
        
        # 纯特殊字符
        result = self.file_generator._create_section_filename("***", 1, 1)
        assert result.startswith("11"), "纯特殊字符应该生成有效文件名"
        
        # 超长章节编号
        result = self.file_generator._create_section_filename("测试", 999, 999)
        assert result.startswith("999999"), "超长编号处理错误"


def test_comprehensive_filename_generation():
    """综合测试：文件名生成功能"""
    print("运行文件名生成功能综合测试...")

    config = ProcessingConfig()
    config.output_dir = "test_output"
    file_generator = FileGenerator(config)

    # 真实场景测试用例
    real_world_cases = [
        # 章节测试 - 实际格式
        ("第一章 马克思主义政治学的基本特点", "第一章_马克思主义政治学的基本特点"),  
        ("第二章 政治学研究的对象和方法", "第二章_政治学研究的对象和方法"),

        # 小节测试 - 实际格式
        ("一、政治形成一定的社会关系", 1, 1, "11_一政治形成一定的社会关系"),
        ("二、政治是一种社会现象", 1, 2, "12_二政治是一种社会现象"),
        ("(一)政治的本质特征", 2, 1, "21_一政治的本质特征"),
        ("(二)政治的功能作用", 2, 2, "22_二政治的功能作用"),
        ("1、基本概念界定", 3, 1, "31_1基本概念界定"),
        ("2、理论框架构建", 3, 2, "32_2理论框架构建"),
    ]

    print("  测试真实场景文件名生成:")
    for case in real_world_cases:
        if len(case) == 2:  # 章节格式
            input_title, expected = case
            result = file_generator._create_chapter_filename(input_title)
        else:  # 小节格式
            input_title, chapter_num, section_num, expected = case
            result = file_generator._create_section_filename(input_title, chapter_num, section_num)

        assert result == expected, f"真实场景测试失败: '{input_title}' -> '{result}'"
        print(f"    ✓ '{input_title}' -> '{result}'")

    # 测试唯一性
    print("  测试文件名唯一性:")
    duplicate_base = "第一章_政治学基础"
    unique_names = []
    for i in range(3):
        unique_name = file_generator._ensure_unique_filename(duplicate_base)
        unique_names.append(unique_name)
        print(f"    {i+1}: {unique_name}")

    assert len(set(unique_names)) == len(unique_names), "文件名应该是唯一的"

    print("✅ 文件名生成综合测试通过")


if __name__ == "__main__":
    # 运行综合测试
    test_comprehensive_filename_generation()

    # 运行pytest测试
    pytest.main([__file__, "-v"])