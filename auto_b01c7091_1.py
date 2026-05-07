```python
#!/usr/bin/env python3
"""
Technical Analysis Module for Stock Trading Signals

This module implements RSI, MACD, and moving average technical indicators
to generate buy/sell signals for stock positions. It fetches real-time
stock data and calculates technical indicators to provide trading recommendations.

Features:
- RSI (Relative Strength Index) calculation
- MACD (Moving Average Convergence Divergence) analysis
- Simple and Exponential Moving Averages
- Buy/Sell signal generation based on technical analysis
- Real-time stock data fetching
- Comprehensive error handling

Note: This module provides ANALYSIS ONLY. No actual trades are executed.
"""

import json
import math
from typing import List, Dict, Tuple, Optional
import httpx
from datetime import datetime, timedelta


class TechnicalAnalysis:
    def __init__(self):
        self.api_key = "demo"  # Demo key for Alpha Vantage
        self.base_url = "https://www.alphavantage.co/query"
    
    def fetch_stock_data(self, symbol: str, interval: str = "daily") -> Optional[Dict]:
        """Fetch stock data from Alpha Vantage API"""
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "full"
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "Error Message" in data:
                    print(f"API Error for {symbol}: {data['Error Message']}")
                    return None
                    
                if "Note" in data:
                    print(f"API Limit reached: {data['Note']}")
                    return None
                    
                return data
                
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        try:
            if len(prices) < period + 1:
                return []
            
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            gains = [max(d, 0) for d in deltas]
            losses = [-min(d, 0) for d in deltas]
            
            # Initial average gain/loss
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period
            
            rsi_values = []
            
            for i in range(period, len(gains)):
                if avg_loss == 0:
                    rsi_values.append(100.0)
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    rsi_values.append(rsi)
                
                # Update averages
                avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
                avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
            
            return rsi_values
            
        except Exception as e:
            print(f"Error calculating RSI: {str(e)}")
            return []
    
    def calculate_sma(self, prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        try:
            if len(prices) < period:
                return []
            
            sma_values = []
            for i in range(period - 1, len(prices)):
                avg = sum(prices[i - period + 1:i + 1]) / period
                sma_values.append(avg)
            
            return sma_values
            
        except Exception as e:
            print(f"Error calculating SMA: {str(e)}")
            return []
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return []
            
            multiplier = 2 / (period + 1)
            ema_values = []
            
            # Start with SMA for first value
            ema = sum(prices[:period]) / period
            ema_values.append(ema)
            
            # Calculate EMA for remaining values
            for i in range(period, len(prices)):
                ema = (prices[i] * multiplier) + (ema * (1 - multiplier))
                ema_values.append(ema)
            
            return ema_values
            
        except Exception as e:
            print(f"Error calculating EMA: {str(e)}")
            return []
    
    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            if len(prices) < slow:
                return [], [], []
            
            ema_fast = self.calculate_ema(prices, fast)
            ema_slow = self.calculate_ema(prices, slow)
            
            if not ema_fast or not ema_slow:
                return [], [], []
            
            # Align the arrays (EMA slow starts later)
            start_idx = slow - fast
            macd_line = [ema_fast[i + start_idx] - ema_slow[i] for i in range(len(ema_slow))]
            
            # Calculate signal line (EMA of MACD)
            signal_line = self.calculate_ema(macd_line, signal)
            
            # Calculate histogram
            histogram = []
            if len(signal_line) > 0:
                start_hist = len(macd_line) - len(signal_line)
                histogram = [macd_line[i + start_hist] - signal_line[i] for i in range(len(signal_line))]
            
            return macd_line, signal_line, histogram
            
        except Exception as e:
            print(f"Error calculating MACD: {str(e)}")
            return [], [], []
    
    def generate_signals(self, symbol: str, data: Dict) -> Dict:
        """Generate buy/sell signals based on technical indicators"""
        try:
            time_series = data.get("Time Series (Daily)", {})
            if not time_series:
                return {"error": "No time series data available"}
            
            # Extract closing prices (most recent first, so reverse)
            dates = sorted(time_series.keys(), reverse=True)[:100]  # Last 100 days
            prices = [float(time_series[date]["4. close"]) for date in dates]
            prices.reverse()  # Oldest to newest for calculations
            
            if len(prices) < 50:
                return {"error": "Insufficient data for analysis"}
            
            # Calculate indicators
            rsi_values = self.calculate_rsi(prices)
            sma_20 = self.calculate_sma(prices, 20)
            sma_50 = self.calculate_sma(prices, 50)
            ema_12 = self.calculate_ema(prices, 12)
            ema_26 = self.calculate_ema(prices, 26)
            macd_line, signal_line, histogram = self.calculate_macd(prices)
            
            # Get latest values
            current_price = prices[-1]
            latest_rsi = rsi_values[-1] if rsi_values else None
            latest_sma_20 = sma_20[-1] if sma_20 else None
            latest_sma_50 = sma_50[-1] if sma_50 else None
            latest_macd = macd_line[-1] if macd_line else None
            latest_signal = signal_line