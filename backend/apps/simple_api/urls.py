from django.urls import path
from . import views

urlpatterns = [
    path('knowledge/', views.knowledge_list),
    path('knowledge/<uuid:knowledge_base_id>/documents/', views.document_list),
    path('knowledge/<uuid:knowledge_base_id>/bim/', views.bim_upload),
    path('ask/', views.ask),
]
