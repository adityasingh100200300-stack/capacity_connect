from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('announcements/', views.announcement_list_view, name='announcement_list'),
    path('announcements/create/', views.create_announcement_view, name='create_announcement'),
]
