```python
"""
Performance Monitoring and Email Alert System

This module monitors system/service performance and sends HTML-formatted email alerts
when performance issues are detected. It tracks response times, detects downtime,
and generates visual reports with graphs embedded in email notifications.

Features:
- HTTP endpoint monitoring with response time tracking
- Downtime detection and duration calculation
- HTML email reports with embedded ASCII graphs
- SMTP email delivery with error handling
- Configurable thresholds and monitoring intervals

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - smtplib (standard library - email sending)
    - email (standard library - email formatting)
"""

import smtplib
import time
import json
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Tuple
import statistics

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Please install with: pip install httpx")
    exit(1)


class PerformanceMonitor:
    def __init__(self, config: Dict):
        self.config = config
        self.response_times = []
        self.downtime_events = []
        self.current_downtime_start = None
        self.last_check_time = datetime.now()
        
    def check_endpoint(self, url: str, timeout: int = 10) -> Tuple[bool, float]:
        """Check endpoint availability and measure response time."""
        try:
            start_time = time.time()
            with httpx.Client() as client:
                response = client.get(url, timeout=timeout)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                is_up = response.status_code < 400
                return is_up, response_time
        except Exception as e:
            print(f"Error checking {url}: {e}")
            return False, 0.0
    
    def record_performance_data(self, url: str, is_up: bool, response_time: float):
        """Record performance metrics and track downtime events."""
        current_time = datetime.now()
        
        if is_up:
            self.response_times.append({
                'timestamp': current_time,
                'response_time': response_time,
                'url': url
            })
            
            # End downtime if it was ongoing
            if self.current_downtime_start:
                downtime_duration = current_time - self.current_downtime_start
                self.downtime_events.append({
                    'start': self.current_downtime_start,
                    'end': current_time,
                    'duration': downtime_duration.total_seconds(),
                    'url': url
                })
                self.current_downtime_start = None
                print(f"Downtime ended for {url}. Duration: {downtime_duration}")
        else:
            # Start tracking downtime if not already started
            if not self.current_downtime_start:
                self.current_downtime_start = current_time
                print(f"Downtime started for {url} at {current_time}")
    
    def generate_ascii_graph(self, data: List[float], width: int = 60, height: int = 10) -> str:
        """Generate ASCII graph for response times."""
        if not data:
            return "No data available"
        
        max_val = max(data)
        min_val = min(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        graph_lines = []
        for i in range(height, 0, -1):
            line = ""
            threshold = min_val + (range_val * i / height)
            for value in data[-width:]:  # Show last 'width' data points
                if value >= threshold:
                    line += "█"
                else:
                    line += " "
            graph_lines.append(f"{threshold:6.1f}ms |{line}|")
        
        graph_lines.append(" " * 10 + "-" * min(len(data), width))
        return "\n".join(graph_lines)
    
    def should_send_alert(self) -> bool:
        """Determine if an alert should be sent based on performance thresholds."""
        recent_times = [rt['response_time'] for rt in self.response_times[-10:]]
        
        if not recent_times:
            return False
        
        avg_response_time = statistics.mean(recent_times)
        
        # Alert conditions
        if avg_response_time > self.config.get('response_time_threshold', 5000):
            return True
        
        if self.current_downtime_start:
            downtime_duration = datetime.now() - self.current_downtime_start
            if downtime_duration.total_seconds() > self.config.get('downtime_threshold', 300):
                return True
        
        if len(self.downtime_events) > 0:
            recent_downtime = [event for event in self.downtime_events 
                             if event['end'] > datetime.now() - timedelta(hours=1)]
            if len(recent_downtime) > 0:
                return True
        
        return False
    
    def generate_html_report(self) -> str:
        """Generate HTML-formatted performance report."""
        current_time = datetime.now()
        recent_times = [rt['response_time'] for rt in self.response_times[-50:]]
        
        # Calculate statistics
        if recent_times:
            avg_response_time = statistics.mean(recent_times)
            max_response_time = max(recent_times)
            min_response_time = min(recent_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # Calculate total downtime in last 24 hours
        recent_downtime_events = [
            event for event in self.downtime_events 
            if event['end'] > current_time - timedelta(hours=24)
        ]
        total_downtime = sum(event['duration'] for event in recent_downtime_events)
        
        # Generate ASCII graph
        ascii_graph = self.generate_ascii_graph(recent_times)
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 10px; }}
                .metrics {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; }}
                .graph {{ background-color: #000; color: #00ff00; padding: 10px; font-family: monospace; white-space: pre; }}
                .downtime {{ background-color: #ffebee; padding: 10px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 Performance Alert - {current_time.strftime('%Y-%m-%d %H:%M:%S')}</h2>
            </div>
            
            <div class="metrics">
                <h3>📊 Performance Metrics (Last 50 checks)</h3>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Average Response Time</td><td>{avg_response_time:.2f} ms</td></tr>
                    <tr><td>Maximum Response Time</td><td>{max_response_time:.2f} ms</td></tr>
                    <tr><td>Minimum Response Time</td><td>{min_response_time:.2f} ms</td></tr>
                    <tr><td>Total Checks</td><td>{len(self