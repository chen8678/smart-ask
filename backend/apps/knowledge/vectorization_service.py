"""
向量化服务 - 负责文档的向量化和检索
使用微服务架构，通过HTTP API调用向量化服务
"""
import numpy as np
from typing import List, Tuple, Optional
import logging
from django.conf import settings
from .vectorization_client import SyncVectorizationClient

logger = logging.getLogger(__name__)

class VectorizationService:
    """文档向量化服务 - 使用微服务架构"""
    
    def __init__(self, model_name: str = 'BAAI/bge-large-zh-v1.5'):
        """
        初始化向量化服务
        
        Args:
            model_name: 使用的向量化模型名称
        """
        self.model_name = model_name
        self.client = SyncVectorizationClient()
        self._check_service_health()
    
    def _check_service_health(self):
        """检查向量化服务健康状态"""
        try:
            health = self.client.health_check()
            if not health.get('model_loaded', False):
                logger.warning("向量化服务模型未加载，可能影响性能")
            logger.info("向量化服务连接正常")
        except Exception as e:
            logger.error(f"向量化服务连接失败: {e}")
            # 不抛出异常，允许降级到简单向量化
            logger.warning("将使用简单向量化作为备用方案")
    
    def vectorize_text(self, text: str) -> np.ndarray:
        """
        将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            向量表示
        """
        if not text or not text.strip():
            return np.zeros(1024)  # 默认维度
        
        try:
            # 使用微服务向量化
            vector = self.client.vectorize_text(text, self.model_name)
            return np.array(vector)
        except Exception as e:
            logger.error(f"微服务向量化失败: {e}")
            # 降级到简单向量化
            return self._fallback_vectorize(text)
    
    def vectorize_query(self, query: str) -> np.ndarray:
        """
        将查询转换为向量
        
        Args:
            query: 查询文本
            
        Returns:
            向量表示
        """
        if not query or not query.strip():
            return np.zeros(1024)
        
        try:
            # 使用微服务向量化
            vector = self.client.vectorize_text(query, self.model_name)
            return np.array(vector)
        except Exception as e:
            logger.error(f"微服务查询向量化失败: {e}")
            # 降级到简单向量化
            return self._fallback_vectorize(query)
    
    def batch_vectorize(self, texts: List[str]) -> np.ndarray:
        """
        批量向量化文本
        
        Args:
            texts: 文本列表
            
        Returns:
            向量矩阵
        """
        if not texts:
            return np.array([])
        
        try:
            # 使用微服务批量向量化
            vectors = self.client.vectorize_batch(texts, self.model_name)
            return np.array(vectors)
        except Exception as e:
            logger.error(f"微服务批量向量化失败: {e}")
            # 降级到简单向量化
            return self._fallback_batch_vectorize(texts)
    
    def _fallback_vectorize(self, text: str) -> np.ndarray:
        """备用简单向量化"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            
            # 创建简单的TF-IDF向量化器
            vectorizer = TfidfVectorizer(max_features=1536, stop_words=None)
            
            # 使用示例文本进行拟合
            sample_texts = [
                "人工智能是计算机科学的一个分支",
                "机器学习是人工智能的核心技术", 
                "深度学习使用神经网络进行学习",
                "自然语言处理让计算机理解人类语言",
                text  # 包含当前文本
            ]
            
            vectorizer.fit(sample_texts)
            vector = vectorizer.transform([text]).toarray()[0]
            
            # 确保向量长度为1024
            if len(vector) < 1024:
                vector = np.pad(vector, (0, 1024 - len(vector)), 'constant')
            elif len(vector) > 1024:
                vector = vector[:1024]
            
            return vector
            
        except Exception as e:
            logger.error(f"备用向量化失败: {e}")
            return np.zeros(1024)
    
    def _fallback_batch_vectorize(self, texts: List[str]) -> np.ndarray:
        """备用批量向量化"""
        vectors = []
        for text in texts:
            vectors.append(self._fallback_vectorize(text))
        return np.array(vectors)

class VectorRetrievalService:
    """向量检索服务"""
    
    def __init__(self):
        self.vectorizer = VectorizationService()
    
    def search_similar_documents(self, query: str, knowledge_base_id: str, top_k: int = 5) -> List[Tuple[object, float]]:
        """
        基于向量相似度搜索文档
        
        Args:
            query: 查询文本
            knowledge_base_id: 知识库ID
            top_k: 返回文档数量
            
        Returns:
            (文档对象, 相似度分数) 的列表
        """
        from .models import Document
        
        try:
            # 向量化查询
            query_vector = self.vectorizer.vectorize_query(query)
            
            # 获取知识库中所有有向量的文档，大幅限制数量以提高性能
            documents = Document.objects.filter(
                knowledge_base_id=knowledge_base_id,
                vector_embedding__isnull=False
            ).only('id', 'title', 'content', 'vector_embedding')[:50]  # 限制最多50个文档，大幅减少处理量
            
            if not documents.exists():
                logger.warning(f"知识库 {knowledge_base_id} 中没有向量化的文档")
                return []
            
            # 批量计算相似度以提高性能
            results = []
            query_vector_np = np.array(query_vector)
            
            for doc in documents:
                if doc.vector_embedding is not None and len(doc.vector_embedding) > 0:
                    try:
                        doc_vector = np.array(doc.vector_embedding)
                        similarity = self._calculate_cosine_similarity(
                            query_vector_np, 
                            doc_vector
                        )
                        results.append((doc, similarity))
                    except Exception as e:
                        logger.warning(f"计算文档 {doc.id} 相似度失败: {e}")
                        continue
            
            # 按相似度排序
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []
    
    def _calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            相似度分数 (0-1)
        """
        try:
            # 确保向量是numpy数组
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            # 计算余弦相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"相似度计算失败: {e}")
            return 0.0

