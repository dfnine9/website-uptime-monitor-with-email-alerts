```python
#!/usr/bin/env python3
"""
Monitoring Data Analyzer and Alert System

This script analyzes recent monitoring data to detect downtime events and response 
times that exceed predefined thresholds. When incidents are detected, it sends 
alerts via email and/or webhooks with detailed incident information.

Features:
- Simulates monitoring data collection (replace with actual data source)
- Configurable response time thresholds
- Email alerts via SMTP
- Webhook notifications via HTTP POST
- Comprehensive error handling
- Detailed logging to stdout

Usage: python script.py

Dependencies: httpx (pip install httpx)
"""

import json
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import random

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx")
    exit(1)


class MonitoringAnalyzer:
    def __init__(self):
        # Configuration - modify these values as needed
        self.config = {
            'response_time_threshold': 5.0,  # seconds
            'downtime_threshold': 0,  # 0 means any failed request triggers alert
            'email': {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'your-email@gmail.com',  # Replace with actual email
                'password': 'your-app-password',      # Replace with actual password
                'recipients': ['admin@company.com']   # Replace with actual recipients
            },
            'webhook': {
                'enabled': True,
                'url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',  # Replace with actual webhook
                'timeout': 10
            }
        }
        
        self.incidents = []
        
    def generate_sample_monitoring_data(self) -> List[Dict[str, Any]]:
        """
        Generate sample monitoring data for demonstration.
        In production, replace this with actual data source integration.
        """
        services = ['web-app', 'api-gateway', 'database', 'cache-server', 'auth-service']
        data = []
        
        current_time = datetime.now()
        
        for i in range(50):  # Generate 50 data points
            timestamp = current_time - timedelta(minutes=i)
            service = random.choice(services)
            
            # Simulate occasional issues
            if random.random() < 0.1:  # 10% chance of issues
                if random.random() < 0.5:  # 50% chance of slow response
                    response_time = random.uniform(5.5, 15.0)  # Slow but successful
                    status = 200
                else:  # 50% chance of downtime
                    response_time = 0
                    status = random.choice([500, 502, 503, 504])
            else:
                response_time = random.uniform(0.1, 3.0)  # Normal response
                status = 200
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'service': service,
                'response_time': response_time,
                'status_code': status,
                'endpoint': f'/{service}/health'
            })
        
        return sorted(data, key=lambda x: x['timestamp'])
    
    def analyze_monitoring_data(self, data: List[Dict[str, Any]]) -> None:
        """Analyze monitoring data for incidents."""
        print(f"Analyzing {len(data)} monitoring data points...")
        
        for record in data:
            try:
                # Check for downtime (non-200 status codes)
                if record['status_code'] != 200:
                    incident = {
                        'type': 'downtime',
                        'service': record['service'],
                        'timestamp': record['timestamp'],
                        'status_code': record['status_code'],
                        'endpoint': record['endpoint'],
                        'severity': 'high' if record['status_code'] >= 500 else 'medium'
                    }
                    self.incidents.append(incident)
                    print(f"INCIDENT: Downtime detected - {record['service']} returned {record['status_code']}")
                
                # Check for slow response times
                elif record['response_time'] > self.config['response_time_threshold']:
                    incident = {
                        'type': 'slow_response',
                        'service': record['service'],
                        'timestamp': record['timestamp'],
                        'response_time': record['response_time'],
                        'threshold': self.config['response_time_threshold'],
                        'endpoint': record['endpoint'],
                        'severity': 'medium' if record['response_time'] < 10 else 'high'
                    }
                    self.incidents.append(incident)
                    print(f"INCIDENT: Slow response detected - {record['service']} took {record['response_time']:.2f}s")
                    
            except KeyError as e:
                print(f"ERROR: Missing field in monitoring data: {e}")
                continue
            except Exception as e:
                print(f"ERROR: Failed to analyze record: {e}")
                continue
    
    def format_incident_details(self, incident: Dict[str, Any]) -> str:
        """Format incident details for alerts."""
        timestamp = datetime.fromisoformat(incident['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        if incident['type'] == 'downtime':
            return f"""
DOWNTIME INCIDENT DETECTED
Service: {incident['service']}
Endpoint: {incident['endpoint']}
Status Code: {incident['status_code']}
Timestamp: {timestamp}
Severity: {incident['severity'].upper()}
"""
        else:  # slow_response
            return f"""
SLOW RESPONSE INCIDENT DETECTED
Service: {incident['service']}
Endpoint: {incident['endpoint']}
Response Time: {incident['response_time']:.2f}s
Threshold: {incident['threshold']:.2f}s
Timestamp: {timestamp}
Severity: {incident['severity'].upper()}
"""
    
    def send_email_alert(self, incident: Dict[str, Any]) -> bool:
        """Send email alert for incident."""
        if not self.config['email']['enabled']:
            return True
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = ', '.join(self.config['email']['recipients'])
            msg['Subject'] = f"MONITORING ALERT: {incident['type'].title()} - {incident['service']}"
            
            body = self.format_incident_details(incident)
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            
            text = msg.as_string()
            server.sendmail(self.config['email']['username'], self.config['email']['recipients'], text)
            server.quit()
            
            print(f"Email alert sent successfully for {incident['service']} incident")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("ERROR: Email authentication failed - check credentials")
            return False
        except smtplib.SMTPException as e:
            print(f"ERROR: Failed to send email alert: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error sending email: {e}")
            return False
    
    def send_webhook_alert(self, incident: Dict[str, Any]) -> bool:
        """Send webhook alert for incident."""
        if not self.config['webhook']['enabled']:
            return True
            
        try:
            payload = {
                'text': f"🚨 Monitoring Alert: {incident['type'].title()} detected",
                'attachments