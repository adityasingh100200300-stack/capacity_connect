from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'created_by', 'is_pinned', 'created_at')
    list_filter = ('announcement_type', 'is_pinned')
    list_editable = ('is_pinned',)
    search_fields = ('title', 'body')
