import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proxyplatform.settings')

app = Celery('proxyplatform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'fetch-public-proxies': {
        'task': 'proxies.tasks.scheduled_fetch_public_proxies',
        'schedule': 3600.0,  # Every hour
    },
    'fetch-basic-proxies': {
        'task': 'proxies.tasks.scheduled_fetch_basic_proxies',
        'schedule': 7200.0,  # Every 2 hours
    },
    'cleanup-old-proxies': {
        'task': 'proxies.tasks.cleanup_old_proxies',
        'schedule': 86400.0,  # Daily
    },
    'revalidate-working-proxies': {
        'task': 'proxies.tasks.schedule_revalidation',
        'schedule': 21600.0,  # Every 6 hours
    },
}