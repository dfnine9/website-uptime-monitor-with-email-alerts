```python
#!/usr/bin/env python3
"""
Expense Categorization Configuration Manager

This module provides a framework for creating and managing expense categorization rules
through configuration files. It allows users to define custom keywords and spending 
categories without modifying the core code, making it easy to adapt to different
spending patterns and requirements.

Features:
- JSON-based configuration file management
- Keyword-based expense categorization
- Case-insensitive matching with configurable priority
- Extensible category system
- Built-in validation and error handling
- Example transaction processing

Usage:
    python script.py

The script will create a sample configuration file, demonstrate categorization
with example transactions, and show how to extend the system with new rules.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ExpenseCategorizer:
    """Manages expense categorization based on configurable keyword rules."""
    
    def __init__(self, config_file: str = "categorization_config.json"):
        """
        Initialize the categorizer with a configuration file.
        
        Args:
            config_file: Path to the JSON configuration file
        """
        self.config_file = config_file
        self.config = {}
        self.categories = {}
        self.default_category = "Uncategorized"
        
        try:
            self.load_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self) -> None:
        """Create a default configuration file with sample categorization rules."""
        default_config = {
            "metadata": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "description": "Expense categorization rules configuration"
            },
            "settings": {
                "case_sensitive": False,
                "default_category": "Uncategorized",
                "match_partial": True,
                "priority_order": ["exact_match", "contains", "starts_with", "ends_with"]
            },
            "categories": {
                "Food & Dining": {
                    "keywords": [
                        "restaurant", "cafe", "coffee", "pizza", "burger", "deli",
                        "grocery", "supermarket", "food", "dining", "lunch", "dinner",
                        "starbucks", "mcdonald", "subway", "chipotle", "domino"
                    ],
                    "patterns": {
                        "exact_match": ["uber eats", "door dash", "grubhub"],
                        "contains": ["restaurant", "cafe", "food"],
                        "starts_with": ["rest ", "cafe "],
                        "ends_with": [" restaurant", " cafe", " diner"]
                    },
                    "priority": 1,
                    "description": "Restaurants, groceries, food delivery"
                },
                "Transportation": {
                    "keywords": [
                        "uber", "lyft", "taxi", "gas", "fuel", "parking", "metro",
                        "bus", "train", "airline", "flight", "car", "auto", "mechanic"
                    ],
                    "patterns": {
                        "exact_match": ["shell", "chevron", "bp", "exxon"],
                        "contains": ["gas", "fuel", "parking", "auto"],
                        "starts_with": ["uber ", "lyft "],
                        "ends_with": [" gas", " fuel", " parking"]
                    },
                    "priority": 2,
                    "description": "Transportation, fuel, parking, rideshare"
                },
                "Shopping": {
                    "keywords": [
                        "amazon", "target", "walmart", "costco", "mall", "store",
                        "shopping", "retail", "purchase", "buy", "order"
                    ],
                    "patterns": {
                        "exact_match": ["amazon.com", "target", "walmart", "costco"],
                        "contains": ["amazon", "store", "shop"],
                        "starts_with": ["amazon ", "shop "],
                        "ends_with": [" store", " shop", " mall"]
                    },
                    "priority": 3,
                    "description": "Retail purchases, online shopping"
                },
                "Bills & Utilities": {
                    "keywords": [
                        "electric", "electricity", "gas bill", "water", "internet",
                        "phone", "cable", "utility", "bill", "payment", "service"
                    ],
                    "patterns": {
                        "exact_match": ["pg&e", "at&t", "verizon", "comcast"],
                        "contains": ["electric", "utility", "bill"],
                        "starts_with": ["bill ", "payment "],
                        "ends_with": [" bill", " utility", " service"]
                    },
                    "priority": 4,
                    "description": "Monthly bills, utilities, services"
                },
                "Entertainment": {
                    "keywords": [
                        "netflix", "spotify", "movie", "theater", "concert",
                        "game", "entertainment", "subscription", "streaming"
                    ],
                    "patterns": {
                        "exact_match": ["netflix", "spotify", "hulu", "disney+"],
                        "contains": ["movie", "game", "stream"],
                        "starts_with": ["netflix ", "spotify "],
                        "ends_with": [" theater", " cinema", " games"]
                    },
                    "priority": 5,
                    "description": "Movies, streaming, games, subscriptions"
                },
                "Healthcare": {
                    "keywords": [
                        "doctor", "hospital", "pharmacy", "medical", "health",
                        "dental", "vision", "prescription", "clinic"
                    ],
                    "patterns": {
                        "exact_match": ["cvs pharmacy", "walgreens", "rite aid"],
                        "contains": ["medical", "health", "doctor"],
                        "starts_with": ["dr ", "medical "],
                        "ends_with": [" medical", " clinic", " hospital"]
                    },
                    "priority": 6,
                    "description": "Medical expenses, pharmacy, healthcare"
                }
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default configuration file: {self.config_file}")
            self.config = default_config
            self._parse_config()
        except Exception as e:
            print(f"Error creating default config: {e}")
            raise
    
    def load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            self._parse_config()
            print(f"Loaded configuration from: {self.config_file}")
        except FileNotFoundError:
            print(f"Configuration file not found: {self.config_file}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in configuration file: {e}")
            raise
    
    def _parse_config(self) -> None:
        """Parse loaded configuration and prepare for categorization."""
        try:
            self.categories = self.config.get("categories", {})
            settings = self.config.get("settings", {})
            self.default_category = settings.get("default_category", "Uncategorized")
            self.case_sensitive = settings.get("case_sensitive", False)
            self.match_partial = settings.get("match_partial", True)
            self.priority_order = settings.get("priority_order", ["exact_match", "contains"])
        except Exception as e:
            print(f"Error parsing configuration: {e}")
            raise
    
    def categorize_expense(self, description: str, amount: float = 0.0) -> Tuple[str, Dict]:
        """
        Categorize an expense based on its description.
        
        Args:
            description: The expense description to categorize
            amount: Optional amount (for future rule extensions)
        
        Returns:
            Tuple of (category_