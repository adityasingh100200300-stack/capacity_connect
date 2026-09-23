from django.urls import path
from . import views

urlpatterns = [
    path('', views.competency_map_view, name='competency_map'),
    path('mine/', views.my_competencies_view, name='my_competencies'),
    path('mine/<int:pk>/edit/', views.competency_update_view, name='competency_update'),
]
