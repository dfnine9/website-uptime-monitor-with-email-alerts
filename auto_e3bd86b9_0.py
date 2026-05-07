"""
URL Status Checker

This module reads URLs from a configuration file, performs HTTP status checks,
and logs the results with timestamps to a CSV file. It uses httpx for HTTP
requests and handles errors gracefully.

Usage:
    python script.py

Configuration:
    Create a 'urls.txt' file with one URL per line in the same directory.

Output:
    - Results are printed to stdout
    - Detailed logs are saved to 'url_status_log.csv'
"""

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


def read_urls_from_config(config_file: str = "urls.txt") -> List[str]:
    """Read URLs from configuration file."""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Creating example config file: {config_file}")
            with open(config_file, 'w') as f:
                f.write("https://httpbin.org/status/200\n")
                f.write("https://httpbin.org/status/404\n")
                f.write("https://google.com\n")
            print(f"Please edit {config_file} with your URLs and run again.")
            return []
        
        with open(config_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except Exception as e:
        print(f"Error reading config file: {e}")
        return []


def check_url_status(url: str, timeout: int = 10) -> Tuple[str, int, str, float]:
    """Check HTTP status of a URL and return results."""
    try:
        start_time = datetime.now()
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        return url, response.status_code, "OK", response_time
    except httpx.TimeoutException:
        return url, 0, "TIMEOUT", 0.0
    except httpx.ConnectError:
        return url, 0, "CONNECTION_ERROR", 0.0
    except Exception as e:
        return url, 0, f"ERROR: {str(e)}", 0.0


def log_to_csv(results: List[Tuple], csv_file: str = "url_status_log.csv") -> None:
    """Log results to CSV file with timestamps."""
    try:
        fieldnames = ['timestamp', 'url', 'status_code', 'status_message', 'response_time_seconds']
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header if file is empty
            if f.tell() == 0:
                writer.writerow(fieldnames)
            
            timestamp = datetime.now().isoformat()
            for url, status_code, message, response_time in results:
                writer.writerow([timestamp, url, status_code, message, response_time])
        
        print(f"Results logged to: {csv_file}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")


def main():
    """Main execution function."""
    print("URL Status Checker Starting...")
    print("-" * 50)
    
    # Read URLs from config
    urls = read_urls_from_config()
    if not urls:
        print("No URLs to check. Exiting.")
        return
    
    print(f"Checking {len(urls)} URLs...")
    
    # Check each URL
    results = []
    for url in urls:
        print(f"Checking: {url}")
        url_result = check_url_status(url)
        results.append(url_result)
        
        # Print immediate result
        _, status_code, message, response_time = url_result
        if status_code == 0:
            print(f"  ❌ {message}")
        elif 200 <= status_code < 300:
            print(f"  ✅ {status_code} ({response_time:.2f}s)")
        else:
            print(f"  ⚠️  {status_code} ({response_time:.2f}s)")
    
    # Log results to CSV
    print("-" * 50)
    log_to_csv(results)
    
    # Summary
    successful = sum(1 for _, code, _, _ in results if 200 <= code < 300)
    print(f"Summary: {successful}/{len(results)} URLs returned 2xx status codes")


if __name__ == "__main__":
    main()