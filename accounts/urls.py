from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.pending_users_view, name='pending_users'),
    path('users/<int:user_id>/status/', views.update_user_status_view, name='update_user_status'),
    path('invite/send/', views.send_invite, name='send_invite'),
    path('invite/<str:token>/', views.invite_signup, name='invite_signup'),
    path('verify/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
]
