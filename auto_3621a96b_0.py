"""
URL Health Check Monitor

A self-contained script that pings multiple URLs, checks their response codes and times,
then logs results to a JSON file with timestamp data. Uses httpx for HTTP requests
and includes comprehensive error handling.

Usage: python script.py
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any
import httpx


def ping_url(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Ping a single URL and return response data.
    
    Args:
        url: URL to ping
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing response data
    """
    try:
        start_time = time.time()
        
        with httpx.Client() as client:
            response = client.get(url, timeout=timeout, follow_redirects=True)
            
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        
        return {
            "url": url,
            "status_code": response.status_code,
            "response_time_ms": response_time,
            "success": True,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "headers": dict(response.headers)
        }
        
    except httpx.TimeoutException:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "success": False,
            "error": "Request timeout",
            "timestamp": datetime.now().isoformat(),
            "headers": None
        }
    except httpx.RequestError as e:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "success": False,
            "error": f"Request error: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "headers": None
        }
    except Exception as e:
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": None,
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "headers": None
        }


def check_urls(urls: List[str], timeout: float = 10.0) -> List[Dict[str, Any]]:
    """
    Check multiple URLs and return results.
    
    Args:
        urls: List of URLs to check
        timeout: Request timeout in seconds
        
    Returns:
        List of dictionaries containing response data
    """
    results = []
    
    for url in urls:
        print(f"Checking {url}...")
        result = ping_url(url, timeout)
        results.append(result)
        
        # Print immediate feedback
        if result["success"]:
            print(f"✓ {url} - Status: {result['status_code']}, Time: {result['response_time_ms']}ms")
        else:
            print(f"✗ {url} - Error: {result['error']}")
    
    return results


def save_results_to_json(results: List[Dict[str, Any]], filename: str = "url_check_results.json") -> None:
    """
    Save results to JSON file with timestamp.
    
    Args:
        results: List of check results
        filename: Output filename
    """
    try:
        output_data = {
            "check_timestamp": datetime.now().isoformat(),
            "total_urls": len(results),
            "successful_checks": sum(1 for r in results if r["success"]),
            "failed_checks": sum(1 for r in results if not r["success"]),
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to {filename}")
        
    except Exception as e:
        print(f"Error saving results to JSON: {e}")


def main():
    """Main function to execute URL health checks."""
    # Default URLs to check - modify as needed
    urls_to_check = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404", 
        "https://httpbin.org/delay/2",
        "https://google.com",
        "https://github.com",
        "https://invalid-url-that-does-not-exist-12345.com"
    ]
    
    print("URL Health Check Monitor")
    print("=" * 40)
    print(f"Checking {len(urls_to_check)} URLs...")
    print()
    
    try:
        # Perform URL checks
        results = check_urls(urls_to_check, timeout=10.0)
        
        # Print summary
        print("\n" + "=" * 40)
        print("SUMMARY")
        print("=" * 40)
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        print(f"Total URLs checked: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        # Save results to JSON
        save_results_to_json(results)
        
        print("\nDetailed results written to url_check_results.json")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error in main execution: {e}")


if __name__ == "__main__":
    main()