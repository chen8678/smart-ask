"""
系统管理Admin配置
"""
from django.contrib import admin
from .models import AIModelConfig, SystemSetting, APILog


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    """AI模型配置管理"""
    list_display = ('model_name', 'provider', 'model_version', 'is_active', 'is_available', 'created_at')
    list_filter = ('provider', 'is_active', 'is_available', 'created_at')
    search_fields = ('model_id', 'model_name', 'provider')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_checked')
    
    fieldsets = (
        (None, {'fields': ('model_id', 'model_name', 'provider')}),
        ('API配置', {'fields': ('api_key', 'base_url', 'model_version')}),
        ('参数设置', {'fields': ('max_tokens', 'temperature', 'supported_content_types')}),
        ('状态', {'fields': ('is_active', 'is_available', 'last_checked', 'error_message')}),
        ('配置数据', {'fields': ('config_data',)}),
        ('创建信息', {'fields': ('created_by', 'created_at', 'updated_at')}),
    )


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """系统设置管理"""
    list_display = ('key', 'setting_type', 'is_encrypted', 'created_at')
    list_filter = ('setting_type', 'is_encrypted', 'created_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    """API日志管理"""
    list_display = ('user', 'log_type', 'model_id', 'status_code', 'created_at')
    list_filter = ('log_type', 'status_code', 'created_at')
    search_fields = ('user__username', 'model_id', 'request_data', 'response_data')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    
    def has_add_permission(self, request):
        """禁止手动添加API日志"""
        return False
