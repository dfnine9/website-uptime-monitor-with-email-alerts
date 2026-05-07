#!/usr/bin/env python3
"""
URL Status Monitor

This module monitors a list of URLs by checking their HTTP status codes at regular intervals.
It reads URLs from a configuration file, makes HTTP requests every 5 minutes, logs results
to a JSON file with timestamps, and prints status updates to stdout.

The script is designed to run continuously until interrupted (Ctrl+C).

Configuration:
- URLs are read from 'config.txt' (one URL per line)
- Results are logged to 'status_log.json'
- Check interval is 5 minutes (300 seconds)

Dependencies: httpx, json, time, datetime (all standard library except httpx)
"""

import json
import time
import datetime
import os
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Please install with: pip install httpx")
    exit(1)


class URLMonitor:
    """Monitors URLs and logs their status codes."""
    
    def __init__(self, config_file: str = "config.txt", log_file: str = "status_log.json"):
        self.config_file = config_file
        self.log_file = log_file
        self.check_interval = 300  # 5 minutes in seconds
        
    def load_urls(self) -> List[str]:
        """Load URLs from configuration file."""
        urls = []
        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    url = line.strip()
                    if url and not url.startswith('#'):
                        urls.append(url)
            print(f"Loaded {len(urls)} URLs from {self.config_file}")
            return urls
        except FileNotFoundError:
            print(f"Config file '{self.config_file}' not found. Creating sample file...")
            self.create_sample_config()
            return []
        except Exception as e:
            print(f"Error loading URLs: {e}")
            return []
    
    def create_sample_config(self):
        """Create a sample configuration file."""
        sample_urls = [
            "https://httpbin.org/status/200",
            "https://httpbin.org/status/404",
            "https://google.com",
            "https://github.com"
        ]
        try:
            with open(self.config_file, 'w') as f:
                f.write("# URL Monitor Configuration\n")
                f.write("# Add one URL per line\n")
                f.write("# Lines starting with # are ignored\n\n")
                for url in sample_urls:
                    f.write(f"{url}\n")
            print(f"Sample config file created at '{self.config_file}'")
        except Exception as e:
            print(f"Error creating sample config: {e}")
    
    def check_url_status(self, url: str) -> Dict[str, Any]:
        """Check the status code of a single URL."""
        result = {
            "url": url,
            "timestamp": datetime.datetime.now().isoformat(),
            "status_code": None,
            "response_time_ms": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                end_time = time.time()
                
                result["status_code"] = response.status_code
                result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
                
        except httpx.TimeoutException:
            result["error"] = "Request timeout"
        except httpx.ConnectError:
            result["error"] = "Connection error"
        except httpx.HTTPError as e:
            result["error"] = f"HTTP error: {str(e)}"
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def log_result(self, result: Dict[str, Any]):
        """Log result to JSON file."""
        try:
            # Load existing data
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Append new result
            data.append(result)
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error logging result: {e}")
    
    def print_result(self, result: Dict[str, Any]):
        """Print result to stdout."""
        timestamp = result["timestamp"]
        url = result["url"]
        
        if result["error"]:
            status_info = f"ERROR: {result['error']}"
        else:
            status_code = result["status_code"]
            response_time = result["response_time_ms"]
            status_info = f"Status: {status_code}, Response time: {response_time}ms"
        
        print(f"[{timestamp}] {url} - {status_info}")
    
    def run_check_cycle(self, urls: List[str]):
        """Run a single check cycle for all URLs."""
        print(f"\n--- Starting check cycle at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        for url in urls:
            result = self.check_url_status(url)
            self.print_result(result)
            self.log_result(result)
        
        print(f"--- Check cycle completed ---")
    
    def run(self):
        """Main monitoring loop."""
        print("URL Status Monitor starting...")
        
        urls = self.load_urls()
        if not urls:
            print("No URLs to monitor. Exiting.")
            return
        
        print(f"Monitoring {len(urls)} URLs every {self.check_interval//60} minutes")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_check_cycle(urls)
                print(f"Waiting {self.check_interval} seconds until next check...\n")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")


def main():
    """Main entry point."""
    monitor = URLMonitor()
    monitor.run()


if __name__ == "__main__":
    main()