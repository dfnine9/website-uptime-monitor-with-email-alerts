```python
"""
Email Notification Module for Site Monitoring

This module provides functionality to send email alerts when websites are down.
It uses smtplib to send emails with SMTP credentials from environment variables,
formats alert messages with site details and downtime duration, and implements
rate limiting to prevent spam.

Features:
- SMTP email sending with environment variable configuration
- Site monitoring with HTTP status checking
- Rate limiting to prevent spam notifications
- Formatted alert messages with downtime tracking
- Error handling for network and email failures

Usage:
    python script.py

Environment Variables Required:
    SMTP_SERVER: SMTP server hostname
    SMTP_PORT: SMTP server port (default: 587)
    SMTP_USERNAME: SMTP authentication username
    SMTP_PASSWORD: SMTP authentication password
    ALERT_FROM_EMAIL: Sender email address
    ALERT_TO_EMAIL: Recipient email address
"""

import smtplib
import os
import time
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import httpx
import threading
from dataclasses import dataclass


@dataclass
class SiteStatus:
    """Data class to track site status information"""
    url: str
    is_down: bool = False
    down_since: Optional[datetime] = None
    last_notification: Optional[datetime] = None
    consecutive_failures: int = 0


class EmailNotifier:
    """Email notification handler for site monitoring alerts"""
    
    def __init__(self):
        """Initialize email notifier with SMTP configuration from environment"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.username = os.getenv('SMTP_USERNAME')
        self.password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('ALERT_FROM_EMAIL')
        self.to_email = os.getenv('ALERT_TO_EMAIL')
        
        if not all([self.username, self.password, self.from_email, self.to_email]):
            raise ValueError("Missing required environment variables for email configuration")
    
    def send_alert(self, site_url: str, downtime_duration: str, error_details: str = "") -> bool:
        """
        Send email alert for site downtime
        
        Args:
            site_url: URL of the down site
            downtime_duration: Human-readable downtime duration
            error_details: Additional error information
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Subject'] = f"SITE DOWN ALERT: {site_url}"
            
            # Format email body
            body = self._format_alert_message(site_url, downtime_duration, error_details)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✓ Alert email sent for {site_url}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email alert for {site_url}: {str(e)}")
            return False
    
    def _format_alert_message(self, site_url: str, downtime_duration: str, error_details: str) -> str:
        """Format HTML email message for site alert"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: #d32f2f;">🚨 Website Down Alert</h2>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #d32f2f;">
                <p><strong>Site URL:</strong> <a href="{site_url}">{site_url}</a></p>
                <p><strong>Status:</strong> DOWN</p>
                <p><strong>Downtime Duration:</strong> {downtime_duration}</p>
                <p><strong>Alert Time:</strong> {timestamp}</p>
                {f'<p><strong>Error Details:</strong> {error_details}</p>' if error_details else ''}
            </div>
            
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                This is an automated alert from the Site Monitoring System.
            </p>
        </body>
        </html>
        """
        
        return html_body


class RateLimiter:
    """Rate limiter to prevent spam notifications"""
    
    def __init__(self, min_interval_minutes: int = 30):
        """
        Initialize rate limiter
        
        Args:
            min_interval_minutes: Minimum interval between notifications for same site
        """
        self.min_interval = timedelta(minutes=min_interval_minutes)
        self.last_notifications: Dict[str, datetime] = {}
    
    def can_send_notification(self, site_url: str) -> bool:
        """
        Check if notification can be sent for a site
        
        Args:
            site_url: URL to check rate limiting for
            
        Returns:
            bool: True if notification can be sent, False if rate limited
        """
        now = datetime.now()
        last_notification = self.last_notifications.get(site_url)
        
        if not last_notification:
            return True
        
        time_since_last = now - last_notification
        return time_since_last >= self.min_interval
    
    def record_notification(self, site_url: str):
        """Record that a notification was sent for rate limiting"""
        self.last_notifications[site_url] = datetime.now()


class SiteMonitor:
    """Website monitoring and alerting system"""
    
    def __init__(self, sites: List[str], check_interval: int = 60):
        """
        Initialize site monitor
        
        Args:
            sites: List of URLs to monitor
            check_interval: Interval between checks in seconds
        """
        self.sites = sites
        self.check_interval = check_interval
        self.site_status: Dict[str, SiteStatus] = {
            url: SiteStatus(url=url) for url in sites
        }
        self.email_notifier = EmailNotifier()
        self.rate_limiter = RateLimiter(min_interval_minutes=30)
        self.running = False
    
    def check_site(self, url: str) -> tuple[bool, str]:
        """
        Check if a site is up
        
        Args:
            url: URL to check
            
        Returns:
            tuple: (is_up, error_message)
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, follow_redirects=True)
                is_up = response.status_code < 500
                error_msg = f"HTTP {response.status_code}" if not is_up else ""
                return is_up, error_msg
                
        except httpx.TimeoutException:
            return False, "Connection timeout"
        except httpx.ConnectError:
            return False, "Connection failed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format timedelta into human-readable string"""
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minutes"
        else:
            hours