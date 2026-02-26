"""
高级检索服务 - 集成pgvector + BM25 + 去重策略
"""
import logging
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from django.db import connection
from django.conf import settings
from .models import Document, KnowledgeBase
from .vectorization_service import VectorizationService

logger = logging.getLogger(__name__)

class AdvancedRetrievalService:
    """高级检索服务 - pgvector + BM25 + 去重"""
    
    def __init__(self):
        self.vectorizer = VectorizationService()
        self._ensure_pgvector_extension()
    
    def _ensure_pgvector_extension(self):
        """确保pgvector扩展已安装"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("pgvector扩展已确保安装")
        except Exception as e:
            logger.warning(f"pgvector扩展安装失败: {e}")
    
    def hybrid_search(
        self, 
        query: str, 
        knowledge_base_id: Optional[str] = None,
        top_k: int = 5,
        score_threshold: float = 0.2,
        alpha: float = 0.5,
        enable_deduplication: bool = True
    ) -> Dict[str, Any]:
        """
        混合检索：pgvector相似度 + BM25关键词匹配
        
        Args:
            query: 查询文本
            knowledge_base_id: 知识库ID（可选）
            top_k: 返回文档数量
            score_threshold: 分数阈值
            alpha: 融合权重 (0-1, 0=纯BM25, 1=纯向量)
            enable_deduplication: 是否启用去重
            
        Returns:
            检索结果字典
        """
        try:
            # 1. 向量化查询
            query_vector = self.vectorizer.vectorize_query(query)
            
            # 2. 构建SQL查询
            sql_query, params = self._build_hybrid_sql(
                query, query_vector, knowledge_base_id, top_k * 3  # 检索更多用于去重
            )
            
            # 3. 执行检索
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                raw_results = cursor.fetchall()
            
            # 4. 处理结果
            processed_results = self._process_hybrid_results(
                raw_results, query, alpha, score_threshold
            )
            
            # 5. 去重处理
            if enable_deduplication:
                processed_results = self._deduplicate_results(processed_results)
            
            # 6. 返回最终结果，确保Top K有明显差异
            final_results = processed_results[:top_k]
            
            # 为每个结果添加更详细的评分信息
            for i, result in enumerate(final_results):
                result['rank'] = i + 1
                result['display_score'] = round(result.get('score', 0), 3)
                result['vector_score'] = round(result.get('vector_score', 0), 3)
                result['bm25_score'] = round(result.get('bm25_score', 0), 3)
            
            return {
                'query': query,
                'params': {
                    'top_k': top_k,
                    'score_threshold': score_threshold,
                    'alpha': alpha,
                    'enable_deduplication': enable_deduplication
                },
                'evidence': final_results,
                'total_found': len(processed_results),
                'unique_found': len([r for r in processed_results if r.get('dedupe_reason') == 'unique']),
                'strategy_info': {
                    'strategy': 'hybrid',
                    'description': f'混合检索 (α={alpha}, 阈值={score_threshold})',
                    'total_candidates': len(processed_results),
                    'returned_count': len(final_results)
                }
            }
            
        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            return {
                'query': query,
                'error': str(e),
                'evidence': []
            }
    
    def _build_hybrid_sql(
        self, 
        query: str, 
        query_vector: np.ndarray, 
        knowledge_base_id: Optional[str],
        limit: int
    ) -> Tuple[str, List]:
        """构建混合检索SQL"""
        
        # 基础查询
        base_query = """
        SELECT 
            d.id,
            d.title,
            d.content,
            d.knowledge_base_id,
            d.created_at,
            d.vector_embedding,
            -- pgvector余弦相似度
            CASE 
                WHEN d.vector_embedding IS NOT NULL 
                THEN 1 - (d.vector_embedding <=> %s::vector)
                ELSE 0.0
            END as vector_score,
            -- BM25关键词匹配（增强版）
            CASE 
                WHEN d.content IS NOT NULL
                THEN (
                    -- 计算查询词在文档中的出现频率，使用更敏感的算法
                    (
                        SELECT SUM(
                            CASE 
                                WHEN lower(d.content) LIKE '%' || q_word || '%' 
                                THEN 1.0 + (length(d.content) - length(replace(lower(d.content), q_word, ''))) / length(q_word) * 0.1
                                ELSE 0.0
                            END
                        )
                        FROM unnest(string_to_array(lower(%s), ' ')) as q_word
                        WHERE q_word != '' AND q_word != '的' AND q_word != '了' AND q_word != '是' AND length(q_word) > 1
                    )::float / GREATEST(
                        (SELECT COUNT(*) FROM unnest(string_to_array(lower(%s), ' ')) WHERE unnest != '' AND length(unnest) > 1), 1
                    )
                )
                ELSE 0.0
            END as bm25_score
        FROM documents d
        WHERE d.vector_embedding IS NOT NULL
        """
        
        params = [query_vector.tolist(), query, query]
        
        # 添加知识库过滤
        if knowledge_base_id:
            base_query += " AND d.knowledge_base_id = %s"
            params.append(knowledge_base_id)
        
        # 添加排序和限制
        base_query += f"""
        ORDER BY 
            (CASE 
                WHEN d.vector_embedding IS NOT NULL 
                THEN 1 - (d.vector_embedding <=> %s::vector)
                ELSE 0.0
            END) DESC,
            d.created_at DESC
        LIMIT %s
        """
        
        params.extend([query_vector.tolist(), limit])
        
        return base_query, params
    
    def _process_hybrid_results(
        self, 
        raw_results: List[Tuple], 
        query: str, 
        alpha: float,
        score_threshold: float
    ) -> List[Dict[str, Any]]:
        """处理混合检索结果"""
        processed = []
        
        for row in raw_results:
            doc_id, title, content, kb_id, created_at, vector_embedding, vector_score, bm25_score = row
            
            # 计算融合分数
            hybrid_score = alpha * vector_score + (1 - alpha) * bm25_score
            
            # 过滤低分结果
            if hybrid_score < score_threshold:
                continue
            
            # 生成内容哈希用于去重
            content_hash = hashlib.sha256(
                (content or '')[:200].encode('utf-8')
            ).hexdigest()
            
            processed.append({
                'source': {
                    'document_id': str(doc_id),
                    'title': title,
                    'knowledge_base_id': str(kb_id),
                    'content_preview': (content or '')[:150] + '...' if content and len(content) > 150 else content,
                    'created_at': created_at.isoformat() if created_at else None
                },
                'score': round(hybrid_score, 4),
                'vector_score': round(vector_score, 4),
                'bm25_score': round(bm25_score, 4),
                'content_hash': content_hash,
                'dedupe_reason': 'pending'  # 待去重处理
            })
        
        # 按分数排序
        processed.sort(key=lambda x: x['score'], reverse=True)
        
        return processed
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重处理"""
        seen_hashes = set()
        deduplicated = []
        
        for result in results:
            content_hash = result['content_hash']
            
            if content_hash not in seen_hashes:
                result['dedupe_reason'] = 'unique'
                deduplicated.append(result)
                seen_hashes.add(content_hash)
            else:
                result['dedupe_reason'] = 'duplicate_content'
                deduplicated.append(result)
        
        return deduplicated
    
    def pgvector_search(
        self, 
        query: str, 
        knowledge_base_id: Optional[str] = None,
        top_k: int = 5,
        score_threshold: float = 0.2
    ) -> List[Dict[str, Any]]:
        """纯pgvector检索"""
        try:
            query_vector = self.vectorizer.vectorize_query(query)
            
            sql_query = """
            SELECT 
                d.id,
                d.title,
                d.content,
                d.knowledge_base_id,
                d.created_at,
                1 - (d.vector_embedding <=> %s::vector) as similarity_score
            FROM documents d
            WHERE d.vector_embedding IS NOT NULL
            """
            
            params = [query_vector.tolist()]
            
            if knowledge_base_id:
                sql_query += " AND d.knowledge_base_id = %s"
                params.append(knowledge_base_id)
            
            sql_query += """
            AND (1 - (d.vector_embedding <=> %s::vector)) >= %s
            ORDER BY similarity_score DESC
            LIMIT %s
            """
            
            params.extend([query_vector.tolist(), score_threshold, top_k])
            
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                results = cursor.fetchall()
            
            processed_results = []
            for row in results:
                doc_id, title, content, kb_id, created_at, similarity_score = row
                processed_results.append({
                    'source': {
                        'document_id': str(doc_id),
                        'title': title,
                        'knowledge_base_id': str(kb_id),
                        'content_preview': (content or '')[:150] + '...' if content and len(content) > 150 else content
                    },
                    'score': round(similarity_score, 4),
                    'method': 'pgvector'
                })
            
            return processed_results
            
        except Exception as e:
            logger.error(f"pgvector检索失败: {e}")
            return []
    
    def bm25_search(
        self, 
        query: str, 
        knowledge_base_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """BM25关键词检索"""
        try:
            # 提取关键词
            keywords = [word for word in query.split() if len(word) > 1]
            
            if not keywords:
                return []
            
            # 构建BM25查询
            keyword_conditions = []
            params = []
            
            for keyword in keywords:
                keyword_conditions.append("lower(d.content) LIKE %s")
                params.append(f"%{keyword.lower()}%")
            
            sql_query = f"""
            SELECT 
                d.id,
                d.title,
                d.content,
                d.knowledge_base_id,
                d.created_at,
                (
                    SELECT COUNT(*)
                    FROM unnest(string_to_array(lower(d.content), ' ')) as word
                    WHERE word = ANY(%s)
                )::float / GREATEST(length(d.content), 1) as bm25_score
            FROM documents d
            WHERE d.content IS NOT NULL
            AND ({' OR '.join(keyword_conditions)})
            """
            
            params.insert(0, keywords)
            
            if knowledge_base_id:
                sql_query += " AND d.knowledge_base_id = %s"
                params.append(knowledge_base_id)
            
            sql_query += """
            ORDER BY bm25_score DESC
            LIMIT %s
            """
            params.append(top_k)
            
            with connection.cursor() as cursor:
                cursor.execute(sql_query, params)
                results = cursor.fetchall()
            
            processed_results = []
            for row in results:
                doc_id, title, content, kb_id, created_at, bm25_score = row
                processed_results.append({
                    'source': {
                        'document_id': str(doc_id),
                        'title': title,
                        'knowledge_base_id': str(kb_id),
                        'content_preview': (content or '')[:150] + '...' if content and len(content) > 150 else content
                    },
                    'score': round(bm25_score, 4),
                    'method': 'bm25'
                })
            
            return processed_results
            
        except Exception as e:
            logger.error(f"BM25检索失败: {e}")
            return []


class RetrievalStrategyManager:
    """检索策略管理器"""
    
    def __init__(self):
        self.retrieval_service = AdvancedRetrievalService()
    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """获取检索策略配置"""
        strategies = {
            'hybrid': {
                'name': '混合检索',
                'description': '向量相似度 + BM25关键词匹配',
                'default_params': {
                    'alpha': 0.5,
                    'top_k': 5,
                    'score_threshold': 0.2,
                    'enable_deduplication': True
                }
            },
            'vector_only': {
                'name': '纯向量检索',
                'description': '仅使用pgvector相似度',
                'default_params': {
                    'top_k': 5,
                    'score_threshold': 0.2
                }
            },
            'bm25_only': {
                'name': '纯关键词检索',
                'description': '仅使用BM25关键词匹配',
                'default_params': {
                    'top_k': 5
                }
            }
        }
        
        return strategies.get(strategy_name, strategies['hybrid'])
    
    def execute_strategy(
        self, 
        strategy_name: str, 
        query: str, 
        knowledge_base_id: Optional[str] = None,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行检索策略"""
        config = self.get_strategy_config(strategy_name)
        params = config['default_params'].copy()
        
        if custom_params:
            params.update(custom_params)
        
        if strategy_name == 'hybrid':
            return self.retrieval_service.hybrid_search(
                query, knowledge_base_id, **params
            )
        elif strategy_name == 'vector_only':
            return {
                'query': query,
                'evidence': self.retrieval_service.pgvector_search(
                    query, knowledge_base_id, **params
                )
            }
        elif strategy_name == 'bm25_only':
            return {
                'query': query,
                'evidence': self.retrieval_service.bm25_search(
                    query, knowledge_base_id, **params
                )
            }
        else:
            raise ValueError(f"未知的检索策略: {strategy_name}")
