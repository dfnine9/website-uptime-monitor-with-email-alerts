```python
"""
Monthly Expense Report Generator

This module generates comprehensive monthly expense reports with:
- Formatted text reports with category breakdowns
- ASCII-based visualizations (charts/graphs)
- Budget vs actual comparisons
- Actionable spending insights and recommendations

The module simulates expense data and budget information to demonstrate
reporting capabilities. In a real implementation, data would be loaded
from external sources like databases or CSV files.

Usage: python script.py
"""

import json
import datetime
from collections import defaultdict
import math

class ExpenseReportGenerator:
    def __init__(self):
        self.expenses = []
        self.budgets = {}
        self.categories = [
            "Housing", "Transportation", "Food", "Entertainment", 
            "Healthcare", "Shopping", "Utilities", "Insurance"
        ]
    
    def load_sample_data(self):
        """Load sample expense data for demonstration"""
        try:
            # Sample monthly expenses
            sample_expenses = [
                {"date": "2024-01-05", "category": "Housing", "amount": 1200.00, "description": "Rent"},
                {"date": "2024-01-10", "category": "Food", "amount": 65.50, "description": "Groceries"},
                {"date": "2024-01-12", "category": "Transportation", "amount": 45.00, "description": "Gas"},
                {"date": "2024-01-15", "category": "Entertainment", "amount": 25.00, "description": "Movie tickets"},
                {"date": "2024-01-18", "category": "Food", "amount": 85.30, "description": "Restaurant"},
                {"date": "2024-01-20", "category": "Healthcare", "amount": 150.00, "description": "Doctor visit"},
                {"date": "2024-01-22", "category": "Shopping", "amount": 120.75, "description": "Clothing"},
                {"date": "2024-01-25", "category": "Utilities", "amount": 95.00, "description": "Electric bill"},
                {"date": "2024-01-28", "category": "Transportation", "amount": 35.00, "description": "Parking"},
                {"date": "2024-01-30", "category": "Food", "amount": 45.20, "description": "Takeout"},
            ]
            
            # Sample budget allocations
            sample_budgets = {
                "Housing": 1300.00,
                "Transportation": 200.00,
                "Food": 400.00,
                "Entertainment": 150.00,
                "Healthcare": 200.00,
                "Shopping": 100.00,
                "Utilities": 150.00,
                "Insurance": 100.00
            }
            
            self.expenses = sample_expenses
            self.budgets = sample_budgets
            
        except Exception as e:
            print(f"Error loading sample data: {e}")
            raise
    
    def calculate_category_totals(self):
        """Calculate total spending per category"""
        try:
            totals = defaultdict(float)
            for expense in self.expenses:
                totals[expense["category"]] += expense["amount"]
            return dict(totals)
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def generate_ascii_bar_chart(self, data, title, max_width=50):
        """Generate ASCII bar chart"""
        try:
            if not data:
                return f"\n{title}\nNo data available\n"
            
            max_value = max(data.values())
            chart = f"\n{title}\n" + "=" * len(title) + "\n\n"
            
            for category, amount in sorted(data.items(), key=lambda x: x[1], reverse=True):
                bar_length = int((amount / max_value) * max_width) if max_value > 0 else 0
                bar = "█" * bar_length
                chart += f"{category:15} │{bar:<{max_width}} ${amount:8.2f}\n"
            
            chart += "\n"
            return chart
            
        except Exception as e:
            print(f"Error generating bar chart: {e}")
            return f"\n{title}\nError generating chart\n"
    
    def generate_budget_comparison(self):
        """Generate budget vs actual comparison"""
        try:
            category_totals = self.calculate_category_totals()
            comparison = "\nBUDGET vs ACTUAL COMPARISON\n" + "=" * 30 + "\n\n"
            comparison += f"{'Category':15} {'Budget':>10} {'Actual':>10} {'Variance':>10} {'Status':>10}\n"
            comparison += "-" * 65 + "\n"
            
            total_budget = 0
            total_actual = 0
            
            for category in self.categories:
                budget = self.budgets.get(category, 0)
                actual = category_totals.get(category, 0)
                variance = actual - budget
                status = "OVER" if variance > 0 else "UNDER" if variance < 0 else "EXACT"
                
                total_budget += budget
                total_actual += actual
                
                comparison += f"{category:15} ${budget:8.2f} ${actual:8.2f} ${variance:8.2f} {status:>10}\n"
            
            comparison += "-" * 65 + "\n"
            comparison += f"{'TOTAL':15} ${total_budget:8.2f} ${total_actual:8.2f} ${total_actual-total_budget:8.2f}\n\n"
            
            return comparison
            
        except Exception as e:
            print(f"Error generating budget comparison: {e}")
            return "\nBUDGET vs ACTUAL COMPARISON\nError generating comparison\n"
    
    def generate_spending_insights(self):
        """Generate actionable spending insights"""
        try:
            category_totals = self.calculate_category_totals()
            total_spent = sum(category_totals.values())
            total_budget = sum(self.budgets.values())
            
            insights = "\nSPENDING INSIGHTS & RECOMMENDATIONS\n" + "=" * 35 + "\n\n"
            
            # Overall spending analysis
            if total_spent > total_budget:
                insights += f"⚠️  BUDGET EXCEEDED: You've spent ${total_spent - total_budget:.2f} over budget this month.\n\n"
            else:
                insights += f"✅ UNDER BUDGET: You've saved ${total_budget - total_spent:.2f} this month.\n\n"
            
            # Category-specific insights
            insights += "Category Analysis:\n"
            insights += "-" * 20 + "\n"
            
            for category, actual in category_totals.items():
                budget = self.budgets.get(category, 0)
                if budget > 0:
                    percentage = (actual / budget) * 100
                    if percentage > 110:
                        insights += f"🔴 {category}: {percentage:.1f}% of budget - Consider reducing spending\n"
                    elif percentage > 90:
                        insights += f"🟡 {category}: {percentage:.1f}% of budget - Monitor closely\n"
                    else:
                        insights += f"🟢 {category}: {percentage:.1f}% of budget - Good control\n"
            
            # Top spending categories
            insights += f"\nTop Spending Categories:\n"
            insights += "-" * 25 + "\n"
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
            for i, (category, amount) in enumerate(sorted_categories, 1):
                percentage = (amount / total_spent) * 100 if total_spent > 0 else 0
                insights += f"{i}. {category}: ${amount:.2f} ({percentage:.1f}% of total spending)\n"
            
            # Recommendations
            insights += f"\nRecommendations:\n"
            insights += "-" * 15 +