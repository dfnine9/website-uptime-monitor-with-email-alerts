```python
#!/usr/bin/env python3
"""
Monthly Spending Insights Data Analysis Module

This module provides comprehensive analysis of monthly spending data including:
- Category totals and percentage breakdowns
- Spending trends over time
- Top expenses identification within each category
- Statistical insights and recommendations

The module generates sample transaction data for demonstration purposes
and provides detailed spending analysis with error handling.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from decimal import Decimal, ROUND_HALF_UP
import random


class SpendingAnalyzer:
    """Analyzes spending data and generates monthly insights."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Personal Care', 'Home & Garden', 'Insurance', 'Taxes'
        ]
    
    def generate_sample_data(self, months=6, transactions_per_month=50):
        """Generate sample transaction data for analysis."""
        try:
            base_date = datetime.now() - timedelta(days=30 * months)
            
            for month in range(months):
                month_date = base_date + timedelta(days=30 * month)
                
                for _ in range(transactions_per_month):
                    transaction = {
                        'date': month_date + timedelta(days=random.randint(0, 29)),
                        'amount': round(random.uniform(5.00, 500.00), 2),
                        'category': random.choice(self.categories),
                        'description': f"Transaction {random.randint(1000, 9999)}"
                    }
                    self.transactions.append(transaction)
            
            print(f"Generated {len(self.transactions)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def calculate_category_totals(self, month=None):
        """Calculate spending totals by category."""
        try:
            category_totals = defaultdict(float)
            filtered_transactions = self._filter_by_month(month) if month else self.transactions
            
            for transaction in filtered_transactions:
                category_totals[transaction['category']] += transaction['amount']
            
            return dict(category_totals)
            
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return {}
    
    def calculate_percentage_breakdown(self, category_totals):
        """Calculate percentage breakdown of spending by category."""
        try:
            total_spending = sum(category_totals.values())
            if total_spending == 0:
                return {}
            
            percentages = {}
            for category, amount in category_totals.items():
                percentage = (amount / total_spending) * 100
                percentages[category] = round(percentage, 2)
            
            return percentages
            
        except Exception as e:
            print(f"Error calculating percentage breakdown: {e}")
            return {}
    
    def analyze_spending_trends(self):
        """Analyze spending trends over multiple months."""
        try:
            monthly_totals = defaultdict(float)
            monthly_transactions = defaultdict(list)
            
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
                monthly_transactions[month_key].append(transaction)
            
            trends = {}
            sorted_months = sorted(monthly_totals.keys())
            
            for i, month in enumerate(sorted_months):
                trend_data = {
                    'total': round(monthly_totals[month], 2),
                    'transaction_count': len(monthly_transactions[month]),
                    'average_transaction': round(monthly_totals[month] / len(monthly_transactions[month]), 2)
                }
                
                if i > 0:
                    previous_total = monthly_totals[sorted_months[i-1]]
                    change = monthly_totals[month] - previous_total
                    change_percent = (change / previous_total) * 100 if previous_total > 0 else 0
                    trend_data['month_over_month_change'] = round(change, 2)
                    trend_data['change_percent'] = round(change_percent, 2)
                
                trends[month] = trend_data
            
            return trends
            
        except Exception as e:
            print(f"Error analyzing spending trends: {e}")
            return {}
    
    def identify_top_expenses(self, category_totals, top_n=3):
        """Identify top expenses within each category."""
        try:
            category_expenses = defaultdict(list)
            
            # Group transactions by category
            for transaction in self.transactions:
                category_expenses[transaction['category']].append({
                    'amount': transaction['amount'],
                    'description': transaction['description'],
                    'date': transaction['date'].strftime('%Y-%m-%d')
                })
            
            top_expenses = {}
            for category in category_totals:
                if category in category_expenses:
                    sorted_expenses = sorted(
                        category_expenses[category], 
                        key=lambda x: x['amount'], 
                        reverse=True
                    )
                    top_expenses[category] = sorted_expenses[:top_n]
            
            return top_expenses
            
        except Exception as e:
            print(f"Error identifying top expenses: {e}")
            return {}
    
    def _filter_by_month(self, target_month):
        """Filter transactions by specific month (YYYY-MM format)."""
        try:
            filtered = []
            for transaction in self.transactions:
                if transaction['date'].strftime('%Y-%m') == target_month:
                    filtered.append(transaction)
            return filtered
            
        except Exception as e:
            print(f"Error filtering by month: {e}")
            return []
    
    def generate_insights_report(self):
        """Generate comprehensive spending insights report."""
        try:
            print("\n" + "="*60)
            print("MONTHLY SPENDING INSIGHTS REPORT")
            print("="*60)
            
            # Overall statistics
            total_spending = sum(t['amount'] for t in self.transactions)
            avg_transaction = total_spending / len(self.transactions) if self.transactions else 0
            
            print(f"\nOVERALL STATISTICS:")
            print(f"Total Transactions: {len(self.transactions):,}")
            print(f"Total Spending: ${total_spending:,.2f}")
            print(f"Average Transaction: ${avg_transaction:.2f}")
            
            # Category analysis
            category_totals = self.calculate_category_totals()
            percentages = self.calculate_percentage_breakdown(category_totals)
            
            print(f"\nCATEGORY BREAKDOWN:")
            print("-" * 40)
            for category in sorted(category_totals, key=category_totals.get, reverse=True):
                amount = category_totals[category]
                percent = percentages.get(category, 0)
                print(f"{category:<20} ${amount:>8,.2f} ({percent:>5.1f}%)")
            
            # Spending trends
            trends = self.analyze_spending_trends()
            print(f"\nMONTHLY SPENDING TRENDS:")
            print("-" * 40)
            for month, data in sorted(trends.items()):
                print(f"\n{month}:")
                print(f"  Total: ${data['total']:,.2f}")
                print(f"  Transactions: {data['transaction_count']}")
                print(f"  Avg Transaction: ${data['average_transaction']:.2f}")
                
                if 'change_percent' in data:
                    change_symbol = "↑" if data['change_percent'] > 0 else "↓"
                    print(f"  Change: {change_symbol} {data['change_percent']:+.1f}% (${data['month_