"""
Stock Data Fetcher and Analysis Module

This module fetches real-time stock data from Alpha Vantage API and calculates
basic financial metrics including price changes, moving averages, and volatility.
Designed for analysis purposes only - no trading execution.

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import json
import sys
from datetime import datetime, timedelta
try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)

class StockAnalyzer:
    def __init__(self, api_key="demo"):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def fetch_stock_data(self, symbol="AAPL"):
        """Fetch daily stock data from Alpha Vantage API"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(self.base_url, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                if "Error Message" in data:
                    raise ValueError(f"API Error: {data['Error Message']}")
                
                if "Note" in data:
                    raise ValueError("API rate limit exceeded. Try again later.")
                
                return data
                
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error: {e}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from API")
    
    def calculate_metrics(self, time_series_data):
        """Calculate basic stock metrics from time series data"""
        if not time_series_data:
            return {}
        
        # Convert to list of (date, price_data) tuples and sort by date
        sorted_data = sorted(time_series_data.items(), reverse=True)
        
        if len(sorted_data) < 2:
            return {"error": "Insufficient data for analysis"}
        
        # Get latest and previous day data
        latest_date, latest_data = sorted_data[0]
        prev_date, prev_data = sorted_data[1]
        
        current_price = float(latest_data["4. close"])
        prev_price = float(prev_data["4. close"])
        
        # Calculate daily change
        daily_change = current_price - prev_price
        daily_change_pct = (daily_change / prev_price) * 100
        
        # Calculate volatility (standard deviation of last 20 days)
        prices = []
        for i in range(min(20, len(sorted_data))):
            prices.append(float(sorted_data[i][1]["4. close"]))
        
        if len(prices) > 1:
            mean_price = sum(prices) / len(prices)
            variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
            volatility = variance ** 0.5
        else:
            volatility = 0
        
        # Calculate moving averages
        ma_5 = sum(prices[:min(5, len(prices))]) / min(5, len(prices))
        ma_20 = sum(prices[:min(20, len(prices))]) / min(20, len(prices))
        
        return {
            "current_price": current_price,
            "daily_change": daily_change,
            "daily_change_pct": daily_change_pct,
            "volatility": volatility,
            "ma_5": ma_5,
            "ma_20": ma_20,
            "volume": int(latest_data["5. volume"]),
            "high_52w": max(float(data["2. high"]) for _, data in sorted_data[:min(252, len(sorted_data))]),
            "low_52w": min(float(data["3. low"]) for _, data in sorted_data[:min(252, len(sorted_data))])
        }
    
    def analyze_stock(self, symbol="AAPL"):
        """Main analysis function"""
        try:
            print(f"Fetching data for {symbol}...")
            data = self.fetch_stock_data(symbol)
            
            if "Time Series (Daily)" not in data:
                print(f"Error: No time series data found for {symbol}")
                return
            
            time_series = data["Time Series (Daily)"]
            metrics = self.calculate_metrics(time_series)
            
            if "error" in metrics:
                print(f"Analysis error: {metrics['error']}")
                return
            
            # Display results
            print(f"\n=== STOCK ANALYSIS: {symbol} ===")
            print(f"Current Price: ${metrics['current_price']:.2f}")
            print(f"Daily Change: ${metrics['daily_change']:.2f} ({metrics['daily_change_pct']:+.2f}%)")
            print(f"Volume: {metrics['volume']:,}")
            print(f"Volatility (20d): ${metrics['volatility']:.2f}")
            print(f"5-Day MA: ${metrics['ma_5']:.2f}")
            print(f"20-Day MA: ${metrics['ma_20']:.2f}")
            print(f"52-Week High: ${metrics['high_52w']:.2f}")
            print(f"52-Week Low: ${metrics['low_52w']:.2f}")
            
            # Simple trend analysis
            if metrics['current_price'] > metrics['ma_5'] > metrics['ma_20']:
                trend = "BULLISH"
            elif metrics['current_price'] < metrics['ma_5'] < metrics['ma_20']:
                trend = "BEARISH"
            else:
                trend = "NEUTRAL"
            
            print(f"Trend Signal: {trend}")
            print(f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n*** FOR ANALYSIS ONLY - NOT TRADING ADVICE ***")
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")

def main():
    """Main execution function"""
    analyzer = StockAnalyzer()
    
    # Default stocks to analyze
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in symbols:
        try:
            analyzer.analyze_stock(symbol)
            print("-" * 50)
        except Exception as e:
            print(f"Failed to analyze {symbol}: {e}")
            continue

if __name__ == "__main__":
    main()