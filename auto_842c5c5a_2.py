```python
"""
Budget Insights Generator

A self-contained Python script that analyzes spending patterns to create personalized
budget recommendations, set category-based limits, and generate overspending alerts.

Features:
- Analyzes historical spending data to identify patterns
- Creates category-based budget limits based on historical averages
- Generates personalized spending recommendations
- Monitors current spending against limits and alerts on overspending
- Provides detailed insights and suggestions for budget optimization

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random


class BudgetInsightsGenerator:
    def __init__(self):
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Travel', 'Education',
            'Personal Care', 'Gifts & Donations'
        ]
        self.historical_data = self._generate_sample_data()
        self.current_month_spending = self._generate_current_month_data()
        self.budget_limits = {}
        self.recommendations = []
        self.alerts = []

    def _generate_sample_data(self) -> Dict[str, List[float]]:
        """Generate sample historical spending data for the last 6 months."""
        data = {}
        for category in self.categories:
            # Generate realistic spending patterns with some variation
            base_amounts = {
                'Food & Dining': 400,
                'Transportation': 200,
                'Shopping': 300,
                'Entertainment': 150,
                'Bills & Utilities': 250,
                'Healthcare': 100,
                'Travel': 200,
                'Education': 50,
                'Personal Care': 80,
                'Gifts & Donations': 60
            }
            
            base_amount = base_amounts.get(category, 100)
            monthly_amounts = []
            
            for month in range(6):
                # Add seasonal variation and randomness
                variation = random.uniform(0.7, 1.3)
                seasonal_factor = 1.2 if month in [4, 5] else 0.9  # Higher in recent months
                amount = base_amount * variation * seasonal_factor
                monthly_amounts.append(round(amount, 2))
            
            data[category] = monthly_amounts
        
        return data

    def _generate_current_month_data(self) -> Dict[str, float]:
        """Generate current month spending data."""
        current_data = {}
        for category in self.categories:
            # Current spending is typically 60-80% through the month
            historical_avg = statistics.mean(self.historical_data[category])
            progress_factor = random.uniform(0.6, 0.9)  # Assume we're partway through month
            current_data[category] = round(historical_avg * progress_factor, 2)
        
        return current_data

    def analyze_spending_patterns(self) -> Dict[str, Dict[str, float]]:
        """Analyze historical spending patterns to identify trends."""
        try:
            patterns = {}
            
            for category, amounts in self.historical_data.items():
                avg_spending = statistics.mean(amounts)
                median_spending = statistics.median(amounts)
                std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                # Calculate trend (comparing last 3 months to first 3 months)
                first_half_avg = statistics.mean(amounts[:3])
                second_half_avg = statistics.mean(amounts[3:])
                trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100
                
                patterns[category] = {
                    'average': round(avg_spending, 2),
                    'median': round(median_spending, 2),
                    'std_dev': round(std_dev, 2),
                    'trend_percentage': round(trend_percentage, 2),
                    'volatility': 'High' if std_dev > avg_spending * 0.3 else 'Medium' if std_dev > avg_spending * 0.15 else 'Low'
                }
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {}

    def set_budget_limits(self, patterns: Dict[str, Dict[str, float]]) -> None:
        """Set category-based budget limits based on historical analysis."""
        try:
            for category, pattern in patterns.items():
                avg_spending = pattern['average']
                trend = pattern['trend_percentage']
                volatility = pattern['std_dev']
                
                # Base limit on average spending with adjustments for trends and volatility
                if trend > 10:  # Increasing trend
                    limit = avg_spending * 1.15  # Allow 15% more
                elif trend < -10:  # Decreasing trend
                    limit = avg_spending * 0.95  # Reduce by 5%
                else:  # Stable trend
                    limit = avg_spending * 1.05  # Small buffer
                
                # Adjust for volatility
                if volatility > avg_spending * 0.3:  # High volatility
                    limit *= 1.1  # Add extra buffer
                
                self.budget_limits[category] = round(limit, 2)
                
        except Exception as e:
            print(f"Error setting budget limits: {e}")

    def generate_recommendations(self, patterns: Dict[str, Dict[str, float]]) -> None:
        """Generate personalized spending recommendations."""
        try:
            self.recommendations = []
            
            # Sort categories by spending amount for prioritization
            sorted_categories = sorted(patterns.items(), key=lambda x: x[1]['average'], reverse=True)
            
            for category, pattern in sorted_categories[:5]:  # Focus on top 5 spending categories
                avg_spending = pattern['average']
                trend = pattern['trend_percentage']
                volatility = pattern['volatility']
                
                if trend > 15:
                    self.recommendations.append(
                        f"🔴 {category}: Spending increased by {trend:.1f}% recently. "
                        f"Consider setting a stricter limit of ${avg_spending * 0.9:.0f}/month."
                    )
                elif trend < -15:
                    self.recommendations.append(
                        f"🟢 {category}: Great job reducing spending by {abs(trend):.1f}%! "
                        f"You could reallocate ${avg_spending * 0.1:.0f} to savings or other priorities."
                    )
                elif volatility == 'High':
                    self.recommendations.append(
                        f"🟡 {category}: Spending varies significantly month-to-month. "
                        f"Try to maintain consistent spending around ${avg_spending:.0f}/month."
                    )
                elif avg_spending > 500:
                    self.recommendations.append(
                        f"💡 {category}: This is your highest spending category (${avg_spending:.0f}/month). "
                        f"Look for opportunities to save 10-15% without impacting quality of life."
                    )
            
            # Add general recommendations
            total_spending = sum(pattern['average'] for pattern in patterns.values())
            self.recommendations.append(
                f"📊 Total average monthly spending: ${total_spending:.0f}. "
                f"Consider the 50/30/20 rule: 50% needs, 30% wants, 20% savings."
            )
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")

    def check_overspending_alerts(self) -> None:
        """Check current spending against limits and generate alerts."""
        try:
            self.alerts = []
            current_day = 20  # Assume we're on day 20 of a 30-day month
            days_remaining = 30 - current_day
            
            for category, current_spending in self.current_month_spending.items():
                if category in self.budget_limits:
                    limit = self.budget_limits[category]
                    usage_percentage = (current_spending / limit) * 100