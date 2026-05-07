```python
#!/usr/bin/env python3
"""
Web Status Monitor and Email Alert System

This script monitors a list of URLs for availability and sends email alerts
when sites are down. It includes configuration templates and setup instructions.

Features:
- Monitors multiple URLs with configurable timeout
- Sends email notifications on status changes
- Logs results to CSV file
- JSON configuration management
- Self-contained with minimal dependencies

Required packages: pip install httpx
Standard library modules: smtplib, csv, json, datetime, time
"""

import json
import csv
import smtplib
import time
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    exit(1)


class WebMonitor:
    def __init__(self, config_file='monitor_config.json'):
        self.config_file = config_file
        self.config = self.load_or_create_config()
        
    def load_or_create_config(self):
        """Load existing config or create default configuration"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.create_default_config()
        else:
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration with sample data"""
        config = {
            "urls": [
                "https://httpbin.org/status/200",
                "https://jsonplaceholder.typicode.com/posts/1",
                "https://api.github.com",
                "https://httpstat.us/200",
                "https://www.google.com"
            ],
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "from_email": "your_email@gmail.com",
                "to_emails": ["admin@example.com", "alerts@example.com"]
            },
            "settings": {
                "timeout": 10,
                "check_interval": 300,
                "enable_email": False,
                "log_file": "url_status.csv"
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Created default configuration: {self.config_file}")
            print("Please edit the email credentials before enabling email alerts!")
        except Exception as e:
            print(f"Error creating config file: {e}")
            
        return config
    
    def check_url_status(self, url, timeout=10):
        """Check if URL is accessible and return status info"""
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url)
                return {
                    'url': url,
                    'status': 'UP',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'error': None,
                    'timestamp': datetime.now().isoformat()
                }
        except httpx.TimeoutException:
            return {
                'url': url,
                'status': 'DOWN',
                'status_code': None,
                'response_time': None,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'DOWN',
                'status_code': None,
                'response_time': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_email_alert(self, subject, body):
        """Send email notification"""
        if not self.config['settings']['enable_email']:
            return
            
        try:
            email_config = self.config['email']
            msg = MimeMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            for to_email in email_config['to_emails']:
                server.sendmail(email_config['from_email'], to_email, msg.as_string())
            
            server.quit()
            print(f"Email alert sent: {subject}")
            
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def log_to_csv(self, results):
        """Log results to CSV file"""
        try:
            log_file = self.config['settings']['log_file']
            file_exists = Path(log_file).exists()
            
            with open(log_file, 'a', newline='') as f:
                fieldnames = ['timestamp', 'url', 'status', 'status_code', 'response_time', 'error']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                for result in results:
                    writer.writerow({
                        'timestamp': result['timestamp'],
                        'url': result['url'],
                        'status': result['status'],
                        'status_code': result['status_code'],
                        'response_time': result['response_time'],
                        'error': result['error']
                    })
                    
        except Exception as e:
            print(f"Error logging to CSV: {e}")
    
    def monitor_urls(self):
        """Monitor all URLs and handle alerts"""
        print(f"Monitoring {len(self.config['urls'])} URLs...")
        print("-" * 80)
        
        results = []
        down_urls = []
        
        for url in self.config['urls']:
            result = self.check_url_status(url, self.config['settings']['timeout'])
            results.append(result)
            
            # Print status
            status_icon = "✅" if result['status'] == 'UP' else "❌"
            print(f"{status_icon} {result['url']}")
            print(f"   Status: {result['status']}")
            if result['status_code']:
                print(f"   Code: {result['status_code']}")
            if result['response_time']:
                print(f"   Response Time: {result['response_time']:.3f}s")
            if result['error']:
                print(f"   Error: {result['error']}")
                down_urls.append(result['url'])
            print()
        
        # Log results
        self.log_to_csv(results)
        
        # Send alerts if any URLs are down
        if down_urls and self.config['settings']['enable_email']:
            subject = f"Website Alert: {len(down_urls)} site(s) down"
            body = f"The following websites are currently down:\n\n"
            body += "\n".join(f"- {url}" for url in down_urls)
            body += f"\n\nCheck time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.send_email_alert(subject, body)
        
        print(f"Summary: {len(results) - len(down_urls)} UP, {len(down_urls)} DOWN")
        return results
    
    def print_setup_instructions(self):
        """Print installation and setup instructions"""
        print("=" * 80)
        print("WEB MONITOR SETUP INSTRUCTIONS")
        print("="