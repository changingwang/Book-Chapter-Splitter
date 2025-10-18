"""
书籍章节拆分器 - 主包

一个高效的markdown书籍文档处理工具，能够将大型书籍文档按章节和小节拆分为独立文件，
并创建带有双向链接的导航系统。支持自动生成Obsidian兼容的标签元数据。
"""

# 顶部元信息
__version__ = "1.0.1"
__author__ = "Book Splitter Team"
__email__ = "team@booksplitter.com"

from .main import BookSplitter
from .config import ProcessingConfig

__all__ = ["BookSplitter", "ProcessingConfig"]