```python
"""
Website Monitoring Notification System

This module provides a comprehensive notification system that monitors website uptime
by reading CSV log files, detecting downtime events, and sending email alerts.

Key Features:
- Reads CSV log files containing website monitoring data
- Detects downtime events (non-200 status codes, timeouts, connection errors)
- Sends email alerts with detailed site status information
- Configurable email settings and monitoring thresholds
- Comprehensive error handling and logging

Dependencies:
- Standard library modules: csv, smtplib, email, datetime, logging, os
- httpx: For HTTP requests (if real-time checking is needed)
- anthropic: For potential AI-enhanced alert analysis

Usage:
    python script.py

The script expects a CSV file with columns: timestamp, url, status_code, response_time
Email configuration should be set via environment variables or modified in the script.
"""

import csv
import smtplib
import logging
import os
import sys
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Dict, Optional
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('monitoring.log')
    ]
)
logger = logging.getLogger(__name__)

class WebsiteMonitor:
    def __init__(self, csv_file: str = "website_logs.csv"):
        """
        Initialize the website monitoring system.
        
        Args:
            csv_file (str): Path to the CSV log file
        """
        self.csv_file = csv_file
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', 'monitor@example.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', 'password')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL', 'admin@example.com')
        self.alert_threshold = int(os.getenv('ALERT_THRESHOLD_MINUTES', '5'))
        
    def read_csv_logs(self) -> List[Dict]:
        """
        Read monitoring logs from CSV file.
        
        Returns:
            List[Dict]: List of log entries
        """
        logs = []
        try:
            if not os.path.exists(self.csv_file):
                logger.warning(f"CSV file {self.csv_file} not found. Creating sample data.")
                self._create_sample_data()
                
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    logs.append({
                        'timestamp': row.get('timestamp', ''),
                        'url': row.get('url', ''),
                        'status_code': row.get('status_code', ''),
                        'response_time': row.get('response_time', ''),
                        'error_message': row.get('error_message', '')
                    })
            
            logger.info(f"Successfully read {len(logs)} log entries from {self.csv_file}")
            return logs
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return []
    
    def _create_sample_data(self):
        """Create sample monitoring data for demonstration."""
        sample_data = [
            {
                'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
                'url': 'https://example.com',
                'status_code': '200',
                'response_time': '0.5',
                'error_message': ''
            },
            {
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'url': 'https://example.com',
                'status_code': '500',
                'response_time': '2.1',
                'error_message': 'Internal Server Error'
            },
            {
                'timestamp': (datetime.now() - timedelta(minutes=2)).isoformat(),
                'url': 'https://test-site.com',
                'status_code': 'TIMEOUT',
                'response_time': '30.0',
                'error_message': 'Connection timeout'
            }
        ]
        
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['timestamp', 'url', 'status_code', 'response_time', 'error_message']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)
            logger.info(f"Created sample data in {self.csv_file}")
        except Exception as e:
            logger.error(f"Error creating sample data: {e}")
    
    def detect_downtime_events(self, logs: List[Dict]) -> List[Dict]:
        """
        Detect downtime events from log entries.
        
        Args:
            logs (List[Dict]): List of log entries
            
        Returns:
            List[Dict]: List of downtime events
        """
        downtime_events = []
        
        try:
            for log in logs:
                is_downtime = False
                severity = "INFO"
                
                # Check status code
                status_code = log.get('status_code', '').strip()
                if status_code and status_code not in ['200', '201', '204', '301', '302']:
                    is_downtime = True
                    if status_code.startswith('5') or status_code in ['TIMEOUT', 'CONNECTION_ERROR']:
                        severity = "CRITICAL"
                    elif status_code.startswith('4'):
                        severity = "WARNING"
                
                # Check response time
                try:
                    response_time = float(log.get('response_time', 0))
                    if response_time > 10.0:  # Slow response threshold
                        severity = "WARNING" if severity == "INFO" else severity
                        if response_time > 30.0:
                            is_downtime = True
                            severity = "CRITICAL"
                except (ValueError, TypeError):
                    pass
                
                # Check for error messages
                error_message = log.get('error_message', '').strip()
                if error_message:
                    is_downtime = True
                    severity = "CRITICAL"
                
                if is_downtime:
                    downtime_event = log.copy()
                    downtime_event['severity'] = severity
                    downtime_event['detected_at'] = datetime.now().isoformat()
                    downtime_events.append(downtime_event)
            
            logger.info(f"Detected {len(downtime_events)} downtime events")
            return downtime_events
            
        except Exception as e:
            logger.error(f"Error detecting downtime events: {e}")
            return []
    
    def format_alert_message(self, events: List[Dict]) -> str:
        """
        Format alert message for email notification.
        
        Args:
            events (List[Dict]): List of downtime events
            
        Returns:
            str: Formatted alert message
        """
        if not events:
            return "No downtime events detected."
        
        message_parts = [
            "🚨 WEBSITE MONITORING ALERT 🚨",
            f"\nDetected {len(events)} downtime event(s):\n"
        ]
        
        for i, event in enumerate(events, 1):
            timestamp = event.get('timestamp', 'Unknown')
            url = event.get('url', 'Unknown URL')
            status_code = event.get('status_code', 'Unknown')
            response_time = event.get('response_time', 'N/A')
            error_message = event.get('error_