#!/usr/bin/env python3
"""
URL Monitor Script

A self-contained Python script that monitors URLs by reading them from a config.json file,
making HTTP requests to each URL every 5 minutes, and logging the results to a CSV file.

The script logs timestamp, URL, status code, and response time for each request.
Includes comprehensive error handling for network issues, file operations, and JSON parsing.

Requirements:
- config.json file with URLs list
- Python 3.6+ with httpx library

Usage: python script.py
"""

import json
import csv
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class URLMonitor:
    def __init__(self, config_file: str = "config.json", log_file: str = "url_monitor.csv"):
        self.config_file = config_file
        self.log_file = log_file
        self.urls = []
        self.setup_csv_file()
    
    def load_config(self) -> bool:
        """Load URLs from config.json file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.urls = config.get('urls', [])
                if not self.urls:
                    print(f"Warning: No URLs found in {self.config_file}")
                    return False
                print(f"Loaded {len(self.urls)} URLs from config")
                return True
        except FileNotFoundError:
            print(f"Error: {self.config_file} not found. Creating sample config...")
            self.create_sample_config()
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {self.config_file}: {e}")
            return False
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def create_sample_config(self):
        """Create a sample config.json file."""
        sample_config = {
            "urls": [
                "https://httpbin.org/status/200",
                "https://httpbin.org/delay/1",
                "https://google.com"
            ]
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(sample_config, f, indent=2)
            print(f"Sample {self.config_file} created. Please edit it and run again.")
        except Exception as e:
            print(f"Error creating sample config: {e}")
    
    def setup_csv_file(self):
        """Setup CSV file with headers if it doesn't exist."""
        csv_path = Path(self.log_file)
        if not csv_path.exists():
            try:
                with open(self.log_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms', 'error'])
                print(f"Created CSV log file: {self.log_file}")
            except Exception as e:
                print(f"Error creating CSV file: {e}")
                sys.exit(1)
    
    def check_url(self, url: str) -> Dict[str, Any]:
        """Make HTTP request to URL and return results."""
        start_time = time.time()
        result = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'status_code': None,
            'response_time_ms': None,
            'error': None
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                end_time = time.time()
                result['status_code'] = response.status_code
                result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
                
        except httpx.TimeoutException:
            result['error'] = 'Timeout'
        except httpx.NetworkError as e:
            result['error'] = f'Network Error: {str(e)}'
        except httpx.HTTPStatusError as e:
            result['error'] = f'HTTP Error: {str(e)}'
        except Exception as e:
            result['error'] = f'Unexpected Error: {str(e)}'
        
        return result
    
    def log_result(self, result: Dict[str, Any]):
        """Log result to CSV file."""
        try:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    result['timestamp'],
                    result['url'],
                    result['status_code'],
                    result['response_time_ms'],
                    result['error']
                ])
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def print_result(self, result: Dict[str, Any]):
        """Print result to stdout."""
        status = result['status_code'] if result['status_code'] else 'ERROR'
        response_time = f"{result['response_time_ms']}ms" if result['response_time_ms'] else 'N/A'
        error_info = f" - {result['error']}" if result['error'] else ""
        
        print(f"[{result['timestamp']}] {result['url']} -> {status} ({response_time}){error_info}")
    
    def monitor_once(self):
        """Monitor all URLs once."""
        if not self.urls:
            return
        
        print(f"\nChecking {len(self.urls)} URLs...")
        for url in self.urls:
            result = self.check_url(url)
            self.log_result(result)
            self.print_result(result)
    
    def run(self):
        """Main monitoring loop."""
        print("URL Monitor Starting...")
        
        if not self.load_config():
            return
        
        print(f"Monitoring URLs every 5 minutes. Logging to {self.log_file}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.monitor_once()
                print("\nWaiting 5 minutes for next check...")
                time.sleep(300)  # 5 minutes
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")


def main():
    """Main entry point."""
    monitor = URLMonitor()
    monitor.run()


if __name__ == "__main__":
    main()