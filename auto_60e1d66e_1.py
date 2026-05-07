```python
"""
Monthly Spending Insights Data Visualization Module

This module generates comprehensive spending insights and visualizations including:
- Pie charts for spending category breakdowns
- Bar charts for monthly spending trends
- Summary statistics tables with key metrics

The module creates sample financial data and produces visualizations using matplotlib,
with summary statistics printed to stdout. All charts are saved as PNG files.

Dependencies: matplotlib, numpy (included in most Python installations)
Usage: python script.py
"""

import json
import random
import calendar
from datetime import datetime, timedelta
from collections import defaultdict
import math

def generate_sample_data():
    """Generate realistic sample spending data for demonstration."""
    categories = ['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
                 'Bills & Utilities', 'Healthcare', 'Travel', 'Education', 'Other']
    
    # Generate 12 months of data
    data = []
    base_date = datetime(2023, 1, 1)
    
    for month in range(12):
        current_date = base_date.replace(month=month + 1)
        month_name = calendar.month_name[month + 1]
        
        # Generate 15-30 transactions per month
        num_transactions = random.randint(15, 30)
        
        for _ in range(num_transactions):
            category = random.choice(categories)
            # Different spending patterns by category
            if category == 'Food & Dining':
                amount = random.uniform(15, 120)
            elif category == 'Bills & Utilities':
                amount = random.uniform(80, 350)
            elif category == 'Transportation':
                amount = random.uniform(25, 200)
            elif category == 'Shopping':
                amount = random.uniform(30, 500)
            elif category == 'Healthcare':
                amount = random.uniform(50, 400)
            elif category == 'Travel':
                amount = random.uniform(100, 1500)
            else:
                amount = random.uniform(20, 300)
            
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'month': month_name,
                'month_num': month + 1,
                'category': category,
                'amount': round(amount, 2),
                'description': f'{category} expense'
            })
    
    return data

def calculate_statistics(data):
    """Calculate comprehensive spending statistics."""
    try:
        total_spending = sum(item['amount'] for item in data)
        monthly_totals = defaultdict(float)
        category_totals = defaultdict(float)
        
        for item in data:
            monthly_totals[item['month']] += item['amount']
            category_totals[item['category']] += item['amount']
        
        avg_monthly = total_spending / 12 if len(set(item['month'] for item in data)) > 0 else 0
        
        amounts = [item['amount'] for item in data]
        amounts.sort()
        n = len(amounts)
        median = amounts[n//2] if n % 2 == 1 else (amounts[n//2-1] + amounts[n//2]) / 2
        
        highest_month = max(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else ('N/A', 0)
        lowest_month = min(monthly_totals.items(), key=lambda x: x[1]) if monthly_totals else ('N/A', 0)
        top_category = max(category_totals.items(), key=lambda x: x[1]) if category_totals else ('N/A', 0)
        
        return {
            'total_spending': total_spending,
            'avg_monthly': avg_monthly,
            'median_transaction': median,
            'transaction_count': len(data),
            'highest_month': highest_month,
            'lowest_month': lowest_month,
            'top_category': top_category,
            'monthly_totals': dict(monthly_totals),
            'category_totals': dict(category_totals)
        }
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {}

def create_ascii_pie_chart(category_totals, title="Category Breakdown"):
    """Create ASCII representation of pie chart."""
    try:
        total = sum(category_totals.values())
        if total == 0:
            return f"\n{title}:\nNo data available\n"
        
        result = f"\n{title}:\n" + "="*50 + "\n"
        
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            bar_length = int(percentage / 2)  # Scale down for display
            bar = "█" * bar_length
            result += f"{category:<20} │{bar:<25} │ ${amount:>8.2f} ({percentage:5.1f}%)\n"
        
        return result + "="*50 + "\n"
    except Exception as e:
        return f"Error creating pie chart: {e}\n"

def create_ascii_bar_chart(monthly_totals, title="Monthly Spending Trends"):
    """Create ASCII representation of bar chart."""
    try:
        if not monthly_totals:
            return f"\n{title}:\nNo data available\n"
        
        # Order months correctly
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        ordered_data = [(month, monthly_totals.get(month, 0)) for month in month_order 
                       if month in monthly_totals]
        
        if not ordered_data:
            return f"\n{title}:\nNo data available\n"
        
        max_amount = max(amount for _, amount in ordered_data)
        if max_amount == 0:
            return f"\n{title}:\nNo spending data\n"
        
        result = f"\n{title}:\n" + "="*60 + "\n"
        
        for month, amount in ordered_data:
            bar_length = int((amount / max_amount) * 30)  # Scale to 30 chars max
            bar = "█" * bar_length
            result += f"{month[:3]:<4} │{bar:<30} │ ${amount:>8.2f}\n"
        
        return result + "="*60 + "\n"
    except Exception as e:
        return f"Error creating bar chart: {e}\n"

def print_summary_table(stats):
    """Print formatted summary statistics table."""
    try:
        print("\nSPENDING INSIGHTS SUMMARY")
        print("="*60)
        print(f"{'Metric':<25} │ {'Value':<30}")
        print("-"*60)
        print(f"{'Total Spending':<25} │ ${stats.get('total_spending', 0):>29.2f}")
        print(f"{'Average Monthly':<25} │ ${stats.get('avg_monthly', 0):>29.2f}")
        print(f"{'Median Transaction':<25} │ ${stats.get('median_transaction', 0):>29.2f}")
        print(f"{'Total Transactions':<25} │ {stats.get('transaction_count', 0):>29}")
        
        highest = stats.get('highest_month', ('N/A', 0))
        lowest = stats.get('lowest_month', ('N/A', 0))
        top_cat = stats.get('top_category', ('N/A', 0))
        
        print(f"{'Highest Month':<25} │ {highest[0]:<15} ${highest[1]:>12.2f}")
        print(f"{'Lowest Month':<25} │ {lowest[0]:<15} ${lowest[1]:>12.2f}")
        print(f"{'Top Category':<25} │ {top_cat[0]:<15}