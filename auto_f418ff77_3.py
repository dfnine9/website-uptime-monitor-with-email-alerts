```python
#!/usr/bin/env python3
"""
Personal Finance Visualization Tool

This module generates interactive spending visualizations including:
- Category breakdown pie charts
- Monthly spending trends
- Budget vs actual comparisons
- Exportable chart functionality

Uses matplotlib for static charts and plotly for interactive visualizations.
Generates sample financial data for demonstration purposes.

Usage: python script.py
"""

import json
import random
import datetime
from pathlib import Path
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available. Install with: pip install plotly")


class FinanceVisualizer:
    """Generates and exports financial visualizations"""
    
    def __init__(self):
        self.data = self._generate_sample_data()
        self.categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 
                          'Healthcare', 'Shopping', 'Utilities', 'Education']
        
    def _generate_sample_data(self):
        """Generate realistic sample financial data"""
        try:
            # Generate 12 months of data
            months = []
            current_date = datetime.date.today().replace(day=1)
            
            for i in range(12):
                month_date = current_date - datetime.timedelta(days=30 * i)
                months.append(month_date.strftime('%Y-%m'))
            
            months.reverse()
            
            # Sample spending data
            data = {
                'monthly_spending': {},
                'category_totals': {},
                'budget_vs_actual': {}
            }
            
            # Generate monthly data
            for month in months:
                spending = {
                    'Housing': random.randint(1200, 1500),
                    'Food': random.randint(300, 600),
                    'Transportation': random.randint(200, 400),
                    'Entertainment': random.randint(100, 300),
                    'Healthcare': random.randint(50, 200),
                    'Shopping': random.randint(100, 400),
                    'Utilities': random.randint(150, 250),
                    'Education': random.randint(0, 300)
                }
                data['monthly_spending'][month] = spending
            
            # Calculate category totals
            for category in self.categories:
                total = sum(data['monthly_spending'][month].get(category, 0) 
                           for month in months)
                data['category_totals'][category] = total
            
            # Generate budget data
            for category in self.categories:
                actual = data['category_totals'][category]
                budget = actual + random.randint(-200, 300)
                data['budget_vs_actual'][category] = {
                    'budget': budget,
                    'actual': actual
                }
            
            return data
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {}
    
    def create_matplotlib_charts(self):
        """Create static charts using matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available - skipping static charts")
            return False
            
        try:
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Personal Finance Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Category breakdown pie chart
            categories = list(self.data['category_totals'].keys())
            amounts = list(self.data['category_totals'].values())
            
            ax1.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Spending by Category')
            
            # 2. Monthly trends line chart
            months = sorted(self.data['monthly_spending'].keys())
            monthly_totals = []
            
            for month in months:
                total = sum(self.data['monthly_spending'][month].values())
                monthly_totals.append(total)
            
            ax2.plot(months, monthly_totals, marker='o', linewidth=2, markersize=6)
            ax2.set_title('Monthly Spending Trends')
            ax2.set_xlabel('Month')
            ax2.set_ylabel('Amount ($)')
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. Budget vs Actual comparison
            categories = list(self.data['budget_vs_actual'].keys())
            budget_amounts = [self.data['budget_vs_actual'][cat]['budget'] for cat in categories]
            actual_amounts = [self.data['budget_vs_actual'][cat]['actual'] for cat in categories]
            
            x_pos = range(len(categories))
            width = 0.35
            
            ax3.bar([x - width/2 for x in x_pos], budget_amounts, width, label='Budget', alpha=0.7)
            ax3.bar([x + width/2 for x in x_pos], actual_amounts, width, label='Actual', alpha=0.7)
            ax3.set_title('Budget vs Actual Spending')
            ax3.set_xlabel('Category')
            ax3.set_ylabel('Amount ($)')
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels(categories, rotation=45)
            ax3.legend()
            
            # 4. Top spending categories
            sorted_categories = sorted(self.data['category_totals'].items(), 
                                     key=lambda x: x[1], reverse=True)
            top_categories = sorted_categories[:5]
            
            cats, amounts = zip(*top_categories)
            ax4.barh(cats, amounts, color='lightcoral')
            ax4.set_title('Top 5 Spending Categories')
            ax4.set_xlabel('Amount ($)')
            
            plt.tight_layout()
            
            # Save as PNG
            plt.savefig('finance_dashboard.png', dpi=300, bbox_inches='tight')
            print("✓ Static charts saved as 'finance_dashboard.png'")
            
            # Save as PDF
            with PdfPages('finance_dashboard.pdf') as pdf:
                pdf.savefig(fig, bbox_inches='tight')
            print("✓ Static charts saved as 'finance_dashboard.pdf'")
            
            plt.close()
            return True
            
        except Exception as e:
            print(f"Error creating matplotlib charts: {e}")
            return False
    
    def create_plotly_charts(self):
        """Create interactive charts using plotly"""
        if not PLOTLY_AVAILABLE:
            print("Plotly not available - skipping interactive charts")
            return False
            
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Spending by Category', 'Monthly Trends', 
                               'Budget vs Actual', 'Category Comparison'),
                specs=[[{"type": "pie"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            # 1. Category pie chart
            categories = list(self.data['category_totals'].keys())
            amounts = list(self.data['category_totals'].values())
            
            fig.add_trace(
                go.Pie(labels=categories, values=amounts, name="Categories"),
                row=1, col=1
            )
            
            # 2. Monthly trends
            months = sorted(self.data['monthly_spending'].keys())