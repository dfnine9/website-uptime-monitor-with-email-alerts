```python
#!/usr/bin/env python3
"""
Personal Finance Visualization Generator

This module creates comprehensive financial visualizations for expense tracking and analysis.
It generates bar charts for category spending, pie charts for expense distribution, 
and line graphs for monthly trends with export capabilities to PNG/HTML formats.

Features:
- Category spending bar charts
- Expense distribution pie charts  
- Monthly trend line graphs
- Export to PNG and HTML formats
- Sample data generation for demonstration
- Error handling and validation

Dependencies: matplotlib, plotly (install via: pip install matplotlib plotly)
Usage: python script.py
"""

import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available. Install with: pip install plotly")


def generate_sample_data():
    """Generate sample financial data for demonstration."""
    categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping', 'Rent']
    
    # Generate monthly data for the past 12 months
    monthly_data = []
    base_date = datetime.now().replace(day=1) - timedelta(days=365)
    
    for i in range(12):
        month_date = base_date + timedelta(days=30 * i)
        month_expenses = {}
        
        for category in categories:
            # Generate realistic expense amounts with some variation
            base_amounts = {
                'Food': 400, 'Transportation': 200, 'Entertainment': 150,
                'Utilities': 120, 'Healthcare': 100, 'Shopping': 250, 'Rent': 1200
            }
            variation = random.uniform(0.7, 1.3)
            amount = base_amounts[category] * variation
            month_expenses[category] = round(amount, 2)
        
        monthly_data.append({
            'date': month_date.strftime('%Y-%m'),
            'expenses': month_expenses
        })
    
    return monthly_data


def create_matplotlib_visualizations(data):
    """Create visualizations using matplotlib."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, skipping matplotlib visualizations.")
        return
    
    try:
        # Calculate totals for each category
        category_totals = {}
        monthly_totals = {}
        
        for month_data in data:
            month = month_data['date']
            month_total = 0
            
            for category, amount in month_data['expenses'].items():
                category_totals[category] = category_totals.get(category, 0) + amount
                month_total += amount
            
            monthly_totals[month] = month_total
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Personal Finance Dashboard - Matplotlib', fontsize=16, fontweight='bold')
        
        # 1. Category spending bar chart
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        colors = plt.cm.Set3(range(len(categories)))
        
        bars = ax1.bar(categories, amounts, color=colors)
        ax1.set_title('Total Spending by Category', fontweight='bold')
        ax1.set_ylabel('Amount ($)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 10,
                    f'${height:.0f}', ha='center', va='bottom')
        
        # 2. Expense distribution pie chart
        ax2.pie(amounts, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Expense Distribution', fontweight='bold')
        
        # 3. Monthly trends line graph
        months = list(monthly_totals.keys())
        month_amounts = list(monthly_totals.values())
        
        ax3.plot(months, month_amounts, marker='o', linewidth=2, markersize=6)
        ax3.set_title('Monthly Spending Trends', fontweight='bold')
        ax3.set_ylabel('Total Amount ($)')
        ax3.set_xlabel('Month')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.0f}'))
        
        # 4. Category trends heatmap-style
        categories_subset = categories[:5]  # Top 5 categories for clarity
        category_monthly = {cat: [] for cat in categories_subset}
        
        for month_data in data:
            for cat in categories_subset:
                category_monthly[cat].append(month_data['expenses'].get(cat, 0))
        
        for i, cat in enumerate(categories_subset):
            ax4.plot(months, category_monthly[cat], label=cat, marker='o', linewidth=2)
        
        ax4.set_title('Category Trends Over Time', fontweight='bold')
        ax4.set_ylabel('Amount ($)')
        ax4.set_xlabel('Month')
        ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Export to PNG
        output_file = 'finance_dashboard_matplotlib.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Matplotlib visualization saved to: {output_file}")
        
        plt.close()
        
    except Exception as e:
        print(f"Error creating matplotlib visualizations: {e}")


def create_plotly_visualizations(data):
    """Create interactive visualizations using plotly."""
    if not PLOTLY_AVAILABLE:
        print("Plotly not available, skipping plotly visualizations.")
        return
    
    try:
        # Calculate totals for each category
        category_totals = {}
        monthly_totals = {}
        
        for month_data in data:
            month = month_data['date']
            month_total = 0
            
            for category, amount in month_data['expenses'].items():
                category_totals[category] = category_totals.get(category, 0) + amount
                month_total += amount
            
            monthly_totals[month] = month_total
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Category Spending', 'Expense Distribution', 
                          'Monthly Trends', 'Category Trends'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # 1. Category spending bar chart
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        
        fig.add_trace(
            go.Bar(x=categories, y=amounts, 
                  text=[f'${x:.0f}' for x in amounts],
                  textposition='outside',
                  name='Category Spending',
                  marker_color='lightblue'),
            row=1, col=1