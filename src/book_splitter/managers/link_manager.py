"""
链接管理器模块

负责生成目录文档和管理文件间的双向导航链接。
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ..models import ChapterInfo, SectionInfo
from ..config import ProcessingConfig


class LinkManager:
    """链接管理器"""
    
    def __init__(self, config: ProcessingConfig):
        """初始化链接管理器
        
        Args:
            config: 处理配置对象
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 存储生成的链接信息
        self._toc_content: Optional[str] = None
        self._navigation_links: Dict[str, str] = {}
        
        self.logger.info(f"链接管理器初始化完成，输出目录: {config.output_dir}")
    
    def generate_toc(self, chapters: List[ChapterInfo], sections: List[SectionInfo] = None) -> str:
        """生成目录文档内容
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表（可选）
            
        Returns:
            目录文档的markdown内容
        """
        if not chapters:
            self.logger.warning("没有章节信息，生成空目录")
            return self._create_empty_toc()
        
        sections = sections or []
        
        # 构建目录内容
        toc_parts = []
        
        # 添加标题和元信息
        toc_parts.append(self._create_toc_header(chapters, sections))
        
        # 添加章节目录
        toc_parts.append(self._create_chapters_toc(chapters))
        
        # 添加小节目录（如果启用）
        if self.config.create_sections and sections:
            toc_parts.append(self._create_sections_toc(sections))
        
        # 添加统计信息
        toc_parts.append(self._create_statistics_section(chapters, sections))
        
        # 添加页脚
        toc_parts.append(self._create_toc_footer())
        
        self._toc_content = "\n\n".join(toc_parts)
        
        self.logger.info(f"目录生成完成，包含 {len(chapters)} 个章节，{len(sections)} 个小节")
        return self._toc_content
    
    def _create_toc_header(self, chapters: List[ChapterInfo], sections: List[SectionInfo]) -> str:
        """创建目录头部"""
        header_parts = [
            "# 目录",
            "",
            f"📚 **文档拆分完成** - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            "",
            f"本文档已被拆分为 **{len(chapters)}** 个章节文件"
        ]
        
        if self.config.create_sections and sections:
            header_parts.append(f"和 **{len(sections)}** 个小节文件。")
        else:
            header_parts.append("。")
        
        header_parts.extend([
            "",
            "---",
            ""
        ])
        
        return "\n".join(header_parts)
    
    def _create_chapters_toc(self, chapters: List[ChapterInfo]) -> str:
        """创建章节目录"""
        toc_parts = [
            "## 📖 章节目录",
            ""
        ]
        
        for i, chapter in enumerate(chapters, 1):
            # 章节链接
            if chapter.file_path:
                chapter_link = f"[{chapter.title}]({chapter.file_path})"
            else:
                chapter_link = chapter.title
            
            # 章节信息
            info_parts = []
            if chapter.line_count > 0:
                info_parts.append(f"{chapter.line_count} 行")
            if chapter.has_sections:
                info_parts.append(f"{len(chapter.sections)} 个小节")
            
            info_text = f" *({', '.join(info_parts)})*" if info_parts else ""
            
            toc_parts.append(f"{i}. {chapter_link}{info_text}")
        
        return "\n".join(toc_parts)
    
    def _create_sections_toc(self, sections: List[SectionInfo]) -> str:
        """创建小节目录"""
        if not sections:
            return ""
        
        toc_parts = [
            "## 📝 小节目录",
            ""
        ]
        
        # 按章节分组小节
        sections_by_chapter = self._group_sections_by_chapter(sections)
        
        for chapter_title, chapter_sections in sections_by_chapter.items():
            toc_parts.append(f"### {chapter_title}")
            toc_parts.append("")
            
            for section in chapter_sections:
                # 小节链接
                if section.file_path:
                    section_link = f"[{section.title}]({section.file_path})"
                else:
                    section_link = section.title
                
                # 小节信息
                info_parts = []
                if section.line_count > 0:
                    info_parts.append(f"{section.line_count} 行")
                if section.has_tags:
                    info_parts.append(f"{len(section.tags)} 个标签")
                
                info_text = f" *({', '.join(info_parts)})*" if info_parts else ""
                
                # 根据级别添加缩进
                indent = "  " * (section.level - 2) if section.level > 2 else ""
                toc_parts.append(f"{indent}- {section_link}{info_text}")
            
            toc_parts.append("")
        
        return "\n".join(toc_parts)
    
    def _group_sections_by_chapter(self, sections: List[SectionInfo]) -> Dict[str, List[SectionInfo]]:
        """按章节分组小节"""
        grouped = {}
        for section in sections:
            chapter_title = section.chapter_title
            if chapter_title not in grouped:
                grouped[chapter_title] = []
            grouped[chapter_title].append(section)
        
        # 按章节标题排序
        return dict(sorted(grouped.items()))
    
    def _create_statistics_section(self, chapters: List[ChapterInfo], sections: List[SectionInfo]) -> str:
        """创建统计信息部分"""
        stats_parts = [
            "## 📊 文档统计",
            ""
        ]
        
        # 基本统计
        total_lines = sum(chapter.line_count for chapter in chapters)
        stats_parts.extend([
            f"- **总章节数**: {len(chapters)}",
            f"- **总行数**: {total_lines:,}",
        ])
        
        if self.config.create_sections and sections:
            stats_parts.append(f"- **总小节数**: {len(sections)}")
            
            # 小节级别分布
            level_counts = {}
            for section in sections:
                level_counts[section.level] = level_counts.get(section.level, 0) + 1
            
            if level_counts:
                stats_parts.append("- **小节级别分布**:")
                for level in sorted(level_counts.keys()):
                    level_name = self._get_level_name(level)
                    stats_parts.append(f"  - {level_name}: {level_counts[level]} 个")
        
        # 标签统计
        if self.config.generate_tags and sections:
            all_tags = []
            for section in sections:
                all_tags.extend(section.tags)
            
            if all_tags:
                unique_tags = len(set(all_tags))
                stats_parts.extend([
                    f"- **总标签数**: {len(all_tags)}",
                    f"- **唯一标签数**: {unique_tags}"
                ])
        
        # 平均长度
        if chapters:
            avg_chapter_length = total_lines / len(chapters)
            stats_parts.append(f"- **平均章节长度**: {avg_chapter_length:.1f} 行")
        
        return "\n".join(stats_parts)
    
    def _get_level_name(self, level: int) -> str:
        """获取级别名称"""
        level_names = {
            1: "一级标题",
            2: "二级标题", 
            3: "三级标题",
            4: "四级标题",
            5: "五级标题",
            6: "六级标题"
        }
        return level_names.get(level, f"{level}级标题")
    
    def _create_toc_footer(self) -> str:
        """创建目录页脚"""
        footer_parts = [
            "---",
            "",
            "## 🔧 使用说明",
            "",
            "- 点击章节或小节标题可直接跳转到对应文件",
            "- 每个文件都包含返回目录的导航链接",
        ]
        
        if self.config.generate_tags:
            footer_parts.append("- 小节文件包含自动生成的关键词标签")
        
        footer_parts.extend([
            "",
            f"*由 BookSplitter 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return "\n".join(footer_parts)
    
    def _create_empty_toc(self) -> str:
        """创建空目录"""
        return """# 目录

⚠️ **未找到章节内容**

请检查源文档是否包含有效的章节标题。

---

*由 BookSplitter 自动生成*"""
    
    def save_toc(self, chapters: List[ChapterInfo], sections: List[SectionInfo] = None) -> str:
        """生成并保存目录文件
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表（可选）
            
        Returns:
            目录文件路径
        """
        try:
            # 生成目录内容
            toc_content = self.generate_toc(chapters, sections)
            
            # 确定目录文件路径
            toc_path = Path(self.config.output_dir) / self.config.toc_filename
            
            # 确保输出目录存在
            toc_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(toc_path, 'w', encoding='utf-8') as f:
                f.write(toc_content)
            
            self.logger.info(f"目录文件已保存: {toc_path}")
            return str(toc_path)
            
        except Exception as e:
            self.logger.error(f"保存目录文件失败: {str(e)}")
            raise
    
    def add_navigation_links(self, file_path: str, toc_path: str = None) -> str:
        """为文件添加返回目录的导航链接
        
        Args:
            file_path: 目标文件路径
            toc_path: 目录文件路径（可选）
            
        Returns:
            更新后的文件路径
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
                return str(file_path)
            
            # 确定目录文件路径
            if toc_path is None:
                toc_path = Path(self.config.output_dir) / self.config.toc_filename
            else:
                toc_path = Path(toc_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已有导航链接
            if "返回目录" in content:
                self.logger.debug(f"文件已包含导航链接: {file_path}")
                return str(file_path)
            
            # 生成导航链接
            navigation = self._create_navigation_for_file(file_path, toc_path)
            
            # 添加导航链接到文件末尾
            if not content.endswith('\n'):
                content += '\n'
            
            content += f"\n---\n\n{navigation}\n"
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"已添加导航链接: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"添加导航链接失败 '{file_path}': {str(e)}")
            raise
    
    def _create_navigation_for_file(self, file_path: Path, toc_path: Path) -> str:
        """为特定文件创建导航链接"""
        try:
            # 计算相对路径
            relative_toc = Path("..") / toc_path.name
            
            # 确定文件类型
            if "chapters" in str(file_path):
                file_type = "章节"
            elif "sections" in str(file_path):
                file_type = "小节"
            else:
                file_type = "文档"
            
            # 生成导航内容
            navigation_parts = [
                f"[← 返回目录]({relative_toc})",
                f"*{file_type}文件*"
            ]
            
            return " | ".join(navigation_parts)
            
        except Exception as e:
            self.logger.warning(f"创建导航链接失败: {str(e)}")
            return "[← 返回目录](../目录.md)"
    
    def create_cross_references(self, chapters: List[ChapterInfo], sections: List[SectionInfo] = None) -> Dict[str, List[str]]:
        """创建交叉引用映射
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表（可选）
            
        Returns:
            交叉引用映射字典
        """
        cross_refs = {}
        sections = sections or []
        
        # 为每个章节创建相关链接
        for chapter in chapters:
            refs = []
            
            # 添加章节内的小节链接
            chapter_sections = [s for s in sections if s.chapter_title == chapter.title]
            for section in chapter_sections:
                if section.file_path:
                    refs.append(f"[{section.title}]({section.file_path})")
            
            cross_refs[chapter.title] = refs
        
        # 为每个小节创建相关链接
        for section in sections:
            refs = []
            
            # 添加所属章节链接
            parent_chapter = next((c for c in chapters if c.title == section.chapter_title), None)
            if parent_chapter and parent_chapter.file_path:
                refs.append(f"[{parent_chapter.title}]({parent_chapter.file_path})")
            
            # 添加同章节的其他小节链接
            sibling_sections = [s for s in sections 
                              if s.chapter_title == section.chapter_title and s != section]
            for sibling in sibling_sections[:5]:  # 限制数量
                if sibling.file_path:
                    refs.append(f"[{sibling.title}]({sibling.file_path})")
            
            cross_refs[section.title] = refs
        
        return cross_refs
    
    def generate_sitemap(self, chapters: List[ChapterInfo], sections: List[SectionInfo] = None) -> str:
        """生成站点地图
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表（可选）
            
        Returns:
            站点地图内容
        """
        sections = sections or []
        
        sitemap_parts = [
            "# 站点地图",
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 文件结构",
            ""
        ]
        
        # 目录文件
        sitemap_parts.append(f"- [{self.config.toc_filename}]({self.config.toc_filename})")
        
        # 章节文件
        if chapters:
            sitemap_parts.append("- chapters/")
            for chapter in chapters:
                if chapter.file_path:
                    sitemap_parts.append(f"  - [{Path(chapter.file_path).name}]({chapter.file_path})")
        
        # 小节文件
        if self.config.create_sections and sections:
            sitemap_parts.append("- sections/")
            for section in sections:
                if section.file_path:
                    sitemap_parts.append(f"  - [{Path(section.file_path).name}]({section.file_path})")
        
        # 图片目录
        if self.config.preserve_images:
            sitemap_parts.append("- images/")
            sitemap_parts.append("  - *(图片文件)*")
        
        return "\n".join(sitemap_parts)
    
    def validate_links(self, chapters: List[ChapterInfo], sections: List[SectionInfo] = None) -> Dict[str, List[str]]:
        """验证链接有效性
        
        Args:
            chapters: 章节信息列表
            sections: 小节信息列表（可选）
            
        Returns:
            验证结果，包含无效链接列表
        """
        sections = sections or []
        validation_result = {
            'valid_links': [],
            'invalid_links': [],
            'missing_files': []
        }
        
        base_dir = Path(self.config.output_dir)
        
        # 验证章节文件
        for chapter in chapters:
            if chapter.file_path:
                file_path = base_dir / chapter.file_path
                if file_path.exists():
                    validation_result['valid_links'].append(str(chapter.file_path))
                else:
                    validation_result['missing_files'].append(str(chapter.file_path))
        
        # 验证小节文件
        for section in sections:
            if section.file_path:
                file_path = base_dir / section.file_path
                if file_path.exists():
                    validation_result['valid_links'].append(str(section.file_path))
                else:
                    validation_result['missing_files'].append(str(section.file_path))
        
        return validation_result
    
    def get_statistics(self) -> Dict[str, any]:
        """获取链接管理器统计信息"""
        return {
            'output_dir': self.config.output_dir,
            'toc_filename': self.config.toc_filename,
            'toc_generated': self._toc_content is not None,
            'navigation_links_count': len(self._navigation_links),
            'config': {
                'create_sections': self.config.create_sections,
                'add_navigation': self.config.add_navigation,
                'generate_tags': self.config.generate_tags,
                'preserve_images': self.config.preserve_images
            }
        }