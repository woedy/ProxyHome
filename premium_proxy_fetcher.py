#!/usr/bin/env python3
"""
Premium Proxy Fetcher - Tier 1
Fetches high-quality proxies from premium services with free tiers
"""

import requests
import json
import time
import os
from typing import List, Dict, Optional
import argparse
from urllib.parse import urljoin
import base64
import concurrent.futures

class PremiumProxyFetcher:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
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
        
    def fetch_webshare_proxies(self, api_key: str = None) -> List[Dict]:
        """Fetch proxies from Webshare free tier (10 free proxies)"""
        proxies = []
        
        if not api_key:
            print("Webshare API key not provided. Skipping Webshare...")
            return proxies
            
        try:
            headers = {
                'Authorization': f'Token {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Get proxy list
            url = "https://proxy.webshare.io/api/v2/proxy/list/"
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                for proxy_data in data.get('results', []):
                    proxy_ip = proxy_data['proxy_address']
                    
                    # Detect location for this proxy
                    location_info = self.detect_proxy_location(proxy_ip)
                    
                    # Webshare supports both HTTP and SOCKS5
                    for proxy_type in ['http', 'socks5']:
                        proxies.append({
                            'ip': proxy_ip,
                            'port': proxy_data['port'],
                            'username': proxy_data['username'],
                            'password': proxy_data['password'],
                            'type': proxy_type,
                            'source': 'webshare',
                            'tier': 1,
                            'country': location_info['country'],
                            'country_code': location_info['country_code'],
                            'region': location_info['region'],
                            'city': location_info['city'],
                            'timezone': location_info['timezone'],
                            'premium': True
                        })
                print(f"Fetched {len(proxies)} proxies from Webshare (HTTP + SOCKS5)")
            else:
                print(f"Webshare API error: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching from Webshare: {e}")
            
        return proxies
    
    def fetch_oxylabs_proxies(self, username: str = None, password: str = None) -> List[Dict]:
        """Fetch proxies from Oxylabs free tier (5 free datacenter proxies)"""
        proxies = []
        
        if not username or not password:
            print("Oxylabs credentials not provided. Skipping Oxylabs...")
            return proxies
            
        try:
            # Oxylabs free datacenter proxy endpoints
            endpoints = [
                'pr.oxylabs.io:10000',
                'pr.oxylabs.io:10001', 
                'pr.oxylabs.io:10002',
                'pr.oxylabs.io:10003',
                'pr.oxylabs.io:10004'
            ]
            
            for i, endpoint in enumerate(endpoints):
                ip, port = endpoint.split(':')
                
                # Detect location for Oxylabs proxies
                location_info = self.detect_proxy_location(ip)
                
                # Oxylabs supports HTTP, HTTPS, and SOCKS5
                for proxy_type in ['http', 'socks5']:
                    proxies.append({
                        'ip': ip,
                        'port': int(port),
                        'username': username,
                        'password': password,
                        'type': proxy_type,
                        'source': 'oxylabs',
                        'tier': 1,
                        'country': location_info['country'],
                        'country_code': location_info['country_code'],
                        'region': location_info['region'],
                        'city': location_info['city'],
                        'timezone': location_info['timezone'],
                        'premium': True,
                        'endpoint_id': i + 1
                    })
                
            print(f"Added {len(proxies)} Oxylabs free datacenter proxies (HTTP + SOCKS5)")
            
        except Exception as e:
            print(f"Error setting up Oxylabs proxies: {e}")
            
        return proxies
    
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
                    if 'country' in data:  # ip-api.com format
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
                    elif 'country' in data:  # ipinfo.io format
                        location_info.update({
                            'country': data.get('country', 'Unknown'),
                            'country_code': data.get('country', 'XX'),
                            'region': data.get('region', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'timezone': data.get('timezone', 'Unknown')
                        })
                        break
                        
            except Exception as e:
                continue
        
        return location_info
    
    def fetch_brightdata_proxies(self, username: str = None, password: str = None, zone: str = None) -> List[Dict]:
        """Fetch proxies from Bright Data free trial"""
        proxies = []
        
        if not all([username, password, zone]):
            print("Bright Data credentials not complete. Skipping Bright Data...")
            return proxies
            
        try:
            # Bright Data proxy endpoints (these are examples - actual endpoints vary)
            endpoints = [
                f'zproxy.lum-superproxy.io:22225',
                f'zproxy.lum-superproxy.io:22226',
                f'zproxy.lum-superproxy.io:22227'
            ]
            
            for i, endpoint in enumerate(endpoints):
                ip, port = endpoint.split(':')
                # Bright Data uses zone-based authentication
                session_id = f"session-{int(time.time())}-{i}"
                auth_username = f"{username}-session-{session_id}-zone-{zone}"
                
                # Detect location for Bright Data proxies
                location_info = self.detect_proxy_location(ip)
                
                # Bright Data supports HTTP and SOCKS5
                for proxy_type in ['http', 'socks5']:
                    proxies.append({
                        'ip': ip,
                        'port': int(port),
                        'username': auth_username,
                        'password': password,
                        'type': proxy_type,
                        'source': 'brightdata',
                        'tier': 1,
                        'country': location_info['country'],
                        'country_code': location_info['country_code'],
                        'region': location_info['region'],
                        'city': location_info['city'],
                        'timezone': location_info['timezone'],
                        'premium': True,
                        'zone': zone,
                        'session_id': session_id
                    })
                
            print(f"Added {len(proxies)} Bright Data proxies (HTTP + SOCKS5)")
            
        except Exception as e:
            print(f"Error setting up Bright Data proxies: {e}")
            
        return proxies
    
    def fetch_iproyal_free_proxies(self) -> List[Dict]:
        """Fetch free proxies from IPRoyal"""
        proxies = []
        
        try:
            # IPRoyal free proxy list endpoint
            url = "https://iproyal.com/free-proxy-list/"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Parse the response for proxy data
                import re
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
                matches = re.findall(pattern, response.text)
                
                for ip, port in matches[:10]:  # Limit to 10 proxies
                    # Detect location for each proxy
                    location_info = self.detect_proxy_location(ip)
                    
                    # IPRoyal free proxies support HTTP and SOCKS4
                    for proxy_type in ['http', 'socks4']:
                        proxies.append({
                            'ip': ip,
                            'port': int(port),
                            'type': proxy_type,
                            'source': 'iproyal',
                            'tier': 1,
                            'country': location_info['country'],
                            'country_code': location_info['country_code'],
                            'region': location_info['region'],
                            'city': location_info['city'],
                            'timezone': location_info['timezone'],
                            'premium': False  # Free tier
                        })
                    
                print(f"Fetched {len(proxies)} free proxies from IPRoyal (HTTP + SOCKS4)")
                
        except Exception as e:
            print(f"Error fetching from IPRoyal: {e}")
            
        return proxies
    
    def validate_premium_proxy(self, proxy: Dict) -> Optional[Dict]:
        """Validate a premium proxy with authentication"""
        try:
            if proxy.get('premium') and 'username' in proxy:
                # Premium proxy with authentication
                auth = (proxy['username'], proxy['password'])
                if proxy['type'] in ['socks4', 'socks5']:
                    proxy_url = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
                else:
                    proxy_url = f"http://{proxy['ip']}:{proxy['port']}"
                proxies_dict = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            else:
                # Free proxy without authentication
                proxy_url = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
                proxies_dict = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                auth = None
            
            # Test with httpbin
            test_url = "http://httpbin.org/ip"
            response = requests.get(
                test_url,
                proxies=proxies_dict,
                auth=auth,
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
    
    def load_credentials(self, config_file: str = "proxy_credentials.json") -> Dict:
        """Load API credentials from config file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading credentials: {e}")
        
        return {}
    
    def create_credentials_template(self, config_file: str = "proxy_credentials.json"):
        """Create a template credentials file"""
        template = {
            "webshare": {
                "api_key": "your_webshare_api_key_here"
            },
            "oxylabs": {
                "username": "your_oxylabs_username",
                "password": "your_oxylabs_password"
            },
            "brightdata": {
                "username": "your_brightdata_username",
                "password": "your_brightdata_password",
                "zone": "your_zone_name"
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"Created credentials template: {config_file}")
        print("Please fill in your API credentials and run again.")
    
    def fetch_all_premium_proxies(self, credentials: Dict = None) -> List[Dict]:
        """Fetch proxies from all premium sources"""
        if credentials is None:
            credentials = self.load_credentials()
        
        if not credentials:
            print("No credentials found. Creating template...")
            self.create_credentials_template()
            return []
        
        all_proxies = []
        
        # Fetch from each premium source
        sources = [
            ("Webshare", lambda: self.fetch_webshare_proxies(
                credentials.get('webshare', {}).get('api_key')
            )),
            ("Oxylabs", lambda: self.fetch_oxylabs_proxies(
                credentials.get('oxylabs', {}).get('username'),
                credentials.get('oxylabs', {}).get('password')
            )),
            ("Bright Data", lambda: self.fetch_brightdata_proxies(
                credentials.get('brightdata', {}).get('username'),
                credentials.get('brightdata', {}).get('password'),
                credentials.get('brightdata', {}).get('zone')
            )),
            ("IPRoyal Free", self.fetch_iproyal_free_proxies)
        ]
        
        for source_name, fetch_func in sources:
            print(f"\nFetching from {source_name}...")
            try:
                proxies = fetch_func()
                all_proxies.extend(proxies)
                print(f"✓ Got {len(proxies)} proxies from {source_name}")
            except Exception as e:
                print(f"✗ Error with {source_name}: {e}")
        
        print(f"\nTotal premium proxies collected: {len(all_proxies)}")
        return all_proxies
    
    def validate_all_proxies(self, proxies: List[Dict]) -> List[Dict]:
        """Validate all premium proxies with concurrent processing"""
        print(f"\nValidating {len(proxies)} premium proxies...")
        
        working_proxies = []
        
        # Use concurrent processing for faster validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {executor.submit(self.validate_premium_proxy, proxy): proxy 
                             for proxy in proxies}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_proxy):
                completed += 1
                print(f"Testing proxy {completed}/{len(proxies)}")
                
                result = future.result()
                if result:
                    working_proxies.append(result)
                    print(f"  ✓ Working - {result['ip']}:{result['port']} ({result['type']}) - {result['country']}")
                else:
                    proxy = future_to_proxy[future]
                    print(f"  ✗ Failed - {proxy['ip']}:{proxy['port']} ({proxy['type']})")
        
        print(f"\nValidation complete: {len(working_proxies)}/{len(proxies)} working")
        return working_proxies
    
    def save_proxies(self, proxies: List[Dict], filename: str = "premium_proxies.json"):
        """Save premium proxies to file"""
        # Add metadata
        output = {
            'metadata': {
                'total_proxies': len(proxies),
                'tier': 1,
                'type': 'premium',
                'fetched_at': time.time(),
                'sources': list(set(p['source'] for p in proxies))
            },
            'proxies': proxies
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Saved {len(proxies)} premium proxies to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Fetch premium proxies (Tier 1)')
    parser.add_argument('--timeout', type=int, default=15, help='Timeout for requests')
    parser.add_argument('--output', type=str, default='premium_proxies.json', help='Output filename')
    parser.add_argument('--no-validate', action='store_true', help='Skip validation')
    parser.add_argument('--create-config', action='store_true', help='Create credentials template')
    
    args = parser.parse_args()
    
    fetcher = PremiumProxyFetcher(timeout=args.timeout)
    
    if args.create_config:
        fetcher.create_credentials_template()
        return
    
    # Fetch premium proxies
    proxies = fetcher.fetch_all_premium_proxies()
    
    if not proxies:
        print("\nNo proxies fetched. Make sure to:")
        print("1. Run with --create-config to create credentials template")
        print("2. Fill in your API credentials in proxy_credentials.json")
        print("3. Run again to fetch proxies")
        return
    
    if not args.no_validate:
        proxies = fetcher.validate_all_proxies(proxies)
    
    if proxies:
        fetcher.save_proxies(proxies, args.output)
        
        # Show summary
        print(f"\n=== Premium Proxy Summary ===")
        print(f"Total working proxies: {len(proxies)}")
        
        by_source = {}
        for proxy in proxies:
            source = proxy['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        for source, count in by_source.items():
            print(f"{source}: {count} proxies")
        
        # Show usage example
        if proxies:
            sample = proxies[0]
            print(f"\nSample usage:")
            if sample.get('premium'):
                print(f"""
import requests

proxy = "http://{sample['ip']}:{sample['port']}"
auth = ("{sample['username']}", "{sample['password']}")
proxies = {{'http': proxy, 'https': proxy}}

response = requests.get('http://httpbin.org/ip', proxies=proxies, auth=auth)
print(response.json())

# Location: {sample.get('city', 'Unknown')}, {sample.get('country', 'Unknown')}
# Type: {sample['type'].upper()}
""")
            else:
                print(f"""
import requests

proxy = "{sample['type']}://{sample['ip']}:{sample['port']}"
proxies = {{'http': proxy, 'https': proxy}}

response = requests.get('http://httpbin.org/ip', proxies=proxies)
print(response.json())

# Location: {sample.get('city', 'Unknown')}, {sample.get('country', 'Unknown')}
# Type: {sample['type'].upper()}
""")
    else:
        print("No working premium proxies found!")


if __name__ == "__main__":
    main()