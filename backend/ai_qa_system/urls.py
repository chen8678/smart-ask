"""
测试包 URL：仅 登录 + 知识库 + BIM + AI 问答
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({
        "message": "智能知识问答平台 API（测试包）",
        "api": "/api/v1/",
        "docs": "请使用前端地址访问，例如 http://localhost:3000",
    })

urlpatterns = [
    path("", root_view),
    path("admin/", admin.site.urls),
    path("api/v1/simple/", include("apps.simple_api.urls")),
    path("api/v1/auth/", include("apps.auth.urls")),
    path("api/v1/knowledge/", include("apps.knowledge.urls")),
    path("api/v1/chat/", include("apps.chat.urls")),
    path("api/v1/system/", include("apps.system.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
