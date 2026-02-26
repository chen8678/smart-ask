from rest_framework import serializers
from .models import QARecord, ChatSession

class QARecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = QARecord
        fields = ['id', 'question', 'answer', 'knowledge_sources', 'confidence_score', 'feedback', 'created_at', 'message_type', 'message_order']
        read_only_fields = ['id', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = QARecordSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'knowledge_base', 'created_at', 'last_activity', 'is_active', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'last_activity']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class ChatSessionListSerializer(serializers.ModelSerializer):
    """简化的会话列表序列化器"""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'last_activity', 'is_active', 'message_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'last_activity']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'question': last_msg.question[:100] + '...' if len(last_msg.question) > 100 else last_msg.question,
                'created_at': last_msg.created_at
            }
        return None
