```python
#!/usr/bin/env python3
"""
Site Health Monitor with Email Alerts

This module monitors website health by performing HTTP checks and sends automated
email notifications when sites fail health checks. It includes detailed failure
information, timestamps, and recovery suggestions in alert messages.

Features:
- HTTP/HTTPS health checks with timeout handling
- SMTP email notifications with HTML formatting
- Detailed failure reporting (URL, failure type, timestamp)
- Basic recovery suggestions based on failure type
- Configurable retry logic and alert thresholds

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - smtplib, email (standard library for email)
    - datetime, json, time (standard library utilities)
"""

import smtplib
import httpx
import json
import time
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class HealthCheckResult:
    """Data class to store health check results."""
    url: str
    status: str  # 'success', 'failure'
    status_code: Optional[int]
    response_time: Optional[float]
    error_message: Optional[str]
    failure_type: Optional[str]
    timestamp: str
    recovery_suggestions: List[str]


class SiteHealthMonitor:
    """Main class for monitoring site health and sending email alerts."""
    
    def __init__(self, email_config: Dict, sites: List[str], timeout: int = 10):
        """
        Initialize the health monitor.
        
        Args:
            email_config: Email configuration dictionary
            sites: List of URLs to monitor
            timeout: HTTP request timeout in seconds
        """
        self.email_config = email_config
        self.sites = sites
        self.timeout = timeout
        self.failed_sites = {}  # Track consecutive failures
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def check_site_health(self, url: str) -> HealthCheckResult:
        """
        Perform health check on a single site.
        
        Args:
            url: URL to check
            
        Returns:
            HealthCheckResult object with check results
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        try:
            start_time = time.time()
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, follow_redirects=True)
                
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                return HealthCheckResult(
                    url=url,
                    status='success',
                    status_code=response.status_code,
                    response_time=response_time,
                    error_message=None,
                    failure_type=None,
                    timestamp=timestamp,
                    recovery_suggestions=[]
                )
            else:
                failure_type = f"HTTP {response.status_code}"
                suggestions = self._get_recovery_suggestions(failure_type, response.status_code)
                
                return HealthCheckResult(
                    url=url,
                    status='failure',
                    status_code=response.status_code,
                    response_time=response_time,
                    error_message=f"HTTP {response.status_code}: {response.reason_phrase}",
                    failure_type=failure_type,
                    timestamp=timestamp,
                    recovery_suggestions=suggestions
                )
                
        except httpx.TimeoutException:
            return HealthCheckResult(
                url=url,
                status='failure',
                status_code=None,
                response_time=None,
                error_message=f"Request timeout after {self.timeout} seconds",
                failure_type="Timeout",
                timestamp=timestamp,
                recovery_suggestions=self._get_recovery_suggestions("Timeout")
            )
            
        except httpx.ConnectError as e:
            return HealthCheckResult(
                url=url,
                status='failure',
                status_code=None,
                response_time=None,
                error_message=f"Connection error: {str(e)}",
                failure_type="Connection Error",
                timestamp=timestamp,
                recovery_suggestions=self._get_recovery_suggestions("Connection Error")
            )
            
        except Exception as e:
            return HealthCheckResult(
                url=url,
                status='failure',
                status_code=None,
                response_time=None,
                error_message=f"Unexpected error: {str(e)}",
                failure_type="Unknown Error",
                timestamp=timestamp,
                recovery_suggestions=self._get_recovery_suggestions("Unknown Error")
            )

    def _get_recovery_suggestions(self, failure_type: str, status_code: Optional[int] = None) -> List[str]:
        """
        Get recovery suggestions based on failure type.
        
        Args:
            failure_type: Type of failure
            status_code: HTTP status code if applicable
            
        Returns:
            List of recovery suggestions
        """
        suggestions = []
        
        if failure_type == "Timeout":
            suggestions = [
                "Check if the server is experiencing high load",
                "Verify network connectivity to the target server",
                "Consider increasing timeout values if this is expected",
                "Check if the server is behind a slow CDN or proxy"
            ]
        elif failure_type == "Connection Error":
            suggestions = [
                "Verify the URL is correct and the server is running",
                "Check DNS resolution for the domain",
                "Ensure firewall rules allow outbound connections",
                "Verify SSL/TLS certificate validity for HTTPS sites"
            ]
        elif status_code == 404:
            suggestions = [
                "Verify the URL path is correct",
                "Check if the resource has been moved or deleted",
                "Review recent deployments that might have affected routing"
            ]
        elif status_code == 500:
            suggestions = [
                "Check server logs for internal errors",
                "Verify database connectivity if applicable",
                "Review recent code deployments",
                "Check server resource usage (CPU, memory, disk)"
            ]
        elif status_code == 502 or status_code == 503:
            suggestions = [
                "Check if the upstream server is running",
                "Verify load balancer configuration",
                "Check if the service is undergoing maintenance",
                "Review server capacity and scaling settings"
            ]
        elif status_code and 400 <= status_code < 500:
            suggestions = [
                "Review request parameters and headers",
                "Check authentication and authorization settings",
                "Verify API rate limits haven't been exceeded"
            ]
        else:
            suggestions = [
                "Review server logs for detailed error information",
                "Check system monitoring dashboards",
                "Verify all dependent services are operational",
                "Consider contacting the development team"
            ]
            
        return suggestions

    def send_alert_email(self, failed_results: List[HealthCheckResult]) -> bool:
        """
        Send email alert for failed health checks.
        
        Args:
            failed_results: List of failed health check results
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Site Health Alert: {len(failed_results)} Site(s) Down"
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            
            # Create HTML content
            html_content = self._create_alert_html(failed_results)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                if self.email_config.get('use_tls', True