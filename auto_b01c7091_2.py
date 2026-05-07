```python
"""
Portfolio Performance Report Generator

This module creates comprehensive PDF/HTML dashboards for investment portfolios,
featuring allocation charts, risk metrics, and recommendation rankings.

Key Features:
- Portfolio allocation visualization with pie/bar charts
- Risk metrics calculation (VaR, Sharpe ratio, volatility)
- Asset recommendation rankings based on performance
- Dual output format (HTML/PDF)
- Real-time market data integration
- Performance analytics and trend analysis

Dependencies: httpx, anthropic (external), json, datetime, math (standard library)
"""

import json
import datetime
import math
import asyncio
from typing import Dict, List, Tuple, Optional
import httpx

class PortfolioAnalyzer:
    def __init__(self):
        self.portfolio_data = {}
        self.market_data = {}
        self.risk_metrics = {}
        
    def generate_sample_portfolio(self) -> Dict:
        """Generate sample portfolio data for demonstration"""
        return {
            "assets": {
                "AAPL": {"shares": 100, "avg_cost": 150.00, "current_price": 175.50},
                "GOOGL": {"shares": 50, "avg_cost": 2500.00, "current_price": 2750.00},
                "MSFT": {"shares": 75, "avg_cost": 300.00, "current_price": 340.00},
                "TSLA": {"shares": 25, "avg_cost": 800.00, "current_price": 950.00},
                "BTC": {"shares": 2, "avg_cost": 45000.00, "current_price": 52000.00}
            },
            "cash": 5000.00,
            "last_updated": datetime.datetime.now().isoformat()
        }
    
    def calculate_portfolio_value(self, portfolio: Dict) -> Tuple[float, Dict]:
        """Calculate total portfolio value and individual asset values"""
        total_value = portfolio["cash"]
        asset_values = {}
        
        for symbol, data in portfolio["assets"].items():
            asset_value = data["shares"] * data["current_price"]
            asset_values[symbol] = asset_value
            total_value += asset_value
            
        return total_value, asset_values
    
    def calculate_risk_metrics(self, portfolio: Dict) -> Dict:
        """Calculate portfolio risk metrics"""
        try:
            total_value, asset_values = self.calculate_portfolio_value(portfolio)
            
            # Portfolio weights
            weights = {}
            for symbol, value in asset_values.items():
                weights[symbol] = value / total_value
            
            # Mock volatility data (in real implementation, fetch historical data)
            mock_volatilities = {
                "AAPL": 0.25, "GOOGL": 0.28, "MSFT": 0.22,
                "TSLA": 0.45, "BTC": 0.65
            }
            
            # Calculate portfolio volatility (simplified)
            portfolio_volatility = 0
            for symbol, weight in weights.items():
                if symbol in mock_volatilities:
                    portfolio_volatility += (weight ** 2) * (mock_volatilities[symbol] ** 2)
            
            portfolio_volatility = math.sqrt(portfolio_volatility)
            
            # Calculate Value at Risk (95% confidence, 1-day)
            var_95 = total_value * 1.645 * portfolio_volatility / math.sqrt(252)
            
            # Mock Sharpe ratio calculation
            risk_free_rate = 0.02
            mock_return = 0.12
            sharpe_ratio = (mock_return - risk_free_rate) / portfolio_volatility
            
            return {
                "portfolio_volatility": round(portfolio_volatility, 4),
                "value_at_risk_95": round(var_95, 2),
                "sharpe_ratio": round(sharpe_ratio, 3),
                "total_value": round(total_value, 2),
                "weights": {k: round(v, 3) for k, v in weights.items()}
            }
            
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return {}
    
    def generate_recommendations(self, portfolio: Dict) -> List[Dict]:
        """Generate investment recommendations based on portfolio analysis"""
        try:
            recommendations = []
            
            # Calculate current gains/losses
            for symbol, data in portfolio["assets"].items():
                current_value = data["shares"] * data["current_price"]
                cost_basis = data["shares"] * data["avg_cost"]
                gain_loss = current_value - cost_basis
                gain_loss_pct = (gain_loss / cost_basis) * 100
                
                # Generate recommendation based on performance
                if gain_loss_pct > 20:
                    action = "HOLD/PARTIAL_SELL"
                    priority = "HIGH"
                elif gain_loss_pct > 10:
                    action = "HOLD"
                    priority = "MEDIUM"
                elif gain_loss_pct < -10:
                    action = "BUY_DIP"
                    priority = "HIGH"
                else:
                    action = "HOLD"
                    priority = "LOW"
                
                recommendations.append({
                    "symbol": symbol,
                    "action": action,
                    "priority": priority,
                    "current_gain_loss": round(gain_loss, 2),
                    "gain_loss_pct": round(gain_loss_pct, 2),
                    "reason": f"Current return: {gain_loss_pct:.1f}%"
                })
            
            # Sort by priority and gain/loss
            priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
            recommendations.sort(
                key=lambda x: (priority_order[x["priority"]], abs(x["gain_loss_pct"])),
                reverse=True
            )
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def create_html_chart_data(self, portfolio: Dict) -> str:
        """Generate JavaScript chart data for HTML dashboard"""
        try:
            total_value, asset_values = self.calculate_portfolio_value(portfolio)
            
            # Allocation chart data
            chart_data = []
            colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
            
            for i, (symbol, value) in enumerate(asset_values.items()):
                chart_data.append({
                    "label": symbol,
                    "value": round((value / total_value) * 100, 1),
                    "color": colors[i % len(colors)]
                })
            
            # Add cash if significant
            if portfolio["cash"] / total_value > 0.05:
                chart_data.append({
                    "label": "Cash",
                    "value": round((portfolio["cash"] / total_value) * 100, 1),
                    "color": "#C9CBCF"
                })
            
            return json.dumps(chart_data)
            
        except Exception as e:
            print(f"Error creating chart data: {e}")
            return "[]"
    
    def generate_html_dashboard(self, portfolio: Dict, risk_metrics: Dict, recommendations: List[Dict]) -> str:
        """Generate HTML dashboard with charts and metrics"""
        try:
            chart_data = self.create_html_chart_data(portfolio)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}