```python
#!/usr/bin/env python3
"""
Weather Alert Notification Module

This module creates a comprehensive notification system for weather alerts.
It formats weather alert data and sends notifications via both email (SMTP)
and SMS (Twilio API) when severe weather conditions are detected.

Features:
- Email notifications via SMTP with HTML formatting
- SMS notifications via Twilio API
- Configurable severity thresholds
- Error handling and logging
- Mock weather data for demonstration

Dependencies: httpx, anthropic (as specified in requirements)
"""

import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import base64
import urllib.parse

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherAlert:
    """Represents a weather alert with severity and details."""
    
    def __init__(self, alert_type: str, severity: str, description: str, 
                 location: str, issued_time: datetime, expires_time: datetime):
        self.alert_type = alert_type
        self.severity = severity
        self.description = description
        self.location = location
        self.issued_time = issued_time
        self.expires_time = expires_time
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary format."""
        return {
            'type': self.alert_type,
            'severity': self.severity,
            'description': self.description,
            'location': self.location,
            'issued': self.issued_time.isoformat(),
            'expires': self.expires_time.isoformat()
        }

class NotificationFormatter:
    """Formats weather alerts for different notification channels."""
    
    @staticmethod
    def format_email(alert: WeatherAlert) -> Dict[str, str]:
        """Format alert for email notification."""
        subject = f"🌩️ SEVERE WEATHER ALERT: {alert.alert_type} - {alert.location}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="background-color: #ff6b6b; color: white; padding: 15px; border-radius: 8px;">
                <h2>⚠️ SEVERE WEATHER ALERT</h2>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; border: 2px solid #ff6b6b; border-radius: 8px;">
                <h3>{alert.alert_type}</h3>
                <p><strong>Severity:</strong> <span style="color: #d32f2f;">{alert.severity}</span></p>
                <p><strong>Location:</strong> {alert.location}</p>
                <p><strong>Issued:</strong> {alert.issued_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Expires:</strong> {alert.expires_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px;">
                <h4>Alert Details:</h4>
                <p>{alert.description}</p>
            </div>
            
            <div style="margin: 20px 0; padding: 10px; background-color: #e8f5e8; border-radius: 8px;">
                <p><strong>Safety Reminder:</strong> Stay indoors and monitor local weather updates.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        SEVERE WEATHER ALERT: {alert.alert_type}
        
        Severity: {alert.severity}
        Location: {alert.location}
        Issued: {alert.issued_time.strftime('%Y-%m-%d %H:%M:%S')}
        Expires: {alert.expires_time.strftime('%Y-%m-%d %H:%M:%S')}
        
        Details: {alert.description}
        
        Safety Reminder: Stay indoors and monitor local weather updates.
        """
        
        return {
            'subject': subject,
            'html_body': html_body,
            'text_body': text_body
        }
    
    @staticmethod
    def format_sms(alert: WeatherAlert) -> str:
        """Format alert for SMS notification."""
        sms_text = (f"🚨 WEATHER ALERT: {alert.alert_type} in {alert.location}. "
                   f"Severity: {alert.severity}. {alert.description[:100]}... "
                   f"Expires: {alert.expires_time.strftime('%m/%d %H:%M')}")
        
        # SMS has character limits, truncate if necessary
        return sms_text[:160] if len(sms_text) > 160 else sms_text

class EmailNotifier:
    """Handles email notifications via SMTP."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """Send email notification."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            # Attach both text and HTML versions
            text_part = MIMEText(text_body, 'plain')
            html_part = MIMEText(html_body, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

class TwilioSMSNotifier:
    """Handles SMS notifications via Twilio API."""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS notification via Twilio API."""
        try:
            # Create authentication header
            credentials = f"{self.account_sid}:{self.auth_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'From': self.from_number,
                'To': to_number,
                'Body': message
            }
            
            # URL encode the data
            encoded_data = urllib.parse.urlencode(data)
            
            with httpx.Client() as client:
                response = client.post(self.base_url, headers=headers, content