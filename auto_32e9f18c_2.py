```python
"""
Personal Budget Recommendation Engine

This module analyzes historical spending patterns and generates personalized monthly budget 
suggestions using established budgeting frameworks like the 50/30/20 rule. It processes 
transaction data to identify spending categories, calculates averages, and provides 
category-specific budget limits with recommendations for optimization.

Features:
- Historical spending pattern analysis
- Multiple budgeting framework support (50/30/20, 70/20/10, custom)
- Category-based spending classification
- Personalized budget recommendations
- Spending variance analysis and alerts

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import re


class BudgetRecommendationEngine:
    """
    A comprehensive budget recommendation engine that analyzes spending patterns
    and generates personalized budget suggestions.
    """
    
    def __init__(self):
        self.budgeting_frameworks = {
            "50/30/20": {"needs": 0.50, "wants": 0.30, "savings": 0.20},
            "70/20/10": {"needs": 0.70, "wants": 0.20, "savings": 0.10},
            "60/20/20": {"needs": 0.60, "wants": 0.20, "savings": 0.20}
        }
        
        # Category mappings for transaction classification
        self.category_mappings = {
            "needs": [
                "rent", "mortgage", "utilities", "groceries", "insurance",
                "transportation", "gas", "fuel", "medical", "pharmacy",
                "minimum_payment", "loan", "childcare", "phone", "internet"
            ],
            "wants": [
                "restaurant", "entertainment", "shopping", "clothes", "gaming",
                "subscription", "streaming", "gym", "hobby", "travel",
                "coffee", "alcohol", "movies", "books", "music"
            ],
            "savings": [
                "savings", "investment", "retirement", "emergency", "401k",
                "ira", "stocks", "bonds", "mutual_fund"
            ]
        }
    
    def generate_sample_transactions(self) -> List[Dict]:
        """Generate sample transaction data for demonstration."""
        sample_data = [
            {"date": "2024-01-15", "amount": 1200.00, "description": "Rent Payment", "category": "housing"},
            {"date": "2024-01-16", "amount": 250.00, "description": "Groceries - Whole Foods", "category": "food"},
            {"date": "2024-01-17", "amount": 45.00, "description": "Gas Station", "category": "transportation"},
            {"date": "2024-01-18", "amount": 80.00, "description": "Restaurant Dinner", "category": "dining"},
            {"date": "2024-01-19", "amount": 120.00, "description": "Electric Bill", "category": "utilities"},
            {"date": "2024-01-20", "amount": 500.00, "description": "Investment Transfer", "category": "savings"},
            {"date": "2024-01-22", "amount": 60.00, "description": "Internet Bill", "category": "utilities"},
            {"date": "2024-01-25", "amount": 200.00, "description": "Shopping - Amazon", "category": "shopping"},
            {"date": "2024-01-28", "amount": 150.00, "description": "Car Insurance", "category": "insurance"},
            {"date": "2024-01-30", "amount": 40.00, "description": "Coffee Shop", "category": "dining"},
            
            # February data
            {"date": "2024-02-01", "amount": 1200.00, "description": "Rent Payment", "category": "housing"},
            {"date": "2024-02-05", "amount": 280.00, "description": "Groceries - Safeway", "category": "food"},
            {"date": "2024-02-08", "amount": 50.00, "description": "Gas Station", "category": "transportation"},
            {"date": "2024-02-12", "amount": 95.00, "description": "Restaurant Lunch", "category": "dining"},
            {"date": "2024-02-15", "amount": 125.00, "description": "Electric Bill", "category": "utilities"},
            {"date": "2024-02-18", "amount": 600.00, "description": "Investment Transfer", "category": "savings"},
            {"date": "2024-02-20", "amount": 15.00, "description": "Netflix Subscription", "category": "entertainment"},
            {"date": "2024-02-22", "amount": 180.00, "description": "Shopping - Target", "category": "shopping"},
            {"date": "2024-02-25", "amount": 35.00, "description": "Coffee Shop", "category": "dining"},
            {"date": "2024-02-28", "amount": 75.00, "description": "Gym Membership", "category": "fitness"},
            
            # March data
            {"date": "2024-03-01", "amount": 1200.00, "description": "Rent Payment", "category": "housing"},
            {"date": "2024-03-03", "amount": 220.00, "description": "Groceries", "category": "food"},
            {"date": "2024-03-07", "amount": 55.00, "description": "Gas Station", "category": "transportation"},
            {"date": "2024-03-10", "amount": 120.00, "description": "Restaurant Dinner", "category": "dining"},
            {"date": "2024-03-15", "amount": 110.00, "description": "Electric Bill", "category": "utilities"},
            {"date": "2024-03-18", "amount": 450.00, "description": "Investment Transfer", "category": "savings"},
            {"date": "2024-03-20", "amount": 300.00, "description": "Shopping - Clothing", "category": "shopping"},
            {"date": "2024-03-22", "amount": 25.00, "description": "Coffee Shop", "category": "dining"},
            {"date": "2024-03-25", "amount": 200.00, "description": "Medical Appointment", "category": "healthcare"},
            {"date": "2024-03-30", "amount": 60.00, "description": "Internet Bill", "category": "utilities"}
        ]
        return sample_data
    
    def classify_transaction(self, description: str, category: str) -> str:
        """Classify transaction into needs/wants/savings categories."""
        description_lower = description.lower()
        category_lower = category.lower() if category else ""
        
        # Check for savings indicators
        for keyword in self.category_mappings["savings"]:
            if keyword in description_lower or keyword in category_lower:
                return "savings"
        
        # Check for needs indicators
        for keyword in self.category_mappings["needs"]:
            if keyword in description_lower or keyword in category_lower:
                return "needs"
        
        # Check for wants indicators
        for keyword in self.category_mappings["wants"]:
            if keyword in description_lower or keyword in category_lower:
                return "wants"
        
        # Default classification based on common categories
        if any(word in category_lower for word in ["housing", "utilities", "food", "transportation", "insurance", "healthcare"]):
            return "needs"
        elif any(word in category_lower for word in ["dining", "entertainment", "shopping", "fitness"]):
            return "wants"
        else:
            return "needs"  # Default to needs for unclassified expenses
    
    def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze historical spending patterns from transaction data."""
        try:
            if not transactions:
                raise ValueError("No transaction data provided")
            
            # Group transactions by month and category
            monthly_spending = defaultdict(lambda: defaultdict(float))
            category_spending = defaultdict(list)
            classified_spending = {"needs": [], "wants": [], "savings": []}
            
            for transaction in transactions