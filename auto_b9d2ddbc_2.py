```python
"""
Financial Data Visualization Script

This module creates comprehensive financial visualizations including:
- Bar charts for category spending analysis
- Line graphs for spending trends over time
- Pie charts for budget allocation breakdown

Uses matplotlib for data visualization with sample financial data.
Self-contained script with error handling and stdout output.

Usage: python script.py
"""

import sys
import traceback
from datetime import datetime, timedelta
import random

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    print("Error: matplotlib is required but not installed.")
    print("Install with: pip install matplotlib")
    sys.exit(1)

def generate_sample_data():
    """Generate realistic sample financial data for visualization."""
    
    # Category spending data
    categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Healthcare', 'Utilities', 'Shopping', 'Savings']
    category_spending = {
        'Housing': 2500,
        'Food': 800,
        'Transportation': 600,
        'Entertainment': 400,
        'Healthcare': 300,
        'Utilities': 250,
        'Shopping': 350,
        'Savings': 1200
    }
    
    # Monthly trend data (12 months)
    months = []
    spending_trends = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(12):
        month_date = base_date + timedelta(days=30*i)
        months.append(month_date)
        # Generate realistic monthly spending with some variation
        base_spending = 4500
        variation = random.uniform(-500, 800)
        spending_trends.append(base_spending + variation)
    
    # Budget allocation data
    budget_categories = ['Fixed Costs', 'Variable Expenses', 'Discretionary', 'Savings', 'Emergency Fund']
    budget_allocation = [45, 25, 15, 10, 5]  # Percentages
    
    return category_spending, months, spending_trends, budget_categories, budget_allocation

def create_category_bar_chart(category_data):
    """Create and display bar chart for category spending."""
    try:
        categories = list(category_data.keys())
        amounts = list(category_data.values())
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(categories, amounts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'])
        
        plt.title('Monthly Spending by Category', fontsize=16, fontweight='bold')
        plt.xlabel('Categories', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, amount in zip(bars, amounts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'${amount:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.grid(axis='y', alpha=0.3)
        
        print("✓ Category spending bar chart created successfully")
        print(f"Total spending across categories: ${sum(amounts):,.2f}")
        
        return plt.gcf()
        
    except Exception as e:
        print(f"Error creating category bar chart: {str(e)}")
        traceback.print_exc()
        return None

def create_trend_line_graph(months, spending_data):
    """Create and display line graph for spending trends."""
    try:
        plt.figure(figsize=(12, 6))
        
        plt.plot(months, spending_data, marker='o', linewidth=2.5, markersize=8, 
                color='#FF6B6B', markerfacecolor='#FF6B6B', markeredgecolor='white', markeredgewidth=2)
        
        plt.title('Monthly Spending Trends (12 Months)', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Total Spending ($)', fontsize=12)
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45)
        
        # Add trend line
        z = np.polyfit(range(len(spending_data)), spending_data, 1)
        p = np.poly1d(z)
        plt.plot(months, p(range(len(spending_data))), "--", alpha=0.7, color='#45B7D1', linewidth=2)
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Calculate trend statistics
        avg_spending = sum(spending_data) / len(spending_data)
        trend_slope = (spending_data[-1] - spending_data[0]) / len(spending_data)
        
        print("✓ Spending trend line graph created successfully")
        print(f"Average monthly spending: ${avg_spending:,.2f}")
        print(f"Spending trend: {'Increasing' if trend_slope > 0 else 'Decreasing'} by ${abs(trend_slope):,.2f}/month")
        
        return plt.gcf()
        
    except Exception as e:
        print(f"Error creating trend line graph: {str(e)}")
        traceback.print_exc()
        return None

def create_budget_pie_chart(categories, percentages):
    """Create and display pie chart for budget allocation."""
    try:
        plt.figure(figsize=(10, 8))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        explode = (0.05, 0.05, 0.05, 0.1, 0.05)  # Slightly separate slices
        
        wedges, texts, autotexts = plt.pie(percentages, labels=categories, colors=colors, 
                                          autopct='%1.1f%%', startangle=90, explode=explode,
                                          shadow=True, textprops={'fontsize': 11, 'fontweight': 'bold'})
        
        plt.title('Budget Allocation by Category', fontsize=16, fontweight='bold', pad=20)
        
        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.axis('equal')  # Equal aspect ratio ensures circular pie
        
        print("✓ Budget allocation pie chart created successfully")
        
        # Print budget breakdown
        print("\nBudget Allocation Breakdown:")
        for category, percentage in zip(categories, percentages):
            print(f"  {category}: {percentage}%")
        
        return plt.gcf()
        
    except Exception as e:
        print(f"Error creating budget pie chart: {str(e)}")
        traceback.print_exc()
        return None

def main():
    """Main function to generate all financial visualizations."""
    try:
        print("=" * 60)
        print("FINANCIAL DATA VISUALIZATION GENERATOR")
        print("=" * 60)
        print()
        
        # Import numpy for trend calculations
        global np
        try:
            import numpy as np
        except ImportError:
            print("Warning: numpy not available, using basic trend calculation")
            # Simple fallback for trend calculation
            class SimpleNumpy:
                @staticmethod
                def polyfit(x, y, deg):
                    # Simple linear regression
                    n = len(x)
                    sum_x = sum(x)
                    sum_y = sum(y)
                    sum_xy = sum(x[i] *