"""
书籍章节拆分器安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="book-chapter-splitter",
    version="1.0.1",
    author="Book Splitter Team",
    author_email="team@booksplitter.com",
    description="一个高效的markdown书籍文档处理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/changingwang/Book-Chapter-Splitter",
    package_dir={"":"src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "book-splitter=book_splitter.cli:main",
        ],
    },
)