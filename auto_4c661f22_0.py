#!/usr/bin/env python3
"""
URL Status Checker

This module reads URLs from a configuration file, performs HTTP status checks
on each URL, and logs the results with timestamps to a JSON file. It provides
real-time feedback via stdout and maintains a persistent log of all checks.

Configuration file (urls.txt) should contain one URL per line.
Results are logged to url_status_log.json with timestamps and status codes.

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import json
import time
from datetime import datetime
from pathlib import Path
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


def load_urls_from_config(config_file="urls.txt"):
    """Load URLs from configuration file."""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            # Create sample config file
            sample_urls = [
                "https://httpbin.org/status/200",
                "https://httpbin.org/status/404",
                "https://google.com",
                "https://github.com"
            ]
            config_path.write_text("\n".join(sample_urls))
            print(f"Created sample config file: {config_file}")
        
        with open(config_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        return urls
    except Exception as e:
        print(f"Error loading config file {config_file}: {e}")
        return []


def check_url_status(url, timeout=10):
    """Check HTTP status code for a given URL."""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            return {
                "url": url,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": True,
                "error": None
            }
    except httpx.TimeoutException:
        return {
            "url": url,
            "status_code": None,
            "response_time": None,
            "success": False,
            "error": "Timeout"
        }
    except httpx.RequestError as e:
        return {
            "url": url,
            "status_code": None,
            "response_time": None,
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "url": url,
            "status_code": None,
            "response_time": None,
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def load_existing_log(log_file):
    """Load existing log file or return empty list."""
    try:
        log_path = Path(log_file)
        if log_path.exists():
            with open(log_path, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Warning: Could not load existing log file: {e}")
        return []


def save_results_to_json(results, log_file="url_status_log.json"):
    """Save results to JSON log file."""
    try:
        existing_log = load_existing_log(log_file)
        existing_log.extend(results)
        
        with open(log_file, 'w') as f:
            json.dump(existing_log, f, indent=2)
        
        print(f"Results saved to {log_file}")
    except Exception as e:
        print(f"Error saving results to JSON: {e}")


def main():
    """Main execution function."""
    print("URL Status Checker Starting...")
    print("-" * 50)
    
    # Load URLs from config
    urls = load_urls_from_config()
    if not urls:
        print("No URLs found in config file. Exiting.")
        return
    
    print(f"Loaded {len(urls)} URLs from config")
    
    # Check each URL and collect results
    results = []
    timestamp = datetime.now().isoformat()
    
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Checking: {url}")
        
        result = check_url_status(url)
        result["timestamp"] = timestamp
        result["check_id"] = f"{timestamp}_{i}"
        
        results.append(result)
        
        # Print immediate result
        if result["success"]:
            print(f"  ✓ Status: {result['status_code']} "
                  f"({result['response_time']:.2f}s)")
        else:
            print(f"  ✗ Error: {result['error']}")
        
        # Small delay between requests to be respectful
        time.sleep(0.5)
    
    # Save results to JSON log
    print("\n" + "-" * 50)
    save_results_to_json(results)
    
    # Summary statistics
    successful_checks = sum(1 for r in results if r["success"])
    failed_checks = len(results) - successful_checks
    
    print(f"Check completed: {successful_checks} successful, {failed_checks} failed")
    
    # Display status code summary
    status_codes = {}
    for result in results:
        if result["success"]:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1
    
    if status_codes:
        print("\nStatus Code Summary:")
        for code, count in sorted(status_codes.items()):
            print(f"  {code}: {count} URLs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)