"""
系统管理序列化器
"""
from rest_framework import serializers
from .models import AIModelConfig, SystemSetting, APILog


class AIModelConfigSerializer(serializers.ModelSerializer):
    """AI模型配置序列化器"""
    is_available_display = serializers.SerializerMethodField()
    last_checked_display = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = AIModelConfig
        fields = [
            'id', 'model_id', 'model_name', 'provider', 'api_key', 'base_url',
            'model_version', 'max_tokens', 'temperature', 'is_active', 'is_available',
            'is_available_display', 'last_checked', 'last_checked_display', 'error_message',
            'supported_content_types', 'config_data', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_available', 'last_checked']
    
    def get_is_available_display(self, obj):
        """获取可用状态显示"""
        if obj.is_available:
            return '可用'
        elif obj.error_message:
            return f'错误: {obj.error_message[:50]}...'
        else:
            return '未知'
    
    def get_last_checked_display(self, obj):
        """获取最后检查时间显示"""
        if obj.last_checked:
            return obj.last_checked.strftime('%Y-%m-%d %H:%M:%S')
        return '从未检查'


class AIModelConfigCreateSerializer(serializers.ModelSerializer):
    """AI模型配置创建序列化器"""
    
    class Meta:
        model = AIModelConfig
        fields = [
            'model_id', 'model_name', 'provider', 'api_key', 'base_url',
            'model_version', 'max_tokens', 'temperature', 'is_active',
            'supported_content_types', 'config_data'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SystemSettingSerializer(serializers.ModelSerializer):
    """系统设置序列化器"""
    setting_type_display = serializers.CharField(source='get_setting_type_display', read_only=True)
    
    class Meta:
        model = SystemSetting
        fields = [
            'id', 'key', 'value', 'setting_type', 'setting_type_display',
            'description', 'is_encrypted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class APILogSerializer(serializers.ModelSerializer):
    """API日志序列化器"""
    log_type_display = serializers.CharField(source='get_log_type_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    created_at_display = serializers.SerializerMethodField()
    
    class Meta:
        model = APILog
        fields = [
            'id', 'log_type', 'log_type_display', 'model_id', 'username',
            'status_code', 'duration', 'tokens_used', 'error_message',
            'ip_address', 'created_at', 'created_at_display'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_created_at_display(self, obj):
        """获取创建时间显示"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')


class AIModelTestSerializer(serializers.Serializer):
    """AI模型测试序列化器"""
    model_id = serializers.CharField(max_length=50)
    test_content = serializers.CharField(default="Hello, this is a test message.")
    content_type = serializers.ChoiceField(
        choices=[
            ('summary', '内容总结'),
            ('outline', '学习大纲'),
            ('key_concepts', '关键概念'),
            ('q_and_a', '问答集'),
        ],
        default='summary'
    )


class SystemStatsSerializer(serializers.Serializer):
    """系统统计序列化器"""
    total_ai_models = serializers.IntegerField()
    active_ai_models = serializers.IntegerField()
    available_ai_models = serializers.IntegerField()
    total_api_calls = serializers.IntegerField()
    total_tokens_used = serializers.IntegerField()
    error_rate = serializers.FloatField()
    avg_response_time = serializers.FloatField()
    recent_errors = serializers.ListField(child=serializers.DictField())
