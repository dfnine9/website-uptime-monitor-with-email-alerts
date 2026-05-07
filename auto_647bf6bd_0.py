#!/usr/bin/env python3
"""
URL Monitor Script

This script monitors a list of URLs by pinging them every 5 minutes.
It captures timestamp, URL, status code, and response time, then logs
this data to a CSV file with proper error handling for timeouts and
connection failures.

Usage: python script.py
"""

import csv
import time
import datetime
import requests
from typing import List, Dict, Any
import os

class URLMonitor:
    def __init__(self, urls: List[str], csv_filename: str = "url_monitor.csv", interval: int = 300):
        """
        Initialize URL monitor.
        
        Args:
            urls: List of URLs to monitor
            csv_filename: Name of CSV file to log results
            interval: Check interval in seconds (default 300 = 5 minutes)
        """
        self.urls = urls
        self.csv_filename = csv_filename
        self.interval = interval
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Create CSV file with headers if it doesn't exist
        if not os.path.exists(csv_filename):
            self._create_csv_file()
    
    def _create_csv_file(self):
        """Create CSV file with headers."""
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms', 'error'])
    
    def ping_url(self, url: str) -> Dict[str, Any]:
        """
        Ping a single URL and return metrics.
        
        Args:
            url: URL to ping
            
        Returns:
            Dictionary with timestamp, url, status_code, response_time_ms, error
        """
        timestamp = datetime.datetime.now().isoformat()
        start_time = time.time()
        
        try:
            response = self.session.get(url, timeout=30)
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': response_time_ms,
                'error': None
            }
            
        except requests.exceptions.Timeout:
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': None,
                'response_time_ms': None,
                'error': 'Timeout'
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': None,
                'response_time_ms': None,
                'error': 'Connection Error'
            }
            
        except requests.exceptions.RequestException as e:
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': None,
                'response_time_ms': None,
                'error': f'Request Error: {str(e)}'
            }
            
        except Exception as e:
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': None,
                'response_time_ms': None,
                'error': f'Unexpected Error: {str(e)}'
            }
        
        return result
    
    def log_result(self, result: Dict[str, Any]):
        """Log result to CSV file."""
        try:
            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
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
        timestamp = result['timestamp']
        url = result['url']
        status = result['status_code'] if result['status_code'] else 'FAIL'
        response_time = f"{result['response_time_ms']}ms" if result['response_time_ms'] else 'N/A'
        error = result['error'] if result['error'] else 'OK'
        
        print(f"[{timestamp}] {url} - Status: {status}, Time: {response_time}, Result: {error}")
    
    def monitor_urls(self):
        """Main monitoring loop."""
        print(f"Starting URL monitoring for {len(self.urls)} URLs")
        print(f"Check interval: {self.interval} seconds")
        print(f"Logging to: {self.csv_filename}")
        print("-" * 60)
        
        try:
            while True:
                for url in self.urls:
                    result = self.ping_url(url)
                    self.log_result(result)
                    self.print_result(result)
                
                print(f"Next check in {self.interval} seconds...")
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Monitor error: {e}")

def main():
    """Main function."""
    # Default URLs to monitor - modify as needed
    urls_to_monitor = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/delay/2",
        "https://google.com",
        "https://github.com"
    ]
    
    monitor = URLMonitor(urls_to_monitor)
    monitor.monitor_urls()

if __name__ == "__main__":
    main()