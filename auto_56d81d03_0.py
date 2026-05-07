#!/usr/bin/env python3
"""
HTTP Endpoint Monitor Script

This script monitors a predefined list of URLs by making HTTP requests and capturing:
- Response status codes
- Response times (in milliseconds)
- Timestamps
- Error information

All data is logged to a CSV file with proper error handling for network issues,
timeouts, and other HTTP-related errors. Results are also printed to stdout.

Dependencies: httpx, anthropic (as specified in requirements)
Usage: python script.py
"""

import csv
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)

# Predefined list of URLs to monitor
URLS = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404",
    "https://httpbin.org/delay/2",
    "https://google.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://nonexistent-domain-12345.com"
]

CSV_FILENAME = "http_monitoring_results.csv"
REQUEST_TIMEOUT = 10.0


def make_request(url: str) -> Dict[str, Any]:
    """
    Make HTTP request to a URL and capture metrics.
    
    Args:
        url: The URL to request
        
    Returns:
        Dictionary containing timestamp, url, status_code, response_time_ms, and error
    """
    timestamp = datetime.now().isoformat()
    start_time = time.time()
    
    result = {
        "timestamp": timestamp,
        "url": url,
        "status_code": None,
        "response_time_ms": None,
        "error": None
    }
    
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(url)
            end_time = time.time()
            
            result["status_code"] = response.status_code
            result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
            
    except httpx.TimeoutException:
        end_time = time.time()
        result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
        result["error"] = "Timeout"
        
    except httpx.ConnectError:
        end_time = time.time()
        result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
        result["error"] = "Connection Error"
        
    except httpx.RequestError as e:
        end_time = time.time()
        result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
        result["error"] = f"Request Error: {str(e)}"
        
    except Exception as e:
        end_time = time.time()
        result["response_time_ms"] = round((end_time - start_time) * 1000, 2)
        result["error"] = f"Unexpected Error: {str(e)}"
    
    return result


def write_to_csv(results: List[Dict[str, Any]], filename: str) -> None:
    """
    Write results to CSV file.
    
    Args:
        results: List of result dictionaries
        filename: CSV filename to write to
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["timestamp", "url", "status_code", "response_time_ms", "error"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
                
        print(f"\nResults written to {filename}")
        
    except IOError as e:
        print(f"Error writing to CSV file: {e}")
    except Exception as e:
        print(f"Unexpected error writing to CSV: {e}")


def print_results(results: List[Dict[str, Any]]) -> None:
    """
    Print results to stdout in a formatted table.
    
    Args:
        results: List of result dictionaries
    """
    print("\n" + "="*100)
    print("HTTP MONITORING RESULTS")
    print("="*100)
    print(f"{'Timestamp':<20} {'URL':<30} {'Status':<8} {'Time(ms)':<10} {'Error':<20}")
    print("-"*100)
    
    for result in results:
        timestamp = result['timestamp'][:19]  # Truncate for display
        url = result['url'][:28] + '..' if len(result['url']) > 30 else result['url']
        status = result['status_code'] if result['status_code'] else 'N/A'
        response_time = result['response_time_ms'] if result['response_time_ms'] else 'N/A'
        error = result['error'][:18] + '..' if result['error'] and len(result['error']) > 20 else (result['error'] or 'None')
        
        print(f"{timestamp:<20} {url:<30} {status:<8} {response_time:<10} {error:<20}")


def main() -> None:
    """
    Main function to execute HTTP monitoring.
    """
    print(f"Starting HTTP monitoring for {len(URLS)} URLs...")
    print(f"Timeout set to {REQUEST_TIMEOUT} seconds")
    
    results = []
    
    for i, url in enumerate(URLS, 1):
        print(f"[{i}/{len(URLS)}] Checking {url}...", end=" ")
        
        try:
            result = make_request(url)
            results.append(result)
            
            if result['error']:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ {result['status_code']} ({result['response_time_ms']}ms)")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "status_code": None,
                "response_time_ms": None,
                "error": f"Script Error: {str(e)}"
            }
            results.append(error_result)
    
    # Print results to stdout
    print_results(results)
    
    # Write results to CSV
    write_to_csv(results, CSV_FILENAME)
    
    # Summary statistics
    successful_requests = sum(1 for r in results if r['status_code'] and r['error'] is None)
    total_requests = len(results)
    
    print(f"\nSUMMARY:")
    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {total_requests - successful_requests}")
    print(f"Success rate: {(successful_requests/total_requests)*100:.1f}%")


if __name__ == "__main__":
    main()