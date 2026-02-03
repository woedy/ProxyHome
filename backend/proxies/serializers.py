from rest_framework import serializers
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.core.exceptions import ValidationError
from .models import Proxy, ProxyCredentials, ProxySource, FetchJob, ProxyTest

class ProxySourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxySource
        fields = '__all__'

class ProxyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new proxies"""
    
    class Meta:
        model = Proxy
        fields = [
            'ip', 'port', 'proxy_type', 'tier', 'source',
            'username', 'password', 'country', 'country_code', 
            'region', 'city', 'timezone'
        ]
        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
        }
    
    def validate_ip(self, value):
        """Validate IP address"""
        try:
            validate_ipv4_address(value)
        except ValidationError:
            try:
                validate_ipv6_address(value)
            except ValidationError:
                raise serializers.ValidationError("Invalid IP address format")
        return value
    
    def validate_port(self, value):
        """Validate port number"""
        if not (1 <= value <= 65535):
            raise serializers.ValidationError("Port must be between 1 and 65535")
        return value
    
    def validate(self, data):
        """Validate unique constraint"""
        if Proxy.objects.filter(
            ip=data['ip'], 
            port=data['port'], 
            proxy_type=data['proxy_type']
        ).exists():
            raise serializers.ValidationError(
                "Proxy with this IP, port, and type already exists"
            )
        return data

class ProxyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating proxies"""
    
    class Meta:
        model = Proxy
        fields = [
            'proxy_type', 'tier', 'source', 'username', 'password',
            'country', 'country_code', 'region', 'city', 'timezone',
            'is_working'
        ]
        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
        }

class ProxySerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    location_display = serializers.CharField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Proxy
        fields = [
            'id', 'ip', 'port', 'proxy_type', 'tier', 'source_name',
            'username', 'password', 'country', 'country_code', 'region', 
            'city', 'timezone', 'location_display', 'is_working', 
            'last_checked', 'response_time', 'success_count', 
            'failure_count', 'success_rate', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
        }

class ProxyListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    source_name = serializers.CharField(source='source.name', read_only=True)
    location_display = serializers.CharField(read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Proxy
        fields = [
            'id', 'ip', 'port', 'proxy_type', 'tier', 'source_name',
            'country', 'location_display', 'is_working', 'response_time',
            'success_rate', 'created_at'
        ]
    
    def get_success_rate(self, obj):
        """Calculate success rate"""
        total = obj.success_count + obj.failure_count
        return round((obj.success_count / total * 100), 2) if total > 0 else 0

class BulkProxyActionSerializer(serializers.Serializer):
    """Serializer for bulk proxy actions"""
    proxy_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=1000
    )
    action = serializers.ChoiceField(choices=[
        ('delete', 'Delete'),
        ('test', 'Test'),
        ('mark_working', 'Mark as Working'),
        ('mark_failed', 'Mark as Failed'),
    ])

class ProxyCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProxyCredentials
        fields = '__all__'
        extra_kwargs = {
            'credentials': {'write_only': True},
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Don't expose actual credentials, just show if they exist
        data['has_credentials'] = bool(instance.credentials)
        data['credential_keys'] = list(instance.credentials.keys()) if instance.credentials else []
        return data
    
    def validate_credentials(self, value):
        """Validate credentials format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Credentials must be a JSON object")
        
        if not value:
            raise serializers.ValidationError("Credentials cannot be empty")
        
        return value

class FetchJobSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = FetchJob
        fields = '__all__'
    
    def get_duration(self, obj):
        if obj.started_at and obj.completed_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None
    
    def get_success_rate(self, obj):
        """Calculate job success rate"""
        if obj.proxies_found > 0:
            return round((obj.proxies_working / obj.proxies_found * 100), 2)
        return 0

class ProxyTestSerializer(serializers.ModelSerializer):
    proxy_display = serializers.CharField(source='proxy.__str__', read_only=True)
    proxy_ip = serializers.CharField(source='proxy.ip', read_only=True)
    proxy_port = serializers.IntegerField(source='proxy.port', read_only=True)
    proxy_type = serializers.CharField(source='proxy.proxy_type', read_only=True)
    
    class Meta:
        model = ProxyTest
        fields = '__all__'

class ProxyExportSerializer(serializers.ModelSerializer):
    """Serializer for exporting proxies in various formats"""
    proxy_url = serializers.SerializerMethodField()
    proxy_with_auth = serializers.SerializerMethodField()
    
    class Meta:
        model = Proxy
        fields = [
            'ip', 'port', 'proxy_type', 'country', 'city', 
            'proxy_url', 'proxy_with_auth', 'response_time'
        ]
    
    def get_proxy_url(self, obj):
        return f"{obj.proxy_type}://{obj.ip}:{obj.port}"
    
    def get_proxy_with_auth(self, obj):
        if obj.username and obj.password:
            return f"{obj.proxy_type}://{obj.username}:{obj.password}@{obj.ip}:{obj.port}"
        return self.get_proxy_url(obj)

class StatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_proxies = serializers.IntegerField()
    working_proxies = serializers.IntegerField()
    premium_proxies = serializers.IntegerField()
    public_proxies = serializers.IntegerField()
    basic_proxies = serializers.IntegerField()
    countries = serializers.IntegerField()
    proxy_types = serializers.DictField()
    top_countries = serializers.ListField()
    recent_jobs = serializers.ListField()
    success_rate = serializers.FloatField()