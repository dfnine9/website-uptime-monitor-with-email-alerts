```python
#!/usr/bin/env python3
"""
Portfolio Analytics System
=========================

A comprehensive stock portfolio analysis tool that fetches real-time market data,
calculates advanced portfolio metrics, and maintains persistent storage for
revenue tracking and performance analysis.

Features:
- Real-time stock data retrieval via Yahoo Finance API
- Portfolio metrics calculation (returns, volatility, Sharpe ratio, beta)
- SQLite database storage for revenue metrics tracking
- Risk-adjusted performance analysis
- Automated portfolio rebalancing suggestions

Author: T.O.A.A Revenue Swarm - Trading Division
"""

import sqlite3
import json
import time
import math
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import ssl

class PortfolioAnalyzer:
    def __init__(self, db_path="revenue_metrics.db"):
        self.db_path = db_path
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with revenue metrics tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Revenue metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    portfolio_value REAL,
                    daily_return REAL,
                    volatility REAL,
                    sharpe_ratio REAL,
                    beta REAL,
                    symbol TEXT,
                    price REAL,
                    change_pct REAL
                )
            """)
            
            # Portfolio holdings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_holdings (
                    symbol TEXT PRIMARY KEY,
                    shares REAL,
                    avg_cost REAL,
                    last_updated TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def fetch_stock_data(self, symbol):
        """Fetch real-time stock data from Yahoo Finance API."""
        try:
            # Yahoo Finance API endpoint
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            # Create SSL context to handle certificates
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urlopen(req, context=context, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                
                current_price = meta.get('regularMarketPrice', 0)
                prev_close = meta.get('previousClose', current_price)
                change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                
                # Get historical data for volatility calculation
                timestamps = result.get('timestamp', [])
                quotes = result.get('indicators', {}).get('quote', [{}])[0]
                closes = quotes.get('close', [])
                
                return {
                    'symbol': symbol,
                    'price': current_price,
                    'prev_close': prev_close,
                    'change_pct': change_pct,
                    'volume': meta.get('regularMarketVolume', 0),
                    'historical_closes': [c for c in closes if c is not None][-30:],  # Last 30 days
                    'market_cap': meta.get('marketCap', 0)
                }
            else:
                raise ValueError(f"No data found for {symbol}")
                
        except (URLError, HTTPError, ValueError) as e:
            print(f"⚠️ Error fetching data for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error for {symbol}: {e}")
            return None
    
    def calculate_returns(self, prices):
        """Calculate daily returns from price series."""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] and prices[i]:
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
        return returns
    
    def calculate_volatility(self, returns):
        """Calculate annualized volatility from daily returns."""
        if len(returns) < 2:
            return 0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        daily_vol = math.sqrt(variance)
        annual_vol = daily_vol * math.sqrt(252)  # 252 trading days
        return annual_vol
    
    def calculate_sharpe_ratio(self, returns, volatility):
        """Calculate Sharpe ratio (risk-adjusted returns)."""
        if volatility == 0:
            return 0
        
        avg_return = sum(returns) / len(returns) if returns else 0
        annual_return = avg_return * 252  # Annualized
        excess_return = annual_return - self.risk_free_rate
        return excess_return / volatility
    
    def calculate_beta(self, stock_returns, market_returns):
        """Calculate stock beta relative to market."""
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
            return 1.0
        
        # Calculate covariance and market variance
        stock_mean = sum(stock_returns) / len(stock_returns)
        market_mean = sum(market_returns) / len(market_returns)
        
        covariance = sum((stock_returns[i] - stock_mean) * (market_returns[i] - market_mean) 
                        for i in range(len(stock_returns))) / (len(stock_returns) - 1)
        
        market_variance = sum((r - market_mean) ** 2 for r in market_returns) / (len(market_returns) - 1)
        
        return covariance / market_variance if market_variance != 0 else 1.0
    
    def store_metrics(self, metrics):
        """Store portfolio metrics in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO revenue_metrics 
                (timestamp, portfolio_value, daily_return, volatility, sharpe_ratio, beta, symbol, price, change_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                metrics.get('portfolio_value', 0),
                metrics.get('daily_return', 0),
                metrics.get('volatility', 0),
                metrics.get('sharpe_ratio', 0),
                metrics.get('beta', 1.0),
                metrics.get('symbol', ''),
                metrics.get('price', 0),
                metrics.get('change_pct', 0)
            ))
            
            conn.commit()
            conn.close()
            print(f"💾 Stored metrics for {metrics.get('symbol', 'Portfolio')}")
        except Exception as e:
            print(f"❌ Database storage error: {e}")
    
    def analyze_portfolio(self, symbols, weights=None):
        """Analyze a portfolio of stocks."""
        if not symbols:
            symbols = ['AAPL', '