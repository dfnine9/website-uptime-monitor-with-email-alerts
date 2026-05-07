"""
Website Monitoring Script

This script monitors website uptime, response times, and SSL certificate expiration dates.
It reads URLs from a config.json file, performs HTTP requests to check availability,
verifies SSL certificates, and logs all results with timestamps to monitoring_results.json.

The script uses only standard library modules plus requests for HTTP operations.
Results are both logged to file and printed to stdout for real-time monitoring.

Usage: python script.py

Config format (config.json):
{
    "urls": ["https://example.com", "https://google.com"]
}
"""

import json
import ssl
import socket
import time
import datetime
import urllib.request
import urllib.error
from urllib.parse import urlparse

def load_config():
    """Load URLs from config.json file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('urls', [])
    except FileNotFoundError:
        print("Error: config.json not found. Creating example config.")
        example_config = {"urls": ["https://example.com", "https://google.com"]}
        with open('config.json', 'w') as f:
            json.dump(example_config, f, indent=2)
        return example_config['urls']
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json: {e}")
        return []

def check_ssl_expiry(hostname, port=443):
    """Check SSL certificate expiration date."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.datetime.now()).days
                return {
                    'expiry_date': expiry_date.isoformat(),
                    'days_until_expiry': days_until_expiry,
                    'status': 'valid' if days_until_expiry > 0 else 'expired'
                }
    except Exception as e:
        return {
            'expiry_date': None,
            'days_until_expiry': None,
            'status': f'error: {str(e)}'
        }

def check_url_status(url):
    """Check URL uptime and response time."""
    start_time = time.time()
    timestamp = datetime.datetime.now().isoformat()
    
    try:
        parsed_url = urlparse(url)
        
        # Create request with timeout
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Website-Monitor/1.0')
        
        with urllib.request.urlopen(request, timeout=10) as response:
            response_time = time.time() - start_time
            status_code = response.getcode()
            
            # Check SSL certificate if HTTPS
            ssl_info = {}
            if parsed_url.scheme == 'https':
                ssl_info = check_ssl_expiry(parsed_url.hostname)
            
            result = {
                'url': url,
                'timestamp': timestamp,
                'status': 'up',
                'status_code': status_code,
                'response_time': round(response_time, 3),
                'ssl_certificate': ssl_info
            }
            
    except urllib.error.HTTPError as e:
        response_time = time.time() - start_time
        result = {
            'url': url,
            'timestamp': timestamp,
            'status': 'http_error',
            'status_code': e.code,
            'response_time': round(response_time, 3),
            'error': str(e),
            'ssl_certificate': {}
        }
        
    except urllib.error.URLError as e:
        response_time = time.time() - start_time
        result = {
            'url': url,
            'timestamp': timestamp,
            'status': 'down',
            'status_code': None,
            'response_time': round(response_time, 3),
            'error': str(e),
            'ssl_certificate': {}
        }
        
    except Exception as e:
        response_time = time.time() - start_time
        result = {
            'url': url,
            'timestamp': timestamp,
            'status': 'error',
            'status_code': None,
            'response_time': round(response_time, 3),
            'error': str(e),
            'ssl_certificate': {}
        }
    
    return result

def load_existing_results():
    """Load existing monitoring results."""
    try:
        with open('monitoring_results.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_results(results):
    """Save results to monitoring_results.json."""
    try:
        existing_results = load_existing_results()
        existing_results.extend(results)
        
        with open('monitoring_results.json', 'w') as f:
            json.dump(existing_results, f, indent=2)
        
        print(f"Results saved to monitoring_results.json ({len(results)} new entries)")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def print_results(results):
    """Print monitoring results to stdout."""
    print("\n" + "="*80)
    print("WEBSITE MONITORING RESULTS")
    print("="*80)
    
    for result in results:
        print(f"\nURL: {result['url']}")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Status: {result['status']}")
        print(f"Status Code: {result['status_code']}")
        print(f"Response Time: {result['response_time']}s")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        ssl_info = result.get('ssl_certificate', {})
        if ssl_info:
            print(f"SSL Status: {ssl_info.get('status', 'N/A')}")
            if ssl_info.get('days_until_expiry') is not None:
                print(f"SSL Expires in: {ssl_info['days_until_expiry']} days")
        
        print("-" * 40)

def main():
    """Main monitoring function."""
    print("Starting website monitoring...")
    
    # Load URLs from config
    urls = load_config()
    
    if not urls:
        print("No URLs found in config. Exiting.")
        return
    
    print(f"Monitoring {len(urls)} URLs...")
    
    # Check each URL
    results = []
    for url in urls:
        print(f"Checking {url}...")
        result = check_url_status(url)
        results.append(result)
    
    # Print and save results
    print_results(results)
    save_results(results)
    
    print("\nMonitoring complete!")

if __name__ == "__main__":
    main()