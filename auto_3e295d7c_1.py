```python
#!/usr/bin/env python3
"""
Website Monitoring Configuration Generator

This module creates a comprehensive configuration file for website monitoring,
including website lists, alert thresholds, and notification settings.
It generates both JSON and YAML format configurations with sensible defaults
for monitoring response times, uptime, and various notification channels.

Features:
- Generates monitoring configuration for multiple websites
- Configurable response time thresholds and alert rules
- Multiple notification channel support (email, slack, webhook)
- Error handling and validation
- Self-contained with minimal dependencies

Usage:
    python script.py
"""

import json
import yaml
import sys
from typing import Dict, List, Any
from datetime import datetime


def create_default_config() -> Dict[str, Any]:
    """Create default monitoring configuration with comprehensive settings."""
    
    config = {
        "metadata": {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "description": "Website monitoring configuration"
        },
        
        "websites": [
            {
                "name": "Google",
                "url": "https://www.google.com",
                "method": "GET",
                "timeout": 10,
                "interval": 60,
                "enabled": True,
                "headers": {
                    "User-Agent": "Website-Monitor/1.0"
                }
            },
            {
                "name": "GitHub",
                "url": "https://github.com",
                "method": "GET",
                "timeout": 15,
                "interval": 120,
                "enabled": True,
                "headers": {
                    "User-Agent": "Website-Monitor/1.0"
                }
            },
            {
                "name": "Stack Overflow",
                "url": "https://stackoverflow.com",
                "method": "GET",
                "timeout": 10,
                "interval": 300,
                "enabled": True,
                "headers": {
                    "User-Agent": "Website-Monitor/1.0"
                }
            }
        ],
        
        "thresholds": {
            "response_time": {
                "warning": 2.0,
                "critical": 5.0,
                "unit": "seconds"
            },
            "uptime": {
                "warning": 99.0,
                "critical": 95.0,
                "unit": "percentage"
            },
            "consecutive_failures": {
                "warning": 2,
                "critical": 5,
                "unit": "count"
            }
        },
        
        "notifications": {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password",
                "from_address": "monitor@yourcompany.com",
                "to_addresses": [
                    "admin@yourcompany.com",
                    "ops@yourcompany.com"
                ],
                "subject_prefix": "[Website Monitor]"
            },
            
            "slack": {
                "enabled": False,
                "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                "channel": "#alerts",
                "username": "Website Monitor",
                "icon_emoji": ":warning:"
            },
            
            "webhook": {
                "enabled": False,
                "url": "https://your-webhook-endpoint.com/alerts",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer YOUR-TOKEN"
                },
                "timeout": 10
            },
            
            "console": {
                "enabled": True,
                "log_level": "INFO",
                "format": "%(asctime)s - %(levelname)s - %(message)s"
            }
        },
        
        "monitoring": {
            "check_interval": 60,
            "retry_attempts": 3,
            "retry_delay": 5,
            "concurrent_checks": 10,
            "history_retention_days": 30,
            "metrics_enabled": True
        },
        
        "alerting": {
            "cooldown_period": 300,
            "escalation_enabled": True,
            "escalation_delay": 600,
            "auto_resolve": True,
            "severity_levels": ["INFO", "WARNING", "CRITICAL"]
        }
    }
    
    return config


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure and values."""
    
    try:
        # Check required sections
        required_sections = ["websites", "thresholds", "notifications", "monitoring"]
        for section in required_sections:
            if section not in config:
                print(f"ERROR: Missing required section: {section}")
                return False
        
        # Validate websites
        if not isinstance(config["websites"], list) or len(config["websites"]) == 0:
            print("ERROR: websites must be a non-empty list")
            return False
        
        for i, website in enumerate(config["websites"]):
            if not isinstance(website, dict):
                print(f"ERROR: Website {i} must be a dictionary")
                return False
            
            required_fields = ["name", "url"]
            for field in required_fields:
                if field not in website:
                    print(f"ERROR: Website {i} missing required field: {field}")
                    return False
        
        # Validate thresholds
        if "response_time" not in config["thresholds"]:
            print("ERROR: Missing response_time thresholds")
            return False
        
        rt_thresholds = config["thresholds"]["response_time"]
        if "warning" not in rt_thresholds or "critical" not in rt_thresholds:
            print("ERROR: Missing warning or critical response time thresholds")
            return False
        
        # Validate notification settings
        notifications = config["notifications"]
        if not isinstance(notifications, dict):
            print("ERROR: notifications must be a dictionary")
            return False
        
        print("Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Configuration validation failed: {str(e)}")
        return False


def save_json_config(config: Dict[str, Any], filename: str = "monitor_config.json") -> bool:
    """Save configuration as JSON file."""
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"JSON configuration saved to: {filename}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to save JSON config: {str(e)}")
        return False


def save_yaml_config(config: Dict[str, Any], filename: str = "monitor_config.yaml") -> bool:
    """Save configuration as YAML file."""
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2, sort_keys=False)
        print(f"YAML configuration saved to: {filename}")
        return True
        
    except ImportError:
        print("WARNING: PyYAML not available, skipping YAML export")
        print("Install with: pip install PyYAML")
        return False
        
    except Exception as e:
        print(f"ERROR: Failed to save YAML config: {str(e)}")
        return False


def print_config_summary(config: Dict[str, Any]) -> None:
    """Print a summary of the configuration."""
    
    try:
        print("\n" + "="*50)
        print("CONFIGURATION SUMMARY")
        print("="*50)
        
        print(f"Version: {config['metadata']['version']}")
        print(f"Created: {config['metadata']['created']}")
        
        print(f"\nWebsites to monitor: {len(config['websites'])}")
        for website in config['websites']:
            status = "ENABLED" if website.get('enabled', True) else "DISABLED"