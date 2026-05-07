```python
"""
Financial Reporting Engine

A self-contained reporting system that generates monthly spending summaries,
calculates category totals and percentages, and creates data visualizations.
Uses matplotlib for charts and includes comprehensive error handling.

Features:
- Monthly spending analysis
- Category-based expense tracking
- Percentage calculations
- Data visualizations (pie charts, bar graphs, trend lines)
- Sample data generation for demonstration
- Comprehensive error handling

Usage: python script.py
"""

import json
import random
import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List, Tuple, Any


class FinancialReportingEngine:
    """Main reporting engine for financial data analysis and visualization."""
    
    def __init__(self):
        self.expenses = []
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Health & Fitness', 'Travel', 'Education',
            'Personal Care', 'Gifts & Donations'
        ]
    
    def generate_sample_data(self, months: int = 6) -> None:
        """Generate sample expense data for demonstration purposes."""
        try:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=months * 30)
            
            current_date = start_date
            while current_date <= end_date:
                # Generate 3-8 expenses per day
                daily_expenses = random.randint(3, 8)
                for _ in range(daily_expenses):
                    expense = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'amount': round(random.uniform(5.0, 200.0), 2),
                        'category': random.choice(self.categories),
                        'description': f"Sample expense {random.randint(1000, 9999)}"
                    }
                    self.expenses.append(expense)
                current_date += datetime.timedelta(days=1)
            
            print(f"Generated {len(self.expenses)} sample expense records")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def calculate_monthly_summaries(self) -> Dict[str, Any]:
        """Calculate monthly spending summaries with category breakdowns."""
        try:
            monthly_data = defaultdict(lambda: {'total': 0, 'categories': defaultdict(float)})
            
            for expense in self.expenses:
                date_obj = datetime.datetime.strptime(expense['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                monthly_data[month_key]['total'] += expense['amount']
                monthly_data[month_key]['categories'][expense['category']] += expense['amount']
            
            # Calculate percentages
            for month in monthly_data:
                total = monthly_data[month]['total']
                monthly_data[month]['percentages'] = {
                    cat: round((amount / total) * 100, 2)
                    for cat, amount in monthly_data[month]['categories'].items()
                }
            
            return dict(monthly_data)
            
        except Exception as e:
            print(f"Error calculating monthly summaries: {e}")
            return {}
    
    def print_summary_report(self, monthly_data: Dict[str, Any]) -> None:
        """Print detailed text summary to stdout."""
        try:
            print("\n" + "="*60)
            print("MONTHLY SPENDING SUMMARY REPORT")
            print("="*60)
            
            total_spending = 0
            for month in sorted(monthly_data.keys()):
                data = monthly_data[month]
                total_spending += data['total']
                
                print(f"\n{month}:")
                print(f"  Total Spending: ${data['total']:,.2f}")
                print("  Category Breakdown:")
                
                # Sort categories by spending amount
                sorted_categories = sorted(
                    data['categories'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for category, amount in sorted_categories:
                    percentage = data['percentages'][category]
                    print(f"    {category:<20} ${amount:>8,.2f} ({percentage:>5.1f}%)")
            
            avg_monthly = total_spending / len(monthly_data) if monthly_data else 0
            print(f"\n{'='*60}")
            print(f"TOTAL SPENDING: ${total_spending:,.2f}")
            print(f"AVERAGE MONTHLY: ${avg_monthly:,.2f}")
            print(f"REPORTING PERIOD: {len(monthly_data)} months")
            
        except Exception as e:
            print(f"Error printing summary report: {e}")
    
    def create_pie_chart(self, monthly_data: Dict[str, Any]) -> None:
        """Create pie chart showing overall category distribution."""
        try:
            # Aggregate all categories across all months
            category_totals = defaultdict(float)
            for month_data in monthly_data.values():
                for category, amount in month_data['categories'].items():
                    category_totals[category] += amount
            
            if not category_totals:
                print("No data available for pie chart")
                return
            
            # Sort and prepare data
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            categories = [item[0] for item in sorted_categories]
            amounts = [item[1] for item in sorted_categories]
            
            # Create pie chart
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(categories)))
            wedges, texts, autotexts = plt.pie(
                amounts, 
                labels=categories,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title('Spending Distribution by Category', fontsize=16, fontweight='bold')
            plt.axis('equal')
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_bar_chart(self, monthly_data: Dict[str, Any]) -> None:
        """Create bar chart showing monthly spending totals."""
        try:
            if not monthly_data:
                print("No data available for bar chart")
                return
            
            months = sorted(monthly_data.keys())
            totals = [monthly_data[month]['total'] for month in months]
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(months, totals, color='steelblue', alpha=0.8)
            
            # Add value labels on bars
            for bar, total in zip(bars, totals):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + max(totals)*0.01,
                        f'${total:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            plt.title('Monthly Spending Totals', fontsize=16, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Total Spending ($)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error creating bar chart: {e}")
    
    def create_trend_line(self, monthly_data: Dict[str, Any]) -> None:
        """Create trend line showing spending patterns over time."""
        try:
            if not monthly_data:
                print("No data available for trend line")
                return
            
            months = sorted(monthly_data.keys