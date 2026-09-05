from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Add custom fields to the admin detail page
    fieldsets = UserAdmin.fieldsets + (
        ('Platform Roles & Status', {'fields': ('role', 'status')}),
    )
    # Add custom fields to the admin list view
    list_display = ['username', 'email', 'role', 'status', 'is_active']
    list_filter = ['role', 'status']