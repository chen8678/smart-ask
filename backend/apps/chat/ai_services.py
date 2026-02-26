"""
AI服务实现
"""
import requests
import json
import os
import time
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from ai_qa_system.ai_config import AIConfig, AIModel

class BaseAIService(ABC):
    """AI服务基类"""
    
    def __init__(self, model: AIModel, api_key: str):
        self.model = model
        self.api_key = api_key
        self.config = AIConfig.get_model_config(model)
        self.max_retries = 3
        self.retry_delay = 1  # 秒
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """生成回复"""
        pass
    
    def format_messages(self, system_prompt: str, user_content: str) -> List[Dict[str, str]]:
        """格式化消息"""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    
    def _make_request_with_retry(self, url: str, headers: Dict, data: Dict, timeout: tuple) -> requests.Response:
        """带重试机制的请求"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                return response
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    print(f"API请求失败，第{attempt + 1}次重试，等待{self.retry_delay}秒...")
                    time.sleep(self.retry_delay * (attempt + 1))  # 指数退避
                else:
                    print(f"API请求失败，已达到最大重试次数: {e}")
            except Exception as e:
                last_exception = e
                print(f"API请求出现未知错误: {e}")
                break
        
        raise last_exception

class DeepSeekService(BaseAIService):
    """DeepSeek AI服务"""
    
    def __init__(self, api_key: str):
        super().__init__(AIModel.DEEPSEEK, api_key)
        self.model_name = "deepseek-chat"
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """调用DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name if hasattr(self, 'model_name') else "deepseek-chat",
                "messages": messages,
                "max_tokens": self.config["max_tokens"],
                "temperature": self.config["temperature"],
                "stream": False
            }
            
            # 设置更长的超时时间：(连接超时, 读取超时)
            timeout_config = (15, 120)  # 15秒连接，120秒读取
            
            response = self._make_request_with_retry(
                f"{self.config['api_base']}/chat/completions",
                headers=headers,
                data=data,
                timeout=timeout_config
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"生成回复时出现错误: {str(e)}"

class QwenService(BaseAIService):
    """通义千问AI服务"""
    
    def __init__(self, api_key: str):
        super().__init__(AIModel.QWEN, api_key)
        self.model_name = "qwen-turbo"
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """调用通义千问API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name if hasattr(self, 'model_name') else "deepseek-chat",
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "max_tokens": self.config["max_tokens"],
                    "temperature": self.config["temperature"]
                }
            }
            
            # 设置更长的超时时间：(连接超时, 读取超时)
            timeout_config = (15, 120)  # 15秒连接，120秒读取
            
            response = self._make_request_with_retry(
                f"{self.config['api_base']}/services/aigc/text-generation/generation",
                headers=headers,
                data=data,
                timeout=timeout_config
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["output"]["text"]
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"生成回复时出现错误: {str(e)}"

class GLMService(BaseAIService):
    """智谱AI服务"""
    
    def __init__(self, api_key: str):
        super().__init__(AIModel.GLM, api_key)
        self.model_name = "glm-4"
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """调用智谱AI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name if hasattr(self, 'model_name') else "deepseek-chat",
                "messages": messages,
                "max_tokens": self.config["max_tokens"],
                "temperature": self.config["temperature"],
                "stream": False
            }
            
            # 设置更长的超时时间：(连接超时, 读取超时)
            timeout_config = (15, 120)  # 15秒连接，120秒读取
            
            response = self._make_request_with_retry(
                f"{self.config['api_base']}/chat/completions",
                headers=headers,
                data=data,
                timeout=timeout_config
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"API调用失败: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"生成回复时出现错误: {str(e)}"

class AIServiceFactory:
    """AI服务工厂"""
    
    @staticmethod
    def create_service(model: str, api_key: str) -> BaseAIService:
        """创建AI服务实例"""
        # 根据模型名称判断提供商
        if model.startswith('deepseek'):
            return DeepSeekService(api_key)
        elif model.startswith('qwen'):
            return QwenService(api_key)
        elif model.startswith('glm') or model.startswith('cogview'):
            return GLMService(api_key)
        else:
            raise ValueError(f"不支持的模型: {model}")
    
    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """获取可用模型列表"""
        return AIConfig.get_available_models()
