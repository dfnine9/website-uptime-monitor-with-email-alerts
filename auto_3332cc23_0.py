```python
"""
Portfolio Analytics and Reporting System

This module fetches stock prices from Yahoo Finance API, calculates key portfolio 
performance metrics including returns, volatility, and Sharpe ratio, then generates 
comprehensive HTML reports with embedded charts for daily portfolio analysis.

Features:
- Real-time stock price fetching via Yahoo Finance API
- Portfolio metrics calculation (returns, volatility, Sharpe ratio)
- HTML report generation with performance visualizations
- Error handling and logging
- Self-contained execution

Usage: python script.py
"""

import json
import datetime
import math
import sqlite3
import os
from typing import Dict, List, Tuple, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    exit(1)

class PortfolioAnalyzer:
    def __init__(self, portfolio: Dict[str, float]):
        """Initialize with portfolio holdings {symbol: shares}"""
        self.portfolio = portfolio
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        self.db_path = "revenue_metrics.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for revenue tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_metrics (
                    date TEXT PRIMARY KEY,
                    total_value REAL,
                    daily_return REAL,
                    volatility REAL,
                    sharpe_ratio REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            print(f"✓ Database initialized: {self.db_path}")
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def fetch_stock_price(self, symbol: str) -> Optional[float]:
        """Fetch current stock price from Yahoo Finance API"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                
                data = response.json()
                result = data['chart']['result'][0]
                current_price = result['meta']['regularMarketPrice']
                
                print(f"✓ {symbol}: ${current_price:.2f}")
                return float(current_price)
                
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def fetch_historical_prices(self, symbol: str, days: int = 30) -> List[float]:
        """Fetch historical prices for volatility calculation"""
        try:
            period1 = int((datetime.datetime.now() - datetime.timedelta(days=days)).timestamp())
            period2 = int(datetime.datetime.now().timestamp())
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': period1,
                'period2': period2,
                'interval': '1d'
            }
            
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                result = data['chart']['result'][0]
                closes = result['indicators']['quote'][0]['close']
                
                # Filter out None values
                prices = [price for price in closes if price is not None]
                return prices[-min(days, len(prices)):]  # Last N days
                
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """Calculate daily returns from price series"""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
        
        return returns
    
    def calculate_volatility(self, returns: List[float]) -> float:
        """Calculate annualized volatility from daily returns"""
        if len(returns) < 2:
            return 0.0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        daily_vol = math.sqrt(variance)
        annualized_vol = daily_vol * math.sqrt(252)  # 252 trading days
        
        return annualized_vol
    
    def calculate_sharpe_ratio(self, returns: List[float], volatility: float) -> float:
        """Calculate Sharpe ratio"""
        if volatility == 0 or len(returns) == 0:
            return 0.0
        
        mean_return = sum(returns) / len(returns)
        annualized_return = mean_return * 252
        
        sharpe = (annualized_return - self.risk_free_rate) / volatility
        return sharpe
    
    def analyze_portfolio(self) -> Dict:
        """Analyze entire portfolio and return metrics"""
        portfolio_data = {}
        total_value = 0.0
        all_returns = []
        
        print("\n🔍 Fetching portfolio data...")
        
        for symbol, shares in self.portfolio.items():
            current_price = self.fetch_stock_price(symbol)
            if current_price is None:
                continue
            
            position_value = current_price * shares
            total_value += position_value
            
            # Get historical data for returns calculation
            historical_prices = self.fetch_historical_prices(symbol, 30)
            returns = self.calculate_returns(historical_prices)
            
            portfolio_data[symbol] = {
                'price': current_price,
                'shares': shares,
                'value': position_value,
                'returns': returns,
                'weight': 0  # Will calculate after total_value known
            }
            
            # Weight returns by position size for portfolio calculation
            weighted_returns = [r * position_value for r in returns]
            all_returns.extend(weighted_returns)
        
        # Calculate portfolio weights
        for symbol in portfolio_data:
            portfolio_data[symbol]['weight'] = portfolio_data[symbol]['value'] / total_value
        
        # Calculate portfolio-level metrics
        if total_value > 0:
            portfolio_returns = [r / total_value for r in all_returns]
        else:
            portfolio_returns = []
        
        volatility = self.calculate_volatility(portfolio_returns)
        sharpe_ratio = self.calculate_sharpe_ratio(portfolio_returns, volatility)
        daily_return = portfolio_returns[-1] if portfolio_returns else 0.0
        
        metrics = {
            'total_value': total_value,
            'daily_return': daily_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'positions': portfolio_data,
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        }
        
        # Log to database
        self.log_metrics(metrics)
        
        return metrics
    
    def log_metrics(self, metrics: Dict):
        """Log portfolio metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO portfolio_metrics 
                (date, total_value, daily_return, volatility, sharpe_ratio)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                metrics['date'],
                metrics['total_value'],
                metrics['daily_return'],
                metrics['volatility'],
                metrics['sharpe_ratio']
            ))