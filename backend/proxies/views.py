from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, F, Case, When, FloatField
from django.utils import timezone
from datetime import timedelta
import json

from .models import Proxy, ProxyCredentials, ProxySource, FetchJob, ProxyTest
from .serializers import (
    ProxySerializer, ProxyListSerializer, ProxyCredentialsSerializer,
    ProxySourceSerializer, FetchJobSerializer, ProxyTestSerializer,
    ProxyExportSerializer, StatsSerializer, ProxyCreateSerializer,
    ProxyUpdateSerializer, BulkProxyActionSerializer
)
from .tasks import fetch_premium_proxies, fetch_public_proxies, fetch_basic_proxies, fetch_unified_proxies
from .filters import ProxyFilter, FetchJobFilter, ProxyTestFilter, ProxyCredentialsFilter, ProxySourceFilter
from .pagination import CustomPageNumberPagination, LargeResultsSetPagination

class ProxyViewSet(viewsets.ModelViewSet):
    queryset = Proxy.objects.select_related('source').all()
    serializer_class = ProxySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProxyFilter
    search_fields = ['ip', 'country', 'city', 'source__name']
    ordering_fields = ['created_at', 'response_time', 'success_count', 'failure_count', 'last_checked', 'port']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProxyListSerializer
        elif self.action == 'create':
            return ProxyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProxyUpdateSerializer
        return ProxySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Add computed success rate for ordering
        queryset = queryset.annotate(
            computed_success_rate=Case(
                When(success_count__gt=0, failure_count__gt=0, 
                     then=F('success_count') * 100.0 / (F('success_count') + F('failure_count'))),
                When(success_count__gt=0, failure_count=0, then=100.0),
                default=0.0,
                output_field=FloatField()
            )
        )
        
        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get proxy statistics for dashboard"""
        total_proxies = Proxy.objects.count()
        working_proxies = Proxy.objects.filter(is_working=True).count()
        
        # By tier
        tier_stats = Proxy.objects.values('tier').annotate(count=Count('id'))
        premium_proxies = next((item['count'] for item in tier_stats if item['tier'] == 1), 0)
        public_proxies = next((item['count'] for item in tier_stats if item['tier'] == 2), 0)
        basic_proxies = next((item['count'] for item in tier_stats if item['tier'] == 3), 0)
        
        # By type
        type_stats = dict(Proxy.objects.values_list('proxy_type').annotate(Count('id')))
        
        # Countries
        countries = Proxy.objects.exclude(country='').values('country').distinct().count()
        top_countries = list(
            Proxy.objects.exclude(country='')
            .values('country')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        # Recent jobs
        recent_jobs = FetchJob.objects.all()[:5]
        recent_jobs_data = FetchJobSerializer(recent_jobs, many=True).data
        
        # Success rate
        success_rate = 0
        if total_proxies > 0:
            success_rate = (working_proxies / total_proxies) * 100

        stats_data = {
            'total_proxies': total_proxies,
            'working_proxies': working_proxies,
            'premium_proxies': premium_proxies,
            'public_proxies': public_proxies,
            'basic_proxies': basic_proxies,
            'countries': countries,
            'proxy_types': type_stats,
            'top_countries': top_countries,
            'recent_jobs': recent_jobs_data,
            'success_rate': round(success_rate, 2)
        }
        
        serializer = StatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_actions(self, request):
        """Perform bulk actions on selected proxies"""
        serializer = BulkProxyActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        proxy_ids = serializer.validated_data['proxy_ids']
        action_type = serializer.validated_data['action']
        
        queryset = Proxy.objects.filter(id__in=proxy_ids)
        
        if action_type == 'delete':
            count = queryset.count()
            queryset.delete()
            return Response({'message': f'Deleted {count} proxies'})
        
        elif action_type == 'test':
            from .tasks import test_proxies_task
            task = test_proxies_task.delay(proxy_ids)
            return Response({
                'message': f'Testing {len(proxy_ids)} proxies',
                'task_id': task.id
            })
        
        elif action_type == 'mark_working':
            count = queryset.update(is_working=True)
            return Response({'message': f'Marked {count} proxies as working'})
        
        elif action_type == 'mark_failed':
            count = queryset.update(is_working=False)
            return Response({'message': f'Marked {count} proxies as failed'})
        
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def test_proxies(self, request):
        """Test selected proxies"""
        proxy_ids = request.data.get('proxy_ids', [])
        if not proxy_ids:
            return Response({'error': 'No proxy IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Start async task to test proxies
        from .tasks import test_proxies_task
        task = test_proxies_task.delay(proxy_ids)
        
        return Response({
            'message': f'Testing {len(proxy_ids)} proxies',
            'task_id': task.id
        })

    @action(detail=False, methods=['get', 'post'])
    def export(self, request):
        """Export proxies in various formats"""
        # Support both query params (GET) and body data (POST)
        format_type = request.data.get('format') or request.query_params.get('format', 'json')
        proxy_ids = request.data.get('proxy_ids')
        
        if proxy_ids:
            # If IDs are provided, only export those
            queryset = Proxy.objects.filter(id__in=proxy_ids)
            # Apply ordering if specific order is requested, otherwise default
            queryset = queryset.order_by(*self.ordering)
        else:
            # Otherwise use current filters
            queryset = self.filter_queryset(self.get_queryset())
        
        if format_type == 'txt':
            # Simple text format - one proxy per line
            lines = []
            for proxy in queryset:
                if proxy.username and proxy.password:
                    lines.append(f"{proxy.proxy_type}://{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}")
                else:
                    lines.append(f"{proxy.proxy_type}://{proxy.ip}:{proxy.port}")
            
            content = '\n'.join(lines)
            response = Response(content, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="proxies.txt"'
            return response
        
        elif format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['IP', 'Port', 'Type', 'Country', 'City', 'Working', 'Response Time', 'Username', 'Password'])
            
            for proxy in queryset:
                writer.writerow([
                    proxy.ip, 
                    proxy.port, 
                    proxy.proxy_type,
                    proxy.country or '', 
                    proxy.city or '', 
                    'Yes' if proxy.is_working else 'No',
                    proxy.response_time or '',
                    proxy.username or '',
                    proxy.password or ''
                ])
            
            content = output.getvalue()
            output.close()
            
            response = Response(content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="proxies.csv"'
            return response
        
        else:  # JSON format
            serializer = ProxyExportSerializer(queryset, many=True)
            return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def cleanup(self, request):
        """Clean up old/non-working proxies"""
        days = int(request.query_params.get('days', 7))
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Delete old non-working proxies
        deleted_count = Proxy.objects.filter(
            is_working=False,
            created_at__lt=cutoff_date
        ).delete()[0]
        
        return Response({
            'message': f'Deleted {deleted_count} old non-working proxies'
        })

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """Delete all proxies - DANGER ZONE"""
        # Additional safety check - require confirmation parameter
        confirm = request.query_params.get('confirm', '').lower()
        if confirm != 'yes':
            return Response({
                'error': 'This action requires confirmation. Add ?confirm=yes to the request.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get total count before deletion
        total_count = Proxy.objects.count()
        
        if total_count == 0:
            return Response({
                'message': 'No proxies to delete'
            })
        
        # Delete all proxies
        Proxy.objects.all().delete()
        
        return Response({
            'message': f'Deleted all {total_count} proxies'
        })

    @action(detail=True, methods=['post'])
    def test_single(self, request, pk=None):
        """Test a single proxy"""
        proxy = self.get_object()
        from .tasks import test_proxies_task
        task = test_proxies_task.delay([proxy.id])
        
        return Response({
            'message': f'Testing proxy {proxy.ip}:{proxy.port}',
            'task_id': task.id
        })

    @action(detail=False, methods=['get'])
    def filters_info(self, request):
        """Get available filter options"""
        return Response({
            'proxy_types': [{'value': choice[0], 'label': choice[1]} for choice in Proxy.PROXY_TYPES],
            'tiers': [{'value': choice[0], 'label': choice[1]} for choice in Proxy.TIERS],
            'countries': list(Proxy.objects.exclude(country='').values_list('country', flat=True).distinct()),
            'sources': list(ProxySource.objects.values('id', 'name')),
        })

class ProxyCredentialsViewSet(viewsets.ModelViewSet):
    queryset = ProxyCredentials.objects.all()
    serializer_class = ProxyCredentialsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProxyCredentialsFilter
    search_fields = ['service_name']
    ordering_fields = ['service_name', 'created_at', 'updated_at']
    ordering = ['-updated_at']

    @action(detail=False, methods=['post'])
    def test_credentials(self, request):
        """Test premium service credentials"""
        service_name = request.data.get('service_name')
        credentials = request.data.get('credentials')
        
        if not service_name or not credentials:
            return Response(
                {'error': 'service_name and credentials required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start async task to test credentials
        from .tasks import test_credentials_task
        task = test_credentials_task.delay(service_name, credentials)
        
        return Response({
            'message': f'Testing {service_name} credentials',
            'task_id': task.id
        })

    @action(detail=True, methods=['post'])
    def test_single(self, request, pk=None):
        """Test specific credentials"""
        credential = self.get_object()
        from .tasks import test_credentials_task
        task = test_credentials_task.delay(credential.service_name, credential.credentials)
        
        return Response({
            'message': f'Testing {credential.service_name} credentials',
            'task_id': task.id
        })

class ProxySourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProxySource.objects.all()
    serializer_class = ProxySourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProxySourceFilter
    search_fields = ['name']
    ordering_fields = ['name', 'tier', 'success_rate', 'total_fetched', 'last_fetch_at']
    ordering = ['-last_fetch_at']

    @action(detail=False, methods=['get'])
    def performance_stats(self, request):
        """Get performance statistics for all sources"""
        sources = self.get_queryset()
        stats = []
        
        for source in sources:
            stats.append({
                'id': source.id,
                'name': source.name,
                'tier': source.tier,
                'success_rate': source.success_rate,
                'total_fetched': source.total_fetched,
                'is_active': source.is_active,
                'last_fetch_at': source.last_fetch_at,
                'last_success_at': source.last_success_at,
            })
        
        return Response(stats)

class FetchJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FetchJob.objects.all()
    serializer_class = FetchJobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = FetchJobFilter
    ordering_fields = ['created_at', 'started_at', 'completed_at', 'proxies_found', 'proxies_working']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'])
    def start_fetch(self, request):
        """Start a new proxy fetch job"""
        job_type = request.data.get('job_type', 'unified')
        validate = request.data.get('validate', True)
        timeout = request.data.get('timeout', 10)
        max_workers = request.data.get('max_workers', 30)
        
        # Create job record
        job = FetchJob.objects.create(
            job_type=job_type,
            validate_proxies=validate,
            timeout=timeout,
            max_workers=max_workers
        )
        
        # Start appropriate task
        task_map = {
            'premium': fetch_premium_proxies,
            'public': fetch_public_proxies,
            'basic': fetch_basic_proxies,
            'unified': fetch_unified_proxies,
        }
        
        task_func = task_map.get(job_type)
        if not task_func:
            return Response(
                {'error': f'Invalid job_type: {job_type}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task = task_func.delay(job.id, validate, timeout, max_workers)
        
        return Response({
            'job_id': job.id,
            'task_id': task.id,
            'message': f'Started {job_type} fetch job'
        })

    @action(detail=False, methods=['get'])
    def job_stats(self, request):
        """Get job statistics"""
        total_jobs = FetchJob.objects.count()
        completed_jobs = FetchJob.objects.filter(status='completed').count()
        failed_jobs = FetchJob.objects.filter(status='failed').count()
        running_jobs = FetchJob.objects.filter(status='running').count()
        
        # Average performance
        avg_proxies_found = FetchJob.objects.filter(status='completed').aggregate(
            avg=Avg('proxies_found')
        )['avg'] or 0
        
        avg_proxies_working = FetchJob.objects.filter(status='completed').aggregate(
            avg=Avg('proxies_working')
        )['avg'] or 0
        
        return Response({
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'running_jobs': running_jobs,
            'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            'avg_proxies_found': round(avg_proxies_found, 2),
            'avg_proxies_working': round(avg_proxies_working, 2),
        })

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Clear all job data - DANGER ZONE"""
        # Additional safety check - require confirmation parameter
        confirm = request.query_params.get('confirm', '').lower()
        if confirm != 'yes':
            return Response({
                'error': 'This action requires confirmation. Add ?confirm=yes to the request.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get total count before deletion
        total_count = FetchJob.objects.count()
        
        if total_count == 0:
            return Response({
                'message': 'No jobs to delete'
            })
        
        # Delete all jobs
        FetchJob.objects.all().delete()
        
        return Response({
            'message': f'Deleted all {total_count} jobs'
        })

class ProxyTestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProxyTest.objects.select_related('proxy').all()
    serializer_class = ProxyTestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProxyTestFilter
    ordering_fields = ['tested_at', 'response_time', 'success']
    ordering = ['-tested_at']

    @action(detail=False, methods=['get'])
    def test_stats(self, request):
        """Get test statistics"""
        total_tests = ProxyTest.objects.count()
        successful_tests = ProxyTest.objects.filter(success=True).count()
        failed_tests = ProxyTest.objects.filter(success=False).count()
        
        # Average response time for successful tests
        avg_response_time = ProxyTest.objects.filter(
            success=True, 
            response_time__isnull=False
        ).aggregate(avg=Avg('response_time'))['avg'] or 0
        
        return Response({
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'avg_response_time': round(avg_response_time, 3),
        })

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Clear all test data - DANGER ZONE"""
        # Additional safety check - require confirmation parameter
        confirm = request.query_params.get('confirm', '').lower()
        if confirm != 'yes':
            return Response({
                'error': 'This action requires confirmation. Add ?confirm=yes to the request.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get total count before deletion
        total_count = ProxyTest.objects.count()
        
        if total_count == 0:
            return Response({
                'message': 'No test data to delete'
            })
        
        # Delete all test data
        ProxyTest.objects.all().delete()
        
        return Response({
            'message': f'Deleted all {total_count} test records'
        })