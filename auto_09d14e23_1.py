```python
#!/usr/bin/env python3
"""
Monthly Spending Insights Visualization Module

This module generates comprehensive spending analytics and visualizations including:
- Category breakdown pie charts and bar charts
- Monthly spending trends over time
- Budget variance analysis with actual vs budgeted amounts
- Statistical summaries and insights

The module creates sample financial data for demonstration and generates
multiple visualization types to help analyze spending patterns and budget performance.

Usage:
    python script.py

Dependencies:
    - matplotlib (for plotting)
    - seaborn (for enhanced visualizations)
    - pandas (for data manipulation)
    - numpy (for numerical operations)

Note: This script requires matplotlib and seaborn to be installed.
If not available, it will print installation instructions.
"""

import sys
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

def check_dependencies():
    """Check if required visualization libraries are available."""
    missing_deps = []
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        missing_deps.append("matplotlib")
    
    try:
        import seaborn as sns
    except ImportError:
        missing_deps.append("seaborn")
    
    try:
        import pandas as pd
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import numpy as np
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install with: pip install matplotlib seaborn pandas numpy")
        return False
    
    return True

def generate_sample_data():
    """Generate sample spending data for the last 12 months."""
    try:
        categories = [
            "Groceries", "Restaurants", "Transportation", "Entertainment",
            "Utilities", "Shopping", "Healthcare", "Education", "Travel", "Other"
        ]
        
        # Generate monthly data for last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        monthly_data = []
        budgets = {
            "Groceries": 600, "Restaurants": 300, "Transportation": 250,
            "Entertainment": 200, "Utilities": 150, "Shopping": 400,
            "Healthcare": 100, "Education": 150, "Travel": 500, "Other": 100
        }
        
        for month_offset in range(12):
            current_date = start_date + timedelta(days=30 * month_offset)
            month_name = current_date.strftime("%B %Y")
            
            month_spending = {}
            for category in categories:
                # Add some randomness to spending (±30% of budget)
                base_amount = budgets[category]
                variation = random.uniform(0.7, 1.3)
                amount = round(base_amount * variation, 2)
                month_spending[category] = amount
            
            monthly_data.append({
                "month": month_name,
                "date": current_date,
                "spending": month_spending,
                "total": sum(month_spending.values()),
                "budget": sum(budgets.values())
            })
        
        return monthly_data, budgets, categories
    
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return None, None, None

def create_category_breakdown_chart(monthly_data, categories):
    """Create pie chart and bar chart for category spending breakdown."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Calculate total spending by category across all months
        category_totals = {category: 0 for category in categories}
        for month_data in monthly_data:
            for category, amount in month_data["spending"].items():
                category_totals[category] += amount
        
        # Create subplot for pie chart and bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Pie Chart
        values = list(category_totals.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        
        wedges, texts, autotexts = ax1.pie(values, labels=categories, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        ax1.set_title('Spending by Category (12-Month Total)', fontsize=14, fontweight='bold')
        
        # Bar Chart
        ax2.bar(categories, values, color=colors)
        ax2.set_title('Total Spending by Category', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Amount ($)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for i, v in enumerate(values):
            ax2.text(i, v + max(values) * 0.01, f'${v:,.0f}', 
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('category_breakdown.png', dpi=300, bbox_inches='tight')
        print("✓ Category breakdown chart saved as 'category_breakdown.png'")
        
        # Print summary
        total_spending = sum(values)
        print(f"\nCategory Spending Summary (12 months):")
        print(f"{'Category':<15} {'Amount':<12} {'Percentage':<10}")
        print("-" * 40)
        for category in sorted(categories, key=lambda x: category_totals[x], reverse=True):
            amount = category_totals[category]
            percentage = (amount / total_spending) * 100
            print(f"{category:<15} ${amount:>8,.0f} {percentage:>8.1f}%")
        print("-" * 40)
        print(f"{'TOTAL':<15} ${total_spending:>8,.0f} {100:>8.1f}%")
        
        plt.close()
        
    except Exception as e:
        print(f"Error creating category breakdown chart: {e}")

def create_spending_trends_chart(monthly_data):
    """Create line chart showing spending trends over time."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        
        dates = [data["date"] for data in monthly_data]
        totals = [data["total"] for data in monthly_data]
        budgets = [data["budget"] for data in monthly_data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot actual spending and budget lines
        ax.plot(dates, totals, marker='o', linewidth=2, markersize=6, 
                label='Actual Spending', color='#e74c3c')
        ax.plot(dates, budgets, marker='s', linewidth=2, markersize=6, 
                label='Budget', color='#2ecc71', linestyle='--')
        
        # Fill area between lines
        ax.fill_between(dates, totals, budgets, alpha=0.3, 
                       color='red' if sum(totals) > sum(budgets) else 'green')
        
        ax.set_title('Monthly Spending Trends vs Budget', fontsize=16, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_xlabel('Month', fontsize=12)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.xticks(rotation=45)
        
        # Add grid and legend
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        # Add trend statistics
        avg_spending = sum(totals) / len(totals)
        avg_budget = sum(budgets)