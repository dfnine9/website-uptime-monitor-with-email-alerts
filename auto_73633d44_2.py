```python
"""
Personal Finance Visualization Tool

This module generates comprehensive financial charts including:
- Spending by category (pie chart)
- Monthly spending trends (line chart)
- Budget vs actual comparisons (bar chart)

Uses matplotlib for visualization with sample financial data.
Designed to be self-contained with minimal dependencies.

Usage: python script.py
"""

import json
import sys
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from collections import defaultdict
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install matplotlib: pip install matplotlib")
    sys.exit(1)


def generate_sample_data() -> Tuple[List[Dict], Dict[str, float]]:
    """Generate sample financial data for demonstration."""
    categories = ['Food', 'Housing', 'Transportation', 'Entertainment', 'Healthcare', 'Shopping', 'Utilities']
    
    # Generate 6 months of sample transactions
    transactions = []
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(150):  # 150 sample transactions
        transaction_date = start_date + timedelta(days=random.randint(0, 180))
        category = random.choice(categories)
        
        # Category-specific spending ranges
        amount_ranges = {
            'Food': (15, 80),
            'Housing': (800, 1500),
            'Transportation': (25, 150),
            'Entertainment': (20, 100),
            'Healthcare': (50, 300),
            'Shopping': (30, 200),
            'Utilities': (100, 250)
        }
        
        min_amount, max_amount = amount_ranges[category]
        amount = round(random.uniform(min_amount, max_amount), 2)
        
        transactions.append({
            'date': transaction_date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': amount,
            'description': f"{category} expense"
        })
    
    # Sample budget data
    budget = {
        'Food': 1500,
        'Housing': 2500,
        'Transportation': 800,
        'Entertainment': 400,
        'Healthcare': 500,
        'Shopping': 600,
        'Utilities': 350
    }
    
    return transactions, budget


def calculate_spending_by_category(transactions: List[Dict]) -> Dict[str, float]:
    """Calculate total spending by category."""
    try:
        category_totals = defaultdict(float)
        
        for transaction in transactions:
            category = transaction['category']
            amount = float(transaction['amount'])
            category_totals[category] += amount
            
        return dict(category_totals)
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error calculating spending by category: {e}")
        return {}


def calculate_monthly_trends(transactions: List[Dict]) -> Dict[str, float]:
    """Calculate spending trends by month."""
    try:
        monthly_totals = defaultdict(float)
        
        for transaction in transactions:
            date_str = transaction['date']
            amount = float(transaction['amount'])
            
            # Extract year-month for grouping
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            month_key = date_obj.strftime('%Y-%m')
            monthly_totals[month_key] += amount
            
        return dict(monthly_totals)
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error calculating monthly trends: {e}")
        return {}


def create_spending_by_category_chart(category_spending: Dict[str, float]) -> None:
    """Create pie chart showing spending by category."""
    try:
        if not category_spending:
            print("No category data available for pie chart")
            return
            
        plt.figure(figsize=(10, 8))
        
        categories = list(category_spending.keys())
        amounts = list(category_spending.values())
        
        # Create pie chart with custom colors
        colors = plt.cm.Set3(range(len(categories)))
        wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        
        plt.title('Spending by Category', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        # Add legend with amounts
        legend_labels = [f"{cat}: ${amt:,.2f}" for cat, amt in category_spending.items()]
        plt.legend(wedges, legend_labels, title="Categories", loc="center left", 
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        plt.show()
        
        print("✓ Category spending pie chart displayed")
        
    except Exception as e:
        print(f"Error creating category spending chart: {e}")


def create_monthly_trends_chart(monthly_data: Dict[str, float]) -> None:
    """Create line chart showing monthly spending trends."""
    try:
        if not monthly_data:
            print("No monthly data available for trends chart")
            return
            
        plt.figure(figsize=(12, 6))
        
        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys())
        dates = [datetime.strptime(month, '%Y-%m') for month in sorted_months]
        amounts = [monthly_data[month] for month in sorted_months]
        
        plt.plot(dates, amounts, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        plt.fill_between(dates, amounts, alpha=0.3, color='#A23B72')
        
        plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Total Spending ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        # Add value labels on points
        for date, amount in zip(dates, amounts):
            plt.annotate(f'${amount:,.0f}', (date, amount), 
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        plt.tight_layout()
        plt.show()
        
        print("✓ Monthly trends line chart displayed")
        
    except Exception as e:
        print(f"Error creating monthly trends chart: {e}")


def create_budget_comparison_chart(category_spending: Dict[str, float], budget: Dict[str, float]) -> None:
    """Create bar chart comparing budget vs actual spending."""
    try:
        if not category_spending or not budget:
            print("Insufficient data for budget comparison chart")
            return
            
        plt.figure(figsize=(12, 8))
        
        # Get common categories
        categories = list(set(category_spending.keys()) & set(budget.keys()))
        categories.sort()
        
        if not categories:
            print("No common categories found between spending and budget data")
            return
        
        actual_amounts = [category_spending.get(cat, 0) for cat in categories]
        budget_amounts = [budget.get(cat, 0) for cat in categories]
        
        x_pos = range(len(categories))
        width = 0.35
        
        # Create bars
        bars1 = plt.bar([x - width/2 for x in x_pos], budget_amounts, width, 
                       label='Budget', color='#4CAF50', alpha=0.8)
        bars2 = plt.bar([x + width/2 for x in x_pos], actual_amounts, width, 
                       label='Actual', color='#