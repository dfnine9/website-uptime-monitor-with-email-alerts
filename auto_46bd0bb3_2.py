```python
"""
Budget Recommendation Engine

This module analyzes spending patterns to provide intelligent budget recommendations.
It processes historical transaction data to suggest optimal budget allocations per category,
identifies overspending alerts, and generates personalized savings opportunities.

Features:
- Analyzes spending patterns across multiple categories
- Suggests optimal budget allocations based on historical averages
- Detects overspending patterns and generates alerts
- Identifies savings opportunities through spending trend analysis
- Provides actionable recommendations for budget optimization

Usage:
    python script.py

The script will generate sample transaction data and provide comprehensive
budget analysis and recommendations.
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median
from typing import Dict, List, Tuple, Any
import random


class BudgetRecommendationEngine:
    """Main engine for budget analysis and recommendations"""
    
    def __init__(self):
        self.transactions = []
        self.categories = [
            'Groceries', 'Transportation', 'Entertainment', 'Utilities',
            'Dining Out', 'Shopping', 'Healthcare', 'Education', 'Insurance'
        ]
        self.overspending_threshold = 1.2  # 20% over average
        
    def add_transaction(self, amount: float, category: str, date: str, description: str = ""):
        """Add a transaction to the dataset"""
        try:
            transaction = {
                'amount': float(amount),
                'category': category,
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'description': description
            }
            self.transactions.append(transaction)
        except (ValueError, TypeError) as e:
            print(f"Error adding transaction: {e}")
    
    def generate_sample_data(self, months: int = 6):
        """Generate sample transaction data for demonstration"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Base spending amounts per category
            base_amounts = {
                'Groceries': 400,
                'Transportation': 150,
                'Entertainment': 200,
                'Utilities': 120,
                'Dining Out': 300,
                'Shopping': 250,
                'Healthcare': 100,
                'Education': 50,
                'Insurance': 180
            }
            
            current_date = start_date
            while current_date <= end_date:
                for category in self.categories:
                    # Generate 2-5 transactions per category per month
                    num_transactions = random.randint(2, 5)
                    for _ in range(num_transactions):
                        # Add some variation to amounts
                        base = base_amounts[category]
                        amount = base * random.uniform(0.5, 1.8) / num_transactions
                        
                        # Add some seasonal variation
                        if category == 'Entertainment' and current_date.month in [11, 12]:
                            amount *= 1.5  # Holiday spending
                        elif category == 'Utilities' and current_date.month in [1, 2, 7, 8]:
                            amount *= 1.3  # Winter/summer utility costs
                        
                        self.add_transaction(
                            amount=round(amount, 2),
                            category=category,
                            date=current_date.strftime('%Y-%m-%d'),
                            description=f"Sample {category.lower()} transaction"
                        )
                
                current_date += timedelta(days=random.randint(1, 3))
                
            print(f"Generated {len(self.transactions)} sample transactions")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
    
    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns by category"""
        try:
            analysis = defaultdict(lambda: {
                'total': 0,
                'count': 0,
                'amounts': [],
                'monthly_totals': defaultdict(float)
            })
            
            for transaction in self.transactions:
                category = transaction['category']
                amount = transaction['amount']
                month_key = transaction['date'].strftime('%Y-%m')
                
                analysis[category]['total'] += amount
                analysis[category]['count'] += 1
                analysis[category]['amounts'].append(amount)
                analysis[category]['monthly_totals'][month_key] += amount
            
            # Calculate statistics for each category
            for category, data in analysis.items():
                if data['amounts']:
                    data['average'] = mean(data['amounts'])
                    data['median'] = median(data['amounts'])
                    data['monthly_average'] = mean(data['monthly_totals'].values()) if data['monthly_totals'] else 0
                    data['max_monthly'] = max(data['monthly_totals'].values()) if data['monthly_totals'] else 0
                    data['min_monthly'] = min(data['monthly_totals'].values()) if data['monthly_totals'] else 0
            
            return dict(analysis)
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}
    
    def suggest_budget_allocations(self, monthly_income: float) -> Dict[str, float]:
        """Suggest optimal budget allocations based on spending patterns"""
        try:
            analysis = self.analyze_spending_patterns()
            suggestions = {}
            
            # Calculate total average monthly spending
            total_monthly_spending = sum(
                data.get('monthly_average', 0) for data in analysis.values()
            )
            
            # Budget allocation strategy
            for category, data in analysis.items():
                monthly_avg = data.get('monthly_average', 0)
                
                if total_monthly_spending > 0:
                    # Base allocation on historical percentage
                    percentage = monthly_avg / total_monthly_spending
                    # Apply recommended budget percentages with adjustments
                    suggested_amount = monthly_income * percentage
                    
                    # Apply category-specific recommendations
                    if category in ['Groceries', 'Utilities', 'Insurance']:
                        # Essential categories - ensure adequate funding
                        suggested_amount = max(suggested_amount, monthly_avg * 1.1)
                    elif category in ['Entertainment', 'Dining Out', 'Shopping']:
                        # Discretionary categories - potential for reduction
                        suggested_amount = min(suggested_amount, monthly_avg * 0.9)
                    
                    suggestions[category] = round(suggested_amount, 2)
                else:
                    suggestions[category] = 0
            
            return suggestions
            
        except Exception as e:
            print(f"Error suggesting budget allocations: {e}")
            return {}
    
    def identify_overspending_alerts(self) -> List[Dict[str, Any]]:
        """Identify categories with overspending patterns"""
        try:
            analysis = self.analyze_spending_patterns()
            alerts = []
            
            for category, data in analysis.items():
                monthly_totals = list(data['monthly_totals'].values())
                if len(monthly_totals) < 2:
                    continue
                
                avg_monthly = data.get('monthly_average', 0)
                recent_month = monthly_totals[-1] if monthly_totals else 0
                
                # Check if recent spending exceeds threshold
                if recent_month > avg_monthly * self.overspending_threshold:
                    overspend_amount = recent_month - avg_monthly
                    overspend_percentage = ((recent_month / avg_monthly) - 1) * 100
                    
                    alerts.append({
                        'category': category,
                        'recent_spending': recent_month,
                        'average_spending': avg_monthly,
                        'overspend_amount': round(overspend_amount, 2),
                        'overspend_percentage': round(overspend_percentage, 1),
                        'severity': 'High' if overspend_percentage > 50 else 'Medium'
                    })
            
            return sorted(alerts, key=lambda x: x['overspend_percentage'], reverse=True)
            
        except Exception as e:
            print(f"