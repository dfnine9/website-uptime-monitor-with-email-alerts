```python
#!/usr/bin/env python3
"""
Email Notification Module for Site Monitoring

This module provides functionality to monitor website availability and send
email notifications when sites go down. It checks HTTP status codes and
connection errors, then sends formatted email alerts with site details,
timestamps, and error information.

Features:
- HTTP/HTTPS site monitoring with timeout handling
- SMTP email notifications with HTML formatting
- Configurable retry logic and error categorization
- Structured logging of monitoring events
- Self-contained with minimal dependencies

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - smtplib, email (standard library)
    - datetime, json (standard library)
"""

import smtplib
import json
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import socket
import ssl

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    exit(1)


class EmailNotifier:
    """Handles email notifications for site monitoring alerts."""
    
    def __init__(self, smtp_config):
        """
        Initialize email notifier with SMTP configuration.
        
        Args:
            smtp_config (dict): SMTP server configuration
        """
        self.smtp_config = smtp_config
    
    def send_alert(self, site_name, error_details, timestamp):
        """
        Send email alert for site downtime.
        
        Args:
            site_name (str): Name/URL of the failed site
            error_details (dict): Error information and diagnostics
            timestamp (datetime): When the error occurred
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔴 Site Down Alert: {site_name}"
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = ', '.join(self.smtp_config['to_emails'])
            
            # Create HTML email body
            html_body = self._create_html_alert(site_name, error_details, timestamp)
            html_part = MIMEText(html_body, 'html')
            
            # Create plain text version
            text_body = self._create_text_alert(site_name, error_details, timestamp)
            text_part = MIMEText(text_body, 'plain')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls()
                if self.smtp_config.get('username'):
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                
                server.send_message(msg)
            
            print(f"✅ Alert email sent for {site_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email alert: {str(e)}")
            return False
    
    def _create_html_alert(self, site_name, error_details, timestamp):
        """Create HTML formatted email alert."""
        severity_color = self._get_severity_color(error_details['error_type'])
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .alert-header {{ background-color: {severity_color}; color: white; padding: 15px; border-radius: 5px; }}
                .details {{ background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid {severity_color}; }}
                .timestamp {{ color: #6c757d; font-size: 0.9em; }}
                .error-code {{ font-family: monospace; background-color: #e9ecef; padding: 2px 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="alert-header">
                <h2>🔴 Site Monitoring Alert</h2>
                <p><strong>{site_name}</strong> is currently unavailable</p>
            </div>
            
            <div class="details">
                <h3>Error Details:</h3>
                <p><strong>Error Type:</strong> {error_details['error_type']}</p>
                <p><strong>Status Code:</strong> <span class="error-code">{error_details.get('status_code', 'N/A')}</span></p>
                <p><strong>Error Message:</strong> {error_details['error_message']}</p>
                <p><strong>Response Time:</strong> {error_details.get('response_time', 'N/A')}ms</p>
                <p><strong>Retry Attempts:</strong> {error_details.get('retry_count', 0)}</p>
            </div>
            
            <div class="timestamp">
                <p><strong>Detected At:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Alert ID:</strong> {error_details.get('alert_id', 'N/A')}</p>
            </div>
            
            <hr>
            <p><small>This is an automated alert from the Site Monitoring System</small></p>
        </body>
        </html>
        """
        return html
    
    def _create_text_alert(self, site_name, error_details, timestamp):
        """Create plain text email alert."""
        return f"""
SITE MONITORING ALERT
====================

Site: {site_name}
Status: DOWN
Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

ERROR DETAILS:
- Type: {error_details['error_type']}
- Status Code: {error_details.get('status_code', 'N/A')}
- Message: {error_details['error_message']}
- Response Time: {error_details.get('response_time', 'N/A')}ms
- Retry Attempts: {error_details.get('retry_count', 0)}
- Alert ID: {error_details.get('alert_id', 'N/A')}

This is an automated alert from the Site Monitoring System.
        """
    
    def _get_severity_color(self, error_type):
        """Get color code based on error severity."""
        colors = {
            'CONNECTION_ERROR': '#dc3545',  # Red
            'TIMEOUT': '#fd7e14',          # Orange
            'HTTP_ERROR': '#ffc107',       # Yellow
            'SSL_ERROR': '#dc3545',        # Red
            'UNKNOWN': '#6c757d'           # Gray
        }
        return colors.get(error_type, '#dc3545')


class SiteMonitor:
    """Monitors website availability and triggers alerts."""
    
    def __init__(self, notifier, timeout=30, max_retries=3):
        """
        Initialize site monitor.
        
        Args:
            notifier (EmailNotifier): Email notification handler
            timeout (int): Request timeout in seconds
            max_retries (int): Maximum retry attempts
        """
        self.notifier = notifier
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.Client(timeout=timeout)
    
    def check_site(self, url, expected_status=200):
        """
        Check if a site is accessible and responding correctly.
        
        Args:
            url (str): URL to monitor
            expected_status (int): Expected HTTP status code
            
        Returns:
            dict: Check results with status and details
        """
        site_name = url
        alert_id = f"{int(time.time())}_{hash(url) % 10000}"
        
        for attempt in range(self.max_