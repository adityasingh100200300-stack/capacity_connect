from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/', views.submit_feedback_view, name='submit_feedback'),
    path('course/<int:course_id>/all/', views.course_feedback_list_view, name='feedback_list'),
]
