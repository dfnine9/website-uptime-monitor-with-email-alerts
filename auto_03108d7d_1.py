```python
#!/usr/bin/env python3
"""
Monthly Spending Insights Generator

This module analyzes financial transaction data to generate comprehensive monthly spending insights.
It provides total spending per category, percentage breakdowns, spending trends over time,
and identifies top merchants within each category.

Features:
- Category-based spending analysis
- Percentage breakdowns with visual representation
- Monthly trend analysis
- Top merchant identification per category
- Data validation and error handling
- Self-contained with minimal dependencies

Usage:
    python script.py

The script uses sample transaction data for demonstration purposes.
In a real-world scenario, this would connect to your financial data source.
"""

import json
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Any
import random


class SpendingAnalyzer:
    """Analyzes spending patterns and generates monthly insights."""
    
    def __init__(self):
        self.transactions = []
        self.categories = defaultdict(Decimal)
        self.monthly_trends = defaultdict(lambda: defaultdict(Decimal))
        self.merchant_spending = defaultdict(lambda: defaultdict(Decimal))
    
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        try:
            categories = ['Groceries', 'Dining', 'Transportation', 'Entertainment', 
                         'Shopping', 'Utilities', 'Healthcare', 'Gas', 'Coffee']
            
            merchants = {
                'Groceries': ['Whole Foods', 'Safeway', 'Trader Joes', 'Costco'],
                'Dining': ['Pizza Palace', 'Burger King', 'Local Bistro', 'Sushi Bar'],
                'Transportation': ['Uber', 'Metro Card', 'Gas Station', 'Parking'],
                'Entertainment': ['Netflix', 'Movie Theater', 'Concert Hall', 'Spotify'],
                'Shopping': ['Amazon', 'Target', 'Best Buy', 'Mall Store'],
                'Utilities': ['Electric Co', 'Water Dept', 'Internet ISP', 'Phone Co'],
                'Healthcare': ['Pharmacy', 'Doctor Office', 'Dental Care', 'Insurance'],
                'Gas': ['Shell', 'BP', 'Chevron', 'Exxon'],
                'Coffee': ['Starbucks', 'Local Cafe', 'Dunkin', 'Coffee Bean']
            }
            
            # Generate transactions for last 6 months
            base_date = datetime.now() - timedelta(days=180)
            
            for i in range(500):  # 500 sample transactions
                date = base_date + timedelta(days=random.randint(0, 180))
                category = random.choice(categories)
                merchant = random.choice(merchants[category])
                
                # Realistic spending amounts by category
                amount_ranges = {
                    'Groceries': (20, 150),
                    'Dining': (15, 80),
                    'Transportation': (5, 50),
                    'Entertainment': (10, 100),
                    'Shopping': (25, 300),
                    'Utilities': (50, 200),
                    'Healthcare': (20, 500),
                    'Gas': (30, 80),
                    'Coffee': (3, 15)
                }
                
                amount = round(random.uniform(*amount_ranges[category]), 2)
                
                self.transactions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'merchant': merchant,
                    'category': category,
                    'amount': amount,
                    'description': f'{merchant} - {category}'
                })
                
        except Exception as e:
            print(f"Error generating sample data: {e}")
            sys.exit(1)
    
    def process_transactions(self) -> None:
        """Process transactions and calculate spending metrics."""
        try:
            for transaction in self.transactions:
                try:
                    amount = Decimal(str(transaction['amount']))
                    category = transaction['category']
                    merchant = transaction['merchant']
                    date_str = transaction['date']
                    
                    # Parse date and get month-year key
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                    
                    # Accumulate data
                    self.categories[category] += amount
                    self.monthly_trends[month_key][category] += amount
                    self.merchant_spending[category][merchant] += amount
                    
                except (InvalidOperation, ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid transaction: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error processing transactions: {e}")
            sys.exit(1)
    
    def calculate_percentages(self) -> Dict[str, float]:
        """Calculate spending percentages by category."""
        try:
            total_spending = sum(self.categories.values())
            if total_spending == 0:
                return {}
            
            percentages = {}
            for category, amount in self.categories.items():
                percentages[category] = float((amount / total_spending) * 100)
            
            return percentages
            
        except Exception as e:
            print(f"Error calculating percentages: {e}")
            return {}
    
    def get_top_merchants_by_category(self, limit: int = 3) -> Dict[str, List[Tuple[str, float]]]:
        """Get top merchants by spending amount for each category."""
        try:
            top_merchants = {}
            
            for category, merchants in self.merchant_spending.items():
                sorted_merchants = sorted(
                    merchants.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:limit]
                
                top_merchants[category] = [
                    (merchant, float(amount)) for merchant, amount in sorted_merchants
                ]
            
            return top_merchants
            
        except Exception as e:
            print(f"Error getting top merchants: {e}")
            return {}
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze spending trends over months."""
        try:
            trends = {}
            
            for month, categories in self.monthly_trends.items():
                month_total = sum(categories.values())
                trends[month] = {
                    'total': float(month_total),
                    'categories': {cat: float(amount) for cat, amount in categories.items()}
                }
            
            return dict(sorted(trends.items()))
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {}
    
    def print_visual_breakdown(self, percentages: Dict[str, float]) -> None:
        """Print a visual representation of spending breakdown."""
        try:
            print("\n" + "="*60)
            print("SPENDING BREAKDOWN (Visual)")
            print("="*60)
            
            sorted_categories = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
            
            for category, percentage in sorted_categories:
                bar_length = int(percentage / 2)  # Scale for display
                bar = "█" * bar_length + "░" * (50 - bar_length)
                print(f"{category:15} {percentage:5.1f}% |{bar}|")
                
        except Exception as e:
            print(f"Error printing visual breakdown: {e}")
    
    def generate_insights(self) -> None:
        """Generate and print comprehensive spending insights."""
        try:
            print("MONTHLY SPENDING INSIGHTS REPORT")
            print("=" * 50)
            print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total transactions analyzed: {len(self.transactions)}")
            
            # Total spending per category
            print("\n" + "="*50)
            print("TOTAL SPENDING BY CATEGORY")
            print("="*50)
            
            total_all = sum(self.categories.values())