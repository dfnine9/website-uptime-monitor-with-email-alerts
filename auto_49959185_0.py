#!/usr/bin/env python3
"""
URL Health Monitor

This module monitors the health of multiple URLs by:
- Pinging URLs and measuring response times
- Checking SSL certificate expiration dates
- Storing all metrics in a timestamped JSON file
- Providing real-time stdout output

Dependencies: httpx (pip install httpx)
Usage: python script.py
"""

import json
import ssl
import socket
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
import httpx


def check_ssl_expiry(hostname, port=443, timeout=10):
    """Check SSL certificate expiration date for a given hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                days_until_expiry = (expiry_date - datetime.now(timezone.utc)).days
                return {
                    'expiry_date': expiry_date.isoformat(),
                    'days_until_expiry': days_until_expiry,
                    'is_expired': days_until_expiry < 0,
                    'expires_soon': days_until_expiry < 30
                }
    except Exception as e:
        return {
            'error': str(e),
            'expiry_date': None,
            'days_until_expiry': None,
            'is_expired': None,
            'expires_soon': None
        }


def ping_url(url, timeout=10):
    """Ping a URL and measure response metrics."""
    try:
        start_time = time.time()
        
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, follow_redirects=True)
            
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        # Check SSL if HTTPS
        ssl_info = {}
        if parsed_url.scheme == 'https':
            ssl_info = check_ssl_expiry(hostname)
        
        return {
            'url': url,
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2),
            'is_success': 200 <= response.status_code < 300,
            'content_length': len(response.content) if response.content else 0,
            'headers': dict(response.headers),
            'ssl_info': ssl_info,
            'error': None
        }
        
    except httpx.TimeoutException:
        return {
            'url': url,
            'status_code': None,
            'response_time_ms': timeout * 1000,
            'is_success': False,
            'content_length': 0,
            'headers': {},
            'ssl_info': {},
            'error': 'Request timeout'
        }
    except Exception as e:
        return {
            'url': url,
            'status_code': None,
            'response_time_ms': None,
            'is_success': False,
            'content_length': 0,
            'headers': {},
            'ssl_info': {},
            'error': str(e)
        }


def monitor_urls(urls):
    """Monitor multiple URLs and return comprehensive health metrics."""
    timestamp = datetime.now(timezone.utc).isoformat()
    results = []
    
    print(f"Starting URL health check at {timestamp}")
    print("=" * 60)
    
    for url in urls:
        print(f"Checking: {url}")
        result = ping_url(url)
        results.append(result)
        
        # Print summary
        if result['is_success']:
            status = f"✓ {result['status_code']} ({result['response_time_ms']}ms)"
        else:
            status = f"✗ {result.get('error', 'Failed')}"
        
        print(f"  Result: {status}")
        
        # Print SSL info if available
        if result['ssl_info'] and 'days_until_expiry' in result['ssl_info']:
            ssl = result['ssl_info']
            if ssl['days_until_expiry'] is not None:
                if ssl['is_expired']:
                    print(f"  SSL: ✗ EXPIRED")
                elif ssl['expires_soon']:
                    print(f"  SSL: ⚠ Expires in {ssl['days_until_expiry']} days")
                else:
                    print(f"  SSL: ✓ Valid ({ssl['days_until_expiry']} days)")
        
        print()
    
    # Create final report structure
    report = {
        'timestamp': timestamp,
        'summary': {
            'total_urls': len(urls),
            'successful': sum(1 for r in results if r['is_success']),
            'failed': sum(1 for r in results if not r['is_success']),
            'avg_response_time_ms': round(
                sum(r['response_time_ms'] for r in results if r['response_time_ms']) / 
                len([r for r in results if r['response_time_ms']]), 2
            ) if any(r['response_time_ms'] for r in results) else 0
        },
        'results': results
    }
    
    return report


def main():
    """Main function to execute URL health monitoring."""
    # Default URLs to monitor (can be customized)
    urls_to_monitor = [
        'https://httpbin.org/get',
        'https://jsonplaceholder.typicode.com/posts/1',
        'https://api.github.com',
        'https://www.google.com',
        'https://httpstat.us/200'
    ]
    
    try:
        # Monitor URLs
        report = monitor_urls(urls_to_monitor)
        
        # Save to JSON file
        output_file = f"url_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("=" * 60)
        print("SUMMARY REPORT")
        print("=" * 60)
        print(f"Total URLs: {report['summary']['total_urls']}")
        print(f"Successful: {report['summary']['successful']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Average Response Time: {report['summary']['avg_response_time_ms']}ms")
        print(f"Report saved to: {output_file}")
        
    except Exception as e:
        print(f"Error running health check: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())