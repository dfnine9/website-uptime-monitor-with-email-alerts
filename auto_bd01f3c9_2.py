```python
#!/usr/bin/env python3
"""
Financial Spending Analysis Engine

This module provides a comprehensive analysis engine for financial spending data.
It calculates spending patterns, identifies trends over time, detects anomalies,
and computes category-wise statistics for monthly and quarterly periods.

Features:
- Spending pattern analysis with trend detection
- Anomaly detection using statistical methods (Z-score and IQR)
- Category-wise spending breakdowns
- Monthly and quarterly aggregations
- Moving averages and growth rate calculations
- Statistical summaries and insights

The engine uses synthetic data for demonstration but can be easily adapted
to work with real financial data sources.
"""

import json
import statistics
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random
import math


class SpendingAnalysisEngine:
    """Main engine for analyzing spending patterns and detecting trends."""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Home & Garden', 'Personal Care', 'Insurance', 'Investments'
        ]
    
    def generate_sample_data(self, num_transactions: int = 1000) -> None:
        """Generate sample transaction data for analysis."""
        try:
            start_date = datetime.date(2023, 1, 1)
            end_date = datetime.date(2024, 12, 31)
            date_range = (end_date - start_date).days
            
            for _ in range(num_transactions):
                random_days = random.randint(0, date_range)
                transaction_date = start_date + datetime.timedelta(days=random_days)
                
                category = random.choice(self.categories)
                
                # Generate realistic amounts based on category
                base_amounts = {
                    'Food & Dining': (15, 150),
                    'Transportation': (5, 200),
                    'Shopping': (20, 500),
                    'Entertainment': (10, 300),
                    'Bills & Utilities': (50, 400),
                    'Healthcare': (25, 800),
                    'Travel': (100, 2000),
                    'Education': (50, 1500),
                    'Home & Garden': (30, 600),
                    'Personal Care': (15, 200),
                    'Insurance': (100, 1000),
                    'Investments': (100, 5000)
                }
                
                min_amt, max_amt = base_amounts.get(category, (10, 200))
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                transaction = {
                    'date': transaction_date.isoformat(),
                    'amount': amount,
                    'category': category,
                    'description': f"{category} transaction"
                }
                
                self.transactions.append(transaction)
            
            # Sort by date
            self.transactions.sort(key=lambda x: x['date'])
            print(f"Generated {len(self.transactions)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
    
    def calculate_spending_patterns(self) -> Dict[str, Any]:
        """Calculate overall spending patterns and statistics."""
        try:
            if not self.transactions:
                return {}
            
            amounts = [t['amount'] for t in self.transactions]
            
            patterns = {
                'total_transactions': len(self.transactions),
                'total_amount': sum(amounts),
                'average_transaction': statistics.mean(amounts),
                'median_transaction': statistics.median(amounts),
                'min_transaction': min(amounts),
                'max_transaction': max(amounts),
                'std_deviation': statistics.stdev(amounts) if len(amounts) > 1 else 0
            }
            
            return patterns
            
        except Exception as e:
            print(f"Error calculating spending patterns: {e}")
            return {}
    
    def identify_trends_over_time(self) -> Dict[str, Any]:
        """Identify spending trends over time with monthly analysis."""
        try:
            monthly_spending = defaultdict(float)
            monthly_counts = defaultdict(int)
            
            for transaction in self.transactions:
                date_obj = datetime.datetime.fromisoformat(transaction['date'])
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                monthly_spending[month_key] += transaction['amount']
                monthly_counts[month_key] += 1
            
            # Sort months chronologically
            sorted_months = sorted(monthly_spending.keys())
            monthly_amounts = [monthly_spending[month] for month in sorted_months]
            
            # Calculate moving averages (3-month)
            moving_averages = []
            for i in range(len(monthly_amounts)):
                if i >= 2:
                    avg = sum(monthly_amounts[i-2:i+1]) / 3
                    moving_averages.append(round(avg, 2))
                else:
                    moving_averages.append(monthly_amounts[i])
            
            # Calculate month-over-month growth rates
            growth_rates = []
            for i in range(1, len(monthly_amounts)):
                if monthly_amounts[i-1] != 0:
                    growth = ((monthly_amounts[i] - monthly_amounts[i-1]) / monthly_amounts[i-1]) * 100
                    growth_rates.append(round(growth, 2))
                else:
                    growth_rates.append(0)
            
            trends = {
                'monthly_spending': dict(zip(sorted_months, monthly_amounts)),
                'monthly_transaction_counts': dict(zip(sorted_months, [monthly_counts[m] for m in sorted_months])),
                'moving_averages': dict(zip(sorted_months, moving_averages)),
                'growth_rates': dict(zip(sorted_months[1:], growth_rates)),
                'overall_trend': 'increasing' if len(growth_rates) > 0 and statistics.mean(growth_rates) > 0 else 'decreasing'
            }
            
            return trends
            
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {}
    
    def detect_anomalies(self, method: str = 'zscore') -> List[Dict[str, Any]]:
        """Detect anomalous transactions using statistical methods."""
        try:
            if not self.transactions:
                return []
            
            amounts = [t['amount'] for t in self.transactions]
            anomalies = []
            
            if method == 'zscore':
                mean_amount = statistics.mean(amounts)
                std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                if std_amount > 0:
                    for transaction in self.transactions:
                        z_score = abs(transaction['amount'] - mean_amount) / std_amount
                        if z_score > 2.5:  # Anomaly threshold
                            anomalies.append({
                                'transaction': transaction,
                                'z_score': round(z_score, 3),
                                'type': 'high' if transaction['amount'] > mean_amount else 'low'
                            })
            
            elif method == 'iqr':
                q1 = statistics.quantiles(amounts, n=4)[0]
                q3 = statistics.quantiles(amounts, n=4)[2]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                for transaction in self.transactions:
                    if transaction['amount'] < lower_bound or transaction['amount'] > upper_bound:
                        anomalies.append({
                            'transaction': transaction,
                            'bounds': {'lower': round(lower_bound, 2), 'upper': round(upper_bound, 2)},
                            'type': 'high' if transaction