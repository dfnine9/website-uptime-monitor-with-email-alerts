#!/usr/bin/env python3
"""
Website Health Checker

A self-contained Python script that monitors website health by checking:
- HTTP status codes
- Response times
- SSL certificate expiry dates

Uses only standard library plus httpx for HTTP requests.
Configurable list of URLs with comprehensive error handling.

Usage: python script.py
"""

import ssl
import socket
import datetime
import time
import sys
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    sys.exit(1)


class WebsiteHealthChecker:
    def __init__(self, urls, timeout=10, max_workers=5):
        self.urls = urls
        self.timeout = timeout
        self.max_workers = max_workers
        
    def check_ssl_expiry(self, hostname, port=443):
        """Check SSL certificate expiry date for a given hostname."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            # Parse expiry date
            expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (expiry_date - datetime.datetime.now()).days
            
            return {
                'expiry_date': expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
                'days_until_expiry': days_until_expiry,
                'expired': days_until_expiry < 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_single_url(self, url):
        """Check a single URL for status, response time, and SSL info."""
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        result = {
            'url': url,
            'timestamp': datetime.datetime.now().isoformat(),
            'status_code': None,
            'response_time_ms': None,
            'ssl_info': None,
            'error': None
        }
        
        # HTTP status and response time check
        try:
            start_time = time.time()
            with httpx.Client(timeout=self.timeout, verify=False) as client:
                response = client.get(url, follow_redirects=True)
                end_time = time.time()
                
                result['status_code'] = response.status_code
                result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
                
        except httpx.TimeoutException:
            result['error'] = 'Request timeout'
        except httpx.RequestError as e:
            result['error'] = f'Request error: {str(e)}'
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
        
        # SSL certificate check for HTTPS URLs
        if parsed_url.scheme == 'https' and hostname:
            try:
                result['ssl_info'] = self.check_ssl_expiry(hostname)
            except Exception as e:
                result['ssl_info'] = {'error': f'SSL check failed: {str(e)}'}
        
        return result
    
    def check_all_urls(self):
        """Check all URLs concurrently and return results."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.check_single_url, url): url for url in self.urls}
            
            for future in as_completed(future_to_url):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    url = future_to_url[future]
                    results.append({
                        'url': url,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'error': f'Future execution error: {str(e)}'
                    })
        
        return results
    
    def print_results(self, results):
        """Print formatted results to stdout."""
        print("=" * 80)
        print("WEBSITE HEALTH CHECK RESULTS")
        print("=" * 80)
        print()
        
        for result in results:
            print(f"URL: {result['url']}")
            print(f"Timestamp: {result['timestamp']}")
            
            if result.get('error'):
                print(f"❌ ERROR: {result['error']}")
            else:
                # Status code
                status = result.get('status_code')
                if status:
                    status_symbol = "✅" if 200 <= status < 300 else "⚠️" if 300 <= status < 400 else "❌"
                    print(f"{status_symbol} Status Code: {status}")
                
                # Response time
                response_time = result.get('response_time_ms')
                if response_time is not None:
                    time_symbol = "✅" if response_time < 1000 else "⚠️" if response_time < 3000 else "❌"
                    print(f"{time_symbol} Response Time: {response_time} ms")
                
                # SSL info
                ssl_info = result.get('ssl_info')
                if ssl_info:
                    if ssl_info.get('error'):
                        print(f"❌ SSL Error: {ssl_info['error']}")
                    else:
                        days_left = ssl_info.get('days_until_expiry')
                        if days_left is not None:
                            if ssl_info.get('expired'):
                                print(f"❌ SSL Certificate: EXPIRED ({abs(days_left)} days ago)")
                            elif days_left < 30:
                                print(f"⚠️ SSL Certificate: Expires in {days_left} days ({ssl_info['expiry_date']})")
                            else:
                                print(f"✅ SSL Certificate: Valid for {days_left} days ({ssl_info['expiry_date']})")
            
            print("-" * 40)
            print()


def main():
    # Configurable list of URLs to check
    urls_to_check = [
        'https://www.google.com',
        'https://www.github.com',
        'https://httpbin.org/status/200',
        'https://httpbin.org/delay/2',
        'https://expired.badssl.com',  # Expired SSL for testing
        'http://www.example.com',      # HTTP site
        'https://self-signed.badssl.com',  # Self-signed SSL for testing
    ]
    
    print("Starting website health check...")
    print(f"Checking {len(urls_to_check)} URLs...")
    print()
    
    checker = WebsiteHealthChecker(urls_to_check, timeout=15, max_workers=3)
    
    try:
        results = checker.check_all_urls()
        checker.print_results(results)
        
        # Summary
        total_checked = len(results)
        successful_checks = len([r for r in results if not r.get('error')])
        
        print("=" * 80)
        print(f"SUMMARY: {successful_checks}/{total_checked} URLs checked successfully")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nHealth check interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error during health check: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()