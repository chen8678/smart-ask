"""
聊天管理Admin配置
"""
from django.contrib import admin
from .models import ChatSession, QARecord


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """聊天会话管理"""
    list_display = ('id', 'user', 'knowledge_base', 'title', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'created_at', 'knowledge_base__category')
    search_fields = ('title', 'user__username', 'user__email', 'knowledge_base__title')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'last_activity')


@admin.register(QARecord)
class QARecordAdmin(admin.ModelAdmin):
    """问答记录管理"""
    list_display = ('session', 'message_type', 'content_preview', 'created_at')
    list_filter = ('message_type', 'created_at', 'session__knowledge_base')
    search_fields = ('content', 'session__title', 'session__user__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    
    def content_preview(self, obj):
        """内容预览"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = '内容预览'
