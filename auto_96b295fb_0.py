```python
"""
Website Health Monitoring Script

This module reads a JSON configuration file containing website URLs, timeout settings,
and alert thresholds, then performs comprehensive health checks including:
- HTTP status code verification
- Response time measurement
- SSL certificate expiration date checking

The script outputs results to stdout with color-coded status indicators.

Configuration file format (config.json):
{
    "websites": [
        {
            "url": "https://example.com",
            "timeout": 10,
            "response_time_threshold": 2000,
            "ssl_expiry_warning_days": 30
        }
    ]
}

Usage: python script.py
"""

import json
import ssl
import socket
import time
import urllib.parse
from datetime import datetime, timedelta
from http.client import HTTPSConnection, HTTPConnection
from typing import Dict, List, Any, Optional, Tuple


def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_file}' not found")
        return {"websites": []}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return {"websites": []}


def check_ssl_expiry(hostname: str, port: int = 443) -> Optional[datetime]:
    """Check SSL certificate expiration date."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                return expiry_date
    except Exception as e:
        print(f"⚠️  SSL check failed for {hostname}: {e}")
        return None


def make_http_request(url: str, timeout: int) -> Tuple[Optional[int], Optional[float], Optional[str]]:
    """Make HTTP request and return status code, response time, and error if any."""
    parsed_url = urllib.parse.urlparse(url)
    hostname = parsed_url.hostname
    port = parsed_url.port
    path = parsed_url.path or '/'
    
    if parsed_url.query:
        path += '?' + parsed_url.query
    
    start_time = time.time()
    
    try:
        if parsed_url.scheme == 'https':
            port = port or 443
            conn = HTTPSConnection(hostname, port, timeout=timeout)
        else:
            port = port or 80
            conn = HTTPConnection(hostname, port, timeout=timeout)
        
        conn.request('GET', path)
        response = conn.getresponse()
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        status_code = response.status
        conn.close()
        
        return status_code, response_time, None
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return None, response_time, str(e)


def format_response_time(response_time: float) -> str:
    """Format response time with appropriate color coding."""
    if response_time < 500:
        return f"🟢 {response_time:.0f}ms"
    elif response_time < 2000:
        return f"🟡 {response_time:.0f}ms"
    else:
        return f"🔴 {response_time:.0f}ms"


def format_ssl_status(expiry_date: Optional[datetime], warning_days: int) -> str:
    """Format SSL certificate status with appropriate color coding."""
    if expiry_date is None:
        return "❌ SSL check failed"
    
    days_until_expiry = (expiry_date - datetime.now()).days
    
    if days_until_expiry < 0:
        return f"🔴 EXPIRED {abs(days_until_expiry)} days ago"
    elif days_until_expiry <= warning_days:
        return f"🟡 Expires in {days_until_expiry} days"
    else:
        return f"🟢 Valid for {days_until_expiry} days"


def format_status_code(status_code: Optional[int]) -> str:
    """Format HTTP status code with appropriate color coding."""
    if status_code is None:
        return "❌ Request failed"
    elif 200 <= status_code < 300:
        return f"🟢 {status_code}"
    elif 300 <= status_code < 400:
        return f"🟡 {status_code}"
    else:
        return f"🔴 {status_code}"


def check_website(site_config: Dict[str, Any]) -> None:
    """Check a single website's health and print results."""
    url = site_config.get('url')
    timeout = site_config.get('timeout', 10)
    response_time_threshold = site_config.get('response_time_threshold', 2000)
    ssl_warning_days = site_config.get('ssl_expiry_warning_days', 30)
    
    print(f"\n🔍 Checking: {url}")
    print("=" * (len(url) + 12))
    
    # HTTP Status and Response Time Check
    status_code, response_time, error = make_http_request(url, timeout)
    
    if error:
        print(f"❌ Request Error: {error}")
        if response_time:
            print(f"⏱️  Response Time: {format_response_time(response_time)}")
    else:
        print(f"📊 Status Code: {format_status_code(status_code)}")
        print(f"⏱️  Response Time: {format_response_time(response_time)}")
        
        # Check if response time exceeds threshold
        if response_time and response_time > response_time_threshold:
            print(f"⚠️  Response time exceeds threshold ({response_time_threshold}ms)")
    
    # SSL Certificate Check (only for HTTPS URLs)
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme == 'https':
        hostname = parsed_url.hostname
        port = parsed_url.port or 443
        expiry_date = check_ssl_expiry(hostname, port)
        print(f"🔒 SSL Status: {format_ssl_status(expiry_date, ssl_warning_days)}")
        
        if expiry_date:
            print(f"📅 Certificate Expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main function to orchestrate website health checks."""
    print("🌐 Website Health Monitor")
    print("=" * 25)
    
    config = load_config()
    websites = config.get('websites', [])
    
    if not websites:
        print("⚠️  No websites configured. Please create a config.json file.")
        print("\nExample config.json:")
        print(json.dumps({
            "websites": [
                {
                    "url": "https://example.com",
                    "timeout": 10,
                    "response_time_threshold": 2000,
                    "ssl_expiry_warning_days": 30
                }
            ]
        }, indent=2))
        return
    
    total_sites = len(websites)
    print(f"📋 Found {total_sites} website(s) to monitor\n")
    
    start_time = time.time()
    
    for i, site_config in enumerate(websites, 1):
        try:
            check_website(site_config)
        except Exception as e:
            print(f"❌ Unexpected error checking {site_config.get('url', 'unknown