```python
#!/usr/bin/env python3
"""
URL Health Monitor

A self-contained monitoring script that performs health checks on a configurable list of URLs.
Monitors response times, status codes, and implements alerting for downtime or performance issues.

Features:
- Configurable monitoring intervals (default: 5 minutes)
- Rolling log of health check results
- Alert logic for site downtime and response time thresholds
- JSON-based configuration
- Comprehensive error handling

Usage: python script.py
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    sys.exit(1)


@dataclass
class HealthCheckResult:
    """Result of a single health check"""
    url: str
    timestamp: datetime
    status_code: Optional[int]
    response_time_ms: Optional[float]
    error: Optional[str]
    is_healthy: bool


@dataclass
class MonitorConfig:
    """Configuration for URL monitoring"""
    urls: List[str]
    check_interval_seconds: int = 300  # 5 minutes
    response_timeout_seconds: int = 30
    max_response_time_ms: float = 5000.0
    rolling_log_size: int = 1000
    alert_failure_threshold: int = 2  # consecutive failures before alert


class URLHealthMonitor:
    """Main monitoring class that orchestrates health checks and alerting"""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.results_log: deque = deque(maxlen=config.rolling_log_size)
        self.site_states: Dict[str, List[bool]] = {url: [] for url in config.urls}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def check_url_health(self, client: httpx.AsyncClient, url: str) -> HealthCheckResult:
        """Perform health check on a single URL"""
        start_time = time.perf_counter()
        
        try:
            response = await client.get(
                url,
                timeout=self.config.response_timeout_seconds,
                follow_redirects=True
            )
            
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000
            
            is_healthy = (
                200 <= response.status_code < 400 and
                response_time_ms <= self.config.max_response_time_ms
            )
            
            return HealthCheckResult(
                url=url,
                timestamp=datetime.now(),
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                error=None,
                is_healthy=is_healthy
            )
            
        except Exception as e:
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000
            
            return HealthCheckResult(
                url=url,
                timestamp=datetime.now(),
                status_code=None,
                response_time_ms=response_time_ms,
                error=str(e),
                is_healthy=False
            )
    
    async def run_health_checks(self) -> List[HealthCheckResult]:
        """Run health checks on all configured URLs"""
        async with httpx.AsyncClient() as client:
            tasks = [
                self.check_url_health(client, url) 
                for url in self.config.urls
            ]
            return await asyncio.gather(*tasks)
    
    def update_site_states(self, results: List[HealthCheckResult]) -> None:
        """Update rolling state for each site and trigger alerts if needed"""
        for result in results:
            url = result.url
            
            # Maintain rolling window of recent states
            self.site_states[url].append(result.is_healthy)
            if len(self.site_states[url]) > self.config.alert_failure_threshold * 2:
                self.site_states[url].pop(0)
            
            # Check for alert conditions
            recent_states = self.site_states[url][-self.config.alert_failure_threshold:]
            
            if (len(recent_states) >= self.config.alert_failure_threshold and 
                not any(recent_states)):
                self.trigger_alert(result, "SITE_DOWN")
            elif result.response_time_ms and result.response_time_ms > self.config.max_response_time_ms:
                self.trigger_alert(result, "SLOW_RESPONSE")
    
    def trigger_alert(self, result: HealthCheckResult, alert_type: str) -> None:
        """Trigger alert for site issues"""
        if alert_type == "SITE_DOWN":
            self.logger.error(
                f"🚨 ALERT: {result.url} is DOWN - "
                f"Status: {result.status_code}, Error: {result.error}"
            )
            print(f"🚨 ALERT: {result.url} is DOWN")
            
        elif alert_type == "SLOW_RESPONSE":
            self.logger.warning(
                f"⚠️  ALERT: {result.url} slow response - "
                f"{result.response_time_ms:.0f}ms (threshold: {self.config.max_response_time_ms}ms)"
            )
            print(f"⚠️  ALERT: {result.url} slow response ({result.response_time_ms:.0f}ms)")
    
    def log_results(self, results: List[HealthCheckResult]) -> None:
        """Log results to rolling log and print to stdout"""
        self.results_log.extend(results)
        
        print(f"\n{'='*60}")
        print(f"Health Check Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        for result in results:
            status_icon = "✅" if result.is_healthy else "❌"
            
            if result.error:
                print(f"{status_icon} {result.url}")
                print(f"    Error: {result.error}")
            else:
                print(f"{status_icon} {result.url}")
                print(f"    Status: {result.status_code} | "
                      f"Response: {result.response_time_ms:.0f}ms")
        
        # Print summary
        healthy_count = sum(1 for r in results if r.is_healthy)
        print(f"\nSummary: {healthy_count}/{len(results)} sites healthy")
    
    async def monitoring_loop(self) -> None:
        """Main monitoring loop that runs health checks at configured intervals"""
        self.logger.info(f"Starting URL health monitor for {len(self.config.urls)} URLs")
        self.logger.info(f"Check interval: {self.config.check_interval_seconds}s")
        self.logger.info(f"Response timeout: {self.config.response_timeout_seconds}s")
        self.logger.info(f"Max response time: {self.config.max_response_time_ms}ms")
        
        print(f"🚀 URL Health Monitor Started")
        print(f"Monitoring {len(self.config.urls)} URLs every {self.config.check_interval_seconds//60} minutes")
        print(f"URLs: {', '.join(self.config.urls)}")
        
        try:
            while True:
                try:
                    # Run health checks
                    results = await self.run_health_checks()
                    
                    # Process results
                    self.log_results(results)
                    self.update_site_states(results)
                    
                    # Wait