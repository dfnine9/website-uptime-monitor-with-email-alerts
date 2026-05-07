#!/usr/bin/env python3
"""
URL Health Monitor

A self-contained Python script that reads URLs from a configuration file,
performs HTTP health checks with timeout handling, and logs results to CSV.

Features:
- Reads URLs from config.txt (one URL per line)
- Makes HTTP requests with configurable timeout
- Logs timestamp, URL, status code, and response time to results.csv
- Comprehensive error handling for network issues
- Real-time stdout feedback
- Uses only standard library + httpx for HTTP requests

Usage: python script.py

Config file format (config.txt):
https://example.com
https://google.com
https://httpbin.org/delay/2
"""

import csv
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    sys.exit(1)


class URLMonitor:
    """Main class for URL health monitoring functionality."""
    
    def __init__(self, config_file: str = "config.txt", output_file: str = "results.csv", timeout: float = 10.0):
        self.config_file = config_file
        self.output_file = output_file
        self.timeout = timeout
        self.session = httpx.Client(timeout=timeout, follow_redirects=True)
    
    def load_urls(self) -> List[str]:
        """Load URLs from configuration file."""
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                # Create sample config if it doesn't exist
                sample_urls = [
                    "https://httpbin.org/status/200",
                    "https://httpbin.org/delay/1", 
                    "https://google.com",
                    "https://httpbin.org/status/404"
                ]
                with open(self.config_file, 'w') as f:
                    f.write('\n'.join(sample_urls))
                print(f"Created sample config file: {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                raise ValueError("No valid URLs found in config file")
                
            print(f"Loaded {len(urls)} URLs from {self.config_file}")
            return urls
            
        except Exception as e:
            print(f"Error loading config file {self.config_file}: {e}")
            return []
    
    def check_url(self, url: str) -> Tuple[str, str, Optional[int], Optional[float], str]:
        """
        Check a single URL and return results.
        
        Returns: (timestamp, url, status_code, response_time, error_message)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_time = time.time()
        
        try:
            response = self.session.get(url)
            response_time = time.time() - start_time
            
            print(f"✓ {url} - {response.status_code} ({response_time:.3f}s)")
            return timestamp, url, response.status_code, response_time, ""
            
        except httpx.TimeoutException:
            response_time = time.time() - start_time
            error_msg = "Timeout"
            print(f"✗ {url} - TIMEOUT ({response_time:.3f}s)")
            return timestamp, url, None, response_time, error_msg
            
        except httpx.ConnectError as e:
            response_time = time.time() - start_time
            error_msg = f"Connection Error: {str(e)}"
            print(f"✗ {url} - CONNECTION ERROR ({response_time:.3f}s)")
            return timestamp, url, None, response_time, error_msg
            
        except httpx.RequestError as e:
            response_time = time.time() - start_time
            error_msg = f"Request Error: {str(e)}"
            print(f"✗ {url} - REQUEST ERROR ({response_time:.3f}s)")
            return timestamp, url, None, response_time, error_msg
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Unexpected Error: {str(e)}"
            print(f"✗ {url} - ERROR ({response_time:.3f}s): {error_msg}")
            return timestamp, url, None, response_time, error_msg
    
    def initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        try:
            output_path = Path(self.output_file)
            if not output_path.exists():
                with open(self.output_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['timestamp', 'url', 'status_code', 'response_time', 'error'])
                print(f"Created output file: {self.output_file}")
        except Exception as e:
            print(f"Error initializing CSV file: {e}")
            raise
    
    def write_result(self, result: Tuple[str, str, Optional[int], Optional[float], str]) -> None:
        """Write a single result to CSV file."""
        try:
            with open(self.output_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(result)
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def run_checks(self) -> None:
        """Main method to run URL checks."""
        print(f"URL Health Monitor Starting - Timeout: {self.timeout}s")
        print("=" * 60)
        
        urls = self.load_urls()
        if not urls:
            print("No URLs to check. Exiting.")
            return
        
        self.initialize_csv()
        
        total_checks = len(urls)
        successful_checks = 0
        
        try:
            for i, url in enumerate(urls, 1):
                print(f"[{i}/{total_checks}] Checking: {url}")
                
                result = self.check_url(url)
                self.write_result(result)
                
                if result[2] is not None and 200 <= result[2] < 300:
                    successful_checks += 1
                
                # Brief pause between requests to be respectful
                if i < total_checks:
                    time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n\nMonitoring interrupted by user")
        
        except Exception as e:
            print(f"\nUnexpected error during monitoring: {e}")
        
        finally:
            self.session.close()
            print("=" * 60)
            print(f"Monitoring complete: {successful_checks}/{total_checks} successful")
            print(f"Results saved to: {self.output_file}")


def main():
    """Entry point for the script."""
    try:
        monitor = URLMonitor()
        monitor.run_checks()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()