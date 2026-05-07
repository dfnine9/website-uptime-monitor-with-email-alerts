```python
"""
Email Alerting Module for Health Check Results

This module analyzes JSON health check results, identifies failures or warnings
based on configurable thresholds, and sends formatted HTML email reports via SMTP.

Features:
- Configurable thresholds for CPU, memory, disk usage, and response times
- HTML email formatting with severity-based styling
- SMTP authentication and TLS support
- Comprehensive error handling and logging
- Self-contained with minimal dependencies

Usage:
    python script.py

The script will:
1. Load health check data from JSON
2. Analyze against configured thresholds
3. Generate HTML email reports for issues found
4. Send alerts via SMTP (if configured)
5. Print results to stdout
"""

import json
import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

class HealthCheckAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration settings."""
        self.config = config
        self.thresholds = config.get('thresholds', {})
        self.smtp_config = config.get('smtp', {})
        self.email_config = config.get('email', {})
        
    def analyze_health_data(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze health check data and identify issues."""
        issues = []
        
        try:
            # Analyze CPU usage
            cpu_usage = health_data.get('cpu_usage', 0)
            if cpu_usage > self.thresholds.get('cpu_critical', 90):
                issues.append({
                    'type': 'CPU',
                    'severity': 'CRITICAL',
                    'value': cpu_usage,
                    'threshold': self.thresholds.get('cpu_critical', 90),
                    'message': f'CPU usage at {cpu_usage}% (critical threshold: {self.thresholds.get("cpu_critical", 90)}%)'
                })
            elif cpu_usage > self.thresholds.get('cpu_warning', 75):
                issues.append({
                    'type': 'CPU',
                    'severity': 'WARNING',
                    'value': cpu_usage,
                    'threshold': self.thresholds.get('cpu_warning', 75),
                    'message': f'CPU usage at {cpu_usage}% (warning threshold: {self.thresholds.get("cpu_warning", 75)}%)'
                })
                
            # Analyze memory usage
            memory_usage = health_data.get('memory_usage', 0)
            if memory_usage > self.thresholds.get('memory_critical', 85):
                issues.append({
                    'type': 'Memory',
                    'severity': 'CRITICAL',
                    'value': memory_usage,
                    'threshold': self.thresholds.get('memory_critical', 85),
                    'message': f'Memory usage at {memory_usage}% (critical threshold: {self.thresholds.get("memory_critical", 85)}%)'
                })
            elif memory_usage > self.thresholds.get('memory_warning', 70):
                issues.append({
                    'type': 'Memory',
                    'severity': 'WARNING',
                    'value': memory_usage,
                    'threshold': self.thresholds.get('memory_warning', 70),
                    'message': f'Memory usage at {memory_usage}% (warning threshold: {self.thresholds.get("memory_warning", 70)}%)'
                })
                
            # Analyze disk usage
            disk_usage = health_data.get('disk_usage', 0)
            if disk_usage > self.thresholds.get('disk_critical', 90):
                issues.append({
                    'type': 'Disk',
                    'severity': 'CRITICAL',
                    'value': disk_usage,
                    'threshold': self.thresholds.get('disk_critical', 90),
                    'message': f'Disk usage at {disk_usage}% (critical threshold: {self.thresholds.get("disk_critical", 90)}%)'
                })
            elif disk_usage > self.thresholds.get('disk_warning', 80):
                issues.append({
                    'type': 'Disk',
                    'severity': 'WARNING',
                    'value': disk_usage,
                    'threshold': self.thresholds.get('disk_warning', 80),
                    'message': f'Disk usage at {disk_usage}% (warning threshold: {self.thresholds.get("disk_warning", 80)}%)'
                })
                
            # Analyze response time
            response_time = health_data.get('response_time_ms', 0)
            if response_time > self.thresholds.get('response_critical', 5000):
                issues.append({
                    'type': 'Response Time',
                    'severity': 'CRITICAL',
                    'value': response_time,
                    'threshold': self.thresholds.get('response_critical', 5000),
                    'message': f'Response time at {response_time}ms (critical threshold: {self.thresholds.get("response_critical", 5000)}ms)'
                })
            elif response_time > self.thresholds.get('response_warning', 2000):
                issues.append({
                    'type': 'Response Time',
                    'severity': 'WARNING',
                    'value': response_time,
                    'threshold': self.thresholds.get('response_warning', 2000),
                    'message': f'Response time at {response_time}ms (warning threshold: {self.thresholds.get("response_warning", 2000)}ms)'
                })
                
            # Check service status
            services = health_data.get('services', {})
            for service_name, service_status in services.items():
                if service_status.get('status') != 'healthy':
                    issues.append({
                        'type': 'Service',
                        'severity': 'CRITICAL',
                        'value': service_status.get('status', 'unknown'),
                        'threshold': 'healthy',
                        'message': f'Service {service_name} is {service_status.get("status", "unknown")}'
                    })
                    
        except Exception as e:
            print(f"Error analyzing health data: {e}")
            issues.append({
                'type': 'Analysis Error',
                'severity': 'CRITICAL',
                'value': str(e),
                'threshold': 'none',
                'message': f'Failed to analyze health data: {e}'
            })
            
        return issues
    
    def generate_html_report(self, issues: List[Dict[str, Any]], health_data: Dict[str, Any]) -> str:
        """Generate HTML email report."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if not issues:
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ color: #2e8b57; border-bottom: 2px solid #2e8b57; padding-bottom: 10px; }}
                    .status-ok {{ color: #2e8b57; font-weight: bold; }}
                    .summary {{ background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <h1 class="header">Health Check Report - All Systems Normal</h1>
                <p><strong>Generated:</strong> {timestamp}</p>
                <div class="summary">
                    <h2 class="status-ok">✓ All systems operating within normal parameters</h2>
                    <ul>
                        <li>CPU Usage: {health_data.get('cpu_usage', 'N/A')}%</li>