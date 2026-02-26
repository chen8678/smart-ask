"""
知识库管理Admin配置
"""
from django.contrib import admin
from .models import KnowledgeBase, Document


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    """知识库管理"""
    list_display = ('title', 'owner', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('title', 'description', 'owner')}),
        ('分类设置', {'fields': ('category', 'status')}),
        ('配置', {'fields': ('settings',)}),
        ('时间信息', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """文档管理"""
    list_display = ('title', 'knowledge_base', 'content_type', 'file_size', 'created_at')
    list_filter = ('content_type', 'created_at', 'knowledge_base__category')
    search_fields = ('title', 'content', 'knowledge_base__title', 'knowledge_base__owner__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'file_size')
    
    fieldsets = (
        (None, {'fields': ('title', 'knowledge_base', 'content')}),
        ('文件信息', {'fields': ('content_type', 'file_size', 'file_path')}),
        ('元数据', {'fields': ('metadata',)}),
        ('时间信息', {'fields': ('created_at',)}),
    )


