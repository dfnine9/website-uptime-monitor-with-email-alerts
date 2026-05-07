```python
"""
Transaction Categorization System

A rule-based expense categorization system that matches transaction descriptions
against predefined keyword dictionaries to assign expense categories with 
confidence scores.

Features:
- Predefined keyword dictionaries for common expense categories
- Fuzzy string matching for partial keyword detection
- Confidence scoring based on keyword match strength
- Case-insensitive matching with normalization
- Comprehensive error handling
- Self-contained implementation using only standard library

Usage:
    python script.py

The script will categorize sample transactions and display results with
category assignments and confidence scores.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher


class TransactionCategorizer:
    """Rule-based transaction categorization system."""
    
    def __init__(self):
        """Initialize categorizer with predefined keyword dictionaries."""
        self.category_keywords = {
            'groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway',
                'whole foods', 'trader joe', 'costco', 'sams club', 'food lion',
                'publix', 'wegmans', 'aldi', 'giant', 'stop shop', 'market',
                'fresh market', 'organic', 'produce'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'burger',
                'pizza', 'subway', 'taco bell', 'kfc', 'wendys', 'chipotle',
                'panera', 'dominos', 'papa john', 'dunkin', 'dining', 'bistro',
                'grill', 'bar', 'pub', 'diner', 'takeout', 'delivery'
            ],
            'gas': [
                'gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                'texaco', 'citgo', 'sunoco', 'speedway', 'marathon', 'valero',
                'station', 'petroleum', 'gasoline'
            ],
            'utilities': [
                'electric', 'electricity', 'power', 'water', 'sewer', 'gas utility',
                'internet', 'cable', 'phone', 'wireless', 'verizon', 'att',
                'comcast', 'spectrum', 'utility', 'energy', 'heating', 'cooling'
            ],
            'entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'amazon prime',
                'hulu', 'disney', 'entertainment', 'concert', 'ticket', 'event',
                'music', 'streaming', 'game', 'arcade', 'amusement'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'store', 'retail', 'clothing', 'shoes',
                'electronics', 'best buy', 'home depot', 'lowes', 'department',
                'fashion', 'accessories', 'online', 'shopping'
            ],
            'healthcare': [
                'medical', 'doctor', 'hospital', 'pharmacy', 'dentist', 'clinic',
                'health', 'prescription', 'cvs', 'walgreens', 'rite aid',
                'medicare', 'insurance', 'dental', 'vision'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking',
                'toll', 'airline', 'flight', 'car rental', 'transport'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'transfer', 'deposit', 'withdrawal',
                'interest', 'loan', 'credit', 'overdraft', 'maintenance'
            ],
            'other': []
        }
        
        # Compile regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for each category."""
        self.compiled_patterns = {}
        for category, keywords in self.category_keywords.items():
            if keywords:
                pattern = '|'.join(re.escape(keyword) for keyword in keywords)
                self.compiled_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def _normalize_description(self, description: str) -> str:
        """Normalize transaction description for better matching."""
        try:
            # Convert to lowercase and remove extra whitespace
            normalized = re.sub(r'\s+', ' ', description.lower().strip())
            # Remove special characters except spaces and alphanumeric
            normalized = re.sub(r'[^\w\s]', ' ', normalized)
            return normalized
        except Exception as e:
            print(f"Error normalizing description: {e}")
            return description.lower()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher."""
        try:
            return SequenceMatcher(None, text1, text2).ratio()
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def _get_exact_matches(self, description: str, category: str) -> List[str]:
        """Get exact keyword matches for a category."""
        matches = []
        try:
            if category in self.compiled_patterns:
                pattern_matches = self.compiled_patterns[category].findall(description)
                matches.extend(pattern_matches)
        except Exception as e:
            print(f"Error finding exact matches: {e}")
        
        return matches
    
    def _get_fuzzy_matches(self, description: str, category: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Get fuzzy keyword matches for a category."""
        fuzzy_matches = []
        try:
            words = description.split()
            for keyword in self.category_keywords.get(category, []):
                for word in words:
                    similarity = self._calculate_similarity(word, keyword)
                    if similarity >= threshold:
                        fuzzy_matches.append((keyword, similarity))
        except Exception as e:
            print(f"Error finding fuzzy matches: {e}")
        
        return fuzzy_matches
    
    def categorize_transaction(self, description: str, amount: float = 0.0) -> Dict:
        """
        Categorize a single transaction.
        
        Args:
            description: Transaction description
            amount: Transaction amount (optional, for future enhancements)
        
        Returns:
            Dictionary with category, confidence, and match details
        """
        try:
            normalized_desc = self._normalize_description(description)
            
            category_scores = {}
            match_details = {}
            
            # Score each category
            for category in self.category_keywords.keys():
                if category == 'other':
                    continue
                
                # Get exact matches
                exact_matches = self._get_exact_matches(normalized_desc, category)
                
                # Get fuzzy matches
                fuzzy_matches = self._get_fuzzy_matches(normalized_desc, category)
                
                # Calculate category score
                score = 0.0
                
                # Exact matches get full points
                score += len(exact_matches) * 1.0
                
                # Fuzzy matches get weighted points
                for _, similarity in fuzzy_matches:
                    score += similarity * 0.7
                
                # Normalize score by description length (word count)
                word_count = len(normalized_desc.split())
                if word_count > 0:
                    score = min(score / word_count * 2, 1.0)  # Cap at 1.0
                
                category_scores[category] = score
                match_details[category] = {
                    'exact_matches': exact_matches,
                    'fuzzy_matches': fuzzy_matches
                }
            
            # Find best category
            if category_scores:
                best_category = max(category_scores.keys