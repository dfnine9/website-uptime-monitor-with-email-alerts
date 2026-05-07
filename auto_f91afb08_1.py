```python
"""
Personal Finance Data Processing Module

This module provides comprehensive spending insights including:
- Monthly spending totals by category
- Trend analysis showing spending patterns over time
- Budget variance tracking with configurable limits
- Statistical analysis of spending behavior

Features:
- Self-contained with minimal dependencies
- Configurable spending categories and limits
- Robust error handling and data validation
- Clear reporting with actionable insights
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import calendar


class SpendingInsightsProcessor:
    """Main processor for financial data analysis and insights generation."""
    
    def __init__(self, budget_limits: Optional[Dict[str, float]] = None):
        """Initialize processor with optional budget limits."""
        self.transactions = []
        self.budget_limits = budget_limits or {
            'groceries': 500.0,
            'dining': 300.0,
            'transportation': 200.0,
            'entertainment': 150.0,
            'utilities': 250.0,
            'healthcare': 200.0,
            'shopping': 400.0,
            'other': 100.0
        }
    
    def add_transaction(self, date: str, category: str, amount: float, description: str = ""):
        """Add a transaction to the dataset."""
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            self.transactions.append({
                'date': parsed_date,
                'category': category.lower(),
                'amount': float(amount),
                'description': description
            })
        except ValueError as e:
            raise ValueError(f"Invalid transaction data: {e}")
    
    def load_sample_data(self):
        """Load sample transaction data for demonstration."""
        sample_transactions = [
            ("2024-01-15", "groceries", 85.50, "Weekly grocery shopping"),
            ("2024-01-16", "dining", 45.00, "Restaurant dinner"),
            ("2024-01-20", "transportation", 25.00, "Gas station"),
            ("2024-01-25", "entertainment", 60.00, "Movie tickets"),
            ("2024-02-01", "groceries", 92.30, "Monthly groceries"),
            ("2024-02-05", "utilities", 180.00, "Electric bill"),
            ("2024-02-10", "healthcare", 120.00, "Doctor visit"),
            ("2024-02-14", "dining", 78.50, "Valentine's dinner"),
            ("2024-02-20", "shopping", 230.00, "Clothing purchase"),
            ("2024-03-01", "groceries", 105.20, "Grocery shopping"),
            ("2024-03-08", "transportation", 55.00, "Car maintenance"),
            ("2024-03-12", "entertainment", 40.00, "Concert tickets"),
            ("2024-03-15", "dining", 32.50, "Lunch out"),
            ("2024-03-22", "utilities", 165.00, "Water bill"),
            ("2024-03-28", "shopping", 89.90, "Online purchase"),
        ]
        
        for transaction in sample_transactions:
            try:
                self.add_transaction(*transaction)
            except ValueError as e:
                print(f"Warning: Skipped invalid transaction: {e}")
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in self.transactions:
            month_key = transaction['date'].strftime("%Y-%m")
            category = transaction['category']
            monthly_data[month_key][category] += transaction['amount']
        
        return dict(monthly_data)
    
    def perform_trend_analysis(self) -> Dict[str, List[Tuple[str, float]]]:
        """Analyze spending trends over time by category."""
        monthly_totals = self.calculate_monthly_totals()
        trends = defaultdict(list)
        
        # Sort months chronologically
        sorted_months = sorted(monthly_totals.keys())
        
        for category in self.budget_limits.keys():
            for month in sorted_months:
                amount = monthly_totals.get(month, {}).get(category, 0.0)
                trends[category].append((month, amount))
        
        return dict(trends)
    
    def calculate_budget_variance(self) -> Dict[str, Dict[str, float]]:
        """Calculate variance from budget limits for each category."""
        monthly_totals = self.calculate_monthly_totals()
        variance_data = {}
        
        for month, categories in monthly_totals.items():
            variance_data[month] = {}
            for category, limit in self.budget_limits.items():
                actual = categories.get(category, 0.0)
                variance = actual - limit
                variance_percentage = (variance / limit) * 100 if limit > 0 else 0
                
                variance_data[month][category] = {
                    'actual': actual,
                    'budget': limit,
                    'variance': variance,
                    'variance_percentage': variance_percentage
                }
        
        return variance_data
    
    def generate_insights(self) -> Dict:
        """Generate comprehensive spending insights."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            trends = self.perform_trend_analysis()
            variance_data = self.calculate_budget_variance()
            
            # Calculate overall statistics
            total_spending = sum(t['amount'] for t in self.transactions)
            avg_transaction = statistics.mean([t['amount'] for t in self.transactions])
            
            # Find highest spending categories
            category_totals = defaultdict(float)
            for transaction in self.transactions:
                category_totals[transaction['category']] += transaction['amount']
            
            top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            
            # Identify budget overruns
            overruns = []
            for month, categories in variance_data.items():
                for category, data in categories.items():
                    if data['variance'] > 0:
                        overruns.append({
                            'month': month,
                            'category': category,
                            'variance': data['variance'],
                            'percentage': data['variance_percentage']
                        })
            
            return {
                'summary': {
                    'total_spending': total_spending,
                    'average_transaction': avg_transaction,
                    'transaction_count': len(self.transactions),
                    'date_range': {
                        'start': min(t['date'] for t in self.transactions).strftime("%Y-%m-%d"),
                        'end': max(t['date'] for t in self.transactions).strftime("%Y-%m-%d")
                    }
                },
                'monthly_totals': monthly_totals,
                'trends': trends,
                'budget_variance': variance_data,
                'top_categories': top_categories[:5],
                'budget_overruns': sorted(overruns, key=lambda x: x['variance'], reverse=True)
            }
        
        except Exception as e:
            raise RuntimeError(f"Error generating insights: {e}")
    
    def print_detailed_report(self, insights: Dict):
        """Print a comprehensive spending report."""
        print("=" * 80)
        print("PERSONAL FINANCE SPENDING INSIGHTS REPORT")
        print("=" * 80)
        
        # Summary Section
        summary = insights['summary']
        print(f"\n📊 SPENDING SUMMARY")
        print(f"   Period: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"   Total Spending: ${summary['total_spending']:.2f}")
        print(f"   Average Transaction: ${summary['average_transaction']:.2f}")
        print(f"   Total Transactions: {summary['transaction_count']}")
        
        # Monthly Totals
        print(f"\n📅 MONTHLY SPENDING BY CATEGORY")