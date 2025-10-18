# 使用指南

本文档提供了书籍章节拆分器的详细使用说明和示例。

## 基本概念

### 支持的文档结构

书籍章节拆分器专门设计用于处理具有层次结构的中文markdown文档。它能够识别以下格式：

#### 章节标题格式

**支持的格式：**
- `# 第一章 标题内容`
- `# 第二章 标题内容`
- `# 第1章 标题内容`
- `# 第2章 标题内容`

**⚠️ 格式要求：**
- 章节标题中**不能包含下划线 `_`**
- 正确：`# 第一章 导论：对象和地位`
- 错误：`# 第一章_导论：对象和地位`

**格式修复工具：**
如果您的文档包含下划线格式的章节标题，可以使用提供的修复工具：
```bash
python fix_chapter_titles.py
```
该工具会自动将章节标题中的下划线替换为空格，并创建备份文件。

📋 **完整格式规范请参考：[FORMAT_REQUIREMENTS.md](FORMAT_REQUIREMENTS.md)**

#### 小节标题格式
- `一、小节标题`
- `二、小节标题`
- `1、小节标题`
- `2、小节标题`
- `(一)小节标题`
- `(二)小节标题`

### 文件命名规范

工具会自动生成规范化的文件名：

- **章节文件**: `第X章_标题.md` (如: `第一章_导论.md`)
- **小节文件**: `X.Y_标题.md` (如: `1.1_研究背景.md`, `2.3_案例分析.md`)

其中 X 是章节编号，Y 是该章节内的小节编号。这种格式确保文件按逻辑顺序排列。

### 处理流程

1. **结构分析**: 扫描文档，识别章节和小节边界
2. **内容提取**: 基于行号范围提取各部分内容
3. **标签生成**: 使用TF-IDF和TextRank算法生成关键词标签
4. **文件生成**: 创建独立的markdown文件，使用规范化文件名
5. **目录生成**: 创建层次化的目录文档
6. **导航链接**: 为每个文件添加导航链接

## 命令行使用

### 基本命令

```bash
# 最简单的使用方式
注意：首次使用 CLI 或出现"找不到模块"提示时，请先在项目根目录执行可编辑安装：`pip install -e .`。这样修改源码会即时生效，并可在任意路径运行 CLI。
python -m book_splitter input.md

# 指定输出目录
python -m book_splitter input.md -o my_output

# 查看帮助
python -m book_splitter --help
```

### 完整选项

```bash
python -m book_splitter input.md \\
  --output output_directory \\
  --sections \\
  --tags \\
  --navigation \\
  --images \\
  --min-tags 2 \\
  --max-tags 6
```

### 选项说明

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-o, --output` | 输出目录路径 | `output` |
| `--sections / --no-sections` | 是否拆分小节 | `--sections` |
| `--tags / --no-tags` | 是否生成标签 | `--tags` |
| `--navigation / --no-navigation` | 是否添加导航链接 | `--navigation` |
| `--images / --no-images` | 是否处理图片 | `--images` |
| `--min-tags` | 每个小节最少标签数 | `3` |
| `--max-tags` | 每个小节最多标签数 | `8` |

## 使用场景

### 场景1：学术论文拆分

**需求**: 将一篇长篇学术论文按章节拆分，便于阅读和引用。

**命令**:
```bash
python -m book_splitter thesis.md -o thesis_chapters --no-sections --tags
```

**结果**: 生成章节文件和目录，每个章节包含相关标签。

### 场景2：技术文档处理

**需求**: 将技术手册拆分成章节和小节，保留图片，添加导航。

**命令**:
```bash
python -m book_splitter manual.md -o manual_split --sections --navigation --images
```

**结果**: 完整的层次化文档结构，包含图片和导航链接。

### 场景3：教材内容整理

**需求**: 将教材按章节和小节拆分，生成详细标签用于知识管理。

**命令**:
```bash
python -m book_splitter textbook.md -o textbook_organized \\
  --sections --tags --navigation \\
  --min-tags 4 --max-tags 10
```

**结果**: 详细的知识点标签和完整的导航结构。

### 场景4：批量处理

**需求**: 处理多个文档文件。

**Python脚本**:
```python
from book_splitter import BookSplitter, ProcessingConfig
import os

# 配置
config = ProcessingConfig()
config.create_sections = True
config.generate_tags = True
config.add_navigation = True

splitter = BookSplitter(config)

# 批量处理
input_files = ["book1.md", "book2.md", "book3.md"]
for input_file in input_files:
    output_dir = f"output_{os.path.splitext(input_file)[0]}"
    config.source_file = input_file
    config.output_dir = output_dir
    
    result = splitter.process()
    print(f"{input_file}: {result['status']}")
