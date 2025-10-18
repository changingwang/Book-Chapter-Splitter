"""
配置管理模块

定义处理配置类和相关的配置管理功能。
"""

# 模块导入区
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml
import json


@dataclass
class ProcessingConfig:
    """处理配置类"""
    
    # 基本文件配置
    source_file: str = "full.md"
    output_dir: str = "output"
    toc_filename: str = "目录.md"
    
    # 处理选项
    create_sections: bool = True
    add_navigation: bool = True
    preserve_images: bool = True
    generate_tags: bool = True
    
    # 标签生成配置
    max_tags_per_section: int = 8
    min_tags_per_section: int = 3
    
    # 文件名配置
    chapter_prefix: str = "第"
    section_prefix: str = "第"
    filename_separator: str = "_"
    
    # 目录结构配置
    chapters_subdir: str = "chapters"
    sections_subdir: str = "sections"
    images_subdir: str = "images"
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'ProcessingConfig':
        """从YAML文件加载配置"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
    
    def to_yaml(self, config_path: str):
        """保存配置到YAML文件"""
        config_data = {
            'source_file': self.source_file,
            'output_dir': self.output_dir,
            'toc_filename': self.toc_filename,
            'create_sections': self.create_sections,
            'add_navigation': self.add_navigation,
            'preserve_images': self.preserve_images,
            'generate_tags': self.generate_tags,
            'max_tags_per_section': self.max_tags_per_section,
            'min_tags_per_section': self.min_tags_per_section,
            'chapter_prefix': self.chapter_prefix,
            'section_prefix': self.section_prefix,
            'filename_separator': self.filename_separator,
            'chapters_subdir': self.chapters_subdir,
            'sections_subdir': self.sections_subdir,
            'images_subdir': self.images_subdir
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    @property
    def chapters_dir(self) -> str:
        """获取章节目录路径"""
        return str(Path(self.output_dir) / self.chapters_subdir)
    
    @property
    def sections_dir(self) -> str:
        """获取小节目录路径"""
        return str(Path(self.output_dir) / self.sections_subdir)
    
    @property
    def images_dir(self) -> str:
        """获取图片目录路径"""
        return str(Path(self.output_dir) / self.images_subdir)
    
    @property
    def toc_path(self) -> str:
        """获取目录文件路径"""
        return str(Path(self.output_dir) / self.toc_filename)
    
    def validate(self):
        """验证配置的有效性"""
        if not self.source_file:
            raise ValueError("源文件路径不能为空")
        
        if not self.output_dir:
            raise ValueError("输出目录不能为空")
        
        if self.max_tags_per_section < self.min_tags_per_section:
            raise ValueError("最大标签数不能小于最小标签数")
        
        if self.min_tags_per_section < 0:
            raise ValueError("最小标签数不能为负数")
    
    @classmethod
    def from_json(cls, config_path: str) -> 'ProcessingConfig':
        """从JSON文件加载配置"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return cls(**config_data)

    @classmethod
    def from_file(cls, config_path: str) -> 'ProcessingConfig':
        """根据扩展名自动从文件加载配置（支持 YAML/JSON）"""
        ext = Path(config_path).suffix.lower()
        if ext in ['.yaml', '.yml']:
            return cls.from_yaml(config_path)
        elif ext == '.json':
            return cls.from_json(config_path)
        else:
            # 优雅降级：先尝试 YAML，再尝试 JSON
            try:
                return cls.from_yaml(config_path)
            except Exception:
                return cls.from_json(config_path)