#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
书籍章节拆分器 - 配置模块

此模块包含处理配置类，用于管理拆分器的各种设置。
"""

import os
import json
import yaml
import logging

class ProcessingConfig:
    """处理配置类"""
    
    def __init__(self, config_file=None):
        """初始化配置
        
        Args:
            config_file (str, optional): 配置文件路径
        """
        # 默认配置
        self.source_file = "full.md"
        self.output_dir = "output"
        self.create_sections = True
        self.generate_tags = True
        self.add_navigation = True
        self.preserve_images = True
        self.min_tags_per_section = 3
        self.max_tags_per_section = 8
        self.filename_separator = "_"
        
        # 如果提供了配置文件，则加载它
        if config_file:
            self.load_config(config_file)
            
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_file):
        """从文件加载配置
        
        Args:
            config_file (str): 配置文件路径
            
        Raises:
            ValueError: 如果配置文件格式不受支持
        """
        if not os.path.exists(config_file):
            self.logger.warning(f"配置文件 {config_file} 不存在，使用默认配置")
            return
        
        file_ext = os.path.splitext(config_file)[1].lower()
        
        try:
            if file_ext == '.json':
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            elif file_ext in ['.yaml', '.yml']:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {file_ext}")
                
            # 更新配置
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    
        except Exception as e:
            self.logger.error(f"加载配置文件时出错: {str(e)}")
            raise
    
    def to_dict(self):
        """将配置转换为字典
        
        Returns:
            dict: 配置字典
        """
        return {
            'source_file': self.source_file,
            'output_dir': self.output_dir,
            'create_sections': self.create_sections,
            'generate_tags': self.generate_tags,
            'add_navigation': self.add_navigation,
            'preserve_images': self.preserve_images,
            'min_tags_per_section': self.min_tags_per_section,
            'max_tags_per_section': self.max_tags_per_section,
            'filename_separator': self.filename_separator
        }
    
    def save_config(self, config_file):
        """保存配置到文件
        
        Args:
            config_file (str): 配置文件路径
            
        Raises:
            ValueError: 如果配置文件格式不受支持
        """
        file_ext = os.path.splitext(config_file)[1].lower()
        config_data = self.to_dict()
        
        try:
            if file_ext == '.json':
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
            elif file_ext in ['.yaml', '.yml']:
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
            else:
                raise ValueError(f"不支持的配置文件格式: {file_ext}")
                
        except Exception as e:
            self.logger.error(f"保存配置文件时出错: {str(e)}")
            raise
