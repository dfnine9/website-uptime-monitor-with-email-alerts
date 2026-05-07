```python
#!/usr/bin/env python3
"""
URL Health Checker

This script reads URLs from a configuration file and performs comprehensive health checks
including HTTP status codes, response times, and SSL certificate validation.

Features:
- Reads URLs from 'urls.txt' configuration file (one URL per line)
- Checks HTTP status codes and response times
- Validates SSL certificates and expiration dates
- Handles various error conditions gracefully
- Outputs results to stdout in a formatted manner

Usage: python script.py

Requirements:
- httpx library for HTTP requests
- Standard library modules for SSL and configuration handling
"""

import ssl
import socket
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import httpx


def load_urls(config_file='urls.txt'):
    """Load URLs from configuration file."""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            # Create sample config if it doesn't exist
            sample_urls = [
                'https://httpbin.org/status/200',
                'https://google.com',
                'https://github.com',
                'https://httpbin.org/delay/2'
            ]
            config_path.write_text('\n'.join(sample_urls))
            print(f"Created sample config file: {config_file}")
        
        with open(config_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except Exception as e:
        print(f"Error loading config file: {e}")
        return []


def get_ssl_info(hostname, port=443):
    """Get SSL certificate information for a hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Parse expiration date
                not_after = cert.get('notAfter')
                if not_after:
                    exp_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    exp_date = exp_date.replace(tzinfo=timezone.utc)
                    days_until_expiry = (exp_date - datetime.now(timezone.utc)).days
                else:
                    days_until_expiry = None
                
                return {
                    'valid': True,
                    'issuer': dict(x[0] for x in cert.get('issuer', [])),
                    'subject': dict(x[0] for x in cert.get('subject', [])),
                    'expires': not_after,
                    'days_until_expiry': days_until_expiry,
                    'version': cert.get('version'),
                }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }


def check_url(url):
    """Perform comprehensive health check on a single URL."""
    result = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'status_code': None,
        'response_time': None,
        'ssl_info': None,
        'error': None
    }
    
    try:
        # Parse URL to extract hostname for SSL check
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        # Make HTTP request and measure response time
        start_time = time.time()
        with httpx.Client(timeout=30.0, verify=True) as client:
            response = client.get(url, follow_redirects=True)
            response_time = time.time() - start_time
            
            result['status_code'] = response.status_code
            result['response_time'] = round(response_time * 1000, 2)  # Convert to ms
            result['headers'] = dict(response.headers)
            result['final_url'] = str(response.url)
        
        # Get SSL information for HTTPS URLs
        if parsed.scheme == 'https' and hostname:
            port = parsed.port or 443
            result['ssl_info'] = get_ssl_info(hostname, port)
            
    except httpx.TimeoutException:
        result['error'] = 'Request timeout'
    except httpx.ConnectError:
        result['error'] = 'Connection failed'
    except httpx.HTTPStatusError as e:
        result['error'] = f'HTTP error: {e}'
    except Exception as e:
        result['error'] = str(e)
    
    return result


def format_result(result):
    """Format a single result for display."""
    url = result['url']
    print(f"\n{'='*60}")
    print(f"URL: {url}")
    print(f"Timestamp: {result['timestamp']}")
    
    if result['error']:
        print(f"❌ ERROR: {result['error']}")
        return
    
    # Status and timing
    status = result['status_code']
    response_time = result['response_time']
    
    status_emoji = "✅" if 200 <= status < 300 else "⚠️" if 300 <= status < 400 else "❌"
    print(f"{status_emoji} Status: {status}")
    print(f"⏱️  Response Time: {response_time}ms")
    
    if result.get('final_url') != url:
        print(f"🔄 Redirected to: {result['final_url']}")
    
    # SSL Information
    ssl_info = result.get('ssl_info')
    if ssl_info:
        if ssl_info['valid']:
            print(f"🔒 SSL Certificate: Valid")
            issuer = ssl_info.get('issuer', {})
            if 'organizationName' in issuer:
                print(f"   Issuer: {issuer['organizationName']}")
            if ssl_info.get('expires'):
                print(f"   Expires: {ssl_info['expires']}")
                days = ssl_info.get('days_until_expiry')
                if days is not None:
                    if days > 30:
                        print(f"   Days until expiry: {days} ✅")
                    elif days > 7:
                        print(f"   Days until expiry: {days} ⚠️")
                    else:
                        print(f"   Days until expiry: {days} ❌")
        else:
            print(f"🔓 SSL Certificate: Invalid - {ssl_info.get('error', 'Unknown error')}")


def main():
    """Main execution function."""
    print("🌐 URL Health Checker Starting...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Load URLs from config
    urls = load_urls()
    if not urls:
        print("❌ No URLs to check. Please add URLs to urls.txt file.")
        return
    
    print(f"\n📋 Checking {len(urls)} URLs...")
    
    # Check each URL
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Checking: {url}")
        result = check_url(url)
        results.append(result)
        format_result(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    successful = len([r for r in results if r['error'] is None and 200 <= (r['status_code'] or 0) < 300])
    failed = total - successful
    
    print(f"Total URLs checked: {total}")
    print(f"Successful: {successful} ✅")
    print(f"Failed: {failed} ❌")
    
    if results:
        avg_response_time = sum(r['response_time'] for r in results if r['response_time']) / len([r for r in results