```python
"""
Configuration File System for Transaction Categorization

This module provides a flexible configuration system that allows users to:
- Customize categorization rules for financial transactions
- Add, modify, and delete spending categories
- Map specific merchant names to categories using regex patterns
- Manage configuration through JSON files with validation

The system supports regex pattern matching for merchant names, priority-based
rule ordering, and comprehensive error handling. Configuration changes are
automatically validated and saved.

Usage:
    python script.py

Features:
- JSON-based configuration storage
- Regex pattern matching for merchant categorization
- Priority-based rule processing
- Interactive command-line interface
- Input validation and error handling
"""

import json
import re
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class ConfigurationManager:
    """Manages categorization rules and configuration for transaction processing."""
    
    def __init__(self, config_file: str = "categorization_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration structure."""
        return {
            "categories": [
                "Food & Dining",
                "Transportation",
                "Shopping",
                "Entertainment",
                "Utilities",
                "Healthcare",
                "Education",
                "Travel",
                "Income",
                "Other"
            ],
            "merchant_rules": [
                {
                    "pattern": r"(?i)(mcdonalds?|burger king|kfc|subway|pizza)",
                    "category": "Food & Dining",
                    "priority": 10,
                    "description": "Fast food restaurants"
                },
                {
                    "pattern": r"(?i)(uber|lyft|taxi|metro|bus)",
                    "category": "Transportation", 
                    "priority": 10,
                    "description": "Transportation services"
                },
                {
                    "pattern": r"(?i)(amazon|walmart|target|costco)",
                    "category": "Shopping",
                    "priority": 10,
                    "description": "Major retailers"
                },
                {
                    "pattern": r"(?i)(netflix|spotify|hulu|disney)",
                    "category": "Entertainment",
                    "priority": 10,
                    "description": "Streaming services"
                },
                {
                    "pattern": r"(?i)(electric|water|gas|internet|phone)",
                    "category": "Utilities",
                    "priority": 10,
                    "description": "Utility services"
                }
            ],
            "settings": {
                "default_category": "Other",
                "case_sensitive": False,
                "enable_fuzzy_matching": False
            },
            "version": "1.0",
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_config(self) -> None:
        """Load configuration from file or create default if not exists."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                print(f"Configuration loaded from {self.config_file}")
            else:
                self._save_config()
                print(f"Default configuration created: {self.config_file}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def _validate_regex(self, pattern: str) -> bool:
        """Validate regex pattern."""
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False
    
    def add_category(self, category: str) -> bool:
        """Add a new category to the configuration."""
        try:
            if not category or not category.strip():
                print("Error: Category name cannot be empty")
                return False
            
            category = category.strip()
            if category in self.config["categories"]:
                print(f"Category '{category}' already exists")
                return False
            
            self.config["categories"].append(category)
            self._save_config()
            print(f"Added category: {category}")
            return True
            
        except Exception as e:
            print(f"Error adding category: {e}")
            return False
    
    def remove_category(self, category: str) -> bool:
        """Remove a category from the configuration."""
        try:
            if category not in self.config["categories"]:
                print(f"Category '{category}' not found")
                return False
            
            # Check if category is used in rules
            used_in_rules = [rule for rule in self.config["merchant_rules"] 
                           if rule["category"] == category]
            
            if used_in_rules:
                print(f"Cannot remove category '{category}' - it's used in {len(used_in_rules)} rule(s)")
                return False
            
            self.config["categories"].remove(category)
            self._save_config()
            print(f"Removed category: {category}")
            return True
            
        except Exception as e:
            print(f"Error removing category: {e}")
            return False
    
    def add_merchant_rule(self, pattern: str, category: str, priority: int = 5, 
                         description: str = "") -> bool:
        """Add a new merchant categorization rule."""
        try:
            if not pattern or not pattern.strip():
                print("Error: Pattern cannot be empty")
                return False
            
            if not self._validate_regex(pattern):
                print("Error: Invalid regex pattern")
                return False
            
            if category not in self.config["categories"]:
                print(f"Error: Category '{category}' does not exist")
                return False
            
            # Check for duplicate patterns
            existing = [rule for rule in self.config["merchant_rules"] 
                       if rule["pattern"] == pattern]
            
            if existing:
                print(f"Pattern '{pattern}' already exists")
                return False
            
            new_rule = {
                "pattern": pattern,
                "category": category,
                "priority": priority,
                "description": description or f"Rule for {category}"
            }
            
            self.config["merchant_rules"].append(new_rule)
            # Sort rules by priority (higher priority first)
            self.config["merchant_rules"].sort(key=lambda x: x["priority"], reverse=True)
            self._save_config()
            print(f"Added merchant rule: {pattern} -> {category}")
            return True
            
        except Exception as e:
            print(f"Error adding merchant rule: {e}")
            return False
    
    def remove_merchant_rule(self, pattern: str) -> bool:
        """Remove a merchant categorization rule."""
        try:
            original_count = len(self.config["merchant_rules"])
            self.config["merchant_rules"] = [
                rule for rule in self.config["merchant_rules"] 
                if rule["pattern"] != pattern
            ]
            
            if len(self.config["merchant_rules"]) == original_count:
                print(f"Pattern '{pattern}' not found")
                return False
            
            self._save_config()
            print(f"Removed merchant rule: {pattern}")
            return True
            
        except Exception as e:
            print(f"Error removing merchant rule: {e}")
            return False
    
    def categorize_merchant(self, merchant_name: str) -> Tuple[str, Optional[str]]: