"""
命令行接口模块

提供用户友好的命令行接口。
"""

import click
import sys
from pathlib import Path

from .main import BookSplitter
from .config import ProcessingConfig


# function main
@click.command()
@click.option('--input', '-i', 'input_file', 
              default='full.md',
              help='输入的markdown文件路径')
@click.option('--output', '-o', 'output_dir',
              default='output',
              help='输出目录路径')
@click.option('--config', '-c', 'config_file',
              help='配置文件路径')
@click.option('--no-sections', is_flag=True,
              help='不创建小节文件，仅创建章节文件')
@click.option('--no-tags', is_flag=True,
              help='不生成标签')
@click.option('--no-navigation', is_flag=True,
              help='不添加导航链接')
@click.option('--min-tags', type=int, help='每个小节的最少标签数')
@click.option('--max-tags', type=int, help='每个小节的最多标签数')
@click.version_option(version='1.0.1')
def main(input_file, output_dir, config_file, no_sections, no_tags, no_navigation, min_tags, max_tags):
    """
    书籍章节拆分器 - 将markdown书籍拆分为独立的章节和小节文件
    """
    try:
        # 加载配置（支持 YAML/JSON）
        if config_file:
            if not Path(config_file).exists():
                click.echo(f"错误: 配置文件不存在: {config_file}", err=True)
                sys.exit(1)
            config = ProcessingConfig.from_file(config_file)
        else:
            config = ProcessingConfig()
        
        # 覆盖命令行参数
        if input_file != 'full.md':
            config.source_file = input_file
        if output_dir != 'output':
            config.output_dir = output_dir
        if no_sections:
            config.create_sections = False
        if no_tags:
            config.generate_tags = False
        if no_navigation:
            config.add_navigation = False
        if min_tags is not None:
            config.min_tags_per_section = min_tags
        if max_tags is not None:
            config.max_tags_per_section = max_tags
        
        # 检查输入文件
        if not Path(config.source_file).exists():
            click.echo(f"错误: 输入文件不存在: {config.source_file}", err=True)
            sys.exit(1)
        
        # 显示配置信息
        click.echo(f"输入文件: {config.source_file}")
        click.echo(f"输出目录: {config.output_dir}")
        click.echo(f"创建小节: {'是' if config.create_sections else '否'}")
        click.echo(f"生成标签: {'是' if config.generate_tags else '否'}")
        click.echo(f"添加导航: {'是' if config.add_navigation else '否'}")
        click.echo(f"标签范围: {config.min_tags_per_section}-{config.max_tags_per_section}")
        click.echo()
        
        # 执行处理
        splitter = BookSplitter(config)
        result = splitter.process()
        
        if result['status'] == 'success':
            click.echo("✅ 处理完成!")
            click.echo(f"输出目录: {result['output_dir']}")
            # TODO: 在后续任务中添加更详细的统计信息
        else:
            click.echo(f"❌ 处理失败: {result.get('error', '未知错误')}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ 发生错误: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()