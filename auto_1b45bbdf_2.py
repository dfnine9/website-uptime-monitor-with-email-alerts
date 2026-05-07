```python
"""
Financial Data Visualization Module

This module generates comprehensive financial visualizations including:
- Pie charts for category spending breakdowns
- Line graphs for spending trends over time
- Bar charts comparing monthly spending by category

Dependencies: matplotlib, pandas (simulated data generation using built-in libraries)
Usage: python script.py
"""

import json
import random
import datetime
from collections import defaultdict
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
except ImportError:
    print("Error: matplotlib is required but not installed")
    print("Please install with: pip install matplotlib")
    sys.exit(1)

class FinancialVisualizer:
    """Generates financial visualizations from spending data"""
    
    def __init__(self):
        self.data = self._generate_sample_data()
        
    def _generate_sample_data(self):
        """Generate realistic sample financial data"""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Other']
        data = []
        
        # Generate 12 months of data
        start_date = datetime.date(2023, 1, 1)
        for month in range(12):
            current_date = start_date + datetime.timedelta(days=month*30)
            
            for category in categories:
                # Generate realistic spending amounts per category
                base_amounts = {
                    'Food': 400, 'Transportation': 200, 'Entertainment': 150,
                    'Utilities': 120, 'Healthcare': 100, 'Shopping': 180, 'Other': 80
                }
                
                amount = base_amounts[category] + random.randint(-50, 100)
                data.append({
                    'date': current_date,
                    'category': category,
                    'amount': max(amount, 0)  # Ensure non-negative
                })
                
        return data
    
    def create_pie_chart(self):
        """Create pie chart for category breakdown"""
        try:
            category_totals = defaultdict(float)
            for item in self.data:
                category_totals[item['category']] += item['amount']
            
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                             colors=colors, startangle=90)
            
            plt.title('Spending by Category - Annual Breakdown', fontsize=16, fontweight='bold')
            
            # Add total spending info
            total_spending = sum(amounts)
            plt.figtext(0.5, 0.02, f'Total Annual Spending: ${total_spending:,.2f}', 
                       ha='center', fontsize=12, style='italic')
            
            plt.tight_layout()
            plt.savefig('category_breakdown_pie.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"✓ Pie chart generated successfully")
            print(f"Total categories: {len(categories)}")
            print(f"Total spending: ${total_spending:,.2f}")
            
        except Exception as e:
            print(f"Error creating pie chart: {str(e)}")
    
    def create_line_graph(self):
        """Create line graph for spending trends over time"""
        try:
            # Aggregate monthly spending
            monthly_totals = defaultdict(float)
            for item in self.data:
                month_key = item['date'].strftime('%Y-%m')
                monthly_totals[month_key] += item['amount']
            
            # Sort by date
            sorted_months = sorted(monthly_totals.items())
            dates = [datetime.datetime.strptime(month, '%Y-%m') for month, _ in sorted_months]
            amounts = [amount for _, amount in sorted_months]
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, amounts, marker='o', linewidth=2, markersize=6, color='#2E86C1')
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            
            # Add trend line
            z = range(len(amounts))
            trend_coeffs = [sum(z[i] * amounts[i] for i in range(len(z))) / sum(z[i]**2 for i in range(len(z)))]
            trend_line = [trend_coeffs[0] * i + (sum(amounts) - trend_coeffs[0] * sum(z)) / len(z) for i in z]
            plt.plot(dates, trend_line, '--', color='red', alpha=0.7, label='Trend')
            
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Add statistics
            avg_monthly = sum(amounts) / len(amounts)
            plt.figtext(0.5, 0.02, f'Average Monthly Spending: ${avg_monthly:,.2f}', 
                       ha='center', fontsize=10, style='italic')
            
            plt.tight_layout()
            plt.savefig('spending_trends_line.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"✓ Line graph generated successfully")
            print(f"Average monthly spending: ${avg_monthly:,.2f}")
            
        except Exception as e:
            print(f"Error creating line graph: {str(e)}")
    
    def create_bar_chart(self):
        """Create bar chart comparing monthly spending by category"""
        try:
            # Organize data by month and category
            monthly_category_data = defaultdict(lambda: defaultdict(float))
            
            for item in self.data:
                month_key = item['date'].strftime('%Y-%m')
                monthly_category_data[month_key][item['category']] += item['amount']
            
            # Get all categories and months
            all_categories = set()
            for month_data in monthly_category_data.values():
                all_categories.update(month_data.keys())
            all_categories = sorted(list(all_categories))
            
            months = sorted(monthly_category_data.keys())
            
            # Prepare data for stacked bar chart
            fig, ax = plt.subplots(figsize=(14, 8))
            
            bottoms = [0] * len(months)
            colors = plt.cm.Set3(range(len(all_categories)))
            
            for i, category in enumerate(all_categories):
                amounts = [monthly_category_data[month].get(category, 0) for month in months]
                ax.bar(months, amounts, bottom=bottoms, label=category, color=colors[i])
                
                # Update bottoms for stacking
                bottoms = [bottom + amount for bottom, amount in zip(bottoms, amounts)]
            
            ax.set_title('Monthly Spending by Category', fontsize=16, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Rotate x-axis labels
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plt.savefig('monthly_category_bar.png', dpi=300, bbox_inches='tight')
            plt