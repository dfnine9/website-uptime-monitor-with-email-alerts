```python
#!/usr/bin/env python3
"""
Monitoring Configuration Generator

This module creates a comprehensive monitoring configuration file that defines:
- Alert thresholds for various system metrics (response time, uptime, SSL expiration)
- Email notification settings with different severity levels
- Configurable parameters for monitoring systems

The configuration is output as both JSON and YAML formats for compatibility
with different monitoring tools like Prometheus, Nagios, or custom solutions.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any


def create_monitoring_config() -> Dict[str, Any]:
    """
    Create a comprehensive monitoring configuration dictionary.
    
    Returns:
        Dict containing all monitoring configuration parameters
    """
    config = {
        "metadata": {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "description": "System monitoring configuration with alerting thresholds"
        },
        
        "alert_thresholds": {
            "response_time": {
                "warning_ms": 2000,
                "critical_ms": 5000,
                "timeout_ms": 10000,
                "check_interval_seconds": 60
            },
            "uptime": {
                "warning_percentage": 99.5,
                "critical_percentage": 99.0,
                "severe_percentage": 95.0,
                "measurement_window_hours": 24
            },
            "ssl_certificate": {
                "warning_days_before_expiry": 30,
                "critical_days_before_expiry": 7,
                "severe_days_before_expiry": 1,
                "check_interval_hours": 6
            },
            "disk_usage": {
                "warning_percentage": 80,
                "critical_percentage": 90,
                "severe_percentage": 95
            },
            "memory_usage": {
                "warning_percentage": 75,
                "critical_percentage": 85,
                "severe_percentage": 95
            },
            "cpu_usage": {
                "warning_percentage": 70,
                "critical_percentage": 85,
                "severe_percentage": 95,
                "measurement_window_minutes": 5
            }
        },
        
        "notification_settings": {
            "email": {
                "smtp_server": "smtp.company.com",
                "smtp_port": 587,
                "use_tls": True,
                "sender_email": "monitoring@company.com",
                "sender_name": "System Monitor"
            },
            
            "severity_levels": {
                "info": {
                    "color": "#0066CC",
                    "priority": 1,
                    "recipients": [
                        "devops@company.com"
                    ],
                    "throttle_minutes": 60
                },
                "warning": {
                    "color": "#FF9900",
                    "priority": 2,
                    "recipients": [
                        "devops@company.com",
                        "sre-team@company.com"
                    ],
                    "throttle_minutes": 30
                },
                "critical": {
                    "color": "#FF3300",
                    "priority": 3,
                    "recipients": [
                        "devops@company.com",
                        "sre-team@company.com",
                        "on-call@company.com"
                    ],
                    "throttle_minutes": 15,
                    "escalation_minutes": 30
                },
                "severe": {
                    "color": "#CC0000",
                    "priority": 4,
                    "recipients": [
                        "devops@company.com",
                        "sre-team@company.com",
                        "on-call@company.com",
                        "management@company.com"
                    ],
                    "throttle_minutes": 5,
                    "escalation_minutes": 15,
                    "sms_enabled": True
                }
            }
        },
        
        "monitoring_targets": {
            "web_services": [
                {
                    "name": "Main Website",
                    "url": "https://www.company.com",
                    "method": "GET",
                    "expected_status": 200,
                    "check_ssl": True,
                    "follow_redirects": True
                },
                {
                    "name": "API Endpoint",
                    "url": "https://api.company.com/health",
                    "method": "GET",
                    "expected_status": 200,
                    "headers": {
                        "User-Agent": "MonitoringBot/1.0"
                    }
                },
                {
                    "name": "Admin Dashboard",
                    "url": "https://admin.company.com/login",
                    "method": "GET",
                    "expected_status": 200,
                    "auth_required": True
                }
            ],
            
            "servers": [
                {
                    "name": "Production Web Server 1",
                    "hostname": "web01.company.com",
                    "ip": "10.0.1.10",
                    "services": ["nginx", "php-fpm"],
                    "critical": True
                },
                {
                    "name": "Database Server",
                    "hostname": "db01.company.com", 
                    "ip": "10.0.1.20",
                    "services": ["mysql", "redis"],
                    "critical": True
                }
            ]
        },
        
        "alert_rules": [
            {
                "name": "High Response Time",
                "condition": "response_time > alert_thresholds.response_time.critical_ms",
                "severity": "critical",
                "message": "Service response time exceeds {threshold}ms",
                "runbook": "https://wiki.company.com/runbooks/high-response-time"
            },
            {
                "name": "Low Uptime",
                "condition": "uptime_percentage < alert_thresholds.uptime.warning_percentage",
                "severity": "warning",
                "message": "Service uptime below {threshold}%",
                "runbook": "https://wiki.company.com/runbooks/low-uptime"
            },
            {
                "name": "SSL Certificate Expiring",
                "condition": "ssl_days_remaining < alert_thresholds.ssl_certificate.warning_days_before_expiry",
                "severity": "warning", 
                "message": "SSL certificate expires in {days} days",
                "runbook": "https://wiki.company.com/runbooks/ssl-renewal"
            },
            {
                "name": "Disk Space Critical",
                "condition": "disk_usage_percentage > alert_thresholds.disk_usage.critical_percentage",
                "severity": "critical",
                "message": "Disk usage at {usage}% on {server}",
                "runbook": "https://wiki.company.com/runbooks/disk-cleanup"
            }
        ]
    }
    
    return config


def generate_yaml_config(config: Dict[str, Any]) -> str:
    """
    Convert configuration dictionary to YAML format string.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        YAML formatted string
    """
    def dict_to_yaml(data: Any, indent: int = 0) -> str:
        yaml_lines = []
        spaces = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    yaml_lines.append(f"{spaces}{key}:")
                    yaml_lines.append(dict_to_yaml(value, indent + 1))
                else:
                    yaml_lines.append(f"{spaces}{key}: {json.dumps(value) if isinstance(value, str) else value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    yaml_lines.append(f"{spaces}- ")
                    item_yaml = dict_to_yaml(item, indent + 1)
                    yaml_lines.append(