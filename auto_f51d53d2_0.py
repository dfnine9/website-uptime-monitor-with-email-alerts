"""
URL Monitor Script

This script reads URLs from a config.json file, makes HTTP requests to each URL
with timeout handling, and logs the results (timestamp, URL, status code, and 
response time) to a CSV file. Includes comprehensive error handling for network
issues, file operations, and malformed configurations.

Dependencies: httpx (for HTTP requests)
Usage: python script.py

The script expects a config.json file in the same directory with the following format:
{
    "urls": ["http://example.com", "https://google.com"],
    "timeout": 10,
    "output_file": "url_monitor.csv"
}
"""

import json
import csv
import sys
from datetime import datetime
from pathlib import Path
import time

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        if 'urls' not in config:
            raise ValueError("Configuration must include 'urls' field")
        
        # Set defaults
        config.setdefault('timeout', 10)
        config.setdefault('output_file', 'url_monitor.csv')
        
        return config
    
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)


def initialize_csv(output_file):
    """Initialize CSV file with headers if it doesn't exist."""
    try:
        csv_path = Path(output_file)
        file_exists = csv_path.exists()
        
        with open(output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms', 'error'])
        
        return True
    
    except Exception as e:
        print(f"Error initializing CSV file: {e}")
        return False


def check_url(url, timeout):
    """Make HTTP request to URL and return results."""
    start_time = time.time()
    
    try:
        with httpx.Client() as client:
            response = client.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'error': ''
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
            'error': f"Unexpected error: {str(e)}"
        }


def log_result(output_file, result):
    """Log result to CSV file."""
    try:
        with open(output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                result['timestamp'],
                result['url'],
                result['status_code'],
                result['response_time_ms'],
                result['error']
            ])
        return True
    
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        return False


def main():
    """Main execution function."""
    print("URL Monitor Script Starting...")
    
    # Load configuration
    config = load_config()
    
    # Initialize CSV file
    if not initialize_csv(config['output_file']):
        sys.exit(1)
    
    print(f"Monitoring {len(config['urls'])} URLs...")
    print(f"Timeout: {config['timeout']} seconds")
    print(f"Output file: {config['output_file']}")
    print("-" * 50)
    
    # Process each URL
    for url in config['urls']:
        print(f"Checking: {url}")
        
        # Make request
        result = check_url(url, config['timeout'])
        
        # Log to CSV
        if log_result(config['output_file'], result):
            # Print result to stdout
            status_display = result['status_code']
            if result['error']:
                print(f"  Status: {status_display} - {result['error']}")
            else:
                print(f"  Status: {status_display} - {result['response_time_ms']}ms")
        else:
            print(f"  Failed to log result for {url}")
    
    print("-" * 50)
    print(f"URL monitoring complete. Results saved to {config['output_file']}")


if __name__ == "__main__":
    main()