```python
#!/usr/bin/env python3
"""
Transaction Categorization System

A rule-based transaction categorization system that uses JSON configuration files
to classify financial transactions into categories like groceries, restaurants, 
utilities, etc. The system supports:

- Keyword matching for merchant names
- Regex pattern matching for complex merchant identification
- Priority-based category mapping
- Fallback logic for uncategorized transactions
- Configurable rules via JSON files

Usage: python script.py

The script will create sample configuration files and demonstrate categorization
of sample transactions.
"""

import json
import re
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a financial transaction"""
    merchant: str
    amount: float
    description: str = ""


class TransactionCategorizer:
    """
    Rule-based transaction categorization system using JSON configuration
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the categorizer with configuration directory
        
        Args:
            config_dir: Directory containing JSON configuration files
        """
        self.config_dir = config_dir
        self.categories = {}
        self.keywords = {}
        self.patterns = {}
        self.fallback_rules = {}
        self.load_configurations()
    
    def load_configurations(self) -> None:
        """Load all JSON configuration files"""
        try:
            # Ensure config directory exists
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Create default configurations if they don't exist
            self._create_default_configs()
            
            # Load category definitions
            self._load_categories()
            
            # Load keyword mappings
            self._load_keywords()
            
            # Load regex patterns
            self._load_patterns()
            
            # Load fallback rules
            self._load_fallback_rules()
            
            print(f"✓ Loaded configurations from {self.config_dir}/")
            
        except Exception as e:
            print(f"✗ Error loading configurations: {e}")
            raise
    
    def _create_default_configs(self) -> None:
        """Create default configuration files if they don't exist"""
        
        # Categories configuration
        categories_file = os.path.join(self.config_dir, "categories.json")
        if not os.path.exists(categories_file):
            categories = {
                "groceries": {
                    "name": "Groceries",
                    "priority": 1,
                    "description": "Food and household items"
                },
                "restaurants": {
                    "name": "Restaurants & Dining",
                    "priority": 2,
                    "description": "Restaurant meals and food delivery"
                },
                "utilities": {
                    "name": "Utilities",
                    "priority": 3,
                    "description": "Electric, gas, water, internet bills"
                },
                "transportation": {
                    "name": "Transportation",
                    "priority": 4,
                    "description": "Gas, public transit, rideshare"
                },
                "shopping": {
                    "name": "Shopping",
                    "priority": 5,
                    "description": "General retail purchases"
                },
                "entertainment": {
                    "name": "Entertainment",
                    "priority": 6,
                    "description": "Movies, streaming, games"
                },
                "healthcare": {
                    "name": "Healthcare",
                    "priority": 7,
                    "description": "Medical expenses and pharmacy"
                },
                "uncategorized": {
                    "name": "Uncategorized",
                    "priority": 999,
                    "description": "Transactions that don't fit other categories"
                }
            }
            with open(categories_file, 'w') as f:
                json.dump(categories, f, indent=2)
        
        # Keywords configuration
        keywords_file = os.path.join(self.config_dir, "keywords.json")
        if not os.path.exists(keywords_file):
            keywords = {
                "groceries": [
                    "walmart", "target", "kroger", "safeway", "whole foods",
                    "trader joe", "costco", "sam's club", "publix", "wegmans",
                    "food lion", "giant eagle", "harris teeter", "aldi"
                ],
                "restaurants": [
                    "mcdonald", "burger king", "subway", "starbucks", "taco bell",
                    "pizza hut", "domino", "kfc", "chipotle", "panera",
                    "olive garden", "applebee", "chili", "restaurant", "cafe",
                    "doordash", "uber eats", "grubhub", "postmates"
                ],
                "utilities": [
                    "electric", "gas company", "water", "internet", "cable",
                    "phone", "verizon", "at&t", "comcast", "spectrum",
                    "xfinity", "cox", "duke energy", "pge", "utility"
                ],
                "transportation": [
                    "shell", "exxon", "chevron", "bp", "mobil", "gas station",
                    "uber", "lyft", "taxi", "metro", "transit", "parking",
                    "toll", "dmv", "registration"
                ],
                "shopping": [
                    "amazon", "ebay", "best buy", "home depot", "lowes",
                    "macy", "nordstrom", "gap", "old navy", "tj maxx",
                    "marshall", "ross", "outlet"
                ],
                "entertainment": [
                    "netflix", "spotify", "apple music", "hulu", "disney",
                    "hbo", "cinema", "movie", "theater", "concert",
                    "ticket", "game", "steam", "playstation", "xbox"
                ],
                "healthcare": [
                    "pharmacy", "cvs", "walgreens", "rite aid", "hospital",
                    "clinic", "doctor", "medical", "dental", "vision",
                    "insurance", "copay"
                ]
            }
            with open(keywords_file, 'w') as f:
                json.dump(keywords, f, indent=2)
        
        # Patterns configuration
        patterns_file = os.path.join(self.config_dir, "patterns.json")
        if not os.path.exists(patterns_file):
            patterns = {
                "utilities": [
                    r".*ELECTRIC.*CO.*",
                    r".*GAS.*COMPANY.*",
                    r".*WATER.*DEPT.*",
                    r".*CABLE.*",
                    r".*INTERNET.*",
                    r".*PHONE.*BILL.*"
                ],
                "groceries": [
                    r".*GROCERY.*",
                    r".*SUPERMARKET.*",
                    r".*FOOD.*STORE.*",
                    r".*MARKET.*\d{4}.*"
                ],
                "restaurants": [
                    r".*RESTAURANT.*",
                    r".*CAFE.*",
                    r".*DINING.*",
                    r".*FOOD.*DELIVERY.*",
                    r".*FAST.*FOOD.*"
                ],
                "transportation": [
                    r".*GAS.*STATION.*",
                    r".*FUEL.*",
                    r".*PARKING.*",
                    r".*TOLL.*",
                    r".*UBER.*|.*LYFT.*"
                ],
                "healthcare": [
                    r".*PHARMACY.*",
                    r".*MEDICAL.*",
                    r".*HOSPITAL.*",
                    r".*CLINIC.*",
                    r".*DR\..*|.*DOCTOR.*"
                ]
            }
            with open(patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
        
        # Fallback rules configuration
        fallback_file = os.path.join(self.config_dir, "fallback_rules.json")
        if not os.path.exists(fallback_file):
            fallback_rules = {
                "amount_based