import django_filters
from django.db import models
from .models import Proxy, FetchJob, ProxyTest, ProxyCredentials, ProxySource

class ProxyFilter(django_filters.FilterSet):
    # Basic filters
    proxy_type = django_filters.ChoiceFilter(choices=Proxy.PROXY_TYPES)
    tier = django_filters.ChoiceFilter(choices=Proxy.TIERS)
    is_working = django_filters.BooleanFilter()
    
    # Location filters
    country = django_filters.CharFilter(lookup_expr='icontains')
    country_code = django_filters.CharFilter(lookup_expr='iexact')
    city = django_filters.CharFilter(lookup_expr='icontains')
    region = django_filters.CharFilter(lookup_expr='icontains')
    
    # Source filter
    source = django_filters.CharFilter(field_name='source__name', lookup_expr='icontains')
    source_id = django_filters.NumberFilter(field_name='source__id')
    
    # Performance filters
    response_time_min = django_filters.NumberFilter(field_name='response_time', lookup_expr='gte')
    response_time_max = django_filters.NumberFilter(field_name='response_time', lookup_expr='lte')
    success_rate_min = django_filters.NumberFilter(method='filter_success_rate_min')
    success_rate_max = django_filters.NumberFilter(method='filter_success_rate_max')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    last_checked_after = django_filters.DateTimeFilter(field_name='last_checked', lookup_expr='gte')
    last_checked_before = django_filters.DateTimeFilter(field_name='last_checked', lookup_expr='lte')
    
    # Multiple choice filters
    proxy_types = django_filters.BaseInFilter(field_name='proxy_type')
    tiers = django_filters.BaseInFilter(field_name='tier')
    countries = django_filters.BaseInFilter(field_name='country')
    
    # Range filters
    port_min = django_filters.NumberFilter(field_name='port', lookup_expr='gte')
    port_max = django_filters.NumberFilter(field_name='port', lookup_expr='lte')
    
    # Authentication filter
    has_auth = django_filters.BooleanFilter(method='filter_has_auth')
    
    class Meta:
        model = Proxy
        fields = {
            'ip': ['exact', 'icontains'],
            'port': ['exact', 'gte', 'lte'],
            'proxy_type': ['exact'],
            'tier': ['exact'],
            'is_working': ['exact'],
            'country': ['exact', 'icontains'],
            'city': ['exact', 'icontains'],
        }
    
    def filter_success_rate_min(self, queryset, name, value):
        """Filter by minimum success rate"""
        return queryset.extra(
            where=["CASE WHEN (success_count + failure_count) > 0 THEN (success_count::float / (success_count + failure_count) * 100) ELSE 0 END >= %s"],
            params=[value]
        )
    
    def filter_success_rate_max(self, queryset, name, value):
        """Filter by maximum success rate"""
        return queryset.extra(
            where=["CASE WHEN (success_count + failure_count) > 0 THEN (success_count::float / (success_count + failure_count) * 100) ELSE 0 END <= %s"],
            params=[value]
        )
    
    def filter_has_auth(self, queryset, name, value):
        """Filter proxies with or without authentication"""
        if value:
            return queryset.exclude(username='').exclude(password='')
        else:
            return queryset.filter(models.Q(username='') | models.Q(password=''))

class FetchJobFilter(django_filters.FilterSet):
    job_type = django_filters.ChoiceFilter(choices=FetchJob.JOB_TYPES)
    status = django_filters.ChoiceFilter(choices=FetchJob.STATUS_CHOICES)
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    started_after = django_filters.DateTimeFilter(field_name='started_at', lookup_expr='gte')
    started_before = django_filters.DateTimeFilter(field_name='started_at', lookup_expr='lte')
    completed_after = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='gte')
    completed_before = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='lte')
    
    # Performance filters
    proxies_found_min = django_filters.NumberFilter(field_name='proxies_found', lookup_expr='gte')
    proxies_found_max = django_filters.NumberFilter(field_name='proxies_found', lookup_expr='lte')
    proxies_working_min = django_filters.NumberFilter(field_name='proxies_working', lookup_expr='gte')
    proxies_working_max = django_filters.NumberFilter(field_name='proxies_working', lookup_expr='lte')
    
    # Multiple choice filters
    job_types = django_filters.BaseInFilter(field_name='job_type')
    statuses = django_filters.BaseInFilter(field_name='status')
    
    class Meta:
        model = FetchJob
        fields = ['job_type', 'status', 'validate_proxies']

class ProxyTestFilter(django_filters.FilterSet):
    success = django_filters.BooleanFilter()
    proxy_id = django_filters.NumberFilter(field_name='proxy__id')
    proxy_type = django_filters.CharFilter(field_name='proxy__proxy_type')
    proxy_tier = django_filters.NumberFilter(field_name='proxy__tier')
    
    # Date filters
    tested_after = django_filters.DateTimeFilter(field_name='tested_at', lookup_expr='gte')
    tested_before = django_filters.DateTimeFilter(field_name='tested_at', lookup_expr='lte')
    
    # Performance filters
    response_time_min = django_filters.NumberFilter(field_name='response_time', lookup_expr='gte')
    response_time_max = django_filters.NumberFilter(field_name='response_time', lookup_expr='lte')
    
    class Meta:
        model = ProxyTest
        fields = ['success', 'test_url']

class ProxyCredentialsFilter(django_filters.FilterSet):
    service_name = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    class Meta:
        model = ProxyCredentials
        fields = ['service_name', 'is_active']

class ProxySourceFilter(django_filters.FilterSet):
    tier = django_filters.ChoiceFilter(choices=[(1, 'Premium'), (2, 'Public'), (3, 'Basic')])
    is_active = django_filters.BooleanFilter()
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    # Performance filters
    success_rate_min = django_filters.NumberFilter(field_name='success_rate', lookup_expr='gte')
    success_rate_max = django_filters.NumberFilter(field_name='success_rate', lookup_expr='lte')
    total_fetched_min = django_filters.NumberFilter(field_name='total_fetched', lookup_expr='gte')
    total_fetched_max = django_filters.NumberFilter(field_name='total_fetched', lookup_expr='lte')
    
    # Date filters
    last_fetch_after = django_filters.DateTimeFilter(field_name='last_fetch_at', lookup_expr='gte')
    last_fetch_before = django_filters.DateTimeFilter(field_name='last_fetch_at', lookup_expr='lte')
    last_success_after = django_filters.DateTimeFilter(field_name='last_success_at', lookup_expr='gte')
    last_success_before = django_filters.DateTimeFilter(field_name='last_success_at', lookup_expr='lte')
    
    class Meta:
        model = ProxySource
        fields = ['tier', 'is_active', 'name']