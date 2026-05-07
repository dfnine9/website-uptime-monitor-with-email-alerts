```python
"""
Monthly Spending Report Generator

This module generates comprehensive monthly spending reports with interactive visualizations
including category breakdowns, spending trends over time, and summary statistics.
The reports are exported in both PDF and HTML formats.

Features:
- Category-wise spending breakdown with pie charts
- Monthly spending trends with line graphs
- Summary statistics and insights
- Interactive HTML reports with Plotly
- PDF export capability
- Sample data generation for demonstration

Dependencies: matplotlib, plotly, pandas (installable via pip)
Usage: python script.py
"""

import json
import random
import datetime
from pathlib import Path
import sys
from typing import Dict, List, Tuple, Any
import calendar

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_pdf import PdfPages
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please install required packages: pip install matplotlib plotly pandas")
    sys.exit(1)

class SpendingReportGenerator:
    """Generates monthly spending reports with visualizations and exports."""
    
    def __init__(self):
        self.categories = [
            'Food & Dining', 'Transportation', 'Entertainment', 'Utilities',
            'Healthcare', 'Shopping', 'Travel', 'Education', 'Insurance', 'Other'
        ]
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
        
    def generate_sample_data(self, months: int = 12) -> pd.DataFrame:
        """Generate sample spending data for demonstration."""
        try:
            data = []
            start_date = datetime.datetime.now() - datetime.timedelta(days=months*30)
            
            for i in range(months):
                current_date = start_date + datetime.timedelta(days=i*30)
                month_year = current_date.strftime('%Y-%m')
                
                for category in self.categories:
                    # Generate realistic spending amounts based on category
                    base_amounts = {
                        'Food & Dining': 800, 'Transportation': 400, 'Entertainment': 300,
                        'Utilities': 250, 'Healthcare': 200, 'Shopping': 500,
                        'Travel': 600, 'Education': 150, 'Insurance': 300, 'Other': 200
                    }
                    
                    base = base_amounts.get(category, 300)
                    amount = round(random.uniform(base * 0.5, base * 1.5), 2)
                    
                    data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'month_year': month_year,
                        'category': category,
                        'amount': amount,
                        'description': f'{category} expense for {calendar.month_name[current_date.month]}'
                    })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            print(f"Generated {len(df)} sample records across {months} months")
            return df
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def calculate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics from spending data."""
        try:
            stats = {
                'total_spending': df['amount'].sum(),
                'average_monthly': df.groupby('month_year')['amount'].sum().mean(),
                'highest_month': df.groupby('month_year')['amount'].sum().idxmax(),
                'highest_amount': df.groupby('month_year')['amount'].sum().max(),
                'top_category': df.groupby('category')['amount'].sum().idxmax(),
                'category_totals': df.groupby('category')['amount'].sum().to_dict(),
                'monthly_totals': df.groupby('month_year')['amount'].sum().to_dict()
            }
            
            print("Summary Statistics:")
            print(f"Total Spending: ${stats['total_spending']:,.2f}")
            print(f"Average Monthly: ${stats['average_monthly']:,.2f}")
            print(f"Highest Month: {stats['highest_month']} (${stats['highest_amount']:,.2f})")
            print(f"Top Category: {stats['top_category']}")
            
            return stats
            
        except Exception as e:
            print(f"Error calculating summary statistics: {e}")
            raise
    
    def create_matplotlib_charts(self, df: pd.DataFrame, stats: Dict[str, Any]) -> str:
        """Create matplotlib charts and save as PDF."""
        try:
            pdf_filename = f"spending_report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
            
            with PdfPages(pdf_filename) as pdf:
                # Page 1: Category Breakdown Pie Chart
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
                
                category_data = list(stats['category_totals'].values())
                category_labels = list(stats['category_totals'].keys())
                
                wedges, texts, autotexts = ax1.pie(
                    category_data, labels=category_labels, autopct='%1.1f%%',
                    colors=self.colors[:len(category_labels)], startangle=90
                )
                ax1.set_title('Spending by Category', fontsize=16, fontweight='bold')
                
                # Page 1: Monthly Trends
                monthly_data = sorted(stats['monthly_totals'].items())
                months = [item[0] for item in monthly_data]
                amounts = [item[1] for item in monthly_data]
                
                ax2.plot(months, amounts, marker='o', linewidth=2, markersize=6, color='#45B7D1')
                ax2.set_title('Monthly Spending Trends', fontsize=16, fontweight='bold')
                ax2.set_xlabel('Month')
                ax2.set_ylabel('Amount ($)')
                ax2.tick_params(axis='x', rotation=45)
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                
                # Page 2: Category Comparison Bar Chart
                fig, ax = plt.subplots(figsize=(12, 8))
                
                bars = ax.bar(category_labels, category_data, color=self.colors[:len(category_labels)])
                ax.set_title('Spending by Category (Bar Chart)', fontsize=16, fontweight='bold')
                ax.set_xlabel('Category')
                ax.set_ylabel('Total Amount ($)')
                ax.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for bar, value in zip(bars, category_data):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + value*0.01,
                           f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                
                # Page 3: Summary Statistics
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.axis('off')
                
                summary_text = f"""
MONTHLY SPENDING REPORT
Generated: {datetime.datetime.now().strftime('%B %d, %Y')}

SUMMARY STATISTICS
━━━━━━━━━━━━━━━