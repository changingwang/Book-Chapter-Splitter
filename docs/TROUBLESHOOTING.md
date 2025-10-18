# 故障排除指南

本文档提供了使用书籍章节拆分器时可能遇到的常见问题及其解决方案。

## 🚨 常见错误

### 1. 文件和路径相关错误

#### FileNotFoundError: 源文件不存在

**错误信息**:
```
FileNotFoundError: 源文件不存在: input.md
```

**原因**:
- 输入文件路径不正确
- 文件不存在或已被删除
- 文件名拼写错误

**解决方案**:
```bash
# 检查文件是否存在
ls -la input.md

# 使用绝对路径
python -m book_splitter /full/path/to/input.md

# 检查当前目录
pwd
ls -la *.md
```

#### PermissionError: 权限不足

**错误信息**:
```
PermissionError: [Errno 13] Permission denied: 'output'
```

**原因**:
- 输出目录权限不足
- 文件被其他程序占用
- 系统权限限制

**解决方案**:
```bash
# 检查目录权限
ls -la output/

# 更改权限
chmod 755 output/

# 使用不同的输出目录
python -m book_splitter input.md -o ~/Documents/output

# Windows上以管理员身份运行
# 右键点击命令提示符 -> "以管理员身份运行"
```

### 2. 文档格式相关错误

#### ValueError: 未找到有效的章节结构

**错误信息**:
```
ValueError: 未找到有效的章节结构，请检查文档格式
```

**原因**:
- 文档中没有符合格式的章节标题
- 章节标题格式不正确
- 文档为空或只包含普通文本

**解决方案**:

1. **检查章节标题格式**:
   ```markdown
   # 第一章 标题内容    ✅ 正确
   # 第1章 标题内容     ✅ 正确
   ## 第一章 标题内容   ❌ 错误（应该是一级标题）
   第一章 标题内容      ❌ 错误（缺少#号）
   # Chapter 1 Title   ❌ 错误（不支持英文格式）
   # 第一章_标题内容    ❌ 错误（包含下划线）
   ```

   **⚠️ 特别注意：章节标题不能包含下划线**
   - 错误格式：`# 第一章_导论：对象和地位`
   - 正确格式：`# 第一章 导论：对象和地位`
   
   **快速修复下划线问题**：
   ```bash
   # 使用提供的修复工具
   python fix_chapter_titles.py
   
   # 或手动替换（Linux/Mac）
   sed -i 's/\(^# 第.*章\)_/\1 /g' input.md
   
   # 或手动替换（Windows PowerShell）
    (Get-Content input.md) -replace '(^# 第.*章)_', '$1 ' | Set-Content input.md
    ```

    📋 **完整格式规范和修复指导请参考：[FORMAT_REQUIREMENTS.md](FORMAT_REQUIREMENTS.md)**

2. **验证文档内容**:
   ```bash
   # 查看文档前几行
   head -20 input.md
   
   # 搜索章节标题
   grep "^# 第.*章" input.md
   ```

3. **修复文档格式**:
   ```markdown
   # 文档标题
   
   # 第一章 导论
   
   这里是第一章的内容...
   
   # 第二章 理论基础
   
   这里是第二章的内容...
   ```

#### 编码错误

**错误信息**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0
```

**原因**:
- 文件编码不是UTF-8
- 文件包含BOM标记
- 文件损坏

**解决方案**:
```bash
# 检查文件编码
file -bi input.md

# 转换编码为UTF-8
iconv -f gbk -t utf-8 input.md > input_utf8.md

# 移除BOM标记
sed -i '1s/^\xEF\xBB\xBF//' input.md

# 在Python中处理
python -c "
with open('input.md', 'r', encoding='utf-8-sig') as f:
    content = f.read()
with open('input_clean.md', 'w', encoding='utf-8') as f:
    f.write(content)
"
```

### 3. 依赖和环境相关错误

#### ModuleNotFoundError: 缺少依赖包

**错误信息**:
```
ModuleNotFoundError: No module named 'jieba'
```

**原因**:
- 未安装必需的依赖包
- Python环境不正确
- 虚拟环境未激活

**解决方案**:
```bash
# 安装所有依赖
pip install -r requirements.txt

# 单独安装缺失的包
pip install jieba scikit-learn networkx click

# 检查已安装的包
pip list | grep jieba

# 升级pip
pip install --upgrade pip

# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### ImportError: 导入错误

**错误信息**:
```
ImportError: cannot import name 'BookSplitter' from 'book_splitter'
```

**原因**:
- Python路径配置问题
- 模块结构不正确
- 文件名冲突

**解决方案**:
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 从项目根目录运行
cd /path/to/book-chapter-splitter
python -m book_splitter input.md

# 设置PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/book-chapter-splitter/src"

# 检查模块结构
find src/ -name "*.py" -type f
```

### 4. 内存和性能相关错误

#### MemoryError: 内存不足

**错误信息**:
```
MemoryError: Unable to allocate array
```

**原因**:
- 文档过大
- 系统内存不足
- 标签生成消耗大量内存

**解决方案**:
```bash
# 禁用标签生成
python -m book_splitter input.md --no-tags

# 只处理章节，不处理小节
python -m book_splitter input.md --no-sections

# 分割大文档
split -l 1000 input.md input_part_

# 监控内存使用
top -p $(pgrep -f book_splitter)

