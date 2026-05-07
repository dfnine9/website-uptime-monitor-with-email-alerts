```python
#!/usr/bin/env python3
"""
Website Health Monitor

This script reads URLs from a JSON configuration file and performs comprehensive
health checks on each website including:
- HTTP status code verification
- Response time measurement  
- SSL certificate expiration date validation

The script uses only standard library modules (json, ssl, socket, urllib, time)
to ensure maximum compatibility and minimal dependencies.

Usage: python script.py

Expected JSON config format:
{
    "urls": [
        "https://example.com",
        "https://google.com",
        "https://github.com"
    ]
}
"""

import json
import ssl
import socket
import urllib.request
import urllib.error
import time
from datetime import datetime
import sys
import os


def load_config(config_file='config.json'):
    """Load URLs from JSON configuration file."""
    try:
        if not os.path.exists(config_file):
            # Create default config if it doesn't exist
            default_config = {
                "urls": [
                    "https://httpbin.org/status/200",
                    "https://google.com",
                    "https://github.com"
                ]
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file: {config_file}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('urls', [])
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading config file: {e}")
        return []


def check_http_status(url, timeout=10):
    """Check HTTP status code and measure response time."""
    try:
        start_time = time.time()
        
        # Create request with proper headers
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Website-Health-Monitor/1.0')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # Convert to ms
            status_code = response.getcode()
            
        return {
            'status_code': status_code,
            'response_time_ms': response_time,
            'success': True,
            'error': None
        }
        
    except urllib.error.HTTPError as e:
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        return {
            'status_code': e.code,
            'response_time_ms': response_time,
            'success': False,
            'error': f"HTTP Error: {e.code} {e.reason}"
        }
        
    except urllib.error.URLError as e:
        return {
            'status_code': None,
            'response_time_ms': None,
            'success': False,
            'error': f"URL Error: {str(e.reason)}"
        }
        
    except Exception as e:
        return {
            'status_code': None,
            'response_time_ms': None,
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }


def check_ssl_certificate(hostname, port=443, timeout=10):
    """Check SSL certificate expiration date."""
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        
        # Parse expiration date
        not_after = cert['notAfter']
        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
        
        # Calculate days until expiration
        days_until_expiry = (expiry_date - datetime.now()).days
        
        return {
            'expiry_date': expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
            'days_until_expiry': days_until_expiry,
            'is_expired': days_until_expiry < 0,
            'success': True,
            'error': None
        }
        
    except ssl.SSLError as e:
        return {
            'expiry_date': None,
            'days_until_expiry': None,
            'is_expired': None,
            'success': False,
            'error': f"SSL Error: {str(e)}"
        }
        
    except socket.error as e:
        return {
            'expiry_date': None,
            'days_until_expiry': None,
            'is_expired': None,
            'success': False,
            'error': f"Socket Error: {str(e)}"
        }
        
    except Exception as e:
        return {
            'expiry_date': None,
            'days_until_expiry': None,
            'is_expired': None,
            'success': False,
            'error': f"Certificate check failed: {str(e)}"
        }


def extract_hostname(url):
    """Extract hostname from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.hostname
    except Exception:
        return None


def format_status_indicator(success, value=None):
    """Format status indicator with color coding."""
    if success:
        return f"✅ {value}" if value else "✅"
    else:
        return "❌"


def main():
    """Main execution function."""
    print("=" * 60)
    print("         WEBSITE HEALTH MONITOR")
    print("=" * 60)
    print()
    
    # Load URLs from config
    urls = load_config()
    
    if not urls:
        print("No URLs found in configuration. Exiting.")
        sys.exit(1)
    
    print(f"Checking {len(urls)} websites...\n")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Checking: {url}")
        print("-" * 50)
        
        # Check HTTP status
        http_result = check_http_status(url)
        
        # Extract hostname for SSL check
        hostname = extract_hostname(url)
        ssl_result = None
        
        if hostname and url.startswith('https://'):
            ssl_result = check_ssl_certificate(hostname)
        
        # Display results
        if http_result['success']:
            status_indicator = format_status_indicator(True, http_result['status_code'])
            print(f"HTTP Status:     {status_indicator}")
            print(f"Response Time:   {http_result['response_time_ms']} ms")
        else:
            print(f"HTTP Status:     {format_status_indicator(False)}")
            print(f"Error:           {http_result['error']}")
        
        if ssl_result:
            if ssl_result['success']:
                ssl_status = "✅ Valid"
                if ssl_result['days_until_expiry'] < 30:
                    ssl_status = f"⚠️  Expires soon ({ssl_result['days_until_expiry']} days)"
                elif ssl_result['is_expired']:
                    ssl_status = "❌ Expired"
                
                print(f"SSL Certificate: {ssl_status}")
                print(f"Expires:         {ssl_result['expiry_date']}")
                print(f"Days remaining:  {ssl_result['days_until_expiry']}")
            else:
                print(f"SSL Certificate: {format_status_indicator(False)}")
                print(f"Error:           {ssl_result['error']}")
        elif url.startswith('https://'):
            print("SSL Certificate: ❌ Could not verify")
        else:
            print("SSL Certificate: N/A (HTTP)")