```python
#!/usr/bin/env python3
"""
Financial Visualization Module

This module creates interactive charts for financial data analysis using matplotlib.
It generates monthly spending breakdowns, category trends over time, and summary dashboards.
The module includes sample data generation and comprehensive error handling.

Features:
- Monthly spending breakdown pie charts
- Category trend analysis over time
- Summary dashboard with multiple visualizations
- Interactive matplotlib charts with hover capabilities
- Error handling for missing data and plotting issues

Usage: python script.py
"""

import json
import random
import datetime
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.widgets import Button
    import numpy as np
except ImportError:
    print("Error: matplotlib not available. Please install with: pip install matplotlib")
    sys.exit(1)

class FinancialVisualizer:
    """Creates interactive financial visualizations using matplotlib."""
    
    def __init__(self):
        """Initialize the visualizer with sample data."""
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare', 'Other']
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
        self.data = self._generate_sample_data()
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
    def _generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate sample financial data for demonstration."""
        data = []
        base_date = datetime.datetime.now() - datetime.timedelta(days=365)
        
        try:
            for i in range(365):
                current_date = base_date + datetime.timedelta(days=i)
                
                # Generate 1-5 transactions per day
                num_transactions = random.randint(1, 5)
                
                for _ in range(num_transactions):
                    transaction = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'category': random.choice(self.categories),
                        'amount': round(random.uniform(5, 200), 2),
                        'description': f"Transaction {random.randint(1000, 9999)}"
                    }
                    data.append(transaction)
                    
            print(f"Generated {len(data)} sample transactions")
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def _aggregate_monthly_data(self) -> Dict[str, Dict[str, float]]:
        """Aggregate transaction data by month and category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.data:
                date_obj = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
                
            return dict(monthly_data)
            
        except Exception as e:
            print(f"Error aggregating monthly data: {e}")
            return {}
    
    def create_monthly_breakdown(self, month: str = None) -> None:
        """Create a pie chart showing spending breakdown for a specific month."""
        try:
            monthly_data = self._aggregate_monthly_data()
            
            if not monthly_data:
                print("No data available for monthly breakdown")
                return
                
            # Use latest month if none specified
            if month is None:
                month = max(monthly_data.keys())
                
            if month not in monthly_data:
                print(f"No data available for month: {month}")
                return
                
            category_totals = monthly_data[month]
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(10, 8))
            
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=categories,
                colors=self.colors[:len(categories)],
                autopct='%1.1f%%',
                startangle=90,
                explode=[0.05] * len(categories)
            )
            
            # Enhance styling
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                
            ax.set_title(f'Monthly Spending Breakdown - {month}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add total spending
            total_spending = sum(amounts)
            plt.figtext(0.5, 0.02, f'Total Spending: ${total_spending:,.2f}', 
                       ha='center', fontsize=12, style='italic')
            
            plt.tight_layout()
            plt.show()
            
            print(f"Monthly breakdown for {month}:")
            for category, amount in category_totals.items():
                print(f"  {category}: ${amount:,.2f}")
            print(f"Total: ${total_spending:,.2f}")
            
        except Exception as e:
            print(f"Error creating monthly breakdown: {e}")
    
    def create_category_trends(self) -> None:
        """Create line chart showing category spending trends over time."""
        try:
            monthly_data = self._aggregate_monthly_data()
            
            if not monthly_data:
                print("No data available for trend analysis")
                return
                
            # Prepare data for plotting
            months = sorted(monthly_data.keys())
            month_dates = [datetime.datetime.strptime(m, '%Y-%m') for m in months]
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Plot trend line for each category
            for i, category in enumerate(self.categories):
                amounts = []
                for month in months:
                    amount = monthly_data[month].get(category, 0)
                    amounts.append(amount)
                
                if any(amounts):  # Only plot if category has data
                    ax.plot(month_dates, amounts, 
                           marker='o', linewidth=2, markersize=6,
                           label=category, color=self.colors[i])
            
            # Formatting
            ax.set_title('Category Spending Trends Over Time', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount Spent ($)', fontsize=12)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            
            # Add grid and legend
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            plt.show()
            
            print("Category trends visualization created")
            
        except Exception as e:
            print(f"Error creating category trends: {e}")
    
    def create_summary_dashboard(self) -> None:
        """Create a comprehensive dashboard with multiple visualizations."""
        try:
            monthly_data = self._aggregate_monthly_data()
            
            if not monthly_data:
                print("No data available for dashboard")
                return
                
            fig = plt.figure(figsize=(16, 12))
            
            # 1. Monthly total spending (top left)
            ax1 = plt.subplot(2, 3, 1)
            months = sorted(monthly_data.keys())
            month_dates = [datetime.datetime.strptime(