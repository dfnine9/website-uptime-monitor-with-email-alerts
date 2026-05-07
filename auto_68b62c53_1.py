```python
"""
Email Notification Module for Website Status Monitoring

This module monitors website status changes from a CSV log file and sends email alerts
when sites go down (status code != 200). It tracks status changes and sends formatted
notifications via SMTP.

Features:
- Detects status code changes from CSV logs
- Sends email alerts for downtime events
- Uses only standard library modules (no external dependencies)
- Configurable SMTP settings
- Error handling and logging to stdout

Usage:
    python script.py

The script expects a CSV file with columns: timestamp, url, status_code
"""

import csv
import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional


class WebsiteStatusMonitor:
    def __init__(self, csv_file: str = "website_logs.csv", state_file: str = "status_state.json"):
        self.csv_file = csv_file
        self.state_file = state_file
        self.previous_status = self.load_previous_status()
        
        # SMTP Configuration - can be set via environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', 'monitor@example.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.recipient_emails = os.getenv('RECIPIENT_EMAILS', 'admin@example.com').split(',')
        
    def load_previous_status(self) -> Dict[str, int]:
        """Load previous status from state file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading previous status: {e}")
        return {}
    
    def save_current_status(self, current_status: Dict[str, int]) -> None:
        """Save current status to state file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(current_status, f, indent=2)
        except Exception as e:
            print(f"Error saving current status: {e}")
    
    def read_csv_logs(self) -> List[Dict]:
        """Read and parse CSV log file"""
        logs = []
        try:
            with open(self.csv_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    logs.append({
                        'timestamp': row.get('timestamp', ''),
                        'url': row.get('url', ''),
                        'status_code': int(row.get('status_code', 0))
                    })
        except FileNotFoundError:
            print(f"CSV file {self.csv_file} not found. Creating sample data...")
            self.create_sample_csv()
            return self.read_csv_logs()
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        return logs
    
    def create_sample_csv(self) -> None:
        """Create sample CSV data for testing"""
        sample_data = [
            {'timestamp': datetime.now().isoformat(), 'url': 'https://example.com', 'status_code': 200},
            {'timestamp': datetime.now().isoformat(), 'url': 'https://test.com', 'status_code': 500},
            {'timestamp': datetime.now().isoformat(), 'url': 'https://demo.com', 'status_code': 404},
        ]
        
        try:
            with open(self.csv_file, 'w', newline='') as csvfile:
                fieldnames = ['timestamp', 'url', 'status_code']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)
            print(f"Created sample CSV file: {self.csv_file}")
        except Exception as e:
            print(f"Error creating sample CSV: {e}")
    
    def detect_status_changes(self, logs: List[Dict]) -> List[Dict]:
        """Detect status code changes and identify downtime events"""
        changes = []
        current_status = {}
        
        # Get the latest status for each URL
        for log in logs:
            url = log['url']
            status_code = log['status_code']
            current_status[url] = status_code
        
        # Compare with previous status
        for url, current_code in current_status.items():
            previous_code = self.previous_status.get(url)
            
            if previous_code is not None and previous_code != current_code:
                changes.append({
                    'url': url,
                    'previous_status': previous_code,
                    'current_status': current_code,
                    'timestamp': datetime.now().isoformat(),
                    'is_down': current_code != 200,
                    'was_down': previous_code != 200
                })
            elif previous_code is None and current_code != 200:
                # New URL that's down
                changes.append({
                    'url': url,
                    'previous_status': None,
                    'current_status': current_code,
                    'timestamp': datetime.now().isoformat(),
                    'is_down': True,
                    'was_down': False
                })
        
        # Update previous status
        self.previous_status = current_status
        self.save_current_status(current_status)
        
        return changes
    
    def format_email_content(self, changes: List[Dict]) -> str:
        """Format email content for status change alerts"""
        html_content = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { color: #d32f2f; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
                .alert { background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 10px; margin: 10px 0; }
                .recovery { background-color: #e8f5e8; border-left: 4px solid #4caf50; padding: 10px; margin: 10px 0; }
                .url { font-weight: bold; color: #1976d2; }
                .status { font-family: monospace; }
                .timestamp { color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">🚨 Website Status Alert</div>
        """
        
        down_sites = []
        recovered_sites = []
        
        for change in changes:
            if change['is_down'] and not change['was_down']:
                down_sites.append(change)
            elif not change['is_down'] and change['was_down']:
                recovered_sites.append(change)
        
        if down_sites:
            html_content += "<h2>🔴 Sites Going Down:</h2>"
            for site in down_sites:
                html_content += f"""
                <div class="alert">
                    <div class="url">{site['url']}</div>
                    <div class="status">Status: {site['previous_status']} → {site['current_status']}</div>
                    <div class="timestamp">Time: {site['timestamp']}</div>
                </div>
                """
        
        if recovered_sites:
            html_content += "<h2>🟢 Sites Recovering:</h2>"
            for site in recovered_sites:
                html_content += f"""
                <div class="recovery">
                    <div class="url">{site['url']}</div>
                    <div class="status">Status: