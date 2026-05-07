```python
"""
Stock Portfolio Analyzer

This module fetches real-time stock data from Alpha Vantage API and calculates
essential portfolio metrics including current value, daily changes, and technical
indicators like moving averages.

Features:
- Real-time stock price fetching
- Portfolio value calculation
- Daily change tracking (price and percentage)
- Simple Moving Average (SMA) calculation
- 52-week high/low analysis
- Error handling for API failures

Usage:
    python script.py

Note: Requires Alpha Vantage API key (free tier available at alphavantage.co)
Set API_KEY variable or use demo key for limited functionality.
"""

import json
import time
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from datetime import datetime, timedelta

# Configuration
API_KEY = "demo"  # Replace with your Alpha Vantage API key
BASE_URL = "https://www.alphavantage.co/query"

# Sample portfolio - modify as needed
PORTFOLIO = {
    "AAPL": {"shares": 10, "avg_cost": 150.00},
    "MSFT": {"shares": 5, "avg_cost": 300.00},
    "GOOGL": {"shares": 3, "avg_cost": 2500.00},
    "TSLA": {"shares": 8, "avg_cost": 200.00}
}

class StockAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def fetch_stock_data(self, symbol):
        """Fetch real-time stock data from Alpha Vantage API"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            url = f"{BASE_URL}?{urlencode(params)}"
            with urlopen(url) as response:
                data = json.loads(response.read().decode())
                
            if "Global Quote" not in data:
                raise ValueError(f"Invalid response for {symbol}: {data}")
                
            quote = data["Global Quote"]
            return {
                "symbol": quote["01. Symbol"],
                "price": float(quote["05. Price"]),
                "change": float(quote["09. Change"]),
                "change_percent": quote["10. Change Percent"].replace("%", ""),
                "volume": int(quote["06. Volume"]),
                "high": float(quote["03. High"]),
                "low": float(quote["04. Low"]),
                "open": float(quote["02. Open"]),
                "previous_close": float(quote["08. Previous Close"])
            }
            
        except (HTTPError, URLError) as e:
            print(f"Network error fetching {symbol}: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"Data parsing error for {symbol}: {e}")
            return None
    
    def fetch_daily_data(self, symbol, days=50):
        """Fetch daily time series data for moving averages"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            url = f"{BASE_URL}?{urlencode(params)}"
            with urlopen(url) as response:
                data = json.loads(response.read().decode())
                
            if "Time Series (Daily)" not in data:
                return None
                
            time_series = data["Time Series (Daily)"]
            prices = []
            
            for date_str, daily_data in sorted(time_series.items(), reverse=True)[:days]:
                prices.append(float(daily_data["4. close"]))
                
            return prices
            
        except Exception as e:
            print(f"Error fetching daily data for {symbol}: {e}")
            return None
    
    def calculate_moving_average(self, prices, window):
        """Calculate Simple Moving Average"""
        if len(prices) < window:
            return None
        return sum(prices[:window]) / window
    
    def analyze_portfolio(self):
        """Analyze entire portfolio and calculate metrics"""
        print("🔍 STOCK PORTFOLIO ANALYZER")
        print("=" * 50)
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_value = 0
        total_cost = 0
        total_daily_change = 0
        
        for symbol, position in PORTFOLIO.items():
            print(f"📊 Analyzing {symbol}...")
            
            # Fetch current data
            stock_data = self.fetch_stock_data(symbol)
            if not stock_data:
                print(f"❌ Failed to fetch data for {symbol}")
                continue
            
            # Calculate position metrics
            shares = position["shares"]
            avg_cost = position["avg_cost"]
            current_price = stock_data["price"]
            position_value = shares * current_price
            position_cost = shares * avg_cost
            position_gain_loss = position_value - position_cost
            position_change_percent = (position_gain_loss / position_cost) * 100
            daily_change = shares * stock_data["change"]
            
            # Fetch historical data for moving averages
            daily_prices = self.fetch_daily_data(symbol)
            sma_20 = None
            sma_50 = None
            
            if daily_prices:
                sma_20 = self.calculate_moving_average(daily_prices, 20)
                sma_50 = self.calculate_moving_average(daily_prices, 50)
            
            # Print stock analysis
            print(f"  Current Price: ${current_price:.2f}")
            print(f"  Daily Change: ${stock_data['change']:.2f} ({stock_data['change_percent']}%)")
            print(f"  Volume: {stock_data['volume']:,}")
            print(f"  Day High/Low: ${stock_data['high']:.2f}/${stock_data['low']:.2f}")
            
            if sma_20:
                print(f"  20-Day SMA: ${sma_20:.2f}")
            if sma_50:
                print(f"  50-Day SMA: ${sma_50:.2f}")
            
            print(f"  Position: {shares} shares @ ${avg_cost:.2f} avg cost")
            print(f"  Position Value: ${position_value:.2f}")
            print(f"  Position P&L: ${position_gain_loss:.2f} ({position_change_percent:+.2f}%)")
            print(f"  Daily P&L: ${daily_change:.2f}")
            print()
            
            # Update totals
            total_value += position_value
            total_cost += position_cost
            total_daily_change += daily_change
            
            # Rate limiting for free API
            time.sleep(12)  # Alpha Vantage free tier: 5 calls/minute
        
        # Portfolio summary
        total_gain_loss = total_value - total_cost
        total_change_percent = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
        
        print("💰 PORTFOLIO SUMMARY")
        print("=" * 30)
        print(f"Total Portfolio Value: ${total_value:.2f}")
        print(f"Total Cost Basis: ${total_cost:.2f}")
        print(f"Total P&L: ${total_gain_loss:.2f} ({total_change_percent:+.2f}%)")
        print(f"Daily Change: ${total_daily_change:.2f}")
        
        # Performance indicators
        if total_change_percent > 10:
            print("📈 Portfolio Performance: STRONG GAINS")
        elif total_change_percent > 0:
            print("📊 Portfolio Performance: POSITIVE")
        elif total_change_percent > -10:
            print("📉 Portfolio Performance