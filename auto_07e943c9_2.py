```python
"""
Budget Recommendation Engine

A comprehensive personal finance tool that analyzes spending patterns against the 50/30/20 rule:
- 50% for needs (housing, utilities, groceries, transportation, insurance, minimum debt payments)
- 30% for wants (entertainment, dining out, hobbies, subscriptions, shopping)
- 20% for savings and debt repayment (emergency fund, retirement, extra debt payments)

The engine identifies overspending categories and provides specific, actionable reduction
suggestions with target amounts to help users achieve optimal budget allocation.
"""

import json
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BudgetCategory:
    """Represents a budget category with spending and target information."""
    name: str
    current_spending: float
    target_percentage: float
    category_type: str  # 'needs', 'wants', or 'savings'


@dataclass
class ReductionSuggestion:
    """Represents a specific suggestion for reducing spending in a category."""
    category: str
    current_amount: float
    target_amount: float
    reduction_needed: float
    specific_suggestions: List[str]
    priority: str  # 'high', 'medium', 'low'


class BudgetRecommendationEngine:
    """Main engine for analyzing budgets and generating recommendations."""
    
    def __init__(self):
        self.fifty_thirty_twenty_rule = {
            'needs': 0.50,
            'wants': 0.30,
            'savings': 0.20
        }
        
        # Default category mappings
        self.default_categories = {
            'needs': {
                'housing': 0.25,
                'utilities': 0.08,
                'groceries': 0.10,
                'transportation': 0.15,
                'insurance': 0.05,
                'minimum_debt_payments': 0.10,
                'healthcare': 0.05,
                'phone': 0.03
            },
            'wants': {
                'entertainment': 0.08,
                'dining_out': 0.10,
                'hobbies': 0.05,
                'subscriptions': 0.04,
                'shopping': 0.10,
                'personal_care': 0.03
            },
            'savings': {
                'emergency_fund': 0.10,
                'retirement': 0.10,
                'investments': 0.05,
                'extra_debt_payments': 0.05
            }
        }
        
        # Reduction suggestions database
        self.reduction_strategies = {
            'dining_out': [
                "Cook more meals at home - aim for 5 home-cooked meals per week",
                "Use meal planning apps to reduce impulse food orders",
                "Set a weekly dining out limit and stick to it",
                "Look for restaurant deals and happy hour specials",
                "Pack lunches for work instead of buying daily"
            ],
            'entertainment': [
                "Cancel unused streaming subscriptions",
                "Look for free community events and activities",
                "Use library resources for books, movies, and events",
                "Share subscription costs with family members",
                "Attend matinee showings for cheaper movie tickets"
            ],
            'shopping': [
                "Implement a 24-hour waiting period for non-essential purchases",
                "Create and stick to shopping lists",
                "Unsubscribe from retailer email lists and social media",
                "Shop with cash only to limit overspending",
                "Focus on buying quality items that last longer"
            ],
            'subscriptions': [
                "Audit all recurring subscriptions monthly",
                "Cancel services you haven't used in 30 days",
                "Downgrade to lower-tier plans where possible",
                "Share family plans with household members",
                "Use free alternatives when available"
            ],
            'utilities': [
                "Adjust thermostat settings by 2-3 degrees",
                "Switch to LED bulbs and unplug unused electronics",
                "Take shorter showers and fix any leaks promptly",
                "Use programmable thermostats and power strips",
                "Consider energy-efficient appliances when replacing old ones"
            ],
            'transportation': [
                "Use public transportation or carpooling when possible",
                "Combine errands into single trips",
                "Walk or bike for short distances",
                "Maintain your vehicle regularly for better fuel efficiency",
                "Consider a more fuel-efficient vehicle if replacement is due"
            ],
            'groceries': [
                "Plan meals around sales and seasonal produce",
                "Use coupons and store loyalty programs",
                "Buy generic brands instead of name brands",
                "Shop the perimeter of the store first",
                "Avoid shopping when hungry to reduce impulse purchases"
            ]
        }

    def analyze_budget(self, income: float, expenses: Dict[str, float]) -> Dict:
        """
        Analyze current spending against the 50/30/20 rule.
        
        Args:
            income: Monthly take-home income
            expenses: Dictionary of category names and spending amounts
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        try:
            if income <= 0:
                raise ValueError("Income must be positive")
            
            # Calculate current category totals
            current_totals = self._calculate_category_totals(expenses)
            
            # Calculate target amounts based on 50/30/20 rule
            target_amounts = {
                'needs': income * self.fifty_thirty_twenty_rule['needs'],
                'wants': income * self.fifty_thirty_twenty_rule['wants'],
                'savings': income * self.fifty_thirty_twenty_rule['savings']
            }
            
            # Identify overspending
            overspending = {}
            for category_type in ['needs', 'wants', 'savings']:
                current = current_totals.get(category_type, 0)
                target = target_amounts[category_type]
                if current > target:
                    overspending[category_type] = current - target
            
            # Generate specific reduction suggestions
            suggestions = self._generate_reduction_suggestions(
                income, expenses, current_totals, target_amounts
            )
            
            # Calculate overall budget health score
            health_score = self._calculate_budget_health(current_totals, target_amounts, income)
            
            return {
                'analysis_date': datetime.now().isoformat(),
                'income': income,
                'current_spending': current_totals,
                'target_spending': target_amounts,
                'overspending': overspending,
                'total_overspending': sum(overspending.values()),
                'suggestions': [asdict(s) for s in suggestions],
                'budget_health_score': health_score,
                'summary': self._generate_summary(current_totals, target_amounts, overspending)
            }
            
        except Exception as e:
            return {'error': f"Budget analysis failed: {str(e)}"}

    def _calculate_category_totals(self, expenses: Dict[str, float]) -> Dict[str, float]:
        """Calculate total spending by category type (needs, wants, savings)."""
        totals = {'needs': 0, 'wants': 0, 'savings': 0}
        
        # Category mapping for common expense names
        category_mapping = {
            'housing': 'needs', 'rent': 'needs', 'mortgage': 'needs',
            'utilities': 'needs', 'electricity': 'needs', 'gas': 'needs', 'water': 'needs',
            'groceries': 'needs', 'food': 'needs',
            'transportation': 'needs', 'car_payment': 'needs', 'gas_fuel': 'needs',
            'insurance': 'needs', 'health_insurance': 'needs', 'car_insurance': 'needs',
            'phone': 'needs', 'internet': 'needs',
            'minimum_debt_payments': 'needs', 'credit_card_minimum': 'needs',
            'healthcare': 'needs', 'medical': 'needs',
            
            'dining_out': 'wants', 'restaurants': 'wants',
            'entertainment': 'wants', 'movies': 'wants', 'concerts