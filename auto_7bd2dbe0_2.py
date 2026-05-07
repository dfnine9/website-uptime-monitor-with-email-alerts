```python
"""
Personal Finance Visualization Dashboard

This module creates interactive financial charts for spending analysis including:
- Spending breakdown by category (pie chart)
- Monthly spending trends (line chart)
- Budget variance analysis (bar chart)

The script generates sample financial data and creates visualizations using matplotlib.
All charts are displayed in separate windows and also saved as PNG files.

Requirements: matplotlib, numpy (both typically included in standard Python distributions)
Usage: python script.py
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import random
import json
import sys

class FinanceVisualizer:
    def __init__(self):
        """Initialize the finance visualizer with sample data."""
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                          'Healthcare', 'Shopping', 'Rent', 'Insurance']
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate realistic sample financial data."""
        try:
            # Monthly spending by category
            monthly_spending = {}
            for month in self.months:
                monthly_spending[month] = {
                    'Food': random.randint(300, 600),
                    'Transportation': random.randint(100, 300),
                    'Entertainment': random.randint(50, 200),
                    'Utilities': random.randint(150, 250),
                    'Healthcare': random.randint(50, 400),
                    'Shopping': random.randint(100, 500),
                    'Rent': random.randint(800, 1200),
                    'Insurance': random.randint(200, 350)
                }
            
            # Budget vs actual for current month
            budgets = {
                'Food': 500,
                'Transportation': 200,
                'Entertainment': 150,
                'Utilities': 200,
                'Healthcare': 200,
                'Shopping': 300,
                'Rent': 1000,
                'Insurance': 300
            }
            
            return {
                'monthly_spending': monthly_spending,
                'budgets': budgets,
                'current_month': self.months[-1]
            }
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}
    
    def create_category_breakdown(self):
        """Create pie chart showing spending breakdown by category for current month."""
        try:
            current_month = self.sample_data['current_month']
            current_spending = self.sample_data['monthly_spending'][current_month]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            categories = list(current_spending.keys())
            amounts = list(current_spending.values())
            
            # Create pie chart with enhanced styling
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                            colors=colors, startangle=90, 
                                            explode=[0.05] * len(categories))
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title(f'Spending Breakdown by Category - {current_month}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            plt.savefig('category_breakdown.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"Category breakdown chart created for {current_month}")
            print("Top spending categories:")
            sorted_spending = sorted(current_spending.items(), key=lambda x: x[1], reverse=True)
            for category, amount in sorted_spending[:3]:
                print(f"  {category}: ${amount:,}")
            
        except Exception as e:
            print(f"Error creating category breakdown chart: {e}")
    
    def create_monthly_trends(self):
        """Create line chart showing monthly spending trends."""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            monthly_totals = []
            for month in self.months:
                total = sum(self.sample_data['monthly_spending'][month].values())
                monthly_totals.append(total)
            
            # Create main trend line
            ax.plot(self.months, monthly_totals, marker='o', linewidth=3, 
                   markersize=8, color='#2E8B57', label='Total Spending')
            
            # Add category trends for top 3 categories
            top_categories = ['Rent', 'Food', 'Shopping']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            for i, category in enumerate(top_categories):
                category_monthly = [self.sample_data['monthly_spending'][month][category] 
                                  for month in self.months]
                ax.plot(self.months, category_monthly, marker='s', linewidth=2,
                       markersize=6, color=colors[i], label=category, alpha=0.7)
            
            ax.set_title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            plt.tight_layout()
            plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("Monthly trends chart created")
            print(f"Average monthly spending: ${np.mean(monthly_totals):,.2f}")
            print(f"Spending trend: {'+' if monthly_totals[-1] > monthly_totals[0] else '-'}${abs(monthly_totals[-1] - monthly_totals[0]):,.2f} from {self.months[0]} to {self.months[-1]}")
            
        except Exception as e:
            print(f"Error creating monthly trends chart: {e}")
    
    def create_budget_variance(self):
        """Create bar chart showing budget vs actual spending variance."""
        try:
            current_month = self.sample_data['current_month']
            current_spending = self.sample_data['monthly_spending'][current_month]
            budgets = self.sample_data['budgets']
            
            categories = list(budgets.keys())
            budget_amounts = [budgets[cat] for cat in categories]
            actual_amounts = [current_spending[cat] for cat in categories]
            variances = [actual - budget for actual, budget in zip(actual_amounts, budget_amounts)]
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            x = np.arange(len(categories))
            width = 0.35
            
            # Create bars
            bars1 = ax.bar(x - width/2, budget_amounts, width, label='Budget', 
                          color='#3498db', alpha=0.8)
            bars2 = ax.bar(x + width/2, actual_amounts, width, label='Actual', 
                          color=['#e74c3c' if v > 0 else '#27ae60' for v in variances], alpha=0.8)
            
            # Add variance labels on bars
            for i, (bar, variance) in enumerate(zip(bars2, variances)):
                height = bar.get_height()
                ax.annotate(f'${variance:+.0f}',
                          xy=(bar.get_x() + bar.get_width() / 2, height),