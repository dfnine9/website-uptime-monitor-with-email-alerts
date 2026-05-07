```python
"""
Transaction Categorization Engine

A self-contained Python script that classifies financial transactions into spending categories
using configurable keyword matching rules. Supports multiple categories including groceries,
utilities, entertainment, etc. with customizable keyword dictionaries for flexible classification.

Features:
- Configurable keyword dictionaries for each spending category
- Case-insensitive keyword matching
- Priority-based categorization (first match wins)
- Comprehensive error handling
- Sample transaction processing demonstration

Usage: python script.py
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Transaction:
    """Represents a financial transaction with description and amount."""
    id: str
    description: str
    amount: float
    category: Optional[str] = None


class TransactionCategorizer:
    """
    A transaction categorization engine using keyword matching rules.
    
    Classifies transactions into spending categories based on configurable
    keyword dictionaries with priority-based matching.
    """
    
    def __init__(self):
        """Initialize the categorizer with default keyword dictionaries."""
        self.category_keywords = {
            "groceries": [
                "supermarket", "grocery", "food", "market", "walmart", "target", 
                "kroger", "safeway", "whole foods", "trader joe", "costco", "sam's club",
                "fresh market", "food lion", "publix", "aldi", "wegmans"
            ],
            "utilities": [
                "electric", "electricity", "gas", "water", "sewer", "trash", "garbage",
                "internet", "cable", "phone", "cell", "mobile", "utility", "power",
                "energy", "heating", "cooling", "waste management"
            ],
            "entertainment": [
                "movie", "cinema", "theater", "netflix", "spotify", "hulu", "disney",
                "amazon prime", "gaming", "xbox", "playstation", "steam", "concert",
                "show", "event", "ticket", "entertainment", "streaming", "music"
            ],
            "transportation": [
                "gas station", "fuel", "gasoline", "uber", "lyft", "taxi", "bus",
                "train", "subway", "metro", "parking", "toll", "car wash", "auto",
                "shell", "exxon", "bp", "chevron", "maintenance", "repair"
            ],
            "dining": [
                "restaurant", "cafe", "coffee", "starbucks", "mcdonald", "burger",
                "pizza", "bar", "pub", "grill", "diner", "fast food", "takeout",
                "delivery", "doordash", "ubereats", "grubhub", "dining", "lunch", "dinner"
            ],
            "shopping": [
                "amazon", "ebay", "store", "retail", "shop", "mall", "outlet",
                "clothing", "shoes", "electronics", "home depot", "lowes", "best buy",
                "macy", "nordstrom", "department", "online", "purchase"
            ],
            "healthcare": [
                "doctor", "hospital", "medical", "pharmacy", "dentist", "clinic",
                "health", "medicine", "prescription", "cvs", "walgreens", "urgent care",
                "specialist", "therapy", "treatment", "checkup"
            ],
            "insurance": [
                "insurance", "premium", "policy", "coverage", "auto insurance",
                "health insurance", "life insurance", "home insurance", "geico",
                "state farm", "allstate", "progressive"
            ],
            "banking": [
                "fee", "charge", "overdraft", "atm", "transfer", "interest",
                "maintenance", "service charge", "penalty", "bank"
            ],
            "education": [
                "tuition", "school", "university", "college", "education", "books",
                "supplies", "learning", "course", "training", "certification"
            ]
        }
        
        # Category priority order (first match wins)
        self.category_priority = [
            "banking", "insurance", "utilities", "healthcare", "education",
            "groceries", "dining", "transportation", "entertainment", "shopping"
        ]
    
    def add_keywords(self, category: str, keywords: List[str]) -> None:
        """
        Add keywords to a category.
        
        Args:
            category: The spending category name
            keywords: List of keywords to add
        """
        try:
            if category not in self.category_keywords:
                self.category_keywords[category] = []
            
            self.category_keywords[category].extend(keywords)
            print(f"Added {len(keywords)} keywords to category '{category}'")
            
        except Exception as e:
            print(f"Error adding keywords to category '{category}': {e}")
    
    def remove_keywords(self, category: str, keywords: List[str]) -> None:
        """
        Remove keywords from a category.
        
        Args:
            category: The spending category name
            keywords: List of keywords to remove
        """
        try:
            if category in self.category_keywords:
                for keyword in keywords:
                    if keyword in self.category_keywords[category]:
                        self.category_keywords[category].remove(keyword)
                
                print(f"Removed {len(keywords)} keywords from category '{category}'")
            else:
                print(f"Category '{category}' not found")
                
        except Exception as e:
            print(f"Error removing keywords from category '{category}': {e}")
    
    def set_category_keywords(self, category: str, keywords: List[str]) -> None:
        """
        Set the complete keyword list for a category.
        
        Args:
            category: The spending category name
            keywords: Complete list of keywords for the category
        """
        try:
            self.category_keywords[category] = keywords.copy()
            print(f"Set {len(keywords)} keywords for category '{category}'")
            
        except Exception as e:
            print(f"Error setting keywords for category '{category}': {e}")
    
    def categorize_transaction(self, transaction: Transaction) -> str:
        """
        Categorize a single transaction based on keyword matching.
        
        Args:
            transaction: Transaction object to categorize
            
        Returns:
            Category name or 'uncategorized' if no match found
        """
        try:
            description_lower = transaction.description.lower()
            
            # Check categories in priority order
            for category in self.category_priority:
                if category in self.category_keywords:
                    keywords = self.category_keywords[category]
                    
                    for keyword in keywords:
                        keyword_lower = keyword.lower()
                        
                        # Use word boundary matching for better accuracy
                        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                        if re.search(pattern, description_lower):
                            return category
            
            # Check remaining categories not in priority list
            for category, keywords in self.category_keywords.items():
                if category not in self.category_priority:
                    for keyword in keywords:
                        keyword_lower = keyword.lower()
                        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                        if re.search(pattern, description_lower):
                            return category
            
            return "uncategorized"
            
        except Exception as e:
            print(f"Error categorizing transaction {transaction.id}: {e}")
            return "uncategorized"
    
    def categorize_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """
        Categorize a list of transactions.
        
        Args:
            transactions: List of Transaction objects to categorize
            
        Returns:
            List of Transaction objects with categories assigned
        """
        try:
            categorized_transactions = []
            
            for transaction in transactions:
                category = self.categorize_transaction(transaction)
                transaction.category = category
                categorized_transactions.append(transaction)
            
            return categorized_transactions
            
        except Exception as e:
            print(f"Error categorizing transactions: {e}")
            return transactions
    
    def get_category_summary(self, transactions: List[Transaction]) -> Dict[str, Dict[str, float]]:
        """