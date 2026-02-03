from django.contrib import admin
from .models import Proxy, ProxyCredentials, ProxySource, FetchJob, ProxyTest

@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ['ip', 'port', 'proxy_type', 'tier', 'source', 'country', 'is_working', 'response_time', 'created_at']
    list_filter = ['tier', 'proxy_type', 'is_working', 'country', 'source']
    search_fields = ['ip', 'country', 'city']
    readonly_fields = ['created_at', 'updated_at', 'success_rate']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('ip', 'port', 'proxy_type', 'tier', 'source')
        }),
        ('Authentication', {
            'fields': ('username', 'password'),
            'classes': ('collapse',)
        }),
        ('Location', {
            'fields': ('country', 'country_code', 'region', 'city', 'timezone')
        }),
        ('Status', {
            'fields': ('is_working', 'last_checked', 'response_time', 'success_count', 'failure_count', 'success_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProxyCredentials)
class ProxyCredentialsAdmin(admin.ModelAdmin):
    list_display = ['service_name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'service_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProxySource)
class ProxySourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'is_active', 'last_fetch_at', 'success_rate', 'total_fetched']
    list_filter = ['tier', 'is_active']
    readonly_fields = ['last_fetch_at', 'last_success_at', 'total_fetched', 'success_rate']

@admin.register(FetchJob)
class FetchJobAdmin(admin.ModelAdmin):
    list_display = ['job_type', 'status', 'proxies_found', 'proxies_working', 'started_at', 'completed_at']
    list_filter = ['job_type', 'status']
    readonly_fields = ['started_at', 'completed_at', 'log_messages']
    
    fieldsets = (
        ('Job Info', {
            'fields': ('job_type', 'status', 'started_at', 'completed_at')
        }),
        ('Configuration', {
            'fields': ('validate_proxies', 'timeout', 'max_workers')
        }),
        ('Results', {
            'fields': ('proxies_found', 'proxies_working', 'sources_tried', 'sources_successful')
        }),
        ('Logs', {
            'fields': ('log_messages', 'error_message'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProxyTest)
class ProxyTestAdmin(admin.ModelAdmin):
    list_display = ['proxy', 'success', 'response_time', 'response_ip', 'tested_at']
    list_filter = ['success', 'proxy__tier', 'proxy__proxy_type']
    readonly_fields = ['tested_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('proxy')