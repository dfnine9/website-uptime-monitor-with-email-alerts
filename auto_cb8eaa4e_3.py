```python
"""
Personal Finance Visualization Dashboard

A self-contained Python script that generates interactive charts and reports
for personal finance analysis. Creates visualizations for spending patterns,
category breakdowns, and trend analysis with exportable HTML output.

Features:
- Interactive spending pattern charts
- Category breakdown analysis
- Trend analysis over time
- Exportable HTML reports
- Sample data generation for demonstration

Dependencies: matplotlib, plotly (installable via pip)
Usage: python script.py
"""

import json
import datetime
import random
import os
from typing import Dict, List, Tuple, Any

def generate_sample_data() -> List[Dict[str, Any]]:
    """Generate sample financial transaction data for demonstration."""
    categories = [
        'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
        'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
        'Personal Care', 'Gifts & Donations'
    ]
    
    transactions = []
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    
    for i in range(500):  # Generate 500 sample transactions
        date = start_date + datetime.timedelta(days=random.randint(0, 365))
        category = random.choice(categories)
        
        # Different spending patterns for different categories
        if category == 'Bills & Utilities':
            amount = random.uniform(50, 300)
        elif category == 'Food & Dining':
            amount = random.uniform(10, 80)
        elif category == 'Shopping':
            amount = random.uniform(20, 200)
        elif category == 'Transportation':
            amount = random.uniform(5, 100)
        else:
            amount = random.uniform(15, 150)
        
        transactions.append({
            'date': date.strftime('%Y-%m-%d'),
            'category': category,
            'amount': round(amount, 2),
            'description': f'{category} expense #{i+1}'
        })
    
    return sorted(transactions, key=lambda x: x['date'])

def create_matplotlib_charts(transactions: List[Dict[str, Any]]) -> str:
    """Create matplotlib-based charts and return HTML representation."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime
        import base64
        from io import BytesIO
        
        # Set style
        plt.style.use('default')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Personal Finance Dashboard', fontsize=16, fontweight='bold')
        
        # Prepare data
        dates = [datetime.strptime(t['date'], '%Y-%m-%d') for t in transactions]
        amounts = [t['amount'] for t in transactions]
        categories = [t['category'] for t in transactions]
        
        # Chart 1: Spending over time
        ax1.scatter(dates, amounts, alpha=0.6, s=30)
        ax1.set_title('Spending Over Time')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Amount ($)')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax1.tick_params(axis='x', rotation=45)
        
        # Chart 2: Category breakdown (pie chart)
        category_totals = {}
        for transaction in transactions:
            cat = transaction['category']
            category_totals[cat] = category_totals.get(cat, 0) + transaction['amount']
        
        ax2.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%')
        ax2.set_title('Spending by Category')
        
        # Chart 3: Monthly spending trend
        monthly_spending = {}
        for transaction in transactions:
            month_key = transaction['date'][:7]  # YYYY-MM
            monthly_spending[month_key] = monthly_spending.get(month_key, 0) + transaction['amount']
        
        months = sorted(monthly_spending.keys())
        monthly_amounts = [monthly_spending[month] for month in months]
        
        ax3.plot(range(len(months)), monthly_amounts, marker='o')
        ax3.set_title('Monthly Spending Trend')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Total Amount ($)')
        ax3.set_xticks(range(0, len(months), max(1, len(months)//6)))
        ax3.set_xticklabels([months[i] for i in range(0, len(months), max(1, len(months)//6))], rotation=45)
        
        # Chart 4: Top spending categories (bar chart)
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:8]
        cat_names, cat_amounts = zip(*sorted_categories)
        
        ax4.bar(range(len(cat_names)), cat_amounts)
        ax4.set_title('Top Spending Categories')
        ax4.set_xlabel('Category')
        ax4.set_ylabel('Total Amount ($)')
        ax4.set_xticks(range(len(cat_names)))
        ax4.set_xticklabels(cat_names, rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Convert to base64 for HTML embedding
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f'<img src="data:image/png;base64,{image_base64}" style="max-width: 100%; height: auto;">'
        
    except ImportError:
        return '<p style="color: red;">Matplotlib not available. Install with: pip install matplotlib</p>'
    except Exception as e:
        return f'<p style="color: red;">Error creating matplotlib charts: {str(e)}</p>'

def create_plotly_charts(transactions: List[Dict[str, Any]]) -> str:
    """Create interactive Plotly charts and return HTML representation."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import plotly.offline as pyo
        from datetime import datetime
        
        # Prepare data
        dates = [datetime.strptime(t['date'], '%Y-%m-%d') for t in transactions]
        amounts = [t['amount'] for t in transactions]
        categories = [t['category'] for t in transactions]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Spending Pattern', 'Category Distribution', 
                          'Monthly Trends', 'Category Comparison'),
            specs=[[{"secondary_y": False}, {"type": "pie"}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Chart 1: Scatter plot of daily spending
        fig.add_trace(
            go.Scatter(
                x=dates, y=amounts, mode='markers',
                name='Daily Spending',
                marker=dict(size=8, opacity=0.6),
                hovertemplate='Date: %{x}<br>Amount: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Chart 2: Pie chart for categories
        category_totals = {}
        for transaction in transactions:
            cat = transaction['category']
            category_totals[cat] = category_totals.get(cat, 0) + transaction['amount']
        
        fig.add_trace(
            go.Pie(
                labels=list(category_totals.keys()),
                values=list(category_totals.values()),
                name="Categories",
                hovertemplate='Category: %{label}<br>Amount: $%{value:.