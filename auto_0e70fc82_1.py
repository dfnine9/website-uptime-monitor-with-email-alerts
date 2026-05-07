```python
"""
Financial Transaction Analysis Module

This module processes categorized financial transactions to identify spending patterns,
calculate monthly totals per category, and detect anomalies in spending behavior.

Features:
- Monthly spending analysis by category
- Anomaly detection using statistical methods
- Spending pattern identification
- Comprehensive error handling

Dependencies: Python standard library only
Usage: python script.py
"""

import json
import statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import random
import math


class TransactionAnalyzer:
    """Analyzes financial transactions for patterns and anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_stats = defaultdict(list)
    
    def generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Utilities', 'Healthcare']
        transactions = []
        
        # Generate 6 months of data
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(200):
            date = base_date + timedelta(days=random.randint(0, 180))
            category = random.choice(categories)
            
            # Create realistic spending patterns
            base_amounts = {
                'Food': (20, 150),
                'Transportation': (10, 80),
                'Entertainment': (15, 200),
                'Shopping': (30, 300),
                'Utilities': (50, 200),
                'Healthcare': (25, 500)
            }
            
            min_amt, max_amt = base_amounts[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Add some anomalies (5% chance of unusually high spending)
            if random.random() < 0.05:
                amount *= random.uniform(3, 8)
                amount = round(amount, 2)
            
            transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': amount,
                'description': f'{category} purchase #{i+1}'
            })
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Load and validate transaction data."""
        try:
            self.transactions = []
            for trans in transactions:
                # Validate required fields
                if not all(key in trans for key in ['date', 'category', 'amount']):
                    raise ValueError(f"Missing required fields in transaction: {trans}")
                
                # Parse and validate date
                try:
                    datetime.strptime(trans['date'], '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f"Invalid date format: {trans['date']}")
                
                # Validate amount
                if not isinstance(trans['amount'], (int, float)) or trans['amount'] < 0:
                    raise ValueError(f"Invalid amount: {trans['amount']}")
                
                self.transactions.append(trans)
            
            print(f"✓ Loaded {len(self.transactions)} transactions")
            
        except Exception as e:
            print(f"✗ Error loading transactions: {e}")
            raise
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        try:
            self.monthly_totals.clear()
            
            for trans in self.transactions:
                date_obj = datetime.strptime(trans['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = trans['category']
                amount = float(trans['amount'])
                
                self.monthly_totals[month_key][category] += amount
            
            return dict(self.monthly_totals)
            
        except Exception as e:
            print(f"✗ Error calculating monthly totals: {e}")
            return {}
    
    def identify_spending_patterns(self) -> Dict[str, Any]:
        """Identify spending patterns and trends."""
        try:
            patterns = {
                'top_categories': {},
                'monthly_trends': {},
                'category_consistency': {}
            }
            
            # Calculate total spending by category
            category_totals = defaultdict(float)
            for trans in self.transactions:
                category_totals[trans['category']] += trans['amount']
            
            # Top spending categories
            patterns['top_categories'] = dict(sorted(
                category_totals.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            # Monthly spending trends
            monthly_totals = {}
            for month, categories in self.monthly_totals.items():
                monthly_totals[month] = sum(categories.values())
            
            patterns['monthly_trends'] = dict(sorted(monthly_totals.items()))
            
            # Category consistency (coefficient of variation)
            for category in category_totals.keys():
                monthly_amounts = []
                for month_data in self.monthly_totals.values():
                    monthly_amounts.append(month_data.get(category, 0))
                
                if len(monthly_amounts) > 1 and sum(monthly_amounts) > 0:
                    mean_amt = statistics.mean(monthly_amounts)
                    if mean_amt > 0:
                        std_dev = statistics.stdev(monthly_amounts)
                        cv = std_dev / mean_amt
                        patterns['category_consistency'][category] = {
                            'coefficient_of_variation': round(cv, 3),
                            'consistency': 'High' if cv < 0.3 else 'Medium' if cv < 0.7 else 'Low'
                        }
            
            return patterns
            
        except Exception as e:
            print(f"✗ Error identifying patterns: {e}")
            return {}
    
    def detect_anomalies(self, threshold_multiplier: float = 2.5) -> List[Dict[str, Any]]:
        """Detect anomalous transactions using statistical methods."""
        try:
            anomalies = []
            
            # Group transactions by category for analysis
            category_amounts = defaultdict(list)
            for trans in self.transactions:
                category_amounts[trans['category']].append(trans['amount'])
            
            # Calculate statistics for each category
            category_stats = {}
            for category, amounts in category_amounts.items():
                if len(amounts) >= 3:  # Need at least 3 transactions for meaningful stats
                    mean_amt = statistics.mean(amounts)
                    std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                    category_stats[category] = {
                        'mean': mean_amt,
                        'std_dev': std_dev,
                        'threshold': mean_amt + (threshold_multiplier * std_dev)
                    }
            
            # Identify anomalous transactions
            for trans in self.transactions:
                category = trans['category']
                amount = trans['amount']
                
                if category in category_stats:
                    stats = category_stats[category]
                    if amount > stats['threshold']:
                        anomaly_score = (amount - stats['mean']) / stats['std_dev'] if stats['std_dev'] > 0 else 0
                        anomalies.append({
                            'transaction': trans,
                            'anomaly_score': round(anomaly_score, 2),
                            'threshold': round(stats['threshold'], 2),
                            'category_mean': round(stats['mean'], 2)
                        })
            
            return sorted(anomalies, key=lambda x: x['anomaly_score'], reverse=True)
            
        except Exception as e:
            print(f"✗ Error detecting anomalies: {e}")
            return []
    
    def generate_summary_report(self) -> None:
        """Generate and print comprehensive analysis report