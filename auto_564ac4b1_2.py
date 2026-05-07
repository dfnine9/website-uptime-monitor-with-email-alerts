```python
"""
Personal Finance Visualization Tool

This module generates interactive visualizations for personal finance data including:
- Monthly spending breakdowns by category (pie charts)
- Spending trends over time (line charts) 
- Budget vs actual spending comparisons (bar charts)

The script creates sample financial data and generates visualizations using matplotlib.
All charts are displayed interactively and can be saved as image files.

Usage: python script.py

Dependencies: matplotlib (will attempt to install if not available)
"""

import sys
import subprocess
import json
from datetime import datetime, timedelta
import random

# Check and install matplotlib if needed
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
except ImportError:
    print("Installing matplotlib...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.patches import Wedge
        print("Successfully installed matplotlib")
    except Exception as e:
        print(f"Error installing matplotlib: {e}")
        sys.exit(1)

def generate_sample_data():
    """Generate sample financial data for demonstration purposes."""
    categories = ['Food', 'Housing', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping']
    budgets = {'Food': 600, 'Housing': 1200, 'Transportation': 300, 'Entertainment': 200, 'Utilities': 150, 'Healthcare': 100, 'Shopping': 250}
    
    data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(12):  # 12 months of data
        month_date = start_date + timedelta(days=30 * i)
        
        for category in categories:
            # Generate realistic spending with some variance
            base_amount = budgets[category] / 4  # Weekly amount
            for week in range(4):
                amount = base_amount * random.uniform(0.7, 1.3)
                data.append({
                    'date': month_date + timedelta(days=7 * week),
                    'category': category,
                    'amount': round(amount, 2),
                    'budget': budgets[category]
                })
    
    return data, budgets

def create_monthly_breakdown(data):
    """Create pie chart showing monthly spending breakdown by category."""
    try:
        # Get most recent month's data
        latest_month = max([item['date'] for item in data])
        month_start = latest_month.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        monthly_data = [item for item in data if month_start <= item['date'] < next_month]
        
        # Aggregate by category
        category_totals = {}
        for item in monthly_data:
            category = item['category']
            category_totals[category] = category_totals.get(category, 0) + item['amount']
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        colors = plt.cm.Set3(range(len(categories)))
        
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title(f'Monthly Spending Breakdown - {latest_month.strftime("%B %Y")}', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        # Add total spending text
        total_spending = sum(amounts)
        plt.figtext(0.02, 0.02, f'Total Spending: ${total_spending:,.2f}', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('monthly_breakdown.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Monthly breakdown for {latest_month.strftime('%B %Y')}:")
        for category, amount in category_totals.items():
            print(f"  {category}: ${amount:,.2f} ({amount/total_spending*100:.1f}%)")
        print(f"Total: ${total_spending:,.2f}\n")
        
    except Exception as e:
        print(f"Error creating monthly breakdown: {e}")

def create_trend_chart(data):
    """Create line chart showing spending trends over time."""
    try:
        # Aggregate monthly spending
        monthly_totals = {}
        for item in data:
            month_key = item['date'].strftime('%Y-%m')
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + item['amount']
        
        # Sort by date
        sorted_months = sorted(monthly_totals.items())
        dates = [datetime.strptime(month, '%Y-%m') for month, _ in sorted_months]
        amounts = [amount for _, amount in sorted_months]
        
        # Create line chart
        plt.figure(figsize=(12, 6))
        plt.plot(dates, amounts, marker='o', linewidth=2, markersize=6, color='#2E86C1')
        plt.fill_between(dates, amounts, alpha=0.3, color='#2E86C1')
        
        plt.title('Monthly Spending Trends Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Total Spending ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45)
        
        # Add trend line
        import numpy as np
        x_numeric = [i for i in range(len(dates))]
        z = np.polyfit(x_numeric, amounts, 1)
        p = np.poly1d(z)
        plt.plot(dates, p(x_numeric), "--", color='red', alpha=0.8, linewidth=1.5, label=f'Trend (${z[0]:+.2f}/month)')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('spending_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print trend analysis
        avg_spending = sum(amounts) / len(amounts)
        trend_direction = "increasing" if z[0] > 0 else "decreasing"
        print(f"Spending Trends Analysis:")
        print(f"  Average monthly spending: ${avg_spending:,.2f}")
        print(f"  Trend: {trend_direction} by ${abs(z[0]):.2f} per month")
        print(f"  Total period: {dates[0].strftime('%b %Y')} to {dates[-1].strftime('%b %Y')}\n")
        
    except Exception as e:
        print(f"Error creating trend chart: {e}")

def create_budget_comparison(data, budgets):
    """Create bar chart comparing budget vs actual spending."""
    try:
        # Get most recent month's data
        latest_month = max([item['date'] for item in data])
        month_start = latest_month.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        monthly_data = [item for item in data if month_start <= item['date'] < next_month]
        
        # Aggregate by category
        actual_spending = {}
        for item in monthly_data:
            category = item['category']
            actual_spending[category] = actual_spending.get(category, 0) + item['amount']
        
        # Create comparison chart
        categories = list(budgets.keys())
        budget_amounts = [budgets[cat