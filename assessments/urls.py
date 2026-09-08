from django.urls import path
from . import views

urlpatterns = [
    # Trainee Views
    path('<int:assessment_id>/start/', views.start_assessment, name='start_assessment'),
    path('attempt/<int:attempt_id>/', views.take_assessment, name='take_assessment'),
    path('attempt/<int:attempt_id>/result/', views.assessment_result, name='assessment_result'),
    
    # Trainer Views
    path('course/<int:course_id>/create/', views.create_assessment, name='create_assessment'),
    path('<int:assessment_id>/manage/', views.manage_assessment, name='manage_assessment'),
    path('<int:assessment_id>/add_question/', views.add_question, name='add_question'),
    path('<int:assessment_id>/publish/', views.publish_assessment, name='publish_assessment'),
]