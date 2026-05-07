```python
"""
Personal Finance Visualization Module

This module generates matplotlib charts for financial data analysis including:
- Pie charts for spending patterns by category
- Bar graphs for monthly spending trends
- Time series plots for budget vs actual comparisons

Requirements: matplotlib, numpy (standard data science libraries)
Usage: python script.py
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import random
from collections import defaultdict
import sys

class FinanceVisualizer:
    def __init__(self):
        """Initialize the finance visualizer with sample data."""
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Other']
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        
    def generate_sample_data(self):
        """Generate sample financial data for demonstration."""
        try:
            # Generate spending by category (last 30 days)
            spending_data = {}
            for category in self.categories:
                spending_data[category] = round(random.uniform(50, 500), 2)
            
            # Generate monthly trends (last 12 months)
            monthly_data = {}
            base_date = datetime.now().replace(day=1)
            for i in range(12):
                month_date = base_date - timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                monthly_data[month_key] = round(random.uniform(1000, 3000), 2)
            
            # Generate budget vs actual data (last 6 months)
            budget_actual_data = {}
            for i in range(6):
                month_date = base_date - timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                budget = round(random.uniform(2000, 2500), 2)
                actual = round(budget * random.uniform(0.8, 1.2), 2)
                budget_actual_data[month_key] = {'budget': budget, 'actual': actual}
            
            return spending_data, monthly_data, budget_actual_data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}, {}, {}
    
    def create_spending_pie_chart(self, spending_data):
        """Create a pie chart showing spending patterns by category."""
        try:
            if not spending_data:
                print("No spending data available for pie chart")
                return
                
            plt.figure(figsize=(10, 8))
            
            categories = list(spending_data.keys())
            amounts = list(spending_data.values())
            
            # Create pie chart
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, colors=self.colors,
                                             autopct='%1.1f%%', startangle=90, explode=[0.05]*len(categories))
            
            # Enhance appearance
            plt.setp(autotexts, size=10, weight='bold')
            plt.setp(texts, size=12)
            
            plt.title('Spending Patterns by Category', fontsize=16, fontweight='bold', pad=20)
            
            # Add total spending annotation
            total_spending = sum(amounts)
            plt.figtext(0.5, 0.02, f'Total Spending: ${total_spending:,.2f}', 
                       ha='center', fontsize=12, style='italic')
            
            plt.tight_layout()
            plt.savefig('spending_pie_chart.png', dpi=300, bbox_inches='tight')
            plt.show()
            print("✓ Spending pie chart generated successfully")
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_monthly_bar_chart(self, monthly_data):
        """Create a bar chart showing monthly spending trends."""
        try:
            if not monthly_data:
                print("No monthly data available for bar chart")
                return
                
            plt.figure(figsize=(12, 6))
            
            # Sort months chronologically
            sorted_months = sorted(monthly_data.items(), key=lambda x: x[0])
            months = [item[0] for item in sorted_months]
            amounts = [item[1] for item in sorted_months]
            
            # Create bar chart
            bars = plt.bar(months, amounts, color='#4ECDC4', alpha=0.8, edgecolor='#2C3E50', linewidth=1)
            
            # Enhance appearance
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12, fontweight='bold')
            plt.ylabel('Amount ($)', fontsize=12, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                        f'${amount:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            # Add trend line
            x_pos = range(len(amounts))
            z = np.polyfit(x_pos, amounts, 1)
            p = np.poly1d(z)
            plt.plot(x_pos, p(x_pos), "r--", alpha=0.8, linewidth=2, label='Trend')
            plt.legend()
            
            plt.tight_layout()
            plt.savefig('monthly_spending_bar_chart.png', dpi=300, bbox_inches='tight')
            plt.show()
            print("✓ Monthly spending bar chart generated successfully")
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
    
    def create_budget_vs_actual_chart(self, budget_actual_data):
        """Create a time series chart comparing budget vs actual spending."""
        try:
            if not budget_actual_data:
                print("No budget vs actual data available for time series chart")
                return
                
            plt.figure(figsize=(12, 6))
            
            # Sort months chronologically
            sorted_data = sorted(budget_actual_data.items(), key=lambda x: x[0])
            months = [item[0] for item in sorted_data]
            budgets = [item[1]['budget'] for item in sorted_data]
            actuals = [item[1]['actual'] for item in sorted_data]
            
            # Create time series plot
            x = range(len(months))
            
            plt.plot(x, budgets, marker='o', linewidth=3, markersize=8, 
                    color='#2E86C1', label='Budget', alpha=0.9)
            plt.plot(x, actuals, marker='s', linewidth=3, markersize=8, 
                    color='#E74C3C', label='Actual', alpha=0.9)
            
            # Fill area between lines
            plt.fill_between(x, budgets, actuals, alpha=0.2, 
                           color=['green' if actual <= budget else 'red' 
                                 for actual, budget in zip(actuals, budgets)])
            
            # Enhance appearance
            plt.title('Budget vs Actual Spending Comparison', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12, fontweight='bold')
            plt.ylabel('Amount ($)', fontsize=12, fontweight='bold')
            plt.xticks(x, months, rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=12)
            
            # Add annotations for over/under budget
            for i, (month, budget, actual) in enumerate(zip(months,