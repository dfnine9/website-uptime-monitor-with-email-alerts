```python
"""
Personal Finance Visualization Module

This module generates comprehensive monthly spending reports with interactive charts
including category breakdowns, spending trends, and summary statistics.

Features:
- Category-wise spending breakdown (pie chart)
- Monthly spending trends (line chart)
- Top spending categories (bar chart)
- Summary statistics table
- Sample data generation for demonstration

Dependencies: matplotlib, pandas (uses sample data if external data unavailable)
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from collections import defaultdict
    import calendar
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install: pip install matplotlib")
    sys.exit(1)


class SpendingReportGenerator:
    """Generates monthly spending reports with visualizations."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Groceries', 'Gas & Fuel', 'Home & Garden', 'Personal Care'
        ]
    
    def generate_sample_data(self, months: int = 6) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        try:
            transactions = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Generate 200-500 sample transactions
            num_transactions = random.randint(200, 500)
            
            for _ in range(num_transactions):
                # Random date within the range
                days_back = random.randint(0, (end_date - start_date).days)
                transaction_date = end_date - timedelta(days=days_back)
                
                # Random category and amount
                category = random.choice(self.categories)
                
                # Different spending patterns per category
                if category in ['Food & Dining', 'Groceries']:
                    amount = round(random.uniform(10, 150), 2)
                elif category in ['Bills & Utilities', 'Healthcare']:
                    amount = round(random.uniform(50, 500), 2)
                elif category == 'Travel':
                    amount = round(random.uniform(100, 2000), 2)
                else:
                    amount = round(random.uniform(20, 300), 2)
                
                transactions.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': amount,
                    'description': f'{category} purchase'
                })
            
            return sorted(transactions, key=lambda x: x['date'])
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def load_transactions(self, data: List[Dict[str, Any]] = None) -> bool:
        """Load transaction data."""
        try:
            if data is None:
                print("No data provided, generating sample data...")
                self.transactions = self.generate_sample_data()
            else:
                self.transactions = data
            
            print(f"Loaded {len(self.transactions)} transactions")
            return True
            
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return False
    
    def calculate_monthly_totals(self) -> Dict[str, float]:
        """Calculate total spending by month."""
        try:
            monthly_totals = defaultdict(float)
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
            
            return dict(sorted(monthly_totals.items()))
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def calculate_category_totals(self, month: str = None) -> Dict[str, float]:
        """Calculate total spending by category for a specific month or all time."""
        try:
            category_totals = defaultdict(float)
            
            for transaction in self.transactions:
                if month:
                    date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                    if date_obj.strftime('%Y-%m') != month:
                        continue
                
                category_totals[transaction['category']] += transaction['amount']
            
            return dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        try:
            if not self.transactions:
                return {}
            
            amounts = [t['amount'] for t in self.transactions]
            monthly_totals = list(self.calculate_monthly_totals().values())
            
            stats = {
                'total_transactions': len(self.transactions),
                'total_amount': sum(amounts),
                'average_transaction': sum(amounts) / len(amounts),
                'max_transaction': max(amounts),
                'min_transaction': min(amounts),
                'avg_monthly_spending': sum(monthly_totals) / len(monthly_totals) if monthly_totals else 0,
                'date_range': {
                    'start': min(t['date'] for t in self.transactions),
                    'end': max(t['date'] for t in self.transactions)
                }
            }
            
            return stats
            
        except Exception as e:
            print(f"Error generating summary stats: {e}")
            return {}
    
    def create_category_pie_chart(self, month: str = None) -> None:
        """Create pie chart for category breakdown."""
        try:
            category_totals = self.calculate_category_totals(month)
            
            if not category_totals:
                print("No data available for pie chart")
                return
            
            # Take top 8 categories and group others
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            top_categories = sorted_categories[:8]
            other_total = sum(amount for _, amount in sorted_categories[8:])
            
            if other_total > 0:
                top_categories.append(('Others', other_total))
            
            labels, sizes = zip(*top_categories)
            
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(labels)))
            wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%',
                                             colors=colors, startangle=90)
            
            title = f"Spending by Category"
            if month:
                month_name = datetime.strptime(month + '-01', '%Y-%m-%d').strftime('%B %Y')
                title += f" - {month_name}"
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.axis('equal')
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_monthly_trend_chart(self) -> None:
        """Create line chart for monthly spending trends."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            
            if not monthly_totals:
                print("No data available for trend chart")
                return
            
            dates = [datetime.strptime(month + '-01', '%Y-%m-%d') for month in monthly_totals.keys()]
            amounts