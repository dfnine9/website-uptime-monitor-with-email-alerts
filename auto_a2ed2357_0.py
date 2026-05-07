```python
#!/usr/bin/env python3
"""
Website Health Monitor

A self-contained Python script that monitors website health by measuring response times,
status codes, and availability. Results are logged to timestamped JSON files and printed
to stdout with comprehensive error handling.

Features:
- Pings multiple websites concurrently
- Measures response times and captures status codes
- Logs results to timestamped JSON files
- Handles network errors, timeouts, and invalid URLs
- Self-contained with minimal dependencies

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - Standard library modules only
"""

import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class WebsiteMonitor:
    """Monitors website health and logs results."""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.results: List[Dict[str, Any]] = []
    
    async def ping_website(self, url: str) -> Dict[str, Any]:
        """
        Ping a single website and return health metrics.
        
        Args:
            url: Website URL to ping
            
        Returns:
            Dictionary containing response metrics and status
        """
        start_time = time.time()
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'response_time_ms': None,
            'success': False,
            'error': None
        }
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
                result['url'] = url
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            result.update({
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'success': 200 <= response.status_code < 400,
                'headers': dict(response.headers) if response.headers else None
            })
            
        except httpx.TimeoutException:
            result['error'] = f'Timeout after {self.timeout} seconds'
        except httpx.RequestError as e:
            result['error'] = f'Request error: {str(e)}'
        except httpx.HTTPStatusError as e:
            result.update({
                'status_code': e.response.status_code,
                'error': f'HTTP error: {e.response.status_code}'
            })
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
        
        return result
    
    async def ping_websites(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Ping multiple websites concurrently.
        
        Args:
            urls: List of website URLs to ping
            
        Returns:
            List of dictionaries containing response metrics
        """
        if not urls:
            print("Warning: No URLs provided")
            return []
        
        print(f"Pinging {len(urls)} websites...")
        
        # Create tasks for concurrent execution
        tasks = [self.ping_website(url) for url in urls]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions that occurred during execution
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = {
                        'url': urls[i],
                        'timestamp': datetime.now().isoformat(),
                        'status_code': None,
                        'response_time_ms': None,
                        'success': False,
                        'error': f'Task error: {str(result)}'
                    }
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            self.results = processed_results
            return processed_results
            
        except Exception as e:
            print(f"Error during concurrent execution: {e}")
            return []
    
    def save_results(self, results: List[Dict[str, Any]]) -> Optional[str]:
        """
        Save results to a timestamped JSON file.
        
        Args:
            results: List of ping results to save
            
        Returns:
            Filename if successful, None if failed
        """
        if not results:
            print("No results to save")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"website_health_{timestamp}.json"
            filepath = Path(filename)
            
            output_data = {
                'scan_timestamp': datetime.now().isoformat(),
                'total_websites': len(results),
                'successful_pings': sum(1 for r in results if r['success']),
                'failed_pings': sum(1 for r in results if not r['success']),
                'results': results
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Results saved to: {filepath}")
            return str(filepath)
            
        except IOError as e:
            print(f"Error saving results to file: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error while saving: {e}")
            return None
    
    def print_results(self, results: List[Dict[str, Any]]) -> None:
        """Print results to stdout in a formatted manner."""
        if not results:
            print("No results to display")
            return
        
        print("\n" + "="*80)
        print("WEBSITE HEALTH MONITOR RESULTS")
        print("="*80)
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        print(f"Total websites checked: {total}")
        print(f"Successful responses: {successful}")
        print(f"Failed responses: {total - successful}")
        print(f"Success rate: {(successful/total)*100:.1f}%")
        print("\n" + "-"*80)
        
        for result in results:
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"\n{status} - {result['url']}")
            print(f"  Status Code: {result['status_code'] or 'N/A'}")
            print(f"  Response Time: {result['response_time_ms'] or 'N/A'} ms")
            print(f"  Timestamp: {result['timestamp']}")
            
            if result['error']:
                print(f"  Error: {result['error']}")


async def main():
    """Main function to run the website health monitor."""
    # Default list of websites to monitor
    websites = [
        'https://google.com',
        'https://github.com',
        'https://stackoverflow.com',
        'https://python.org',
        'https://httpbin.org/status/200',
        'https://httpbin.org/status/404',
        'https://httpbin.org/delay/5',
        'https://nonexistent-website-12345.com',
        'invalid-url',
    ]
    
    print("Website Health Monitor Starting...")
    print(f"Monitoring {len(websites)} websites with {10}s timeout")
    
    try:
        # Initialize monitor
        monitor = WebsiteMonitor(timeout=10)
        
        # Ping all websites