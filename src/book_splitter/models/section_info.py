"""
小节信息数据类

定义小节的基本信息结构，包括标题、行号范围、所属章节、标签等。
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class SectionInfo:
    """小节信息数据类"""
    
    title: str                                   # 小节标题
    start_line: int                             # 起始行号
    end_line: int                               # 结束行号
    chapter_title: str                          # 所属章节标题
    level: int                                  # 标题级别 (2, 3, 4...)
    file_path: str = ""                         # 生成的文件路径
    tags: List[str] = field(default_factory=list)  # 关键词标签
    
    def __post_init__(self):
        """初始化后处理"""
        if self.end_line <= self.start_line:
            raise ValueError(f"结束行号({self.end_line})必须大于起始行号({self.start_line})")
        
        if self.level < 2:
            raise ValueError(f"小节级别({self.level})必须大于等于2")
    
    @property
    def line_count(self) -> int:
        """获取小节行数"""
        return self.end_line - self.start_line
    
    @property
    def has_tags(self) -> bool:
        """检查是否有标签"""
        return len(self.tags) > 0
    
    def add_tag(self, tag: str):
        """添加标签"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def add_tags(self, tags: List[str]):
        """批量添加标签"""
        for tag in tags:
            self.add_tag(tag)
    
    def __str__(self) -> str:
        return f"SectionInfo(title='{self.title}', level={self.level}, lines={self.start_line}-{self.end_line})"