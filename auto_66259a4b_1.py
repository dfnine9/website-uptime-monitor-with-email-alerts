```python
"""
Financial Transaction Categorizer with Dynamic Configuration

This module provides a comprehensive system for categorizing financial transactions
using user-defined rules and keywords. It includes:
- Dynamic configuration loading from JSON files
- Flexible categorization rules with priority handling
- Robust error handling for edge cases
- Support for uncategorized transactions
- Transaction amount and description processing

The system allows users to define custom categories, keywords, and rules
without modifying the core logic, making it highly adaptable for different
financial categorization needs.
"""

import json
import re
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Transaction:
    """Represents a financial transaction with amount and description."""
    amount: float
    description: str
    date: Optional[str] = None
    account: Optional[str] = None

@dataclass
class CategoryRule:
    """Defines a categorization rule with keywords and conditions."""
    name: str
    keywords: List[str]
    priority: int = 0
    amount_range: Optional[Tuple[float, float]] = None
    regex_patterns: Optional[List[str]] = None
    case_sensitive: bool = False

class TransactionCategorizer:
    """Main categorizer class that processes transactions using dynamic rules."""
    
    def __init__(self, config_path: str = "categorization_config.json"):
        self.config_path = config_path
        self.rules: List[CategoryRule] = []
        self.default_category = "Uncategorized"
        self.load_configuration()
    
    def create_default_config(self) -> Dict[str, Any]:
        """Creates a default configuration structure."""
        return {
            "default_category": "Uncategorized",
            "case_sensitive_matching": False,
            "categories": {
                "Food & Dining": {
                    "priority": 10,
                    "keywords": [
                        "restaurant", "cafe", "pizza", "mcdonalds", "starbucks",
                        "grocery", "supermarket", "food", "dining", "lunch", "dinner"
                    ],
                    "regex_patterns": [
                        r".*restaurant.*",
                        r".*food.*court.*"
                    ]
                },
                "Transportation": {
                    "priority": 9,
                    "keywords": [
                        "uber", "lyft", "taxi", "gas station", "shell", "chevron",
                        "parking", "metro", "transit", "bus", "train"
                    ],
                    "amount_range": [5.0, 200.0]
                },
                "Shopping": {
                    "priority": 8,
                    "keywords": [
                        "amazon", "target", "walmart", "shopping", "store", "mall",
                        "clothing", "electronics", "department"
                    ]
                },
                "Bills & Utilities": {
                    "priority": 12,
                    "keywords": [
                        "electric", "water", "gas bill", "internet", "phone",
                        "cable", "insurance", "mortgage", "rent"
                    ],
                    "regex_patterns": [
                        r".*bill.*payment.*",
                        r".*utility.*"
                    ]
                },
                "Healthcare": {
                    "priority": 11,
                    "keywords": [
                        "hospital", "doctor", "pharmacy", "medical", "clinic",
                        "dentist", "prescription", "health"
                    ]
                },
                "Entertainment": {
                    "priority": 7,
                    "keywords": [
                        "netflix", "spotify", "movie", "theater", "game",
                        "entertainment", "concert", "show"
                    ]
                },
                "Income": {
                    "priority": 15,
                    "keywords": [
                        "salary", "payroll", "deposit", "income", "wage",
                        "bonus", "refund", "cashback"
                    ],
                    "amount_range": [0.0, float('inf')]
                }
            }
        }
    
    def load_configuration(self) -> None:
        """Loads categorization rules from configuration file."""
        try:
            if not os.path.exists(self.config_path):
                print(f"Configuration file not found. Creating default config at {self.config_path}")
                self.create_config_file()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.default_category = config.get("default_category", "Uncategorized")
            self.case_sensitive = config.get("case_sensitive_matching", False)
            
            # Convert configuration to CategoryRule objects
            self.rules = []
            categories = config.get("categories", {})
            
            for category_name, category_config in categories.items():
                try:
                    rule = CategoryRule(
                        name=category_name,
                        keywords=category_config.get("keywords", []),
                        priority=category_config.get("priority", 0),
                        case_sensitive=category_config.get("case_sensitive", self.case_sensitive),
                        regex_patterns=category_config.get("regex_patterns"),
                        amount_range=tuple(category_config["amount_range"]) if "amount_range" in category_config else None
                    )
                    self.rules.append(rule)
                except Exception as e:
                    print(f"Warning: Error loading rule for category '{category_name}': {e}")
            
            # Sort rules by priority (higher priority first)
            self.rules.sort(key=lambda x: x.priority, reverse=True)
            print(f"Loaded {len(self.rules)} categorization rules from {self.config_path}")
            
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            print("Creating backup and using default configuration")
            self.backup_and_create_default()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using default configuration")
            self.load_default_rules()
    
    def create_config_file(self) -> None:
        """Creates a new configuration file with default settings."""
        try:
            config = self.create_default_config()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"Created default configuration file: {self.config_path}")
        except Exception as e:
            print(f"Error creating configuration file: {e}")
    
    def backup_and_create_default(self) -> None:
        """Creates backup of corrupted config and generates new default."""
        try:
            if os.path.exists(self.config_path):
                backup_path = f"{self.config_path}.backup"
                os.rename(self.config_path, backup_path)
                print(f"Backed up corrupted config to {backup_path}")
            self.create_config_file()
            self.load_configuration()
        except Exception as e:
            print(f"Error during backup and recovery: {e}")
            self.load_default_rules()
    
    def load_default_rules(self) -> None:
        """Loads minimal default rules when config loading fails."""
        self.rules = [
            CategoryRule("Food & Dining", ["restaurant", "food", "grocery"], 10),
            CategoryRule("Transportation", ["gas", "uber", "parking"], 9),
            CategoryRule("Shopping", ["amazon", "store", "shopping"], 8),
            CategoryRule("Bills & Utilities", ["bill", "utility", "rent"], 12),
            CategoryRule("Uncategorized", [], 0)
        ]
        self.default_category = "Uncategorized"
        print("Loaded minimal default categorization rules")
    
    def categorize_transaction(self, transaction: Transaction) -> str:
        """Categorizes a single transaction based on loaded rules."""
        try:
            description = transaction.description.strip()
            if not description:
                return self.default_category
            
            # Check each rule in priority order
            for rule in