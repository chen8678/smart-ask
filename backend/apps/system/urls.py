"""
系统管理URL配置
"""
from django.urls import path
from . import views
from . import health_views

urlpatterns = [
    # AI模型配置管理
    path('ai-models/', views.ai_model_config_list, name='ai-model-config-list'),
    path('ai-models/<uuid:pk>/', views.ai_model_config_detail, name='ai-model-config-detail'),
    path('ai-models/<uuid:pk>/test/', views.test_ai_model, name='test-ai-model'),
    path('ai-models/test-generation/', views.test_ai_generation, name='test-ai-generation'),
    path('ai-models/batch-test/', views.batch_test_ai_models, name='batch-test-ai-models'),
    
    # 系统设置管理
    path('settings/', views.system_settings_list, name='system-settings-list'),
    path('settings/<uuid:pk>/', views.system_setting_detail, name='system-setting-detail'),
    
    # API日志管理
    path('logs/', views.api_logs_list, name='api-logs-list'),
    path('logs/stats/', views.api_logs_stats, name='api-logs-stats'),
    
    # 系统统计
    path('stats/', views.system_stats, name='system-stats'),
    
    # 系统操作
    path('refresh-cache/', views.refresh_ai_engine_cache, name='refresh-ai-engine-cache'),
    
    # 健康检查
    path('health/', health_views.health_check, name='health-check'),
]
