```python
#!/usr/bin/env python3
"""
Website Monitoring Configuration Management System

This module provides a comprehensive configuration management system for monitoring websites.
It tracks response times, SSL certificate expiration dates, and provides configurable alerting
thresholds. The system allows dynamic addition/removal of monitored websites and maintains
persistent configuration storage.

Features:
- Add/remove websites from monitoring list
- Configure response time alert thresholds
- Set certificate expiration warning periods
- Real-time website health checking
- Persistent JSON-based configuration storage
- Interactive command-line interface

Dependencies: httpx (for HTTP requests), anthropic (specified in requirements)
Standard library modules: json, ssl, socket, datetime, time, urllib.parse
"""

import json
import ssl
import socket
import datetime
import time
import urllib.parse
import os
from typing import Dict, List, Optional, Tuple

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    exit(1)

try:
    import anthropic
except ImportError:
    print("Warning: anthropic not available but listed in requirements")

class WebsiteMonitor:
    def __init__(self, config_file: str = "monitor_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file or create default config."""
        default_config = {
            "websites": {},
            "global_settings": {
                "response_time_threshold_ms": 5000,
                "cert_expiry_warning_days": 30,
                "timeout_seconds": 10
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                return default_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            return default_config
    
    def save_config(self) -> bool:
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def add_website(self, url: str, custom_threshold_ms: Optional[int] = None, 
                   custom_cert_warning_days: Optional[int] = None) -> bool:
        """Add a website to monitoring configuration."""
        try:
            # Validate URL format
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                print(f"Error: Invalid URL format: {url}")
                return False
            
            # Ensure URL has scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            website_config = {
                "url": url,
                "added_date": datetime.datetime.now().isoformat(),
                "active": True
            }
            
            if custom_threshold_ms is not None:
                website_config["response_time_threshold_ms"] = custom_threshold_ms
            
            if custom_cert_warning_days is not None:
                website_config["cert_expiry_warning_days"] = custom_cert_warning_days
            
            self.config["websites"][url] = website_config
            
            if self.save_config():
                print(f"Successfully added website: {url}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error adding website {url}: {e}")
            return False
    
    def remove_website(self, url: str) -> bool:
        """Remove a website from monitoring configuration."""
        try:
            if url in self.config["websites"]:
                del self.config["websites"][url]
                if self.save_config():
                    print(f"Successfully removed website: {url}")
                    return True
                else:
                    return False
            else:
                print(f"Website not found in configuration: {url}")
                return False
        except Exception as e:
            print(f"Error removing website {url}: {e}")
            return False
    
    def update_global_thresholds(self, response_time_ms: Optional[int] = None,
                               cert_warning_days: Optional[int] = None,
                               timeout_seconds: Optional[int] = None) -> bool:
        """Update global alert thresholds."""
        try:
            if response_time_ms is not None:
                self.config["global_settings"]["response_time_threshold_ms"] = response_time_ms
            
            if cert_warning_days is not None:
                self.config["global_settings"]["cert_expiry_warning_days"] = cert_warning_days
            
            if timeout_seconds is not None:
                self.config["global_settings"]["timeout_seconds"] = timeout_seconds
            
            if self.save_config():
                print("Successfully updated global thresholds")
                return True
            else:
                return False
        except Exception as e:
            print(f"Error updating global thresholds: {e}")
            return False
    
    def get_ssl_cert_expiry(self, hostname: str, port: int = 443) -> Optional[datetime.datetime]:
        """Get SSL certificate expiration date for a hostname."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    return expiry_date
        except Exception as e:
            print(f"Error checking SSL cert for {hostname}: {e}")
            return None
    
    def check_website_health(self, url: str) -> Dict:
        """Check website health including response time and certificate status."""
        result = {
            "url": url,
            "timestamp": datetime.datetime.now().isoformat(),
            "response_time_ms": None,
            "status_code": None,
            "ssl_cert_expiry": None,
            "ssl_days_remaining": None,
            "alerts": []
        }
        
        try:
            # Get thresholds for this website
            website_config = self.config["websites"].get(url, {})
            response_threshold = website_config.get("response_time_threshold_ms", 
                                                   self.config["global_settings"]["response_time_threshold_ms"])
            cert_warning_days = website_config.get("cert_expiry_warning_days",
                                                  self.config["global_settings"]["cert_expiry_warning_days"])
            timeout = self.config["global_settings"]["timeout_seconds"]
            
            # Check HTTP response
            start_time = time.time()
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url)
                end_time = time.time()
                
                result["response_time_ms"] = int((end_time - start_time) * 1000)
                result["status_code"] = response.status_code
                
                # Check response time alert
                if result["response_time_ms"] > response_threshold:
                    result["alerts"].append(
                        f"SLOW_RESPONSE: {result['response_time_ms']}ms > {response_threshold}ms threshold"
                    )
                
                # Check HTTP status
                if response.status_code >= 400:
                    result["alerts"].append(f"HTTP_ERROR: Status code {response.status_code}")
            
            # Check SSL certificate if HTTPS
            if url