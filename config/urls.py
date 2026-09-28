from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lms-demo/', RedirectView.as_view(url='/', permanent=False)),
    path('profile/', RedirectView.as_view(url='/profiles/', permanent=False)),
    path('catalog/', RedirectView.as_view(url='/courses/', permanent=False)),
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('logout/', RedirectView.as_view(url='/accounts/logout/', permanent=False)),
    path('register/', RedirectView.as_view(url='/accounts/register/', permanent=False)),
    path('pending-users/', RedirectView.as_view(url='/accounts/users/', permanent=False)),
    path('send-invite/', RedirectView.as_view(url='/accounts/invite/send/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('courses/', include('courses.urls')),
    path('library/', include('library.urls')),
    path('assessments/', include('assessments.urls')),
    path('feedback/', include('feedback.urls')),
    path('competencies/', include('competencies.urls')),
    path('analytics/', include('analytics.urls')),
    path('', include('announcements.urls')),       # homepage lives at root /
]

# Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

