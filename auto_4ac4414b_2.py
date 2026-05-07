```python
#!/usr/bin/env python3
"""
Monthly Spending Report Visualization Generator

This module generates comprehensive monthly spending reports with interactive visualizations
including category breakdowns, trend analysis, and comparative analysis between time periods.
Uses matplotlib for static charts and includes sample data generation for demonstration.

Features:
- Category breakdown pie charts and bar charts
- Monthly spending trend lines
- Year-over-year comparative analysis
- Statistical summaries and insights
- Export capabilities for reports

Dependencies: matplotlib, pandas (will attempt graceful fallback if not available)
"""

import json
import random
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")

def generate_sample_spending_data():
    """Generate realistic sample spending data for demonstration."""
    categories = [
        'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
        'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
        'Home & Garden', 'Personal Care', 'Gifts & Donations'
    ]
    
    # Base spending amounts per category (monthly averages)
    base_amounts = {
        'Food & Dining': 800,
        'Transportation': 400,
        'Shopping': 600,
        'Bills & Utilities': 300,
        'Entertainment': 250,
        'Healthcare': 150,
        'Travel': 200,
        'Education': 100,
        'Home & Garden': 180,
        'Personal Care': 120,
        'Gifts & Donations': 80
    }
    
    data = []
    start_date = datetime(2022, 1, 1)
    
    # Generate 24 months of data
    for month_offset in range(24):
        current_date = start_date + timedelta(days=30 * month_offset)
        month_str = current_date.strftime('%Y-%m')
        
        for category in categories:
            # Add seasonal variation and randomness
            base = base_amounts[category]
            seasonal_factor = 1 + 0.3 * random.sin(month_offset * 0.5)
            random_factor = 1 + random.uniform(-0.4, 0.4)
            amount = base * seasonal_factor * random_factor
            
            # Generate multiple transactions per category per month
            num_transactions = random.randint(3, 15)
            for _ in range(num_transactions):
                transaction_amount = amount / num_transactions * random.uniform(0.1, 2.0)
                day = random.randint(1, 28)
                transaction_date = current_date.replace(day=day)
                
                data.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': round(transaction_amount, 2),
                    'description': f'{category} expense'
                })
    
    return data

class SpendingAnalyzer:
    """Analyzes spending data and generates insights."""
    
    def __init__(self, data):
        self.data = data
        self.monthly_totals = self._calculate_monthly_totals()
        self.category_totals = self._calculate_category_totals()
    
    def _calculate_monthly_totals(self):
        """Calculate total spending by month."""
        monthly = defaultdict(float)
        for transaction in self.data:
            date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
            month_key = date_obj.strftime('%Y-%m')
            monthly[month_key] += transaction['amount']
        return dict(monthly)
    
    def _calculate_category_totals(self):
        """Calculate total spending by category."""
        category = defaultdict(float)
        for transaction in self.data:
            category[transaction['category']] += transaction['amount']
        return dict(category)
    
    def get_monthly_category_breakdown(self, year_month):
        """Get category breakdown for specific month."""
        category_monthly = defaultdict(float)
        for transaction in self.data:
            date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
            if date_obj.strftime('%Y-%m') == year_month:
                category_monthly[transaction['category']] += transaction['amount']
        return dict(category_monthly)
    
    def calculate_trends(self):
        """Calculate spending trends and statistics."""
        amounts = list(self.monthly_totals.values())
        if len(amounts) < 2:
            return {}
        
        avg_spending = sum(amounts) / len(amounts)
        max_spending = max(amounts)
        min_spending = min(amounts)
        
        # Calculate trend (simple linear regression slope)
        months = list(range(len(amounts)))
        n = len(months)
        sum_x = sum(months)
        sum_y = sum(amounts)
        sum_xy = sum(x * y for x, y in zip(months, amounts))
        sum_x2 = sum(x * x for x in months)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            slope = 0
        
        return {
            'average_monthly': avg_spending,
            'max_monthly': max_spending,
            'min_monthly': min_spending,
            'trend_slope': slope,
            'total_months': len(amounts),
            'total_spent': sum(amounts)
        }

class SpendingVisualizer:
    """Creates visualizations for spending data."""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        
        if MATPLOTLIB_AVAILABLE:
            plt.style.use('default')
            self.colors = plt.cm.Set3(range(12))
    
    def create_monthly_trend_chart(self):
        """Create monthly spending trend line chart."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for trend chart")
            return
        
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            months = sorted(self.analyzer.monthly_totals.keys())
            amounts = [self.analyzer.monthly_totals[month] for month in months]
            
            # Convert month strings to datetime for better plotting
            dates = [datetime.strptime(month, '%Y-%m') for month in months]
            
            ax.plot(dates, amounts, marker='o', linewidth=2, markersize=6, color='#2E8B57')
            ax.fill_between(dates, amounts, alpha=0.3, color='#2E8B57')
            
            ax.set_title('Monthly Spending Trends', fontsize=16, fontweight='bold')
            ax.set_xlabel('Month', fontsize=12)
            ax.set_ylabel('Amount Spent ($)', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.xticks(rotation=45)
            
            # Add trend line
            if len(amounts) > 1:
                z = range(len(amounts))
                coeffs = [self.analyzer.calculate_trends()['trend_slope'], amounts[0]]
                trend_line = [coeffs[0] * x + coeffs[1] for x in z]
                ax.plot(dates, trend_line, '--', color='red', alpha=0.7, label='Trend')
                ax.legend()
            
            plt.tight_layout()
            plt.savefig('monthly_trends.png', dpi=300, bbox_inches='tight')
            print("Monthly trend chart saved as 'monthly