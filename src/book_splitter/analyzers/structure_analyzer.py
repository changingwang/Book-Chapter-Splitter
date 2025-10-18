"""
结构分析器模块

使用正则表达式模式匹配识别markdown文档中的章节和小节边界。
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from ..models import ChapterInfo, SectionInfo


class StructureAnalyzer:
    """文档结构分析器"""
    
    # 章节和小节识别的正则表达式模式
    CHAPTER_PATTERN = r'^#\s*第([一二三四五六七八九十0-9]+)章(?:\s+(.+?)(?:\s+…+.*)?)?$'
    # 添加对 "## 一、" 格式的支持
    CHAPTER_PATTERN_ALT = r'^## ([一二三四五六七八九十0-9]+)、(.+?)$'
    SECTION_PATTERNS = {
        2: r'^# 第[一二三四五六七八九十0-9]+节\s+(.+?)(?:\s+\d+)?$',
        3: r'^[一二三四五六七八九十0-9]+、\s*(.+?)(?:\s+\d+)?$',
        4: r'^\([一二三四五六七八九十0-9]+\)\s*(.+?)(?:\s+\d+)?$',
        # 添加对 "### （一）" 格式的支持
        5: r'^### （[一二三四五六七八九十0-9]+）(.+?)$'
    }
    
    def __init__(self, source_file: str):
        """初始化结构分析器
        
        Args:
            source_file: 源markdown文件路径
        """
        self.source_file = source_file
        self.logger = logging.getLogger(__name__)
        
        # 存储分析结果
        self.chapters: List[ChapterInfo] = []
        self.sections: List[SectionInfo] = []
        self._lines: List[str] = []
        
        # 验证源文件存在
        if not Path(source_file).exists():
            raise FileNotFoundError(f"源文件不存在: {source_file}")
    
    def analyze_structure(self) -> Dict[str, List]:
        """分析文档结构，返回章节和小节信息
        
        Returns:
            包含chapters和sections列表的字典
        """
        self.logger.info(f"开始分析文档结构: {self.source_file}")
        
        # 读取文件内容（仅读取一次）
        self._read_file()
        
        # 识别章节
        self.chapters = self.find_chapters()
        self.logger.info(f"识别到 {len(self.chapters)} 个章节")
        
        # 识别小节
        self.sections = self.find_sections()
        self.logger.info(f"识别到 {len(self.sections)} 个小节")
        
        # 建立章节和小节的关联关系
        self._associate_sections_with_chapters()
        
        return {
            'chapters': self.chapters,
            'sections': self.sections
        }
    
    def _read_file(self):
        """读取源文件内容到内存"""
        try:
            with open(self.source_file, 'r', encoding='utf-8') as f:
                self._lines = f.readlines()
            self.logger.debug(f"读取文件完成，共 {len(self._lines)} 行")
        except Exception as e:
            raise IOError(f"读取文件失败: {str(e)}")
    
    def find_chapters(self) -> List[ChapterInfo]:
        """识别所有章节边界
        
        Returns:
            章节信息列表
        """
        chapters = []
        chapter_pattern = re.compile(self.CHAPTER_PATTERN)
        chapter_pattern_alt = re.compile(self.CHAPTER_PATTERN_ALT)
        
        for line_num, line in enumerate(self._lines, 1):
            line = line.strip()
            match = chapter_pattern.match(line)
            match_alt = chapter_pattern_alt.match(line)
            
            if match:
                chapter_num = match.group(1).strip()
                raw_title = match.group(2).strip() if match.group(2) else ""
                # 清理标题中的页码等信息
                title = re.sub(r'\s+\d+$', '', raw_title) if raw_title else ""
                full_title = f"第{chapter_num}章" + (f" {title}" if title else "")
                
                chapter_info = ChapterInfo(
                    title=full_title,
                    start_line=line_num,
                    end_line=line_num + 1  # 临时设置，后续会更新
                )
                chapters.append(chapter_info)
                self.logger.debug(f"发现章节: {chapter_info.title} (行 {line_num})")
            elif match_alt:
                # 处理 "## 一、" 格式
                chapter_num = match_alt.group(1).strip()
                title = match_alt.group(2).strip()
                
                chapter_info = ChapterInfo(
                    title=f"{chapter_num}、{title}",
                    start_line=line_num,
                    end_line=line_num + 1  # 临时设置，后续会更新
                )
                chapters.append(chapter_info)
                self.logger.debug(f"发现章节: {chapter_info.title} (行 {line_num})")
        
        # 计算每个章节的结束行号
        for i in range(len(chapters)):
            if i < len(chapters) - 1:
                chapters[i].end_line = chapters[i + 1].start_line - 1
            else:
                chapters[i].end_line = len(self._lines)
            
            # 确保结束行号大于起始行号
            if chapters[i].end_line <= chapters[i].start_line:
                chapters[i].end_line = chapters[i].start_line + 1
        
        return chapters
    
    def find_sections(self) -> List[SectionInfo]:
        """识别所有小节边界
        
        Returns:
            小节信息列表
        """
        sections = []
        
        # 编译所有小节模式
        compiled_patterns = {
            level: re.compile(pattern) 
            for level, pattern in self.SECTION_PATTERNS.items()
        }
        
        current_chapter = None
        
        for line_num, line in enumerate(self._lines, 1):
            line = line.strip()
            
            # 检查是否是章节标题（用于确定当前章节上下文）
            if re.match(self.CHAPTER_PATTERN, line) or re.match(self.CHAPTER_PATTERN_ALT, line):
                current_chapter = self._find_chapter_by_line(line_num)
                continue
            
            # 检查各级小节模式
            for level, pattern in compiled_patterns.items():
                match = pattern.match(line)
                if match:
                    title = match.group(1).strip()
                    
                    section_info = SectionInfo(
                        title=title,
                        start_line=line_num,
                        end_line=line_num + 1,  # 临时设置
                        chapter_title=current_chapter.title if current_chapter else "未知章节",
                        level=level
                    )
                    sections.append(section_info)
                    self.logger.debug(f"发现小节: {section_info.title} (行 {line_num}, 级别 {level})")
                    break
        
        # 计算每个小节的结束行号
        self._calculate_section_end_lines(sections)
        
        return sections
    
    def _calculate_section_end_lines(self, sections: List[SectionInfo]):
        """计算小节的结束行号"""
        for i in range(len(sections)):
            current_section = sections[i]
            
            # 查找下一个同级或更高级的标题
            next_boundary = len(self._lines)
            
            for j in range(i + 1, len(sections)):
                next_section = sections[j]
                if next_section.level <= current_section.level:
                    next_boundary = next_section.start_line - 1
                    break
            
            # 检查是否有章节边界
            for chapter in self.chapters:
                if (chapter.start_line > current_section.start_line and 
                    chapter.start_line < next_boundary):
                    next_boundary = chapter.start_line - 1
                    break
            
            current_section.end_line = max(next_boundary, current_section.start_line + 1)
    
    def _associate_sections_with_chapters(self):
        """建立章节和小节的关联关系"""
        for section in self.sections:
            for chapter in self.chapters:
                if (chapter.start_line <= section.start_line <= chapter.end_line):
                    chapter.add_section(section)
                    section.chapter_title = chapter.title
                    break
    
    def _find_chapter_by_line(self, line_num: int) -> Optional[ChapterInfo]:
        """根据行号查找对应的章节"""
        for chapter in self.chapters:
            if chapter.start_line == line_num:
                return chapter
        return None
    
    def _extract_chapter_number(self, line: str) -> str:
        """从章节标题行提取章节号"""
        match = re.search(r'第([一二三四五六七八九十0-9]+)章', line)
        return match.group(1) if match else "未知"
    
    def get_statistics(self) -> Dict[str, any]:
        """获取分析统计信息"""
        return {
            'total_lines': len(self._lines),
            'chapters_count': len(self.chapters),
            'sections_count': len(self.sections),
            'sections_by_level': {
                level: len([s for s in self.sections if s.level == level])
                for level in self.SECTION_PATTERNS.keys()
            },
            'chapters_with_sections': len([c for c in self.chapters if c.has_sections]),
            'average_chapter_length': (
                sum(c.line_count for c in self.chapters) / len(self.chapters)
                if self.chapters else 0
            )
        }
    
    def validate_structure(self) -> List[str]:
        """验证分析结果的有效性
        
        Returns:
            发现的问题列表
        """
        issues = []
        
        # 检查章节重叠
        for i, chapter in enumerate(self.chapters):
            for j, other_chapter in enumerate(self.chapters):
                if i != j and self._ranges_overlap(
                    (chapter.start_line, chapter.end_line),
                    (other_chapter.start_line, other_chapter.end_line)
                ):
                    issues.append(f"章节重叠: {chapter.title} 和 {other_chapter.title}")
        
        # 检查小节是否在章节范围内
        for section in self.sections:
            found_chapter = False
            for chapter in self.chapters:
                if chapter.start_line <= section.start_line <= chapter.end_line:
                    found_chapter = True
                    break
            if not found_chapter:
                issues.append(f"小节不在任何章节范围内: {section.title}")
        
        # 检查空章节
        empty_chapters = [c for c in self.chapters if c.line_count <= 1]
        for chapter in empty_chapters:
            issues.append(f"空章节: {chapter.title}")
        
        return issues
    
    def _ranges_overlap(self, range1: Tuple[int, int], range2: Tuple[int, int]) -> bool:
        """检查两个行号范围是否重叠"""
        return not (range1[1] < range2[0] or range2[1] < range1[0])