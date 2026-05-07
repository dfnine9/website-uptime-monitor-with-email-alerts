"""
URL Response Time Monitor

This script pings a list of URLs, measures their response times, and logs the results
to a CSV file with timestamps. It uses the httpx library for HTTP requests and includes
comprehensive error handling.

Features:
- Measures response time for multiple URLs
- Logs results to CSV with timestamps
- Handles network errors and timeouts gracefully
- Prints real-time results to stdout
- Self-contained with minimal dependencies

Usage: python script.py
"""

import csv
import datetime
import sys
import time
from typing import List, Tuple

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


def ping_url(url: str, timeout: int = 10) -> Tuple[str, float, int, str]:
    """
    Ping a URL and measure response time.
    
    Args:
        url: URL to ping
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (url, response_time_ms, status_code, status_message)
    """
    try:
        start_time = time.time()
        
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, follow_redirects=True)
            
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        return url, response_time_ms, response.status_code, "Success"
        
    except httpx.TimeoutException:
        return url, 0.0, 0, "Timeout"
    except httpx.ConnectError:
        return url, 0.0, 0, "Connection Error"
    except httpx.RequestError as e:
        return url, 0.0, 0, f"Request Error: {str(e)}"
    except Exception as e:
        return url, 0.0, 0, f"Unknown Error: {str(e)}"


def ping_urls(urls: List[str], csv_filename: str = "url_monitor.csv") -> None:
    """
    Ping multiple URLs and log results to CSV.
    
    Args:
        urls: List of URLs to ping
        csv_filename: Output CSV filename
    """
    # CSV headers
    headers = ["timestamp", "url", "response_time_ms", "status_code", "status_message"]
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            print(f"Starting URL monitoring - logging to {csv_filename}")
            print("-" * 80)
            print(f"{'URL':<40} {'Time(ms)':<12} {'Status':<8} {'Message'}")
            print("-" * 80)
            
            for url in urls:
                timestamp = datetime.datetime.now().isoformat()
                url_result, response_time, status_code, status_msg = ping_url(url)
                
                # Write to CSV
                writer.writerow([timestamp, url_result, response_time, status_code, status_msg])
                
                # Print to stdout
                print(f"{url_result:<40} {response_time:<12.2f} {status_code:<8} {status_msg}")
                
                # Flush CSV buffer
                csvfile.flush()
                
    except IOError as e:
        print(f"Error writing to CSV file: {e}")
        sys.exit(1)


def main():
    """Main function to run the URL monitor."""
    # List of URLs to monitor
    urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.python.org",
        "https://httpbin.org/status/200",
        "https://httpbin.org/delay/2",
        "https://nonexistent-domain-12345.com"  # This will fail for testing
    ]
    
    try:
        ping_urls(urls)
        print("-" * 80)
        print("URL monitoring completed. Results saved to url_monitor.csv")
        
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()