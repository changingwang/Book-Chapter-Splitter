"""
主控制器模块

BookSplitter主类，整合所有组件的处理流程。
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import time

from .config import ProcessingConfig
from .models import ChapterInfo, SectionInfo
from .analyzers import StructureAnalyzer
from .extractors import ContentExtractor
from .generators import TagGenerator, FileGenerator
from .managers import LinkManager


class BookSplitter:
    """书籍拆分器主控制器"""
    
    def __init__(self, config: ProcessingConfig):
        """初始化书籍拆分器
        
        Args:
            config: 处理配置对象
        """
        self.config = config
        self.config.validate()
        
        # 初始化日志
        self._setup_logging()
        
        # 初始化所有组件
        self._initialize_components()
        
        self.logger.info(f"BookSplitter初始化完成，源文件: {config.source_file}")
    
    def _setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize_components(self):
        """初始化所有处理组件"""
        try:
            self.logger.info("初始化处理组件...")
            
            # 延迟初始化，在process方法中检查文件存在性
            self.structure_analyzer = None
            self.content_extractor = None
            
            # 初始化标签生成器（如果启用）
            if self.config.generate_tags:
                self.tag_generator = TagGenerator(
                    min_tags=self.config.min_tags_per_section,
                    max_tags=self.config.max_tags_per_section
                )
            else:
                self.tag_generator = None
            
            # 初始化文件生成器
            self.file_generator = FileGenerator(self.config)
            
            # 初始化链接管理器
            self.link_manager = LinkManager(self.config)
            
            self.logger.info("基础组件初始化完成")
            
        except Exception as e:
            self.logger.error(f"组件初始化失败: {str(e)}")
            raise
    
    def _initialize_file_components(self):
        """初始化依赖文件的组件"""
        if self.structure_analyzer is None:
            self.structure_analyzer = StructureAnalyzer(self.config.source_file)
        
        if self.content_extractor is None:
            self.content_extractor = ContentExtractor(self.config.source_file)
    
    def process(self) -> Dict[str, any]:
        """执行完整的书籍拆分处理流程
        
        Returns:
            处理结果统计信息
        """
        start_time = time.time()
        self.logger.info("开始处理书籍拆分...")
        
        try:
            # 检查源文件是否存在
            source_path = Path(self.config.source_file)
            if not source_path.exists():
                raise FileNotFoundError(f"源文件不存在: {self.config.source_file}")
            
            # 创建输出目录
            self._create_output_directories()
            
            # 初始化依赖文件的组件
            self._initialize_file_components()
            
            # 步骤1: 结构分析
            self.logger.info("步骤1: 分析文档结构...")
            structure_result = self.structure_analyzer.analyze_structure()
            chapters = structure_result['chapters']
            sections = structure_result['sections']
            
            self.logger.info(f"结构分析完成: 发现 {len(chapters)} 个章节，{len(sections)} 个小节")
            
            if not chapters:
                raise ValueError("未找到有效的章节结构，请检查文档格式")
            
            # 步骤2: 内容提取和文件生成
            self.logger.info("步骤2: 提取内容并生成文件...")
            generated_files = self._process_chapters_and_sections(chapters, sections)
            
            # 步骤3: 生成目录和链接
            self.logger.info("步骤3: 生成目录和导航链接...")
            toc_path = self.link_manager.save_toc(chapters, sections)
            
            # 步骤4: 添加导航链接
            if self.config.add_navigation:
                self.logger.info("步骤4: 添加导航链接...")
                self._add_navigation_to_files(generated_files)
            
            # 步骤5: 验证结果
            self.logger.info("步骤5: 验证处理结果...")
            validation_result = self._validate_results(chapters, sections)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 构建结果
            result = {
                'status': 'success',
                'source_file': self.config.source_file,
                'output_dir': self.config.output_dir,
                'toc_file': toc_path,
                'chapters_count': len(chapters),
                'sections_count': len(sections),
                'generated_files_count': len(generated_files),
                'processing_time': round(processing_time, 2),
                'validation': validation_result,
                'statistics': self._get_processing_statistics(chapters, sections),
                'message': '处理完成'
            }
            
            self.logger.info(f"书籍拆分处理完成，耗时 {processing_time:.2f} 秒")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"处理过程中发生错误: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': round(processing_time, 2),
                'message': '处理失败'
            }
    
    def _process_chapters_and_sections(self, chapters: List[ChapterInfo], 
                                     sections: List[SectionInfo]) -> List[str]:
        """处理章节和小节，生成文件
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表
            
        Returns:
            生成的文件路径列表
        """
        generated_files = []
        
        # 处理章节
        self.logger.info(f"处理 {len(chapters)} 个章节...")
        for i, chapter in enumerate(chapters, 1):
            try:
                # 提取章节内容
                chapter_content = self.content_extractor.extract_chapter_content(chapter)
                
                # 处理图片（如果启用）
                if self.config.preserve_images:
                    source_dir = Path(self.config.source_file).parent
                    chapter_content = self.file_generator.process_images(chapter_content, source_dir)
                
                # 生成标签（如果启用）
                chapter_tags = None
                if self.config.generate_tags and self.tag_generator:
                    chapter_tags = self.tag_generator.generate_tags(chapter_content, chapter.title)
                
                # 创建章节文件
                chapter_file = self.file_generator.create_chapter_file(
                    chapter, chapter_content, chapter_tags
                )
                generated_files.append(chapter_file)
                
                self.logger.debug(f"章节 {i}/{len(chapters)} 处理完成: {chapter.title}")
                
            except Exception as e:
                self.logger.error(f"处理章节 '{chapter.title}' 失败: {str(e)}")
                # 继续处理其他章节
                continue
        
        # 处理小节（如果启用）
        if self.config.create_sections and sections:
            self.logger.info(f"处理 {len(sections)} 个小节...")
            
            # 为每个章节的小节建立索引
            chapter_section_counters = {}
            
            for i, section in enumerate(sections, 1):
                try:
                    # 计算小节在其章节中的序号
                    chapter_title = section.chapter_title
                    if chapter_title not in chapter_section_counters:
                        chapter_section_counters[chapter_title] = 0
                    chapter_section_counters[chapter_title] += 1
                    section_index = chapter_section_counters[chapter_title]
                    
                    # 提取小节内容
                    section_content = self.content_extractor.extract_section_content(section)
                    
                    # 处理图片（如果启用）
                    if self.config.preserve_images:
                        source_dir = Path(self.config.source_file).parent
                        section_content = self.file_generator.process_images(section_content, source_dir)
                    
                    # 生成标签（如果启用）
                    section_tags = None
                    if self.config.generate_tags and self.tag_generator:
                        section_tags = self.tag_generator.generate_tags(section_content, section.title)
                        # 更新小节的标签信息
                        section.add_tags(section_tags)
                    
                    # 创建小节文件，传递小节序号
                    section_file = self.file_generator.create_section_file(
                        section, section_content, section_tags, section_index
                    )
                    generated_files.append(section_file)
                    
                    self.logger.debug(f"小节 {i}/{len(sections)} 处理完成: {section.title}")
                    
                except Exception as e:
                    self.logger.error(f"处理小节 '{section.title}' 失败: {str(e)}")
                    # 继续处理其他小节
                    continue
        
        return generated_files
    
    def _add_navigation_to_files(self, file_paths: List[str]):
        """为生成的文件添加导航链接
        
        Args:
            file_paths: 文件路径列表
        """
        for file_path in file_paths:
            try:
                self.link_manager.add_navigation_links(file_path)
            except Exception as e:
                self.logger.warning(f"添加导航链接失败 '{file_path}': {str(e)}")
                # 继续处理其他文件
                continue
    
    def _validate_results(self, chapters: List[ChapterInfo], 
                         sections: List[SectionInfo]) -> Dict[str, any]:
        """验证处理结果
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表
            
        Returns:
            验证结果
        """
        try:
            # 验证链接有效性
            link_validation = self.link_manager.validate_links(chapters, sections)
            
            # 验证文件生成统计
            file_stats = self.file_generator.get_statistics()
            
            # 验证结构分析统计
            structure_stats = self.structure_analyzer.get_statistics()
            
            # 检查结构问题
            structure_issues = self.structure_analyzer.validate_structure()
            
            return {
                'links': link_validation,
                'files': file_stats,
                'structure': structure_stats,
                'issues': structure_issues,
                'valid': len(structure_issues) == 0 and len(link_validation['missing_files']) == 0
            }
            
        except Exception as e:
            self.logger.warning(f"验证过程中发生错误: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _get_processing_statistics(self, chapters: List[ChapterInfo], 
                                 sections: List[SectionInfo]) -> Dict[str, any]:
        """获取处理统计信息
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表
            
        Returns:
            统计信息
        """
        try:
            stats = {
                'source_file_size': Path(self.config.source_file).stat().st_size,
                'total_lines': sum(chapter.line_count for chapter in chapters),
                'average_chapter_length': (
                    sum(chapter.line_count for chapter in chapters) / len(chapters)
                    if chapters else 0
                ),
                'chapters_with_sections': len([c for c in chapters if c.has_sections]),
                'sections_by_level': {},
                'total_tags': 0,
                'unique_tags': 0
            }
            
            # 小节级别统计
            if sections:
                for section in sections:
                    level = section.level
                    stats['sections_by_level'][level] = stats['sections_by_level'].get(level, 0) + 1
            
            # 标签统计
            if self.config.generate_tags and sections:
                all_tags = []
                for section in sections:
                    all_tags.extend(section.tags)
                stats['total_tags'] = len(all_tags)
                stats['unique_tags'] = len(set(all_tags))
            
            # 组件统计
            if self.tag_generator:
                stats['tag_generator'] = self.tag_generator.get_statistics()
            
            if self.file_generator:
                stats['file_generator'] = self.file_generator.get_statistics()
            
            if self.link_manager:
                stats['link_manager'] = self.link_manager.get_statistics()
            
            return stats
            
        except Exception as e:
            self.logger.warning(f"获取统计信息失败: {str(e)}")
            return {'error': str(e)}
    
    def _create_output_directories(self):
        """创建输出目录结构"""
        directories = [
            self.config.output_dir,
            self.config.chapters_dir,
            self.config.sections_dir,
            self.config.images_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"创建目录: {directory}")
    
    def get_status(self) -> Dict[str, any]:
        """获取当前处理状态"""
        return {
            'config': {
                'source_file': self.config.source_file,
                'output_dir': self.config.output_dir,
                'create_sections': self.config.create_sections,
                'generate_tags': self.config.generate_tags,
                'add_navigation': self.config.add_navigation,
                'preserve_images': self.config.preserve_images
            },
            'components_initialized': {
                'structure_analyzer': self.structure_analyzer is not None,
                'content_extractor': self.content_extractor is not None,
                'file_generator': self.file_generator is not None,
                'link_manager': self.link_manager is not None,
                'tag_generator': self.tag_generator is not None
            },
            'source_file_exists': Path(self.config.source_file).exists(),
            'output_dir_exists': Path(self.config.output_dir).exists()
        }
    
    def process_preview(self) -> Dict[str, any]:
        """预览处理结果，不实际生成文件
        
        Returns:
            预览结果
        """
        try:
            self.logger.info("开始预览处理...")
            
            # 检查源文件
            source_path = Path(self.config.source_file)
            if not source_path.exists():
                raise FileNotFoundError(f"源文件不存在: {self.config.source_file}")
            
            # 初始化依赖文件的组件
            self._initialize_file_components()
            
            # 仅进行结构分析
            structure_result = self.structure_analyzer.analyze_structure()
            chapters = structure_result['chapters']
            sections = structure_result['sections']
            
            # 获取统计信息
            structure_stats = self.structure_analyzer.get_statistics()
            structure_issues = self.structure_analyzer.validate_structure()
            
            return {
                'status': 'success',
                'preview': True,
                'chapters_count': len(chapters),
                'sections_count': len(sections),
                'chapters': [
                    {
                        'title': chapter.title,
                        'start_line': chapter.start_line,
                        'end_line': chapter.end_line,
                        'line_count': chapter.line_count,
                        'sections_count': len(chapter.sections)
                    }
                    for chapter in chapters[:10]  # 限制预览数量
                ],
                'sections': [
                    {
                        'title': section.title,
                        'chapter_title': section.chapter_title,
                        'level': section.level,
                        'start_line': section.start_line,
                        'end_line': section.end_line,
                        'line_count': section.line_count
                    }
                    for section in sections[:20]  # 限制预览数量
                ],
                'statistics': structure_stats,
                'issues': structure_issues,
                'estimated_files': len(chapters) + (len(sections) if self.config.create_sections else 0) + 1  # +1 for TOC
            }
            
        except Exception as e:
            self.logger.error(f"预览处理失败: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'message': '预览失败'
            }
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.content_extractor:
                self.content_extractor.clear_cache()
            
            if self.file_generator:
                # 注意：这里不调用cleanup_generated_files，因为用户可能需要保留文件
                pass
            
            self.logger.info("资源清理完成")
            
        except Exception as e:
            self.logger.warning(f"资源清理失败: {str(e)}")