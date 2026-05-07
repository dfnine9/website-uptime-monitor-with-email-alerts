```python
#!/usr/bin/env python3
"""
Website Monitoring Configuration Management System

This module provides a comprehensive configuration management system for website monitoring
that reads URLs, alert thresholds, and email settings from a YAML configuration file.
It validates URL formats, timeout values, and email configurations to ensure proper
monitoring setup.

Features:
- YAML-based configuration with validation
- URL format validation using urllib.parse
- Timeout and threshold validation
- Email settings validation
- Error handling for malformed configurations
- Self-contained with minimal dependencies

Usage:
    python script.py

The script expects a 'config.yaml' file in the same directory with the following structure:
    websites:
      - url: "https://example.com"
        name: "Example Site"
        timeout: 30
        alert_threshold: 5000
    email:
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "user@example.com"
      password: "password"
      from_email: "alerts@example.com"
      to_emails:
        - "admin@example.com"
    general:
      check_interval: 300
      retry_count: 3
"""

import yaml
import re
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional
import sys
import os


class ConfigurationError(Exception):
    """Custom exception for configuration validation errors."""
    pass


class WebsiteMonitorConfig:
    """Configuration manager for website monitoring system."""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to YAML configuration file
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load and validate configuration from YAML file.
        
        Returns:
            Dict containing validated configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"Configuration file '{self.config_file}' not found")
                
            with open(self.config_file, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
                
            if not self.config:
                raise ConfigurationError("Configuration file is empty or invalid YAML")
                
            self._validate_config()
            return self.config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        required_sections = ['websites', 'email', 'general']
        
        for section in required_sections:
            if section not in self.config:
                raise ConfigurationError(f"Missing required section: {section}")
        
        self._validate_websites()
        self._validate_email()
        self._validate_general()
    
    def _validate_websites(self) -> None:
        """Validate website configurations."""
        websites = self.config.get('websites', [])
        
        if not websites:
            raise ConfigurationError("No websites configured")
            
        if not isinstance(websites, list):
            raise ConfigurationError("'websites' must be a list")
        
        for i, website in enumerate(websites):
            if not isinstance(website, dict):
                raise ConfigurationError(f"Website {i} must be a dictionary")
                
            # Validate required fields
            required_fields = ['url', 'name']
            for field in required_fields:
                if field not in website:
                    raise ConfigurationError(f"Website {i} missing required field: {field}")
            
            # Validate URL format
            self._validate_url(website['url'], f"Website {i}")
            
            # Validate timeout (optional)
            if 'timeout' in website:
                self._validate_timeout(website['timeout'], f"Website {i}")
            else:
                website['timeout'] = 30  # Default timeout
            
            # Validate alert threshold (optional)
            if 'alert_threshold' in website:
                self._validate_threshold(website['alert_threshold'], f"Website {i}")
            else:
                website['alert_threshold'] = 5000  # Default 5 seconds
    
    def _validate_url(self, url: str, context: str) -> None:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            context: Context for error messages
        """
        if not isinstance(url, str) or not url.strip():
            raise ConfigurationError(f"{context}: URL cannot be empty")
            
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ConfigurationError(f"{context}: Invalid URL format - {url}")
                
            if parsed.scheme not in ['http', 'https']:
                raise ConfigurationError(f"{context}: URL must use http or https - {url}")
                
        except Exception as e:
            raise ConfigurationError(f"{context}: URL validation error - {e}")
    
    def _validate_timeout(self, timeout: Any, context: str) -> None:
        """
        Validate timeout value.
        
        Args:
            timeout: Timeout value to validate
            context: Context for error messages
        """
        if not isinstance(timeout, (int, float)):
            raise ConfigurationError(f"{context}: Timeout must be a number")
            
        if timeout <= 0:
            raise ConfigurationError(f"{context}: Timeout must be positive")
            
        if timeout > 300:  # 5 minutes max
            raise ConfigurationError(f"{context}: Timeout too large (max 300 seconds)")
    
    def _validate_threshold(self, threshold: Any, context: str) -> None:
        """
        Validate alert threshold value.
        
        Args:
            threshold: Threshold value to validate (in milliseconds)
            context: Context for error messages
        """
        if not isinstance(threshold, (int, float)):
            raise ConfigurationError(f"{context}: Alert threshold must be a number")
            
        if threshold <= 0:
            raise ConfigurationError(f"{context}: Alert threshold must be positive")
            
        if threshold > 60000:  # 60 seconds max
            raise ConfigurationError(f"{context}: Alert threshold too large (max 60000ms)")
    
    def _validate_email(self) -> None:
        """Validate email configuration."""
        email_config = self.config.get('email', {})
        
        required_fields = ['smtp_server', 'smtp_port', 'username', 'from_email', 'to_emails']
        for field in required_fields:
            if field not in email_config:
                raise ConfigurationError(f"Email config missing required field: {field}")
        
        # Validate SMTP port
        smtp_port = email_config['smtp_port']
        if not isinstance(smtp_port, int) or smtp_port <= 0 or smtp_port > 65535:
            raise ConfigurationError("SMTP port must be a valid port number (1-65535)")
        
        # Validate email addresses
        self._validate_email_address(email_config['from_email'], "from_email")
        self._validate_email_address(email_config['username'], "username")
        
        # Validate to_emails list
        to_emails = email_config['to_emails']
        if not isinstance(to_emails, list) or not to_emails:
            raise ConfigurationError("to_emails must be a non-empty list")
            
        for i, email in enumerate(to_emails):
            self._validate_email_address(email, f"to_emails[{i}]")
    
    def _validate_email_address(self, email: str, field_name: str) -> None:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            field_name: Field name for error messages
        """