```python
"""
Personal Budget Recommendation Engine

This module analyzes historical spending patterns from transaction data and generates
personalized budget recommendations including category limits and savings opportunities.

Features:
- Parses transaction data from CSV or manual input
- Categorizes expenses automatically
- Calculates spending patterns and trends
- Generates category-based budget limits
- Identifies potential savings opportunities
- Provides actionable budget recommendations

Usage:
    python script.py

The script will either read from 'transactions.csv' if available, or use sample data
to demonstrate the budget recommendation engine capabilities.
"""

import json
import csv
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import re
import os

class BudgetRecommendationEngine:
    """
    A comprehensive budget recommendation engine that analyzes spending patterns
    and generates personalized financial advice.
    """
    
    def __init__(self):
        self.transactions = []
        self.categories = {
            'groceries': ['grocery', 'food', 'supermarket', 'walmart', 'target', 'kroger'],
            'dining': ['restaurant', 'cafe', 'pizza', 'starbucks', 'mcdonald', 'subway'],
            'transportation': ['gas', 'uber', 'lyft', 'taxi', 'bus', 'train', 'parking'],
            'utilities': ['electric', 'water', 'internet', 'phone', 'cable', 'netflix'],
            'entertainment': ['movie', 'theater', 'spotify', 'game', 'concert', 'bar'],
            'shopping': ['amazon', 'mall', 'clothing', 'shoes', 'electronics', 'books'],
            'healthcare': ['doctor', 'pharmacy', 'hospital', 'dental', 'medical'],
            'education': ['school', 'university', 'course', 'training', 'books'],
            'miscellaneous': []
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Automatically categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if category == 'miscellaneous':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'miscellaneous'
    
    def load_transactions_from_csv(self, filename: str) -> bool:
        """Load transactions from a CSV file."""
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    transaction = {
                        'date': datetime.strptime(row['date'], '%Y-%m-%d'),
                        'amount': float(row['amount']),
                        'description': row['description'],
                        'category': row.get('category', '')
                    }
                    if not transaction['category']:
                        transaction['category'] = self.categorize_transaction(transaction['description'])
                    self.transactions.append(transaction)
            return True
        except (FileNotFoundError, KeyError, ValueError) as e:
            print(f"Error loading CSV file: {e}")
            return False
    
    def generate_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        sample_transactions = [
            {'date': '2024-01-15', 'amount': 85.50, 'description': 'Walmart Supercenter'},
            {'date': '2024-01-16', 'amount': 45.00, 'description': 'Shell Gas Station'},
            {'date': '2024-01-17', 'amount': 25.99, 'description': 'Netflix Subscription'},
            {'date': '2024-01-18', 'amount': 120.75, 'description': 'Amazon Purchase'},
            {'date': '2024-01-19', 'amount': 35.00, 'description': 'Olive Garden Restaurant'},
            {'date': '2024-01-20', 'amount': 150.00, 'description': 'Electric Company'},
            {'date': '2024-01-22', 'amount': 95.25, 'description': 'Kroger Grocery'},
            {'date': '2024-01-23', 'amount': 15.00, 'description': 'Starbucks Coffee'},
            {'date': '2024-01-24', 'amount': 200.00, 'description': 'Target Shopping'},
            {'date': '2024-01-25', 'amount': 75.00, 'description': 'Doctor Visit'},
            {'date': '2024-02-01', 'amount': 90.00, 'description': 'Grocery Store'},
            {'date': '2024-02-03', 'amount': 50.00, 'description': 'Gas Station'},
            {'date': '2024-02-05', 'amount': 180.00, 'description': 'Amazon Electronics'},
            {'date': '2024-02-08', 'amount': 65.00, 'description': 'Restaurant Dinner'},
            {'date': '2024-02-10', 'amount': 40.00, 'description': 'Movie Theater'},
            {'date': '2024-02-12', 'amount': 110.00, 'description': 'Walmart Groceries'},
            {'date': '2024-02-15', 'amount': 25.00, 'description': 'Uber Ride'},
            {'date': '2024-02-18', 'amount': 300.00, 'description': 'Clothing Store'},
            {'date': '2024-02-20', 'amount': 80.00, 'description': 'Pharmacy'},
            {'date': '2024-02-22', 'amount': 55.00, 'description': 'Internet Bill'},
        ]
        
        for transaction_data in sample_transactions:
            transaction = {
                'date': datetime.strptime(transaction_data['date'], '%Y-%m-%d'),
                'amount': transaction_data['amount'],
                'description': transaction_data['description'],
                'category': self.categorize_transaction(transaction_data['description'])
            }
            self.transactions.append(transaction)
    
    def analyze_spending_patterns(self) -> Dict:
        """Analyze historical spending patterns and calculate statistics."""
        if not self.transactions:
            return {}
        
        # Group transactions by category
        category_spending = defaultdict(list)
        monthly_spending = defaultdict(float)
        
        for transaction in self.transactions:
            category_spending[transaction['category']].append(transaction['amount'])
            month_key = transaction['date'].strftime('%Y-%m')
            monthly_spending[month_key] += transaction['amount']
        
        # Calculate statistics for each category
        analysis = {}
        total_spent = sum(t['amount'] for t in self.transactions)
        
        for category, amounts in category_spending.items():
            category_total = sum(amounts)
            analysis[category] = {
                'total_spent': category_total,
                'average_transaction': statistics.mean(amounts),
                'median_transaction': statistics.median(amounts),
                'transaction_count': len(amounts),
                'percentage_of_total': (category_total / total_spent) * 100,
                'monthly_average': category_total / len(set(t['date'].strftime('%Y-%m') for t in self.transactions))
            }
        
        # Overall spending analysis
        analysis['overall'] = {
            'total_spent': total_spent,
            'monthly_spending': dict(monthly_spending),
            'average_monthly': statistics.mean(monthly_spending.values()) if monthly_spending else 0,
            'spending_trend': self._calculate_spending_trend(monthly_spending)
        }
        
        return analysis
    
    def _calculate_spending_trend(self, monthly_spending: Dict[str, float]) -> str:
        """Calculate whether spending is increasing, decreasing, or stable."""
        if len(monthly_spending) < 2:
            return "insufficient_data"
        
        months = sorted(monthly