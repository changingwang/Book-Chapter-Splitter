#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
书籍章节拆分器 - 命令行接口

此模块提供命令行接口，用于从命令行运行拆分器。
"""

import os
import sys
import click
import logging

from .main import BookSplitter
from .config import ProcessingConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@click.command()
@click.option('-i', '--input', default='full.md', help='输入的markdown文件路径')
@click.option('-o', '--output', default='output', help='输出目录路径')
@click.option('-c', '--config', default=None, help='配置文件路径')
@click.option('--sections/--no-sections', default=True, help='是否拆分小节')
@click.option('--tags/--no-tags', default=True, help='是否生成标签')
@click.option('--navigation/--no-navigation', default=True, help='是否添加导航链接')
@click.option('--min-tags', default=3, help='每个小节的最少标签数')
@click.option('--max-tags', default=8, help='每个小节的最多标签数')
def main(input, output, config, sections, tags, navigation, min_tags, max_tags):
    """书籍章节拆分器 - 将大型markdown文档拆分为章节和小节文件"""
    try:
        # 创建配置
        if config:
            cfg = ProcessingConfig(config)
        else:
            cfg = ProcessingConfig()
            
        # 更新命令行参数
        cfg.source_file = input
        cfg.output_dir = output
        cfg.create_sections = sections
        cfg.generate_tags = tags
        cfg.add_navigation = navigation
        cfg.min_tags_per_section = min_tags
        cfg.max_tags_per_section = max_tags
        
        # 创建拆分器并处理
        splitter = BookSplitter(cfg)
        result = splitter.process()
        
        if result['status'] == 'success':
            click.echo(f"\n✅ 处理完成！")
            click.echo(f"📊 统计信息:")
            click.echo(f"  - 总章节数: {result['chapters_count']}")
            click.echo(f"  - 总小节数: {result['sections_count']}")
            click.echo(f"  - 生成文件数: {result['generated_files_count']}")
            click.echo(f"  - 处理时间: {result['elapsed_time']:.2f} 秒")
            click.echo(f"\n📂 输出目录: {os.path.abspath(output)}")
            click.echo(f"📄 目录文件: {os.path.join(os.path.abspath(output), '目录.md')}")
            return 0
        else:
            click.echo(f"\n❌ 处理失败: {result['error']}")
            return 1
            
    except Exception as e:
        click.echo(f"\n❌ 发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
