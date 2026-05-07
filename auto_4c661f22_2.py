```python
#!/usr/bin/env python3
"""
URL Monitoring Configuration System

A self-contained Python script that creates and manages configuration for URL monitoring
with email notifications. Supports both JSON and YAML configuration formats.

Features:
- URL list management with customizable check intervals
- Email SMTP configuration for notifications
- Global and per-URL monitoring intervals
- Configuration validation and error handling
- Support for both JSON and YAML formats

Usage:
    python script.py

Requirements:
    - Python 3.6+
    - httpx (pip install httpx)
    - anthropic (pip install anthropic)
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available, using JSON format only")


@dataclass
class EmailConfig:
    """Email configuration for notifications"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_address: str = ""
    to_addresses: List[str] = None
    use_tls: bool = True
    
    def __post_init__(self):
        if self.to_addresses is None:
            self.to_addresses = []


@dataclass
class URLConfig:
    """Individual URL monitoring configuration"""
    url: str
    name: str = ""
    method: str = "GET"
    expected_status: int = 200
    timeout: int = 30
    interval: int = 300  # seconds
    headers: Dict[str, str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if not self.name:
            self.name = self.url


@dataclass
class MonitoringConfig:
    """Main monitoring configuration"""
    urls: List[URLConfig] = None
    email: EmailConfig = None
    global_interval: int = 300  # seconds
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    log_level: str = "INFO"
    config_version: str = "1.0"
    
    def __post_init__(self):
        if self.urls is None:
            self.urls = []
        if self.email is None:
            self.email = EmailConfig()


class ConfigurationManager:
    """Manages configuration loading, saving, and validation"""
    
    def __init__(self, config_path: str = "monitoring_config"):
        self.config_path = Path(config_path)
        self.json_path = self.config_path.with_suffix('.json')
        self.yaml_path = self.config_path.with_suffix('.yaml')
    
    def create_default_config(self) -> MonitoringConfig:
        """Create a default configuration with sample data"""
        try:
            sample_urls = [
                URLConfig(
                    url="https://httpbin.org/status/200",
                    name="HTTPBin Status Check",
                    interval=60
                ),
                URLConfig(
                    url="https://jsonplaceholder.typicode.com/posts/1",
                    name="JSONPlaceholder API",
                    method="GET",
                    interval=120
                ),
                URLConfig(
                    url="https://httpstat.us/503",
                    name="HTTP Status Test (503)",
                    expected_status=503,
                    interval=300,
                    enabled=False
                )
            ]
            
            email_config = EmailConfig(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                username="your-email@gmail.com",
                password="your-app-password",
                from_address="your-email@gmail.com",
                to_addresses=["admin@example.com", "alerts@example.com"],
                use_tls=True
            )
            
            config = MonitoringConfig(
                urls=sample_urls,
                email=email_config,
                global_interval=300,
                max_retries=3,
                retry_delay=60,
                log_level="INFO"
            )
            
            return config
            
        except Exception as e:
            print(f"Error creating default configuration: {e}")
            raise
    
    def save_config(self, config: MonitoringConfig, format_type: str = "json") -> bool:
        """Save configuration to file"""
        try:
            config_dict = self._config_to_dict(config)
            
            if format_type.lower() == "yaml" and YAML_AVAILABLE:
                with open(self.yaml_path, 'w') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                print(f"Configuration saved to: {self.yaml_path}")
                return True
            else:
                with open(self.json_path, 'w') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                print(f"Configuration saved to: {self.json_path}")
                return True
                
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def load_config(self) -> Optional[MonitoringConfig]:
        """Load configuration from file (YAML preferred, JSON fallback)"""
        try:
            # Try YAML first if available
            if YAML_AVAILABLE and self.yaml_path.exists():
                return self._load_yaml_config()
            
            # Fallback to JSON
            if self.json_path.exists():
                return self._load_json_config()
            
            print("No configuration file found, creating default...")
            return None
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return None
    
    def _load_yaml_config(self) -> MonitoringConfig:
        """Load YAML configuration"""
        try:
            with open(self.yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            return self._dict_to_config(data)
        except Exception as e:
            print(f"Error loading YAML config: {e}")
            raise
    
    def _load_json_config(self) -> MonitoringConfig:
        """Load JSON configuration"""
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
            return self._dict_to_config(data)
        except Exception as e:
            print(f"Error loading JSON config: {e}")
            raise
    
    def _config_to_dict(self, config: MonitoringConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary"""
        try:
            config_dict = asdict(config)
            return config_dict
        except Exception as e:
            print(f"Error converting config to dict: {e}")
            raise
    
    def _dict_to_config(self, data: Dict[str, Any]) -> MonitoringConfig:
        """Convert dictionary to configuration object"""
        try:
            # Convert email config
            email_data = data.get('email', {})
            email_config = EmailConfig(**email_data)
            
            # Convert URL configs
            urls_data = data.get('urls', [])
            url_configs = [URLConfig(**url_data) for url_data in urls_data]
            
            # Create main config
            config_data = data.copy()
            config_data['email'] = email_config
            config_data['urls'] = url_configs
            
            return MonitoringConfig(**config_data)
            
        except Exception as e:
            print(f"Error converting dict to config: {e}")
            raise
    
    def validate_config(self, config: MonitoringConfig) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        try:
            # Validate global settings
            if config.global_interval <= 0:
                errors.append("global_interval must be positive")