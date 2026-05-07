```python
"""
Transaction Categorization Engine

A self-contained Python script that classifies financial transactions into spending categories
using configurable keyword matching rules. Categories and their associated keywords are stored
in a JSON configuration file for easy modification without code changes.

Features:
- Keyword-based transaction categorization
- Configurable JSON rules file
- Case-insensitive matching
- Priority-based category assignment
- Error handling for missing files and malformed data
- Sample transaction processing with results output

Usage: python script.py
"""

import json
import re
import os
from typing import Dict, List, Optional, Tuple


class TransactionCategorizer:
    """Categorizes transactions based on configurable keyword matching rules."""
    
    def __init__(self, config_file: str = "categorization_rules.json"):
        """
        Initialize the categorizer with rules from JSON config file.
        
        Args:
            config_file: Path to JSON file containing categorization rules
        """
        self.config_file = config_file
        self.rules = {}
        self.default_category = "Other"
        self.load_rules()
    
    def create_default_config(self) -> None:
        """Create a default configuration file with sample categorization rules."""
        default_rules = {
            "categories": {
                "Groceries": {
                    "keywords": ["grocery", "supermarket", "walmart", "kroger", "safeway", 
                               "whole foods", "trader joe", "costco", "target", "food mart",
                               "market", "deli", "bakery"],
                    "priority": 1
                },
                "Restaurants": {
                    "keywords": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", 
                               "burger", "pizza", "subway", "chipotle", "taco bell",
                               "dining", "bistro", "grill", "bar & grill"],
                    "priority": 2
                },
                "Utilities": {
                    "keywords": ["electric", "gas company", "water", "internet", "phone",
                               "cable", "utility", "power", "energy", "telecom", "verizon",
                               "att", "comcast", "spectrum"],
                    "priority": 1
                },
                "Transportation": {
                    "keywords": ["gas station", "shell", "exxon", "chevron", "bp", "uber",
                               "lyft", "taxi", "metro", "transit", "parking", "toll",
                               "auto repair", "mechanic"],
                    "priority": 1
                },
                "Entertainment": {
                    "keywords": ["movie", "cinema", "theater", "netflix", "spotify", "gaming",
                               "steam", "entertainment", "concert", "ticket", "amusement",
                               "recreation", "gym", "fitness"],
                    "priority": 3
                },
                "Shopping": {
                    "keywords": ["amazon", "ebay", "mall", "department store", "clothing",
                               "electronics", "best buy", "home depot", "lowes", "ikea",
                               "retail", "store", "shop"],
                    "priority": 4
                },
                "Healthcare": {
                    "keywords": ["hospital", "clinic", "doctor", "pharmacy", "medical",
                               "dentist", "veterinarian", "health", "cvs", "walgreens",
                               "urgent care"],
                    "priority": 1
                },
                "Banking": {
                    "keywords": ["bank", "atm", "fee", "transfer", "interest", "loan",
                               "mortgage", "credit card", "payment", "finance charge"],
                    "priority": 1
                }
            },
            "settings": {
                "default_category": "Other",
                "case_sensitive": False,
                "partial_match": True
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_rules, f, indent=2)
            print(f"Created default configuration file: {self.config_file}")
        except IOError as e:
            print(f"Error creating config file: {e}")
            raise
    
    def load_rules(self) -> None:
        """Load categorization rules from JSON config file."""
        if not os.path.exists(self.config_file):
            print(f"Config file {self.config_file} not found. Creating default configuration...")
            self.create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.rules = config.get("categories", {})
                settings = config.get("settings", {})
                self.default_category = settings.get("default_category", "Other")
                self.case_sensitive = settings.get("case_sensitive", False)
                self.partial_match = settings.get("partial_match", True)
                
            print(f"Loaded {len(self.rules)} categories from {self.config_file}")
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}")
            print("Using empty rules set.")
            self.rules = {}
    
    def categorize_transaction(self, description: str, amount: float = None) -> Tuple[str, int]:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description/merchant name
            amount: Transaction amount (optional, for future use)
            
        Returns:
            Tuple of (category_name, confidence_score)
        """
        if not description:
            return self.default_category, 0
        
        search_text = description if self.case_sensitive else description.lower()
        matches = []
        
        for category, rule_data in self.rules.items():
            keywords = rule_data.get("keywords", [])
            priority = rule_data.get("priority", 5)
            
            for keyword in keywords:
                search_keyword = keyword if self.case_sensitive else keyword.lower()
                
                if self.partial_match:
                    if search_keyword in search_text:
                        confidence = len(search_keyword) * (6 - priority)  # Higher priority = lower number = higher confidence
                        matches.append((category, confidence, priority))
                else:
                    if re.search(r'\b' + re.escape(search_keyword) + r'\b', search_text):
                        confidence = len(search_keyword) * (6 - priority)
                        matches.append((category, confidence, priority))
        
        if not matches:
            return self.default_category, 0
        
        # Sort by priority (lower number = higher priority), then by confidence
        matches.sort(key=lambda x: (x[2], -x[1]))
        return matches[0][0], matches[0][1]
    
    def batch_categorize(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize a batch of transactions.
        
        Args:
            transactions: List of transaction dictionaries with 'description' and optionally 'amount'
            
        Returns:
            List of transaction dictionaries with added 'category' and 'confidence' fields
        """
        results = []
        
        for transaction in transactions:
            try:
                description = transaction.get('description', '')
                amount = transaction.get('amount', None)
                
                category, confidence = self.categorize_transaction(description, amount)
                
                result = transaction.copy()
                result['category'] = category
                result['confidence'] = confidence
                results.append(result)
                
            except Exception as e:
                print(f"Error processing transaction {transaction}: {e}")
                result = transaction.copy()
                result['category'] = self.default_category
                result['confidence'] = 0
                results.append(result)
        
        return results
    
    def print_category_summary(self, categorized_transactions: List[Dict]) -> None:
        """Print a summary of categorized transactions."""
        category_counts = {}
        category_totals = {}
        
        for transaction in categorized_transactions:
            category = transaction.get('category', self.default_category)
            amount = abs(transaction.get('amount', 0))