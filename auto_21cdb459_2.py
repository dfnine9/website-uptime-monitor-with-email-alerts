```python
#!/usr/bin/env python3
"""
Portfolio Dashboard Generator

This module creates a comprehensive HTML daily dashboard for portfolio performance tracking.
It generates portfolio metrics, risk assessments, and automated rebalancing recommendations
based on target allocations. The dashboard includes performance charts, risk metrics,
allocation analysis, and actionable rebalancing suggestions.

Features:
- Daily portfolio performance tracking
- Risk assessment with VaR, Sharpe ratio, and volatility metrics
- Target vs actual allocation comparison
- Automated rebalancing recommendations
- Interactive HTML dashboard with embedded CSS/JS
- Portfolio diversification analysis
- Performance attribution reporting

Usage: python script.py
"""

import json
import sqlite3
import datetime
import math
import random
from typing import Dict, List, Tuple, Any
import os

class PortfolioDashboard:
    def __init__(self):
        self.db_path = "portfolio_metrics.db"
        self.target_allocations = {
            "Large Cap Stocks": 40.0,
            "Small Cap Stocks": 15.0,
            "International Stocks": 20.0,
            "Bonds": 15.0,
            "REITs": 5.0,
            "Commodities": 5.0
        }
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for portfolio metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    asset_class TEXT NOT NULL,
                    value REAL NOT NULL,
                    weight REAL NOT NULL,
                    daily_return REAL,
                    volatility REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rebalancing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    action TEXT NOT NULL,
                    asset_class TEXT NOT NULL,
                    amount REAL NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")

    def generate_mock_data(self) -> Dict[str, Any]:
        """Generate realistic mock portfolio data for demonstration"""
        try:
            portfolio_value = 250000.0
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Generate current allocations with some drift from target
            current_allocations = {}
            performance_data = {}
            
            for asset_class, target_weight in self.target_allocations.items():
                # Add some random drift from target allocation
                drift = random.uniform(-5.0, 5.0)
                current_weight = max(0, target_weight + drift)
                current_allocations[asset_class] = current_weight
                
                # Generate performance metrics
                daily_return = random.uniform(-0.03, 0.03)  # -3% to +3% daily
                annual_volatility = random.uniform(0.08, 0.25)  # 8% to 25% annual
                ytd_return = random.uniform(-0.15, 0.20)  # -15% to +20% YTD
                
                performance_data[asset_class] = {
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'value': portfolio_value * (current_weight / 100),
                    'daily_return': daily_return,
                    'ytd_return': ytd_return,
                    'volatility': annual_volatility
                }
            
            # Normalize current allocations to 100%
            total_current = sum(current_allocations.values())
            for asset_class in current_allocations:
                performance_data[asset_class]['current_weight'] = (
                    current_allocations[asset_class] / total_current * 100
                )
            
            return {
                'date': current_date,
                'total_value': portfolio_value,
                'performance': performance_data
            }
            
        except Exception as e:
            print(f"Error generating mock data: {e}")
            return {}

    def calculate_risk_metrics(self, performance_data: Dict) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        try:
            portfolio_return = 0
            portfolio_variance = 0
            weights = []
            returns = []
            volatilities = []
            
            for asset_class, data in performance_data.items():
                weight = data['current_weight'] / 100
                daily_return = data['daily_return']
                volatility = data['volatility']
                
                weights.append(weight)
                returns.append(daily_return)
                volatilities.append(volatility)
                
                portfolio_return += weight * daily_return
                portfolio_variance += (weight ** 2) * (volatility ** 2)
            
            # Calculate portfolio volatility (simplified - assumes no correlation)
            portfolio_volatility = math.sqrt(portfolio_variance)
            
            # Calculate Sharpe ratio (annualized)
            annual_return = portfolio_return * 252  # 252 trading days
            annual_volatility = portfolio_volatility * math.sqrt(252)
            sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
            
            # Calculate Value at Risk (95% confidence, 1-day)
            var_95 = portfolio_return - (1.645 * portfolio_volatility)
            
            # Calculate maximum drawdown (simplified estimate)
            max_drawdown = -random.uniform(0.05, 0.15)  # -5% to -15%
            
            return {
                'portfolio_daily_return': portfolio_return,
                'portfolio_annual_volatility': annual_volatility,
                'sharpe_ratio': sharpe_ratio,
                'var_95_1day': var_95,
                'max_drawdown': max_drawdown,
                'diversification_ratio': len([w for w in weights if w > 0.01]) / len(weights)
            }
            
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return {}

    def generate_rebalancing_recommendations(self, performance_data: Dict) -> List[Dict]:
        """Generate automated rebalancing recommendations"""
        try:
            recommendations = []
            threshold = 5.0  # 5% deviation threshold
            
            for asset_class, data in performance_data.items():
                current_weight = data['current_weight']
                target_weight = data['target_weight']
                deviation = current_weight - target_weight
                
                if abs(deviation) > threshold:
                    action = "SELL" if deviation > 0 else "BUY"
                    amount = abs(deviation) * data['value'] / current_weight if current_weight > 0 else 0
                    
                    recommendations.append({
                        'asset_class': asset_class,
                        'action': action,
                        'current_weight': current_weight,
                        'target_weight': target_weight,
                        'deviation': deviation,
                        'recommended_amount': amount,
                        'priority': 'HIGH' if abs(deviation) > 10 else 'MEDIUM',
                        'reason': f"Allocation drift of {deviation:.1f}% from target"
                    })
            
            # Sort by absolute deviation (highest priority first)
            recommendations.sort(key=lambda x: abs(x['deviation']), reverse=True)
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating rebalancing recommendations: {e}")
            return []

    def save_metrics_to_db(self, data: Dict, risk_metrics: Dict):
        """Save portfolio metrics to database"""
        try: