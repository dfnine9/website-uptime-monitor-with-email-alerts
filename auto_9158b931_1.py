```python
#!/usr/bin/env python3
"""
Data Visualization Module for Financial Analytics

This module generates interactive financial charts using Plotly to visualize:
1. Spending by category (pie chart)
2. Monthly spending trends (line chart) 
3. Top merchants by spending (bar chart)

Charts are exported as standalone HTML files that can be viewed in any web browser.
Includes sample financial data for demonstration purposes.

Dependencies: plotly (will attempt to install if missing)
Usage: python script.py
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

def install_plotly():
    """Install plotly if not available"""
    try:
        import plotly
    except ImportError:
        print("Installing plotly...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
        import plotly

def generate_sample_data() -> Dict[str, Any]:
    """Generate realistic sample financial data for visualization"""
    categories = ["Food & Dining", "Transportation", "Shopping", "Entertainment", 
                 "Bills & Utilities", "Healthcare", "Travel", "Gas & Fuel"]
    
    merchants = ["Amazon", "Walmart", "Starbucks", "Shell", "Target", "McDonald's",
                "Netflix", "Uber", "Costco", "Home Depot", "CVS", "Best Buy"]
    
    # Generate spending by category
    category_spending = {}
    total_budget = 3000
    remaining = total_budget
    
    for i, category in enumerate(categories[:-1]):
        if i == len(categories) - 2:
            category_spending[category] = remaining
        else:
            amount = random.randint(100, min(800, remaining - (len(categories) - i - 1) * 100))
            category_spending[category] = amount
            remaining -= amount
    
    # Generate monthly trends (last 12 months)
    monthly_data = {}
    base_date = datetime.now().replace(day=1)
    
    for i in range(12):
        month_date = base_date - timedelta(days=30 * i)
        month_key = month_date.strftime("%Y-%m")
        # Add some variance to monthly spending
        variance = random.uniform(0.8, 1.2)
        monthly_data[month_key] = int(total_budget * variance)
    
    # Generate top merchants data
    merchant_spending = {}
    for merchant in merchants[:8]:
        merchant_spending[merchant] = random.randint(150, 800)
    
    return {
        "categories": category_spending,
        "monthly": dict(sorted(monthly_data.items())),
        "merchants": dict(sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True))
    }

def create_spending_pie_chart(category_data: Dict[str, float]) -> str:
    """Create interactive pie chart for spending by category"""
    try:
        import plotly.graph_objects as go
        
        labels = list(category_data.keys())
        values = list(category_data.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Spending by Category',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            margin=dict(t=60, b=20, l=20, r=120),
            height=500
        )
        
        return fig.to_html(include_plotlyjs=True, div_id="spending-pie-chart")
        
    except Exception as e:
        print(f"Error creating pie chart: {e}")
        return f"<div>Error generating pie chart: {e}</div>"

def create_monthly_trends_chart(monthly_data: Dict[str, float]) -> str:
    """Create interactive line chart for monthly spending trends"""
    try:
        import plotly.graph_objects as go
        
        months = list(monthly_data.keys())
        amounts = list(monthly_data.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=months,
            y=amounts,
            mode='lines+markers',
            name='Monthly Spending',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8, color='#1f77b4'),
            hovertemplate='<b>%{x}</b><br>Spending: $%{y:,.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Monthly Spending Trends',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Month',
            yaxis_title='Amount ($)',
            xaxis=dict(tickangle=45),
            yaxis=dict(tickformat='$,.0f'),
            hovermode='x unified',
            margin=dict(t=60, b=80, l=80, r=20),
            height=500
        )
        
        return fig.to_html(include_plotlyjs=True, div_id="monthly-trends-chart")
        
    except Exception as e:
        print(f"Error creating line chart: {e}")
        return f"<div>Error generating line chart: {e}</div>"

def create_top_merchants_chart(merchant_data: Dict[str, float]) -> str:
    """Create interactive bar chart for top merchants by spending"""
    try:
        import plotly.graph_objects as go
        
        merchants = list(merchant_data.keys())
        amounts = list(merchant_data.values())
        
        # Create color gradient
        colors = ['#1f77b4' if i == 0 else f'rgba(31, 119, 180, {0.8 - i*0.1})' 
                 for i in range(len(merchants))]
        
        fig = go.Figure(data=[go.Bar(
            x=merchants,
            y=amounts,
            marker_color=colors,
            hovertemplate='<b>%{x}</b><br>Spending: $%{y:,.2f}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Top Merchants by Spending',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Merchant',
            yaxis_title='Amount ($)',
            xaxis=dict(tickangle=45),
            yaxis=dict(tickformat='$,.0f'),
            margin=dict(t=60, b=100, l=80, r=20),
            height=500
        )
        
        return fig.to_html(include_plotlyjs=True, div_id="top-merchants-chart")
        
    except Exception as e:
        print(f"Error creating bar chart: {e}")
        return f"<div>Error generating bar chart: {e}</div>"

def export_charts_to_html(charts: Dict[str, str], filename: str = "financial_dashboard.html") -> None:
    """Export all charts to a single HTML file"""
    try:
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Financial Analytics Dashboard</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20