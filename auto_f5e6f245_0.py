"""
Stock Price Threshold Monitor

This script fetches real-time stock prices from Alpha Vantage API and compares them
against user-defined price thresholds loaded from a JSON configuration file.

Features:
- Fetches real-time stock prices using Alpha Vantage API
- Loads price thresholds from config.json
- Compares current prices against buy/sell thresholds
- Provides actionable alerts for threshold breaches
- Self-contained with minimal dependencies

Usage: python script.py
"""

import json
import sys
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
import time

# Alpha Vantage API configuration
API_KEY = "demo"  # Replace with your actual API key
BASE_URL = "https://www.alphavantage.co/query"

def load_config():
    """Load stock thresholds from config.json file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # Create default config if none exists
        default_config = {
            "stocks": {
                "AAPL": {"buy_threshold": 150.0, "sell_threshold": 200.0},
                "MSFT": {"buy_threshold": 300.0, "sell_threshold": 400.0},
                "GOOGL": {"buy_threshold": 100.0, "sell_threshold": 150.0}
            }
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=2)
        print("Created default config.json file")
        return default_config
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json: {e}")
        sys.exit(1)

def fetch_stock_price(symbol):
    """Fetch real-time stock price from Alpha Vantage API."""
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': API_KEY
    }
    
    url = f"{BASE_URL}?{urlencode(params)}"
    
    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        # Check for API errors
        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        
        if "Note" in data:
            raise ValueError(f"API Rate Limit: {data['Note']}")
        
        # Extract price from response
        quote = data.get("Global Quote", {})
        price_str = quote.get("05. price", "")
        
        if not price_str:
            raise ValueError(f"No price data found for {symbol}")
        
        return float(price_str)
    
    except (URLError, HTTPError) as e:
        raise ConnectionError(f"Network error fetching {symbol}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response for {symbol}: {e}")
    except ValueError as e:
        raise ValueError(f"Data parsing error for {symbol}: {e}")

def check_thresholds(symbol, current_price, thresholds):
    """Check if current price breaches buy/sell thresholds."""
    buy_threshold = thresholds.get("buy_threshold")
    sell_threshold = thresholds.get("sell_threshold")
    
    alerts = []
    
    if buy_threshold and current_price <= buy_threshold:
        alerts.append(f"BUY ALERT: {symbol} at ${current_price:.2f} (threshold: ${buy_threshold:.2f})")
    
    if sell_threshold and current_price >= sell_threshold:
        alerts.append(f"SELL ALERT: {symbol} at ${current_price:.2f} (threshold: ${sell_threshold:.2f})")
    
    return alerts

def main():
    """Main execution function."""
    try:
        print("Stock Price Threshold Monitor")
        print("=" * 40)
        
        # Load configuration
        config = load_config()
        stocks = config.get("stocks", {})
        
        if not stocks:
            print("No stocks configured in config.json")
            return
        
        print(f"Monitoring {len(stocks)} stocks...")
        print()
        
        all_alerts = []
        
        for symbol, thresholds in stocks.items():
            try:
                print(f"Fetching {symbol}...", end=" ")
                current_price = fetch_stock_price(symbol)
                print(f"${current_price:.2f}")
                
                # Check thresholds
                alerts = check_thresholds(symbol, current_price, thresholds)
                all_alerts.extend(alerts)
                
                # Display current status
                buy_thresh = thresholds.get("buy_threshold", "N/A")
                sell_thresh = thresholds.get("sell_threshold", "N/A")
                print(f"  Buy: ${buy_thresh} | Sell: ${sell_thresh}")
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"ERROR: {e}")
                continue
        
        print()
        print("ALERTS")
        print("-" * 20)
        
        if all_alerts:
            for alert in all_alerts:
                print(f"🚨 {alert}")
        else:
            print("No threshold breaches detected")
        
        print()
        print(f"Monitoring complete at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()