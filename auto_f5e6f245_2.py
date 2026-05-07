```python
"""
Cryptocurrency Price Monitoring Daemon

This module implements a configurable monitoring daemon that tracks cryptocurrency
prices at regular intervals. It checks prices, stores all data in a SQLite database,
and provides alerts when significant price changes occur.

Features:
- Configurable monitoring intervals (5-15 minutes)
- SQLite database logging for all price checks and alerts
- Error handling and recovery
- Console output for real-time monitoring
- Self-contained with minimal dependencies

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - sqlite3 (built-in)
    - threading, time, json, datetime (built-in)
"""

import sqlite3
import time
import threading
import json
import datetime
import sys
from typing import Dict, Optional, List
import logging

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)

class PriceMonitorDaemon:
    def __init__(self, db_path: str = "price_monitor.db", interval: int = 300):
        """
        Initialize the price monitoring daemon.
        
        Args:
            db_path: Path to SQLite database file
            interval: Monitoring interval in seconds (default 300 = 5 minutes)
        """
        self.db_path = db_path
        self.interval = max(300, min(900, interval))  # Clamp between 5-15 minutes
        self.running = False
        self.last_prices = {}
        self.alert_threshold = 0.05  # 5% price change threshold
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Price checks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_checks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        volume_24h REAL,
                        change_24h REAL,
                        market_cap REAL,
                        status TEXT DEFAULT 'success'
                    )
                """)
                
                # Alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        symbol TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        old_price REAL,
                        new_price REAL,
                        change_percent REAL,
                        message TEXT
                    )
                """)
                
                conn.commit()
                self.logger.info(f"Database initialized at {self.db_path}")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def _fetch_prices(self) -> Optional[Dict]:
        """
        Fetch cryptocurrency prices from CoinGecko API.
        
        Returns:
            Dictionary of price data or None if error
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                # Fetch top cryptocurrencies
                url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 10,
                    "page": 1,
                    "sparkline": False
                }
                
                response = client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                prices = {}
                
                for coin in data:
                    prices[coin['symbol'].upper()] = {
                        'price': coin['current_price'],
                        'volume_24h': coin.get('total_volume'),
                        'change_24h': coin.get('price_change_percentage_24h'),
                        'market_cap': coin.get('market_cap'),
                        'name': coin['name']
                    }
                
                return prices
                
        except httpx.RequestError as e:
            self.logger.error(f"Network error fetching prices: {e}")
            return None
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error fetching prices: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching prices: {e}")
            return None
    
    def _log_price_check(self, prices: Dict) -> None:
        """Log price check results to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for symbol, data in prices.items():
                    cursor.execute("""
                        INSERT INTO price_checks 
                        (symbol, price, volume_24h, change_24h, market_cap, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        data['price'],
                        data.get('volume_24h'),
                        data.get('change_24h'),
                        data.get('market_cap'),
                        'success'
                    ))
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Error logging price check: {e}")
    
    def _log_error(self, error_msg: str) -> None:
        """Log error to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO price_checks (symbol, price, status)
                    VALUES (?, ?, ?)
                """, ('ERROR', 0.0, error_msg))
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Error logging error to database: {e}")
    
    def _check_alerts(self, current_prices: Dict) -> List[Dict]:
        """Check for price alerts based on threshold changes."""
        alerts = []
        
        for symbol, current_data in current_prices.items():
            if symbol in self.last_prices:
                old_price = self.last_prices[symbol]['price']
                new_price = current_data['price']
                
                if old_price > 0:
                    change_percent = (new_price - old_price) / old_price
                    
                    if abs(change_percent) >= self.alert_threshold:
                        alert_type = "PRICE_SURGE" if change_percent > 0 else "PRICE_DROP"
                        
                        alert = {
                            'symbol': symbol,
                            'alert_type': alert_type,
                            'old_price': old_price,
                            'new_price': new_price,
                            'change_percent': change_percent,
                            'message': f"{symbol} {alert_type.lower()}: {change_percent:.2%} change"
                        }
                        alerts.append(alert)
        
        return alerts
    
    def _log_alerts(self, alerts: List[Dict]) -> None:
        """Log alerts to database."""
        if not alerts:
            return
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for alert in alerts:
                    cursor.execute("""
                        INSERT INTO alerts 
                        (symbol, alert_type, old_price, new_price, change_percent, message)
                        VALUES (?, ?, ?, ?,