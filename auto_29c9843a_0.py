```python
#!/usr/bin/env python3
"""
URL Status Checker

This module reads URLs from a JSON configuration file and performs HTTP status checks
on each URL. It logs the results with timestamps to both console and file output.

Features:
- Reads URL list from JSON config file
- Performs HTTP GET requests with configurable timeout
- Handles network errors and timeouts gracefully
- Logs results with timestamps to console and file
- Uses only standard library plus httpx for HTTP requests

Usage:
    python script.py

Config file format (config.json):
{
    "urls": [
        "https://example.com",
        "https://google.com",
        "https://httpstat.us/404"
    ],
    "timeout": 10,
    "log_file": "status_check.log"
}
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    sys.exit(1)


class URLStatusChecker:
    """Checks HTTP status codes for a list of URLs."""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the URL status checker.
        
        Args:
            config_file: Path to JSON configuration file
        """
        self.config = self._load_config(config_file)
        self.logger = self._setup_logging()
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                # Create default config if none exists
                default_config = {
                    "urls": [
                        "https://httpbin.org/status/200",
                        "https://httpbin.org/status/404", 
                        "https://httpbin.org/status/500",
                        "https://google.com",
                        "https://nonexistent-domain-12345.com"
                    ],
                    "timeout": 10,
                    "log_file": "status_check.log"
                }
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default config file: {config_file}")
                return default_config
            
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Validate required fields
            if 'urls' not in config:
                raise ValueError("Config must contain 'urls' field")
            if not isinstance(config['urls'], list):
                raise ValueError("'urls' must be a list")
                
            # Set defaults for optional fields
            config.setdefault('timeout', 10)
            config.setdefault('log_file', 'status_check.log')
            
            return config
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config file {config_file}: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"Invalid config: {e}")
            sys.exit(1)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging to both console and file."""
        logger = logging.getLogger('url_status_checker')
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler
        try:
            file_handler = logging.FileHandler(self.config['log_file'])
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
        
        return logger
    
    def check_url(self, url: str) -> Dict[str, any]:
        """
        Check the status of a single URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dict containing URL, status_code, response_time, error (if any)
        """
        start_time = datetime.now()
        result = {
            'url': url,
            'status_code': None,
            'response_time': None,
            'error': None,
            'timestamp': start_time.isoformat()
        }
        
        try:
            with httpx.Client(timeout=self.config['timeout']) as client:
                response = client.get(url, follow_redirects=True)
                end_time = datetime.now()
                
                result['status_code'] = response.status_code
                result['response_time'] = (end_time - start_time).total_seconds()
                
        except httpx.TimeoutException:
            result['error'] = f"Timeout after {self.config['timeout']} seconds"
        except httpx.NetworkError as e:
            result['error'] = f"Network error: {str(e)}"
        except httpx.InvalidURL:
            result['error'] = "Invalid URL format"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        
        return result
    
    def check_all_urls(self) -> List[Dict]:
        """
        Check status codes for all URLs in config.
        
        Returns:
            List of result dictionaries
        """
        results = []
        urls = self.config['urls']
        
        self.logger.info(f"Starting status check for {len(urls)} URLs")
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Checking URL {i}/{len(urls)}: {url}")
            
            result = self.check_url(url)
            results.append(result)
            
            # Log result
            if result['error']:
                self.logger.error(f"  ❌ {url} - ERROR: {result['error']}")
            else:
                status_code = result['status_code']
                response_time = result['response_time']
                emoji = "✅" if 200 <= status_code < 400 else "⚠️" if status_code < 500 else "❌"
                self.logger.info(f"  {emoji} {url} - Status: {status_code}, Time: {response_time:.2f}s")
        
        return results
    
    def print_summary(self, results: List[Dict]) -> None:
        """Print a summary of all results."""
        total = len(results)
        successful = len([r for r in results if r['status_code'] and 200 <= r['status_code'] < 400])
        errors = len([r for r in results if r['error']])
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Total URLs checked: {total}")
        print(f"Successful (2xx-3xx): {successful}")
        print(f"Client/Server errors: {total - successful - errors}")
        print(f"Network/Timeout errors: {errors}")
        print(f"Success rate: {(successful/total)*100:.1f}%")
        print("="*50)


def main():
    """Main execution function."""
    try:
        checker = URLStatusChecker()
        results = checker.check_all_urls()
        checker.print_summary(results)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(