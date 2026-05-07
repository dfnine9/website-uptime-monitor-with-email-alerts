#!/usr/bin/env python3
"""
URL Response Time Monitor

This module reads URLs from a configuration file, measures HTTP response times,
and logs results to a JSON file. It provides real-time monitoring capabilities
for web service performance tracking.

Features:
- Reads URLs from config.txt (one URL per line)
- Measures response times using httpx
- Logs results with timestamps to response_times.json
- Handles errors gracefully with detailed logging
- Prints real-time results to stdout

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - Standard library modules: json, time, datetime, asyncio
"""

import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    exit(1)


class URLMonitor:
    def __init__(self, config_file: str = "config.txt", log_file: str = "response_times.json"):
        self.config_file = config_file
        self.log_file = log_file
        self.results = []

    def load_urls(self) -> List[str]:
        """Load URLs from configuration file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                print(f"Warning: No URLs found in {self.config_file}")
                return []
                
            print(f"Loaded {len(urls)} URLs from {self.config_file}")
            return urls
        
        except FileNotFoundError:
            print(f"Error: Config file {self.config_file} not found. Creating sample config...")
            self._create_sample_config()
            return []
        except Exception as e:
            print(f"Error reading config file: {e}")
            return []

    def _create_sample_config(self):
        """Create a sample configuration file."""
        sample_urls = [
            "https://httpbin.org/delay/1",
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://api.github.com/zen",
            "https://httpstat.us/200"
        ]
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("# URL Response Time Monitor Configuration\n")
                f.write("# One URL per line, lines starting with # are ignored\n\n")
                for url in sample_urls:
                    f.write(f"{url}\n")
            print(f"Created sample config file: {self.config_file}")
        except Exception as e:
            print(f"Error creating sample config: {e}")

    async def measure_response_time(self, client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        """Measure response time for a single URL."""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            response = await client.get(url, timeout=30.0)
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
            
            result = {
                "timestamp": timestamp,
                "url": url,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": True,
                "error": None
            }
            
            print(f"✓ {url} - {response.status_code} - {response_time}ms")
            
        except httpx.TimeoutException:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            result = {
                "timestamp": timestamp,
                "url": url,
                "status_code": None,
                "response_time_ms": response_time,
                "success": False,
                "error": "Timeout"
            }
            print(f"✗ {url} - TIMEOUT - {response_time}ms")
            
        except Exception as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            result = {
                "timestamp": timestamp,
                "url": url,
                "status_code": None,
                "response_time_ms": response_time,
                "success": False,
                "error": str(e)
            }
            print(f"✗ {url} - ERROR: {e}")
        
        return result

    async def monitor_urls(self, urls: List[str]):
        """Monitor all URLs concurrently."""
        if not urls:
            print("No URLs to monitor.")
            return

        print(f"\nStarting monitoring of {len(urls)} URLs...")
        print("-" * 60)

        async with httpx.AsyncClient() as client:
            tasks = [self.measure_response_time(client, url) for url in urls]
            results = await asyncio.gather(*tasks)
            
            self.results.extend(results)
            
        print("-" * 60)
        self._print_summary()

    def _print_summary(self):
        """Print monitoring summary."""
        if not self.results:
            return
            
        successful = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        avg_time = sum(r['response_time_ms'] for r in self.results) / total
        
        print(f"\nSummary:")
        print(f"Successful requests: {successful}/{total}")
        print(f"Average response time: {avg_time:.2f}ms")
        print(f"Results logged to: {self.log_file}")

    def save_results(self):
        """Save results to JSON log file."""
        if not self.results:
            print("No results to save.")
            return

        try:
            # Load existing data if file exists
            existing_data = []
            if Path(self.log_file).exists():
                try:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: {self.log_file} contains invalid JSON, overwriting...")
                    existing_data = []

            # Append new results
            existing_data.extend(self.results)
            
            # Save to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
            print(f"Results saved to {self.log_file}")
            
        except Exception as e:
            print(f"Error saving results: {e}")

    async def run(self):
        """Main execution method."""
        print("URL Response Time Monitor")
        print("=" * 40)
        
        urls = self.load_urls()
        if urls:
            await self.monitor_urls(urls)
            self.save_results()
        else:
            print("Please add URLs to config.txt and run again.")


async def main():
    """Main entry point."""
    monitor = URLMonitor()
    await monitor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")