# 增加虚拟内存（Linux）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 处理速度过慢

**症状**:
- 处理时间过长
- 程序似乎卡住
- CPU使用率过高

**解决方案**:
```bash
# 禁用标签生成（最有效）
python -m book_splitter input.md --no-tags

# 禁用图片处理
python -m book_splitter input.md --no-images

# 减少标签数量
python -m book_splitter input.md --min-tags 1 --max-tags 3

# 使用SSD存储
# 将输入和输出文件放在SSD上

# 监控进程
htop
```

### 5. 输出相关问题

#### 生成的文件名包含特殊字符

**问题**:
- 文件名包含不支持的字符
- 文件名过长
- 重复文件名

**解决方案**:

工具会自动处理这些问题，但如果仍有问题：

```python
# 自定义文件名清理
from book_splitter.generators.file_generator import FileGenerator

generator = FileGenerator(config)
clean_name = generator.sanitize_filename("问题标题！@#$%")
print(clean_name)  # 输出: 问题标题
```

#### 标签质量不高

**问题**:
- 生成的标签不相关
- 标签数量不合适
- 标签重复

**解决方案**:
```bash
# 调整标签数量
python -m book_splitter input.md --min-tags 2 --max-tags 5

# 检查文档内容质量
# 确保文档内容丰富，专业术语较多

# 手动编辑生成的标签
# 在YAML前置元数据中修改tags字段
```

#### 导航链接失效

**问题**:
- 链接指向不存在的文件
- 相对路径错误
- 目录结构不匹配

**解决方案**:
```bash
# 检查输出目录结构
tree output/

# 验证链接
find output/ -name "*.md" -exec grep -l "返回目录" {} \;

# 重新生成（会修复链接）
python -m book_splitter input.md -o output --navigation
```

## 🔧 调试技巧

### 启用详细日志

```python
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 然后运行处理
from book_splitter import BookSplitter, ProcessingConfig

config = ProcessingConfig()
config.source_file = "input.md"
config.output_dir = "output"

splitter = BookSplitter(config)
result = splitter.process()
```

### 使用预览模式

```python
# 预览处理结果，不实际生成文件
result = splitter.process_preview()
print(f"预计生成 {result['estimated_files']} 个文件")
print(f"发现 {result['chapters_count']} 个章节")
print(f"发现 {result['sections_count']} 个小节")
```

### 分步调试

```python
# 单独测试各个组件
from book_splitter.analyzers import StructureAnalyzer
from book_splitter.extractors import ContentExtractor

# 测试结构分析
analyzer = StructureAnalyzer("input.md")
result = analyzer.analyze_structure()
print(f"章节数: {len(result['chapters'])}")
print(f"小节数: {len(result['sections'])}")

# 测试内容提取
extractor = ContentExtractor("input.md")
if result['chapters']:
    content = extractor.extract_chapter_content(result['chapters'][0])
    print(f"第一章内容长度: {len(content)}")
```

## 📊 性能监控

### 监控脚本

```python
import time
import psutil
import os
from book_splitter import BookSplitter, ProcessingConfig

def monitor_processing(input_file, output_dir):
    # 获取当前进程
    process = psutil.Process(os.getpid())
    
    # 记录开始状态
    start_time = time.time()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"开始处理: {input_file}")
    print(f"初始内存使用: {start_memory:.1f} MB")
    
    # 配置和处理
    config = ProcessingConfig()
    config.source_file = input_file
    config.output_dir = output_dir
    
    splitter = BookSplitter(config)
    result = splitter.process()
    
    # 记录结束状态
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"处理完成: {result['status']}")
    print(f"处理时间: {end_time - start_time:.2f} 秒")
    print(f"内存使用: {end_memory:.1f} MB (增加 {end_memory - start_memory:.1f} MB)")
    
    if result['status'] == 'success':
        print(f"生成文件: {result['generated_files_count']} 个")
    
    return result

# 使用示例
result = monitor_processing("input.md", "output")
```

## 🆘 获取帮助

### 自助诊断

1. **检查系统环境**:
   ```bash
   python --version
   pip --version
   python -c "import sys; print(sys.path)"
   ```

2. **验证依赖**:
   ```bash
   pip check
   python -c "import jieba, sklearn, networkx, click; print('所有依赖正常')"
   ```

3. **测试基本功能**:
   ```bash
   # 创建简单测试文件
   echo -e "# 测试文档\n\n# 第一章 测试章节\n\n这是测试内容。" > test.md
   
   # 运行测试
   python -m book_splitter test.md -o test_output --no-tags
   ```

### 报告问题

如果问题仍然存在，请提供以下信息：

1. **系统信息**:
   - 操作系统和版本
   - Python版本
   - 依赖包版本

2. **错误信息**:
   - 完整的错误堆栈
   - 使用的命令
   - 输入文件特征

3. **重现步骤**:
   - 详细的操作步骤
   - 最小化的测试用例
   - 预期结果vs实际结果

### 联系方式

- 创建 [GitHub Issue](https://github.com/your-username/book-chapter-splitter/issues)
- 参与 [GitHub Discussions](https://github.com/your-username/book-chapter-splitter/discussions)
- 查看 [FAQ](https://github.com/your-username/book-chapter-splitter/wiki/FAQ)

---

如果本指南没有解决您的问题，请不要犹豫寻求帮助！