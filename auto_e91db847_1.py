```python
"""
Configuration Management System for Monitoring and Alerting

This module provides a comprehensive configuration management system that:
1. Generates config.json files with URL lists for monitoring
2. Manages email settings including SMTP server configuration
3. Sets up alert thresholds and monitoring intervals
4. Validates email credentials and URL formats
5. Provides a complete configuration validation framework

The system is designed to be self-contained and easy to deploy for
monitoring infrastructure and alerting systems.
"""

import json
import re
import smtplib
import ssl
from email.mime.text import MimeText
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional, Tuple
import socket
import sys


class ConfigurationManager:
    """Main configuration management class for monitoring systems."""
    
    def __init__(self):
        self.config = {
            "urls": [],
            "email_settings": {},
            "monitoring": {},
            "alerts": {}
        }
    
    def add_urls(self, urls: List[str]) -> None:
        """Add URLs to monitor with validation."""
        valid_urls = []
        for url in urls:
            if self._validate_url(url):
                valid_urls.append(url)
                print(f"✓ Added valid URL: {url}")
            else:
                print(f"✗ Invalid URL format: {url}")
        
        self.config["urls"].extend(valid_urls)
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, 
                       password: str, recipients: List[str]) -> None:
        """Configure email settings with validation."""
        self.config["email_settings"] = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "recipients": []
        }
        
        # Validate email addresses
        for email in recipients:
            if self._validate_email(email):
                self.config["email_settings"]["recipients"].append(email)
                print(f"✓ Added valid email: {email}")
            else:
                print(f"✗ Invalid email format: {email}")
    
    def set_monitoring_intervals(self, check_interval: int, timeout: int, 
                               retry_attempts: int) -> None:
        """Set monitoring intervals and parameters."""
        self.config["monitoring"] = {
            "check_interval_seconds": check_interval,
            "timeout_seconds": timeout,
            "retry_attempts": retry_attempts,
            "enabled": True
        }
        print(f"✓ Monitoring configured: {check_interval}s intervals, {timeout}s timeout")
    
    def set_alert_thresholds(self, response_time_threshold: float, 
                           failure_threshold: int, recovery_threshold: int) -> None:
        """Configure alert thresholds."""
        self.config["alerts"] = {
            "response_time_threshold_ms": response_time_threshold,
            "consecutive_failures_threshold": failure_threshold,
            "consecutive_successes_for_recovery": recovery_threshold,
            "email_alerts_enabled": True
        }
        print(f"✓ Alert thresholds set: {response_time_threshold}ms response, {failure_threshold} failures")
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_email_credentials(self) -> bool:
        """Validate email credentials by attempting SMTP connection."""
        if not self.config.get("email_settings"):
            print("✗ No email settings configured")
            return False
        
        settings = self.config["email_settings"]
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Test SMTP connection
            with smtplib.SMTP(settings["smtp_server"], settings["smtp_port"]) as server:
                server.starttls(context=context)
                server.login(settings["username"], settings["password"])
                print(f"✓ Email credentials validated for {settings['smtp_server']}")
                return True
                
        except smtplib.SMTPAuthenticationError:
            print("✗ Email authentication failed - check username/password")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error: {str(e)}")
            return False
        except socket.gaierror:
            print(f"✗ Cannot connect to SMTP server: {settings['smtp_server']}")
            return False
        except Exception as e:
            print(f"✗ Email validation error: {str(e)}")
            return False
    
    def validate_urls(self) -> Dict[str, bool]:
        """Validate all configured URLs by checking if they're reachable."""
        results = {}
        for url in self.config["urls"]:
            try:
                # Basic socket connection test
                parsed = urlparse(url)
                host = parsed.hostname
                port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    print(f"✓ URL reachable: {url}")
                    results[url] = True
                else:
                    print(f"✗ URL unreachable: {url}")
                    results[url] = False
                    
            except Exception as e:
                print(f"✗ Error validating {url}: {str(e)}")
                results[url] = False
        
        return results
    
    def generate_config_file(self, filename: str = "config.json") -> bool:
        """Generate the configuration JSON file."""
        try:
            # Add metadata
            self.config["metadata"] = {
                "version": "1.0",
                "generated_by": "ConfigurationManager",
                "description": "Monitoring and alerting configuration"
            }
            
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            print(f"✓ Configuration file generated: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error generating config file: {str(e)}")
            return False
    
    def load_config_file(self, filename: str = "config.json") -> bool:
        """Load configuration from JSON file."""
        try:
            with open(filename, 'r') as f:
                self.config = json.load(f)
            print(f"✓ Configuration loaded from: {filename}")
            return True
            
        except FileNotFoundError:
            print(f"✗ Config file not found: {filename}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in config file: {str(e)}")
            return False
        except Exception as e:
            print(f"✗ Error loading config file: {str(e)}")
            return False
    
    def print_config_summary(self) -> None:
        """Print a summary of the current configuration."""
        print("\n" + "="*50)
        print("CONFIGURATION SUMMARY")
        print("="*50)
        
        print(f"URLs to monitor: {len(self.config.get('urls', []))}")
        for i, url in enumerate(self.config.get('urls', []), 1):
            print(f"  {i}. {url}")
        
        email_