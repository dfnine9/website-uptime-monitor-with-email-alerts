```python
"""
Financial Visualization Module

This module generates comprehensive financial visualizations including:
- Monthly spending breakdown charts
- Category comparison analysis
- Budget vs actual spending analysis

Uses matplotlib for creating static charts with sample financial data.
Designed to be self-contained with minimal dependencies.

Usage: python script.py
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random
import sys
import os

# Suppress matplotlib GUI warnings
os.environ['MPLBACKEND'] = 'Agg'

def generate_sample_data():
    """Generate sample financial data for visualization."""
    categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Generate monthly spending data
    monthly_data = {}
    for month in months:
        monthly_data[month] = {cat: random.randint(200, 1500) for cat in categories}
    
    # Generate budget vs actual data
    budget_data = {cat: random.randint(800, 2000) for cat in categories}
    actual_data = {cat: budget_data[cat] + random.randint(-300, 400) for cat in categories}
    
    return monthly_data, budget_data, actual_data, categories, months

def create_monthly_breakdown_chart(monthly_data, categories, months):
    """Create a stacked bar chart showing monthly spending breakdown by category."""
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data for stacked bar chart
        bottom = [0] * len(months)
        colors = plt.cm.Set3(range(len(categories)))
        
        for i, category in enumerate(categories):
            values = [monthly_data[month][category] for month in months]
            ax.bar(months, values, bottom=bottom, label=category, color=colors[i])
            bottom = [b + v for b, v in zip(bottom, values)]
        
        ax.set_title('Monthly Spending Breakdown by Category', fontsize=16, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('monthly_breakdown.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Monthly breakdown chart created: monthly_breakdown.png")
        
    except Exception as e:
        print(f"Error creating monthly breakdown chart: {e}")
        return False
    
    return True

def create_category_comparison_chart(monthly_data, categories, months):
    """Create a horizontal bar chart comparing total spending by category."""
    try:
        # Calculate total spending per category
        category_totals = {}
        for category in categories:
            total = sum(monthly_data[month][category] for month in months)
            category_totals[category] = total
        
        # Sort categories by total spending
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        categories_sorted = [item[0] for item in sorted_categories]
        totals_sorted = [item[1] for item in sorted_categories]
        colors = plt.cm.viridis(range(len(categories_sorted)))
        
        bars = ax.barh(categories_sorted, totals_sorted, color=colors)
        
        # Add value labels on bars
        for i, (bar, total) in enumerate(zip(bars, totals_sorted)):
            ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2, 
                   f'${total:,}', va='center', fontweight='bold')
        
        ax.set_title('Annual Spending by Category', fontsize=16, fontweight='bold')
        ax.set_xlabel('Total Amount ($)', fontsize=12)
        ax.set_ylabel('Category', fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig('category_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Category comparison chart created: category_comparison.png")
        
    except Exception as e:
        print(f"Error creating category comparison chart: {e}")
        return False
    
    return True

def create_budget_vs_actual_chart(budget_data, actual_data, categories):
    """Create a grouped bar chart comparing budget vs actual spending."""
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x_pos = range(len(categories))
        width = 0.35
        
        budget_values = [budget_data[cat] for cat in categories]
        actual_values = [actual_data[cat] for cat in categories]
        
        bars1 = ax.bar([x - width/2 for x in x_pos], budget_values, width, 
                      label='Budget', color='skyblue', alpha=0.8)
        bars2 = ax.bar([x + width/2 for x in x_pos], actual_values, width,
                      label='Actual', color='lightcoral', alpha=0.8)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 20,
                       f'${int(height):,}', ha='center', va='bottom', fontsize=9)
        
        # Add variance indicators
        for i, (budget, actual) in enumerate(zip(budget_values, actual_values)):
            variance = actual - budget
            color = 'red' if variance > 0 else 'green'
            ax.annotate(f'{variance:+d}', xy=(i, max(budget, actual) + 100),
                       ha='center', color=color, fontweight='bold', fontsize=8)
        
        ax.set_title('Budget vs Actual Spending Analysis', fontsize=16, fontweight='bold')
        ax.set_xlabel('Category', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('budget_vs_actual.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Budget vs actual chart created: budget_vs_actual.png")
        
    except Exception as e:
        print(f"Error creating budget vs actual chart: {e}")
        return False
    
    return True

def create_spending_trend_chart(monthly_data, categories, months):
    """Create a line chart showing spending trends over time."""
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Calculate total monthly spending
        monthly_totals = [sum(monthly_data[month].values()) for month in months]
        
        ax.plot(months, monthly_totals, marker='o', linewidth=3, markersize=8, 
               color='darkblue', label='Total Monthly Spending')
        
        # Add trend lines for top 3 categories by total spending
        category_totals = {cat: sum(monthly_data[month][cat] for month in months)