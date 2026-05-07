#!/usr/bin/env python3
"""
URL Response Time Monitor

This script reads a list of URLs from a JSON configuration file, makes HTTP requests
to each URL, measures response times, and logs the results to a CSV file. It handles
errors gracefully and provides real-time feedback to stdout.

The script expects a config.json file with the following format:
{
    "urls": [
        "https://example.com",
        "https://google.com",
        "https://github.com"
    ],
    "output_file": "response_times.csv",
    "timeout": 10
}

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import json
import csv
import time
import sys
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    sys.exit(1)


def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        if 'urls' not in config or not isinstance(config['urls'], list):
            raise ValueError("Config must contain 'urls' list")
        
        # Set defaults
        config.setdefault('output_file', 'response_times.csv')
        config.setdefault('timeout', 10)
        
        return config
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


def create_csv_file(output_file):
    """Create CSV file with headers if it doesn't exist."""
    try:
        file_path = Path(output_file)
        if not file_path.exists():
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms'])
            print(f"Created new CSV file: {output_file}")
        return True
    except Exception as e:
        print(f"Error creating CSV file: {e}")
        return False


def measure_url_response(url, timeout=10):
    """Make HTTP request and measure response time."""
    start_time = time.time()
    
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, follow_redirects=True)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'error': None
            }
    
    except httpx.TimeoutException:
        response_time = (time.time() - start_time) * 1000
        return {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'status_code': 'TIMEOUT',
            'response_time_ms': round(response_time, 2),
            'error': 'Request timeout'
        }
    
    except httpx.RequestError as e:
        response_time = (time.time() - start_time) * 1000
        return {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'status_code': 'ERROR',
            'response_time_ms': round(response_time, 2),
            'error': str(e)
        }
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'status_code': 'ERROR',
            'response_time_ms': round(response_time, 2),
            'error': str(e)
        }


def log_to_csv(result, output_file):
    """Log result to CSV file."""
    try:
        with open(output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                result['timestamp'],
                result['url'],
                result['status_code'],
                result['response_time_ms']
            ])
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False


def main():
    """Main function to orchestrate URL monitoring."""
    print("URL Response Time Monitor Starting...")
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Exiting.")
        sys.exit(1)
    
    urls = config['urls']
    output_file = config['output_file']
    timeout = config['timeout']
    
    print(f"Monitoring {len(urls)} URLs with {timeout}s timeout")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    # Create CSV file
    if not create_csv_file(output_file):
        sys.exit(1)
    
    # Process each URL
    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Testing: {url}")
        
        result = measure_url_response(url, timeout)
        results.append(result)
        
        # Log to CSV
        if log_to_csv(result, output_file):
            # Print result to stdout
            if result['error']:
                print(f"  ❌ {result['status_code']} | {result['response_time_ms']}ms | Error: {result['error']}")
            else:
                status_emoji = "✅" if 200 <= int(result['status_code']) < 300 else "⚠️"
                print(f"  {status_emoji} {result['status_code']} | {result['response_time_ms']}ms")
        else:
            print(f"  ❌ Failed to log result for {url}")
    
    # Summary
    print("-" * 50)
    print("Summary:")
    successful = sum(1 for r in results if not r['error'] and 200 <= int(str(r['status_code'])) < 300)
    print(f"Successful requests: {successful}/{len(results)}")
    print(f"Results logged to: {output_file}")
    
    # Calculate average response time for successful requests
    successful_times = [r['response_time_ms'] for r in results if not r['error'] and 200 <= int(str(r['status_code'])) < 300]
    if successful_times:
        avg_time = sum(successful_times) / len(successful_times)
        print(f"Average response time: {avg_time:.2f}ms")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Monitoring interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)