```python
#!/usr/bin/env python3
"""
Personal Budget Recommendation Engine

This module implements a rule-based budget recommendation system that analyzes
historical spending data, income patterns, and financial goals to generate
personalized spending limits across different categories.

The engine uses configurable rules and weightings to calculate optimal budget
allocations based on the 50/30/20 rule as a baseline, with adjustments for
individual circumstances and goals.

Features:
- Historical spending analysis and trend detection
- Income pattern recognition and stability assessment
- Goal-based budget adjustments
- Category-specific spending limit recommendations
- Risk assessment and emergency fund calculations

Usage:
    python script.py
"""

import json
import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math


class GoalType(Enum):
    EMERGENCY_FUND = "emergency_fund"
    DEBT_PAYOFF = "debt_payoff"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    MAJOR_PURCHASE = "major_purchase"


class SpendingCategory(Enum):
    HOUSING = "housing"
    FOOD = "food"
    TRANSPORTATION = "transportation"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    DEBT_PAYMENT = "debt_payment"
    SAVINGS = "savings"
    OTHER = "other"


@dataclass
class Transaction:
    date: str
    amount: float
    category: SpendingCategory
    description: str


@dataclass
class IncomeEntry:
    date: str
    amount: float
    source: str
    is_recurring: bool = True


@dataclass
class FinancialGoal:
    goal_type: GoalType
    target_amount: float
    target_date: str
    priority: int  # 1-5, 1 being highest priority
    current_progress: float = 0.0


@dataclass
class BudgetRecommendation:
    category: SpendingCategory
    recommended_limit: float
    current_average: float
    adjustment_reason: str
    confidence_score: float


class BudgetRecommendationEngine:
    """
    Rule-based budget recommendation engine that analyzes financial data
    and generates personalized spending limits.
    """
    
    def __init__(self):
        # Default budget allocation percentages (50/30/20 rule adjusted)
        self.default_allocations = {
            SpendingCategory.HOUSING: 0.25,
            SpendingCategory.FOOD: 0.12,
            SpendingCategory.TRANSPORTATION: 0.08,
            SpendingCategory.UTILITIES: 0.05,
            SpendingCategory.INSURANCE: 0.03,
            SpendingCategory.HEALTHCARE: 0.04,
            SpendingCategory.ENTERTAINMENT: 0.08,
            SpendingCategory.SHOPPING: 0.05,
            SpendingCategory.DEBT_PAYMENT: 0.10,
            SpendingCategory.SAVINGS: 0.20
        }
        
        # Risk adjustment factors
        self.risk_factors = {
            "income_volatility": {"low": 0.9, "medium": 1.0, "high": 1.2},
            "debt_ratio": {"low": 0.9, "medium": 1.0, "high": 1.3},
            "emergency_fund": {"adequate": 0.9, "minimal": 1.1, "none": 1.4}
        }

    def analyze_income_stability(self, income_history: List[IncomeEntry]) -> Dict:
        """Analyze income patterns and stability."""
        try:
            if not income_history:
                return {"stability": "unknown", "average": 0, "volatility": "high"}
            
            monthly_incomes = {}
            for entry in income_history:
                month_key = entry.date[:7]  # YYYY-MM format
                if month_key not in monthly_incomes:
                    monthly_incomes[month_key] = 0
                monthly_incomes[month_key] += entry.amount
            
            income_values = list(monthly_incomes.values())
            if len(income_values) < 2:
                return {"stability": "unknown", "average": income_values[0] if income_values else 0, "volatility": "high"}
            
            avg_income = statistics.mean(income_values)
            income_std = statistics.stdev(income_values)
            cv = income_std / avg_income if avg_income > 0 else 1.0
            
            # Determine volatility based on coefficient of variation
            if cv < 0.1:
                volatility = "low"
            elif cv < 0.25:
                volatility = "medium"
            else:
                volatility = "high"
            
            return {
                "stability": "stable" if cv < 0.2 else "volatile",
                "average": avg_income,
                "volatility": volatility,
                "coefficient_of_variation": cv
            }
        
        except Exception as e:
            print(f"Error analyzing income stability: {e}")
            return {"stability": "unknown", "average": 0, "volatility": "high"}

    def analyze_spending_patterns(self, transactions: List[Transaction]) -> Dict[SpendingCategory, Dict]:
        """Analyze historical spending patterns by category."""
        try:
            category_spending = {}
            
            for transaction in transactions:
                if transaction.category not in category_spending:
                    category_spending[transaction.category] = []
                category_spending[transaction.category].append(transaction.amount)
            
            analysis = {}
            for category, amounts in category_spending.items():
                if amounts:
                    analysis[category] = {
                        "average": statistics.mean(amounts),
                        "total": sum(amounts),
                        "count": len(amounts),
                        "trend": self._calculate_trend(amounts),
                        "volatility": statistics.stdev(amounts) if len(amounts) > 1 else 0
                    }
            
            return analysis
        
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate spending trend (increasing/decreasing/stable)."""
        try:
            if len(values) < 3:
                return "stable"
            
            # Simple linear trend calculation
            x = list(range(len(values)))
            n = len(values)
            
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"
        
        except Exception:
            return "stable"

    def assess_financial_health(self, income_analysis: Dict, spending_analysis: Dict, 
                              goals: List[FinancialGoal]) -> Dict:
        """Assess overall financial health and risk factors."""
        try:
            avg_monthly_income = income_analysis.get("average", 0)
            total_spending = sum(cat_data.get("average", 0) for cat_data in spending_analysis.values())
            
            # Calculate key ratios
            spending_ratio = total_spending / avg_monthly_income if avg_monthly_income > 0 else 1.0
            
            debt_spending = spending_analysis.get(SpendingCategory.DEBT_PAYMENT, {}).get("average", 0)
            debt_ratio = debt_spending / avg_monthly_income if avg_monthly_income > 0 else 0
            
            savings_rate = spending_analysis.get(SpendingCategory.SAVINGS, {}).get("average", 0)
            savings