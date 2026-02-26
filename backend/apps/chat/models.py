from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

class ChatSession(models.Model):
    """聊天会话模型 - 类似NotebookLM的会话概念"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    knowledge_base = models.ForeignKey('knowledge.KnowledgeBase', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)  # 会话标题
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_sessions'
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username}: {self.title or 'Untitled Session'}"

class QARecord(models.Model):
    """问答记录模型 - 临时存储，定期清理"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # 保持向后兼容
    question = models.TextField()
    answer = models.TextField(blank=True)
    knowledge_sources = models.JSONField(default=list, blank=True)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    feedback = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 添加消息类型和顺序
    message_type = models.CharField(max_length=20, choices=[
        ('user', '用户消息'),
        ('assistant', '助手回复'),
        ('system', '系统消息')
    ], default='user')
    message_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'qa_records'
        verbose_name = '问答记录'
        verbose_name_plural = '问答记录'
        ordering = ['session', 'message_order']

    def __str__(self):
        return f"{self.session}: {self.question[:50]}..."

    @classmethod
    def cleanup_old_records(cls, days=7):
        """清理超过指定天数的记录"""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_records = cls.objects.filter(created_at__lt=cutoff_date)
        count = old_records.count()
        old_records.delete()
        return count

    @classmethod
    def cleanup_inactive_sessions(cls, days=30):
        """清理不活跃的会话"""
        cutoff_date = timezone.now() - timedelta(days=days)
        inactive_sessions = ChatSession.objects.filter(
            last_activity__lt=cutoff_date,
            is_active=True
        )
        count = inactive_sessions.count()
        inactive_sessions.update(is_active=False)
        return count
