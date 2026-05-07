```python
#!/usr/bin/env python3
"""
Website Monitoring Dashboard Generator

This module provides a comprehensive website monitoring solution that:
1. Monitors website uptime and response times
2. Checks SSL certificate expiry dates
3. Generates a styled HTML dashboard report
4. Displays results with color-coded status indicators

The script monitors a predefined list of websites and generates an HTML report
showing uptime status, response times, and SSL certificate warnings.

Dependencies: httpx, ssl, socket (standard library modules)
Usage: python script.py
"""

import asyncio
import ssl
import socket
import json
import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    exit(1)


class WebsiteMonitor:
    """Monitors websites for uptime, response time, and SSL certificate status."""
    
    def __init__(self):
        self.results = []
        
    async def check_website(self, url: str, timeout: int = 10) -> Dict:
        """Check a single website's status and response time."""
        result = {
            'url': url,
            'status': 'Unknown',
            'response_time': 0,
            'status_code': 0,
            'ssl_expiry': None,
            'ssl_days_remaining': 0,
            'error': None,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
                start_time = datetime.datetime.now()
                response = await client.get(url)
                end_time = datetime.datetime.now()
                
                result['response_time'] = (end_time - start_time).total_seconds() * 1000
                result['status_code'] = response.status_code
                result['status'] = 'Online' if 200 <= response.status_code < 400 else 'Warning'
                
        except Exception as e:
            result['status'] = 'Offline'
            result['error'] = str(e)
            
        # Check SSL certificate
        if url.startswith('https://'):
            try:
                ssl_info = await self.check_ssl_certificate(url)
                result.update(ssl_info)
            except Exception as e:
                result['error'] = f"{result.get('error', '')} SSL Error: {str(e)}".strip()
                
        return result
    
    async def check_ssl_certificate(self, url: str) -> Dict:
        """Check SSL certificate expiry for HTTPS URLs."""
        ssl_result = {
            'ssl_expiry': None,
            'ssl_days_remaining': 0
        }
        
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or 443
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Get certificate
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            # Parse expiry date
            if cert and 'notAfter' in cert:
                expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                ssl_result['ssl_expiry'] = expiry_date.isoformat()
                
                days_remaining = (expiry_date - datetime.datetime.now()).days
                ssl_result['ssl_days_remaining'] = days_remaining
                
        except Exception as e:
            # SSL check failed, but don't fail the entire check
            pass
            
        return ssl_result
    
    async def monitor_websites(self, urls: List[str]) -> List[Dict]:
        """Monitor multiple websites concurrently."""
        tasks = [self.check_website(url) for url in urls]
        self.results = await asyncio.gather(*tasks)
        return self.results


class HTMLReportGenerator:
    """Generates styled HTML reports for website monitoring results."""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def _get_html_template(self) -> str:
        """Return the HTML template with embedded CSS."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Monitoring Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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
        
        .header p {
            font-size: 1.1em;
            opacity: 0.8;
        }
        
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .summary-card h3 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .summary-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .online { color: #27ae60; }
        .warning { color: #f39c12; }
        .offline { color: #e74c3c; }
        
        .monitoring-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .monitoring-table th {
            background: #34495e;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        .monitoring-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .monitoring-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .monitoring-table tr:hover {
            background: #e8f4f8;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 0.85em;
        }
        
        .status-online {
            background: #27ae60;
        }
        
        .status-warning {