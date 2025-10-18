# -*- coding: utf-8 -*-
"""
集成测试
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from src.book_splitter import BookSplitter, ProcessingConfig

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def create_test_file(directory, content):
    """创建测试文件"""
    test_file = os.path.join(directory, "test_book.md")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(content)
    return test_file

def test_end_to_end_processing(temp_dir):
    """端到端处理测试"""
    # 创建测试内容
    test_content = """
# 测试文档

# 第一章 介绍

这是介绍章节的内容。

一、背景

这是背景小节的内容。

二、目标

这是目标小节的内容。

# 第二章 方法

这是方法章节的内容。

一、研究方法

这是研究方法小节的内容。

二、分析方法

这是分析方法小节的内容。
"""
    
    # 创建测试文件
    test_file = create_test_file(temp_dir, test_content)
    
    # 创建配置
    config = ProcessingConfig()
    config.source_file = test_file
    config.output_dir = os.path.join(temp_dir, "output")
    config.create_sections = True
    config.generate_tags = False  # 禁用标签生成以简化测试
    config.add_navigation = True
    
    # 处理文件
    splitter = BookSplitter(config)
    result = splitter.process()
    
    # 验证结果
    assert result['status'] == 'success'
    assert result['chapters_count'] == 2
    assert result['sections_count'] == 4
    assert result['generated_files_count'] == 7  # 目录 + 2章 + 4节
    
    # 验证文件生成
    assert os.path.exists(os.path.join(config.output_dir, "目录.md"))
    assert os.path.exists(os.path.join(config.output_dir, "chapters", "第一章_介绍.md"))
    assert os.path.exists(os.path.join(config.output_dir, "chapters", "第二章_方法.md"))
    assert os.path.exists(os.path.join(config.output_dir, "sections", "1.1_背景.md"))
    assert os.path.exists(os.path.join(config.output_dir, "sections", "1.2_目标.md"))
    assert os.path.exists(os.path.join(config.output_dir, "sections", "2.1_研究方法.md"))
    assert os.path.exists(os.path.join(config.output_dir, "sections", "2.2_分析方法.md"))
