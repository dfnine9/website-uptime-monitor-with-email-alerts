#!/usr/bin/env python3
"""
Website Status Monitor

A self-contained Python script that monitors website availability and performance.
Checks website status every 15 minutes, logs response times and status codes to CSV files,
and sends email alerts for downtime events.

Features:
- Periodic website status checking (every 15 minutes)
- CSV logging of response times and status codes
- Email alerting for downtime events
- Error handling and recovery
- Configurable website list and email settings

Usage:
    python script.py

Dependencies:
    - requests (for HTTP requests)
    - smtplib (built-in for email)
    - csv, time, datetime, threading (built-in)
"""

import requests
import smtplib
import csv
import time
import datetime
import threading
import os
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Configuration
WEBSITES = [
    'https://www.google.com',
    'https://www.github.com',
    'https://www.stackoverflow.com'
]

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',  # Use app password for Gmail
    'recipient_email': 'alert-recipient@gmail.com'
}

# Monitoring configuration
CHECK_INTERVAL = 900  # 15 minutes in seconds
TIMEOUT = 30  # Request timeout in seconds
CSV_FILE = 'website_monitoring.csv'

class WebsiteMonitor:
    def __init__(self):
        self.last_status = {}
        self.setup_csv()
    
    def setup_csv(self):
        """Initialize CSV file with headers if it doesn't exist"""
        try:
            if not os.path.exists(CSV_FILE):
                with open(CSV_FILE, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['timestamp', 'website', 'status_code', 'response_time_ms', 'status'])
                print(f"Created CSV file: {CSV_FILE}")
        except Exception as e:
            print(f"Error setting up CSV file: {e}")
    
    def check_website(self, url):
        """Check a single website and return status information"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=TIMEOUT)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            status = 'UP' if response.status_code == 200 else 'DOWN'
            
            return {
                'url': url,
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'status': status,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'status_code': 0,
                'response_time': 0,
                'status': 'DOWN',
                'timestamp': datetime.datetime.now().isoformat(),
                'error': str(e)
            }
    
    def log_to_csv(self, result):
        """Log monitoring result to CSV file"""
        try:
            with open(CSV_FILE, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    result['timestamp'],
                    result['url'],
                    result['status_code'],
                    result['response_time'],
                    result['status']
                ])
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def send_email_alert(self, website, status_info):
        """Send email alert for downtime events"""
        try:
            msg = MimeMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = EMAIL_CONFIG['recipient_email']
            msg['Subject'] = f"Website Alert: {website} is {status_info['status']}"
            
            body = f"""
Website Monitoring Alert

Website: {website}
Status: {status_info['status']}
Status Code: {status_info['status_code']}
Response Time: {status_info['response_time']}ms
Timestamp: {status_info['timestamp']}
            """
            
            if 'error' in status_info:
                body += f"\nError: {status_info['error']}"
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"Email alert sent for {website}")
            
        except Exception as e:
            print(f"Error sending email alert: {e}")
    
    def monitor_websites(self):
        """Monitor all configured websites"""
        print(f"Checking {len(WEBSITES)} websites...")
        
        for website in WEBSITES:
            try:
                result = self.check_website(website)
                
                # Print status to stdout
                print(f"{result['timestamp']} | {website} | {result['status']} | "
                      f"{result['status_code']} | {result['response_time']}ms")
                
                # Log to CSV
                self.log_to_csv(result)
                
                # Check if status changed to DOWN and send alert
                previous_status = self.last_status.get(website, 'UP')
                current_status = result['status']
                
                if current_status == 'DOWN' and previous_status == 'UP':
                    print(f"ALERT: {website} went down!")
                    self.send_email_alert(website, result)
                elif current_status == 'UP' and previous_status == 'DOWN':
                    print(f"RECOVERY: {website} is back up!")
                    # Optionally send recovery notification
                    
                self.last_status[website] = current_status
                
            except Exception as e:
                print(f"Error monitoring {website}: {e}")
    
    def start_monitoring(self):
        """Start the monitoring loop"""
        print(f"Website monitor started. Checking every {CHECK_INTERVAL/60} minutes.")
        print(f"Monitoring websites: {', '.join(WEBSITES)}")
        print(f"Logging to: {CSV_FILE}")
        print("-" * 80)
        
        while True:
            try:
                self.monitor_websites()
                print(f"Next check in {CHECK_INTERVAL/60} minutes...")
                print("-" * 80)
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user.")
                break
            except Exception as e:
                print(f"Unexpected error in monitoring loop: {e}")
                print("Retrying in 60 seconds...")
                time.sleep(60)

def main():
    """Main function to start the website monitor"""
    try:
        monitor = WebsiteMonitor()
        monitor.start_monitoring()
    except Exception as e:
        print(f"Failed to start monitor: {e}")

if __name__ == "__main__":
    main()