```python
"""
Email Notification Module for Website Monitoring

This module monitors website uptime and sends email notifications when sites go down.
It also generates daily status reports with uptime statistics.

Features:
- Monitors multiple websites for availability
- Sends email alerts when sites go down or come back up
- Generates daily uptime reports
- Stores uptime data in JSON format
- Configurable check intervals and email settings

Dependencies: httpx for HTTP requests, anthropic for AI-powered report generation
"""

import smtplib
import json
import time
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

try:
    from anthropic import Anthropic
except ImportError:
    print("Warning: anthropic not installed. AI report generation disabled.")
    Anthropic = None


class WebsiteMonitor:
    def __init__(self, config_file: str = "monitor_config.json"):
        """Initialize the website monitor with configuration."""
        self.config_file = config_file
        self.data_file = "uptime_data.json"
        self.config = self.load_config()
        self.uptime_data = self.load_uptime_data()
        
        if Anthropic and self.config.get("anthropic_api_key"):
            self.anthropic_client = Anthropic(api_key=self.config["anthropic_api_key"])
        else:
            self.anthropic_client = None

    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "websites": [
                {"url": "https://google.com", "name": "Google"},
                {"url": "https://github.com", "name": "GitHub"}
            ],
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "from_email": "your_email@gmail.com",
                "to_emails": ["admin@company.com"]
            },
            "check_interval": 300,  # 5 minutes
            "timeout": 10,
            "anthropic_api_key": ""
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"Loaded configuration from {self.config_file}")
                return config
            else:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default configuration at {self.config_file}")
                print("Please update the configuration with your email settings and websites to monitor.")
                return default_config
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return default_config

    def load_uptime_data(self) -> Dict:
        """Load uptime data from JSON file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading uptime data: {e}")
        
        return {}

    def save_uptime_data(self):
        """Save uptime data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.uptime_data, f, indent=2)
        except Exception as e:
            print(f"Error saving uptime data: {e}")

    def check_website(self, website: Dict) -> Dict:
        """Check if a website is accessible."""
        url = website["url"]
        name = website["name"]
        
        try:
            with httpx.Client(timeout=self.config["timeout"]) as client:
                response = client.get(url)
                is_up = response.status_code == 200
                response_time = response.elapsed.total_seconds()
                
            return {
                "name": name,
                "url": url,
                "is_up": is_up,
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": None
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "is_up": False,
                "status_code": None,
                "response_time": None,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            }

    def send_email(self, subject: str, body: str):
        """Send email notification."""
        try:
            email_config = self.config["email"]
            
            msg = MIMEMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = ", ".join(email_config["to_emails"])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            text = msg.as_string()
            server.sendmail(email_config["from_email"], email_config["to_emails"], text)
            server.quit()
            
            print(f"Email sent: {subject}")
            
        except Exception as e:
            print(f"Error sending email: {e}")

    def record_check(self, result: Dict):
        """Record check result in uptime data."""
        website_name = result["name"]
        
        if website_name not in self.uptime_data:
            self.uptime_data[website_name] = {
                "url": result["url"],
                "checks": [],
                "last_status": None,
                "total_checks": 0,
                "total_uptime": 0
            }
        
        site_data = self.uptime_data[website_name]
        site_data["checks"].append(result)
        site_data["total_checks"] += 1
        
        if result["is_up"]:
            site_data["total_uptime"] += 1
        
        # Keep only last 1000 checks to prevent file from growing too large
        if len(site_data["checks"]) > 1000:
            site_data["checks"] = site_data["checks"][-1000:]
        
        # Check for status change
        if site_data["last_status"] is not None and site_data["last_status"] != result["is_up"]:
            if result["is_up"]:
                self.send_alert_up(result)
            else:
                self.send_alert_down(result)
        elif site_data["last_status"] is None and not result["is_up"]:
            self.send_alert_down(result)
        
        site_data["last_status"] = result["is_up"]

    def send_alert_down(self, result: Dict):
        """Send alert when website goes down."""
        subject = f"ALERT: {result['name']} is DOWN"
        body = f"""
        <html>
        <body>
        <h2 style="color: red;">Website Down Alert</h2>
        <p><strong>Website:</strong> {result['name']}</p>
        <p><strong>URL:</strong> {result['url']}</p>
        <p><strong>Status:</strong> DOWN</p>
        <p><strong>Time:</strong> {result['timestamp']}</p>
        <p><strong>Error:</strong> {result['error'] or 'HTTP ' + str(result['status_code'])}</p>
        </body>
        </html>