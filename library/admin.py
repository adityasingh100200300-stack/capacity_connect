from django.contrib import admin
from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'course', 'uploaded_by', 'uploaded_at')
    list_filter = ('resource_type', 'course')
    search_fields = ('title', 'course__title', 'uploaded_by__username')
