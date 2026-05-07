```python
#!/usr/bin/env python3
"""
Financial Data Analysis Module

This module provides comprehensive spending analysis capabilities including:
- Monthly category breakdowns and summaries
- Trend analysis across time periods
- Top expense identification and ranking
- Budget variance calculations and alerts
- Interactive visualization charts using ASCII art

The module generates synthetic financial data for demonstration purposes
and provides actionable insights for personal finance management.
"""

import json
import random
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar


class SpendingAnalyzer:
    """Main class for analyzing spending patterns and generating insights."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Groceries', 'Gas & Fuel', 'Home & Garden', 'Personal Care'
        ]
        self.budgets = {
            'Food & Dining': 800,
            'Transportation': 400,
            'Shopping': 300,
            'Entertainment': 200,
            'Bills & Utilities': 600,
            'Healthcare': 150,
            'Travel': 500,
            'Education': 100,
            'Groceries': 600,
            'Gas & Fuel': 200,
            'Home & Garden': 150,
            'Personal Care': 100
        }
    
    def generate_sample_data(self, months: int = 12) -> None:
        """Generate synthetic transaction data for analysis."""
        try:
            start_date = datetime.now() - timedelta(days=months * 30)
            
            for i in range(months * 50):  # ~50 transactions per month
                date = start_date + timedelta(days=random.randint(0, months * 30))
                category = random.choice(self.categories)
                
                # Category-specific amount ranges for realism
                amount_ranges = {
                    'Food & Dining': (15, 80),
                    'Transportation': (5, 120),
                    'Shopping': (20, 200),
                    'Entertainment': (10, 100),
                    'Bills & Utilities': (50, 300),
                    'Healthcare': (25, 400),
                    'Travel': (100, 800),
                    'Education': (30, 200),
                    'Groceries': (30, 150),
                    'Gas & Fuel': (25, 80),
                    'Home & Garden': (20, 180),
                    'Personal Care': (10, 60)
                }
                
                min_amt, max_amt = amount_ranges[category]
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                transaction = {
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': amount,
                    'category': category,
                    'description': f"{category} expense"
                }
                self.transactions.append(transaction)
            
            # Sort by date
            self.transactions.sort(key=lambda x: x['date'])
            print(f"✓ Generated {len(self.transactions)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def monthly_category_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending breakdown by category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_data[month_key][category] += amount
            
            return dict(monthly_data)
        
        except Exception as e:
            print(f"Error calculating monthly breakdown: {e}")
            return {}
    
    def trend_analysis(self) -> Dict[str, Any]:
        """Analyze spending trends over time."""
        try:
            monthly_totals = defaultdict(float)
            category_trends = defaultdict(list)
            
            monthly_breakdown = self.monthly_category_breakdown()
            
            for month, categories in monthly_breakdown.items():
                monthly_total = sum(categories.values())
                monthly_totals[month] = monthly_total
                
                for category, amount in categories.items():
                    category_trends[category].append(amount)
            
            # Calculate trend metrics
            total_amounts = list(monthly_totals.values())
            avg_monthly = statistics.mean(total_amounts) if total_amounts else 0
            
            trend_direction = "stable"
            if len(total_amounts) >= 2:
                recent_avg = statistics.mean(total_amounts[-3:]) if len(total_amounts) >= 3 else total_amounts[-1]
                older_avg = statistics.mean(total_amounts[:-3]) if len(total_amounts) >= 6 else statistics.mean(total_amounts[:-1])
                
                if recent_avg > older_avg * 1.1:
                    trend_direction = "increasing"
                elif recent_avg < older_avg * 0.9:
                    trend_direction = "decreasing"
            
            return {
                'monthly_totals': dict(monthly_totals),
                'average_monthly': round(avg_monthly, 2),
                'trend_direction': trend_direction,
                'category_trends': dict(category_trends)
            }
        
        except Exception as e:
            print(f"Error in trend analysis: {e}")
            return {}
    
    def top_expenses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Identify top expenses and spending patterns."""
        try:
            # Sort transactions by amount
            sorted_transactions = sorted(self.transactions, key=lambda x: x['amount'], reverse=True)
            top_transactions = sorted_transactions[:limit]
            
            # Category spending totals
            category_totals = defaultdict(float)
            for transaction in self.transactions:
                category_totals[transaction['category']] += transaction['amount']
            
            top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'top_transactions': top_transactions,
                'top_categories': top_categories[:limit]
            }
        
        except Exception as e:
            print(f"Error identifying top expenses: {e}")
            return {'top_transactions': [], 'top_categories': []}
    
    def budget_variance(self) -> Dict[str, Dict[str, float]]:
        """Calculate budget vs actual spending variance."""
        try:
            # Get current month data
            current_date = datetime.now()
            current_month = current_date.strftime('%Y-%m')
            
            monthly_breakdown = self.monthly_category_breakdown()
            current_spending = monthly_breakdown.get(current_month, {})
            
            variance_analysis = {}
            
            for category, budget_amount in self.budgets.items():
                actual_spending = current_spending.get(category, 0)
                variance = actual_spending - budget_amount
                variance_pct = (variance / budget_amount * 100) if budget_amount > 0 else 0
                
                status = "under budget"
                if variance > 0:
                    status = "over budget"
                elif abs(variance) < budget_amount * 0.05:  # Within 5%
                    status = "on track"
                
                variance_analysis[category] = {
                    'budget': budget_amount,
                    'actual': round(actual_spending, 2),
                    'variance': round(variance, 2),
                    'variance_pct': round(variance_pct, 1),
                    'status': status
                }
            
            return variance_analysis
        
        except Exception as e:
            print(f"Error calculating budget variance: {e}")
            return {}
    
    def create_ascii_chart(