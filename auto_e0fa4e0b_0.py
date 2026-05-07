```python
#!/usr/bin/env python3
"""
Website Content Monitor and Hash Generator

This script scrapes specified websites, extracts content from defined sections,
generates SHA256 hashes of the content, and maintains a baseline configuration
in JSON format. It can be used for content change detection and monitoring.

Features:
- Scrapes multiple websites using HTTP requests
- Extracts content from specified CSS selectors or XPath expressions
- Generates SHA256 hashes for content integrity checking
- Stores and updates baseline hashes in JSON configuration
- Self-contained with minimal dependencies

Usage: python script.py
"""

import json
import hashlib
import sys
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not found. Install with: pip install httpx beautifulsoup4")
    sys.exit(1)


class WebContentMonitor:
    """Main class for monitoring website content changes via hash comparison."""
    
    def __init__(self, config_file: str = "content_monitor_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.session = httpx.Client(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file or create default config."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Creating default configuration.")
            default_config = {
                "targets": [
                    {
                        "url": "https://example.com",
                        "name": "Example Site",
                        "selectors": [
                            {"name": "title", "selector": "title", "type": "css"},
                            {"name": "main_content", "selector": "main", "type": "css"}
                        ]
                    }
                ],
                "baselines": {}
            }
            self.save_config(default_config)
            return default_config
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            sys.exit(1)
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except httpx.RequestError as e:
            print(f"Request error for {url}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error for {url}: {e.response.status_code}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching {url}: {e}")
            return None
    
    def extract_content(self, soup: BeautifulSoup, selector_config: Dict[str, str]) -> str:
        """Extract content from parsed HTML using CSS selector or XPath."""
        try:
            selector_type = selector_config.get('type', 'css').lower()
            selector = selector_config['selector']
            
            if selector_type == 'css':
                elements = soup.select(selector)
            else:
                # Basic XPath-like functionality (simplified)
                if selector.startswith('//'):
                    tag_name = selector.split('//')[1].split('[')[0]
                    elements = soup.find_all(tag_name)
                else:
                    elements = soup.select(selector)
            
            if not elements:
                return ""
            
            # Extract text content from all matching elements
            content_parts = []
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    content_parts.append(text)
            
            return '\n'.join(content_parts)
        
        except Exception as e:
            print(f"Error extracting content with selector '{selector_config}': {e}")
            return ""
    
    def generate_hash(self, content: str) -> str:
        """Generate SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def process_target(self, target_config: Dict[str, Any]) -> Dict[str, str]:
        """Process a single target website and return content hashes."""
        url = target_config['url']
        name = target_config.get('name', url)
        selectors = target_config.get('selectors', [])
        
        print(f"\nProcessing: {name} ({url})")
        
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        hashes = {}
        for selector_config in selectors:
            selector_name = selector_config.get('name', 'unnamed')
            content = self.extract_content(soup, selector_config)
            
            if content:
                content_hash = self.generate_hash(content)
                hashes[selector_name] = content_hash
                print(f"  ✓ {selector_name}: {content_hash[:16]}... ({len(content)} chars)")
            else:
                print(f"  ✗ {selector_name}: No content found")
        
        return hashes
    
    def compare_with_baseline(self, target_key: str, current_hashes: Dict[str, str]) -> None:
        """Compare current hashes with baseline and report changes."""
        baseline = self.config['baselines'].get(target_key, {})
        
        if not baseline:
            print(f"  → No baseline found. Setting new baseline.")
            self.config['baselines'][target_key] = current_hashes
            return
        
        changes_detected = False
        for selector_name, current_hash in current_hashes.items():
            baseline_hash = baseline.get(selector_name)
            
            if baseline_hash is None:
                print(f"  → NEW: {selector_name}")
                changes_detected = True
            elif baseline_hash != current_hash:
                print(f"  → CHANGED: {selector_name}")
                print(f"    Old: {baseline_hash[:16]}...")
                print(f"    New: {current_hash[:16]}...")
                changes_detected = True
        
        # Check for removed selectors
        for selector_name in baseline:
            if selector_name not in current_hashes:
                print(f"  → REMOVED: {selector_name}")
                changes_detected = True
        
        if not changes_detected:
            print(f"  → No changes detected")
        
        # Update baseline with current hashes
        self.config['baselines'][target_key] = current_hashes
    
    def run(self) -> None:
        """Main execution method."""
        print("Website Content Monitor Starting...")
        print(f"Configuration file: {self.config_file}")
        
        if not self.config.get('targets'):
            print("No targets configured. Please edit the configuration file.")
            return
        
        for i, target_config in enumerate(self.config['targets']):
            try:
                target_key = f"target_{i}_{urlparse(target_config['url']).netloc}"
                current_hashes = self.process_target(target_config)
                
                if current_hashes:
                    self.compare_with_baseline(target_key,