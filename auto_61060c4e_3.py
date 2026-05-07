```python
"""
Personal Finance Dashboard Generator

This module creates a comprehensive financial visualization dashboard that generates:
- Monthly spending charts
- Category breakdowns
- Trend analysis graphs
- Budget vs actual comparison reports

The dashboard uses matplotlib for creating professional financial visualizations
with sample data generation capabilities for demonstration purposes.

Usage:
    python script.py

Dependencies:
    - matplotlib (for visualizations)
    - datetime (standard library)
    - random (standard library)
    - json (standard library)
"""

import json
import random
import datetime
from datetime import datetime as dt, timedelta
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
except ImportError:
    print("Error: matplotlib is required but not installed.")
    print("Please install it with: pip install matplotlib")
    sys.exit(1)

class FinanceDashboard:
    """Financial dashboard generator with comprehensive visualization capabilities."""
    
    def __init__(self):
        """Initialize the dashboard with sample data."""
        self.categories = [
            'Housing', 'Transportation', 'Food', 'Utilities', 
            'Entertainment', 'Healthcare', 'Shopping', 'Savings'
        ]
        self.months = []
        self.spending_data = {}
        self.budget_data = {}
        self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate realistic sample financial data for the last 12 months."""
        try:
            # Generate last 12 months
            current_date = dt.now()
            for i in range(12):
                month_date = current_date - timedelta(days=30*i)
                month_key = month_date.strftime('%Y-%m')
                self.months.insert(0, month_key)
            
            # Generate spending data with realistic patterns
            base_spending = {
                'Housing': 1200,
                'Transportation': 300,
                'Food': 400,
                'Utilities': 150,
                'Entertainment': 200,
                'Healthcare': 100,
                'Shopping': 250,
                'Savings': 500
            }
            
            # Generate budget (typically 10-20% higher than average spending)
            self.budget_data = {cat: int(amount * 1.15) for cat, amount in base_spending.items()}
            
            # Generate monthly variations
            for month in self.months:
                self.spending_data[month] = {}
                for category in self.categories:
                    base_amount = base_spending[category]
                    # Add seasonal variation and random fluctuation
                    variation = random.uniform(0.7, 1.3)
                    if category == 'Entertainment' and month.endswith(('12', '01')):
                        variation *= 1.5  # Holiday spending
                    elif category == 'Utilities' and month.endswith(('12', '01', '02', '06', '07', '08')):
                        variation *= 1.3  # Heating/cooling seasons
                    
                    amount = int(base_amount * variation)
                    self.spending_data[month][category] = amount
                    
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def create_monthly_spending_chart(self):
        """Create a bar chart showing total spending by month."""
        try:
            monthly_totals = []
            month_labels = []
            
            for month in self.months:
                total = sum(self.spending_data[month].values())
                monthly_totals.append(total)
                # Convert to readable month format
                month_obj = dt.strptime(month, '%Y-%m')
                month_labels.append(month_obj.strftime('%b %Y'))
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(month_labels, monthly_totals, color='steelblue', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 50,
                        f'${height:,.0f}', ha='center', va='bottom', fontsize=9)
            
            plt.title('Monthly Total Spending', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Calculate statistics
            avg_spending = sum(monthly_totals) / len(monthly_totals)
            max_spending = max(monthly_totals)
            min_spending = min(monthly_totals)
            
            print(f"Monthly Spending Summary:")
            print(f"Average: ${avg_spending:,.2f}")
            print(f"Highest: ${max_spending:,.2f}")
            print(f"Lowest: ${min_spending:,.2f}")
            print("-" * 40)
            
            plt.show()
            
        except Exception as e:
            print(f"Error creating monthly spending chart: {e}")
    
    def create_category_breakdown(self):
        """Create a pie chart showing spending breakdown by category."""
        try:
            # Calculate total spending by category across all months
            category_totals = {cat: 0 for cat in self.categories}
            
            for month_data in self.spending_data.values():
                for category, amount in month_data.items():
                    category_totals[category] += amount
            
            # Sort categories by spending amount
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            labels = [item[0] for item in sorted_categories]
            sizes = [item[1] for item in sorted_categories]
            
            # Create color palette
            colors = plt.cm.Set3(range(len(labels)))
            
            plt.figure(figsize=(10, 8))
            wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                              startangle=90, textprops={'fontsize': 10})
            
            # Enhance the appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title('Spending Breakdown by Category (12 Months)', fontsize=16, fontweight='bold')
            plt.axis('equal')
            
            # Print category breakdown
            print(f"Category Breakdown (Total):")
            total_all = sum(sizes)
            for label, size in sorted_categories:
                percentage = (size / total_all) * 100
                print(f"{label}: ${size:,.2f} ({percentage:.1f}%)")
            print("-" * 40)
            
            plt.show()
            
        except Exception as e:
            print(f"Error creating category breakdown: {e}")
    
    def create_trend_analysis(self):
        """Create line charts showing spending trends for major categories."""
        try:
            # Select top 4 spending categories for trend analysis
            category_totals = {cat: 0 for cat in self.categories}
            for month_data in self.spending_data.values():
                for category, amount in month_data.items():
                    category_totals[category] += amount
            
            top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:4]
            top_category_names = [item[0] for item in top_categories]
            
            plt.figure(figsize=(14, 8))
            
            # Create month labels for x-axis
            month_labels = []
            for month in self.months:
                month_obj = dt.strptime(month, '%Y-%m')
                month_labels.append(month_obj.strftime('%b %Y'))
            
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            
            for