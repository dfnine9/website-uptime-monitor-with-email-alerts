```python
#!/usr/bin/env python3
"""
Financial Data Visualization Module

This module generates comprehensive financial visualizations including:
- Monthly spending charts showing expenditure patterns over time
- Trend analysis graphs with moving averages and projections
- Budget vs actual spending comparisons with variance analysis

The module creates sample financial data and generates three types of charts:
1. Monthly spending bar chart with trend line
2. Category-wise spending pie chart with trend analysis
3. Budget vs actual comparison with variance highlighting

Uses matplotlib for visualization and includes error handling for robust execution.
No external dependencies required beyond standard library.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import numpy as np
except ImportError:
    print("Error: matplotlib is required but not available. Please install with: pip install matplotlib")
    sys.exit(1)

class FinancialDataGenerator:
    """Generates sample financial data for visualization"""
    
    def __init__(self):
        self.categories = ['Housing', 'Food', 'Transportation', 'Healthcare', 'Entertainment', 'Utilities', 'Shopping']
        self.months = self._generate_months(12)
    
    def _generate_months(self, count: int) -> List[datetime]:
        """Generate list of month dates"""
        end_date = datetime.now().replace(day=1)
        months = []
        for i in range(count):
            month = end_date - timedelta(days=30 * i)
            months.append(month)
        return sorted(months)
    
    def generate_spending_data(self) -> Dict[str, Any]:
        """Generate comprehensive spending data"""
        try:
            data = {
                'monthly_totals': {},
                'category_spending': {category: {} for category in self.categories},
                'budgets': {},
                'actual_spending': {}
            }
            
            # Generate monthly data
            for month in self.months:
                month_str = month.strftime('%Y-%m')
                
                # Base spending with seasonal variation
                base_spending = 3000 + random.randint(-500, 500)
                if month.month in [11, 12]:  # Holiday spending
                    base_spending *= 1.3
                elif month.month in [6, 7, 8]:  # Summer activities
                    base_spending *= 1.1
                
                data['monthly_totals'][month_str] = base_spending
                
                # Category breakdown
                remaining = base_spending
                for i, category in enumerate(self.categories):
                    if i == len(self.categories) - 1:  # Last category gets remainder
                        amount = remaining
                    else:
                        # Category-specific spending patterns
                        if category == 'Housing':
                            amount = base_spending * 0.3 + random.randint(-100, 100)
                        elif category == 'Food':
                            amount = base_spending * 0.2 + random.randint(-150, 150)
                        elif category == 'Transportation':
                            amount = base_spending * 0.15 + random.randint(-50, 100)
                        else:
                            amount = random.randint(50, 300)
                        
                        remaining -= amount
                    
                    data['category_spending'][category][month_str] = max(0, amount)
                
                # Budget vs actual
                budget = base_spending * random.uniform(0.9, 1.2)
                data['budgets'][month_str] = budget
                data['actual_spending'][month_str] = base_spending
            
            return data
            
        except Exception as e:
            print(f"Error generating spending data: {e}")
            return {}

class FinancialVisualizer:
    """Creates financial data visualizations"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
    
    def create_monthly_spending_chart(self) -> None:
        """Create monthly spending bar chart with trend line"""
        try:
            months = list(self.data['monthly_totals'].keys())
            amounts = list(self.data['monthly_totals'].values())
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Bar chart
            bars = ax.bar(months, amounts, color='steelblue', alpha=0.7, edgecolor='navy')
            
            # Trend line
            x_numeric = range(len(months))
            z = np.polyfit(x_numeric, amounts, 1)
            trend_line = np.poly1d(z)
            ax.plot(months, trend_line(x_numeric), color='red', linewidth=2, label='Trend')
            
            # Formatting
            ax.set_title('Monthly Spending Analysis', fontsize=16, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Spending Amount ($)', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                       f'${height:,.0f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            plt.show()
            print("Monthly spending chart displayed successfully")
            
        except Exception as e:
            print(f"Error creating monthly spending chart: {e}")
    
    def create_category_trend_analysis(self) -> None:
        """Create category spending trend analysis"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Pie chart for latest month spending
            latest_month = max(self.data['category_spending']['Housing'].keys())
            latest_spending = []
            labels = []
            
            for category in self.data['category_spending']:
                amount = self.data['category_spending'][category].get(latest_month, 0)
                if amount > 0:
                    latest_spending.append(amount)
                    labels.append(category)
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            wedges, texts, autotexts = ax1.pie(latest_spending, labels=labels, autopct='%1.1f%%',
                                             colors=colors, startangle=90)
            ax1.set_title(f'Category Spending Distribution\n{latest_month}', fontweight='bold')
            
            # Trend lines for top categories
            months = sorted(list(self.data['monthly_totals'].keys()))
            top_categories = sorted(labels, key=lambda x: self.data['category_spending'][x][latest_month], reverse=True)[:5]
            
            for category in top_categories:
                amounts = [self.data['category_spending'][category].get(month, 0) for month in months]
                ax2.plot(months, amounts, marker='o', linewidth=2, label=category)
            
            ax2.set_title('Top 5 Categories Trend Analysis', fontweight='bold')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Spending Amount ($)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            print("Category trend analysis displayed successfully")
            
        except Exception as e:
            print(f"Error creating category trend analysis: {e}")
    
    def create_budget_comparison(self) -> None:
        """Create budget vs actual spending comparison"""
        try:
            months = sorted(list(self