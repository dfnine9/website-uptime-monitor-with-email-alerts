```python
"""
Website Monitoring Report Generator

This module generates comprehensive HTML and JSON status reports for monitored websites.
It tracks uptime percentages, performance metrics, and SSL certificate status.

Features:
- Multi-threaded website monitoring
- SSL certificate validation and expiry checking
- Performance metrics (response time, status codes)
- HTML and JSON report generation
- Uptime percentage calculations
- Error handling and logging

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - Standard library modules only
"""

import json
import ssl
import socket
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import concurrent.futures
import threading
from dataclasses import dataclass, asdict

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    exit(1)

@dataclass
class WebsiteStatus:
    url: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    ssl_valid: Optional[bool] = None
    ssl_expires: Optional[str] = None
    ssl_days_remaining: Optional[int] = None
    error: Optional[str] = None
    timestamp: str = ""
    uptime_percentage: float = 0.0

class SSLChecker:
    """Handles SSL certificate validation and expiry checking."""
    
    @staticmethod
    def check_ssl_certificate(hostname: str, port: int = 443) -> Tuple[bool, Optional[str], Optional[int]]:
        """Check SSL certificate validity and expiration."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            # Parse expiry date
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_remaining = (expiry_date - datetime.now()).days
            
            return True, expiry_date.isoformat(), days_remaining
            
        except Exception as e:
            return False, None, None

class WebsiteMonitor:
    """Main monitoring class that checks website status and generates reports."""
    
    def __init__(self, websites: List[str], check_interval: int = 60, history_hours: int = 24):
        self.websites = websites
        self.check_interval = check_interval
        self.history_hours = history_hours
        self.history: Dict[str, List[WebsiteStatus]] = {url: [] for url in websites}
        self.ssl_checker = SSLChecker()
        
    def check_website(self, url: str) -> WebsiteStatus:
        """Check a single website's status."""
        status = WebsiteStatus(url=url, timestamp=datetime.now().isoformat())
        
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = f"https://{url}"
                parsed_url = urlparse(url)
            
            start_time = time.time()
            
            with httpx.Client(timeout=30.0, verify=False) as client:
                response = client.get(url, follow_redirects=True)
                
            status.response_time = round((time.time() - start_time) * 1000, 2)  # ms
            status.status_code = response.status_code
            
            # Check SSL if HTTPS
            if parsed_url.scheme == 'https':
                hostname = parsed_url.hostname
                if hostname:
                    ssl_valid, ssl_expires, days_remaining = self.ssl_checker.check_ssl_certificate(hostname)
                    status.ssl_valid = ssl_valid
                    status.ssl_expires = ssl_expires
                    status.ssl_days_remaining = days_remaining
                    
        except Exception as e:
            status.error = str(e)
            
        return status
    
    def calculate_uptime(self, url: str) -> float:
        """Calculate uptime percentage for a URL based on historical data."""
        if url not in self.history or not self.history[url]:
            return 0.0
            
        successful_checks = sum(1 for check in self.history[url] 
                              if check.status_code and 200 <= check.status_code < 400)
        total_checks = len(self.history[url])
        
        return round((successful_checks / total_checks) * 100, 2) if total_checks > 0 else 0.0
    
    def monitor_websites(self) -> List[WebsiteStatus]:
        """Monitor all websites concurrently."""
        current_statuses = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.check_website, url): url 
                           for url in self.websites}
            
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    status = future.result()
                    # Calculate uptime
                    status.uptime_percentage = self.calculate_uptime(status.url)
                    current_statuses.append(status)
                    
                    # Add to history
                    self.history[status.url].append(status)
                    
                    # Keep only recent history
                    cutoff_time = datetime.now() - timedelta(hours=self.history_hours)
                    self.history[status.url] = [
                        s for s in self.history[status.url] 
                        if datetime.fromisoformat(s.timestamp) > cutoff_time
                    ]
                    
                except Exception as e:
                    print(f"Error monitoring website: {e}")
        
        return current_statuses
    
    def generate_json_report(self, statuses: List[WebsiteStatus]) -> str:
        """Generate JSON status report."""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_websites": len(statuses),
            "websites": [asdict(status) for status in statuses],
            "summary": {
                "total_up": sum(1 for s in statuses if s.status_code and 200 <= s.status_code < 400),
                "total_down": sum(1 for s in statuses if s.error or not s.status_code or s.status_code >= 400),
                "ssl_issues": sum(1 for s in statuses if s.ssl_valid is False or (s.ssl_days_remaining and s.ssl_days_remaining < 30)),
                "average_response_time": round(sum(s.response_time for s in statuses if s.response_time) / len([s for s in statuses if s.response_time]), 2) if any(s.response_time for s in statuses) else 0
            }
        }
        
        return json.dumps(report_data, indent=2)
    
    def generate_html_report(self, statuses: List[WebsiteStatus]) -> str:
        """Generate HTML status report."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Website Monitoring Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: