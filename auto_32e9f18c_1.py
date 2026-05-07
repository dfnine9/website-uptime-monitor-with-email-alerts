```python
#!/usr/bin/env python3
"""
Personal Finance Data Analysis Module

This module provides comprehensive financial data analysis capabilities including:
- Monthly spending totals by category
- Spending trend analysis over time
- Unusual transaction pattern detection
- Budget overrun alerts

The module generates sample transaction data and performs various analyses
to help users understand their spending patterns and identify potential issues.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class FinancialAnalyzer:
    """Core financial data analysis engine."""
    
    def __init__(self):
        self.transactions = []
        self.budgets = {}
        
    def load_sample_data(self):
        """Generate realistic sample transaction data for demonstration."""
        categories = [
            'Groceries', 'Utilities', 'Transportation', 'Entertainment',
            'Dining Out', 'Healthcare', 'Shopping', 'Insurance',
            'Gas', 'Subscriptions', 'Home Improvement', 'Travel'
        ]
        
        # Generate 6 months of sample data
        start_date = datetime.now() - timedelta(days=180)
        
        for i in range(300):  # 300 transactions over 6 months
            transaction_date = start_date + timedelta(days=random.randint(0, 180))
            category = random.choice(categories)
            
            # Create realistic amounts based on category
            amount_ranges = {
                'Groceries': (30, 150),
                'Utilities': (80, 250),
                'Transportation': (20, 100),
                'Entertainment': (15, 80),
                'Dining Out': (25, 120),
                'Healthcare': (50, 300),
                'Shopping': (20, 200),
                'Insurance': (100, 400),
                'Gas': (35, 85),
                'Subscriptions': (10, 50),
                'Home Improvement': (50, 500),
                'Travel': (100, 1000)
            }
            
            min_amt, max_amt = amount_ranges[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Occasionally create unusual transactions for anomaly detection
            if random.random() < 0.05:  # 5% chance of unusual transaction
                amount *= random.uniform(2, 5)  # 2-5x normal amount
            
            transaction = {
                'date': transaction_date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': amount,
                'description': f'{category} purchase'
            }
            
            self.transactions.append(transaction)
        
        # Set sample budgets
        self.budgets = {
            'Groceries': 500,
            'Utilities': 200,
            'Transportation': 300,
            'Entertainment': 200,
            'Dining Out': 300,
            'Healthcare': 250,
            'Shopping': 400,
            'Insurance': 350,
            'Gas': 150,
            'Subscriptions': 100,
            'Home Improvement': 200,
            'Travel': 500
        }
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
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
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def identify_spending_trends(self, monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """Identify spending trends over time for each category."""
        try:
            trends = {}
            
            for category in set(cat for month in monthly_data.values() for cat in month.keys()):
                monthly_amounts = []
                months = sorted(monthly_data.keys())
                
                for month in months:
                    amount = monthly_data[month].get(category, 0)
                    monthly_amounts.append(amount)
                
                if len(monthly_amounts) > 1:
                    # Calculate trend metrics
                    avg_amount = statistics.mean(monthly_amounts)
                    trend_direction = "Increasing" if monthly_amounts[-1] > monthly_amounts[0] else "Decreasing"
                    
                    # Calculate percentage change
                    if monthly_amounts[0] != 0:
                        pct_change = ((monthly_amounts[-1] - monthly_amounts[0]) / monthly_amounts[0]) * 100
                    else:
                        pct_change = 0
                    
                    # Calculate volatility (standard deviation)
                    volatility = statistics.stdev(monthly_amounts) if len(monthly_amounts) > 1 else 0
                    
                    trends[category] = {
                        'average_monthly': round(avg_amount, 2),
                        'trend_direction': trend_direction,
                        'percentage_change': round(pct_change, 1),
                        'volatility': round(volatility, 2),
                        'monthly_amounts': monthly_amounts
                    }
            
            return trends
        
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {}
    
    def detect_unusual_patterns(self) -> List[Dict[str, Any]]:
        """Detect unusual transaction patterns and anomalies."""
        try:
            anomalies = []
            
            # Group transactions by category for analysis
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction['category']].append(transaction['amount'])
            
            # Detect outliers using IQR method
            for category, amounts in category_amounts.items():
                if len(amounts) < 10:  # Need sufficient data
                    continue
                
                amounts.sort()
                q1 = amounts[len(amounts) // 4]
                q3 = amounts[3 * len(amounts) // 4]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Find transactions outside normal range
                for transaction in self.transactions:
                    if (transaction['category'] == category and 
                        (transaction['amount'] > upper_bound or transaction['amount'] < lower_bound)):
                        
                        anomalies.append({
                            'date': transaction['date'],
                            'category': category,
                            'amount': transaction['amount'],
                            'description': transaction['description'],
                            'reason': f'Amount {transaction["amount"]:.2f} is outside normal range ({lower_bound:.2f}-{upper_bound:.2f})',
                            'severity': 'High' if transaction['amount'] > upper_bound * 1.5 else 'Medium'
                        })
            
            # Detect frequency anomalies
            daily_counts = Counter()
            for transaction in self.transactions:
                daily_counts[transaction['date']] += 1
            
            avg_daily_transactions = statistics.mean(daily_counts.values())
            threshold = avg_daily_transactions * 2
            
            for date, count in daily_counts.items():
                if count > threshold:
                    anomalies.append({
                        'date': date,
                        'category': 'Multiple',
                        'amount': 0,
                        'description': f'Unusually high transaction frequency: {count} transactions',
                        'reason': f'Daily transaction count {count} exceeds threshold of {threshold:.1f}',
                        'severity': 'Medium'
                    })
            
            return sorted(anomalies, key=lambda x