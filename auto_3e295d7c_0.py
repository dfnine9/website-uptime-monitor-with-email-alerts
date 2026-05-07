```python
"""
URL Health Check and SSL Certificate Monitor

This module performs comprehensive health checks on a list of URLs by:
1. Pinging URLs to collect response metrics (status codes, response times)
2. Checking SSL certificate expiration dates
3. Providing detailed reporting on URL accessibility and certificate validity

Dependencies: requests, ssl, socket (all standard library except requests)
Usage: python script.py
"""

import requests
import ssl
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse
import time


def check_ssl_certificate(hostname, port=443):
    """
    Check SSL certificate expiration date for a given hostname.
    
    Args:
        hostname (str): The hostname to check
        port (int): The port to connect to (default: 443)
    
    Returns:
        dict: Certificate information including expiration date and days until expiry
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Parse the certificate expiration date
                exp_date_str = cert['notAfter']
                exp_date = datetime.strptime(exp_date_str, '%b %d %H:%M:%S %Y %Z')
                exp_date = exp_date.replace(tzinfo=timezone.utc)
                
                # Calculate days until expiration
                now = datetime.now(timezone.utc)
                days_until_expiry = (exp_date - now).days
                
                return {
                    'valid': True,
                    'expiration_date': exp_date.isoformat(),
                    'days_until_expiry': days_until_expiry,
                    'expired': days_until_expiry < 0,
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer'])
                }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'expiration_date': None,
            'days_until_expiry': None,
            'expired': None
        }


def check_url_health(url, timeout=10):
    """
    Check URL health by making HTTP request and measuring response metrics.
    
    Args:
        url (str): The URL to check
        timeout (int): Request timeout in seconds
    
    Returns:
        dict: Response metrics including status code, response time, and headers
    """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response_time_ms': response_time,
            'content_length': len(response.content),
            'headers': dict(response.headers),
            'final_url': response.url,
            'redirected': url != response.url,
            'error': None
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'status_code': None,
            'response_time_ms': None,
            'error': 'Request timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'status_code': None,
            'response_time_ms': None,
            'error': 'Connection error'
        }
    except Exception as e:
        return {
            'success': False,
            'status_code': None,
            'response_time_ms': None,
            'error': str(e)
        }


def main():
    """Main function to run URL health checks and SSL certificate validation."""
    
    # List of URLs to check
    urls = [
        'https://www.google.com',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://httpbin.org/status/200',
        'https://httpbin.org/status/404',
        'https://httpbin.org/delay/2',
        'https://expired.badssl.com',  # Expired certificate for testing
        'https://self-signed.badssl.com',  # Self-signed certificate for testing
    ]
    
    print("=" * 80)
    print("URL HEALTH CHECK AND SSL CERTIFICATE MONITOR")
    print("=" * 80)
    print(f"Checking {len(urls)} URLs...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Checking: {url}")
        print("-" * 60)
        
        # Parse URL to get hostname
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        # Check URL health
        health_result = check_url_health(url)
        
        # Check SSL certificate if HTTPS
        ssl_result = None
        if parsed_url.scheme == 'https':
            ssl_result = check_ssl_certificate(hostname)
        
        # Store results
        result = {
            'url': url,
            'hostname': hostname,
            'health': health_result,
            'ssl': ssl_result
        }
        results.append(result)
        
        # Print health results
        if health_result['success']:
            print(f"✓ Status: {health_result['status_code']}")
            print(f"✓ Response Time: {health_result['response_time_ms']}ms")
            print(f"✓ Content Length: {health_result['content_length']} bytes")
            if health_result['redirected']:
                print(f"→ Redirected to: {health_result['final_url']}")
        else:
            print(f"✗ Error: {health_result['error']}")
        
        # Print SSL results
        if ssl_result:
            if ssl_result['valid']:
                print(f"🔒 SSL Certificate Valid")
                print(f"🔒 Expires: {ssl_result['expiration_date']}")
                print(f"🔒 Days until expiry: {ssl_result['days_until_expiry']}")
                if ssl_result['expired']:
                    print("⚠️  Certificate is EXPIRED!")
                elif ssl_result['days_until_expiry'] < 30:
                    print("⚠️  Certificate expires soon!")
                print(f"🔒 Subject: {ssl_result['subject'].get('commonName', 'N/A')}")
                print(f"🔒 Issuer: {ssl_result['issuer'].get('organizationName', 'N/A')}")
            else:
                print(f"✗ SSL Error: {ssl_result['error']}")
        
        print()
    
    # Print summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful_requests = sum(1 for r in results if r['health']['success'])
    failed_requests = len(results) - successful_requests
    
    valid_certificates = sum(1 for r in results if r['ssl'] and r['ssl']['valid'])
    invalid_certificates = sum(1 for r in results if r['ssl'] and not r['ssl']['valid'])
    
    print(f"Total URLs checked: {len(results)}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Valid SSL certificates: {valid_certificates}")
    print(f"Invalid SSL certificates: {invalid_certificates}")
    
    # Show fastest and slowest response times
    successful_results = [r for r in results if r['health']['success']]
    if successful_results:
        fastest = min(successful_results, key=lambda x: x['health']['response_time