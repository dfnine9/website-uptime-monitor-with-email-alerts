```python
#!/usr/bin/env python3
"""
Portfolio Analytics Module

This module calculates key financial risk metrics for investment portfolios including:
- Portfolio Volatility (annualized standard deviation)
- Beta Coefficients (systematic risk relative to market)
- Sharpe Ratio (risk-adjusted return)
- Correlation Matrix (diversification analysis)

The module uses synthetic data generation to demonstrate calculations when external
data sources are unavailable, making it fully self-contained for testing purposes.
"""

import json
import math
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class PortfolioAnalytics:
    """Portfolio risk analytics calculator with key financial metrics."""
    
    def __init__(self):
        self.trading_days = 252  # Annual trading days for annualization
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    def generate_synthetic_data(self, symbols: List[str], days: int = 252) -> Dict[str, List[float]]:
        """Generate synthetic price data for demonstration purposes."""
        try:
            data = {}
            random.seed(42)  # Reproducible results
            
            for symbol in symbols:
                prices = [100.0]  # Starting price
                
                # Generate correlated random walks
                volatility = random.uniform(0.15, 0.35)  # 15-35% annual volatility
                drift = random.uniform(-0.05, 0.15)  # -5% to 15% annual return
                
                for _ in range(days - 1):
                    daily_return = random.normalvariate(drift/252, volatility/math.sqrt(252))
                    new_price = prices[-1] * (1 + daily_return)
                    prices.append(max(new_price, 0.01))  # Prevent negative prices
                
                data[symbol] = prices
            
            return data
        except Exception as e:
            raise ValueError(f"Error generating synthetic data: {e}")
    
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """Calculate daily returns from price series."""
        try:
            if len(prices) < 2:
                raise ValueError("Need at least 2 price points")
            
            returns = []
            for i in range(1, len(prices)):
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
            
            return returns
        except Exception as e:
            raise ValueError(f"Error calculating returns: {e}")
    
    def calculate_portfolio_volatility(self, returns_matrix: Dict[str, List[float]], 
                                     weights: Dict[str, float]) -> float:
        """Calculate annualized portfolio volatility."""
        try:
            symbols = list(returns_matrix.keys())
            n = len(returns_matrix[symbols[0]])
            
            # Calculate portfolio returns
            portfolio_returns = []
            for i in range(n):
                portfolio_return = sum(weights[symbol] * returns_matrix[symbol][i] 
                                     for symbol in symbols)
                portfolio_returns.append(portfolio_return)
            
            # Calculate variance and annualize
            mean_return = sum(portfolio_returns) / len(portfolio_returns)
            variance = sum((r - mean_return) ** 2 for r in portfolio_returns) / (len(portfolio_returns) - 1)
            
            # Annualized volatility
            return math.sqrt(variance * self.trading_days)
        
        except Exception as e:
            raise ValueError(f"Error calculating portfolio volatility: {e}")
    
    def calculate_beta(self, asset_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta coefficient (systematic risk)."""
        try:
            if len(asset_returns) != len(market_returns):
                raise ValueError("Asset and market returns must have same length")
            
            n = len(asset_returns)
            if n < 2:
                raise ValueError("Need at least 2 data points")
            
            # Calculate means
            asset_mean = sum(asset_returns) / n
            market_mean = sum(market_returns) / n
            
            # Calculate covariance and market variance
            covariance = sum((asset_returns[i] - asset_mean) * (market_returns[i] - market_mean) 
                           for i in range(n)) / (n - 1)
            
            market_variance = sum((market_returns[i] - market_mean) ** 2 
                                for i in range(n)) / (n - 1)
            
            if market_variance == 0:
                return 0.0
            
            return covariance / market_variance
        
        except Exception as e:
            raise ValueError(f"Error calculating beta: {e}")
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio (risk-adjusted return)."""
        try:
            if len(returns) < 2:
                raise ValueError("Need at least 2 return observations")
            
            # Annualized return
            mean_return = sum(returns) / len(returns)
            annualized_return = (1 + mean_return) ** self.trading_days - 1
            
            # Annualized volatility
            variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
            annualized_volatility = math.sqrt(variance * self.trading_days)
            
            if annualized_volatility == 0:
                return 0.0
            
            return (annualized_return - self.risk_free_rate) / annualized_volatility
        
        except Exception as e:
            raise ValueError(f"Error calculating Sharpe ratio: {e}")
    
    def calculate_correlation_matrix(self, returns_matrix: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between assets."""
        try:
            symbols = list(returns_matrix.keys())
            correlation_matrix = {}
            
            for symbol1 in symbols:
                correlation_matrix[symbol1] = {}
                
                for symbol2 in symbols:
                    if symbol1 == symbol2:
                        correlation_matrix[symbol1][symbol2] = 1.0
                    else:
                        returns1 = returns_matrix[symbol1]
                        returns2 = returns_matrix[symbol2]
                        
                        if len(returns1) != len(returns2):
                            raise ValueError(f"Return series length mismatch: {symbol1} vs {symbol2}")
                        
                        n = len(returns1)
                        mean1 = sum(returns1) / n
                        mean2 = sum(returns2) / n
                        
                        # Calculate correlation coefficient
                        numerator = sum((returns1[i] - mean1) * (returns2[i] - mean2) for i in range(n))
                        
                        variance1 = sum((r - mean1) ** 2 for r in returns1)
                        variance2 = sum((r - mean2) ** 2 for r in returns2)
                        
                        denominator = math.sqrt(variance1 * variance2)
                        
                        if denominator == 0:
                            correlation_matrix[symbol1][symbol2] = 0.0
                        else:
                            correlation_matrix[symbol1][symbol2] = numerator / denominator
            
            return correlation_matrix
        
        except Exception as e:
            raise ValueError(f"Error calculating correlation matrix: {e}")


def main():
    """Main execution function with comprehensive error handling."""
    try:
        print("=== PORTFOLIO ANALYTICS MODULE ===")
        print("Calculating key risk metrics for investment portfolio\n")
        
        # Initialize analytics engine
        analytics = PortfolioAnalytics()
        
        # Define portfolio
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY']  # SPY as market proxy
        weights = {
            'AAPL': 0.25,