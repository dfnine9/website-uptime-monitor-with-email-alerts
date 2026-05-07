```python
#!/usr/bin/env python3
"""
Trend Analysis Component for Financial Data

This module provides comprehensive spending pattern analysis including:
- Monthly spending trend calculation
- Category-wise spending increase/decrease identification
- Unusual transaction and spending spike detection

The component uses statistical methods to identify anomalies and trends
in financial transaction data. It calculates rolling averages, standard
deviations, and percentage changes to provide actionable insights.

Usage:
    python script.py

Dependencies:
    - Standard library modules: json, datetime, statistics, random
    - No external dependencies required
"""

import json
import datetime
import statistics
import random
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter


class TrendAnalyzer:
    """Financial trend analysis component for spending patterns."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(lambda: defaultdict(list))
        self.category_trends = {}
        
    def generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        categories = ['Groceries', 'Gas', 'Dining', 'Shopping', 'Utilities', 'Entertainment']
        transactions = []
        
        # Generate 12 months of sample data
        base_date = datetime.datetime.now() - datetime.timedelta(days=365)
        
        for i in range(500):  # 500 sample transactions
            date = base_date + datetime.timedelta(days=random.randint(0, 365))
            category = random.choice(categories)
            
            # Create some spending patterns and anomalies
            base_amount = {
                'Groceries': 75,
                'Gas': 45,
                'Dining': 35,
                'Shopping': 120,
                'Utilities': 150,
                'Entertainment': 60
            }[category]
            
            # Add seasonal variations and occasional spikes
            amount = base_amount + random.uniform(-20, 50)
            if random.random() < 0.05:  # 5% chance of spike
                amount *= random.uniform(2, 5)
                
            transactions.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'category': category,
                'description': f'{category} transaction'
            })
            
        return sorted(transactions, key=lambda x: x['date'])
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Load and organize transaction data by month and category."""
        try:
            self.transactions = transactions
            
            for transaction in transactions:
                date_obj = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = float(transaction['amount'])
                
                self.monthly_data[month_key][category].append(amount)
                
        except (ValueError, KeyError) as e:
            print(f"Error loading transactions: {e}")
            raise
    
    def calculate_monthly_trends(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals and trends."""
        monthly_totals = {}
        monthly_changes = {}
        
        try:
            # Calculate monthly totals
            for month, categories in self.monthly_data.items():
                total = sum(sum(amounts) for amounts in categories.values())
                monthly_totals[month] = total
            
            # Calculate month-over-month changes
            sorted_months = sorted(monthly_totals.keys())
            for i in range(1, len(sorted_months)):
                current_month = sorted_months[i]
                prev_month = sorted_months[i-1]
                
                current_total = monthly_totals[current_month]
                prev_total = monthly_totals[prev_month]
                
                if prev_total > 0:
                    change_pct = ((current_total - prev_total) / prev_total) * 100
                    monthly_changes[current_month] = change_pct
                    
            return {
                'totals': monthly_totals,
                'changes': monthly_changes
            }
            
        except Exception as e:
            print(f"Error calculating monthly trends: {e}")
            return {'totals': {}, 'changes': {}}
    
    def analyze_category_trends(self) -> Dict[str, Dict[str, Any]]:
        """Analyze spending trends by category."""
        category_analysis = {}
        
        try:
            # Get all categories
            all_categories = set()
            for categories in self.monthly_data.values():
                all_categories.update(categories.keys())
            
            for category in all_categories:
                monthly_spending = {}
                
                # Calculate monthly spending for this category
                for month, categories in self.monthly_data.items():
                    if category in categories:
                        monthly_spending[month] = sum(categories[category])
                    else:
                        monthly_spending[month] = 0
                
                # Calculate trends
                sorted_months = sorted(monthly_spending.keys())
                spending_values = [monthly_spending[month] for month in sorted_months]
                
                if len(spending_values) > 1:
                    # Calculate average and trend
                    avg_spending = statistics.mean(spending_values)
                    
                    # Simple linear trend calculation
                    trend_direction = "stable"
                    if len(spending_values) >= 3:
                        recent_avg = statistics.mean(spending_values[-3:])
                        early_avg = statistics.mean(spending_values[:3])
                        
                        if recent_avg > early_avg * 1.1:
                            trend_direction = "increasing"
                        elif recent_avg < early_avg * 0.9:
                            trend_direction = "decreasing"
                    
                    # Calculate percentage changes
                    changes = []
                    for i in range(1, len(spending_values)):
                        if spending_values[i-1] > 0:
                            change = ((spending_values[i] - spending_values[i-1]) / spending_values[i-1]) * 100
                            changes.append(change)
                    
                    avg_change = statistics.mean(changes) if changes else 0
                    
                    category_analysis[category] = {
                        'average_monthly': round(avg_spending, 2),
                        'trend_direction': trend_direction,
                        'avg_monthly_change': round(avg_change, 2),
                        'total_months': len(spending_values)
                    }
                    
            return category_analysis
            
        except Exception as e:
            print(f"Error analyzing category trends: {e}")
            return {}
    
    def detect_unusual_transactions(self, threshold_multiplier: float = 2.5) -> List[Dict[str, Any]]:
        """Detect transactions that are unusually large compared to category averages."""
        unusual_transactions = []
        
        try:
            # Calculate category averages and standard deviations
            category_stats = {}
            
            for transaction in self.transactions:
                category = transaction['category']
                if category not in category_stats:
                    category_stats[category] = []
                category_stats[category].append(float(transaction['amount']))
            
            # Calculate stats for each category
            for category, amounts in category_stats.items():
                if len(amounts) > 1:
                    mean_amount = statistics.mean(amounts)
                    stdev_amount = statistics.stdev(amounts)
                    
                    # Find transactions exceeding threshold
                    for transaction in self.transactions:
                        if transaction['category'] == category:
                            amount = float(transaction['amount'])
                            z_score = (amount - mean_amount) / stdev_amount if stdev_amount > 0 else 0
                            
                            if abs(z_score) > threshold_multiplier:
                                unusual_transactions.append({
                                    'date': transaction['date'],
                                    'amount': amount,
                                    'category': category,
                                    'description': transaction['description'],