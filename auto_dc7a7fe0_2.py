```python
"""
Personal Budget Recommendation Engine

This module implements a comprehensive budget recommendation system that analyzes
historical spending data, income ratios, and user-defined category priorities to
generate personalized spending limits using statistical analysis.

Features:
- Historical spending pattern analysis with trend detection
- Income-based budget allocation using proven financial ratios
- Category prioritization with weighted scoring
- Statistical anomaly detection for spending behavior
- Confidence intervals for budget recommendations
- Risk-based budget adjustments

The engine uses statistical methods including moving averages, standard deviation
analysis, and percentile-based recommendations to provide data-driven budget
suggestions that adapt to individual spending patterns.
"""

import json
import statistics
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random

class BudgetRecommendationEngine:
    """
    A statistical budget recommendation engine that analyzes spending patterns
    and generates personalized budget limits based on historical data.
    """
    
    def __init__(self):
        self.categories = [
            "housing", "transportation", "food", "utilities", "entertainment",
            "healthcare", "shopping", "education", "savings", "debt_payment"
        ]
        
        # Standard financial ratios (50/30/20 rule variations)
        self.base_ratios = {
            "housing": 0.28,
            "transportation": 0.15,
            "food": 0.12,
            "utilities": 0.08,
            "entertainment": 0.08,
            "healthcare": 0.05,
            "shopping": 0.08,
            "education": 0.04,
            "savings": 0.20,
            "debt_payment": 0.12
        }
    
    def generate_sample_data(self, months: int = 12) -> Tuple[float, List[Dict], Dict[str, int]]:
        """Generate realistic sample financial data for demonstration."""
        try:
            # Generate monthly income with slight variation
            base_income = random.uniform(4000, 8000)
            monthly_income = base_income * random.uniform(0.95, 1.05)
            
            # Generate historical spending data
            historical_data = []
            current_date = datetime.now()
            
            for i in range(months):
                month_date = current_date - timedelta(days=30 * i)
                month_data = {
                    "date": month_date.strftime("%Y-%m"),
                    "categories": {}
                }
                
                # Generate spending for each category with some randomness
                for category in self.categories:
                    base_amount = monthly_income * self.base_ratios[category]
                    # Add seasonal and random variations
                    variation = random.uniform(0.7, 1.3)
                    if category == "entertainment" and month_date.month in [11, 12]:
                        variation *= 1.4  # Holiday spending
                    
                    month_data["categories"][category] = round(base_amount * variation, 2)
                
                historical_data.append(month_data)
            
            # Generate category priorities (1-10 scale)
            priorities = {category: random.randint(3, 10) for category in self.categories}
            priorities["savings"] = 10  # Always prioritize savings
            priorities["housing"] = random.randint(8, 10)  # Essential
            
            return monthly_income, historical_data, priorities
            
        except Exception as e:
            raise Exception(f"Error generating sample data: {str(e)}")
    
    def analyze_spending_patterns(self, historical_data: List[Dict]) -> Dict:
        """Perform statistical analysis on historical spending patterns."""
        try:
            patterns = {}
            
            for category in self.categories:
                amounts = []
                for month in historical_data:
                    if category in month["categories"]:
                        amounts.append(month["categories"][category])
                
                if amounts:
                    patterns[category] = {
                        "mean": statistics.mean(amounts),
                        "median": statistics.median(amounts),
                        "stdev": statistics.stdev(amounts) if len(amounts) > 1 else 0,
                        "min": min(amounts),
                        "max": max(amounts),
                        "trend": self._calculate_trend(amounts),
                        "volatility": self._calculate_volatility(amounts)
                    }
                else:
                    patterns[category] = {
                        "mean": 0, "median": 0, "stdev": 0,
                        "min": 0, "max": 0, "trend": 0, "volatility": 0
                    }
            
            return patterns
            
        except Exception as e:
            raise Exception(f"Error analyzing spending patterns: {str(e)}")
    
    def _calculate_trend(self, amounts: List[float]) -> float:
        """Calculate spending trend using linear regression slope."""
        try:
            if len(amounts) < 2:
                return 0
            
            n = len(amounts)
            x = list(range(n))
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(amounts)
            
            numerator = sum((x[i] - x_mean) * (amounts[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            return numerator / denominator if denominator != 0 else 0
            
        except Exception:
            return 0
    
    def _calculate_volatility(self, amounts: List[float]) -> float:
        """Calculate coefficient of variation as volatility measure."""
        try:
            if not amounts or statistics.mean(amounts) == 0:
                return 0
            return statistics.stdev(amounts) / statistics.mean(amounts)
        except Exception:
            return 0
    
    def calculate_income_ratios(self, income: float, priorities: Dict[str, int]) -> Dict[str, float]:
        """Calculate adjusted ratios based on income level and priorities."""
        try:
            # Adjust base ratios based on income level
            adjusted_ratios = self.base_ratios.copy()
            
            # Higher income allows for more discretionary spending
            if income > 6000:
                adjusted_ratios["entertainment"] *= 1.2
                adjusted_ratios["shopping"] *= 1.1
                adjusted_ratios["savings"] *= 1.3
            elif income < 4000:
                adjusted_ratios["housing"] *= 0.9
                adjusted_ratios["entertainment"] *= 0.8
                adjusted_ratios["shopping"] *= 0.7
            
            # Apply priority weighting
            total_priority = sum(priorities.values())
            priority_weights = {cat: prio / total_priority for cat, prio in priorities.items()}
            
            # Blend base ratios with priority weights
            final_ratios = {}
            for category in self.categories:
                base_weight = 0.6
                priority_weight = 0.4
                final_ratios[category] = (
                    adjusted_ratios[category] * base_weight +
                    priority_weights.get(category, 0.05) * priority_weight
                )
            
            # Normalize to ensure sum <= 1.0
            total_ratio = sum(final_ratios.values())
            if total_ratio > 1.0:
                final_ratios = {cat: ratio / total_ratio for cat, ratio in final_ratios.items()}
            
            return final_ratios
            
        except Exception as e:
            raise Exception(f"Error calculating income ratios: {str(e)}")
    
    def generate_recommendations(self, income: float, patterns: Dict, 
                               ratios: Dict[str, float]) -> Dict:
        """Generate statistical budget recommendations with confidence intervals."""
        try:
            recommendations = {}
            
            for category in self.categories:
                pattern = patterns[category]
                ideal_amount = income * ratios[category]
                
                # Statistical recommendation based on historical patterns
                if pattern["mean"] > 0:
                    # Use weighted average of ideal and historical mean
                    historical_weight = 0.6
                    ideal_weight = 0.4
                    
                    base_recommendation =