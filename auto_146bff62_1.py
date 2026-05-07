```python
"""
Expense Categorization System with Custom Configuration and Fuzzy Matching

This module provides a self-contained expense categorization system that allows users to:
1. Define custom categorization rules through a JSON configuration file
2. Add new expense categories dynamically
3. Train a classifier on specific merchant patterns using fuzzy string matching
4. Categorize transactions based on merchant names and amounts

The system uses fuzzy string matching to handle merchant name variations and
provides a simple interface for managing expense categories and rules.
"""

import json
import re
import os
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher


class FuzzyMatcher:
    """Handles fuzzy string matching for merchant names."""
    
    @staticmethod
    def similarity(a: str, b: str) -> float:
        """Calculate similarity ratio between two strings (0.0 to 1.0)."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    @staticmethod
    def fuzzy_match(target: str, candidates: List[str], threshold: float = 0.7) -> Optional[str]:
        """Find the best matching candidate above threshold."""
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = FuzzyMatcher.similarity(target, candidate)
            if score > best_score and score >= threshold:
                best_match = candidate
                best_score = score
        
        return best_match


class ExpenseCategorizationSystem:
    """Main expense categorization system with configurable rules."""
    
    def __init__(self, config_file: str = "expense_config.json"):
        self.config_file = config_file
        self.categories = {}
        self.merchant_patterns = {}
        self.amount_rules = {}
        self.fuzzy_threshold = 0.7
        self.load_configuration()
    
    def load_configuration(self) -> None:
        """Load configuration from JSON file or create default if not exists."""
        default_config = {
            "categories": {
                "Food & Dining": {
                    "description": "Restaurants, cafes, food delivery",
                    "merchants": ["mcdonalds", "starbucks", "subway", "pizza", "restaurant", "cafe", "doordash", "ubereats"],
                    "keywords": ["food", "dining", "restaurant", "cafe", "delivery"]
                },
                "Transportation": {
                    "description": "Gas, uber, public transit",
                    "merchants": ["shell", "exxon", "uber", "lyft", "metro", "transit", "parking"],
                    "keywords": ["gas", "fuel", "uber", "taxi", "transit", "parking"]
                },
                "Shopping": {
                    "description": "Retail purchases, online shopping",
                    "merchants": ["amazon", "walmart", "target", "costco", "best buy", "apple store"],
                    "keywords": ["store", "shop", "retail", "purchase"]
                },
                "Entertainment": {
                    "description": "Movies, streaming, games",
                    "merchants": ["netflix", "spotify", "steam", "cinema", "theater", "amc"],
                    "keywords": ["entertainment", "movie", "streaming", "game", "music"]
                },
                "Utilities": {
                    "description": "Electric, gas, water, internet",
                    "merchants": ["electric", "gas company", "water dept", "internet", "comcast", "verizon"],
                    "keywords": ["electric", "gas", "water", "internet", "utility", "bill"]
                },
                "Healthcare": {
                    "description": "Medical expenses, pharmacy",
                    "merchants": ["cvs", "walgreens", "pharmacy", "hospital", "clinic", "dental"],
                    "keywords": ["medical", "pharmacy", "health", "dental", "doctor"]
                }
            },
            "amount_rules": {
                "small_purchase": {"max": 10.0, "category": "Miscellaneous"},
                "large_purchase": {"min": 500.0, "requires_manual_review": True}
            },
            "fuzzy_threshold": 0.7
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = default_config
                self.save_configuration(config)
            
            self.categories = config.get("categories", {})
            self.amount_rules = config.get("amount_rules", {})
            self.fuzzy_threshold = config.get("fuzzy_threshold", 0.7)
            
            # Build merchant patterns for quick lookup
            self._build_merchant_patterns()
            
            print(f"Configuration loaded successfully. Categories: {len(self.categories)}")
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using default configuration")
            self.categories = default_config["categories"]
            self.amount_rules = default_config["amount_rules"]
            self._build_merchant_patterns()
    
    def save_configuration(self, config: Optional[Dict] = None) -> None:
        """Save current configuration to JSON file."""
        if config is None:
            config = {
                "categories": self.categories,
                "amount_rules": self.amount_rules,
                "fuzzy_threshold": self.fuzzy_threshold
            }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def _build_merchant_patterns(self) -> None:
        """Build merchant patterns dictionary for faster lookup."""
        self.merchant_patterns = {}
        for category, data in self.categories.items():
            merchants = data.get("merchants", [])
            for merchant in merchants:
                self.merchant_patterns[merchant.lower()] = category
    
    def add_category(self, name: str, description: str, merchants: List[str], keywords: List[str]) -> None:
        """Add a new expense category."""
        try:
            self.categories[name] = {
                "description": description,
                "merchants": [m.lower() for m in merchants],
                "keywords": [k.lower() for k in keywords]
            }
            self._build_merchant_patterns()
            self.save_configuration()
            print(f"Added new category: {name}")
        except Exception as e:
            print(f"Error adding category: {e}")
    
    def train_on_merchant(self, merchant_name: str, category: str) -> None:
        """Train the classifier by adding a merchant to a category."""
        try:
            if category not in self.categories:
                print(f"Category '{category}' does not exist. Available categories:")
                for cat in self.categories.keys():
                    print(f"  - {cat}")
                return
            
            if "merchants" not in self.categories[category]:
                self.categories[category]["merchants"] = []
            
            merchant_lower = merchant_name.lower()
            if merchant_lower not in self.categories[category]["merchants"]:
                self.categories[category]["merchants"].append(merchant_lower)
                self._build_merchant_patterns()
                self.save_configuration()
                print(f"Trained: '{merchant_name}' -> '{category}'")
            else:
                print(f"Merchant '{merchant_name}' already exists in category '{category}'")
                
        except Exception as e:
            print(f"Error training on merchant: {e}")
    
    def categorize_expense(self, merchant: str, amount: float, description: str = "") -> Dict:
        """Categorize an expense based on merchant, amount, and description."""
        try:
            result = {
                "merchant": merchant,
                "amount": amount,
                "description": description,
                "category": "Uncategorized",
                "confidence": 0.0,
                "method": "none",
                "requires_review": False
            }
            
            # Check amount rules first
            for rule_name,