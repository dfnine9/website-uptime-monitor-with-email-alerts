```python
#!/usr/bin/env python3
"""
Transaction Categorization Module

A self-contained expense classification system that uses configurable keyword
matching rules to automatically categorize financial transactions. Supports
custom rule sets and provides detailed categorization results.

Usage:
    python script.py

The module processes sample transactions and categorizes them based on
predefined keyword rules for categories like groceries, gas, restaurants,
shopping, utilities, and entertainment.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Transaction:
    """Represents a financial transaction with basic details."""
    id: str
    description: str
    amount: float
    date: str
    category: Optional[str] = None
    confidence: float = 0.0


class TransactionCategorizer:
    """
    A configurable transaction categorizer that uses keyword matching rules
    to classify expenses into predefined categories.
    """
    
    def __init__(self, custom_rules: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the categorizer with default or custom rules.
        
        Args:
            custom_rules: Optional dictionary of category -> keyword list mappings
        """
        self.default_rules = {
            'groceries': [
                'grocery', 'supermarket', 'safeway', 'kroger', 'walmart', 'target',
                'whole foods', 'trader joe', 'costco', 'market', 'food store',
                'fresh market', 'organic', 'produce'
            ],
            'gas': [
                'gas', 'fuel', 'station', 'chevron', 'shell', 'exxon', 'bp',
                'mobil', 'texaco', 'arco', 'speedway', 'wawa', 'circle k'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald',
                'burger', 'pizza', 'taco', 'subway', 'chipotle', 'dining',
                'kitchen', 'grill', 'bistro', 'bar', 'pub', 'food truck'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'mall', 'retail', 'shop',
                'clothing', 'fashion', 'electronics', 'best buy',
                'home depot', 'lowes', 'pharmacy', 'cvs', 'walgreens'
            ],
            'utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone',
                'cable', 'utility', 'power', 'heating', 'cooling',
                'verizon', 'att', 'comcast', 'spectrum'
            ],
            'entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'game',
                'concert', 'tickets', 'entertainment', 'streaming',
                'subscription', 'gym', 'fitness', 'sports'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                'parking', 'toll', 'airline', 'flight', 'car rental'
            ],
            'healthcare': [
                'doctor', 'hospital', 'pharmacy', 'medical', 'dental',
                'clinic', 'health', 'medicine', 'prescription'
            ]
        }
        
        # Use custom rules if provided, otherwise use defaults
        self.rules = custom_rules if custom_rules else self.default_rules
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        self.compiled_patterns = {}
        for category, keywords in self.rules.items():
            # Create case-insensitive pattern that matches whole words
            pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            self.compiled_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def categorize_transaction(self, transaction: Transaction) -> Transaction:
        """
        Categorize a single transaction based on keyword matching.
        
        Args:
            transaction: Transaction object to categorize
            
        Returns:
            Transaction object with category and confidence assigned
        """
        try:
            best_category = 'other'
            best_confidence = 0.0
            matches_found = {}
            
            description = transaction.description.lower()
            
            # Check each category for keyword matches
            for category, pattern in self.compiled_patterns.items():
                matches = pattern.findall(description)
                if matches:
                    # Calculate confidence based on number of matches and keyword specificity
                    match_count = len(matches)
                    unique_matches = len(set(matches))
                    
                    # Confidence score: weighted by unique matches and total matches
                    confidence = (unique_matches * 0.6 + match_count * 0.4) / len(self.rules[category])
                    confidence = min(confidence, 1.0)  # Cap at 100%
                    
                    matches_found[category] = {
                        'confidence': confidence,
                        'matches': matches,
                        'unique_matches': unique_matches
                    }
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_category = category
            
            # If no matches found, keep as 'other' with 0 confidence
            transaction.category = best_category
            transaction.confidence = round(best_confidence, 3)
            
            return transaction
            
        except Exception as e:
            print(f"Error categorizing transaction {transaction.id}: {str(e)}")
            transaction.category = 'error'
            transaction.confidence = 0.0
            return transaction
    
    def categorize_batch(self, transactions: List[Transaction]) -> List[Transaction]:
        """
        Categorize a batch of transactions.
        
        Args:
            transactions: List of Transaction objects to categorize
            
        Returns:
            List of categorized Transaction objects
        """
        try:
            categorized = []
            for transaction in transactions:
                categorized.append(self.categorize_transaction(transaction))
            return categorized
        except Exception as e:
            print(f"Error in batch categorization: {str(e)}")
            return transactions
    
    def add_rule(self, category: str, keywords: List[str]):
        """
        Add or update a categorization rule.
        
        Args:
            category: Category name
            keywords: List of keywords for the category
        """
        try:
            self.rules[category] = keywords
            self._compile_patterns()
            print(f"Rule for category '{category}' updated with {len(keywords)} keywords")
        except Exception as e:
            print(f"Error adding rule: {str(e)}")
    
    def get_category_summary(self, transactions: List[Transaction]) -> Dict:
        """
        Generate a summary of categorized transactions.
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Dictionary with category statistics
        """
        try:
            summary = {
                'total_transactions': len(transactions),
                'categories': {},
                'total_amount': 0.0,
                'avg_confidence': 0.0
            }
            
            category_stats = {}
            total_confidence = 0.0
            
            for transaction in transactions:
                category = transaction.category
                amount = abs(transaction.amount)  # Use absolute value for expenses
                
                if category not in category_stats:
                    category_stats[category] = {
                        'count': 0,
                        'total_amount': 0.0,
                        'avg_confidence': 0.0,
                        'transactions': []
                    }
                
                category_stats[category]['count'] += 1
                category_stats[category]['total_amount'] += amount
                category_stats[category]['transactions'].append(transaction.id)
                
                summary['total_amount'] += amount
                total_confidence += transaction.confidence
            
            # Calculate averages and percentages