```python
"""
Website Monitoring Script

A self-contained Python script that monitors a predefined list of URLs by:
- Pinging URLs every 5 minutes
- Measuring response times and capturing status codes
- Storing results in SQLite database with proper schema
- Handling errors gracefully and providing stdout feedback

Tables:
- sites: stores monitored URLs and metadata
- monitoring_logs: stores ping results with timestamps
- alerts: stores alert conditions and notifications

Dependencies: requests (for HTTP requests), sqlite3 (built-in)
Usage: python script.py
"""

import sqlite3
import time
import requests
import threading
from datetime import datetime
from typing import List, Tuple, Optional

class WebsiteMonitor:
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.urls = [
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://python.org",
            "https://httpbin.org/status/200"
        ]
        self.setup_database()
        self.populate_sites()
        
    def setup_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Monitoring logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER,
                    status_code INTEGER,
                    response_time REAL,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error_message TEXT,
                    FOREIGN KEY (site_id) REFERENCES sites (id)
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER,
                    alert_type TEXT,
                    message TEXT,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (site_id) REFERENCES sites (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✓ Database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"✗ Database setup failed: {e}")
            
    def populate_sites(self):
        """Insert predefined URLs into sites table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for url in self.urls:
                cursor.execute(
                    "INSERT OR IGNORE INTO sites (url, name) VALUES (?, ?)",
                    (url, url.replace("https://", "").replace("http://", ""))
                )
            
            conn.commit()
            conn.close()
            print(f"✓ Sites populated: {len(self.urls)} URLs")
            
        except Exception as e:
            print(f"✗ Site population failed: {e}")
            
    def get_site_id(self, url: str) -> Optional[int]:
        """Get site ID from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM sites WHERE url = ?", (url,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            print(f"✗ Failed to get site ID for {url}: {e}")
            return None
            
    def ping_url(self, url: str) -> Tuple[Optional[int], Optional[float], Optional[str]]:
        """Ping a single URL and return status code, response time, and error message"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = round((time.time() - start_time) * 1000, 2)  # Convert to ms
            return response.status_code, response_time, None
            
        except requests.exceptions.Timeout:
            return None, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return None, None, "Connection error"
        except requests.exceptions.RequestException as e:
            return None, None, f"Request failed: {str(e)}"
        except Exception as e:
            return None, None, f"Unexpected error: {str(e)}"
            
    def log_result(self, site_id: int, status_code: Optional[int], 
                  response_time: Optional[float], error_message: Optional[str]):
        """Store monitoring result in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO monitoring_logs 
                (site_id, status_code, response_time, error_message)
                VALUES (?, ?, ?, ?)
            ''', (site_id, status_code, response_time, error_message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"✗ Failed to log result: {e}")
            
    def create_alert(self, site_id: int, alert_type: str, message: str):
        """Create an alert for monitoring issues"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (site_id, alert_type, message)
                VALUES (?, ?, ?)
            ''', (site_id, alert_type, message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"✗ Failed to create alert: {e}")
            
    def monitor_sites(self):
        """Monitor all sites and handle results"""
        print(f"\n🔍 Monitoring cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for url in self.urls:
            try:
                site_id = self.get_site_id(url)
                if not site_id:
                    print(f"✗ No site ID found for {url}")
                    continue
                    
                status_code, response_time, error_message = self.ping_url(url)
                
                # Log the result
                self.log_result(site_id, status_code, response_time, error_message)
                
                # Print status
                if error_message:
                    print(f"✗ {url}: {error_message}")
                    self.create_alert(site_id, "ERROR", error_message)
                elif status_code and status_code >= 400:
                    print(f"⚠ {url}: HTTP {status_code} ({response_time}ms)")
                    self.create_alert(site_id, "HTTP_ERROR", f"Status code: {status_code}")
                elif response_time and response_time > 5000:  # 5 seconds
                    print(f"🐌 {url}: HTTP {status_code} ({response_time}ms) - SLOW")
                    self.create_alert(site_id, "SLOW_RESPONSE", f"Response time: {response_time}ms")
                else:
                    print(f"✓ {url}: HTTP {status_code} ({response_time}ms)")
                    
            except Exception as e:
                print(f"✗ Unexpected error monitoring {url}: {e}")
                
        print(f"📊 Monitoring cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
    def get_recent_stats(self):
        """Display recent monitoring statistics"""
        try:
            conn = sqlite