"""
标签生成器模块

基于内容分析生成关键词标签，支持政治学领域词汇识别和YAML前置元数据生成。
"""

import re
import logging
from typing import List, Dict, Set, Tuple
from collections import Counter
import jieba
import jieba.analyse


class TagGenerator:
    """标签生成器"""
    
    def __init__(self, min_tags: int = 3, max_tags: int = 8):
        """初始化标签生成器
        
        Args:
            min_tags: 最少标签数量
            max_tags: 最多标签数量
        """
        self.min_tags = min_tags
        self.max_tags = max_tags
        self.logger = logging.getLogger(__name__)
        
        # 初始化停用词集合
        self.stop_words = self._load_stop_words()
        
        # 初始化政治学领域词汇库
        self.political_terms = self._load_political_terms()
        
        # 配置jieba分词
        self._setup_jieba()
        
        self.logger.info(f"标签生成器初始化完成，标签范围: {min_tags}-{max_tags}")
    
    def _load_stop_words(self) -> Set[str]:
        """加载停用词集合"""
        stop_words = {
            # 基础停用词
            '的', '是', '在', '和', '与', '或', '但', '等', '了', '着', '过', '把', '被',
            '将', '要', '会', '能', '可', '应', '该', '就', '都', '也', '还', '又', '再',
            '很', '更', '最', '非常', '十分', '特别', '尤其', '特殊', '一般', '通常',
            '主要', '重要', '关键', '核心', '基本', '根本', '本质', '实际', '具体',
            '这', '那', '这个', '那个', '这些', '那些', '这样', '那样', '如此',
            '因为', '由于', '所以', '因此', '然而', '但是', '不过', '虽然', '尽管',
            '如果', '假如', '要是', '倘若', '无论', '不管', '无论如何', '总之',
            '首先', '其次', '然后', '最后', '另外', '此外', '而且', '并且', '同时',
            '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '第一', '第二',
            '年', '月', '日', '时', '分', '秒', '世纪', '年代', '时期', '阶段',
            '中', '内', '外', '上', '下', '前', '后', '左', '右', '东', '西', '南', '北',
            # 补充常见停用词
            '应该', '可以', '需要', '必须', '必要', '可能', '或许', '大概', '也许',
            '来源', '来自', '通过', '根据', '按照', '依据', '基于', '关于', '对于',
            '有关', '相关', '涉及', '包括', '包含', '具有', '拥有', '存在', '出现',
            '发生', '产生', '形成', '建立', '创建', '制定', '实施', '执行', '进行'
        }
        return stop_words
    
    def _load_political_terms(self) -> Set[str]:
        """加载政治学领域词汇库"""
        political_terms = {
            # 政治制度
            '政治', '政府', '国家', '政权', '政治制度', '民主', '专制', '独裁', '共和',
            '君主制', '联邦制', '单一制', '分权', '集权', '地方自治', '中央集权',
            
            # 政治理论
            '政治学', '政治理论', '政治哲学', '政治思想', '意识形态', '自由主义',
            '保守主义', '社会主义', '共产主义', '法西斯主义', '无政府主义',
            '民族主义', '国际主义', '全球化', '本土化',
            
            # 权力与治理
            '权力', '权威', '统治', '治理', '管理', '行政', '立法', '司法', '执法',
            '监督', '制衡', '问责', '透明度', '腐败', '廉政', '公共政策', '决策',
            
            # 政治参与
            '选举', '投票', '民意', '公民', '公民权', '政治权利', '人权', '自由',
            '平等', '正义', '公正', '法治', '宪政', '宪法', '法律', '法规',
            
            # 政治组织
            '政党', '党派', '政治组织', '利益集团', '压力集团', '社会团体',
            '工会', '商会', '协会', '联盟', '联合', '合作', '对抗', '竞争',
            
            # 国际政治
            '国际关系', '外交', '国际法', '国际组织', '联合国', '主权', '领土',
            '边界', '战争', '和平', '冲突', '合作', '谈判', '条约', '协议',
            
            # 经济政治
            '经济', '市场', '计划经济', '市场经济', '混合经济', '财政', '税收',
            '预算', '公共财政', '社会保障', '福利', '分配', '再分配', '贫富差距',
            
            # 社会政治
            '社会', '阶级', '阶层', '社会结构', '社会流动', '社会公正', '社会稳定',
            '社会变迁', '社会运动', '革命', '改革', '变革', '转型', '现代化',
            
            # 文化政治
            '文化', '价值观', '传统', '现代性', '文明', '多元化', '一体化',
            '认同', '身份', '族群', '民族', '种族', '宗教', '信仰'
        }
        return political_terms
    
    def _setup_jieba(self):
        """配置jieba分词器"""
        # 添加政治学词汇到jieba词典
        for term in self.political_terms:
            jieba.add_word(term)
        
        # 设置jieba日志级别
        jieba.setLogLevel(logging.WARNING)
    
    def extract_keywords(self, content: str) -> List[str]:
        """从内容中提取关键词
        
        Args:
            content: 文本内容
            
        Returns:
            关键词列表
        """
        if not content or not content.strip():
            return []
        
        # 清理内容
        cleaned_content = self._clean_content(content)
        
        # 使用TF-IDF提取关键词
        tfidf_keywords = jieba.analyse.extract_tags(
            cleaned_content, 
            topK=self.max_tags * 2,  # 提取更多候选词
            withWeight=True
        )
        
        # 使用TextRank提取关键词
        textrank_keywords = jieba.analyse.textrank(
            cleaned_content,
            topK=self.max_tags * 2,
            withWeight=True
        )
        
        # 合并两种算法的结果
        keyword_scores = {}
        
        # TF-IDF结果权重为0.6
        for word, score in tfidf_keywords:
            if self._is_valid_keyword(word):
                keyword_scores[word] = keyword_scores.get(word, 0) + score * 0.6
        
        # TextRank结果权重为0.4
        for word, score in textrank_keywords:
            if self._is_valid_keyword(word):
                keyword_scores[word] = keyword_scores.get(word, 0) + score * 0.4
        
        # 政治学词汇加权
        for word in keyword_scores:
            if word in self.political_terms:
                keyword_scores[word] *= 1.5  # 政治学词汇权重提升50%
        
        # 按分数排序并返回
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, score in sorted_keywords]
        
        self.logger.debug(f"提取到 {len(keywords)} 个关键词")
        return keywords
    
    def _clean_content(self, content: str) -> str:
        """清理文本内容"""
        # 移除markdown标记
        content = re.sub(r'#+\s*', '', content)  # 移除标题标记
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # 移除粗体标记
        content = re.sub(r'\*(.+?)\*', r'\1', content)  # 移除斜体标记
        content = re.sub(r'`(.+?)`', r'\1', content)  # 移除代码标记
        content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', content)  # 移除链接，保留文本
        content = re.sub(r'!\[.*?\]\(.+?\)', '', content)  # 移除图片
        
        # 移除特殊字符和数字
        content = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', ' ', content)
        
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def _is_valid_keyword(self, word: str) -> bool:
        """检查关键词是否有效"""
        # 长度检查
        if len(word) < 2 or len(word) > 10:
            return False
        
        # 停用词检查
        if word in self.stop_words:
            return False
        
        # 纯数字检查
        if word.isdigit():
            return False
        
        # 纯英文字母检查（保留专业术语）
        if word.isalpha() and word.islower() and len(word) < 4:
            return False
        
        return True
    
    def generate_tags(self, content: str, title: str = "") -> List[str]:
        """生成标准化的标签列表
        
        Args:
            content: 文本内容
            title: 标题（可选，用于补充关键词）
            
        Returns:
            标准化的标签列表
        """
        # 合并内容和标题
        full_content = content
        if title:
            # 标题权重更高，重复添加
            full_content = f"{title} {title} {content}"
        
        # 提取关键词
        keywords = self.extract_keywords(full_content)
        
        # 标准化标签
        tags = []
        for keyword in keywords:
            normalized_tag = self._normalize_tag(keyword)
            if normalized_tag and normalized_tag not in tags:
                tags.append(normalized_tag)
                
                # 达到最大标签数就停止
                if len(tags) >= self.max_tags:
                    break
        
        # 确保最少标签数
        if len(tags) < self.min_tags:
            # 尝试从标题中提取更多标签
            if title:
                title_keywords = self.extract_keywords(title)
                for keyword in title_keywords:
                    normalized_tag = self._normalize_tag(keyword)
                    if normalized_tag and normalized_tag not in tags:
                        tags.append(normalized_tag)
                        if len(tags) >= self.min_tags:
                            break
        
        # 如果还是不够，添加通用标签
        if len(tags) < self.min_tags:
            generic_tags = ['政治学', '理论', '分析']
            for tag in generic_tags:
                if tag not in tags:
                    tags.append(tag)
                    if len(tags) >= self.min_tags:
                        break
        
        self.logger.debug(f"生成 {len(tags)} 个标签: {tags}")
        return tags[:self.max_tags]  # 确保不超过最大数量
    
    def _normalize_tag(self, tag: str) -> str:
        """标准化标签格式"""
        if not tag:
            return ""
        
        # 移除空白字符
        tag = tag.strip()
        
        # 转换为适合Obsidian的格式
        # 移除特殊字符，保留中文、英文和数字
        tag = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', tag)
        
        # 确保不为空
        if not tag:
            return ""
        
        return tag
    
    def create_frontmatter(self, tags: List[str], title: str = "", 
                          additional_metadata: Dict[str, any] = None) -> str:
        """创建YAML前置元数据
        
        Args:
            tags: 标签列表
            title: 文档标题（可选）
            additional_metadata: 额外的元数据（可选）
            
        Returns:
            YAML前置元数据字符串
        """
        frontmatter_lines = ["---"]
        
        # 添加标题
        if title:
            frontmatter_lines.append(f"title: \"{title}\"")
        
        # 添加标签
        if tags:
            frontmatter_lines.append("tags:")
            for tag in tags:
                frontmatter_lines.append(f"  - {tag}")
        
        # 添加额外元数据
        if additional_metadata:
            for key, value in additional_metadata.items():
                if isinstance(value, str):
                    frontmatter_lines.append(f"{key}: \"{value}\"")
                elif isinstance(value, list):
                    frontmatter_lines.append(f"{key}:")
                    for item in value:
                        frontmatter_lines.append(f"  - {item}")
                else:
                    frontmatter_lines.append(f"{key}: {value}")
        
        frontmatter_lines.append("---")
        frontmatter_lines.append("")  # 空行分隔
        
        return "\n".join(frontmatter_lines)
    
    def analyze_content_themes(self, content: str) -> Dict[str, float]:
        """分析内容主题分布
        
        Args:
            content: 文本内容
            
        Returns:
            主题及其权重的字典
        """
        themes = {
            '政治制度': ['政治制度', '民主', '专制', '政府', '政权', '制度'],
            '政治理论': ['政治理论', '政治哲学', '政治思想', '理论', '思想'],
            '权力治理': ['权力', '权威', '统治', '治理', '管理', '行政'],
            '政治参与': ['选举', '投票', '民意', '公民', '参与', '权利'],
            '国际政治': ['国际关系', '外交', '国际', '外交政策', '国际组织'],
            '经济政治': ['经济', '市场', '财政', '税收', '经济政策'],
            '社会政治': ['社会', '阶级', '阶层', '社会结构', '社会运动']
        }
        
        theme_scores = {}
        cleaned_content = self._clean_content(content)
        
        for theme_name, theme_words in themes.items():
            score = 0
            for word in theme_words:
                # 计算词频
                count = cleaned_content.count(word)
                score += count
                
                # 政治学专业词汇加权
                if word in self.political_terms:
                    score += count * 0.5
            
            # 标准化分数
            theme_scores[theme_name] = score / len(cleaned_content) if cleaned_content else 0
        
        return theme_scores
    
    def analyze_keyword_distribution(self, content: str) -> Dict[str, any]:
        """分析关键词分布统计
        
        Args:
            content: 文本内容
            
        Returns:
            关键词分布统计信息
        """
        if not content or not content.strip():
            return {}
        
        # 提取关键词
        keywords = self.extract_keywords(content)
        
        # 分类统计
        political_keywords = [kw for kw in keywords if kw in self.political_terms]
        general_keywords = [kw for kw in keywords if kw not in self.political_terms]
        
        # 长度分布
        length_distribution = {}
        for kw in keywords:
            length = len(kw)
            length_distribution[length] = length_distribution.get(length, 0) + 1
        
        return {
            'total_keywords': len(keywords),
            'political_keywords_count': len(political_keywords),
            'general_keywords_count': len(general_keywords),
            'political_keywords': political_keywords[:10],  # 前10个
            'general_keywords': general_keywords[:10],  # 前10个
            'length_distribution': length_distribution,
            'average_keyword_length': sum(len(kw) for kw in keywords) / len(keywords) if keywords else 0
        }
    
    def get_keyword_suggestions(self, content: str, existing_tags: List[str] = None) -> List[str]:
        """获取关键词建议
        
        Args:
            content: 文本内容
            existing_tags: 已有标签列表
            
        Returns:
            建议的关键词列表
        """
        existing_tags = existing_tags or []
        
        # 提取所有关键词
        all_keywords = self.extract_keywords(content)
        
        # 过滤已有标签
        suggestions = []
        for keyword in all_keywords:
            normalized = self._normalize_tag(keyword)
            if normalized and normalized not in existing_tags and normalized not in suggestions:
                suggestions.append(normalized)
                
                # 限制建议数量
                if len(suggestions) >= self.max_tags * 2:
                    break
        
        return suggestions
    
    def validate_tags(self, tags: List[str]) -> Dict[str, any]:
        """验证标签质量
        
        Args:
            tags: 标签列表
            
        Returns:
            验证结果
        """
        validation_result = {
            'valid_tags': [],
            'invalid_tags': [],
            'warnings': [],
            'suggestions': []
        }
        
        for tag in tags:
            if not tag or not isinstance(tag, str):
                validation_result['invalid_tags'].append(tag)
                validation_result['warnings'].append(f"无效标签: {tag}")
                continue
            
            normalized = self._normalize_tag(tag)
            if not normalized:
                validation_result['invalid_tags'].append(tag)
                validation_result['warnings'].append(f"标签格式无效: {tag}")
                continue
            
            if len(normalized) < 2:
                validation_result['invalid_tags'].append(tag)
                validation_result['warnings'].append(f"标签过短: {tag}")
                continue
            
            if normalized in self.stop_words:
                validation_result['invalid_tags'].append(tag)
                validation_result['warnings'].append(f"标签为停用词: {tag}")
                continue
            
            validation_result['valid_tags'].append(normalized)
        
        # 检查标签数量
        if len(validation_result['valid_tags']) < self.min_tags:
            validation_result['warnings'].append(
                f"标签数量不足，建议至少 {self.min_tags} 个"
            )
        
        if len(validation_result['valid_tags']) > self.max_tags:
            validation_result['warnings'].append(
                f"标签数量过多，建议最多 {self.max_tags} 个"
            )
            # 截取前max_tags个
            validation_result['valid_tags'] = validation_result['valid_tags'][:self.max_tags]
        
        return validation_result
    
    def get_statistics(self) -> Dict[str, any]:
        """获取标签生成器统计信息"""
        return {
            'min_tags': self.min_tags,
            'max_tags': self.max_tags,
            'stop_words_count': len(self.stop_words),
            'political_terms_count': len(self.political_terms),
            'jieba_initialized': True,
            'algorithms': ['TF-IDF', 'TextRank'],
            'supported_features': [
                'keyword_extraction',
                'tag_generation', 
                'frontmatter_creation',
                'theme_analysis',
                'keyword_distribution',
                'tag_validation'
            ]
        }