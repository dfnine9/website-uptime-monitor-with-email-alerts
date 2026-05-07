```python
"""
Personal Finance Dashboard Generator

This module creates an interactive HTML dashboard that visualizes spending insights,
budget comparisons, and financial trends. It generates sample financial data,
creates various charts using Chart.js, and exports actionable budget recommendations.

The dashboard includes:
- Monthly spending trends
- Budget vs actual spending comparisons
- Category-wise spending breakdown
- Actionable budget recommendations

Dependencies: None beyond Python standard library
Usage: python script.py
"""

import json
import random
import calendar
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import webbrowser
import tempfile
import os

class FinanceDashboard:
    def __init__(self):
        self.categories = [
            'Housing', 'Transportation', 'Food', 'Utilities', 'Healthcare',
            'Entertainment', 'Shopping', 'Education', 'Insurance', 'Savings'
        ]
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        
    def generate_sample_data(self) -> Dict:
        """Generate realistic sample financial data"""
        try:
            data = {
                'monthly_spending': [],
                'budget_vs_actual': [],
                'category_breakdown': {},
                'trends': []
            }
            
            # Generate monthly spending data
            base_spending = 3500
            for i, month in enumerate(self.months):
                variance = random.uniform(-0.15, 0.15)
                spending = base_spending + (base_spending * variance)
                data['monthly_spending'].append({
                    'month': month,
                    'amount': round(spending, 2)
                })
            
            # Generate budget vs actual data
            for category in self.categories:
                if category == 'Housing':
                    budget = random.uniform(1200, 1500)
                elif category == 'Transportation':
                    budget = random.uniform(300, 500)
                elif category == 'Food':
                    budget = random.uniform(400, 600)
                else:
                    budget = random.uniform(100, 300)
                
                actual = budget * random.uniform(0.8, 1.2)
                
                data['budget_vs_actual'].append({
                    'category': category,
                    'budget': round(budget, 2),
                    'actual': round(actual, 2),
                    'variance': round(((actual - budget) / budget) * 100, 1)
                })
            
            # Generate category breakdown for pie chart
            total_spending = sum([item['actual'] for item in data['budget_vs_actual']])
            for item in data['budget_vs_actual']:
                percentage = (item['actual'] / total_spending) * 100
                data['category_breakdown'][item['category']] = round(percentage, 1)
            
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}
    
    def analyze_spending_patterns(self, data: Dict) -> List[str]:
        """Analyze spending data and generate actionable recommendations"""
        try:
            recommendations = []
            
            # Analyze budget variances
            over_budget_categories = [
                item for item in data['budget_vs_actual'] 
                if item['variance'] > 10
            ]
            
            if over_budget_categories:
                worst_category = max(over_budget_categories, key=lambda x: x['variance'])
                recommendations.append(
                    f"🔴 PRIORITY: Reduce {worst_category['category']} spending by "
                    f"{worst_category['variance']:.1f}% (${worst_category['actual'] - worst_category['budget']:.2f})"
                )
            
            # Analyze spending trends
            monthly_amounts = [item['amount'] for item in data['monthly_spending']]
            if len(monthly_amounts) >= 3:
                recent_trend = monthly_amounts[-3:]
                if all(recent_trend[i] < recent_trend[i+1] for i in range(len(recent_trend)-1)):
                    recommendations.append("📈 WARNING: Spending has increased for 3 consecutive months")
            
            # Category-specific recommendations
            category_breakdown = data['category_breakdown']
            if category_breakdown.get('Housing', 0) > 35:
                recommendations.append("🏠 Housing costs exceed 35% of spending - consider refinancing or downsizing")
            
            if category_breakdown.get('Food', 0) > 15:
                recommendations.append("🍽️ Food spending is high - try meal planning and cooking at home")
            
            if category_breakdown.get('Entertainment', 0) > 10:
                recommendations.append("🎬 Entertainment spending is elevated - look for free/low-cost activities")
            
            # Positive reinforcement
            under_budget_categories = [
                item for item in data['budget_vs_actual'] 
                if item['variance'] < -5
            ]
            
            if under_budget_categories:
                best_category = min(under_budget_categories, key=lambda x: x['variance'])
                recommendations.append(
                    f"✅ GREAT JOB: {best_category['category']} spending is "
                    f"{abs(best_category['variance']):.1f}% under budget!"
                )
            
            # Savings recommendations
            total_budget = sum([item['budget'] for item in data['budget_vs_actual']])
            total_actual = sum([item['actual'] for item in data['budget_vs_actual']])
            
            if total_actual < total_budget:
                surplus = total_budget - total_actual
                recommendations.append(f"💰 You have a surplus of ${surplus:.2f} - consider increasing savings")
            
            return recommendations if recommendations else ["📊 Your spending appears to be well-balanced!"]
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return ["Error generating recommendations"]
    
    def generate_html_dashboard(self, data: Dict, recommendations: List[str]) -> str:
        """Generate HTML dashboard with charts and recommendations"""
        try:
            # Prepare data for charts
            monthly_labels = json.dumps([item['month'] for item in data['monthly_spending']])
            monthly_values = json.dumps([item['amount'] for item in data['monthly_spending']])
            
            budget_labels = json.dumps([item['category'] for item in data['budget_vs_actual']])
            budget_values = json.dumps([item['budget'] for item in data['budget_vs_actual']])
            actual_values = json.dumps([item['actual'] for item in data['budget_vs_actual']])
            
            pie_labels = json.dumps(list(data['category_breakdown'].keys()))
            pie_values = json.dumps(list(data['category_breakdown'].values()))
            
            recommendations_html = ''.join([f"<li>{rec}</li>" for rec in recommendations])
            
            html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Finance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; color: #2c3e50; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .chart-title {{ font-size: 18px; font-weight: