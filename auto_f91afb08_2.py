```python
#!/usr/bin/env python3
"""
Financial Data Visualization Generator

This module creates interactive financial charts including:
- Spending breakdown pie charts
- Monthly trend lines
- Category comparison bar graphs

Uses matplotlib for static visualizations and plotly for interactive charts.
Includes sample financial data generation and comprehensive error handling.

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, skipping static charts")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available, skipping interactive charts")

class FinancialDataGenerator:
    """Generates sample financial data for visualization."""
    
    CATEGORIES = [
        "Housing", "Food", "Transportation", "Healthcare", 
        "Entertainment", "Shopping", "Utilities", "Insurance",
        "Savings", "Education", "Travel", "Miscellaneous"
    ]
    
    @staticmethod
    def generate_monthly_data(months: int = 12) -> List[Dict[str, Any]]:
        """Generate sample monthly financial data."""
        try:
            data = []
            base_date = datetime.now() - timedelta(days=30 * months)
            
            for i in range(months):
                month_date = base_date + timedelta(days=30 * i)
                month_data = {
                    "date": month_date.strftime("%Y-%m"),
                    "month_name": month_date.strftime("%B %Y"),
                    "categories": {}
                }
                
                total_spending = random.uniform(3000, 6000)
                remaining = total_spending
                
                for j, category in enumerate(FinancialDataGenerator.CATEGORIES):
                    if j == len(FinancialDataGenerator.CATEGORIES) - 1:
                        amount = remaining
                    else:
                        max_amount = remaining * 0.4 if remaining > 0 else 0
                        amount = random.uniform(50, max_amount) if max_amount > 50 else remaining
                        remaining -= amount
                    
                    month_data["categories"][category] = max(0, amount)
                
                data.append(month_data)
            
            return data
        except Exception as e:
            print(f"Error generating monthly data: {e}")
            return []

class MatplotlibVisualizer:
    """Creates static visualizations using matplotlib."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
    
    def create_spending_pie_chart(self, month_index: int = -1) -> bool:
        """Create a pie chart for spending breakdown."""
        try:
            if not self.data:
                raise ValueError("No data available")
            
            month_data = self.data[month_index]
            categories = month_data["categories"]
            
            # Filter out zero values
            filtered_categories = {k: v for k, v in categories.items() if v > 0}
            
            if not filtered_categories:
                raise ValueError("No spending data for selected month")
            
            plt.figure(figsize=(10, 8))
            
            labels = list(filtered_categories.keys())
            sizes = list(filtered_categories.values())
            colors = plt.cm.Set3(range(len(labels)))
            
            wedges, texts, autotexts = plt.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                explode=[0.05] * len(labels)
            )
            
            plt.title(f'Spending Breakdown - {month_data["month_name"]}', 
                     fontsize=16, fontweight='bold')
            
            # Enhance text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig('spending_pie_chart.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"✓ Pie chart created for {month_data['month_name']}")
            return True
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return False
    
    def create_monthly_trend_lines(self) -> bool:
        """Create line chart showing monthly trends."""
        try:
            if not self.data:
                raise ValueError("No data available")
            
            plt.figure(figsize=(14, 8))
            
            months = [item["month_name"] for item in self.data]
            
            # Calculate total spending per month
            total_spending = []
            for month_data in self.data:
                total = sum(month_data["categories"].values())
                total_spending.append(total)
            
            # Plot total spending trend
            plt.subplot(2, 1, 1)
            plt.plot(months, total_spending, marker='o', linewidth=2, 
                    markersize=6, color='#1f77b4')
            plt.title('Monthly Total Spending Trend', fontsize=14, fontweight='bold')
            plt.ylabel('Amount ($)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Plot top 3 categories
            plt.subplot(2, 1, 2)
            
            # Calculate average spending per category
            category_totals = {}
            for month_data in self.data:
                for category, amount in month_data["categories"].items():
                    category_totals[category] = category_totals.get(category, 0) + amount
            
            # Get top 3 categories
            top_categories = sorted(category_totals.items(), 
                                  key=lambda x: x[1], reverse=True)[:3]
            
            colors = ['#ff7f0e', '#2ca02c', '#d62728']
            
            for i, (category, _) in enumerate(top_categories):
                category_amounts = [month_data["categories"][category] 
                                 for month_data in self.data]
                plt.plot(months, category_amounts, marker='o', 
                        label=category, color=colors[i], linewidth=2)
            
            plt.title('Top 3 Categories - Monthly Trends', fontsize=14, fontweight='bold')
            plt.ylabel('Amount ($)')
            plt.xlabel('Month')
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Monthly trend lines created")
            return True
            
        except Exception as e:
            print(f"Error creating trend lines: {e}")
            return False
    
    def create_category_comparison_bar(self) -> bool:
        """Create bar chart comparing categories across months."""
        try:
            if not self.data:
                raise ValueError("No data available")
            
            # Calculate total spending per category
            category_totals = {}
            for month_data in self.data:
                for category, amount in month_data["categories"].items():
                    category_totals[category] = category_totals.get(category, 0) + amount
            
            # Sort categories by total spending
            sorted_categories = sorted(category_totals.items(), 
                                     key=lambda x: x[1], reverse=True)
            
            plt