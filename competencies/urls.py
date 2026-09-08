from django.urls import path
from . import views

urlpatterns = [
    path('', views.competency_map_view, name='competency_map'),
]
