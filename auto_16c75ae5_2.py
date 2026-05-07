```python
"""
Personal Budget Recommendation Engine

This module analyzes spending patterns from historical transaction data to generate
personalized monthly budget recommendations. It calculates optimal spending limits
per category based on user behavior, income, and configurable savings goals.

Features:
- Processes transaction history to identify spending patterns
- Categorizes expenses automatically
- Generates personalized budget recommendations
- Supports configurable savings goals (percentage-based)
- Provides spending limit recommendations per category
- Includes variance analysis and budget optimization

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import re


class BudgetRecommendationEngine:
    """
    A comprehensive budget recommendation system that analyzes spending patterns
    and generates personalized monthly budget suggestions.
    """
    
    def __init__(self):
        self.categories = {
            'housing': ['rent', 'mortgage', 'utilities', 'home', 'property'],
            'food': ['grocery', 'restaurant', 'dining', 'food', 'coffee', 'lunch'],
            'transportation': ['gas', 'uber', 'lyft', 'transit', 'car', 'parking'],
            'entertainment': ['movie', 'netflix', 'spotify', 'games', 'concert'],
            'shopping': ['amazon', 'clothing', 'retail', 'store', 'mall'],
            'healthcare': ['medical', 'pharmacy', 'doctor', 'hospital', 'health'],
            'bills': ['phone', 'internet', 'insurance', 'subscription'],
            'misc': []
        }
        
        # Sample historical data (in real implementation, this would come from user input)
        self.sample_transactions = [
            {'date': '2024-01-15', 'amount': 1200.00, 'description': 'Monthly Rent Payment'},
            {'date': '2024-01-16', 'amount': 85.50, 'description': 'Grocery Store Purchase'},
            {'date': '2024-01-18', 'amount': 45.20, 'description': 'Gas Station'},
            {'date': '2024-01-20', 'amount': 32.75, 'description': 'Restaurant Dinner'},
            {'date': '2024-01-22', 'amount': 15.99, 'description': 'Netflix Subscription'},
            {'date': '2024-01-25', 'amount': 120.00, 'description': 'Grocery Store'},
            {'date': '2024-01-28', 'amount': 65.00, 'description': 'Utility Bill'},
            {'date': '2024-02-01', 'amount': 1200.00, 'description': 'Rent Payment'},
            {'date': '2024-02-03', 'amount': 95.30, 'description': 'Whole Foods'},
            {'date': '2024-02-05', 'amount': 50.00, 'description': 'Gas'},
            {'date': '2024-02-08', 'amount': 28.50, 'description': 'Coffee Shop'},
            {'date': '2024-02-10', 'amount': 75.25, 'description': 'Department Store'},
            {'date': '2024-02-15', 'amount': 42.99, 'description': 'Phone Bill'},
            {'date': '2024-02-18', 'amount': 110.00, 'description': 'Groceries'},
            {'date': '2024-03-01', 'amount': 1200.00, 'description': 'March Rent'},
            {'date': '2024-03-04', 'amount': 88.75, 'description': 'Safeway Grocery'},
            {'date': '2024-03-06', 'amount': 55.00, 'description': 'Shell Gas Station'},
            {'date': '2024-03-10', 'amount': 35.60, 'description': 'Restaurant Lunch'},
            {'date': '2024-03-12', 'amount': 25.00, 'description': 'Movie Theater'},
            {'date': '2024-03-15', 'amount': 67.80, 'description': 'Electric Bill'},
        ]
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorizes a transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name as string
        """
        try:
            description_lower = description.lower()
            
            for category, keywords in self.categories.items():
                if category == 'misc':
                    continue
                for keyword in keywords:
                    if keyword in description_lower:
                        return category
            
            return 'misc'
            
        except Exception as e:
            print(f"Error categorizing transaction '{description}': {e}")
            return 'misc'
    
    def process_transactions(self, transactions: List[Dict]) -> Dict[str, List[float]]:
        """
        Processes transactions and groups them by category.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Dictionary mapping categories to lists of amounts
        """
        try:
            categorized_spending = defaultdict(list)
            
            for transaction in transactions:
                category = self.categorize_transaction(transaction['description'])
                amount = float(transaction['amount'])
                categorized_spending[category].append(amount)
            
            return dict(categorized_spending)
            
        except Exception as e:
            print(f"Error processing transactions: {e}")
            return {}
    
    def calculate_monthly_averages(self, categorized_spending: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Calculates monthly average spending per category.
        
        Args:
            categorized_spending: Dictionary of categorized spending data
            
        Returns:
            Dictionary mapping categories to monthly averages
        """
        try:
            monthly_averages = {}
            
            for category, amounts in categorized_spending.items():
                if amounts:
                    # Calculate monthly average (assuming 3 months of data)
                    monthly_avg = sum(amounts) / 3
                    monthly_averages[category] = round(monthly_avg, 2)
            
            return monthly_averages
            
        except Exception as e:
            print(f"Error calculating monthly averages: {e}")
            return {}
    
    def calculate_spending_variance(self, categorized_spending: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Calculates spending variance per category to understand consistency.
        
        Args:
            categorized_spending: Dictionary of categorized spending data
            
        Returns:
            Dictionary mapping categories to variance values
        """
        try:
            variances = {}
            
            for category, amounts in categorized_spending.items():
                if len(amounts) > 1:
                    variance = statistics.variance(amounts)
                    variances[category] = round(variance, 2)
                else:
                    variances[category] = 0.0
            
            return variances
            
        except Exception as e:
            print(f"Error calculating variance: {e}")
            return {}
    
    def generate_budget_recommendations(
        self, 
        monthly_averages: Dict[str, float],
        monthly_income: float,
        savings_goal_percentage: float = 20.0
    ) -> Dict[str, Dict[str, float]]:
        """
        Generates personalized budget recommendations based on spending patterns.
        
        Args:
            monthly_averages: Monthly average spending per category
            monthly_income: User's monthly income
            savings_goal_percentage: Desired savings percentage (default 20%)
            
        Returns:
            Dictionary with budget recommendations and analysis
        """
        try:
            total_current_spending = sum(monthly_averages.values())
            target_savings = monthly_income * (savings_goal_percentage / 100)
            available_for_spending = monthly_income - target_savings
            
            # Calculate spending adjustment factor
            if total_current_spending > available_for_spending:
                adjustment_factor = available_for_spending