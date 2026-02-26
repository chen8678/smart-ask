from rest_framework import serializers
from .models import KnowledgeBase, Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'content_type', 'file_path', 'metadata', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'title', 'description', 'category', 'settings', 'status', 'document_count', 'documents', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        return obj.documents.count()

class KnowledgeBaseListSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'title', 'description', 'category', 'status', 'document_count', 'created_at', 'updated_at']
    
    def get_document_count(self, obj):
        return obj.documents.count()

class DocumentCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    title = serializers.CharField(required=False, write_only=True)
    content = serializers.CharField(required=False, write_only=True)
    content_type = serializers.CharField(required=False, write_only=True)
    file_path = serializers.CharField(required=False, write_only=True)
    metadata = serializers.JSONField(required=False, write_only=True)
    
    class Meta:
        model = Document
        fields = ['file', 'title', 'content', 'content_type', 'file_path', 'metadata']
    
    def create(self, validated_data):
        knowledge_base_id = self.context['knowledge_base_id']
        file = validated_data.pop('file')
        
        # 处理文件上传
        validated_data['title'] = file.name
        validated_data['file_path'] = file.name
        validated_data['content_type'] = file.content_type or 'text/plain'
        
        # 读取文件内容
        file.seek(0)  # 重置文件指针
        try:
            # 尝试读取文本内容
            content = file.read().decode('utf-8')
            validated_data['content'] = content
        except UnicodeDecodeError:
            # 如果不是文本文件，保存基本信息
            validated_data['content'] = f"文件: {file.name}"
        
        # 获取知识库对象
        from .models import KnowledgeBase
        knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id)
        validated_data['knowledge_base'] = knowledge_base
        
        return super().create(validated_data)
