```python
#!/usr/bin/env python3
"""
Configuration Management and Email Alert System

This script provides two main functionalities:
1. Configuration Management: Generates initial config.json files with sample URLs and email settings
2. Email Alert System: Sends HTML-formatted downtime notifications via SMTP

The script is self-contained and only requires standard library modules plus httpx and anthropic
(though those are imported conditionally and not used in this implementation).

Usage: python script.py
"""

import json
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional

class ConfigManager:
    """Manages configuration file generation and loading."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
    
    def generate_initial_config(self) -> Dict:
        """Generate initial configuration with sample data."""
        config = {
            "monitoring": {
                "urls": [
                    {
                        "name": "Primary Website",
                        "url": "https://example.com",
                        "timeout": 30,
                        "check_interval": 300
                    },
                    {
                        "name": "API Endpoint",
                        "url": "https://api.example.com/health",
                        "timeout": 15,
                        "check_interval": 60
                    },
                    {
                        "name": "Database Service",
                        "url": "https://db.example.com/status",
                        "timeout": 45,
                        "check_interval": 600
                    }
                ]
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password",
                "use_tls": True,
                "sender_name": "System Monitor",
                "recipients": [
                    "admin@example.com",
                    "ops-team@example.com"
                ]
            },
            "alerts": {
                "enabled": True,
                "retry_attempts": 3,
                "retry_delay": 30,
                "escalation_threshold": 5
            }
        }
        return config
    
    def save_config(self, config: Dict) -> bool:
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            print(f"✓ Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving configuration: {e}")
            return False
    
    def load_config(self) -> Optional[Dict]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✓ Configuration loaded from {self.config_file}")
            return config
        except FileNotFoundError:
            print(f"✗ Configuration file {self.config_file} not found")
            return None
        except Exception as e:
            print(f"✗ Error loading configuration: {e}")
            return None

class EmailAlertSystem:
    """Handles email notifications for downtime alerts."""
    
    def __init__(self, email_config: Dict):
        self.smtp_server = email_config.get('smtp_server')
        self.smtp_port = email_config.get('smtp_port', 587)
        self.username = email_config.get('username')
        self.password = email_config.get('password')
        self.use_tls = email_config.get('use_tls', True)
        self.sender_name = email_config.get('sender_name', 'System Monitor')
        self.recipients = email_config.get('recipients', [])
    
    def create_html_template(self, service_name: str, url: str, status: str, 
                           timestamp: str, error_message: str = "") -> str:
        """Create HTML-formatted email template."""
        status_color = "#dc3545" if status.lower() == "down" else "#28a745"
        status_icon = "🔴" if status.lower() == "down" else "🟢"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
                .status {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .service-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .timestamp {{ color: #666; font-size: 14px; }}
                .error-box {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
                .url {{ word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="status">{status_icon} Service Alert: {status.upper()}</div>
                    <div>System Monitoring Notification</div>
                </div>
                
                <div class="service-info">
                    <h3>Service Details</h3>
                    <p><strong>Service Name:</strong> {service_name}</p>
                    <p><strong>URL:</strong> <span class="url">{url}</span></p>
                    <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status.upper()}</span></p>
                    <p class="timestamp"><strong>Timestamp:</strong> {timestamp}</p>
                </div>
                
                {f'<div class="error-box"><h4>Error Details</h4><p>{error_message}</p></div>' if error_message else ''}
                
                <div class="footer">
                    <p>This is an automated notification from your system monitoring service.</p>
                    <p>Please investigate and take appropriate action if necessary.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_template
    
    def send_alert(self, service_name: str, url: str, status: str, error_message: str = "") -> bool:
        """Send HTML-formatted downtime alert email."""
        if not self.recipients:
            print("✗ No recipients configured for email alerts")
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.username}>"
            msg['Subject'] = f"🚨 Service Alert: {service_name} is {status.upper()}"
            
            # Create HTML content
            html_content = self.create_html_template(
                service_name,