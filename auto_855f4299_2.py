```python
"""
Personal Budget Recommendation Engine

This module analyzes historical spending data and generates personalized budget recommendations
using established budgeting frameworks like the 50/30/20 rule. It processes spending patterns,
categorizes expenses, and provides monthly budget suggestions with category-specific limits.

The engine supports multiple budgeting frameworks:
- 50/30/20 Rule: 50% needs, 30% wants, 20% savings
- 60/20/20 Rule: 60% needs, 20% wants, 20% savings
- Zero-based budgeting approach

Features:
- Historical spending analysis
- Category-based expense tracking
- Personalized budget recommendations
- Variance analysis and alerts
- Future spending predictions
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import random


@dataclass
class Transaction:
    """Represents a single financial transaction"""
    date: str
    amount: float
    category: str
    description: str
    is_essential: bool = True


@dataclass
class BudgetRecommendation:
    """Represents budget recommendations for a category"""
    category: str
    recommended_amount: float
    historical_avg: float
    variance: float
    priority: str
    suggestions: List[str]


class BudgetEngine:
    """Core budget recommendation engine"""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.income_history: List[Tuple[str, float]] = []
        
        # Define essential vs non-essential categories
        self.essential_categories = {
            'housing', 'utilities', 'groceries', 'transportation', 
            'insurance', 'healthcare', 'debt_payments', 'childcare'
        }
        
        self.discretionary_categories = {
            'dining_out', 'entertainment', 'shopping', 'hobbies',
            'subscriptions', 'travel', 'gifts', 'miscellaneous'
        }
    
    def load_sample_data(self) -> None:
        """Generate realistic sample transaction data"""
        try:
            # Sample income data
            base_income = 5500
            for i in range(6):
                date = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-%d')
                income = base_income + random.randint(-200, 300)
                self.income_history.append((date, income))
            
            # Sample transactions for last 6 months
            categories_data = {
                'housing': {'avg': 1800, 'var': 50, 'essential': True},
                'utilities': {'avg': 250, 'var': 80, 'essential': True},
                'groceries': {'avg': 600, 'var': 150, 'essential': True},
                'transportation': {'avg': 400, 'var': 100, 'essential': True},
                'insurance': {'avg': 300, 'var': 20, 'essential': True},
                'healthcare': {'avg': 200, 'var': 150, 'essential': True},
                'dining_out': {'avg': 450, 'var': 200, 'essential': False},
                'entertainment': {'avg': 300, 'var': 180, 'essential': False},
                'shopping': {'avg': 350, 'var': 250, 'essential': False},
                'subscriptions': {'avg': 80, 'var': 30, 'essential': False},
                'travel': {'avg': 200, 'var': 400, 'essential': False},
                'miscellaneous': {'avg': 150, 'var': 100, 'essential': False}
            }
            
            for month_offset in range(6):
                base_date = datetime.now() - timedelta(days=30*month_offset)
                
                for category, data in categories_data.items():
                    # Generate 2-8 transactions per category per month
                    num_transactions = random.randint(2, 8)
                    monthly_total = max(0, data['avg'] + random.randint(-data['var'], data['var']))
                    
                    for _ in range(num_transactions):
                        amount = monthly_total / num_transactions * random.uniform(0.3, 2.0)
                        amount = round(amount, 2)
                        
                        transaction_date = base_date + timedelta(days=random.randint(0, 29))
                        
                        transaction = Transaction(
                            date=transaction_date.strftime('%Y-%m-%d'),
                            amount=amount,
                            category=category,
                            description=f"{category.replace('_', ' ').title()} expense",
                            is_essential=data['essential']
                        )
                        self.transactions.append(transaction)
                        
        except Exception as e:
            print(f"Error loading sample data: {e}")
            raise
    
    def analyze_spending_patterns(self) -> Dict[str, Dict]:
        """Analyze historical spending patterns by category"""
        try:
            category_spending = defaultdict(list)
            
            for transaction in self.transactions:
                category_spending[transaction.category].append(transaction.amount)
            
            analysis = {}
            for category, amounts in category_spending.items():
                if amounts:
                    analysis[category] = {
                        'total': sum(amounts),
                        'average_monthly': sum(amounts) / 6,  # 6 months of data
                        'median': statistics.median(amounts),
                        'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                        'min': min(amounts),
                        'max': max(amounts),
                        'transaction_count': len(amounts),
                        'is_essential': category in self.essential_categories
                    }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}
    
    def calculate_average_income(self) -> float:
        """Calculate average monthly income"""
        try:
            if not self.income_history:
                return 0.0
            return statistics.mean([income for _, income in self.income_history])
        except Exception as e:
            print(f"Error calculating average income: {e}")
            return 0.0
    
    def apply_50_30_20_rule(self, monthly_income: float) -> Dict[str, float]:
        """Apply the 50/30/20 budgeting rule"""
        return {
            'needs': monthly_income * 0.50,
            'wants': monthly_income * 0.30,
            'savings': monthly_income * 0.20
        }
    
    def apply_60_20_20_rule(self, monthly_income: float) -> Dict[str, float]:
        """Apply the 60/20/20 budgeting rule (higher needs allocation)"""
        return {
            'needs': monthly_income * 0.60,
            'wants': monthly_income * 0.20,
            'savings': monthly_income * 0.20
        }
    
    def generate_category_recommendations(self, 
                                        spending_analysis: Dict[str, Dict],
                                        budget_framework: Dict[str, float]) -> List[BudgetRecommendation]:
        """Generate detailed recommendations for each spending category"""
        try:
            recommendations = []
            
            # Calculate total current spending by type
            total_needs = sum(data['average_monthly'] for cat, data in spending_analysis.items() 
                            if data['is_essential'])
            total_wants = sum(data['average_monthly'] for cat, data in spending_analysis.items() 
                            if not data['is_essential'])
            
            # Allocate budget proportionally within needs and wants
            needs_budget = budget_framework['needs']
            wants_budget = budget_framework['wants']
            
            for category, data in spending_analysis.items():
                current_avg = data['average_monthly']
                variance = data['std_dev']
                
                if data['is_essential']:
                    # For needs: proportional allocation based on current