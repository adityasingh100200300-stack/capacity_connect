from django.contrib import admin
from .models import TrainerCompetency


@admin.register(TrainerCompetency)
class TrainerCompetencyAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'skill', 'score')
    list_filter = ('skill', 'score')
    search_fields = ('trainer__username', 'skill__name')
