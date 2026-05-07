#!/usr/bin/env python3
"""
URL Health Monitor

A self-contained script that monitors URL health by checking:
- HTTP response codes
- SSL certificate expiration dates
- Response times

Results are logged to a JSON file with timestamps and printed to stdout.
Only requires standard library plus httpx for HTTP requests.
"""

import json
import ssl
import socket
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, List, Any
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    sys.exit(1)


def get_ssl_cert_expiry(hostname: str, port: int = 443) -> str:
    """Get SSL certificate expiration date for a hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                return expiry_date.isoformat()
    except Exception as e:
        return f"SSL Error: {str(e)}"


def check_url_health(url: str) -> Dict[str, Any]:
    """Check health of a single URL including SSL certificate."""
    result = {
        'url': url,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status_code': None,
        'response_time_ms': None,
        'ssl_expiry': None,
        'error': None
    }
    
    try:
        # Parse URL to get hostname for SSL check
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        
        # Make HTTP request
        start_time = datetime.now()
        with httpx.Client(timeout=30.0, verify=True) as client:
            response = client.get(url, follow_redirects=True)
            end_time = datetime.now()
            
            result['status_code'] = response.status_code
            result['response_time_ms'] = int((end_time - start_time).total_seconds() * 1000)
            
            # Check SSL certificate if HTTPS
            if parsed.scheme.lower() == 'https' and hostname:
                port = parsed.port or 443
                result['ssl_expiry'] = get_ssl_cert_expiry(hostname, port)
                
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    """Main function to check URLs and log results."""
    # Default URLs to check - modify as needed
    urls_to_check = [
        'https://httpbin.org/get',
        'https://google.com',
        'https://github.com',
        'https://expired.badssl.com',  # Test expired SSL
        'http://httpbin.org/status/404'  # Test error status
    ]
    
    all_results = []
    
    print(f"Checking {len(urls_to_check)} URLs...")
    print("-" * 80)
    
    for url in urls_to_check:
        print(f"Checking: {url}")
        result = check_url_health(url)
        all_results.append(result)
        
        # Print result to stdout
        if result['error']:
            print(f"  ❌ Error: {result['error']}")
        else:
            status_icon = "✅" if result['status_code'] and result['status_code'] < 400 else "❌"
            print(f"  {status_icon} Status: {result['status_code']} | "
                  f"Response Time: {result['response_time_ms']}ms")
            
            if result['ssl_expiry'] and not result['ssl_expiry'].startswith('SSL Error'):
                try:
                    expiry = datetime.fromisoformat(result['ssl_expiry'].replace('Z', '+00:00'))
                    days_until_expiry = (expiry - datetime.now(timezone.utc)).days
                    ssl_icon = "✅" if days_until_expiry > 30 else "⚠️" if days_until_expiry > 0 else "❌"
                    print(f"  {ssl_icon} SSL expires in {days_until_expiry} days ({expiry.strftime('%Y-%m-%d')})")
                except:
                    print(f"  ⚠️ SSL: {result['ssl_expiry']}")
            elif result['ssl_expiry']:
                print(f"  ❌ {result['ssl_expiry']}")
        
        print()
    
    # Save to JSON file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'url_health_check_{timestamp}.json'
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'check_time': datetime.now(timezone.utc).isoformat(),
                'total_urls': len(urls_to_check),
                'results': all_results
            }, f, indent=2)
        
        print(f"Results saved to: {filename}")
        
    except Exception as e:
        print(f"Error saving results: {e}")
    
    # Summary
    successful_checks = sum(1 for r in all_results if not r['error'] and r['status_code'] and r['status_code'] < 400)
    print(f"\nSummary: {successful_checks}/{len(urls_to_check)} URLs healthy")


if __name__ == '__main__':
    main()