```

## 配置文件使用

### 创建配置文件

创建 `config.json` 文件：

```json
{
  "source_file": "my_book.md",
  "output_dir": "my_output",
  "create_sections": true,
  "generate_tags": true,
  "add_navigation": true,
  "preserve_images": true,
  "min_tags_per_section": 3,
  "max_tags_per_section": 8,
  "filename_separator": "-"
}
```

### 使用配置文件

```bash
python -m book_splitter --config config.json
```

## 输出结构详解

### 目录结构

```
output/
├── 目录.md                    # 主目录文件
├── chapters/                  # 章节目录
│   ├── 第一章_导论.md
│   ├── 第二章_理论基础.md
│   └── ...
├── sections/                  # 小节目录（如果启用小节拆分）
│   ├── 1.1_研究背景.md
│   ├── 1.2_研究意义.md
│   └── ...
└── images/                    # 图片目录（如果包含图片）
    ├── image1.png
    ├── image2.jpg
    └── ...
```

### 目录文件内容

目录文件 (`目录.md`) 包含：

1. **文档统计信息**: 总章节数、小节数、文件数
2. **章节列表**: 按顺序排列的章节链接
3. **小节列表**: 按章节组织的详细小节链接
4. **标签索引**: 按标签分类的内容索引

### 文件内容结构

每个生成的markdown文件包含：

1. **标题**: 原始章节/小节标题
2. **内容**: 原始markdown内容
3. **标签**: 自动生成的关键词标签
4. **导航**: 返回目录的链接
5. **元数据**: 创建时间、处理信息等

## Python API 使用

### 基本使用

```python
from book_splitter import BookSplitter, ProcessingConfig

# 创建配置
config = ProcessingConfig()
config.source_file = "my_book.md"
config.output_dir = "output"
config.create_sections = True
config.generate_tags = True
config.add_navigation = True

# 创建拆分器实例
splitter = BookSplitter(config)

# 执行处理
result = splitter.process()

# 查看结果
print(f"状态: {result['status']}")
print(f"章节数: {result['chapter_count']}")
print(f"小节数: {result['section_count']}")
print(f"输出目录: {result['output_dir']}")
```

### 高级配置

```python
from book_splitter import BookSplitter, ProcessingConfig

# 详细配置
config = ProcessingConfig(
    source_file="document.md",
    output_dir="processed_output",
    create_sections=True,
    generate_tags=True,
    add_navigation=True,
    preserve_images=True,
    min_tags_per_section=3,
    max_tags_per_section=8,
    filename_separator="-",
    tag_algorithms=["tfidf", "textrank"],
    tag_weights={"tfidf": 0.6, "textrank": 0.4}
)

splitter = BookSplitter(config)
result = splitter.process()
```

### 自定义处理

```python
from book_splitter import (
    BookSplitter, ProcessingConfig,
    StructureAnalyzer, ContentExtractor,
    TagGenerator, FileGenerator, LinkManager
)

# 自定义处理流程
config = ProcessingConfig(source_file="book.md", output_dir="output")

# 单独使用组件
analyzer = StructureAnalyzer(config)
chapters, sections = analyzer.analyze_structure()

extractor = ContentExtractor(config)
content_blocks = extractor.extract_contents(chapters, sections)

tag_generator = TagGenerator(config)
tagged_blocks = tag_generator.generate_tags(content_blocks)

file_generator = FileGenerator(config)
file_generator.generate_files(tagged_blocks)

link_manager = LinkManager(config)
link_manager.create_navigation(tagged_blocks)
```

## 错误处理和调试

### 常见错误

1. **文件不存在错误**:
   ```
   FileNotFoundError: 输入文件不存在: nonexistent.md
   ```
   
   **解决方案**: 检查文件路径是否正确

2. **格式错误**:
   ```
   ValueError: 未找到有效的章节标题
   ```
   
   **解决方案**: 检查文档格式，使用修复工具

3. **权限错误**:
   ```
   PermissionError: 无法写入输出目录
   ```
   
   **解决方案**: 检查目录权限或选择其他输出目录

### 调试模式

启用详细日志输出：

```bash
python -m book_splitter input.md --verbose
```

或者在代码中启用调试：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from book_splitter import BookSplitter, ProcessingConfig
# ...
```

## 性能优化

### 处理大文档

对于大型文档（>10MB），建议：

1. **禁用标签生成**: 减少内存使用
   ```bash
   python -m book_splitter large.md --no-tags
   ```

2. **分批处理**: 使用Python API进行分批处理

3. **增加内存**: 确保系统有足够内存

### 内存管理

工具会自动优化内存使用：

- 使用流式读取处理大文件
- 分批处理内容块
- 及时释放不再需要的资源

## 示例

### 示例文档

项目包含示例文档 `data/demo.md`，可用于测试：

```bash
python -m book_splitter data/demo.md -o demo_output --sections --tags
```

### 自定义示例

创建测试文档 `test.md`:

```markdown
# 第一章 引言

这是第一章的内容。

## 一、研究背景

研究背景描述...

## 二、研究意义

研究意义描述...

# 第二章 理论基础

第二章内容...
```

处理测试文档：

```bash
python -m book_splitter test.md -o test_output --sections
```

## 故障排除

详细故障排除指南请参考：[TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 支持与反馈

如果遇到问题或有建议：

1. 查看详细文档
2. 检查常见问题
3. 提交Issue报告问题
4. 联系开发团队

---

**版本**: v1.0.1  
**最后更新**: 2025-10-18  
**文档状态**: ✅ 完整