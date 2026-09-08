from django.contrib import admin
from .models import Assessment, Question, AssessmentAttempt, AttemptAnswer

# This allows you to add Questions directly on the Assessment creation page
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration_minutes', 'deadline')
    list_filter = ('course',)
    inlines = [QuestionInline]

@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'assessment', 'status', 'score_percent', 'started_at')
    list_filter = ('status', 'assessment')
    readonly_fields = ('started_at', 'submitted_at', 'score_percent')

admin.site.register(AttemptAnswer)