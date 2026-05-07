```python
#!/usr/bin/env python3
"""
Financial Visualization Module

A self-contained module for generating monthly spending reports with comprehensive
visualizations including bar charts, pie charts, and trend analysis using matplotlib.

Features:
- Monthly spending bar charts
- Category breakdown pie charts
- Spending trend analysis over time
- Statistical summaries and insights
- Error handling for data validation
- Sample data generation for demonstration

Dependencies: matplotlib (for visualization)
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
    from collections import defaultdict
    import numpy as np
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("Please install matplotlib: pip install matplotlib")
    sys.exit(1)


class SpendingReportGenerator:
    """Generate comprehensive monthly spending reports with visualizations."""
    
    def __init__(self):
        self.categories = [
            'Housing', 'Food', 'Transportation', 'Utilities', 
            'Entertainment', 'Healthcare', 'Shopping', 'Savings'
        ]
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
    
    def generate_sample_data(self, months: int = 12) -> List[Dict[str, Any]]:
        """Generate sample spending data for demonstration."""
        try:
            data = []
            base_date = datetime.now().replace(day=1) - timedelta(days=30 * months)
            
            for month in range(months):
                current_date = base_date + timedelta(days=30 * month)
                month_data = {
                    'month': current_date.strftime('%Y-%m'),
                    'date': current_date,
                    'categories': {}
                }
                
                # Generate realistic spending patterns
                base_amounts = {
                    'Housing': random.uniform(1200, 1800),
                    'Food': random.uniform(400, 800),
                    'Transportation': random.uniform(200, 500),
                    'Utilities': random.uniform(150, 300),
                    'Entertainment': random.uniform(100, 400),
                    'Healthcare': random.uniform(50, 200),
                    'Shopping': random.uniform(200, 600),
                    'Savings': random.uniform(300, 1000)
                }
                
                # Add seasonal variation
                seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * month / 12)
                
                for category, base_amount in base_amounts.items():
                    amount = base_amount * seasonal_factor * random.uniform(0.8, 1.2)
                    month_data['categories'][category] = round(amount, 2)
                
                month_data['total'] = sum(month_data['categories'].values())
                data.append(month_data)
            
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def create_monthly_bar_chart(self, data: List[Dict], save_path: str = None) -> bool:
        """Create monthly total spending bar chart."""
        try:
            months = [item['month'] for item in data]
            totals = [item['total'] for item in data]
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(months, totals, color='#4ECDC4', alpha=0.8, edgecolor='#2C3E50')
            
            # Add value labels on bars
            for bar, total in zip(bars, totals):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(totals) * 0.01,
                        f'${total:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Monthly Total Spending', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y', alpha=0.3)
            
            # Format y-axis as currency
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error creating monthly bar chart: {e}")
            return False
    
    def create_category_pie_chart(self, data: List[Dict], month_index: int = -1, save_path: str = None) -> bool:
        """Create pie chart for category breakdown of specified month."""
        try:
            if not data:
                raise ValueError("No data provided")
            
            month_data = data[month_index]
            categories = list(month_data['categories'].keys())
            amounts = list(month_data['categories'].values())
            
            plt.figure(figsize=(10, 8))
            
            # Create pie chart with custom styling
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, colors=self.colors[:len(categories)],
                                             autopct='%1.1f%%', startangle=90, explode=[0.05] * len(categories))
            
            # Enhance text styling
            for text in texts:
                text.set_fontsize(10)
                text.set_fontweight('bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            plt.title(f'Spending Breakdown - {month_data["month"]}', 
                     fontsize=16, fontweight='bold', pad=20)
            
            # Add total spending information
            total = sum(amounts)
            plt.figtext(0.5, 0.02, f'Total Spending: ${total:,.2f}', 
                       ha='center', fontsize=12, style='italic')
            
            plt.axis('equal')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:
                plt.show()
            
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error creating category pie chart: {e}")
            return False
    
    def create_trend_analysis(self, data: List[Dict], save_path: str = None) -> bool:
        """Create trend analysis chart showing spending patterns over time."""
        try:
            dates = [item['date'] for item in data]
            totals = [item['total'] for item in data]
            
            # Calculate moving average
            window_size = min(3, len(data))
            moving_avg = []
            for i in range(len(totals)):
                start = max(0, i - window_size + 1)
                avg = sum(totals[start:i+1]) / (i - start + 1)
                moving_avg.append(avg)
            
            plt.figure(figsize=(14, 8))
            
            # Plot actual spending
            plt.plot(dates, totals, marker='o', linewidth=2, markersize=6, 
                    color='#E74C3C', label='Monthly Spending', alpha=0.8)
            
            # Plot moving average
            plt.plot(dates, moving_avg, linewidth=3, color='#3498DB', 
                    label=f'{window_size}-Month Moving Average', alpha=0.9