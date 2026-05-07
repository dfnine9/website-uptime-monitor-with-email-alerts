#!/usr/bin/env python3
"""
HTTP Endpoint Monitor

A self-contained Python script that monitors HTTP endpoints by making requests
to a configurable list of URLs, measuring response times and status codes,
and logging results with timestamps to a CSV file.

Features:
- Configurable URL list
- Response time measurement
- Status code tracking  
- CSV logging with timestamps
- Console output
- Error handling for network issues

Dependencies: httpx, anthropic (as specified in requirements)
Usage: python script.py
"""

import csv
import time
import sys
from datetime import datetime
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

# Configuration
URLS_TO_MONITOR = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/delay/1", 
    "https://httpbin.org/status/404",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://example.com"
]

CSV_FILENAME = "http_monitor_results.csv"
REQUEST_TIMEOUT = 10.0
USER_AGENT = "HTTP-Monitor/1.0"

def setup_csv_file() -> None:
    """Initialize CSV file with headers if it doesn't exist."""
    try:
        with open(CSV_FILENAME, 'x', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms', 'error'])
    except FileExistsError:
        pass

def check_url(url: str) -> Dict[str, Any]:
    """
    Make HTTP request to URL and measure response time.
    
    Args:
        url: The URL to check
        
    Returns:
        Dictionary containing timestamp, url, status_code, response_time_ms, and error
    """
    timestamp = datetime.now().isoformat()
    result = {
        'timestamp': timestamp,
        'url': url,
        'status_code': None,
        'response_time_ms': None,
        'error': None
    }
    
    try:
        start_time = time.perf_counter()
        
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(
                url,
                headers={'User-Agent': USER_AGENT},
                follow_redirects=True
            )
            
        end_time = time.perf_counter()
        
        result['status_code'] = response.status_code
        result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        
    except httpx.TimeoutException:
        result['error'] = 'Timeout'
    except httpx.ConnectError:
        result['error'] = 'Connection Error'
    except httpx.RequestError as e:
        result['error'] = f'Request Error: {str(e)}'
    except Exception as e:
        result['error'] = f'Unexpected Error: {str(e)}'
    
    return result

def log_result_to_csv(result: Dict[str, Any]) -> None:
    """Log a single result to CSV file."""
    try:
        with open(CSV_FILENAME, 'a', newline='') as csvfile:
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

def print_result(result: Dict[str, Any]) -> None:
    """Print result to stdout in a readable format."""
    url = result['url']
    timestamp = result['timestamp']
    
    if result['error']:
        print(f"[{timestamp}] {url} - ERROR: {result['error']}")
    else:
        status = result['status_code']
        response_time = result['response_time_ms']
        print(f"[{timestamp}] {url} - Status: {status}, Time: {response_time}ms")

def monitor_urls(urls: List[str]) -> None:
    """
    Monitor a list of URLs and log results.
    
    Args:
        urls: List of URLs to monitor
    """
    print(f"Starting HTTP monitoring for {len(urls)} URLs...")
    print(f"Results will be logged to: {CSV_FILENAME}")
    print("-" * 80)
    
    setup_csv_file()
    
    for url in urls:
        try:
            result = check_url(url)
            print_result(result)
            log_result_to_csv(result)
        except KeyboardInterrupt:
            print("\nMonitoring interrupted by user")
            break
        except Exception as e:
            print(f"Unexpected error processing {url}: {e}")
    
    print("-" * 80)
    print(f"Monitoring complete. Results saved to {CSV_FILENAME}")

def main():
    """Main entry point."""
    try:
        monitor_urls(URLS_TO_MONITOR)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()