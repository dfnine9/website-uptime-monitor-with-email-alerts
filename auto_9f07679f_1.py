```python
"""
Transaction Data Analysis Module

This module processes categorized financial transaction data to generate comprehensive
spending summaries and analysis. It provides functionality to:

1. Generate monthly spending summaries with category breakdowns
2. Calculate category totals and percentage distributions
3. Identify spending patterns and trends over time periods
4. Detect anomalies and significant changes in spending behavior

The module uses only standard library components plus httpx and anthropic for
external data processing capabilities, making it lightweight and portable.

Usage: python script.py
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import statistics
import re


class TransactionAnalyzer:
    """Analyzes transaction data to identify spending patterns and trends."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        
    def load_sample_data(self) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        sample_transactions = [
            {"date": "2024-01-15", "amount": 85.50, "category": "Groceries", "description": "Supermarket"},
            {"date": "2024-01-20", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-01-22", "amount": 45.30, "category": "Utilities", "description": "Electric bill"},
            {"date": "2024-01-25", "amount": 120.75, "category": "Groceries", "description": "Grocery store"},
            {"date": "2024-02-03", "amount": 65.20, "category": "Entertainment", "description": "Movie tickets"},
            {"date": "2024-02-10", "amount": 95.40, "category": "Groceries", "description": "Weekly shopping"},
            {"date": "2024-02-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-02-18", "amount": 52.10, "category": "Utilities", "description": "Water bill"},
            {"date": "2024-02-25", "amount": 180.90, "category": "Dining", "description": "Restaurant"},
            {"date": "2024-03-05", "amount": 110.25, "category": "Groceries", "description": "Supermarket"},
            {"date": "2024-03-12", "amount": 75.80, "category": "Entertainment", "description": "Concert"},
            {"date": "2024-03-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
            {"date": "2024-03-20", "amount": 48.90, "category": "Utilities", "description": "Gas bill"},
            {"date": "2024-03-28", "amount": 220.15, "category": "Dining", "description": "Fine dining"},
        ]
        return sample_transactions
    
    def parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Load and validate transaction data."""
        try:
            for transaction in transactions:
                # Validate required fields
                required_fields = ['date', 'amount', 'category']
                for field in required_fields:
                    if field not in transaction:
                        raise ValueError(f"Missing required field: {field}")
                
                # Parse and validate date
                date_obj = self.parse_date(transaction['date'])
                
                # Validate amount
                amount = float(transaction['amount'])
                if amount <= 0:
                    raise ValueError(f"Amount must be positive: {amount}")
                
                # Store processed transaction
                processed_transaction = {
                    'date': date_obj,
                    'amount': amount,
                    'category': transaction['category'].strip(),
                    'description': transaction.get('description', '').strip()
                }
                
                self.transactions.append(processed_transaction)
                self.categories.add(processed_transaction['category'])
                
                # Build monthly data structure
                month_key = date_obj.strftime("%Y-%m")
                self.monthly_data[month_key][processed_transaction['category']] += amount
                
        except Exception as e:
            print(f"Error loading transactions: {str(e)}", file=sys.stderr)
            raise
    
    def generate_monthly_summaries(self) -> Dict[str, Dict[str, float]]:
        """Generate monthly spending summaries by category."""
        try:
            summaries = {}
            
            for month, categories in self.monthly_data.items():
                monthly_total = sum(categories.values())
                summaries[month] = {
                    'total': monthly_total,
                    'categories': dict(categories),
                    'category_percentages': {
                        cat: (amount / monthly_total * 100) if monthly_total > 0 else 0
                        for cat, amount in categories.items()
                    }
                }
            
            return summaries
            
        except Exception as e:
            print(f"Error generating monthly summaries: {str(e)}", file=sys.stderr)
            return {}
    
    def calculate_category_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate overall category totals and percentages."""
        try:
            category_totals = defaultdict(float)
            
            for transaction in self.transactions:
                category_totals[transaction['category']] += transaction['amount']
            
            grand_total = sum(category_totals.values())
            
            return {
                'totals': dict(category_totals),
                'percentages': {
                    cat: (total / grand_total * 100) if grand_total > 0 else 0
                    for cat, total in category_totals.items()
                },
                'grand_total': grand_total
            }
            
        except Exception as e:
            print(f"Error calculating category totals: {str(e)}", file=sys.stderr)
            return {}
    
    def identify_spending_patterns(self) -> Dict[str, Any]:
        """Identify spending patterns and trends over time."""
        try:
            patterns = {}
            
            # Monthly spending trends
            monthly_totals = {
                month: sum(categories.values())
                for month, categories in self.monthly_data.items()
            }
            
            if len(monthly_totals) > 1:
                amounts = list(monthly_totals.values())
                patterns['monthly_trend'] = {
                    'average_monthly_spending': statistics.mean(amounts),
                    'median_monthly_spending': statistics.median(amounts),
                    'spending_variance': statistics.variance(amounts) if len(amounts) > 1 else 0,
                    'highest_month': max(monthly_totals.items(), key=lambda x: x[1]),
                    'lowest_month': min(monthly_totals.items(), key=lambda x: x[1])
                }
            
            # Category consistency analysis
            category_frequency = Counter()
            category_amounts = defaultdict(list)
            
            for month, categories in self.monthly_data.items():
                for category, amount in categories.items():
                    category_frequency[category] += 1
                    category_amounts[category].append(amount)
            
            patterns['category_analysis'] = {}
            for category in self.categories:
                amounts = category_amounts[category]
                if amounts:
                    patterns['category_analysis'][category] = {
                        'frequency': category_frequency[category],
                        'average_monthly': statistics.mean(amounts),
                        'variance': statistics.variance(amounts) if len(amounts) > 1 else 0,
                        'consistency_score': (
                            category