```python
"""
Financial Data Visualization Module

This module generates comprehensive financial visualizations including:
- Pie charts for expense category breakdowns
- Line charts for spending trends over time
- Bar charts for monthly spending comparisons

Uses matplotlib for chart generation with sample financial data.
Designed to be self-contained with minimal dependencies.

Usage: python script.py
"""

import json
import random
import datetime
from typing import Dict, List, Tuple, Any

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    print("Error: matplotlib not available. Install with: pip install matplotlib")
    exit(1)

class FinancialVisualizer:
    """Generates various financial charts and visualizations."""
    
    def __init__(self):
        self.categories = ['Food', 'Transportation', 'Housing', 'Entertainment', 'Healthcare', 'Shopping', 'Utilities']
        self.sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate realistic sample financial data."""
        try:
            # Generate 12 months of data
            months = []
            monthly_totals = []
            category_data = {cat: [] for cat in self.categories}
            
            base_date = datetime.datetime.now() - datetime.timedelta(days=365)
            
            for i in range(12):
                month_date = base_date + datetime.timedelta(days=30*i)
                months.append(month_date)
                
                # Generate monthly spending by category
                month_total = 0
                for category in self.categories:
                    # Base amounts with some variation
                    base_amounts = {
                        'Food': 800, 'Transportation': 400, 'Housing': 1200,
                        'Entertainment': 300, 'Healthcare': 200, 'Shopping': 350, 'Utilities': 250
                    }
                    
                    amount = base_amounts[category] * random.uniform(0.7, 1.3)
                    category_data[category].append(amount)
                    month_total += amount
                
                monthly_totals.append(month_total)
            
            return {
                'months': months,
                'monthly_totals': monthly_totals,
                'category_data': category_data,
                'total_by_category': {cat: sum(amounts) for cat, amounts in category_data.items()}
            }
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}
    
    def create_pie_chart(self) -> None:
        """Generate pie chart for expense category breakdown."""
        try:
            plt.figure(figsize=(10, 8))
            
            categories = list(self.sample_data['total_by_category'].keys())
            amounts = list(self.sample_data['total_by_category'].values())
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
            
            wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              colors=colors, startangle=90, explode=[0.05]*len(categories))
            
            plt.title('Expense Breakdown by Category', fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')
            
            # Add total amount as subtitle
            total = sum(amounts)
            plt.figtext(0.5, 0.02, f'Total Annual Spending: ${total:,.2f}', 
                       ha='center', fontsize=12, style='italic')
            
            plt.tight_layout()
            plt.savefig('expense_pie_chart.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Pie chart generated successfully")
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_line_chart(self) -> None:
        """Generate line chart for spending trends over time."""
        try:
            plt.figure(figsize=(12, 6))
            
            months = self.sample_data['months']
            monthly_totals = self.sample_data['monthly_totals']
            
            plt.plot(months, monthly_totals, marker='o', linewidth=2.5, markersize=8, 
                    color='#3498db', markerfacecolor='#e74c3c')
            
            plt.title('Monthly Spending Trends', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            
            # Format x-axis to show month names
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            
            # Add grid for better readability
            plt.grid(True, alpha=0.3)
            
            # Format y-axis as currency
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add trend line
            z = range(len(monthly_totals))
            trend = [sum(monthly_totals)/len(monthly_totals)] * len(monthly_totals)
            plt.plot(months, trend, '--', alpha=0.7, color='red', label='Average')
            
            plt.legend()
            plt.tight_layout()
            plt.savefig('spending_trends.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Line chart generated successfully")
            
        except Exception as e:
            print(f"Error creating line chart: {e}")
    
    def create_bar_chart(self) -> None:
        """Generate bar chart for monthly spending comparisons."""
        try:
            plt.figure(figsize=(14, 8))
            
            months = [date.strftime('%b') for date in self.sample_data['months']]
            monthly_totals = self.sample_data['monthly_totals']
            
            # Create gradient colors
            colors = plt.cm.viridis([i/len(monthly_totals) for i in range(len(monthly_totals))])
            
            bars = plt.bar(months, monthly_totals, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            plt.title('Monthly Spending Comparison', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Spending ($)', fontsize=12)
            
            # Add value labels on bars
            for bar, value in zip(bars, monthly_totals):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(monthly_totals)*0.01,
                        f'${value:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
            
            # Format y-axis as currency
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Add average line
            avg_spending = sum(monthly_totals) / len(monthly_totals)
            plt.axhline(y=avg_spending, color='red', linestyle='--', alpha=0.7, 
                       label=f'Average: ${avg_spending:,.0f}')
            
            plt.legend()
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            plt.savefig('monthly_comparison.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✓ Bar chart generated successfully")
            
        except Exception as e: