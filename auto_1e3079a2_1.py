```python
"""
Website Monitoring Configuration Generator

This module creates a comprehensive configuration file for website monitoring systems.
It generates a JSON configuration that includes target URLs, monitoring thresholds
(response time limits, SSL certificate expiry warnings), and notification settings.

The configuration supports multiple websites with individual thresholds and can be
used by monitoring systems to track website health, performance, and SSL certificate
status.

Usage:
    python script.py

The script will create a 'monitoring_config.json' file with sample configurations
that can be customized for specific monitoring needs.
"""

import json
import os
from datetime import datetime, timedelta


def create_monitoring_config():
    """
    Creates a comprehensive monitoring configuration file in JSON format.
    
    Returns:
        dict: The configuration dictionary
    """
    
    # Sample configuration with multiple monitoring targets
    config = {
        "monitoring_settings": {
            "check_interval_minutes": 5,
            "retry_attempts": 3,
            "timeout_seconds": 30,
            "user_agent": "WebMonitor/1.0"
        },
        
        "targets": [
            {
                "name": "Primary Website",
                "url": "https://example.com",
                "enabled": True,
                "thresholds": {
                    "response_time_warning_ms": 2000,
                    "response_time_critical_ms": 5000,
                    "ssl_expiry_warning_days": 30,
                    "ssl_expiry_critical_days": 7
                },
                "expected_status_codes": [200, 301, 302],
                "check_ssl": True,
                "check_content": {
                    "enabled": True,
                    "contains": ["Welcome", "Home"],
                    "not_contains": ["Error", "404", "Internal Server Error"]
                }
            },
            {
                "name": "API Endpoint",
                "url": "https://api.example.com/health",
                "enabled": True,
                "thresholds": {
                    "response_time_warning_ms": 1000,
                    "response_time_critical_ms": 3000,
                    "ssl_expiry_warning_days": 14,
                    "ssl_expiry_critical_days": 3
                },
                "expected_status_codes": [200],
                "check_ssl": True,
                "check_content": {
                    "enabled": True,
                    "contains": ["status", "healthy"],
                    "not_contains": ["error", "failed"]
                },
                "headers": {
                    "Authorization": "Bearer YOUR_TOKEN_HERE",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "E-commerce Site",
                "url": "https://shop.example.com",
                "enabled": True,
                "thresholds": {
                    "response_time_warning_ms": 3000,
                    "response_time_critical_ms": 8000,
                    "ssl_expiry_warning_days": 45,
                    "ssl_expiry_critical_days": 10
                },
                "expected_status_codes": [200],
                "check_ssl": True,
                "check_content": {
                    "enabled": False
                }
            }
        ],
        
        "notifications": {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "from_address": "monitor@yourcompany.com",
                "to_addresses": [
                    "admin@yourcompany.com",
                    "devops@yourcompany.com"
                ],
                "subject_prefix": "[Website Monitor]"
            },
            
            "slack": {
                "enabled": False,
                "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                "channel": "#alerts",
                "username": "WebMonitor",
                "emoji": ":warning:"
            },
            
            "webhook": {
                "enabled": False,
                "url": "https://your-webhook-endpoint.com/alerts",
                "headers": {
                    "Authorization": "Bearer YOUR_WEBHOOK_TOKEN",
                    "Content-Type": "application/json"
                },
                "method": "POST"
            },
            
            "discord": {
                "enabled": False,
                "webhook_url": "https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK",
                "username": "Website Monitor",
                "avatar_url": "https://example.com/monitor-avatar.png"
            }
        },
        
        "logging": {
            "enabled": True,
            "level": "INFO",
            "file_path": "monitoring.log",
            "max_file_size_mb": 10,
            "backup_count": 5,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        
        "database": {
            "enabled": True,
            "type": "sqlite",
            "connection_string": "monitoring.db",
            "retention_days": 90
        },
        
        "dashboard": {
            "enabled": True,
            "host": "0.0.0.0",
            "port": 8080,
            "auth": {
                "enabled": False,
                "username": "admin",
                "password": "change_me"
            }
        },
        
        "advanced_settings": {
            "dns_check": {
                "enabled": True,
                "nameservers": ["8.8.8.8", "1.1.1.1"]
            },
            "port_check": {
                "enabled": False,
                "ports": [80, 443, 22]
            },
            "certificate_transparency": {
                "enabled": False,
                "check_ct_logs": True
            }
        }
    }
    
    return config


def validate_config(config):
    """
    Validates the monitoring configuration for required fields and logical consistency.
    
    Args:
        config (dict): The configuration dictionary to validate
        
    Returns:
        list: List of validation errors, empty if valid
    """
    errors = []
    
    try:
        # Check required top-level keys
        required_keys = ["monitoring_settings", "targets", "notifications"]
        for key in required_keys:
            if key not in config:
                errors.append(f"Missing required key: {key}")
        
        # Validate targets
        if "targets" in config:
            for i, target in enumerate(config["targets"]):
                if "url" not in target:
                    errors.append(f"Target {i}: Missing required 'url' field")
                if "name" not in target:
                    errors.append(f"Target {i}: Missing required 'name' field")
                
                # Validate thresholds
                if "thresholds" in target:
                    thresholds = target["thresholds"]
                    if "response_time_warning_ms" in thresholds and "response_time_critical_ms" in thresholds:
                        if thresholds["response_time_warning_ms"] >= thresholds["response_time_critical_ms"]:
                            errors.append(f"Target {i}: Warning threshold should be less than critical threshold")
        
        # Validate notification settings
        if "notifications" in config:
            notifications = config["notifications"]
            if "email" in notifications and notifications["email"].get("enabled", False):
                email_config = notifications["email"]
                required_email_keys = ["smtp_server", "username", "to_addresses"]
                for key in required_email_keys:
                    if key not in email_config:
                        errors.append(f"Email notifications enabled but missing: {key}")
    
    except Exception as e:
        errors.append(f"Configuration validation error: {str(e)}")
    
    return errors


def save_config_file(config, filename="monitoring_config.json"):
    """
    Saves the configuration to a JSON file with proper formatting.