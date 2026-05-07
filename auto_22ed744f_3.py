```python
"""
Budget Recommendation System

This module analyzes personal spending patterns by comparing actual expenses against
category averages, identifying overspending areas, and generating actionable budget
recommendations with specific target amounts for each spending category.

The system calculates variance from average spending, identifies problematic patterns,
and provides concrete suggestions for budget optimization based on statistical analysis
of spending behavior.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random


class BudgetAnalyzer:
    """Analyzes spending patterns and generates budget recommendations."""
    
    def __init__(self):
        self.spending_data = {}
        self.category_averages = {}
        self.recommendations = []
        
    def load_sample_data(self) -> Dict:
        """Generate sample spending data for demonstration."""
        categories = [
            'Housing', 'Food', 'Transportation', 'Entertainment', 
            'Utilities', 'Healthcare', 'Shopping', 'Savings'
        ]
        
        # Generate 6 months of sample data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        spending_data = {}
        
        for month in months:
            spending_data[month] = {}
            for category in categories:
                # Generate realistic spending amounts with some variation
                base_amounts = {
                    'Housing': 1200, 'Food': 600, 'Transportation': 300,
                    'Entertainment': 200, 'Utilities': 150, 'Healthcare': 100,
                    'Shopping': 250, 'Savings': 400
                }
                
                # Add random variation (±30%)
                variation = random.uniform(0.7, 1.3)
                amount = base_amounts[category] * variation
                spending_data[month][category] = round(amount, 2)
        
        return spending_data
    
    def calculate_category_averages(self, data: Dict) -> Dict[str, float]:
        """Calculate average spending per category across all months."""
        try:
            averages = {}
            categories = set()
            
            # Collect all categories
            for month_data in data.values():
                categories.update(month_data.keys())
            
            # Calculate averages
            for category in categories:
                amounts = []
                for month_data in data.values():
                    if category in month_data:
                        amounts.append(month_data[category])
                
                if amounts:
                    averages[category] = statistics.mean(amounts)
                    
            return averages
            
        except Exception as e:
            print(f"Error calculating averages: {e}")
            return {}
    
    def identify_overspending_patterns(self, data: Dict, averages: Dict[str, float]) -> List[Dict]:
        """Identify categories and months with significant overspending."""
        try:
            patterns = []
            threshold = 1.2  # 20% over average considered overspending
            
            for month, month_data in data.items():
                for category, amount in month_data.items():
                    if category in averages:
                        avg = averages[category]
                        if amount > avg * threshold:
                            overspend_pct = ((amount - avg) / avg) * 100
                            patterns.append({
                                'month': month,
                                'category': category,
                                'actual': amount,
                                'average': avg,
                                'overspend_amount': amount - avg,
                                'overspend_percentage': round(overspend_pct, 1)
                            })
            
            # Sort by overspending amount (descending)
            patterns.sort(key=lambda x: x['overspend_amount'], reverse=True)
            return patterns
            
        except Exception as e:
            print(f"Error identifying patterns: {e}")
            return []
    
    def generate_budget_recommendations(self, averages: Dict[str, float], 
                                      patterns: List[Dict]) -> List[Dict]:
        """Generate actionable budget recommendations with target amounts."""
        try:
            recommendations = []
            
            # Get categories with frequent overspending
            overspend_categories = {}
            for pattern in patterns:
                category = pattern['category']
                if category in overspend_categories:
                    overspend_categories[category].append(pattern)
                else:
                    overspend_categories[category] = [pattern]
            
            for category, avg_amount in averages.items():
                rec = {
                    'category': category,
                    'current_average': round(avg_amount, 2),
                    'recommended_target': round(avg_amount, 2),
                    'potential_savings': 0,
                    'priority': 'Low',
                    'actions': []
                }
                
                if category in overspend_categories:
                    overspends = overspend_categories[category]
                    avg_overspend = statistics.mean([p['overspend_amount'] for p in overspends])
                    
                    # Set more conservative target
                    rec['recommended_target'] = round(avg_amount * 0.9, 2)
                    rec['potential_savings'] = round(avg_overspend * 0.7, 2)
                    
                    # Determine priority based on frequency and amount
                    if len(overspends) >= 3 or avg_overspend > 100:
                        rec['priority'] = 'High'
                    elif len(overspends) >= 2 or avg_overspend > 50:
                        rec['priority'] = 'Medium'
                    
                    # Generate specific actions
                    rec['actions'] = self._generate_category_actions(category, avg_overspend)
                
                recommendations.append(rec)
            
            # Sort by priority and potential savings
            priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
            recommendations.sort(key=lambda x: (priority_order[x['priority']], x['potential_savings']), 
                               reverse=True)
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def _generate_category_actions(self, category: str, overspend_amount: float) -> List[str]:
        """Generate specific actionable suggestions for each category."""
        actions_map = {
            'Housing': [
                'Consider refinancing mortgage for lower rates',
                'Look into downsizing or finding roommates',
                'Negotiate rent or explore cheaper neighborhoods'
            ],
            'Food': [
                'Plan weekly meals and create shopping lists',
                'Cook more meals at home instead of dining out',
                'Use coupons and shop sales/bulk items'
            ],
            'Transportation': [
                'Use public transport or carpool more often',
                'Consider bike/walk for short distances',
                'Maintain vehicle regularly to improve efficiency'
            ],
            'Entertainment': [
                'Set monthly entertainment budget limit',
                'Look for free community events and activities',
                'Cancel unused streaming subscriptions'
            ],
            'Shopping': [
                'Implement 24-hour wait rule before purchases',
                'Create shopping lists and stick to them',
                'Compare prices and look for deals before buying'
            ],
            'Utilities': [
                'Adjust thermostat settings to save energy',
                'Switch to LED bulbs and energy-efficient appliances',
                'Unplug devices when not in use'
            ],
            'Healthcare': [
                'Use generic medications when available',
                'Take advantage of preventive care coverage',
                'Compare costs for non-emergency procedures'
            ]
        }
        
        return actions_map.get(category, ['Review and monitor spending in this category'])
    
    def analyze_and_recommend(self) -> None:
        """Main analysis workflow."""
        try:
            print("=" * 60)
            print("BUDGET RECOMMENDATION SYSTEM")
            print("=" * 60)
            print()
            
            # Load data
            print("Loading spending data...")
            self.spending_data = self.load_sample_data()
            
            # Calculate averages
            print("Calculating category averages...")