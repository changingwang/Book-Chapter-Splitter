"""
文件生成器模块

负责创建章节和小节的markdown文件，处理文件名规范化和目录结构管理。
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import unicodedata

from ..models import ChapterInfo, SectionInfo
from ..config import ProcessingConfig


class FileGenerator:
    """文件生成器"""
    
    def __init__(self, config: ProcessingConfig):
        """初始化文件生成器
        
        Args:
            config: 处理配置对象
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 文件名计数器，用于处理重复文件名
        self._filename_counters: Dict[str, int] = {}
        
        # 已生成的文件路径记录
        self._generated_files: List[str] = []
        
        self.logger.info(f"文件生成器初始化完成，输出目录: {config.output_dir}")
    
    def sanitize_filename(self, title: str, max_length: int = 100) -> str:
        """清理文件名，确保文件系统安全
        
        Args:
            title: 原始标题
            max_length: 最大文件名长度
            
        Returns:
            清理后的安全文件名
        """
        if not title:
            return "untitled"
        
        # 移除markdown标记
        filename = re.sub(r'#+\s*', '', title)
        filename = re.sub(r'\*\*(.+?)\*\*', r'\1', filename)
        filename = re.sub(r'\*(.+?)\*', r'\1', filename)
        filename = re.sub(r'`(.+?)`', r'\1', filename)
        
        # 移除章节编号前缀（如"第一章"、"第1章"等）
        filename = re.sub(r'^第[一二三四五六七八九十\d]+章\s*', '', filename)
        filename = re.sub(r'^第[一二三四五六七八九十\d]+节\s*', '', filename)
        filename = re.sub(r'^[一二三四五六七八九十\d]+、\s*', '', filename)
        filename = re.sub(r'^\([一二三四五六七八九十\d]+\)\s*', '', filename)
        
        # 移除特殊字符，保留中文、英文、数字、空格、连字符、下划线
        filename = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\-_]', '', filename)
        
        # 规范化Unicode字符
        filename = unicodedata.normalize('NFKC', filename)
        
        # 替换空格为下划线或连字符
        separator = self.config.filename_separator
        filename = re.sub(r'\s+', separator, filename.strip())
        
        # 移除连续的分隔符
        filename = re.sub(f'{re.escape(separator)}+', separator, filename)
        
        # 移除开头和结尾的分隔符
        filename = filename.strip(separator)
        
        # 确保文件名不为空
        if not filename:
            filename = "untitled"
        
        # 限制长度
        if len(filename) > max_length:
            # 尝试在合适的位置截断
            truncated = filename[:max_length]
            # 如果截断位置是分隔符，向前移动
            while truncated.endswith(separator) and len(truncated) > 1:
                truncated = truncated[:-1]
            filename = truncated
        
        # 确保文件名以字母或中文开头（数字开头是允许的）
        if filename and not (filename[0].isalnum() or ord(filename[0]) >= 0x4e00):
            filename = "file" + separator + filename
        
        self.logger.debug(f"文件名清理: '{title}' -> '{filename}'")
        return filename
    
    def _create_chapter_filename(self, title: str) -> str:
        """为章节创建符合README格式的文件名
        
        Args:
            title: 章节标题
            
        Returns:
            格式化的章节文件名
        """
        if not title:
            return "untitled"
        
        # 移除markdown标记
        clean_title = re.sub(r'#+\s*', '', title)
        clean_title = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_title)
        clean_title = re.sub(r'\*(.+?)\*', r'\1', clean_title)
        clean_title = re.sub(r'`(.+?)`', r'\1', clean_title)
        
        # 提取章节编号和标题
        chapter_match = re.match(r'^(第[一二三四五六七八九十\d]+章)\s*(.*)$', clean_title)
        if chapter_match:
            chapter_num = chapter_match.group(1)
            chapter_title = chapter_match.group(2).strip()
            if chapter_title:
                # 格式: 第一章_标题
                filename = f"{chapter_num}_{chapter_title}"
            else:
                # 只有章节编号
                filename = chapter_num
        else:
            # 没有标准格式，使用原标题
            filename = clean_title
        
        # 清理文件名
        return self._clean_filename(filename)
    
    def _create_section_filename(self, title: str, chapter_num: int = 0, section_num: int = 0) -> str:
        """为小节创建符合README格式的文件名
        
        Args:
            title: 小节标题
            chapter_num: 章节编号
            section_num: 小节编号
            
        Returns:
            格式化的小节文件名，格式为: X.Y_标题 (如: 1.1_马克思主义政治学的形成)
        """
        if not title:
            return "untitled"
        
        # 移除markdown标记
        clean_title = re.sub(r'#+\s*', '', title)
        clean_title = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_title)
        clean_title = re.sub(r'\*(.+?)\*', r'\1', clean_title)
        clean_title = re.sub(r'`(.+?)`', r'\1', clean_title)
        
        # 如果提供了章节和小节编号，使用 X.Y 格式
        if chapter_num > 0 and section_num > 0:
            filename = f"{chapter_num}.{section_num}_{clean_title}"
            return self._clean_filename(filename)
        
        # 尝试从标题中提取编号（备用方案）
        section_patterns = [
            r'^([一二三四五六七八九十]+)、\s*(.*)$',  # 一、标题
            r'^(\d+)、\s*(.*)$',                      # 1、标题
            r'^\(([一二三四五六七八九十]+)\)\s*(.*)$', # (一)标题
            r'^\((\d+)\)\s*(.*)$',                    # (1)标题
        ]
        
        for pattern in section_patterns:
            match = re.match(pattern, clean_title)
            if match:
                section_num = match.group(1)
                section_title = match.group(2).strip()
                if section_title:
                    # 格式: X.Y_标题
                    section_num_arabic = self._chinese_to_arabic(section_num)
                    filename = f"{chapter_num}.{section_num_arabic}_{section_title}"
                else:
                    # 只有小节编号
                    section_num_arabic = self._chinese_to_arabic(section_num)
                    filename = f"{chapter_num}.{section_num_arabic}"
                return self._clean_filename(filename)
        
        # 没有标准格式，直接使用标题
        return self._clean_filename(clean_title)
    
    def _chinese_to_arabic(self, chinese_num: str) -> int:
        """将中文数字转换为阿拉伯数字
        
        Args:
            chinese_num: 中文数字字符串
            
        Returns:
            对应的阿拉伯数字
        """
        chinese_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }
        
        # 如果已经是阿拉伯数字，直接返回
        if chinese_num.isdigit():
            return int(chinese_num)
        
        # 处理简单的中文数字
        if chinese_num in chinese_map:
            return chinese_map[chinese_num]
        
        # 处理十几的情况（如：十一、十二等）
        if chinese_num.startswith('十') and len(chinese_num) == 2:
            return 10 + chinese_map.get(chinese_num[1], 0)
        
        # 默认返回1
        return 1
    
    def _extract_chapter_number_from_title(self, chapter_title: str) -> int:
        """从章节标题中提取章节编号
        
        Args:
            chapter_title: 章节标题，如"第一章 导论：对象和地位"
            
        Returns:
            章节编号（阿拉伯数字）
        """
        if not chapter_title:
            return 1
        
        # 匹配"第X章"格式
        match = re.search(r'第([一二三四五六七八九十\d]+)章', chapter_title)
        if match:
            chapter_num_str = match.group(1)
            return self._chinese_to_arabic(chapter_num_str)
        
        return 1
    
    def _clean_filename(self, filename: str) -> str:
        """清理文件名，移除特殊字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        if not filename:
            return "untitled"
        
        # 先进行Unicode规范化（全角转半角等）
        filename = unicodedata.normalize('NFKC', filename)
        
        # 移除特殊字符，保留中文、英文、数字、空格、连字符、下划线
        filename = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\-_]', '', filename)
        
        # 替换空格为下划线或连字符
        separator = self.config.filename_separator
        filename = re.sub(r'\s+', separator, filename.strip())
        
        # 移除连续的分隔符
        filename = re.sub(f'{re.escape(separator)}+', separator, filename)
        
        # 移除开头和结尾的分隔符
        filename = filename.strip(separator)
        
        # 确保文件名不为空
        if not filename:
            filename = "untitled"
        
        # 限制长度
        max_length = 100
        if len(filename) > max_length:
            # 尝试在合适的位置截断
            truncated = filename[:max_length]
            # 如果截断位置是分隔符，向前移动
            while truncated.endswith(separator) and len(truncated) > 1:
                truncated = truncated[:-1]
            filename = truncated
        
        # 允许文件名以数字开头（X.Y格式）
        
        return filename
    
    def _ensure_unique_filename(self, base_filename: str, extension: str = ".md") -> str:
        """确保文件名唯一性
        
        Args:
            base_filename: 基础文件名
            extension: 文件扩展名
            
        Returns:
            唯一的文件名
        """
        full_filename = base_filename + extension
        
        # 如果文件名未使用过，直接返回
        if full_filename not in self._filename_counters:
            self._filename_counters[full_filename] = 1
            return full_filename
        
        # 如果已使用，添加数字后缀
        counter = self._filename_counters[full_filename]
        while True:
            counter += 1
            new_filename = f"{base_filename}_{counter}{extension}"
            if new_filename not in self._filename_counters:
                self._filename_counters[full_filename] = counter
                self._filename_counters[new_filename] = 1
                return new_filename
    
    def _create_file_path(self, filename: str, subdirectory: str) -> Path:
        """创建完整的文件路径
        
        Args:
            filename: 文件名
            subdirectory: 子目录名
            
        Returns:
            完整的文件路径
        """
        # 确保子目录存在
        subdir_path = Path(self.config.output_dir) / subdirectory
        subdir_path.mkdir(parents=True, exist_ok=True)
        
        return subdir_path / filename
    
    def create_chapter_file(self, chapter_info: ChapterInfo, content: str, 
                          tags: Optional[List[str]] = None) -> str:
        """创建章节文件
        
        Args:
            chapter_info: 章节信息
            content: 章节内容
            tags: 标签列表（可选）
            
        Returns:
            生成的文件路径
        """
        try:
            # 生成文件名 - 保持章节编号格式
            base_filename = self._create_chapter_filename(chapter_info.title)
            filename = self._ensure_unique_filename(base_filename)
            
            # 创建文件路径
            file_path = self._create_file_path(filename, self.config.chapters_subdir)
            
            # 准备文件内容
            file_content = self._prepare_chapter_content(
                chapter_info, content, tags, file_path
            )
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # 更新章节信息
            chapter_info.file_path = str(file_path.relative_to(self.config.output_dir))
            
            # 记录生成的文件
            self._generated_files.append(str(file_path))
            
            self.logger.info(f"章节文件已创建: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"创建章节文件失败 '{chapter_info.title}': {str(e)}")
            raise
    
    def create_section_file(self, section_info: SectionInfo, content: str,
                          tags: Optional[List[str]] = None, section_index: int = 1) -> str:
        """创建小节文件
        
        Args:
            section_info: 小节信息
            content: 小节内容
            tags: 标签列表（可选）
            section_index: 小节在章节中的序号（从1开始）
            
        Returns:
            生成的文件路径
        """
        try:
            # 生成文件名 - 使用小节标题格式
            # 从章节标题中提取章节编号
            chapter_num = self._extract_chapter_number_from_title(section_info.chapter_title)
            # 使用传入的小节序号
            section_num = section_index
            base_filename = self._create_section_filename(section_info.title, chapter_num, section_num)
            filename = self._ensure_unique_filename(base_filename)
            
            # 创建文件路径
            file_path = self._create_file_path(filename, self.config.sections_subdir)
            
            # 准备文件内容
            file_content = self._prepare_section_content(
                section_info, content, tags, file_path
            )
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # 更新小节信息
            section_info.file_path = str(file_path.relative_to(self.config.output_dir))
            
            # 记录生成的文件
            self._generated_files.append(str(file_path))
            
            self.logger.info(f"小节文件已创建: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"创建小节文件失败 '{section_info.title}': {str(e)}")
            raise
    
    def _prepare_chapter_content(self, chapter_info: ChapterInfo, content: str,
                               tags: Optional[List[str]], file_path: Path) -> str:
        """准备章节文件内容
        
        Args:
            chapter_info: 章节信息
            content: 原始内容
            tags: 标签列表
            file_path: 文件路径
            
        Returns:
            完整的文件内容
        """
        content_parts = []
        
        # 添加YAML前置元数据（如果启用标签生成）
        if self.config.generate_tags and tags:
            from .tag_generator import TagGenerator
            tag_generator = TagGenerator()
            
            metadata = {
                "type": "chapter",
                "chapter_title": chapter_info.title,
                "line_range": f"{chapter_info.start_line}-{chapter_info.end_line}",
                "sections_count": len(chapter_info.sections)
            }
            
            frontmatter = tag_generator.create_frontmatter(
                tags=tags,
                title=chapter_info.title,
                additional_metadata=metadata
            )
            content_parts.append(frontmatter)
        
        # 添加章节标题（如果内容中没有）
        if not content.strip().startswith('#'):
            content_parts.append(f"# {chapter_info.title}\n")
        
        # 添加主要内容
        content_parts.append(content)
        
        # 添加导航链接（如果启用）
        if self.config.add_navigation:
            navigation = self._create_navigation_links(file_path, "chapter")
            if navigation:
                content_parts.append("\n---\n")
                content_parts.append(navigation)
        
        return "\n".join(content_parts)
    
    def _prepare_section_content(self, section_info: SectionInfo, content: str,
                               tags: Optional[List[str]], file_path: Path) -> str:
        """准备小节文件内容
        
        Args:
            section_info: 小节信息
            content: 原始内容
            tags: 标签列表
            file_path: 文件路径
            
        Returns:
            完整的文件内容
        """
        content_parts = []
        
        # 添加YAML前置元数据（如果启用标签生成）
        if self.config.generate_tags and tags:
            from .tag_generator import TagGenerator
            tag_generator = TagGenerator()
            
            metadata = {
                "type": "section",
                "section_title": section_info.title,
                "chapter_title": section_info.chapter_title,
                "level": section_info.level,
                "line_range": f"{section_info.start_line}-{section_info.end_line}"
            }
            
            frontmatter = tag_generator.create_frontmatter(
                tags=tags,
                title=section_info.title,
                additional_metadata=metadata
            )
            content_parts.append(frontmatter)
        
        # 添加小节标题（如果内容中没有合适的标题）
        title_pattern = r'^#{1,6}\s+'
        if not re.match(title_pattern, content.strip()):
            level_marker = '#' * min(section_info.level, 6)
            content_parts.append(f"{level_marker} {section_info.title}\n")
        
        # 添加主要内容
        content_parts.append(content)
        
        # 添加导航链接（如果启用）
        if self.config.add_navigation:
            navigation = self._create_navigation_links(file_path, "section")
            if navigation:
                content_parts.append("\n---\n")
                content_parts.append(navigation)
        
        return "\n".join(content_parts)
    
    def _create_navigation_links(self, current_file: Path, file_type: str) -> str:
        """创建导航链接
        
        Args:
            current_file: 当前文件路径
            file_type: 文件类型（chapter或section）
            
        Returns:
            导航链接内容
        """
        navigation_parts = []
        
        # 返回目录的链接（总是添加，即使目录文件还不存在）
        relative_toc = Path("..") / self.config.toc_filename
        navigation_parts.append(f"[← 返回目录]({relative_toc})")
        
        # 添加文件类型标识
        type_text = "章节" if file_type == "chapter" else "小节"
        navigation_parts.append(f"*{type_text}文件*")
        
        return " | ".join(navigation_parts) if navigation_parts else ""
    
    def process_images(self, content: str, source_dir: Path) -> str:
        """处理图片资源
        
        Args:
            content: 文档内容
            source_dir: 源文档目录
            
        Returns:
            更新图片路径后的内容
        """
        if not self.config.preserve_images:
            return content
        
        # 查找所有图片引用
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        images = re.findall(image_pattern, content)
        
        updated_content = content
        
        for alt_text, image_path in images:
            try:
                # 处理相对路径
                if not Path(image_path).is_absolute():
                    source_image = source_dir / image_path
                else:
                    source_image = Path(image_path)
                
                if source_image.exists():
                    # 复制图片到输出目录
                    target_image = self._copy_image(source_image)
                    if target_image:
                        # 更新内容中的图片路径
                        old_ref = f'![{alt_text}]({image_path})'
                        new_ref = f'![{alt_text}]({target_image})'
                        updated_content = updated_content.replace(old_ref, new_ref)
                        
                        self.logger.debug(f"图片路径已更新: {image_path} -> {target_image}")
                
            except Exception as e:
                self.logger.warning(f"处理图片失败 '{image_path}': {str(e)}")
                continue
        
        return updated_content
    
    def _copy_image(self, source_image: Path) -> Optional[str]:
        """复制图片文件到输出目录
        
        Args:
            source_image: 源图片路径
            
        Returns:
            目标图片的相对路径
        """
        try:
            import shutil
            
            # 创建图片目录
            images_dir = Path(self.config.output_dir) / self.config.images_subdir
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成目标文件名
            target_filename = self.sanitize_filename(source_image.stem) + source_image.suffix
            target_path = images_dir / target_filename
            
            # 处理文件名冲突
            counter = 1
            original_target = target_path
            while target_path.exists():
                name_part = self.sanitize_filename(source_image.stem)
                target_filename = f"{name_part}_{counter}{source_image.suffix}"
                target_path = images_dir / target_filename
                counter += 1
            
            # 复制文件
            shutil.copy2(source_image, target_path)
            
            # 返回相对路径
            return f"{self.config.images_subdir}/{target_path.name}"
            
        except Exception as e:
            self.logger.error(f"复制图片失败 '{source_image}': {str(e)}")
            return None
    
    def get_generated_files(self) -> List[str]:
        """获取已生成的文件列表"""
        return self._generated_files.copy()
    
    def get_statistics(self) -> Dict[str, any]:
        """获取文件生成统计信息"""
        return {
            'output_dir': self.config.output_dir,
            'chapters_dir': self.config.chapters_dir,
            'sections_dir': self.config.sections_dir,
            'images_dir': self.config.images_dir,
            'generated_files_count': len(self._generated_files),
            'filename_conflicts_resolved': sum(
                count - 1 for count in self._filename_counters.values() if count > 1
            ),
            'config': {
                'create_sections': self.config.create_sections,
                'add_navigation': self.config.add_navigation,
                'preserve_images': self.config.preserve_images,
                'generate_tags': self.config.generate_tags,
                'filename_separator': self.config.filename_separator
            }
        }
    
    def cleanup_generated_files(self):
        """清理已生成的文件（用于测试或重置）"""
        for file_path in self._generated_files:
            try:
                Path(file_path).unlink(missing_ok=True)
                self.logger.debug(f"已删除文件: {file_path}")
            except Exception as e:
                self.logger.warning(f"删除文件失败 '{file_path}': {str(e)}")
        
        self._generated_files.clear()
        self._filename_counters.clear()
        self.logger.info("已清理所有生成的文件")