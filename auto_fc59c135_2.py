```python
"""
Personal Finance Visualization Tool

This module generates comprehensive spending visualizations including:
- Monthly spending breakdowns by category
- Trend analysis over time periods
- Spending pattern visualizations with insights

Uses matplotlib for chart generation and includes sample data for demonstration.
Designed to be self-contained with minimal dependencies.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from collections import defaultdict
    import numpy as np
except ImportError as e:
    print(f"Error: Required dependency missing - {e}")
    print("Please install matplotlib: pip install matplotlib")
    sys.exit(1)


class FinanceVisualizer:
    """Generates financial spending visualizations and analytics."""
    
    def __init__(self):
        self.spending_data = self._generate_sample_data()
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                          'Healthcare', 'Shopping', 'Housing', 'Education']
        
    def _generate_sample_data(self) -> List[Dict]:
        """Generate realistic sample spending data for the last 12 months."""
        data = []
        base_date = datetime.now() - timedelta(days=365)
        
        # Category spending ranges
        category_ranges = {
            'Food': (200, 600),
            'Transportation': (100, 300),
            'Entertainment': (50, 250),
            'Utilities': (150, 250),
            'Healthcare': (50, 400),
            'Shopping': (100, 500),
            'Housing': (800, 1200),
            'Education': (0, 300)
        }
        
        for i in range(365):
            current_date = base_date + timedelta(days=i)
            
            # Generate 1-5 transactions per day
            for _ in range(random.randint(1, 5)):
                category = random.choice(self.categories)
                min_amount, max_amount = category_ranges[category]
                amount = round(random.uniform(min_amount * 0.1, max_amount * 0.1), 2)
                
                data.append({
                    'date': current_date,
                    'category': category,
                    'amount': amount,
                    'description': f"{category} expense"
                })
        
        return data
    
    def generate_monthly_breakdown(self) -> None:
        """Create monthly spending breakdown by category chart."""
        try:
            # Group data by month and category
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.spending_data:
                month_key = transaction['date'].strftime('%Y-%m')
                monthly_data[month_key][transaction['category']] += transaction['amount']
            
            # Get last 6 months for readability
            sorted_months = sorted(monthly_data.keys())[-6:]
            
            # Prepare data for stacked bar chart
            categories = self.categories
            month_labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in sorted_months]
            
            # Create matrix of spending by category and month
            spending_matrix = []
            for category in categories:
                category_spending = [monthly_data[month].get(category, 0) for month in sorted_months]
                spending_matrix.append(category_spending)
            
            # Create stacked bar chart
            fig, ax = plt.subplots(figsize=(12, 8))
            
            bottom = [0] * len(month_labels)
            colors = plt.cm.Set3(range(len(categories)))
            
            for i, (category, amounts) in enumerate(zip(categories, spending_matrix)):
                ax.bar(month_labels, amounts, bottom=bottom, label=category, color=colors[i])
                bottom = [b + a for b, a in zip(bottom, amounts)]
            
            ax.set_title('Monthly Spending Breakdown by Category', fontsize=16, fontweight='bold')
            ax.set_xlabel('Month')
            ax.set_ylabel('Amount ($)')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('monthly_breakdown.png', dpi=150, bbox_inches='tight')
            plt.show()
            
            print("✓ Monthly breakdown chart generated")
            
        except Exception as e:
            print(f"Error generating monthly breakdown: {e}")
    
    def generate_trend_analysis(self) -> None:
        """Create trend analysis showing spending patterns over time."""
        try:
            # Group by month for trend analysis
            monthly_totals = defaultdict(float)
            category_trends = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.spending_data:
                month_key = transaction['date'].strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
                category_trends[transaction['category']][month_key] += transaction['amount']
            
            # Sort months and get dates
            sorted_months = sorted(monthly_totals.keys())
            dates = [datetime.strptime(m, '%Y-%m') for m in sorted_months]
            total_amounts = [monthly_totals[m] for m in sorted_months]
            
            # Create trend visualization
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # Overall spending trend
            ax1.plot(dates, total_amounts, marker='o', linewidth=2, markersize=6, color='#2E86C1')
            ax1.fill_between(dates, total_amounts, alpha=0.3, color='#2E86C1')
            ax1.set_title('Total Monthly Spending Trend', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Total Amount ($)')
            ax1.grid(True, alpha=0.3)
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
            # Top categories trend
            top_categories = sorted(self.categories[:4])  # Top 4 for readability
            colors = ['#E74C3C', '#F39C12', '#27AE60', '#8E44AD']
            
            for i, category in enumerate(top_categories):
                category_amounts = [category_trends[category].get(m, 0) for m in sorted_months]
                ax2.plot(dates, category_amounts, marker='o', label=category, 
                        linewidth=2, markersize=4, color=colors[i])
            
            ax2.set_title('Top Categories Spending Trends', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Amount ($)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('trend_analysis.png', dpi=150, bbox_inches='tight')
            plt.show()
            
            print("✓ Trend analysis chart generated")
            
        except Exception as e:
            print(f"Error generating trend analysis: {e}")
    
    def generate_pattern_visualization(self) -> None:
        """Create spending pattern visualizations with insights."""
        try:
            # Calculate category totals and percentages
            category_totals = defaultdict(float)
            total_spending = 0
            
            for transaction in self.spending_data:
                category_totals[transaction['category']] += transaction['amount']
                total_spending += transaction['amount']