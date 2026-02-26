from django.db import models
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField
from django.conf import settings
from django.utils import timezone
import uuid

class KnowledgeBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, default='general', choices=[
        ('general', '通用'),
        ('legal', '法律'),
        ('education', '教育'),
        ('healthcare', '医疗健康'),
        ('finance', '金融'),
        ('technology', '技术'),
        ('business', '商业'),
        ('science', '科学'),
        ('humanities', '人文社科'),
        ('engineering', '工程'),
        ('arts', '艺术设计'),
        ('other', '其他'),
    ])
    settings = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', '活跃'),
        ('inactive', '非活跃'),
        ('archived', '已归档'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'knowledge_bases'
        verbose_name = '知识库'
        verbose_name_plural = '知识库'

    def __str__(self):
        return self.title

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_type = models.CharField(max_length=20, default='text', choices=[
        ('text', '文本'),
        ('code', '代码'),
        ('image', '图像'),
        ('pdf', 'PDF'),
        ('markdown', 'Markdown'),
    ])
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text='文件大小（字节）')
    metadata = models.JSONField(default=dict, blank=True)
    vector_embedding = VectorField(dimensions=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        verbose_name = '文档'
        verbose_name_plural = '文档'

    def __str__(self):
        return self.title


class ImportJob(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', '待处理'
        PROCESSING = 'PROCESSING', '处理中'
        SUCCEEDED = 'SUCCEEDED', '成功'
        FAILED = 'FAILED', '失败'
        CANCELED = 'CANCELED', '已取消'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    knowledge_base = models.ForeignKey(KnowledgeBase, related_name='import_jobs', on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    file_path = models.CharField(max_length=500)
    original_filename = models.CharField(max_length=255, blank=True)
    total_documents = models.PositiveIntegerField(default=0)
    created_documents = models.PositiveIntegerField(default=0)
    vectorized_documents = models.PositiveIntegerField(default=0)
    skipped_documents = models.PositiveIntegerField(default=0)
    skipped_samples = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'knowledge_import_jobs'
        ordering = ['-created_at']

    def mark_processing(self):
        self.status = self.Status.PROCESSING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_failed(self, error_message: str):
        self.status = self.Status.FAILED
        self.error_message = error_message[:2000] if error_message else ''
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'finished_at'])

    def mark_succeeded(self):
        self.status = self.Status.SUCCEEDED
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'finished_at'])

    def mark_canceled(self, reason: str = ''):
        self.status = self.Status.CANCELED
        if reason:
            self.error_message = reason[:2000]
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'finished_at'])

    def update_progress(self, created: int, vectorized: int, skipped: int, samples: list):
        self.created_documents = created
        self.vectorized_documents = vectorized
        self.skipped_documents = skipped
        if samples is not None:
            self.skipped_samples = samples[:10]
        self.save(update_fields=['created_documents', 'vectorized_documents', 'skipped_documents', 'skipped_samples'])

    @property
    def is_final(self) -> bool:
        return self.status in {self.Status.SUCCEEDED, self.Status.FAILED, self.Status.CANCELED}
