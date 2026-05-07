```python
#!/usr/bin/env python3
"""
Portfolio Analytics Script

This script fetches real-time stock data and calculates key portfolio metrics:
- Portfolio returns (daily and cumulative)
- Volatility (annualized standard deviation)
- Sharpe ratio (risk-adjusted return)

Uses only standard library plus httpx for HTTP requests.
No yfinance dependency - implements Yahoo Finance API calls directly.

Usage: python script.py
"""

import json
import math
import statistics
from datetime import datetime, timedelta
from urllib.parse import urlencode
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    sys.exit(1)


class PortfolioAnalyzer:
    def __init__(self):
        # Sample portfolio: ticker -> weight
        self.portfolio = {
            'AAPL': 0.3,
            'GOOGL': 0.25,
            'MSFT': 0.2,
            'TSLA': 0.15,
            'NVDA': 0.1
        }
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        
    def fetch_stock_data(self, symbol, period="1y"):
        """Fetch historical stock data from Yahoo Finance API"""
        try:
            # Yahoo Finance query parameters
            end_time = int(datetime.now().timestamp())
            start_time = int((datetime.now() - timedelta(days=365)).timestamp())
            
            params = {
                'period1': start_time,
                'period2': end_time,
                'interval': '1d',
                'events': 'history'
            }
            
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                
                lines = response.text.strip().split('\n')
                if len(lines) < 2:
                    raise ValueError(f"Insufficient data for {symbol}")
                
                # Parse CSV data (skip header)
                prices = []
                for line in lines[1:]:
                    parts = line.split(',')
                    if len(parts) >= 5 and parts[4] != 'null':
                        try:
                            close_price = float(parts[4])  # Adjusted Close
                            prices.append(close_price)
                        except (ValueError, IndexError):
                            continue
                
                if len(prices) < 30:
                    raise ValueError(f"Insufficient price data for {symbol}")
                
                return prices
                
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_returns(self, prices):
        """Calculate daily returns from price series"""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
        
        return returns
    
    def calculate_portfolio_metrics(self):
        """Calculate portfolio returns, volatility, and Sharpe ratio"""
        print("Fetching stock data...")
        
        # Fetch data for all stocks
        stock_data = {}
        for symbol, weight in self.portfolio.items():
            print(f"Fetching {symbol}...")
            prices = self.fetch_stock_data(symbol)
            if prices:
                returns = self.calculate_returns(prices)
                if returns:
                    stock_data[symbol] = {
                        'returns': returns,
                        'weight': weight,
                        'prices': prices
                    }
                    print(f"✓ {symbol}: {len(returns)} daily returns")
                else:
                    print(f"✗ {symbol}: No valid returns calculated")
            else:
                print(f"✗ {symbol}: Failed to fetch data")
        
        if not stock_data:
            raise ValueError("No valid stock data retrieved")
        
        # Find minimum length to align all return series
        min_length = min(len(data['returns']) for data in stock_data.values())
        print(f"\nAligning {min_length} days of data across all stocks")
        
        # Calculate portfolio daily returns
        portfolio_returns = []
        for day in range(min_length):
            daily_portfolio_return = 0
            for symbol, data in stock_data.items():
                daily_portfolio_return += data['returns'][day] * data['weight']
            portfolio_returns.append(daily_portfolio_return)
        
        # Calculate metrics
        avg_daily_return = statistics.mean(portfolio_returns)
        annual_return = (1 + avg_daily_return) ** 252 - 1  # 252 trading days
        
        daily_volatility = statistics.stdev(portfolio_returns) if len(portfolio_returns) > 1 else 0
        annual_volatility = daily_volatility * math.sqrt(252)
        
        # Sharpe ratio
        excess_return = annual_return - self.risk_free_rate
        sharpe_ratio = excess_return / annual_volatility if annual_volatility > 0 else 0
        
        # Cumulative return
        cumulative_return = 1
        for ret in portfolio_returns:
            cumulative_return *= (1 + ret)
        cumulative_return -= 1
        
        return {
            'portfolio_composition': self.portfolio,
            'data_period_days': min_length,
            'avg_daily_return': avg_daily_return,
            'annualized_return': annual_return,
            'annualized_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'cumulative_return': cumulative_return,
            'total_return_pct': cumulative_return * 100
        }


def main():
    """Main execution function"""
    try:
        print("=" * 60)
        print("PORTFOLIO ANALYTICS - REAL-TIME STOCK DATA")
        print("=" * 60)
        
        analyzer = PortfolioAnalyzer()
        
        print(f"Portfolio Composition:")
        for symbol, weight in analyzer.portfolio.items():
            print(f"  {symbol}: {weight*100:.1f}%")
        print()
        
        # Calculate metrics
        metrics = analyzer.calculate_portfolio_metrics()
        
        # Display results
        print("\n" + "=" * 60)
        print("PORTFOLIO METRICS RESULTS")
        print("=" * 60)
        
        print(f"Analysis Period: {metrics['data_period_days']} trading days")
        print(f"Risk-Free Rate: {analyzer.risk_free_rate*100:.1f}% annually")
        print()
        
        print("RETURNS:")
        print(f"  Average Daily Return: {metrics['avg_daily_return']*100:.3f}%")
        print(f"  Annualized Return: {metrics['annualized_return']*100:.2f}%")
        print(f"  Total Cumulative Return: {metrics['total_return_pct']:.2f}%")
        print()
        
        print("RISK METRICS:")
        print(f"  Annualized Volatility: {metrics['annualized_volatility']*100:.2f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
        print()
        
        # Risk assessment
        if metrics['sharpe_ratio'] > 1.0:
            risk_assessment = "Excellent"
        elif metrics['sharpe_ratio'] > 0.5:
            risk_assessment = "Good"
        elif metrics['sharpe_ratio'] > 0:
            risk_assessment = "Fair"
        else:
            risk_assessment = "Poor"
        
        print(f"RISK-ADJUSTED PERFORMANCE: {risk_assessment}")
        print("=" * 60