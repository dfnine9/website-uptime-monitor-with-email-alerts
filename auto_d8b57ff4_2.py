```python
"""
Monthly Financial Analysis Generator

This module processes categorized financial transactions to generate comprehensive
spending summaries, trend analyses, and identify unusual spending patterns.

Features:
- Monthly spending summaries by category
- Trend analysis comparing current vs previous periods
- Statistical anomaly detection for unusual spending
- Percentage distribution analysis
- Growth rate calculations

The script processes sample transaction data and outputs detailed financial insights
to help users understand their spending habits and identify potential areas for
budget optimization.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import math


class TransactionAnalyzer:
    """Analyzes financial transactions for spending patterns and trends."""
    
    def __init__(self):
        self.transactions = []
        self.categories = set()
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        try:
            sample_data = [
                {"date": "2024-01-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-01-16", "amount": 85.50, "category": "Groceries", "description": "Weekly shopping"},
                {"date": "2024-01-20", "amount": 45.00, "category": "Dining", "description": "Restaurant dinner"},
                {"date": "2024-01-25", "amount": 120.00, "category": "Utilities", "description": "Electric bill"},
                {"date": "2024-02-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-02-16", "amount": 92.30, "category": "Groceries", "description": "Weekly shopping"},
                {"date": "2024-02-22", "amount": 65.00, "category": "Dining", "description": "Restaurant lunch"},
                {"date": "2024-02-28", "amount": 135.00, "category": "Utilities", "description": "Electric bill"},
                {"date": "2024-03-01", "amount": 300.00, "category": "Shopping", "description": "Clothing"},
                {"date": "2024-03-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-03-16", "amount": 88.75, "category": "Groceries", "description": "Weekly shopping"},
                {"date": "2024-03-20", "amount": 180.00, "category": "Dining", "description": "Special dinner"},
                {"date": "2024-03-25", "amount": 110.00, "category": "Utilities", "description": "Electric bill"},
                {"date": "2024-04-02", "amount": 500.00, "category": "Car", "description": "Car maintenance"},
                {"date": "2024-04-15", "amount": 1200.00, "category": "Rent", "description": "Monthly rent"},
                {"date": "2024-04-16", "amount": 95.20, "category": "Groceries", "description": "Weekly shopping"},
                {"date": "2024-04-18", "amount": 55.00, "category": "Dining", "description": "Restaurant dinner"},
                {"date": "2024-04-25", "amount": 125.00, "category": "Utilities", "description": "Electric bill"},
                {"date": "2024-04-30", "amount": 2500.00, "category": "Travel", "description": "Vacation expenses"},
            ]
            
            for transaction in sample_data:
                transaction['date'] = datetime.strptime(transaction['date'], '%Y-%m-%d')
                self.categories.add(transaction['category'])
            
            self.transactions = sample_data
            print("✓ Sample transaction data loaded successfully")
            
        except Exception as e:
            print(f"Error loading sample data: {e}")
            raise
    
    def categorize_by_month(self) -> Dict[str, List[Dict]]:
        """Group transactions by month-year."""
        try:
            monthly_data = defaultdict(list)
            
            for transaction in self.transactions:
                month_key = transaction['date'].strftime('%Y-%m')
                monthly_data[month_key].append(transaction)
            
            return dict(monthly_data)
        
        except Exception as e:
            print(f"Error categorizing transactions by month: {e}")
            return {}
    
    def generate_monthly_summary(self, monthly_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Generate spending summary for each month."""
        try:
            summaries = {}
            
            for month, transactions in monthly_data.items():
                total_spending = sum(t['amount'] for t in transactions)
                category_totals = defaultdict(float)
                transaction_count = len(transactions)
                
                for transaction in transactions:
                    category_totals[transaction['category']] += transaction['amount']
                
                # Calculate percentages
                category_percentages = {
                    cat: (amount / total_spending) * 100 
                    for cat, amount in category_totals.items()
                }
                
                summaries[month] = {
                    'total_spending': total_spending,
                    'transaction_count': transaction_count,
                    'average_transaction': total_spending / transaction_count if transaction_count > 0 else 0,
                    'category_totals': dict(category_totals),
                    'category_percentages': category_percentages
                }
            
            return summaries
        
        except Exception as e:
            print(f"Error generating monthly summary: {e}")
            return {}
    
    def calculate_trends(self, summaries: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate spending trends across months."""
        try:
            sorted_months = sorted(summaries.keys())
            if len(sorted_months) < 2:
                return {'error': 'Need at least 2 months of data for trend analysis'}
            
            trends = {
                'monthly_totals': {},
                'growth_rates': {},
                'category_trends': defaultdict(dict)
            }
            
            # Monthly total trends
            for month in sorted_months:
                trends['monthly_totals'][month] = summaries[month]['total_spending']
            
            # Calculate month-over-month growth rates
            for i in range(1, len(sorted_months)):
                current_month = sorted_months[i]
                previous_month = sorted_months[i-1]
                
                current_total = summaries[current_month]['total_spending']
                previous_total = summaries[previous_month]['total_spending']
                
                if previous_total > 0:
                    growth_rate = ((current_total - previous_total) / previous_total) * 100
                    trends['growth_rates'][current_month] = growth_rate
            
            # Category-specific trends
            all_categories = set()
            for summary in summaries.values():
                all_categories.update(summary['category_totals'].keys())
            
            for category in all_categories:
                category_monthly = {}
                for month in sorted_months:
                    amount = summaries[month]['category_totals'].get(category, 0)
                    category_monthly[month] = amount
                
                trends['category_trends'][category] = category_monthly
            
            return trends
        
        except Exception as e:
            print(f"Error calculating trends: {e}")
            return {}
    
    def detect_anomalies(self, summaries: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns using statistical analysis."""
        try:
            anomalies = []
            
            # Collect all spending amounts by category
            category_amounts = defaultdict(list)
            
            for month_data in summaries.values():
                for category, amount in month_data['category_totals'].items():
                    category_amounts[category].append(amount)
            
            # Detect anomalies for each category
            for category, amounts in category_amounts.