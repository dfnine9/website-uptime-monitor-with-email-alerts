```python
#!/usr/bin/env python3
"""
Configuration Management System

This module provides a comprehensive configuration management system for monitoring applications.
It handles SMTP email settings, alert thresholds, monitoring intervals, and website lists
with built-in validation and robust error handling.

Features:
- SMTP configuration with authentication
- Alert threshold management with numeric validation
- Monitoring interval configuration with time unit support
- Website list management with URL validation
- JSON-based persistence with atomic writes
- Comprehensive error handling and logging
- Configuration validation and sanitization

Usage:
    python script.py

The script demonstrates all configuration management features including:
- Loading/saving configurations
- Adding and validating websites
- Setting alert thresholds
- Configuring monitoring intervals
- SMTP settings management
"""

import json
import os
import re
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse
import smtplib
from email.mime.text import MIMEText


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigurationManager:
    """
    Manages application configuration including SMTP settings, alert thresholds,
    monitoring intervals, and website lists with validation and persistence.
    """
    
    def __init__(self, config_file: str = "monitoring_config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = {
            "smtp": {
                "server": "",
                "port": 587,
                "username": "",
                "password": "",
                "use_tls": True,
                "timeout": 30
            },
            "alerts": {
                "response_time_threshold": 5.0,
                "error_rate_threshold": 0.05,
                "consecutive_failures": 3,
                "alert_cooldown": 300
            },
            "monitoring": {
                "check_interval": 60,
                "timeout": 30,
                "retry_count": 3,
                "concurrent_checks": 10
            },
            "websites": []
        }
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file with error handling."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    self._merge_config(loaded_config)
                    print(f"Configuration loaded from {self.config_file}")
            else:
                print(f"Configuration file {self.config_file} not found, using defaults")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except IOError as e:
            raise ConfigurationError(f"Error reading configuration file: {e}")
    
    def _merge_config(self, loaded_config: Dict[str, Any]) -> None:
        """Merge loaded configuration with defaults."""
        try:
            for section, values in loaded_config.items():
                if section in self.config:
                    if isinstance(values, dict):
                        self.config[section].update(values)
                    else:
                        self.config[section] = values
                else:
                    self.config[section] = values
        except Exception as e:
            raise ConfigurationError(f"Error merging configuration: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file atomically."""
        try:
            # Write to temporary file first for atomic operation
            temp_file = None
            with tempfile.NamedTemporaryFile(
                mode='w', 
                dir=os.path.dirname(self.config_file) or '.',
                delete=False,
                encoding='utf-8'
            ) as f:
                temp_file = f.name
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Atomic move
            shutil.move(temp_file, self.config_file)
            print(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
            raise ConfigurationError(f"Error saving configuration: {e}")
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
    
    def set_smtp_config(self, server: str, port: int, username: str, 
                       password: str, use_tls: bool = True, timeout: int = 30) -> None:
        """
        Configure SMTP settings with validation.
        
        Args:
            server: SMTP server hostname
            port: SMTP server port
            username: Username for authentication
            password: Password for authentication
            use_tls: Whether to use TLS encryption
            timeout: Connection timeout in seconds
        """
        try:
            # Validate inputs
            if not server or not isinstance(server, str):
                raise ConfigurationError("SMTP server must be a non-empty string")
            
            if not isinstance(port, int) or not (1 <= port <= 65535):
                raise ConfigurationError("SMTP port must be an integer between 1 and 65535")
            
            if username and not self.validate_email(username):
                print(f"Warning: Username '{username}' doesn't appear to be a valid email")
            
            if not password:
                raise ConfigurationError("Password cannot be empty")
            
            if not isinstance(timeout, int) or timeout <= 0:
                raise ConfigurationError("Timeout must be a positive integer")
            
            self.config["smtp"].update({
                "server": server,
                "port": port,
                "username": username,
                "password": password,
                "use_tls": use_tls,
                "timeout": timeout
            })
            
            print(f"SMTP configuration updated: {server}:{port}")
            
        except Exception as e:
            raise ConfigurationError(f"Error setting SMTP configuration: {e}")
    
    def test_smtp_connection(self) -> bool:
        """Test SMTP connection with current settings."""
        try:
            smtp_config = self.config["smtp"]
            
            if not all([smtp_config["server"], smtp_config["username"], smtp_config["password"]]):
                raise ConfigurationError("SMTP configuration incomplete")
            
            server = smtplib.SMTP(smtp_config["server"], smtp_config["port"], 
                                 timeout=smtp_config["timeout"])
            
            if smtp_config["use_tls"]:
                server.starttls()
            
            server.login(smtp_config["username"], smtp_config["password"])
            server.quit()
            
            print("SMTP connection test successful")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("SMTP authentication failed - check username/password")
            return False
        except smtplib.SMTPConnectError:
            print("SMTP connection failed - check server/port")
            return False
        except Exception as e:
            print(f"SMTP test failed: {e}")
            return False
    
    def set_alert_threshold(self, threshold_name: str, value: Union[float, int]) -> None:
        """
        Set alert threshold with validation.
        
        Args:
            threshold_name: Name of the threshold
            value: Threshold value