```python
#!/usr/bin/env python3
"""
Transaction Spending Pattern Analyzer

This module analyzes categorized transaction data to provide comprehensive spending insights:
- Monthly spending totals by category
- Percentage breakdowns of spending patterns
- Trend analysis over time periods
- Detection of unusual spending spikes (>2 standard deviations from mean)

The script generates sample transaction data and performs statistical analysis
to identify patterns, trends, and anomalies in spending behavior.

Requirements: Python 3.6+ (uses only standard library)
Usage: python script.py
"""

import json
import statistics
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import calendar


class TransactionAnalyzer:
    """Analyzes transaction data for spending patterns and anomalies."""
    
    def __init__(self):
        self.transactions = []
        self.categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                          'Healthcare', 'Shopping', 'Bills', 'Travel', 'Education', 'Other']
    
    def generate_sample_data(self, num_transactions: int = 500) -> List[Dict[str, Any]]:
        """Generate sample transaction data for analysis."""
        try:
            transactions = []
            start_date = datetime.now() - timedelta(days=365)
            
            for _ in range(num_transactions):
                # Generate realistic spending amounts by category
                category = random.choice(self.categories)
                base_amounts = {
                    'Food': (20, 150), 'Transportation': (10, 200),
                    'Entertainment': (15, 300), 'Utilities': (50, 400),
                    'Healthcare': (25, 500), 'Shopping': (30, 800),
                    'Bills': (100, 1500), 'Travel': (200, 2000),
                    'Education': (50, 1000), 'Other': (10, 200)
                }
                
                min_amt, max_amt = base_amounts[category]
                amount = round(random.uniform(min_amt, max_amt), 2)
                
                # Occasionally add spending spikes
                if random.random() < 0.05:  # 5% chance of spike
                    amount *= random.uniform(2.5, 4.0)
                
                transaction_date = start_date + timedelta(days=random.randint(0, 365))
                
                transactions.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'amount': round(amount, 2),
                    'category': category,
                    'description': f'{category} transaction'
                })
            
            return sorted(transactions, key=lambda x: x['date'])
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return []
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Load transaction data for analysis."""
        try:
            self.transactions = transactions
            print(f"Loaded {len(transactions)} transactions for analysis")
        except Exception as e:
            print(f"Error loading transactions: {e}")
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        try:
            monthly_data = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                monthly_data[month_key][category] += amount
            
            return dict(monthly_data)
            
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def calculate_category_percentages(self) -> Dict[str, float]:
        """Calculate percentage breakdown of spending by category."""
        try:
            category_totals = defaultdict(float)
            total_spending = 0
            
            for transaction in self.transactions:
                amount = float(transaction['amount'])
                category_totals[transaction['category']] += amount
                total_spending += amount
            
            if total_spending == 0:
                return {}
            
            percentages = {
                category: round((amount / total_spending) * 100, 2)
                for category, amount in category_totals.items()
            }
            
            return percentages
            
        except Exception as e:
            print(f"Error calculating category percentages: {e}")
            return {}
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze spending trends over time."""
        try:
            monthly_totals = self.calculate_monthly_totals()
            if not monthly_totals:
                return {}
            
            # Calculate month-over-month changes
            sorted_months = sorted(monthly_totals.keys())
            trends = {}
            
            for category in self.categories:
                monthly_amounts = []
                for month in sorted_months:
                    amount = monthly_totals[month].get(category, 0)
                    monthly_amounts.append(amount)
                
                if len(monthly_amounts) < 2:
                    continue
                
                # Calculate trend metrics
                avg_spending = statistics.mean(monthly_amounts)
                if len(monthly_amounts) > 1:
                    std_dev = statistics.stdev(monthly_amounts)
                else:
                    std_dev = 0
                
                # Simple trend direction (comparing first half vs second half)
                mid_point = len(monthly_amounts) // 2
                first_half_avg = statistics.mean(monthly_amounts[:mid_point]) if mid_point > 0 else 0
                second_half_avg = statistics.mean(monthly_amounts[mid_point:])
                
                trend_direction = "increasing" if second_half_avg > first_half_avg else "decreasing"
                if abs(second_half_avg - first_half_avg) < (avg_spending * 0.1):
                    trend_direction = "stable"
                
                trends[category] = {
                    'average_monthly': round(avg_spending, 2),
                    'std_deviation': round(std_dev, 2),
                    'trend_direction': trend_direction,
                    'change_percentage': round(((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0, 2)
                }
            
            return trends
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {}
    
    def identify_spending_spikes(self, threshold_multiplier: float = 2.0) -> List[Dict[str, Any]]:
        """Identify unusual spending spikes (transactions above threshold * std deviation)."""
        try:
            # Calculate statistics by category
            category_stats = defaultdict(list)
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = float(transaction['amount'])
                category_stats[category].append(amount)
            
            spikes = []
            
            for category, amounts in category_stats.items():
                if len(amounts) < 3:  # Need sufficient data
                    continue
                
                mean_amount = statistics.mean(amounts)
                std_dev = statistics.stdev(amounts)
                threshold = mean_amount + (threshold_multiplier * std_dev)
                
                # Find transactions above threshold
                for transaction in self.transactions:
                    if (transaction['category'] == category and 
                        float(transaction['amount']) > threshold):
                        
                        spike_info = {
                            'date': transaction['date'],
                            'category': category,
                            'amount': transaction['amount'],
                            'description': transaction['description'],
                            'category_average': round(mean_amount, 2),
                            'spike_multiplier': round(transaction['amount'] / mean_amount, 2),
                            'threshold_used': round(threshold, 2)
                        }