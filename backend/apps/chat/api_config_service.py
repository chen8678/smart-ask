"""
API Key配置和测试服务
"""
import os
import requests
import json
from typing import Dict, Any, List
from ai_qa_system.ai_config import AIConfig

class APIConfigService:
    """API配置服务"""
    
    @staticmethod
    def test_deepseek_api(api_key: str) -> Dict[str, Any]:
        """测试DeepSeek API Key"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "provider": "DeepSeek",
                    "available_models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner", "deepseek-v3"]
                }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"连接失败: {str(e)}"
            }
    
    @staticmethod
    def test_qwen_api(api_key: str) -> Dict[str, Any]:
        """测试通义千问API Key"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-turbo",
                "input": {
                    "messages": [{"role": "user", "content": "Hello"}]
                },
                "parameters": {
                    "max_tokens": 10
                }
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "provider": "通义千问",
                    "available_models": ["qwen-max", "qwen-plus", "qwen-turbo", "qwen-long"]
                }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"连接失败: {str(e)}"
            }
    
    @staticmethod
    def test_glm_api(api_key: str) -> Dict[str, Any]:
        """测试智谱AI API Key"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "glm-4",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "provider": "智谱AI",
                    "available_models": ["glm-4", "glm-4v", "glm-3-turbo", "cogview-3"]
                }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"连接失败: {str(e)}"
            }
    
    @classmethod
    def test_api_key(cls, provider_key: str, api_key: str) -> Dict[str, Any]:
        """测试API Key"""
        if provider_key == "deepseek":
            return cls.test_deepseek_api(api_key)
        elif provider_key == "qwen":
            return cls.test_qwen_api(api_key)
        elif provider_key == "glm":
            return cls.test_glm_api(api_key)
        else:
            return {
                "success": False,
                "error": "不支持的提供商"
            }
    
    @classmethod
    def save_api_key(cls, provider_key: str, api_key: str) -> bool:
        """保存API Key到数据库和环境变量"""
        try:
            from apps.system.models import APIKeyConfig
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # 先测试API Key
            test_result = cls.test_api_key(provider_key, api_key)
            
            # 保存到数据库（无论测试是否成功都保存）
            config, created = APIKeyConfig.objects.get_or_create(
                provider=provider_key,
                defaults={
                    'api_key': api_key,
                    'is_active': True,
                    'is_valid': test_result.get('success', False),
                    'error_message': test_result.get('error', '') if not test_result.get('success', False) else ''
                }
            )
            
            if not created:
                config.api_key = api_key
                config.is_active = True
                config.is_valid = test_result.get('success', False)
                config.error_message = test_result.get('error', '') if not test_result.get('success', False) else ''
                config.save()
            
            # 更新AI引擎配置
            from ai_qa_system.ai_config import AIConfig
            AIConfig.update_provider_api_key(provider_key, api_key)
            
            # 清除学习内容生成器的AI引擎工厂缓存
            try:
                from apps.learning.ai_engines.engine_factory import clear_ai_engine_factory
                clear_ai_engine_factory()
            except Exception as e:
                print(f"清除AI引擎工厂缓存失败: {e}")
            
            return test_result.get('success', False)
        except Exception as e:
            print(f"保存API Key失败: {e}")
            return False
    
    @classmethod
    def get_configured_providers(cls) -> List[Dict[str, Any]]:
        """获取已配置的提供商"""
        providers = AIConfig.get_providers()
        configured = []
        
        for provider in providers:
            if provider["available"]:
                models = AIConfig.get_provider_models(provider["key"])
                configured.append({
                    "provider": provider,
                    "models": models
                })
        
        return configured
