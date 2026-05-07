```python
#!/usr/bin/env python3
"""
Financial Transaction Analysis Module

This module processes categorized financial transactions to:
1. Calculate monthly spending patterns by category
2. Identify spending trends over time using linear regression
3. Generate budget variance alerts when spending exceeds predefined thresholds

The module includes sample transaction data and budget thresholds for demonstration.
It calculates month-over-month changes, trend slopes, and alerts for budget overruns.

Usage: python script.py

Dependencies: Standard library only (datetime, collections, statistics)
"""

import datetime
import json
from collections import defaultdict, namedtuple
from statistics import mean
import sys

Transaction = namedtuple('Transaction', ['date', 'category', 'amount', 'description'])

class TransactionAnalyzer:
    """Analyzes financial transactions for spending patterns and budget compliance."""
    
    def __init__(self, budget_thresholds=None):
        """
        Initialize analyzer with optional budget thresholds.
        
        Args:
            budget_thresholds (dict): Monthly budget limits per category
        """
        self.transactions = []
        self.budget_thresholds = budget_thresholds or {
            'groceries': 800,
            'dining': 400,
            'transportation': 300,
            'entertainment': 200,
            'utilities': 250,
            'shopping': 500
        }
    
    def add_transaction(self, date_str, category, amount, description=""):
        """Add a transaction to the dataset."""
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            self.transactions.append(Transaction(date_obj, category.lower(), float(amount), description))
        except (ValueError, TypeError) as e:
            print(f"Error adding transaction: {e}", file=sys.stderr)
    
    def get_monthly_spending(self):
        """Calculate monthly spending totals by category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                month_key = f"{transaction.date.year}-{transaction.date.month:02d}"
                monthly_data[month_key][transaction.category] += transaction.amount
            
            return dict(monthly_data)
        except Exception as e:
            print(f"Error calculating monthly spending: {e}", file=sys.stderr)
            return {}
    
    def calculate_trends(self, monthly_data):
        """Calculate spending trends using simple linear regression."""
        trends = {}
        
        try:
            # Get all unique categories
            all_categories = set()
            for month_data in monthly_data.values():
                all_categories.update(month_data.keys())
            
            for category in all_categories:
                amounts = []
                months = sorted(monthly_data.keys())
                
                for month in months:
                    amounts.append(monthly_data[month].get(category, 0))
                
                if len(amounts) >= 2:
                    # Simple linear regression slope calculation
                    n = len(amounts)
                    x_values = list(range(n))
                    x_mean = mean(x_values)
                    y_mean = mean(amounts)
                    
                    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, amounts))
                    denominator = sum((x - x_mean) ** 2 for x in x_values)
                    
                    if denominator != 0:
                        slope = numerator / denominator
                        trends[category] = {
                            'slope': slope,
                            'avg_monthly': y_mean,
                            'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                        }
            
            return trends
        except Exception as e:
            print(f"Error calculating trends: {e}", file=sys.stderr)
            return {}
    
    def check_budget_alerts(self, monthly_data):
        """Generate alerts for spending that exceeds budget thresholds."""
        alerts = []
        
        try:
            for month, categories in monthly_data.items():
                for category, amount in categories.items():
                    if category in self.budget_thresholds:
                        threshold = self.budget_thresholds[category]
                        if amount > threshold:
                            variance = amount - threshold
                            variance_pct = (variance / threshold) * 100
                            alerts.append({
                                'month': month,
                                'category': category,
                                'spent': amount,
                                'budget': threshold,
                                'variance': variance,
                                'variance_pct': variance_pct
                            })
            
            return sorted(alerts, key=lambda x: x['variance_pct'], reverse=True)
        except Exception as e:
            print(f"Error checking budget alerts: {e}", file=sys.stderr)
            return []
    
    def generate_report(self):
        """Generate comprehensive spending analysis report."""
        try:
            print("=" * 60)
            print("FINANCIAL TRANSACTION ANALYSIS REPORT")
            print("=" * 60)
            print(f"Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Transactions: {len(self.transactions)}")
            print()
            
            # Monthly spending patterns
            monthly_data = self.get_monthly_spending()
            if not monthly_data:
                print("No transaction data available for analysis.")
                return
            
            print("MONTHLY SPENDING PATTERNS")
            print("-" * 30)
            for month in sorted(monthly_data.keys()):
                print(f"\n{month}:")
                total_month = sum(monthly_data[month].values())
                for category, amount in sorted(monthly_data[month].items()):
                    pct = (amount / total_month * 100) if total_month > 0 else 0
                    print(f"  {category.title():<15}: ${amount:>8.2f} ({pct:>5.1f}%)")
                print(f"  {'TOTAL':<15}: ${total_month:>8.2f}")
            
            # Trend analysis
            trends = self.calculate_trends(monthly_data)
            if trends:
                print("\n\nSPENDING TRENDS ANALYSIS")
                print("-" * 30)
                for category, trend_data in sorted(trends.items()):
                    direction = trend_data['direction']
                    avg_monthly = trend_data['avg_monthly']
                    slope = trend_data['slope']
                    
                    direction_symbol = "↗" if direction == "increasing" else "↘" if direction == "decreasing" else "→"
                    print(f"{category.title():<15}: {direction_symbol} {direction.title():<10} "
                          f"(Avg: ${avg_monthly:>6.2f}, Slope: {slope:>+6.2f})")
            
            # Budget alerts
            alerts = self.check_budget_alerts(monthly_data)
            if alerts:
                print("\n\nBUDGET VARIANCE ALERTS")
                print("-" * 30)
                print("⚠️  Categories exceeding budget thresholds:")
                for alert in alerts:
                    print(f"  {alert['month']} - {alert['category'].title()}:")
                    print(f"    Spent: ${alert['spent']:.2f} | Budget: ${alert['budget']:.2f}")
                    print(f"    Variance: ${alert['variance']:.2f} ({alert['variance_pct']:+.1f}%)")
                    print()
            else:
                print("\n\nBUDGET COMPLIANCE")
                print("-" * 30)
                print("✅ All spending within budget thresholds")
            
            # Summary statistics
            print("\n\nSUMMARY STATISTICS")
            print("-" * 30)
            total_spending = sum(t.amount for t in self.transactions)
            avg_transaction = total_spending / len(self.transactions) if self.transactions else 0
            
            category_totals