```python
"""
Financial Transaction Analysis Module

This module analyzes spending patterns from categorized transaction data.
It detects trends, calculates category averages, identifies spending spikes,
and generates statistical insights.

Features:
- Trend detection across multiple months
- Category-wise spending analysis
- Spike detection using statistical thresholds
- Monthly comparison and variance analysis
- Statistical summaries and insights

Usage: python script.py
"""

import json
import statistics
import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class SpendingAnalyzer:
    def __init__(self):
        self.transactions = []
        self.categories = defaultdict(list)
        self.monthly_data = defaultdict(lambda: defaultdict(float))
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for analysis."""
        import random
        
        categories = ['groceries', 'dining', 'entertainment', 'utilities', 'transport', 'shopping', 'healthcare']
        months = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
        
        for month in months:
            for _ in range(random.randint(15, 30)):  # 15-30 transactions per month
                category = random.choice(categories)
                base_amount = {
                    'groceries': 50, 'dining': 30, 'entertainment': 25,
                    'utilities': 100, 'transport': 40, 'shopping': 60, 'healthcare': 80
                }
                
                # Add some variability and occasional spikes
                amount = base_amount[category] * random.uniform(0.5, 2.0)
                if random.random() < 0.05:  # 5% chance of spike
                    amount *= random.uniform(2.0, 4.0)
                
                transaction = {
                    'date': f"{month}-{random.randint(1, 28):02d}",
                    'amount': round(amount, 2),
                    'category': category,
                    'description': f"{category.title()} purchase"
                }
                self.transactions.append(transaction)
    
    def categorize_transactions(self) -> None:
        """Organize transactions by category and month."""
        try:
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                date = transaction['date']
                month = date[:7]  # Extract YYYY-MM
                
                self.categories[category].append(amount)
                self.monthly_data[month][category] += amount
                
        except KeyError as e:
            print(f"Error processing transaction: Missing key {e}")
        except Exception as e:
            print(f"Unexpected error in categorization: {e}")
    
    def calculate_category_averages(self) -> Dict[str, Dict[str, float]]:
        """Calculate average spending per category across all months."""
        averages = {}
        
        try:
            for category, amounts in self.categories.items():
                if amounts:
                    avg_amount = statistics.mean(amounts)
                    median_amount = statistics.median(amounts)
                    std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                    
                    averages[category] = {
                        'mean': round(avg_amount, 2),
                        'median': round(median_amount, 2),
                        'std_dev': round(std_dev, 2),
                        'total_transactions': len(amounts),
                        'total_spent': round(sum(amounts), 2)
                    }
                    
        except statistics.StatisticsError as e:
            print(f"Statistics calculation error: {e}")
        except Exception as e:
            print(f"Error calculating averages: {e}")
            
        return averages
    
    def detect_spending_trends(self) -> Dict[str, Any]:
        """Analyze spending trends across months."""
        trends = {}
        
        try:
            sorted_months = sorted(self.monthly_data.keys())
            
            for category in self.categories.keys():
                monthly_totals = [self.monthly_data[month].get(category, 0) for month in sorted_months]
                
                if len(monthly_totals) > 1:
                    # Calculate trend (simple linear regression slope)
                    n = len(monthly_totals)
                    x_vals = list(range(n))
                    x_mean = statistics.mean(x_vals)
                    y_mean = statistics.mean(monthly_totals)
                    
                    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, monthly_totals))
                    denominator = sum((x - x_mean) ** 2 for x in x_vals)
                    
                    slope = numerator / denominator if denominator != 0 else 0
                    
                    trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                    
                    trends[category] = {
                        'slope': round(slope, 2),
                        'direction': trend_direction,
                        'monthly_totals': [round(x, 2) for x in monthly_totals],
                        'months': sorted_months
                    }
                    
        except Exception as e:
            print(f"Error detecting trends: {e}")
            
        return trends
    
    def identify_spending_spikes(self, threshold_multiplier: float = 2.0) -> Dict[str, List[Dict]]:
        """Identify spending spikes using statistical thresholds."""
        spikes = defaultdict(list)
        
        try:
            for category, amounts in self.categories.items():
                if len(amounts) > 1:
                    mean_amount = statistics.mean(amounts)
                    std_dev = statistics.stdev(amounts)
                    threshold = mean_amount + (threshold_multiplier * std_dev)
                    
                    # Find transactions that exceed threshold
                    for transaction in self.transactions:
                        if (transaction['category'] == category and 
                            transaction['amount'] > threshold):
                            spike_info = {
                                'date': transaction['date'],
                                'amount': transaction['amount'],
                                'threshold': round(threshold, 2),
                                'deviation': round(transaction['amount'] - mean_amount, 2),
                                'description': transaction['description']
                            }
                            spikes[category].append(spike_info)
                            
        except Exception as e:
            print(f"Error identifying spikes: {e}")
            
        return dict(spikes)
    
    def generate_monthly_comparison(self) -> Dict[str, Any]:
        """Generate month-over-month comparison statistics."""
        comparison = {}
        
        try:
            sorted_months = sorted(self.monthly_data.keys())
            
            if len(sorted_months) < 2:
                return comparison
                
            for i in range(1, len(sorted_months)):
                current_month = sorted_months[i]
                previous_month = sorted_months[i-1]
                
                current_total = sum(self.monthly_data[current_month].values())
                previous_total = sum(self.monthly_data[previous_month].values())
                
                if previous_total > 0:
                    change_percent = ((current_total - previous_total) / previous_total) * 100
                else:
                    change_percent = 0
                
                comparison[f"{previous_month}_to_{current_month}"] = {
                    'previous_total': round(previous_total, 2),
                    'current_total': round(current_total, 2),
                    'change_amount': round(current_total - previous_total, 2),
                    'change_percent': round(change_percent, 2)
                }
                
        except Exception as e:
            print(f"Error in monthly comparison: {e}")
            
        return comparison
    
    def generate_insights(self) -> Dict[str, Any]:
        """Generate high-level insights from the analysis