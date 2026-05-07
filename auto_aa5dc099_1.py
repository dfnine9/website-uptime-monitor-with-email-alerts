```python
#!/usr/bin/env python3
"""
Performance Log Analyzer

This module analyzes web performance log data to detect downtime events and slow response times.
It monitors HTTP status codes and response times against configurable thresholds, generating
alert messages for anomalies.

Features:
- Detects downtime (HTTP status codes != 200)
- Monitors slow response times (> configurable threshold)
- Generates structured alert messages with site details and metrics
- Configurable response time thresholds
- Comprehensive error handling

Usage:
    python script.py

Dependencies:
    - Standard library only (json, datetime, statistics)
"""

import json
import sys
from datetime import datetime, timedelta
from statistics import mean, median
from typing import List, Dict, Any, Tuple
import re


class PerformanceAnalyzer:
    """Analyzes performance log data for downtime and slow response detection."""
    
    def __init__(self, response_time_threshold: float = 2000):
        """
        Initialize the performance analyzer.
        
        Args:
            response_time_threshold: Response time threshold in milliseconds (default: 2000ms)
        """
        self.response_time_threshold = response_time_threshold
        self.alerts = []
        
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """
        Parse a single log line into structured data.
        
        Args:
            line: Raw log line string
            
        Returns:
            Dictionary containing parsed log data
        """
        try:
            # Common log format: timestamp url status_code response_time_ms
            # Example: "2024-01-15 10:30:45 https://example.com 200 1500"
            parts = line.strip().split()
            if len(parts) >= 4:
                timestamp_str = f"{parts[0]} {parts[1]}"
                url = parts[2]
                status_code = int(parts[3])
                response_time = float(parts[4]) if len(parts) > 4 else 0
                
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                return {
                    'timestamp': timestamp,
                    'url': url,
                    'status_code': status_code,
                    'response_time': response_time,
                    'site': self._extract_domain(url)
                }
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse log line: {line.strip()} - {e}")
            return None
            
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            if url.startswith(('http://', 'https://')):
                domain = url.split('/')[2]
            else:
                domain = url.split('/')[0]
            return domain
        except IndexError:
            return url
            
    def detect_downtime(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect downtime events (status codes != 200).
        
        Args:
            log_entries: List of parsed log entries
            
        Returns:
            List of downtime events
        """
        downtime_events = []
        
        for entry in log_entries:
            if entry and entry['status_code'] != 200:
                downtime_events.append({
                    'type': 'downtime',
                    'site': entry['site'],
                    'url': entry['url'],
                    'timestamp': entry['timestamp'],
                    'status_code': entry['status_code'],
                    'response_time': entry['response_time']
                })
                
        return downtime_events
        
    def detect_slow_responses(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect slow response times.
        
        Args:
            log_entries: List of parsed log entries
            
        Returns:
            List of slow response events
        """
        slow_responses = []
        
        for entry in log_entries:
            if entry and entry['response_time'] > self.response_time_threshold:
                slow_responses.append({
                    'type': 'slow_response',
                    'site': entry['site'],
                    'url': entry['url'],
                    'timestamp': entry['timestamp'],
                    'status_code': entry['status_code'],
                    'response_time': entry['response_time'],
                    'threshold': self.response_time_threshold
                })
                
        return slow_responses
        
    def generate_site_metrics(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Generate performance metrics by site.
        
        Args:
            log_entries: List of parsed log entries
            
        Returns:
            Dictionary of site metrics
        """
        site_metrics = {}
        
        for entry in log_entries:
            if not entry:
                continue
                
            site = entry['site']
            if site not in site_metrics:
                site_metrics[site] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'response_times': [],
                    'status_codes': {}
                }
            
            metrics = site_metrics[site]
            metrics['total_requests'] += 1
            
            if entry['status_code'] == 200:
                metrics['successful_requests'] += 1
            else:
                metrics['failed_requests'] += 1
                
            metrics['response_times'].append(entry['response_time'])
            
            status_code = entry['status_code']
            metrics['status_codes'][status_code] = metrics['status_codes'].get(status_code, 0) + 1
            
        # Calculate aggregated metrics
        for site, metrics in site_metrics.items():
            response_times = metrics['response_times']
            if response_times:
                metrics['avg_response_time'] = mean(response_times)
                metrics['median_response_time'] = median(response_times)
                metrics['max_response_time'] = max(response_times)
                metrics['min_response_time'] = min(response_times)
            else:
                metrics['avg_response_time'] = 0
                metrics['median_response_time'] = 0
                metrics['max_response_time'] = 0
                metrics['min_response_time'] = 0
                
            if metrics['total_requests'] > 0:
                metrics['success_rate'] = (metrics['successful_requests'] / metrics['total_requests']) * 100
            else:
                metrics['success_rate'] = 0
                
        return site_metrics
        
    def generate_alert_message(self, event: Dict[str, Any], site_metrics: Dict[str, Dict[str, Any]]) -> str:
        """
        Generate a formatted alert message for an event.
        
        Args:
            event: Event data
            site_metrics: Site performance metrics
            
        Returns:
            Formatted alert message
        """
        site = event['site']
        timestamp = event['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        if event['type'] == 'downtime':
            alert = f"🚨 DOWNTIME ALERT - {site}\n"
            alert += f"   URL: {event['url']}\n"
            alert += f"   Status Code: {event['status_code']}\n"
            alert += f"   Timestamp: {timestamp}\n"
            alert += f"   Response Time: {event['response_time']}ms\n"
            
        elif event['type'] == 'slow_response':
            alert = f"⚠️  SLOW RESPONSE ALERT - {site}\n"
            alert += f"   URL: {event['url']}\n"
            alert += f"   Response Time: {event['response_time']}ms (threshold: {event['threshold']}ms)\n"
            alert += f"   Status Code: {event['status_code']}\n"
            alert += f"   Timestamp: {timestamp}\n