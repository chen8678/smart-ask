"""
文档内容分析器 - 智能识别文档质量与相关性
通用平台文档质量评估系统
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DocumentRelevance(Enum):
    """文档相关性等级"""
    HIGHLY_RELEVANT = "highly_relevant"  # 高度相关
    RELEVANT = "relevant"  # 相关
    PARTIALLY_RELEVANT = "partially_relevant"  # 部分相关
    IRRELEVANT = "irrelevant"  # 不相关
    UNKNOWN = "unknown"  # 无法确定


class ContentType(Enum):
    """内容类型"""
    EDUCATIONAL = "educational"  # 教育内容
    TECHNICAL = "technical"  # 技术文档
    RESEARCH = "research"  # 研究论文
    TUTORIAL = "tutorial"  # 教程指南
    REFERENCE = "reference"  # 参考资料
    BUSINESS = "business"  # 商业文档
    LEGAL = "legal"  # 法律文档
    MEDICAL = "medical"  # 医疗文档
    FINANCIAL = "financial"  # 金融文档
    PERSONAL = "personal"  # 个人文档
    SPAM = "spam"  # 垃圾内容
    UNKNOWN = "unknown"  # 未知类型


@dataclass
class DocumentAnalysisResult:
    """文档分析结果"""
    relevance: DocumentRelevance
    content_type: ContentType
    confidence: float  # 0-1 之间的置信度
    keywords: List[str]
    issues: List[str]  # 发现的问题
    suggestions: List[str]  # 改进建议
    quality_score: float  # 0-100 的质量分数


class DocumentAnalyzer:
    """文档内容分析器"""
    
    def __init__(self):
        # 教育相关关键词（中英文）
        self.educational_keywords = {
            '学习', '教育', '教学', '课程', '知识', '技能', '培训', '指导',
            '教程', '指南', '手册', '说明', '解释', '概念', '理论', '实践',
            '练习', '作业', '考试', '评估', '测试', '研究', '分析', '总结',
            'learning', 'education', 'teaching', 'course', 'knowledge', 'skill',
            'training', 'guide', 'tutorial', 'manual', 'explanation', 'concept',
            'theory', 'practice', 'exercise', 'assignment', 'exam', 'evaluation',
            'test', 'research', 'analysis', 'summary', 'study', 'academic'
        }
        
        # 技术相关关键词（中英文）
        self.technical_keywords = {
            '技术', '系统', '开发', '编程', '代码', '算法', '数据', '软件',
            '硬件', '网络', '安全', '数据库', '应用', '平台', '工具', '方法',
            'technology', 'system', 'development', 'programming', 'code', 'algorithm',
            'data', 'software', 'hardware', 'network', 'security', 'database',
            'application', 'platform', 'tool', 'method', 'api', 'framework'
        }
        
        # 商业相关关键词
        self.business_keywords = {
            '商业', '企业', '管理', '营销', '销售', '市场', '客户', '产品',
            '服务', '财务', '投资', '战略', '运营', '人力资源', '项目',
            'business', 'enterprise', 'management', 'marketing', 'sales', 'market',
            'customer', 'product', 'service', 'finance', 'investment', 'strategy',
            'operation', 'hr', 'project', 'revenue', 'profit'
        }
        
        # 法律相关关键词
        self.legal_keywords = {
            '法律', '法规', '条例', '合同', '协议', '权利', '义务', '责任',
            '诉讼', '仲裁', '判决', '律师', '法院', '司法', '合规', '风险',
            'legal', 'law', 'regulation', 'contract', 'agreement', 'right', 'obligation',
            'liability', 'litigation', 'arbitration', 'judgment', 'lawyer', 'court',
            'justice', 'compliance', 'risk'
        }
        
        # 医疗相关关键词
        self.medical_keywords = {
            '医疗', '健康', '疾病', '治疗', '药物', '诊断', '症状', '患者',
            '医生', '医院', '护理', '康复', '预防', '检查', '手术', '临床',
            'medical', 'health', 'disease', 'treatment', 'drug', 'diagnosis', 'symptom',
            'patient', 'doctor', 'hospital', 'nursing', 'rehabilitation', 'prevention',
            'examination', 'surgery', 'clinical'
        }
        
        # 金融相关关键词
        self.financial_keywords = {
            '金融', '银行', '投资', '股票', '债券', '基金', '保险', '贷款',
            '理财', '资产', '负债', '收益', '风险', '市场', '交易', '分析',
            'financial', 'bank', 'investment', 'stock', 'bond', 'fund', 'insurance',
            'loan', 'wealth', 'asset', 'liability', 'return', 'risk', 'market',
            'trading', 'analysis'
        }
        
        # 不相关内容关键词
        self.irrelevant_keywords = {
            '广告', '推广', '销售', '购买', '价格', '优惠', '促销', '营销',
            '娱乐', '游戏', '电影', '音乐', '小说', '故事', '八卦', '新闻',
            '政治', '宗教', '个人', '私密', '垃圾', 'spam', 'advertisement',
            'promotion', 'entertainment', 'game', 'movie', 'music', 'novel',
            'story', 'gossip', 'news', 'politics', 'religion', 'personal', 'private'
        }
        
        # 文档质量指标
        self.quality_indicators = {
            'min_length': 100,  # 最小字符数
            'max_length': 100000,  # 最大字符数
            'min_paragraphs': 2,  # 最小段落数
            'min_sentences': 5,  # 最小句子数
        }

    def analyze_document(self, content: str, filename: str = "") -> DocumentAnalysisResult:
        """
        分析文档内容，评估文档质量和相关性
        
        Args:
            content: 文档内容
            filename: 文件名（可选）
            
        Returns:
            DocumentAnalysisResult: 分析结果
        """
        try:
            # 1. 基础内容检查
            basic_issues = self._check_basic_quality(content)
            
            # 2. 内容类型识别
            content_type = self._identify_content_type(content, filename)
            
            # 3. 相关性分析
            relevance = self._analyze_relevance(content, content_type)
            
            # 4. 关键词提取
            keywords = self._extract_keywords(content)
            
            # 5. 计算质量分数
            quality_score = self._calculate_quality_score(content, relevance, content_type)
            
            # 6. 生成建议
            suggestions = self._generate_suggestions(content, relevance, content_type, basic_issues)
            
            return DocumentAnalysisResult(
                relevance=relevance,
                content_type=content_type,
                confidence=self._calculate_confidence(relevance, content_type, quality_score),
                keywords=keywords,
                issues=basic_issues,
                suggestions=suggestions,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"文档分析失败: {e}")
            return DocumentAnalysisResult(
                relevance=DocumentRelevance.UNKNOWN,
                content_type=ContentType.UNKNOWN,
                confidence=0.0,
                keywords=[],
                issues=[f"分析失败: {str(e)}"],
                suggestions=["请检查文档格式是否正确"],
                quality_score=0.0
            )

    def _check_basic_quality(self, content: str) -> List[str]:
        """检查文档基础质量"""
        issues = []
        
        # 检查长度
        if len(content) < self.quality_indicators['min_length']:
            issues.append(f"文档过短（{len(content)}字符），建议至少{self.quality_indicators['min_length']}字符")
        
        if len(content) > self.quality_indicators['max_length']:
            issues.append(f"文档过长（{len(content)}字符），建议不超过{self.quality_indicators['max_length']}字符")
        
        # 检查段落数
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) < self.quality_indicators['min_paragraphs']:
            issues.append(f"段落数过少（{len(paragraphs)}个），建议至少{self.quality_indicators['min_paragraphs']}个段落")
        
        # 检查句子数
        sentences = re.split(r'[.!?。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < self.quality_indicators['min_sentences']:
            issues.append(f"句子数过少（{len(sentences)}个），建议至少{self.quality_indicators['min_sentences']}个句子")
        
        # 检查是否包含过多重复内容
        words = content.split()
        if len(words) > 0:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > 0.7:
                issues.append("文档包含过多重复内容，可能影响学习效果")
        
        return issues

    def _identify_content_type(self, content: str, filename: str = "") -> ContentType:
        """识别内容类型"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # 检查文件名特征
        if any(keyword in filename_lower for keyword in ['tutorial', 'guide', 'manual', '教程', '指南', '手册']):
            return ContentType.TUTORIAL
        
        if any(keyword in filename_lower for keyword in ['research', 'paper', 'study', '研究', '论文', '学术']):
            return ContentType.RESEARCH
        
        if any(keyword in filename_lower for keyword in ['legal', 'law', 'contract', '法律', '合同', '法规']):
            return ContentType.LEGAL
        
        if any(keyword in filename_lower for keyword in ['medical', 'health', '医疗', '健康', '医学']):
            return ContentType.MEDICAL
        
        if any(keyword in filename_lower for keyword in ['financial', 'finance', 'bank', '金融', '银行', '财务']):
            return ContentType.FINANCIAL
        
        if any(keyword in filename_lower for keyword in ['business', 'enterprise', '商业', '企业', '管理']):
            return ContentType.BUSINESS
        
        # 检查内容特征
        educational_score = sum(1 for keyword in self.educational_keywords if keyword in content_lower)
        technical_score = sum(1 for keyword in self.technical_keywords if keyword in content_lower)
        business_score = sum(1 for keyword in self.business_keywords if keyword in content_lower)
        legal_score = sum(1 for keyword in self.legal_keywords if keyword in content_lower)
        medical_score = sum(1 for keyword in self.medical_keywords if keyword in content_lower)
        financial_score = sum(1 for keyword in self.financial_keywords if keyword in content_lower)
        irrelevant_score = sum(1 for keyword in self.irrelevant_keywords if keyword in content_lower)
        
        # 计算各领域得分
        domain_scores = {
            ContentType.EDUCATIONAL: educational_score,
            ContentType.TECHNICAL: technical_score,
            ContentType.BUSINESS: business_score,
            ContentType.LEGAL: legal_score,
            ContentType.MEDICAL: medical_score,
            ContentType.FINANCIAL: financial_score,
        }
        
        # 如果垃圾内容得分过高
        if irrelevant_score > max(domain_scores.values()) * 2:
            return ContentType.SPAM
        
        # 返回得分最高的领域
        if max(domain_scores.values()) > 0:
            return max(domain_scores, key=domain_scores.get)
        else:
            return ContentType.UNKNOWN

    def _analyze_relevance(self, content: str, content_type: ContentType) -> DocumentRelevance:
        """分析文档的相关性"""
        content_lower = content.lower()
        
        # 如果被识别为垃圾内容，直接标记为不相关
        if content_type == ContentType.SPAM:
            return DocumentRelevance.IRRELEVANT
        
        # 计算各领域相关性分数
        educational_score = sum(1 for keyword in self.educational_keywords if keyword in content_lower)
        technical_score = sum(1 for keyword in self.technical_keywords if keyword in content_lower)
        business_score = sum(1 for keyword in self.business_keywords if keyword in content_lower)
        legal_score = sum(1 for keyword in self.legal_keywords if keyword in content_lower)
        medical_score = sum(1 for keyword in self.medical_keywords if keyword in content_lower)
        financial_score = sum(1 for keyword in self.financial_keywords if keyword in content_lower)
        irrelevant_score = sum(1 for keyword in self.irrelevant_keywords if keyword in content_lower)
        
        total_relevant = educational_score + technical_score + business_score + legal_score + medical_score + financial_score
        total_irrelevant = irrelevant_score
        
        if total_irrelevant > total_relevant * 2:
            return DocumentRelevance.IRRELEVANT
        elif total_relevant >= 5:
            return DocumentRelevance.HIGHLY_RELEVANT
        elif total_relevant >= 2:
            return DocumentRelevance.RELEVANT
        elif total_relevant >= 1:
            return DocumentRelevance.PARTIALLY_RELEVANT
        else:
            return DocumentRelevance.IRRELEVANT

    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（可以后续集成更复杂的NLP库）
        words = re.findall(r'\b\w+\b', content.lower())
        word_freq = {}
        
        for word in words:
            if len(word) > 2:  # 过滤短词
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的前10个词
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    def _calculate_quality_score(self, content: str, relevance: DocumentRelevance, content_type: ContentType) -> float:
        """计算文档质量分数（0-100）"""
        score = 0.0
        
        # 基础分数
        score += 20.0
        
        # 长度分数
        length_score = min(20.0, len(content) / 1000 * 20)
        score += length_score
        
        # 相关性分数
        relevance_scores = {
            DocumentRelevance.HIGHLY_RELEVANT: 30.0,
            DocumentRelevance.RELEVANT: 20.0,
            DocumentRelevance.PARTIALLY_RELEVANT: 10.0,
            DocumentRelevance.IRRELEVANT: 0.0,
            DocumentRelevance.UNKNOWN: 5.0
        }
        score += relevance_scores.get(relevance, 0.0)
        
        # 内容类型分数
        type_scores = {
            ContentType.EDUCATIONAL: 15.0,
            ContentType.TECHNICAL: 15.0,
            ContentType.RESEARCH: 15.0,
            ContentType.TUTORIAL: 15.0,
            ContentType.BUSINESS: 15.0,
            ContentType.LEGAL: 15.0,
            ContentType.MEDICAL: 15.0,
            ContentType.FINANCIAL: 15.0,
            ContentType.REFERENCE: 10.0,
            ContentType.PERSONAL: 5.0,
            ContentType.SPAM: 0.0,
            ContentType.UNKNOWN: 5.0
        }
        score += type_scores.get(content_type, 0.0)
        
        # 结构分数
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 10.0
        elif len(paragraphs) >= 2:
            score += 5.0
        
        return min(100.0, max(0.0, score))

    def _generate_suggestions(self, content: str, relevance: DocumentRelevance, 
                            content_type: ContentType, issues: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if relevance == DocumentRelevance.IRRELEVANT:
            suggestions.append("此文档似乎与知识库主题无关，建议上传相关领域的内容")
        
        if content_type == ContentType.SPAM:
            suggestions.append("检测到垃圾内容，请上传有意义的文档")
        
        if len(content) < 500:
            suggestions.append("文档内容较少，建议提供更详细的信息")
        
        # 检查是否有任何相关关键词
        all_relevant_keywords = (self.educational_keywords | self.technical_keywords | 
                               self.business_keywords | self.legal_keywords | 
                               self.medical_keywords | self.financial_keywords)
        
        if not any(keyword in content.lower() for keyword in all_relevant_keywords):
            suggestions.append("建议添加更多专业相关内容以提高文档价值")
        
        if len(issues) > 0:
            suggestions.append("请根据检测到的问题改进文档质量")
        
        return suggestions

    def _calculate_confidence(self, relevance: DocumentRelevance, content_type: ContentType, quality_score: float) -> float:
        """计算分析结果的置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于质量分数调整
        if quality_score > 80:
            confidence += 0.3
        elif quality_score > 60:
            confidence += 0.2
        elif quality_score > 40:
            confidence += 0.1
        
        # 基于内容类型调整
        if content_type in [ContentType.EDUCATIONAL, ContentType.TECHNICAL, ContentType.RESEARCH,
                           ContentType.BUSINESS, ContentType.LEGAL, ContentType.MEDICAL, ContentType.FINANCIAL]:
            confidence += 0.2
        
        return min(1.0, max(0.0, confidence))
