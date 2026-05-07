#!/usr/bin/env python3
"""
URL Health Monitor

This script reads URLs from a JSON configuration file and performs comprehensive
health checks including HTTP status codes, response times, and SSL certificate
validation. It uses the httpx library for HTTP requests and provides detailed
error handling for various failure scenarios.

Usage: python script.py

The script expects a 'config.json' file in the same directory with the following format:
{
    "urls": [
        "https://example.com",
        "https://api.example.com/health",
        "http://insecure-site.com"
    ],
    "timeout": 10
}
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class URLHealthChecker:
    """Performs health checks on URLs including status, response time, and SSL validation."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout, verify=True)
    
    def check_url(self, url: str) -> Dict[str, Any]:
        """
        Check a single URL for health metrics.
        
        Args:
            url: The URL to check
            
        Returns:
            Dictionary containing check results
        """
        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status_code": None,
            "response_time_ms": None,
            "ssl_valid": None,
            "error": None,
            "success": False
        }
        
        start_time = time.time()
        
        try:
            response = self.client.get(url)
            response_time = (time.time() - start_time) * 1000
            
            result.update({
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "ssl_valid": url.startswith("https://"),
                "success": True
            })
            
        except httpx.TimeoutException:
            result["error"] = f"Request timeout after {self.timeout}s"
        except httpx.ConnectTimeout:
            result["error"] = "Connection timeout"
        except httpx.ReadTimeout:
            result["error"] = "Read timeout"
        except httpx.SSLError as e:
            result["error"] = f"SSL error: {str(e)}"
            result["ssl_valid"] = False
        except httpx.ConnectError:
            result["error"] = "Connection failed"
        except httpx.InvalidURL:
            result["error"] = "Invalid URL format"
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
        
        if not result["success"] and result["response_time_ms"] is None:
            result["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        return result
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        SystemExit: If config file is not found or invalid
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        if "urls" not in config:
            raise ValueError("Config must contain 'urls' field")
        
        if not isinstance(config["urls"], list):
            raise ValueError("'urls' must be a list")
        
        if not config["urls"]:
            raise ValueError("'urls' list cannot be empty")
        
        # Set default timeout if not specified
        config.setdefault("timeout", 10)
        
        return config
        
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found")
        print("Please create a config.json file with the following format:")
        print('{"urls": ["https://example.com"], "timeout": 10}')
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Configuration validation failed: {e}")
        sys.exit(1)


def print_results(results: List[Dict[str, Any]]):
    """
    Print formatted results to stdout.
    
    Args:
        results: List of URL check results
    """
    print("\n" + "="*80)
    print(f"URL Health Check Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    for result in results:
        status_icon = "✓" if result["success"] else "✗"
        
        print(f"\n{status_icon} {result['url']}")
        print(f"   Status Code: {result['status_code'] or 'N/A'}")
        print(f"   Response Time: {result['response_time_ms']}ms")
        
        if result['url'].startswith('https://'):
            ssl_status = "Valid" if result.get('ssl_valid') else "Invalid"
            print(f"   SSL Certificate: {ssl_status}")
        
        if result["error"]:
            print(f"   Error: {result['error']}")
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\n" + "-"*80)
    print(f"Summary: {successful}/{total} URLs successful")
    
    if successful < total:
        print(f"Failed URLs: {total - successful}")


def main():
    """Main execution function."""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize checker
        checker = URLHealthChecker(timeout=config["timeout"])
        
        # Check all URLs
        results = []
        for url in config["urls"]:
            result = checker.check_url(url)
            results.append(result)
        
        # Print results
        print_results(results)
        
        # Close resources
        checker.close()
        
        # Exit with appropriate code
        failed_count = sum(1 for r in results if not r["success"])
        sys.exit(0 if failed_count == 0 else 1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()