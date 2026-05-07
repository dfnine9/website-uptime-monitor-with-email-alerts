```python
#!/usr/bin/env python3
"""
Website Monitoring Configuration Generator

This module creates and validates configuration files for website monitoring systems.
It generates JSON configuration files with target websites, email settings, alert
thresholds, and monitoring intervals. Includes URL format validation and handles
configuration loading with proper error handling.

Features:
- URL format validation using urllib.parse
- Email format validation with regex
- JSON configuration file generation and loading
- Input validation for monitoring intervals and thresholds
- Self-contained with minimal dependencies

Usage:
    python script.py

The script will create a 'monitoring_config.json' file with sample configuration
and demonstrate loading and validation of the configuration.
"""

import json
import re
import sys
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
import os


class ConfigurationValidator:
    """Validates website monitoring configuration parameters."""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format using urllib.parse."""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme in ('http', 'https'), parsed.netloc])
        except Exception:
            return False
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format using regex."""
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_interval(interval: int) -> bool:
        """Validate monitoring interval (must be positive integer)."""
        return isinstance(interval, int) and interval > 0
    
    @staticmethod
    def validate_threshold(threshold: int) -> bool:
        """Validate alert threshold (must be positive integer)."""
        return isinstance(threshold, int) and threshold > 0


class MonitoringConfig:
    """Handles creation and validation of website monitoring configurations."""
    
    def __init__(self):
        self.validator = ConfigurationValidator()
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create a default monitoring configuration."""
        return {
            "target_websites": [
                {
                    "name": "Google",
                    "url": "https://www.google.com",
                    "expected_status": 200,
                    "timeout": 10
                },
                {
                    "name": "GitHub",
                    "url": "https://github.com",
                    "expected_status": 200,
                    "timeout": 15
                },
                {
                    "name": "Stack Overflow",
                    "url": "https://stackoverflow.com",
                    "expected_status": 200,
                    "timeout": 10
                }
            ],
            "email_settings": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "monitoring@example.com",
                "smtp_password": "app_password_here",
                "from_email": "monitoring@example.com",
                "to_emails": ["admin@example.com", "ops@example.com"],
                "use_tls": True
            },
            "alert_thresholds": {
                "response_time_ms": 5000,
                "failure_count": 3,
                "consecutive_failures": 2
            },
            "monitoring_intervals": {
                "check_interval_seconds": 300,
                "report_interval_hours": 24,
                "retry_interval_seconds": 60
            },
            "general_settings": {
                "log_level": "INFO",
                "max_concurrent_checks": 10,
                "user_agent": "Website-Monitor/1.0"
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        try:
            # Validate target websites
            if "target_websites" not in config:
                errors.append("Missing 'target_websites' section")
            else:
                for i, website in enumerate(config["target_websites"]):
                    if not isinstance(website, dict):
                        errors.append(f"Website {i}: Must be a dictionary")
                        continue
                    
                    if "url" not in website:
                        errors.append(f"Website {i}: Missing 'url' field")
                    elif not self.validator.validate_url(website["url"]):
                        errors.append(f"Website {i}: Invalid URL format '{website['url']}'")
                    
                    if "name" not in website:
                        errors.append(f"Website {i}: Missing 'name' field")
                    
                    if "expected_status" in website and not isinstance(website["expected_status"], int):
                        errors.append(f"Website {i}: 'expected_status' must be an integer")
            
            # Validate email settings
            if "email_settings" not in config:
                errors.append("Missing 'email_settings' section")
            else:
                email_config = config["email_settings"]
                
                if "from_email" in email_config and not self.validator.validate_email(email_config["from_email"]):
                    errors.append(f"Invalid 'from_email' format: {email_config['from_email']}")
                
                if "to_emails" in email_config:
                    if not isinstance(email_config["to_emails"], list):
                        errors.append("'to_emails' must be a list")
                    else:
                        for email in email_config["to_emails"]:
                            if not self.validator.validate_email(email):
                                errors.append(f"Invalid email format in 'to_emails': {email}")
                
                if "smtp_port" in email_config and not isinstance(email_config["smtp_port"], int):
                    errors.append("'smtp_port' must be an integer")
            
            # Validate alert thresholds
            if "alert_thresholds" not in config:
                errors.append("Missing 'alert_thresholds' section")
            else:
                thresholds = config["alert_thresholds"]
                
                for field in ["response_time_ms", "failure_count", "consecutive_failures"]:
                    if field in thresholds and not self.validator.validate_threshold(thresholds[field]):
                        errors.append(f"'{field}' must be a positive integer")
            
            # Validate monitoring intervals
            if "monitoring_intervals" not in config:
                errors.append("Missing 'monitoring_intervals' section")
            else:
                intervals = config["monitoring_intervals"]
                
                for field in ["check_interval_seconds", "report_interval_hours", "retry_interval_seconds"]:
                    if field in intervals and not self.validator.validate_interval(intervals[field]):
                        errors.append(f"'{field}' must be a positive integer")
        
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def save_config(self, config: Dict[str, Any], filename: str) -> bool:
        """Save configuration to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}", file=sys.stderr)
            return False
    
    def load_config(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load configuration from JSON file."""
        try:
            if not os.path.exists(filename):
                print(f"Configuration file '{filename}' not found", file=sys.stderr)
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in configuration file: {e}", file=