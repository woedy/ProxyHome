from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProxyAccess


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_premium', 'proxy_access_limit', 'created_at')
    list_filter = ('is_premium', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('is_premium', 'proxy_access_limit')
        }),
    )


@admin.register(UserProxyAccess)
class UserProxyAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'proxies_accessed')
    list_filter = ('date',)
    search_fields = ('user__email', 'user__username')