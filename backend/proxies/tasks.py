from celery import shared_task
from django.utils import timezone
from django.conf import settings
import sys
import os
import json
import subprocess
import logging

from .models import Proxy, ProxySource, FetchJob, ProxyCredentials, ProxyTest
from proxies.utils.fetchers.premium import PremiumProxyFetcher
from proxies.utils.fetchers.public import PublicProxyFetcher
from proxies.utils.fetchers.basic import BasicProxyFetcher

logger = logging.getLogger(__name__)

@shared_task
def scheduled_fetch_public_proxies():
    """Scheduled task wrapper for public proxy fetching"""
    job = FetchJob.objects.create(
        job_type='public',
        validate_proxies=True,
        timeout=10,
        max_workers=30
    )
    return fetch_public_proxies.delay(job.id, validate=True, timeout=10, max_workers=30)

@shared_task
def scheduled_fetch_basic_proxies():
    """Scheduled task wrapper for basic proxy fetching"""
    job = FetchJob.objects.create(
        job_type='basic',
        validate_proxies=True,
        timeout=8,
        max_workers=40
    )
    return fetch_basic_proxies.delay(job.id, validate=True, timeout=8, max_workers=40)

@shared_task
def fetch_premium_proxies(job_id, validate=True, timeout=15, max_workers=10):
    """Fetch premium proxies using credentials"""
    job = FetchJob.objects.get(id=job_id)
    job.status = 'running'
    job.started_at = timezone.now()
    job.save()
    
    try:
        job.add_log("Starting premium proxy fetch")
        
        # Load credentials
        credentials = {}
        for cred in ProxyCredentials.objects.filter(is_active=True):
            credentials[cred.service_name] = cred.credentials
        
        if not credentials:
            job.add_log("No premium credentials found")
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            return
        
        fetcher = PremiumProxyFetcher(timeout=timeout)
        
        # Fetch proxies
        all_proxies = fetcher.fetch_all_premium_proxies(credentials)
        job.proxies_found = len(all_proxies)
        job.add_log(f"Found {len(all_proxies)} premium proxies")
        
        if validate and all_proxies:
            job.add_log("Validating proxies...")
            working_proxies = fetcher.validate_all_proxies(all_proxies)
            job.proxies_working = len(working_proxies)
            all_proxies = working_proxies
        
        # Save to database
        saved_count = save_proxies_to_db(all_proxies, tier=1)
        job.add_log(f"Saved {saved_count} proxies to database")
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
    except Exception as e:
        logger.error(f"Premium fetch job {job_id} failed: {e}")
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()

@shared_task
def fetch_public_proxies(job_id, validate=True, timeout=10, max_workers=30):
    """Fetch public proxies"""
    job = FetchJob.objects.get(id=job_id)
    job.status = 'running'
    job.started_at = timezone.now()
    job.save()
    
    try:
        job.add_log("Starting public proxy fetch")
        
        fetcher = PublicProxyFetcher(timeout=timeout, max_workers=max_workers)
        
        # Fetch proxies
        all_proxies = fetcher.fetch_all_public_proxies()
        job.proxies_found = len(all_proxies)
        job.add_log(f"Found {len(all_proxies)} public proxies")
        
        if validate and all_proxies:
            job.add_log("Validating proxies...")
            working_proxies = fetcher.validate_proxies(all_proxies)
            job.proxies_working = len(working_proxies)
            all_proxies = working_proxies
        
        # Save to database
        saved_count = save_proxies_to_db(all_proxies, tier=2)
        job.add_log(f"Saved {saved_count} proxies to database")
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
    except Exception as e:
        logger.error(f"Public fetch job {job_id} failed: {e}")
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()

