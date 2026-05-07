```python
#!/usr/bin/env python3
"""
Website Monitoring Report Generator

This script analyzes website monitoring data from monitoring_results.json and generates
comprehensive reports including:
- Uptime percentages over configurable time periods
- Average response times
- SSL certificate expiration warnings (within 30 days)

The script is self-contained and requires only standard library modules plus httpx
and anthropic (though these are not used in the actual implementation).

Usage: python script.py
"""

import json
import ssl
import socket
import datetime
from urllib.parse import urlparse
from statistics import mean
from typing import Dict, List, Any, Optional


def load_monitoring_data(filename: str = "monitoring_results.json") -> Optional[Dict[str, Any]]:
    """Load monitoring data from JSON file with error handling."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filename}: {e}")
        return None
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None


def parse_timestamp(timestamp_str: str) -> Optional[datetime.datetime]:
    """Parse timestamp string to datetime object."""
    try:
        # Support multiple timestamp formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ", 
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # If no format matches, try parsing as ISO format
        return datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except Exception:
        return None


def calculate_uptime(checks: List[Dict], period_hours: int = 24) -> float:
    """Calculate uptime percentage for a given time period."""
    if not checks:
        return 0.0
    
    now = datetime.datetime.now()
    cutoff_time = now - datetime.timedelta(hours=period_hours)
    
    recent_checks = []
    for check in checks:
        timestamp = parse_timestamp(check.get('timestamp', ''))
        if timestamp and timestamp >= cutoff_time:
            recent_checks.append(check)
    
    if not recent_checks:
        return 0.0
    
    successful_checks = sum(1 for check in recent_checks if check.get('status') == 'success')
    return (successful_checks / len(recent_checks)) * 100


def calculate_average_response_time(checks: List[Dict], period_hours: int = 24) -> float:
    """Calculate average response time for successful checks in a given period."""
    if not checks:
        return 0.0
    
    now = datetime.datetime.now()
    cutoff_time = now - datetime.timedelta(hours=period_hours)
    
    response_times = []
    for check in checks:
        timestamp = parse_timestamp(check.get('timestamp', ''))
        if (timestamp and timestamp >= cutoff_time and 
            check.get('status') == 'success' and 
            'response_time' in check):
            response_times.append(float(check['response_time']))
    
    return mean(response_times) if response_times else 0.0


def check_ssl_expiration(hostname: str) -> Optional[Dict[str, Any]]:
    """Check SSL certificate expiration for a hostname."""
    try:
        # Extract hostname from URL if needed
        if hostname.startswith(('http://', 'https://')):
            hostname = urlparse(hostname).hostname
        
        # Get SSL certificate info
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        
        # Parse expiration date
        expiry_date_str = cert['notAfter']
        expiry_date = datetime.datetime.strptime(expiry_date_str, '%b %d %H:%M:%S %Y %Z')
        
        # Calculate days until expiration
        days_until_expiry = (expiry_date - datetime.datetime.now()).days
        
        return {
            'hostname': hostname,
            'expiry_date': expiry_date.isoformat(),
            'days_until_expiry': days_until_expiry,
            'expires_soon': days_until_expiry <= 30
        }
    
    except Exception as e:
        return {
            'hostname': hostname,
            'error': str(e),
            'expires_soon': False
        }


def generate_report(data: Dict[str, Any], time_periods: List[int] = [24, 168, 720]) -> None:
    """Generate and print comprehensive monitoring report."""
    print("=" * 80)
    print("WEBSITE MONITORING REPORT")
    print("=" * 80)
    print(f"Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Process each monitored site
    sites = data.get('sites', {})
    if isinstance(data.get('checks'), list):
        # Alternative data structure - group checks by URL
        sites = {}
        for check in data['checks']:
            url = check.get('url', 'unknown')
            if url not in sites:
                sites[url] = []
            sites[url].append(check)
    
    if not sites:
        print("No monitoring data found")
        return
    
    print(f"Monitoring {len(sites)} site(s)")
    print()
    
    # SSL certificates expiring soon
    print("SSL CERTIFICATE EXPIRATION CHECK")
    print("-" * 40)
    ssl_warnings = []
    
    for site_url in sites.keys():
        try:
            ssl_info = check_ssl_expiration(site_url)
            if ssl_info and ssl_info.get('expires_soon'):
                ssl_warnings.append(ssl_info)
                days = ssl_info.get('days_until_expiry', 0)
                print(f"⚠️  {ssl_info['hostname']}: {days} days until expiration")
        except Exception as e:
            print(f"❌ {site_url}: Error checking SSL - {e}")
    
    if not ssl_warnings:
        print("✅ No SSL certificates expiring within 30 days")
    
    print()
    
    # Site-by-site analysis
    for site_url, checks in sites.items():
        print(f"SITE: {site_url}")
        print("-" * len(f"SITE: {site_url}"))
        
        if not checks:
            print("No monitoring data available")
            print()
            continue
        
        # Display uptime and response times for different periods
        for period_hours in time_periods:
            period_name = f"{period_hours}h"
            if period_hours >= 168:
                period_name = f"{period_hours // 24}d"
            
            uptime = calculate_uptime(checks, period_hours)
            avg_response = calculate_average_response_time(checks, period_hours)
            
            status_icon = "✅" if uptime >= 99.5 else "⚠️" if uptime >= 95 else "❌"
            
            print(f"{status_icon} {period_name:>4}: {uptime:6.2f}% uptime | "
                  f"{avg_response:7.2f}ms avg response")
        
        # Recent status
        recent_checks = sorted(checks, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        print("\nRecent checks:")
        for check in recent_checks:
            timestamp