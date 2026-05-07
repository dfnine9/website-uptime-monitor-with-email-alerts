#!/usr/bin/env python3
"""
URL Health Monitor Script

This script reads URLs from a configuration file, sends HTTP requests to each URL,
measures response times, checks status codes, and logs comprehensive monitoring
data to a timestamped CSV file.

Features:
- Reads URLs from 'urls.txt' config file (one URL per line)
- Measures HTTP response times and status codes
- Logs all data to timestamped CSV files
- Comprehensive error handling
- Real-time stdout reporting
- Self-contained with minimal dependencies

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - Standard library modules only
"""

import csv
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    sys.exit(1)

class URLMonitor:
    """URL health monitoring and logging system."""
    
    def __init__(self, config_file: str = "urls.txt", timeout: int = 30):
        self.config_file = config_file
        self.timeout = timeout
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = f"url_monitor_{self.timestamp}.csv"
        
    def load_urls(self) -> List[str]:
        """Load URLs from configuration file."""
        urls = []
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            print(f"Creating sample config file: {self.config_file}")
            sample_urls = [
                "https://httpbin.org/status/200",
                "https://httpbin.org/delay/1",
                "https://github.com",
                "https://stackoverflow.com"
            ]
            with open(self.config_file, 'w') as f:
                f.write('\n'.join(sample_urls))
            urls = sample_urls
        else:
            try:
                with open(self.config_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except Exception as e:
                print(f"Error reading config file: {e}")
                return []
        
        print(f"Loaded {len(urls)} URLs from {self.config_file}")
        return urls
    
    def ping_url(self, url: str) -> Dict[str, Any]:
        """Send HTTP request and measure response metrics."""
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, follow_redirects=True)
                response_time = round((time.time() - start_time) * 1000, 2)
                
                result = {
                    'timestamp': timestamp,
                    'url': url,
                    'status_code': response.status_code,
                    'response_time_ms': response_time,
                    'success': 200 <= response.status_code < 400,
                    'error_message': None
                }
                
        except httpx.TimeoutException:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': 0,
                'response_time_ms': response_time,
                'success': False,
                'error_message': 'Timeout'
            }
            
        except httpx.RequestError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': 0,
                'response_time_ms': response_time,
                'success': False,
                'error_message': str(e)
            }
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'timestamp': timestamp,
                'url': url,
                'status_code': 0,
                'response_time_ms': response_time,
                'success': False,
                'error_message': f"Unexpected error: {str(e)}"
            }
        
        return result
    
    def initialize_csv(self):
        """Initialize CSV file with headers."""
        headers = ['timestamp', 'url', 'status_code', 'response_time_ms', 'success', 'error_message']
        
        try:
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"Initialized log file: {self.csv_file}")
        except Exception as e:
            print(f"Error initializing CSV file: {e}")
            sys.exit(1)
    
    def log_result(self, result: Dict[str, Any]):
        """Log monitoring result to CSV file."""
        try:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    result['timestamp'],
                    result['url'],
                    result['status_code'],
                    result['response_time_ms'],
                    result['success'],
                    result['error_message'] or ''
                ])
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def print_result(self, result: Dict[str, Any]):
        """Print monitoring result to stdout."""
        status = "SUCCESS" if result['success'] else "FAILURE"
        status_code = result['status_code'] if result['status_code'] > 0 else "N/A"
        
        print(f"[{result['timestamp']}] {status} - {result['url']}")
        print(f"  Status: {status_code} | Response Time: {result['response_time_ms']}ms")
        
        if result['error_message']:
            print(f"  Error: {result['error_message']}")
        
        print("-" * 60)
    
    def monitor_urls(self):
        """Execute URL monitoring cycle."""
        urls = self.load_urls()
        
        if not urls:
            print("No URLs to monitor. Exiting.")
            return
        
        self.initialize_csv()
        print(f"Starting URL monitoring at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        success_count = 0
        total_count = len(urls)
        
        for url in urls:
            print(f"Monitoring: {url}")
            result = self.ping_url(url)
            self.log_result(result)
            self.print_result(result)
            
            if result['success']:
                success_count += 1
        
        # Summary
        print("=" * 60)
        print(f"MONITORING COMPLETE")
        print(f"Total URLs: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"Success Rate: {(success_count/total_count)*100:.1f}%")
        print(f"Results logged to: {self.csv_file}")

def main():
    """Main execution function."""
    try:
        monitor = URLMonitor()
        monitor.monitor_urls()
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()