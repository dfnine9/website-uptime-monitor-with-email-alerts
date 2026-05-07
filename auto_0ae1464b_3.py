```python
#!/usr/bin/env python3
"""
Financial Data Visualization and Reporting Tool

This module creates comprehensive financial visualizations including:
- Pie charts for expense category breakdown
- Line graphs for spending trends over time
- Bar charts for monthly spending comparisons
- PDF and HTML report generation

The script generates sample financial data and creates multiple chart types
to demonstrate spending patterns and trends. Reports are exported in both
PDF and HTML formats for easy sharing and analysis.

Dependencies: matplotlib, plotly, weasyprint (for PDF generation)
Usage: python script.py
"""

import json
import datetime
import random
import os
import sys
from typing import Dict, List, Tuple, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
except ImportError as e:
    print(f"Error: Required plotting libraries not installed. {e}")
    print("Install with: pip install matplotlib plotly")
    sys.exit(1)

class FinancialDataGenerator:
    """Generate sample financial data for demonstration purposes."""
    
    def __init__(self):
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Personal Care', 'Business Services'
        ]
        
    def generate_monthly_data(self, months: int = 12) -> List[Dict[str, Any]]:
        """Generate sample monthly financial data."""
        data = []
        base_date = datetime.datetime.now() - datetime.timedelta(days=months * 30)
        
        for i in range(months):
            month_date = base_date + datetime.timedelta(days=i * 30)
            month_data = {
                'month': month_date.strftime('%Y-%m'),
                'date': month_date,
                'total_spending': 0,
                'categories': {}
            }
            
            # Generate spending for each category
            for category in self.categories:
                # Add some randomness and seasonal variation
                base_amount = random.uniform(100, 800)
                seasonal_factor = 1 + 0.3 * random.sin(i * 0.5)  # Seasonal variation
                amount = round(base_amount * seasonal_factor, 2)
                month_data['categories'][category] = amount
                month_data['total_spending'] += amount
            
            month_data['total_spending'] = round(month_data['total_spending'], 2)
            data.append(month_data)
        
        return data

class FinancialVisualizer:
    """Create various financial visualizations using matplotlib and plotly."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.output_dir = "financial_reports"
        self._ensure_output_dir()
        
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except OSError as e:
            print(f"Warning: Could not create output directory: {e}")
            self.output_dir = "."
    
    def create_category_pie_chart_matplotlib(self) -> str:
        """Create pie chart showing expense category breakdown using matplotlib."""
        try:
            # Aggregate category totals
            category_totals = {}
            for month_data in self.data:
                for category, amount in month_data['categories'].items():
                    category_totals[category] = category_totals.get(category, 0) + amount
            
            # Create pie chart
            plt.figure(figsize=(12, 8))
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            colors = plt.cm.Set3(range(len(categories)))
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              colors=colors, startangle=90)
            
            plt.title('Expense Category Breakdown', fontsize=16, fontweight='bold', pad=20)
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.axis('equal')
            plt.tight_layout()
            
            filepath = os.path.join(self.output_dir, 'category_breakdown_matplotlib.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Category pie chart (matplotlib) saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error creating matplotlib pie chart: {e}")
            return ""
    
    def create_spending_trend_line_chart(self) -> str:
        """Create line chart showing spending trends over time using matplotlib."""
        try:
            # Extract dates and total spending
            dates = [month_data['date'] for month_data in self.data]
            totals = [month_data['total_spending'] for month_data in self.data]
            
            plt.figure(figsize=(14, 8))
            plt.plot(dates, totals, marker='o', linewidth=2.5, markersize=6, color='#2E86AB')
            
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Spending ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Add value labels on points
            for i, (date, total) in enumerate(zip(dates, totals)):
                plt.annotate(f'${total:,.0f}', (date, total), 
                           textcoords="offset points", xytext=(0,10), ha='center')
            
            plt.tight_layout()
            
            filepath = os.path.join(self.output_dir, 'spending_trends.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Spending trend line chart saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error creating spending trend chart: {e}")
            return ""
    
    def create_monthly_comparison_bar_chart(self) -> str:
        """Create bar chart for monthly spending comparisons using matplotlib."""
        try:
            months = [month_data['month'] for month_data in self.data]
            totals = [month_data['total_spending'] for month_data in self.data]
            
            plt.figure(figsize=(15, 8))
            bars = plt.bar(months, totals, color='#A23B72', alpha=0.8, edgecolor='black', linewidth=0.5)
            
            plt.title('Monthly Spending Comparison', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Spending ($)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar, total in zip(bars, totals):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + max(totals)*0.01,
                        f'${total:,.0f}', ha='center', va='bottom', fontsize=