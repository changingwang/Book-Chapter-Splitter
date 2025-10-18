"""
章节信息数据类

定义章节的基本信息结构，包括标题、行号范围、文件路径等。
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ChapterInfo:
    """章节信息数据类"""
    
    title: str                                    # 章节标题
    start_line: int                              # 起始行号
    end_line: int                                # 结束行号
    file_path: str = ""                          # 生成的文件路径
    sections: List['SectionInfo'] = field(default_factory=list)  # 包含的小节列表
    
    def __post_init__(self):
        """初始化后处理"""
        if self.end_line <= self.start_line:
            raise ValueError(f"结束行号({self.end_line})必须大于起始行号({self.start_line})")
    
    @property
    def line_count(self) -> int:
        """获取章节行数"""
        return self.end_line - self.start_line
    
    @property
    def has_sections(self) -> bool:
        """检查是否包含小节"""
        return len(self.sections) > 0
    
    def add_section(self, section: 'SectionInfo'):
        """添加小节"""
        if section.start_line < self.start_line or section.end_line > self.end_line:
            raise ValueError("小节行号范围必须在章节范围内")
        self.sections.append(section)
    
    def __str__(self) -> str:
        return f"ChapterInfo(title='{self.title}', lines={self.start_line}-{self.end_line})"