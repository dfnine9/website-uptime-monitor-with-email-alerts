```python
"""
Portfolio Analysis Module

A comprehensive portfolio risk assessment tool that implements:
- Value at Risk (VaR) calculations using historical simulation and parametric methods
- Beta coefficient calculations against market benchmarks
- Correlation analysis between portfolio holdings
- Portfolio diversification metrics

This module provides financial risk analysis capabilities for investment portfolios,
helping assess potential losses, market sensitivity, and asset relationships.
"""

import json
import math
import statistics
from datetime import datetime, timedelta
import httpx


class PortfolioAnalyzer:
    def __init__(self):
        self.api_key = "demo"  # Demo API key for Alpha Vantage
        self.base_url = "https://www.alphavantage.co/query"
        
    def fetch_price_data(self, symbol, days=252):
        """Fetch historical price data for a symbol"""
        try:
            with httpx.Client() as client:
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": symbol,
                    "apikey": self.api_key,
                    "outputsize": "full"
                }
                response = client.get(self.base_url, params=params, timeout=30)
                data = response.json()
                
                if "Time Series (Daily)" not in data:
                    # Return mock data for demo purposes
                    return self.generate_mock_data(symbol, days)
                
                prices = []
                time_series = data["Time Series (Daily)"]
                sorted_dates = sorted(time_series.keys(), reverse=True)
                
                for date in sorted_dates[:days]:
                    close_price = float(time_series[date]["4. close"])
                    prices.append(close_price)
                
                return prices[::-1]  # Reverse to chronological order
                
        except Exception as e:
            print(f"API fetch failed for {symbol}: {e}")
            return self.generate_mock_data(symbol, days)
    
    def generate_mock_data(self, symbol, days):
        """Generate realistic mock price data"""
        import random
        random.seed(hash(symbol) % 2147483647)  # Deterministic seed based on symbol
        
        base_price = 100 + (hash(symbol) % 200)
        prices = [base_price]
        
        for i in range(days - 1):
            # Random walk with slight upward bias
            change = random.gauss(0.001, 0.02)  # 0.1% mean return, 2% volatility
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1))  # Prevent negative prices
            
        return prices
    
    def calculate_returns(self, prices):
        """Calculate daily returns from price series"""
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        return returns
    
    def calculate_var(self, returns, confidence_level=0.05):
        """
        Calculate Value at Risk using historical simulation method
        
        Args:
            returns: List of historical returns
            confidence_level: Confidence level (0.05 = 95% VaR)
        
        Returns:
            VaR value as positive number (loss)
        """
        if not returns:
            return 0
        
        sorted_returns = sorted(returns)
        var_index = int(len(sorted_returns) * confidence_level)
        var_return = sorted_returns[var_index]
        
        return abs(var_return)  # Return as positive loss
    
    def calculate_parametric_var(self, returns, confidence_level=0.05):
        """Calculate VaR using parametric (normal distribution) method"""
        if not returns or len(returns) < 2:
            return 0
        
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        # Z-score for confidence level
        z_scores = {0.01: 2.33, 0.05: 1.65, 0.10: 1.28}
        z_score = z_scores.get(confidence_level, 1.65)
        
        var = abs(mean_return - z_score * std_return)
        return var
    
    def calculate_beta(self, asset_returns, market_returns):
        """
        Calculate beta coefficient of an asset relative to market
        
        Beta = Covariance(asset, market) / Variance(market)
        """
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
            return 1.0
        
        try:
            # Calculate covariance and variance manually
            mean_asset = statistics.mean(asset_returns)
            mean_market = statistics.mean(market_returns)
            
            covariance = sum((asset_returns[i] - mean_asset) * (market_returns[i] - mean_market)
                           for i in range(len(asset_returns))) / (len(asset_returns) - 1)
            
            market_variance = statistics.variance(market_returns)
            
            if market_variance == 0:
                return 1.0
                
            beta = covariance / market_variance
            return beta
            
        except Exception as e:
            print(f"Beta calculation error: {e}")
            return 1.0
    
    def calculate_correlation(self, returns1, returns2):
        """Calculate Pearson correlation coefficient between two return series"""
        if len(returns1) != len(returns2) or len(returns1) < 2:
            return 0
        
        try:
            mean1 = statistics.mean(returns1)
            mean2 = statistics.mean(returns2)
            
            numerator = sum((returns1[i] - mean1) * (returns2[i] - mean2) 
                          for i in range(len(returns1)))
            
            sum_sq1 = sum((x - mean1) ** 2 for x in returns1)
            sum_sq2 = sum((x - mean2) ** 2 for x in returns2)
            
            denominator = math.sqrt(sum_sq1 * sum_sq2)
            
            if denominator == 0:
                return 0
                
            correlation = numerator / denominator
            return correlation
            
        except Exception as e:
            print(f"Correlation calculation error: {e}")
            return 0
    
    def calculate_portfolio_var(self, holdings, confidence_level=0.05):
        """Calculate portfolio-level VaR considering correlations"""
        portfolio_returns = []
        total_value = sum(holdings.values())
        
        # Get data for all assets
        asset_data = {}
        for symbol in holdings.keys():
            prices = self.fetch_price_data(symbol)
            returns = self.calculate_returns(prices)
            asset_data[symbol] = returns
        
        # Calculate portfolio returns
        max_length = max(len(returns) for returns in asset_data.values())
        
        for i in range(max_length):
            portfolio_return = 0
            for symbol, weight in holdings.items():
                if i < len(asset_data[symbol]):
                    weight_pct = weight / total_value
                    portfolio_return += weight_pct * asset_data[symbol][i]
            portfolio_returns.append(portfolio_return)
        
        # Calculate portfolio VaR
        return self.calculate_var(portfolio_returns, confidence_level)
    
    def analyze_portfolio(self, portfolio):
        """
        Comprehensive portfolio analysis
        
        Args:
            portfolio: Dict with 'holdings' (symbol: dollar_amount) and optional 'benchmark'
        """
        print("=== PORTFOLIO RISK ANALYSIS ===")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        holdings = portfolio.get('holdings', {})
        benchmark = portfolio.get('benchmark', 'SPY')
        
        if not holdings