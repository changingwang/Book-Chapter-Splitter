# 使用指南

## 基本用法

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 准备配置文件
将 `config.example.json` 或 `config.example.yaml` 复制为 `config.json` 或 `config.yaml` 并根据需要修改配置。

3. 运行程序
```bash
python run_splitter.py --config config.json
```
或
```bash
python -m book_splitter --config config.yaml
```

## 配置选项

- `source_file`: 源Markdown文件路径
- `output_dir`: 输出目录
- `create_sections`: 是否创建小节文件
- `generate_tags`: 是否生成标签
- `add_navigation`: 是否添加导航链接
- `clean_filenames`: 是否清理文件名
- `toc_filename`: 目录文件名
- `chapters_dir`: 章节目录名
- `sections_dir`: 小节目录名
- `tags_dir`: 标签目录名

## 高级用法

### 作为库使用

```python
from book_splitter import BookSplitter, ProcessingConfig

config = ProcessingConfig()
config.source_file = "my_book.md"
config.output_dir = "output"

splitter = BookSplitter(config)
result = splitter.process()

print(f"处理完成，生成了 {result['generated_files_count']} 个文件")
```

### 自定义处理流程

```python
from book_splitter import BookSplitter, ProcessingConfig
from book_splitter.extractors import ContentExtractor
from book_splitter.analyzers import StructureAnalyzer

# 创建配置
config = ProcessingConfig()
config.source_file = "my_book.md"
config.output_dir = "output"

# 创建拆分器但不立即处理
splitter = BookSplitter(config)

# 手动执行处理步骤
extractor = ContentExtractor(config)
content = extractor.extract_from_file(config.source_file)

analyzer = StructureAnalyzer(config)
structure = analyzer.analyze(content)

# 生成文件
splitter.generate_files(structure, content)
```
