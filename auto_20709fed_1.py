```python
"""
Personal Finance Transaction Aggregator Module

This module processes financial transaction data to provide monthly spending insights.
It aggregates transactions by month and category, calculates spending totals,
and identifies top expense categories to help users understand their spending patterns.

Features:
- Monthly transaction aggregation by category
- Total spending calculations
- Top expense category identification
- Comprehensive error handling
- Sample data generation for demonstration

Usage: python script.py
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import random


class TransactionProcessor:
    """Processes and aggregates financial transaction data."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
    
    def add_transaction(self, date: str, category: str, amount: float, description: str = ""):
        """Add a single transaction to the processor."""
        try:
            transaction = {
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'category': category,
                'amount': abs(float(amount)),  # Store as positive for expenses
                'description': description
            }
            self.transactions.append(transaction)
        except (ValueError, TypeError) as e:
            print(f"Error adding transaction: {e}")
    
    def load_sample_data(self):
        """Generate sample transaction data for demonstration."""
        categories = [
            'Groceries', 'Transportation', 'Utilities', 'Entertainment',
            'Dining Out', 'Healthcare', 'Shopping', 'Insurance',
            'Gas', 'Subscriptions', 'Education', 'Travel'
        ]
        
        descriptions = {
            'Groceries': ['Walmart', 'Target', 'Whole Foods', 'Local Market'],
            'Transportation': ['Uber', 'Metro Card', 'Parking', 'Bus Pass'],
            'Utilities': ['Electric Bill', 'Water Bill', 'Internet', 'Phone'],
            'Entertainment': ['Movie Theater', 'Concert', 'Streaming', 'Games'],
            'Dining Out': ['Restaurant', 'Fast Food', 'Coffee Shop', 'Delivery'],
            'Healthcare': ['Doctor Visit', 'Pharmacy', 'Dental', 'Lab Test'],
            'Shopping': ['Amazon', 'Clothing Store', 'Electronics', 'Home Goods'],
            'Insurance': ['Car Insurance', 'Health Insurance', 'Home Insurance'],
            'Gas': ['Shell', 'BP', 'Exxon', 'Chevron'],
            'Subscriptions': ['Netflix', 'Spotify', 'Gym', 'Software'],
            'Education': ['Books', 'Course Fee', 'Supplies', 'Tuition'],
            'Travel': ['Hotel', 'Airfare', 'Car Rental', 'Tourism']
        }
        
        # Generate transactions for the last 6 months
        start_date = datetime.now() - timedelta(days=180)
        
        for _ in range(150):  # 150 sample transactions
            random_days = random.randint(0, 180)
            transaction_date = start_date + timedelta(days=random_days)
            category = random.choice(categories)
            
            # Different spending ranges for different categories
            amount_ranges = {
                'Groceries': (20, 200),
                'Transportation': (5, 50),
                'Utilities': (50, 300),
                'Entertainment': (10, 100),
                'Dining Out': (15, 80),
                'Healthcare': (25, 500),
                'Shopping': (20, 300),
                'Insurance': (100, 400),
                'Gas': (30, 80),
                'Subscriptions': (5, 50),
                'Education': (50, 1000),
                'Travel': (100, 2000)
            }
            
            min_amount, max_amount = amount_ranges.get(category, (10, 100))
            amount = round(random.uniform(min_amount, max_amount), 2)
            description = random.choice(descriptions[category])
            
            self.add_transaction(
                transaction_date.strftime('%Y-%m-%d'),
                category,
                amount,
                description
            )
    
    def aggregate_by_month_and_category(self) -> Dict[str, Dict[str, float]]:
        """Aggregate transactions by month and category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
                self.category_totals[category] += amount
            
            # Convert to regular dict for JSON serialization
            return {month: dict(categories) for month, categories in monthly_data.items()}
        
        except Exception as e:
            print(f"Error aggregating transactions: {e}")
            return {}
    
    def calculate_monthly_totals(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate total spending for each month."""
        try:
            return {
                month: sum(categories.values())
                for month, categories in monthly_data.items()
            }
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def get_top_categories(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get top expense categories by total amount."""
        try:
            return sorted(
                self.category_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
        except Exception as e:
            print(f"Error getting top categories: {e}")
            return []
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive spending report."""
        try:
            monthly_data = self.aggregate_by_month_and_category()
            monthly_totals = self.calculate_monthly_totals(monthly_data)
            top_categories = self.get_top_categories()
            
            # Calculate additional statistics
            total_transactions = len(self.transactions)
            total_spending = sum(self.category_totals.values())
            average_transaction = total_spending / total_transactions if total_transactions > 0 else 0
            
            return {
                'summary': {
                    'total_transactions': total_transactions,
                    'total_spending': round(total_spending, 2),
                    'average_transaction': round(average_transaction, 2),
                    'months_analyzed': len(monthly_totals)
                },
                'monthly_breakdown': monthly_data,
                'monthly_totals': {k: round(v, 2) for k, v in monthly_totals.items()},
                'top_categories': [(cat, round(amount, 2)) for cat, amount in top_categories],
                'category_totals': {k: round(v, 2) for k, v in self.category_totals.items()}
            }
        
        except Exception as e:
            print(f"Error generating report: {e}")
            return {}


def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}"


def print_report(report: Dict[str, Any]):
    """Print formatted spending report to stdout."""
    try:
        print("=" * 60)
        print("           PERSONAL FINANCE SPENDING REPORT")
        print("=" * 60)
        
        # Summary section
        summary = report['summary']
        print(f"\nSUMMARY:")
        print(f"  Total Transactions: {summary['total_transactions']}")
        print(f"  Total Spending: {format_currency(summary['total_spending'])}")
        print(f"  Average Transaction: {format_currency(summary['average_transaction'])}")
        print(f"  Months Analyzed: {summary['months_analyzed']}")
        
        # Monthly totals
        print