#!/usr/bin/env python3
"""
Website Health Monitor

This script monitors website health by performing the following checks:
1. HTTP/HTTPS requests to configurable URLs
2. Response time measurement
3. HTTP status code validation
4. SSL certificate expiry date extraction
5. Timestamped JSON logging

The script uses only standard library modules plus httpx for HTTP requests.
All results are saved to timestamped JSON files and printed to stdout.

Usage: python script.py
"""

import json
import ssl
import socket
import time
import datetime
from urllib.parse import urlparse
from pathlib import Path
import httpx


def get_ssl_expiry(hostname, port=443, timeout=10):
    """Extract SSL certificate expiry date for a given hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                return {
                    'expiry_date': expiry_date.isoformat(),
                    'days_until_expiry': (expiry_date - datetime.datetime.now()).days,
                    'is_expired': expiry_date < datetime.datetime.now()
                }
    except Exception as e:
        return {
            'error': str(e),
            'expiry_date': None,
            'days_until_expiry': None,
            'is_expired': None
        }


def check_url(url, timeout=30):
    """Perform health check on a single URL."""
    start_time = time.time()
    result = {
        'url': url,
        'timestamp': datetime.datetime.now().isoformat(),
        'response_time_ms': None,
        'status_code': None,
        'status_text': None,
        'ssl_info': None,
        'error': None
    }
    
    try:
        with httpx.Client(timeout=timeout, verify=True) as client:
            response = client.get(url, follow_redirects=True)
            
        end_time = time.time()
        result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        result['status_code'] = response.status_code
        result['status_text'] = response.reason_phrase
        
        # Extract SSL info for HTTPS URLs
        parsed_url = urlparse(url)
        if parsed_url.scheme == 'https':
            hostname = parsed_url.hostname
            port = parsed_url.port or 443
            result['ssl_info'] = get_ssl_expiry(hostname, port)
            
    except Exception as e:
        end_time = time.time()
        result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        result['error'] = str(e)
    
    return result


def main():
    """Main execution function."""
    # Configurable list of URLs to monitor
    urls_to_check = [
        'https://httpbin.org/get',
        'https://github.com',
        'https://stackoverflow.com',
        'http://httpbin.org/status/200',
        'https://expired.badssl.com',  # Intentionally expired SSL
        'https://wrong.host.badssl.com'  # SSL hostname mismatch
    ]
    
    print("Website Health Monitor")
    print("=" * 50)
    print(f"Checking {len(urls_to_check)} URLs...")
    print()
    
    results = []
    
    for i, url in enumerate(urls_to_check, 1):
        print(f"[{i}/{len(urls_to_check)}] Checking: {url}")
        
        try:
            result = check_url(url)
            results.append(result)
            
            # Print summary to stdout
            status = "✓" if result['status_code'] and 200 <= result['status_code'] < 300 else "✗"
            print(f"    {status} Status: {result['status_code']} ({result['status_text']})")
            print(f"    ⏱ Response Time: {result['response_time_ms']}ms")
            
            if result['ssl_info']:
                ssl_status = "✓" if not result['ssl_info'].get('is_expired') else "✗"
                days = result['ssl_info'].get('days_until_expiry')
                if days is not None:
                    print(f"    {ssl_status} SSL: {days} days until expiry")
                else:
                    print(f"    ✗ SSL: {result['ssl_info'].get('error', 'Unknown error')}")
            
            if result['error']:
                print(f"    ✗ Error: {result['error']}")
                
        except Exception as e:
            error_result = {
                'url': url,
                'timestamp': datetime.datetime.now().isoformat(),
                'error': f"Unexpected error: {str(e)}",
                'response_time_ms': None,
                'status_code': None,
                'status_text': None,
                'ssl_info': None
            }
            results.append(error_result)
            print(f"    ✗ Unexpected Error: {str(e)}")
        
        print()
    
    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"website_health_{timestamp}.json"
    
    # Save results to JSON file
    try:
        output_data = {
            'scan_timestamp': datetime.datetime.now().isoformat(),
            'total_urls': len(urls_to_check),
            'results': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {filename}")
        
        # Print summary statistics
        successful = sum(1 for r in results if r['status_code'] and 200 <= r['status_code'] < 300)
        failed = len(results) - successful
        avg_response_time = sum(r['response_time_ms'] for r in results if r['response_time_ms']) / len(results)
        
        print(f"\nSummary:")
        print(f"  Total URLs: {len(results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Average Response Time: {avg_response_time:.2f}ms")
        
    except Exception as e:
        print(f"Error saving results: {str(e)}")


if __name__ == "__main__":
    main()