```python
"""
Automated Budget Recommendation Engine

This module implements a budget recommendation system that suggests spending limits
per category based on income percentage rules (variations of the 50/30/20 rule)
and historical spending patterns. The engine analyzes past spending behavior and
provides personalized budget recommendations.

The 50/30/20 rule allocates:
- 50% for needs (housing, utilities, groceries, transportation)
- 30% for wants (entertainment, dining out, hobbies)
- 20% for savings and debt repayment

The engine supports multiple rule variations and adapts recommendations based on
historical spending patterns to provide more realistic and achievable budgets.
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class BudgetRecommendationEngine:
    """
    A budget recommendation engine that analyzes spending patterns and suggests
    optimal budget allocations based on income percentage rules.
    """
    
    def __init__(self):
        self.budget_rules = {
            "50_30_20": {"needs": 50, "wants": 30, "savings": 20},
            "60_20_20": {"needs": 60, "wants": 20, "savings": 20},
            "70_20_10": {"needs": 70, "wants": 20, "savings": 10},
            "40_30_30": {"needs": 40, "wants": 30, "savings": 30}
        }
        
        self.category_mapping = {
            "needs": ["housing", "utilities", "groceries", "transportation", "insurance", "minimum_debt_payments"],
            "wants": ["entertainment", "dining_out", "hobbies", "shopping", "subscriptions"],
            "savings": ["emergency_fund", "retirement", "investments", "extra_debt_payments"]
        }
    
    def generate_sample_data(self) -> Tuple[float, List[Dict]]:
        """Generate sample income and spending data for demonstration."""
        monthly_income = 5000.0
        
        # Generate 6 months of sample spending data
        sample_spending = []
        base_spending = {
            "housing": 1200, "utilities": 200, "groceries": 400, "transportation": 300,
            "insurance": 150, "minimum_debt_payments": 250, "entertainment": 300,
            "dining_out": 250, "hobbies": 150, "shopping": 200, "subscriptions": 50,
            "emergency_fund": 300, "retirement": 400, "investments": 200, "extra_debt_payments": 100
        }
        
        for month in range(6):
            monthly_data = {}
            for category, base_amount in base_spending.items():
                # Add some variation (±20%) to make it realistic
                variation = base_amount * (0.8 + 0.4 * (month % 3) / 2)
                monthly_data[category] = round(variation, 2)
            sample_spending.append(monthly_data)
        
        return monthly_income, sample_spending
    
    def analyze_spending_patterns(self, historical_data: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze historical spending patterns to calculate averages and trends.
        
        Args:
            historical_data: List of monthly spending dictionaries
            
        Returns:
            Dictionary with spending analysis including averages and trends
        """
        try:
            if not historical_data:
                raise ValueError("No historical data provided")
            
            analysis = {}
            all_categories = set()
            
            # Collect all categories from historical data
            for month_data in historical_data:
                all_categories.update(month_data.keys())
            
            for category in all_categories:
                category_data = []
                for month_data in historical_data:
                    if category in month_data:
                        category_data.append(month_data[category])
                
                if category_data:
                    analysis[category] = {
                        "average": round(statistics.mean(category_data), 2),
                        "median": round(statistics.median(category_data), 2),
                        "min": min(category_data),
                        "max": max(category_data),
                        "trend": self._calculate_trend(category_data)
                    }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}
    
    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate spending trend (increasing, decreasing, stable)."""
        try:
            if len(data) < 2:
                return "stable"
            
            first_half_avg = statistics.mean(data[:len(data)//2])
            second_half_avg = statistics.mean(data[len(data)//2:])
            
            change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            
            if change_percent > 10:
                return "increasing"
            elif change_percent < -10:
                return "decreasing"
            else:
                return "stable"
                
        except Exception:
            return "stable"
    
    def calculate_category_totals(self, spending_analysis: Dict) -> Dict[str, float]:
        """Calculate total spending by budget category (needs, wants, savings)."""
        category_totals = {"needs": 0, "wants": 0, "savings": 0}
        
        try:
            for budget_category, categories in self.category_mapping.items():
                total = 0
                for category in categories:
                    if category in spending_analysis:
                        total += spending_analysis[category]["average"]
                category_totals[budget_category] = round(total, 2)
            
            return category_totals
            
        except Exception as e:
            print(f"Error calculating category totals: {e}")
            return category_totals
    
    def recommend_budget(self, income: float, historical_data: List[Dict], 
                        rule_name: str = "50_30_20") -> Dict:
        """
        Generate budget recommendations based on income and spending patterns.
        
        Args:
            income: Monthly income
            historical_data: Historical spending data
            rule_name: Budget rule to use (50_30_20, 60_20_20, etc.)
            
        Returns:
            Dictionary with budget recommendations and analysis
        """
        try:
            if income <= 0:
                raise ValueError("Income must be positive")
            
            if rule_name not in self.budget_rules:
                raise ValueError(f"Unknown budget rule: {rule_name}")
            
            # Analyze historical spending
            spending_analysis = self.analyze_spending_patterns(historical_data)
            current_totals = self.calculate_category_totals(spending_analysis)
            
            # Get budget rule percentages
            rule = self.budget_rules[rule_name]
            
            # Calculate recommended allocations
            recommended_allocations = {}
            for category, percentage in rule.items():
                recommended_allocations[category] = round(income * (percentage / 100), 2)
            
            # Calculate current spending percentages
            current_percentages = {}
            total_current_spending = sum(current_totals.values())
            
            for category, amount in current_totals.items():
                if total_current_spending > 0:
                    current_percentages[category] = round((amount / income) * 100, 1)
                else:
                    current_percentages[category] = 0
            
            # Generate recommendations
            recommendations = {}
            for category in ["needs", "wants", "savings"]:
                current_amount = current_totals.get(category, 0)
                recommended_amount = recommended_allocations.get(category, 0)
                difference = recommended_amount - current_amount
                
                recommendations[category] = {
                    "current_amount": current_amount,
                    "current_percentage": current_percentages.get(category, 0),
                    "recommended_amount": recommended_amount,
                    "recommended_percentage": rule.get(category, 0),
                    "difference": round(difference, 2),
                    "status": "over_budget" if difference < 0