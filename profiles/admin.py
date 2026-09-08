from django.contrib import admin
from .models import Profile, Skill, UserSkill, Certificate, WorkExperience


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone')
    search_fields = ('user__username', 'department')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'proficiency')
    list_filter = ('skill', 'proficiency')
    search_fields = ('user__username', 'skill__name')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'issued_by', 'issued_date')
    list_filter = ('issued_by',)
    search_fields = ('user__username', 'title')


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company', 'start_date', 'end_date')
    search_fields = ('user__username', 'company', 'role')
