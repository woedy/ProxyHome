import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proxyplatform.settings')
django.setup()

from proxies.utils.fetchers.public import PublicProxyFetcher
from proxies.utils.fetchers.basic import BasicProxyFetcher

def test_public_socks():
    print("Testing PublicProxyFetcher for SOCKS...")
    fetcher = PublicProxyFetcher(timeout=5, max_workers=10)
    proxies = fetcher.fetch_all_public_proxies()
    
    types = {}
    for p in proxies:
        p_type = p['type']
        types[p_type] = types.get(p_type, 0) + 1
    
    print("\nPublic Proxy Counts by Type:")
    for t, count in types.items():
        print(f" - {t}: {count}")

def test_basic_socks():
    print("\nTesting BasicProxyFetcher for SOCKS...")
    fetcher = BasicProxyFetcher(timeout=5, max_workers=10)
    proxies = fetcher.fetch_all_basic_proxies()
    
    types = {}
    for p in proxies:
        p_type = p['type']
        types[p_type] = types.get(p_type, 0) + 1
    
    print("\nBasic Proxy Counts by Type:")
    for t, count in types.items():
        print(f" - {t}: {count}")

if __name__ == "__main__":
    test_public_socks()
    test_basic_socks()
