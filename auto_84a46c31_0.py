```python
#!/usr/bin/env python3
"""
Website Health Monitor

A self-contained Python script that reads URLs from a config file and monitors:
- HTTP status codes
- Response times
- SSL certificate details (expiration date, issuer)

The script reads URLs from 'urls.txt' (one URL per line) and outputs results to stdout.
Requires: httpx library for HTTP requests with SSL certificate inspection.

Usage: python script.py
"""

import json
import ssl
import socket
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    exit(1)


class WebsiteHealthMonitor:
    """Monitor website health including HTTP status, response time, and SSL certificates."""
    
    def __init__(self, config_file: str = "urls.txt", timeout: int = 30):
        self.config_file = config_file
        self.timeout = timeout
        
    def load_urls(self) -> List[str]:
        """Load URLs from configuration file."""
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                # Create sample config if it doesn't exist
                sample_urls = [
                    "https://httpbin.org/get",
                    "https://github.com",
                    "https://www.google.com"
                ]
                config_path.write_text("\n".join(sample_urls))
                print(f"Created sample config file: {self.config_file}")
            
            with open(config_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return urls
        except Exception as e:
            print(f"Error loading URLs from {self.config_file}: {e}")
            return []
    
    def get_ssl_info(self, hostname: str, port: int = 443) -> Optional[Dict]:
        """Get SSL certificate information."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse expiration date
                    not_after = cert.get('notAfter')
                    expiry_date = None
                    days_until_expiry = None
                    
                    if not_after:
                        try:
                            expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                            days_until_expiry = (expiry_date - datetime.now()).days
                        except ValueError:
                            pass
                    
                    # Extract issuer
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    issuer_name = issuer.get('organizationName', 'Unknown')
                    
                    return {
                        'valid': True,
                        'issuer': issuer_name,
                        'expiry_date': expiry_date.isoformat() if expiry_date else None,
                        'days_until_expiry': days_until_expiry,
                        'subject': dict(x[0] for x in cert.get('subject', []))
                    }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def check_website(self, url: str) -> Dict:
        """Check a single website's health."""
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'response_time_ms': None,
            'ssl_info': None,
            'error': None
        }
        
        try:
            # Parse URL to get hostname for SSL check
            parsed_url = urllib.parse.urlparse(url)
            hostname = parsed_url.hostname
            
            # Make HTTP request and measure response time
            start_time = time.time()
            
            with httpx.Client(timeout=self.timeout, verify=False) as client:
                response = client.get(url)
                
            end_time = time.time()
            response_time_ms = round((end_time - start_time) * 1000, 2)
            
            result.update({
                'status_code': response.status_code,
                'response_time_ms': response_time_ms,
                'headers': dict(response.headers)
            })
            
            # Get SSL certificate info for HTTPS URLs
            if parsed_url.scheme.lower() == 'https' and hostname:
                port = parsed_url.port or 443
                result['ssl_info'] = self.get_ssl_info(hostname, port)
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def run_health_check(self) -> List[Dict]:
        """Run health check on all configured URLs."""
        urls = self.load_urls()
        if not urls:
            print("No URLs to check. Please add URLs to urls.txt")
            return []
        
        print(f"Checking {len(urls)} websites...")
        print("-" * 80)
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Checking: {url}")
            result = self.check_website(url)
            results.append(result)
            
            # Print immediate results
            self.print_result(result)
            print("-" * 40)
            
        return results
    
    def print_result(self, result: Dict):
        """Print formatted result for a single website check."""
        url = result['url']
        
        if result['error']:
            print(f"❌ ERROR: {result['error']}")
            return
            
        status = result['status_code']
        response_time = result['response_time_ms']
        
        # Status indicator
        if status and 200 <= status < 300:
            status_icon = "✅"
        elif status and 300 <= status < 400:
            status_icon = "🔀"
        else:
            status_icon = "❌"
            
        print(f"{status_icon} Status: {status} | Response Time: {response_time}ms")
        
        # SSL information
        ssl_info = result.get('ssl_info')
        if ssl_info:
            if ssl_info.get('valid'):
                days_left = ssl_info.get('days_until_expiry')
                issuer = ssl_info.get('issuer', 'Unknown')
                
                if days_left is not None:
                    if days_left > 30:
                        ssl_icon = "🔒"
                    elif days_left > 0:
                        ssl_icon = "⚠️"
                    else:
                        ssl_icon = "💥"
                    
                    print(f"{ssl_icon} SSL: {issuer} | Expires in {days_left} days")
                else:
                    print(f"🔒 SSL: {issuer} | Expiry date unknown")
            else:
                print(f"❌ SSL Error: {ssl_info.get('error', 'Unknown SSL error')}")


def main():
    """Main function to run the website health monitor."""
    monitor = WebsiteHealthMonitor()
    results = monitor.run_health_check()
    
    if results:
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        total_sites = len(results)
        healthy_sites = sum(1 for r in results if r.get('status_code') and 200 <= r['status_code'] < 300 and not r.get('error'))
        
        print(f"Total sites checked: {total_sites}")
        print(f"Healthy sites: {healthy_sites}")
        print(