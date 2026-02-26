from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
import json
from typing import Any, Dict, List, Tuple, Optional
from .models import KnowledgeBase, Document, ImportJob
from .serializers import KnowledgeBaseSerializer, KnowledgeBaseListSerializer, DocumentSerializer, DocumentCreateSerializer
from .document_analyzer import DocumentAnalyzer, DocumentRelevance
from .pdf_processor import PDFProcessor
from .docx_processor import DOCXProcessor
from .vectorization_service import VectorizationService
from .retrieval_service import AdvancedRetrievalService, RetrievalStrategyManager
from .import_utils import normalize_json_entry
from .tasks import process_import_job
from .bim_processor import bim_to_json, bim_json_to_searchable_text, bim_json_to_elements_list
from django.db.models import F

logger = logging.getLogger(__name__)


def clean_file_content(raw_content: bytes) -> bytes:
    """
    清理文件内容，移除可能导致问题的字符
    
    Args:
        raw_content: 原始文件内容（字节）
        
    Returns:
        清理后的文件内容（字节）
    """
    # 过滤掉 NUL 字符 (0x00)
    content = raw_content.replace(b'\x00', b'')
    
    # 过滤掉其他控制字符（除了常见的换行符、制表符等）
    # 保留的字符：\t (0x09), \n (0x0A), \r (0x0D)
    cleaned_bytes = bytearray()
    for byte in content:
        if byte >= 32 or byte in [9, 10, 13]:  # 可打印字符 + TAB, LF, CR
            cleaned_bytes.append(byte)
        else:
            # 替换为空格
            cleaned_bytes.append(32)
    
    return bytes(cleaned_bytes)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def knowledge_base_list(request):
    """获取知识库列表或创建知识库"""
    if request.method == 'GET':
        knowledge_bases = KnowledgeBase.objects.filter(owner=request.user)
        serializer = KnowledgeBaseListSerializer(knowledge_bases, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = KnowledgeBaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def knowledge_base_detail(request, pk):
    """获取、更新或删除知识库"""
    knowledge_base = get_object_or_404(KnowledgeBase, pk=pk, owner=request.user)
    
    if request.method == 'GET':
        serializer = KnowledgeBaseSerializer(knowledge_base)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = KnowledgeBaseSerializer(knowledge_base, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            # 按依赖顺序显式删除关联数据，避免级联顺序或 pgvector 等导致的 500
            from apps.chat.models import ChatSession
            ChatSession.objects.filter(knowledge_base_id=pk).delete()
            try:
                ImportJob.objects.filter(knowledge_base_id=pk).delete()
            except Exception:
                # 若 knowledge_import_jobs 表不存在（迁移未执行）则跳过
                pass
            knowledge_base.documents.all().delete()
            knowledge_base.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception("删除知识库失败: pk=%s", pk)
            return Response(
                {'error': f'删除知识库失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def document_list(request, knowledge_base_id):
    """获取文档列表或创建文档"""
    knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
    
    if request.method == 'GET':
        documents = knowledge_base.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # 检查是否包含文件上传
        if 'file' in request.FILES:
            return handle_document_upload(request, knowledge_base)
        else:
            # 处理文本内容上传
            serializer = DocumentCreateSerializer(data=request.data, context={'knowledge_base_id': knowledge_base_id})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def document_detail(request, knowledge_base_id, pk):
    """获取、更新或删除文档"""
    knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
    document = get_object_or_404(Document, pk=pk, knowledge_base=knowledge_base)
    
    if request.method == 'GET':
        serializer = DocumentSerializer(document)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = DocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def handle_document_upload(request, knowledge_base):
    """处理文档上传，包含智能分析"""
    try:
        # 检查文件是否存在
        if 'file' not in request.FILES:
            return Response({
                'error': '未找到上传的文件，请确保使用 multipart/form-data 格式上传'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        
        # 检查文件名
        if not uploaded_file.name:
            return Response({
                'error': '文件名不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        filename = uploaded_file.name
        
        # 检查文件大小（10MB限制）
        max_file_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_file_size:
            return Response({
                'error': f'文件大小不能超过10MB，当前文件大小：{uploaded_file.size / 1024 / 1024:.2f}MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 读取文件内容
        try:
            raw_content = uploaded_file.read()
        except Exception as e:
            logger.error(f"读取文件内容失败: {e}")
            return Response({
                'error': f'读取文件内容失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查文件是否为空
        if not raw_content or len(raw_content) == 0:
            return Response({
                'error': '文件内容为空，无法处理'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查文件类型并处理
        if PDFProcessor.is_pdf_file(raw_content):
            # 处理PDF文件
            content = PDFProcessor.extract_text_from_pdf(raw_content)
            if not content:
                return Response({
                    'error': 'PDF文件无法提取文本内容，可能是加密文件或损坏文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取PDF信息
            file_info = PDFProcessor.get_pdf_info(raw_content)
            file_type = 'pdf'
        elif DOCXProcessor.is_docx_file(raw_content):
            # 处理DOCX文件
            content = DOCXProcessor.extract_text_from_docx(raw_content)
            if not content:
                return Response({
                    'error': 'DOCX文件无法提取文本内容，可能是损坏文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取DOCX信息
            file_info = DOCXProcessor.get_docx_info(raw_content)
            file_type = 'docx'
        else:
            # 处理其他文件类型（文本文件）
            # 过滤掉问题字符
            filtered_content = clean_file_content(raw_content)
            content = filtered_content.decode('utf-8', errors='ignore')
            file_info = None
            file_type = 'text'
        
        # 使用文档分析器分析内容
        analyzer = DocumentAnalyzer()
        analysis_result = analyzer.analyze_document(content, filename)
        
        # 根据分析结果决定处理策略
        if analysis_result.relevance == DocumentRelevance.IRRELEVANT:
            return Response({
                'error': '文档内容与AI学习无关',
                'analysis': {
                    'relevance': analysis_result.relevance.value,
                    'content_type': analysis_result.content_type.value,
                    'confidence': analysis_result.confidence,
                    'quality_score': analysis_result.quality_score,
                    'issues': analysis_result.issues,
                    'suggestions': analysis_result.suggestions
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果文档质量较低，给出警告但仍允许上传
        if analysis_result.quality_score < 50:
            warning_message = f"文档质量较低（{analysis_result.quality_score:.1f}分），建议改进后再上传"
        else:
            warning_message = None
        
        # 保存文档
        document = Document.objects.create(
            knowledge_base=knowledge_base,
            title=filename,
            content=content,
            content_type=file_type,  # 使用检测到的文件类型
            file_path=filename,  # 存储文件名
            file_size=uploaded_file.size,  # 存储文件大小
            # 存储分析结果和文件信息
            metadata={
                'analysis': {
                    'relevance': analysis_result.relevance.value,
                    'content_type': analysis_result.content_type.value,
                    'confidence': analysis_result.confidence,
                    'quality_score': analysis_result.quality_score,
                    'keywords': analysis_result.keywords,
                    'issues': analysis_result.issues,
                    'suggestions': analysis_result.suggestions
                },
                'file_info': {
                    'original_filename': filename,
                    'mime_type': uploaded_file.content_type or 'text/plain',
                    'file_type': file_type
                },
                'file_details': file_info if file_info else None
            }
        )
        
        # 向量化文档内容
        try:
            vectorizer = VectorizationService()
            embedding = vectorizer.vectorize_text(content)
            document.vector_embedding = embedding.tolist()
            document.save()
            logger.info(f"文档 {filename} 向量化成功")
        except Exception as e:
            logger.error(f"文档 {filename} 向量化失败: {e}")
            # 向量化失败不影响文档保存，但记录错误
        
        serializer = DocumentSerializer(document)
        response_data = serializer.data
        
        if warning_message:
            response_data['warning'] = warning_message
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except KeyError as e:
        logger.error(f"文档上传失败 - 缺少必要参数: {e}")
        return Response({
            'error': f'请求参数错误: 缺少必要字段 {str(e)}',
            'detail': '请确保使用 multipart/form-data 格式，并包含 file 字段'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"文档上传失败: {e}", exc_info=True)
        return Response({
            'error': f'文档上传失败: {str(e)}',
            'detail': '请检查文件格式是否正确，或联系管理员'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _ensure_json_serializable(obj: Any) -> Any:
    """递归确保对象可被 JSON 序列化（避免 IFC/第三方返回的非标准类型导致 500）。"""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode('utf-8', errors='replace')
    if isinstance(obj, dict):
        return {str(k): _ensure_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_ensure_json_serializable(v) for v in obj]
    return str(obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_bim(request, knowledge_base_id):
    """
    BIM 数据上传：BIM/IFC/JSON → 自动转 JSON → 入库并向量化。
    支持 .json（BIM 导出）、.ifc（需安装 ifcopenshell）。
    """
    try:
        knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
        if 'file' not in request.FILES:
            return Response({'error': '请上传文件（.json 或 .ifc）'}, status=status.HTTP_400_BAD_REQUEST)
        uploaded_file = request.FILES['file']
        filename = (uploaded_file.name or '').strip()
        if not filename:
            return Response({'error': '文件名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if ext not in ('json', 'ifc'):
            return Response({'error': '仅支持 .json 或 .ifc 格式'}, status=status.HTTP_400_BAD_REQUEST)
        max_size = 50 * 1024 * 1024  # 50MB
        if uploaded_file.size > max_size:
            return Response({
                'error': f'文件不能超过 50MB，当前：{uploaded_file.size / 1024 / 1024:.2f}MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            raw = uploaded_file.read()
        except Exception as e:
            logger.error("BIM 文件读取失败: %s", e)
            return Response({'error': f'读取文件失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        if not raw:
            return Response({'error': '文件内容为空'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            bim_json = bim_to_json(raw, filename)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("BIM 解析失败: %s", e)
            return Response({'error': f'BIM 解析失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        # 入库：content 存可检索文本（供 RAG），metadata 仅存可序列化数据
        content_for_vector = bim_json_to_searchable_text(bim_json)
        # 大 IFC 时只存 bim_meta，避免 metadata 过大导致 DB/序列化失败
        bim_meta_safe = _ensure_json_serializable(bim_json.get('bim_meta') or {})
        bim_elements_safe = _ensure_json_serializable(bim_json_to_elements_list(bim_json))
        try:
            bim_json_safe = _ensure_json_serializable(bim_json)
        except Exception as e:
            logger.warning("BIM JSON 序列化清洗异常，仅存 bim_meta: %s", e)
            bim_json_safe = {}
        safe_meta = {
            'source': 'bim',
            'format': ext,
            'bim_meta': bim_meta_safe,
            'bim_elements': bim_elements_safe,
            'bim_json': bim_json_safe,
        }
        title = (filename[:197] + '...') if len(filename) > 200 else filename
        try:
            document = Document.objects.create(
                knowledge_base=knowledge_base,
                title=title,
                content=content_for_vector,
                content_type='text',
                file_path=filename,
                file_size=uploaded_file.size,
                metadata=safe_meta,
            )
        except Exception as e:
            logger.exception("BIM 文档入库失败: %s", e)
            return Response({
                'error': f'文档入库失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            vectorizer = VectorizationService()
            embedding = vectorizer.vectorize_text(content_for_vector)
            if embedding is not None and hasattr(embedding, 'tolist'):
                vec_list = embedding.tolist()
                if len(vec_list) != 1024:
                    vec_list = (vec_list + [0.0] * 1024)[:1024]
                document.vector_embedding = vec_list
                document.save()
                logger.info("BIM 文档 %s 向量化成功", filename)
        except Exception as e:
            logger.warning("BIM 文档向量化失败（已入库，可后续补算）: %s", e, exc_info=True)
        try:
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("BIM 文档序列化返回失败: %s", e)
            return Response({
                'error': f'响应序列化失败: {str(e)}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Http404:
        raise
    except Exception as e:
        logger.exception("BIM 上传未捕获异常: %s", e)
        return Response({
            'error': f'BIM 上传失败: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_documents_from_json(request, knowledge_base_id):
    """异步批量导入 JSON 文档 - 创建 ImportJob 并触发后台任务"""
    knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)

    try:
        if 'file' not in request.FILES:
            return Response({
                'error': '请上传 JSON 文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        max_file_size = 100 * 1024 * 1024  # 100MB
        if uploaded_file.size > max_file_size:
            return Response({
                'error': f'JSON 文件不能超过 100MB，当前大小为 {uploaded_file.size / 1024 / 1024:.2f} MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证 JSON 格式
        raw_bytes = uploaded_file.read()
        try:
            data = json.loads(raw_bytes.decode('utf-8'))
            if isinstance(data, dict):
                entries = data.get('documents', [])
            else:
                entries = data
            if not isinstance(entries, list):
                return Response({
                    'error': 'JSON 顶层必须是数组或包含 documents 数组'
                }, status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError as exc:
            return Response({
                'error': f'JSON 解析失败: {exc}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 保存文件到存储
        file_path = f'imports/{knowledge_base_id}/{uploaded_file.name}'
        saved_path = default_storage.save(file_path, ContentFile(raw_bytes))

        # 创建 ImportJob
        import_job = ImportJob.objects.create(
            knowledge_base=knowledge_base,
            owner=request.user,
            file_path=saved_path,
            original_filename=uploaded_file.name,
            total_documents=len(entries),
            status=ImportJob.Status.PENDING
        )

        # 触发异步任务
        try:
            process_import_job.delay(str(import_job.id))
        except Exception as exc:
            logger.error(f"无法启动 Celery 任务: {exc}")
            import_job.mark_failed(f'无法启动后台任务: {exc}')
            return Response({
                'error': '无法启动后台导入任务，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'JSON 导入任务已创建',
            'job_id': str(import_job.id),
            'status': import_job.status,
            'knowledge_base_id': str(knowledge_base.id)
        }, status=status.HTTP_201_CREATED)

    except Exception as exc:
        logger.error(f"JSON 导入失败: {exc}", exc_info=True)
        return Response({'error': f'JSON 导入失败: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def import_job_detail(request, knowledge_base_id, job_id):
    """查询 ImportJob 状态和进度"""
    knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
    import_job = get_object_or_404(ImportJob, pk=job_id, knowledge_base=knowledge_base)

    return Response({
        'id': str(import_job.id),
        'status': import_job.status,
        'total_documents': import_job.total_documents,
        'created_documents': import_job.created_documents,
        'vectorized_documents': import_job.vectorized_documents,
        'skipped_documents': import_job.skipped_documents,
        'skipped_samples': import_job.skipped_samples,
        'error_message': import_job.error_message,
        'created_at': import_job.created_at,
        'started_at': import_job.started_at,
        'finished_at': import_job.finished_at,
        'progress_percentage': (
            int((import_job.created_documents / import_job.total_documents * 100))
            if import_job.total_documents > 0 else 0
        )
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_import_job(request, knowledge_base_id, job_id):
    """取消 ImportJob"""
    knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
    import_job = get_object_or_404(ImportJob, pk=job_id, knowledge_base=knowledge_base)

    if import_job.is_final:
        return Response({
            'error': f'任务已结束，无法取消（状态：{import_job.status}）'
        }, status=status.HTTP_400_BAD_REQUEST)

    reason = request.data.get('reason', '用户取消')
    import_job.mark_canceled(reason)

    return Response({
        'message': '导入任务已取消',
        'job_id': str(import_job.id),
        'status': import_job.status
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def import_job_list(request, knowledge_base_id):
    """获取知识库的所有 ImportJob 列表"""
    knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
    jobs = ImportJob.objects.filter(knowledge_base=knowledge_base).order_by('-created_at')[:50]

    return Response({
        'results': [{
            'id': str(job.id),
            'status': job.status,
            'original_filename': job.original_filename,
            'total_documents': job.total_documents,
            'created_documents': job.created_documents,
            'vectorized_documents': job.vectorized_documents,
            'skipped_documents': job.skipped_documents,
            'created_at': job.created_at,
            'finished_at': job.finished_at,
            'progress_percentage': (
                int((job.created_documents / job.total_documents * 100))
                if job.total_documents > 0 else 0
            )
        } for job in jobs]
    })


@api_view(['POST'])
@permission_classes([])  # 允许匿名访问，用于测试
def analyze_document(request):
    """分析文档内容（不保存）"""
    try:
        content = request.data.get('content', '')
        filename = request.data.get('filename', '')
        
        if not content:
            return Response({
                'error': '请提供文档内容'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = DocumentAnalyzer()
        analysis_result = analyzer.analyze_document(content, filename)
        
        return Response({
            'relevance': analysis_result.relevance.value,
            'content_type': analysis_result.content_type.value,
            'confidence': analysis_result.confidence,
            'quality_score': analysis_result.quality_score,
            'keywords': analysis_result.keywords,
            'issues': analysis_result.issues,
            'suggestions': analysis_result.suggestions
        })
        
    except Exception as e:
        logger.error(f"文档分析失败: {e}")
        return Response({
            'error': f'文档分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vectorize_document(request, knowledge_base_id, document_id):
    """向量化指定文档"""
    try:
        knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
        document = get_object_or_404(Document, pk=document_id, knowledge_base=knowledge_base)
        
        if not document.content:
            return Response({
                'error': '文档内容为空，无法向量化'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 向量化文档内容
        vectorizer = VectorizationService()
        embedding = vectorizer.vectorize_text(document.content)
        
        # 保存向量
        document.vector_embedding = embedding.tolist()
        document.save()
        
        return Response({
            'message': '文档向量化成功',
            'document_id': str(document.id),
            'vector_dimension': len(embedding)
        })
        
    except Exception as e:
        logger.error(f"文档向量化失败: {e}")
        return Response({
            'error': f'文档向量化失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vectorize_knowledge_base(request, knowledge_base_id):
    """批量向量化知识库中的所有文档"""
    try:
        knowledge_base = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
        documents = knowledge_base.documents.filter(content__isnull=False).exclude(content='')
        
        if not documents.exists():
            return Response({
                'error': '知识库中没有可向量化的文档'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        vectorizer = VectorizationService()
        success_count = 0
        error_count = 0
        
        for document in documents:
            try:
                embedding = vectorizer.vectorize_text(document.content)
                document.vector_embedding = embedding.tolist()
                document.save()
                success_count += 1
            except Exception as e:
                logger.error(f"文档 {document.id} 向量化失败: {e}")
                error_count += 1
        
        return Response({
            'message': f'批量向量化完成',
            'total_documents': documents.count(),
            'success_count': success_count,
            'error_count': error_count
        })
        
    except Exception as e:
        logger.error(f"批量向量化失败: {e}")
        return Response({
            'error': f'批量向量化失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieval_strategies(request):
    """获取可用的检索策略配置"""
    try:
        strategy_manager = RetrievalStrategyManager()
        
        strategies = {}
        for strategy_name in ['hybrid', 'vector_only', 'bm25_only']:
            strategies[strategy_name] = strategy_manager.get_strategy_config(strategy_name)
        
        return Response({
            'strategies': strategies,
            'default_strategy': 'hybrid'
        })
    except Exception as e:
        logger.error(f"获取检索策略失败: {e}")
        return Response({'error': f'获取检索策略失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preview_retrieval(request):
    """检索策略与证据预览：返回证据条目（source/score/rank/dedupe_reason）"""
    try:
        query = request.data.get('query', '')
        knowledge_base_id = request.data.get('knowledge_base_id')
        top_k = int(request.data.get('top_k', 5))
        score_threshold = float(request.data.get('score_threshold', 0.2))
        alpha = float(request.data.get('alpha', 0.5))  # 融合权重 [0,1]
        strategy = request.data.get('strategy', 'hybrid')  # 检索策略

        if not query:
            return Response({'error': 'query 不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证知识库权限
        if knowledge_base_id:
            kb = get_object_or_404(KnowledgeBase, pk=knowledge_base_id, owner=request.user)
        else:
            kb = None

        # 使用高级检索服务
        retrieval_service = AdvancedRetrievalService()
        strategy_manager = RetrievalStrategyManager()
        
        # 执行检索策略
        result = strategy_manager.execute_strategy(
            strategy_name=strategy,
            query=query,
            knowledge_base_id=knowledge_base_id,
            custom_params={
                'top_k': top_k,
                'score_threshold': score_threshold,
                'alpha': alpha,
                'enable_deduplication': True
            }
        )

        # 添加rank字段
        evidence = result.get('evidence', [])
        for i, item in enumerate(evidence):
            item['rank'] = i + 1

        return Response({
            'query': query,
            'strategy': strategy,
            'params': {
                'top_k': top_k,
                'score_threshold': score_threshold,
                'alpha': alpha
            },
            'evidence': evidence,
            'total_found': result.get('total_found', len(evidence)),
            'unique_found': result.get('unique_found', len([e for e in evidence if e.get('dedupe_reason') == 'unique']))
        })
    except Exception as e:
        logger.error(f"检索预览失败: {e}")
        return Response({'error': f'检索预览失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
