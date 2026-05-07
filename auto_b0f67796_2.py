```python
#!/usr/bin/env python3
"""
Financial Data Visualization Generator

This module creates comprehensive financial visualizations including:
- Pie charts for expense category breakdowns
- Bar charts for monthly spending trends  
- Summary dashboards with key financial metrics

Uses matplotlib for visualization with sample financial data.
Designed to be self-contained with minimal dependencies.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random
import sys
from typing import Dict, List, Tuple, Any

def generate_sample_data() -> Tuple[Dict[str, float], Dict[str, List[float]], Dict[str, float]]:
    """Generate realistic sample financial data for visualization."""
    try:
        # Category breakdown data
        categories = {
            'Housing': 1200.00,
            'Food & Dining': 450.00,
            'Transportation': 320.00,
            'Utilities': 180.00,
            'Healthcare': 250.00,
            'Entertainment': 200.00,
            'Shopping': 300.00,
            'Savings': 500.00,
            'Other': 150.00
        }
        
        # Monthly spending trends (12 months)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_data = {}
        
        for category in categories:
            base_amount = categories[category]
            # Add some variation (+/- 20%)
            monthly_data[category] = [
                base_amount + random.uniform(-base_amount*0.2, base_amount*0.2) 
                for _ in range(12)
            ]
        
        # Key financial metrics
        total_monthly = sum(categories.values())
        metrics = {
            'Total Monthly Expenses': total_monthly,
            'Annual Expenses': total_monthly * 12,
            'Highest Category': max(categories.values()),
            'Average Monthly Spending': total_monthly,
            'Savings Rate': (categories['Savings'] / total_monthly) * 100
        }
        
        return categories, monthly_data, metrics
        
    except Exception as e:
        print(f"Error generating sample data: {e}", file=sys.stderr)
        return {}, {}, {}

def create_category_pie_chart(categories: Dict[str, float]) -> None:
    """Create and display pie chart for expense categories."""
    try:
        if not categories:
            raise ValueError("No category data available")
            
        plt.figure(figsize=(10, 8))
        
        # Prepare data
        labels = list(categories.keys())
        sizes = list(categories.values())
        colors = plt.cm.Set3(range(len(labels)))
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, 
                                          autopct='%1.1f%%', startangle=90,
                                          explode=[0.05 if label == 'Housing' else 0 for label in labels])
        
        # Enhance appearance
        plt.setp(autotexts, size=8, weight="bold")
        plt.title('Monthly Expense Breakdown by Category', fontsize=16, fontweight='bold', pad=20)
        
        # Add legend with dollar amounts
        legend_labels = [f'{label}: ${amount:.0f}' for label, amount in categories.items()]
        plt.legend(wedges, legend_labels, title="Categories", loc="center left", 
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
        print("✓ Category pie chart generated successfully")
        
    except Exception as e:
        print(f"Error creating pie chart: {e}", file=sys.stderr)

def create_monthly_trends_chart(monthly_data: Dict[str, List[float]]) -> None:
    """Create bar chart showing monthly spending trends."""
    try:
        if not monthly_data:
            raise ValueError("No monthly data available")
            
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        plt.figure(figsize=(14, 8))
        
        # Calculate monthly totals
        monthly_totals = []
        for i in range(12):
            total = sum(monthly_data[category][i] for category in monthly_data)
            monthly_totals.append(total)
        
        # Create bar chart
        bars = plt.bar(months, monthly_totals, color='steelblue', alpha=0.8, edgecolor='navy')
        
        # Enhance appearance
        plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12, fontweight='bold')
        plt.ylabel('Total Spending ($)', fontsize=12, fontweight='bold')
        
        # Add value labels on bars
        for bar, value in zip(bars, monthly_totals):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'${value:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Add trend line
        plt.plot(months, monthly_totals, color='red', marker='o', linewidth=2, 
                markersize=6, alpha=0.7, label='Trend')
        
        plt.grid(axis='y', alpha=0.3)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        print("✓ Monthly trends chart generated successfully")
        
    except Exception as e:
        print(f"Error creating monthly trends chart: {e}", file=sys.stderr)

def create_summary_dashboard(categories: Dict[str, float], metrics: Dict[str, float]) -> None:
    """Create comprehensive summary dashboard with key metrics."""
    try:
        if not categories or not metrics:
            raise ValueError("Insufficient data for dashboard")
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Financial Summary Dashboard', fontsize=20, fontweight='bold', y=0.98)
        
        # 1. Top 5 Categories (Horizontal Bar)
        top_categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
        ax1.barh(list(top_categories.keys()), list(top_categories.values()), 
                color='lightcoral', edgecolor='darkred')
        ax1.set_title('Top 5 Expense Categories', fontweight='bold', fontsize=14)
        ax1.set_xlabel('Amount ($)')
        
        # Add value labels
        for i, (category, value) in enumerate(top_categories.items()):
            ax1.text(value + 10, i, f'${value:.0f}', va='center', fontweight='bold')
        
        # 2. Savings vs Expenses Pie
        savings = categories.get('Savings', 0)
        expenses = sum(v for k, v in categories.items() if k != 'Savings')
        ax2.pie([expenses, savings], labels=['Expenses', 'Savings'], 
               colors=['lightblue', 'lightgreen'], autopct='%1.1f%%', startangle=90)
        ax2.set_title('Savings vs Expenses Ratio', fontweight='bold', fontsize=14)
        
        # 3. Key Metrics Table
        ax3.axis('tight')
        ax3.axis('off')
        metric_data = []
        for key, value in metrics.items():
            if 'Rate' in key:
                metric_data.append([key, f'{value:.1f}%'])
            else:
                metric