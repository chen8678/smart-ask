"""
简单的FastGPT式查询接口 - 最简化版本
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import QAService
from apps.knowledge.models import KnowledgeBase


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simple_query(request):
    """
    简单的知识库查询接口
    
    请求格式：
    {
        "question": "BIM里规划的塔吊安全距离是多少？",
        "knowledge_base_id": "知识库ID（可选）"
    }
    
    返回格式：
    {
        "answer": "专业答案...",
        "sources": ["文档1", "文档2"],
        "from_private_kb": true,
        "question": "用户问题"
    }
    """
    question = request.data.get('question', '').strip()
    
    if not question:
        return Response(
            {'error': '请提供问题'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 获取知识库ID（如果提供）
    knowledge_base_id = request.data.get('knowledge_base_id')
    
    # 如果没有提供知识库ID，使用用户的第一个知识库
    if not knowledge_base_id:
        user_kb = KnowledgeBase.objects.filter(owner=request.user).first()
        if not user_kb:
            return Response(
                {'error': '请先创建知识库并上传文档'},
                status=status.HTTP_400_BAD_REQUEST
            )
        knowledge_base_id = str(user_kb.id)
    
    # 使用现有的QAService
    qa_service = QAService(model='deepseek-chat')
    
    try:
        # 查询答案
        result = qa_service.ask_question(
            question=question,
            knowledge_base_id=knowledge_base_id,
            user=request.user
        )
        
        # 返回简化格式
        return Response({
            'answer': result.get('answer', ''),
            'sources': result.get('sources', []),
            'from_private_kb': True,
            'question': question
        })
        
    except Exception as e:
        return Response(
            {'error': f'查询失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

