```python
#!/usr/bin/env python3
"""
Email Notification System for Status Change Detection

This module provides a comprehensive email notification system that monitors service status
changes and sends formatted alert emails via SMTP. It includes intelligent state tracking
to prevent notification spam by only sending alerts when actual status transitions occur.

Key Features:
- Detects up/down status transitions for monitored services
- Sends formatted HTML and plain text alert emails via SMTP
- Maintains persistent state tracking using JSON file storage
- Implements cooldown periods to prevent notification spam
- Supports multiple email recipients and SMTP configurations
- Includes comprehensive error handling and logging
- Self-contained with minimal external dependencies

Usage:
    python script.py

The script will monitor predefined services and send notifications when status changes occur.
State is persisted between runs to maintain accurate transition detection.
"""

import json
import smtplib
import time
import os
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import httpx
from typing import Dict, List, Optional, Tuple


class StatusMonitor:
    """
    A comprehensive status monitoring and notification system.
    
    Tracks service status changes and sends email notifications for transitions,
    with built-in spam prevention through state tracking and cooldown periods.
    """
    
    def __init__(self, state_file: str = "status_state.json", cooldown_minutes: int = 15):
        """
        Initialize the status monitor.
        
        Args:
            state_file: Path to JSON file for storing service states
            cooldown_minutes: Minimum minutes between notifications for same service
        """
        self.state_file = state_file
        self.cooldown_period = timedelta(minutes=cooldown_minutes)
        self.state_data = self._load_state()
        
        # SMTP Configuration (update with your settings)
        self.smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'your_email@gmail.com',
            'password': 'your_app_password',  # Use app password for Gmail
            'use_tls': True
        }
        
        # Notification settings
        self.recipients = ['admin@company.com', 'ops@company.com']
        self.sender_name = 'System Monitor'
        
        # Services to monitor (add your services here)
        self.services = {
            'google': 'https://www.google.com',
            'github': 'https://api.github.com',
            'httpbin': 'https://httpbin.org/status/200'
        }
    
    def _load_state(self) -> Dict:
        """Load service states from JSON file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading state file: {e}")
            return {}
    
    def _save_state(self) -> None:
        """Save current service states to JSON file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state_data, f, indent=2, default=str)
            print(f"State saved to {self.state_file}")
        except Exception as e:
            print(f"Error saving state file: {e}")
    
    def _check_service_status(self, service_name: str, url: str) -> bool:
        """
        Check if a service is up by making HTTP request.
        
        Args:
            service_name: Name of the service
            url: URL to check
            
        Returns:
            True if service is up, False otherwise
        """
        try:
            print(f"Checking {service_name} at {url}...")
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                is_up = response.status_code < 400
                
            print(f"{service_name}: {'UP' if is_up else 'DOWN'} (Status: {response.status_code})")
            return is_up
            
        except Exception as e:
            print(f"Error checking {service_name}: {e}")
            return False
    
    def _should_send_notification(self, service_name: str, current_status: bool) -> Tuple[bool, str]:
        """
        Determine if notification should be sent based on state changes and cooldown.
        
        Args:
            service_name: Name of the service
            current_status: Current status (True=up, False=down)
            
        Returns:
            Tuple of (should_send, reason)
        """
        now = datetime.now()
        service_state = self.state_data.get(service_name, {})
        
        # Get previous status and last notification time
        previous_status = service_state.get('status')
        last_notification_str = service_state.get('last_notification')
        last_notification = None
        
        if last_notification_str:
            try:
                last_notification = datetime.fromisoformat(last_notification_str)
            except ValueError:
                pass
        
        # Check if status has changed
        if previous_status is None:
            return True, "Initial status check"
        
        if previous_status == current_status:
            return False, "No status change"
        
        # Status has changed, check cooldown
        if last_notification and (now - last_notification) < self.cooldown_period:
            remaining = self.cooldown_period - (now - last_notification)
            return False, f"Cooldown active (remaining: {remaining})"
        
        transition = "UP → DOWN" if not current_status else "DOWN → UP"
        return True, f"Status transition: {transition}"
    
    def _format_email_content(self, service_name: str, current_status: bool, 
                            previous_status: Optional[bool], timestamp: datetime) -> Tuple[str, str]:
        """
        Format email content for status change notification.
        
        Args:
            service_name: Name of the service
            current_status: Current service status
            previous_status: Previous service status
            timestamp: When the change occurred
            
        Returns:
            Tuple of (plain_text_content, html_content)
        """
        status_text = "UP" if current_status else "DOWN"
        status_emoji = "✅" if current_status else "❌"
        urgency = "CRITICAL" if not current_status else "INFO"
        
        if previous_status is not None:
            prev_text = "UP" if previous_status else "DOWN"
            transition = f"{prev_text} → {status_text}"
        else:
            transition = f"Initial check: {status_text}"
        
        # Plain text version
        plain_text = f"""
{urgency}: Service Status Change Alert

Service: {service_name}
Status: {status_text}
Transition: {transition}
Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

This is an automated notification from the System Monitor.
        """.strip()
        
        # HTML version
        html_content = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px;">
                <h2 style="color: {'#d32f2f' if not current_status else '#388e3c'};">
                    {status_emoji} {urgency}: Service Status Change
                </h2>
                
                <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Service</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{service_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #d