"""
文件生成器 - 负责创建章节和部分的Markdown文件
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..models.chapter_info import ChapterInfo
from ..models.section_info import SectionInfo


class FileGenerator:
    """生成章节和部分的Markdown文件"""
    
    def __init__(self, output_dir: str, use_chinese_naming: bool = True):
        """
        初始化文件生成器
        
        Args:
            output_dir: 输出目录路径
            use_chinese_naming: 是否使用中文命名（如"第一章"）
        """
        self.output_dir = Path(output_dir)
        self.use_chinese_naming = use_chinese_naming
        self.created_files: List[str] = []
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 图片目录
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
    
    def generate_chapter_files(self, chapters: List[ChapterInfo], content_extractor) -> Dict[str, str]:
        """
        生成章节文件
        
        Args:
            chapters: 章节信息列表
            content_extractor: 内容提取器实例
            
        Returns:
            文件路径映射字典
        """
        file_mapping = {}
        
        for chapter in chapters:
            try:
                # 提取章节内容
                content = content_extractor.extract_chapter_content(chapter)
                
                # 生成文件名
                filename = self._generate_chapter_filename(chapter)
                filepath = self.output_dir / filename
                
                # 准备文件内容
                file_content = self._prepare_chapter_content(chapter, content, chapters)
                
                # 写入文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                
                file_mapping[chapter.title] = str(filepath)
                self.created_files.append(str(filepath))
                
                print(f"✓ 生成章节文件: {filename}")
                
            except Exception as e:
                print(f"✗ 生成章节文件失败: {chapter.title} - {str(e)}")
                continue
        
        return file_mapping
    
    def generate_section_files(self, sections: List[SectionInfo], content_extractor) -> Dict[str, str]:
        """
        生成部分文件
        
        Args:
            sections: 部分信息列表
            content_extractor: 内容提取器实例
            
        Returns:
            文件路径映射字典
        """
        file_mapping = {}
        
        for section in sections:
            try:
                # 提取部分内容
                content = content_extractor.extract_section_content(section)
                
                # 生成文件名
                filename = self._generate_section_filename(section)
                filepath = self.output_dir / filename
                
                # 准备文件内容
                file_content = self._prepare_section_content(section, content)
                
                # 写入文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                
                file_mapping[section.title] = str(filepath)
                self.created_files.append(str(filepath))
                
                print(f"✓ 生成部分文件: {filename}")
                
            except Exception as e:
                print(f"✗ 生成部分文件失败: {section.title} - {str(e)}")
                continue
        
        return file_mapping
    
    def _generate_chapter_filename(self, chapter: ChapterInfo) -> str:
        """生成章节文件名"""
        if self.use_chinese_naming:
            # 中文命名：第一章_标题.md
            chapter_num = self._number_to_chinese(chapter.chapter_number)
            title = self._sanitize_filename(chapter.title)
            return f"第{chapter_num}章_{title}.md"
        else:
            # 英文命名：chapter_01_标题.md
            title = self._sanitize_filename(chapter.title)
            return f"chapter_{chapter.chapter_number:02d}_{title}.md"
    
    def _generate_section_filename(self, section: SectionInfo) -> str:
        """生成部分文件名"""
        # 提取章节号和小节号
        chapter_num, section_num = self._extract_section_numbers(section.title)
        
        if self.use_chinese_naming:
            # 中文命名：1.1_标题.md
            title = self._sanitize_filename(section.title)
            return f"{chapter_num}.{section_num}_{title}.md"
        else:
            # 英文命名：section_01_01_标题.md
            title = self._sanitize_filename(section.title)
            return f"section_{chapter_num:02d}_{section_num:02d}_{title}.md"
    
    def _number_to_chinese(self, num: int) -> str:
        """将数字转换为中文数字"""
        chinese_nums = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        
        if num <= 10:
            return chinese_nums[num]
        elif num < 20:
            return "十" + (chinese_nums[num % 10] if num % 10 != 0 else "")
        else:
            tens = num // 10
            ones = num % 10
            result = chinese_nums[tens] + "十"
            if ones != 0:
                result += chinese_nums[ones]
            return result
    
    def _extract_section_numbers(self, title: str) -> Tuple[int, int]:
        """从标题中提取章节和小节号"""
        # 尝试匹配 "1.1 标题" 格式
        match = re.match(r'(\d+)\.(\d+)', title.strip())
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # 尝试匹配 "第一章 第一节" 格式
        match = re.match(r'第(\w+)章\s*第(\w+)节', title.strip())
        if match:
            chapter_num = self._chinese_to_number(match.group(1))
            section_num = self._chinese_to_number(match.group(2))
            return chapter_num, section_num
        
        # 默认返回 1, 1
        return 1, 1
    
    def _chinese_to_number(self, chinese: str) -> int:
        """将中文数字转换为阿拉伯数字"""
        chinese_nums = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, 
                         "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
        
        if chinese in chinese_nums:
            return chinese_nums[chinese]
        
        # 处理 "十一" 到 "十九"
        if chinese.startswith("十") and len(chinese) > 1:
            return 10 + chinese_nums.get(chinese[1:], 0)
        
        # 处理 "二十" 等
        if chinese.endswith("十") and len(chinese) > 1:
            return chinese_nums.get(chinese[0], 1) * 10
        
        return 1
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        # 移除标题中的章节编号
        filename = re.sub(r'^\d+\.\d+\s*', '', filename)
        filename = re.sub(r'^第\w+章\s*第\w+节\s*', '', filename)
        filename = re.sub(r'^第\w+章\s*', '', filename)
        
        # 替换非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)  # 空白字符替换为下划线
        filename = filename.strip('_')
        
        # 限制长度
        if len(filename) > 50:
            filename = filename[:50]
        
        return filename or "untitled"
    
    def _prepare_chapter_content(self, chapter: ChapterInfo, content: str, all_chapters: List[ChapterInfo]) -> str:
        """准备章节文件内容"""
        # YAML frontmatter
        frontmatter = self._generate_chapter_frontmatter(chapter, all_chapters)
        
        # 导航链接
        navigation = self._generate_chapter_navigation(chapter, all_chapters)
        
        # 处理图片路径
        processed_content = self._process_images(content)
        
        return f"{frontmatter}\n{navigation}\n{processed_content}"
    
    def _prepare_section_content(self, section: SectionInfo, content: str) -> str:
        """准备部分文件内容"""
        # YAML frontmatter
        frontmatter = self._generate_section_frontmatter(section)
        
        # 处理图片路径
        processed_content = self._process_images(content)
        
        return f"{frontmatter}\n{processed_content}"
    
    def _generate_chapter_frontmatter(self, chapter: ChapterInfo, all_chapters: List[ChapterInfo]) -> str:
        """生成章节YAML frontmatter"""
        tags = self._generate_chapter_tags(chapter, all_chapters)
        
        frontmatter = f"""---
