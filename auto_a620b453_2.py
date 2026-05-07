```python
#!/usr/bin/env python3
"""
Website Monitoring System

A self-contained website monitoring tool that checks URL availability,
response times, and content changes. Configurable via JSON/YAML files
with email alerting capabilities.

Features:
- Multi-URL monitoring with individual thresholds
- Email notifications via SMTP
- Response time tracking
- Basic content change detection
- Configurable monitoring intervals
- Comprehensive error handling and logging

Usage: python script.py

Configuration is loaded from 'monitor_config.json' or 'monitor_config.yaml'
in the current directory. If no config file exists, a sample will be created.
"""

import json
import yaml
import time
import smtplib
import hashlib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import signal
import sys

try:
    import httpx
except ImportError:
    print("ERROR: httpx is required. Install with: pip install httpx")
    sys.exit(1)

class WebsiteMonitor:
    def __init__(self, config_path: str = "monitor_config.json"):
        self.config_path = config_path
        self.config = {}
        self.running = False
        self.content_hashes = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def create_sample_config(self) -> Dict[str, Any]:
        """Create a sample configuration file."""
        sample_config = {
            "monitoring": {
                "interval_seconds": 300,
                "timeout_seconds": 30,
                "user_agent": "WebsiteMonitor/1.0"
            },
            "urls": [
                {
                    "name": "Google",
                    "url": "https://www.google.com",
                    "response_time_threshold": 2.0,
                    "expected_status_code": 200,
                    "check_content_changes": False,
                    "alert_on_failure": True
                },
                {
                    "name": "Example Site",
                    "url": "https://httpbin.org/status/200",
                    "response_time_threshold": 5.0,
                    "expected_status_code": 200,
                    "check_content_changes": True,
                    "alert_on_failure": True
                }
            ],
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "use_tls": True,
                "recipients": ["admin@yourcompany.com"],
                "subject_prefix": "[Website Monitor Alert]"
            }
        }
        return sample_config

    def load_config(self) -> bool:
        """Load configuration from JSON or YAML file."""
        config_file = Path(self.config_path)
        yaml_file = Path(self.config_path.replace('.json', '.yaml'))
        
        # Try to load existing config
        for file_path in [config_file, yaml_file]:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        if file_path.suffix.lower() in ['.yaml', '.yml']:
                            self.config = yaml.safe_load(f)
                        else:
                            self.config = json.load(f)
                    
                    self.logger.info(f"Loaded configuration from {file_path}")
                    return True
                except Exception as e:
                    self.logger.error(f"Error loading config from {file_path}: {e}")
                    continue
        
        # Create sample config if none exists
        try:
            self.config = self.create_sample_config()
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.logger.info(f"Created sample configuration file: {config_file}")
            self.logger.info("Please edit the configuration file and restart the monitor.")
            return True
        except Exception as e:
            self.logger.error(f"Error creating sample config: {e}")
            return False

    def send_email_alert(self, subject: str, body: str) -> bool:
        """Send email alert using configured SMTP settings."""
        email_config = self.config.get('email', {})
        
        if not email_config.get('enabled', False):
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = f"{email_config.get('subject_prefix', '')} {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            
            if email_config.get('use_tls', True):
                server.starttls()
            
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False

    def get_content_hash(self, content: str) -> str:
        """Generate MD5 hash of content for change detection."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def check_website(self, site_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check a single website and return status information."""
        site_name = site_config['name']
        url = site_config['url']
        
        result = {
            'name': site_name,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'response_time': None,
            'status_code': None,
            'error': None,
            'content_changed': False
        }
        
        try:
            timeout = self.config['monitoring'].get('timeout_seconds', 30)
            user_agent = self.config['monitoring'].get('user_agent', 'WebsiteMonitor/1.0')
            
            headers = {'User-Agent': user_agent}
            
            with httpx.Client(timeout=timeout) as client:
                start_time = time.time()
                response = client.get(url, headers=headers, follow_redirects=True)
                response_time = time.time() - start_time
                
                result['response_time'] = round(response_time, 3)
                result['status_code'] = response.status_code
                
                # Check status code
                expected_status = site_config.get('expected_status_code', 200)
                if response.status_code == expected_status:
                    result['success'] = True
                else:
                    result['error'] = f"Unexpected status code: {response.status_code} (expected: {expected_status})"
                
                # Check response time threshold
                threshold = site_config.get('response_time_threshold', 10.0)
                if response_time > threshold:
                    result['success