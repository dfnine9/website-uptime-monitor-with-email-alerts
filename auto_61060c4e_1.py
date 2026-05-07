```python
#!/usr/bin/env python3
"""
Transaction Categorization Module

This module automatically categorizes financial transactions into predefined categories
using keyword matching and regex patterns. It processes transaction descriptions and
assigns them to categories like groceries, utilities, entertainment, transportation,
and dining based on merchant names, transaction descriptions, and common patterns.

The categorizer uses a combination of:
- Exact keyword matching for known merchants and services
- Regex patterns for common transaction formats
- Fallback category assignment for unmatched transactions

Categories supported:
- Groceries: Supermarkets, food stores, grocery chains
- Utilities: Electric, gas, water, internet, phone bills
- Entertainment: Movies, streaming, games, concerts
- Transportation: Gas stations, public transit, rideshare, parking
- Dining: Restaurants, cafes, food delivery, bars
- Shopping: Retail stores, online shopping, clothing
- Healthcare: Medical, pharmacy, insurance
- Other: Unmatched transactions
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """Represents a financial transaction"""
    date: str
    description: str
    amount: float
    category: Optional[str] = None


class TransactionCategorizer:
    """Categorizes transactions based on keywords and regex patterns"""
    
    def __init__(self):
        self.categories = {
            'groceries': {
                'keywords': [
                    'walmart', 'target', 'kroger', 'safeway', 'whole foods',
                    'trader joe', 'costco', 'sams club', 'publix', 'wegmans',
                    'aldi', 'food lion', 'harris teeter', 'giant', 'stop shop',
                    'market', 'grocery', 'supermarket', 'food store'
                ],
                'patterns': [
                    r'\bwm\b.*supercenter',
                    r'grocery.*store',
                    r'market.*\d+',
                    r'food.*mart'
                ]
            },
            'utilities': {
                'keywords': [
                    'electric', 'electricity', 'power', 'gas company', 'water',
                    'sewer', 'internet', 'cable', 'phone', 'wireless',
                    'verizon', 'att', 'tmobile', 'sprint', 'comcast',
                    'xfinity', 'spectrum', 'cox', 'directv', 'dish'
                ],
                'patterns': [
                    r'electric.*co',
                    r'gas.*utility',
                    r'water.*dept',
                    r'city.*utilities',
                    r'municipal.*services'
                ]
            },
            'entertainment': {
                'keywords': [
                    'netflix', 'hulu', 'disney', 'amazon prime', 'spotify',
                    'apple music', 'youtube', 'movie', 'theater', 'cinema',
                    'concert', 'ticket', 'gaming', 'steam', 'xbox', 'playstation',
                    'entertainment', 'amusement', 'recreation'
                ],
                'patterns': [
                    r'movie.*theater',
                    r'cinema.*\d+',
                    r'streaming.*service',
                    r'game.*store'
                ]
            },
            'transportation': {
                'keywords': [
                    'gas', 'gasoline', 'fuel', 'shell', 'exxon', 'bp',
                    'chevron', 'mobil', 'uber', 'lyft', 'taxi', 'metro',
                    'bus', 'train', 'subway', 'parking', 'toll', 'dmv',
                    'car wash', 'auto', 'mechanic'
                ],
                'patterns': [
                    r'gas.*station',
                    r'fuel.*\d+',
                    r'parking.*meter',
                    r'toll.*road',
                    r'auto.*service'
                ]
            },
            'dining': {
                'keywords': [
                    'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin',
                    'mcdonalds', 'burger king', 'subway', 'pizza', 'dominos',
                    'kfc', 'taco bell', 'chipotle', 'panera', 'chilis',
                    'applebees', 'olive garden', 'bar', 'pub', 'grill',
                    'doordash', 'uber eats', 'grubhub', 'takeout'
                ],
                'patterns': [
                    r'restaurant.*\d+',
                    r'cafe.*\w+',
                    r'pizza.*\w+',
                    r'bar.*grill',
                    r'food.*delivery'
                ]
            },
            'shopping': {
                'keywords': [
                    'amazon', 'ebay', 'best buy', 'home depot', 'lowes',
                    'macys', 'nordstrom', 'kohls', 'jcpenney', 'sears',
                    'clothing', 'shoes', 'electronics', 'furniture',
                    'online purchase', 'retail', 'department store'
                ],
                'patterns': [
                    r'amzn.*mktp',
                    r'paypal.*\w+',
                    r'online.*purchase',
                    r'retail.*store'
                ]
            },
            'healthcare': {
                'keywords': [
                    'hospital', 'clinic', 'doctor', 'medical', 'pharmacy',
                    'cvs', 'walgreens', 'rite aid', 'dentist', 'dental',
                    'insurance', 'health', 'prescription', 'medicine'
                ],
                'patterns': [
                    r'medical.*center',
                    r'health.*care',
                    r'pharmacy.*\d+',
                    r'dr\..*\w+'
                ]
            }
        }
    
    def normalize_description(self, description: str) -> str:
        """Normalize transaction description for matching"""
        try:
            # Convert to lowercase and remove extra whitespace
            normalized = re.sub(r'\s+', ' ', description.lower().strip())
            # Remove common transaction codes and numbers at the end
            normalized = re.sub(r'\s+\d{4,}$', '', normalized)
            # Remove special characters except spaces and hyphens
            normalized = re.sub(r'[^\w\s\-]', ' ', normalized)
            return normalized
        except Exception as e:
            print(f"Error normalizing description '{description}': {e}")
            return description.lower()
    
    def match_keywords(self, description: str, keywords: List[str]) -> bool:
        """Check if any keywords match the description"""
        try:
            normalized_desc = self.normalize_description(description)
            for keyword in keywords:
                if keyword.lower() in normalized_desc:
                    return True
            return False
        except Exception as e:
            print(f"Error matching keywords for '{description}': {e}")
            return False
    
    def match_patterns(self, description: str, patterns: List[str]) -> bool:
        """Check if any regex patterns match the description"""
        try:
            normalized_desc = self.normalize_description(description)
            for pattern in patterns:
                if re.search(pattern, normalized_desc, re.IGNORECASE):
                    return True
            return False
        except Exception as e:
            print(f"Error matching patterns for '{description}': {e}")
            return False
    
    def categorize_transaction(self, transaction: Transaction) -> str:
        """Categorize a single transaction"""
        try:
            description = transaction.description
            
            # Check each category for matches
            for category, rules in self.categories.items():
                # Check keyword matches
                if self.match_keywords(description, rules['keywords']):
                    return category
                
                # Check pattern matches
                if self.match_patterns(description, rules['patterns']):
                    return category
            
            # Default category if no matches found
            return 'other'