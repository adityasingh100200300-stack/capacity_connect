from django.contrib import admin
from .models import CourseFeedback


@admin.register(CourseFeedback)
class CourseFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course')
    search_fields = ('user__username', 'course__title')
