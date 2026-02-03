from django.db import models
from django.utils import timezone
import json

class ProxyCredentials(models.Model):
    """Store premium proxy service credentials"""
    service_name = models.CharField(max_length=50, unique=True)
    credentials = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Proxy Credentials"

    def __str__(self):
        return f"{self.service_name} credentials"

class ProxySource(models.Model):
    """Track proxy sources and their status"""
    name = models.CharField(max_length=100, unique=True)
    tier = models.IntegerField(choices=[(1, 'Premium'), (2, 'Public'), (3, 'Basic')])
    is_active = models.BooleanField(default=True)
    last_fetch_at = models.DateTimeField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    total_fetched = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.name} (Tier {self.tier})"

class Proxy(models.Model):
    """Individual proxy records"""
    PROXY_TYPES = [
        ('http', 'HTTP'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    ]
    
    TIERS = [
        (1, 'Premium'),
        (2, 'Public'),
        (3, 'Basic'),
    ]

    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    proxy_type = models.CharField(max_length=10, choices=PROXY_TYPES)
    tier = models.IntegerField(choices=TIERS)
    source = models.ForeignKey(ProxySource, on_delete=models.CASCADE)
    
    # Authentication (for premium proxies)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    
    # Location data
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    # Status and performance
    is_working = models.BooleanField(default=False)
    last_checked = models.DateTimeField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['ip', 'port', 'proxy_type']
        indexes = [
            models.Index(fields=['is_working', 'tier']),
            models.Index(fields=['country', 'proxy_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.ip}:{self.port} ({self.proxy_type})"
    
    @property
    def success_rate(self):
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 0
    
    @property
    def location_display(self):
        parts = [self.city, self.region, self.country]
        return ", ".join(filter(None, parts)) or "Unknown"

class FetchJob(models.Model):
    """Track proxy fetching jobs"""
    JOB_TYPES = [
        ('premium', 'Premium'),
        ('public', 'Public'),
        ('basic', 'Basic'),
        ('unified', 'Unified'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    proxies_found = models.IntegerField(default=0)
    proxies_working = models.IntegerField(default=0)
    sources_tried = models.IntegerField(default=0)
    sources_successful = models.IntegerField(default=0)
    
    # Configuration
    validate_proxies = models.BooleanField(default=True)
    timeout = models.IntegerField(default=10)
    max_workers = models.IntegerField(default=30)
    
    # Logs and errors
    log_messages = models.JSONField(default=list)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job_type.title()} job - {self.status}"
    
    def add_log(self, message):
        self.log_messages.append({
            'timestamp': timezone.now().isoformat(),
            'message': message
        })
        self.save(update_fields=['log_messages'])

class ProxyTest(models.Model):
    """Track proxy testing results"""
    proxy = models.ForeignKey(Proxy, on_delete=models.CASCADE, related_name='tests')
    test_url = models.URLField(default='http://httpbin.org/ip')
    success = models.BooleanField()
    response_time = models.FloatField(null=True, blank=True)
    response_ip = models.GenericIPAddressField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    tested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-tested_at']

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.proxy} - {self.tested_at.strftime('%Y-%m-%d %H:%M')}"