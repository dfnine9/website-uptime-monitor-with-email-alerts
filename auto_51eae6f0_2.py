```python
#!/usr/bin/env python3
"""
Monthly Budget Insights Generator

This module analyzes monthly spending data against predefined category budgets,
calculates variance percentages, identifies overspending categories, and provides
actionable recommendations for budget optimization.

Features:
- Compares actual spending vs budgeted amounts across categories
- Calculates variance percentages and identifies trends
- Flags overspending categories with severity levels
- Generates actionable recommendations for budget optimization
- Provides summary statistics and insights

Usage: python script.py
"""

import json
import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SpendingLevel(Enum):
    UNDER_BUDGET = "Under Budget"
    NEAR_BUDGET = "Near Budget"
    OVER_BUDGET = "Over Budget"
    SEVERELY_OVER = "Severely Over Budget"


@dataclass
class CategoryAnalysis:
    category: str
    budgeted: float
    actual: float
    variance: float
    variance_percentage: float
    spending_level: SpendingLevel
    recommendation: str


@dataclass
class BudgetInsights:
    month: str
    total_budgeted: float
    total_actual: float
    overall_variance: float
    overall_variance_percentage: float
    categories: List[CategoryAnalysis]
    overspending_categories: List[str]
    top_recommendations: List[str]


class BudgetAnalyzer:
    def __init__(self):
        # Sample budget data - in production, this would come from external sources
        self.budget_data = {
            "housing": 2000.00,
            "food": 600.00,
            "transportation": 400.00,
            "utilities": 200.00,
            "entertainment": 300.00,
            "healthcare": 150.00,
            "shopping": 250.00,
            "savings": 500.00,
            "miscellaneous": 100.00
        }
        
        # Sample actual spending data
        self.actual_spending = {
            "housing": 2100.00,
            "food": 750.00,
            "transportation": 320.00,
            "utilities": 180.00,
            "entertainment": 450.00,
            "healthcare": 125.00,
            "shopping": 380.00,
            "savings": 400.00,
            "miscellaneous": 150.00
        }

    def calculate_variance(self, budgeted: float, actual: float) -> Tuple[float, float]:
        """Calculate variance and variance percentage."""
        try:
            variance = actual - budgeted
            variance_percentage = (variance / budgeted) * 100 if budgeted > 0 else 0
            return variance, variance_percentage
        except (ZeroDivisionError, TypeError) as e:
            print(f"Error calculating variance: {e}")
            return 0.0, 0.0

    def determine_spending_level(self, variance_percentage: float) -> SpendingLevel:
        """Determine spending level based on variance percentage."""
        if variance_percentage <= -10:
            return SpendingLevel.UNDER_BUDGET
        elif variance_percentage <= 5:
            return SpendingLevel.NEAR_BUDGET
        elif variance_percentage <= 20:
            return SpendingLevel.OVER_BUDGET
        else:
            return SpendingLevel.SEVERELY_OVER

    def generate_recommendation(self, category: str, variance_percentage: float, 
                              spending_level: SpendingLevel, actual: float) -> str:
        """Generate actionable recommendations based on spending patterns."""
        try:
            if spending_level == SpendingLevel.UNDER_BUDGET:
                return f"Consider reallocating ${abs(actual * variance_percentage / 100):.2f} from {category} to other categories or increase savings."
            
            elif spending_level == SpendingLevel.NEAR_BUDGET:
                return f"Good control on {category} spending. Monitor closely to stay within budget."
            
            elif spending_level == SpendingLevel.OVER_BUDGET:
                recommendations = {
                    "food": "Try meal planning, cook more at home, and look for grocery discounts.",
                    "entertainment": "Reduce dining out frequency and look for free entertainment options.",
                    "shopping": "Implement a 24-hour wait rule before purchases and review subscriptions.",
                    "transportation": "Consider carpooling, public transit, or combining trips.",
                    "utilities": "Check for energy-saving opportunities and compare providers.",
                    "housing": "Review housing costs and consider refinancing or downsizing if feasible.",
                    "healthcare": "Review insurance coverage and look for generic alternatives.",
                    "miscellaneous": "Track miscellaneous expenses more carefully to identify patterns."
                }
                return recommendations.get(category, f"Reduce {category} spending by {variance_percentage:.1f}% to stay within budget.")
            
            else:  # SEVERELY_OVER
                return f"URGENT: {category} spending is {variance_percentage:.1f}% over budget. Immediate action required - consider cutting non-essential expenses."
                
        except Exception as e:
            print(f"Error generating recommendation for {category}: {e}")
            return "Review spending patterns and adjust accordingly."

    def analyze_category(self, category: str) -> CategoryAnalysis:
        """Analyze a single budget category."""
        try:
            budgeted = self.budget_data.get(category, 0.0)
            actual = self.actual_spending.get(category, 0.0)
            
            variance, variance_percentage = self.calculate_variance(budgeted, actual)
            spending_level = self.determine_spending_level(variance_percentage)
            recommendation = self.generate_recommendation(category, variance_percentage, 
                                                        spending_level, actual)
            
            return CategoryAnalysis(
                category=category,
                budgeted=budgeted,
                actual=actual,
                variance=variance,
                variance_percentage=variance_percentage,
                spending_level=spending_level,
                recommendation=recommendation
            )
            
        except Exception as e:
            print(f"Error analyzing category {category}: {e}")
            return CategoryAnalysis(category, 0.0, 0.0, 0.0, 0.0, 
                                  SpendingLevel.NEAR_BUDGET, "Analysis error occurred.")

    def generate_insights(self) -> BudgetInsights:
        """Generate comprehensive budget insights."""
        try:
            current_month = datetime.datetime.now().strftime("%B %Y")
            
            # Analyze all categories
            category_analyses = []
            for category in self.budget_data.keys():
                analysis = self.analyze_category(category)
                category_analyses.append(analysis)
            
            # Calculate totals
            total_budgeted = sum(self.budget_data.values())
            total_actual = sum(self.actual_spending.values())
            overall_variance = total_actual - total_budgeted
            overall_variance_percentage = (overall_variance / total_budgeted) * 100 if total_budgeted > 0 else 0
            
            # Identify overspending categories
            overspending_categories = [
                analysis.category for analysis in category_analyses
                if analysis.spending_level in [SpendingLevel.OVER_BUDGET, SpendingLevel.SEVERELY_OVER]
            ]
            
            # Generate top recommendations
            top_recommendations = []
            severely_over = [a for a in category_analyses if a.spending_level == SpendingLevel.SEVERELY_OVER]
            over_budget = [a for a in category_analyses if a.spending_level == SpendingLevel.OVER_BUDGET]
            
            # Prioritize severely over budget items
            for analysis in severely_over[:3]:
                top_recommendations.append(f"🚨 {analysis.category.title()}: {analysis.recommendation}")
            
            # Add other over-budget items
            for analysis in over_budget[:2]:
                if len(top_recommendations) < 5:
                    top_recommendations.append(f"⚠️ {analysis.category.title()}: {analysis.recommendation}")
            
            # Add general recommendations if under total budget
            if