```python
"""
Personal Finance Data Processing Module

This module calculates monthly spending insights from transaction data including:
- Total expenses per category
- Spending trends over time
- Average transaction amounts
- Top merchants by spending volume

The module processes sample transaction data and provides comprehensive
financial analytics to help users understand their spending patterns.

Usage: python script.py
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class SpendingAnalyzer:
    """Analyzes spending data and generates insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        self.category_totals = defaultdict(float)
        self.merchant_totals = defaultdict(float)
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        categories = ['Groceries', 'Dining', 'Gas', 'Shopping', 'Utilities', 'Entertainment', 'Healthcare']
        merchants = {
            'Groceries': ['Walmart', 'Kroger', 'Target', 'Whole Foods'],
            'Dining': ['McDonalds', 'Starbucks', 'Pizza Hut', 'Local Bistro'],
            'Gas': ['Shell', 'Exxon', 'BP', 'Chevron'],
            'Shopping': ['Amazon', 'Best Buy', 'Macy\'s', 'Nike'],
            'Utilities': ['Electric Company', 'Gas Company', 'Water Dept', 'Internet ISP'],
            'Entertainment': ['Netflix', 'Movie Theater', 'Concert Hall', 'Gaming Store'],
            'Healthcare': ['CVS Pharmacy', 'Doctor Office', 'Dentist', 'Hospital']
        }
        
        # Generate 6 months of sample data
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(200):
            try:
                transaction_date = base_date + timedelta(days=random.randint(0, 180))
                category = random.choice(categories)
                merchant = random.choice(merchants[category])
                
                # Generate realistic amounts based on category
                amount_ranges = {
                    'Groceries': (20, 150),
                    'Dining': (8, 75),
                    'Gas': (25, 80),
                    'Shopping': (15, 300),
                    'Utilities': (50, 200),
                    'Entertainment': (10, 100),
                    'Healthcare': (20, 500)
                }
                
                min_amt, max_amt = amount_ranges[category]
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                self.transactions.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'amount': amount,
                    'category': category,
                    'merchant': merchant,
                    'description': f'{merchant} - {category}'
                })
            except Exception as e:
                print(f"Error generating sample transaction {i}: {e}")
                continue
    
    def process_transactions(self) -> None:
        """Process transactions and calculate various metrics."""
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                merchant = transaction['merchant']
                amount = transaction['amount']
                
                # Monthly category totals
                self.monthly_data[month_key][category] += amount
                
                # Overall category totals
                self.category_totals[category] += amount
                
                # Merchant totals
                self.merchant_totals[merchant] += amount
                
        except Exception as e:
            print(f"Error processing transactions: {e}")
    
    def calculate_category_totals(self) -> Dict[str, float]:
        """Calculate total expenses per category."""
        try:
            sorted_categories = dict(sorted(self.category_totals.items(), 
                                         key=lambda x: x[1], reverse=True))
            return sorted_categories
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def calculate_spending_trends(self) -> Dict[str, Dict[str, float]]:
        """Calculate spending trends over time by month and category."""
        try:
            trends = {}
            for month, categories in sorted(self.monthly_data.items()):
                trends[month] = dict(categories)
            return trends
        except Exception as e:
            print(f"Error calculating spending trends: {e}")
            return {}
    
    def calculate_average_transactions(self) -> Dict[str, float]:
        """Calculate average transaction amounts per category."""
        try:
            category_counts = Counter(t['category'] for t in self.transactions)
            averages = {}
            
            for category, total in self.category_totals.items():
                count = category_counts[category]
                if count > 0:
                    averages[category] = round(total / count, 2)
                    
            return dict(sorted(averages.items(), key=lambda x: x[1], reverse=True))
        except Exception as e:
            print(f"Error calculating average transactions: {e}")
            return {}
    
    def get_top_merchants(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Get top merchants by spending volume."""
        try:
            sorted_merchants = sorted(self.merchant_totals.items(), 
                                    key=lambda x: x[1], reverse=True)
            return sorted_merchants[:limit]
        except Exception as e:
            print(f"Error getting top merchants: {e}")
            return []
    
    def generate_monthly_summary(self) -> Dict[str, float]:
        """Generate monthly spending summary."""
        try:
            monthly_totals = {}
            for month, categories in self.monthly_data.items():
                monthly_totals[month] = round(sum(categories.values()), 2)
            return dict(sorted(monthly_totals.items()))
        except Exception as e:
            print(f"Error generating monthly summary: {e}")
            return {}


def print_insights(analyzer: SpendingAnalyzer) -> None:
    """Print all spending insights in a formatted manner."""
    try:
        print("=" * 60)
        print("MONTHLY SPENDING INSIGHTS REPORT")
        print("=" * 60)
        
        # Category totals
        print("\n📊 TOTAL EXPENSES BY CATEGORY")
        print("-" * 40)
        category_totals = analyzer.calculate_category_totals()
        for category, amount in category_totals.items():
            print(f"{category:<20} ${amount:>8.2f}")
        
        total_spending = sum(category_totals.values())
        print("-" * 40)
        print(f"{'TOTAL':<20} ${total_spending:>8.2f}")
        
        # Monthly summary
        print("\n📅 MONTHLY SPENDING SUMMARY")
        print("-" * 40)
        monthly_summary = analyzer.generate_monthly_summary()
        for month, amount in monthly_summary.items():
            print(f"{month:<20} ${amount:>8.2f}")
        
        # Average transactions
        print("\n💰 AVERAGE TRANSACTION BY CATEGORY")
        print("-" * 40)
        averages = analyzer.calculate_average_transactions()
        for category, avg in averages.items():
            print(f"{category:<20} ${avg:>8.2f}")
        
        # Top merchants
        print("\n🏪 TOP 10 MERCHANTS BY SPENDING")
        print("-" * 40)
        top_merchants = analyzer.get_top_merchants(10)
        for rank, (merchant, amount) in enumerate(top_merchants, 1):
            print(f"{rank:>2}. {merchant:<25} ${amount:>8.2f}")
        
        # Spending trends
        print("\n📈