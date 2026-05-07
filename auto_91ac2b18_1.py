```python
#!/usr/bin/env python3
"""
URL Monitoring Daemon

A self-contained monitoring daemon that continuously checks URL availability
at configurable intervals. Features persistent logging, graceful error handling,
and real-time status reporting to stdout.

Dependencies: httpx, anthropic (optional for enhanced reporting)
Usage: python script.py
"""

import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import signal
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic not available. Enhanced reporting disabled.")


class URLMonitor:
    """Main monitoring class that handles URL checking and logging."""
    
    def __init__(self, config_file: str = "monitor_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.running = False
        self.threads = []
        self.status_cache = {}
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file or create default."""
        default_config = {
            "urls": [
                {"url": "https://google.com", "timeout": 10, "interval": 60},
                {"url": "https://github.com", "timeout": 10, "interval": 60},
                {"url": "https://stackoverflow.com", "timeout": 10, "interval": 60}
            ],
            "log_file": "url_monitor.log",
            "max_retries": 3,
            "retry_delay": 5,
            "user_agent": "URLMonitor/1.0"
        }
        
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default config: {self.config_file}")
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return default_config
    
    def _setup_logging(self):
        """Configure logging to file and console."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # File handler
        file_handler = logging.FileHandler(self.config['log_file'])
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Root logger
        self.logger = logging.getLogger('URLMonitor')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.stop()
        
    def check_url(self, url_config: Dict) -> Dict:
        """Check a single URL and return status information."""
        url = url_config['url']
        timeout = url_config.get('timeout', 10)
        max_retries = self.config['max_retries']
        retry_delay = self.config['retry_delay']
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'response_time': None,
            'status_code': None,
            'error': None,
            'retry_count': 0
        }
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                with httpx.Client(timeout=timeout) as client:
                    headers = {'User-Agent': self.config['user_agent']}
                    response = client.get(url, headers=headers, follow_redirects=True)
                    
                response_time = time.time() - start_time
                
                result.update({
                    'status': 'up' if response.status_code < 400 else 'down',
                    'response_time': round(response_time, 3),
                    'status_code': response.status_code,
                    'retry_count': attempt
                })
                
                break
                
            except Exception as e:
                result['retry_count'] = attempt
                result['error'] = str(e)
                
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    result['status'] = 'down'
                    
        return result
    
    def _log_status_change(self, url: str, old_status: str, new_status: str, result: Dict):
        """Log when URL status changes."""
        if old_status != new_status:
            if new_status == 'up':
                self.logger.info(f"✅ {url} is UP (recovered) - Response: {result['response_time']}s - Code: {result['status_code']}")
            else:
                error_msg = f" - Error: {result['error']}" if result['error'] else ""
                self.logger.warning(f"❌ {url} is DOWN{error_msg}")
        else:
            # Log periodic status for up sites
            if new_status == 'up':
                self.logger.info(f"✅ {url} - Response: {result['response_time']}s - Code: {result['status_code']}")
    
    def monitor_url(self, url_config: Dict):
        """Monitor a single URL in a loop."""
        url = url_config['url']
        interval = url_config.get('interval', 60)
        
        print(f"Starting monitor for {url} (interval: {interval}s)")
        
        while self.running:
            try:
                result = self.check_url(url_config)
                
                # Check for status changes
                old_status = self.status_cache.get(url, {}).get('status', 'unknown')
                new_status = result['status']
                
                # Update cache
                self.status_cache[url] = result
                
                # Log results
                self._log_status_change(url, old_status, new_status, result)
                
                # Log detailed info to file
                log_entry = json.dumps(result)
                with open(f"{self.config['log_file']}.json", 'a') as f:
                    f.write(log_entry + '\n')
                
            except Exception as e:
                self.logger.error(f"Monitor error for {url}: {e}")
            
            # Wait for next check
            time.sleep(interval)
    
    def start(self):
        """Start monitoring all configured URLs."""
        if self.running:
            print("Monitor already running")
            return
            
        self.running = True
        print(f"Starting URL Monitor with {len(self.config['urls'])} URLs")
        
        # Create monitoring threads
        for url_config in self.config['urls']:
            thread = threading.Thread(
                target=self.monitor_url,
                args=(url_config,),
                daemon=