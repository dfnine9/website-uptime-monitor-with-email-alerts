```python
"""
Personal Budget Recommendation Engine

A comprehensive budget planning system that analyzes historical spending patterns,
income data, and user-defined savings goals to generate personalized monthly budget
recommendations. Uses both rule-based algorithms and simple machine learning techniques
to optimize budget allocations across different spending categories.

Features:
- Historical spending pattern analysis
- Income trend analysis
- Configurable savings goals
- Category-wise budget recommendations
- Emergency fund planning
- Debt payoff suggestions
- Seasonal spending adjustments

Usage:
    python script.py

The script generates sample data and provides budget recommendations based on
intelligent analysis of spending habits and financial goals.
"""

import json
import statistics
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Transaction:
    """Represents a financial transaction"""
    date: str
    amount: float
    category: str
    description: str
    type: str  # 'income' or 'expense'


@dataclass
class SavingsGoal:
    """Represents a savings goal"""
    name: str
    target_amount: float
    target_date: str
    current_amount: float = 0.0
    priority: int = 1  # 1-5, where 1 is highest priority


@dataclass
class BudgetRecommendation:
    """Budget recommendation for a category"""
    category: str
    recommended_amount: float
    current_average: float
    variance: float
    confidence: float
    reasoning: str


class BudgetEngine:
    """Main budget recommendation engine"""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.savings_goals: List[SavingsGoal] = []
        self.category_weights = {
            'housing': 0.30,
            'food': 0.15,
            'transportation': 0.15,
            'utilities': 0.10,
            'healthcare': 0.08,
            'entertainment': 0.05,
            'shopping': 0.07,
            'miscellaneous': 0.10
        }
    
    def add_transaction(self, transaction: Transaction):
        """Add a transaction to the dataset"""
        try:
            self.transactions.append(transaction)
        except Exception as e:
            print(f"Error adding transaction: {e}")
    
    def add_savings_goal(self, goal: SavingsGoal):
        """Add a savings goal"""
        try:
            self.savings_goals.append(goal)
        except Exception as e:
            print(f"Error adding savings goal: {e}")
    
    def analyze_spending_patterns(self) -> Dict[str, Dict[str, float]]:
        """Analyze historical spending patterns by category"""
        try:
            category_data = defaultdict(list)
            
            for transaction in self.transactions:
                if transaction.type == 'expense':
                    category_data[transaction.category].append(transaction.amount)
            
            patterns = {}
            for category, amounts in category_data.items():
                if amounts:
                    patterns[category] = {
                        'average': statistics.mean(amounts),
                        'median': statistics.median(amounts),
                        'variance': statistics.variance(amounts) if len(amounts) > 1 else 0,
                        'total': sum(amounts),
                        'count': len(amounts),
                        'min': min(amounts),
                        'max': max(amounts)
                    }
            
            return patterns
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}
    
    def analyze_income_trends(self) -> Dict[str, float]:
        """Analyze income trends and stability"""
        try:
            income_transactions = [t for t in self.transactions if t.type == 'income']
            
            if not income_transactions:
                return {'monthly_average': 0, 'variance': 0, 'trend': 0}
            
            monthly_income = defaultdict(float)
            for transaction in income_transactions:
                month_key = transaction.date[:7]  # YYYY-MM
                monthly_income[month_key] += transaction.amount
            
            monthly_amounts = list(monthly_income.values())
            
            # Simple trend calculation
            trend = 0
            if len(monthly_amounts) > 1:
                first_half = monthly_amounts[:len(monthly_amounts)//2]
                second_half = monthly_amounts[len(monthly_amounts)//2:]
                if first_half and second_half:
                    trend = statistics.mean(second_half) - statistics.mean(first_half)
            
            return {
                'monthly_average': statistics.mean(monthly_amounts) if monthly_amounts else 0,
                'variance': statistics.variance(monthly_amounts) if len(monthly_amounts) > 1 else 0,
                'trend': trend
            }
        except Exception as e:
            print(f"Error analyzing income trends: {e}")
            return {'monthly_average': 0, 'variance': 0, 'trend': 0}
    
    def calculate_savings_requirements(self) -> float:
        """Calculate monthly savings needed for goals"""
        try:
            total_monthly_savings = 0
            current_date = datetime.now()
            
            for goal in self.savings_goals:
                try:
                    target_date = datetime.strptime(goal.target_date, '%Y-%m-%d')
                    months_remaining = max(1, (target_date - current_date).days / 30.44)
                    
                    remaining_amount = goal.target_amount - goal.current_amount
                    monthly_required = remaining_amount / months_remaining
                    
                    # Apply priority weighting
                    priority_multiplier = 2.0 - (goal.priority - 1) * 0.2
                    total_monthly_savings += monthly_required * priority_multiplier
                    
                except ValueError as ve:
                    print(f"Error parsing date for goal {goal.name}: {ve}")
                    continue
            
            return total_monthly_savings
        except Exception as e:
            print(f"Error calculating savings requirements: {e}")
            return 0
    
    def apply_ml_optimization(self, spending_patterns: Dict[str, Dict[str, float]], 
                            income_data: Dict[str, float]) -> Dict[str, float]:
        """Apply machine learning-inspired optimization"""
        try:
            optimized_allocations = {}
            monthly_income = income_data['monthly_average']
            
            if monthly_income <= 0:
                return optimized_allocations
            
            # Calculate total current spending
            total_spending = sum(pattern['average'] for pattern in spending_patterns.values())
            
            # Apply variance penalty - categories with high variance get slight reduction
            for category, pattern in spending_patterns.items():
                base_allocation = pattern['average']
                
                # Variance penalty (reduce budget for highly variable categories)
                if pattern['variance'] > 0:
                    variance_coefficient = min(0.2, pattern['variance'] / base_allocation)
                    variance_penalty = base_allocation * variance_coefficient * 0.1
                else:
                    variance_penalty = 0
                
                # Income scaling
                income_ratio = monthly_income / max(total_spending, 1)
                scaled_allocation = base_allocation * min(income_ratio, 1.2)
                
                # Apply category importance weights
                weight = self.category_weights.get(category, 0.05)
                weighted_allocation = scaled_allocation * (1 + weight)
                
                optimized_allocations[category] = max(0, weighted_allocation - variance_penalty)
            
            return optimized_allocations
        except Exception as e:
            print(f"Error in ML optimization: {e}")
            return {}
    
    def generate_recommendations(self) -> List[BudgetRecommendation]:
        """Generate personalized budget recommendations"""
        try:
            recommendations = []
            
            # Analyze data
            spending_patterns = self.analyze_spending_patterns()
            income_data = self.analyze_income_trends()
            savings_needed = self.calculate_savings_requirements()
            
            if