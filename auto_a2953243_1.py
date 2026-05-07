```python
#!/usr/bin/env python3
"""
URL Monitoring Configuration Generator

This module creates a comprehensive configuration file for URL monitoring systems.
It generates JSON configuration with URL targets, response time thresholds, and alert settings.
The configuration supports multiple monitoring scenarios including web services, APIs, and health checks.

Dependencies: json (standard library), pathlib (standard library)
Usage: python script.py
Output: Creates 'url_monitoring_config.json' with sample monitoring configuration
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def create_monitoring_config() -> Dict[str, Any]:
    """
    Create a comprehensive URL monitoring configuration.
    
    Returns:
        Dict containing complete monitoring configuration
    """
    config = {
        "monitoring_settings": {
            "check_interval_seconds": 300,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "retry_delay_seconds": 5,
            "concurrent_checks": 10
        },
        "alert_settings": {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.company.com",
                "smtp_port": 587,
                "sender": "monitoring@company.com",
                "recipients": [
                    "devops@company.com",
                    "alerts@company.com"
                ],
                "escalation_recipients": [
                    "manager@company.com"
                ]
            },
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                "channel": "#alerts",
                "escalation_channel": "#critical"
            },
            "sms": {
                "enabled": False,
                "provider": "twilio",
                "numbers": ["+1234567890"]
            }
        },
        "thresholds": {
            "response_time_warning_ms": 1000,
            "response_time_critical_ms": 5000,
            "availability_warning_percent": 95.0,
            "availability_critical_percent": 90.0,
            "consecutive_failures_warning": 3,
            "consecutive_failures_critical": 5
        },
        "url_targets": [
            {
                "name": "Main Website",
                "url": "https://example.com",
                "method": "GET",
                "expected_status_codes": [200],
                "expected_content": "Welcome",
                "headers": {
                    "User-Agent": "URLMonitor/1.0"
                },
                "custom_thresholds": {
                    "response_time_warning_ms": 800,
                    "response_time_critical_ms": 3000
                },
                "tags": ["production", "frontend", "critical"],
                "priority": "critical"
            },
            {
                "name": "API Health Check",
                "url": "https://api.example.com/health",
                "method": "GET",
                "expected_status_codes": [200],
                "expected_content": "\"status\":\"healthy\"",
                "headers": {
                    "Accept": "application/json",
                    "User-Agent": "URLMonitor/1.0"
                },
                "custom_thresholds": {
                    "response_time_warning_ms": 500,
                    "response_time_critical_ms": 2000
                },
                "tags": ["production", "api", "critical"],
                "priority": "critical"
            },
            {
                "name": "User Authentication API",
                "url": "https://auth.example.com/api/v1/status",
                "method": "POST",
                "expected_status_codes": [200, 201],
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer monitoring_token"
                },
                "body": {
                    "action": "health_check"
                },
                "custom_thresholds": {
                    "response_time_warning_ms": 1500,
                    "response_time_critical_ms": 4000
                },
                "tags": ["production", "auth", "critical"],
                "priority": "critical"
            },
            {
                "name": "Documentation Site",
                "url": "https://docs.example.com",
                "method": "GET",
                "expected_status_codes": [200],
                "expected_content": "<title>Documentation</title>",
                "custom_thresholds": {
                    "response_time_warning_ms": 2000,
                    "response_time_critical_ms": 6000
                },
                "tags": ["documentation", "low-priority"],
                "priority": "low"
            },
            {
                "name": "Database API",
                "url": "https://db-api.example.com/ping",
                "method": "GET",
                "expected_status_codes": [200],
                "expected_content": "pong",
                "headers": {
                    "X-API-Key": "monitoring_api_key"
                },
                "custom_thresholds": {
                    "response_time_warning_ms": 300,
                    "response_time_critical_ms": 1000
                },
                "tags": ["production", "database", "critical"],
                "priority": "critical"
            },
            {
                "name": "CDN Endpoint",
                "url": "https://cdn.example.com/assets/health.txt",
                "method": "GET",
                "expected_status_codes": [200],
                "expected_content": "healthy",
                "custom_thresholds": {
                    "response_time_warning_ms": 200,
                    "response_time_critical_ms": 800
                },
                "tags": ["cdn", "assets", "medium"],
                "priority": "medium"
            }
        ],
        "notification_rules": {
            "critical_priority": {
                "immediate_channels": ["email", "slack", "sms"],
                "escalation_delay_minutes": 15,
                "escalation_channels": ["email", "slack"]
            },
            "medium_priority": {
                "immediate_channels": ["slack"],
                "escalation_delay_minutes": 30,
                "escalation_channels": ["email"]
            },
            "low_priority": {
                "immediate_channels": ["slack"],
                "escalation_delay_minutes": 60,
                "escalation_channels": []
            }
        },
        "maintenance_windows": [
            {
                "name": "Weekly Maintenance",
                "description": "Regular weekly maintenance window",
                "start_time": "02:00",
                "end_time": "04:00",
                "days": ["sunday"],
                "timezone": "UTC",
                "suppress_alerts": True
            }
        ],
        "reporting": {
            "daily_summary": {
                "enabled": True,
                "recipients": ["reports@company.com"],
                "send_time": "09:00"
            },
            "weekly_report": {
                "enabled": True,
                "recipients": ["management@company.com"],
                "send_day": "monday",
                "send_time": "08:00"
            }
        }
    }
    
    return config


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate the monitoring configuration for common issues.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    try:
        # Check required sections
        required_sections = ["monitoring_settings", "alert_settings", "thresholds", "url_targets"]
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate URL targets
        if "url_targets" in config:
            for idx, target in enumerate(config["url_targets"]):
                if "url" not in target:
                    errors.append(f"URL target {idx} missing 'url' field")
                if "name" not in target:
                    errors.append(f"URL target {idx