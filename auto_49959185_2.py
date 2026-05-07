```python
#!/usr/bin/env python3
"""
Health Monitoring Alerting System

This module provides a comprehensive alerting system for JSON health data monitoring.
It analyzes health metrics against configurable thresholds, generates immediate email 
alerts for critical issues, and maintains persistent alert state to prevent notification spam.

Features:
- Configurable health thresholds for various metrics
- Email alerting via SMTP with HTML formatting
- Alert state persistence to prevent duplicate notifications
- Exponential backoff for repeated alerts
- JSON-based configuration and state management
- Comprehensive error handling and logging

Usage:
    python script.py

The script will:
1. Load configuration and previous alert state
2. Fetch current health data (simulated or from API)
3. Evaluate metrics against thresholds
4. Send alerts for new critical issues
5. Update alert state with backoff logic
"""

import json
import smtplib
import time
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
import hashlib

class HealthAlerter:
    """Health monitoring and alerting system"""
    
    def __init__(self, config_file: str = "health_config.json", state_file: str = "alert_state.json"):
        self.config_file = config_file
        self.state_file = state_file
        self.config = self.load_config()
        self.alert_state = self.load_alert_state()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with defaults"""
        default_config = {
            "thresholds": {
                "cpu_usage": {"critical": 90, "warning": 75},
                "memory_usage": {"critical": 95, "warning": 80},
                "disk_usage": {"critical": 90, "warning": 80},
                "response_time": {"critical": 5000, "warning": 2000},
                "error_rate": {"critical": 5, "warning": 2},
                "uptime": {"critical": 95, "warning": 98}
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender": "alerts@company.com",
                "password": "app_password",
                "recipients": ["admin@company.com", "devops@company.com"]
            },
            "alert_settings": {
                "min_interval_minutes": 15,
                "max_backoff_hours": 24,
                "backoff_multiplier": 2
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in loaded_config:
                        loaded_config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in loaded_config[key]:
                                loaded_config[key][subkey] = subvalue
                return loaded_config
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default configuration file: {self.config_file}")
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def load_alert_state(self) -> Dict[str, Any]:
        """Load persistent alert state"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading alert state: {e}")
            return {}
    
    def save_alert_state(self):
        """Save alert state to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.alert_state, f, indent=2)
        except Exception as e:
            print(f"Error saving alert state: {e}")
    
    def get_sample_health_data(self) -> Dict[str, Any]:
        """Generate sample health data for testing"""
        import random
        
        # Simulate various health scenarios
        scenarios = [
            # Normal operation
            {
                "timestamp": datetime.now().isoformat(),
                "service": "web-api",
                "metrics": {
                    "cpu_usage": random.uniform(20, 60),
                    "memory_usage": random.uniform(30, 70),
                    "disk_usage": random.uniform(40, 75),
                    "response_time": random.uniform(100, 800),
                    "error_rate": random.uniform(0, 1),
                    "uptime": random.uniform(99, 100)
                }
            },
            # High load scenario
            {
                "timestamp": datetime.now().isoformat(),
                "service": "database",
                "metrics": {
                    "cpu_usage": random.uniform(85, 95),
                    "memory_usage": random.uniform(90, 98),
                    "disk_usage": random.uniform(70, 85),
                    "response_time": random.uniform(2000, 6000),
                    "error_rate": random.uniform(3, 8),
                    "uptime": random.uniform(92, 97)
                }
            }
        ]
        
        return random.choice(scenarios)
    
    def evaluate_metric(self, metric_name: str, value: float) -> Optional[str]:
        """Evaluate a metric against thresholds"""
        try:
            thresholds = self.config["thresholds"].get(metric_name, {})
            
            if "critical" in thresholds:
                # For uptime, lower is worse
                if metric_name == "uptime":
                    if value < thresholds["critical"]:
                        return "critical"
                    elif value < thresholds.get("warning", 100):
                        return "warning"
                else:
                    # For other metrics, higher is worse
                    if value > thresholds["critical"]:
                        return "critical"
                    elif value > thresholds.get("warning", float('inf')):
                        return "warning"
            
            return None
        except Exception as e:
            print(f"Error evaluating metric {metric_name}: {e}")
            return None
    
    def generate_alert_id(self, service: str, metric: str, severity: str) -> str:
        """Generate unique alert ID"""
        alert_string = f"{service}:{metric}:{severity}"
        return hashlib.md5(alert_string.encode()).hexdigest()[:8]
    
    def should_send_alert(self, alert_id: str) -> bool:
        """Determine if alert should be sent based on state and backoff"""
        try:
            now = datetime.now()
            
            if alert_id not in self.alert_state:
                return True
            
            alert_info = self.alert_state[alert_id]
            last_sent = datetime.fromisoformat(alert_info["last_sent"])
            send_count = alert_info.get("send_count", 0)
            
            # Calculate backoff interval
            min_interval = self.config["alert_settings"]["min_interval_minutes"]
            backoff_multiplier = self.config["alert_settings"]["backoff_multiplier"]
            max_backoff_hours = self.config["alert_settings"]["max_backoff_hours"]
            
            backoff_minutes = min(
                min_interval * (backoff_multiplier ** send_count),
                max_backoff_hours * 60
            )
            
            next_send_time = last_sent + timedelta(minutes=backoff_minutes)
            
            return now >= next_send_time
        except Exception as e:
            print(