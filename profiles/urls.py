from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile_view'),
    path('<int:user_id>/', views.profile_view, name='profile_view_user'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('add-certificate/', views.add_certificate_view, name='add_certificate'),
    path('add-experience/', views.add_experience_view, name='add_experience'),
    path('add-skill/', views.add_skill_view, name='add_skill'),
    path('remove-skill/<int:skill_id>/', views.delete_skill_view, name='delete_skill'),
]
