"""
AI模型配置
"""
import os
from enum import Enum
from typing import Dict, Any

class AIModel(Enum):
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    GLM = "glm"
    ZHIPU = "zhipu"

class AIConfig:
    """AI模型配置类"""
    
    # 提供商配置
    PROVIDERS = {
        "deepseek": {
            "name": "DeepSeek",
            "api_base": "https://api.deepseek.com/v1",
            "models": {
                "deepseek-chat": {"name": "DeepSeek Chat", "version": "V1"},
                "deepseek-coder": {"name": "DeepSeek Coder", "version": "V1.5"},
                "deepseek-reasoner": {"name": "DeepSeek R1", "version": "R1"},
                "deepseek-v3": {"name": "DeepSeek V3", "version": "V3"}
            },
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 120,
            "connect_timeout": 15
        },
        "qwen": {
            "name": "通义千问",
            "api_base": "https://dashscope.aliyuncs.com/api/v1",
            "models": {
                "qwen-max": {"name": "通义千问-Max", "version": "Max"},
                "qwen-plus": {"name": "通义千问-Plus", "version": "Plus"},
                "qwen-turbo": {"name": "通义千问-Turbo", "version": "Turbo"},
                "qwen-long": {"name": "通义千问-Long", "version": "Long"}
            },
            "max_tokens": 2000,
            "temperature": 0.7,
            "timeout": 120,
            "connect_timeout": 15
        },
        "glm": {
            "name": "智谱AI",
            "api_base": "https://open.bigmodel.cn/api/paas/v4",
            "models": {
                "glm-4": {"name": "GLM-4", "version": "V4"},
                "glm-4v": {"name": "GLM-4V", "version": "V4V"},
                "glm-3-turbo": {"name": "GLM-3 Turbo", "version": "V3"},
                "cogview-3": {"name": "CogView-3", "version": "V3"}
            },
            "max_tokens": 2000,
            "temperature": 0.7,
            "timeout": 120,
            "connect_timeout": 15
        }
    }
    
    # 兼容旧版本
    MODELS = {
        AIModel.DEEPSEEK: PROVIDERS["deepseek"],
        AIModel.QWEN: PROVIDERS["qwen"],
        AIModel.GLM: PROVIDERS["glm"],
        AIModel.ZHIPU: PROVIDERS["glm"]
    }
    
    @classmethod
    def get_model_config(cls, model: AIModel) -> Dict[str, Any]:
        """获取模型配置"""
        return cls.MODELS.get(model, cls.MODELS[AIModel.DEEPSEEK])
    
    @classmethod
    def get_providers(cls) -> list:
        """获取所有提供商列表"""
        providers = []
        
        # 从数据库获取API Key配置
        db_api_keys = {}
        try:
            from apps.system.models import APIKeyConfig
            for config in APIKeyConfig.objects.filter(is_active=True):
                db_api_keys[config.provider] = {
                    'api_key': config.api_key,
                    'is_valid': config.is_valid,
                    'last_tested': config.last_tested
                }
        except Exception as e:
            print(f"从数据库获取API Key配置失败: {e}")
        
        for provider_key, provider in cls.PROVIDERS.items():
            available = False
            api_key = None
            
            # 优先使用数据库中的配置
            if provider_key in db_api_keys:
                db_config = db_api_keys[provider_key]
                api_key = db_config['api_key']
                available = db_config['is_valid']
            else:
                # 回退到环境变量
                api_key = os.getenv(f"{provider_key.upper()}_API_KEY")
                if api_key and api_key != 'sk-test-key-for-development':
                    test_result = cls.test_api_key(provider_key, api_key)
                    available = test_result.get('success', False)
            
            # 获取完整的模型信息
            models = cls.get_provider_models(provider_key)
            
            providers.append({
                "key": provider_key,
                "name": provider["name"],
                "api_base": provider["api_base"],
                "available": available,
                "api_key": api_key,
                "models": models
            })
        
        return providers
    
    @classmethod
    def get_provider_models(cls, provider_key: str) -> list:
        """获取指定提供商的所有模型"""
        if provider_key not in cls.PROVIDERS:
            return []
        
        provider = cls.PROVIDERS[provider_key]
        return [
            {
                "key": model_key,
                "name": model_info["name"],
                "version": model_info["version"],
                "provider": provider_key
            }
            for model_key, model_info in provider["models"].items()
        ]
    
    @classmethod
    def test_api_key(cls, provider_key: str, api_key: str) -> dict:
        """测试API Key是否有效"""
        if provider_key not in cls.PROVIDERS:
            return {"success": False, "error": "不支持的提供商"}
        
        provider = cls.PROVIDERS[provider_key]
        
        # 调用实际的API测试
        try:
            import requests
            import json
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 根据不同的提供商使用不同的测试端点
            if provider_key == 'deepseek':
                test_url = "https://api.deepseek.com/v1/chat/completions"
                test_data = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
            elif provider_key == 'qwen':
                test_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                test_data = {
                    "model": "qwen-turbo",
                    "input": {"messages": [{"role": "user", "content": "Hello"}]},
                    "parameters": {"max_tokens": 10}
                }
            elif provider_key == 'glm':
                test_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                test_data = {
                    "model": "glm-4",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
            else:
                return {"success": False, "error": "不支持的提供商"}
            
            response = requests.post(test_url, headers=headers, json=test_data, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "provider": provider["name"],
                    "available_models": list(provider["models"].keys())
                }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"连接失败: {str(e)}"
            }
    
    @classmethod
    def update_provider_api_key(cls, provider_key: str, api_key: str) -> bool:
        """更新提供商的API Key"""
        try:
            if provider_key not in cls.PROVIDERS:
                return False
            
            # 更新环境变量
            env_key = f"{provider_key.upper()}_API_KEY"
            os.environ[env_key] = api_key
            
            # 更新AI引擎配置
            from ai_qa_system.settings import AI_ENGINE_CONFIG
            if provider_key in AI_ENGINE_CONFIG:
                AI_ENGINE_CONFIG[provider_key]['api_key'] = api_key
            
            return True
        except Exception as e:
            print(f"更新API Key失败: {e}")
            return False
    
    @classmethod
    def get_available_models(cls) -> list:
        """获取可用模型列表（兼容旧版本）"""
        return [
            {
                "value": model.value,
                "label": config["name"],
                "available": bool(os.getenv(f"{model.value.upper()}_API_KEY")),
                "provider": config["name"],
                "version": "Default"
            }
            for model, config in cls.MODELS.items()
        ]
