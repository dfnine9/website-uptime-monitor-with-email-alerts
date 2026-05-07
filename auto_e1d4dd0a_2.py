```python
#!/usr/bin/env python3
"""
Personal Finance Visualization Tool

This script generates interactive financial visualizations including:
- Monthly spending bar charts by category
- Pie charts showing spending distribution
- Line graphs tracking spending trends over time

The script creates sample financial data and generates interactive HTML visualizations
that can be opened in a web browser. All charts are self-contained and interactive.

Usage: python script.py

Dependencies: matplotlib, plotly (will attempt to install if missing)
"""

import sys
import subprocess
import json
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple

def install_package(package: str) -> bool:
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def ensure_dependencies():
    """Ensure required packages are installed."""
    required_packages = ["matplotlib", "plotly", "pandas"]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            if not install_package(package):
                print(f"Failed to install {package}. Please install manually.")
                sys.exit(1)

# Ensure dependencies are available
ensure_dependencies()

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

class FinanceVisualizer:
    """Generate interactive financial visualizations."""
    
    def __init__(self):
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Entertainment",
            "Bills & Utilities", "Healthcare", "Travel", "Education",
            "Personal Care", "Gifts & Donations"
        ]
        self.data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[Dict]:
        """Generate sample financial data for the last 12 months."""
        data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(365):
            current_date = start_date + timedelta(days=i)
            
            # Generate 1-3 transactions per day
            num_transactions = random.randint(1, 3)
            
            for _ in range(num_transactions):
                category = random.choice(self.categories)
                
                # Different spending patterns by category
                amount_ranges = {
                    "Food & Dining": (10, 80),
                    "Transportation": (5, 50),
                    "Shopping": (20, 200),
                    "Entertainment": (15, 100),
                    "Bills & Utilities": (50, 300),
                    "Healthcare": (20, 500),
                    "Travel": (100, 1000),
                    "Education": (50, 500),
                    "Personal Care": (10, 150),
                    "Gifts & Donations": (25, 200)
                }
                
                min_amount, max_amount = amount_ranges[category]
                amount = round(random.uniform(min_amount, max_amount), 2)
                
                data.append({
                    "date": current_date,
                    "category": category,
                    "amount": amount,
                    "month": current_date.strftime("%Y-%m"),
                    "month_name": current_date.strftime("%B %Y")
                })
        
        return data
    
    def create_monthly_bar_chart(self) -> str:
        """Create interactive monthly spending bar chart by category."""
        try:
            df = pd.DataFrame(self.data)
            monthly_data = df.groupby(['month_name', 'category'])['amount'].sum().unstack(fill_value=0)
            
            fig = go.Figure()
            
            colors = px.colors.qualitative.Set3
            for i, category in enumerate(self.categories):
                if category in monthly_data.columns:
                    fig.add_trace(go.Bar(
                        name=category,
                        x=monthly_data.index,
                        y=monthly_data[category],
                        marker_color=colors[i % len(colors)],
                        hovertemplate=f'<b>{category}</b><br>' +
                                    'Month: %{x}<br>' +
                                    'Amount: $%{y:,.2f}<extra></extra>'
                    ))
            
            fig.update_layout(
                title='Monthly Spending by Category',
                xaxis_title='Month',
                yaxis_title='Amount ($)',
                barmode='stack',
                height=600,
                hovermode='x unified'
            )
            
            html_file = "monthly_spending_bar.html"
            fig.write_html(html_file)
            print(f"✓ Monthly bar chart saved as {html_file}")
            return html_file
            
        except Exception as e:
            print(f"Error creating monthly bar chart: {e}")
            return ""
    
    def create_spending_pie_chart(self) -> str:
        """Create interactive pie chart showing spending distribution."""
        try:
            df = pd.DataFrame(self.data)
            category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
            
            fig = go.Figure(data=[go.Pie(
                labels=category_totals.index,
                values=category_totals.values,
                hovertemplate='<b>%{label}</b><br>' +
                            'Amount: $%{value:,.2f}<br>' +
                            'Percentage: %{percent}<extra></extra>',
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig.update_layout(
                title='Spending Distribution by Category',
                height=600,
                showlegend=True
            )
            
            html_file = "spending_pie_chart.html"
            fig.write_html(html_file)
            print(f"✓ Pie chart saved as {html_file}")
            return html_file
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return ""
    
    def create_trend_line_chart(self) -> str:
        """Create interactive line chart tracking spending trends."""
        try:
            df = pd.DataFrame(self.data)
            
            # Daily totals
            daily_totals = df.groupby('date')['amount'].sum().reset_index()
            
            # Monthly totals
            monthly_totals = df.groupby('month_name')['amount'].sum().reset_index()
            monthly_totals['date'] = pd.to_datetime(monthly_totals['month_name'], format='%B %Y')
            monthly_totals = monthly_totals.sort_values('date')
            
            # Weekly totals
            df['week'] = df['date'].dt.isocalendar().week
            df['year'] = df['date'].dt.year
            df['week_start'] = df['date'] - pd.to_timedelta(df['date'].dt.dayofweek, unit='d')
            weekly_totals = df.groupby('week_start')['amount'].sum().reset_index()
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=('Daily Spending Trend', 'Weekly Spending Trend', 'Monthly Spending Trend'),
                vertical_spacing=0.08
            )
            
            # Daily trend
            fig.add_trace(
                go.Scatter(
                    x=daily_totals['date'],
                    y=daily_totals['amount'],
                    mode='lines+markers',
                    name='Daily',
                    line=dict(color='blue', width=1),
                    marker=dict(size=3),
                    hovertemplate='Date: %{x}<br>Amount: $%{y:,.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Weekly