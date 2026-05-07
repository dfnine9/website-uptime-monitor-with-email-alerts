#!/usr/bin/env python3
"""
Website Monitor Script

This script reads URLs from a config.json file and monitors their availability
by making HTTP requests with timeout handling. It logs response status codes,
response times, and errors to a timestamped CSV file while also printing
results to stdout.

Features:
- Configurable URLs via config.json
- 10-second timeout handling
- CSV logging with timestamps
- Error handling for connection failures
- Self-contained with minimal dependencies

Usage: python script.py
"""

import json
import csv
import time
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import httpx


def load_config():
    """Load URLs from config.json file."""
    config_file = Path('config.json')
    
    if not config_file.exists():
        # Create sample config if it doesn't exist
        sample_config = {
            "urls": [
                "https://httpbin.org/delay/1",
                "https://httpbin.org/status/200",
                "https://httpbin.org/status/404"
            ]
        }
        with open(config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"Created sample {config_file}. Please edit and re-run.")
        return None
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('urls', [])
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading config.json: {e}")
        return None


def create_csv_writer():
    """Create CSV file with timestamp and return writer."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'website_monitor_{timestamp}.csv'
    
    csv_file = open(csv_filename, 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms', 'error'])
    
    print(f"Logging to: {csv_filename}")
    return writer, csv_file


def check_url(client, url):
    """Check a single URL and return results."""
    start_time = time.time()
    timestamp = datetime.now().isoformat()
    
    try:
        response = client.get(url, timeout=10.0)
        response_time = (time.time() - start_time) * 1000
        
        return {
            'timestamp': timestamp,
            'url': url,
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2),
            'error': ''
        }
        
    except httpx.TimeoutException:
        response_time = (time.time() - start_time) * 1000
        return {
            'timestamp': timestamp,
            'url': url,
            'status_code': 'TIMEOUT',
            'response_time_ms': round(response_time, 2),
            'error': 'Request timeout (>10s)'
        }
        
    except httpx.ConnectError as e:
        response_time = (time.time() - start_time) * 1000
        return {
            'timestamp': timestamp,
            'url': url,
            'status_code': 'CONNECTION_ERROR',
            'response_time_ms': round(response_time, 2),
            'error': f'Connection failed: {str(e)}'
        }
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            'timestamp': timestamp,
            'url': url,
            'status_code': 'ERROR',
            'response_time_ms': round(response_time, 2),
            'error': f'Unexpected error: {str(e)}'
        }


def main():
    """Main execution function."""
    print("Website Monitor Starting...")
    
    # Load URLs from config
    urls = load_config()
    if not urls:
        sys.exit(1)
    
    print(f"Monitoring {len(urls)} URLs...")
    
    # Create CSV writer
    try:
        csv_writer, csv_file = create_csv_writer()
    except Exception as e:
        print(f"Error creating CSV file: {e}")
        sys.exit(1)
    
    # Create HTTP client
    with httpx.Client() as client:
        try:
            for url in urls:
                print(f"\nChecking: {url}")
                
                result = check_url(client, url)
                
                # Write to CSV
                csv_writer.writerow([
                    result['timestamp'],
                    result['url'],
                    result['status_code'],
                    result['response_time_ms'],
                    result['error']
                ])
                
                # Print to stdout
                if result['error']:
                    print(f"  Status: {result['status_code']} | "
                          f"Time: {result['response_time_ms']}ms | "
                          f"Error: {result['error']}")
                else:
                    print(f"  Status: {result['status_code']} | "
                          f"Time: {result['response_time_ms']}ms | "
                          f"OK")
                
        except KeyboardInterrupt:
            print("\n\nMonitoring interrupted by user.")
        except Exception as e:
            print(f"\nUnexpected error during monitoring: {e}")
        finally:
            csv_file.close()
            print(f"\nMonitoring complete. Results saved to CSV.")


if __name__ == "__main__":
    main()