@shared_task
def fetch_basic_proxies(job_id, validate=True, timeout=8, max_workers=40):
    """Fetch basic proxies"""
    job = FetchJob.objects.get(id=job_id)
    job.status = 'running'
    job.started_at = timezone.now()
    job.save()
    
    try:
        job.add_log("Starting basic proxy fetch")
        
        fetcher = BasicProxyFetcher(timeout=timeout, max_workers=max_workers)
        
        # Fetch proxies
        all_proxies = fetcher.fetch_all_basic_proxies()
        job.proxies_found = len(all_proxies)
        job.add_log(f"Found {len(all_proxies)} basic proxies")
        
        if validate and all_proxies:
            job.add_log("Validating proxies...")
            working_proxies = fetcher.validate_proxies(all_proxies)
            job.proxies_working = len(working_proxies)
            all_proxies = working_proxies
        
        # Save to database
        saved_count = save_proxies_to_db(all_proxies, tier=3)
        job.add_log(f"Saved {saved_count} proxies to database")
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
    except Exception as e:
        logger.error(f"Basic fetch job {job_id} failed: {e}")
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()

@shared_task
def fetch_unified_proxies(job_id, validate=True, timeout=10, max_workers=30):
    """Fetch proxies from all tiers"""
    job = FetchJob.objects.get(id=job_id)
    job.status = 'running'
    job.started_at = timezone.now()
    job.save()
    
    try:
        job.add_log("Starting unified proxy fetch")
        
        # Run all tier fetches
        total_found = 0
        total_working = 0
        
        # Premium
        try:
            credentials = {}
            for cred in ProxyCredentials.objects.filter(is_active=True):
                credentials[cred.service_name] = cred.credentials
            
            if credentials:
                fetcher = PremiumProxyFetcher(timeout=timeout)
                proxies = fetcher.fetch_all_premium_proxies(credentials)
                if validate and proxies:
                    proxies = fetcher.validate_all_proxies(proxies)
                saved = save_proxies_to_db(proxies, tier=1)
                total_found += len(proxies)
                total_working += saved
                job.add_log(f"Premium: {saved} proxies saved")
        except Exception as e:
            job.add_log(f"Premium fetch failed: {e}")
        
        # Public
        try:
            fetcher = PublicProxyFetcher(timeout=timeout, max_workers=max_workers)
            proxies = fetcher.fetch_all_public_proxies()
            if validate and proxies:
                proxies = fetcher.validate_proxies(proxies)
            saved = save_proxies_to_db(proxies, tier=2)
            total_found += len(proxies)
            total_working += saved
            job.add_log(f"Public: {saved} proxies saved")
        except Exception as e:
            job.add_log(f"Public fetch failed: {e}")
        
        # Basic
        try:
            fetcher = BasicProxyFetcher(timeout=timeout, max_workers=max_workers)
            proxies = fetcher.fetch_all_basic_proxies()
            if validate and proxies:
                proxies = fetcher.validate_proxies(proxies)
            saved = save_proxies_to_db(proxies, tier=3)
            total_found += len(proxies)
            total_working += saved
            job.add_log(f"Basic: {saved} proxies saved")
        except Exception as e:
            job.add_log(f"Basic fetch failed: {e}")
        
        job.proxies_found = total_found
        job.proxies_working = total_working
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
    except Exception as e:
        logger.error(f"Unified fetch job {job_id} failed: {e}")
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()

def save_proxies_to_db(proxies_data, tier):
    """Save proxy data to database"""
    saved_count = 0
    
    for proxy_data in proxies_data:
        try:
            # Get or create source
            source, _ = ProxySource.objects.get_or_create(
                name=proxy_data['source'],
                defaults={'tier': tier}
            )
            
            # Create or update proxy
            proxy, created = Proxy.objects.update_or_create(
                ip=proxy_data['ip'],
                port=proxy_data['port'],
                proxy_type=proxy_data['type'],
                defaults={
                    'tier': tier,
                    'source': source,
                    'username': proxy_data.get('username', ''),
                    'password': proxy_data.get('password', ''),
                    'country': proxy_data.get('country', ''),
                    'country_code': proxy_data.get('country_code', ''),
                    'region': proxy_data.get('region', ''),
                    'city': proxy_data.get('city', ''),
                    'timezone': proxy_data.get('timezone', ''),
                    'is_working': proxy_data.get('validated', False),
                    'response_time': proxy_data.get('response_time'),
                    'last_checked': timezone.now() if proxy_data.get('validated') else None,
                }
            )
            
            if proxy_data.get('validated'):
                proxy.success_count += 1
            
            proxy.save()
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Error saving proxy {proxy_data.get('ip')}:{proxy_data.get('port')}: {e}")
    
    return saved_count

