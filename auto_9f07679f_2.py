```python
#!/usr/bin/env python3
"""
Budget Recommendation Engine

A comprehensive personal finance tool that analyzes historical spending data to provide
intelligent budget recommendations, overspending alerts, and savings opportunities.

Features:
- Analyzes spending patterns across multiple categories
- Generates realistic monthly budget recommendations based on historical data
- Identifies overspending alerts when current spending exceeds recommended budgets
- Discovers savings opportunities through pattern analysis and outlier detection
- Provides actionable insights for financial optimization

The engine uses statistical analysis to calculate budget recommendations based on
historical averages, seasonal variations, and spending trends. It flags potential
overspending scenarios and identifies categories where users can optimize their spending.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import random


@dataclass
class Transaction:
    """Represents a single financial transaction"""
    date: datetime
    category: str
    amount: float
    description: str


@dataclass
class BudgetRecommendation:
    """Represents a budget recommendation for a category"""
    category: str
    recommended_monthly: float
    current_month_spent: float
    last_month_spent: float
    three_month_avg: float
    is_overspending: bool
    savings_opportunity: Optional[str] = None


class BudgetRecommendationEngine:
    """Main engine for budget analysis and recommendations"""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.categories = [
            'Groceries', 'Dining Out', 'Transportation', 'Entertainment',
            'Utilities', 'Shopping', 'Healthcare', 'Travel', 'Subscriptions', 'Other'
        ]
    
    def generate_sample_data(self) -> None:
        """Generate realistic sample transaction data for demonstration"""
        try:
            # Generate 6 months of sample data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            # Base spending amounts per category (monthly averages)
            base_spending = {
                'Groceries': 450,
                'Dining Out': 280,
                'Transportation': 220,
                'Entertainment': 150,
                'Utilities': 180,
                'Shopping': 320,
                'Healthcare': 120,
                'Travel': 200,
                'Subscriptions': 85,
                'Other': 100
            }
            
            current_date = start_date
            while current_date <= end_date:
                # Generate 8-15 transactions per day
                daily_transactions = random.randint(8, 15)
                
                for _ in range(daily_transactions):
                    category = random.choice(self.categories)
                    base_amount = base_spending[category]
                    
                    # Add realistic variance to amounts
                    if category == 'Groceries':
                        amount = random.uniform(15, 120)
                    elif category == 'Dining Out':
                        amount = random.uniform(8, 85)
                    elif category == 'Transportation':
                        amount = random.uniform(5, 45)
                    elif category == 'Utilities':
                        amount = random.uniform(25, 180)
                    elif category == 'Travel':
                        # Occasional larger travel expenses
                        amount = random.uniform(20, 800) if random.random() < 0.1 else random.uniform(15, 60)
                    else:
                        amount = random.uniform(5, base_amount * 0.4)
                    
                    # Add seasonal variations
                    if current_date.month in [11, 12]:  # Holiday season
                        if category in ['Shopping', 'Dining Out', 'Travel']:
                            amount *= random.uniform(1.2, 1.8)
                    
                    description = f"{category} purchase"
                    transaction = Transaction(current_date, category, amount, description)
                    self.transactions.append(transaction)
                
                current_date += timedelta(days=1)
                
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def get_monthly_spending(self, category: str, months_back: int = 0) -> float:
        """Calculate total spending for a specific category in a given month"""
        try:
            target_date = datetime.now() - timedelta(days=30 * months_back)
            target_month = target_date.month
            target_year = target_date.year
            
            total = sum(
                t.amount for t in self.transactions 
                if t.category == category and t.date.month == target_month and t.date.year == target_year
            )
            return total
        except Exception as e:
            print(f"Error calculating monthly spending for {category}: {e}")
            return 0.0
    
    def get_category_statistics(self, category: str) -> Dict[str, float]:
        """Calculate comprehensive statistics for a spending category"""
        try:
            amounts = [t.amount for t in self.transactions if t.category == category]
            
            if not amounts:
                return {
                    'total': 0.0, 'average': 0.0, 'median': 0.0,
                    'std_dev': 0.0, 'min': 0.0, 'max': 0.0
                }
            
            return {
                'total': sum(amounts),
                'average': statistics.mean(amounts),
                'median': statistics.median(amounts),
                'std_dev': statistics.stdev(amounts) if len(amounts) > 1 else 0.0,
                'min': min(amounts),
                'max': max(amounts)
            }
        except Exception as e:
            print(f"Error calculating statistics for {category}: {e}")
            return {'total': 0.0, 'average': 0.0, 'median': 0.0, 'std_dev': 0.0, 'min': 0.0, 'max': 0.0}
    
    def calculate_budget_recommendation(self, category: str) -> BudgetRecommendation:
        """Calculate budget recommendation for a specific category"""
        try:
            # Get spending for current month and previous months
            current_month = self.get_monthly_spending(category, 0)
            last_month = self.get_monthly_spending(category, 1)
            month_2 = self.get_monthly_spending(category, 2)
            month_3 = self.get_monthly_spending(category, 3)
            
            # Calculate three-month average
            three_month_avg = (last_month + month_2 + month_3) / 3
            
            # Calculate recommended budget (weighted average with slight buffer)
            if three_month_avg > 0:
                recommended = three_month_avg * 1.1  # 10% buffer
            else:
                recommended = current_month * 1.2 if current_month > 0 else 100  # Default fallback
            
            # Determine if overspending
            is_overspending = current_month > recommended
            
            # Identify savings opportunities
            savings_opportunity = self.identify_savings_opportunity(category, current_month, recommended)
            
            return BudgetRecommendation(
                category=category,
                recommended_monthly=recommended,
                current_month_spent=current_month,
                last_month_spent=last_month,
                three_month_avg=three_month_avg,
                is_overspending=is_overspending,
                savings_opportunity=savings_opportunity
            )
        except Exception as e:
            print(f"Error calculating budget recommendation for {category}: {e}")
            return BudgetRecommendation(
                category=category,
                recommended_monthly=0,
                current_month_spent=0,
                last_month_spent=0,
                three_month_avg=0,
                is_overspending=False
            )
    
    def identify_savings_opportunity(self, category: str, current_spent: float, recommended: float) -> Optional[str]:
        """Identify potential savings opportunities for a category"""
        try: