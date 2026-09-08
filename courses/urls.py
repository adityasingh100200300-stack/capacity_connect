from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_view, name='enroll_course'),
    path('create/', views.create_course_view, name='create_course'),
    path('dashboard/', views.trainer_dashboard_view, name='trainer_dashboard'),
]
