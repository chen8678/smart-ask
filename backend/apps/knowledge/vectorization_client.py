"""
向量化服务客户端 - 与向量化微服务通信
"""
import httpx
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

class VectorizationClient:
    """向量化服务客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or getattr(settings, 'VECTORIZATION_SERVICE_URL', 'http://vectorization:8001')
        self.timeout = 30.0
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求到向量化服务"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"向量化服务请求超时: {url}")
            raise Exception("向量化服务请求超时")
        except httpx.HTTPStatusError as e:
            logger.error(f"向量化服务HTTP错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"向量化服务错误: {e.response.status_code}")
        except Exception as e:
            logger.error(f"向量化服务请求失败: {e}")
            raise Exception(f"向量化服务请求失败: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """检查向量化服务健康状态"""
        return await self._make_request("GET", "/health")
    
    async def list_models(self) -> Dict[str, Any]:
        """获取可用模型列表"""
        return await self._make_request("GET", "/models")
    
    async def vectorize_text(self, text: str, model_name: str = "BAAI/bge-large-zh-v1.5") -> List[float]:
        """
        向量化单个文本
        
        Args:
            text: 输入文本
            model_name: 模型名称
            
        Returns:
            向量列表
        """
        data = {
            "text": text,
            "model_name": model_name
        }
        
        response = await self._make_request("POST", "/vectorize", json=data)
        return response["vector"]
    
    async def vectorize_batch(self, texts: List[str], model_name: str = "BAAI/bge-large-zh-v1.5") -> List[List[float]]:
        """
        批量向量化文本
        
        Args:
            texts: 文本列表
            model_name: 模型名称
            
        Returns:
            向量矩阵
        """
        data = {
            "texts": texts,
            "model_name": model_name
        }
        
        response = await self._make_request("POST", "/vectorize/batch", json=data)
        return response["vectors"]
    
    async def search_similar(self, query: str, vectors: List[List[float]], top_k: int = 5, model_name: str = "BAAI/bge-large-zh-v1.5") -> List[Dict[str, Any]]:
        """
        相似度检索
        
        Args:
            query: 查询文本
            vectors: 候选向量列表
            top_k: 返回数量
            model_name: 模型名称
            
        Returns:
            相似度结果列表
        """
        data = {
            "query": query,
            "vectors": vectors,
            "top_k": top_k,
            "model_name": model_name
        }
        
        response = await self._make_request("POST", "/search", json=data)
        return response["results"]
    
    async def switch_model(self, model_name: str) -> Dict[str, Any]:
        """切换向量化模型"""
        return await self._make_request("POST", f"/models/switch?model_name={model_name}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return await self._make_request("GET", "/stats")

# 全局客户端实例
_vectorization_client = None

def get_vectorization_client() -> VectorizationClient:
    """获取向量化客户端实例"""
    global _vectorization_client
    if _vectorization_client is None:
        _vectorization_client = VectorizationClient()
    return _vectorization_client

# 同步包装器（用于在Django视图中使用）
class SyncVectorizationClient:
    """同步向量化客户端包装器"""
    
    def __init__(self):
        self.client = get_vectorization_client()
    
    def vectorize_text(self, text: str, model_name: str = "BAAI/bge-large-zh-v1.5") -> List[float]:
        """同步向量化文本"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.client.vectorize_text(text, model_name)
        )
    
    def vectorize_batch(self, texts: List[str], model_name: str = "BAAI/bge-large-zh-v1.5") -> List[List[float]]:
        """同步批量向量化"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.client.vectorize_batch(texts, model_name)
        )
    
    def search_similar(self, query: str, vectors: List[List[float]], top_k: int = 5, model_name: str = "BAAI/bge-large-zh-v1.5") -> List[Dict[str, Any]]:
        """同步相似度检索"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.client.search_similar(query, vectors, top_k, model_name)
        )
    
    def health_check(self) -> Dict[str, Any]:
        """同步健康检查"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.client.health_check()
        )
