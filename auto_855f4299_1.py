```python
"""
Personal Finance Data Analysis Module

This module provides comprehensive analysis of spending patterns including:
- Monthly spending averages per category
- Unusual expense detection using statistical outliers
- Spending trend analysis over time periods
- Category-wise spending distribution analysis

The module processes financial transaction data and generates insights
to help users understand their spending behavior and identify anomalies.
"""

import json
import statistics
import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import math


class SpendingAnalyzer:
    """Analyzes spending patterns and detects financial anomalies."""
    
    def __init__(self, transactions_data: List[Dict[str, Any]]):
        """
        Initialize with transaction data.
        
        Expected format:
        [
            {
                "date": "2024-01-15",
                "amount": 75.50,
                "category": "groceries",
                "description": "Whole Foods"
            }
        ]
        """
        self.transactions = transactions_data
        self.processed_data = self._process_transactions()
    
    def _process_transactions(self) -> Dict[str, Any]:
        """Process raw transaction data into analyzable format."""
        try:
            processed = {
                'by_month': defaultdict(lambda: defaultdict(list)),
                'by_category': defaultdict(list),
                'all_amounts': [],
                'date_range': {'start': None, 'end': None}
            }
            
            dates = []
            for transaction in self.transactions:
                date_str = transaction['date']
                amount = float(transaction['amount'])
                category = transaction['category'].lower()
                
                # Parse date
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date_obj)
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                
                # Organize data
                processed['by_month'][month_key][category].append(amount)
                processed['by_category'][category].append(amount)
                processed['all_amounts'].append(amount)
            
            if dates:
                processed['date_range']['start'] = min(dates)
                processed['date_range']['end'] = max(dates)
            
            return processed
            
        except Exception as e:
            print(f"Error processing transactions: {e}")
            return {}
    
    def calculate_monthly_averages(self) -> Dict[str, float]:
        """Calculate average monthly spending per category."""
        try:
            category_totals = defaultdict(list)
            
            for month_data in self.processed_data['by_month'].values():
                for category, amounts in month_data.items():
                    category_totals[category].append(sum(amounts))
            
            averages = {}
            for category, monthly_totals in category_totals.items():
                averages[category] = statistics.mean(monthly_totals)
            
            return averages
            
        except Exception as e:
            print(f"Error calculating monthly averages: {e}")
            return {}
    
    def detect_unusual_expenses(self, std_dev_threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect unusual expenses using statistical outliers."""
        try:
            unusual_expenses = []
            
            for category, amounts in self.processed_data['by_category'].items():
                if len(amounts) < 3:  # Need minimum data points
                    continue
                
                mean_amount = statistics.mean(amounts)
                std_dev = statistics.stdev(amounts)
                
                threshold = mean_amount + (std_dev_threshold * std_dev)
                
                for i, transaction in enumerate(self.transactions):
                    if (transaction['category'].lower() == category and 
                        float(transaction['amount']) > threshold):
                        unusual_expenses.append({
                            'transaction': transaction,
                            'category_mean': mean_amount,
                            'amount_deviation': float(transaction['amount']) - mean_amount,
                            'std_devs_above_mean': (float(transaction['amount']) - mean_amount) / std_dev
                        })
            
            return sorted(unusual_expenses, key=lambda x: x['std_devs_above_mean'], reverse=True)
            
        except Exception as e:
            print(f"Error detecting unusual expenses: {e}")
            return []
    
    def analyze_spending_trends(self) -> Dict[str, Any]:
        """Analyze spending trends over time."""
        try:
            trends = {
                'monthly_totals': {},
                'category_trends': {},
                'overall_trend': 'stable'
            }
            
            # Monthly totals
            for month, categories in self.processed_data['by_month'].items():
                month_total = sum(sum(amounts) for amounts in categories.values())
                trends['monthly_totals'][month] = month_total
            
            # Calculate overall trend
            if len(trends['monthly_totals']) >= 2:
                monthly_amounts = list(trends['monthly_totals'].values())
                first_half = monthly_amounts[:len(monthly_amounts)//2]
                second_half = monthly_amounts[len(monthly_amounts)//2:]
                
                if statistics.mean(second_half) > statistics.mean(first_half) * 1.1:
                    trends['overall_trend'] = 'increasing'
                elif statistics.mean(second_half) < statistics.mean(first_half) * 0.9:
                    trends['overall_trend'] = 'decreasing'
            
            # Category trends
            for category, amounts in self.processed_data['by_category'].items():
                if len(amounts) >= 3:
                    recent_avg = statistics.mean(amounts[-3:])
                    older_avg = statistics.mean(amounts[:-3]) if len(amounts) > 3 else statistics.mean(amounts)
                    
                    if recent_avg > older_avg * 1.2:
                        trends['category_trends'][category] = 'increasing'
                    elif recent_avg < older_avg * 0.8:
                        trends['category_trends'][category] = 'decreasing'
                    else:
                        trends['category_trends'][category] = 'stable'
            
            return trends
            
        except Exception as e:
            print(f"Error analyzing spending trends: {e}")
            return {}
    
    def generate_spending_summary(self) -> Dict[str, Any]:
        """Generate comprehensive spending summary."""
        try:
            total_spent = sum(self.processed_data['all_amounts'])
            num_transactions = len(self.transactions)
            avg_transaction = total_spent / num_transactions if num_transactions > 0 else 0
            
            category_totals = {}
            for category, amounts in self.processed_data['by_category'].items():
                category_totals[category] = sum(amounts)
            
            top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'total_spent': total_spent,
                'num_transactions': num_transactions,
                'avg_transaction_amount': avg_transaction,
                'top_spending_categories': top_categories,
                'date_range': self.processed_data['date_range'],
                'num_categories': len(category_totals)
            }
            
        except Exception as e:
            print(f"Error generating spending summary: {e}")
            return {}


def generate_sample_data() -> List[Dict[str, Any]]:
    """Generate sample transaction data for demonstration."""
    import random
    
    categories = ['groceries', 'restaurants', 'gas', 'entertainment', 'utilities', 'shopping', 'healthcare']
    transactions = []
    
    # Generate 3 months of sample data
    for month in range(1, 4):
        for day in range(1, 29):
            if random.random() < 0.7:  # 70% chance of transaction per day
                num_transactions = random.randint(1, 3)
                for _ in range(num_transactions):
                    category = random.choice(categories)