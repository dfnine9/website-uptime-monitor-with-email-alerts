```python
#!/usr/bin/env python3
"""
Financial Data Analysis Module

This module provides comprehensive analysis of financial transaction data including:
- Spending pattern analysis across different categories
- Monthly trend identification and visualization
- Category percentage breakdowns
- Statistical anomaly detection for unusual spending behavior

The module uses statistical methods including z-score analysis and interquartile range
to identify outliers and unusual spending patterns. It processes transaction data
and generates insights about financial behavior over time.

Usage: python script.py
"""

import json
import statistics
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class FinancialAnalyzer:
    """Main class for analyzing financial transaction data."""
    
    def __init__(self):
        self.transactions = []
        self.categories = ['Groceries', 'Dining', 'Transportation', 'Entertainment', 
                          'Utilities', 'Shopping', 'Healthcare', 'Education', 'Other']
    
    def generate_sample_data(self, num_transactions: int = 500) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        transactions = []
        start_date = datetime.now() - timedelta(days=365)
        
        # Base amounts for different categories
        category_ranges = {
            'Groceries': (20, 150),
            'Dining': (15, 80),
            'Transportation': (5, 200),
            'Entertainment': (10, 100),
            'Utilities': (50, 300),
            'Shopping': (25, 500),
            'Healthcare': (30, 400),
            'Education': (100, 1000),
            'Other': (10, 200)
        }
        
        for i in range(num_transactions):
            # Random date within the last year
            days_ago = random.randint(0, 365)
            transaction_date = start_date + timedelta(days=days_ago)
            
            # Random category
            category = random.choice(self.categories)
            min_amt, max_amt = category_ranges[category]
            
            # Generate amount with some seasonal variation
            base_amount = random.uniform(min_amt, max_amt)
            
            # Add some outliers (5% chance of unusual spending)
            if random.random() < 0.05:
                base_amount *= random.uniform(2.0, 5.0)
            
            transaction = {
                'id': f'txn_{i:04d}',
                'date': transaction_date.strftime('%Y-%m-%d'),
                'amount': round(base_amount, 2),
                'category': category,
                'description': f'{category} purchase #{i}'
            }
            transactions.append(transaction)
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def load_data(self, transactions: List[Dict[str, Any]]) -> None:
        """Load transaction data into the analyzer."""
        self.transactions = transactions
    
    def calculate_category_percentages(self) -> Dict[str, float]:
        """Calculate spending percentage by category."""
        try:
            category_totals = defaultdict(float)
            total_spending = 0
            
            for transaction in self.transactions:
                amount = float(transaction['amount'])
                category = transaction['category']
                category_totals[category] += amount
                total_spending += amount
            
            if total_spending == 0:
                return {}
            
            percentages = {}
            for category, total in category_totals.items():
                percentages[category] = round((total / total_spending) * 100, 2)
            
            return percentages
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error calculating category percentages: {e}")
            return {}
    
    def analyze_monthly_trends(self) -> Dict[str, Dict[str, float]]:
        """Analyze spending trends by month."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                amount = float(transaction['amount'])
                category = transaction['category']
                
                monthly_data[month_key]['total'] += amount
                monthly_data[month_key][category] += amount
            
            return dict(monthly_data)
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error analyzing monthly trends: {e}")
            return {}
    
    def calculate_spending_statistics(self) -> Dict[str, float]:
        """Calculate basic spending statistics."""
        try:
            amounts = [float(t['amount']) for t in self.transactions]
            
            if not amounts:
                return {}
            
            stats = {
                'total_spending': round(sum(amounts), 2),
                'average_transaction': round(statistics.mean(amounts), 2),
                'median_transaction': round(statistics.median(amounts), 2),
                'min_transaction': round(min(amounts), 2),
                'max_transaction': round(max(amounts), 2)
            }
            
            if len(amounts) > 1:
                stats['std_deviation'] = round(statistics.stdev(amounts), 2)
            else:
                stats['std_deviation'] = 0.0
            
            return stats
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error calculating spending statistics: {e}")
            return {}
    
    def detect_anomalies_zscore(self, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect unusual spending using z-score analysis."""
        try:
            amounts = [float(t['amount']) for t in self.transactions]
            
            if len(amounts) < 2:
                return []
            
            mean_amount = statistics.mean(amounts)
            std_dev = statistics.stdev(amounts)
            
            if std_dev == 0:
                return []
            
            anomalies = []
            for transaction in self.transactions:
                amount = float(transaction['amount'])
                z_score = abs((amount - mean_amount) / std_dev)
                
                if z_score > threshold:
                    anomaly = transaction.copy()
                    anomaly['z_score'] = round(z_score, 2)
                    anomaly['deviation_type'] = 'high' if amount > mean_amount else 'low'
                    anomalies.append(anomaly)
            
            return sorted(anomalies, key=lambda x: x['z_score'], reverse=True)
            
        except (KeyError, ValueError, TypeError, ZeroDivisionError) as e:
            print(f"Error detecting anomalies with z-score: {e}")
            return []
    
    def detect_anomalies_iqr(self) -> List[Dict[str, Any]]:
        """Detect unusual spending using Interquartile Range method."""
        try:
            amounts = sorted([float(t['amount']) for t in self.transactions])
            
            if len(amounts) < 4:
                return []
            
            n = len(amounts)
            q1_idx = n // 4
            q3_idx = 3 * n // 4
            
            q1 = amounts[q1_idx]
            q3 = amounts[q3_idx]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            anomalies = []
            for transaction in self.transactions:
                amount = float(transaction['amount'])
                
                if amount < lower_bound or amount > upper_bound:
                    anomaly = transaction.copy()
                    anomaly['iqr_deviation'] = 'outlier'
                    anomaly['bounds'] = f'[{lower_bound:.2f}, {upper_bound:.2f}]'
                    anomalies.append(anomaly)
            
            return sorted(anomalies, key=