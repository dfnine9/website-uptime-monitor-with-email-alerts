```python
#!/usr/bin/env python3
"""
Financial Visualization Module

A comprehensive financial data visualization tool that generates interactive charts
for spending analysis, trend tracking, and budget comparisons. Supports multiple
chart types with export functionality for financial reporting and analysis.

Features:
- Spending breakdown pie charts and bar charts
- Time-series trend analysis with moving averages
- Budget vs actual comparison visualizations
- Interactive charts with zoom, pan, and hover details
- Export functionality to HTML, PNG, and JSON formats
- Sample data generation for demonstration purposes

Dependencies: matplotlib, plotly (will attempt graceful degradation if unavailable)
"""

import sys
import json
import datetime
import random
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Core libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Wedge
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available, using text-based visualizations")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available, falling back to matplotlib only")


class FinancialVisualizer:
    """Main visualization class for financial data analysis and charting."""
    
    def __init__(self):
        self.data = {}
        self.charts = []
        
    def generate_sample_data(self):
        """Generate realistic sample financial data for demonstration."""
        try:
            # Monthly spending data for 12 months
            months = []
            spending_data = {}
            budget_data = {}
            
            categories = ['Housing', 'Food', 'Transportation', 'Utilities', 
                         'Entertainment', 'Healthcare', 'Shopping', 'Other']
            
            base_date = datetime.datetime.now() - datetime.timedelta(days=365)
            
            for i in range(12):
                month_date = base_date + datetime.timedelta(days=30*i)
                month_str = month_date.strftime('%Y-%m')
                months.append(month_str)
                
                # Generate spending data with some variance
                monthly_spending = {}
                monthly_budget = {}
                
                for category in categories:
                    base_amount = {
                        'Housing': 1200, 'Food': 400, 'Transportation': 300,
                        'Utilities': 200, 'Entertainment': 150, 'Healthcare': 100,
                        'Shopping': 200, 'Other': 150
                    }
                    
                    # Add random variance (-20% to +30%)
                    variance = random.uniform(-0.2, 0.3)
                    actual = base_amount[category] * (1 + variance)
                    budget = base_amount[category] * random.uniform(1.0, 1.1)
                    
                    monthly_spending[category] = round(actual, 2)
                    monthly_budget[category] = round(budget, 2)
                
                spending_data[month_str] = monthly_spending
                budget_data[month_str] = monthly_budget
            
            self.data = {
                'months': months,
                'spending': spending_data,
                'budget': budget_data,
                'categories': categories
            }
            
            print("✓ Sample financial data generated successfully")
            return True
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return False
    
    def create_spending_breakdown(self, month=None):
        """Create pie chart and bar chart for spending breakdown."""
        try:
            if not self.data:
                self.generate_sample_data()
            
            # Use latest month if none specified
            if month is None:
                month = self.data['months'][-1]
            
            spending = self.data['spending'][month]
            categories = list(spending.keys())
            amounts = list(spending.values())
            
            # Create matplotlib charts if available
            if MATPLOTLIB_AVAILABLE:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                
                # Pie chart
                colors = plt.cm.Set3(range(len(categories)))
                wedges, texts, autotexts = ax1.pie(amounts, labels=categories, autopct='%1.1f%%',
                                                  colors=colors, startangle=90)
                ax1.set_title(f'Spending Breakdown - {month}', fontsize=14, fontweight='bold')
                
                # Bar chart
                bars = ax2.bar(categories, amounts, color=colors)
                ax2.set_title(f'Spending by Category - {month}', fontsize=14, fontweight='bold')
                ax2.set_ylabel('Amount ($)')
                ax2.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar, amount in zip(bars, amounts):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 10,
                            f'${amount:.0f}', ha='center', va='bottom')
                
                plt.tight_layout()
                
                # Save matplotlib chart
                plt_filename = f'spending_breakdown_{month}.png'
                plt.savefig(plt_filename, dpi=300, bbox_inches='tight')
                print(f"✓ Matplotlib charts saved to {plt_filename}")
                
                plt.show()
            
            # Create plotly charts if available
            if PLOTLY_AVAILABLE:
                # Interactive pie chart
                fig_pie = go.Figure(data=[go.Pie(
                    labels=categories, 
                    values=amounts,
                    hole=0.3,
                    hovertemplate='<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>'
                )])
                
                fig_pie.update_layout(
                    title=f'Interactive Spending Breakdown - {month}',
                    font_size=12,
                    showlegend=True
                )
                
                # Interactive bar chart
                fig_bar = go.Figure(data=[go.Bar(
                    x=categories,
                    y=amounts,
                    text=[f'${x:.0f}' for x in amounts],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Amount: $%{y:.2f}<extra></extra>'
                )])
                
                fig_bar.update_layout(
                    title=f'Interactive Spending by Category - {month}',
                    xaxis_title='Category',
                    yaxis_title='Amount ($)',
                    font_size=12
                )
                
                # Save interactive charts
                pie_filename = f'interactive_pie_{month}.html'
                bar_filename = f'interactive_bar_{month}.html'
                
                pyo.plot(fig_pie, filename=pie_filename, auto_open=False)
                pyo.plot(fig_bar, filename=bar_filename, auto_open=False)
                
                print(f"✓ Interactive charts saved to {pie_filename} and {bar_filename}")
            
            # Text-based fallback
            print(f"\n📊 SPENDING BREAKDOWN - {month}")
            print("=" * 50)
            total = sum(amounts)
            for cat, amount in zip(categories, amounts):
                percentage = (amount / total) * 100
                bar = "█" * int(percentage / 2)
                print(f"{cat:15} ${amount:7.2f} ({percentage:5.1f}%) {bar}")
            print("=" * 50)
            print(f"{'TOTAL':15} ${total:7.2f}")
            
            return True
            
        except Exception as e:
            print(f"Error creating spending breakdown: {e}")
            return False