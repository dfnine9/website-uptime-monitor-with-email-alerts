```python
"""
Alpha Vantage Stock Portfolio Monitor

This module connects to the Alpha Vantage API to fetch real-time stock prices
for a predefined portfolio. It implements rate limiting, error handling, and
stores data in a structured JSON format.

Features:
- Rate limiting (5 requests per minute for free tier)
- Comprehensive error handling
- Structured data storage
- Real-time price monitoring
- Portfolio performance tracking

Usage: python script.py
"""

import json
import time
import sys
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from datetime import datetime
import os

class StockPortfolioMonitor:
    def __init__(self, api_key=None):
        # Demo API key - replace with your own
        self.api_key = api_key or "demo"
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_delay = 12  # 5 requests per minute = 12 seconds between calls
        self.last_request_time = 0
        
        # Predefined portfolio - major tech stocks
        self.portfolio = [
            {"symbol": "AAPL", "shares": 10},
            {"symbol": "MSFT", "shares": 5},
            {"symbol": "GOOGL", "shares": 3},
            {"symbol": "TSLA", "shares": 2},
            {"symbol": "AMZN", "shares": 4}
        ]
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "portfolio_data": [],
            "total_value": 0.0,
            "errors": []
        }

    def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _make_api_request(self, symbol):
        """Make API request with error handling"""
        try:
            self._rate_limit()
            
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            url = f"{self.base_url}?{urlencode(params)}"
            print(f"Fetching data for {symbol}...")
            
            with urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"API Error: {data['Error Message']}")
            
            if "Note" in data:
                raise Exception(f"API Rate Limit: {data['Note']}")
            
            # Check for valid quote data
            if "Global Quote" not in data:
                raise Exception(f"No quote data returned for {symbol}")
            
            quote = data["Global Quote"]
            if not quote:
                raise Exception(f"Empty quote data for {symbol}")
            
            return quote
            
        except HTTPError as e:
            error_msg = f"HTTP Error {e.code} for {symbol}: {e.reason}"
            self.results["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            return None
            
        except URLError as e:
            error_msg = f"Network Error for {symbol}: {e.reason}"
            self.results["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            return None
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON Decode Error for {symbol}: {str(e)}"
            self.results["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            return None
            
        except Exception as e:
            error_msg = f"Unexpected Error for {symbol}: {str(e)}"
            self.results["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            return None

    def _parse_quote_data(self, quote_data, stock_info):
        """Parse and structure quote data"""
        try:
            price = float(quote_data.get("05. price", 0))
            change = float(quote_data.get("09. change", 0))
            change_percent = quote_data.get("10. change percent", "0%").rstrip("%")
            change_percent = float(change_percent)
            
            position_value = price * stock_info["shares"]
            
            return {
                "symbol": stock_info["symbol"],
                "shares": stock_info["shares"],
                "current_price": price,
                "change": change,
                "change_percent": change_percent,
                "position_value": position_value,
                "last_updated": quote_data.get("07. latest trading day", "N/A")
            }
            
        except (ValueError, TypeError) as e:
            error_msg = f"Data parsing error for {stock_info['symbol']}: {str(e)}"
            self.results["errors"].append(error_msg)
            print(f"Error: {error_msg}")
            return None

    def fetch_portfolio_data(self):
        """Fetch data for entire portfolio"""
        print("=== Stock Portfolio Monitor ===")
        print(f"Fetching data for {len(self.portfolio)} stocks...")
        print(f"API Key: {'demo' if self.api_key == 'demo' else 'configured'}")
        print()
        
        for stock_info in self.portfolio:
            symbol = stock_info["symbol"]
            
            # Fetch quote data
            quote_data = self._make_api_request(symbol)
            if quote_data is None:
                continue
            
            # Parse and structure data
            parsed_data = self._parse_quote_data(quote_data, stock_info)
            if parsed_data is None:
                continue
            
            self.results["portfolio_data"].append(parsed_data)
            self.results["total_value"] += parsed_data["position_value"]
            
            # Print individual stock info
            print(f"{symbol}: ${parsed_data['current_price']:.2f} "
                  f"({parsed_data['change']:+.2f}, {parsed_data['change_percent']:+.2f}%) "
                  f"Position: ${parsed_data['position_value']:,.2f}")

    def save_results(self, filename="portfolio_data.json"):
        """Save results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\nData saved to {filename}")
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def print_summary(self):
        """Print portfolio summary"""
        print("\n=== Portfolio Summary ===")
        print(f"Total Portfolio Value: ${self.results['total_value']:,.2f}")
        print(f"Successful Fetches: {len(self.results['portfolio_data'])}")
        print(f"Errors: {len(self.results['errors'])}")
        
        if self.results["errors"]:
            print("\nErrors encountered:")
            for error in self.results["errors"]:
                print(f"- {error}")

def main():
    """Main execution function"""
    # Get API key from environment or use demo
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")
    
    if api_key == "demo":
        print("WARNING: Using demo API key. Get your free key at: https://www.alphavantage.co/support/#api-key")
        print("Set environment variable: ALPHA_VANTAGE_API_KEY=your_key\n")
    
    try:
        #