```python
#!/usr/bin/env python3
"""
HTTP Log Monitor and Email Alert System

This module monitors a CSV log file for HTTP error status codes (4xx, 5xx) 
and connection timeouts, sending formatted alert emails via SMTP when 
downtime incidents are detected.

Features:
- Monitors CSV log files for HTTP errors and timeouts
- Sends email alerts via SMTP for incident detection
- Self-contained with minimal dependencies
- Configurable thresholds and monitoring intervals
- Real-time log file monitoring with file watching

Usage:
    python script.py

The script expects a CSV log file named 'http_log.csv' with columns:
timestamp, url, status_code, response_time, error_message
"""

import csv
import smtplib
import time
import os
import sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import logging

# Configuration
LOG_FILE = "http_log.csv"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
ALERT_EMAIL = "alerts@company.com"
CHECK_INTERVAL = 30  # seconds
ERROR_THRESHOLD = 3  # consecutive errors before alert

class HTTPLogMonitor:
    def __init__(self, log_file, smtp_config, alert_email):
        """Initialize the HTTP log monitor."""
        self.log_file = Path(log_file)
        self.smtp_config = smtp_config
        self.alert_email = alert_email
        self.last_position = 0
        self.error_count = 0
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 5 minutes between alerts
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def is_error_status(self, status_code):
        """Check if status code indicates an error."""
        try:
            code = int(status_code)
            return code >= 400
        except (ValueError, TypeError):
            return False
    
    def is_timeout_error(self, error_message):
        """Check if error message indicates a timeout."""
        if not error_message:
            return False
        
        timeout_keywords = ['timeout', 'connection timeout', 'read timeout']
        error_lower = str(error_message).lower()
        return any(keyword in error_lower for keyword in timeout_keywords)
    
    def send_alert_email(self, incidents):
        """Send email alert for detected incidents."""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['user']
            msg['To'] = self.alert_email
            msg['Subject'] = f"HTTP Monitoring Alert - {len(incidents)} Incidents Detected"
            
            # Create email body
            body = self.format_alert_message(incidents)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['user'], self.smtp_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.smtp_config['user'], self.alert_email, text)
            server.quit()
            
            self.logger.info(f"Alert email sent successfully for {len(incidents)} incidents")
            print(f"✓ Alert email sent for {len(incidents)} incidents")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {e}")
            print(f"✗ Failed to send alert email: {e}")
    
    def format_alert_message(self, incidents):
        """Format the alert message for email."""
        html_body = f"""
        <html>
        <body>
        <h2>HTTP Monitoring Alert</h2>
        <p><strong>Alert Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total Incidents:</strong> {len(incidents)}</p>
        
        <h3>Incident Details:</h3>
        <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Timestamp</th>
            <th>URL</th>
            <th>Status Code</th>
            <th>Response Time</th>
            <th>Error Message</th>
        </tr>
        """
        
        for incident in incidents:
            html_body += f"""
            <tr>
                <td>{incident.get('timestamp', 'N/A')}</td>
                <td>{incident.get('url', 'N/A')}</td>
                <td>{incident.get('status_code', 'N/A')}</td>
                <td>{incident.get('response_time', 'N/A')}</td>
                <td>{incident.get('error_message', 'N/A')}</td>
            </tr>
            """
        
        html_body += """
        </table>
        
        <p><em>This is an automated alert from the HTTP monitoring system.</em></p>
        </body>
        </html>
        """
        
        return html_body
    
    def read_new_entries(self):
        """Read new entries from the log file since last check."""
        try:
            if not self.log_file.exists():
                self.logger.warning(f"Log file {self.log_file} does not exist")
                return []
            
            file_size = self.log_file.stat().st_size
            
            # If file is smaller than last position, it may have been rotated
            if file_size < self.last_position:
                self.last_position = 0
            
            entries = []
            with open(self.log_file, 'r', newline='', encoding='utf-8') as file:
                file.seek(self.last_position)
                
                # Skip header if we're at the beginning
                if self.last_position == 0:
                    first_line = file.readline()
                    if 'timestamp' in first_line.lower():
                        pass  # Skip header
                    else:
                        file.seek(0)  # Reset if not a header
                
                csv_reader = csv.DictReader(file, fieldnames=[
                    'timestamp', 'url', 'status_code', 'response_time', 'error_message'
                ])
                
                for row in csv_reader:
                    if any(row.values()):  # Skip empty rows
                        entries.append(row)
                
                self.last_position = file.tell()
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            print(f"✗ Error reading log file: {e}")
            return []
    
    def analyze_entries(self, entries):
        """Analyze log entries for errors and timeouts."""
        incidents = []
        
        for entry in entries:
            status_code = entry.get('status_code', '')
            error_message = entry.get('error_message', '')
            
            # Check for HTTP errors (4xx, 5xx)
            if self.is_error_status(status_code):
                incidents.append({
                    **entry,
                    'incident_type': f'HTTP Error {status_code}'
                })
                print(f"⚠ HTTP Error detected: {status_code} for {entry.get('url', 'Unknown URL')}")
            
            # Check for timeout errors
            elif self.is_timeout_error(error_message):
                incidents.append({
                    **entry,
                    'incident_type': 'Connection Timeout'
                })
                print(f"⚠ Timeout detected for {