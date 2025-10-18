#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
书籍章节拆分器 - 主处理模块

此模块包含主要的BookSplitter类，负责协调整个处理流程。
"""

import os
import time
import logging
from pathlib import Path

from .config import ProcessingConfig
from .analyzers.structure_analyzer import StructureAnalyzer
from .extractors.content_extractor import ContentExtractor
from .generators.file_generator import FileGenerator
from .generators.tag_generator import TagGenerator
from .managers.link_manager import LinkManager

class BookSplitter:
    """书籍章节拆分器主类"""
    
    def __init__(self, config=None):
        """初始化拆分器
        
        Args:
            config (ProcessingConfig, optional): 处理配置对象
        """
        self.config = config or ProcessingConfig()
        self.logger = logging.getLogger(__name__)
        
    def process(self):
        """处理单个文件
        
        Returns:
            dict: 处理结果信息
        """
        start_time = time.time()
        
        try:
            # 确保输出目录存在
            os.makedirs(self.config.output_dir, exist_ok=True)
            os.makedirs(os.path.join(self.config.output_dir, "chapters"), exist_ok=True)
            
            if self.config.create_sections:
                os.makedirs(os.path.join(self.config.output_dir, "sections"), exist_ok=True)
            
            # 分析文档结构
            analyzer = StructureAnalyzer(self.config)
            structure = analyzer.analyze(self.config.source_file)
            
            if not structure['chapters']:
                return {
                    'status': 'error',
                    'error': '未找到有效的章节结构',
                    'elapsed_time': time.time() - start_time
                }
            
            # 提取内容
            extractor = ContentExtractor(self.config)
            content = extractor.extract(self.config.source_file, structure)
            
            # 生成标签（如果启用）
            if self.config.generate_tags:
                tag_generator = TagGenerator(self.config)
                content = tag_generator.generate_tags(content)
            
            # 管理链接（如果启用）
            if self.config.add_navigation:
                link_manager = LinkManager(self.config)
                content = link_manager.add_navigation(content)
            
            # 生成文件
            file_generator = FileGenerator(self.config)
            result = file_generator.generate_files(content)
            
            # 添加处理时间
            elapsed_time = time.time() - start_time
            result['elapsed_time'] = elapsed_time
            
            return result
            
        except Exception as e:
            self.logger.exception("处理过程中发生错误")
            return {
                'status': 'error',
                'error': str(e),
                'elapsed_time': time.time() - start_time
            }
    
    def process_batch(self, file_list, output_base_dir=None):
        """批量处理多个文件
        
        Args:
            file_list (list): 要处理的文件路径列表
            output_base_dir (str, optional): 输出的基础目录
            
        Returns:
            dict: 每个文件的处理结果
        """
        results = {}
        original_output_dir = self.config.output_dir
        
        for file_path in file_list:
            file_name = Path(file_path).stem
            
            if output_base_dir:
                self.config.output_dir = os.path.join(output_base_dir, file_name)
            else:
                self.config.output_dir = os.path.join(original_output_dir, file_name)
                
            self.config.source_file = file_path
            result = self.process()
            results[file_path] = result['status'] == 'success'
        
        # 恢复原始输出目录
        self.config.output_dir = original_output_dir
        
        return results
