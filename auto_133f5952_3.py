```python
"""
Budget Recommendation System

This module analyzes historical spending patterns to provide intelligent budget recommendations.
It processes transaction data to identify spending patterns, suggest realistic budget limits
per category, highlight potential savings opportunities, and export actionable insights.

Key Features:
- Analyzes spending trends across categories and time periods
- Suggests budget limits based on statistical analysis of historical data
- Identifies anomalies and potential cost-cutting opportunities
- Exports results in CSV and JSON formats for further analysis
- Provides actionable recommendations for budget optimization

Usage:
    python script.py

The system expects transaction data in a specific format and will generate
sample data if none is provided.
"""

import json
import csv
import statistics
import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import random


class BudgetRecommendationSystem:
    def __init__(self):
        self.transactions = []
        self.categories = {}
        self.recommendations = {}
        self.savings_opportunities = []
        
    def load_sample_data(self):
        """Generate sample transaction data for demonstration."""
        categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Personal Care', 'Home & Garden', 'Insurance', 'Gas'
        ]
        
        start_date = datetime.datetime.now() - datetime.timedelta(days=365)
        
        for i in range(500):
            transaction = {
                'date': (start_date + datetime.timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
                'category': random.choice(categories),
                'amount': round(random.uniform(5, 500), 2),
                'description': f'Transaction {i+1}',
                'merchant': f'Merchant {random.randint(1, 50)}'
            }
            self.transactions.append(transaction)
    
    def analyze_spending_patterns(self):
        """Analyze historical spending to identify patterns and trends."""
        try:
            # Group transactions by category
            category_spending = defaultdict(list)
            monthly_totals = defaultdict(float)
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                date = datetime.datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                
                category_spending[category].append(amount)
                monthly_totals[month_key] += amount
            
            # Calculate statistics for each category
            for category, amounts in category_spending.items():
                self.categories[category] = {
                    'total_spent': sum(amounts),
                    'average_transaction': statistics.mean(amounts),
                    'median_transaction': statistics.median(amounts),
                    'transaction_count': len(amounts),
                    'monthly_average': sum(amounts) / 12,  # Assuming 12 months of data
                    'std_deviation': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                    'max_transaction': max(amounts),
                    'min_transaction': min(amounts)
                }
            
            return True
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return False
    
    def generate_budget_recommendations(self):
        """Generate budget recommendations based on spending analysis."""
        try:
            for category, stats in self.categories.items():
                monthly_avg = stats['monthly_average']
                std_dev = stats['std_deviation']
                
                # Conservative recommendation (mean - 0.5 * std_dev)
                conservative_budget = max(monthly_avg - (0.5 * std_dev), monthly_avg * 0.7)
                
                # Moderate recommendation (mean)
                moderate_budget = monthly_avg
                
                # Liberal recommendation (mean + 0.5 * std_dev)
                liberal_budget = monthly_avg + (0.5 * std_dev)
                
                # Determine recommended budget based on spending consistency
                if std_dev < monthly_avg * 0.3:  # Low variability
                    recommended_budget = conservative_budget
                    confidence = "High"
                elif std_dev < monthly_avg * 0.6:  # Moderate variability
                    recommended_budget = moderate_budget
                    confidence = "Medium"
                else:  # High variability
                    recommended_budget = liberal_budget
                    confidence = "Low"
                
                self.recommendations[category] = {
                    'current_monthly_average': round(monthly_avg, 2),
                    'recommended_budget': round(recommended_budget, 2),
                    'conservative_budget': round(conservative_budget, 2),
                    'moderate_budget': round(moderate_budget, 2),
                    'liberal_budget': round(liberal_budget, 2),
                    'confidence_level': confidence,
                    'potential_savings': round(max(0, monthly_avg - recommended_budget), 2),
                    'spending_consistency': 'High' if std_dev < monthly_avg * 0.3 else 'Medium' if std_dev < monthly_avg * 0.6 else 'Low'
                }
            
            return True
            
        except Exception as e:
            print(f"Error generating budget recommendations: {e}")
            return False
    
    def identify_savings_opportunities(self):
        """Identify potential savings opportunities."""
        try:
            # High-spending categories with potential for reduction
            sorted_categories = sorted(
                self.categories.items(),
                key=lambda x: x[1]['monthly_average'],
                reverse=True
            )
            
            for category, stats in sorted_categories[:5]:  # Top 5 spending categories
                monthly_avg = stats['monthly_average']
                max_transaction = stats['max_transaction']
                std_dev = stats['std_deviation']
                
                opportunity = {
                    'category': category,
                    'monthly_spending': round(monthly_avg, 2),
                    'opportunity_type': '',
                    'potential_savings': 0,
                    'recommendation': ''
                }
                
                # Identify opportunity type
                if max_transaction > monthly_avg * 2:
                    opportunity['opportunity_type'] = 'Large Transaction Review'
                    opportunity['potential_savings'] = round(monthly_avg * 0.1, 2)
                    opportunity['recommendation'] = f'Review large transactions in {category}. Consider alternatives for purchases over ${max_transaction/2:.2f}'
                
                elif std_dev > monthly_avg * 0.5:
                    opportunity['opportunity_type'] = 'Spending Consistency'
                    opportunity['potential_savings'] = round(monthly_avg * 0.15, 2)
                    opportunity['recommendation'] = f'High spending variability in {category}. Set spending limits and track more closely.'
                
                elif monthly_avg > 300:  # High spending category
                    opportunity['opportunity_type'] = 'Budget Optimization'
                    opportunity['potential_savings'] = round(monthly_avg * 0.08, 2)
                    opportunity['recommendation'] = f'{category} is a high-spend area. Look for subscription optimizations or alternative vendors.'
                
                if opportunity['opportunity_type']:
                    self.savings_opportunities.append(opportunity)
            
            # Sort by potential savings
            self.savings_opportunities.sort(key=lambda x: x['potential_savings'], reverse=True)
            
            return True
            
        except Exception as e:
            print(f"Error identifying savings opportunities: {e}")
            return False
    
    def export_to_csv(self, filename='budget_recommendations.csv'):
        """Export recommendations to CSV format."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'category', 'current_monthly_average', 'recommended_budget',
                    'conservative_budget', 'moderate_budget', 'liberal_budget',
                    'confidence_level', 'potential_savings', 'spending_consistency'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer