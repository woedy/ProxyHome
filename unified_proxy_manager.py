#!/usr/bin/env python3
"""
Unified Proxy Manager - Orchestrator
Manages all proxy tiers and provides a single interface
"""

import json
import time
import argparse
import os
from typing import List, Dict, Optional
import subprocess
import sys

class UnifiedProxyManager:
    def __init__(self):
        self.tier_files = {
            1: 'premium_proxies.json',
            2: 'public_proxies.json', 
            3: 'basic_proxies.json'
        }
        self.tier_scripts = {
            1: 'premium_proxy_fetcher.py',
            2: 'public_proxy_fetcher.py',
            3: 'basic_proxy_fetcher.py'
        }
        
    def run_tier_fetcher(self, tier: int, **kwargs) -> bool:
        """Run a specific tier fetcher script"""
        script = self.tier_scripts.get(tier)
        if not script:
            print(f"Invalid tier: {tier}")
            return False
        
        if not os.path.exists(script):
            print(f"Script not found: {script}")
            return False
        
        print(f"\n{'='*50}")
        print(f"Running Tier {tier} Fetcher")
        print(f"{'='*50}")
        
        # Build command arguments
        cmd = [sys.executable, script]
        
        # Add common arguments
        if 'timeout' in kwargs:
            cmd.extend(['--timeout', str(kwargs['timeout'])])
        if 'workers' in kwargs:
            cmd.extend(['--workers', str(kwargs['workers'])])
        if kwargs.get('no_validate'):
            cmd.append('--no-validate')
        if 'output' in kwargs:
            cmd.extend(['--output', kwargs['output']])
        
        # Special handling for premium tier
        if tier == 1 and kwargs.get('create_config'):
            cmd.append('--create-config')
        
        try:
            result = subprocess.run(cmd, capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running {script}: {e}")
            return False
    
    def load_tier_proxies(self, tier: int) -> List[Dict]:
        """Load proxies from a specific tier file"""
        filename = self.tier_files.get(tier)
        if not filename or not os.path.exists(filename):
            return []
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                return data.get('proxies', [])
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []
    
    def get_all_proxies(self, include_tiers: List[int] = None) -> List[Dict]:
        """Get all proxies from specified tiers (default: all tiers)"""
        if include_tiers is None:
            include_tiers = [1, 2, 3]
        
        all_proxies = []
        
        for tier in sorted(include_tiers):  # Process in tier order (premium first)
            proxies = self.load_tier_proxies(tier)
            all_proxies.extend(proxies)
            if proxies:
                print(f"Loaded {len(proxies)} proxies from Tier {tier}")
        
        return all_proxies
    
    def get_best_proxies(self, limit: int = 50, prefer_premium: bool = True) -> List[Dict]:
        """Get the best proxies across all tiers"""
        all_proxies = self.get_all_proxies()
        
        if not all_proxies:
            return []
        
        # Sort by tier (premium first) and response time
        def sort_key(proxy):
            tier_priority = proxy.get('tier', 3)  # Lower tier number = higher priority
            response_time = proxy.get('response_time', 999)  # Lower response time = better
            premium_bonus = 0 if proxy.get('premium', False) else 1  # Premium gets priority
            
            return (tier_priority, premium_bonus, response_time)
        
        sorted_proxies = sorted(all_proxies, key=sort_key)
        
        return sorted_proxies[:limit]
    
    def get_proxies_by_type(self, proxy_type: str, limit: int = 20) -> List[Dict]:
        """Get proxies of a specific type (http, socks4, socks5)"""
        all_proxies = self.get_all_proxies()
        
        filtered = [p for p in all_proxies if p.get('type', '').lower() == proxy_type.lower()]
        
        # Sort by tier and response time
        def sort_key(proxy):
            return (proxy.get('tier', 3), proxy.get('response_time', 999))
        
        return sorted(filtered, key=sort_key)[:limit]
    
    def get_proxies_by_country(self, country: str, limit: int = 20) -> List[Dict]:
        """Get proxies from a specific country"""
        all_proxies = self.get_all_proxies()
        
        filtered = [p for p in all_proxies 
                   if p.get('country', '').lower() == country.lower()]
        
        # Sort by tier and response time
        def sort_key(proxy):
            return (proxy.get('tier', 3), proxy.get('response_time', 999))
        
        return sorted(filtered, key=sort_key)[:limit]
    
    def run_all_tiers(self, **kwargs) -> Dict[int, bool]:
        """Run all tier fetchers in sequence"""
        results = {}
        
        print("Starting unified proxy collection across all tiers...")
        print("This may take several minutes depending on validation settings.")
        
        # Run tiers in order (premium first for best results)
        for tier in [1, 2, 3]:
            print(f"\n{'='*60}")
            print(f"TIER {tier} - {'PREMIUM' if tier == 1 else 'PUBLIC' if tier == 2 else 'BASIC'}")
            print(f"{'='*60}")
            
            success = self.run_tier_fetcher(tier, **kwargs)
            results[tier] = success
            
            if success:
                proxies = self.load_tier_proxies(tier)
                print(f"✓ Tier {tier} completed: {len(proxies)} working proxies")
            else:
                print(f"✗ Tier {tier} failed or returned no results")
        
        return results
    
    def create_unified_output(self, output_file: str = "all_proxies.json"):
        """Create a unified output file with all proxies"""
        all_proxies = self.get_all_proxies()
        
        if not all_proxies:
            print("No proxies found to unify")
            return
        
        # Create comprehensive metadata
        metadata = {
            'total_proxies': len(all_proxies),
            'created_at': time.time(),
            'tiers_included': list(set(p.get('tier', 3) for p in all_proxies)),
            'sources': list(set(p.get('source', 'unknown') for p in all_proxies)),
            'types': list(set(p.get('type', 'http') for p in all_proxies)),
            'countries': list(set(p.get('country', 'unknown') for p in all_proxies if p.get('country'))),
            'tier_breakdown': {}
        }
        
        # Calculate tier breakdown
        for tier in [1, 2, 3]:
            tier_proxies = [p for p in all_proxies if p.get('tier') == tier]
            metadata['tier_breakdown'][f'tier_{tier}'] = {
                'count': len(tier_proxies),
                'sources': list(set(p.get('source', 'unknown') for p in tier_proxies))
            }
        
        # Create output structure
        output = {
            'metadata': metadata,
            'best_proxies': self.get_best_proxies(limit=50),
            'all_proxies': all_proxies
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nUnified proxy file created: {output_file}")
        print(f"Total proxies: {len(all_proxies)}")
        print(f"Best proxies (top 50): included")
        
        return output_file
    
    def show_summary(self):
        """Show summary of all available proxies"""
        print("\n" + "="*60)
        print("PROXY COLLECTION SUMMARY")
        print("="*60)
        
        total_proxies = 0
        
        for tier in [1, 2, 3]:
            proxies = self.load_tier_proxies(tier)
            tier_name = {1: "PREMIUM", 2: "PUBLIC", 3: "BASIC"}[tier]
            
            print(f"\nTier {tier} ({tier_name}):")
            print(f"  File: {self.tier_files[tier]}")
            print(f"  Proxies: {len(proxies)}")
            
            if proxies:
                # Show breakdown by source
                sources = {}
                types = {}
                for proxy in proxies:
                    source = proxy.get('source', 'unknown')
                    ptype = proxy.get('type', 'http')
                    sources[source] = sources.get(source, 0) + 1
                    types[ptype] = types.get(ptype, 0) + 1
                
                print(f"  Sources: {', '.join(f'{s}({c})' for s, c in sources.items())}")
                print(f"  Types: {', '.join(f'{t}({c})' for t, c in types.items())}")
                
                # Show average response time if available
                response_times = [p.get('response_time', 0) for p in proxies if p.get('response_time')]
                if response_times:
                    avg_time = sum(response_times) / len(response_times)
                    print(f"  Avg Response Time: {avg_time:.2f}s")
            
            total_proxies += len(proxies)
        
        print(f"\nTOTAL WORKING PROXIES: {total_proxies}")
        
        if total_proxies > 0:
            # Show location breakdown
            all_proxies = self.get_all_proxies()
            countries = {}
            proxy_types = {}
            
            for proxy in all_proxies:
                country = proxy.get('country', 'Unknown')
                ptype = proxy.get('type', 'http')
                countries[country] = countries.get(country, 0) + 1
                proxy_types[ptype] = proxy_types.get(ptype, 0) + 1
            
            print(f"\nTop Countries:")
            for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {country}: {count} proxies")
            
            print(f"\nProxy Types:")
            for ptype, count in sorted(proxy_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {ptype.upper()}: {count} proxies")
            
            print(f"\nRecommended usage:")
            print(f"1. Use Tier 1 (Premium) for production-like testing")
            print(f"2. Use Tier 2 (Public) for general development")
            print(f"3. Use Tier 3 (Basic) for high-volume, low-reliability testing")
            print(f"4. Filter by country: --country US")
            print(f"5. Filter by type: --type socks5")
    
    def export_for_tools(self, tool_format: str = "requests"):
        """Export proxies in format suitable for different tools"""
        all_proxies = self.get_best_proxies(limit=100)
        
        if not all_proxies:
            print("No proxies available for export")
            return
        
        if tool_format.lower() == "requests":
            filename = "proxies_for_requests.txt"
            with open(filename, 'w') as f:
                f.write("# Best Working Proxies for Python requests\n")
                f.write("# Format: protocol://ip:port\n")
                f.write("# Usage: proxies = {'http': proxy_url, 'https': proxy_url}\n\n")
                
                for proxy in all_proxies:
                    if proxy.get('premium') and 'username' in proxy:
                        f.write(f"# Premium: {proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}\n")
                    else:
                        f.write(f"{proxy['type']}://{proxy['ip']}:{proxy['port']}\n")
            
            print(f"Exported {len(all_proxies)} proxies to {filename}")
        
        elif tool_format.lower() == "curl":
            filename = "proxies_for_curl.txt"
            with open(filename, 'w') as f:
                f.write("# Best Working Proxies for curl\n")
                f.write("# Usage: curl --proxy [proxy] [url]\n\n")
                
                for proxy in all_proxies:
                    if proxy.get('premium') and 'username' in proxy:
                        f.write(f"# Premium: --proxy {proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}\n")
                    else:
                        f.write(f"--proxy {proxy['ip']}:{proxy['port']}\n")
            
            print(f"Exported {len(all_proxies)} proxies to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Unified Proxy Manager - Run all tiers')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout for requests')
    parser.add_argument('--workers', type=int, default=30, help='Concurrent workers')
    parser.add_argument('--no-validate', action='store_true', help='Skip validation')
    parser.add_argument('--tiers', type=str, default='1,2,3', help='Tiers to run (e.g., "1,2")')
    parser.add_argument('--summary-only', action='store_true', help='Show summary without fetching')
    parser.add_argument('--create-config', action='store_true', help='Create premium credentials config')
    parser.add_argument('--export', type=str, choices=['requests', 'curl'], help='Export format')
    parser.add_argument('--best', type=int, help='Get N best proxies across all tiers')
    parser.add_argument('--type', type=str, help='Filter by proxy type (http, socks4, socks5)')
    parser.add_argument('--country', type=str, help='Filter by country code')
    
    args = parser.parse_args()
    
    manager = UnifiedProxyManager()
    
    # Handle special commands first
    if args.create_config:
        from premium_proxy_fetcher import PremiumProxyFetcher
        fetcher = PremiumProxyFetcher()
        fetcher.create_credentials_template()
        return
    
    if args.summary_only:
        manager.show_summary()
        return
    
    if args.export:
        manager.export_for_tools(args.export)
        return
    
    if args.best:
        proxies = manager.get_best_proxies(limit=args.best)
        print(f"Top {len(proxies)} proxies:")
        for i, proxy in enumerate(proxies, 1):
            tier_name = {1: "Premium", 2: "Public", 3: "Basic"}[proxy.get('tier', 3)]
            location = f"{proxy.get('city', 'Unknown')}, {proxy.get('country', 'Unknown')}"
            print(f"{i:2d}. {proxy['ip']}:{proxy['port']} ({proxy['type'].upper()}) - {tier_name} - {location} - {proxy['source']}")
        return
    
    if args.type:
        proxies = manager.get_proxies_by_type(args.type)
        print(f"Found {len(proxies)} {args.type.upper()} proxies:")
        for proxy in proxies:
            tier_name = {1: "Premium", 2: "Public", 3: "Basic"}[proxy.get('tier', 3)]
            location = f"{proxy.get('city', 'Unknown')}, {proxy.get('country', 'Unknown')}"
            print(f"  {proxy['ip']}:{proxy['port']} - {tier_name} - {location} - {proxy['source']}")
        return
    
    if args.country:
        proxies = manager.get_proxies_by_country(args.country)
        print(f"Found {len(proxies)} proxies from {args.country.upper()}:")
        for proxy in proxies:
            tier_name = {1: "Premium", 2: "Public", 3: "Basic"}[proxy.get('tier', 3)]
            location = f"{proxy.get('city', 'Unknown')}, {proxy.get('country', 'Unknown')}"
            print(f"  {proxy['ip']}:{proxy['port']} ({proxy['type'].upper()}) - {tier_name} - {location} - {proxy['source']}")
        return
    
    # Parse tiers to run
    try:
        tiers_to_run = [int(t.strip()) for t in args.tiers.split(',')]
        tiers_to_run = [t for t in tiers_to_run if t in [1, 2, 3]]
    except:
        tiers_to_run = [1, 2, 3]
    
    if not tiers_to_run:
        print("No valid tiers specified. Use --tiers 1,2,3")
        return
    
    print(f"Running tiers: {tiers_to_run}")
    
    # Run specified tiers
    kwargs = {
        'timeout': args.timeout,
        'workers': args.workers,
        'no_validate': args.no_validate
    }
    
    results = {}
    for tier in sorted(tiers_to_run):
        success = manager.run_tier_fetcher(tier, **kwargs)
        results[tier] = success
    
    # Create unified output and show summary
    manager.create_unified_output()
    manager.show_summary()
    
    # Show final results
    print(f"\n{'='*60}")
    print("EXECUTION RESULTS")
    print(f"{'='*60}")
    
    for tier, success in results.items():
        tier_name = {1: "Premium", 2: "Public", 3: "Basic"}[tier]
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"Tier {tier} ({tier_name}): {status}")
    
    successful_tiers = sum(1 for success in results.values() if success)
    print(f"\nCompleted: {successful_tiers}/{len(results)} tiers successful")
    
    if successful_tiers > 0:
        print(f"\nNext steps:")
        print(f"1. Check all_proxies.json for unified results")
        print(f"2. Use proxy_usage_example.py to test the proxies")
        print(f"3. Run with --export requests to get ready-to-use format")


if __name__ == "__main__":
    main()