```python
"""
Automated Budget Recommendation Report Generator

This module generates comprehensive budget analysis reports in HTML and PDF formats.
It analyzes spending patterns, creates visualizations, and provides actionable savings
suggestions based on financial data analysis algorithms.

Features:
- Spending breakdown analysis with category classification
- Interactive HTML reports with embedded charts
- PDF generation for professional presentation
- Automated savings recommendations based on spending patterns
- Error handling for robust operation

Usage:
    python script.py

Dependencies:
    - Standard library modules (json, datetime, base64, etc.)
    - httpx (for potential API integrations)
    - anthropic (for AI-powered insights)
"""

import json
import datetime
import base64
import io
import sys
import traceback
from typing import Dict, List, Tuple, Any
import re
import math

try:
    import httpx
    import anthropic
except ImportError as e:
    print(f"Warning: Optional dependencies not available: {e}")
    httpx = None
    anthropic = None


class BudgetAnalyzer:
    """Core budget analysis engine"""
    
    def __init__(self):
        self.spending_categories = {
            'Housing': ['rent', 'mortgage', 'utilities', 'insurance'],
            'Transportation': ['gas', 'car payment', 'public transit', 'uber', 'lyft'],
            'Food': ['groceries', 'restaurants', 'delivery', 'coffee'],
            'Entertainment': ['movies', 'streaming', 'games', 'concerts'],
            'Healthcare': ['medical', 'pharmacy', 'dental', 'vision'],
            'Personal': ['clothing', 'haircut', 'gym', 'subscriptions'],
            'Savings': ['401k', 'ira', 'emergency fund', 'investments']
        }
        
    def categorize_expense(self, description: str, amount: float) -> str:
        """Categorize an expense based on description"""
        description_lower = description.lower()
        for category, keywords in self.spending_categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        return 'Other'
    
    def analyze_spending(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze spending patterns and generate insights"""
        category_totals = {}
        total_spending = 0
        
        for transaction in transactions:
            category = self.categorize_expense(transaction['description'], transaction['amount'])
            category_totals[category] = category_totals.get(category, 0) + transaction['amount']
            total_spending += transaction['amount']
        
        # Calculate percentages
        category_percentages = {
            cat: (amount / total_spending * 100) if total_spending > 0 else 0
            for cat, amount in category_totals.items()
        }
        
        return {
            'category_totals': category_totals,
            'category_percentages': category_percentages,
            'total_spending': total_spending,
            'transaction_count': len(transactions)
        }
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable savings recommendations"""
        recommendations = []
        percentages = analysis['category_percentages']
        totals = analysis['category_totals']
        
        # High food spending
        if percentages.get('Food', 0) > 15:
            potential_savings = totals.get('Food', 0) * 0.3
            recommendations.append(
                f"Food spending is {percentages.get('Food', 0):.1f}% of budget. "
                f"Consider meal planning and cooking at home to save ~${potential_savings:.2f}/month."
            )
        
        # High entertainment spending
        if percentages.get('Entertainment', 0) > 10:
            potential_savings = totals.get('Entertainment', 0) * 0.4
            recommendations.append(
                f"Entertainment spending is high at {percentages.get('Entertainment', 0):.1f}%. "
                f"Review subscriptions and find free alternatives to save ~${potential_savings:.2f}/month."
            )
        
        # Transportation optimization
        if percentages.get('Transportation', 0) > 20:
            potential_savings = totals.get('Transportation', 0) * 0.2
            recommendations.append(
                f"Transportation costs are {percentages.get('Transportation', 0):.1f}% of budget. "
                f"Consider carpooling or public transit to save ~${potential_savings:.2f}/month."
            )
        
        # Low savings rate
        if percentages.get('Savings', 0) < 10:
            target_savings = analysis['total_spending'] * 0.1
            recommendations.append(
                f"Savings rate is only {percentages.get('Savings', 0):.1f}%. "
                f"Aim to save at least ${target_savings:.2f}/month (10% of income)."
            )
        
        return recommendations


class ChartGenerator:
    """Generate SVG charts for visualizations"""
    
    @staticmethod
    def create_pie_chart(data: Dict[str, float], title: str = "Spending Breakdown") -> str:
        """Create an SVG pie chart"""
        total = sum(data.values())
        if total == 0:
            return f"<div>No data available for {title}</div>"
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        
        svg_parts = [f'<svg width="400" height="400" viewBox="0 0 400 400">']
        svg_parts.append(f'<text x="200" y="30" text-anchor="middle" font-size="16" font-weight="bold">{title}</text>')
        
        angle_start = 0
        legend_y = 60
        
        for i, (category, amount) in enumerate(data.items()):
            if amount <= 0:
                continue
                
            percentage = (amount / total) * 100
            angle_size = (amount / total) * 360
            
            # Calculate pie slice
            x1 = 200 + 80 * math.cos(math.radians(angle_start))
            y1 = 200 + 80 * math.sin(math.radians(angle_start))
            x2 = 200 + 80 * math.cos(math.radians(angle_start + angle_size))
            y2 = 200 + 80 * math.sin(math.radians(angle_start + angle_size))
            
            large_arc = 1 if angle_size > 180 else 0
            color = colors[i % len(colors)]
            
            path = f"M 200 200 L {x1} {y1} A 80 80 0 {large_arc} 1 {x2} {y2} Z"
            svg_parts.append(f'<path d="{path}" fill="{color}" stroke="white" stroke-width="2"/>')
            
            # Legend
            svg_parts.append(f'<rect x="320" y="{legend_y}" width="15" height="15" fill="{color}"/>')
            svg_parts.append(f'<text x="340" y="{legend_y + 12}" font-size="12">{category} ({percentage:.1f}%)</text>')
            legend_y += 20
            
            angle_start += angle_size
        
        svg_parts.append('</svg>')
        return ''.join(svg_parts)
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str = "Monthly Comparison") -> str:
        """Create an SVG bar chart"""
        if not data:
            return f"<div>No data available for {title}</div>"
        
        max_value = max(data.values()) if data.values() else 1
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA