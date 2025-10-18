#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置文件转换工具

将JSON配置文件转换为YAML格式，或将YAML配置文件转换为JSON格式
"""

import os
import sys
import json
import yaml
import argparse

def convert_json_to_yaml(json_file, yaml_file=None):
    """将JSON配置文件转换为YAML格式"""
    if yaml_file is None:
        yaml_file = os.path.splitext(json_file)[0] + '.yaml'
    
    with open(json_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"已将 {json_file} 转换为 {yaml_file}")
    return yaml_file

def convert_yaml_to_json(yaml_file, json_file=None):
    """将YAML配置文件转换为JSON格式"""
    if json_file is None:
        json_file = os.path.splitext(yaml_file)[0] + '.json'
    
    with open(yaml_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"已将 {yaml_file} 转换为 {json_file}")
    return json_file

def main():
    parser = argparse.ArgumentParser(description='配置文件格式转换工具')
    parser.add_argument('input_file', help='输入配置文件路径')
    parser.add_argument('--output', '-o', help='输出配置文件路径')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output
    
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        sys.exit(1)
    
    ext = os.path.splitext(input_file)[1].lower()
    
    if ext == '.json':
        convert_json_to_yaml(input_file, output_file)
    elif ext in ['.yaml', '.yml']:
        convert_yaml_to_json(input_file, output_file)
    else:
        print(f"错误：不支持的文件格式 {ext}")
        sys.exit(1)

if __name__ == '__main__':
    main()
