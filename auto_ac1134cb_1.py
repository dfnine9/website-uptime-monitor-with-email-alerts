```python
"""
Configuration Management System for URL Monitoring

This module provides a comprehensive URL monitoring system with configuration management.
It reads monitoring targets from URLs.txt, loads settings from config.json, and monitors
URLs with configurable intervals, timeouts, and retry attempts. Includes email alerting
and robust error handling for network failures and invalid URLs.

Features:
- Configurable monitoring intervals and timeouts
- Retry logic with exponential backoff
- Email alerts for failures
- Comprehensive error handling
- Self-contained with minimal dependencies

Usage:
    python script.py
"""

import json
import time
import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
import httpx


class ConfigManager:
    """Manages configuration settings and URL targets."""
    
    def __init__(self, config_path: str = "config.json", urls_path: str = "URLs.txt"):
        self.config_path = Path(config_path)
        self.urls_path = Path(urls_path)
        self.config = self._load_config()
        self.urls = self._load_urls()
        self._setup_logging()
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file with defaults."""
        default_config = {
            "check_interval": 300,  # 5 minutes
            "timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 5,
            "email_alerts": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": []
            },
            "log_level": "INFO"
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict) and isinstance(config[key], dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in config[key]:
                                config[key][sub_key] = sub_value
                return config
            else:
                print(f"Config file {self.config_path} not found. Creating with defaults...")
                self._save_config(default_config)
                return default_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}. Using defaults.")
            return default_config
    
    def _save_config(self, config: Dict) -> None:
        """Save configuration to JSON file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def _load_urls(self) -> List[str]:
        """Load URLs from text file."""
        try:
            if self.urls_path.exists():
                with open(self.urls_path, 'r') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                return [url for url in urls if self._is_valid_url(url)]
            else:
                print(f"URLs file {self.urls_path} not found. Creating with example URLs...")
                example_urls = [
                    "https://www.google.com",
                    "https://www.github.com",
                    "https://httpbin.org/status/200"
                ]
                self._save_urls(example_urls)
                return example_urls
        except IOError as e:
            print(f"Error loading URLs: {e}")
            return []
    
    def _save_urls(self, urls: List[str]) -> None:
        """Save URLs to text file."""
        try:
            with open(self.urls_path, 'w') as f:
                f.write("# URL Monitoring Targets\n")
                f.write("# One URL per line, lines starting with # are ignored\n\n")
                for url in urls:
                    f.write(f"{url}\n")
        except IOError as e:
            print(f"Error saving URLs: {e}")
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            print(f"Invalid URL format: {url}")
            return False
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('url_monitor.log')
            ]
        )


class URLMonitor:
    """Monitors URLs with retry logic and alerting."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager.config
        self.urls = config_manager.urls
        self.logger = logging.getLogger(__name__)
        self.failed_urls = set()
    
    def check_url(self, url: str) -> Dict:
        """Check a single URL with retry logic."""
        for attempt in range(1, self.config['retry_attempts'] + 1):
            try:
                with httpx.Client(timeout=self.config['timeout']) as client:
                    response = client.get(url)
                    
                result = {
                    'url': url,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'success': 200 <= response.status_code < 400,
                    'error': None,
                    'attempt': attempt
                }
                
                if result['success']:
                    if url in self.failed_urls:
                        self.failed_urls.remove(url)
                        self.logger.info(f"URL recovered: {url}")
                    return result
                else:
                    result['error'] = f"HTTP {response.status_code}"
                    
            except httpx.TimeoutException:
                result = {
                    'url': url,
                    'status_code': None,
                    'response_time': None,
                    'success': False,
                    'error': f"Timeout after {self.config['timeout']}s",
                    'attempt': attempt
                }
            except httpx.ConnectError:
                result = {
                    'url': url,
                    'status_code': None,
                    'response_time': None,
                    'success': False,
                    'error': "Connection failed",
                    'attempt': attempt
                }
            except Exception as e:
                result = {
                    'url': url,
                    'status_code': None,
                    'response_time': None,
                    'success': False,
                    'error': f"Unexpected error: {str(e)}",
                    'attempt': attempt
                }
            
            if attempt < self.config['retry_attempts']:
                delay = self.config['retry_delay'] * (2 ** (attempt - 1))  # Exponential backoff
                self.logger.warning(f"Attempt {attempt} failed for {url}: {result['error']}. Retrying in {delay}s...")
                time.sleep(delay)
        
        # All attempts failed
        if url not in self.failed_urls:
            self.failed_urls.add(url)
            self._send_alert(url, result['error'])
        
        return result
    
    def monitor_urls(self) -> None: