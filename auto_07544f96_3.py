```python
"""
Financial Data Visualization Generator

This module creates comprehensive financial visualizations including:
- Monthly spending charts showing expenditure trends over time
- Category breakdown pie charts for spending analysis
- Trend analysis graphs with moving averages and projections
- Export functionality to PNG and HTML formats

The script generates sample financial data and creates multiple visualization types
using matplotlib and plotly, with robust error handling and export capabilities.

Usage: python script.py
"""

import json
import random
import datetime
from typing import Dict, List, Tuple, Any
import os
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import numpy as np
except ImportError:
    print("Error: matplotlib and numpy are required. Install with: pip install matplotlib numpy")
    sys.exit(1)

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except ImportError:
    print("Error: plotly is required. Install with: pip install plotly")
    sys.exit(1)


class FinancialDataGenerator:
    """Generates sample financial data for visualization testing."""
    
    def __init__(self):
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Health & Fitness', 'Travel', 'Education',
            'Personal Care', 'Miscellaneous'
        ]
        
    def generate_monthly_data(self, months: int = 12) -> List[Dict[str, Any]]:
        """Generate monthly spending data."""
        data = []
        base_date = datetime.date.today() - datetime.timedelta(days=30 * months)
        
        for i in range(months):
            month_date = base_date + datetime.timedelta(days=30 * i)
            monthly_total = random.uniform(2000, 5000)
            
            # Generate category breakdown
            category_data = {}
            remaining = monthly_total
            
            for j, category in enumerate(self.categories[:-1]):
                if j == len(self.categories) - 2:  # Second to last
                    amount = remaining * random.uniform(0.1, 0.8)
                else:
                    amount = remaining * random.uniform(0.05, 0.25)
                category_data[category] = round(amount, 2)
                remaining -= amount
            
            # Last category gets remaining amount
            category_data[self.categories[-1]] = round(remaining, 2)
            
            data.append({
                'date': month_date,
                'total': round(monthly_total, 2),
                'categories': category_data
            })
        
        return data


class VisualizationGenerator:
    """Creates various financial visualizations with export capabilities."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.output_dir = 'financial_charts'
        self._ensure_output_directory()
        
    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except OSError as e:
            print(f"Warning: Could not create output directory: {e}")
            self.output_dir = '.'
    
    def create_monthly_spending_chart(self) -> Tuple[str, str]:
        """Create monthly spending trend chart using matplotlib."""
        try:
            dates = [item['date'] for item in self.data]
            totals = [item['total'] for item in self.data]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(dates, totals, marker='o', linewidth=2, markersize=6, color='#2E86C1')
            ax.fill_between(dates, totals, alpha=0.3, color='#85C1E9')
            
            # Calculate and plot trend line
            x_numeric = [i for i in range(len(dates))]
            z = np.polyfit(x_numeric, totals, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(x_numeric), "--", alpha=0.8, color='#E74C3C', 
                   label=f'Trend: ${z[0]:.0f}/month')
            
            ax.set_title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount ($)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Export to PNG
            png_path = os.path.join(self.output_dir, 'monthly_spending.png')
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return png_path, "Monthly spending chart created successfully"
            
        except Exception as e:
            return "", f"Error creating monthly spending chart: {str(e)}"
    
    def create_category_pie_chart(self, month_index: int = -1) -> Tuple[str, str]:
        """Create category breakdown pie chart for specified month."""
        try:
            if month_index < 0:
                month_index = len(self.data) + month_index
                
            month_data = self.data[month_index]
            categories = list(month_data['categories'].keys())
            values = list(month_data['categories'].values())
            
            # Create color palette
            colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.1f%%',
                                            colors=colors, startangle=90,
                                            textprops={'fontsize': 10})
            
            # Enhance text visibility
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title(f'Spending Breakdown - {month_data["date"].strftime("%B %Y")}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Export to PNG
            png_path = os.path.join(self.output_dir, 'category_breakdown.png')
            plt.savefig(png_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return png_path, "Category pie chart created successfully"
            
        except Exception as e:
            return "", f"Error creating category pie chart: {str(e)}"
    
    def create_trend_analysis_plotly(self) -> Tuple[str, str]:
        """Create comprehensive trend analysis using Plotly."""
        try:
            dates = [item['date'] for item in self.data]
            totals = [item['total'] for item in self.data]
            
            # Calculate moving averages
            window_3 = 3
            window_6 = min(6, len(totals))
            
            moving_avg_3 = []
            moving_avg_6 = []
            
            for i in range(len(totals)):
                if i >= window_3 - 1:
                    moving_avg_3.append(sum(totals[i-window_3+1:i+1]) / window_3)
                else:
                    moving_avg_3.append(None)
                    
                if i >= window_6 - 1:
                    moving_avg_6.append(sum