```python
"""
Financial Data Visualization Generator

This module creates comprehensive financial visualizations including:
- Monthly spending breakdown charts
- Category pie charts  
- Trend analysis graphs

Uses matplotlib for static charts and plotly for interactive visualizations.
Processes sample financial data to demonstrate visualization capabilities.

Dependencies: matplotlib, plotly, pandas, numpy
Usage: python script.py
"""

import json
import random
import datetime
from typing import Dict, List, Any
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import numpy as np
except ImportError:
    print("Error: matplotlib not installed. Install with: pip install matplotlib")
    sys.exit(1)

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
except ImportError:
    print("Error: plotly not installed. Install with: pip install plotly")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed. Install with: pip install pandas")
    sys.exit(1)


class FinancialDataGenerator:
    """Generate sample financial data for visualization"""
    
    def __init__(self):
        self.categories = [
            'Housing', 'Food & Dining', 'Transportation', 'Entertainment',
            'Shopping', 'Healthcare', 'Utilities', 'Insurance', 'Travel',
            'Education', 'Personal Care', 'Investment'
        ]
        
    def generate_sample_data(self, months: int = 12) -> List[Dict[str, Any]]:
        """Generate sample financial transactions"""
        transactions = []
        base_date = datetime.date.today() - datetime.timedelta(days=30 * months)
        
        for month in range(months):
            month_date = base_date + datetime.timedelta(days=30 * month)
            
            # Generate 20-50 transactions per month
            num_transactions = random.randint(20, 50)
            
            for _ in range(num_transactions):
                day_offset = random.randint(0, 29)
                transaction_date = month_date + datetime.timedelta(days=day_offset)
                
                category = random.choice(self.categories)
                
                # Category-specific amount ranges
                amount_ranges = {
                    'Housing': (800, 2500),
                    'Food & Dining': (10, 150),
                    'Transportation': (20, 300),
                    'Entertainment': (15, 200),
                    'Shopping': (25, 500),
                    'Healthcare': (50, 800),
                    'Utilities': (80, 300),
                    'Insurance': (100, 500),
                    'Travel': (200, 2000),
                    'Education': (100, 1500),
                    'Personal Care': (20, 150),
                    'Investment': (100, 1000)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (10, 200))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                transactions.append({
                    'date': transaction_date.isoformat(),
                    'category': category,
                    'amount': amount,
                    'description': f"{category} expense"
                })
        
        return transactions


class FinancialVisualizer:
    """Create financial data visualizations"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.df = pd.DataFrame(data)
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['month'] = self.df['date'].dt.to_period('M')
        
    def create_monthly_spending_chart(self) -> None:
        """Create matplotlib bar chart of monthly spending"""
        try:
            monthly_totals = self.df.groupby('month')['amount'].sum()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            months = [str(month) for month in monthly_totals.index]
            amounts = monthly_totals.values
            
            bars = ax.bar(months, amounts, color='steelblue', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom', fontsize=10)
            
            ax.set_title('Monthly Spending Breakdown', fontsize=16, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            plt.tight_layout()
            plt.savefig('monthly_spending.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Monthly spending chart created and saved as 'monthly_spending.png'")
            
        except Exception as e:
            print(f"Error creating monthly spending chart: {e}")
    
    def create_category_pie_chart(self) -> None:
        """Create matplotlib pie chart of spending by category"""
        try:
            category_totals = self.df.groupby('category')['amount'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Use a colorful palette
            colors = plt.cm.Set3(np.linspace(0, 1, len(category_totals)))
            
            wedges, texts, autotexts = ax.pie(
                category_totals.values,
                labels=category_totals.index,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                explode=[0.05 if i == 0 else 0 for i in range(len(category_totals))]
            )
            
            # Enhance text formatting
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            ax.set_title('Spending by Category', fontsize=16, fontweight='bold', pad=20)
            
            # Add legend with amounts
            legend_labels = [f'{cat}: ${amt:,.0f}' for cat, amt in category_totals.items()]
            ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))
            
            plt.tight_layout()
            plt.savefig('category_pie_chart.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Category pie chart created and saved as 'category_pie_chart.png'")
            
        except Exception as e:
            print(f"Error creating category pie chart: {e}")
    
    def create_trend_analysis(self) -> None:
        """Create matplotlib line chart showing spending trends"""
        try:
            # Monthly trends
            monthly_data = self.df.groupby(['month', 'category'])['amount'].sum().unstack(fill_value=0)
            monthly_totals = self.df.groupby('month')['amount'].sum()
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # Overall monthly trend
            months_str = [str(month) for month in monthly_totals.index]
            ax1.plot(months_str, monthly_totals.values, marker='o', linewidth=2, markersize=6, color='darkblue')
            ax1.set_title('