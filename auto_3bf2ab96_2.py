```python
"""
Financial Transaction Analysis Engine

This module processes categorized financial transactions to identify spending patterns,
calculate monthly averages per category, detect unusual spending spikes, and find
potential savings opportunities.

Features:
- Calculates monthly spending averages by category
- Detects spending spikes (transactions > 2 standard deviations above mean)
- Identifies potential savings opportunities based on spending patterns
- Provides detailed analysis reports

Usage:
    python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import random


class TransactionAnalyzer:
    """Analyzes financial transactions for spending patterns and savings opportunities."""
    
    def __init__(self):
        self.transactions = []
        self.monthly_stats = defaultdict(lambda: defaultdict(list))
        self.category_totals = defaultdict(float)
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for demonstration."""
        categories = [
            'Groceries', 'Gas', 'Restaurants', 'Entertainment', 'Utilities',
            'Rent', 'Insurance', 'Healthcare', 'Shopping', 'Travel'
        ]
        
        base_date = datetime(2023, 1, 1)
        
        for i in range(500):
            date = base_date + timedelta(days=random.randint(0, 365))
            category = random.choice(categories)
            
            # Set realistic spending ranges by category
            if category == 'Rent':
                amount = random.uniform(1200, 1500)
            elif category == 'Groceries':
                amount = random.uniform(50, 200)
            elif category == 'Gas':
                amount = random.uniform(30, 80)
            elif category == 'Utilities':
                amount = random.uniform(80, 150)
            elif category == 'Insurance':
                amount = random.uniform(100, 300)
            else:
                amount = random.uniform(10, 300)
            
            # Occasionally add spending spikes
            if random.random() < 0.05:  # 5% chance of spike
                amount *= random.uniform(2.5, 5.0)
            
            transaction = {
                'date': date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'category': category,
                'description': f'{category} purchase #{i+1}'
            }
            self.transactions.append(transaction)
    
    def process_transactions(self) -> None:
        """Process transactions and organize by month and category."""
        try:
            for transaction in self.transactions:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                self.monthly_stats[month_key][category].append(amount)
                self.category_totals[category] += amount
                
        except (ValueError, KeyError) as e:
            print(f"Error processing transaction: {e}")
    
    def calculate_monthly_averages(self) -> Dict[str, float]:
        """Calculate monthly spending averages per category."""
        try:
            category_averages = {}
            
            for category in self.category_totals.keys():
                monthly_totals = []
                
                for month_data in self.monthly_stats.values():
                    if category in month_data:
                        monthly_total = sum(month_data[category])
                        monthly_totals.append(monthly_total)
                
                if monthly_totals:
                    category_averages[category] = statistics.mean(monthly_totals)
                else:
                    category_averages[category] = 0.0
            
            return category_averages
            
        except Exception as e:
            print(f"Error calculating monthly averages: {e}")
            return {}
    
    def detect_spending_spikes(self) -> List[Dict[str, Any]]:
        """Detect unusual spending spikes (> 2 standard deviations above mean)."""
        spikes = []
        
        try:
            for category in self.category_totals.keys():
                all_amounts = []
                
                # Collect all transaction amounts for this category
                for transaction in self.transactions:
                    if transaction['category'] == category:
                        all_amounts.append(transaction['amount'])
                
                if len(all_amounts) > 3:  # Need sufficient data
                    mean_amount = statistics.mean(all_amounts)
                    stdev_amount = statistics.stdev(all_amounts)
                    threshold = mean_amount + (2 * stdev_amount)
                    
                    # Find transactions above threshold
                    for transaction in self.transactions:
                        if (transaction['category'] == category and 
                            transaction['amount'] > threshold):
                            spikes.append({
                                'date': transaction['date'],
                                'category': category,
                                'amount': transaction['amount'],
                                'mean': round(mean_amount, 2),
                                'threshold': round(threshold, 2),
                                'description': transaction['description']
                            })
            
        except Exception as e:
            print(f"Error detecting spending spikes: {e}")
        
        return sorted(spikes, key=lambda x: x['amount'], reverse=True)
    
    def find_savings_opportunities(self) -> List[Dict[str, Any]]:
        """Identify potential savings opportunities based on spending patterns."""
        opportunities = []
        
        try:
            monthly_averages = self.calculate_monthly_averages()
            
            # Categories with high variability suggest savings potential
            for category in self.category_totals.keys():
                monthly_amounts = []
                
                for month_data in self.monthly_stats.values():
                    if category in month_data:
                        monthly_total = sum(month_data[category])
                        monthly_amounts.append(monthly_total)
                
                if len(monthly_amounts) > 2:
                    avg_spending = statistics.mean(monthly_amounts)
                    
                    if len(monthly_amounts) > 3:
                        variability = statistics.stdev(monthly_amounts)
                        cv = variability / avg_spending if avg_spending > 0 else 0
                        
                        # High coefficient of variation suggests optimization potential
                        if cv > 0.3 and avg_spending > 50:  # Minimum threshold
                            potential_savings = variability * 0.5  # Conservative estimate
                            opportunities.append({
                                'category': category,
                                'monthly_average': round(avg_spending, 2),
                                'variability': round(variability, 2),
                                'coefficient_variation': round(cv, 2),
                                'potential_monthly_savings': round(potential_savings, 2),
                                'annual_savings': round(potential_savings * 12, 2)
                            })
            
        except Exception as e:
            print(f"Error finding savings opportunities: {e}")
        
        return sorted(opportunities, key=lambda x: x['annual_savings'], reverse=True)
    
    def generate_spending_summary(self) -> Dict[str, Any]:
        """Generate comprehensive spending summary."""
        try:
            total_spending = sum(self.category_totals.values())
            category_percentages = {
                category: (amount / total_spending * 100) if total_spending > 0 else 0
                for category, amount in self.category_totals.items()
            }
            
            # Find top spending categories
            top_categories = sorted(
                category_percentages.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return {
                'total_spending': round(total_spending, 2),
                'number_of_transactions': len(self.transactions),
                'average_transaction': round(total_spending / len(self.transactions), 2) if self.transactions else 0,
                'top_spending_categories': [
                    {'category': cat, 'percentage': round(pct, 1)}
                    for cat, pct