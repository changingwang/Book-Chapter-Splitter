"""
链接管理器 - 负责管理章节和部分之间的链接关系
"""

from typing import Dict, List, Optional, Set
from pathlib import Path

from ..models.chapter_info import ChapterInfo
from ..models.section_info import SectionInfo


class LinkManager:
    """管理章节和部分之间的链接关系"""
    
    def __init__(self):
        """初始化链接管理器"""
        self.chapter_links: Dict[int, Dict[str, str]] = {}  # chapter_number -> {link_type: target}
        self.section_links: Dict[str, Dict[str, str]] = {}  # section_id -> {link_type: target}
        self.cross_references: Dict[str, List[str]] = {}    # source_id -> [target_ids]
        
    def create_chapter_links(self, chapters: List[ChapterInfo], 
                           file_generator) -> Dict[int, Dict[str, str]]:
        """
        创建章节链接
        
        Args:
            chapters: 章节信息列表
            file_generator: 文件生成器实例
            
        Returns:
            章节链接映射
        """
        self.chapter_links.clear()
        
        # 按章节号排序
        sorted_chapters = sorted(chapters, key=lambda x: x.chapter_number)
        
        for i, chapter in enumerate(sorted_chapters):
            links = {}
            
            # 上一章链接
            if i > 0:
                prev_chapter = sorted_chapters[i - 1]
                prev_filename = file_generator._generate_chapter_filename(prev_chapter)
                links["prev"] = prev_filename
            
            # 下一章链接
            if i < len(sorted_chapters) - 1:
                next_chapter = sorted_chapters[i + 1]
                next_filename = file_generator._generate_chapter_filename(next_chapter)
                links["next"] = next_filename
            
            # 目录链接
            links["toc"] = "README.md"  # 假设目录在README.md中
            
            self.chapter_links[chapter.chapter_number] = links
        
        return self.chapter_links.copy()
    
    def create_section_links(self, sections: List[SectionInfo], 
                           file_generator) -> Dict[str, Dict[str, str]]:
        """
        创建部分链接
        
        Args:
            sections: 部分信息列表
            file_generator: 文件生成器实例
            
        Returns:
            部分链接映射
        """
        self.section_links.clear()
        
        # 按章节和小节号排序
        sorted_sections = sorted(sections, key=lambda x: (x.chapter_number, x.section_number))
        
        # 按章节分组
        chapter_groups = {}
        for section in sorted_sections:
            if section.chapter_number not in chapter_groups:
                chapter_groups[section.chapter_number] = []
            chapter_groups[section.chapter_number].append(section)
        
        for chapter_num, chapter_sections in chapter_groups.items():
            chapter_sections.sort(key=lambda x: x.section_number)
            
            for i, section in enumerate(chapter_sections):
                section_id = self._get_section_id(section)
                links = {}
                
                # 同一章节内的上一节链接
                if i > 0:
                    prev_section = chapter_sections[i - 1]
                    prev_filename = file_generator._generate_section_filename(prev_section)
                    links["prev"] = prev_filename
                
                # 同一章节内的下一节链接
                if i < len(chapter_sections) - 1:
                    next_section = chapter_sections[i + 1]
                    next_filename = file_generator._generate_section_filename(next_section)
                    links["next"] = next_filename
                
                # 章节首页链接
                chapter_filename = file_generator._generate_chapter_filename(
                    ChapterInfo(chapter_num, f"Chapter {chapter_num}", 0, 0)
                )
                links["chapter"] = chapter_filename
                
                # 目录链接
                links["toc"] = "README.md"
                
                self.section_links[section_id] = links
        
        return self.section_links.copy()
    
    def analyze_cross_references(self, content: str, current_section_id: str) -> List[str]:
        """
        分析内容中的交叉引用
        
        Args:
            content: 文本内容
            current_section_id: 当前部分的ID
            
        Returns:
            引用的目标ID列表
        """
        references = []
        
        # 查找章节引用（如"参见第1章"）
        chapter_refs = re.findall(r'第(\d+)章', content)
        for chapter_num in chapter_refs:
            ref_id = f"chapter_{chapter_num}"
            if ref_id not in references:
                references.append(ref_id)
        
        # 查找小节引用（如"参见1.1节"）
        section_refs = re.findall(r'(\d+\.\d+)节', content)
        for section_ref in section_refs:
            ref_id = f"section_{section_ref.replace('.', '_')}"
            if ref_id not in references:
                references.append(ref_id)
        
        # 查找图表引用（如"见图1-1"）
        figure_refs = re.findall(r'[见图表表](\d+-\d+)', content)
        for figure_ref in figure_refs:
            ref_id = f"figure_{figure_ref.replace('-', '_')}"
            if ref_id not in references:
                references.append(ref_id)
        
        # 记录交叉引用
        if references:
            self.cross_references[current_section_id] = references
        
        return references
    
    def generate_navigation_html(self, links: Dict[str, str], current_title: str) -> str:
        """
        生成导航HTML
        
        Args:
            links: 链接字典
            current_title: 当前页面标题
            
        Returns:
            HTML导航代码
        """
        html_parts = ['<div class="navigation">']
        
        if "prev" in links:
            html_parts.append(f'<a href="{links["prev"]}" class="nav-prev">← 上一页</a>')
        
        if "toc" in links:
            html_parts.append(f'<a href="{links["toc"]}" class="nav-toc">目录</a>')
        
        if "next" in links:
            html_parts.append(f'<a href="{links["next"]}" class="nav-next">下一页 →</a>')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def generate_markdown_navigation(self, links: Dict[str, str]) -> str:
        """
        生成Markdown格式的导航
        
        Args:
            links: 链接字典
            
        Returns:
            Markdown导航文本
        """
        md_parts = []
        
        if "prev" in links:
            md_parts.append(f'[← 上一页]({links["prev"]})')
        
        if "toc" in links:
            md_parts.append(f'[目录]({links["toc"]})')
        
        if "next" in links:
            md_parts.append(f'[下一页 →]({links["next"]})')
        
        if md_parts:
            return ' | '.join(md_parts) + '\n\n---\n'
        
        return ""
    
    def validate_links(self, output_dir: str) -> Dict[str, List[str]]:
        """
        验证所有链接的有效性
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            验证结果：{link_type: [错误信息]}
        """
        errors = {"chapter_links": [], "section_links": [], "cross_references": []}
        output_path = Path(output_dir)
        
        # 验证章节链接
        for chapter_num, links in self.chapter_links.items():
            for link_type, target in links.items():
                if not self._validate_link_target(output_path, target):
                    errors["chapter_links"].append(
                        f"章节{chapter_num}的{link_type}链接目标不存在: {target}"
                    )
        
        # 验证部分链接
        for section_id, links in self.section_links.items():
            for link_type, target in links.items():
                if not self._validate_link_target(output_path, target):
                    errors["section_links"].append(
                        f"部分{section_id}的{link_type}链接目标不存在: {target}"
                    )
        
        # 验证交叉引用（需要实际文件内容检查）
        for source_id, targets in self.cross_references.items():
            for target_id in targets:
                # 这里可以添加更复杂的交叉引用验证逻辑
                pass
        
        return errors
    
    def _validate_link_target(self, output_path: Path, target: str) -> bool:
        """验证链接目标是否存在"""
        if not target:
            return False
        
        target_path = output_path / target
        return target_path.exists()
    
    def _get_section_id(self, section: SectionInfo) -> str:
        """获取部分的唯一ID"""
        return f"section_{section.chapter_number}_{section.section_number}"
    
    def get_link_statistics(self) -> Dict[str, any]:
        """获取链接统计信息"""
        total_chapter_links = sum(len(links) for links in self.chapter_links.values())
        total_section_links = sum(len(links) for links in self.section_links.values())
        total_cross_refs = sum(len(refs) for refs in self.cross_references.values())
        
        return {
            "total_chapters": len(self.chapter_links),
            "total_sections": len(self.section_links),
            "total_chapter_links": total_chapter_links,
            "total_section_links": total_section_links,
            "total_cross_references": total_cross_refs,
            "avg_links_per_chapter": total_chapter_links / len(self.chapter_links) if self.chapter_links else 0,
            "avg_links_per_section": total_section_links / len(self.section_links) if self.section_links else 0,
            "chapters_with_links": [num for num, links in self.chapter_links.items() if links],
            "sections_with_links": [id for id, links in self.section_links.items() if links]
        }
    
    def export_link_map(self, format: str = "json") -> str:
        """
        导出链接映射
        
        Args:
            format: 导出格式 ("json", "yaml", "csv")
            
        Returns:
            格式化后的链接映射
        """
        import json
        import yaml
        import csv
        from io import StringIO
        
        data = {
            "chapter_links": self.chapter_links,
            "section_links": self.section_links,
            "cross_references": self.cross_references,
            "statistics": self.get_link_statistics()
        }
        
        if format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format == "yaml":
            return yaml.dump(data, allow_unicode=True)
        elif format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            
            # 写入章节链接
            writer.writerow(["Type", "Source", "Link Type", "Target"])
            for chapter_num, links in self.chapter_links.items():
                for link_type, target in links.items():
                    writer.writerow(["chapter", f"chapter_{chapter_num}", link_type, target])
            
            # 写入部分链接
            for section_id, links in self.section_links.items():
                for link_type, target in links.items():
                    writer.writerow(["section", section_id, link_type, target])
            
            return output.getvalue()
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def clear_all_links(self):
        """清除所有链接"""
        self.chapter_links.clear()
        self.section_links.clear()
        self.cross_references.clear()
    
    def find_broken_links(self, output_dir: str) -> List[Dict[str, str]]:
        """
        查找损坏的链接
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            损坏的链接列表
        """
        broken_links = []
        output_path = Path(output_dir)
        
        # 检查章节链接
        for chapter_num, links in self.chapter_links.items():
            for link_type, target in links.items():
                if not self._validate_link_target(output_path, target):
                    broken_links.append({
                        "type": "chapter",
                        "source": f"chapter_{chapter_num}",
                        "link_type": link_type,
                        "target": target,
                        "error": "目标文件不存在"
                    })
        
        # 检查部分链接
        for section_id, links in self.section_links.items():
            for link_type, target in links.items():
                if not self._validate_link_target(output_path, target):
                    broken_links.append({
                        "type": "section",
                        "source": section_id,
                        "link_type": link_type,
                        "target": target,
                        "error": "目标文件不存在"
                    })
        
        return broken_links
    
    def generate_sitemap(self, output_dir: str) -> str:
        """
        生成网站地图
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            sitemap.xml内容
        """
        import datetime
        
        output_path = Path(output_dir)
        base_url = "https://example.com"  # 需要根据实际情况修改
        
        sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        # 添加章节文件
        for chapter_num in self.chapter_links.keys():
            filename = f"chapter_{chapter_num:02d}.md"
            filepath = output_path / filename
            if filepath.exists():
                url = f"{base_url}/{filename}"
                lastmod = datetime.datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                sitemap.append(f'  <url>')
                sitemap.append(f'    <loc>{url}</loc>')
                sitemap.append(f'    <lastmod>{lastmod}</lastmod>')
                sitemap.append(f'    <changefreq>monthly</changefreq>')
                sitemap.append(f'    <priority>0.8</priority>')
                sitemap.append(f'  </url>')
        
        # 添加部分文件
        for section_id in self.section_links.keys():
            # 从section_id提取文件名（需要根据实际命名规则调整）
            filename = f"{section_id}.md"
            filepath = output_path / filename
            if filepath.exists():
                url = f"{base_url}/{filename}"
                lastmod = datetime.datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                sitemap.append(f'  <url>')
                sitemap.append(f'    <loc>{url}</loc>')
                sitemap.append(f'    <lastmod>{lastmod}</lastmod>')
                sitemap.append(f'    <changefreq>monthly</changefreq>')
                sitemap.append(f'    <priority>0.6</priority>')
                sitemap.append(f'  </url>')
        
        sitemap.append('</urlset>')
        
        return '\n'.join(sitemap)