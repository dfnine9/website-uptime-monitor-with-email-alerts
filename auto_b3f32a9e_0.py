"""
Website Monitoring Script

This script monitors multiple websites by pinging them and recording their response times,
HTTP status codes, and uptime status. Results are logged to a CSV file with timestamps.

Features:
- Pings multiple websites using the requests library
- Measures response times in milliseconds
- Checks HTTP status codes
- Determines uptime status (UP/DOWN)
- Logs results to CSV file with timestamps
- Includes error handling for network issues
- Prints results to stdout for real-time monitoring

Usage: python script.py
"""

import csv
import time
import requests
from datetime import datetime
from typing import List, Dict, Any

def ping_website(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Ping a website and return response metrics.
    
    Args:
        url: The URL to ping
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing URL, response_time_ms, status_code, uptime_status, timestamp
    """
    result = {
        'URL': url,
        'response_time_ms': None,
        'status_code': None,
        'uptime_status': 'DOWN',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        
        result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        result['status_code'] = response.status_code
        result['uptime_status'] = 'UP' if 200 <= response.status_code < 400 else 'DOWN'
        
    except requests.exceptions.RequestException as e:
        print(f"Error pinging {url}: {e}")
        result['response_time_ms'] = 0
        result['status_code'] = 0
        result['uptime_status'] = 'DOWN'
    
    return result

def log_to_csv(results: List[Dict[str, Any]], filename: str = 'website_monitoring.csv'):
    """
    Log results to CSV file.
    
    Args:
        results: List of ping results
        filename: CSV filename to write to
    """
    fieldnames = ['URL', 'response_time_ms', 'status_code', 'uptime_status', 'timestamp']
    
    try:
        # Check if file exists to determine if we need to write headers
        try:
            with open(filename, 'r'):
                file_exists = True
        except FileNotFoundError:
            file_exists = False
        
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write headers if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write results
            for result in results:
                writer.writerow(result)
                
        print(f"Results logged to {filename}")
        
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def main():
    """Main function to monitor websites."""
    # List of websites to monitor
    websites = [
        'https://google.com',
        'https://github.com',
        'https://stackoverflow.com',
        'https://python.org',
        'https://httpbin.org/status/200',
        'https://httpbin.org/delay/2',
        'https://httpbin.org/status/500'
    ]
    
    print("Starting website monitoring...")
    print("-" * 80)
    print(f"{'URL':<30} {'Response Time (ms)':<18} {'Status Code':<12} {'Status':<8}")
    print("-" * 80)
    
    results = []
    
    for url in websites:
        result = ping_website(url)
        results.append(result)
        
        # Print result to stdout
        response_time = result['response_time_ms'] if result['response_time_ms'] is not None else 'N/A'
        status_code = result['status_code'] if result['status_code'] is not None else 'N/A'
        
        print(f"{url:<30} {str(response_time):<18} {str(status_code):<12} {result['uptime_status']:<8}")
    
    print("-" * 80)
    
    # Log results to CSV
    log_to_csv(results)
    
    # Summary statistics
    up_count = sum(1 for r in results if r['uptime_status'] == 'UP')
    total_count = len(results)
    avg_response_time = sum(r['response_time_ms'] for r in results if r['response_time_ms'] is not None) / max(1, up_count)
    
    print(f"\nSummary:")
    print(f"Total websites monitored: {total_count}")
    print(f"Websites UP: {up_count}")
    print(f"Websites DOWN: {total_count - up_count}")
    print(f"Average response time: {avg_response_time:.2f}ms")

if __name__ == "__main__":
    main()