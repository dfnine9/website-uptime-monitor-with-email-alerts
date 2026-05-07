#!/usr/bin/env python3
"""
Website Uptime Monitor

This module monitors website uptime by reading URLs from config.json,
checking HTTP status codes every 5 minutes, and logging results with
timestamps to uptime_log.csv. Designed to run continuously until interrupted.

Requirements:
- config.json with URLs list
- httpx library for HTTP requests
- Standard library modules for JSON, CSV, logging, and scheduling

Usage: python script.py
"""

import json
import csv
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    exit(1)


def load_config() -> List[str]:
    """Load URLs from config.json file."""
    try:
        config_path = Path("config.json")
        if not config_path.exists():
            # Create sample config if it doesn't exist
            sample_config = {
                "urls": [
                    "https://google.com",
                    "https://github.com",
                    "https://stackoverflow.com"
                ]
            }
            with open(config_path, 'w') as f:
                json.dump(sample_config, f, indent=2)
            print(f"Created sample {config_path}. Edit it with your URLs.")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        urls = config.get('urls', [])
        if not urls:
            raise ValueError("No URLs found in config.json")
        
        return urls
    
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        logging.error(f"Config error: {e}")
        raise


def check_url_status(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Check HTTP status code for a given URL."""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            return {
                'url': url,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'status': 'UP' if 200 <= response.status_code < 300 else 'DOWN',
                'error': None
            }
    
    except httpx.TimeoutException:
        return {
            'url': url,
            'status_code': None,
            'response_time': None,
            'status': 'TIMEOUT',
            'error': 'Request timeout'
        }
    
    except httpx.RequestError as e:
        return {
            'url': url,
            'status_code': None,
            'response_time': None,
            'status': 'ERROR',
            'error': str(e)
        }


def log_result(result: Dict[str, Any], csv_file: str = "uptime_log.csv"):
    """Log check result to CSV file."""
    timestamp = datetime.now().isoformat()
    
    # Prepare CSV row
    row = [
        timestamp,
        result['url'],
        result['status_code'] or 'N/A',
        result['response_time'] or 'N/A',
        result['status'],
        result['error'] or ''
    ]
    
    # Check if CSV exists and write header if needed
    csv_path = Path(csv_file)
    write_header = not csv_path.exists()
    
    try:
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if write_header:
                writer.writerow([
                    'timestamp', 'url', 'status_code', 
                    'response_time', 'status', 'error'
                ])
            
            writer.writerow(row)
    
    except IOError as e:
        logging.error(f"Failed to write to CSV: {e}")


def monitor_websites():
    """Main monitoring loop."""
    try:
        urls = load_config()
        print(f"Monitoring {len(urls)} URLs every 5 minutes...")
        print("Press Ctrl+C to stop")
        
        while True:
            print(f"\n--- Check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            for url in urls:
                result = check_url_status(url)
                log_result(result)
                
                # Print to stdout
                status_msg = f"{result['status']} - {url}"
                if result['status_code']:
                    status_msg += f" (HTTP {result['status_code']}"
                    if result['response_time']:
                        status_msg += f", {result['response_time']:.2f}s"
                    status_msg += ")"
                
                if result['error']:
                    status_msg += f" - {result['error']}"
                
                print(status_msg)
            
            # Wait 5 minutes
            print("Waiting 5 minutes for next check...")
            time.sleep(300)  # 5 minutes = 300 seconds
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    
    except Exception as e:
        logging.error(f"Monitoring error: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    monitor_websites()