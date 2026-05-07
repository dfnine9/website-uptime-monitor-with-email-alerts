```python
#!/usr/bin/env python3
"""
URL Monitor and Performance Tracker

This script monitors a configurable list of URLs by making HTTP requests,
recording response times, status codes, and timestamps. All data is stored
in a SQLite database for analysis and historical tracking.

Features:
- Configurable URL list
- Concurrent request processing
- SQLite database storage with proper schema
- Error handling and logging
- Performance metrics collection

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import sqlite3
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)


class URLMonitor:
    def __init__(self, db_path: str = "url_monitor.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self) -> None:
        """Initialize SQLite database with proper schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS url_monitoring (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        status_code INTEGER,
                        response_time REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        error_message TEXT,
                        content_length INTEGER,
                        headers TEXT
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_url_timestamp 
                    ON url_monitoring(url, timestamp)
                """)
                
                conn.commit()
                print(f"Database initialized: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database setup error: {e}")
            raise

    async def check_url(self, session: httpx.AsyncClient, url: str) -> Dict[str, Any]:
        """Check a single URL and return metrics."""
        start_time = time.perf_counter()
        timestamp = datetime.now().isoformat()
        
        try:
            response = await session.get(url, timeout=10.0)
            end_time = time.perf_counter()
            response_time = end_time - start_time
            
            return {
                'url': url,
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': timestamp,
                'error_message': None,
                'content_length': len(response.content) if response.content else 0,
                'headers': str(dict(response.headers))
            }
            
        except httpx.TimeoutException:
            end_time = time.perf_counter()
            response_time = end_time - start_time
            return {
                'url': url,
                'status_code': None,
                'response_time': response_time,
                'timestamp': timestamp,
                'error_message': 'Request timeout',
                'content_length': 0,
                'headers': None
            }
            
        except Exception as e:
            end_time = time.perf_counter()
            response_time = end_time - start_time
            return {
                'url': url,
                'status_code': None,
                'response_time': response_time,
                'timestamp': timestamp,
                'error_message': str(e),
                'content_length': 0,
                'headers': None
            }

    def store_results(self, results: List[Dict[str, Any]]) -> None:
        """Store monitoring results in SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for result in results:
                    cursor.execute("""
                        INSERT INTO url_monitoring 
                        (url, status_code, response_time, timestamp, error_message, content_length, headers)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        result['url'],
                        result['status_code'],
                        result['response_time'],
                        result['timestamp'],
                        result['error_message'],
                        result['content_length'],
                        result['headers']
                    ))
                
                conn.commit()
                print(f"Stored {len(results)} monitoring records")
                
        except sqlite3.Error as e:
            print(f"Database storage error: {e}")
            raise

    async def monitor_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Monitor all URLs concurrently."""
        async with httpx.AsyncClient() as session:
            tasks = [self.check_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and convert to proper results
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    valid_results.append({
                        'url': urls[i],
                        'status_code': None,
                        'response_time': 0.0,
                        'timestamp': datetime.now().isoformat(),
                        'error_message': str(result),
                        'content_length': 0,
                        'headers': None
                    })
                else:
                    valid_results.append(result)
            
            return valid_results

    def print_results(self, results: List[Dict[str, Any]]) -> None:
        """Print monitoring results to stdout."""
        print("\n" + "="*80)
        print("URL MONITORING RESULTS")
        print("="*80)
        
        for result in results:
            status = result['status_code'] or 'ERROR'
            response_time_ms = result['response_time'] * 1000
            
            print(f"\nURL: {result['url']}")
            print(f"Status: {status}")
            print(f"Response Time: {response_time_ms:.2f}ms")
            print(f"Timestamp: {result['timestamp']}")
            
            if result['error_message']:
                print(f"Error: {result['error_message']}")
            elif result['content_length']:
                print(f"Content Length: {result['content_length']} bytes")
        
        print("\n" + "="*80)

    def get_summary_stats(self) -> None:
        """Print summary statistics from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        url,
                        COUNT(*) as total_checks,
                        AVG(response_time) as avg_response_time,
                        MIN(response_time) as min_response_time,
                        MAX(response_time) as max_response_time,
                        SUM(CASE WHEN status_code BETWEEN 200 AND 299 THEN 1 ELSE 0 END) as success_count
                    FROM url_monitoring
                    GROUP BY url
                """)
                
                results = cursor.fetchall()
                
                if results:
                    print("\nSUMMARY STATISTICS")
                    print("-"*50)
                    for row in results:
                        url, total, avg_time, min_time, max_time, success = row
                        success_rate = (success / total) * 100 if total > 0 else 0
                        
                        print(f"\nURL: {url}")
                        print(f"Total Checks: {total}")
                        print(f"Success Rate: {success_rate:.1f}%")
                        print(f"Avg Response Time: {avg_time*1000:.2f}ms")
                        print(f"Min Response Time: {min_time*1000:.2f}ms")
                        print(f"Max Response Time: {max_time*1000:.2f}ms")
                
        except sqlite3.Error as e:
            print(f"Error retrieving statistics: {e}")


async def main():