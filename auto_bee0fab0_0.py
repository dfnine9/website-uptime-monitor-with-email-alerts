#!/usr/bin/env python3
"""
Website Health Monitor

A self-contained Python script that pings multiple websites and logs their response times
and HTTP status codes to a CSV file. Uses the httpx library for HTTP requests and includes
comprehensive error handling for network timeouts, DNS failures, and connection issues.

The script monitors a predefined list of websites and outputs results both to stdout
and a timestamped CSV file for historical tracking.

Requirements: httpx library (pip install httpx)
Usage: python script.py
"""

import csv
import time
import sys
from datetime import datetime
from typing import List, Tuple, Optional
import asyncio

try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    sys.exit(1)


class WebsiteMonitor:
    """Monitor websites for response times and status codes."""
    
    def __init__(self, timeout: int = 10):
        """Initialize monitor with configurable timeout."""
        self.timeout = timeout
        self.websites = [
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://python.org",
            "https://httpbin.org/delay/2"
        ]
    
    async def ping_website(self, url: str) -> Tuple[str, Optional[int], Optional[float], str]:
        """
        Ping a single website and return status information.
        
        Args:
            url: Website URL to ping
            
        Returns:
            Tuple of (url, status_code, response_time, status_message)
        """
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response_time = round((time.time() - start_time) * 1000, 2)
                
                return (url, response.status_code, response_time, "OK")
                
        except httpx.TimeoutException:
            response_time = round((time.time() - start_time) * 1000, 2)
            return (url, None, response_time, "TIMEOUT")
            
        except httpx.ConnectError:
            response_time = round((time.time() - start_time) * 1000, 2)
            return (url, None, response_time, "CONNECTION_ERROR")
            
        except httpx.DNSError:
            response_time = round((time.time() - start_time) * 1000, 2)
            return (url, None, response_time, "DNS_ERROR")
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            return (url, None, response_time, f"ERROR: {str(e)[:50]}")
    
    async def monitor_websites(self) -> List[Tuple]:
        """Monitor all websites concurrently."""
        tasks = [self.ping_website(url) for url in self.websites]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that weren't caught in ping_website
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                url = self.websites[i]
                processed_results.append((url, None, None, f"EXCEPTION: {str(result)[:50]}"))
            else:
                processed_results.append(result)
                
        return processed_results
    
    def write_to_csv(self, results: List[Tuple], filename: str):
        """Write results to CSV file with proper headers."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['timestamp', 'url', 'status_code', 'response_time_ms', 'status'])
                
                # Write data
                timestamp = datetime.now().isoformat()
                for url, status_code, response_time, status in results:
                    writer.writerow([timestamp, url, status_code, response_time, status])
                    
            print(f"✓ Results saved to {filename}")
            
        except PermissionError:
            print(f"✗ Permission denied writing to {filename}")
        except Exception as e:
            print(f"✗ Error writing CSV file: {e}")
    
    def print_results(self, results: List[Tuple]):
        """Print formatted results to stdout."""
        print("\n" + "="*80)
        print(f"Website Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        print(f"{'URL':<30} {'Status':<8} {'Time(ms)':<10} {'Message':<20}")
        print("-"*80)
        
        for url, status_code, response_time, status in results:
            # Truncate URL for display
            display_url = url[:27] + "..." if len(url) > 30 else url
            
            # Format status code
            status_display = str(status_code) if status_code else "N/A"
            
            # Format response time
            time_display = f"{response_time:.1f}" if response_time else "N/A"
            
            # Color coding for status
            if status == "OK" and status_code and 200 <= status_code < 300:
                status_indicator = "✓"
            elif status == "OK" and status_code and 300 <= status_code < 400:
                status_indicator = "→"
            else:
                status_indicator = "✗"
            
            print(f"{display_url:<30} {status_display:<8} {time_display:<10} {status_indicator} {status}")


async def main():
    """Main execution function."""
    try:
        print("Starting website health monitoring...")
        
        # Initialize monitor
        monitor = WebsiteMonitor(timeout=10)
        
        # Run monitoring
        results = await monitor.monitor_websites()
        
        # Output results
        monitor.print_results(results)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"website_health_{timestamp}.csv"
        
        # Save to CSV
        monitor.write_to_csv(results, csv_filename)
        
        # Summary statistics
        total_sites = len(results)
        successful = len([r for r in results if r[3] == "OK" and r[1] and 200 <= r[1] < 400])
        
        print(f"\nSummary: {successful}/{total_sites} sites responding normally")
        
    except KeyboardInterrupt:
        print("\n✗ Monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version for asyncio compatibility
    if sys.version_info < (3, 7):
        print("Error: This script requires Python 3.7 or higher")
        sys.exit(1)
    
    # Run the async main function
    asyncio.run(main())