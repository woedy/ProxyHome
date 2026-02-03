"""
Public Proxy Fetcher - Tier 2
Fetches proxies from established public sources and GitHub repositories
"""

import requests
import json
import re
import time
import concurrent.futures
from typing import List, Dict, Optional
import argparse
from urllib.parse import urlparse

class PublicProxyFetcher:
    def __init__(self, timeout: int = 10, max_workers: int = 30):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Location detection service URLs
        self.location_services = [
            'http://ip-api.com/json/',
            'https://ipapi.co/json/',
            'http://ipinfo.io/json'
        ]
        
    def detect_proxy_location(self, proxy_ip: str) -> Dict[str, str]:
        """Detect proxy location using IP geolocation services"""
        location_info = {
            'country': 'Unknown',
            'country_code': 'XX',
            'region': 'Unknown',
            'city': 'Unknown',
            'timezone': 'Unknown'
        }
        
        for service_url in self.location_services:
            try:
                response = self.session.get(f"{service_url}{proxy_ip}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different API response formats
                    if 'country' in data and 'countryCode' in data:  # ip-api.com format
                        location_info.update({
                            'country': data.get('country', 'Unknown'),
                            'country_code': data.get('countryCode', 'XX'),
                            'region': data.get('regionName', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'timezone': data.get('timezone', 'Unknown')
                        })
                        break
                    elif 'country_name' in data:  # ipapi.co format
                        location_info.update({
                            'country': data.get('country_name', 'Unknown'),
                            'country_code': data.get('country_code', 'XX'),
                            'region': data.get('region', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'timezone': data.get('timezone', 'Unknown')
                        })
                        break
                        
            except Exception as e:
                continue
        
        return location_info
        
    def fetch_from_spys_one(self) -> List[Dict]:
        """Fetch proxies from Spys.one with protocol-specific pages"""
        proxies = []
        # Spys.one protocol-specific pages are more reliable for detection
        pages = [
            ("http", "https://spys.one/en/free-proxy-list/"),
            ("socks", "https://spys.one/en/socks-proxy-list/")
        ]
        
        for p_type, url in pages:
            try:
                response = self.session.get(url, timeout=self.timeout)
                # Extract proxy data using regex
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
                matches = re.findall(pattern, response.text)
                
                for ip, port in matches[:50]:
                    location_info = self.detect_proxy_location(ip)
                    
                    # If we're on the socks page, it could be socks4 or socks5
                    # spys usually indicates this in the row, but regex is faster
                    # for now we'll add both or try to detect if we were more surgical
                    types_to_add = [p_type] if p_type == "http" else ["socks4", "socks5"]
                    
                    for final_type in types_to_add:
                        proxies.append({
                            'ip': ip,
                            'port': int(port),
                            'type': final_type,
                            'source': 'spys.one',
                            'tier': 2,
                            'country': location_info['country'],
                            'country_code': location_info['country_code'],
                            'region': location_info['region'],
                            'city': location_info['city'],
                            'timezone': location_info['timezone']
                        })
            except Exception as e:
                print(f"Error fetching from Spys.one ({p_type}): {e}")
                
        return proxies
    
    def fetch_from_hidemy_name(self) -> List[Dict]:
        """Fetch proxies from HideMyName"""
        proxies = []
        try:
            # HideMyName free proxy list
            urls = [
                "https://hidemy.name/en/proxy-list/?type=h#list",
                "https://hidemy.name/en/proxy-list/?type=s#list"
            ]
            
            for url in urls:
                response = self.session.get(url, timeout=self.timeout)
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d+)'
                matches = re.findall(pattern, response.text)
                
                proxy_type = 'socks4' if 'type=s' in url else 'http'
                
                for ip, port in matches[:25]:  # Limit per type
                    # Detect location for each proxy
                    location_info = self.detect_proxy_location(ip)
                    
                    proxies.append({
                        'ip': ip,
                        'port': int(port),
                        'type': proxy_type,
                        'source': 'hidemy.name',
                        'tier': 2,
                        'country': location_info['country'],
                        'country_code': location_info['country_code'],
                        'region': location_info['region'],
                        'city': location_info['city'],
                        'timezone': location_info['timezone']
                    })
                    
        except Exception as e:
            print(f"Error fetching from HideMyName: {e}")
            
        return proxies
    
    def fetch_from_geonode(self) -> List[Dict]:
        """Fetch proxies from GeoNode"""
        proxies = []
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                for proxy_data in data.get('data', []):
                    protocols = proxy_data.get('protocols', ['http'])
                    proxy_ip = proxy_data['ip']
                    
                    # Detect location (GeoNode might already have it, but let's be consistent)
                    location_info = self.detect_proxy_location(proxy_ip)
                    
                    # Use the actual protocols supported by this proxy
                    for protocol in protocols:
                        proxy_type = protocol.lower()
                        proxies.append({
                            'ip': proxy_ip,
                            'port': int(proxy_data['port']),
                            'type': proxy_type,
                            'source': 'geonode',
                            'tier': 2,
                            'country': location_info['country'],
                            'country_code': location_info['country_code'],
                            'region': location_info['region'],
                            'city': location_info['city'],
                            'timezone': location_info['timezone'],
                            'anonymity': proxy_data.get('anonymityLevel', 'Unknown'),
                            'uptime': proxy_data.get('upTime', 0)
                        })
                    
        except Exception as e:
            print(f"Error fetching from GeoNode: {e}")
            
        return proxies
    
    def fetch_from_proxylists_org(self) -> List[Dict]:
        """Fetch proxies from ProxyLists.org"""
        proxies = []
        try:
            # ProxyLists.org API endpoints
            endpoints = [
                "http://www.proxylists.net/http_highanon.txt",
                "http://www.proxylists.net/http.txt"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, timeout=self.timeout)
                    lines = response.text.strip().split('\n')
                    
                    for line in lines[:30]:  # Limit per endpoint
                        if ':' in line and len(line.split(':')) == 2:
                            ip, port = line.strip().split(':')
                            if self._is_valid_ip(ip) and port.isdigit():
                                # Detect location for each proxy
                                location_info = self.detect_proxy_location(ip)
                                
                                proxies.append({
                                    'ip': ip,
                                    'port': int(port),
                                    'type': 'http',
                                    'source': 'proxylists.org',
                                    'tier': 2,
                                    'country': location_info['country'],
                                    'country_code': location_info['country_code'],
                                    'region': location_info['region'],
                                    'city': location_info['city'],
                                    'timezone': location_info['timezone']
                                })
                except:
                    continue
                    
        except Exception as e:
            print(f"Error fetching from ProxyLists.org: {e}")
            
        return proxies
    
    def fetch_github_repositories(self) -> List[Dict]:
        """Fetch from multiple GitHub proxy repositories"""
        proxies = []
        
        # GitHub raw file URLs for proxy lists
        github_sources = [
            {
                'name': 'proxifly/free-proxy-list',
                'urls': [
                    'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt',
                    'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4.txt',
                    'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5.txt'
                ]
            },
            {
                'name': 'TheSpeedX/PROXY-List',
                'urls': [
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt'
                ]
            },
            {
                'name': 'clarketm/proxy-list',
                'urls': [
                    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
                ]
            },
            {
                'name': 'a2u/free-proxy-list',
                'urls': [
                    'https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt'
                ]
            },
            {
                'name': 'monosans/proxy-list',
                'urls': [
                    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
                    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
                    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt'
                ]
            },
            {
                'name': 'TheSpeedX/SOCKS-List',
                'urls': [
                    'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt',
                    'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt'
                ]
            },
            {
                'name': 'hookzof/socks5_list',
                'urls': [
                    'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt'
                ]
            },
            {
                'name': 'gfpcom/free-proxy-list',
                'urls': [
                    'https://raw.githubusercontent.com/gfpcom/free-proxy-list/main/proxies.txt'
                ]
            }
        ]
        
        for source in github_sources:
            print(f"Fetching from {source['name']}...")
            source_proxies = []
            
            for url in source['urls']:
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
                        
                        for line in lines[:20]:  # Limit per file
                            if ':' in line and len(line.split(':')) == 2:
                                ip, port = line.strip().split(':')
                                if self._is_valid_ip(ip) and port.isdigit():
                                    # Detect location for each proxy
                                    location_info = self.detect_proxy_location(ip)
                                    
                                    source_proxies.append({
                                        'ip': ip,
                                        'port': int(port),
                                        'type': proxy_type,
                                        'source': f"github-{source['name'].split('/')[0]}",
                                        'tier': 2,
                                        'repo': source['name'],
                                        'country': location_info['country'],
                                        'country_code': location_info['country_code'],
                                        'region': location_info['region'],
                                        'city': location_info['city'],
                                        'timezone': location_info['timezone']
                                    })
                except Exception as e:
                    print(f"  Error with {url}: {e}")
                    continue
            
            proxies.extend(source_proxies)
            print(f"  Got {len(source_proxies)} proxies")
        
        return proxies
    
    def fetch_from_free_proxy_list_net(self) -> List[Dict]:
        """Fetch from free-proxy-list.net and socks-proxy.net"""
        proxies = []
        targets = [
            ("http", "https://free-proxy-list.net/"),
            ("socks4", "https://www.socks-proxy.net/"),
            ("socks5", "https://www.socks-proxy.net/") # They usually list both on this page
        ]
        
        for p_type, url in targets:
            try:
                response = self.session.get(url, timeout=self.timeout)
                # Parse the table data
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d+)</td>'
                matches = re.findall(pattern, response.text)
                
                for ip, port in matches[:40]:
                    location_info = self.detect_proxy_location(ip)
                    
                    proxies.append({
                        'ip': ip,
                        'port': int(port),
                        'type': p_type,
                        'source': urlparse(url).netloc,
                        'tier': 2,
                        'country': location_info['country'],
                        'country_code': location_info['country_code'],
                        'region': location_info['region'],
                        'city': location_info['city'],
                        'timezone': location_info['timezone']
                    })
            except Exception as e:
                print(f"Error fetching from {url}: {e}")
                
        return proxies

    def fetch_from_pubproxy(self) -> List[Dict]:
        """Fetch from PubProxy API"""
        proxies = []
        try:
            # Fetch HTTP, SOCKS4, SOCKS5
            for p_type in ['http', 'socks4', 'socks5']:
                url = f"http://pubproxy.com/api/proxy?limit=20&format=json&type={p_type}"
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('data', []):
                        ip = item['ip']
                        port = item['port']
                        location_info = self.detect_proxy_location(ip)
                        
                        proxies.append({
                            'ip': ip,
                            'port': int(port),
                            'type': p_type,
                            'source': 'pubproxy.com',
                            'tier': 2,
                            'country': location_info['country'],
                            'country_code': location_info['country_code']
                        })
        except Exception as e:
            print(f"Error fetching from PubProxy: {e}")
        return proxies

    def fetch_from_iproyal(self) -> List[Dict]:
        """Fetch from IPRoyal free proxy list"""
        proxies = []
        try:
            url = "https://iproyal.com/free-proxy-list/"
            response = self.session.get(url, timeout=self.timeout)
            # Regex for IP:Port in their table structure
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</div>\s*<div[^>]*>\s*(\d+)</div>'
            matches = re.findall(pattern, response.text)
            
            for ip, port in matches[:30]:
                location_info = self.detect_proxy_location(ip)
                proxies.append({
                    'ip': ip,
                    'port': int(port),
                    'type': 'http', # default to http for iproyal free as they are mixed but often http
                    'source': 'iproyal.com',
                    'tier': 2,
                    'country': location_info['country']
                })
        except Exception as e:
            print(f"Error fetching from IPRoyal: {e}")
        return proxies
    
    def fetch_from_proxy_nova(self) -> List[Dict]:
        """Fetch from ProxyNova"""
        proxies = []
        try:
            url = "https://www.proxynova.com/proxy-server-list/"
            response = self.session.get(url, timeout=self.timeout)
            
            # Extract proxy data
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
            matches = re.findall(pattern, response.text)
            
            for ip, port in matches[:50]:  # Limit to 50
                proxies.append({
                    'ip': ip,
                    'port': int(port),
                    'type': 'http',
                    'source': 'proxynova',
                    'tier': 2
                })
                
        except Exception as e:
            print(f"Error fetching from ProxyNova: {e}")
            
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
        """Validate a single proxy"""
        try:
            proxy_url = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
            proxies_dict = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test with httpbin
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
    
    def fetch_all_public_proxies(self) -> List[Dict]:
        """Fetch proxies from all public sources"""
        print("Fetching from public proxy sources...")
        
        all_proxies = []
        
        # Define sources with their fetch functions
        sources = [
            ("Spys.one", self.fetch_from_spys_one),
            ("HideMyName", self.fetch_from_hidemy_name),
            ("GeoNode", self.fetch_from_geonode),
            ("ProxyLists.org", self.fetch_from_proxylists_org),
            ("Free-Proxy-List.net", self.fetch_from_free_proxy_list_net),
            ("ProxyNova", self.fetch_from_proxy_nova),
            ("PubProxy", self.fetch_from_pubproxy),
            ("IPRoyal", self.fetch_from_iproyal),
            ("GitHub Repositories", self.fetch_github_repositories)
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
        
        print(f"\nTotal unique public proxies: {len(unique_proxies)}")
        return unique_proxies
    
    def validate_proxies(self, proxies: List[Dict]) -> List[Dict]:
        """Validate proxies concurrently"""
        print(f"\nValidating {len(proxies)} public proxies...")
        
        working_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {executor.submit(self.validate_proxy, proxy): proxy 
                             for proxy in proxies}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_proxy):
                completed += 1
                if completed % 20 == 0:
                    print(f"Validated {completed}/{len(proxies)} proxies...")
                
                result = future.result()
                if result:
                    working_proxies.append(result)
        
        print(f"Validation complete: {len(working_proxies)}/{len(proxies)} working")
        return working_proxies
    
    def save_proxies(self, proxies: List[Dict], filename: str = "public_proxies.json"):
        """Save public proxies to file"""
        # Add metadata
        output = {
            'metadata': {
                'total_proxies': len(proxies),
                'tier': 2,
                'type': 'public',
                'fetched_at': time.time(),
                'sources': list(set(p['source'] for p in proxies))
            },
            'proxies': proxies
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Saved {len(proxies)} public proxies to {filename}")
