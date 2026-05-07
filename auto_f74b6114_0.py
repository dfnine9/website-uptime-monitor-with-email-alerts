```python
#!/usr/bin/env python3
"""
HTTP Health Check Monitor

This module performs comprehensive health checks on URLs specified in a JSON configuration file.
It validates HTTP status codes, measures response times, and checks SSL certificate expiry dates.
All results are logged with structured formatting and printed to stdout.

Features:
- Reads URL configurations from JSON file
- Performs HTTP GET requests with timeout handling
- Validates SSL certificate expiry dates
- Measures and reports response times
- Structured logging with JSON output
- Comprehensive error handling

Usage:
    python script.py

Configuration file (config.json) format:
{
    "urls": [
        {"name": "Example Site", "url": "https://example.com", "timeout": 10},
        {"name": "API Endpoint", "url": "https://api.example.com/health", "timeout": 5}
    ]
}
"""

import json
import ssl
import socket
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging
import sys

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class HealthChecker:
    """Performs HTTP health checks and SSL certificate validation."""
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize health checker with configuration file."""
        self.config_file = config_file
        self.results = []
    
    def load_config(self) -> List[Dict[str, Any]]:
        """Load URL configurations from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('urls', [])
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found")
            # Create sample config file
            sample_config = {
                "urls": [
                    {"name": "Google", "url": "https://google.com", "timeout": 10},
                    {"name": "GitHub", "url": "https://github.com", "timeout": 5},
                    {"name": "Invalid URL", "url": "https://nonexistent-domain-12345.com", "timeout": 5}
                ]
            }
            with open(self.config_file, 'w') as f:
                json.dump(sample_config, f, indent=2)
            logger.info(f"Created sample configuration file: {self.config_file}")
            return sample_config.get('urls', [])
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return []
    
    def get_ssl_expiry(self, hostname: str, port: int = 443) -> Optional[datetime]:
        """Get SSL certificate expiry date for a hostname."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    expiry_str = cert['notAfter']
                    # Parse SSL date format: 'MMM DD HH:MM:SS YYYY GMT'
                    expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                    return expiry_date.replace(tzinfo=timezone.utc)
        except Exception as e:
            logger.warning(f"Could not retrieve SSL certificate for {hostname}: {e}")
            return None
    
    def check_url(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform health check on a single URL."""
        name = config.get('name', 'Unknown')
        url = config.get('url', '')
        timeout = config.get('timeout', 10)
        
        result = {
            'name': name,
            'url': url,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'unknown',
            'status_code': None,
            'response_time_ms': None,
            'ssl_expiry': None,
            'ssl_days_until_expiry': None,
            'error': None
        }
        
        try:
            # Parse URL to get hostname for SSL check
            parsed_url = urllib.parse.urlparse(url)
            hostname = parsed_url.hostname
            
            # Measure response time
            start_time = time.time()
            
            # Create request with timeout
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'HealthChecker/1.0')
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                end_time = time.time()
                response_time_ms = round((end_time - start_time) * 1000, 2)
                
                result['status'] = 'healthy'
                result['status_code'] = response.getcode()
                result['response_time_ms'] = response_time_ms
                
                logger.info(f"✓ {name}: HTTP {response.getcode()} - {response_time_ms}ms")
            
            # Check SSL certificate if HTTPS
            if parsed_url.scheme == 'https' and hostname:
                ssl_expiry = self.get_ssl_expiry(hostname)
                if ssl_expiry:
                    result['ssl_expiry'] = ssl_expiry.isoformat()
                    days_until_expiry = (ssl_expiry - datetime.now(timezone.utc)).days
                    result['ssl_days_until_expiry'] = days_until_expiry
                    
                    if days_until_expiry <= 30:
                        logger.warning(f"⚠ {name}: SSL certificate expires in {days_until_expiry} days")
                    else:
                        logger.info(f"✓ {name}: SSL certificate valid for {days_until_expiry} days")
        
        except urllib.error.HTTPError as e:
            end_time = time.time()
            response_time_ms = round((end_time - start_time) * 1000, 2)
            
            result['status'] = 'unhealthy'
            result['status_code'] = e.code
            result['response_time_ms'] = response_time_ms
            result['error'] = f"HTTP {e.code}: {e.reason}"
            
            logger.error(f"✗ {name}: HTTP {e.code} - {e.reason}")
        
        except urllib.error.URLError as e:
            result['status'] = 'failed'
            result['error'] = f"URL Error: {str(e.reason)}"
            logger.error(f"✗ {name}: {result['error']}")
        
        except socket.timeout:
            result['status'] = 'timeout'
            result['error'] = f"Request timeout after {timeout}s"
            logger.error(f"✗ {name}: Timeout after {timeout}s")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f"Unexpected error: {str(e)}"
            logger.error(f"✗ {name}: {result['error']}")
        
        return result
    
    def run_checks(self) -> List[Dict[str, Any]]:
        """Run health checks on all configured URLs."""
        urls = self.load_config()
        
        if not urls:
            logger.error("No URLs configured for health checks")
            return []
        
        logger.info(f"Starting health checks for {len(urls)} URLs")
        
        for url_config in urls:
            result = self.check_url(url_config)
            self.results.append(result)
        
        return self.