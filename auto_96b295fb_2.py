```python
"""
Website Monitoring and Email Alert System

This module monitors website health by checking:
- Site availability (HTTP status codes)
- Response time performance
- SSL certificate expiration dates

Sends formatted email alerts when configured thresholds are exceeded.
Requires only standard library plus httpx for HTTP requests.

Usage: python script.py
"""

import smtplib
import ssl
import socket
import datetime
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
import logging

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    exit(1)

# Configuration
CONFIG = {
    "sites": [
        {"url": "https://example.com", "max_response_time": 2.0},
        {"url": "https://google.com", "max_response_time": 1.5},
        {"url": "https://github.com", "max_response_time": 3.0}
    ],
    "ssl_warning_days": 30,
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your-email@gmail.com",
        "sender_password": "your-app-password",
        "recipient_email": "alerts@company.com"
    },
    "timeout": 10
}

class WebsiteMonitor:
    def __init__(self, config):
        self.config = config
        self.alerts = []
        
    def check_ssl_expiration(self, hostname, port=443):
        """Check SSL certificate expiration date"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.config["timeout"]) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (expiry_date - datetime.datetime.now()).days
                    return days_until_expiry, expiry_date
        except Exception as e:
            print(f"SSL check failed for {hostname}: {e}")
            return None, None
            
    def check_website(self, site):
        """Check individual website health"""
        url = site["url"]
        max_response_time = site["max_response_time"]
        
        try:
            print(f"Checking {url}...")
            
            start_time = time.time()
            with httpx.Client(timeout=self.config["timeout"]) as client:
                response = client.get(url)
            response_time = time.time() - start_time
            
            # Check HTTP status
            if response.status_code >= 400:
                self.alerts.append({
                    "type": "downtime",
                    "url": url,
                    "status_code": response.status_code,
                    "message": f"Site {url} returned status {response.status_code}"
                })
                
            # Check response time
            if response_time > max_response_time:
                self.alerts.append({
                    "type": "slow_response",
                    "url": url,
                    "response_time": response_time,
                    "threshold": max_response_time,
                    "message": f"Site {url} response time {response_time:.2f}s exceeds threshold {max_response_time}s"
                })
                
            # Check SSL certificate
            parsed_url = urlparse(url)
            if parsed_url.scheme == "https":
                days_until_expiry, expiry_date = self.check_ssl_expiration(parsed_url.hostname)
                if days_until_expiry is not None and days_until_expiry <= self.config["ssl_warning_days"]:
                    self.alerts.append({
                        "type": "ssl_expiring",
                        "url": url,
                        "days_until_expiry": days_until_expiry,
                        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                        "message": f"SSL certificate for {url} expires in {days_until_expiry} days ({expiry_date.strftime('%Y-%m-%d')})"
                    })
                    
            print(f"✓ {url} - Status: {response.status_code}, Response: {response_time:.2f}s")
            
        except httpx.TimeoutException:
            self.alerts.append({
                "type": "timeout",
                "url": url,
                "message": f"Site {url} timed out after {self.config['timeout']} seconds"
            })
            print(f"✗ {url} - TIMEOUT")
            
        except Exception as e:
            self.alerts.append({
                "type": "error",
                "url": url,
                "error": str(e),
                "message": f"Error checking {url}: {str(e)}"
            })
            print(f"✗ {url} - ERROR: {e}")
            
    def format_alert_email(self):
        """Format alerts into HTML email"""
        if not self.alerts:
            return None
            
        html = """
        <html>
        <body>
        <h2>Website Monitoring Alerts</h2>
        <p>The following issues were detected:</p>
        """
        
        # Group alerts by type
        alert_types = {
            "downtime": "🔴 Site Downtime",
            "slow_response": "🟡 Slow Response Times", 
            "ssl_expiring": "🔶 SSL Certificate Expiring",
            "timeout": "⏰ Connection Timeouts",
            "error": "❌ Monitoring Errors"
        }
        
        for alert_type, title in alert_types.items():
            type_alerts = [a for a in self.alerts if a["type"] == alert_type]
            if type_alerts:
                html += f"<h3>{title}</h3><ul>"
                for alert in type_alerts:
                    html += f"<li>{alert['message']}</li>"
                html += "</ul>"
                
        html += f"""
        <p><strong>Alert generated at:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        return html
        
    def send_email_alert(self):
        """Send email notification with alerts"""
        if not self.alerts:
            print("No alerts to send")
            return
            
        try:
            email_config = self.config["email"]
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Website Monitoring Alert - {len(self.alerts)} issues detected"
            msg["From"] = email_config["sender_email"]
            msg["To"] = email_config["recipient_email"]
            
            html_content = self.format_alert_email()
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
                server.starttls(context=context)
                server.login(email_config["sender_email"], email_config["sender_password"])
                server.send_message(msg)
                
            print(f"✓ Alert email sent to {email_config['recipient_email']}")
            
        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            
    def run_monitoring(self):
        """Run complete monitoring cycle"""
        print("Starting website monitoring...")
        print("-" * 50)
        
        for site in self.config["sites"]:
            self.check_website(site)
            
        print("-