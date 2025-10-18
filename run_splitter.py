#!/usr/bin/env python3
"""
书籍章节拆分器运行脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from book_splitter.main import BookSplitter
from book_splitter.config import ProcessingConfig

def main():
    """运行书籍拆分器"""
    # 尝试自动加载配置文件（优先本地配置，其次示例配置）
    config = None
    for candidate in [
        "config.yaml",
        "config.yml",
        "config.json",
        "config.example.yaml",
        "config.example.json",
    ]:
        if Path(candidate).exists():
            config = ProcessingConfig.from_file(candidate)
            print(f"⚙️ 使用配置文件: {candidate}")
            break
    if config is None:
        config = ProcessingConfig()
        print("⚙️ 使用默认配置")

    # 基本信息
    print(f"🚀 开始处理 {config.source_file} 文件...")
    print(f"📚 输入文件: {config.source_file}")
    print(f"📁 输出目录: {config.output_dir}")
    print(
        "⚙️ 配置: "
        f"章节{'✅' if True else '❌'} "
        f"小节{'✅' if config.create_sections else '❌'} "
        f"标签{'✅' if config.generate_tags else '❌'} "
        f"导航{'✅' if config.add_navigation else '❌'} "
        f"图片{'✅' if config.preserve_images else '❌'}"
    )
    print()

    # 检查输入文件
    if not Path(config.source_file).exists():
        print(f"❌ 输入文件不存在: {config.source_file}")
        print("请在配置文件中设置有效的 source_file，或将示例文档复制到项目根目录。")
        return

    # 创建处理器
    splitter = BookSplitter(config)

    # 处理文件
    result = splitter.process()

    # 显示结果
    if result['status'] == 'success':
        print("🎉 处理完成!")
        print(f"📊 统计信息:")
        print(f"  - 章节数量: {result['chapters_count']}")
        print(f"  - 小节数量: {result['sections_count']}")
        print(f"  - 生成文件: {result['generated_files_count']}")
        print(f"  - 处理时间: {result.get('processing_time', 'N/A')}")
        print()
        print(f"📁 输出文件位置: {config.output_dir}/")
        print("  - 目录.md (主目录文件)")
        print("  - chapters/ (章节文件)")
        print("  - sections/ (小节文件)")
        if config.preserve_images:
            print("  - images/ (图片文件)")
    else:
        print("❌ 处理失败!")
        print(f"错误信息: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()