@shared_task
def test_proxies_task(proxy_ids):
    """Test specific proxies"""
    proxies = Proxy.objects.filter(id__in=proxy_ids)
    
    for proxy in proxies:
        try:
            # Test the proxy
            import requests
            
            if proxy.username and proxy.password:
                auth = (proxy.username, proxy.password)
                proxy_url = f"http://{proxy.ip}:{proxy.port}"
            else:
                auth = None
                proxy_url = f"{proxy.proxy_type}://{proxy.ip}:{proxy.port}"
            
            proxies_dict = {'http': proxy_url, 'https': proxy_url}
            
            start_time = timezone.now()
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies_dict,
                auth=auth,
                timeout=10
            )
            end_time = timezone.now()
            
            success = response.status_code == 200
            response_time = (end_time - start_time).total_seconds()
            response_ip = None
            error_message = ''
            
            if success:
                try:
                    data = response.json()
                    response_ip = data.get('origin', '').split(',')[0].strip()
                except:
                    pass
            
            # Update proxy
            proxy.is_working = success
            proxy.last_checked = timezone.now()
            proxy.response_time = response_time
            
            if success:
                proxy.success_count += 1
            else:
                proxy.failure_count += 1
            
            proxy.save()
            
            # Create test record
            ProxyTest.objects.create(
                proxy=proxy,
                success=success,
                response_time=response_time,
                response_ip=response_ip,
                error_message=error_message
            )
            
        except Exception as e:
            # Update proxy as failed
            proxy.is_working = False
            proxy.last_checked = timezone.now()
            proxy.failure_count += 1
            proxy.save()
            
            # Create test record
            ProxyTest.objects.create(
                proxy=proxy,
                success=False,
                error_message=str(e)
            )

@shared_task
def test_credentials_task(service_name, credentials):
    """Test premium service credentials"""
    try:
        if service_name == 'webshare':
            # Test Webshare API
            import requests
            headers = {
                'Authorization': f'Token {credentials.get("api_key")}',
                'Content-Type': 'application/json'
            }
            response = requests.get(
                'https://proxy.webshare.io/api/v2/proxy/list/',
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
            
        elif service_name == 'oxylabs':
            # Test Oxylabs endpoint
            import requests
            proxy_url = f"http://pr.oxylabs.io:10000"
            auth = (credentials.get('username'), credentials.get('password'))
            
            response = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': proxy_url, 'https': proxy_url},
                auth=auth,
                timeout=10
            )
            return response.status_code == 200
            
        # Add more credential tests as needed
        return False
        
    except Exception as e:
        logger.error(f"Credential test failed for {service_name}: {e}")
        return False

@shared_task
def cleanup_old_proxies():
    """Clean up old non-working proxies"""
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=7)
    
    # Delete old non-working proxies
    deleted_count = Proxy.objects.filter(
        is_working=False,
        created_at__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old non-working proxies")
    return deleted_count

@shared_task
def schedule_revalidation():
    """Periodically check all working proxies to ensure they are still alive"""
    # Get all working proxies that haven't been checked in the last hour
    # (to avoid redundant checks if they were just fetched)
    cutoff_time = timezone.now() - timezone.timedelta(hours=1)
    working_proxy_ids = list(Proxy.objects.filter(
        is_working=True,
        last_checked__lt=cutoff_time
    ).values_list('id', flat=True))
    
    if not working_proxy_ids:
        return "No working proxies to revalidate"

    # Chunk size for parallel processing
    CHUNK_SIZE = 50
    
    logger.info(f"Scheduling revalidation for {len(working_proxy_ids)} working proxies")
    
    # Dispatch test tasks in chunks
    for i in range(0, len(working_proxy_ids), CHUNK_SIZE):
        chunk = working_proxy_ids[i:i + CHUNK_SIZE]
        test_proxies_task.delay(chunk)
        
    return f"Scheduled validation for {len(working_proxy_ids)} proxies"