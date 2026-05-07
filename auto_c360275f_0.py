#!/usr/bin/env python3
"""
Website Health Monitor

This script monitors website uptime, response times, and SSL certificate expiry dates.
It checks a predefined list of URLs and reports:
- HTTP status codes and response times
- SSL certificate validity and expiration dates
- Connection errors and timeouts

Dependencies: requests (install with: pip install requests)
Usage: python script.py
"""

import ssl
import socket
import datetime
import requests
from urllib.parse import urlparse
import time


def check_ssl_certificate(hostname, port=443):
    """
    Check SSL certificate expiry date for a given hostname.
    
    Args:
        hostname (str): The hostname to check
        port (int): The port to connect to (default 443)
    
    Returns:
        dict: Certificate information including expiry date and days until expiry
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Parse expiry date
                expiry_date_str = cert['notAfter']
                expiry_date = datetime.datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
                
                # Calculate days until expiry
                days_until_expiry = (expiry_date - datetime.datetime.now()).days
                
                return {
                    'valid': True,
                    'expiry_date': expiry_date,
                    'days_until_expiry': days_until_expiry,
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer'])
                }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }


def check_website_health(url):
    """
    Check website uptime and response time.
    
    Args:
        url (str): The URL to check
    
    Returns:
        dict: Health check results including status code, response time, and SSL info
    """
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    
    result = {
        'url': url,
        'hostname': hostname,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # Check HTTP health
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10, verify=True)
        end_time = time.time()
        
        result.update({
            'status_code': response.status_code,
            'response_time_ms': round((end_time - start_time) * 1000, 2),
            'accessible': True,
            'headers': dict(response.headers)
        })
        
    except requests.exceptions.RequestException as e:
        result.update({
            'accessible': False,
            'error': str(e),
            'status_code': None,
            'response_time_ms': None
        })
    
    # Check SSL certificate if HTTPS
    if parsed_url.scheme == 'https':
        ssl_info = check_ssl_certificate(hostname)
        result['ssl'] = ssl_info
    
    return result


def print_results(results):
    """
    Print formatted results to stdout.
    
    Args:
        results (list): List of health check results
    """
    print("=" * 80)
    print("WEBSITE HEALTH MONITOR REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Hostname: {result['hostname']}")
        
        if result['accessible']:
            print(f"✓ Status: {result['status_code']} - Accessible")
            print(f"✓ Response Time: {result['response_time_ms']} ms")
        else:
            print(f"✗ Status: Inaccessible")
            print(f"✗ Error: {result['error']}")
        
        # SSL Certificate info
        if 'ssl' in result:
            ssl_info = result['ssl']
            if ssl_info['valid']:
                expiry_date = ssl_info['expiry_date'].strftime('%Y-%m-%d')
                days_left = ssl_info['days_until_expiry']
                
                if days_left > 30:
                    status_icon = "✓"
                elif days_left > 7:
                    status_icon = "⚠"
                else:
                    status_icon = "✗"
                
                print(f"{status_icon} SSL Certificate: Valid until {expiry_date} ({days_left} days)")
                print(f"  Issued by: {ssl_info['issuer'].get('organizationName', 'Unknown')}")
            else:
                print(f"✗ SSL Certificate: Invalid - {ssl_info['error']}")
        
        print("-" * 80)


def main():
    """
    Main function to run the website health monitor.
    """
    # List of URLs to monitor
    target_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://httpbin.org/status/200",
        "https://httpbin.org/delay/2",
        "http://example.com",
        "https://expired.badssl.com",  # Example of expired SSL
    ]
    
    print("Starting website health checks...")
    print(f"Monitoring {len(target_urls)} URLs...")
    print()
    
    results = []
    
    for i, url in enumerate(target_urls, 1):
        print(f"Checking {i}/{len(target_urls)}: {url}")
        try:
            result = check_website_health(url)
            results.append(result)
        except Exception as e:
            print(f"Unexpected error checking {url}: {e}")
            results.append({
                'url': url,
                'hostname': urlparse(url).hostname,
                'accessible': False,
                'error': f"Unexpected error: {e}",
                'timestamp': datetime.datetime.now().isoformat()
            })
    
    print("\nHealth checks completed!")
    print_results(results)
    
    # Summary
    accessible_count = sum(1 for r in results if r['accessible'])
    print(f"\nSUMMARY:")
    print(f"Total URLs checked: {len(results)}")
    print(f"Accessible: {accessible_count}")
    print(f"Inaccessible: {len(results) - accessible_count}")
    
    # SSL Certificate warnings
    ssl_warnings = []
    for result in results:
        if 'ssl' in result and result['ssl']['valid']:
            days_left = result['ssl']['days_until_expiry']
            if days_left <= 30:
                ssl_warnings.append(f"{result['hostname']}: {days_left} days")
    
    if ssl_warnings:
        print(f"\nSSL CERTIFICATE WARNINGS:")
        for warning in ssl_warnings:
            print(f"⚠ {warning}")


if __name__ == "__main__":
    main()