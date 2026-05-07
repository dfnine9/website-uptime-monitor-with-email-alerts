[ACTION:RESEARCH]

```python
#!/usr/bin/env python3
"""
Website Monitoring Script with Configuration File Support

This script monitors multiple websites for availability and response times based on
configuration settings defined in a JSON or YAML file. It performs HTTP requests
to specified URLs at configured intervals and logs results to CSV files.

Features:
- Configurable monitoring intervals and timeouts
- Support for JSON and YAML configuration files
- CSV output with timestamps, status codes, and response times
- Comprehensive error handling and logging
- Self-contained with minimal dependencies

Usage: python script.py

Dependencies: httpx, anthropic (if needed), standard library modules
"""

import json
import yaml
import httpx
import asyncio
import csv
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys

class WebsiteMonitor:
    def __init__(self, config_path: str = "monitor_config.yaml"):
        """Initialize the website monitor with configuration file."""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.client = httpx.AsyncClient(timeout=self.config.get('default_timeout', 10))
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON or YAML file."""
        config_file = Path(config_path)
        
        # Create default config if file doesn't exist
        if not config_file.exists():
            default_config = {
                "urls": [
                    {"url": "https://httpbin.org/status/200", "name": "httpbin_ok"},
                    {"url": "https://httpbin.org/status/404", "name": "httpbin_404"},
                    {"url": "https://www.google.com", "name": "google"}
                ],
                "check_interval": 60,
                "default_timeout": 10,
                "csv_output_path": "monitoring_results.csv",
                "max_retries": 3
            }
            
            try:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    with open(config_path, 'w') as f:
                        yaml.dump(default_config, f, default_flow_style=False)
                else:
                    with open(config_path, 'w') as f:
                        json.dump(default_config, f, indent=2)
                print(f"Created default configuration file: {config_path}")
            except Exception as e:
                print(f"Error creating default config: {e}")
                return default_config
        
        # Load existing config
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found. Using defaults.")
            return self._get_default_config()
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            print(f"Error parsing configuration file: {e}")
            return self._get_default_config()
        except Exception as e:
            print(f"Unexpected error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "urls": [
                {"url": "https://httpbin.org/status/200", "name": "httpbin_ok"},
                {"url": "https://www.google.com", "name": "google"}
            ],
            "check_interval": 60,
            "default_timeout": 10,
            "csv_output_path": "monitoring_results.csv",
            "max_retries": 3
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def check_website(self, url_config: Dict[str, str]) -> Dict[str, Any]:
        """Check a single website and return status information."""
        url = url_config['url']
        name = url_config.get('name', url)
        timeout = url_config.get('timeout', self.config.get('default_timeout', 10))
        
        start_time = time.time()
        result = {
            'timestamp': datetime.now().isoformat(),
            'name': name,
            'url': url,
            'status_code': None,
            'response_time': None,
            'error': None
        }
        
        try:
            response = await self.client.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            result.update({
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'error': None
            })
            
            print(f"✓ {name} ({url}): {response.status_code} - {response_time:.2f}ms")
            
        except httpx.TimeoutException:
            result['error'] = 'Timeout'
            print(f"✗ {name} ({url}): Timeout after {timeout}s")
            
        except httpx.ConnectError:
            result['error'] = 'Connection Error'
            print(f"✗ {name} ({url}): Connection Error")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"✗ {name} ({url}): {str(e)}")
        
        return result
    
    async def monitor_websites(self):
        """Monitor all configured websites."""
        urls = self.config.get('urls', [])
        if not urls:
            print("No URLs configured for monitoring.")
            return []
        
        print(f"Checking {len(urls)} websites...")
        tasks = [self.check_website(url_config) for url_config in urls]
        results = await asyncio.gather(*tasks)
        return results
    
    def save_to_csv(self, results: List[Dict[str, Any]]):
        """Save monitoring results to CSV file."""
        if not results:
            return
        
        csv_path = self.config.get('csv_output_path', 'monitoring_results.csv')
        file_exists = Path(csv_path).exists()
        
        try:
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'name', 'url', 'status_code', 'response_time', 'error']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                for result in results:
                    writer.writerow(result)
                
            print(f"Results saved to {csv_path}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    async def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        try:
            results = await self.monitor_websites()
            self.save_to_csv(results)
            return results
        except Exception as e:
            print(f"Error during monitoring cycle: {e}")
            return []
    
    async def start_continuous_monitoring(self):
        """Start continuous monitoring based on configured interval."""
        check_interval = self.config.get('check_interval', 60)
        print(f"Starting continuous monitoring (interval: {check_interval}s)")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                await self.run_monitoring_cycle()
                print(f"Waiting {check_interval} seconds until next check...\n")
                await asyncio.sleep(check_interval)
        except KeyboardInterrupt