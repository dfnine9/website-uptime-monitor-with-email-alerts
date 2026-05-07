"""
HTTP Health Checker and SSL Certificate Validator

This module provides functionality to monitor multiple URLs by:
- Checking HTTP status codes
- Measuring response times
- Validating SSL certificate expiration dates
- Logging all results to timestamped JSON files

Dependencies: requests, ssl, socket (standard library)
Usage: python script.py
"""

import json
import time
import ssl
import socket
import datetime
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def check_ssl_expiry(hostname, port=443):
    """Check SSL certificate expiration date for a given hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.datetime.now()).days
                return {
                    'expiry_date': cert['notAfter'],
                    'days_until_expiry': days_until_expiry,
                    'is_valid': days_until_expiry > 0
                }
    except Exception as e:
        return {
            'error': str(e),
            'expiry_date': None,
            'days_until_expiry': None,
            'is_valid': False
        }

def ping_url(url, timeout=10):
    """Ping a URL and return status code, response time, and SSL info."""
    try:
        # Configure session with retries
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        start_time = time.time()
        response = session.get(url, timeout=timeout, allow_redirects=True)
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'response_time_ms': response_time,
            'success': True,
            'error': None,
            'ssl_info': None
        }
        
        # Check SSL certificate if HTTPS
        if url.startswith('https://'):
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            result['ssl_info'] = check_ssl_expiry(hostname)
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status_code': None,
            'response_time_ms': None,
            'success': False,
            'error': str(e),
            'ssl_info': None
        }
    except Exception as e:
        return {
            'url': url,
            'status_code': None,
            'response_time_ms': None,
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'ssl_info': None
        }

def main():
    """Main function to check multiple URLs and save results."""
    # List of URLs to check
    urls = [
        'https://www.google.com',
        'https://www.github.com',
        'https://httpbin.org/status/200',
        'https://httpbin.org/delay/2',
        'http://httpbin.org/status/404',
        'https://expired.badssl.com',  # For SSL testing
        'https://self-signed.badssl.com'  # For SSL testing
    ]
    
    print("Starting HTTP Health Check...")
    print(f"Checking {len(urls)} URLs...")
    print("-" * 50)
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Checking: {url}")
        result = ping_url(url)
        results.append(result)
        
        # Print immediate results
        if result['success']:
            print(f"  ✓ Status: {result['status_code']} | Response: {result['response_time_ms']}ms")
            if result['ssl_info']:
                ssl_status = "Valid" if result['ssl_info']['is_valid'] else "Invalid/Expired"
                days = result['ssl_info'].get('days_until_expiry', 'Unknown')
                print(f"  🔒 SSL: {ssl_status} | Days until expiry: {days}")
        else:
            print(f"  ✗ Error: {result['error']}")
        print()
    
    # Create summary
    summary = {
        'timestamp': datetime.datetime.now().isoformat(),
        'total_urls': len(urls),
        'successful_checks': sum(1 for r in results if r['success']),
        'failed_checks': sum(1 for r in results if not r['success']),
        'average_response_time_ms': round(
            sum(r['response_time_ms'] for r in results if r['response_time_ms']) / 
            len([r for r in results if r['response_time_ms']]), 2
        ) if any(r['response_time_ms'] for r in results) else 0,
        'ssl_issues': sum(1 for r in results if r['ssl_info'] and not r['ssl_info']['is_valid']),
        'results': results
    }
    
    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"health_check_{timestamp}.json"
    
    # Save to JSON file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total URLs checked: {summary['total_urls']}")
    print(f"Successful checks: {summary['successful_checks']}")
    print(f"Failed checks: {summary['failed_checks']}")
    print(f"Average response time: {summary['average_response_time_ms']}ms")
    print(f"SSL issues detected: {summary['ssl_issues']}")
    print(f"Results saved to: {filename}")

if __name__ == "__main__":
    main()