title: "{chapter.title}"
chapter: {chapter.chapter_number}
start_line: {chapter.start_line}
end_line: {chapter.end_line}
tags: {tags}
created_date: {datetime.now().strftime("%Y-%m-%d")}
---"""
        return frontmatter
    
    def _generate_section_frontmatter(self, section: SectionInfo) -> str:
        """生成部分YAML frontmatter"""
        frontmatter = f"""---
title: "{section.title}"
chapter: {section.chapter_number}
section: {section.section_number}
start_line: {section.start_line}
end_line: {section.end_line}
created_date: {datetime.now().strftime("%Y-%m-%d")}
---"""
        return frontmatter
    
    def _generate_chapter_tags(self, chapter: ChapterInfo, all_chapters: List[ChapterInfo]) -> List[str]:
        """生成章节标签"""
        tags = ["chapter"]
        
        # 根据章节标题添加标签
        title_lower = chapter.title.lower()
        if "政治" in title_lower:
            tags.append("政治")
        if "经济" in title_lower:
            tags.append("经济")
        if "社会" in title_lower:
            tags.append("社会")
        if "文化" in title_lower:
            tags.append("文化")
        if "历史" in title_lower:
            tags.append("历史")
        
        return tags
    
    def _generate_chapter_navigation(self, chapter: ChapterInfo, all_chapters: List[ChapterInfo]) -> str:
        """生成章节导航链接"""
        nav_links = []
        
        # 上一章
        if chapter.chapter_number > 1:
            prev_chapter = next((c for c in all_chapters if c.chapter_number == chapter.chapter_number - 1), None)
            if prev_chapter:
                prev_filename = self._generate_chapter_filename(prev_chapter)
                nav_links.append(f'[← 上一章：{prev_chapter.title}]({prev_filename})')
        
        # 下一章
        if chapter.chapter_number < len(all_chapters):
            next_chapter = next((c for c in all_chapters if c.chapter_number == chapter.chapter_number + 1), None)
            if next_chapter:
                next_filename = self._generate_chapter_filename(next_chapter)
                nav_links.append(f'[下一章：{next_chapter.title} →]({next_filename})')
        
        if nav_links:
            return "\n".join(nav_links) + "\n\n---\n\n"
        
        return ""
    
    def _process_images(self, content: str) -> str:
        """处理图片路径"""
        # 查找所有图片引用
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def replace_image_path(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            
            # 如果图片路径是相对路径，复制到images目录
            if not image_path.startswith(('http://', 'https://', '/', 'data:')):
                original_path = Path(image_path)
                if original_path.exists():
                    # 生成新的图片文件名
                    new_filename = f"image_{len(self.created_files)}_{original_path.name}"
                    new_path = self.images_dir / new_filename
                    
                    # 复制图片
                    try:
                        shutil.copy2(original_path, new_path)
                        return f'![{alt_text}](images/{new_filename})'
                    except Exception as e:
                        print(f"警告：复制图片失败 {image_path} - {str(e)}")
            
            return match.group(0)  # 返回原始匹配
        
        return re.sub(image_pattern, replace_image_path, content)
    
    def get_created_files(self) -> List[str]:
        """获取已创建的文件列表"""
        return self.created_files.copy()
    
    def get_statistics(self) -> Dict[str, any]:
        """获取生成统计信息"""
        return {
            "total_files": len(self.created_files),
            "output_directory": str(self.output_dir),
            "images_directory": str(self.images_dir),
            "use_chinese_naming": self.use_chinese_naming,
            "created_files": self.created_files
        }