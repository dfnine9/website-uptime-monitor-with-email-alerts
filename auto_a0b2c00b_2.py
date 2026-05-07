[ACTION:RESEARCH]

```python
#!/usr/bin/env python3
"""
URL Monitor Orchestrator

A comprehensive monitoring system that:
- Reads URL configurations from a JSON config file
- Performs scheduled HTTP health checks with configurable intervals
- Detects state changes by comparing current vs previous results
- Sends email alerts for new failures and recoveries
- Maintains rotating log files with size-based rotation
- Supports multiple check types (HTTP status, response time, content validation)

Dependencies: httpx, anthropic (optional for AI-enhanced error analysis)
Usage: python script.py
"""

import json
import time
import smtplib
import logging
import hashlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import signal
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

@dataclass
class CheckResult:
    """Represents the result of a single URL check"""
    url: str
    status_code: int
    response_time: float
    content_match: bool
    error: Optional[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckResult':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class URLMonitor:
    """Core monitoring class that performs URL health checks"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = httpx.Client(timeout=config.get('timeout', 30))
        
    def check_url(self, url_config: Dict[str, Any]) -> CheckResult:
        """Perform a single URL check"""
        url = url_config['url']
        method = url_config.get('method', 'GET').upper()
        headers = url_config.get('headers', {})
        expected_status = url_config.get('expected_status', 200)
        content_check = url_config.get('content_check', '')
        max_response_time = url_config.get('max_response_time', 10.0)
        
        start_time = time.time()
        error = None
        status_code = 0
        content_match = True
        
        try:
            response = self.client.request(method, url, headers=headers)
            response_time = time.time() - start_time
            status_code = response.status_code
            
            # Check status code
            if status_code != expected_status:
                error = f"Expected status {expected_status}, got {status_code}"
            
            # Check response time
            elif response_time > max_response_time:
                error = f"Response time {response_time:.2f}s exceeds limit {max_response_time}s"
            
            # Check content if specified
            elif content_check and content_check not in response.text:
                content_match = False
                error = f"Content check failed: '{content_check}' not found"
                
        except Exception as e:
            response_time = time.time() - start_time
            error = str(e)
            
        return CheckResult(
            url=url,
            status_code=status_code,
            response_time=response_time,
            content_match=content_match,
            error=error,
            timestamp=datetime.now()
        )
    
    def close(self):
        """Clean up HTTP client"""
        self.client.close()

class StateManager:
    """Manages previous check results for state change detection"""
    
    def __init__(self, state_file: str = "monitor_state.json"):
        self.state_file = Path(state_file)
        self.previous_results: Dict[str, CheckResult] = {}
        self.load_state()
    
    def load_state(self):
        """Load previous results from state file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.previous_results = {
                        url: CheckResult.from_dict(result_data)
                        for url, result_data in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
    
    def save_state(self):
        """Save current results to state file"""
        try:
            data = {
                url: result.to_dict()
                for url, result in self.previous_results.items()
            }
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save state file: {e}")
    
    def detect_changes(self, current_results: List[CheckResult]) -> List[Dict[str, Any]]:
        """Detect state changes between current and previous results"""
        changes = []
        
        for current in current_results:
            url = current.url
            previous = self.previous_results.get(url)
            
            if previous is None:
                # New URL being monitored
                if current.error:
                    changes.append({
                        'type': 'new_failure',
                        'url': url,
                        'current': current,
                        'previous': None
                    })
            else:
                # Compare with previous result
                if previous.error and not current.error:
                    changes.append({
                        'type': 'recovery',
                        'url': url,
                        'current': current,
                        'previous': previous
                    })
                elif not previous.error and current.error:
                    changes.append({
                        'type': 'new_failure',
                        'url': url,
                        'current': current,
                        'previous': previous
                    })
                elif previous.error and current.error and previous.error != current.error:
                    changes.append({
                        'type': 'failure_change',
                        'url': url,
                        'current': current,
                        'previous': previous
                    })
        
        # Update stored results
        for result in current_results:
            self.previous_results[result.url] = result
        
        return changes

class AlertManager:
    """Handles email alerts for state changes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)
        self.anthropic_client = None
        
        if ANTHROPIC_AVAILABLE and config.get('anthropic_api_key'):
            self.anthropic_client = Anthropic(api_key=config['anthropic_api_key'])
    
    def send_alert(self, changes: List[Dict[str, Any]]):
        """Send email alert for detected changes"""
        if not self.enabled or not changes:
            return
        
        try:
            subject = f"URL Monitor Alert - {len(changes)} change(s) detected"
            body = self._generate_alert_body(changes)
            
            msg = MIMEMultipart()
            msg['From'] = self.config['smtp_from']
            msg['To'] = ', '.join(self.config['recipients'])
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.config['smtp_host'], self.config.get('smtp_port', 587)) as server:
                if self.config.get('smtp_tls', True):
                    server