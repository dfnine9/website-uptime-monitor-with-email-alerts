```python
"""
Personal Finance Data Analysis Module

This module analyzes spending data to calculate monthly trends, category breakdowns,
and identify unusual spending patterns or budget overruns. It generates sample
transaction data for demonstration purposes and provides comprehensive financial
insights including trend analysis, category spending distribution, anomaly detection,
and budget variance reporting.

Features:
- Monthly spending trend calculation
- Category-wise expenditure breakdown
- Unusual spending pattern detection using statistical analysis
- Budget overrun identification
- Summary statistics and insights

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class SpendingAnalyzer:
    """Analyzes spending patterns and generates financial insights."""
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        
    def load_sample_data(self):
        """Generate sample transaction data for analysis."""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                     'Healthcare', 'Shopping', 'Travel', 'Education']
        
        # Generate transactions for the last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        current_date = start_date
        while current_date <= end_date:
            # Generate 5-15 transactions per day
            num_transactions = random.randint(5, 15)
            
            for _ in range(num_transactions):
                category = random.choice(categories)
                # Different spending ranges by category
                if category == 'Travel':
                    amount = random.uniform(200, 1500)
                elif category == 'Utilities':
                    amount = random.uniform(50, 300)
                elif category == 'Food':
                    amount = random.uniform(10, 150)
                else:
                    amount = random.uniform(20, 500)
                
                # Occasionally add unusual spending (10% chance)
                if random.random() < 0.1:
                    amount *= random.uniform(2, 5)
                
                transaction = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'amount': round(amount, 2),
                    'category': category,
                    'description': f'{category} purchase'
                }
                self.transactions.append(transaction)
            
            current_date += timedelta(days=1)
        
        # Set monthly budgets
        self.budgets = {
            'Food': 800,
            'Transportation': 400,
            'Entertainment': 300,
            'Utilities': 250,
            'Healthcare': 200,
            'Shopping': 500,
            'Travel': 1000,
            'Education': 300
        }
    
    def calculate_monthly_trends(self) -> Dict[str, float]:
        """Calculate monthly spending trends."""
        try:
            monthly_totals = defaultdict(float)
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                monthly_totals[month_key] += transaction['amount']
            
            # Sort by month
            sorted_months = sorted(monthly_totals.items())
            
            return dict(sorted_months)
        
        except Exception as e:
            print(f"Error calculating monthly trends: {e}")
            return {}
    
    def calculate_category_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Calculate spending breakdown by category."""
        try:
            category_totals = defaultdict(float)
            category_counts = defaultdict(int)
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                category_totals[category] += amount
                category_counts[category] += 1
            
            total_spending = sum(category_totals.values())
            
            breakdown = {}
            for category, total in category_totals.items():
                breakdown[category] = {
                    'total': round(total, 2),
                    'percentage': round((total / total_spending) * 100, 2),
                    'average_per_transaction': round(total / category_counts[category], 2),
                    'transaction_count': category_counts[category]
                }
            
            return breakdown
        
        except Exception as e:
            print(f"Error calculating category breakdown: {e}")
            return {}
    
    def detect_unusual_patterns(self) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns using statistical analysis."""
        try:
            unusual_patterns = []
            
            # Group transactions by category for analysis
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction['category']].append(transaction['amount'])
            
            for category, amounts in category_amounts.items():
                if len(amounts) < 3:  # Need at least 3 data points
                    continue
                
                mean_amount = statistics.mean(amounts)
                stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                # Define unusual as more than 2 standard deviations from mean
                threshold = mean_amount + (2 * stdev_amount)
                
                unusual_transactions = [
                    {
                        'date': t['date'],
                        'amount': t['amount'],
                        'category': t['category'],
                        'description': t['description'],
                        'deviation_factor': round((t['amount'] - mean_amount) / stdev_amount, 2) if stdev_amount > 0 else 0
                    }
                    for t in self.transactions
                    if t['category'] == category and t['amount'] > threshold
                ]
                
                unusual_patterns.extend(unusual_transactions)
            
            # Sort by deviation factor (highest first)
            unusual_patterns.sort(key=lambda x: x['deviation_factor'], reverse=True)
            
            return unusual_patterns[:20]  # Return top 20 unusual transactions
        
        except Exception as e:
            print(f"Error detecting unusual patterns: {e}")
            return []
    
    def identify_budget_overruns(self) -> Dict[str, Dict[str, float]]:
        """Identify categories where spending exceeds budget."""
        try:
            # Calculate monthly spending by category
            monthly_category_spending = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                monthly_category_spending[month_key][category] += transaction['amount']
            
            overruns = {}
            
            for month, categories in monthly_category_spending.items():
                month_overruns = {}
                
                for category, spent in categories.items():
                    budget = self.budgets.get(category, 0)
                    if budget > 0 and spent > budget:
                        overrun_amount = spent - budget
                        overrun_percentage = (overrun_amount / budget) * 100
                        
                        month_overruns[category] = {
                            'budget': budget,
                            'spent': round(spent, 2),
                            'overrun_amount': round(overrun_amount, 2),
                            'overrun_percentage': round(overrun_percentage, 2)
                        }
                
                if month_overruns:
                    overruns[month] = month_overruns
            
            return overruns
        
        except Exception as e:
            print(f"Error identifying budget overruns: {e}")
            return {}
    
    def generate_summary_insights(self, monthly_trends: Dict, category_breakdown: Dict, 
                                unusual_patterns: List, budget_overruns: Dict) -> Dict[str, Any]:
        """Generate summary insights from the analysis."""
        try:
            insights = {}
            
            # Monthly trend insights
            if monthly_trends:
                amounts = list(monthly_