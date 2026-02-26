"""
免登录简单 API：知识库 + AI 问答（使用默认用户）
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from apps.knowledge.models import KnowledgeBase, Document
from apps.knowledge.serializers import KnowledgeBaseListSerializer, KnowledgeBaseSerializer, DocumentSerializer
from apps.knowledge.views import upload_bim as knowledge_upload_bim
from apps.chat.services import QAService
import json

User = get_user_model()

DEFAULT_USERNAME = 'default'
DEFAULT_EMAIL = 'default@local.dev'


def get_default_user():
    user, created = User.objects.get_or_create(
        username=DEFAULT_USERNAME,
        defaults={'email': DEFAULT_EMAIL, 'is_active': True}
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=['password'])
    return user


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def knowledge_list(request):
    """知识库列表 / 创建（免登录）"""
    user = get_default_user()
    if request.method == 'GET':
        qs = KnowledgeBase.objects.filter(owner=user)
        serializer = KnowledgeBaseListSerializer(qs, many=True)
        return Response(serializer.data)
    # POST
    serializer = KnowledgeBaseSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save(owner=user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def document_list(request, knowledge_base_id):
    """文档列表（免登录）"""
    user = get_default_user()
    kb = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=user)
    docs = kb.documents.all()
    serializer = DocumentSerializer(docs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def bim_upload(request, knowledge_base_id):
    """BIM 上传（免登录）。传入底层 HttpRequest，避免 DRF 对 Request 类型校验报错。"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        user = get_default_user()
        kb = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=user)
        # knowledge_upload_bim 由 @api_view 装饰，内部会要求收到 django.http.HttpRequest
        django_request = getattr(request, '_request', request)
        django_request.user = user
        return knowledge_upload_bim(django_request, knowledge_base_id)
    except Exception as e:
        logger.exception("BIM 上传失败: %s", e)
        return Response(
            {'error': f'BIM 上传失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def ask(request):
    """AI 问答（免登录）"""
    user = get_default_user()
    question = (request.data.get('question') or '').strip()
    if not question:
        return Response({'error': '请提供问题'}, status=status.HTTP_400_BAD_REQUEST)
    knowledge_base_id = request.data.get('knowledge_base_id')
    if not knowledge_base_id:
        kb = KnowledgeBase.objects.filter(owner=user).first()
        if not kb:
            return Response({'error': '请先创建知识库并上传文档'}, status=status.HTTP_400_BAD_REQUEST)
        knowledge_base_id = str(kb.id)
    qa_service = QAService(model='deepseek-chat')
    try:
        result = qa_service.ask_question(question=question, knowledge_base_id=knowledge_base_id, user=user)
        return Response({
            'answer': result.get('answer', ''),
            'sources': result.get('sources', []),
            'question': question,
        })
    except Exception as e:
        return Response({'error': f'查询失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
