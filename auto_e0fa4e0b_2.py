```python
#!/usr/bin/env python3
"""
Website Content Monitoring Scheduler

This module implements a configurable website monitoring system that:
- Periodically checks websites for content changes using hash comparison
- Stores baseline content hashes in a local JSON file
- Triggers notifications when changes are detected
- Automatically updates baseline hashes after detecting changes
- Uses APScheduler for flexible scheduling configuration

The script monitors websites by computing SHA-256 hashes of their content
and comparing against stored baselines. When changes are detected, it
logs the changes and optionally sends notifications.

Usage: python script.py

Requirements: httpx, apscheduler
"""

import json
import hashlib
import logging
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    import httpx
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.interval import IntervalTrigger
except ImportError as e:
    print(f"Error: Missing required dependencies. Install with: pip install httpx apscheduler")
    print(f"Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebsiteMonitor:
    """Website content monitoring system with hash-based change detection."""
    
    def __init__(self, config_file: str = "monitor_config.json", baseline_file: str = "baselines.json"):
        self.config_file = Path(config_file)
        self.baseline_file = Path(baseline_file)
        self.scheduler = BlockingScheduler()
        self.client = httpx.Client(timeout=30.0)
        
        # Load configuration and baselines
        self.config = self._load_config()
        self.baselines = self._load_baselines()
        
    def _load_config(self) -> dict:
        """Load monitoring configuration from JSON file."""
        default_config = {
            "websites": [
                {"url": "https://httpbin.org/json", "name": "HTTPBin Test"},
                {"url": "https://api.github.com/zen", "name": "GitHub Zen"}
            ],
            "check_interval_minutes": 5,
            "notification": {
                "enabled": True,
                "method": "console"  # console, email, webhook
            },
            "user_agent": "WebsiteMonitor/1.0"
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default configuration at {self.config_file}")
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config
    
    def _load_baselines(self) -> dict:
        """Load baseline content hashes from JSON file."""
        try:
            if self.baseline_file.exists():
                with open(self.baseline_file, 'r') as f:
                    baselines = json.load(f)
                logger.info(f"Loaded {len(baselines)} baselines from {self.baseline_file}")
                return baselines
            else:
                logger.info(f"No baseline file found at {self.baseline_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading baselines: {e}")
            return {}
    
    def _save_baselines(self):
        """Save current baselines to JSON file."""
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(self.baselines, f, indent=2)
            logger.info(f"Saved baselines to {self.baseline_file}")
        except Exception as e:
            logger.error(f"Error saving baselines: {e}")
    
    def _compute_content_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _fetch_website_content(self, url: str) -> Optional[str]:
        """Fetch website content and return as string."""
        try:
            headers = {"User-Agent": self.config.get("user_agent", "WebsiteMonitor/1.0")}
            response = self.client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    def _send_notification(self, website_name: str, url: str, old_hash: str, new_hash: str):
        """Send notification about website change."""
        try:
            if not self.config.get("notification", {}).get("enabled", False):
                return
            
            method = self.config.get("notification", {}).get("method", "console")
            
            message = (
                f"CHANGE DETECTED: {website_name}\n"
                f"URL: {url}\n"
                f"Old hash: {old_hash[:16]}...\n"
                f"New hash: {new_hash[:16]}...\n"
                f"Timestamp: {datetime.now().isoformat()}"
            )
            
            if method == "console":
                print("=" * 50)
                print("🚨 WEBSITE CHANGE ALERT 🚨")
                print("=" * 50)
                print(message)
                print("=" * 50)
            
            # Additional notification methods can be implemented here
            # elif method == "email":
            #     self._send_email_notification(message)
            # elif method == "webhook":
            #     self._send_webhook_notification(message)
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def check_website(self, website: dict) -> bool:
        """Check a single website for changes. Returns True if changed."""
        url = website["url"]
        name = website["name"]
        
        try:
            logger.info(f"Checking {name} ({url})")
            
            # Fetch current content
            current_content = self._fetch_website_content(url)
            if current_content is None:
                logger.warning(f"Failed to fetch content for {name}")
                return False
            
            # Compute current hash
            current_hash = self._compute_content_hash(current_content)
            
            # Get baseline hash
            baseline_hash = self.baselines.get(url)
            
            if baseline_hash is None:
                # First time checking this website
                self.baselines[url] = current_hash
                self._save_baselines()
                logger.info(f"Stored initial baseline for {name}: {current_hash[:16]}...")
                return False
            
            # Compare hashes
            if current_hash != baseline_hash:
                logger.warning(f"Content changed for {name}!")
                self._send_notification(name, url, baseline_hash, current_hash)
                
                # Update baseline
                self.baselines[url] = current_hash
                self._save_baselines()
                
                return True
            else:
                logger.info(f"No changes detected for {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking {name}: {e}")
            return False
    
    def check_all_websites(self):
        """Check all configured websites for changes."""
        try: