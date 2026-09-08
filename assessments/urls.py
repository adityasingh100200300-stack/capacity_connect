from django.urls import path
from . import views

urlpatterns = [
    path('<int:assessment_id>/start/', views.start_assessment, name='start_assessment'),
    path('attempt/<int:attempt_id>/', views.take_assessment, name='take_assessment'),
    path('attempt/<int:attempt_id>/result/', views.assessment_result, name='assessment_result'),
]