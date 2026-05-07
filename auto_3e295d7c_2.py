```python
#!/usr/bin/env python3
"""
Website Status Dashboard Generator

This module creates a self-contained HTML dashboard for monitoring website status.
It checks multiple websites for:
- HTTP response status and time
- SSL certificate expiration dates
- Basic connectivity

The dashboard includes:
- Color-coded status indicators (green=ok, yellow=warning, red=error)
- Response time visualization
- SSL certificate expiration warnings
- Auto-refresh functionality

Dependencies: httpx, ssl, socket (standard library)
Usage: python script.py
"""

import asyncio
import json
import ssl
import socket
from datetime import datetime, timedelta
from urllib.parse import urlparse
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)


class WebsiteMonitor:
    def __init__(self):
        self.websites = [
            'https://google.com',
            'https://github.com',
            'https://stackoverflow.com',
            'https://python.org',
            'https://httpbin.org'
        ]
        self.results = []

    async def check_ssl_expiry(self, hostname, port=443):
        """Check SSL certificate expiration date"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (expiry_date - datetime.now()).days
                    return {
                        'expiry_date': expiry_date.isoformat(),
                        'days_until_expiry': days_until_expiry,
                        'status': 'warning' if days_until_expiry < 30 else 'ok'
                    }
        except Exception as e:
            return {
                'expiry_date': None,
                'days_until_expiry': None,
                'status': 'error',
                'error': str(e)
            }

    async def check_website(self, url):
        """Check website status and performance"""
        try:
            start_time = datetime.now()
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            parsed_url = urlparse(url)
            ssl_info = None
            
            if parsed_url.scheme == 'https':
                ssl_info = await self.check_ssl_expiry(parsed_url.hostname)

            status = 'ok' if response.status_code < 400 else 'error'
            if response_time > 2000:
                status = 'warning' if status == 'ok' else status

            return {
                'url': url,
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'status': status,
                'ssl_info': ssl_info,
                'checked_at': datetime.now().isoformat(),
                'error': None
            }

        except Exception as e:
            return {
                'url': url,
                'status_code': None,
                'response_time': None,
                'status': 'error',
                'ssl_info': None,
                'checked_at': datetime.now().isoformat(),
                'error': str(e)
            }

    async def check_all_websites(self):
        """Check all websites concurrently"""
        tasks = [self.check_website(url) for url in self.websites]
        self.results = await asyncio.gather(*tasks)

    def generate_html_report(self):
        """Generate complete HTML dashboard"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Status Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .last-updated {
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        .stats-bar {
            display: flex;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .stat {
            flex: 1;
            padding: 20px;
            text-align: center;
            border-right: 1px solid #dee2e6;
        }
        
        .stat:last-child {
            border-right: none;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
        }
        
        .websites-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        
        .website-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            overflow: hidden;
            transition: transform 0.2s;
        }
        
        .website-card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        
        .site-url {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            word-break: break-all;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-ok { background: #d4edda; color: #155724; }
        .status-warning { background: #fff3cd; color: #856404; }
        .status-error { background: #f8d7da; color: #721c24; }
        
        .card-body {
            padding: 20px;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric {
            text-align: center;
            padding: