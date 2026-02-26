from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import QARecord, ChatSession
from .services import QAService
from .ai_services import AIModel, AIServiceFactory
from .api_config_service import APIConfigService
from ai_qa_system.ai_config import AIConfig
from .serializers import QARecordSerializer, ChatSessionSerializer, ChatSessionListSerializer
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_question(request):
    """发送问题"""
    print(f"收到请求数据: {request.data}")
    
    question = request.data.get('question')
    knowledge_base_id = request.data.get('knowledge_base_id')
    session_id = request.data.get('session_id')  # 可选的会话ID
    model_name = request.data.get('model', 'deepseek')
    # 检索策略（与 preview-retrieval 一致，可选）
    strategy = request.data.get('strategy', 'hybrid')
    top_k = request.data.get('top_k', 5)
    score_threshold = request.data.get('score_threshold', 0.15)
    alpha = request.data.get('alpha', 0.5)
    auxiliary_knowledge_base_ids = request.data.get('auxiliary_knowledge_base_ids')  # 可选辅助知识库 ID 列表
    
    print(f"解析的数据 - question: {question}, knowledge_base_id: {knowledge_base_id}, model: {model_name}")
    
    if not question or not knowledge_base_id:
        print(f"缺少必要字段 - question: {question}, knowledge_base_id: {knowledge_base_id}")
        return Response({'error': '缺少必要字段'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 模型名称映射 - 支持简化的模型名称
    model_mapping = {
        'deepseek': 'deepseek-chat',
        'qwen': 'qwen-turbo', 
        'glm': 'glm-4'
    }
    
    # 如果发送的是简化名称，映射到完整名称
    if model_name in model_mapping:
        model_name = model_mapping[model_name]
        print(f"模型名称映射: {request.data.get('model')} -> {model_name}")
    
    # 验证模型名称
    valid_models = ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner', 'deepseek-v3',
                   'qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen-long',
                   'glm-4', 'glm-4v', 'glm-3-turbo', 'cogview-3']
    
    if model_name not in valid_models:
        print(f"不支持的模型: {model_name}, 有效模型: {valid_models}")
        return Response({'error': f'不支持的模型: {model_name}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取或创建会话
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user, is_active=True)
        except ChatSession.DoesNotExist:
            return Response({'error': '会话不存在或已失效'}, status=status.HTTP_404_NOT_FOUND)
    else:
        # 创建新会话
        session = ChatSession.objects.create(
            user=request.user,
            knowledge_base_id=knowledge_base_id,
            title=question[:50] + '...' if len(question) > 50 else question
        )
    
    qa_service = QAService(model=model_name)
    
    try:
        top_k = min(20, max(1, int(top_k)))
    except (TypeError, ValueError):
        top_k = 5
    try:
        score_threshold = min(1.0, max(0.0, float(score_threshold)))
    except (TypeError, ValueError):
        score_threshold = 0.15
    try:
        alpha = min(1.0, max(0.0, float(alpha)))
    except (TypeError, ValueError):
        alpha = 0.5
    retrieval_params = {
        'strategy': strategy,
        'top_k': top_k,
        'score_threshold': score_threshold,
        'alpha': alpha,
    }
    aux_ids = None
    if auxiliary_knowledge_base_ids and isinstance(auxiliary_knowledge_base_ids, list):
        aux_ids = [str(k) for k in auxiliary_knowledge_base_ids]
    
    try:
        result = qa_service.ask_question(
            question,
            knowledge_base_id,
            request.user,
            retrieval_params=retrieval_params,
            auxiliary_knowledge_base_ids=aux_ids,
        )
        
        # 保存到会话中
        message_order = session.messages.count()
        
        # 保存用户问题
        user_message = QARecord.objects.create(
            session=session,
            question=question,
            message_type='user',
            message_order=message_order
        )
        
        # 保存AI回答
        assistant_message = QARecord.objects.create(
            session=session,
            question=question,  # 为了保持一致性
            answer=result['answer'],
            knowledge_sources=result['sources'],
            confidence_score=0.8,
            message_type='assistant',
            message_order=message_order + 1
        )
        
        # 更新会话活动时间
        session.last_activity = timezone.now()
        session.save()
        
        # 更新学习进度
        try:
            from apps.learning.services import LearningService
            learning_service = LearningService()
            learning_service.update_knowledge_learning_progress(
                user_id=request.user.id,
                knowledge_base_id=knowledge_base_id,
                activity_type='question',
                activity_data={'time_spent': 1}  # 假设每次问答1分钟
            )
            learning_service.update_knowledge_learning_progress(
                user_id=request.user.id,
                knowledge_base_id=knowledge_base_id,
                activity_type='answer',
                activity_data={'time_spent': 1}
            )
        except Exception as e:
            print(f"更新学习进度失败: {str(e)}")
        
        result['session_id'] = str(session.id)
        result['message_id'] = str(assistant_message.id)
        
        return Response(result)
    except Exception as e:
        return Response({'error': f'处理问题时出现错误：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_sessions(request):
    """获取用户的聊天会话列表"""
    sessions = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-last_activity')[:20]
    serializer = ChatSessionListSerializer(sessions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_session_detail(request, session_id):
    """获取特定会话的详细信息"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user, is_active=True)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)
    except ChatSession.DoesNotExist:
        return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session(request):
    """创建新的聊天会话"""
    knowledge_base_id = request.data.get('knowledge_base_id')
    title = request.data.get('title', '新对话')
    
    if not knowledge_base_id:
        return Response({'error': '缺少知识库ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    session = ChatSession.objects.create(
        user=request.user,
        knowledge_base_id=knowledge_base_id,
        title=title
    )
    
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_session(request, session_id):
    """删除聊天会话"""
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
        session.is_active = False
        session.save()
        return Response({'message': '会话已删除'})
    except ChatSession.DoesNotExist:
        return Response({'error': '会话不存在'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    """获取聊天历史 - 保持向后兼容"""
    # 获取最近活跃的会话
    recent_sessions = ChatSession.objects.filter(
        user=request.user, 
        is_active=True
    ).order_by('-last_activity')[:5]
    
    all_messages = []
    for session in recent_sessions:
        messages = session.messages.order_by('message_order')[:10]  # 每个会话最多10条消息
        all_messages.extend(messages)
    
    # 按时间排序并限制数量
    all_messages.sort(key=lambda x: x.created_at, reverse=True)
    all_messages = all_messages[:50]
    
    serializer = QARecordSerializer(all_messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """提交反馈"""
    qa_id = request.data.get('qa_id')
    feedback = request.data.get('feedback')
    
    if not qa_id or not feedback:
        return Response({'error': '缺少必要字段'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        qa_record = QARecord.objects.get(id=qa_id, user=request.user)
        qa_record.feedback = feedback
        qa_record.save()
        return Response({'message': '反馈提交成功'})
    except QARecord.DoesNotExist:
        return Response({'error': '问答记录不存在'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_models(request):
    """获取可用的AI模型列表"""
    models = AIServiceFactory.get_available_models()
    return Response(models)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def providers(request):
    """获取所有提供商列表"""
    providers = AIConfig.get_providers()
    return Response(providers)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_models(request, provider_key):
    """获取指定提供商的所有模型"""
    models = AIConfig.get_provider_models(provider_key)
    return Response(models)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_api_key(request):
    """测试API Key"""
    provider_key = request.data.get('provider_key')
    api_key = request.data.get('api_key')
    
    if not provider_key or not api_key:
        return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    result = APIConfigService.test_api_key(provider_key, api_key)
    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_api_key(request):
    """保存API Key"""
    provider_key = request.data.get('provider_key')
    api_key = request.data.get('api_key')
    
    if not provider_key or not api_key:
        return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 保存API Key（包含测试）
    success = APIConfigService.save_api_key(provider_key, api_key)
    
    if success:
        return Response({'message': 'API Key保存成功'})
    else:
        # 即使测试失败，也返回成功，但包含错误信息
        return Response({
            'message': 'API Key已保存，但测试失败',
            'error': 'API Key测试失败，请检查密钥是否正确'
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def configured_providers(request):
    """获取已配置的提供商和模型"""
    providers = APIConfigService.get_configured_providers()
    return Response(providers)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """获取用户仪表板统计数据"""
    from django.db.models import Count
    from apps.knowledge.models import KnowledgeBase, Document
    from apps.learning.models import LearningContent
    
    try:
        # 获取知识库数量
        knowledge_bases_count = KnowledgeBase.objects.filter(owner=request.user).count()
        
        # 获取文档数量
        documents_count = Document.objects.filter(knowledge_base__owner=request.user).count()
        
        # 获取问答次数（使用QARecord表）
        questions_count = QARecord.objects.filter(user=request.user).count()
        
        # 获取生成内容次数
        content_generated_count = LearningContent.objects.filter(
            knowledge_base__owner=request.user
        ).count()
        
        return Response({
            'knowledgeBases': knowledge_bases_count,
            'documents': documents_count,
            'questions': questions_count,
            'content_generated': content_generated_count
        })
    except Exception as e:
        return Response({
            'knowledgeBases': 0,
            'documents': 0,
            'questions': 0,
            'content_generated': 0,
            'error': str(e)
        })
