```python
"""
Website Health Monitor Dashboard Generator

This module creates a comprehensive HTML dashboard for monitoring website health metrics.
It checks multiple websites for uptime, response times, SSL certificate status, and generates
historical trend visualizations with color-coded alerts for easy issue identification.

Features:
- Real-time website health monitoring
- Response time tracking with trend analysis
- SSL certificate expiration monitoring
- Color-coded status indicators (green/yellow/red)
- Historical data simulation with charts
- Self-contained HTML dashboard generation
- Responsive design with CSS styling

Usage:
    python script.py

Dependencies:
    - httpx: HTTP client for website monitoring
    - ssl, socket: SSL certificate validation
    - datetime, json: Data handling and timestamps
    - Standard library modules for file operations
"""

import httpx
import ssl
import socket
import datetime
import json
import time
import random
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse


class WebsiteHealthMonitor:
    """Main class for monitoring website health and generating dashboard"""
    
    def __init__(self):
        self.websites = [
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://python.org",
            "https://httpx.dev"
        ]
        self.results = {}
        self.historical_data = {}
        
    def check_website_health(self, url: str) -> Dict:
        """Check comprehensive health metrics for a single website"""
        try:
            start_time = time.time()
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Get SSL certificate info
            ssl_info = self.get_ssl_certificate_info(url)
            
            # Determine status based on response
            if response.status_code == 200:
                status = "healthy"
                status_color = "#28a745"  # Green
            elif 200 <= response.status_code < 400:
                status = "warning"
                status_color = "#ffc107"  # Yellow
            else:
                status = "error"
                status_color = "#dc3545"  # Red
                
            return {
                "url": url,
                "status": status,
                "status_color": status_color,
                "status_code": response.status_code,
                "response_time": round(response_time, 2),
                "ssl_valid": ssl_info["valid"],
                "ssl_expires": ssl_info["expires"],
                "ssl_days_left": ssl_info["days_left"],
                "last_checked": datetime.datetime.now().isoformat(),
                "uptime": 99.9 if status == "healthy" else 95.2  # Simulated uptime
            }
            
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "status_color": "#dc3545",
                "status_code": 0,
                "response_time": 0,
                "ssl_valid": False,
                "ssl_expires": "Unknown",
                "ssl_days_left": 0,
                "last_checked": datetime.datetime.now().isoformat(),
                "uptime": 0,
                "error": str(e)
            }
    
    def get_ssl_certificate_info(self, url: str) -> Dict:
        """Get SSL certificate information for a URL"""
        try:
            hostname = urlparse(url).hostname
            if not hostname:
                return {"valid": False, "expires": "Unknown", "days_left": 0}
                
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            # Parse expiration date
            expires_str = cert['notAfter']
            expires_date = datetime.datetime.strptime(expires_str, '%b %d %H:%M:%S %Y %Z')
            days_left = (expires_date - datetime.datetime.now()).days
            
            return {
                "valid": days_left > 0,
                "expires": expires_date.strftime('%Y-%m-%d'),
                "days_left": days_left
            }
            
        except Exception:
            return {"valid": False, "expires": "Unknown", "days_left": 0}
    
    def generate_historical_data(self) -> Dict:
        """Generate simulated historical data for trending"""
        historical = {}
        
        for url in self.websites:
            data_points = []
            current_time = datetime.datetime.now()
            
            # Generate 24 hours of data points (hourly)
            for i in range(24):
                timestamp = current_time - datetime.timedelta(hours=i)
                # Simulate response times with some variation
                base_time = random.uniform(100, 300)
                response_time = max(50, base_time + random.uniform(-50, 100))
                
                data_points.append({
                    "timestamp": timestamp.isoformat(),
                    "response_time": round(response_time, 2),
                    "uptime": random.uniform(98, 100)
                })
            
            historical[url] = list(reversed(data_points))
            
        return historical
    
    def monitor_all_websites(self):
        """Monitor all configured websites"""
        print("🔍 Starting website health monitoring...")
        
        for url in self.websites:
            print(f"Checking {url}...")
            self.results[url] = self.check_website_health(url)
            time.sleep(1)  # Rate limiting
            
        # Generate historical data
        self.historical_data = self.generate_historical_data()
        print("✅ Health monitoring completed")
    
    def generate_html_dashboard(self) -> str:
        """Generate complete HTML dashboard"""
        
        # Calculate overall statistics
        total_sites = len(self.results)
        healthy_sites = sum(1 for r in self.results.values() if r['status'] == 'healthy')
        avg_response_time = sum(r['response_time'] for r in self.results.values()) / total_sites
        
        # Generate website status cards
        status_cards = ""
        for url, data in self.results.items():
            ssl_status = "✅ Valid" if data['ssl_valid'] else "❌ Invalid"
            if data['ssl_valid'] and data['ssl_days_left'] < 30:
                ssl_status = f"⚠️ Expires in {data['ssl_days_left']} days"
            
            status_cards += f"""
            <div class="status-card" style="border-left: 4px solid {data['status_color']}">
                <div class="card-header">
                    <h3>{url}</h3>
                    <span class="status-badge" style="background-color: {data['status_color']}">{data['status'].upper()}</span>
                </div>
                <div class="metrics">
                    <div class="metric">
                        <span class="metric-label">Status Code:</span>
                        <span class="metric-value">{data['status_code']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Response Time:</span>
                        <span class="metric-value">{data['response_time']} ms</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Uptime:</span>
                        <span class="metric-value">{data['uptime']:.1f}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">SSL Certificate:</span>
                        <span class="metric-value">{ssl_status}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Checked:</span>