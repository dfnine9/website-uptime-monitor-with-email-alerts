```python
"""
Spending Pattern Analyzer Module

This module analyzes categorized spending patterns by calculating monthly totals
per category, identifying spending trends over time, and detecting anomalies or
unusual expenses in financial data.

Features:
- Calculate monthly spending totals by category
- Identify spending trends and patterns over time
- Detect spending anomalies using statistical analysis
- Generate comprehensive spending reports

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import random
import math


class SpendingAnalyzer:
    """Analyzes spending patterns and detects anomalies in financial data."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_totals = defaultdict(lambda: defaultdict(float))
        self.category_stats = defaultdict(list)
    
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare']
        
        # Generate 200 sample transactions over 12 months
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(200):
            category = random.choice(categories)
            
            # Create category-specific spending patterns
            if category == 'Food':
                amount = random.uniform(10, 150)
            elif category == 'Transportation':
                amount = random.uniform(5, 200)
            elif category == 'Entertainment':
                amount = random.uniform(15, 300)
            elif category == 'Utilities':
                amount = random.uniform(50, 400)
            elif category == 'Shopping':
                amount = random.uniform(20, 500)
            else:  # Healthcare
                amount = random.uniform(30, 1000)
            
            # Add some anomalies (5% chance of unusual spending)
            if random.random() < 0.05:
                amount *= random.uniform(3, 8)
            
            transaction_date = base_date + timedelta(days=random.randint(0, 365))
            
            self.transactions.append({
                'date': transaction_date.strftime('%Y-%m-%d'),
                'category': category,
                'amount': round(amount, 2),
                'description': f'{category} expense #{i+1}'
            })
    
    def calculate_monthly_totals(self) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending totals by category."""
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_totals[month_key][category] += amount
                self.category_stats[category].append(amount)
            
            return dict(self.monthly_totals)
        
        except Exception as e:
            print(f"Error calculating monthly totals: {e}")
            return {}
    
    def identify_trends(self) -> Dict[str, Dict[str, Any]]:
        """Identify spending trends over time for each category."""
        trends = {}
        
        try:
            for category in self.category_stats:
                if len(self.category_stats[category]) < 3:
                    continue
                
                # Calculate monthly averages
                monthly_data = []
                sorted_months = sorted(self.monthly_totals.keys())
                
                for month in sorted_months:
                    if category in self.monthly_totals[month]:
                        monthly_data.append(self.monthly_totals[month][category])
                    else:
                        monthly_data.append(0)
                
                if len(monthly_data) >= 3:
                    # Calculate trend direction
                    first_half = monthly_data[:len(monthly_data)//2]
                    second_half = monthly_data[len(monthly_data)//2:]
                    
                    avg_first = sum(first_half) / len(first_half)
                    avg_second = sum(second_half) / len(second_half)
                    
                    trend_direction = "Increasing" if avg_second > avg_first else "Decreasing"
                    trend_percentage = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
                    
                    trends[category] = {
                        'direction': trend_direction,
                        'percentage_change': round(trend_percentage, 2),
                        'average_monthly': round(statistics.mean(monthly_data), 2),
                        'total_months': len(monthly_data)
                    }
            
            return trends
        
        except Exception as e:
            print(f"Error identifying trends: {e}")
            return {}
    
    def detect_anomalies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect spending anomalies using statistical analysis."""
        anomalies = defaultdict(list)
        
        try:
            for category in self.category_stats:
                amounts = self.category_stats[category]
                
                if len(amounts) < 5:
                    continue
                
                # Calculate statistical measures
                mean_amount = statistics.mean(amounts)
                std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                # Define anomaly threshold (2.5 standard deviations from mean)
                threshold = 2.5
                upper_bound = mean_amount + (threshold * std_dev)
                lower_bound = max(0, mean_amount - (threshold * std_dev))
                
                # Find anomalous transactions
                for transaction in self.transactions:
                    if transaction['category'] == category:
                        amount = transaction['amount']
                        
                        if amount > upper_bound or amount < lower_bound:
                            z_score = (amount - mean_amount) / std_dev if std_dev > 0 else 0
                            
                            anomalies[category].append({
                                'date': transaction['date'],
                                'amount': amount,
                                'description': transaction['description'],
                                'z_score': round(z_score, 2),
                                'deviation_type': 'High' if amount > upper_bound else 'Low'
                            })
            
            return dict(anomalies)
        
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {}
    
    def generate_report(self) -> None:
        """Generate and print comprehensive spending analysis report."""
        try:
            print("=" * 60)
            print("SPENDING PATTERN ANALYSIS REPORT")
            print("=" * 60)
            
            # Monthly totals
            monthly_totals = self.calculate_monthly_totals()
            print("\n📊 MONTHLY SPENDING TOTALS BY CATEGORY")
            print("-" * 40)
            
            for month in sorted(monthly_totals.keys()):
                print(f"\n{month}:")
                total_month = sum(monthly_totals[month].values())
                
                for category, amount in sorted(monthly_totals[month].items()):
                    percentage = (amount / total_month * 100) if total_month > 0 else 0
                    print(f"  {category:<15}: ${amount:>8.2f} ({percentage:>5.1f}%)")
                
                print(f"  {'TOTAL':<15}: ${total_month:>8.2f}")
            
            # Spending trends
            trends = self.identify_trends()
            print("\n📈 SPENDING TRENDS ANALYSIS")
            print("-" * 40)
            
            for category, trend_data in trends.items():
                direction_icon = "📈" if trend_data['direction'] == "Increasing" else "📉"
                print(f"\n{direction_icon} {category}:")
                print(f"  Trend: {trend_data['direction']} ({trend_data['percentage_change']:+.1f}