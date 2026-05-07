#!/usr/bin/env python3
"""
HTTP Response Time Monitor

A self-contained Python script that monitors HTTP response times for a configurable
list of URLs. Measures response times, handles errors gracefully, and logs all
results to a structured JSON file with timestamps.

Features:
- Configurable URL list and timeout settings
- Comprehensive error handling for timeouts and connection issues
- Structured JSON logging with timestamps
- Real-time stdout output
- Self-contained with minimal dependencies

Usage:
    python script.py

Dependencies:
    - requests (for HTTP requests)
    - json, datetime, time (standard library)
"""

import json
import time
import datetime
from typing import List, Dict, Any
import sys

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install with: pip install requests")
    sys.exit(1)


class HTTPMonitor:
    def __init__(self, urls: List[str], timeout: int = 10, output_file: str = "http_monitor_results.json"):
        """
        Initialize HTTP Monitor
        
        Args:
            urls: List of URLs to monitor
            timeout: Request timeout in seconds
            output_file: JSON file to log results
        """
        self.urls = urls
        self.timeout = timeout
        self.output_file = output_file
        self.results = []
    
    def make_request(self, url: str) -> Dict[str, Any]:
        """
        Make HTTP request and measure response time
        
        Args:
            url: URL to request
            
        Returns:
            Dictionary containing request results
        """
        timestamp = datetime.datetime.now().isoformat()
        start_time = time.time()
        
        result = {
            "timestamp": timestamp,
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "error": None,
            "error_type": None
        }
        
        try:
            response = requests.get(url, timeout=self.timeout)
            end_time = time.time()
            
            result["status_code"] = response.status_code
            result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
            
            print(f"✓ {url} - Status: {response.status_code} - Time: {result['response_time_ms']}ms")
            
        except requests.exceptions.Timeout:
            result["error"] = f"Request timeout after {self.timeout} seconds"
            result["error_type"] = "timeout"
            print(f"✗ {url} - TIMEOUT ({self.timeout}s)")
            
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"Connection error: {str(e)}"
            result["error_type"] = "connection_error"
            print(f"✗ {url} - CONNECTION ERROR")
            
        except requests.exceptions.RequestException as e:
            result["error"] = f"Request error: {str(e)}"
            result["error_type"] = "request_error"
            print(f"✗ {url} - REQUEST ERROR: {str(e)}")
            
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            result["error_type"] = "unexpected_error"
            print(f"✗ {url} - UNEXPECTED ERROR: {str(e)}")
        
        return result
    
    def save_results(self):
        """Save results to JSON file"""
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\nResults saved to: {self.output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def run_monitoring(self):
        """Run monitoring for all configured URLs"""
        print(f"Starting HTTP monitoring for {len(self.urls)} URLs...")
        print(f"Timeout: {self.timeout}s")
        print("-" * 60)
        
        for url in self.urls:
            result = self.make_request(url)
            self.results.append(result)
        
        print("-" * 60)
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print monitoring summary"""
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r["error"] is None])
        failed_requests = total_requests - successful_requests
        
        if successful_requests > 0:
            avg_response_time = sum(r["response_time_ms"] for r in self.results if r["response_time_ms"]) / successful_requests
        else:
            avg_response_time = 0
        
        print(f"Summary:")
        print(f"  Total requests: {total_requests}")
        print(f"  Successful: {successful_requests}")
        print(f"  Failed: {failed_requests}")
        print(f"  Average response time: {avg_response_time:.2f}ms")


def main():
    """Main function to run HTTP monitoring"""
    
    # Configuration
    URLS_TO_MONITOR = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
        "https://httpbin.org/status/500",
        "https://google.com",
        "https://github.com",
        "https://nonexistent-website-12345.com",  # This will fail
    ]
    
    TIMEOUT_SECONDS = 10
    OUTPUT_FILE = "http_monitor_results.json"
    
    try:
        monitor = HTTPMonitor(
            urls=URLS_TO_MONITOR,
            timeout=TIMEOUT_SECONDS,
            output_file=OUTPUT_FILE
        )
        monitor.run_monitoring()
        
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()