class HybridRetrievalService:
    """混合检索服务 - 结合向量检索和关键词检索"""
    
    def __init__(self):
        self.vector_retrieval = VectorRetrievalService()
        self.keyword_retrieval = None  # 可以添加关键词检索服务
    
    def search_documents(self, query: str, knowledge_base_id: str, top_k: int = 5) -> List[Tuple[object, float]]:
        """
        混合检索文档
        
        Args:
            query: 查询文本
            knowledge_base_id: 知识库ID
            top_k: 返回文档数量
            
        Returns:
            (文档对象, 综合分数) 的列表
        """
        # 向量检索，限制检索数量
        vector_results = self.vector_retrieval.search_similar_documents(
            query, knowledge_base_id, min(top_k, 10)  # 最多检索10个文档
        )
        
        # 如果没有向量检索结果，回退到关键词检索
        if not vector_results:
            logger.warning("向量检索无结果，回退到关键词检索")
            return self._fallback_keyword_search(query, knowledge_base_id, top_k)
        
        # 对结果进行重排序和去重
        final_results = self._rerank_results(vector_results, query)
        
        return final_results[:top_k]
    
    def _fallback_keyword_search(self, query: str, knowledge_base_id: str, top_k: int) -> List[Tuple[object, float]]:
        """回退到关键词检索"""
        from .models import Document
        import re
        
        try:
            # 简单的关键词匹配
            keywords = re.findall(r'[\u4e00-\u9fff\w]+', query)
            documents = Document.objects.filter(knowledge_base_id=knowledge_base_id)
            
            results = []
            for doc in documents:
                if doc.content:
                    score = self._calculate_keyword_score(query, doc.content, keywords)
                    if score > 0.1:
                        results.append((doc, score))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"关键词检索失败: {e}")
            return []
    
    def _calculate_keyword_score(self, query: str, content: str, keywords: List[str]) -> float:
        """计算关键词匹配分数"""
        if not content or not keywords:
            return 0.0
        
        content_lower = content.lower()
        query_lower = query.lower()
        
        # 关键词匹配
        keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
        keyword_score = keyword_matches / len(keywords) if keywords else 0
        
        # 直接匹配
        direct_matches = sum(1 for word in query_lower.split() if word in content_lower)
        direct_score = direct_matches / len(query_lower.split()) if query_lower.split() else 0
        
        return keyword_score * 0.7 + direct_score * 0.3
    
    def _rerank_results(self, results: List[Tuple[object, float]], query: str) -> List[Tuple[object, float]]:
        """重排序结果"""
        # 简单的重排序逻辑，可以根据需要扩展
        return results
