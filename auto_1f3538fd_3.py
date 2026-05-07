```python
#!/usr/bin/env python3
"""
Log Monitor Email Alert System

This module monitors log files for HTTP status code failures (4xx, 5xx) and sends
email notifications when downtime is detected. It tracks failure timestamps and
recovery periods, providing comprehensive downtime reporting.

Features:
- Monitors log files for HTTP status code patterns
- Detects service failures and recovery events
- Sends email alerts with downtime details
- Tracks cumulative downtime statistics
- Self-contained with minimal dependencies

Usage:
    python script.py

The script will continuously monitor the specified log file and send email
notifications when failures are detected or services recover.
"""

import re
import time
import smtplib
import os
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from collections import defaultdict
import json

class LogMonitor:
    def __init__(self, config_file='monitor_config.json'):
        """Initialize the log monitor with configuration."""
        self.config = self.load_config(config_file)
        self.failure_states = {}  # Track ongoing failures
        self.downtime_stats = defaultdict(list)  # Track downtime history
        self.last_position = 0
        
    def load_config(self, config_file):
        """Load configuration from JSON file or use defaults."""
        default_config = {
            "log_file": "/var/log/access.log",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email_user": os.getenv("EMAIL_USER", "monitor@example.com"),
            "email_password": os.getenv("EMAIL_PASSWORD", "password"),
            "alert_recipients": ["admin@example.com"],
            "failure_threshold": 3,  # Number of failures before alert
            "check_interval": 60,    # Seconds between checks
            "status_pattern": r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?"[^"]*" (\d{3})',
            "failure_codes": ["4", "5"]  # Status code prefixes (4xx, 5xx)
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            print("Using default configuration")
            
        return default_config
    
    def parse_log_line(self, line):
        """Parse a log line to extract timestamp and status code."""
        try:
            match = re.search(self.config["status_pattern"], line)
            if match:
                timestamp_str, status_code = match.groups()
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                return timestamp, status_code
        except Exception as e:
            print(f"Error parsing log line: {e}")
        return None, None
    
    def is_failure_status(self, status_code):
        """Check if status code indicates a failure."""
        return any(status_code.startswith(prefix) for prefix in self.config["failure_codes"])
    
    def send_email_alert(self, subject, body):
        """Send email notification."""
        try:
            msg = MimeMultipart()
            msg['From'] = self.config["email_user"]
            msg['To'] = ', '.join(self.config["alert_recipients"])
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'html'))
            
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            server.starttls()
            server.login(self.config["email_user"], self.config["email_password"])
            
            for recipient in self.config["alert_recipients"]:
                server.sendmail(self.config["email_user"], recipient, msg.as_string())
            
            server.quit()
            print(f"Email alert sent: {subject}")
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False
    
    def format_downtime_alert(self, service, failure_start, failure_count):
        """Format downtime alert email."""
        duration = datetime.now() - failure_start
        
        subject = f"🚨 SERVICE ALERT: {service} experiencing failures"
        
        body = f"""
        <html>
        <body>
            <h2>Service Failure Detected</h2>
            <table border="1" cellpadding="5">
                <tr><td><b>Service</b></td><td>{service}</td></tr>
                <tr><td><b>Failure Started</b></td><td>{failure_start.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                <tr><td><b>Duration</b></td><td>{str(duration).split('.')[0]}</td></tr>
                <tr><td><b>Failure Count</b></td><td>{failure_count}</td></tr>
                <tr><td><b>Alert Time</b></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            </table>
            
            <h3>Recent Downtime History</h3>
            <ul>
        """
        
        # Add recent downtime history
        recent_downtimes = self.downtime_stats[service][-5:]  # Last 5 incidents
        for downtime in recent_downtimes:
            body += f"<li>{downtime['start']} - {downtime['end']} (Duration: {downtime['duration']})</li>"
        
        body += """
            </ul>
            <p><i>This is an automated alert from the Log Monitor system.</i></p>
        </body>
        </html>
        """
        
        return subject, body
    
    def format_recovery_alert(self, service, failure_start, recovery_time):
        """Format service recovery alert email."""
        downtime_duration = recovery_time - failure_start
        
        subject = f"✅ SERVICE RECOVERED: {service} is back online"
        
        body = f"""
        <html>
        <body>
            <h2>Service Recovery Confirmed</h2>
            <table border="1" cellpadding="5">
                <tr><td><b>Service</b></td><td>{service}</td></tr>
                <tr><td><b>Failure Started</b></td><td>{failure_start.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                <tr><td><b>Recovery Time</b></td><td>{recovery_time.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                <tr><td><b>Total Downtime</b></td><td>{str(downtime_duration).split('.')[0]}</td></tr>
            </table>
            
            <h3>Downtime Statistics</h3>
            <p><b>Total incidents today:</b> {len([d for d in self.downtime_stats[service] if d['start'].date() == datetime.now().date()])}</p>
            <p><b>Total downtime today:</b> {self.calculate_daily_downtime(service)}</p>
            
            <p><i>This is an automated recovery notification from the Log Monitor system.</i></p>
        </body>
        </html>
        """
        
        return subject, body
    
    def calculate_daily_downtime(self, service):
        """Calculate total downtime for today."""
        today = datetime.now().date()
        total_seconds = 0
        
        for downtime in self.downtime_stats[service]:
            if downtime['start'].date() == today:
                total_seconds += downtime['duration_seconds']
        
        return str(timedelta(seconds=total_seconds))
    
    def process_log_entries(