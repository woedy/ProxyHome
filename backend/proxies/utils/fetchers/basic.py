"""
Basic Proxy Fetcher - Tier 3
Fetches proxies from basic sources and fallback lists
"""

import requests
import json
import re
import time
import concurrent.futures
from typing import List, Dict, Optional
import argparse

class BasicProxyFetcher:
    def __init__(self, timeout: int = 8, max_workers: int = 40):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Location detection service URLs
        self.location_services = [
            'http://ip-api.com/json/',
            'https://ipapi.co/json/'
        ]
        
    def detect_proxy_location(self, proxy_ip: str) -> Dict[str, str]:
        """Detect proxy location using IP geolocation services (basic version)"""
        location_info = {
            'country': 'Unknown',
            'country_code': 'XX',
            'region': 'Unknown',
            'city': 'Unknown'
        }
        
        # Only try first service for basic tier (faster)
        try:
            response = self.session.get(f"{self.location_services[0]}{proxy_ip}", timeout=3)
            if response.status_code == 200:
                data = response.json()
                location_info.update({
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', 'XX'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown')
                })
        except:
            pass
        
        return location_info
        
    def fetch_from_advanced_name(self) -> List[Dict]:
        """Fetch from Advanced.name (basic tier)"""
        proxies = []
        try:
            urls = [
                "https://advanced.name/freeproxy",
                "https://advanced.name/freeproxy?type=socks4",
                "https://advanced.name/freeproxy?type=socks5"
            ]
            
            for url in urls:
                response = self.session.get(url, timeout=self.timeout)
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
                matches = re.findall(pattern, response.text)
                
                if 'socks4' in url:
                    proxy_type = 'socks4'
                elif 'socks5' in url:
                    proxy_type = 'socks5'
                else:
                    proxy_type = 'http'
                
                for ip, port in matches[:30]:  # Limit per type
                    # Basic location detection (faster for basic tier)
                    location_info = self.detect_proxy_location(ip)
                    
                    proxies.append({
                        'ip': ip,
                        'port': int(port),
                        'type': proxy_type,
                        'source': 'advanced.name',
                        'tier': 3,
                        'country': location_info['country'],
                        'country_code': location_info['country_code'],
                        'region': location_info['region'],
                        'city': location_info['city']
                    })
                    
        except Exception as e:
            print(f"Error fetching from Advanced.name: {e}")
            
        return proxies
    
    def fetch_from_oneproxy_pro(self) -> List[Dict]:
        """Fetch from OneProxy.pro"""
        proxies = []
        try:
            url = "https://oneproxy.pro/free-proxy/"
            response = self.session.get(url, timeout=self.timeout)
            
            # Extract proxy data
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
            matches = re.findall(pattern, response.text)
            
            for ip, port in matches[:40]:
                # Basic location detection (faster for basic tier)
                location_info = self.detect_proxy_location(ip)
                
                proxies.append({
                    'ip': ip,
                    'port': int(port),
                    'type': 'http',
                    'source': 'oneproxy.pro',
                    'tier': 3,
                    'country': location_info['country'],
                    'country_code': location_info['country_code'],
                    'region': location_info['region'],
                    'city': location_info['city']
                })
                
        except Exception as e:
            print(f"Error fetching from OneProxy.pro: {e}")
            
        return proxies
    
    def fetch_from_proxyelite_info(self) -> List[Dict]:
        """Fetch from ProxyElite.info"""
        proxies = []
        try:
            # ProxyElite.info API-like endpoints
            urls = [
                "https://proxyelite.info/free-proxy-list/",
                "https://proxyelite.info/free-proxy-list/?type=http",
                "https://proxyelite.info/free-proxy-list/?type=socks4"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=self.timeout)
                    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
                    matches = re.findall(pattern, response.text)
                    
                    proxy_type = 'socks4' if 'socks4' in url else 'http'
                    
                    for ip, port in matches[:25]:  # Limit per URL
                        # Basic location detection (faster for basic tier)
                        location_info = self.detect_proxy_location(ip)
                        
                        proxies.append({
                            'ip': ip,
                            'port': int(port),
                            'type': proxy_type,
                            'source': 'proxyelite.info',
                            'tier': 3,
                            'country': location_info['country'],
                            'country_code': location_info['country_code'],
                            'region': location_info['region'],
                            'city': location_info['city']
                        })
                except:
                    continue
                    
        except Exception as e:
            print(f"Error fetching from ProxyElite.info: {e}")
            
        return proxies
    
    def fetch_from_proxyverity(self) -> List[Dict]:
        """Fetch from ProxyVerity"""
        proxies = []
        try:
            url = "https://proxyverity.com/"
            response = self.session.get(url, timeout=self.timeout)
            
            # Extract proxy data
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
            matches = re.findall(pattern, response.text)
            
            for ip, port in matches[:35]:
                # Basic location detection (faster for basic tier)
                location_info = self.detect_proxy_location(ip)
                
                proxies.append({
                    'ip': ip,
                    'port': int(port),
                    'type': 'http',
                    'source': 'proxyverity',
                    'tier': 3,
                    'country': location_info['country'],
                    'country_code': location_info['country_code'],
                    'region': location_info['region'],
                    'city': location_info['city']
                })
                
        except Exception as e:
            print(f"Error fetching from ProxyVerity: {e}")
            
        return proxies
    
    def fetch_from_we1_town(self) -> List[Dict]:
        """Fetch from we1.town"""
        proxies = []
        try:
            url = "https://we1.town/en/free-proxy-list"
            response = self.session.get(url, timeout=self.timeout)
            
            # Extract proxy data
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
            matches = re.findall(pattern, response.text)
            
            for ip, port in matches[:35]:
                # Basic location detection (faster for basic tier)
                location_info = self.detect_proxy_location(ip)
                
                proxies.append({
                    'ip': ip,
                    'port': int(port),
                    'type': 'http',
                    'source': 'we1.town',
                    'tier': 3,
                    'country': location_info['country'],
                    'country_code': location_info['country_code'],
                    'region': location_info['region'],
                    'city': location_info['city']
                })
                
        except Exception as e:
            print(f"Error fetching from we1.town: {e}")
            
        return proxies
    
    def fetch_fallback_github_sources(self) -> List[Dict]:
        """Fetch from additional GitHub sources (fallback)"""
        proxies = []
        
        # Additional GitHub sources for fallback
        github_sources = [
            'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt',
            'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt',
            'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
            'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
            'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt',
            'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt'
        ]
        
        for url in github_sources:
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    
                    # Determine proxy type from URL
                    if 'socks4' in url:
                        proxy_type = 'socks4'
                    elif 'socks5' in url:
                        proxy_type = 'socks5'
                    else:
                        proxy_type = 'http'
                    
                    for line in lines[:15]:  # Limit per source
                        if ':' in line and len(line.split(':')) == 2:
                            ip, port = line.strip().split(':')
                            if self._is_valid_ip(ip) and port.isdigit():
                                # Basic location detection (faster for basic tier)
                                location_info = self.detect_proxy_location(ip)
                                
                                proxies.append({
                                    'ip': ip,
                                    'port': int(port),
                                    'type': proxy_type,
                                    'source': 'github-fallback',
                                    'tier': 3,
                                    'repo_url': url,
                                    'country': location_info['country'],
                                    'country_code': location_info['country_code'],
                                    'region': location_info['region'],
                                    'city': location_info['city']
                                })
            except Exception as e:
                print(f"Error with fallback source {url}: {e}")
                continue
        
        return proxies
    
    def fetch_from_simple_lists(self) -> List[Dict]:
        """Fetch from simple text-based proxy lists"""
        proxies = []
        
        # Simple proxy list URLs
        simple_sources = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://api.proxyscrape.com/v2/?request=get&protocol=socks4&timeout=5000&country=all',
            'https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=5000&country=all'
        ]
        
        for url in simple_sources:
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    
                    # Determine proxy type from URL
                    if 'socks4' in url:
                        proxy_type = 'socks4'
                    elif 'socks5' in url:
                        proxy_type = 'socks5'
                    else:
                        proxy_type = 'http'
                    
                    for line in lines[:20]:  # Limit per source
                        if ':' in line and len(line.split(':')) == 2:
                            ip, port = line.strip().split(':')
                            if self._is_valid_ip(ip) and port.isdigit():
                                # Basic location detection (faster for basic tier)
                                location_info = self.detect_proxy_location(ip)
                                
                                proxies.append({
                                    'ip': ip,
                                    'port': int(port),
                                    'type': proxy_type,
                                    'source': 'proxyscrape-api',
                                    'tier': 3,
                                    'country': location_info['country'],
                                    'country_code': location_info['country_code'],
                                    'region': location_info['region'],
                                    'city': location_info['city']
                                })
            except Exception as e:
                print(f"Error with simple source {url}: {e}")
                continue
        
        return proxies
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    def validate_proxy(self, proxy: Dict) -> Optional[Dict]:
        """Validate a single proxy with shorter timeout"""
        try:
            proxy_url = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
            proxies_dict = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test with httpbin (shorter timeout for basic tier)
            test_url = "http://httpbin.org/ip"
            response = requests.get(
                test_url,
                proxies=proxies_dict,
                timeout=self.timeout,
                verify=False
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if 'origin' in response_data:
                        proxy['validated'] = True
                        proxy['response_time'] = response.elapsed.total_seconds()
                        proxy['test_ip'] = response_data['origin']
                        return proxy
                except:
                    pass
                    
        except Exception as e:
            proxy['validation_error'] = str(e)
            
        return None
    
    def fetch_all_basic_proxies(self) -> List[Dict]:
        """Fetch proxies from all basic sources"""
        print("Fetching from basic proxy sources...")
        
        all_proxies = []
        
        # Define sources with their fetch functions
        sources = [
            ("Advanced.name", self.fetch_from_advanced_name),
            ("OneProxy.pro", self.fetch_from_oneproxy_pro),
            ("ProxyElite.info", self.fetch_from_proxyelite_info),
            ("ProxyVerity", self.fetch_from_proxyverity),
            ("we1.town", self.fetch_from_we1_town),
            ("GitHub Fallback", self.fetch_fallback_github_sources),
            ("Simple Lists", self.fetch_from_simple_lists)
        ]
        
        for source_name, fetch_func in sources:
            print(f"\nFetching from {source_name}...")
            try:
                proxies = fetch_func()
                all_proxies.extend(proxies)
                print(f"✓ Got {len(proxies)} proxies from {source_name}")
            except Exception as e:
                print(f"✗ Error with {source_name}: {e}")
        
        # Remove duplicates
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            key = f"{proxy['ip']}:{proxy['port']}"
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        print(f"\nTotal unique basic proxies: {len(unique_proxies)}")
        return unique_proxies
    
    def validate_proxies(self, proxies: List[Dict]) -> List[Dict]:
        """Validate proxies concurrently with higher concurrency"""
        print(f"\nValidating {len(proxies)} basic proxies...")
        
        working_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {executor.submit(self.validate_proxy, proxy): proxy 
                             for proxy in proxies}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_proxy):
                completed += 1
                if completed % 25 == 0:
                    print(f"Validated {completed}/{len(proxies)} proxies...")
                
                result = future.result()
                if result:
                    working_proxies.append(result)
        
        print(f"Validation complete: {len(working_proxies)}/{len(proxies)} working")
        return working_proxies
    
    def save_proxies(self, proxies: List[Dict], filename: str = "basic_proxies.json"):
        """Save basic proxies to file"""
        # Add metadata
        output = {
            'metadata': {
                'total_proxies': len(proxies),
                'tier': 3,
                'type': 'basic',
                'fetched_at': time.time(),
                'sources': list(set(p['source'] for p in proxies))
            },
            'proxies': proxies
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Saved {len(proxies)} basic proxies to {filename}")
