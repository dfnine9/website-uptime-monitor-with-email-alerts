```python
"""
Financial Spending Pattern Visualization Tool

This module generates interactive visualizations of spending patterns including:
- Pie charts for category breakdowns
- Bar graphs for comparative analysis
- Time series plots for trend analysis
- PDF export functionality for reports

Dependencies: matplotlib, plotly, pandas (standard data science stack)
Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
    print("✓ Matplotlib imported successfully")
except ImportError:
    print("✗ Error: matplotlib not found. Install with: pip install matplotlib")
    exit(1)

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    print("✓ Plotly imported successfully")
except ImportError:
    print("✗ Error: plotly not found. Install with: pip install plotly")
    exit(1)

try:
    import pandas as pd
    print("✓ Pandas imported successfully")
except ImportError:
    print("✗ Error: pandas not found. Install with: pip install pandas")
    exit(1)

class SpendingAnalyzer:
    """Main class for analyzing and visualizing spending patterns."""
    
    def __init__(self):
        """Initialize the spending analyzer with sample data."""
        self.data = self._generate_sample_data()
        self.df = pd.DataFrame(self.data)
        print(f"✓ Generated {len(self.data)} sample transactions")
    
    def _generate_sample_data(self) -> List[Dict]:
        """Generate realistic sample spending data."""
        categories = [
            'Groceries', 'Transportation', 'Entertainment', 'Utilities', 
            'Dining Out', 'Healthcare', 'Shopping', 'Education', 'Travel'
        ]
        
        data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(500):
            date = start_date + timedelta(days=random.randint(0, 365))
            category = random.choice(categories)
            
            # Generate realistic amounts based on category
            amount_ranges = {
                'Groceries': (20, 150),
                'Transportation': (10, 80),
                'Entertainment': (15, 120),
                'Utilities': (50, 300),
                'Dining Out': (25, 100),
                'Healthcare': (30, 500),
                'Shopping': (20, 300),
                'Education': (100, 1000),
                'Travel': (200, 2000)
            }
            
            min_amt, max_amt = amount_ranges[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            data.append({
                'date': date,
                'category': category,
                'amount': amount,
                'description': f"{category} purchase"
            })
        
        return sorted(data, key=lambda x: x['date'])
    
    def create_pie_chart(self) -> None:
        """Create pie chart showing spending by category."""
        try:
            # Matplotlib version
            category_totals = self.df.groupby('category')['amount'].sum()
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Matplotlib pie chart
            colors = plt.cm.Set3(range(len(category_totals)))
            wedges, texts, autotexts = ax1.pie(
                category_totals.values, 
                labels=category_totals.index,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            ax1.set_title('Spending by Category (Matplotlib)', fontsize=14, fontweight='bold')
            
            # Top 5 categories bar chart
            top_categories = category_totals.nlargest(5)
            bars = ax2.bar(top_categories.index, top_categories.values, color=colors[:5])
            ax2.set_title('Top 5 Spending Categories', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Amount ($)')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig('spending_categories_matplotlib.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            # Plotly version
            fig_plotly = go.Figure(data=[
                go.Pie(
                    labels=category_totals.index,
                    values=category_totals.values,
                    hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>',
                    textinfo='label+percent'
                )
            ])
            
            fig_plotly.update_layout(
                title='Spending by Category (Interactive)',
                title_font_size=16,
                showlegend=True,
                height=600
            )
            
            fig_plotly.write_html('spending_pie_chart.html')
            fig_plotly.show()
            
            print("✓ Pie charts created successfully")
            
        except Exception as e:
            print(f"✗ Error creating pie charts: {str(e)}")
    
    def create_time_series(self) -> None:
        """Create time series plot showing spending trends over time."""
        try:
            # Prepare data
            self.df['date'] = pd.to_datetime(self.df['date'])
            monthly_spending = self.df.groupby([
                self.df['date'].dt.to_period('M'),
                'category'
            ])['amount'].sum().reset_index()
            monthly_spending['date'] = monthly_spending['date'].dt.to_timestamp()
            
            # Matplotlib version
            fig, ax = plt.subplots(figsize=(14, 8))
            
            categories = self.df['category'].unique()
            colors = plt.cm.tab10(range(len(categories)))
            
            for i, category in enumerate(categories):
                cat_data = monthly_spending[monthly_spending['category'] == category]
                ax.plot(cat_data['date'], cat_data['amount'], 
                       marker='o', label=category, color=colors[i], linewidth=2)
            
            ax.set_title('Monthly Spending Trends by Category', fontsize=16, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Amount ($)')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig('spending_trends_matplotlib.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            # Plotly version
            fig_plotly = px.line(
                monthly_spending, 
                x='date', 
                y='amount', 
                color='category',
                title='Monthly Spending Trends (Interactive)',
                labels={'amount': 'Amount ($)', 'date': 'Date'}
            )
            
            fig_plotly.update_layout(
                title_font_size=16,
                hovermode='x unified',
                height