#!/usr/bin/env python3
"""
URL Health Check Monitor

This script reads a list of URLs from a configuration file, performs HTTP requests
to check their status codes and response times, and outputs the results to both
stdout and a structured JSON file.

Features:
- Reads URLs from config.json file
- Checks HTTP status codes and response times
- Handles timeouts and connection errors
- Outputs results to results.json
- Prints summary to stdout

Usage:
    python script.py

Configuration file format (config.json):
{
    "urls": [
        "https://example.com",
        "https://google.com"
    ],
    "timeout": 10
}
"""

import json
import time
import sys
from urllib.parse import urlparse
from datetime import datetime

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


def load_config(config_file="config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        print("Creating default config file...")
        default_config = {
            "urls": [
                "https://httpbin.org/status/200",
                "https://httpbin.org/status/404",
                "https://httpbin.org/delay/2"
            ],
            "timeout": 10
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"Default config created at '{config_file}'. Please edit and run again.")
        return default_config
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def check_url(url, timeout=10):
    """Check a single URL and return status info."""
    result = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "status_code": None,
        "response_time_ms": None,
        "error": None,
        "success": False
    }
    
    try:
        start_time = time.time()
        
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, follow_redirects=True)
            
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        result.update({
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "success": 200 <= response.status_code < 300
        })
        
    except httpx.TimeoutException:
        result["error"] = f"Request timed out after {timeout} seconds"
    except httpx.ConnectError:
        result["error"] = "Connection failed"
    except httpx.InvalidURL:
        result["error"] = "Invalid URL format"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
    
    return result


def main():
    """Main execution function."""
    print("URL Health Check Monitor")
    print("=" * 40)
    
    # Load configuration
    config = load_config()
    urls = config.get("urls", [])
    timeout = config.get("timeout", 10)
    
    if not urls:
        print("Error: No URLs found in configuration.")
        sys.exit(1)
    
    print(f"Checking {len(urls)} URLs with {timeout}s timeout...")
    print()
    
    results = []
    successful_checks = 0
    
    # Check each URL
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Checking: {url}")
        
        result = check_url(url, timeout)
        results.append(result)
        
        if result["success"]:
            successful_checks += 1
            print(f"  ✓ Status: {result['status_code']} | Time: {result['response_time_ms']}ms")
        else:
            print(f"  ✗ Error: {result['error'] or f'HTTP {result['status_code']}'}")
        print()
    
    # Save results to JSON file
    output_file = "results.json"
    output_data = {
        "check_timestamp": datetime.now().isoformat(),
        "total_urls": len(urls),
        "successful_checks": successful_checks,
        "failed_checks": len(urls) - successful_checks,
        "results": results
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")
    
    # Print summary
    print("\nSummary:")
    print(f"Total URLs: {len(urls)}")
    print(f"Successful: {successful_checks}")
    print(f"Failed: {len(urls) - successful_checks}")
    print(f"Success Rate: {(successful_checks / len(urls) * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if successful_checks == len(urls) else 1)


if __name__ == "__main__":
    main()