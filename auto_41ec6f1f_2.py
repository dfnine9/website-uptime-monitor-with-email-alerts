```python
"""
Savings Recommendation Engine

This module analyzes personal spending patterns from transaction data to identify
high-spend categories and generate actionable budget optimization suggestions.

The engine performs the following analysis:
1. Categorizes transactions by spending type
2. Identifies top spending categories and trends
3. Detects unusual spending patterns and outliers
4. Generates personalized savings recommendations
5. Provides specific actionable budget optimization strategies

Features:
- Transaction categorization using keyword matching
- Statistical analysis of spending patterns
- Anomaly detection for unusual expenses
- Personalized recommendation generation
- Budget optimization suggestions with target savings amounts

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import re


class SavingsRecommendationEngine:
    """
    Analyzes spending patterns and generates personalized savings recommendations.
    """
    
    def __init__(self):
        """Initialize the recommendation engine with category mappings."""
        # Category mappings for transaction classification
        self.category_keywords = {
            'Food & Dining': ['restaurant', 'cafe', 'food', 'pizza', 'burger', 'starbucks', 'mcdonald', 'subway', 'delivery', 'uber eats', 'doordash'],
            'Groceries': ['grocery', 'supermarket', 'walmart', 'target', 'costco', 'safeway', 'kroger', 'whole foods'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus', 'train', 'car wash'],
            'Shopping': ['amazon', 'ebay', 'mall', 'store', 'retail', 'clothing', 'shoes', 'electronics'],
            'Entertainment': ['netflix', 'spotify', 'movie', 'theater', 'concert', 'game', 'bar', 'club'],
            'Utilities': ['electric', 'gas bill', 'water', 'internet', 'phone', 'cable', 'utility'],
            'Healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'dental', 'health'],
            'Subscriptions': ['subscription', 'membership', 'monthly', 'annual', 'premium'],
            'Travel': ['hotel', 'flight', 'airline', 'booking', 'airbnb', 'travel'],
            'Other': []
        }
        
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name as string
        """
        description_lower = description.lower()
        
        for category, keywords in self.category_keywords.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'
    
    def generate_sample_data(self) -> List[Dict[str, Any]]:
        """
        Generate sample transaction data for demonstration.
        
        Returns:
            List of transaction dictionaries
        """
        sample_transactions = [
            # Food & Dining
            {"date": "2024-01-15", "amount": 45.67, "description": "Restaurant ABC", "type": "debit"},
            {"date": "2024-01-16", "amount": 12.50, "description": "Starbucks Coffee", "type": "debit"},
            {"date": "2024-01-18", "amount": 78.90, "description": "Pizza Palace", "type": "debit"},
            {"date": "2024-01-20", "amount": 35.25, "description": "Food Delivery", "type": "debit"},
            {"date": "2024-01-22", "amount": 89.15, "description": "Fine Dining Restaurant", "type": "debit"},
            
            # Groceries
            {"date": "2024-01-14", "amount": 125.30, "description": "Walmart Grocery", "type": "debit"},
            {"date": "2024-01-21", "amount": 87.45, "description": "Safeway Supermarket", "type": "debit"},
            {"date": "2024-01-28", "amount": 156.78, "description": "Whole Foods Market", "type": "debit"},
            
            # Transportation
            {"date": "2024-01-17", "amount": 45.00, "description": "Gas Station", "type": "debit"},
            {"date": "2024-01-19", "amount": 15.75, "description": "Uber Ride", "type": "debit"},
            {"date": "2024-01-25", "amount": 48.20, "description": "Gas Fill Up", "type": "debit"},
            {"date": "2024-01-27", "amount": 25.50, "description": "Parking Fee", "type": "debit"},
            
            # Shopping
            {"date": "2024-01-23", "amount": 234.99, "description": "Amazon Purchase", "type": "debit"},
            {"date": "2024-01-26", "amount": 189.50, "description": "Electronics Store", "type": "debit"},
            {"date": "2024-01-29", "amount": 75.25, "description": "Clothing Store", "type": "debit"},
            
            # Entertainment
            {"date": "2024-01-24", "amount": 15.99, "description": "Netflix Subscription", "type": "debit"},
            {"date": "2024-01-30", "amount": 9.99, "description": "Spotify Premium", "type": "debit"},
            {"date": "2024-01-31", "amount": 45.00, "description": "Movie Theater", "type": "debit"},
            
            # Utilities
            {"date": "2024-01-01", "amount": 85.50, "description": "Electric Bill", "type": "debit"},
            {"date": "2024-01-01", "amount": 65.00, "description": "Internet Service", "type": "debit"},
            {"date": "2024-01-01", "amount": 45.30, "description": "Water Utility", "type": "debit"},
        ]
        
        return sample_transactions
    
    def analyze_spending_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze spending patterns from transaction data.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Categorize transactions
            categorized_spending = defaultdict(list)
            total_spending = 0
            monthly_spending = defaultdict(float)
            
            for transaction in transactions:
                if transaction['type'] == 'debit' and transaction['amount'] > 0:
                    category = self.categorize_transaction(transaction['description'])
                    amount = transaction['amount']
                    
                    categorized_spending[category].append({
                        'amount': amount,
                        'date': transaction['date'],
                        'description': transaction['description']
                    })
                    
                    total_spending += amount
                    
                    # Track monthly spending
                    date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                    monthly_spending[month_key] += amount
            
            # Calculate category totals and percentages
            category_analysis = {}
            for category, transactions_list in categorized_spending.items():
                total_category_spending = sum(t['amount'] for t in transactions_list)
                avg_transaction = total_category_spending / len(transactions_list)
                percentage = (total_category_spending / total_spending) * 100
                
                category_analysis[category] = {
                    'total_spending': total_category_spending,
                    'transaction_count': len(transactions_list),
                    'average_transaction': avg_transaction,
                    'percentage_of_