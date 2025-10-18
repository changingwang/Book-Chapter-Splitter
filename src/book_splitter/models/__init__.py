"""
模型模块 - 包含数据模型和数据结构定义
"""

from .chapter_info import ChapterInfo
from .section_info import SectionInfo
from .book_metadata import BookMetadata
from .extraction_stats import ExtractionStats

__all__ = [
    'ChapterInfo',
    'SectionInfo', 
    'BookMetadata',
    'ExtractionStats'
]