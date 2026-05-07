```python
#!/usr/bin/env python3
"""
System Monitoring Scheduler with Downtime Detection

This module provides a comprehensive monitoring solution that:
- Runs system health checks every 15 minutes
- Generates daily summary reports
- Sends email notifications for critical downtime events
- Maintains detailed logs of all monitoring activities

The scheduler monitors multiple endpoints and services, detecting downtime
and performance issues. Critical events trigger immediate email alerts,
while routine monitoring data is compiled into daily reports.

Dependencies: httpx, anthropic (for advanced analysis)
Usage: python script.py
"""

import asyncio
import smtplib
import json
import logging
import schedule
import time
import httpx
import sys
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading


@dataclass
class MonitoringResult:
    """Data class for monitoring results."""
    timestamp: str
    endpoint: str
    status: str
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None


class SystemMonitor:
    """Core monitoring functionality."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.endpoints = config.get('endpoints', [])
        self.timeout = config.get('timeout', 10)
        
    async def check_endpoint(self, endpoint: str) -> MonitoringResult:
        """Check a single endpoint for availability and response time."""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                status = "UP" if response.status_code < 400 else "DOWN"
                
                return MonitoringResult(
                    timestamp=timestamp,
                    endpoint=endpoint,
                    status=status,
                    response_time=response_time,
                    status_code=response.status_code
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return MonitoringResult(
                timestamp=timestamp,
                endpoint=endpoint,
                status="DOWN",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def monitor_all_endpoints(self) -> List[MonitoringResult]:
        """Monitor all configured endpoints concurrently."""
        tasks = [self.check_endpoint(endpoint) for endpoint in self.endpoints]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(MonitoringResult(
                    timestamp=datetime.now().isoformat(),
                    endpoint=self.endpoints[i],
                    status="DOWN",
                    response_time=0.0,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
                
        return processed_results


class EmailNotifier:
    """Handles email notifications for critical events."""
    
    def __init__(self, config: Dict):
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.email = config.get('email', '')
        self.password = config.get('password', '')
        self.recipients = config.get('recipients', [])
        self.enabled = bool(self.email and self.password and self.recipients)
        
    def send_notification(self, subject: str, body: str) -> bool:
        """Send email notification."""
        if not self.enabled:
            logging.warning("Email notifications not configured")
            return False
            
        try:
            msg = MimeMultipart()
            msg['From'] = self.email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False


class ReportGenerator:
    """Generates monitoring reports."""
    
    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        
    def load_daily_data(self, date: datetime) -> List[MonitoringResult]:
        """Load monitoring data for a specific date."""
        try:
            if not self.data_file.exists():
                return []
                
            with open(self.data_file, 'r') as f:
                all_data = [json.loads(line) for line in f if line.strip()]
                
            # Filter data for the specific date
            target_date = date.strftime('%Y-%m-%d')
            daily_data = []
            
            for record in all_data:
                record_date = record['timestamp'][:10]  # Extract date part
                if record_date == target_date:
                    daily_data.append(MonitoringResult(**record))
                    
            return daily_data
            
        except Exception as e:
            logging.error(f"Failed to load daily data: {e}")
            return []
    
    def generate_daily_report(self, date: datetime) -> str:
        """Generate a comprehensive daily report."""
        data = self.load_daily_data(date)
        
        if not data:
            return f"No monitoring data available for {date.strftime('%Y-%m-%d')}"
            
        # Calculate statistics
        total_checks = len(data)
        up_count = sum(1 for r in data if r.status == "UP")
        down_count = total_checks - up_count
        uptime_percentage = (up_count / total_checks) * 100 if total_checks > 0 else 0
        
        # Group by endpoint
        endpoint_stats = {}
        for result in data:
            if result.endpoint not in endpoint_stats:
                endpoint_stats[result.endpoint] = {
                    'total': 0, 'up': 0, 'down': 0, 
                    'avg_response_time': 0, 'response_times': []
                }
            
            stats = endpoint_stats[result.endpoint]
            stats['total'] += 1
            if result.status == "UP":
                stats['up'] += 1
            else:
                stats['down'] += 1
            stats['response_times'].append(result.response_time)
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            if stats['response_times']:
                stats['avg_response_time'] = sum(stats['response_times']) / len(stats['response_times'])
            stats['uptime_percentage'] = (stats['up'] / stats['total']) * 100 if stats['total'] > 0 else 0
        
        # Generate report
        report = f"""
Daily Monitoring Report - {date.strftime('%Y-%m-%d')}
{'='*50}

Overall Statistics:
- Total Checks: {total_checks}
- Successful Checks: {up_count}
- Failed Checks: {down_count}
- Overall Uptime: {uptime_percentage:.2f}%

Endpoint Details:
"""
        
        for endpoint, stats in endpoint_stats.items():
            report += f"""
{endpoint}:
  - Total Checks: {stats['total']}
  - Uptime: {stats['uptime_percentage']:.2