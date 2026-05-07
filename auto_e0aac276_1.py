```python
#!/usr/bin/env python3
"""
Personal Finance Data Analysis Module

This module provides comprehensive financial data analysis capabilities including:
- Monthly spending totals by category calculation
- Spending trend analysis over time
- Budget anomaly and unusual transaction detection
- Statistical analysis of spending patterns

The module uses synthetic transaction data for demonstration purposes and includes
robust error handling, data validation, and clear output formatting.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class FinanceAnalyzer:
    """Main class for financial data analysis and anomaly detection."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_trends = defaultdict(list)
        
    def generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate realistic sample transaction data for analysis."""
        try:
            categories = [
                'Groceries', 'Dining', 'Transportation', 'Entertainment',
                'Utilities', 'Shopping', 'Healthcare', 'Insurance',
                'Subscriptions', 'Gas', 'Coffee', 'Travel'
            ]
            
            transactions = []
            start_date = datetime.now() - timedelta(days=365)
            
            # Generate regular transactions
            for i in range(500):
                date = start_date + timedelta(days=random.randint(0, 365))
                category = random.choice(categories)
                
                # Category-specific amount ranges
                amount_ranges = {
                    'Groceries': (50, 200),
                    'Dining': (15, 80),
                    'Transportation': (5, 50),
                    'Entertainment': (20, 150),
                    'Utilities': (80, 300),
                    'Shopping': (25, 500),
                    'Healthcare': (30, 400),
                    'Insurance': (100, 600),
                    'Subscriptions': (10, 50),
                    'Gas': (40, 80),
                    'Coffee': (3, 15),
                    'Travel': (200, 2000)
                }
                
                min_amt, max_amt = amount_ranges.get(category, (10, 100))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                # Add some anomalous transactions (5% chance)
                if random.random() < 0.05:
                    amount *= random.uniform(3, 8)  # 3-8x normal amount
                
                transaction = {
                    'id': f'tx_{i:04d}',
                    'date': date.strftime('%Y-%m-%d'),
                    'category': category,
                    'amount': round(amount, 2),
                    'description': f'{category} purchase #{i}'
                }
                transactions.append(transaction)
            
            return sorted(transactions, key=lambda x: x['date'])
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def load_data(self) -> bool:
        """Load transaction data (using generated sample data)."""
        try:
            self.transactions = self.generate_sample_data()
            if not self.transactions:
                raise ValueError("No transaction data available")
            
            print(f"Loaded {len(self.transactions)} transactions")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        try:
            monthly_totals = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                monthly_totals[month_key][category] += amount
                monthly_totals[month_key]['TOTAL'] += amount
            
            self.monthly_totals = monthly_totals
            return dict(monthly_totals)
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def analyze_spending_trends(self) -> Dict[str, Dict[str, Any]]:
        """Analyze spending trends over time for each category."""
        try:
            trends = {}
            
            # Get all categories
            all_categories = set()
            for month_data in self.monthly_totals.values():
                all_categories.update(month_data.keys())
            all_categories.discard('TOTAL')
            
            for category in all_categories:
                monthly_amounts = []
                months = sorted(self.monthly_totals.keys())
                
                for month in months:
                    amount = self.monthly_totals[month].get(category, 0)
                    monthly_amounts.append(amount)
                
                if len(monthly_amounts) >= 2:
                    # Calculate trend statistics
                    avg_spending = statistics.mean(monthly_amounts)
                    median_spending = statistics.median(monthly_amounts)
                    std_dev = statistics.stdev(monthly_amounts) if len(monthly_amounts) > 1 else 0
                    
                    # Calculate trend direction
                    recent_3_months = monthly_amounts[-3:] if len(monthly_amounts) >= 3 else monthly_amounts
                    older_3_months = monthly_amounts[:3] if len(monthly_amounts) >= 6 else monthly_amounts[:-3]
                    
                    if older_3_months:
                        recent_avg = statistics.mean(recent_3_months)
                        older_avg = statistics.mean(older_3_months)
                        trend_direction = "Increasing" if recent_avg > older_avg * 1.1 else "Decreasing" if recent_avg < older_avg * 0.9 else "Stable"
                        trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
                    else:
                        trend_direction = "Insufficient data"
                        trend_percentage = 0
                    
                    trends[category] = {
                        'average_monthly': round(avg_spending, 2),
                        'median_monthly': round(median_spending, 2),
                        'std_deviation': round(std_dev, 2),
                        'trend_direction': trend_direction,
                        'trend_percentage': round(trend_percentage, 1),
                        'months_analyzed': len(monthly_amounts),
                        'total_spent': round(sum(monthly_amounts), 2)
                    }
            
            return trends
            
        except Exception as e:
            print(f"Error analyzing spending trends: {e}")
            return {}
    
    def detect_anomalies(self, z_threshold: float = 2.5) -> List[Dict[str, Any]]:
        """Detect budget anomalies and unusual transactions using statistical analysis."""
        try:
            anomalies = []
            
            # Group transactions by category for analysis
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction['category']].append(transaction['amount'])
            
            # Calculate thresholds for each category
            category_thresholds = {}
            for category, amounts in category_amounts.items():
                if len(amounts) >= 5:  # Need sufficient data
                    mean_amount = statistics.mean(amounts)
                    std_amount = statistics.stdev(amounts)
                    threshold = mean_amount + (z_threshold * std_amount)
                    category_thresholds[category] = {
                        'mean': mean_amount,
                        'std': std_amount,
                        'threshold': threshold
                    }
            
            # Check each transaction for anomalies
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount