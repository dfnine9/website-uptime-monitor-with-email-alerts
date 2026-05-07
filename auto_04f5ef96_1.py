```python
#!/usr/bin/env python3
"""
Website Monitor Email Notification Module

This module monitors website availability and sends email alerts when sites go down or come back online.
It uses SMTP to send notifications through Gmail or Outlook email services.

Features:
- Monitors multiple websites with customizable check intervals
- Sends email alerts for status changes (up/down)
- Supports Gmail and Outlook SMTP configurations
- Persistent status tracking to avoid duplicate notifications
- Comprehensive error handling and logging

Usage:
    python script.py

Configuration:
    Update the EMAIL_CONFIG and WEBSITES dictionaries with your settings.
"""

import smtplib
import ssl
import time
import json
import os
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from datetime import datetime
import threading

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Gmail: smtp.gmail.com, Outlook: smtp-mail.outlook.com
    'smtp_port': 587,  # Gmail: 587, Outlook: 587
    'sender_email': 'your_email@gmail.com',
    'sender_password': 'your_app_password',  # Use app password for Gmail
    'recipient_emails': ['alert@example.com', 'admin@example.com']
}

# Websites to monitor
WEBSITES = {
    'Google': 'https://www.google.com',
    'GitHub': 'https://github.com',
    'Stack Overflow': 'https://stackoverflow.com'
}

# Status file to track website states
STATUS_FILE = 'website_status.json'
CHECK_INTERVAL = 300  # 5 minutes


class WebsiteMonitor:
    def __init__(self):
        self.status_data = self.load_status()
        
    def load_status(self):
        """Load previous status data from file."""
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading status file: {e}")
            return {}
    
    def save_status(self):
        """Save current status data to file."""
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(self.status_data, f, indent=2)
        except Exception as e:
            print(f"Error saving status file: {e}")
    
    def check_website(self, name, url):
        """Check if a website is accessible."""
        try:
            response = urlopen(url, timeout=10)
            if response.getcode() == 200:
                return True, f"HTTP {response.getcode()}"
            else:
                return False, f"HTTP {response.getcode()}"
        except HTTPError as e:
            return False, f"HTTP Error: {e.code}"
        except URLError as e:
            return False, f"URL Error: {e.reason}"
        except Exception as e:
            return False, f"Unknown error: {str(e)}"
    
    def send_email(self, subject, body):
        """Send email notification."""
        try:
            # Create message
            message = MimeMultipart()
            message["From"] = EMAIL_CONFIG['sender_email']
            message["To"] = ", ".join(EMAIL_CONFIG['recipient_emails'])
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MimeText(body, "plain"))
            
            # Create SMTP session
            context = ssl.create_default_context()
            
            with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
                server.starttls(context=context)
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
                
                for recipient in EMAIL_CONFIG['recipient_emails']:
                    server.sendmail(
                        EMAIL_CONFIG['sender_email'],
                        recipient,
                        message.as_string()
                    )
            
            print(f"Email sent successfully: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("SMTP Authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPConnectError:
            print("Failed to connect to SMTP server.")
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def monitor_websites(self):
        """Monitor all websites and send notifications for status changes."""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting website monitoring...")
        
        for name, url in WEBSITES.items():
            try:
                is_up, status_msg = self.check_website(name, url)
                previous_status = self.status_data.get(name, {}).get('is_up', None)
                
                # Update status
                self.status_data[name] = {
                    'is_up': is_up,
                    'status_msg': status_msg,
                    'last_checked': datetime.now().isoformat(),
                    'url': url
                }
                
                print(f"{name}: {'UP' if is_up else 'DOWN'} - {status_msg}")
                
                # Send notification if status changed
                if previous_status is not None and previous_status != is_up:
                    if is_up:
                        # Website came back online
                        subject = f"✅ {name} is back online"
                        body = f"""
Website Monitor Alert

Good news! {name} is back online.

URL: {url}
Status: {status_msg}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This website was previously down and has now recovered.
                        """.strip()
                    else:
                        # Website went down
                        subject = f"🚨 {name} is down"
                        body = f"""
Website Monitor Alert

ALERT: {name} is currently down!

URL: {url}
Status: {status_msg}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please investigate this issue immediately.
                        """.strip()
                    
                    self.send_email(subject, body)
                
            except Exception as e:
                print(f"Error monitoring {name}: {e}")
        
        self.save_status()
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring with specified interval."""
        print(f"Starting continuous website monitoring...")
        print(f"Check interval: {CHECK_INTERVAL} seconds")
        print(f"Monitoring websites: {', '.join(WEBSITES.keys())}")
        print(f"Email alerts will be sent to: {', '.join(EMAIL_CONFIG['recipient_emails'])}")
        
        try:
            while True:
                self.monitor_websites()
                print(f"Next check in {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        except Exception as e:
            print(f"Monitoring error: {e}")
    
    def run_single_check(self):
        """Run a single monitoring check."""
        self.monitor_websites()


def main():
    """Main function to run the website monitor."""
    print("Website Monitor Email Notification System")
    print("=" * 50)
    
    # Validate email configuration
    required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'recipient_emails']
    missing_fields = [field for field in required_fields if not EMAIL_CONFIG.get(field)]
    
    if missing_fields:
        print(f"Error: Missing email configuration fields: {', '.join(missing_fields)}")
        print("Please update the EMAIL_CONFIG dictionary with your email settings.")
        return
    
    if not WEBSITES:
        print("Error: No websites configured for monitoring.")