```python
"""
Budget Recommendation Engine

A comprehensive budget analysis and recommendation system that:
1. Compares actual spending against category benchmarks
2. Applies the 50/30/20 budgeting rule (needs/wants/savings)
3. Generates personalized monthly budget suggestions with specific dollar amounts

Features:
- Category-based spending analysis with industry benchmarks
- 50/30/20 rule implementation for balanced budgeting
- Variance analysis between actual and recommended spending
- Personalized recommendations based on income and spending patterns
- Self-contained implementation using only standard library
"""

import json
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class BudgetCategory(Enum):
    """Budget category classifications"""
    # Needs (50%)
    HOUSING = "housing"
    UTILITIES = "utilities"
    GROCERIES = "groceries"
    TRANSPORTATION = "transportation"
    INSURANCE = "insurance"
    MINIMUM_DEBT = "minimum_debt_payments"
    
    # Wants (30%)
    DINING_OUT = "dining_out"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    HOBBIES = "hobbies"
    SUBSCRIPTIONS = "subscriptions"
    PERSONAL_CARE = "personal_care"
    
    # Savings (20%)
    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT = "retirement"
    INVESTMENTS = "investments"
    DEBT_PAYOFF = "debt_payoff"


@dataclass
class CategoryBenchmark:
    """Benchmark data for budget categories"""
    name: str
    category_type: str  # "needs", "wants", or "savings"
    recommended_percentage: float
    min_percentage: float
    max_percentage: float


@dataclass
class SpendingData:
    """User's actual spending data"""
    category: BudgetCategory
    amount: float
    description: str = ""


@dataclass
class BudgetRecommendation:
    """Budget recommendation for a category"""
    category: BudgetCategory
    recommended_amount: float
    actual_amount: float
    variance: float
    variance_percentage: float
    status: str  # "over", "under", "on_track"
    recommendation: str


class BudgetEngine:
    """Main budget recommendation engine"""
    
    def __init__(self):
        self.benchmarks = self._initialize_benchmarks()
        
    def _initialize_benchmarks(self) -> Dict[BudgetCategory, CategoryBenchmark]:
        """Initialize category benchmarks based on financial best practices"""
        return {
            # Needs categories (50% total)
            BudgetCategory.HOUSING: CategoryBenchmark("Housing", "needs", 0.25, 0.20, 0.30),
            BudgetCategory.UTILITIES: CategoryBenchmark("Utilities", "needs", 0.08, 0.05, 0.12),
            BudgetCategory.GROCERIES: CategoryBenchmark("Groceries", "needs", 0.10, 0.08, 0.15),
            BudgetCategory.TRANSPORTATION: CategoryBenchmark("Transportation", "needs", 0.15, 0.10, 0.20),
            BudgetCategory.INSURANCE: CategoryBenchmark("Insurance", "needs", 0.05, 0.03, 0.08),
            BudgetCategory.MINIMUM_DEBT: CategoryBenchmark("Minimum Debt Payments", "needs", 0.05, 0.00, 0.15),
            
            # Wants categories (30% total)
            BudgetCategory.DINING_OUT: CategoryBenchmark("Dining Out", "wants", 0.08, 0.03, 0.12),
            BudgetCategory.ENTERTAINMENT: CategoryBenchmark("Entertainment", "wants", 0.05, 0.02, 0.08),
            BudgetCategory.SHOPPING: CategoryBenchmark("Shopping", "wants", 0.07, 0.03, 0.10),
            BudgetCategory.HOBBIES: CategoryBenchmark("Hobbies", "wants", 0.04, 0.01, 0.08),
            BudgetCategory.SUBSCRIPTIONS: CategoryBenchmark("Subscriptions", "wants", 0.03, 0.01, 0.05),
            BudgetCategory.PERSONAL_CARE: CategoryBenchmark("Personal Care", "wants", 0.03, 0.02, 0.05),
            
            # Savings categories (20% total)
            BudgetCategory.EMERGENCY_FUND: CategoryBenchmark("Emergency Fund", "savings", 0.05, 0.03, 0.10),
            BudgetCategory.RETIREMENT: CategoryBenchmark("Retirement", "savings", 0.10, 0.05, 0.15),
            BudgetCategory.INVESTMENTS: CategoryBenchmark("Investments", "savings", 0.03, 0.00, 0.08),
            BudgetCategory.DEBT_PAYOFF: CategoryBenchmark("Additional Debt Payoff", "savings", 0.02, 0.00, 0.10),
        }
    
    def analyze_spending(self, monthly_income: float, spending_data: List[SpendingData]) -> List[BudgetRecommendation]:
        """Analyze spending and generate recommendations"""
        try:
            if monthly_income <= 0:
                raise ValueError("Monthly income must be positive")
            
            # Create spending dictionary
            actual_spending = {data.category: data.amount for data in spending_data}
            
            recommendations = []
            
            for category, benchmark in self.benchmarks.items():
                actual_amount = actual_spending.get(category, 0.0)
                recommended_amount = monthly_income * benchmark.recommended_percentage
                
                variance = actual_amount - recommended_amount
                variance_percentage = (variance / recommended_amount * 100) if recommended_amount > 0 else 0
                
                # Determine status
                if abs(variance_percentage) <= 10:
                    status = "on_track"
                elif variance > 0:
                    status = "over"
                else:
                    status = "under"
                
                # Generate recommendation text
                recommendation_text = self._generate_recommendation(
                    category, benchmark, actual_amount, recommended_amount, 
                    variance, variance_percentage, status, monthly_income
                )
                
                recommendations.append(BudgetRecommendation(
                    category=category,
                    recommended_amount=recommended_amount,
                    actual_amount=actual_amount,
                    variance=variance,
                    variance_percentage=variance_percentage,
                    status=status,
                    recommendation=recommendation_text
                ))
            
            return recommendations
            
        except Exception as e:
            print(f"Error analyzing spending: {e}")
            return []
    
    def _generate_recommendation(self, category: BudgetCategory, benchmark: CategoryBenchmark,
                               actual: float, recommended: float, variance: float,
                               variance_pct: float, status: str, income: float) -> str:
        """Generate personalized recommendation text"""
        try:
            if status == "on_track":
                return f"Good job! Your {benchmark.name.lower()} spending is well-balanced."
            
            elif status == "over":
                if variance_pct > 50:
                    severity = "significantly"
                elif variance_pct > 25:
                    severity = "moderately"
                else:
                    severity = "slightly"
                
                suggestion = self._get_reduction_suggestion(category, variance)
                return f"You're spending {severity} more than recommended on {benchmark.name.lower()}. " \
                       f"Consider reducing by ${variance:.0f}/month. {suggestion}"
            
            else:  # under
                if benchmark.category_type == "savings":
                    return f"Great opportunity! You could increase your {benchmark.name.lower()} " \
                           f"by ${abs(variance):.0f}/month to reach the recommended amount."
                else:
                    return f"You're spending less than typical on {benchmark.name.lower()}. " \
                           f"This could free up ${abs(variance)