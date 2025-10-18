"""
文件名唯一性测试模块

测试FileGenerator类中的文件名唯一性保证功能，包括：
- 基本唯一性处理
- 混合格式计数
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


class TestFilenameUniqueness:
    """文件名唯一性测试类"""

    def setup_method(self):
        """测试初始化"""
        config = ProcessingConfig()
        config.output_dir = "test_output"
        self.file_generator = FileGenerator(config)

    def test_basic_uniqueness(self):
        """测试基本唯一性处理"""
        base_name = "test_file"
        
        # 第一次生成
        result1 = self.file_generator._ensure_unique_filename(base_name)
        assert result1 == "test_file", "第一次生成应该使用基础名称"
        
        # 模拟文件已存在，再次生成
        result2 = self.file_generator._ensure_unique_filename(base_name)
        assert result2 == "test_file_2", "第二次生成应该添加序号"
        
        # 继续生成
        result3 = self.file_generator._ensure_unique_filename(base_name)
        assert result3 == "test_file_3", "第三次生成应该添加递增序号"
        
        # 验证所有结果都是唯一的
        results = [result1, result2, result3]
        assert len(set(results)) == len(results), "所有生成的文件名应该是唯一的"

    def test_different_base_names(self):
        """测试不同基础名称的唯一性处理"""
        base_names = ["chapter1", "section1", "appendix"]
        all_results = []
        
        for base in base_names:
            # 每个基础名称生成3个文件
            for i in range(3):
                result = self.file_generator._ensure_unique_filename(base)
                all_results.append(result)
                
                if i == 0:
                    assert result == base, f"{base} 第一次生成应该使用基础名称"
                else:
                    expected = f"{base}_{i+1}"
                    assert result == expected, f"{base} 第{i+1}次生成应该是 {expected}"
        
        # 验证所有生成的文件名都是唯一的
        assert len(set(all_results)) == len(all_results), "所有生成的文件名应该是唯一的"

    def test_edge_cases_uniqueness(self):
        """测试边界情况的唯一性处理"""
        # 空基础名称
        result = self.file_generator._ensure_unique_filename("")
        assert result.startswith("untitled"), "空基础名称应该生成默认文件名"
        
        # 包含特殊字符的基础名称
        result1 = self.file_generator._ensure_unique_filename("test*file")
        result2 = self.file_generator._ensure_unique_filename("test*file")
        
        assert result1 != result2, "相同基础名称应该生成不同的文件名"
        assert result2.endswith("_2"), "第二次生成应该添加序号"

    def test_mixed_format_counting(self):
        """测试混合格式的计数处理"""
        # 模拟混合格式的文件名生成
        test_cases = [
            "第一章_导论",
            "小节1_概念",
            "第一章_导论",  # 重复
            "小节2_方法",
            "第一章_导论",  # 再次重复
            "小节1_概念",  # 重复
        ]
        
        results = []
        for name in test_cases:
            result = self.file_generator._ensure_unique_filename(name)
            results.append(result)
        
        # 期望的结果
        expected = [
            "第一章_导论",
            "小节1_概念",
            "第一章_导论_2",
            "小节2_方法",
            "第一章_导论_3",
            "小节1_概念_2",
        ]
        
        assert results == expected, f"混合格式计数测试失败: {results}"


def test_filename_uniqueness_integration():
    """集成测试：文件名唯一性处理"""
    print("运行文件名唯一性处理集成测试...")

    config = ProcessingConfig()
    config.output_dir = "test_output"
    file_generator = FileGenerator(config)

    # 测试大量重复文件名
    base_names = ["政治学", "权力理论", "民主制度"]
    all_generated = []

    for base in base_names:
        print(f"  测试基础名称: {base}")
        for i in range(10):
            unique_name = file_generator._ensure_unique_filename(base)
            all_generated.append(unique_name)
            if i < 3:  # 只显示前几个
                print(f"    {i+1}: {unique_name}")

    # 验证所有生成的文件名都是唯一的
    assert len(set(all_generated)) == len(all_generated), "所有文件名应该是唯一的"   

    # 验证每个基础名称的计数正确
    for base in base_names:
        base_files = [name for name in all_generated if name.startswith(base)]       
        assert len(base_files) == 10, f"{base} 应该有10个文件"

        # 验证第一个文件没有后缀
        assert f"{base}.md" in base_files, f"{base} 的第一个文件应该没有后缀"       

        # 验证后续文件有正确的数字后缀
        for i in range(2, 11):
            expected = f"{base}_{i}.md"
            assert expected in base_files, f"应该包含 {expected}"

    print(f"  ✓ 生成了 {len(all_generated)} 个唯一文件名")
    print("✅ 文件名唯一性处理集成测试通过")


if __name__ == "__main__":
    # 运行集成测试
    test_filename_uniqueness_integration()

    # 运行pytest测试
    pytest.main([__file__, "-v"])