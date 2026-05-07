```python
#!/usr/bin/env python3
"""
Website Response Time Monitoring Module

This module monitors website response times and triggers email alerts when
configurable thresholds are exceeded. It stores response time data and
analyzes it to detect performance issues.

Features:
- Monitors multiple websites with configurable response time thresholds
- Stores response time data in JSON format
- Sends email alerts via SMTP when thresholds are exceeded
- Handles HTTP errors and connection timeouts
- Self-contained with minimal dependencies

Usage:
    python script.py

Configuration:
- Modify SITES list to add/remove monitored websites
- Update SMTP settings for email alerts
- Adjust thresholds in ALERT_CONFIG
"""

import json
import time
import smtplib
import asyncio
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from pathlib import Path
import httpx

# Configuration
SITES = [
    {"url": "https://httpbin.org/delay/1", "name": "Test Site 1", "threshold": 3.0},
    {"url": "https://httpbin.org/delay/6", "name": "Test Site 2", "threshold": 5.0},
    {"url": "https://httpbin.org/status/500", "name": "Test Error Site", "threshold": 2.0}
]

ALERT_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_user": "your_email@gmail.com",
    "email_password": "your_app_password",
    "alert_recipients": ["admin@example.com"],
    "cooldown_minutes": 30  # Prevent spam alerts
}

DATA_FILE = "response_times.json"

class ResponseTimeMonitor:
    def __init__(self):
        self.data_file = Path(DATA_FILE)
        self.last_alerts = {}
        
    def load_data(self):
        """Load existing response time data from JSON file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    
    def save_data(self, data):
        """Save response time data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    async def check_site(self, site):
        """Check a single site's response time and status."""
        url = site["url"]
        name = site["name"]
        threshold = site["threshold"]
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response_time = time.time() - start_time
                
                result = {
                    "name": name,
                    "url": url,
                    "response_time": round(response_time, 3),
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat(),
                    "threshold": threshold,
                    "error": None
                }
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    result["error"] = f"HTTP {response.status_code}"
                
                print(f"✓ {name}: {response_time:.3f}s (HTTP {response.status_code})")
                return result
                
        except httpx.TimeoutException:
            response_time = time.time() - start_time
            result = {
                "name": name,
                "url": url,
                "response_time": round(response_time, 3),
                "status_code": None,
                "timestamp": datetime.now().isoformat(),
                "threshold": threshold,
                "error": "Timeout"
            }
            print(f"✗ {name}: Timeout ({response_time:.3f}s)")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            result = {
                "name": name,
                "url": url,
                "response_time": round(response_time, 3),
                "status_code": None,
                "timestamp": datetime.now().isoformat(),
                "threshold": threshold,
                "error": str(e)
            }
            print(f"✗ {name}: Error - {e}")
            return result
    
    def should_alert(self, site_name):
        """Check if enough time has passed since last alert for this site."""
        if site_name not in self.last_alerts:
            return True
        
        last_alert = datetime.fromisoformat(self.last_alerts[site_name])
        cooldown = timedelta(minutes=ALERT_CONFIG["cooldown_minutes"])
        
        return datetime.now() - last_alert > cooldown
    
    def send_alert(self, issues):
        """Send email alert for sites with issues."""
        try:
            msg = MimeMultipart()
            msg['From'] = ALERT_CONFIG["email_user"]
            msg['To'] = ", ".join(ALERT_CONFIG["alert_recipients"])
            msg['Subject'] = f"Website Monitoring Alert - {len(issues)} Issues Detected"
            
            # Create email body
            body = "The following websites are experiencing issues:\n\n"
            
            for issue in issues:
                body += f"Site: {issue['name']}\n"
                body += f"URL: {issue['url']}\n"
                body += f"Response Time: {issue['response_time']}s\n"
                body += f"Threshold: {issue['threshold']}s\n"
                body += f"Status Code: {issue['status_code']}\n"
                if issue['error']:
                    body += f"Error: {issue['error']}\n"
                body += f"Timestamp: {issue['timestamp']}\n"
                body += "-" * 50 + "\n"
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(ALERT_CONFIG["smtp_server"], ALERT_CONFIG["smtp_port"])
            server.starttls()
            server.login(ALERT_CONFIG["email_user"], ALERT_CONFIG["email_password"])
            
            text = msg.as_string()
            server.sendmail(ALERT_CONFIG["email_user"], ALERT_CONFIG["alert_recipients"], text)
            server.quit()
            
            print(f"📧 Alert sent for {len(issues)} issues")
            
            # Update last alert times
            now = datetime.now().isoformat()
            for issue in issues:
                self.last_alerts[issue['name']] = now
                
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    def analyze_results(self, results):
        """Analyze results and determine if alerts should be sent."""
        issues = []
        
        for result in results:
            site_name = result["name"]
            response_time = result["response_time"]
            threshold = result["threshold"]
            error = result["error"]
            status_code = result["status_code"]
            
            # Check for issues
            has_issue = False
            
            if error:
                has_issue = True
                print(f"🚨 {site_name}: Error detected - {error}")
            elif status_code and status_code >= 400:
                has_issue = True
                print(f"🚨 {site_name}: HTTP error - {status_code}")
            elif response_time > threshold:
                has_issue = True
                print(f"🚨 {site_name}: Slow response - {response_time}s > {threshold}s")
            
            if has_issue and self.should_alert(site_name):
                issues.append(result)
            elif has_issue: