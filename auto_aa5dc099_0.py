"""
URL Monitor Script

This script reads URLs from a JSON configuration file, makes HTTP requests to each URL,
measures response times and status codes, and logs the results with timestamps to a JSON file.

The script performs health checks on web services by:
- Reading URLs from 'config.json'
- Making HTTP requests with timeout handling
- Measuring response times in milliseconds
- Logging results with ISO timestamps to 'results.json'
- Printing results to stdout for monitoring

Dependencies: httpx (for async HTTP requests)
Usage: python script.py
"""

import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)


class URLMonitor:
    def __init__(self, config_file="config.json", results_file="results.json"):
        self.config_file = config_file
        self.results_file = results_file
        self.timeout = 10.0
        
    def load_config(self):
        """Load URLs from JSON config file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('urls', [])
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Creating default...")
            default_config = {
                "urls": [
                    "https://httpbin.org/status/200",
                    "https://httpbin.org/delay/2",
                    "https://httpbin.org/status/404"
                ]
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config['urls']
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return []
    
    async def check_url(self, session, url):
        """Check a single URL and return results."""
        start_time = time.time()
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        try:
            response = await session.get(url, timeout=self.timeout)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'timestamp': timestamp,
                'success': True,
                'error': None
            }
            
            print(f"✓ {url} - Status: {response.status_code}, Time: {response_time}ms")
            
        except asyncio.TimeoutError:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'url': url,
                'status_code': None,
                'response_time_ms': response_time,
                'timestamp': timestamp,
                'success': False,
                'error': 'Timeout'
            }
            print(f"✗ {url} - Timeout after {response_time}ms")
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'url': url,
                'status_code': None,
                'response_time_ms': response_time,
                'timestamp': timestamp,
                'success': False,
                'error': str(e)
            }
            print(f"✗ {url} - Error: {str(e)}")
        
        return result
    
    async def check_all_urls(self, urls):
        """Check all URLs concurrently."""
        async with httpx.AsyncClient() as session:
            tasks = [self.check_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
        return results
    
    def save_results(self, results):
        """Save results to JSON file."""
        try:
            # Load existing results
            existing_results = []
            if Path(self.results_file).exists():
                with open(self.results_file, 'r') as f:
                    existing_results = json.load(f)
            
            # Append new results
            existing_results.extend(results)
            
            # Save back to file
            with open(self.results_file, 'w') as f:
                json.dump(existing_results, f, indent=2)
                
            print(f"\nResults saved to {self.results_file}")
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    async def run(self):
        """Main execution method."""
        print("URL Monitor Starting...")
        
        # Load configuration
        urls = self.load_config()
        if not urls:
            print("No URLs to check. Exiting.")
            return
        
        print(f"Checking {len(urls)} URLs...")
        
        # Check all URLs
        results = await self.check_all_urls(urls)
        
        # Save results
        self.save_results(results)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        print(f"\nSummary: {successful}/{len(results)} URLs successful")


async def main():
    """Main entry point."""
    monitor = URLMonitor()
    await monitor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)