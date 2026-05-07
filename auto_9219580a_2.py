```python
"""
Portfolio Risk Assessment Engine

A comprehensive risk analysis tool that evaluates portfolio concentration, sector allocation,
and generates rebalancing recommendations based on Modern Portfolio Theory (MPT) principles.

Features:
- Portfolio concentration analysis using Herfindahl-Hirschman Index
- Sector diversification assessment
- Risk-return optimization using MPT
- Automated rebalancing recommendations
- Value at Risk (VaR) calculations
- Sharpe ratio optimization

This engine helps investors maintain optimal portfolio balance by identifying concentration
risks and suggesting allocations that maximize returns for given risk levels.
"""

import json
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Asset:
    symbol: str
    name: str
    sector: str
    current_weight: float
    expected_return: float
    volatility: float
    price: float
    market_cap: float

@dataclass
class Portfolio:
    assets: List[Asset]
    total_value: float
    
class RiskAssessmentEngine:
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.target_sectors = {
            'Technology': 0.25,
            'Healthcare': 0.15,
            'Finance': 0.15,
            'Consumer': 0.15,
            'Energy': 0.10,
            'Utilities': 0.10,
            'Materials': 0.10
        }
    
    def generate_sample_portfolio(self) -> Portfolio:
        """Generate sample portfolio data for demonstration"""
        sample_assets = [
            Asset("AAPL", "Apple Inc.", "Technology", 0.15, 0.12, 0.25, 150.0, 2500000000000),
            Asset("GOOGL", "Alphabet Inc.", "Technology", 0.12, 0.14, 0.28, 2500.0, 1800000000000),
            Asset("MSFT", "Microsoft Corp.", "Technology", 0.18, 0.11, 0.23, 300.0, 2300000000000),
            Asset("JPM", "JPMorgan Chase", "Finance", 0.08, 0.09, 0.22, 140.0, 420000000000),
            Asset("JNJ", "Johnson & Johnson", "Healthcare", 0.10, 0.07, 0.15, 160.0, 430000000000),
            Asset("PFE", "Pfizer Inc.", "Healthcare", 0.06, 0.08, 0.18, 40.0, 220000000000),
            Asset("XOM", "Exxon Mobil", "Energy", 0.12, 0.06, 0.35, 110.0, 460000000000),
            Asset("PG", "Procter & Gamble", "Consumer", 0.07, 0.06, 0.16, 145.0, 340000000000),
            Asset("KO", "Coca-Cola", "Consumer", 0.05, 0.05, 0.14, 58.0, 250000000000),
            Asset("NEE", "NextEra Energy", "Utilities", 0.07, 0.08, 0.19, 75.0, 150000000000)
        ]
        
        return Portfolio(sample_assets, 1000000.0)  # $1M portfolio
    
    def calculate_concentration_risk(self, portfolio: Portfolio) -> Dict:
        """Calculate portfolio concentration using Herfindahl-Hirschman Index"""
        try:
            # Asset concentration
            weights = [asset.current_weight for asset in portfolio.assets]
            hhi_assets = sum(w**2 for w in weights)
            
            # Sector concentration
            sector_weights = {}
            for asset in portfolio.assets:
                sector_weights[asset.sector] = sector_weights.get(asset.sector, 0) + asset.current_weight
            
            hhi_sectors = sum(w**2 for w in sector_weights.values())
            
            # Concentration risk levels
            asset_concentration_risk = "High" if hhi_assets > 0.25 else "Medium" if hhi_assets > 0.15 else "Low"
            sector_concentration_risk = "High" if hhi_sectors > 0.4 else "Medium" if hhi_sectors > 0.25 else "Low"
            
            return {
                "hhi_assets": hhi_assets,
                "hhi_sectors": hhi_sectors,
                "asset_concentration_risk": asset_concentration_risk,
                "sector_concentration_risk": sector_concentration_risk,
                "sector_weights": sector_weights,
                "top_holdings": sorted([(asset.symbol, asset.current_weight) for asset in portfolio.assets], 
                                     key=lambda x: x[1], reverse=True)[:5]
            }
        except Exception as e:
            print(f"Error calculating concentration risk: {e}")
            return {}
    
    def calculate_portfolio_metrics(self, portfolio: Portfolio) -> Dict:
        """Calculate key portfolio risk metrics"""
        try:
            weights = [asset.current_weight for asset in portfolio.assets]
            returns = [asset.expected_return for asset in portfolio.assets]
            volatilities = [asset.volatility for asset in portfolio.assets]
            
            # Portfolio expected return
            portfolio_return = sum(w * r for w, r in zip(weights, returns))
            
            # Simplified portfolio volatility (assuming correlation = 0.3)
            portfolio_variance = 0
            for i, (w1, v1) in enumerate(zip(weights, volatilities)):
                portfolio_variance += w1**2 * v1**2
                for j, (w2, v2) in enumerate(zip(weights, volatilities)):
                    if i != j:
                        portfolio_variance += w1 * w2 * v1 * v2 * 0.3  # Assumed correlation
            
            portfolio_volatility = math.sqrt(portfolio_variance)
            
            # Sharpe ratio
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Value at Risk (95% confidence)
            var_95 = portfolio_return - 1.645 * portfolio_volatility
            
            return {
                "expected_return": portfolio_return,
                "volatility": portfolio_volatility,
                "sharpe_ratio": sharpe_ratio,
                "var_95": var_95,
                "portfolio_value": portfolio.total_value
            }
        except Exception as e:
            print(f"Error calculating portfolio metrics: {e}")
            return {}
    
    def generate_efficient_allocation(self, portfolio: Portfolio) -> Dict:
        """Generate optimal allocation using simplified MPT"""
        try:
            assets = portfolio.assets
            n = len(assets)
            
            # Simple optimization: maximize Sharpe ratio with constraints
            best_sharpe = -float('inf')
            best_weights = None
            
            # Monte Carlo optimization (simplified)
            for _ in range(1000):
                # Generate random weights
                weights = [random.random() for _ in range(n)]
                weights_sum = sum(weights)
                weights = [w/weights_sum for w in weights]
                
                # Check constraints (no single asset > 20%, sectors balanced)
                if max(weights) > 0.20:
                    continue
                
                # Calculate portfolio metrics
                portfolio_return = sum(w * asset.expected_return for w, asset in zip(weights, assets))
                
                portfolio_variance = 0
                for i, (w1, asset1) in enumerate(zip(weights, assets)):
                    portfolio_variance += w1**2 * asset1.volatility**2
                    for j, (w2, asset2) in enumerate(zip(weights, assets)):
                        if i != j:
                            portfolio_variance += w1 * w2 * asset1.volatility * asset2.volatility * 0.3
                
                portfolio_volatility = math.sqrt(portfolio_variance)
                sharpe