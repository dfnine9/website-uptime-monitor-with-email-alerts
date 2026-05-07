```python
"""
Budget Recommendation Engine

This module analyzes historical spending patterns from sample data to provide:
- Budget allocation recommendations per category
- Expense optimization insights
- Spending trend analysis
- Actionable recommendations for financial improvement

The engine uses statistical analysis to identify spending patterns, detect anomalies,
and suggest optimal budget distributions based on historical data and best practices.
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import random


class BudgetRecommendationEngine:
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Housing', 'Transportation', 'Food', 'Healthcare', 'Entertainment',
            'Utilities', 'Shopping', 'Education', 'Insurance', 'Savings'
        ]
        
    def generate_sample_data(self, months=12):
        """Generate realistic sample transaction data for demonstration"""
        transactions = []
        base_date = datetime.now() - timedelta(days=30 * months)
        
        # Category spending patterns (monthly averages)
        category_patterns = {
            'Housing': (1200, 200),  # (mean, std_dev)
            'Transportation': (400, 100),
            'Food': (600, 150),
            'Healthcare': (200, 80),
            'Entertainment': (300, 120),
            'Utilities': (250, 50),
            'Shopping': (400, 200),
            'Education': (150, 50),
            'Insurance': (300, 30),
            'Savings': (500, 100)
        }
        
        for month in range(months):
            month_date = base_date + timedelta(days=30 * month)
            
            for category, (mean, std_dev) in category_patterns.items():
                # Generate 3-8 transactions per category per month
                num_transactions = random.randint(3, 8)
                monthly_total = max(50, random.gauss(mean, std_dev))
                
                for _ in range(num_transactions):
                    amount = max(10, monthly_total / num_transactions * random.uniform(0.3, 1.7))
                    transaction_date = month_date + timedelta(days=random.randint(0, 29))
                    
                    transactions.append({
                        'date': transaction_date.strftime('%Y-%m-%d'),
                        'amount': round(amount, 2),
                        'category': category,
                        'description': f"{category.lower()}_purchase_{random.randint(1000, 9999)}"
                    })
        
        return sorted(transactions, key=lambda x: x['date'])
    
    def load_data(self, transactions=None):
        """Load transaction data"""
        if transactions is None:
            self.transactions = self.generate_sample_data()
        else:
            self.transactions = transactions
    
    def analyze_spending_patterns(self):
        """Analyze historical spending patterns by category"""
        try:
            category_spending = defaultdict(list)
            monthly_spending = defaultdict(lambda: defaultdict(float))
            
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                category = transaction['category']
                amount = transaction['amount']
                
                category_spending[category].append(amount)
                monthly_spending[month_key][category] += amount
            
            # Calculate statistics per category
            category_stats = {}
            for category, amounts in category_spending.items():
                if amounts:
                    category_stats[category] = {
                        'total': sum(amounts),
                        'average_monthly': sum(amounts) / max(1, len(set(t['date'][:7] for t in self.transactions))),
                        'median': statistics.median(amounts),
                        'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                        'transaction_count': len(amounts),
                        'average_transaction': sum(amounts) / len(amounts)
                    }
            
            return category_stats, dict(monthly_spending)
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}, {}
    
    def calculate_budget_recommendations(self, category_stats, income=5000):
        """Calculate recommended budget allocations based on patterns and best practices"""
        try:
            recommendations = {}
            total_current_spending = sum(stats['average_monthly'] for stats in category_stats.values())
            
            # Best practice percentage ranges for each category
            recommended_percentages = {
                'Housing': (25, 30),
                'Transportation': (10, 15),
                'Food': (10, 15),
                'Healthcare': (5, 10),
                'Entertainment': (5, 10),
                'Utilities': (5, 10),
                'Shopping': (5, 10),
                'Education': (2, 5),
                'Insurance': (5, 10),
                'Savings': (20, 30)
            }
            
            for category, stats in category_stats.items():
                current_monthly = stats['average_monthly']
                current_percentage = (current_monthly / income) * 100 if income > 0 else 0
                
                min_rec, max_rec = recommended_percentages.get(category, (5, 15))
                recommended_amount = income * (min_rec + max_rec) / 200  # Average of range
                
                status = "optimal"
                if current_percentage < min_rec:
                    status = "underspending"
                elif current_percentage > max_rec:
                    status = "overspending"
                
                recommendations[category] = {
                    'current_monthly': current_monthly,
                    'current_percentage': current_percentage,
                    'recommended_monthly': recommended_amount,
                    'recommended_percentage': (min_rec + max_rec) / 2,
                    'difference': recommended_amount - current_monthly,
                    'status': status
                }
            
            return recommendations
            
        except Exception as e:
            print(f"Error calculating budget recommendations: {e}")
            return {}
    
    def identify_optimization_opportunities(self, category_stats, recommendations):
        """Identify specific opportunities for expense optimization"""
        try:
            opportunities = []
            
            for category, rec in recommendations.items():
                stats = category_stats.get(category, {})
                
                if rec['status'] == 'overspending':
                    overspend_amount = rec['current_monthly'] - rec['recommended_monthly']
                    opportunities.append({
                        'type': 'reduce_spending',
                        'category': category,
                        'potential_savings': overspend_amount,
                        'priority': 'high' if overspend_amount > 200 else 'medium',
                        'description': f"Reduce {category} spending by ${overspend_amount:.2f}/month"
                    })
                
                # High transaction frequency optimization
                if stats.get('transaction_count', 0) > 20:  # Monthly average
                    avg_transaction = stats.get('average_transaction', 0)
                    if avg_transaction < 50:  # Many small transactions
                        opportunities.append({
                            'type': 'consolidate_purchases',
                            'category': category,
                            'potential_savings': avg_transaction * 0.1 * stats['transaction_count'],
                            'priority': 'low',
                            'description': f"Consolidate frequent small {category} purchases to reduce fees/impulse buying"
                        })
                
                # High variability optimization
                if stats.get('std_dev', 0) > stats.get('average_transaction', 1) * 0.5:
                    opportunities.append({
                        'type': 'stabilize_spending',
                        'category': category,
                        'potential_savings': stats['std_dev'] * 0.2,
                        'priority': 'medium',
                        'description': f"Create more consistent {category} spending patterns to improve budgeting"
                    })
            
            # Sort by potential savings