```python
#!/usr/bin/env python3
"""
URL Performance Monitor and Metrics Extractor

A comprehensive web monitoring tool that pings multiple URLs, measures response times,
extracts basic page metrics (status codes, content length, response headers), and
compiles the results into a formatted report.

Features:
- Concurrent URL testing for improved performance
- Response time measurement with timeout handling
- Basic page metrics extraction (status, size, server info)
- Error handling for network failures and timeouts
- Formatted console output with summary statistics

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - Standard library modules (time, statistics, concurrent.futures)
"""

import time
import statistics
import concurrent.futures
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    exit(1)


@dataclass
class URLMetrics:
    """Data class to store metrics for a single URL"""
    url: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    content_length: Optional[int] = None
    server: Optional[str] = None
    content_type: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


class URLMonitor:
    """Main class for monitoring URLs and extracting metrics"""
    
    def __init__(self, timeout: int = 10, max_workers: int = 10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)
    
    def ping_url(self, url: str) -> URLMetrics:
        """
        Ping a single URL and extract basic metrics
        
        Args:
            url: The URL to test
            
        Returns:
            URLMetrics object containing the results
        """
        metrics = URLMetrics(url=url, timestamp=datetime.now())
        
        try:
            # Ensure URL has proper scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                metrics.url = url
            
            # Measure response time
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            # Extract metrics
            metrics.response_time = round((end_time - start_time) * 1000, 2)  # Convert to ms
            metrics.status_code = response.status_code
            metrics.content_length = len(response.content) if response.content else 0
            metrics.server = response.headers.get('server', 'Unknown')
            metrics.content_type = response.headers.get('content-type', 'Unknown')
            
        except httpx.TimeoutException:
            metrics.error = f"Timeout after {self.timeout}s"
        except httpx.RequestError as e:
            metrics.error = f"Request error: {str(e)}"
        except Exception as e:
            metrics.error = f"Unexpected error: {str(e)}"
        
        return metrics
    
    def ping_urls(self, urls: List[str]) -> List[URLMetrics]:
        """
        Ping multiple URLs concurrently
        
        Args:
            urls: List of URLs to test
            
        Returns:
            List of URLMetrics objects
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(self.ping_url, url): url for url in urls}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    url = future_to_url[future]
                    error_result = URLMetrics(url=url, error=f"Future error: {str(e)}", timestamp=datetime.now())
                    results.append(error_result)
        
        return results
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()


def format_report(results: List[URLMetrics]) -> str:
    """
    Format the results into a comprehensive report
    
    Args:
        results: List of URLMetrics objects
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("URL PERFORMANCE MONITORING REPORT")
    report.append("=" * 80)
    report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total URLs tested: {len(results)}")
    report.append("")
    
    # Separate successful and failed results
    successful = [r for r in results if r.error is None and r.response_time is not None]
    failed = [r for r in results if r.error is not None]
    
    # Summary statistics
    if successful:
        response_times = [r.response_time for r in successful]
        report.append("SUMMARY STATISTICS")
        report.append("-" * 40)
        report.append(f"Successful requests: {len(successful)}")
        report.append(f"Failed requests: {len(failed)}")
        report.append(f"Success rate: {len(successful)/len(results)*100:.1f}%")
        report.append(f"Average response time: {statistics.mean(response_times):.2f}ms")
        report.append(f"Median response time: {statistics.median(response_times):.2f}ms")
        report.append(f"Min response time: {min(response_times):.2f}ms")
        report.append(f"Max response time: {max(response_times):.2f}ms")
        if len(response_times) > 1:
            report.append(f"Std deviation: {statistics.stdev(response_times):.2f}ms")
        report.append("")
    
    # Detailed results
    report.append("DETAILED RESULTS")
    report.append("-" * 40)
    
    for i, result in enumerate(results, 1):
        report.append(f"{i}. {result.url}")
        if result.error:
            report.append(f"   Status: ERROR - {result.error}")
        else:
            report.append(f"   Status: {result.status_code}")
            report.append(f"   Response Time: {result.response_time}ms")
            report.append(f"   Content Length: {result.content_length:,} bytes")
            report.append(f"   Server: {result.server}")
            report.append(f"   Content Type: {result.content_type}")
        report.append(f"   Timestamp: {result.timestamp.strftime('%H:%M:%S')}")
        report.append("")
    
    # Performance categories
    if successful:
        report.append("PERFORMANCE CATEGORIES")
        report.append("-" * 40)
        fast = [r for r in successful if r.response_time < 200]
        medium = [r for r in successful if 200 <= r.response_time < 1000]
        slow = [r for r in successful if r.response_time >= 1000]
        
        report.append(f"Fast (< 200ms): {len(fast)} URLs")
        for r in fast:
            report.append(f"  - {r.url} ({r.response_time}ms)")
        
        report.append(f"Medium (200-1000ms): {len(medium)} URLs")
        for r in medium:
            report.append(f"  - {r.url} ({r.response_time}ms)")
        
        report.append(f"Slow (> 1000ms): {len(slow)} URLs")
        for r in slow:
            report.append(f"  - {r.url} ({r.response_time}ms