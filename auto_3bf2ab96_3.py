```python
"""
Automated Monthly Budget Analysis and Reporting System

This module generates comprehensive monthly budget reports with:
- Category-wise spending breakdowns and visualizations
- Trend analysis across multiple months
- Personalized spending recommendations
- Actionable savings strategies based on data patterns

The system analyzes simulated financial data to demonstrate budget tracking,
visualization, and recommendation generation capabilities.

Usage: python script.py
"""

import json
import calendar
from datetime import datetime, timedelta
from collections import defaultdict
import math

class BudgetAnalyzer:
    def __init__(self):
        self.categories = [
            'Housing', 'Food', 'Transportation', 'Utilities', 'Healthcare',
            'Entertainment', 'Shopping', 'Insurance', 'Savings', 'Miscellaneous'
        ]
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        
    def generate_sample_data(self, months=6):
        """Generate realistic sample transaction data for analysis"""
        try:
            import random
            
            base_amounts = {
                'Housing': 1200, 'Food': 400, 'Transportation': 300,
                'Utilities': 150, 'Healthcare': 200, 'Entertainment': 250,
                'Shopping': 300, 'Insurance': 180, 'Savings': 500, 'Miscellaneous': 100
            }
            
            for month_offset in range(months):
                current_date = datetime.now().replace(day=1) - timedelta(days=30*month_offset)
                month_key = current_date.strftime("%Y-%m")
                
                for category in self.categories:
                    # Add some randomness to simulate real spending patterns
                    base = base_amounts[category]
                    variation = random.uniform(0.8, 1.3)
                    monthly_total = base * variation
                    
                    # Generate 3-8 transactions per category per month
                    num_transactions = random.randint(3, 8)
                    for i in range(num_transactions):
                        amount = monthly_total / num_transactions * random.uniform(0.5, 1.8)
                        transaction = {
                            'date': current_date.strftime("%Y-%m-%d"),
                            'category': category,
                            'amount': round(amount, 2),
                            'description': f"{category} expense {i+1}"
                        }
                        self.transactions.append(transaction)
                        self.monthly_data[month_key][category] += amount
                        
        except Exception as e:
            print(f"Error generating sample data: {e}")
            
    def create_ascii_chart(self, data, title, max_width=50):
        """Create ASCII bar chart visualization"""
        try:
            if not data:
                return f"{title}\nNo data available\n"
            
            max_value = max(data.values()) if data else 1
            chart = [f"\n{title}", "=" * len(title)]
            
            for category, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
                bar_length = int((value / max_value) * max_width)
                bar = "█" * bar_length
                chart.append(f"{category:15} │{bar:<{max_width}} ${value:,.2f}")
                
            return "\n".join(chart) + "\n"
            
        except Exception as e:
            return f"Error creating chart: {e}\n"
    
    def analyze_trends(self):
        """Analyze spending trends across months"""
        try:
            trends = {}
            months = sorted(self.monthly_data.keys())
            
            if len(months) < 2:
                return "Insufficient data for trend analysis"
            
            for category in self.categories:
                values = [self.monthly_data[month].get(category, 0) for month in months]
                if len(values) >= 2:
                    # Simple trend calculation
                    recent_avg = sum(values[-2:]) / 2
                    older_avg = sum(values[:-2]) / max(len(values[:-2]), 1)
                    trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
                    trends[category] = trend_pct
                    
            return trends
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {}
    
    def generate_recommendations(self, current_month_data, trends):
        """Generate personalized spending recommendations"""
        try:
            recommendations = []
            total_spending = sum(current_month_data.values())
            
            # High spending categories
            sorted_spending = sorted(current_month_data.items(), key=lambda x: x[1], reverse=True)
            
            for category, amount in sorted_spending[:3]:
                pct_of_total = (amount / total_spending) * 100
                if pct_of_total > 30:
                    recommendations.append(
                        f"🔴 {category} represents {pct_of_total:.1f}% of spending (${amount:,.2f}). "
                        f"Consider reviewing and reducing expenses in this area."
                    )
                elif pct_of_total > 20:
                    recommendations.append(
                        f"🟡 Monitor {category} spending (${amount:,.2f}, {pct_of_total:.1f}% of total). "
                        f"Look for optimization opportunities."
                    )
            
            # Trend-based recommendations
            for category, trend in trends.items():
                if trend > 20:
                    recommendations.append(
                        f"📈 {category} spending increased by {trend:.1f}% recently. "
                        f"Investigate the cause and consider budget adjustments."
                    )
                elif trend < -10:
                    recommendations.append(
                        f"📉 Great job reducing {category} spending by {abs(trend):.1f}%! "
                        f"Continue this positive trend."
                    )
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations due to data processing error"]
    
    def generate_savings_strategies(self, current_month_data):
        """Generate actionable savings strategies"""
        try:
            strategies = []
            total = sum(current_month_data.values())
            
            # Category-specific strategies
            strategy_map = {
                'Food': [
                    "Meal prep on weekends to reduce dining out costs",
                    "Use grocery store apps for coupons and discounts",
                    "Buy generic brands for 20-30% savings"
                ],
                'Transportation': [
                    "Combine errands into single trips",
                    "Use public transportation or carpooling when possible",
                    "Maintain your vehicle regularly to improve fuel efficiency"
                ],
                'Entertainment': [
                    "Look for free community events and activities",
                    "Share streaming subscriptions with family/friends",
                    "Take advantage of happy hours and early bird specials"
                ],
                'Shopping': [
                    "Implement a 24-hour waiting period for non-essential purchases",
                    "Use price comparison apps before buying",
                    "Shop end-of-season sales for future needs"
                ],
                'Utilities': [
                    "Adjust thermostat by 2-3 degrees to save 10-15% on heating/cooling",
                    "Use LED bulbs and unplug electronics when not in use",
                    "Consider programmable thermostats for automated savings"
                ]
            }
            
            # Add strategies for top spending categories
            sorted_categories = sorted(current_month_data.items(), key=lambda x: x[1], reverse=True)
            
            for category, amount in sorted_categories[:3]:
                if category in strategy_map and amount > 0:
                    potential_savings = amount * 0.1  # Assume 10% potential savings
                    strategies.append(f"\n💡 {category} Savings Strategies (Potential: ${potential_savings:.2f}/month):")
                    for strategy in strategy_