# -*- coding: utf-8 -*-
"""
基础功能测试
"""

import os
import pytest
from src.book_splitter import BookSplitter, ProcessingConfig

def test_config_initialization():
    """测试配置初始化"""
    config = ProcessingConfig()
    assert config.source_file == "full.md"
    assert config.output_dir == "output"
    assert config.create_sections == True
    assert config.generate_tags == True
    assert config.add_navigation == True

def test_config_to_dict():
    """测试配置转换为字典"""
    config = ProcessingConfig()
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert config_dict['source_file'] == "full.md"
    assert config_dict['output_dir'] == "output"
    assert config_dict['create_sections'] == True

def test_splitter_initialization():
    """测试拆分器初始化"""
    splitter = BookSplitter()
    assert splitter.config is not None
    assert splitter.config.source_file == "full.md"
