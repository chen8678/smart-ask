"""
系统管理模型
用于存储AI模型配置、系统设置等
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()


class AIModelConfig(models.Model):
    """AI模型配置"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_id = models.CharField(max_length=50, unique=True, help_text='模型ID')
    model_name = models.CharField(max_length=100, help_text='模型显示名称')
    provider = models.CharField(max_length=50, help_text='提供商')
    api_key = models.TextField(help_text='API密钥（加密存储）')
    base_url = models.URLField(help_text='API基础URL')
    model_version = models.CharField(max_length=50, default='', help_text='模型版本')
    max_tokens = models.IntegerField(default=2000, help_text='最大token数')
    temperature = models.FloatField(default=0.7, help_text='默认温度参数')
    is_active = models.BooleanField(default=True, help_text='是否启用')
    is_available = models.BooleanField(default=False, help_text='是否可用')
    last_checked = models.DateTimeField(null=True, blank=True, help_text='最后检查时间')
    error_message = models.TextField(blank=True, help_text='错误信息')
    supported_content_types = models.JSONField(default=list, help_text='支持的内容类型')
    config_data = models.JSONField(default=dict, help_text='额外配置数据')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_ai_models')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_model_configs'
        verbose_name = 'AI模型配置'
        verbose_name_plural = 'AI模型配置'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_name} ({self.provider})"

    def get_encrypted_api_key(self):
        """获取加密的API密钥"""
        # 这里应该实现真正的加密逻辑
        return self.api_key

    def set_encrypted_api_key(self, api_key):
        """设置加密的API密钥"""
        # 这里应该实现真正的加密逻辑
        self.api_key = api_key

    def test_connection(self):
        """测试API连接"""
        try:
            # 直接测试API连接，不依赖工厂
            import requests
            import json
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 根据提供商选择不同的测试数据
            if self.provider.lower() == 'deepseek':
                test_data = {
                    "model": self.model_version or "deepseek-chat",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                test_url = self.base_url
            elif self.provider.lower() == 'qwen':
                test_data = {
                    "model": self.model_version or "qwen-turbo",
                    "input": {"messages": [{"role": "user", "content": "Hello"}]},
                    "parameters": {"max_tokens": 10}
                }
                test_url = self.base_url
            elif self.provider.lower() == 'glm':
                test_data = {
                    "model": self.model_version or "glm-4",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                test_url = self.base_url
            else:
                # 通用测试
                test_data = {
                    "model": self.model_version or "test",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                test_url = self.base_url
            
            response = requests.post(
                test_url,
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.is_available = True
                self.error_message = ''
            else:
                self.is_available = False
                self.error_message = f'API调用失败: {response.status_code} - {response.text[:200]}'
                
        except requests.exceptions.Timeout:
            self.is_available = False
            self.error_message = '连接超时'
        except requests.exceptions.ConnectionError:
            self.is_available = False
            self.error_message = '连接失败，请检查网络或API地址'
        except Exception as e:
            self.is_available = False
            self.error_message = f'测试失败: {str(e)}'
        finally:
            from django.utils import timezone
            self.last_checked = timezone.now()
            self.save()


class SystemSetting(models.Model):
    """系统设置"""
    SETTING_TYPES = [
        ('ai', 'AI配置'),
        ('system', '系统配置'),
        ('security', '安全配置'),
        ('ui', '界面配置'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, help_text='设置键')
    value = models.TextField(help_text='设置值')
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='system')
    description = models.TextField(blank=True, help_text='设置描述')
    is_encrypted = models.BooleanField(default=False, help_text='是否加密存储')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_settings'
        verbose_name = '系统设置'
        verbose_name_plural = '系统设置'

    def __str__(self):
        return f"{self.key} ({self.get_setting_type_display()})"

    @classmethod
    def get_setting(cls, key, default=None):
        """获取设置值"""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_setting(cls, key, value, setting_type='system', description='', is_encrypted=False):
        """设置值"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={
                'value': value,
                'setting_type': setting_type,
                'description': description,
                'is_encrypted': is_encrypted
            }
        )
        if not created:
            setting.value = value
            setting.setting_type = setting_type
            setting.description = description
            setting.is_encrypted = is_encrypted
            setting.save()
        return setting


class APIKeyConfig(models.Model):
    """API Key配置"""
    PROVIDER_CHOICES = [
        ('deepseek', 'DeepSeek'),
        ('qwen', '通义千问'),
        ('glm', '智谱AI'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, unique=True, help_text='提供商')
    api_key = models.TextField(help_text='API密钥')
    is_active = models.BooleanField(default=True, help_text='是否启用')
    last_tested = models.DateTimeField(null=True, blank=True, help_text='最后测试时间')
    is_valid = models.BooleanField(default=False, help_text='是否有效')
    error_message = models.TextField(blank=True, help_text='错误信息')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_api_keys')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_key_configs'
        verbose_name = 'API Key配置'
        verbose_name_plural = 'API Key配置'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_provider_display()} - {'有效' if self.is_valid else '无效'}"

    def test_api_key(self):
        """测试API Key"""
        from apps.chat.api_config_service import APIConfigService
        result = APIConfigService.test_api_key(self.provider, self.api_key)
        self.is_valid = result.get('success', False)
        self.error_message = result.get('error', '') if not self.is_valid else ''
        from django.utils import timezone
        self.last_tested = timezone.now()
        self.save()
        return result


class APILog(models.Model):
    """API调用日志"""
    LOG_TYPES = [
        ('ai_generation', 'AI内容生成'),
        ('ai_query', 'AI查询'),
        ('system', '系统调用'),
        ('error', '错误日志'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default='ai_generation')
    model_id = models.CharField(max_length=50, blank=True, help_text='使用的AI模型')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    request_data = models.JSONField(default=dict, help_text='请求数据')
    response_data = models.JSONField(default=dict, help_text='响应数据')
    status_code = models.IntegerField(default=200, help_text='状态码')
    duration = models.FloatField(default=0.0, help_text='耗时（秒）')
    tokens_used = models.IntegerField(default=0, help_text='使用的token数')
    error_message = models.TextField(blank=True, help_text='错误信息')
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text='IP地址')
    user_agent = models.TextField(blank=True, help_text='用户代理')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_logs'
        verbose_name = 'API日志'
        verbose_name_plural = 'API日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_log_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
