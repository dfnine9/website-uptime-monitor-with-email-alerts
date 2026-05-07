#!/usr/bin/env python3
"""
URL Ping Monitor Script

This script monitors a predefined list of URLs by sending HTTP requests and collecting
response metrics including HTTP status codes, response times, and timestamps.
The collected data is stored in a structured format with comprehensive error handling
for timeouts and connection failures.

Features:
- Pings multiple URLs with configurable timeout
- Collects HTTP status codes, response times (ms), and timestamps
- Handles network errors, timeouts, and connection failures gracefully
- Outputs results in JSON format to stdout
- Uses only standard library + requests for minimal dependencies

Usage: python script.py
"""

import requests
import time
import json
from datetime import datetime
from typing import List, Dict, Any


def ping_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Ping a single URL and collect response metrics.
    
    Args:
        url: The URL to ping
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing response metrics
    """
    result = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'status_code': None,
        'response_time_ms': None,
        'error': None,
        'success': False
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        
        result['status_code'] = response.status_code
        result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        result['success'] = True
        
    except requests.exceptions.Timeout:
        result['error'] = f'Request timeout after {timeout} seconds'
    except requests.exceptions.ConnectionError:
        result['error'] = 'Connection failed - unable to reach host'
    except requests.exceptions.HTTPError as e:
        result['error'] = f'HTTP error: {str(e)}'
    except requests.exceptions.RequestException as e:
        result['error'] = f'Request failed: {str(e)}'
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
    
    return result


def ping_urls(urls: List[str], timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Ping multiple URLs and collect response metrics for each.
    
    Args:
        urls: List of URLs to ping
        timeout: Request timeout in seconds
        
    Returns:
        List of dictionaries containing response metrics for each URL
    """
    results = []
    
    for url in urls:
        print(f"Pinging {url}...")
        result = ping_url(url, timeout)
        results.append(result)
        
        # Print individual result
        if result['success']:
            print(f"  ✓ {result['status_code']} - {result['response_time_ms']}ms")
        else:
            print(f"  ✗ {result['error']}")
    
    return results


def main():
    """Main function to execute the URL ping monitoring."""
    
    # Predefined list of URLs to monitor
    urls_to_ping = [
        'https://www.google.com',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://httpstat.us/200',
        'https://httpstat.us/404',
        'https://httpstat.us/500',
        'https://this-domain-does-not-exist-12345.com',
        'https://httpstat.us/200?sleep=5000'  # Slow response for timeout testing
    ]
    
    print("URL Ping Monitor Starting...")
    print(f"Monitoring {len(urls_to_ping)} URLs")
    print("-" * 50)
    
    try:
        # Ping all URLs with 5-second timeout
        results = ping_urls(urls_to_ping, timeout=5)
        
        print("-" * 50)
        print("Summary Results (JSON):")
        print(json.dumps(results, indent=2))
        
        # Calculate summary statistics
        successful_pings = [r for r in results if r['success']]
        failed_pings = [r for r in results if not r['success']]
        
        print("-" * 50)
        print(f"Total URLs: {len(results)}")
        print(f"Successful: {len(successful_pings)}")
        print(f"Failed: {len(failed_pings)}")
        
        if successful_pings:
            avg_response_time = sum(r['response_time_ms'] for r in successful_pings) / len(successful_pings)
            print(f"Average response time: {avg_response_time:.2f}ms")
            
        if failed_pings:
            print("\nFailed URLs:")
            for failed in failed_pings:
                print(f"  - {failed['url']}: {failed['error']}")
                
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
    except Exception as e:
        print(f"Unexpected error in main execution: {str(e)}")


if __name__ == "__main__":
    main()