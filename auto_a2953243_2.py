```python
#!/usr/bin/env python3
"""
Website Performance Alert System

This module monitors website performance by reading CSV log files containing response times
and comparing them against configurable thresholds. When response times exceed the defined
thresholds, it sends notifications via email (SMTP) or webhook (HTTP POST).

The system processes CSV files with columns: timestamp, url, response_time, status_code
and alerts when response times are above the configured slow threshold.

Dependencies: httpx (for webhook notifications)
Usage: python script.py
"""

import csv
import json
import smtplib
import sys
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import httpx
except ImportError:
    print("Warning: httpx not available. Webhook notifications disabled.")
    httpx = None


class AlertSystem:
    """Website performance monitoring and alerting system."""
    
    def __init__(self, config: Dict):
        """Initialize the alert system with configuration."""
        self.config = config
        self.thresholds = config.get('thresholds', {})
        self.email_config = config.get('email', {})
        self.webhook_config = config.get('webhook', {})
        self.log_file = config.get('log_file', 'performance_logs.csv')
        self.last_check_time = None
        
    def read_csv_logs(self, since_timestamp: Optional[float] = None) -> List[Dict]:
        """
        Read CSV logs and return entries since the specified timestamp.
        
        Args:
            since_timestamp: Unix timestamp to filter logs from
            
        Returns:
            List of log entries as dictionaries
        """
        logs = []
        log_path = Path(self.log_file)
        
        if not log_path.exists():
            print(f"Log file {self.log_file} not found. Creating sample data...")
            self._create_sample_logs()
            
        try:
            with open(log_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        # Convert timestamp to float for comparison
                        log_timestamp = float(row.get('timestamp', 0))
                        
                        # Skip old entries if since_timestamp is provided
                        if since_timestamp and log_timestamp <= since_timestamp:
                            continue
                            
                        logs.append({
                            'timestamp': log_timestamp,
                            'url': row.get('url', ''),
                            'response_time': float(row.get('response_time', 0)),
                            'status_code': int(row.get('status_code', 0))
                        })
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Skipping malformed log entry: {row} - {e}")
                        continue
                        
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []
            
        return logs
    
    def _create_sample_logs(self):
        """Create sample log data for demonstration."""
        sample_data = [
            {'timestamp': time.time() - 300, 'url': 'https://example.com', 'response_time': 0.15, 'status_code': 200},
            {'timestamp': time.time() - 240, 'url': 'https://example.com/api', 'response_time': 2.5, 'status_code': 200},
            {'timestamp': time.time() - 180, 'url': 'https://example.com/slow', 'response_time': 5.2, 'status_code': 200},
            {'timestamp': time.time() - 120, 'url': 'https://example.com', 'response_time': 0.08, 'status_code': 200},
            {'timestamp': time.time() - 60, 'url': 'https://example.com/api', 'response_time': 3.1, 'status_code': 500},
        ]
        
        with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'url', 'response_time', 'status_code']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"Created sample log file: {self.log_file}")
    
    def check_thresholds(self, logs: List[Dict]) -> List[Dict]:
        """
        Check logs against configured thresholds and return alerts.
        
        Args:
            logs: List of log entries to check
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        for log in logs:
            url = log['url']
            response_time = log['response_time']
            status_code = log['status_code']
            
            # Get threshold for this URL or use default
            url_threshold = self.thresholds.get(url, self.thresholds.get('default', 2.0))
            
            # Check if response time exceeds threshold
            if response_time > url_threshold:
                alert = {
                    'type': 'slow_response',
                    'url': url,
                    'response_time': response_time,
                    'threshold': url_threshold,
                    'status_code': status_code,
                    'timestamp': log['timestamp'],
                    'severity': self._get_severity(response_time, url_threshold)
                }
                alerts.append(alert)
                
            # Check for HTTP errors
            if status_code >= 400:
                alert = {
                    'type': 'http_error',
                    'url': url,
                    'response_time': response_time,
                    'status_code': status_code,
                    'timestamp': log['timestamp'],
                    'severity': 'high' if status_code >= 500 else 'medium'
                }
                alerts.append(alert)
                
        return alerts
    
    def _get_severity(self, response_time: float, threshold: float) -> str:
        """Determine alert severity based on how much threshold is exceeded."""
        ratio = response_time / threshold
        if ratio >= 3.0:
            return 'critical'
        elif ratio >= 2.0:
            return 'high'
        elif ratio >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def send_email_alert(self, alerts: List[Dict]) -> bool:
        """
        Send email notification for alerts.
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.email_config.get('enabled', False):
            return False
            
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['smtp_user']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"Performance Alert - {len(alerts)} issues detected"
            
            # Create email body
            body = self._format_alert_email(alerts)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                if self.email_config.get('use_tls', True):
                    server.starttls()
                
                server.login(self.email_config['smtp_user'], self.email_config['smtp_password'])
                server.send_message(msg)
                
            print(f"Email alert sent successfully to {self.email_config['recipient']}")
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False
    
    def send_webhook_alert(self, alerts: List[