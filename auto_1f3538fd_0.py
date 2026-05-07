#!/usr/bin/env python3
"""
Website Status Monitor

This module sends HTTP requests to a list of websites, captures their status codes 
and response times, then logs the results to a JSON file with timestamps. It uses 
httpx for HTTP requests and includes comprehensive error handling.

Usage: python script.py
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any
import asyncio
import httpx


class WebsiteMonitor:
    """Monitor website availability and performance."""
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.results: List[Dict[str, Any]] = []
    
    async def check_website(self, client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        """Check a single website and return status information."""
        start_time = time.time()
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'response_time_ms': None,
            'error': None
        }
        
        try:
            response = await client.get(url, follow_redirects=True)
            response_time = (time.time() - start_time) * 1000
            
            result.update({
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2)
            })
            
            print(f"✓ {url} - Status: {response.status_code}, Time: {response_time:.2f}ms")
            
        except httpx.TimeoutException:
            result['error'] = 'Request timeout'
            print(f"✗ {url} - Timeout after {self.timeout}s")
            
        except httpx.ConnectError:
            result['error'] = 'Connection failed'
            print(f"✗ {url} - Connection failed")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"✗ {url} - Error: {e}")
        
        return result
    
    async def monitor_websites(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Monitor multiple websites concurrently."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [self.check_website(client, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = 'website_status.json'):
        """Save results to JSON file."""
        try:
            # Try to load existing data
            try:
                with open(filename, 'r') as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []
            
            # Append new results
            existing_data.extend(results)
            
            # Save updated data
            with open(filename, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print(f"\n📊 Results saved to {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print a summary of the monitoring results."""
        total = len(results)
        successful = sum(1 for r in results if r['status_code'] and 200 <= r['status_code'] < 300)
        failed = total - successful
        
        print(f"\n📈 Summary:")
        print(f"   Total websites: {total}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        
        if successful > 0:
            response_times = [r['response_time_ms'] for r in results if r['response_time_ms']]
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                print(f"   Average response time: {avg_time:.2f}ms")


async def main():
    """Main function to run the website monitor."""
    # List of websites to monitor
    websites = [
        'https://www.google.com',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://www.reddit.com',
        'https://www.wikipedia.org',
        'https://httpbin.org/delay/2',  # Test slow response
        'https://httpstat.us/500',      # Test error status
        'https://nonexistent-site-12345.com'  # Test connection error
    ]
    
    print("🔍 Starting website monitoring...")
    print(f"Checking {len(websites)} websites...\n")
    
    monitor = WebsiteMonitor(timeout=10.0)
    
    try:
        results = await monitor.monitor_websites(websites)
        monitor.save_results(results)
        monitor.print_summary(results)
        
    except KeyboardInterrupt:
        print("\n⏸️  Monitoring interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == '__main__':
    asyncio.run(main())