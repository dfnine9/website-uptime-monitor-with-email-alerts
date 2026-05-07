```python
"""
Transaction Categorization Engine

This module provides a sophisticated transaction categorization system that:
1. Matches transaction descriptions against keyword patterns
2. Handles edge cases and ambiguous descriptions
3. Assigns expense categories with confidence scores
4. Uses fuzzy matching and multiple scoring methods for accuracy

The engine supports common expense categories like groceries, restaurants, gas,
utilities, and more, with configurable confidence thresholds.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import difflib


class TransactionCategorizationEngine:
    def __init__(self):
        """Initialize the categorization engine with predefined patterns."""
        self.categories = {
            'groceries': {
                'keywords': ['grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway', 
                           'whole foods', 'trader joe', 'costco', 'sams club', 'food lion',
                           'publix', 'stop shop', 'giant', 'aldi', 'wegmans', 'heb'],
                'patterns': [r'\bfood\b', r'\bgrocery\b', r'\bmarket\b'],
                'weight': 1.0
            },
            'restaurants': {
                'keywords': ['restaurant', 'cafe', 'bistro', 'grill', 'pizza', 'burger',
                           'mcdonalds', 'subway', 'starbucks', 'dunkin', 'kfc', 'taco bell',
                           'chipotle', 'panera', 'olive garden', 'applebee', 'chili'],
                'patterns': [r'\brest\b', r'\bcafe\b', r'\bdining\b', r'\beat\b'],
                'weight': 1.0
            },
            'gas': {
                'keywords': ['gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp', 'mobil',
                           'valero', 'citgo', 'speedway', 'wawa', '7-eleven'],
                'patterns': [r'\bgas\b', r'\bfuel\b', r'\bstation\b'],
                'weight': 1.2
            },
            'utilities': {
                'keywords': ['electric', 'water', 'gas bill', 'utility', 'power', 'energy',
                           'pg&e', 'southern company', 'duke energy', 'edison', 'comcast',
                           'verizon', 'att', 'internet', 'phone', 'cable'],
                'patterns': [r'\butility\b', r'\belectric\b', r'\bwater\b', r'\binternet\b'],
                'weight': 1.1
            },
            'transportation': {
                'keywords': ['uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking',
                           'toll', 'subway', 'transit', 'car wash', 'auto repair'],
                'patterns': [r'\btransit\b', r'\bparking\b', r'\btoll\b', r'\brepair\b'],
                'weight': 1.0
            },
            'shopping': {
                'keywords': ['amazon', 'ebay', 'store', 'shop', 'mall', 'retail',
                           'clothing', 'electronics', 'best buy', 'home depot', 'lowes'],
                'patterns': [r'\bstore\b', r'\bshop\b', r'\bretail\b', r'\bmall\b'],
                'weight': 0.8
            },
            'healthcare': {
                'keywords': ['medical', 'doctor', 'hospital', 'pharmacy', 'cvs', 'walgreens',
                           'clinic', 'dental', 'health', 'prescription', 'medicare'],
                'patterns': [r'\bmed\b', r'\bdoctor\b', r'\bhealth\b', r'\bpharm\b'],
                'weight': 1.1
            },
            'entertainment': {
                'keywords': ['movie', 'theater', 'netflix', 'spotify', 'gaming', 'concert',
                           'ticket', 'amusement', 'park', 'museum', 'gym', 'fitness'],
                'patterns': [r'\bmovie\b', r'\bgame\b', r'\bticket\b', r'\bgym\b'],
                'weight': 0.9
            },
            'finance': {
                'keywords': ['bank', 'atm', 'fee', 'interest', 'loan', 'credit', 'investment',
                           'insurance', 'tax', 'irs', 'transfer', 'payment'],
                'patterns': [r'\bbank\b', r'\bfee\b', r'\bloan\b', r'\btax\b'],
                'weight': 1.0
            }
        }
        
        self.min_confidence = 0.3
        self.fuzzy_threshold = 0.6
    
    def clean_description(self, description: str) -> str:
        """Clean and normalize transaction description."""
        try:
            # Convert to lowercase and remove special characters
            cleaned = re.sub(r'[^\w\s-]', '', description.lower())
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            # Remove common transaction prefixes
            cleaned = re.sub(r'^(purchase|payment|debit|credit)\s+', '', cleaned)
            return cleaned
        except Exception as e:
            print(f"Error cleaning description: {e}")
            return description.lower()
    
    def exact_keyword_match(self, description: str, category_data: Dict) -> float:
        """Calculate score based on exact keyword matches."""
        score = 0.0
        words = description.split()
        
        for keyword in category_data['keywords']:
            if keyword in description:
                # Bonus for whole word matches
                if re.search(rf'\b{re.escape(keyword)}\b', description):
                    score += 1.0
                else:
                    score += 0.7
        
        return min(score, 1.0)
    
    def pattern_match(self, description: str, category_data: Dict) -> float:
        """Calculate score based on regex pattern matches."""
        score = 0.0
        
        for pattern in category_data.get('patterns', []):
            try:
                if re.search(pattern, description, re.IGNORECASE):
                    score += 0.8
            except re.error:
                continue
        
        return min(score, 1.0)
    
    def fuzzy_match(self, description: str, category_data: Dict) -> float:
        """Calculate score based on fuzzy string matching."""
        max_score = 0.0
        words = description.split()
        
        for keyword in category_data['keywords']:
            for word in words:
                if len(word) > 2:  # Skip very short words
                    similarity = difflib.SequenceMatcher(None, word, keyword).ratio()
                    if similarity > self.fuzzy_threshold:
                        max_score = max(max_score, similarity * 0.6)
        
        return max_score
    
    def calculate_category_score(self, description: str, category: str, category_data: Dict) -> float:
        """Calculate overall score for a category."""
        try:
            exact_score = self.exact_keyword_match(description, category_data)
            pattern_score = self.pattern_match(description, category_data)
            fuzzy_score = self.fuzzy_match(description, category_data)
            
            # Weighted combination of scores
            combined_score = (exact_score * 0.5 + pattern_score * 0.3 + fuzzy_score * 0.2)
            
            # Apply category weight
            weighted_score = combined_score * category_data.get('weight', 1.0)
            
            return min(weighted_score, 1.0)
        
        except Exception as e:
            print(f"Error calculating score for category {category}: {e}")
            return