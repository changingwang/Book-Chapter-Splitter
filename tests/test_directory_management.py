#!/usr/bin/env python3
"""
目录结构管理测试脚本

测试FileGenerator类的目录管理和图片处理功能。
"""

import sys
import tempfile
import shutil
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from book_splitter.generators import FileGenerator
from book_splitter.models import ChapterInfo, SectionInfo
from book_splitter.config import ProcessingConfig


def create_test_image(image_path: Path):
    """创建一个测试图片文件"""
    # 创建一个简单的文本文件作为测试图片
    with open(image_path, 'w', encoding='utf-8') as f:
        f.write("这是一个测试图片文件")


def test_directory_structure_creation():
    """测试目录结构创建"""
    print("测试目录结构创建...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 自定义配置
            config = ProcessingConfig()
            config.output_dir = temp_dir
            config.chapters_subdir = "chapters"
            config.sections_subdir = "sections"
            config.images_subdir = "images"
            
            file_generator = FileGenerator(config)
            
            # 创建测试内容
            chapter = ChapterInfo(title="测试章节", start_line=1, end_line=50)
            section = SectionInfo(
                title="测试小节", start_line=10, end_line=30,
                chapter_title="测试章节", level=2
            )
            
            # 创建文件（这会自动创建目录结构）
            chapter_path = file_generator.create_chapter_file(chapter, "章节内容")
            section_path = file_generator.create_section_file(section, "小节内容")
            
            # 验证目录结构
            base_dir = Path(temp_dir)
            chapters_dir = base_dir / "chapters"
            sections_dir = base_dir / "sections"
            
            assert base_dir.exists(), "输出根目录应该存在"
            assert chapters_dir.exists(), "章节目录应该存在"
            assert sections_dir.exists(), "小节目录应该存在"
            assert chapters_dir.is_dir(), "章节路径应该是目录"
            assert sections_dir.is_dir(), "小节路径应该是目录"
            
            # 验证文件位置
            chapter_file = Path(chapter_path)
            section_file = Path(section_path)
            
            assert chapter_file.parent == chapters_dir, "章节文件应在正确目录"
            assert section_file.parent == sections_dir, "小节文件应在正确目录"
            
            print(f"📁 目录结构验证:")
            print(f"  ✅ 根目录: {base_dir}")
            print(f"  ✅ 章节目录: {chapters_dir}")
            print(f"  ✅ 小节目录: {sections_dir}")
            print(f"  ✅ 章节文件: {chapter_file.name}")
            print(f"  ✅ 小节文件: {section_file.name}")
            
            print("✅ 目录结构创建测试通过")
            
        except Exception as e:
            print(f"❌ 目录结构创建测试失败: {str(e)}")
            raise


def test_custom_directory_names():
    """测试自定义目录名称"""
    print("测试自定义目录名称...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 自定义目录名称
            config = ProcessingConfig()
            config.output_dir = temp_dir
            config.chapters_subdir = "我的章节"
            config.sections_subdir = "我的小节"
            config.images_subdir = "我的图片"
            
            file_generator = FileGenerator(config)
            
            # 创建测试文件
            chapter = ChapterInfo(title="测试", start_line=1, end_line=10)
            file_generator.create_chapter_file(chapter, "内容")
            
            # 验证自定义目录
            custom_chapters_dir = Path(temp_dir) / "我的章节"
            assert custom_chapters_dir.exists(), "自定义章节目录应该存在"
            
            # 验证配置属性
            assert config.chapters_dir == str(Path(temp_dir) / "我的章节")
            assert config.sections_dir == str(Path(temp_dir) / "我的小节")
            assert config.images_dir == str(Path(temp_dir) / "我的图片")
            
            print(f"📁 自定义目录验证:")
            print(f"  ✅ 章节目录: {custom_chapters_dir}")
            print(f"  ✅ 配置正确: {config.chapters_dir}")
            
            print("✅ 自定义目录名称测试通过")
            
        except Exception as e:
            print(f"❌ 自定义目录名称测试失败: {str(e)}")
            raise


def test_image_processing():
    """测试图片处理功能"""
    print("测试图片处理功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 创建源目录和图片
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()
            
            # 创建测试图片
            test_image1 = source_dir / "test1.jpg"
            test_image2 = source_dir / "test2.png"
            create_test_image(test_image1)
            create_test_image(test_image2)
            
            # 配置
            config = ProcessingConfig()
            config.output_dir = str(Path(temp_dir) / "output")
            config.preserve_images = True
            
            file_generator = FileGenerator(config)
            
            # 包含图片引用的内容
            content_with_images = f"""
# 测试章节

这是一个包含图片的章节。

![图片1](test1.jpg)

一些文本内容。

![图片2](test2.png)

更多内容。
            """
            
            # 处理图片
            processed_content = file_generator.process_images(content_with_images, source_dir)
            
            print(f"📷 图片处理结果:")
            print(f"原始内容包含: test1.jpg, test2.png")
            print(f"处理后内容:")
            print(processed_content[:200] + "...")
            
            # 验证图片路径更新
            assert "images/test1.jpg" in processed_content, "图片1路径应该更新"
            assert "images/test2.png" in processed_content, "图片2路径应该更新"
            
            # 验证图片文件复制
            images_dir = Path(config.output_dir) / "images"
            copied_image1 = images_dir / "test1.jpg"
            copied_image2 = images_dir / "test2.png"
            
            assert copied_image1.exists(), "图片1应该被复制"
            assert copied_image2.exists(), "图片2应该被复制"
            
            print(f"  ✅ 图片目录: {images_dir}")
            print(f"  ✅ 复制的图片: {copied_image1.name}, {copied_image2.name}")
            
            print("✅ 图片处理测试通过")
            
        except Exception as e:
            print(f"❌ 图片处理测试失败: {str(e)}")
            raise


def test_image_name_conflicts():
    """测试图片名称冲突处理"""
    print("测试图片名称冲突处理...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 创建源目录
            source_dir1 = Path(temp_dir) / "source1"
            source_dir1.mkdir()
            source_dir2 = Path(temp_dir) / "source2"
            source_dir2.mkdir()
            
            # 创建同名图片
            image1 = source_dir1 / "image.jpg"
            image2 = source_dir2 / "image.jpg"
            create_test_image(image1)
            create_test_image(image2)
            
            # 配置
            config = ProcessingConfig()
            config.output_dir = str(Path(temp_dir) / "output")
            config.preserve_images = True
            
            file_generator = FileGenerator(config)
            
            # 处理来自不同目录的同名图片
            content1 = "![图片](image.jpg)"
            content2 = "![图片](image.jpg)"
            
            processed1 = file_generator.process_images(content1, source_dir1)
            processed2 = file_generator.process_images(content2, source_dir2)
            
            # 验证冲突处理
            images_dir = Path(config.output_dir) / "images"
            image_files = list(images_dir.glob("image*.jpg"))
            
            assert len(image_files) == 2, "应该有2个不同的图片文件"
            
            print(f"📷 图片冲突处理:")
            print(f"  ✅ 处理后的图片文件数: {len(image_files)}")
            for img_file in image_files:
                print(f"  ✅ 图片文件: {img_file.name}")
            
            print("✅ 图片名称冲突测试通过")
            
        except Exception as e:
            print(f"❌ 图片名称冲突测试失败: {str(e)}")
            raise


def test_image_preservation_disabled():
    """测试图片保存禁用功能"""
    print("测试图片保存禁用功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 创建源目录和图片
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()
            
            test_image = source_dir / "test.jpg"
            create_test_image(test_image)
            
            # 配置 - 禁用图片保存
            config = ProcessingConfig()
            config.output_dir = str(Path(temp_dir) / "output")
            config.preserve_images = False
            
            file_generator = FileGenerator(config)
            
            # 包含图片的内容
            content = "![图片](test.jpg)"
            processed_content = file_generator.process_images(content, source_dir)
            
            # 验证图片路径未更新
            assert "test.jpg" in processed_content, "图片路径不应该被更新"
            
            # 验证图片文件未复制
            images_dir = Path(config.output_dir) / "images"
            assert not images_dir.exists(), "图片目录不应该存在"
            
            print(f"📷 图片保存禁用测试:")
            print(f"  ✅ 图片路径保持原样: test.jpg")
            print(f"  ✅ 图片目录未创建")
            
            print("✅ 图片保存禁用测试通过")
            
        except Exception as e:
            print(f"❌ 图片保存禁用测试失败: {str(e)}")
            raise


def test_directory_cleanup():
    """测试目录清理功能"""
    print("测试目录清理功能...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            config = ProcessingConfig()
            config.output_dir = temp_dir
            
            file_generator = FileGenerator(config)
            
            # 创建一些文件和目录
            test_dir = Path(temp_dir) / "test_subdir"
            test_dir.mkdir()
            
            test_file = test_dir / "test.txt"
            test_file.write_text("测试内容")
            
            # 清理目录
            file_generator.cleanup_output_directory()
            
            # 验证清理
            assert not test_dir.exists(), "测试目录应该被清理"
            assert not test_file.exists(), "测试文件应该被清理"
            
            print(f"🧹 目录清理测试:")
            print(f"  ✅ 输出目录已清理")
            print(f"  ✅ 文件和子目录已删除")
            
            print("✅ 目录清理测试通过")
            
        except Exception as e:
            print(f"❌ 目录清理测试失败: {str(e)}")
            raise


def test_nested_directory_creation():
    """测试嵌套目录创建"""
    print("测试嵌套目录创建...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            config = ProcessingConfig()
            config.output_dir = temp_dir
            config.chapters_subdir = "docs/chapters"
            config.sections_subdir = "docs/sections"
            config.images_subdir = "assets/images"
            
            file_generator = FileGenerator(config)
            
            # 创建测试文件
            chapter = ChapterInfo(title="测试", start_line=1, end_line=10)
            file_generator.create_chapter_file(chapter, "内容")
            
            # 验证嵌套目录
            chapters_dir = Path(temp_dir) / "docs" / "chapters"
            sections_dir = Path(temp_dir) / "docs" / "sections"
            images_dir = Path(temp_dir) / "assets" / "images"
            
            assert chapters_dir.exists(), "嵌套章节目录应该存在"
            assert sections_dir.exists(), "嵌套小节目录应该存在"
            assert images_dir.exists(), "嵌套图片目录应该存在"
            
            print(f"📁 嵌套目录验证:")
            print(f"  ✅ 章节目录: {chapters_dir}")
            print(f"  ✅ 小节目录: {sections_dir}")
            print(f"  ✅ 图片目录: {images_dir}")
            
            print("✅ 嵌套目录创建测试通过")
            
        except Exception as e:
            print(f"❌ 嵌套目录创建测试失败: {str(e)}")
            raise


def main():
    """运行所有测试"""
    print("开始目录结构管理测试...\n")
    
    try:
        test_directory_structure_creation()
        print()
        test_custom_directory_names()
        print()
        test_image_processing()
        print()
        test_image_name_conflicts()
        print()
        test_image_preservation_disabled()
        print()
        test_directory_cleanup()
        print()
        test_nested_directory_creation()
        
        print("\n🎉 所有目录结构管理测试通过!")
        print("目录结构管理和图片处理功能已正确实现。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()