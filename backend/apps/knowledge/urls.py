from django.urls import path
from . import views

urlpatterns = [
    # 知识库管理
    path('', views.knowledge_base_list, name='knowledge-base-list'),  # 根路径，兼容前端请求
    path('knowledge-bases/', views.knowledge_base_list, name='knowledge-base-list-alt'),
    path('<uuid:pk>/', views.knowledge_base_detail, name='knowledge-base-detail'),  # 兼容前端请求
    path('knowledge-bases/<uuid:pk>/', views.knowledge_base_detail, name='knowledge-base-detail-alt'),
    
    # 文档管理
    path('<uuid:knowledge_base_id>/documents/', views.document_list, name='document-list'),  # 兼容前端请求
    path('knowledge-bases/<uuid:knowledge_base_id>/documents/', views.document_list, name='document-list-alt'),
    path('<uuid:knowledge_base_id>/documents/<uuid:pk>/', views.document_detail, name='document-detail'),  # 兼容前端请求
    path('knowledge-bases/<uuid:knowledge_base_id>/documents/<uuid:pk>/', views.document_detail, name='document-detail-alt'),
    path('knowledge-bases/<uuid:knowledge_base_id>/import-json/', views.import_documents_from_json, name='import-documents-from-json'),
    path('<uuid:knowledge_base_id>/bim/', views.upload_bim, name='upload-bim'),
    path('knowledge-bases/<uuid:knowledge_base_id>/bim/', views.upload_bim, name='upload-bim-alt'),
    path('knowledge-bases/<uuid:knowledge_base_id>/import-jobs/', views.import_job_list, name='import-job-list'),
    path('knowledge-bases/<uuid:knowledge_base_id>/import-jobs/<uuid:job_id>/', views.import_job_detail, name='import-job-detail'),
    path('knowledge-bases/<uuid:knowledge_base_id>/import-jobs/<uuid:job_id>/cancel/', views.cancel_import_job, name='cancel-import-job'),
    
    # 其他功能
    path('analyze-document/', views.analyze_document, name='analyze-document'),
    path('knowledge-bases/<uuid:knowledge_base_id>/documents/<uuid:document_id>/vectorize/', views.vectorize_document, name='vectorize-document'),
    path('knowledge-bases/<uuid:knowledge_base_id>/vectorize/', views.vectorize_knowledge_base, name='vectorize-knowledge-base'),
    # 检索策略/证据预览
    path('retrieval-strategies/', views.retrieval_strategies, name='retrieval-strategies'),
    path('preview-retrieval/', views.preview_retrieval, name='preview-retrieval'),
]
