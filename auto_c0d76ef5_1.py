```python
#!/usr/bin/env python3
"""
Expense Categorization Configuration System

This module provides a flexible configuration system for categorizing financial transactions
using JSON-defined rules with regex patterns. It allows users to define custom categorization
rules for different expense categories (groceries, dining, utilities, etc.) with fallback
logic for unmatched transactions.

Features:
- JSON-based configuration for easy customization
- Regex pattern matching for transaction descriptions
- Priority-based rule matching
- Fallback categorization for unmatched transactions
- Extensible category system

Usage:
    python script.py

The script will create a sample configuration file if none exists, then demonstrate
the categorization system with sample transactions.
"""

import json
import re
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CategoryRule:
    """Represents a single categorization rule."""
    name: str
    patterns: List[str]
    priority: int = 0
    compiled_patterns: Optional[List[re.Pattern]] = None
    
    def __post_init__(self):
        """Compile regex patterns after initialization."""
        if self.compiled_patterns is None:
            self.compiled_patterns = []
            for pattern in self.patterns:
                try:
                    self.compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    print(f"Warning: Invalid regex pattern '{pattern}' for category '{self.name}': {e}")


class ExpenseCategorizerConfig:
    """Configuration system for expense categorization rules."""
    
    def __init__(self, config_path: str = "expense_categories.json"):
        self.config_path = config_path
        self.rules: List[CategoryRule] = []
        self.fallback_category = "Other"
        self.case_sensitive = False
        
    def create_default_config(self) -> Dict[str, Any]:
        """Create a default configuration with common expense categories."""
        return {
            "fallback_category": "Other",
            "case_sensitive": False,
            "categories": {
                "Groceries": {
                    "patterns": [
                        r"\b(grocery|supermarket|market|food|walmart|target|costco|kroger|safeway)\b",
                        r"\b(whole foods|trader joe|publix|wegmans)\b"
                    ],
                    "priority": 10
                },
                "Dining": {
                    "patterns": [
                        r"\b(restaurant|cafe|coffee|pizza|burger|mcdonald|starbucks|subway)\b",
                        r"\b(dining|takeout|delivery|uber eats|doordash|grubhub)\b"
                    ],
                    "priority": 10
                },
                "Utilities": {
                    "patterns": [
                        r"\b(electric|electricity|gas|water|sewer|trash|internet|cable|phone)\b",
                        r"\b(utility|utilities|power|energy|telecom|broadband)\b"
                    ],
                    "priority": 15
                },
                "Transportation": {
                    "patterns": [
                        r"\b(gas station|fuel|gasoline|uber|lyft|taxi|metro|transit)\b",
                        r"\b(parking|toll|car wash|auto|vehicle|dmv)\b"
                    ],
                    "priority": 10
                },
                "Entertainment": {
                    "patterns": [
                        r"\b(movie|cinema|theater|netflix|spotify|gaming|steam)\b",
                        r"\b(entertainment|music|streaming|subscription)\b"
                    ],
                    "priority": 5
                },
                "Healthcare": {
                    "patterns": [
                        r"\b(pharmacy|hospital|medical|doctor|dentist|clinic)\b",
                        r"\b(health|medicine|prescription|cvs|walgreens)\b"
                    ],
                    "priority": 15
                },
                "Shopping": {
                    "patterns": [
                        r"\b(amazon|ebay|mall|store|retail|shopping)\b",
                        r"\b(clothing|electronics|home depot|lowes)\b"
                    ],
                    "priority": 5
                },
                "Bills": {
                    "patterns": [
                        r"\b(mortgage|rent|loan|credit card|insurance)\b",
                        r"\b(payment|bill|invoice|subscription)\b"
                    ],
                    "priority": 20
                }
            }
        }
    
    def load_config(self) -> bool:
        """Load configuration from JSON file."""
        try:
            if not os.path.exists(self.config_path):
                print(f"Config file '{self.config_path}' not found. Creating default config...")
                self.save_default_config()
                return self.load_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.fallback_category = config_data.get("fallback_category", "Other")
            self.case_sensitive = config_data.get("case_sensitive", False)
            
            self.rules = []
            categories = config_data.get("categories", {})
            
            for category_name, category_config in categories.items():
                patterns = category_config.get("patterns", [])
                priority = category_config.get("priority", 0)
                
                rule = CategoryRule(
                    name=category_name,
                    patterns=patterns,
                    priority=priority
                )
                self.rules.append(rule)
            
            # Sort rules by priority (higher priority first)
            self.rules.sort(key=lambda x: x.priority, reverse=True)
            
            print(f"Loaded {len(self.rules)} categorization rules from '{self.config_path}'")
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON config file: {e}")
            return False
        except Exception as e:
            print(f"Error loading config file: {e}")
            return False
    
    def save_default_config(self) -> bool:
        """Save default configuration to JSON file."""
        try:
            config_data = self.create_default_config()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"Created default config file: {self.config_path}")
            return True
        except Exception as e:
            print(f"Error creating default config file: {e}")
            return False
    
    def categorize_transaction(self, description: str, amount: float = None) -> str:
        """Categorize a transaction based on its description."""
        try:
            if not description:
                return self.fallback_category
            
            # Try to match against each rule in priority order
            for rule in self.rules:
                if rule.compiled_patterns:
                    for pattern in rule.compiled_patterns:
                        if pattern.search(description):
                            return rule.name
            
            # No match found, return fallback category
            return self.fallback_category
            
        except Exception as e:
            print(f"Error categorizing transaction '{description}': {e}")
            return self.fallback_category
    
    def add_category_rule(self, name: str, patterns: List[str], priority: int = 0) -> bool:
        """Add a new category rule programmatically."""
        try:
            rule = CategoryRule(name=name, patterns=patterns, priority=priority)
            self.rules.append(rule)
            # Re-sort rules by priority
            self.rules.sort(key=lambda x: x.priority, reverse=True)
            return True
        except Exception as e:
            print(f"Error adding category rule '{name}': {e}")
            return False
    
    def get_category_stats(self, transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get statistics about categorization results."""
        try:
            stats = {}
            total_amount = 0
            total_