from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'status', 'date_joined')
    list_filter = ('role', 'status', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # Add role and status to the fieldsets shown in the detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Capacity Connect', {'fields': ('role', 'status')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Capacity Connect', {'fields': ('role', 'status')}),
    )

    # Quick actions from the list view
    actions = ['approve_users', 'reject_users', 'suspend_users']

    @admin.action(description='Approve selected users')
    def approve_users(self, request, queryset):
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} user(s) approved.')

    @admin.action(description='Reject selected users')
    def reject_users(self, request, queryset):
        updated = queryset.update(status='REJECTED')
        self.message_user(request, f'{updated} user(s) rejected.')

    @admin.action(description='Suspend selected users')
    def suspend_users(self, request, queryset):
        updated = queryset.update(status='SUSPENDED')
        self.message_user(request, f'{updated} user(s) suspended.')