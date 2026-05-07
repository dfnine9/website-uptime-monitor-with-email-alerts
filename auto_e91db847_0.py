```python
#!/usr/bin/env python3
"""
Website Monitoring and Alert System

This module monitors website availability by reading URLs from a config.json file,
performing HTTP requests to check site status, measuring response times, and logging
results to CSV with timestamps. It includes SMTP email functionality to send alerts
when sites return non-200 status codes.

Dependencies: httpx (for HTTP requests)
Usage: python script.py

The script expects a config.json file in the same directory with the following structure:
{
    "urls": ["https://example1.com", "https://example2.com"],
    "smtp_settings": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "email": "your-email@gmail.com",
        "password": "your-app-password",
        "alert_recipients": ["admin@company.com"]
    },
    "timeout": 30,
    "log_file": "monitoring_results.csv"
}
"""

import json
import csv
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class WebsiteMonitor:
    def __init__(self, config_file="config.json"):
        """Initialize the website monitor with configuration."""
        self.config_file = config_file
        self.config = self._load_config()
        self.log_file = self.config.get("log_file", "monitoring_results.csv")
        self.timeout = self.config.get("timeout", 30)
        
    def _load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file '{self.config_file}' not found.")
            self._create_sample_config()
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def _create_sample_config(self):
        """Create a sample configuration file."""
        sample_config = {
            "urls": [
                "https://httpbin.org/status/200",
                "https://httpbin.org/status/404",
                "https://google.com"
            ],
            "smtp_settings": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "your-email@gmail.com",
                "password": "your-app-password",
                "alert_recipients": ["admin@company.com"]
            },
            "timeout": 30,
            "log_file": "monitoring_results.csv"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"Sample configuration created: {self.config_file}")
        print("Please update the configuration with your actual settings.")
    
    def check_website(self, url):
        """Check a single website's availability and response time."""
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response_time = round((time.time() - start_time) * 1000, 2)  # ms
                
                result = {
                    "timestamp": timestamp,
                    "url": url,
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "status": "UP" if response.status_code == 200 else "DOWN",
                    "error": None
                }
                
                print(f"[{timestamp}] {url} - Status: {response.status_code} - Time: {response_time}ms")
                return result
                
        except httpx.TimeoutException:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                "timestamp": timestamp,
                "url": url,
                "status_code": "TIMEOUT",
                "response_time_ms": response_time,
                "status": "DOWN",
                "error": "Request timeout"
            }
            print(f"[{timestamp}] {url} - TIMEOUT after {response_time}ms")
            return result
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                "timestamp": timestamp,
                "url": url,
                "status_code": "ERROR",
                "response_time_ms": response_time,
                "status": "DOWN",
                "error": str(e)
            }
            print(f"[{timestamp}] {url} - ERROR: {str(e)}")
            return result
    
    def log_to_csv(self, results):
        """Log results to CSV file."""
        try:
            file_exists = Path(self.log_file).exists()
            
            with open(self.log_file, 'a', newline='') as csvfile:
                fieldnames = ["timestamp", "url", "status_code", "response_time_ms", "status", "error"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                for result in results:
                    writer.writerow(result)
                    
            print(f"Results logged to {self.log_file}")
            
        except Exception as e:
            print(f"Error writing to CSV file: {e}")
    
    def send_email_alert(self, failed_sites):
        """Send email alert for failed sites."""
        if not failed_sites:
            return
            
        smtp_config = self.config.get("smtp_settings", {})
        
        if not all(key in smtp_config for key in ["smtp_server", "email", "password", "alert_recipients"]):
            print("Warning: SMTP configuration incomplete. Email alerts disabled.")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config["email"]
            msg['To'] = ", ".join(smtp_config["alert_recipients"])
            msg['Subject'] = f"Website Alert: {len(failed_sites)} Site(s) Down"
            
            # Create email body
            body = "The following websites are experiencing issues:\n\n"
            for site in failed_sites:
                body += f"• {site['url']} - Status: {site['status_code']} - Error: {site['error'] or 'N/A'}\n"
            
            body += f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_config["smtp_server"], smtp_config.get("smtp_port", 587))
            server.starttls()
            server.login(smtp_config["email"], smtp_config["password"])
            
            text = msg.as_string()
            server.sendmail(smtp_config["email"], smtp_config["alert_recipients"], text)
            server.quit()
            
            print(f"Alert email sent to {len(smtp_config['alert_recipients'])} recipient(s)")
            
        except Exception as e:
            print(f"Error sending email alert: {e}")
    
    def monitor_websites(self):
        """Main monitoring function."""
        urls = self.config.get("urls", [])
        
        if not urls:
            print("Error: No URLs configured for monitoring.")
            return
        
        print(f"Starting website monitoring for {len(