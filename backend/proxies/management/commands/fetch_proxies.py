import logging
import concurrent.futures
from django.core.management.base import BaseCommand
from django.utils import timezone
from proxies.models import Proxy, ProxySource, FetchJob, ProxyCredentials
from proxies.utils.fetchers.premium import PremiumProxyFetcher
from proxies.utils.fetchers.public import PublicProxyFetcher
from proxies.utils.fetchers.basic import BasicProxyFetcher
from proxies.tasks import save_proxies_to_db

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch proxies from various sources'

    def add_arguments(self, parser):
        parser.add_argument('--type', type=str, default='unified', choices=['unified', 'premium', 'public', 'basic'], help='Type of fetch to run')
        parser.add_argument('--timeout', type=int, default=10, help='Timeout for requests')
        parser.add_argument('--workers', type=int, default=30, help='Max workers for validation')
        parser.add_argument('--no-validate', action='store_true', help='Skip validation')

    def handle(self, *args, **options):
        job_type = options['type']
        timeout = options['timeout']
        max_workers = options['workers']
        validate = not options['no_validate']

        self.stdout.write(self.style.SUCCESS(f'Starting {job_type} fetch job...'))

        # Create job record
        job = FetchJob.objects.create(
            job_type=job_type,
            validate_proxies=validate,
            timeout=timeout,
            max_workers=max_workers,
            status='running',
            started_at=timezone.now()
        )

        try:
            total_found = 0
            total_working = 0
            
            if job_type in ['premium', 'unified']:
                self.stdout.write('Fetching Premium Proxies...')
                credentials = {}
                for cred in ProxyCredentials.objects.filter(is_active=True):
                    credentials[cred.service_name] = cred.credentials
                
                if credentials:
                    fetcher = PremiumProxyFetcher(timeout=timeout)
                    proxies = fetcher.fetch_all_premium_proxies(credentials)
                    job.add_log(f"Fetched {len(proxies)} premium proxies")
                    
                    if validate and proxies:
                        self.stdout.write(f'Validating {len(proxies)} premium proxies...')
                        proxies = fetcher.validate_all_proxies(proxies)
                    
                    saved = save_proxies_to_db(proxies, tier=1)
                    total_found += len(proxies)
                    total_working += saved
                    self.stdout.write(self.style.SUCCESS(f"Saved {saved} Premium proxies"))
                else:
                    self.stdout.write(self.style.WARNING("No premium credentials found"))

            if job_type in ['public', 'unified']:
                self.stdout.write('Fetching Public Proxies...')
                fetcher = PublicProxyFetcher(timeout=timeout, max_workers=max_workers)
                proxies = fetcher.fetch_all_public_proxies()
                job.add_log(f"Fetched {len(proxies)} public proxies")
                
                if validate and proxies:
                    self.stdout.write(f'Validating {len(proxies)} public proxies...')
                    proxies = fetcher.validate_proxies(proxies)
                
                saved = save_proxies_to_db(proxies, tier=2)
                total_found += len(proxies)
                total_working += saved
                self.stdout.write(self.style.SUCCESS(f"Saved {saved} Public proxies"))

            if job_type in ['basic', 'unified']:
                self.stdout.write('Fetching Basic Proxies...')
                fetcher = BasicProxyFetcher(timeout=timeout, max_workers=max_workers)
                proxies = fetcher.fetch_all_basic_proxies()
                job.add_log(f"Fetched {len(proxies)} basic proxies")
                
                if validate and proxies:
                    self.stdout.write(f'Validating {len(proxies)} basic proxies...')
                    proxies = fetcher.validate_proxies(proxies)
                
                saved = save_proxies_to_db(proxies, tier=3)
                total_found += len(proxies)
                total_working += saved
                self.stdout.write(self.style.SUCCESS(f"Saved {saved} Basic proxies"))

            job.proxies_found = total_found
            job.proxies_working = total_working
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
            self.stdout.write(self.style.SUCCESS(f'Job completed. Total working proxies saved: {total_working}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Job failed: {e}'))
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
