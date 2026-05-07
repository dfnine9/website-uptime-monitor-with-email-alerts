```python
#!/usr/bin/env python3
"""
Portfolio Analytics Module

This module provides comprehensive portfolio analysis capabilities including:
- Returns calculation (simple, log, cumulative)
- Risk metrics (volatility, Value at Risk, maximum drawdown)
- Performance ratios (Sharpe, Sortino, Calmar)
- Beta calculation against benchmark
- Risk-adjusted return metrics

Uses only standard library with pandas-style calculations implemented via numpy.
Includes sample data for demonstration purposes.
"""

import json
import math
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import random


class PortfolioAnalytics:
    """Portfolio analytics engine for calculating comprehensive risk and return metrics."""
    
    def __init__(self, portfolio_data: List[Dict], benchmark_data: Optional[List[Dict]] = None):
        """
        Initialize portfolio analytics with price data.
        
        Args:
            portfolio_data: List of dicts with 'date', 'price', 'symbol' keys
            benchmark_data: Optional benchmark data for beta calculation
        """
        self.portfolio_data = portfolio_data
        self.benchmark_data = benchmark_data or []
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        
    def calculate_returns(self, prices: List[float], return_type: str = 'simple') -> List[float]:
        """Calculate returns from price series."""
        if len(prices) < 2:
            return []
            
        returns = []
        for i in range(1, len(prices)):
            if return_type == 'simple':
                ret = (prices[i] - prices[i-1]) / prices[i-1]
            elif return_type == 'log':
                ret = math.log(prices[i] / prices[i-1])
            else:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        return returns
    
    def calculate_volatility(self, returns: List[float], annualize: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)."""
        if len(returns) < 2:
            return 0.0
            
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        volatility = math.sqrt(variance)
        
        if annualize:
            volatility *= math.sqrt(252)  # Annualize assuming 252 trading days
            
        return volatility
    
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0
            
        mean_return = sum(returns) / len(returns)
        volatility = self.calculate_volatility(returns, annualize=False)
        
        if volatility == 0:
            return 0.0
            
        # Annualize returns and adjust for risk-free rate
        annual_return = mean_return * 252
        daily_risk_free = self.risk_free_rate / 252
        
        excess_return = annual_return - self.risk_free_rate
        annual_volatility = volatility * math.sqrt(252)
        
        return excess_return / annual_volatility if annual_volatility > 0 else 0.0
    
    def calculate_sortino_ratio(self, returns: List[float]) -> float:
        """Calculate Sortino ratio (downside deviation)."""
        if len(returns) < 2:
            return 0.0
            
        mean_return = sum(returns) / len(returns)
        negative_returns = [r for r in returns if r < 0]
        
        if not negative_returns:
            return float('inf')
            
        downside_variance = sum(r ** 2 for r in negative_returns) / len(returns)
        downside_deviation = math.sqrt(downside_variance)
        
        annual_return = mean_return * 252
        annual_downside_deviation = downside_deviation * math.sqrt(252)
        
        excess_return = annual_return - self.risk_free_rate
        return excess_return / annual_downside_deviation if annual_downside_deviation > 0 else 0.0
    
    def calculate_maximum_drawdown(self, prices: List[float]) -> Tuple[float, int, int]:
        """Calculate maximum drawdown and its duration."""
        if len(prices) < 2:
            return 0.0, 0, 0
            
        cumulative_returns = []
        cumulative = 1.0
        
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            cumulative *= (1 + ret)
            cumulative_returns.append(cumulative)
        
        peak = cumulative_returns[0]
        max_drawdown = 0.0
        peak_idx = 0
        trough_idx = 0
        
        for i, value in enumerate(cumulative_returns):
            if value > peak:
                peak = value
                peak_idx = i
            
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                trough_idx = i
                
        return max_drawdown, peak_idx, trough_idx
    
    def calculate_beta(self, portfolio_returns: List[float], benchmark_returns: List[float]) -> float:
        """Calculate beta against benchmark."""
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return 1.0
            
        # Calculate means
        port_mean = sum(portfolio_returns) / len(portfolio_returns)
        bench_mean = sum(benchmark_returns) / len(benchmark_returns)
        
        # Calculate covariance and benchmark variance
        covariance = sum((portfolio_returns[i] - port_mean) * (benchmark_returns[i] - bench_mean) 
                        for i in range(len(portfolio_returns))) / (len(portfolio_returns) - 1)
        
        benchmark_variance = sum((r - bench_mean) ** 2 for r in benchmark_returns) / (len(benchmark_returns) - 1)
        
        return covariance / benchmark_variance if benchmark_variance > 0 else 1.0
    
    def calculate_value_at_risk(self, returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR)."""
        if not returns:
            return 0.0
            
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0
    
    def calculate_calmar_ratio(self, returns: List[float], prices: List[float]) -> float:
        """Calculate Calmar ratio (annual return / max drawdown)."""
        if len(returns) < 2:
            return 0.0
            
        annual_return = (sum(returns) / len(returns)) * 252
        max_drawdown, _, _ = self.calculate_maximum_drawdown(prices)
        
        return annual_return / max_drawdown if max_drawdown > 0 else 0.0
    
    def generate_report(self) -> Dict:
        """Generate comprehensive portfolio analytics report."""
        try:
            # Extract prices by symbol
            symbols = list(set(d['symbol'] for d in self.portfolio_data))
            portfolio_metrics = {}
            
            for symbol in symbols:
                symbol_data = [d for d in self.portfolio_data if d['symbol'] == symbol]
                symbol_data.sort(key=lambda x: x['date'])
                
                prices = [d['price'] for d in symbol_data]
                returns = self.calculate_returns(prices)
                
                if not returns:
                    continue
                
                # Calculate all metrics
                volatility = self.calculate_volatility(returns)