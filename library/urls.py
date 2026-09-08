from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list_view, name='library_list'),
    path('upload/', views.upload_resource_view, name='upload_resource'),
    path('<int:resource_id>/download/', views.download_resource_view, name='download_resource'),
]
