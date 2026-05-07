```python
#!/usr/bin/env python3
"""
Monthly Spending Report Visualization Generator

This module generates comprehensive monthly spending reports using matplotlib
for data visualization. It creates three types of charts:
1. Bar charts showing spending by category for each month
2. Line charts displaying spending trends over time
3. Pie charts showing expense distribution for the current month

The script generates sample financial data and creates interactive visualizations
to help users understand their spending patterns and financial trends.

Dependencies: matplotlib, numpy (standard data science libraries)
Usage: python script.py
"""

import json
import random
import datetime
from pathlib import Path
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
except ImportError as e:
    print(f"Error: Required package not found: {e}")
    print("Please install matplotlib and numpy: pip install matplotlib numpy")
    sys.exit(1)


class SpendingReportGenerator:
    """Generates monthly spending reports with comprehensive visualizations."""
    
    def __init__(self):
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Personal Care', 'Gifts & Donations'
        ]
        self.months = self._generate_last_12_months()
        self.spending_data = self._generate_sample_data()
    
    def _generate_last_12_months(self):
        """Generate list of last 12 months as datetime objects."""
        try:
            months = []
            current_date = datetime.date.today().replace(day=1)
            
            for i in range(12):
                months.insert(0, current_date)
                # Go to previous month
                if current_date.month == 1:
                    current_date = current_date.replace(year=current_date.year - 1, month=12)
                else:
                    current_date = current_date.replace(month=current_date.month - 1)
            
            return months
        except Exception as e:
            print(f"Error generating months: {e}")
            return []
    
    def _generate_sample_data(self):
        """Generate realistic sample spending data."""
        try:
            data = {}
            
            for month in self.months:
                month_key = month.strftime('%Y-%m')
                data[month_key] = {}
                
                # Generate seasonal variations
                base_multiplier = 1.0
                if month.month in [11, 12]:  # Holiday spending
                    base_multiplier = 1.4
                elif month.month in [6, 7, 8]:  # Summer spending
                    base_multiplier = 1.2
                
                for category in self.categories:
                    # Base spending amounts per category
                    base_amounts = {
                        'Food & Dining': 600,
                        'Transportation': 300,
                        'Shopping': 400,
                        'Entertainment': 250,
                        'Bills & Utilities': 800,
                        'Healthcare': 200,
                        'Travel': 300,
                        'Education': 150,
                        'Personal Care': 100,
                        'Gifts & Donations': 100
                    }
                    
                    base_amount = base_amounts.get(category, 200)
                    # Add random variation (±30%)
                    variation = random.uniform(0.7, 1.3)
                    amount = base_amount * base_multiplier * variation
                    data[month_key][category] = round(amount, 2)
            
            return data
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}
    
    def create_category_bar_chart(self):
        """Create bar chart showing spending by category for recent months."""
        try:
            # Use last 6 months for readability
            recent_months = self.months[-6:]
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            x = np.arange(len(self.categories))
            width = 0.12
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(recent_months)))
            
            for i, month in enumerate(recent_months):
                month_key = month.strftime('%Y-%m')
                amounts = [self.spending_data[month_key][cat] for cat in self.categories]
                
                offset = (i - len(recent_months)/2) * width
                bars = ax.bar(x + offset, amounts, width, 
                             label=month.strftime('%b %Y'), color=colors[i], alpha=0.8)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                               f'${height:.0f}', ha='center', va='bottom', fontsize=8)
            
            ax.set_xlabel('Spending Categories', fontweight='bold')
            ax.set_ylabel('Amount ($)', fontweight='bold')
            ax.set_title('Monthly Spending by Category (Last 6 Months)', 
                        fontweight='bold', fontsize=14)
            ax.set_xticks(x)
            ax.set_xticklabels(self.categories, rotation=45, ha='right')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('category_spending_bar_chart.png', dpi=300, bbox_inches='tight')
            print("✓ Category bar chart saved as 'category_spending_bar_chart.png'")
            
        except Exception as e:
            print(f"Error creating category bar chart: {e}")
    
    def create_spending_trend_line_chart(self):
        """Create line chart showing spending trends over time."""
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Calculate monthly totals and category trends
            monthly_totals = []
            dates = []
            
            for month in self.months:
                month_key = month.strftime('%Y-%m')
                total = sum(self.spending_data[month_key].values())
                monthly_totals.append(total)
                dates.append(month)
            
            # Plot total spending trend
            ax.plot(dates, monthly_totals, marker='o', linewidth=3, 
                   markersize=8, color='darkblue', label='Total Monthly Spending')
            
            # Plot top 3 category trends
            top_categories = ['Food & Dining', 'Bills & Utilities', 'Shopping']
            colors = ['red', 'green', 'orange']
            
            for i, category in enumerate(top_categories):
                category_amounts = []
                for month in self.months:
                    month_key = month.strftime('%Y-%m')
                    category_amounts.append(self.spending_data[month_key][category])
                
                ax.plot(dates, category_amounts, marker='s', linewidth=2, 
                       markersize=6, color=colors[i], label=category, alpha=0.8)
            
            # Formatting
            ax.set_xlabel('Month', fontweight='bold')
            ax.set_ylabel('Amount ($)', fontweight='bold')
            ax.set_title('Spending Trends Over Time (12 Months)', 
                        fontweight='bold', fontsize=14)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add annotations for highest and lowest points
            max