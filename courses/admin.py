from django.contrib import admin
from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'is_active', 'created_at', 'enrollment_count')
    list_filter = ('is_active', 'trainer')
    search_fields = ('title', 'trainer__username')
    list_editable = ('is_active',)

    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrollments'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'course', 'enrolled_at', 'is_completed')
    list_filter = ('is_completed', 'course')
    search_fields = ('trainee__username', 'course__title')
