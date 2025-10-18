"""
数据模型模块

包含章节信息、小节信息等核心数据结构的定义。
"""

from .chapter_info import ChapterInfo
from .section_info import SectionInfo

__all__ = ["ChapterInfo", "SectionInfo"]