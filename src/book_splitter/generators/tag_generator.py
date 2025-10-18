"""
标签生成器 - 负责从内容中生成关键词标签
"""

import re
from typing import Dict, List, Optional, Tuple
import jieba
import jieba.analyse
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class TagGenerator:
    """从内容中生成关键词标签"""
    
    def __init__(self, use_political_science_vocab: bool = True):
        """
        初始化标签生成器
        
        Args:
            use_political_science_vocab: 是否使用政治学专业词汇
        """
        self.use_political_science_vocab = use_political_science_vocab
        
        # 政治学专业词汇词典
        self.political_science_vocab = {
            "政治", "经济", "社会", "文化", "历史", "哲学", "法律", "制度", 
            "政府", "国家", "权力", "民主", "专制", "选举", "政党", "政策",
            "改革", "发展", "现代化", "全球化", "意识形态", "价值观", "人权",
            "自由", "平等", "正义", "法治", "宪法", "立法", "司法", "行政",
            "外交", "国际关系", "军事", "安全", "民族", "宗教", "阶级", "阶层",
            "市场经济", "计划经济", "资本主义", "社会主义", "共产主义", "自由主义",
            "保守主义", "民族主义", "帝国主义", "殖民主义", "马克思主义", "列宁主义",
            "毛泽东思想", "邓小平理论", "三个代表", "科学发展观", "习近平新时代中国特色社会主义思想"
        }
        
        # 初始化jieba分词
        jieba.initialize()
        
        # 添加政治学专业词汇到jieba词典
        if use_political_science_vocab:
            for word in self.political_science_vocab:
                jieba.add_word(word, freq=1000)
    
    def generate_tags(self, content: str, max_tags: int = 10, method: str = "tfidf") -> List[Dict[str, any]]:
        """
        生成内容标签
        
        Args:
            content: 文本内容
            max_tags: 最大标签数量
            method: 标签生成方法 ("tfidf", "textrank", "combined")
            
        Returns:
            标签列表，包含标签和权重
        """
        if not content or len(content.strip()) < 10:
            return []
        
        # 清理内容
        cleaned_content = self._clean_content(content)
        
        if method == "tfidf":
            tags = self._generate_tfidf_tags(cleaned_content, max_tags)
        elif method == "textrank":
            tags = self._generate_textrank_tags(cleaned_content, max_tags)
        else:  # combined
            tfidf_tags = self._generate_tfidf_tags(cleaned_content, max_tags * 2)
            textrank_tags = self._generate_textrank_tags(cleaned_content, max_tags * 2)
            tags = self._combine_tags(tfidf_tags, textrank_tags, max_tags)
        
        # 标准化权重
        tags = self._normalize_weights(tags)
        
        # 过滤和排序
        tags = self._filter_and_sort_tags(tags, max_tags)
        
        return tags
    
    def generate_chapter_tags(self, chapter_title: str, chapter_content: str, 
                            max_tags: int = 8) -> List[Dict[str, any]]:
        """
        生成章节标签
        
        Args:
            chapter_title: 章节标题
            chapter_content: 章节内容
            max_tags: 最大标签数量
            
        Returns:
            标签列表
        """
        # 从标题中提取关键词
        title_tags = self._extract_tags_from_title(chapter_title)
        
        # 从内容中生成标签
        content_tags = self.generate_tags(chapter_content, max_tags * 2, "combined")
        
        # 合并标签
        combined_tags = self._merge_tags(title_tags, content_tags, max_tags)
        
        return combined_tags
    
    def generate_section_tags(self, section_title: str, section_content: str,
                             max_tags: int = 6) -> List[Dict[str, any]]:
        """
        生成部分标签
        
        Args:
            section_title: 部分标题
            section_content: 部分内容
            max_tags: 最大标签数量
            
        Returns:
            标签列表
        """
        # 从标题中提取关键词
        title_tags = self._extract_tags_from_title(section_title)
        
        # 从内容中生成标签
        content_tags = self.generate_tags(section_content, max_tags * 2, "tfidf")
        
        # 合并标签
        combined_tags = self._merge_tags(title_tags, content_tags, max_tags)
        
        return combined_tags
    
    def _clean_content(self, content: str) -> str:
        """清理文本内容"""
        # 移除Markdown标记
        content = re.sub(r'#+\s*', '', content)  # 标题
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # 粗体
        content = re.sub(r'\*([^*]+)\*', r'\1', content)  # 斜体
        content = re.sub(r'`([^`]+)`', r'\1', content)  # 代码
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', '', content)  # 图片
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', content)  # 链接
        
        # 移除特殊字符和多余空格
        content = re.sub(r'[^\w\u4e00-\u9fff\s]', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _generate_tfidf_tags(self, content: str, max_tags: int) -> List[Dict[str, any]]:
        """使用TF-IDF方法生成标签"""
        try:
            # 分词
            words = list(jieba.cut(content))
            
            # 过滤停用词和短词
            filtered_words = [
                word for word in words 
                if len(word) > 1 and not self._is_stopword(word)
            ]
            
            if not filtered_words:
                return []
            
            # 使用Counter统计词频
            word_freq = Counter(filtered_words)
            
            # 计算TF-IDF权重（简化版）
            total_words = len(filtered_words)
            tags = []
            
            for word, freq in word_freq.most_common(max_tags * 2):
                # TF-IDF权重 = 词频 * 逆文档频率（这里使用log简化）
                tf = freq / total_words
                idf = np.log(total_words / (freq + 1)) + 1  # 避免除零
                weight = tf * idf
                
                # 如果是政治学词汇，增加权重
                if self.use_political_science_vocab and word in self.political_science_vocab:
                    weight *= 1.5
                
                tags.append({"tag": word, "weight": weight, "method": "tfidf"})
            
            return tags
            
        except Exception as e:
            print(f"TF-IDF标签生成失败: {str(e)}")
            return []
    
    def _generate_textrank_tags(self, content: str, max_tags: int) -> List[Dict[str, any]]:
        """使用TextRank方法生成标签"""
        try:
            # 使用jieba的TextRank提取关键词
            keywords = jieba.analyse.textrank(
                content, 
                topK=max_tags * 2,
                withWeight=True,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'a')
            )
            
            tags = []
            for word, weight in keywords:
                # 如果是政治学词汇，增加权重
                if self.use_political_science_vocab and word in self.political_science_vocab:
                    weight *= 1.5
                
                tags.append({"tag": word, "weight": weight, "method": "textrank"})
            
            return tags
            
        except Exception as e:
            print(f"TextRank标签生成失败: {str(e)}")
            return []
    
    def _combine_tags(self, tags1: List[Dict[str, any]], tags2: List[Dict[str, any]], 
                     max_tags: int) -> List[Dict[str, any]]:
        """合并两种方法的标签"""
        combined = {}
        
        # 添加第一种方法的标签
        for tag_info in tags1:
            tag = tag_info["tag"]
            if tag not in combined:
                combined[tag] = tag_info.copy()
            else:
                combined[tag]["weight"] = max(combined[tag]["weight"], tag_info["weight"])
        
        # 添加第二种方法的标签
        for tag_info in tags2:
            tag = tag_info["tag"]
            if tag not in combined:
                combined[tag] = tag_info.copy()
            else:
                combined[tag]["weight"] = (combined[tag]["weight"] + tag_info["weight"]) / 2
        
        # 转换为列表并排序
        combined_list = list(combined.values())
        combined_list.sort(key=lambda x: x["weight"], reverse=True)
        
        return combined_list[:max_tags]
    
    def _normalize_weights(self, tags: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """标准化权重到0-1范围"""
        if not tags:
            return tags
        
        max_weight = max(tag["weight"] for tag in tags)
        if max_weight > 0:
            for tag in tags:
                tag["weight"] = tag["weight"] / max_weight
        
        return tags
    
    def _filter_and_sort_tags(self, tags: List[Dict[str, any]], max_tags: int) -> List[Dict[str, any]]:
        """过滤和排序标签"""
        # 过滤权重过低的标签
        filtered_tags = [tag for tag in tags if tag["weight"] >= 0.1]
        
        # 按权重排序
        filtered_tags.sort(key=lambda x: x["weight"], reverse=True)
        
        # 限制数量
        return filtered_tags[:max_tags]
    
    def _extract_tags_from_title(self, title: str) -> List[Dict[str, any]]:
        """从标题中提取标签"""
        if not title:
            return []
        
        # 清理标题
        cleaned_title = self._clean_content(title)
        
        # 分词
        words = list(jieba.cut(cleaned_title))
        
        tags = []
        for word in words:
            if len(word) > 1 and not self._is_stopword(word):
                # 标题中的词给予较高权重
                weight = 0.8 if word in self.political_science_vocab else 0.6
                tags.append({"tag": word, "weight": weight, "method": "title"})
        
        return tags
    
    def _merge_tags(self, title_tags: List[Dict[str, any]], content_tags: List[Dict[str, any]], 
                   max_tags: int) -> List[Dict[str, any]]:
        """合并标题和内容标签"""
        merged = {}
        
        # 添加标题标签（给予较高权重）
        for tag_info in title_tags:
            tag = tag_info["tag"]
            merged[tag] = tag_info.copy()
            merged[tag]["weight"] *= 1.2  # 标题标签权重加成
        
        # 添加内容标签
        for tag_info in content_tags:
            tag = tag_info["tag"]
            if tag in merged:
                # 如果标签已存在，取最大值
                merged[tag]["weight"] = max(merged[tag]["weight"], tag_info["weight"])
            else:
                merged[tag] = tag_info.copy()
        
        # 转换为列表并排序
        merged_list = list(merged.values())
        merged_list.sort(key=lambda x: x["weight"], reverse=True)
        
        return merged_list[:max_tags]
    
    def _is_stopword(self, word: str) -> bool:
        """判断是否为停用词"""
        stopwords = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", 
            "中", "上", "下", "大", "小", "这", "那", "你", "我", "他", "她", "它", "我们", 
            "你们", "他们", "这个", "那个", "这些", "那些", "什么", "怎么", "为什么", "因为", 
            "所以", "但是", "虽然", "如果", "然后", "现在", "以后", "以前", "今天", "明天", 
            "昨天", "这里", "那里", "哪里", "很", "非常", "太", "真", "好", "坏", "多", "少",
            "来", "去", "到", "从", "向", "对", "关于", "对于", "通过", "根据", "按照", "为了"
        }
        
        return word in stopwords or len(word.strip()) == 0
    
    def generate_yaml_frontmatter(self, tags: List[Dict[str, any]]) -> str:
        """生成YAML frontmatter格式的标签"""
        if not tags:
            return "[]"
        
        # 只提取标签名称
        tag_names = [tag["tag"] for tag in tags]
        
        # 转换为YAML格式
        if len(tag_names) == 1:
            return f"['{tag_names[0]}']"
        else:
            tags_str = ', '.join([f"'{tag}'" for tag in tag_names])
            return f"[{tags_str}]"
    
    def analyze_content_themes(self, content: str) -> Dict[str, any]:
        """分析内容主题分布"""
        if not content:
            return {"themes": {}, "dominant_theme": None}
        
        themes = {}
        cleaned_content = self._clean_content(content)
        
        # 检查政治学主题
        for theme in ["政治", "经济", "社会", "文化", "历史"]:
            if theme in cleaned_content:
                # 计算主题出现频率
                count = cleaned_content.count(theme)
                themes[theme] = count
        
        # 确定主导主题
        dominant_theme = None
        if themes:
            dominant_theme = max(themes.items(), key=lambda x: x[1])[0]
        
        return {
            "themes": themes,
            "dominant_theme": dominant_theme
        }
    
    def get_tag_statistics(self, tags: List[Dict[str, any]]) -> Dict[str, any]:
        """获取标签统计信息"""
        if not tags:
            return {"total_tags": 0, "avg_weight": 0, "method_distribution": {}}
        
        total_weight = sum(tag["weight"] for tag in tags)
        avg_weight = total_weight / len(tags)
        
        # 方法分布统计
        method_distribution = {}
        for tag in tags:
            method = tag.get("method", "unknown")
            method_distribution[method] = method_distribution.get(method, 0) + 1
        
        return {
            "total_tags": len(tags),
            "avg_weight": avg_weight,
            "method_distribution": method_distribution
        }
    
    def validate_tags(self, tags: List[Dict[str, any]]) -> Tuple[bool, List[str]]:
        """验证标签有效性"""
        issues = []
        
        if not tags:
            issues.append("没有生成任何标签")
            return False, issues
        
        # 检查标签长度
        for tag_info in tags:
            tag = tag_info["tag"]
            if len(tag) < 2:
                issues.append(f"标签过短: {tag}")
            if len(tag) > 20:
                issues.append(f"标签过长: {tag}")
        
        # 检查权重范围
        for tag_info in tags:
            weight = tag_info["weight"]
            if weight < 0 or weight > 1:
                issues.append(f"权重超出范围: {tag_info['tag']} = {weight}")
        
        return len(issues) == 0, issues