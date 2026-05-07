```python
"""
Financial Transaction Analysis Module

This module processes categorized financial transactions to generate comprehensive
spending insights including monthly totals by category, spending trends over time,
and budget variance calculations. It provides a complete analysis framework for
personal or business financial data.

Features:
- Monthly spending totals by category
- Trend analysis over time periods
- Budget variance calculations
- Statistical summaries and insights
- Data validation and error handling

Usage:
    python script.py

The script generates sample transaction data and demonstrates all analysis
capabilities with formatted output to stdout.
"""

import json
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import statistics
import calendar


class TransactionAnalyzer:
    """Analyzes financial transactions to generate spending insights."""
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        
    def add_transaction(self, date: str, category: str, amount: float, description: str = ""):
        """Add a transaction to the dataset."""
        try:
            # Validate date format
            datetime.datetime.strptime(date, '%Y-%m-%d')
            transaction = {
                'date': date,
                'category': category.strip().lower(),
                'amount': float(amount),
                'description': description.strip()
            }
            self.transactions.append(transaction)
        except (ValueError, TypeError) as e:
            print(f"Error adding transaction: {e}")
    
    def set_budget(self, category: str, monthly_limit: float):
        """Set monthly budget for a category."""
        try:
            self.budgets[category.strip().lower()] = float(monthly_limit)
        except (ValueError, TypeError) as e:
            print(f"Error setting budget: {e}")
    
    def get_monthly_totals_by_category(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        monthly_totals = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            try:
                date_obj = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                category = transaction['category']
                amount = abs(transaction['amount'])  # Use absolute value for spending
                
                monthly_totals[month_key][category] += amount
            except (ValueError, KeyError) as e:
                print(f"Error processing transaction: {e}")
                continue
        
        return dict(monthly_totals)
    
    def calculate_spending_trends(self) -> Dict[str, Any]:
        """Calculate spending trends over time."""
        monthly_totals = self.get_monthly_totals_by_category()
        trends = {}
        
        try:
            # Overall monthly spending trend
            monthly_sums = {}
            for month, categories in monthly_totals.items():
                monthly_sums[month] = sum(categories.values())
            
            # Sort by month
            sorted_months = sorted(monthly_sums.keys())
            monthly_amounts = [monthly_sums[month] for month in sorted_months]
            
            trends['monthly_total_trend'] = {
                'months': sorted_months,
                'amounts': monthly_amounts,
                'average': statistics.mean(monthly_amounts) if monthly_amounts else 0,
                'median': statistics.median(monthly_amounts) if monthly_amounts else 0
            }
            
            # Category trends
            category_trends = defaultdict(list)
            for month in sorted_months:
                for category in set().union(*(categories.keys() for categories in monthly_totals.values())):
                    amount = monthly_totals.get(month, {}).get(category, 0)
                    category_trends[category].append(amount)
            
            trends['category_trends'] = {}
            for category, amounts in category_trends.items():
                if amounts:
                    trends['category_trends'][category] = {
                        'amounts': amounts,
                        'average': statistics.mean(amounts),
                        'trend': 'increasing' if amounts[-1] > amounts[0] else 'decreasing' if amounts[-1] < amounts[0] else 'stable'
                    }
            
        except (StatisticsError, ValueError) as e:
            print(f"Error calculating trends: {e}")
        
        return trends
    
    def calculate_budget_variance(self) -> Dict[str, Any]:
        """Calculate budget variance for categories with set budgets."""
        monthly_totals = self.get_monthly_totals_by_category()
        variance_analysis = {}
        
        try:
            for month, categories in monthly_totals.items():
                variance_analysis[month] = {}
                
                for category, budget_limit in self.budgets.items():
                    actual_spending = categories.get(category, 0)
                    variance = actual_spending - budget_limit
                    variance_pct = (variance / budget_limit * 100) if budget_limit > 0 else 0
                    
                    variance_analysis[month][category] = {
                        'budget': budget_limit,
                        'actual': actual_spending,
                        'variance': variance,
                        'variance_percentage': variance_pct,
                        'status': 'over' if variance > 0 else 'under' if variance < 0 else 'on_target'
                    }
        
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error calculating budget variance: {e}")
        
        return variance_analysis
    
    def generate_insights_report(self) -> str:
        """Generate a comprehensive insights report."""
        try:
            report = []
            report.append("=== FINANCIAL TRANSACTION ANALYSIS REPORT ===\n")
            
            # Basic statistics
            total_transactions = len(self.transactions)
            total_spending = sum(abs(t['amount']) for t in self.transactions)
            unique_categories = len(set(t['category'] for t in self.transactions))
            
            report.append(f"Total Transactions: {total_transactions}")
            report.append(f"Total Spending: ${total_spending:.2f}")
            report.append(f"Unique Categories: {unique_categories}\n")
            
            # Monthly totals by category
            report.append("=== MONTHLY TOTALS BY CATEGORY ===")
            monthly_totals = self.get_monthly_totals_by_category()
            
            for month in sorted(monthly_totals.keys()):
                report.append(f"\n{month}:")
                categories = monthly_totals[month]
                for category in sorted(categories.keys()):
                    report.append(f"  {category.title()}: ${categories[category]:.2f}")
                report.append(f"  Month Total: ${sum(categories.values()):.2f}")
            
            # Spending trends
            report.append("\n=== SPENDING TRENDS ===")
            trends = self.calculate_spending_trends()
            
            if 'monthly_total_trend' in trends:
                trend_data = trends['monthly_total_trend']
                report.append(f"Average Monthly Spending: ${trend_data['average']:.2f}")
                report.append(f"Median Monthly Spending: ${trend_data['median']:.2f}")
            
            if 'category_trends' in trends:
                report.append("\nCategory Trends:")
                for category, data in trends['category_trends'].items():
                    report.append(f"  {category.title()}: {data['trend'].title()} (Avg: ${data['average']:.2f})")
            
            # Budget variance
            if self.budgets:
                report.append("\n=== BUDGET VARIANCE ANALYSIS ===")
                variance_data = self.calculate_budget_variance()
                
                for month in sorted(variance_data.keys()):
                    report.append(f"\n{month}:")
                    for category, analysis in variance_data[month].items():
                        status_icon = "⚠️" if analysis['status'] == 'over' else "✅"
                        report.append(f"  {status_icon} {category.title()}:")