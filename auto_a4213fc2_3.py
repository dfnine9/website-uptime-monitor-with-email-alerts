```python
"""
Budget Recommendation Engine

This module implements a comprehensive budget recommendation system that analyzes
historical spending data to suggest realistic budget limits per category and generates
actionable insights for expense optimization.

Features:
- Analyzes spending patterns and trends
- Calculates statistical budget recommendations
- Identifies seasonal patterns and anomalies
- Generates actionable optimization insights
- Provides variance analysis and forecasting
- Outputs detailed recommendations with confidence scores

The engine uses statistical analysis including percentiles, moving averages,
and trend detection to provide data-driven budget recommendations.
"""

import json
import statistics
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import random


class BudgetRecommendationEngine:
    def __init__(self):
        self.spending_data = []
        self.categories = set()
        self.analysis_results = {}
        
    def load_sample_data(self):
        """Generate realistic sample spending data for demonstration"""
        try:
            categories = [
                'Groceries', 'Rent', 'Utilities', 'Transportation', 'Dining Out',
                'Entertainment', 'Healthcare', 'Shopping', 'Insurance', 'Savings'
            ]
            
            base_amounts = {
                'Groceries': 400, 'Rent': 1200, 'Utilities': 150, 'Transportation': 300,
                'Dining Out': 200, 'Entertainment': 150, 'Healthcare': 100,
                'Shopping': 250, 'Insurance': 180, 'Savings': 500
            }
            
            # Generate 12 months of data
            for month in range(12):
                date = datetime.now() - timedelta(days=30 * (11 - month))
                
                for category in categories:
                    base_amount = base_amounts[category]
                    # Add seasonal variation and randomness
                    seasonal_factor = 1 + 0.2 * math.sin(2 * math.pi * month / 12)
                    random_factor = random.uniform(0.7, 1.3)
                    amount = base_amount * seasonal_factor * random_factor
                    
                    self.spending_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'category': category,
                        'amount': round(amount, 2),
                        'description': f'{category} expense for {date.strftime("%B")}'
                    })
            
            self.categories = set(categories)
            print(f"✓ Loaded {len(self.spending_data)} spending records across {len(self.categories)} categories")
            
        except Exception as e:
            print(f"✗ Error loading sample data: {str(e)}")
            raise
    
    def analyze_spending_patterns(self):
        """Analyze historical spending patterns by category"""
        try:
            category_data = defaultdict(list)
            monthly_totals = defaultdict(lambda: defaultdict(float))
            
            # Group data by category and month
            for record in self.spending_data:
                category = record['category']
                amount = record['amount']
                date = datetime.strptime(record['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                
                category_data[category].append(amount)
                monthly_totals[month_key][category] += amount
            
            # Calculate statistics for each category
            for category, amounts in category_data.items():
                if amounts:
                    self.analysis_results[category] = {
                        'total_spent': sum(amounts),
                        'average_monthly': statistics.mean(amounts),
                        'median_monthly': statistics.median(amounts),
                        'std_deviation': statistics.stdev(amounts) if len(amounts) > 1 else 0,
                        'min_amount': min(amounts),
                        'max_amount': max(amounts),
                        'percentile_75': self._percentile(amounts, 75),
                        'percentile_90': self._percentile(amounts, 90),
                        'trend': self._calculate_trend(amounts),
                        'volatility': self._calculate_volatility(amounts),
                        'monthly_data': amounts
                    }
            
            print("✓ Completed spending pattern analysis")
            
        except Exception as e:
            print(f"✗ Error analyzing spending patterns: {str(e)}")
            raise
    
    def _percentile(self, data, percentile):
        """Calculate percentile of a dataset"""
        try:
            sorted_data = sorted(data)
            index = (percentile / 100) * (len(sorted_data) - 1)
            
            if index.is_integer():
                return sorted_data[int(index)]
            else:
                lower = sorted_data[int(index)]
                upper = sorted_data[int(index) + 1]
                return lower + (upper - lower) * (index - int(index))
        except:
            return 0
    
    def _calculate_trend(self, amounts):
        """Calculate spending trend (increasing/decreasing/stable)"""
        try:
            if len(amounts) < 3:
                return "insufficient_data"
            
            # Simple linear trend calculation
            n = len(amounts)
            x_sum = sum(range(n))
            y_sum = sum(amounts)
            xy_sum = sum(i * amounts[i] for i in range(n))
            x_squared_sum = sum(i * i for i in range(n))
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x_squared_sum - x_sum * x_sum)
            
            if slope > 10:
                return "increasing"
            elif slope < -10:
                return "decreasing"
            else:
                return "stable"
        except:
            return "unknown"
    
    def _calculate_volatility(self, amounts):
        """Calculate spending volatility (coefficient of variation)"""
        try:
            if len(amounts) < 2:
                return 0
            
            mean_val = statistics.mean(amounts)
            if mean_val == 0:
                return 0
            
            std_val = statistics.stdev(amounts)
            return (std_val / mean_val) * 100
        except:
            return 0
    
    def generate_budget_recommendations(self):
        """Generate budget recommendations based on analysis"""
        recommendations = {}
        
        try:
            for category, analysis in self.analysis_results.items():
                avg_monthly = analysis['average_monthly']
                median_monthly = analysis['median_monthly']
                p75 = analysis['percentile_75']
                volatility = analysis['volatility']
                trend = analysis['trend']
                
                # Base recommendation on percentile approach
                if volatility < 20:  # Low volatility
                    recommended_budget = p75 * 1.1
                    confidence = "high"
                elif volatility < 40:  # Medium volatility
                    recommended_budget = p75 * 1.2
                    confidence = "medium"
                else:  # High volatility
                    recommended_budget = p75 * 1.3
                    confidence = "low"
                
                # Adjust for trend
                if trend == "increasing":
                    recommended_budget *= 1.15
                elif trend == "decreasing":
                    recommended_budget *= 0.95
                
                # Calculate potential savings
                potential_savings = max(0, avg_monthly - median_monthly)
                
                recommendations[category] = {
                    'current_average': round(avg_monthly, 2),
                    'recommended_budget': round(recommended_budget, 2),
                    'confidence_level': confidence,
                    'potential_savings': round(potential_savings, 2),
                    'trend': trend,
                    'volatility_score': round(volatility, 1),
                    'budget_change': round(((recommended_budget - avg_monthly) / avg_monthly) * 100, 1)
                }
            
            print("✓ Generated budget recommendations for all categories")
            return recommendations
            
        except Exception as e:
            print(f"✗ Error generating recommendations: {str(e)