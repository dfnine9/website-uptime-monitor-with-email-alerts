```python
#!/usr/bin/env python3
"""
Automated Daily Monitoring Report Generator

This module generates comprehensive HTML reports containing:
- Service status summaries with uptime percentages
- Response time graphs and statistics
- SSL certificate expiration alerts
- Organized file output with timestamps

Dependencies: httpx, ssl, socket (standard library modules)
Usage: python script.py
"""

import asyncio
import ssl
import socket
import json
import time
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.parse
import base64

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    exit(1)

class MonitoringReportGenerator:
    def __init__(self):
        self.endpoints = [
            "https://httpbin.org/status/200",
            "https://httpbin.org/delay/1",
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com"
        ]
        self.report_dir = Path("monitoring_reports")
        self.report_dir.mkdir(exist_ok=True)
        
    async def check_endpoint_status(self, url: str) -> Dict:
        """Check endpoint status and response time"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "status": "UP" if response.status_code < 400 else "DOWN",
                    "error": None
                }
        except Exception as e:
            return {
                "url": url,
                "status_code": 0,
                "response_time_ms": 0,
                "status": "DOWN",
                "error": str(e)
            }
    
    def check_ssl_certificate(self, hostname: str, port: int = 443) -> Dict:
        """Check SSL certificate expiration"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse expiration date
                    not_after = cert['notAfter']
                    expiry_date = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    
                    days_until_expiry = (expiry_date - datetime.datetime.now()).days
                    
                    return {
                        "hostname": hostname,
                        "expiry_date": expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
                        "days_until_expiry": days_until_expiry,
                        "status": "CRITICAL" if days_until_expiry < 30 else "WARNING" if days_until_expiry < 90 else "OK",
                        "error": None
                    }
        except Exception as e:
            return {
                "hostname": hostname,
                "expiry_date": "Unknown",
                "days_until_expiry": 0,
                "status": "ERROR",
                "error": str(e)
            }
    
    def generate_response_time_chart(self, results: List[Dict]) -> str:
        """Generate SVG chart for response times"""
        if not results:
            return "<p>No data available for chart</p>"
            
        max_time = max([r['response_time_ms'] for r in results if r['response_time_ms'] > 0], default=100)
        chart_width = 800
        chart_height = 400
        bar_width = chart_width // len(results) - 10
        
        svg_content = f'''<svg width="{chart_width}" height="{chart_height + 100}" viewBox="0 0 {chart_width} {chart_height + 100}">
            <rect width="{chart_width}" height="{chart_height + 100}" fill="#f8f9fa" stroke="#dee2e6"/>
            <text x="{chart_width//2}" y="20" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">Response Times (ms)</text>
        '''
        
        for i, result in enumerate(results):
            x = i * (chart_width // len(results)) + 5
            height = (result['response_time_ms'] / max_time * (chart_height - 50)) if result['response_time_ms'] > 0 else 5
            y = chart_height - height - 30
            
            color = "#28a745" if result['status'] == "UP" else "#dc3545"
            
            svg_content += f'''
                <rect x="{x}" y="{y}" width="{bar_width}" height="{height}" fill="{color}" opacity="0.8"/>
                <text x="{x + bar_width//2}" y="{chart_height - 10}" text-anchor="middle" font-family="Arial" font-size="10" transform="rotate(-45 {x + bar_width//2} {chart_height - 10})">{urllib.parse.urlparse(result['url']).netloc}</text>
                <text x="{x + bar_width//2}" y="{y - 5}" text-anchor="middle" font-family="Arial" font-size="10">{result['response_time_ms']}ms</text>
            '''
        
        svg_content += "</svg>"
        return svg_content
    
    def generate_html_report(self, status_results: List[Dict], ssl_results: List[Dict]) -> str:
        """Generate complete HTML report"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate statistics
        total_endpoints = len(status_results)
        up_endpoints = len([r for r in status_results if r['status'] == 'UP'])
        uptime_percentage = (up_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
        avg_response_time = sum([r['response_time_ms'] for r in status_results if r['response_time_ms'] > 0]) / len([r for r in status_results if r['response_time_ms'] > 0]) if any(r['response_time_ms'] > 0 for r in status_results) else 0
        
        # SSL alerts
        ssl_alerts = [r for r in ssl_results if r['status'] in ['CRITICAL', 'WARNING']]
        
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Monitoring Report - {datetime.datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: #e3f2fd; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 2em; font-weight: