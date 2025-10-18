"""
内容提取器模块

基于行号范围从源文档提取特定章节和小节内容，保持原始markdown格式。
"""

import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from ..models import ChapterInfo, SectionInfo


class ContentExtractor:
    """内容提取器"""
    
    def __init__(self, source_file: str):
        """初始化内容提取器
        
        Args:
            source_file: 源markdown文件路径
        """
        self.source_file = source_file
        self.logger = logging.getLogger(__name__)
        
        # 缓存文件内容以避免重复读取
        self._lines_cache: Optional[List[str]] = None
        
        # 验证源文件存在
        if not Path(source_file).exists():
            raise FileNotFoundError(f"源文件不存在: {source_file}")
    
    def _load_file_content(self) -> List[str]:
        """加载文件内容到缓存
        
        Returns:
            文件行列表
        """
        if self._lines_cache is None:
            try:
                with open(self.source_file, 'r', encoding='utf-8') as f:
                    self._lines_cache = f.readlines()
                self.logger.debug(f"加载文件内容完成，共 {len(self._lines_cache)} 行")
            except Exception as e:
                raise IOError(f"读取文件失败: {str(e)}")
        
        return self._lines_cache
    
    def extract_content(self, start_line: int, end_line: int) -> str:
        """提取指定行范围的内容
        
        Args:
            start_line: 起始行号（1-based）
            end_line: 结束行号（1-based，包含）
            
        Returns:
            提取的内容字符串
        """
        lines = self._load_file_content()
        
        # 验证行号范围
        if start_line < 1 or end_line < 1:
            raise ValueError("行号必须大于0")
        
        if start_line > len(lines) or end_line > len(lines):
            raise ValueError(f"行号超出文件范围 (1-{len(lines)})")
        
        if start_line > end_line:
            raise ValueError("起始行号不能大于结束行号")
        
        # 提取内容（转换为0-based索引）
        start_idx = start_line - 1
        end_idx = end_line  # end_line是包含的，所以不需要-1
        
        extracted_lines = lines[start_idx:end_idx]
        content = ''.join(extracted_lines)
        
        self.logger.debug(f"提取内容: 行 {start_line}-{end_line} ({len(extracted_lines)} 行)")
        
        return content
    
    def extract_multiple_ranges(self, ranges: List[Tuple[int, int]]) -> Dict[str, str]:
        """批量提取多个行范围的内容
        
        Args:
            ranges: 行号范围列表，每个元素为 (start_line, end_line)
            
        Returns:
            字典，键为 "start_line-end_line"，值为提取的内容
        """
        if not ranges:
            return {}
        
        # 预加载文件内容
        self._load_file_content()
        
        results = {}
        
        for start_line, end_line in ranges:
            try:
                content = self.extract_content(start_line, end_line)
                key = f"{start_line}-{end_line}"
                results[key] = content
            except Exception as e:
                self.logger.warning(f"提取范围 {start_line}-{end_line} 失败: {str(e)}")
                continue
        
        self.logger.info(f"批量提取完成，成功提取 {len(results)}/{len(ranges)} 个范围")
        
        return results
    
    def extract_chapter_content(self, chapter: ChapterInfo) -> str:
        """提取章节内容
        
        Args:
            chapter: 章节信息对象
            
        Returns:
            章节内容字符串
        """
        try:
            content = self.extract_content(chapter.start_line, chapter.end_line)
            self.logger.debug(f"提取章节内容: {chapter.title}")
            return content
        except Exception as e:
            self.logger.error(f"提取章节 '{chapter.title}' 内容失败: {str(e)}")
            raise
    
    def extract_section_content(self, section: SectionInfo) -> str:
        """提取小节内容
        
        Args:
            section: 小节信息对象
            
        Returns:
            小节内容字符串
        """
        try:
            content = self.extract_content(section.start_line, section.end_line)
            self.logger.debug(f"提取小节内容: {section.title}")
            return content
        except Exception as e:
            self.logger.error(f"提取小节 '{section.title}' 内容失败: {str(e)}")
            raise
    
    def extract_chapters_batch(self, chapters: List[ChapterInfo]) -> Dict[str, str]:
        """批量提取章节内容
        
        Args:
            chapters: 章节信息列表
            
        Returns:
            字典，键为章节标题，值为章节内容
        """
        if not chapters:
            return {}
        
        # 准备行号范围列表
        ranges = [(chapter.start_line, chapter.end_line) for chapter in chapters]
        
        # 批量提取
        range_contents = self.extract_multiple_ranges(ranges)
        
        # 映射到章节标题
        results = {}
        for chapter in chapters:
            range_key = f"{chapter.start_line}-{chapter.end_line}"
            if range_key in range_contents:
                results[chapter.title] = range_contents[range_key]
            else:
                self.logger.warning(f"章节 '{chapter.title}' 内容提取失败")
        
        self.logger.info(f"批量提取章节完成，成功提取 {len(results)}/{len(chapters)} 个章节")
        
        return results
    
    def extract_sections_batch(self, sections: List[SectionInfo]) -> Dict[str, str]:
        """批量提取小节内容
        
        Args:
            sections: 小节信息列表
            
        Returns:
            字典，键为小节标题，值为小节内容
        """
        if not sections:
            return {}
        
        # 准备行号范围列表
        ranges = [(section.start_line, section.end_line) for section in sections]
        
        # 批量提取
        range_contents = self.extract_multiple_ranges(ranges)
        
        # 映射到小节标题
        results = {}
        for section in sections:
            range_key = f"{section.start_line}-{section.end_line}"
            if range_key in range_contents:
                results[section.title] = range_contents[range_key]
            else:
                self.logger.warning(f"小节 '{section.title}' 内容提取失败")
        
        self.logger.info(f"批量提取小节完成，成功提取 {len(results)}/{len(sections)} 个小节")
        
        return results
    
    def extract_content_with_context(self, start_line: int, end_line: int, 
                                   context_lines: int = 2) -> Dict[str, str]:
        """提取内容并包含上下文行
        
        Args:
            start_line: 起始行号
            end_line: 结束行号
            context_lines: 上下文行数
            
        Returns:
            包含 'content', 'before_context', 'after_context' 的字典
        """
        lines = self._load_file_content()
        
        # 计算上下文范围
        context_start = max(1, start_line - context_lines)
        context_end = min(len(lines), end_line + context_lines)
        
        # 提取各部分内容
        before_context = ""
        if context_start < start_line:
            before_context = self.extract_content(context_start, start_line - 1)
        
        main_content = self.extract_content(start_line, end_line)
        
        after_context = ""
        if end_line < context_end:
            after_context = self.extract_content(end_line + 1, context_end)
        
        return {
            'content': main_content,
            'before_context': before_context,
            'after_context': after_context,
            'full_context': before_context + main_content + after_context
        }
    
    def validate_content_integrity(self, content: str, expected_lines: int = None) -> bool:
        """验证提取内容的完整性
        
        Args:
            content: 提取的内容
            expected_lines: 期望的行数（可选）
            
        Returns:
            内容是否完整
        """
        if not content:
            return False
        
        # 检查内容是否为空或只包含空白字符
        if not content.strip():
            return False
        
        # 如果指定了期望行数，验证行数
        if expected_lines is not None:
            actual_lines = len(content.splitlines())
            if actual_lines != expected_lines:
                self.logger.warning(f"行数不匹配: 期望 {expected_lines}，实际 {actual_lines}")
                return False
        
        return True
    
    def get_extraction_statistics(self) -> Dict[str, any]:
        """获取提取统计信息
        
        Returns:
            统计信息字典
        """
        lines = self._load_file_content()
        
        return {
            'source_file': self.source_file,
            'total_lines': len(lines),
            'file_size_bytes': Path(self.source_file).stat().st_size,
            'cache_loaded': self._lines_cache is not None,
            'encoding': 'utf-8'
        }
    
    def clear_cache(self):
        """清除文件内容缓存"""
        self._lines_cache = None
        self.logger.debug("文件内容缓存已清除")