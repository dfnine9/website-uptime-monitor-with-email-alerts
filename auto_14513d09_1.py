```python
"""
Expense Categorization Engine

This module provides an expense categorization system that uses keyword matching
against merchant names and descriptions. It implements fuzzy string matching for
merchant name variations and includes a predefined dictionary of common expense
categories like groceries, gas, dining, etc.

The engine uses a two-tier matching system:
1. Exact keyword matching for high confidence categorization
2. Fuzzy string matching using difflib for merchant name variations

Usage:
    python script.py

The script will demonstrate categorization of sample transactions and can be
extended to process actual expense data.
"""

import re
import difflib
from typing import Dict, List, Tuple, Optional


class ExpenseCategorizationEngine:
    """
    A categorization engine that matches expenses to categories using
    keyword matching and fuzzy string matching.
    """
    
    def __init__(self):
        """Initialize the categorization engine with predefined categories."""
        self.categories = {
            'groceries': {
                'keywords': [
                    'grocery', 'supermarket', 'market', 'food', 'safeway', 
                    'kroger', 'walmart', 'target', 'whole foods', 'trader joe',
                    'costco', 'sams club', 'aldi', 'publix', 'wegmans'
                ],
                'merchants': [
                    'safeway', 'kroger', 'walmart supercenter', 'target',
                    'whole foods market', 'trader joes', 'costco wholesale',
                    'sams club', 'aldi', 'publix', 'wegmans'
                ]
            },
            'gas': {
                'keywords': [
                    'gas', 'fuel', 'station', 'shell', 'bp', 'exxon', 'chevron',
                    'mobil', 'texaco', 'sunoco', 'marathon', 'speedway'
                ],
                'merchants': [
                    'shell', 'bp', 'exxon mobil', 'chevron', 'mobil',
                    'texaco', 'sunoco', 'marathon', 'speedway'
                ]
            },
            'dining': {
                'keywords': [
                    'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'taco',
                    'mcdonalds', 'subway', 'starbucks', 'chipotle', 'panera',
                    'kfc', 'wendys', 'dominos', 'papa johns'
                ],
                'merchants': [
                    'mcdonalds', 'subway', 'starbucks', 'chipotle',
                    'panera bread', 'kfc', 'wendys', 'dominos pizza',
                    'papa johns', 'taco bell'
                ]
            },
            'entertainment': {
                'keywords': [
                    'movie', 'theater', 'cinema', 'netflix', 'spotify',
                    'amazon prime', 'hulu', 'disney', 'gaming', 'xbox'
                ],
                'merchants': [
                    'netflix', 'spotify', 'amazon prime video', 'hulu',
                    'disney plus', 'xbox live', 'steam'
                ]
            },
            'retail': {
                'keywords': [
                    'amazon', 'ebay', 'department store', 'clothing', 'shoes',
                    'macys', 'nordstrom', 'gap', 'old navy', 'best buy'
                ],
                'merchants': [
                    'amazon', 'ebay', 'macys', 'nordstrom', 'gap',
                    'old navy', 'best buy', 'target'
                ]
            },
            'utilities': {
                'keywords': [
                    'electric', 'water', 'gas bill', 'internet', 'phone',
                    'verizon', 'att', 'comcast', 'pge', 'utility'
                ],
                'merchants': [
                    'verizon', 'att', 'comcast', 'pacific gas electric',
                    'pg&e', 'city water dept'
                ]
            },
            'transportation': {
                'keywords': [
                    'uber', 'lyft', 'taxi', 'bus', 'train', 'subway',
                    'metro', 'parking', 'toll'
                ],
                'merchants': [
                    'uber', 'lyft', 'metro transit', 'parking meter'
                ]
            },
            'health': {
                'keywords': [
                    'pharmacy', 'medical', 'doctor', 'hospital', 'dental',
                    'cvs', 'walgreens', 'rite aid'
                ],
                'merchants': [
                    'cvs pharmacy', 'walgreens', 'rite aid'
                ]
            }
        }
        
        # Compile regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for each category for efficient matching."""
        self.compiled_patterns = {}
        for category, data in self.categories.items():
            pattern = '|'.join(re.escape(keyword.lower()) for keyword in data['keywords'])
            self.compiled_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def _fuzzy_match_merchant(self, merchant: str, threshold: float = 0.7) -> Optional[str]:
        """
        Use fuzzy string matching to find the best category match for a merchant.
        
        Args:
            merchant: Merchant name to match
            threshold: Minimum similarity score (0.0 to 1.0)
        
        Returns:
            Best matching category or None if no match above threshold
        """
        best_match = None
        best_score = 0
        
        merchant_lower = merchant.lower()
        
        for category, data in self.categories.items():
            for known_merchant in data['merchants']:
                similarity = difflib.SequenceMatcher(
                    None, merchant_lower, known_merchant.lower()
                ).ratio()
                
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = category
        
        return best_match
    
    def categorize_transaction(self, merchant: str, description: str = "") -> Tuple[Optional[str], float]:
        """
        Categorize a transaction based on merchant name and description.
        
        Args:
            merchant: Merchant name
            description: Transaction description (optional)
        
        Returns:
            Tuple of (category, confidence_score)
        """
        try:
            # Combine merchant and description for keyword matching
            text_to_search = f"{merchant} {description}".lower()
            
            # First, try exact keyword matching
            for category, pattern in self.compiled_patterns.items():
                if pattern.search(text_to_search):
                    return category, 1.0
            
            # If no keyword match, try fuzzy matching on merchant name
            fuzzy_category = self._fuzzy_match_merchant(merchant)
            if fuzzy_category:
                return fuzzy_category, 0.8
            
            # No match found
            return None, 0.0
            
        except Exception as e:
            print(f"Error categorizing transaction: {e}")
            return None, 0.0
    
    def categorize_batch(self, transactions: List[Dict[str, str]]) -> List[Dict[str, any]]:
        """
        Categorize a batch of transactions.
        
        Args:
            transactions: List of transaction dictionaries with 'merchant' and optional 'description'
        
        Returns:
            List of categorized transactions with category and confidence
        """
        results = []
        
        for transaction in transactions:
            try:
                merchant = transaction.get('merchant', '')
                description = transaction.get('description', '')
                
                category, confidence = self.categorize_transaction(merchant, description)
                
                result = {
                    'merchant': merchant,
                    'description': description,
                    'category': category or 'uncategorized',
                    'confidence': confidence
                }
                results.append