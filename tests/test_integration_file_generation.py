"""
文件生成集成测试模块

测试FileGenerator类中的文件生成集成功能，包括：
- 完整文件生成流程
- 目录结构创建
- 文件名格式验证
- 统计信息收集
"""

import os
import re
import pytest
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_generator import FileGenerator
from src.config import ProcessingConfig


class TestIntegrationFileGeneration:
    """文件生成集成测试类"""

    def setup_method(self):
        """测试初始化"""
        self.test_dir = tempfile.mkdtemp()
        config = ProcessingConfig()
        config.output_dir = self.test_dir
        self.file_generator = FileGenerator(config)

    def teardown_method(self):
        """测试清理"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_complete_file_generation_workflow(self):
        """测试完整的文件生成工作流程"""
        # 模拟章节和小节数据
        chapter_data = [
            {
                'title': '第一章 马克思主义政治学的基本特点',
                'content': '马克思主义政治学的基本特点内容...',
                'sections': [
                    {
                        'title': '一、政治形成一定的社会关系',
                        'content': '政治形成一定的社会关系的详细内容...',
                        'tags': ['政治学', '马克思主义']
                    },
                    {
                        'title': '二、政治是一种社会现象',
                        'content': '政治是一种社会现象的详细内容...',
                        'tags': ['政治学', '社会现象']
                    }
                ]
            },
            {
                'title': '第二章 政治学研究的对象和方法',
                'content': '政治学研究的对象和方法内容...',
                'sections': [
                    {
                        'title': '1、研究对象界定',
                        'content': '研究对象界定的详细内容...',
                        'tags': ['政治学', '研究方法']
                    },
                    {
                        'title': '2、研究方法论',
                        'content': '研究方法论的详细内容...',
                        'tags': ['政治学', '方法论']
                    }
                ]
            }
        ]

        generated_files = []
        section_counters = {}

        # 生成目录文件
        toc_path = self.file_generator.generate_toc_file(chapter_data)
        generated_files.append(toc_path)
        assert os.path.exists(toc_path), "目录文件应该被创建"

        # 生成章节和小节文件
        for chapter_num, chapter_info in enumerate(chapter_data, 1):
            # 生成章节文件
            chapter_path = self.file_generator.generate_chapter_file(
                chapter_info['title'], chapter_info['content'], 
                chapter_info.get('tags', []), chapter_num
            )
            generated_files.append(chapter_path)
            assert os.path.exists(chapter_path), "章节文件应该被创建"

            # 初始化章节计数器
            section_counters[chapter_num] = 0

            # 生成小节文件
            for section_info in chapter_info['sections']:
                section_counters[chapter_num] += 1
                section_path = self.file_generator.generate_section_file(
                    section_info['title'], section_info['content'],
                    section_info.get('tags', []), chapter_num, 
                    section_counters[chapter_num]
                )
                generated_files.append(section_path)
                assert os.path.exists(section_path), "小节文件应该被创建"

        # 验证生成的文件数量
        assert len(generated_files) == 7, f"应该生成7个文件，实际{len(generated_files)}个"

        # 验证文件内容
        for file_path in generated_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, "文件内容不应该为空"
                # 验证包含YAML front matter
                assert '---' in content, "文件应该包含YAML front matter"

        # 验证统计信息
        stats = self.file_generator.get_statistics()
        assert stats['generated_files_count'] == 7, "统计信息应该正确"
        assert stats['chapters_count'] == 2, "应该有2个章节"
        assert stats['sections_count'] == 4, "应该有4个小节"


def test_integration_file_generation():
    """集成测试：文件生成功能"""
    print("运行文件生成功能集成测试...")

    # 创建临时目录
    test_dir = tempfile.mkdtemp()
    try:
        config = ProcessingConfig()
        config.output_dir = test_dir
        file_generator = FileGenerator(config)

        # 模拟真实书籍结构
        book_structure = [
            {
                'title': '第一章 马克思主义政治学的基本特点',
                'content': '本章介绍马克思主义政治学的基本特点...',
                'sections': [
                    {
                        'title': '一、政治形成一定的社会关系',
                        'content': '政治形成一定的社会关系的详细内容...',
                        'tags': ['政治学', '马克思主义']
                    },
                    {
                        'title': '二、政治是一种社会现象', 
                        'content': '政治是一种社会现象的详细内容...',
                        'tags': ['政治学', '社会现象']
                    }
                ]
            },
            {
                'title': '第二章 政治学研究的对象和方法',
                'content': '本章介绍政治学研究的对象和方法...',
                'sections': [
                    {
                        'title': '1、研究对象界定',
                        'content': '研究对象界定的详细内容...',
                        'tags': ['政治学', '研究方法']
                    },
                    {
                        'title': '2、研究方法论',
                        'content': '研究方法论的详细内容...',
                        'tags': ['政治学', '方法论']
                    }
                ]
            }
        ]

        generated_files = []
        section_counters = {}

        # 生成目录
        toc_path = file_generator.generate_toc_file(book_structure)
        generated_files.append(toc_path)
        print(f"  ✓ 生成目录: {Path(toc_path).name}")

        # 生成章节和小节
        for chapter_num, chapter_info in enumerate(book_structure, 1):
            title = chapter_info['title']
            
            # 生成章节文件
            chapter_path = file_generator.generate_chapter_file(
                title, chapter_info['content'], 
                chapter_info.get('tags', []), chapter_num
            )
            generated_files.append(chapter_path)
            print(f"  ✓ 章节: {Path(chapter_path).name}")

            # 初始化章节计数器
            section_counters[chapter_num] = 0

            # 生成小节文件
            for section_info in chapter_info['sections']:
                section_counters[chapter_num] += 1
                section_title = section_info['title']
                
                section_path = file_generator.generate_section_file(
                    section_title, section_info['content'],
                    section_info.get('tags', []), chapter_num, 
                    section_counters[chapter_num]
                )
                generated_files.append(section_path)
                print(f"    ✓ 小节: {Path(section_path).name}")

        # 验证生成结果
        assert len(generated_files) == 7, f"应该生成7个文件，实际{len(generated_files)}个"

        # 验证文件名格式
        filenames = [Path(f).name for f in generated_files]

        # 验证章节文件名
        chapter_files = [f for f in filenames if f.startswith("第")]
        expected_chapters = [
            "第一章_马克思主义政治学的基本特点.md",
            "第二章_政治学研究的对象和方法.md"
        ]

        for expected in expected_chapters:
            assert expected in chapter_files, f"缺少章节文件: {expected}"

        # 验证小节文件名 - XY格式
        section_files = [f for f in filenames if not f.startswith("第") and not f.startswith("目录")]
        expected_sections = [
            "11_一政治形成一定的社会关系.md",
            "12_二政治是一种社会现象.md",
            "21_1研究对象界定.md",
            "22_2研究方法论.md"
        ]

        for expected in expected_sections:
            assert expected in section_files, f"缺少小节文件: {expected}"

        # 验证统计信息
        stats = file_generator.get_statistics()
        assert stats['generated_files_count'] == 7, "统计信息应正确"

        print(f"  ✓ 成功生成 {len(generated_files)} 个文件")
        print(f"  ✓ 文件名格式符合规范")
        print(f"  ✓ 目录结构正确")

    finally:
        # 清理临时目录
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

    print("✅ 文件生成集成测试通过")


if __name__ == "__main__":
    # 运行集成测试
    test_integration_file_generation()

    # 运行pytest测试
    pytest.main([__file__, "-v"])