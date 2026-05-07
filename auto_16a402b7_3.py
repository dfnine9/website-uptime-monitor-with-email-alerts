```python
"""
Financial Visualization Module

This module creates comprehensive financial visualizations including:
- Monthly spending breakdowns by category
- Trend analysis graphs
- Budget vs actual spending comparisons
- PDF/HTML report exports

Dependencies: matplotlib, pandas (simulated with built-in data structures)
"""

import json
import datetime
import random
from typing import Dict, List, Tuple, Any
import os
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
    import numpy as np
except ImportError:
    print("Error: matplotlib and numpy are required for this script")
    print("Install with: pip install matplotlib numpy")
    sys.exit(1)

class FinancialVisualizer:
    """Main class for generating financial visualizations and reports."""
    
    def __init__(self):
        """Initialize the visualizer with sample data."""
        self.data = self._generate_sample_data()
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
        
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample financial data for demonstration."""
        try:
            months = []
            spending_data = {}
            budget_data = {}
            
            # Generate 12 months of data
            for i in range(12):
                month = datetime.date(2024, i + 1, 1)
                months.append(month)
                
                # Generate spending data by category
                spending_data[month] = {
                    'Food': random.randint(300, 600),
                    'Transportation': random.randint(200, 400),
                    'Entertainment': random.randint(100, 300),
                    'Utilities': random.randint(150, 250),
                    'Shopping': random.randint(200, 500),
                    'Healthcare': random.randint(50, 200)
                }
                
                # Generate budget data
                budget_data[month] = {
                    'Food': 500,
                    'Transportation': 300,
                    'Entertainment': 200,
                    'Utilities': 200,
                    'Shopping': 350,
                    'Healthcare': 150
                }
            
            return {
                'months': months,
                'spending': spending_data,
                'budget': budget_data
            }
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}
    
    def create_monthly_breakdown(self, month_index: int = -1) -> plt.Figure:
        """Create a pie chart showing spending breakdown by category for a specific month."""
        try:
            month = self.data['months'][month_index]
            spending = self.data['spending'][month]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            categories = list(spending.keys())
            amounts = list(spending.values())
            
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, colors=self.colors,
                                            autopct='%1.1f%%', startangle=90)
            
            ax.set_title(f'Spending Breakdown - {month.strftime("%B %Y")}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add legend with amounts
            legend_labels = [f'{cat}: ${amt}' for cat, amt in spending.items()]
            ax.legend(wedges, legend_labels, title="Categories", 
                     loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            return fig
        except Exception as e:
            print(f"Error creating monthly breakdown: {e}")
            return plt.figure()
    
    def create_trend_analysis(self) -> plt.Figure:
        """Create line charts showing spending trends over time."""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            months = self.data['months']
            
            # Plot 1: Total spending trend
            total_spending = []
            for month in months:
                total = sum(self.data['spending'][month].values())
                total_spending.append(total)
            
            ax1.plot(months, total_spending, marker='o', linewidth=2, 
                    color='#2E86AB', markersize=6)
            ax1.set_title('Total Monthly Spending Trend', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Amount ($)')
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
            # Plot 2: Category-wise trends
            for i, category in enumerate(self.categories):
                amounts = [self.data['spending'][month][category] for month in months]
                ax2.plot(months, amounts, marker='o', label=category, 
                        color=self.colors[i], linewidth=2, markersize=4)
            
            ax2.set_title('Category-wise Spending Trends', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Amount ($)')
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
            plt.tight_layout()
            return fig
        except Exception as e:
            print(f"Error creating trend analysis: {e}")
            return plt.figure()
    
    def create_budget_comparison(self) -> plt.Figure:
        """Create bar charts comparing budget vs actual spending."""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Calculate totals for latest month
            latest_month = self.data['months'][-1]
            actual = self.data['spending'][latest_month]
            budget = self.data['budget'][latest_month]
            
            categories = list(actual.keys())
            actual_amounts = list(actual.values())
            budget_amounts = list(budget.values())
            
            x = np.arange(len(categories))
            width = 0.35
            
            # Plot 1: Side-by-side comparison
            bars1 = ax1.bar(x - width/2, budget_amounts, width, label='Budget', 
                           color='#A8E6CF', alpha=0.8)
            bars2 = ax1.bar(x + width/2, actual_amounts, width, label='Actual', 
                           color='#FFB3BA', alpha=0.8)
            
            ax1.set_title(f'Budget vs Actual - {latest_month.strftime("%B %Y")}', 
                         fontsize=14, fontweight='bold')
            ax1.set_xlabel('Categories')
            ax1.set_ylabel('Amount ($)')
            ax1.set_xticks(x)
            ax1.set_xticklabels(categories, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                        f'${int(height)}', ha='center', va='bottom', fontsize=9)
            for bar in bars