```python
"""
Personal Finance Categorization Engine

This module provides a transaction categorization system that matches transaction
descriptions against predefined keyword dictionaries to automatically assign
expense categories such as groceries, dining, utilities, transportation, etc.

The engine uses fuzzy string matching and keyword weighting to determine the most
appropriate category for each transaction description. It includes comprehensive
error handling and outputs results in a structured format.

Usage:
    python script.py

Dependencies:
    - Python standard library only
    - No external dependencies required
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class TransactionCategorizer:
    """
    A categorization engine that matches transaction descriptions to expense categories.
    """
    
    def __init__(self):
        """Initialize the categorizer with predefined keyword dictionaries."""
        self.categories = {
            'groceries': {
                'keywords': ['grocery', 'supermarket', 'market', 'food', 'walmart', 'target', 
                           'safeway', 'kroger', 'whole foods', 'trader joe', 'costco', 'sams club',
                           'fresh', 'organic', 'produce', 'deli', 'bakery', 'meat', 'dairy'],
                'weight': 1.0
            },
            'dining': {
                'keywords': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'sushi', 'taco',
                           'mcdonald', 'subway', 'starbucks', 'kfc', 'domino', 'chipotle',
                           'dining', 'bistro', 'grill', 'bar', 'pub', 'kitchen', 'eatery'],
                'weight': 1.0
            },
            'utilities': {
                'keywords': ['electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
                           'utility', 'power', 'energy', 'heating', 'cooling', 'telecom',
                           'verizon', 'att', 'comcast', 'pge', 'edison', 'municipal'],
                'weight': 1.2
            },
            'transportation': {
                'keywords': ['gas station', 'fuel', 'gasoline', 'uber', 'lyft', 'taxi', 'bus',
                           'train', 'subway', 'parking', 'toll', 'auto', 'car wash', 'mechanic',
                           'shell', 'exxon', 'chevron', 'bp', 'mobil', 'metro', 'transit'],
                'weight': 1.0
            },
            'entertainment': {
                'keywords': ['movie', 'theater', 'cinema', 'netflix', 'spotify', 'gaming',
                           'concert', 'show', 'museum', 'park', 'zoo', 'amusement', 'tickets',
                           'entertainment', 'streaming', 'subscription', 'hulu', 'amazon prime'],
                'weight': 0.9
            },
            'healthcare': {
                'keywords': ['hospital', 'doctor', 'medical', 'pharmacy', 'dentist', 'clinic',
                           'health', 'prescription', 'medicine', 'cvs', 'walgreens', 'rite aid',
                           'urgent care', 'emergency', 'insurance', 'copay', 'deductible'],
                'weight': 1.1
            },
            'shopping': {
                'keywords': ['amazon', 'ebay', 'store', 'shop', 'retail', 'mall', 'outlet',
                           'clothing', 'shoes', 'electronics', 'home depot', 'lowes', 'best buy',
                           'department', 'boutique', 'online', 'purchase', 'buy'],
                'weight': 0.8
            },
            'insurance': {
                'keywords': ['insurance', 'premium', 'policy', 'coverage', 'deductible',
                           'allstate', 'geico', 'state farm', 'progressive', 'auto insurance',
                           'home insurance', 'health insurance', 'life insurance'],
                'weight': 1.3
            },
            'banking': {
                'keywords': ['bank', 'atm', 'fee', 'charge', 'overdraft', 'maintenance',
                           'transfer', 'wire', 'check', 'deposit', 'withdrawal', 'interest',
                           'chase', 'wells fargo', 'bank of america', 'citibank'],
                'weight': 1.1
            },
            'education': {
                'keywords': ['school', 'university', 'college', 'tuition', 'books', 'supplies',
                           'education', 'learning', 'course', 'training', 'certification',
                           'student', 'academic', 'textbook', 'library'],
                'weight': 1.0
            }
        }
    
    def preprocess_description(self, description: str) -> str:
        """
        Clean and normalize transaction description for better matching.
        
        Args:
            description: Raw transaction description
            
        Returns:
            Cleaned and normalized description
        """
        try:
            # Convert to lowercase
            cleaned = description.lower().strip()
            
            # Remove special characters but keep spaces and alphanumeric
            cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
            
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            
            return cleaned
        except Exception as e:
            print(f"Error preprocessing description '{description}': {e}")
            return description.lower()
    
    def calculate_category_score(self, description: str, category: str) -> float:
        """
        Calculate matching score between description and category keywords.
        
        Args:
            description: Preprocessed transaction description
            category: Category name to check against
            
        Returns:
            Weighted score for the category match
        """
        try:
            keywords = self.categories[category]['keywords']
            weight = self.categories[category]['weight']
            
            score = 0.0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in description:
                    # Exact match gets full points
                    score += 1.0
                    matched_keywords.append(keyword)
                elif any(word in keyword or keyword in word for word in description.split()):
                    # Partial match gets half points
                    score += 0.5
                    matched_keywords.append(f"{keyword}*")
            
            # Apply category weight
            weighted_score = score * weight
            
            return weighted_score
            
        except Exception as e:
            print(f"Error calculating score for category '{category}': {e}")
            return 0.0
    
    def categorize_transaction(self, description: str) -> Dict:
        """
        Categorize a single transaction based on its description.
        
        Args:
            description: Transaction description to categorize
            
        Returns:
            Dictionary with category, confidence, and match details
        """
        try:
            cleaned_desc = self.preprocess_description(description)
            
            if not cleaned_desc:
                return {
                    'original_description': description,
                    'category': 'uncategorized',
                    'confidence': 0.0,
                    'scores': {},
                    'error': 'Empty description after cleaning'
                }
            
            # Calculate scores for each category
            scores = {}
            for category in self.categories:
                scores[category] = self.calculate_category_score(cleaned_desc, category)
            
            # Find best matching category
            best_category = max(scores, key=scores.get)
            best_score = scores[best_category]
            
            # Calculate confidence (normalize score)
            max_possible_score = len(self.categories[best_category]['keywords']) * \
                               self.categories[best_category]['weight']
            confidence = min(best_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
            
            # If confidence is too low, mark as uncategorized
            if confidence