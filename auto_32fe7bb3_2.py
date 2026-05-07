```python
"""
Monthly Spending Insights Analyzer

This module analyzes categorized transaction data to generate comprehensive spending insights.
It produces summary reports showing:
- Spending breakdown by category
- Monthly spending trends over time
- Budget variance calculations and alerts
- Key financial metrics and recommendations

The script processes transaction data from CSV format and generates actionable insights
for personal or business financial management.

Usage: python script.py

Author: T.O.A.A Intelligence Swarm
"""

import csv
import json
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import statistics
import io

class SpendingAnalyzer:
    """Main class for analyzing spending patterns and generating insights."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_budgets = {
            'groceries': 800.00,
            'dining': 400.00,
            'transportation': 300.00,
            'utilities': 200.00,
            'entertainment': 250.00,
            'shopping': 350.00,
            'healthcare': 150.00,
            'other': 200.00
        }
    
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        sample_data = [
            {'date': '2024-01-15', 'amount': 89.50, 'category': 'groceries', 'description': 'Whole Foods'},
            {'date': '2024-01-18', 'amount': 45.20, 'category': 'dining', 'description': 'Pizza Palace'},
            {'date': '2024-01-22', 'amount': 125.00, 'category': 'utilities', 'description': 'Electric Bill'},
            {'date': '2024-02-03', 'amount': 67.80, 'category': 'groceries', 'description': 'Safeway'},
            {'date': '2024-02-08', 'amount': 32.50, 'category': 'transportation', 'description': 'Gas Station'},
            {'date': '2024-02-14', 'amount': 156.75, 'category': 'entertainment', 'description': 'Concert Tickets'},
            {'date': '2024-02-20', 'amount': 89.99, 'category': 'shopping', 'description': 'Amazon Purchase'},
            {'date': '2024-03-05', 'amount': 78.30, 'category': 'dining', 'description': 'Restaurant ABC'},
            {'date': '2024-03-12', 'amount': 234.50, 'category': 'groceries', 'description': 'Costco'},
            {'date': '2024-03-18', 'amount': 95.00, 'category': 'healthcare', 'description': 'Pharmacy'},
            {'date': '2024-03-25', 'amount': 167.80, 'category': 'shopping', 'description': 'Department Store'},
            {'date': '2024-04-02', 'amount': 45.60, 'category': 'transportation', 'description': 'Uber Ride'},
            {'date': '2024-04-10', 'amount': 123.45, 'category': 'utilities', 'description': 'Internet Bill'},
            {'date': '2024-04-15', 'amount': 87.25, 'category': 'groceries', 'description': 'Local Market'},
            {'date': '2024-04-22', 'amount': 198.50, 'category': 'entertainment', 'description': 'Movie & Dinner'},
        ]
        self.transactions = sample_data
    
    def parse_date(self, date_str: str) -> datetime.date:
        """Parse date string into datetime object."""
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.datetime.strptime(date_str, '%m/%d/%Y').date()
            except ValueError:
                raise ValueError(f"Unable to parse date: {date_str}")
    
    def get_month_year(self, date_obj: datetime.date) -> str:
        """Convert date to YYYY-MM format for monthly grouping."""
        return date_obj.strftime('%Y-%m')
    
    def analyze_spending_by_category(self) -> Dict[str, float]:
        """Calculate total spending by category."""
        category_totals = defaultdict(float)
        
        try:
            for transaction in self.transactions:
                category = transaction['category'].lower()
                amount = float(transaction['amount'])
                category_totals[category] += amount
        except (KeyError, ValueError) as e:
            print(f"Error processing transaction data: {e}")
            return {}
        
        return dict(category_totals)
    
    def analyze_monthly_trends(self) -> Dict[str, Dict[str, float]]:
        """Analyze spending trends by month and category."""
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        try:
            for transaction in self.transactions:
                date_obj = self.parse_date(transaction['date'])
                month_key = self.get_month_year(date_obj)
                category = transaction['category'].lower()
                amount = float(transaction['amount'])
                
                monthly_data[month_key][category] += amount
                monthly_data[month_key]['total'] += amount
        except (KeyError, ValueError) as e:
            print(f"Error analyzing monthly trends: {e}")
            return {}
        
        return dict(monthly_data)
    
    def calculate_budget_variance(self, category_totals: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Calculate budget variance for each category."""
        variance_data = {}
        
        try:
            for category, spent in category_totals.items():
                budget = self.monthly_budgets.get(category, 0)
                variance = budget - spent
                variance_pct = (variance / budget * 100) if budget > 0 else 0
                
                variance_data[category] = {
                    'budgeted': budget,
                    'spent': spent,
                    'variance': variance,
                    'variance_percentage': variance_pct,
                    'status': 'over' if variance < 0 else 'under'
                }
        except (TypeError, ZeroDivisionError) as e:
            print(f"Error calculating budget variance: {e}")
            return {}
        
        return variance_data
    
    def generate_insights(self, monthly_data: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate actionable insights from spending data."""
        insights = []
        
        try:
            # Calculate average monthly spending
            monthly_totals = [data.get('total', 0) for data in monthly_data.values()]
            if monthly_totals:
                avg_monthly = statistics.mean(monthly_totals)
                insights.append(f"Average monthly spending: ${avg_monthly:.2f}")
                
                # Find highest and lowest spending months
                sorted_months = sorted(monthly_data.items(), key=lambda x: x[1].get('total', 0))
                if len(sorted_months) >= 2:
                    lowest_month = sorted_months[0]
                    highest_month = sorted_months[-1]
                    insights.append(f"Lowest spending month: {lowest_month[0]} (${lowest_month[1].get('total', 0):.2f})")
                    insights.append(f"Highest spending month: {highest_month[0]} (${highest_month[1].get('total', 0):.2f})")
            
            # Find most expensive category overall
            all_categories = defaultdict(float)
            for month_data in monthly_data.values():
                for category, amount in month_data.items():
                    if category != 'total':
                        all_categories[category] += amount
            
            if all_categories:
                top_category = max(all_categories.items(), key=lambda x: x[1])
                insights.append(f"