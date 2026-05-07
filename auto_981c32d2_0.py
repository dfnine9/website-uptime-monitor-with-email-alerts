#!/usr/bin/env python3
"""
URL Status Checker

This module reads a list of URLs from a file and checks their HTTP status codes
and response times. It provides a simple way to monitor website availability
and performance.

The script expects a text file with one URL per line and outputs the status
code and response time for each URL to stdout.

Usage:
    python script.py

Requirements:
    - urls.txt file in the same directory with one URL per line
    - httpx library for HTTP requests
"""

import time
import sys
from urllib.parse import urlparse
try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    sys.exit(1)


def validate_url(url):
    """Validate if the URL has a proper scheme."""
    parsed = urlparse(url)
    if not parsed.scheme:
        return f"http://{url}"
    return url


def check_url_status(url, timeout=10):
    """
    Check the HTTP status code and response time for a given URL.
    
    Args:
        url (str): The URL to check
        timeout (int): Request timeout in seconds
        
    Returns:
        tuple: (status_code, response_time_ms, error_message)
    """
    try:
        start_time = time.time()
        
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            
        end_time = time.time()
        response_time_ms = round((end_time - start_time) * 1000, 2)
        
        return response.status_code, response_time_ms, None
        
    except httpx.TimeoutException:
        return None, None, "Timeout"
    except httpx.RequestError as e:
        return None, None, f"Request Error: {str(e)}"
    except Exception as e:
        return None, None, f"Unexpected Error: {str(e)}"


def read_urls_from_file(filename="urls.txt"):
    """
    Read URLs from a text file.
    
    Args:
        filename (str): Path to the file containing URLs
        
    Returns:
        list: List of URLs
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        print("Please create a 'urls.txt' file with one URL per line.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        sys.exit(1)


def main():
    """Main function to execute the URL status checking."""
    print("URL Status Checker")
    print("=" * 50)
    
    urls = read_urls_from_file()
    
    if not urls:
        print("No URLs found in the file.")
        return
    
    print(f"Checking {len(urls)} URLs...\n")
    
    results = []
    
    for i, url in enumerate(urls, 1):
        # Validate and format URL
        formatted_url = validate_url(url)
        
        print(f"[{i}/{len(urls)}] Checking: {formatted_url}")
        
        status_code, response_time, error = check_url_status(formatted_url)
        
        if error:
            print(f"  ❌ Error: {error}")
            results.append((formatted_url, "Error", error, None))
        else:
            status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"
            print(f"  {status_emoji} Status: {status_code} | Response Time: {response_time}ms")
            results.append((formatted_url, status_code, None, response_time))
        
        print()
    
    # Summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    successful = sum(1 for r in results if isinstance(r[1], int) and 200 <= r[1] < 300)
    total = len(results)
    
    print(f"Total URLs checked: {total}")
    print(f"Successful (2xx): {successful}")
    print(f"Failed/Errors: {total - successful}")
    
    if results:
        successful_times = [r[3] for r in results if r[3] is not None]
        if successful_times:
            avg_response_time = sum(successful_times) / len(successful_times)
            print(f"Average response time: {avg_response_time:.2f}ms")


if __name__ == "__main__":
    main()