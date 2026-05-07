```python
"""
Web Content Change Monitor

This script fetches webpage content using the httpx library, compares it with a 
previously stored version, and identifies changes between the two versions. 
The script stores the current content for future comparisons and outputs 
detected changes to stdout.

Features:
- Fetches web content with proper error handling
- Stores content locally for version comparison
- Identifies and reports content changes
- Self-contained with minimal dependencies (httpx for HTTP requests)
- Comprehensive error handling for network and file operations

Usage:
    python script.py

The script will prompt for a URL or use a default example URL for demonstration.
"""

import httpx
import hashlib
import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any


class WebContentMonitor:
    """Monitor web content changes by comparing current and stored versions."""
    
    def __init__(self, storage_dir: str = "web_monitor_data"):
        """
        Initialize the web content monitor.
        
        Args:
            storage_dir: Directory to store previous content versions
        """
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self) -> None:
        """Create storage directory if it doesn't exist."""
        try:
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)
        except OSError as e:
            print(f"Error creating storage directory: {e}")
            sys.exit(1)
    
    def _get_storage_path(self, url: str) -> str:
        """
        Generate a safe filename for storing URL content.
        
        Args:
            url: The URL to generate a filename for
            
        Returns:
            Path to the storage file
        """
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        return os.path.join(self.storage_dir, f"{url_hash}.json")
    
    def fetch_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch content from a URL.
        
        Args:
            url: URL to fetch content from
            
        Returns:
            Dictionary containing content data or None on failure
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                content_data = {
                    'url': url,
                    'content': response.text,
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'timestamp': datetime.now().isoformat(),
                    'content_length': len(response.text),
                    'content_hash': hashlib.sha256(response.text.encode('utf-8')).hexdigest()
                }
                
                print(f"Successfully fetched content from {url}")
                print(f"Status Code: {response.status_code}")
                print(f"Content Length: {len(response.text)} characters")
                
                return content_data
                
        except httpx.TimeoutException:
            print(f"Error: Timeout while fetching {url}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"Error: HTTP {e.response.status_code} while fetching {url}")
            return None
        except httpx.RequestError as e:
            print(f"Error: Network error while fetching {url} - {e}")
            return None
        except Exception as e:
            print(f"Error: Unexpected error while fetching {url} - {e}")
            return None
    
    def load_previous_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Load previously stored content for a URL.
        
        Args:
            url: URL to load previous content for
            
        Returns:
            Dictionary containing previous content data or None if not found
        """
        storage_path = self._get_storage_path(url)
        
        try:
            if os.path.exists(storage_path):
                with open(storage_path, 'r', encoding='utf-8') as f:
                    previous_data = json.load(f)
                    print(f"Loaded previous content from {previous_data.get('timestamp', 'unknown time')}")
                    return previous_data
            else:
                print("No previous content found for this URL")
                return None
                
        except json.JSONDecodeError as e:
            print(f"Error: Corrupted storage file - {e}")
            return None
        except IOError as e:
            print(f"Error: Could not read storage file - {e}")
            return None
        except Exception as e:
            print(f"Error: Unexpected error loading previous content - {e}")
            return None
    
    def store_content(self, content_data: Dict[str, Any]) -> bool:
        """
        Store content data for future comparisons.
        
        Args:
            content_data: Content data to store
            
        Returns:
            True if successfully stored, False otherwise
        """
        storage_path = self._get_storage_path(content_data['url'])
        
        try:
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, indent=2, ensure_ascii=False)
            print(f"Content stored successfully")
            return True
            
        except IOError as e:
            print(f"Error: Could not write storage file - {e}")
            return False
        except Exception as e:
            print(f"Error: Unexpected error storing content - {e}")
            return False
    
    def compare_content(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare current and previous content versions.
        
        Args:
            current: Current content data
            previous: Previous content data
            
        Returns:
            Dictionary containing comparison results
        """
        comparison = {
            'has_changes': False,
            'hash_changed': False,
            'length_changed': False,
            'status_changed': False,
            'changes': {}
        }
        
        # Compare content hashes
        if current['content_hash'] != previous['content_hash']:
            comparison['has_changes'] = True
            comparison['hash_changed'] = True
        
        # Compare content lengths
        current_length = current['content_length']
        previous_length = previous['content_length']
        
        if current_length != previous_length:
            comparison['has_changes'] = True
            comparison['length_changed'] = True
            comparison['changes']['length_diff'] = current_length - previous_length
        
        # Compare status codes
        if current['status_code'] != previous['status_code']:
            comparison['has_changes'] = True
            comparison['status_changed'] = True
            comparison['changes']['status_change'] = {
                'from': previous['status_code'],
                'to': current['status_code']
            }
        
        # Simple content difference analysis (first 500 chars)
        if comparison['hash_changed']:
            current_preview = current['content'][:500]
            previous_preview = previous['content'][:500]
            
            if current_preview != previous_preview:
                comparison['changes']['content_preview_changed'] = True
        
        return comparison
    
    def print_comparison_report(self, comparison: Dict[str, Any], current: Dict[str, Any], previous: Dict[str, Any]) -> None:
        """
        Print a detailed comparison report.
        
        Args:
            comparison: Comparison results
            current: Current content data
            previous: Previous content data
        """
        print("\n" + "="*60)
        print("CONTENT CHANGE REPORT")
        print("="*60)
        
        print(f"URL: {current['url']}")
        print(f"Current Timestamp: {current['timestamp']}")
        print(f"Previous Timestamp: {previous['timestamp']}")
        
        if not comparison['has_changes']:
            print("\n✅ NO CHANGES DETECTED")
            print("The content is identical to the previous version.")
        else: