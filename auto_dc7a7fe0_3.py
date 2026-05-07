```python
#!/usr/bin/env python3
"""
Monthly Budget Insights Report Generator

This script generates comprehensive monthly financial reports in HTML format with:
- Spending summaries and category breakdowns
- Trend analysis with ASCII-based visualizations
- Budget variance analysis
- Actionable recommendations for budget optimization

The script simulates financial data and creates a self-contained HTML report
that can be saved and viewed in any web browser.

Usage: python script.py
"""

import json
import datetime
import random
import math
from typing import Dict, List, Tuple, Any

class ReportGenerator:
    def __init__(self):
        self.current_month = datetime.datetime.now().strftime("%B %Y")
        self.categories = [
            "Housing", "Transportation", "Food", "Utilities", 
            "Healthcare", "Entertainment", "Shopping", "Insurance",
            "Savings", "Debt Payment", "Education", "Other"
        ]
        
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample financial data for demonstration"""
        try:
            # Generate spending data for current and previous months
            current_spending = {}
            previous_spending = {}
            budgets = {}
            
            for category in self.categories:
                base_amount = random.randint(200, 2000)
                current_spending[category] = base_amount + random.randint(-100, 100)
                previous_spending[category] = base_amount + random.randint(-150, 150)
                budgets[category] = base_amount + random.randint(50, 200)
            
            # Generate daily spending for trend analysis
            daily_spending = []
            for day in range(1, 31):
                daily_total = random.randint(50, 300)
                daily_spending.append({
                    'day': day,
                    'amount': daily_total
                })
            
            return {
                'current_spending': current_spending,
                'previous_spending': previous_spending,
                'budgets': budgets,
                'daily_spending': daily_spending,
                'total_income': random.randint(5000, 8000)
            }
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}
    
    def calculate_variance(self, actual: float, budget: float) -> Tuple[float, str]:
        """Calculate budget variance and status"""
        try:
            variance = actual - budget
            percentage = (variance / budget) * 100 if budget > 0 else 0
            status = "over" if variance > 0 else "under"
            return percentage, status
        except Exception as e:
            print(f"Error calculating variance: {e}")
            return 0.0, "error"
    
    def create_ascii_chart(self, data: List[Tuple[str, float]], width: int = 50) -> str:
        """Create ASCII bar chart"""
        try:
            if not data:
                return "No data available"
            
            max_value = max(value for _, value in data)
            if max_value == 0:
                return "All values are zero"
            
            chart = []
            for label, value in data:
                bar_length = int((value / max_value) * width)
                bar = "█" * bar_length
                chart.append(f"{label:<15} |{bar:<{width}} ${value:,.2f}")
            
            return "\n".join(chart)
        except Exception as e:
            return f"Error creating chart: {e}"
    
    def generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate actionable budget recommendations"""
        recommendations = []
        
        try:
            current = data['current_spending']
            budgets = data['budgets']
            previous = data['previous_spending']
            
            # Find categories over budget
            over_budget = []
            for category in current:
                if current[category] > budgets[category]:
                    over_amount = current[category] - budgets[category]
                    over_budget.append((category, over_amount))
            
            over_budget.sort(key=lambda x: x[1], reverse=True)
            
            # Find categories with increasing spending
            increasing_spend = []
            for category in current:
                if current[category] > previous[category] * 1.1:  # 10% increase
                    increase = current[category] - previous[category]
                    increasing_spend.append((category, increase))
            
            # Generate recommendations
            if over_budget:
                top_overspend = over_budget[0]
                recommendations.append(
                    f"🔴 Priority: Reduce {top_overspend[0]} spending by ${top_overspend[1]:.2f} "
                    f"to meet budget target"
                )
            
            if increasing_spend:
                recommendations.append(
                    f"⚠️ Monitor {increasing_spend[0][0]} - spending increased by "
                    f"${increasing_spend[0][1]:.2f} from last month"
                )
            
            # Savings recommendation
            total_spent = sum(current.values())
            total_income = data['total_income']
            savings_rate = ((total_income - total_spent) / total_income) * 100
            
            if savings_rate < 20:
                recommendations.append(
                    f"💰 Increase savings rate from {savings_rate:.1f}% to 20% "
                    f"by reducing discretionary spending"
                )
            
            # Category-specific recommendations
            if current.get('Entertainment', 0) > budgets.get('Entertainment', 0):
                recommendations.append(
                    "🎬 Consider free entertainment alternatives or set weekly limits"
                )
            
            if current.get('Food', 0) > budgets.get('Food', 0):
                recommendations.append(
                    "🍽️ Try meal planning and cooking at home to reduce food costs"
                )
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            return [f"Error generating recommendations: {e}"]
    
    def create_html_report(self, data: Dict[str, Any]) -> str:
        """Create HTML report with all analysis"""
        try:
            current = data['current_spending']
            budgets = data['budgets']
            previous = data['previous_spending']
            daily = data['daily_spending']
            
            # Calculate totals
            total_spent = sum(current.values())
            total_budget = sum(budgets.values())
            total_previous = sum(previous.values())
            
            # Create spending chart data
            spending_chart_data = [(cat, amount) for cat, amount in current.items()]
            spending_chart_data.sort(key=lambda x: x[1], reverse=True)
            
            # Generate recommendations
            recommendations = self.generate_recommendations(data)
            
            # Create HTML
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Monthly Budget Report - {self.current_month}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }}
        .over-budget {{ color: #e74c3c; font-weight: bold; }}
        .under-budget {{ color: #27ae60; font-weight: bold; }}
        .chart {{ font-family: monospace; background: #f8f9fa; padding: 15px; border-radius: