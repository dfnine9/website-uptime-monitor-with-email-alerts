```python
"""
Budget Recommendation Engine

This module analyzes historical spending data to generate personalized monthly budget 
suggestions. It processes income vs expenses, establishes category-wise spending limits, 
and accounts for seasonal spending patterns to provide intelligent budget recommendations.

Features:
- Historical spending analysis
- Income-to-expense ratio optimization
- Category-wise budget allocation
- Seasonal pattern recognition
- Personalized recommendations based on spending behavior
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import calendar


class BudgetRecommendationEngine:
    def __init__(self):
        self.spending_data = []
        self.income_data = []
        self.categories = [
            "Housing", "Transportation", "Food", "Utilities", "Healthcare",
            "Entertainment", "Shopping", "Education", "Savings", "Miscellaneous"
        ]
        self.seasonal_multipliers = {
            "Housing": {"spring": 1.0, "summer": 1.05, "fall": 1.0, "winter": 1.1},
            "Transportation": {"spring": 1.0, "summer": 1.15, "fall": 1.0, "winter": 0.9},
            "Food": {"spring": 1.0, "summer": 1.1, "fall": 1.05, "winter": 1.15},
            "Utilities": {"spring": 0.9, "summer": 1.2, "fall": 1.0, "winter": 1.3},
            "Healthcare": {"spring": 1.0, "summer": 1.0, "fall": 1.1, "winter": 1.2},
            "Entertainment": {"spring": 1.1, "summer": 1.3, "fall": 1.0, "winter": 0.8},
            "Shopping": {"spring": 1.0, "summer": 1.1, "fall": 1.0, "winter": 1.4},
            "Education": {"spring": 1.2, "summer": 0.8, "fall": 1.3, "winter": 1.0},
            "Savings": {"spring": 1.0, "summer": 1.0, "fall": 1.0, "winter": 1.0},
            "Miscellaneous": {"spring": 1.0, "summer": 1.1, "fall": 1.0, "winter": 1.1}
        }

    def generate_sample_data(self, months: int = 12) -> None:
        """Generate sample historical spending and income data"""
        try:
            base_income = 5000
            base_expenses = {
                "Housing": 1200, "Transportation": 400, "Food": 600, "Utilities": 200,
                "Healthcare": 300, "Entertainment": 300, "Shopping": 250, "Education": 150,
                "Savings": 800, "Miscellaneous": 200
            }
            
            for i in range(months):
                month_date = datetime.now() - timedelta(days=30 * i)
                season = self._get_season(month_date.month)
                
                # Generate income with some variation
                monthly_income = base_income + ((-1) ** i) * (i * 50) + (i * 25)
                self.income_data.append({
                    "date": month_date.strftime("%Y-%m"),
                    "amount": monthly_income
                })
                
                # Generate expenses with seasonal variations
                monthly_expenses = {}
                for category, base_amount in base_expenses.items():
                    seasonal_mult = self.seasonal_multipliers[category][season]
                    variation = ((-1) ** i) * (i * 5) + (i * 2)
                    monthly_expenses[category] = max(0, base_amount * seasonal_mult + variation)
                
                self.spending_data.append({
                    "date": month_date.strftime("%Y-%m"),
                    "expenses": monthly_expenses
                })
                
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise

    def _get_season(self, month: int) -> str:
        """Determine season based on month"""
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"

    def analyze_spending_patterns(self) -> Dict:
        """Analyze historical spending patterns"""
        try:
            if not self.spending_data:
                raise ValueError("No spending data available for analysis")
            
            analysis = {
                "avg_monthly_spending": {},
                "spending_trends": {},
                "seasonal_patterns": {},
                "total_avg_expenses": 0
            }
            
            # Calculate average monthly spending by category
            category_totals = {category: [] for category in self.categories}
            total_expenses = []
            
            for record in self.spending_data:
                month_total = 0
                for category, amount in record["expenses"].items():
                    if category in category_totals:
                        category_totals[category].append(amount)
                        month_total += amount
                total_expenses.append(month_total)
            
            # Calculate averages and trends
            for category, amounts in category_totals.items():
                if amounts:
                    analysis["avg_monthly_spending"][category] = statistics.mean(amounts)
                    
                    # Simple trend analysis (comparing first half vs second half)
                    if len(amounts) >= 4:
                        first_half = statistics.mean(amounts[:len(amounts)//2])
                        second_half = statistics.mean(amounts[len(amounts)//2:])
                        trend = (second_half - first_half) / first_half * 100
                        analysis["spending_trends"][category] = trend
            
            analysis["total_avg_expenses"] = statistics.mean(total_expenses) if total_expenses else 0
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}

    def analyze_income_patterns(self) -> Dict:
        """Analyze historical income patterns"""
        try:
            if not self.income_data:
                raise ValueError("No income data available for analysis")
            
            incomes = [record["amount"] for record in self.income_data]
            
            return {
                "avg_monthly_income": statistics.mean(incomes),
                "min_income": min(incomes),
                "max_income": max(incomes),
                "income_stability": statistics.stdev(incomes) if len(incomes) > 1 else 0
            }
            
        except Exception as e:
            print(f"Error analyzing income patterns: {e}")
            return {}

    def calculate_seasonal_adjustments(self, month: int) -> Dict[str, float]:
        """Calculate seasonal adjustments for given month"""
        try:
            season = self._get_season(month)
            adjustments = {}
            
            for category in self.categories:
                if category in self.seasonal_multipliers:
                    adjustments[category] = self.seasonal_multipliers[category][season]
                else:
                    adjustments[category] = 1.0
            
            return adjustments
            
        except Exception as e:
            print(f"Error calculating seasonal adjustments: {e}")
            return {category: 1.0 for category in self.categories}

    def generate_budget_recommendations(self, target_month: Optional[int] = None) -> Dict:
        """Generate personalized budget recommendations"""
        try:
            if target_month is None:
                target_month = datetime.now().month
            
            spending_analysis = self.analyze_spending_patterns()
            income_analysis = self.analyze_income_patterns()
            seasonal_adjustments = self.calculate_seasonal_adjustments(target_month)
            
            if not spending_analysis or not income_analysis:
                raise ValueError("Insufficient data for generating recommendations")
            
            recommendations = {
                "target_month": calendar.month_name[target_month],
                "projected_income