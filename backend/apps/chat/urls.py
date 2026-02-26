from django.urls import path
from . import views
from . import simple_query
from . import voice_qa

urlpatterns = [
    # 简单查询接口（FastGPT式）
    path('simple-query/', simple_query.simple_query, name='simple-query'),
    
    # 语音问答接口
    path('voice/stt/', voice_qa.voice_to_text, name='voice-to-text'),
    path('voice/tts/', voice_qa.text_to_voice, name='text-to-voice'),
    path('voice/qa/', voice_qa.voice_qa, name='voice-qa'),
    
    # 问答相关
    path('ask/', views.ask_question, name='ask-question'),
    path('models/', views.available_models, name='available-models'),
    
    # API配置管理
    path('providers/', views.providers, name='providers'),
    path('providers/<str:provider_key>/models/', views.provider_models, name='provider-models'),
    path('test-api-key/', views.test_api_key, name='test-api-key'),
    path('save-api-key/', views.save_api_key, name='save-api-key'),
    path('configured-providers/', views.configured_providers, name='configured-providers'),
    
    # 会话管理
    path('sessions/', views.chat_sessions, name='chat-sessions'),
    path('sessions/create/', views.create_session, name='create-session'),
    path('sessions/<uuid:session_id>/', views.chat_session_detail, name='session-detail'),
    path('sessions/<uuid:session_id>/delete/', views.delete_session, name='delete-session'),
    
    # 仪表板统计
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    
    # 向后兼容
    path('history/', views.chat_history, name='chat-history'),
    path('feedback/', views.submit_feedback, name='submit-feedback'),
]
