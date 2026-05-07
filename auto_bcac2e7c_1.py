```python
"""
Expense Categorization Configuration Manager

This module provides a self-contained system for managing expense categorization rules
through JSON configuration files. It allows users to define keyword/pattern mappings
to spending categories and automatically categorize expenses based on these rules.

The script creates a default configuration file with common categorization rules
and provides functionality to load, validate, and apply these rules to expense data.

Usage: python script.py
"""

import json
import re
import os
import sys
from typing import Dict, List, Any, Optional


class ExpenseCategorizer:
    """Manages expense categorization rules and applies them to transaction data."""
    
    def __init__(self, config_file: str = "categorization_config.json"):
        self.config_file = config_file
        self.rules = {}
        self.load_config()
    
    def create_default_config(self) -> Dict[str, Any]:
        """Create default categorization rules configuration."""
        return {
            "version": "1.0",
            "categories": {
                "Food & Dining": {
                    "keywords": [
                        "restaurant", "cafe", "pizza", "burger", "starbucks",
                        "mcdonald", "subway", "domino", "uber eats", "doordash",
                        "grubhub", "food", "dining", "kitchen", "grocery"
                    ],
                    "patterns": [
                        r".*restaurant.*",
                        r".*cafe.*",
                        r".*food.*",
                        r".*grocery.*"
                    ]
                },
                "Transportation": {
                    "keywords": [
                        "uber", "lyft", "taxi", "gas", "fuel", "parking",
                        "metro", "subway", "bus", "train", "airline",
                        "flight", "car wash", "toll"
                    ],
                    "patterns": [
                        r".*gas\s+station.*",
                        r".*parking.*",
                        r".*airlines?.*",
                        r".*transport.*"
                    ]
                },
                "Shopping": {
                    "keywords": [
                        "amazon", "walmart", "target", "costco", "ebay",
                        "mall", "store", "shop", "retail", "clothing",
                        "electronics", "furniture"
                    ],
                    "patterns": [
                        r".*amazon.*",
                        r".*walmart.*",
                        r".*target.*",
                        r".*shop.*"
                    ]
                },
                "Entertainment": {
                    "keywords": [
                        "netflix", "spotify", "movie", "theater", "cinema",
                        "concert", "game", "entertainment", "bar", "club",
                        "streaming", "subscription"
                    ],
                    "patterns": [
                        r".*netflix.*",
                        r".*spotify.*",
                        r".*movie.*",
                        r".*entertainment.*"
                    ]
                },
                "Utilities": {
                    "keywords": [
                        "electric", "electricity", "water", "gas bill",
                        "internet", "phone", "cable", "utility", "power",
                        "heating", "cooling"
                    ],
                    "patterns": [
                        r".*electric.*company.*",
                        r".*water.*department.*",
                        r".*utility.*"
                    ]
                },
                "Healthcare": {
                    "keywords": [
                        "doctor", "hospital", "pharmacy", "medical",
                        "dental", "clinic", "health", "medicine",
                        "prescription", "cvs", "walgreens"
                    ],
                    "patterns": [
                        r".*medical.*center.*",
                        r".*pharmacy.*",
                        r".*dental.*"
                    ]
                },
                "Banking & Finance": {
                    "keywords": [
                        "bank", "atm", "fee", "interest", "loan",
                        "credit card", "investment", "transfer",
                        "withdrawal", "deposit"
                    ],
                    "patterns": [
                        r".*bank.*fee.*",
                        r".*atm.*",
                        r".*interest.*"
                    ]
                },
                "Other": {
                    "keywords": ["misc", "other", "unknown"],
                    "patterns": [r".*"]
                }
            },
            "settings": {
                "case_sensitive": False,
                "use_partial_matching": True,
                "default_category": "Other"
            }
        }
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
            raise
    
    def load_config(self) -> None:
        """Load configuration from JSON file or create default if not exists."""
        try:
            if not os.path.exists(self.config_file):
                print(f"Configuration file {self.config_file} not found. Creating default...")
                default_config = self.create_default_config()
                self.save_config(default_config)
                self.rules = default_config
            else:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.rules = json.load(f)
                print(f"Configuration loaded from {self.config_file}")
                self.validate_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON configuration: {e}")
            print("Creating backup and using default configuration...")
            self.create_backup_and_reset()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise
    
    def validate_config(self) -> None:
        """Validate the loaded configuration structure."""
        required_keys = ['categories', 'settings']
        
        for key in required_keys:
            if key not in self.rules:
                raise ValueError(f"Missing required configuration key: {key}")
        
        if not isinstance(self.rules['categories'], dict):
            raise ValueError("Categories must be a dictionary")
        
        for category, rules in self.rules['categories'].items():
            if not isinstance(rules, dict):
                raise ValueError(f"Category '{category}' rules must be a dictionary")
            
            if 'keywords' not in rules:
                rules['keywords'] = []
            if 'patterns' not in rules:
                rules['patterns'] = []
        
        print("Configuration validation passed")
    
    def create_backup_and_reset(self) -> None:
        """Create backup of corrupted config and reset to default."""
        try:
            backup_file = f"{self.config_file}.backup"
            if os.path.exists(self.config_file):
                os.rename(self.config_file, backup_file)
                print(f"Corrupted config backed up to {backup_file}")
            
            default_config = self.create_default_config()
            self.save_config(default_config)
            self.rules = default_config
        except Exception as e:
            print(f"Error creating backup: {e}")
            raise
    
    def categorize_expense(self, description: str, amount: Optional[float] = None) -> str:
        """Categorize an expense based on its description."""
        try:
            if not description:
                return self.rules['settings'].get('default_category', 'Other')
            
            case_sensitive = self.rules['settings'].get('case_sensitive', False)
            description_to_match = description if case_sensitive else description.lower()
            
            # Check each category's rules
            for category, rules in self.rules['categories'].items():
                # Check keywords
                keywords = rules.get('keywords', [])
                for keyword in keywords:
                    keyword_to_match = keyword if case_sensitive else keyword.lower()
                    if keyword_to_match in description_to_match:
                        return category
                
                # Check regex patterns