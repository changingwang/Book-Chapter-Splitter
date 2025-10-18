#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量处理工具

批量处理多个Markdown文件
"""

import os
import sys
import glob
import argparse
import json
import yaml
from pathlib import Path

# 添加父目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.book_splitter import BookSplitter, ProcessingConfig

def load_config(config_file):
    """加载配置文件"""
    ext = os.path.splitext(config_file)[1].lower()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        if ext == '.json':
            return json.load(f)
        elif ext in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的配置文件格式：{ext}")

def process_file(file_path, base_config, output_dir=None):
    """处理单个文件"""
    print(f"处理文件：{file_path}")
    
    # 创建配置
    config = ProcessingConfig()
    
    # 应用基础配置
    for key, value in base_config.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    # 设置文件特定配置
    config.source_file = file_path
    
    if output_dir:
        # 使用文件名作为子目录
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        config.output_dir = os.path.join(output_dir, file_name)
    
    # 处理文件
    splitter = BookSplitter(config)
    result = splitter.process()
    
    return result

def main():
    parser = argparse.ArgumentParser(description='批量处理Markdown文件')
    parser.add_argument('--config', '-c', required=True, help='基础配置文件路径')
    parser.add_argument('--input', '-i', required=True, help='输入文件或目录')
    parser.add_argument('--pattern', '-p', default='*.md', help='文件匹配模式（默认：*.md）')
    parser.add_argument('--output', '-o', help='输出根目录')
    
    args = parser.parse_args()
    
    # 加载基础配置
    base_config = load_config(args.config)
    
    # 获取输入文件列表
    if os.path.isdir(args.input):
        files = glob.glob(os.path.join(args.input, args.pattern))
    else:
        files = [args.input]
    
    if not files:
        print(f"没有找到匹配的文件：{args.pattern}")
        sys.exit(1)
    
    print(f"找到 {len(files)} 个文件待处理")
    
    # 处理文件
    results = []
    for file_path in files:
        try:
            result = process_file(file_path, base_config, args.output)
            results.append({
                'file': file_path,
                'status': result['status'],
                'files_count': result['generated_files_count']
            })
        except Exception as e:
            print(f"处理文件 {file_path} 时出错：{str(e)}")
            results.append({
                'file': file_path,
                'status': 'error',
                'error': str(e)
            })
    
    # 输出统计信息
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = len(results) - success_count
    
    print(f"\n处理完成：")
    print(f"  成功：{success_count}")
    print(f"  失败：{error_count}")
    
    if error_count > 0:
        print("\n失败的文件：")
        for r in results:
            if r['status'] != 'success':
                print(f"  {r['file']}: {r.get('error', '未知错误')}")

if __name__ == '__main__':
    main()
