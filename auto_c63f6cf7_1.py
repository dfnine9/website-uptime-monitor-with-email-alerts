```python
#!/usr/bin/env python3
"""
Website Monitoring Dashboard Generator

This module generates an HTML dashboard from JSON monitoring data, displaying:
- Website uptime status with color-coded indicators
- Response time metrics and trends
- SSL certificate expiration warnings
- Last check timestamps with human-readable formatting

The script reads JSON monitoring data (either from a file or generates sample data)
and produces a self-contained HTML report with embedded CSS styling.

Usage: python script.py

Dependencies: Standard library only (json, datetime, os, sys)
"""

import json
import datetime
import os
import sys
from typing import Dict, List, Any, Optional


def generate_sample_data() -> List[Dict[str, Any]]:
    """Generate sample monitoring data for demonstration purposes."""
    base_time = datetime.datetime.now()
    
    sample_sites = [
        {
            "url": "https://google.com",
            "status": "up",
            "response_time": 145,
            "ssl_days_remaining": 89,
            "last_check": (base_time - datetime.timedelta(minutes=2)).isoformat()
        },
        {
            "url": "https://github.com",
            "status": "up", 
            "response_time": 234,
            "ssl_days_remaining": 156,
            "last_check": (base_time - datetime.timedelta(minutes=1)).isoformat()
        },
        {
            "url": "https://stackoverflow.com",
            "status": "down",
            "response_time": 0,
            "ssl_days_remaining": 12,
            "last_check": (base_time - datetime.timedelta(minutes=3)).isoformat()
        },
        {
            "url": "https://python.org",
            "status": "up",
            "response_time": 89,
            "ssl_days_remaining": 234,
            "last_check": (base_time - datetime.timedelta(minutes=1)).isoformat()
        }
    ]
    
    return sample_sites


def load_monitoring_data(filename: str = "monitoring_data.json") -> List[Dict[str, Any]]:
    """Load monitoring data from JSON file, fallback to sample data if file not found."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                print(f"Loaded monitoring data from {filename}", file=sys.stderr)
                return data
        else:
            print(f"File {filename} not found, using sample data", file=sys.stderr)
            return generate_sample_data()
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {filename}: {e}. Using sample data.", file=sys.stderr)
        return generate_sample_data()


def format_timestamp(iso_timestamp: str) -> str:
    """Convert ISO timestamp to human-readable format."""
    try:
        dt = datetime.datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return iso_timestamp


def get_ssl_warning_class(days_remaining: int) -> str:
    """Return CSS class based on SSL certificate days remaining."""
    if days_remaining <= 7:
        return "ssl-critical"
    elif days_remaining <= 30:
        return "ssl-warning"
    else:
        return "ssl-good"


def get_response_time_class(response_time: int) -> str:
    """Return CSS class based on response time."""
    if response_time == 0:
        return "response-down"
    elif response_time > 1000:
        return "response-slow"
    elif response_time > 500:
        return "response-medium"
    else:
        return "response-fast"


def calculate_stats(monitoring_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics from monitoring data."""
    try:
        total_sites = len(monitoring_data)
        up_sites = len([site for site in monitoring_data if site.get('status') == 'up'])
        down_sites = total_sites - up_sites
        
        response_times = [site.get('response_time', 0) for site in monitoring_data if site.get('status') == 'up']
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        ssl_warnings = len([site for site in monitoring_data if site.get('ssl_days_remaining', 999) <= 30])
        
        return {
            'total_sites': total_sites,
            'up_sites': up_sites,
            'down_sites': down_sites,
            'uptime_percentage': (up_sites / total_sites * 100) if total_sites > 0 else 0,
            'avg_response_time': round(avg_response_time, 2),
            'ssl_warnings': ssl_warnings
        }
    except (TypeError, ZeroDivisionError) as e:
        print(f"Error calculating stats: {e}", file=sys.stderr)
        return {
            'total_sites': 0,
            'up_sites': 0,
            'down_sites': 0,
            'uptime_percentage': 0,
            'avg_response_time': 0,
            'ssl_warnings': 0
        }


def generate_html_dashboard(monitoring_data: List[Dict[str, Any]]) -> str:
    """Generate complete HTML dashboard with embedded CSS."""
    
    stats = calculate_stats(monitoring_data)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate site rows
    site_rows = ""
    for site in monitoring_data:
        try:
            status_class = "status-up" if site.get('status') == 'up' else "status-down"
            ssl_class = get_ssl_warning_class(site.get('ssl_days_remaining', 999))
            response_class = get_response_time_class(site.get('response_time', 0))
            
            site_rows += f"""
            <tr>
                <td class="url-cell">{site.get('url', 'N/A')}</td>
                <td><span class="status-badge {status_class}">{site.get('status', 'unknown').upper()}</span></td>
                <td class="{response_class}">{site.get('response_time', 0)}ms</td>
                <td class="{ssl_class}">{site.get('ssl_days_remaining', 'N/A')} days</td>
                <td class="timestamp">{format_timestamp(site.get('last_check', ''))}</td>
            </tr>
            """
        except Exception as e:
            print(f"Error processing site {site.get('url', 'unknown')}: {e}", file=sys.stderr)
            continue
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Website Monitoring Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(