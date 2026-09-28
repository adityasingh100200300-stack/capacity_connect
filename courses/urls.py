from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_view, name='enroll_course'),
    path('create/', views.create_course_view, name='create_course'),
    path('dashboard/', views.trainer_dashboard_view, name='trainer_dashboard'),
    path('<int:course_id>/certificate/', views.generate_certificate_view, name='generate_certificate'),
    path('courses/<int:course_id>/doubts/', views.doubt_list, name='doubt_list'),
    path('courses/<int:course_id>/doubts/new/', views.create_doubt, name='create_doubt'),
    path('doubts/<int:doubt_id>/', views.doubt_detail, name='doubt_detail'),
    # Add inside urlpatterns in courses/urls.py
    path('courses/<int:course_id>/practice/start/', views.start_practice, name='start_practice'),
    path('practice/<int:session_id>/q/<int:order>/', views.practice_question, name='practice_question'),
    path('practice/<int:session_id>/finish/', views.practice_finish, name='practice_finish'),
]
