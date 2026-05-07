```python
#!/usr/bin/env python3
"""
URL Monitoring Script

This script monitors a list of URLs for uptime and response times. It:
- Reads URLs from a JSON configuration file
- Pings each URL and logs response times, status codes, and timestamps
- Saves results to a CSV file with timestamps
- Sends email notifications when downtime is detected (4xx/5xx status codes)
- Prints monitoring results to stdout

The script is designed to be run periodically (e.g., via cron) to continuously
monitor web services and alert administrators of any downtime.

Requirements:
- Python 3.6+
- httpx library for HTTP requests
- Standard library modules: json, csv, smtplib, email, datetime, time, os

Usage:
    python script.py

Configuration:
    Create a 'config.json' file with the following structure:
    {
        "urls": ["https://example.com", "https://google.com"],
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your-email@gmail.com",
            "sender_password": "your-app-password",
            "recipient_email": "admin@yourcompany.com"
        },
        "csv_file": "monitoring_results.csv"
    }
"""

import json
import csv
import smtplib
import os
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    exit(1)


class URLMonitor:
    def __init__(self, config_file='config.json'):
        """Initialize the URL monitor with configuration."""
        self.config = self.load_config(config_file)
        self.csv_file = self.config.get('csv_file', 'monitoring_results.csv')
        self.initialize_csv()
    
    def load_config(self, config_file):
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Validate required fields
            if 'urls' not in config or not config['urls']:
                raise ValueError("Configuration must include 'urls' list")
            
            # Create default config if missing
            if config_file not in os.listdir('.'):
                default_config = {
                    "urls": ["https://httpbin.org/status/200", "https://google.com"],
                    "email": {
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "sender_email": "your-email@gmail.com",
                        "sender_password": "your-app-password",
                        "recipient_email": "admin@yourcompany.com"
                    },
                    "csv_file": "monitoring_results.csv"
                }
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default config file: {config_file}")
                print("Please update the email settings before running again.")
                
            return config
            
        except FileNotFoundError:
            # Create default config
            default_config = {
                "urls": ["https://httpbin.org/status/200", "https://google.com"],
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your-email@gmail.com",
                    "sender_password": "your-app-password",
                    "recipient_email": "admin@yourcompany.com"
                },
                "csv_file": "monitoring_results.csv"
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config file: {config_file}")
            print("Please update the configuration and run again.")
            return default_config
            
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            exit(1)
        except Exception as e:
            print(f"Error loading config: {e}")
            exit(1)
    
    def initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        try:
            if not os.path.exists(self.csv_file):
                with open(self.csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms', 'status'])
        except Exception as e:
            print(f"Error initializing CSV file: {e}")
    
    def ping_url(self, url, timeout=10):
        """Ping a single URL and return status information."""
        try:
            start_time = time.time()
            
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url, follow_redirects=True)
                
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            status = 'UP' if response.status_code < 400 else 'DOWN'
            
            return {
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'status': status,
                'error': None
            }
            
        except httpx.RequestError as e:
            return {
                'url': url,
                'status_code': 0,
                'response_time_ms': 0,
                'status': 'ERROR',
                'error': str(e)
            }
        except Exception as e:
            return {
                'url': url,
                'status_code': 0,
                'response_time_ms': 0,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def log_result(self, result):
        """Log result to CSV file."""
        try:
            timestamp = datetime.now().isoformat()
            
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    result['url'],
                    result['status_code'],
                    result['response_time_ms'],
                    result['status']
                ])
        except Exception as e:
            print(f"Error logging to CSV: {e}")
    
    def send_email_notification(self, failed_urls):
        """Send email notification for failed URLs."""
        try:
            email_config = self.config.get('email', {})
            
            if not all(key in email_config for key in ['sender_email', 'sender_password', 'recipient_email']):
                print("Email configuration incomplete. Skipping email notification.")
                return
            
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            sender_email = email_config['sender_email']
            sender_password = email_config['sender_password']
            recipient_email = email_config['recipient_email']
            
            # Skip if default values are still in place
            if sender_email == 'your-email@gmail.com':
                print("Email not configured. Skipping email notification.")
                return
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"URL Monitor Alert - {len(failed_urls)} URLs Down"
            
            body = "The following URLs are experiencing issues:\n\n"
            for url_data in failed_urls:
                body += f"URL: {url_data['url']}\n"
                body += f"Status: {url_data['status']}\n"
                body += f"Status Code: {url_data