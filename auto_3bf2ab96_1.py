```python
"""
Transaction Categorization Module

This module provides functionality to classify financial transactions into predefined
categories using keyword matching and regex patterns. It supports configurable rules
for categorizing expenses such as groceries, dining, utilities, transportation, 
entertainment, and more.

Features:
- Keyword-based transaction categorization
- Regex pattern matching for flexible classification
- Configurable category rules via JSON
- Case-insensitive matching
- Priority-based rule application
- Detailed categorization reporting

Usage:
    python script.py

The script will process sample transactions and demonstrate the categorization
functionality with built-in rules and sample data.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """Represents a financial transaction."""
    id: str
    description: str
    amount: float
    date: str
    merchant: str = ""
    category: str = "uncategorized"


class TransactionCategorizer:
    """
    Categorizes transactions using keyword matching and regex patterns.
    
    Supports configurable rules with priority-based matching for accurate
    expense classification across multiple categories.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the categorizer with default or custom rules.
        
        Args:
            config_path: Path to JSON configuration file (optional)
        """
        self.categories = {}
        self.rules = {}
        
        if config_path:
            try:
                self.load_config(config_path)
            except Exception as e:
                print(f"Error loading config: {e}")
                print("Using default rules instead.")
                self._load_default_rules()
        else:
            self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default categorization rules."""
        self.rules = {
            "groceries": {
                "keywords": [
                    "grocery", "supermarket", "walmart", "target", "costco", "safeway",
                    "kroger", "whole foods", "trader joe", "food mart", "market",
                    "fresh", "organic", "produce"
                ],
                "regex_patterns": [
                    r".*food.*store.*",
                    r".*market.*",
                    r".*grocery.*"
                ],
                "priority": 1
            },
            "dining": {
                "keywords": [
                    "restaurant", "cafe", "coffee", "pizza", "burger", "deli",
                    "bistro", "grill", "bar", "pub", "takeout", "delivery",
                    "starbucks", "mcdonald", "subway", "chipotle", "domino"
                ],
                "regex_patterns": [
                    r".*restaurant.*",
                    r".*cafe.*",
                    r".*pizza.*",
                    r".*coffee.*"
                ],
                "priority": 2
            },
            "utilities": {
                "keywords": [
                    "electric", "gas", "water", "sewer", "internet", "phone",
                    "cable", "utility", "power", "energy", "telecom", "verizon",
                    "att", "comcast", "pge", "edison"
                ],
                "regex_patterns": [
                    r".*electric.*company.*",
                    r".*gas.*company.*",
                    r".*utility.*",
                    r".*power.*"
                ],
                "priority": 1
            },
            "transportation": {
                "keywords": [
                    "gas station", "fuel", "parking", "uber", "lyft", "taxi",
                    "metro", "bus", "train", "airline", "flight", "car wash",
                    "auto", "mechanic", "shell", "chevron", "bp", "exxon"
                ],
                "regex_patterns": [
                    r".*gas.*station.*",
                    r".*parking.*",
                    r".*auto.*",
                    r".*fuel.*"
                ],
                "priority": 2
            },
            "entertainment": {
                "keywords": [
                    "movie", "theater", "cinema", "netflix", "spotify", "gym",
                    "fitness", "sports", "game", "concert", "show", "museum",
                    "park", "recreation", "streaming", "subscription"
                ],
                "regex_patterns": [
                    r".*entertainment.*",
                    r".*streaming.*",
                    r".*subscription.*"
                ],
                "priority": 3
            },
            "shopping": {
                "keywords": [
                    "amazon", "ebay", "store", "mall", "retail", "clothing",
                    "shoes", "electronics", "best buy", "home depot", "lowes",
                    "online", "purchase"
                ],
                "regex_patterns": [
                    r".*store.*",
                    r".*retail.*",
                    r".*shop.*"
                ],
                "priority": 4
            },
            "healthcare": {
                "keywords": [
                    "doctor", "dentist", "pharmacy", "hospital", "clinic",
                    "medical", "health", "cvs", "walgreens", "prescription",
                    "dental", "vision"
                ],
                "regex_patterns": [
                    r".*medical.*",
                    r".*pharmacy.*",
                    r".*dental.*"
                ],
                "priority": 1
            },
            "financial": {
                "keywords": [
                    "bank", "atm", "fee", "interest", "loan", "credit",
                    "insurance", "investment", "transfer", "payment"
                ],
                "regex_patterns": [
                    r".*bank.*fee.*",
                    r".*atm.*",
                    r".*insurance.*"
                ],
                "priority": 5
            }
        }
    
    def load_config(self, config_path: str):
        """
        Load categorization rules from JSON configuration file.
        
        Args:
            config_path: Path to JSON configuration file
        """
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            self.rules = config_data.get('rules', {})
    
    def save_config(self, config_path: str):
        """
        Save current rules to JSON configuration file.
        
        Args:
            config_path: Path where to save configuration
        """
        config_data = {'rules': self.rules}
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def categorize_transaction(self, transaction: Transaction) -> str:
        """
        Categorize a single transaction based on description and merchant.
        
        Args:
            transaction: Transaction object to categorize
            
        Returns:
            Category name as string
        """
        text_to_analyze = f"{transaction.description} {transaction.merchant}".lower()
        
        # Sort categories by priority (lower number = higher priority)
        sorted_categories = sorted(
            self.rules.items(),
            key=lambda x: x[1].get('priority', 999)
        )
        
        for category, rules in sorted_categories:
            try:
                # Check keywords
                for keyword in rules.get('keywords', []):
                    if keyword.lower() in text_to_analyze:
                        return category
                
                # Check regex patterns
                for pattern in rules.get('regex_patterns', []):
                    if re.search(pattern, text_to_analyze, re.IGNORECASE):
                        return category
                        
            except Exception as e:
                print(f"Error processing category {category}: {e}")
                continue
        
        return "uncategorized"
    
    def categorize_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """
        Categorize a list of transactions.
        
        Args:
            transactions: List of Transaction objects
            
        Returns:
            List of Transaction objects with updated categories
        """
        categorized = []
        
        for transaction in transactions:
            try:
                transaction.category = self.categorize_transaction(transaction)
                categorized.