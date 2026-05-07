```python
#!/usr/bin/env python3
"""
Personal Budget Recommendation System

This module analyzes spending patterns and generates personalized budget recommendations
based on historical data and industry standards. It calculates suggested budget limits
for various spending categories and identifies potential savings opportunities.

Features:
- Analyzes spending patterns across multiple categories
- Calculates recommended budget limits using 50/30/20 rule and historical averages
- Identifies categories with potential savings opportunities
- Provides actionable recommendations for budget optimization

Usage:
    python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random


class BudgetAnalyzer:
    """Analyzes spending patterns and generates budget recommendations."""
    
    # Industry standard budget percentages (50/30/20 rule variations)
    INDUSTRY_STANDARDS = {
        'housing': 0.30,
        'transportation': 0.15,
        'food': 0.12,
        'utilities': 0.08,
        'healthcare': 0.05,
        'entertainment': 0.05,
        'shopping': 0.05,
        'personal_care': 0.03,
        'education': 0.03,
        'savings': 0.20,
        'other': 0.04
    }
    
    def __init__(self):
        self.spending_data = []
        self.monthly_income = 0
        
    def generate_sample_data(self, months: int = 6) -> None:
        """Generate sample spending data for demonstration."""
        try:
            self.monthly_income = 5000  # Sample monthly income
            categories = list(self.INDUSTRY_STANDARDS.keys())
            categories.remove('savings')  # Don't include savings in spending
            
            for month in range(months):
                date = datetime.now() - timedelta(days=30 * month)
                month_data = {
                    'month': date.strftime('%Y-%m'),
                    'income': self.monthly_income,
                    'spending': {}
                }
                
                # Generate realistic spending with some variation
                for category in categories:
                    base_amount = self.monthly_income * self.INDUSTRY_STANDARDS[category]
                    # Add 20% random variation
                    variation = random.uniform(0.8, 1.2)
                    amount = round(base_amount * variation, 2)
                    month_data['spending'][category] = amount
                
                self.spending_data.append(month_data)
                
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def calculate_averages(self) -> Dict[str, float]:
        """Calculate average spending per category."""
        try:
            if not self.spending_data:
                return {}
            
            averages = {}
            categories = self.spending_data[0]['spending'].keys()
            
            for category in categories:
                amounts = [month['spending'][category] for month in self.spending_data]
                averages[category] = statistics.mean(amounts)
                
            return averages
        except Exception as e:
            print(f"Error calculating averages: {e}")
            return {}
    
    def calculate_budget_recommendations(self) -> Dict[str, Dict]:
        """Calculate recommended budget limits based on income and spending patterns."""
        try:
            averages = self.calculate_averages()
            recommendations = {}
            
            for category, avg_spending in averages.items():
                industry_recommended = self.monthly_income * self.INDUSTRY_STANDARDS[category]
                
                # Use conservative approach: lower of historical average or industry standard
                recommended_limit = min(avg_spending * 1.1, industry_recommended)
                
                recommendations[category] = {
                    'current_average': round(avg_spending, 2),
                    'recommended_limit': round(recommended_limit, 2),
                    'industry_standard': round(industry_recommended, 2),
                    'percentage_of_income': round((recommended_limit / self.monthly_income) * 100, 1)
                }
            
            # Add savings recommendation
            total_recommended_spending = sum(rec['recommended_limit'] for rec in recommendations.values())
            recommended_savings = self.monthly_income - total_recommended_spending
            
            recommendations['savings'] = {
                'current_average': 0,  # Assume no tracked savings data
                'recommended_limit': round(recommended_savings, 2),
                'industry_standard': round(self.monthly_income * self.INDUSTRY_STANDARDS['savings'], 2),
                'percentage_of_income': round((recommended_savings / self.monthly_income) * 100, 1)
            }
            
            return recommendations
        except Exception as e:
            print(f"Error calculating recommendations: {e}")
            return {}
    
    def identify_savings_opportunities(self, recommendations: Dict) -> List[Dict]:
        """Identify categories with potential savings opportunities."""
        try:
            opportunities = []
            
            for category, data in recommendations.items():
                if category == 'savings':
                    continue
                    
                current_avg = data['current_average']
                recommended = data['recommended_limit']
                industry_std = data['industry_standard']
                
                # Opportunity if current spending exceeds recommended or industry standard
                if current_avg > recommended:
                    potential_savings = current_avg - recommended
                    opportunities.append({
                        'category': category,
                        'current_spending': current_avg,
                        'recommended_limit': recommended,
                        'potential_monthly_savings': round(potential_savings, 2),
                        'potential_annual_savings': round(potential_savings * 12, 2),
                        'priority': 'high' if potential_savings > 200 else 'medium' if potential_savings > 50 else 'low'
                    })
            
            # Sort by potential savings (highest first)
            opportunities.sort(key=lambda x: x['potential_monthly_savings'], reverse=True)
            return opportunities
        except Exception as e:
            print(f"Error identifying savings opportunities: {e}")
            return []
    
    def generate_recommendations_report(self) -> str:
        """Generate a comprehensive budget recommendations report."""
        try:
            recommendations = self.calculate_budget_recommendations()
            opportunities = self.identify_savings_opportunities(recommendations)
            
            report = f"""
=== PERSONALIZED BUDGET RECOMMENDATIONS ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Monthly Income: ${self.monthly_income:,.2f}
Analysis Period: {len(self.spending_data)} months

=== RECOMMENDED BUDGET LIMITS ===
"""
            
            total_recommended = 0
            for category, data in recommendations.items():
                report += f"\n{category.replace('_', ' ').title()}:"
                report += f"\n  Current Average: ${data['current_average']:,.2f}"
                report += f"\n  Recommended Limit: ${data['recommended_limit']:,.2f} ({data['percentage_of_income']}% of income)"
                report += f"\n  Industry Standard: ${data['industry_standard']:,.2f}"
                
                if category != 'savings':
                    total_recommended += data['recommended_limit']
                
                if data['current_average'] > data['recommended_limit'] and category != 'savings':
                    report += f"\n  ⚠️  OVER BUDGET by ${data['current_average'] - data['recommended_limit']:,.2f}"
                elif data['current_average'] < data['recommended_limit'] * 0.8 and category != 'savings':
                    report += f"\n  ✅ Good control - under budget"
                report += "\n"
            
            report += f"\n=== BUDGET SUMMARY ===\n"
            report += f"Total Recommended Spending: ${total_recommended:,.2f}\n"
            report += f"Recommended Savings: ${recommendations['savings']['recommended_limit']:,.2f}\n"
            report += f"Budget Utilization: {(total_recommended/self.monthly_income)*100:.1f}%\n"
            
            if opportunities:
                report += f"\n=== SAVINGS OPPORTUNITIES ===