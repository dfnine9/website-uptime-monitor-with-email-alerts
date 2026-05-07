#!/usr/bin/env python3
"""
Website Monitoring Script

This script monitors a configurable list of URLs by:
- Making HTTP requests and measuring response times
- Checking HTTP status codes
- Validating SSL certificate expiration dates
- Saving all monitoring results to a structured JSON file

The script uses only standard library modules plus httpx for HTTP requests.
Results are printed to stdout and saved to monitoring_results.json.

Usage: python script.py
"""

import json
import ssl
import socket
import time
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, List, Any
import httpx


def check_ssl_certificate(hostname: str, port: int = 443) -> Dict[str, Any]:
    """Check SSL certificate expiration date for a hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Parse the expiration date
                not_after = cert['notAfter']
                expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                
                # Calculate days until expiration
                now = datetime.now(timezone.utc)
                days_until_expiry = (expiry_date - now).days
                
                return {
                    'valid': True,
                    'expiry_date': expiry_date.isoformat(),
                    'days_until_expiry': days_until_expiry,
                    'expired': days_until_expiry < 0,
                    'error': None
                }
    except Exception as e:
        return {
            'valid': False,
            'expiry_date': None,
            'days_until_expiry': None,
            'expired': None,
            'error': str(e)
        }


def monitor_url(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Monitor a single URL and return comprehensive monitoring data."""
    start_time = time.time()
    result = {
        'url': url,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'response_time_ms': None,
        'status_code': None,
        'status_text': None,
        'ssl_info': None,
        'error': None,
        'accessible': False
    }
    
    try:
        # Parse URL to get hostname for SSL check
        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.hostname
        
        # Make HTTP request
        with httpx.Client(timeout=timeout, verify=False) as client:
            response = client.get(url)
            end_time = time.time()
            
            # Calculate response time
            response_time_ms = round((end_time - start_time) * 1000, 2)
            
            result.update({
                'response_time_ms': response_time_ms,
                'status_code': response.status_code,
                'status_text': response.reason_phrase,
                'accessible': response.status_code < 400
            })
            
            # Check SSL certificate if HTTPS
            if parsed_url.scheme == 'https' and hostname:
                port = parsed_url.port or 443
                result['ssl_info'] = check_ssl_certificate(hostname, port)
                
    except Exception as e:
        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        result.update({
            'response_time_ms': response_time_ms,
            'error': str(e),
            'accessible': False
        })
    
    return result


def main():
    """Main monitoring function."""
    # Configurable list of URLs to monitor
    urls_to_monitor = [
        'https://google.com',
        'https://github.com',
        'https://stackoverflow.com',
        'https://python.org',
        'https://httpbin.org/status/200',
        'https://httpbin.org/status/404',
        'https://httpbin.org/delay/2',
        'http://httpbin.org/get',
        'https://expired.badssl.com',  # For SSL testing
        'https://wrong.host.badssl.com'  # For SSL testing
    ]
    
    print("Starting website monitoring...")
    print(f"Monitoring {len(urls_to_monitor)} URLs")
    print("-" * 50)
    
    monitoring_results = []
    
    for i, url in enumerate(urls_to_monitor, 1):
        print(f"[{i}/{len(urls_to_monitor)}] Checking {url}...")
        
        try:
            result = monitor_url(url)
            monitoring_results.append(result)
            
            # Print summary to stdout
            status = "✓" if result['accessible'] else "✗"
            print(f"  {status} Status: {result['status_code']} | "
                  f"Response: {result['response_time_ms']}ms")
            
            if result['ssl_info']:
                ssl_status = "✓" if result['ssl_info']['valid'] and not result['ssl_info']['expired'] else "✗"
                days = result['ssl_info']['days_until_expiry']
                print(f"  {ssl_status} SSL: {days} days until expiry" if days else f"  {ssl_status} SSL: Invalid")
            
            if result['error']:
                print(f"  ⚠ Error: {result['error']}")
                
        except Exception as e:
            print(f"  ✗ Failed to monitor {url}: {e}")
            monitoring_results.append({
                'url': url,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e),
                'accessible': False
            })
        
        print()
    
    # Save results to JSON file
    output_file = 'monitoring_results.json'
    summary = {
        'monitoring_run': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_urls': len(urls_to_monitor),
            'successful_checks': sum(1 for r in monitoring_results if r['accessible']),
            'failed_checks': sum(1 for r in monitoring_results if not r['accessible'])
        },
        'results': monitoring_results
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Failed to save results: {e}")
    
    # Print summary
    print("\nMonitoring Summary:")
    print(f"Total URLs: {summary['monitoring_run']['total_urls']}")
    print(f"Successful: {summary['monitoring_run']['successful_checks']}")
    print(f"Failed: {summary['monitoring_run']['failed_checks']}")
    
    # Show SSL warnings
    ssl_warnings = []
    for result in monitoring_results:
        if result.get('ssl_info') and result['ssl_info']['valid']:
            days = result['ssl_info']['days_until_expiry']
            if days is not None and days < 30:
                ssl_warnings.append(f"{result['url']} - SSL expires in {days} days")
    
    if ssl_warnings:
        print("\nSSL Certificate Warnings:")
        for warning in ssl_warnings:
            print(f"  ⚠ {warning}")


if __name__ == "__main__":
    main()