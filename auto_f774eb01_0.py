```python
"""
Stock Portfolio Management System

A self-contained Python script that fetches real-time stock data using yfinance API,
establishes database connection to store portfolio holdings, and implements basic
data validation for ticker symbols.

Features:
- Real-time stock data retrieval
- SQLite database for portfolio storage
- Ticker symbol validation
- Error handling and logging
- Portfolio performance tracking

Usage: python script.py
"""

import sqlite3
import json
import re
import time
from datetime import datetime, timedelta
import httpx


class StockPortfolioManager:
    def __init__(self, db_path="portfolio.db"):
        self.db_path = db_path
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Portfolio holdings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    shares REAL NOT NULL,
                    avg_price REAL NOT NULL,
                    purchase_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Stock data cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume INTEGER,
                    market_cap REAL,
                    pe_ratio REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ticker, timestamp)
                )
            """)
            
            # Revenue metrics table for tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    transaction_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def validate_ticker(self, ticker):
        """Validate ticker symbol format"""
        if not ticker or not isinstance(ticker, str):
            return False
        
        # Basic ticker validation (1-5 alphanumeric characters)
        pattern = r'^[A-Za-z]{1,5}$'
        return bool(re.match(pattern, ticker.upper()))
    
    def fetch_stock_data(self, ticker):
        """Fetch real-time stock data using Yahoo Finance API"""
        if not self.validate_ticker(ticker):
            raise ValueError(f"Invalid ticker symbol: {ticker}")
        
        ticker = ticker.upper()
        
        try:
            with httpx.Client(timeout=10.0) as client:
                url = f"{self.base_url}/{ticker}"
                params = {
                    'interval': '1d',
                    'range': '1d',
                    'includePrePost': 'false'
                }
                
                response = client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'chart' not in data or not data['chart']['result']:
                    raise ValueError(f"No data found for ticker: {ticker}")
                
                result = data['chart']['result'][0]
                meta = result['meta']
                
                stock_info = {
                    'ticker': ticker,
                    'price': meta.get('regularMarketPrice', 0),
                    'volume': meta.get('regularMarketVolume', 0),
                    'market_cap': meta.get('marketCap', 0),
                    'pe_ratio': meta.get('trailingPE', 0),
                    'currency': meta.get('currency', 'USD'),
                    'exchange': meta.get('exchangeName', 'Unknown'),
                    'timestamp': datetime.now().isoformat()
                }
                
                return stock_info
                
        except httpx.TimeoutException:
            raise Exception(f"Timeout while fetching data for {ticker}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code} for {ticker}")
        except Exception as e:
            raise Exception(f"Error fetching data for {ticker}: {e}")
    
    def store_stock_data(self, stock_data):
        """Store stock data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO stock_data 
                (ticker, price, volume, market_cap, pe_ratio)
                VALUES (?, ?, ?, ?, ?)
            """, (
                stock_data['ticker'],
                stock_data['price'],
                stock_data['volume'],
                stock_data['market_cap'],
                stock_data['pe_ratio']
            ))
            
            conn.commit()
            conn.close()
            print(f"Stored data for {stock_data['ticker']}")
            
        except Exception as e:
            print(f"Error storing stock data: {e}")
    
    def add_portfolio_holding(self, ticker, shares, avg_price):
        """Add a stock holding to portfolio"""
        if not self.validate_ticker(ticker):
            raise ValueError(f"Invalid ticker symbol: {ticker}")
        
        if shares <= 0 or avg_price <= 0:
            raise ValueError("Shares and price must be positive numbers")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO portfolio (ticker, shares, avg_price, purchase_date)
                VALUES (?, ?, ?, ?)
            """, (ticker.upper(), shares, avg_price, datetime.now().date().isoformat()))
            
            conn.commit()
            conn.close()
            print(f"Added {shares} shares of {ticker.upper()} at ${avg_price:.2f}")
            
        except Exception as e:
            print(f"Error adding portfolio holding: {e}")
    
    def get_portfolio_value(self):
        """Calculate current portfolio value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT ticker, SUM(shares), AVG(avg_price) FROM portfolio GROUP BY ticker")
            holdings = cursor.fetchall()
            
            total_value = 0
            total_cost = 0
            portfolio_summary = []
            
            for ticker, shares, avg_price in holdings:
                try:
                    stock_data = self.fetch_stock_data(ticker)
                    current_price = stock_data['price']
                    
                    position_value = shares * current_price
                    position_cost = shares * avg_price
                    gain_loss = position_value - position_cost
                    gain_loss_pct = (gain_loss / position_cost) * 100 if position_cost > 0 else 0
                    
                    portfolio_summary.append({
                        'ticker': ticker,
                        'shares': shares,
                        'avg_price': avg_price,
                        'current_price': current_price,
                        'position_value': position_value,
                        'gain_loss': gain_loss,
                        'gain_loss_pct': gain_loss_pct
                    })
                    
                    total_value += position_value
                    total_cost += position_cost
                    
                    # Store current data
                    self.store_stock_data(stock_data)
                    
                except Exception as e:
                    print(f"Error processing {ticker}: {e}")
                    continue
            
            conn.close()
            
            total_gain_loss = total_value - total_cost