"""
Notification Module for Change Alerts

This module provides a unified notification system that can send alerts via both
SMTP email and Slack webhooks. It supports configurable templates for change
alerts with diff highlights and timestamp information.

Features:
- SMTP email notifications with HTML and plain text support
- Slack webhook notifications with rich formatting
- Configurable message templates
- Diff highlighting for change visualization
- Automatic timestamp generation
- Error handling and logging

Usage:
    notifier = NotificationManager()
    notifier.send_change_alert(
        title="Code Change Detected",
        changes=["+ Added new feature", "- Removed old code"],
        recipients={"email": ["user@example.com"], "slack": "webhook_url"}
    )
"""

import smtplib
import json
import urllib.request
import urllib.parse
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional, Union
import os


class NotificationTemplate:
    """Template class for formatting notification messages"""
    
    def __init__(self):
        self.email_html_template = """
        <html>
        <body>
            <h2>{title}</h2>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <h3>Changes Detected:</h3>
            <div style="background-color: #f5f5f5; padding: 10px; border-left: 4px solid #007cba;">
                <pre>{diff_content}</pre>
            </div>
            <p>{description}</p>
        </body>
        </html>
        """
        
        self.email_text_template = """
{title}

Timestamp: {timestamp}

Changes Detected:
{diff_content}

{description}
        """
        
        self.slack_template = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "{title}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Timestamp:*\n{timestamp}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Changes Detected:*\n